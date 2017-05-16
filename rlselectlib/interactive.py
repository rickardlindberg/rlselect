from collections import namedtuple
from itertools import islice

from rlselectlib.unicode import (
    CTRL_W,
    CTRL_N,
    CTRL_P,
    CTRL_C,
    CTRL_G,
    ESC,
    BS,
    CR,
    LF,
    TAB,
    is_printable,
)


Action = namedtuple("Action", ["abort", "name"])
ACTION_ENTER = Action(False, "enter")
ACTION_TAB = Action(False, "tab")
ACTION_ESC = Action(True, "esc")
ACTION_CTRL_C = Action(True, "ctrl-c")
ACTION_CTRL_G = Action(True, "ctrl-g")


class UiController(object):

    MATCHES_START_LINE = 2

    def __init__(self, lines, term, search_fn, tab_exits):
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
        return u"selecting among {:,} lines ".format(
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
