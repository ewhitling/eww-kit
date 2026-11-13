import json
from pathlib import Path

import snapshot


def make_settings(root: Path) -> Path:
    settings = root / ".obsidian"
    (settings / "snippets").mkdir(parents=True)
    (settings / "snippets" / "real.css").write_text("body {}")
    (settings / "app.json").write_text('{"showInlineTitle": false}')
    (settings / "appearance.json").write_text('{"cssTheme": "Atom", "enabledCssSnippets": ["real", "missing"]}')
    (settings / "community-plugins.json").write_text('["hood", "not-shipped"]')
    (settings / "workspace.json").write_text('{"layout": 1}')
    return settings


def test_snapshot_copies_settings_and_skips_machine_state(tmp_path: Path) -> None:
    written = snapshot.snapshot(make_settings(tmp_path), tmp_path / "out", plugins={"hood"})
    assert written == ["app.json", "appearance.json", "community-plugins.json"]
    assert not (tmp_path / "out" / "workspace.json").exists()
    assert json.loads((tmp_path / "out" / "app.json").read_text()) == {"showInlineTitle": False}


def test_snapshot_drops_missing_snippets(tmp_path: Path) -> None:
    snapshot.snapshot(make_settings(tmp_path), tmp_path / "out", plugins={"hood"})
    appearance = json.loads((tmp_path / "out" / "appearance.json").read_text())
    assert appearance["enabledCssSnippets"] == ["real"]


def test_snapshot_keeps_only_shipped_plugins(tmp_path: Path) -> None:
    snapshot.snapshot(make_settings(tmp_path), tmp_path / "out", plugins={"hood"})
    assert json.loads((tmp_path / "out" / "community-plugins.json").read_text()) == ["hood"]


def test_vault_path_reads_the_pointer_and_expands_home(tmp_path: Path) -> None:
    assert snapshot.vault_path(tmp_path) is None
    pointer = tmp_path / ".config" / "eww" / "vault"
    pointer.parent.mkdir(parents=True)
    pointer.write_text("~/notes\n")
    assert snapshot.vault_path(tmp_path) == tmp_path / "notes"


def test_shipped_plugins_lists_plugin_folders() -> None:
    assert "hood" in snapshot.shipped_plugins()
