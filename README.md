# Select

Select allows you to select a line interactively by searching. It works by
reading input from stdin and printing the selected line to stdout. You can
therefore use it to search anything, and it is up to you what to do with the
selected line.

![Demo](https://raw.github.com/rickardlindberg/dotfiles/master/select/demo.gif)

## Examples

Replace `Ctrl-R` in Bash:

    In ~/.bashrc:

        if [[ $- =~ .*i.* ]]; then bind '"\C-r": "\C-a select-history \C-j"'; fi

    In ~/bin/select-history:

        #!/usr/bin/env bash

        tac ~/.bash_history | select --complete -- "$@"

Open a file, buffer, or tag from vim/gvim:

    In ~/.vimrc:

        function! Select()
            if has("gui_running")
                let select_command="select --gui"
            else
                let select_command="select"
            endif
            let bufnrs = filter(range(1, bufnr("$")), 'buflisted(v:val)')
            let buffers = map(bufnrs, 'bufname(v:val)')
            let buffersout = join(buffers, "\n") . "\n"
            let selection = system("vim-find-select | " . select_command, buffersout)
            if ! has("gui_running")
                redraw!
            endif
            if strpart(selection, 0, 1) == "b"
                exec ":b " . strpart(selection, 2)
            elseif strpart(selection, 0, 1) == "t"
                exec ":tj " . strpart(selection, 2)
            elseif strlen(selection) > 0
                exec ":e " . strpart(selection, 2)
            endif
        endfunction

        nmap <C-t> :call Select()<CR>

    In ~/bin/vim-find-select:

        #!/usr/bin/env bash

        while read buffer; do
            echo "b $buffer"
        done

        find-files | awk '{ print "  " $0 }'

        if [ -f tags ]; then
            cat tags | awk '{ print "t " $1 }'
        fi

Open a file in vim:

    vim $(find | ./select)

## History

Select is inspired by [hstr](https://github.com/dvorka/hstr) and
[selecta](https://github.com/garybernhardt/selecta).

I was using hstr as a replacement for `Ctrl-R` in Bash. I found it excellent
and wanted to use the same interface to select other things. For example to
switch buffers in Vim. But hstr only allowed selecting Bash history. Then I
found selecta. It could do almost what I wanted, but one thing it lacked
was a GUI mode. I often use GVim, and then a proper console is not
available.
