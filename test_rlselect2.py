# Copyright (C) 2017  Rickard Lindberg
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

from io import BytesIO
from unittest.mock import Mock
import pytest

from rlselect2 import (
    Action,
    Config,
    CR,
    CTRL_C,
    CTRL_G,
    ESC,
    LF,
    Lines,
    search,
    TAB,
    UiController,
)

def test_defaults():
    config = Config()
    assert config.get_highlight_fg() == "RED"
    assert config.get_highlight_bg() == "BACKGROUND"
    assert config.get_selection_fg() == "WHITE"
    assert config.get_selection_bg() == "GREEN"
    assert config.get_rgb("BACKGROUND") == (253, 246, 227)
    assert config.get_rgb("FOREGROUND") == (101, 123, 131)
    assert config.get_rgb("BLACK") == (7, 54, 66)
    assert config.get_rgb("BLUE") == (38, 139, 210)
    assert config.get_rgb("CYAN") == (42, 161, 152)
    assert config.get_rgb("GREEN") == (133, 153, 0)
    assert config.get_rgb("MAGENTA") == (211, 54, 130)
    assert config.get_rgb("RED") == (220, 50, 47)
    assert config.get_rgb("WHITE") == (238, 232, 213)
    assert config.get_rgb("YELLOW") == (181, 137, 0)
    assert config.get_gui_font_size() == 11
    assert config.get_gui_size() == (900, 648)


def test_custom(tmpdir):
    tmpdir.join("example.cfg").write("""\
[theme]
highlight_fg = MAGENTA
highlight_bg = CYAN
selection_fg = BLACK
selection_bg = BLUE
gui_font_size = 20
gui_size = 1000, 1000

[rgb]
BACKGROUND = 1, 1, 1
FOREGROUND = 2, 2, 2
BLACK = 3, 3, 3
BLUE = 4, 4, 4
CYAN = 5, 5, 5
GREEN = 6, 6, 6
MAGENTA = 7, 7, 7
RED = 8, 8, 8
WHITE = 9, 9, 9
YELLOW = 10, 10, 10
""")
    config = Config(str(tmpdir.join("example.cfg")))
    assert config.get_highlight_fg() == "MAGENTA"
    assert config.get_highlight_bg() == "CYAN"
    assert config.get_selection_fg() == "BLACK"
    assert config.get_selection_bg() == "BLUE"
    assert config.get_rgb("BACKGROUND") == (1, 1, 1)
    assert config.get_rgb("FOREGROUND") == (2, 2, 2)
    assert config.get_rgb("BLACK") == (3, 3, 3)
    assert config.get_rgb("BLUE") == (4, 4, 4)
    assert config.get_rgb("CYAN") == (5, 5, 5)
    assert config.get_rgb("GREEN") == (6, 6, 6)
    assert config.get_rgb("MAGENTA") == (7, 7, 7)
    assert config.get_rgb("RED") == (8, 8, 8)
    assert config.get_rgb("WHITE") == (9, 9, 9)
    assert config.get_rgb("YELLOW") == (10, 10, 10)
    assert config.get_gui_font_size() == 20
    assert config.get_gui_size() == (1000, 1000)

def test_filter():
    lines = Lines([
        "one",
        "two",
        "three",
    ])
    term = "t"
    assert list(search(lines, term)) == [
        (1, [(0, 1)]),
        (2, [(0, 1)]),
    ]

def test_re():
    lines = Lines([
        "one",
        "some].*chars",
        "three",
    ])
    term = "].*"
    assert list(search(lines, term)) == [
        (1, [(4, 7)]),
    ]

def test_ignores_case():
    lines = Lines([
        "hone",
        "tHree",
    ])
    term = "h"
    assert list(search(lines, term)) == [
        (0, [(0, 1)]),
        (1, [(1, 2)]),
    ]

def test_uses_case():
    lines = Lines([
        "hone",
        "tHree",
    ])
    term = "H"
    assert list(search(lines, term)) == [
        (1, [(1, 2)]),
    ]

def test_multiple_terms():
    lines = Lines([
        "one of them",
        "two",
    ])
    term = "ne th"
    assert list(search(lines, term)) == [
        (0, [(1, 3), (7, 9)]),
    ]

def test_repeat():
    lines = Lines([
        "aaa",
    ])
    term = "aa"
    assert list(search(lines, term)) == [
        (0, [(0, 2)]),
    ]

def test_incorrect_mark_bug():
    lines = Lines([
        "/tests/test",
    ])
    term = "/test"
    assert list(search(lines, term)) == [
        (0, [(0, 5), (6, 11)]),
    ]

@pytest.mark.parametrize("kwargs,input_,expected_output", [
    ({},                   CR,     (Action(False, "enter"), "")),
    ({},                   LF,     (Action(False, "enter"), "")),
    ({"tab_exits": True},  TAB,    (Action(False, "tab"), "")),
    ({"tab_exits": False}, TAB,    None),
    ({},                   ESC,    (Action(True, "esc"), "")),
    ({},                   CTRL_C, (Action(True, "ctrl-c"), "")),
    ({},                   CTRL_G, (Action(True, "ctrl-g"), "")),
], ids=lambda x: "{!r}".format(x))
def test_return_values(kwargs, input_, expected_output):
    assert create_controller(**kwargs).process_input(input_) == expected_output

def create_controller(tab_exits=False):
    screen = Mock()
    screen.getmaxyx.return_value = (100,  100)
    controller = UiController(
        Lines([]),
        "",
        lambda x, y: [],
        tab_exits
    )
    controller.setup(screen)
    return controller

def test_splits_stream_into_lines():
    assert get_lines(b"one\ntwo\r\nthree\rfour\n", "ascii") == [
        u"one",
        u"two",
        u"three",
        u"four",
    ]

def test_skips_duplicate_lines():
    assert get_lines(b"dup\ndup", "ascii") == [
        u"dup",
    ]

def test_converts_unknown_bytes_to_special_character():
    UNICODCE_UNKNOWN_CHAR = u"\uFFFD"
    assert get_lines(b"a\xFFb", "ascii") == [
        u"a{0}b".format(UNICODCE_UNKNOWN_CHAR),
    ]

def get_lines(binary, encoding):
    lines = Lines.from_stream(BytesIO(binary), encoding)
    return [
        lines.get(index)
        for index
        in range(lines.count())
    ]
