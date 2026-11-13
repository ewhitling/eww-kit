#!/bin/sh
# First run on a new machine. Unattended. Works on macOS and Ubuntu.
#
#   1. Install base tools: git, zsh, curl, fzf, jq, neovim, uv
#   2. Clone this repo, or use the checkout this script is running from
#   3. Run eww install
#
# Agent tools (claude, pi, herdr) are not installed here. `eww doctor` reports
# which of them are missing.
#
# Settings, all optional:
#   EWW_REPO_URL  where to clone from
#   EWW_DIR       where to clone to (default: ~/Developer/eww)
set -eu

EWW_REPO_URL=${EWW_REPO_URL:-https://github.com/ewhitling/eww-kit.git}
EWW_DIR=${EWW_DIR:-$HOME/Developer/eww}

say() { printf '→ %s\n' "$1"; }
have() { command -v "$1" >/dev/null 2>&1; }

install_base_tools() {
  case $(uname -s) in
    Darwin)
      if ! have brew; then
        say "installing Homebrew"
        NONINTERACTIVE=1 /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        eval "$(/opt/homebrew/bin/brew shellenv 2>/dev/null || /usr/local/bin/brew shellenv)"
      fi
      for tool in git fzf jq neovim uv gitleaks; do
        command_name=$tool
        [ "$tool" = neovim ] && command_name=nvim
        have "$command_name" || brew install "$tool"
      done
      ;;
    Linux)
      if ! have apt-get; then
        printf '✗ setup: only Ubuntu and macOS are supported\n' >&2
        exit 1
      fi
      sudo=''
      [ "$(id -u)" -eq 0 ] || sudo=sudo
      say "installing packages with apt"
      $sudo apt-get update -qq
      DEBIAN_FRONTEND=noninteractive $sudo apt-get install -y -qq git zsh curl fzf jq neovim ca-certificates
      if ! have uv; then
        say "installing uv"
        curl -LsSf https://astral.sh/uv/install.sh | sh
      fi
      # Make zsh the login shell. This is not fatal when it fails.
      if [ "${SHELL##*/}" != zsh ]; then
        $sudo chsh -s "$(command -v zsh)" "$(id -un)" || say "could not change the login shell to zsh"
      fi
      ;;
    *)
      printf '✗ setup: unsupported system %s\n' "$(uname -s)" >&2
      exit 1
      ;;
  esac
}

install_base_tools

# Use the checkout this script sits in, when there is one. Otherwise clone.
script_dir=$(cd "$(dirname "$0")" 2>/dev/null && pwd -P || true)
if [ -n "$script_dir" ] && [ -x "$script_dir/bin/eww-install" ]; then
  EWW_DIR=$script_dir
elif [ -d "$EWW_DIR/.git" ]; then
  say "updating $EWW_DIR"
  git -C "$EWW_DIR" pull --ff-only --quiet
else
  say "cloning $EWW_REPO_URL"
  mkdir -p "$(dirname "$EWW_DIR")"
  git clone --quiet "$EWW_REPO_URL" "$EWW_DIR"
fi

"$EWW_DIR/bin/eww-install"
PATH=$HOME/.local/bin:$PATH "$EWW_DIR/bin/eww-doctor" || true
