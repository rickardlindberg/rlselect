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


from mock import Mock
import pytest

from rlselectlib.interactive import UiController, Action
from rlselectlib.reader import Lines
from rlselectlib.unicode import (
    CR,
    LF,
    TAB,
    ESC,
    CTRL_C,
    CTRL_G,
)


@pytest.mark.parametrize("kwargs,input_,expected_output", [
    ({},                    CR,     (Action(False, "enter"), "")),
    ({},                    LF,     (Action(False, "enter"), "")),
    ({"tab_exists": True},  TAB,    (Action(False, "tab"), "")),
    ({"tab_exists": False}, TAB,    None),
    ({},                    ESC,    (Action(True, "esc"), "")),
    ({},                    CTRL_C, (Action(True, "ctrl-c"), "")),
    ({},                    CTRL_G, (Action(True, "ctrl-g"), "")),
], ids=lambda x: "{!r}".format(x))
def test_return_values(kwargs, input_, expected_output):
    assert create_controller(**kwargs).process_input(input_) == expected_output


def create_controller(tab_exists=False):
    screen = Mock()
    screen.getmaxyx.return_value = (100,  100)
    controller = UiController(
        Lines([]),
        "",
        lambda x, y: [],
        tab_exists
    )
    controller.setup(screen)
    return controller
