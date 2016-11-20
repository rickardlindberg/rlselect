from curses.ascii import unctrl, isprint, BS, CR, LF, TAB, ESC
from curses import KEY_ENTER, KEY_BACKSPACE
from itertools import islice
import contextlib
import curses
import os
import sys


def run_curses(lines, term, search_fn):
    return Curses().run(lines, term, search_fn)


class Curses(object):

    MATCHES_START_LINE = 2

    def run(self, lines, term, search_fn):
        self._lines = lines
        self._search_fn = search_fn
        with self._redirect_terminal():
            return curses.wrapper(self._run, term)

    @contextlib.contextmanager
    def _redirect_terminal(self):
        stdin_fileno = sys.stdin.fileno()
        stdout_fileno = sys.stdout.fileno()
        terminal_stdin = open("/dev/tty", "rb")
        terminal_stdout = open("/dev/tty", "wb")
        process_stdin = os.dup(sys.stdin.fileno())
        process_stdout = os.dup(sys.stdout.fileno())
        os.dup2(terminal_stdin.fileno(), stdin_fileno)
        os.dup2(terminal_stdout.fileno(), stdout_fileno)
        yield
        os.dup2(process_stdin, stdin_fileno)
        os.dup2(process_stdout, stdout_fileno)

    def _run(self, screen, term):
        curses.raw()
        if curses.has_colors():
            curses.use_default_colors()
            STYLE_HIGHLIGHT.init_pair(1)
            STYLE_SELECT.init_pair(2)
        self._read_size(screen)
        self._set_term(term)
        return self._loop(screen)

    def _read_size(self, screen):
        y, x = screen.getmaxyx()
        self._height = y
        self._width = x

    def _loop(self, screen):
        while True:
            self._render(screen)
            ch = screen.getch()
            if isprint(ch):
                self._set_term(self._term + chr(ch))
            elif ch in (BS, KEY_BACKSPACE):
                self._set_term(self._term[:-1])
            elif unctrl(ch) == "^N":
                self._set_match_highlight(self._match_highlight + 1)
            elif unctrl(ch) == "^P":
                self._set_match_highlight(self._match_highlight - 1)
            elif ch in (KEY_ENTER, CR, LF):
                return ("select", self._get_selected_item())
            elif ch in (ESC,) or unctrl(ch) in ("^C", "^G"):
                return ("abort", self._get_selected_item())
            elif ch == TAB:
                return ("tab", self._get_selected_item())

    def _render(self, screen):
        screen.erase()
        self._render_matches(screen)
        self._render_header(screen)
        self._render_term(screen)
        screen.refresh()

    def _render_matches(self, screen):
        y = self.MATCHES_START_LINE
        for (match_index, (line_index, items)) in enumerate(self._matches):
            self._render_match(
                screen, y, match_index, self._lines[line_index], items
            )
            y += 1

    def _render_match(self, screen, y, match_index, line, items):
        if match_index == self._match_highlight:
            self._text(screen, y, 0, line.ljust(self._width), STYLE_SELECT)
        else:
            x = 0
            for start, end in items:
                self._text(screen, y, x, line[x:start], STYLE_DEFAULT)
                self._text(screen, y, start, line[start:end], STYLE_HIGHLIGHT)
                x = end
            self._text(screen, y, x, line[x:], STYLE_DEFAULT)

    def _render_header(self, screen):
        self._text(screen, 1, 0, self._get_status_text(), STYLE_STATUS)

    def _get_status_text(self):
        return "selecting among {:,} lines ".format(
            len(self._lines)
        ).rjust(self._width)

    def _render_term(self, screen):
        self._text(screen, 0, 0, "> {}".format(self._term), STYLE_DEFAULT)

    def _text(self, screen, y, x, text, style):
        if x >= self._width:
            return
        text = text.replace("\t", " "*4)
        if x + len(text) >= self._width:
            text = text[:self._width-x]
        try:
            screen.addstr(y, x, text, style.attrs())
        except curses.error:
            # Writing last position (max_y, max_x) fails, but we can ignore it.
            pass

    def _set_term(self, new_term):
        self._term = new_term
        self._search()

    def _search(self):
        self._matches = list(islice(
            self._search_fn(self._lines, self._term),
            self._max_matches()
        ))
        if len(self._matches) > 0:
            self._match_highlight = 0
        else:
            self._match_highlight = -1

    def _max_matches(self):
        return self._height - self.MATCHES_START_LINE

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
            return self._lines[self._matches[self._match_highlight][0]]
        elif len(self._matches) > 0:
            return self._lines[self._matches[0][0]]
        else:
            return self._term


class Style(object):

    def __init__(self, fg, bg, extra_attrs=0):
        self._fg = fg
        self._bg = bg
        self._extra_attrs = extra_attrs

    def init_pair(self, number):
        self._number = number
        curses.init_pair(number, self._fg, self._bg)

    def attrs(self):
        return curses.color_pair(self._number) | self._extra_attrs


class BuiltinStyle(object):

    def __init__(self, attrs=0):
        self._attrs = attrs

    def attrs(self):
        return self._attrs


STYLE_DEFAULT = BuiltinStyle()
STYLE_HIGHLIGHT = Style(curses.COLOR_RED, -1, curses.A_BOLD)
STYLE_SELECT = Style(curses.COLOR_WHITE, curses.COLOR_GREEN, curses.A_BOLD)
STYLE_STATUS = BuiltinStyle(curses.A_REVERSE | curses.A_BOLD)
