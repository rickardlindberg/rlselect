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


from rlselectlib.config import Config


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
