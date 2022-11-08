#!/usr/bin/env python3
#
# Copyright (C) 2017, 2021  Rickard Lindberg
#
# This file is part of rlselect.
#
# rlselect is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# rlselect is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with rlselect.  If not, see <http://www.gnu.org/licenses/>.

from collections import namedtuple
from configparser import RawConfigParser
from itertools import islice
import locale
import os
import sys
import io


class Config(object):

    def __init__(self, path=None):
        self._config_parser = RawConfigParser()
        self._config_parser.add_section("theme")
        self._config_parser.set("theme", "highlight_fg", "RED")
        self._config_parser.set("theme", "highlight_bg", "BACKGROUND")
        self._config_parser.set("theme", "selection_fg", "WHITE")
        self._config_parser.set("theme", "selection_bg", "GREEN")
        self._config_parser.set("theme", "gui_font_size", "11")
        self._config_parser.set("theme", "gui_size", "900, 648")
        self._config_parser.add_section("rgb")
        self._config_parser.set("rgb", "BACKGROUND", "253, 246, 227")
        self._config_parser.set("rgb", "FOREGROUND", "101, 123, 131")
        self._config_parser.set("rgb", "BLACK", "7, 54, 66")
        self._config_parser.set("rgb", "BLUE", "38, 139, 210")
        self._config_parser.set("rgb", "CYAN", "42, 161, 152")
        self._config_parser.set("rgb", "GREEN", "133, 153, 0")
        self._config_parser.set("rgb", "MAGENTA", "211, 54, 130")
        self._config_parser.set("rgb", "RED", "220, 50, 47")
        self._config_parser.set("rgb", "WHITE", "238, 232, 213")
        self._config_parser.set("rgb", "YELLOW", "181, 137, 0")
        if path is not None:
            self._config_parser.read([path])

    def get_highlight_fg(self):
        return self._config_parser.get("theme", "highlight_fg")

    def get_highlight_bg(self):
        return self._config_parser.get("theme", "highlight_bg")

    def get_selection_fg(self):
        return self._config_parser.get("theme", "selection_fg")

    def get_selection_bg(self):
        return self._config_parser.get("theme", "selection_bg")

    def get_rgb(self, name):
        return self._get_int_tuple("rgb", name, 3)

    def get_gui_font_size(self):
        return self._config_parser.getint("theme", "gui_font_size")

    def get_gui_size(self):
        return self._get_int_tuple("theme", "gui_size", 2)

    def _get_int_tuple(self, section, name, size):
        result = tuple(
            int(x.strip())
            for x
            in self._config_parser.get(section, name).split(",")
        )
        if len(result) != size:
            raise ValueError("Expected {} integers but got {} for {}".format(
                size,
                len(result),
                name
            ))
        return result

def search(lines, expression):
    match = get_match_fn(expression)
    for index, line in lines.iter():
        result = match(line)
        if result is not None:
            yield (index, marks_to_ranges(result))

def get_match_fn(expression):
    def match(line):
        if ignore_case:
            line = line.lower()
        marks = set()
        for term, term_len in terms:
            # Negative matching..
            if term[0] == '!':
                # A single exclamation char always matches
                if term == '!':
                    continue
                # A double exclamation string means match for single exclamation char
                elif term.startswith('!!'):
                    term = term[1:]
                else:
                    # If the term after exclamation char is not in line..
                    # we have a match, so continue matching.
                    if term[1:] not in line:
                        continue
            if term in line:
                index = line.find(term)
                while index != -1:
                    marks.update(range(index, index+term_len))
                    index = line.find(term, index+term_len)
            else:
                # If one term doesn't match, the expression doesn't match.
                return None
        return marks
    ignore_case = expression == expression.lower()
    terms = [(term, len(term)) for term in expression.split()]
    return match

def marks_to_ranges(marks):
    result = []
    start = None
    end = None
    for mark in sorted(marks):
        if start is None:
            start = mark
            end = start + 1
        elif mark > end:
            result.append((start, end))
            start = mark
            end = start + 1
        else:
            end = mark + 1
    if start is not None:
        result.append((start, end))
    return result

CTRL_W = u"\u0017"
CTRL_N = u"\u000E"
CTRL_P = u"\u0010"
CTRL_C = u"\u0003"
CTRL_G = u"\u0007"
ESC = u"\u001B"
BS = u"\u0008"
CR = u"\u000D"
LF = u"\u000A"
TAB = u"\u0009"

def is_printable(unicode_character):
    return ord(unicode_character) >= 32

Action = namedtuple("Action", ["abort", "name"])
ACTION_ENTER = Action(False, "enter")
ACTION_TAB = Action(False, "tab")
ACTION_ESC = Action(True, "esc")
ACTION_CTRL_C = Action(True, "ctrl-c")
ACTION_CTRL_G = Action(True, "ctrl-g")

class UiController(object):

    MATCHES_START_LINE = 2

    def __init__(self, lines, term, search_fn, tab_exits, extended_status_line):
        self._lines = lines
        self._term = term
        self._search_fn = search_fn
        self._action_map = {
            CR: ACTION_ENTER,
            LF: ACTION_ENTER,
            ESC: ACTION_ESC,
            CTRL_C: ACTION_CTRL_C,
            CTRL_G: ACTION_CTRL_G,
        }
        if tab_exits:
            self._action_map[TAB] = ACTION_TAB
        self._extended_status_line = extended_status_line
        self._total_nbr_of_matched_lines = 0

    def setup(self, screen):
        self._read_size(screen)
        self._set_term(self._term)

    def render(self, screen):
        screen.erase()
        self._render_matches(screen)
        self._render_header(screen)
        self._render_term(screen)
        screen.refresh()

    def process_input(self, unicode_character):
        if unicode_character == BS:
            self._set_term(self._term[:-1])
        elif unicode_character == CTRL_W:
            self._set_term(strip_last_word(self._term))
        elif unicode_character == CTRL_N:
            self._set_match_highlight(self._match_highlight + 1)
        elif unicode_character == CTRL_P:
            self._set_match_highlight(self._match_highlight - 1)
        elif unicode_character in self._action_map:
            return (
                self._action_map[unicode_character],
                self._get_selected_item()
            )
        elif is_printable(unicode_character):
            self._set_term(self._term + unicode_character)

    def _read_size(self, screen):
        y, x = screen.getmaxyx()
        self._height = y
        self._width = x

    def _render_matches(self, screen):
        y = self.MATCHES_START_LINE
        for (match_index, (line_index, items)) in enumerate(self._matches):
            self._render_match(
                screen, y, match_index, self._lines.get(line_index), items
            )
            y += 1

    def _render_match(self, screen, y, match_index, line, items):
        if match_index == self._match_highlight:
            self._text(screen, y, 0, self._get_line_text(line), "select")
        else:
            last = 0
            x = 0
            for start, end in items:
                x += self._text(screen, y, x, line[last:start], "default")
                x += self._text(screen, y, x, line[start:end], "highlight")
                last = end
            self._text(screen, y, x, line[last:], "default")

    def _get_line_text(self, line):
        return line.ljust(self._width)

    def _render_header(self, screen):
        self._text(screen, 1, 0, self._get_status_text(), "status")

    def _get_status_text(self):
        if self._extended_status_line:
            return u"{} lines matched, {} lines visible, among {:,} lines ".format(
                self._total_nbr_of_matched_lines,
                len(self._matches),
                self._lines.count()
            ).rjust(self._width)
        else:
            return u"selectiong among {:,} lines ".format(
                self._lines.count()
            ).rjust(self._width)

    def _render_term(self, screen):
        self._text(screen, 0, 0, self._get_term_text(), "default")

    def _get_term_text(self):
        return u"> {}".format(self._term)

    def _text(self, screen, y, x, text, style):
        if x >= self._width:
            return 0
        text = expand_variable_width(text)
        if x + len(text) >= self._width:
            text = text[:self._width-x]
        screen.addstr(y, x, text, style)
        return len(text)

    def _set_term(self, new_term):
        self._term = new_term
        if self._extended_status_line:
            self._search_extended()
        else:
            self._search()
        if len(self._matches) > 0:
            self._match_highlight = 0
        else:
            self._match_highlight = -1

    def _search(self):
        self._matches = list(islice(
            self._search_fn(self._lines, self._term),
            self._max_matches()
        ))

    def _search_extended(self):
        all_matches = list(self._search_fn(self._lines, self._term))
        self._total_nbr_of_matched_lines = len(all_matches)
        self._matches = all_matches[: self._max_matches()]

    def _max_matches(self):
        return max(0, self._height - self.MATCHES_START_LINE)

    def _set_match_highlight(self, new_value):
        if len(self._matches) == 0:
            return
        if new_value >= len(self._matches):
            self._match_highlight = 0
        elif new_value < 0:
            self._match_highlight = len(self._matches) - 1
        else:
            self._match_highlight = new_value

    def _get_selected_item(self):
        if self._match_highlight != -1:
            return self._lines.get(self._matches[self._match_highlight][0])
        elif len(self._matches) > 0:
            return self._lines.get(self._matches[0][0])
        else:
            return self._term

def expand_variable_width(text):
    return text.replace("\t", "    ")

def strip_last_word(text):
    remaining_parts = text.rstrip().split(" ")[:-1]
    if remaining_parts:
        return " ".join(remaining_parts) + " "
    else:
        return ""

class Lines(object):

    @staticmethod
    def from_stream(stream, no_ansi_esc=False):
        if platform_is_windows():
            data = io.TextIOWrapper(sys.stdin.buffer, encoding='utf-8').read()
        else:
            data = stream.read()
        if no_ansi_esc:
            data = Lines.remove_ansi_sequencies(data)
        return Lines(data.splitlines())

    @staticmethod
    def remove_ansi_sequencies(data):
        ansi_sequences_to_remove = (
            "\x1b[0m",  # End mark
            "\x1b[30m", # Color black
            "\x1b[31m", # Color red
            "\x1b[32m", # Color green
            "\x1b[33m", # Color yellow
            "\x1b[34m", # Color blue
            "\x1b[35m", # Color magenta
            "\x1b[36m", # Color cyan
            "\x1b[37m", # Color white
        )
        for ansi_sequence in ansi_sequences_to_remove:
            data = data.replace(ansi_sequence, '')
        return data

    def __init__(self, lines):
        self._lines = unique(lines)


    def iter(self):
        return enumerate(self._lines)

    def count(self):
        return len(self._lines)

    def get(self, index):
        return self._lines[index]

def unique(items):
    result = []
    seen = {}
    for item in items:
        if item not in seen:
            seen[item] = True
            result.append(item)
    return result

USAGE = """\
I select stuff.

Usage:
  {name} [--tab] [--action] [--gui] [--x-status] [--no-ansi-esc] [--] [<initial-search-term>...]
  {name} (-h | --help)

Options:
  --tab         Allow <Tab> to select an item.
  --action      Print the action taken on the first line.
  --gui         Use GUI version instead of console version.
  --x-status    Extended information in status line.
  --no-ansi-esc Remove ansi escape sequences for coloring from input.
  -h,  --help   Show this message and exit.
""".format(
    name=os.path.basename(__file__)
)

def main():
    args = parse_args()
    if args["-h"] or args["--help"]:
        usage()
        success()
    locale.setlocale(locale.LC_ALL, "")
    (action, result) = get_ui_fn(args)(
        Config(os.path.expanduser("~/.rlselect.cfg")),
        UiController(
            lines=Lines.from_stream(sys.stdin, no_ansi_esc=args["--no-ansi-esc"]),
            term=(" ".join(args["<initial-search-term>"])),
            search_fn=search,
            tab_exits=args["--tab"],
            extended_status_line=args["--x-status"]
        )
    )
    if args["--action"]:
        print(action.name)
    if action.abort:
        fail()
    else:
        print(result)
        success()

def platform_is_windows():
    return sys.platform.startswith("win32")

def get_ui_fn(args):
    if platform_is_windows() or args["--gui"]:
        import wx

        def wx_ui_run(config, controller):
            app = MyApp()
            main_frame = WxCurses(app, config, controller)
            main_frame.Show()
            app.MainLoop()
            return app.get_result()

        class MyApp(wx.App):

            def __init__(self):
                wx.App.__init__(self, False)
                self.set_result(None)

            def set_result(self, result):
                self._result = result

            def get_result(self):
                return self._result

        class WxCurses(wx.Frame):

            def __init__(self, app, config, controller):
                wx.Frame.__init__(self, None, size=config.get_gui_size())
                self._screen = WxScreen(self, app, config, controller)

        class WxScreen(wx.Panel):

            def __init__(self, parent, app, config, controller):
                wx.Panel.__init__(self, parent, style=wx.NO_BORDER | wx.WANTS_CHARS)
                self._app = app
                self._config = config
                self._controller = controller
                self._surface_bitmap = None
                self._commands = []
                self._init_fonts()
                self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
                self.Bind(wx.EVT_CHAR, self._on_key_down)
                self.Bind(wx.EVT_PAINT, self._on_paint)
                self.Bind(wx.EVT_SIZE, self._on_size)
                wx.CallAfter(self._after_init)

            def _after_init(self):
                self._controller.setup(self)
                self._controller.render(self)

            def getmaxyx(self):
                ww, wh = self.GetSize()
                max_y = int(wh) / int(self._fh)
                max_x = int(ww) / int(self._fw)
                return (int(max_y), int(max_x))

            def erase(self):
                self._commands = []

            def addstr(self, y, x, text, style):
                self._commands.append((y, x, text, style))

            def refresh(self):
                width, height = self.GetSize()
                self._surface_bitmap = wx.Bitmap(width, height)
                memdc = wx.MemoryDC()
                memdc.SelectObject(self._surface_bitmap)
                memdc.SetBackground(wx.Brush(
                    self._config.get_rgb("BACKGROUND"), wx.SOLID
                ))
                memdc.SetBackgroundMode(wx.PENSTYLE_SOLID)
                memdc.Clear()
                for (y, x, text, style) in self._commands:
                    if style == "highlight":
                        memdc.SetFont(self._base_font_bold)
                        fg = self._config.get_rgb(self._config.get_highlight_fg())
                        bg = self._config.get_rgb(self._config.get_highlight_bg())
                    elif style == "select":
                        memdc.SetFont(self._base_font_bold)
                        fg = self._config.get_rgb(self._config.get_selection_fg())
                        bg = self._config.get_rgb(self._config.get_selection_bg())
                    elif style == "status":
                        memdc.SetFont(self._base_font_bold)
                        fg = self._config.get_rgb("BACKGROUND")
                        bg = self._config.get_rgb("FOREGROUND")
                    else:
                        memdc.SetFont(self._base_font)
                        fg = self._config.get_rgb("FOREGROUND")
                        bg = self._config.get_rgb("BACKGROUND")
                    memdc.SetTextBackground(bg)
                    memdc.SetTextForeground(fg)
                    memdc.DrawText(text, x*self._fw, y*self._fh)
                del memdc
                self.Refresh()
                self.Update()

            def _init_fonts(self):
                self._base_font = wx.Font(
                    self._config.get_gui_font_size(),
                    wx.FONTFAMILY_TELETYPE,
                    wx.FONTSTYLE_NORMAL,
                    wx.FONTWEIGHT_NORMAL
                )
                self._base_font_bold = self._base_font.Bold()
                self._find_text_size()

            def _find_text_size(self):
                bitmap = wx.Bitmap(100, 100)
                memdc = wx.MemoryDC()
                memdc.SetFont(self._base_font)
                memdc.SelectObject(bitmap)
                self._fw, self._fh = memdc.GetTextExtent(".")

            def _on_key_down(self, evt):
                result = self._controller.process_input(chr(evt.GetUnicodeKey()))
                if result:
                    self._app.set_result(result)
                    self.GetParent().Close()
                self._controller.render(self)

            def _on_paint(self, event):
                dc = wx.AutoBufferedPaintDC(self)
                if self._surface_bitmap:
                    dc.DrawBitmap(self._surface_bitmap, 0, 0, True)

            def _on_size(self, event):
                self._after_init()
        return wx_ui_run
    else:
        import contextlib
        import curses

        COLOR_MAP = {
            "BACKGROUND": -1,
            "FOREGROUND": -1,
            "BLACK": curses.COLOR_BLACK,
            "BLUE": curses.COLOR_BLUE,
            "CYAN": curses.COLOR_CYAN,
            "GREEN": curses.COLOR_GREEN,
            "MAGENTA": curses.COLOR_MAGENTA,
            "RED": curses.COLOR_RED,
            "WHITE": curses.COLOR_WHITE,
            "YELLOW": curses.COLOR_YELLOW,
        }

        def curses_ui_run(config, controller):
            with _redirect_terminal():
                return curses.wrapper(_run, config, controller)

        @contextlib.contextmanager
        def _redirect_terminal():
            stdin_fileno = sys.stdin.fileno()
            stdout_fileno = sys.stdout.fileno()
            process_stdin = os.dup(sys.stdin.fileno())
            process_stdout = os.dup(sys.stdout.fileno())
            try:
                terminal_stdin = open("/dev/tty", "rb")
                terminal_stdout = open("/dev/tty", "wb")
                os.dup2(terminal_stdin.fileno(), stdin_fileno)
                os.dup2(terminal_stdout.fileno(), stdout_fileno)
                yield
            finally:
                os.dup2(process_stdin, stdin_fileno)
                os.dup2(process_stdout, stdout_fileno)

        def _run(screen, config, controller):
            curses.raw()
            if curses.has_colors():
                curses.use_default_colors()
                curses.init_pair(
                    1,
                    COLOR_MAP[config.get_highlight_fg()],
                    COLOR_MAP[config.get_highlight_bg()],
                )
                curses.init_pair(
                    2,
                    COLOR_MAP[config.get_selection_fg()],
                    COLOR_MAP[config.get_selection_bg()]
                )
            controller.setup(screen)
            return _loop(controller, screen)

        def _loop(controller, screen):
            patched_screen = _Screen(screen)
            buf = b""
            while True:
                controller.render(patched_screen)
                ch = screen.getch()
                if ch > 255:
                    if ch == curses.KEY_BACKSPACE:
                        buf = BS.encode(locale.getpreferredencoding())
                    elif ch == curses.KEY_ENTER:
                        buf = CR.encode(locale.getpreferredencoding())
                    else:
                        buf = b""
                        continue
                else:
                    buf += bytes([ch])
                try:
                    unicode_character = buf.decode(locale.getpreferredencoding())
                except UnicodeDecodeError:
                    # We are dealing with an incomplete multi-byte character.
                    pass
                else:
                    buf = b""
                    result = controller.process_input(unicode_character)
                    if result:
                        return result

        class _Screen(object):

            def __init__(self, curses_screen):
                self._curses_screen = curses_screen

            def getmaxyx(self):
                return self._curses_screen.getmaxyx()

            def erase(self):
                return self._curses_screen.erase()

            def addstr(self, y, x, text, style):
                if style == "highlight":
                    attrs = curses.A_BOLD
                    if curses.has_colors():
                        attrs |= curses.color_pair(1)
                elif style == "select":
                    attrs = curses.A_BOLD
                    if curses.has_colors():
                        attrs |= curses.color_pair(2)
                elif style == "status":
                    attrs = curses.A_REVERSE | curses.A_BOLD
                else:
                    attrs = 0
                try:
                    self._curses_screen.addstr(y, x, self._encode(text), attrs)
                except curses.error:
                    # Writing last position (max_y, max_x) fails, but we can ignore it.
                    pass

            def refresh(self):
                return self._curses_screen.refresh()

            def _encode(self, text):
                return text.encode(locale.getpreferredencoding())
        return curses_ui_run

def parse_args():
    args = {
        "-h": False,
        "--help": False,
        "--tab": False,
        "--action": False,
        "--gui": False,
        "--x-status": False,
        "--no-ansi-esc": False,
        "<initial-search-term>": [],
    }
    rest = sys.argv[1:]
    if rest == ["-h"]:
        args["-h"] = True
        rest = []
    if rest == ["--help"]:
        args["--help"] = True
        rest = []
    while rest:
        if rest[:1] == ["--tab"]:
            args["--tab"] = True
            rest = rest[1:]
        if rest[:1] == ["--action"]:
            args["--action"] = True
            rest = rest[1:]
        elif rest[:1] == ["--gui"]:
            args["--gui"] = True
            rest = rest[1:]
        elif rest[:1] == ["--x-status"]:
            args["--x-status"] = True
            rest = rest[1:]
        elif rest[:1] == ["--no-ansi-esc"]:
            args["--no-ansi-esc"] = True
            rest = rest[1:]
        elif rest[:1] == ["--"]:
            args["<initial-search-term>"] = rest[1:]
            rest = []
        else:
            args["<initial-search-term>"] = rest
            rest = []
    return args

def usage():
    print(USAGE.strip())

def success():
    sys.exit(0)

def fail():
    sys.exit(1)

if __name__ == "__main__":
    main()
