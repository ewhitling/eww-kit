"""Copy the Obsidian settings of this machine's vault into obsidian/defaults/.

    make obsidian-snapshot

The copies are a starting place for a new vault. `eww install` copies each one
into a vault only when that vault lacks the file. Review the diff before
committing: this repo is public.

Two files are filtered so a new vault starts clean:
  appearance.json         keeps only CSS snippets whose file exists in the vault
  community-plugins.json  keeps only plugins this repo ships in obsidian/plugins/
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULTS = REPO / "obsidian" / "defaults"
# Settings that describe how the vault behaves. Window layout, bookmarks,
# plugin data, and other per-machine state are left out.
SETTINGS_FILES = (
    "app.json", "appearance.json", "hotkeys.json",
    "core-plugins.json", "community-plugins.json", "daily-notes.json",
)


def vault_path(home: Path) -> Path | None:
    """The vault named in ~/.config/eww/vault, or None when the file is absent."""
    pointer = home / ".config" / "eww" / "vault"
    if not pointer.is_file():
        return None
    first_line = pointer.read_text().splitlines()[0].strip()
    if first_line.startswith("~/"):
        return home / first_line[2:]
    return Path(first_line)


def shipped_plugins(repo: Path = REPO) -> set[str]:
    """Ids of the plugins this repo can install into a vault."""
    plugins = repo / "obsidian" / "plugins"
    return {entry.name for entry in plugins.iterdir() if entry.is_dir()} if plugins.is_dir() else set()


def filtered(name: str, data: object, settings_dir: Path, plugins: set[str]) -> object:
    """Drop references a new vault could not resolve."""
    if name == "appearance.json" and isinstance(data, dict):
        snippets = settings_dir / "snippets"
        data["enabledCssSnippets"] = [
            snippet for snippet in data.get("enabledCssSnippets", []) if (snippets / f"{snippet}.css").is_file()
        ]
    if name == "community-plugins.json" and isinstance(data, list):
        data = [plugin for plugin in data if plugin in plugins]
    return data


def snapshot(settings_dir: Path, destination: Path = DEFAULTS, plugins: set[str] | None = None) -> list[str]:
    """Write each settings file found in settings_dir to destination. Returns the names written."""
    plugins = shipped_plugins() if plugins is None else plugins
    destination.mkdir(parents=True, exist_ok=True)
    written = []
    for name in SETTINGS_FILES:
        source = settings_dir / name
        if not source.is_file():
            continue
        data = filtered(name, json.loads(source.read_text()), settings_dir, plugins)
        (destination / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
        written.append(name)
    return written


def main() -> int:
    home = Path(os.environ.get("EWW_HOME", Path.home()))
    vault = vault_path(home)
    if vault is None or not (vault / ".obsidian").is_dir():
        print("✗ snapshot: no vault with an .obsidian folder is named in ~/.config/eww/vault", file=sys.stderr)
        return 1
    for name in snapshot(vault / ".obsidian"):
        print(f"wrote obsidian/defaults/{name}")
    print("Review with: git diff obsidian/defaults")
    return 0


if __name__ == "__main__":
    sys.exit(main())
