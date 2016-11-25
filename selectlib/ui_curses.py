import contextlib
import curses
import os
import sys


def curses_ui_run(controller):
    with _redirect_terminal():
        return curses.wrapper(_run, controller)


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


def _run(screen, controller):
    curses.raw()
    if curses.has_colors():
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_GREEN)
    controller.setup(screen)
    return _loop(controller, screen)


def _loop(controller, screen):
    patched_screen = _Screen(screen)
    while True:
        controller.render(patched_screen)
        result = controller.process_input(screen.getch())
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
            self._curses_screen.addstr(y, x, text, attrs)
        except curses.error:
            # Writing last position (max_y, max_x) fails, but we can ignore it.
            pass

    def refresh(self):
        return self._curses_screen.refresh()
