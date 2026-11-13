# Shared zsh settings for every machine. This file is public.
# ~/.zshrc loads it through one line that `eww install` adds.
# Private settings belong in ~/.config/eww/private.zsh, which comes from the vault.

# Programs installed by eww and other user tools.
typeset -U path
path=("$HOME/.local/bin" $path)

# Starship prompt. Skipped quietly when starship is not installed.
if (( $+commands[starship] )); then
    eval "$(starship init zsh)"
fi

# Steady block cursor at every prompt. Inside herdr, an idle shell pane
# otherwise falls back to the terminal's blinking cursor.
_eww_steady_cursor() { printf '\033[2 q'; }
(( ${precmd_functions[(I)_eww_steady_cursor]} )) || precmd_functions+=(_eww_steady_cursor)

# vault: change to the primary notes vault, the first line of ~/.config/eww/vault.
# An alias with the same name would break this file: zsh expands aliases while
# it reads "vault() {". So any such alias is removed first, and the function
# is defined with the "function" keyword, which is never alias-expanded.
unalias vault 2>/dev/null
function vault {
    local file="$HOME/.config/eww/vault" dir
    if [[ ! -f $file ]]; then
        print -u2 -r -- "vault: no ~/.config/eww/vault on this machine"
        return 1
    fi
    dir=$(head -n 1 "$file")
    dir=${dir/#\~/$HOME}
    if [[ ! -d $dir ]]; then
        print -u2 -r -- "vault: folder not found: $dir"
        [[ $dir == *\\* ]] && print -u2 -r -- "vault: write the path in ~/.config/eww/vault plainly, with no backslashes"
        return 1
    fi
    cd "$dir"
}

# Private settings for this person, when the vault provides them.
[[ -f "$HOME/.config/eww/private.zsh" ]] && source "$HOME/.config/eww/private.zsh"
