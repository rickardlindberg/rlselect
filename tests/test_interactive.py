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
