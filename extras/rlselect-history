#!/usr/bin/env bash

set -e

result=$(tac ~/.bash_history | rlselect --tab --action -- "$@")

python - "$result" << EOF
import fcntl
import sys
import termios

action, selection = sys.argv[1].split("\n", 1)

if action != "tab":
    selection += "\n"

for ch in selection:
    fcntl.ioctl(sys.stdout.fileno(), termios.TIOCSTI, ch)
EOF
