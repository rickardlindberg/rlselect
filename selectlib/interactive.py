from curses.ascii import unctrl, isprint, BS, CR, LF, TAB, ESC
from curses import KEY_ENTER
from curses import KEY_BACKSPACE
from itertools import islice


class UiController(object):

    MATCHES_START_LINE = 2

    def __init__(self, lines, term, search_fn):
        self._lines = lines
        self._term = term
        self._search_fn = search_fn

    def setup(self, screen):
        self._read_size(screen)
        self._set_term(self._term)

    def render(self, screen):
        screen.erase()
        self._render_matches(screen)
        self._render_header(screen)
        self._render_term(screen)
        screen.refresh()

    def process_input(self, ch):
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

    def _read_size(self, screen):
        y, x = screen.getmaxyx()
        self._height = y
        self._width = x

    def _render_matches(self, screen):
        y = self.MATCHES_START_LINE
        for (match_index, (line_index, items)) in enumerate(self._matches):
            self._render_match(
                screen, y, match_index, self._lines[line_index], items
            )
            y += 1

    def _render_match(self, screen, y, match_index, line, items):
        if match_index == self._match_highlight:
            self._text(screen, y, 0, line.ljust(self._width), "select")
        else:
            x = 0
            for start, end in items:
                self._text(screen, y, x, line[x:start], "default")
                self._text(screen, y, start, line[start:end], "highlight")
                x = end
            self._text(screen, y, x, line[x:], "default")

    def _render_header(self, screen):
        self._text(screen, 1, 0, self._get_status_text(), "status")

    def _get_status_text(self):
        return "selecting among {:,} lines ".format(
            len(self._lines)
        ).rjust(self._width)

    def _render_term(self, screen):
        self._text(screen, 0, 0, "> {}".format(self._term), "default")

    def _text(self, screen, y, x, text, style):
        if x >= self._width:
            return
        text = text.replace("\t", " "*4)
        if x + len(text) >= self._width:
            text = text[:self._width-x]
        screen.addstr(y, x, text, style)

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
            return self._lines[self._matches[self._match_highlight][0]]
        elif len(self._matches) > 0:
            return self._lines[self._matches[0][0]]
        else:
            return self._term
