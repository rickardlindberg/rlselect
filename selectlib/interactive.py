from itertools import islice
import locale


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


class UiController(object):

    MATCHES_START_LINE = 2

    def __init__(self, lines, term, search_fn, tab_exits):
        self._lines = lines
        self._term = term
        self._search_fn = search_fn
        self._tab_exits = tab_exits

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
            self._set_term(
                self._term.decode(
                    locale.getpreferredencoding()
                )[:-1].encode(
                    locale.getpreferredencoding()
                )
            )
        elif unicode_character == CTRL_W:
            self._set_term(self._strip_last_word(self._term))
        elif unicode_character == CTRL_N:
            self._set_match_highlight(self._match_highlight + 1)
        elif unicode_character == CTRL_P:
            self._set_match_highlight(self._match_highlight - 1)
        elif unicode_character in (CR, LF):
            return ("select", self._get_selected_item())
        elif unicode_character in (ESC, CTRL_C, CTRL_G):
            return ("abort", self._get_selected_item())
        elif unicode_character == TAB and self._tab_exits:
            return ("tab", self._get_selected_item())
        elif ord(unicode_character) >= 32:
            self._set_term(
                self._term
                +
                unicode_character.encode(locale.getpreferredencoding())
            )

    def _strip_last_word(self, text):
        remaining_parts = text.rstrip().split(" ")[:-1]
        if remaining_parts:
            return " ".join(remaining_parts) + " "
        else:
            return ""

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
            self._text(screen, y, 0, self._get_line_text(line), "select")
        else:
            last = 0
            x = 0
            for start, end in items:
                before = self._unicodify(line[last:start])
                self._text(screen, y, x, before, "default")
                x += len(before)
                after = self._unicodify(line[start:end])
                self._text(screen, y, x, after, "highlight")
                x += len(after)
                last = end
            self._text(screen, y, x, self._unicodify(line[last:]), "default")

    def _get_line_text(self, line):
        return self._unicodify(line).ljust(self._width)

    def _render_header(self, screen):
        self._text(screen, 1, 0, self._get_status_text(), "status")

    def _get_status_text(self):
        return u"selecting among {:,} lines ".format(
            len(self._lines)
        ).rjust(self._width)

    def _render_term(self, screen):
        self._text(screen, 0, 0, self._get_term_text(), "default")

    def _get_term_text(self):
        return u"> {}".format(self._unicodify(self._term))

    def _unicodify(self, text):
        return text.decode(
            locale.getpreferredencoding(),
            "replace"
        ).replace("\t", "    ")

    def _text(self, screen, y, x, text, style):
        if x >= self._width:
            return
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
