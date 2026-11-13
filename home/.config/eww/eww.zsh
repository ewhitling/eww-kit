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

# vault: change to the notes vault named in ~/.config/eww/vault.
vault() {
    local file="$HOME/.config/eww/vault" dir
    if [[ ! -f $file ]]; then
        print -u2 -r -- "vault: no ~/.config/eww/vault on this machine"
        return 1
    fi
    dir=$(head -n 1 "$file")
    cd "${dir/#\~/$HOME}"
}

# Private settings for this person, when the vault provides them.
[[ -f "$HOME/.config/eww/private.zsh" ]] && source "$HOME/.config/eww/private.zsh"
