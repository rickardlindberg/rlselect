# rlselect

rlselect allows you to select a line interactively by searching. It works by
reading input from stdin and printing the selected line to stdout. You can
therefore use it to search anything, and it is up to you what to do with the
selected line.

![Demo](https://raw.github.com/rickardlindberg/rlselect/master/demo.gif)

## Shortcuts

Shortcut | Meaning
---------|------------------------------------------
BS       | Erase last typed character.
CTRL+W   | Erase last typed word.
CTRL+N   | Move to the next match.
CTRL+P   | Move to the previous match.
ENTER    | Select the current.
TAB      | Select the current if `--tab` was given.
ESC      | Exit without selecting.
CTRL+C   | Exit without selecting.
CTRL+G   | Exit without selecting.

## Default configuration

~/.rlselect.cfg

    [theme]
    highlight_fg = RED
    highlight_bg = BACKGROUND
    selection_fg = WHITE
    selection_bg = GREEN
    gui_font_size = 11
    gui_size = 900, 648

    [rgb]
    BACKGROUND = 253, 246, 227
    FOREGROUND = 101, 123, 131
    BLACK = 7, 54, 66
    BLUE = 38, 139, 210
    CYAN = 42, 161, 152
    GREEN = 133, 153, 0
    MAGENTA = 211, 54, 130
    RED = 220, 50, 47
    WHITE = 238, 232, 213
    YELLOW = 181, 137, 0

## Examples

Replace `Ctrl-R` in Bash (requires the extra `rlselect-history`):

    In ~/.bashrc:

        if [[ $- =~ .*i.* ]]; then bind '"\C-r": "\C-a rlselect-history \C-j"'; fi

Open a file, buffer, or tag from vim/gvim:

    In ~/.vimrc:

        function! Rlselect()
            if has("gui_running")
                let rlselect_command="rlselect --gui"
            else
                let rlselect_command="rlselect"
            endif
            let bufnrs = filter(range(1, bufnr("$")), 'buflisted(v:val)')
            let buffers = map(bufnrs, 'bufname(v:val)')
            let buffersout = join(buffers, "\n") . "\n"
            let selection = system("vim-find-select | " . rlselect_command, buffersout)
            if ! has("gui_running")
                redraw!
            endif
            if strpart(selection, 0, 1) == "b"
                exec ":b " . strpart(selection, 2)
            elseif strpart(selection, 0, 1) == "t"
                exec ":tj " . strpart(selection, 2)
            elseif strlen(selection) > 0
                exec ":e " . substitute(strpart(selection, 2), " ", "\\\\ ", "g")
            endif
        endfunction

        nmap <C-t> :call Rlselect()<CR>

    In ~/bin/vim-find-select:

        #!/usr/bin/env bash

        while read buffer; do
            echo "b $buffer"
        done

        find-files | awk '{ print "  " $0 }'

        if [ -f tags ]; then
            cat tags | awk '{ print "t " $1 }'
        fi

    In ~/bin/find-files

        #!/usr/bin/env bash

        find . \
            -type d -name .git        -prune -o \
            -type d -name .hg         -prune -o \
            -type d -name __pycache__ -prune -o \
            -type d -name venv        -prune -o \
            -type d -name .cache      -prune -o \
            -type f -name '.*swp'     -prune -o \
            -type f -name '*pyc'      -prune -o \
            -type f -print

Open a file in vim:

    vim $(find | rlselect)

## History

rlselect is inspired by [hstr](https://github.com/dvorka/hstr) and
[selecta](https://github.com/garybernhardt/selecta).

I was using hstr as a replacement for `Ctrl-R` in Bash. I found it excellent
and wanted to use the same interface to select other things. For example to
switch buffers in Vim. But hstr only allowed selecting Bash history. Then I
found selecta. It could do almost what I wanted, but one thing it lacked
was a GUI mode. I often use GVim, and then a proper console is not
available.
