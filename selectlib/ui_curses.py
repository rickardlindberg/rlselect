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
    controller.setup(curses, screen)
    return _loop(controller, screen)


def _loop(controller, screen):
    patched_screen = _PatchedScreen(screen)
    while True:
        controller.render(patched_screen)
        result = controller.process_input(screen.getch())
        if result:
            return result


class _PatchedScreen(object):

    def __init__(self, curses_screen):
        self._curses_screen = curses_screen

    def getmaxyx(self, *args, **kwargs):
        return self._curses_screen.getmaxyx(*args, **kwargs)

    def erase(self, *args, **kwargs):
        return self._curses_screen.erase(*args, **kwargs)

    def addstr(self, y, x, text, attrs):
        try:
            self._curses_screen.addstr(y, x, text, attrs)
        except curses.error:
            # Writing last position (max_y, max_x) fails, but we can ignore it.
            pass

    def refresh(self, *args, **kwargs):
        return self._curses_screen.refresh(*args, **kwargs)
