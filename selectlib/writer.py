import fcntl
import sys
import termios


def output_to_prompt(text):
    for ch in text:
        fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSTI, ch)
