from pathlib import Path
import json
import re
import shutil

import pytest

import build

ROOT = build.ROOT


@pytest.fixture
def package(tmp_path: Path) -> Path:
    # Two levels down, so exports written outside the skill stay inside tmp_path.
    destination = tmp_path / "skills" / "house-style"
    hood = tmp_path / "obsidian" / "plugins" / "hood"
    hood.mkdir(parents=True)
    shutil.copy(ROOT / build.HOOD_STYLES, hood / "styles.css")
    shutil.copytree(ROOT, destination, ignore=shutil.ignore_patterns(".venv", "__pycache__", ".pytest_cache"))
    return destination


def test_exports_are_current() -> None:
    assert build.stale_outputs(ROOT) == []


def test_theme_value_inherits_night() -> None:
    assert build.theme_value("#123456", "paper") == "#123456"
    assert build.theme_value({"night": "#111111"}, "paper") == "#111111"


def test_resolve_follows_aliases() -> None:
    tokens = {"color": {"tokens": [{"name": "a", "value": "#abcdef"}, {"name": "b", "value": "{a}"}]}}
    assert build.resolve_colors(tokens)["paper"]["b"] == "#ABCDEF"


def test_resolve_rejects_cycles() -> None:
    tokens = {"color": {"tokens": [{"name": "a", "value": "{b}"}, {"name": "b", "value": "{a}"}]}}
    with pytest.raises(ValueError, match="Alias cycle"):
        build.resolve_colors(tokens)


def test_token_edit_marks_exports_stale(package: Path) -> None:
    path = package / "tokens/tokens.json"
    data = json.loads(path.read_text())
    next(t for t in data["color"]["tokens"] if t["name"] == "ink")["value"]["night"] = "#FFFFFF"
    path.write_text(json.dumps(data))
    stale = {str(p) for p in build.stale_outputs(package)}
    assert {"tokens/resolved.json", "assets/fonts/strata.css", "swift/Strata.swift"} <= stale


def test_mplstyle_has_no_hash_colors() -> None:
    colors = build.resolve_colors(build.load_tokens())["night"]
    assert ": #" not in build.render_mplstyle(colors, "night")


def test_template_requires_markers() -> None:
    with pytest.raises(ValueError, match="tokens:start"):
        build.render_template(build.load_tokens(ROOT), "<style></style>")


def test_token_css_aliases_artifact_themes() -> None:
    css = build.render_token_css(build.load_tokens(ROOT))
    assert '[data-theme="dark"], [data-theme="night"] {' in css
    assert '[data-theme="light"], [data-theme="paper"] {' in css
    assert ":root:not([data-theme])" in css


def test_skill_text_uses_token_colors() -> None:
    """Hex colors written by hand in SKILL.md must be real token values."""
    resolved = build.resolve_colors(build.load_tokens(ROOT))
    known = {value for theme in resolved.values() for value in theme.values()}
    written = set(re.findall(r"#[0-9A-Fa-f]{6}\b", (ROOT / "SKILL.md").read_text()))
    assert {value.upper() for value in written} <= known


def test_hood_requires_markers() -> None:
    resolved = build.resolve_colors(build.load_tokens(ROOT))
    with pytest.raises(ValueError, match="palette:start"):
        build.render_hood(resolved, "body {}")


def test_hood_night_swaps_page_and_sidebar() -> None:
    resolved = build.resolve_colors(build.load_tokens(ROOT))
    css = build.render_hood(resolved, f"{build.HOOD_START}{build.HOOD_END}")
    night, paper = css.split("body.theme-light")
    assert f"--hood-page: {resolved['night']['surface']};" in night
    assert f"--hood-sidebar: {resolved['night']['ground']};" in night
    assert f"--hood-page: {resolved['paper']['ground']};" in paper
