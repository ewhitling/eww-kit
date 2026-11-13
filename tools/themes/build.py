"""Generate every Strata export from skills/house-style/tokens/tokens.json.

    make themes                                          write all exports
    uv run --no-project tools/themes/build.py --check    exit 1 if any export is out of date

tokens.json is the only file to edit by hand. Everything this script writes
carries a "generated" header and is overwritten on the next build. The token
block inside assets/template.html, between the tokens:start and tokens:end
markers, is generated too.

Most exports sit inside the house-style skill. A few are written elsewhere in
the repo, where eww install links them into the home folder.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "skills" / "house-style"
# Exports are keyed by a path relative to ROOT, so paths elsewhere in the repo climb out with "../..".
HOME_FILES = Path("../../home")
THEMES = ("night", "paper")
GENERATED = "Generated from tokens/tokens.json by tools/themes/build.py. Do not edit."

# Tokens exported to SwiftUI, in declaration order.
SWIFT_COLORS = [
    "ground", "surface", "raised", "wash", "line", "line-strong", "ink", "ink-muted", "ink-faint",
    "action", "action-soft", "on-action", "sun", "sun-soft", "on-sun", "ok", "ok-soft", "fail", "fail-soft",
    "series-1", "series-2", "series-3", "series-4", "series-5", "series-6", "series-context",
]
# Semantic terminal roles mapped to color tokens.
TERMINAL_ROLES = {
    "prompt": "action", "text": "ink", "muted": "ink-muted", "faint": "ink-faint", "ok": "ok",
    "warn": "warn", "fail": "fail", "accent": "action", "highlight": "sun", "rule": "line-strong",
}
GHOSTTY_ORDER = [
    "black", "red", "green", "yellow", "blue", "magenta", "cyan", "white",
    "brightBlack", "brightRed", "brightGreen", "brightYellow", "brightBlue", "brightMagenta", "brightCyan", "brightWhite",
]


def load_tokens(root: Path = ROOT) -> dict:
    """Read the single source of truth."""
    return json.loads((root / "tokens/tokens.json").read_text())


def theme_value(value: str | dict[str, str], theme: str) -> str:
    """A token value for one theme. A plain string applies to every theme; a missing theme inherits night."""
    if isinstance(value, str):
        return value
    return value.get(theme, value["night"])


def resolve_colors(tokens: dict) -> dict[str, dict[str, str]]:
    """Resolve every color token, following {alias} references, to a hex value per theme."""
    definitions = {item["name"]: item["value"] for item in tokens["color"]["tokens"]}

    def resolve(name: str, theme: str, seen: tuple[str, ...] = ()) -> str:
        if name in seen:
            raise ValueError(f"Alias cycle: {' -> '.join(seen + (name,))}")
        value = theme_value(definitions[name], theme)
        alias = re.fullmatch(r"\{(.+)\}", value)
        return resolve(alias.group(1), theme, seen + (name,)) if alias else value.upper()

    return {theme: {name: resolve(name, theme) for name in definitions} for theme in THEMES}


def _css_value(value: str) -> str:
    alias = re.fullmatch(r"\{(.+)\}", value)
    return f"var(--{alias.group(1)})" if alias else value


def _theme_declarations(tokens: dict, theme: str, indent: str) -> list[str]:
    lines = [f"{indent}color-scheme: {'dark' if theme == 'night' else 'light'};"]
    for item in tokens["color"]["tokens"]:
        lines.append(f"{indent}--{item['name']}: {_css_value(theme_value(item['value'], theme))};")
    for item in tokens.get("shadow", {}).get("tokens", []):
        lines.append(f"{indent}--{item['name']}: {theme_value(item['value'], theme)};")
    return lines


def render_token_css(tokens: dict) -> str:
    """Custom properties, theme selectors and type classes, without @font-face.

    Night is the default. data-theme "night" or "dark" selects night; "paper" or
    "light" selects paper, so the Artifact viewer's dark and light stamp works.
    With no attribute, a light system setting selects paper.
    """
    lines = ['/* Theme selectors: night is the default; data-theme="paper" or "light" selects paper. */']
    lines.append(':root, [data-theme="dark"], [data-theme="night"] {')
    lines += _theme_declarations(tokens, "night", "  ")
    lines.append("}")
    lines.append("@media (prefers-color-scheme: light) {")
    lines.append("  :root:not([data-theme]) {")
    lines += _theme_declarations(tokens, "paper", "    ")
    lines.append("  }")
    lines.append("}")
    lines.append('[data-theme="light"], [data-theme="paper"] {')
    lines += _theme_declarations(tokens, "paper", "  ")
    lines.append("}")
    lines.append(":root {")
    for family in ("spacing", "radius", "layout", "stroke", "timing"):
        for item in tokens.get(family, {}).get("tokens", []):
            lines.append(f"  --{item['name']}: {item['value']};")
    for key, stack in tokens["type"]["families"].items():
        lines.append(f"  --font-{key}: {stack};")
    lines.append("}")
    for group in tokens["type"]["groups"]:
        for style in group["styles"]:
            family = style.get("family", group["family"])
            transform = " text-transform: uppercase;" if style["name"] == "label" else ""
            lines.append(
                f".{style['name']} {{ font-family: var(--font-{family}); font-size: {style['fontSize']}; "
                f"line-height: {style['lineHeight']}; font-weight: {style['fontWeight']}; "
                f"letter-spacing: {style.get('letterSpacing', '0')};{transform} }}"
            )
    return "\n".join(lines) + "\n"


def render_css(tokens: dict) -> str:
    """The token CSS plus @font-face rules for the font files beside it (assets/fonts/)."""
    lines = [f"/* Strata: {GENERATED} */"]
    for font in tokens["type"]["fonts"]:
        file_name = Path(font["file"]).name
        lines.append(
            f'@font-face {{ font-family: "{font["family"]}"; src: url("{file_name}") format("woff2"); '
            f'font-weight: {font["weight"]}; font-style: {font.get("style", "normal")}; font-display: swap; }}'
        )
    return "\n".join(lines) + "\n" + render_token_css(tokens)


TEMPLATE_START = "/* tokens:start */"
TEMPLATE_END = "/* tokens:end */"


def render_template(tokens: dict, current: str) -> str:
    """Replace the generated token block inside assets/template.html, keeping the rest."""
    if TEMPLATE_START not in current or TEMPLATE_END not in current:
        raise ValueError("assets/template.html lacks the tokens:start and tokens:end markers")
    head, rest = current.split(TEMPLATE_START, 1)
    _, tail = rest.split(TEMPLATE_END, 1)
    return f"{head}{TEMPLATE_START}\n{render_token_css(tokens)}{TEMPLATE_END}{tail}"


HOOD_STYLES = Path("../../obsidian/plugins/hood/styles.css")
HOOD_START = "/* palette:start */"
HOOD_END = "/* palette:end */"
# Hood palette names mapped to color tokens, in declaration order.
HOOD_ROLES = {
    "page": "ground", "sidebar": "surface", "panel": "raised", "text": "ink", "muted": "ink-muted",
    "faint": "ink-faint", "blue": "action", "selection": "action-soft", "tab-active": "wash", "hover": "wash",
    "code": "wash", "line": "line", "line-strong": "line-strong", "on-action": "on-action", "ok": "ok",
    "warn": "warn", "fail": "fail", "ok-soft": "ok-soft", "warn-soft": "sun-soft", "fail-soft": "fail-soft",
}
# Night puts the editor on surface and the sidebar on ground. Paper keeps the mapping above.
HOOD_NIGHT_ROLES = {"page": "surface", "sidebar": "ground"}


def render_hood(resolved: dict[str, dict[str, str]], current: str) -> str:
    """Replace the generated palette inside the Hood plugin's styles.css, keeping the rest."""
    if HOOD_START not in current or HOOD_END not in current:
        raise ValueError("the Hood styles.css lacks the palette:start and palette:end markers")
    head, rest = current.split(HOOD_START, 1)
    _, tail = rest.split(HOOD_END, 1)
    blocks = []
    for selector, theme in (("body.theme-dark", "night"), ("body.theme-light", "paper")):
        roles = {**HOOD_ROLES, **(HOOD_NIGHT_ROLES if theme == "night" else {})}
        lines = [f"  --hood-{name}: {resolved[theme][token]};" for name, token in roles.items()]
        blocks.append(f"{selector} {{\n" + "\n".join(lines) + "\n}")
    return f"{head}{HOOD_START}\n" + "\n\n".join(blocks) + f"\n{HOOD_END}{tail}"


def render_mplstyle(colors: dict[str, str], theme: str) -> str:
    """A matplotlib style. Hex values carry no '#', which mplstyle treats as a comment."""
    c = {name: value.lstrip("#") for name, value in colors.items()}
    cycle = ", ".join(repr(c[f"series-{i}"]) for i in range(1, 7))
    return f"""# Strata {theme} theme for matplotlib. {GENERATED}
# Register fonts first: strata_viz.use("{theme}").
figure.facecolor: {c['ground']}
figure.edgecolor: {c['ground']}
figure.dpi: 144
savefig.facecolor: {c['ground']}
savefig.edgecolor: {c['ground']}
savefig.bbox: tight
axes.facecolor: {c['ground']}
axes.edgecolor: {c['line-strong']}
axes.linewidth: 1
axes.labelcolor: {c['ink-muted']}
axes.titlecolor: {c['ink']}
axes.titlesize: 15
axes.titleweight: 600
axes.titlelocation: left
axes.titlepad: 14
axes.labelsize: 10
axes.spines.top: False
axes.spines.right: False
axes.spines.left: False
axes.grid: True
axes.grid.axis: y
axes.axisbelow: True
axes.prop_cycle: cycler('color', [{cycle}])
grid.color: {c['line']}
grid.linewidth: 1
lines.linewidth: 2
lines.solid_capstyle: round
lines.markersize: 6
patch.edgecolor: {c['ground']}
patch.linewidth: 2
xtick.color: {c['line-strong']}
ytick.color: {c['line-strong']}
xtick.labelcolor: {c['ink-faint']}
ytick.labelcolor: {c['ink-faint']}
xtick.labelsize: 9
ytick.labelsize: 9
ytick.left: False
xtick.major.size: 4
font.family: sans-serif
font.sans-serif: Avenir Next, Figtree, DejaVu Sans
font.monospace: DM Mono, DejaVu Sans Mono
font.size: 11
text.color: {c['ink']}
legend.frameon: False
legend.fontsize: 9
legend.labelcolor: {c['ink-muted']}
"""


def _camel(name: str) -> str:
    head, *rest = name.split("-")
    return head + "".join(part.capitalize() for part in rest)


def _swift_rgb(value: str) -> str:
    r, g, b = (int(value[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return f"red: {r:.3f}, green: {g:.3f}, blue: {b:.3f}"


def render_swift(resolved: dict[str, dict[str, str]], tokens: dict) -> str:
    """SwiftUI colors and type helpers."""
    spacing = ", ".join(item["value"].removesuffix("px") for item in tokens["spacing"]["tokens"])
    radius = {item["name"]: item["value"].removesuffix("px") for item in tokens["radius"]["tokens"]}
    lines = [f"// Strata tokens for SwiftUI. {GENERATED}", "import SwiftUI", "",
             "public enum StrataTheme { case night, paper }", "", "public struct Strata {", "    public let theme: StrataTheme"]
    for name in SWIFT_COLORS:
        lines.append(f"    public var {_camel(name)}: Color {{ theme == .night ? Color({_swift_rgb(resolved['night'][name])}) "
                     f": Color({_swift_rgb(resolved['paper'][name])}) }}")
    lines += [
        "    public init(_ theme: StrataTheme = .night) { self.theme = theme }", "",
        "    // Type: Avenir Next ships with macOS and iOS. Mono: bundle DMMono-*.ttf in the app.",
        '    public static func sans(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font { .custom("Avenir Next", size: size).weight(weight) }',
        '    public static func mono(_ size: CGFloat, _ weight: Font.Weight = .regular) -> Font { .custom("DM Mono", size: size).weight(weight) }',
        f"    public static let space: [CGFloat] = [0, {spacing}]",
        f"    public static let radiusSm: CGFloat = {radius['radius-sm']}, radiusMd: CGFloat = {radius['radius-md']}, radiusLg: CGFloat = {radius['radius-lg']}",
        "}", "",
    ]
    return "\n".join(lines)


def render_streamlit(colors: dict[str, str], theme: str) -> str:
    return f"""# Strata {theme} for Streamlit. {GENERATED}
# Copy to .streamlit/config.toml
[theme]
base = "{'dark' if theme == 'night' else 'light'}"
primaryColor = "{colors['action']}"
backgroundColor = "{colors['ground']}"
secondaryBackgroundColor = "{colors['surface']}"
textColor = "{colors['ink']}"
font = "sans serif"
"""


def render_ghostty(colors: dict[str, str], ansi16: dict[str, dict[str, str]], theme: str) -> str:
    palette = "\n".join(f"palette = {i}={ansi16[key][theme]}" for i, key in enumerate(GHOSTTY_ORDER))
    return f"""# Strata {theme} for Ghostty. {GENERATED}
# Copy to ~/.config/ghostty/themes/strata-{theme}
background = {colors['ground']}
foreground = {colors['ink']}
cursor-color = {colors['action']}
selection-background = {colors['action-soft']}
selection-foreground = {colors['ink']}
{palette}
"""


NVIM_COLORS = HOME_FILES / ".config/nvim/colors/strata.lua"
# Names used by the nvim color scheme, mapped to color tokens.
NVIM_TOKENS = {
    "ground": "ground", "surface": "surface", "raised": "raised", "wash": "wash", "line": "line",
    "line_strong": "line-strong", "ink": "ink", "muted": "ink-muted", "faint": "ink-faint",
    "action": "action", "action_soft": "action-soft", "on_action": "on-action", "sun": "sun",
    "sun_soft": "sun-soft", "ok": "ok", "ok_soft": "ok-soft", "fail": "fail", "fail_soft": "fail-soft",
}
# Two more names taken from the terminal's 16 colors, for syntax only.
NVIM_ANSI = {"purple": "magenta", "cyan": "cyan"}
# Highlight groups. Each value is Lua table fields that refer to the palette as "c".
NVIM_GROUPS = {
    # Editor surfaces
    "Normal": "fg = c.ink, bg = c.ground",
    "NormalFloat": "fg = c.ink, bg = c.raised",
    "FloatBorder": "fg = c.line_strong, bg = c.raised",
    "FloatTitle": "fg = c.ink, bg = c.raised, bold = true",
    "Pmenu": "fg = c.ink, bg = c.raised",
    "PmenuSel": "fg = c.ink, bg = c.action_soft",
    "PmenuSbar": "bg = c.raised",
    "PmenuThumb": "bg = c.line_strong",
    "CursorLine": "bg = c.surface",
    "CursorColumn": "bg = c.surface",
    "ColorColumn": "bg = c.surface",
    "LineNr": "fg = c.faint",
    "CursorLineNr": "fg = c.ink, bold = true",
    "SignColumn": "fg = c.faint, bg = c.ground",
    "FoldColumn": "fg = c.faint, bg = c.ground",
    "Folded": "fg = c.muted, bg = c.surface",
    "WinSeparator": "fg = c.line",
    "StatusLine": "fg = c.ink, bg = c.raised",
    "StatusLineNC": "fg = c.muted, bg = c.surface",
    "TabLine": "fg = c.muted, bg = c.surface",
    "TabLineSel": "fg = c.ink, bg = c.wash",
    "TabLineFill": "bg = c.surface",
    "Visual": "bg = c.action_soft",
    "Search": "fg = c.ink, bg = c.sun_soft",
    "IncSearch": "fg = c.on_action, bg = c.sun",
    "CurSearch": "fg = c.on_action, bg = c.sun",
    "MatchParen": "fg = c.action, bold = true",
    "NonText": "fg = c.line_strong",
    "Whitespace": "fg = c.line",
    "EndOfBuffer": "fg = c.ground",
    "Conceal": "fg = c.faint",
    "Directory": "fg = c.action",
    "Title": "fg = c.ink, bold = true",
    "Question": "fg = c.action",
    "MoreMsg": "fg = c.action",
    "ModeMsg": "fg = c.muted",
    "ErrorMsg": "fg = c.fail",
    "WarningMsg": "fg = c.sun",
    "SpellBad": "undercurl = true, sp = c.fail",
    "SpellCap": "undercurl = true, sp = c.sun",
    "SpellRare": "undercurl = true, sp = c.purple",
    "SpellLocal": "undercurl = true, sp = c.cyan",
    # Syntax
    "Comment": "fg = c.faint, italic = true",
    "Constant": "fg = c.sun",
    "String": "fg = c.ok",
    "Character": "fg = c.ok",
    "Number": "fg = c.sun",
    "Boolean": "fg = c.sun",
    "Identifier": "fg = c.ink",
    "Function": "fg = c.action",
    "Statement": "fg = c.purple",
    "Keyword": "fg = c.purple",
    "Operator": "fg = c.muted",
    "PreProc": "fg = c.purple",
    "Type": "fg = c.cyan",
    "Special": "fg = c.action",
    "Delimiter": "fg = c.muted",
    "Underlined": "fg = c.action, underline = true",
    "Todo": "fg = c.sun, bold = true",
    "Error": "fg = c.fail",
    # Diffs and diagnostics
    "Added": "fg = c.ok",
    "Removed": "fg = c.fail",
    "Changed": "fg = c.sun",
    "DiffAdd": "bg = c.ok_soft",
    "DiffDelete": "fg = c.fail, bg = c.fail_soft",
    "DiffChange": "bg = c.sun_soft",
    "DiffText": "fg = c.ink, bg = c.action_soft",
    "DiagnosticError": "fg = c.fail",
    "DiagnosticWarn": "fg = c.sun",
    "DiagnosticInfo": "fg = c.action",
    "DiagnosticHint": "fg = c.muted",
    "DiagnosticOk": "fg = c.ok",
    "DiagnosticUnderlineError": "undercurl = true, sp = c.fail",
    "DiagnosticUnderlineWarn": "undercurl = true, sp = c.sun",
    # Markdown, through treesitter and render-markdown
    "@markup.heading": "fg = c.ink, bold = true",
    "@markup.heading.1": "fg = c.action, bold = true",
    "@markup.heading.2": "fg = c.action, bold = true",
    "@markup.strong": "bold = true",
    "@markup.italic": "italic = true",
    "@markup.strikethrough": "strikethrough = true",
    "@markup.link": "fg = c.action",
    "@markup.link.url": "fg = c.muted, underline = true",
    "@markup.raw": "fg = c.ok",
    "@markup.quote": "fg = c.muted, italic = true",
    "@markup.list": "fg = c.action",
    "@variable": "fg = c.ink",
    "RenderMarkdownCode": "bg = c.surface",
    "RenderMarkdownCodeInline": "fg = c.ok, bg = c.surface",
    "RenderMarkdownH1Bg": "bg = c.action_soft",
    "RenderMarkdownH2Bg": "bg = c.surface",
    "RenderMarkdownH3Bg": "bg = c.surface",
    "RenderMarkdownH4Bg": "bg = c.surface",
    "RenderMarkdownH5Bg": "bg = c.surface",
    "RenderMarkdownH6Bg": "bg = c.surface",
    "RenderMarkdownBullet": "fg = c.action",
    "RenderMarkdownQuote": "fg = c.line_strong",
    # mini.nvim
    "MiniStatuslineModeNormal": "fg = c.on_action, bg = c.action, bold = true",
    "MiniStatuslineModeInsert": "fg = c.on_action, bg = c.ok, bold = true",
    "MiniStatuslineModeVisual": "fg = c.on_action, bg = c.purple, bold = true",
    "MiniStatuslineModeReplace": "fg = c.on_action, bg = c.fail, bold = true",
    "MiniStatuslineModeCommand": "fg = c.on_action, bg = c.sun, bold = true",
    "MiniStatuslineModeOther": "fg = c.ink, bg = c.wash",
    "MiniStatuslineDevinfo": "fg = c.ink, bg = c.wash",
    "MiniStatuslineFilename": "fg = c.muted, bg = c.raised",
    "MiniStatuslineFileinfo": "fg = c.ink, bg = c.wash",
    "MiniStatuslineInactive": "fg = c.faint, bg = c.surface",
    "MiniPickMatchCurrent": "bg = c.action_soft",
    "MiniPickMatchRanges": "fg = c.sun, bold = true",
    "MiniFilesCursorLine": "bg = c.action_soft",
}


def render_nvim(resolved: dict[str, dict[str, str]], ansi16: dict[str, dict[str, str]]) -> str:
    """An nvim color scheme holding both themes. It follows the 'background' option."""
    lines = [f"-- Strata for nvim. {GENERATED}", "-- Night when 'background' is dark, paper when it is light.", "local palettes = {"]
    for theme in THEMES:
        lines.append(f"  {theme} = {{")
        for name, token in NVIM_TOKENS.items():
            lines.append(f'    {name} = "{resolved[theme][token]}",')
        for name, key in NVIM_ANSI.items():
            lines.append(f'    {name} = "{ansi16[key][theme]}",')
        lines.append("  },")
    lines += [
        "}",
        "",
        'vim.cmd.highlight("clear")',
        'vim.g.colors_name = "strata"',
        'local c = vim.o.background == "light" and palettes.paper or palettes.night',
        "",
        "local groups = {",
    ]
    for group, fields in NVIM_GROUPS.items():
        lines.append(f'  ["{group}"] = {{ {fields} }},')
    lines += ["}", "for name, settings in pairs(groups) do", "  vim.api.nvim_set_hl(0, name, settings)", "end", ""]
    return "\n".join(lines)


def render_semantic(resolved: dict[str, dict[str, str]], tokens: dict) -> str:
    data: dict = {theme: {role: resolved[theme][token] for role, token in TERMINAL_ROLES.items()} for theme in THEMES}
    data["glyphs"] = tokens["terminal"]["glyphs"]
    data["ansi16"] = {key: tokens["terminal"]["ansi16"][key] for key in GHOSTTY_ORDER}
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def render_all(root: Path = ROOT) -> dict[Path, str]:
    """Every export, keyed by its path relative to the package root."""
    tokens = load_tokens(root)
    resolved = resolve_colors(tokens)
    outputs = {
        Path("tokens/resolved.json"): json.dumps(resolved, indent=2) + "\n",
        Path("assets/fonts/strata.css"): render_css(tokens),
        Path("assets/tokens.css"): f"/* house-style tokens: {GENERATED} */\n" + render_token_css(tokens),
        Path("assets/template.html"): render_template(tokens, (root / "assets/template.html").read_text()),
        Path("swift/Strata.swift"): render_swift(resolved, tokens),
        Path("terminal/semantic.json"): render_semantic(resolved, tokens),
        NVIM_COLORS: render_nvim(resolved, tokens["terminal"]["ansi16"]),
        HOOD_STYLES: render_hood(resolved, (root / HOOD_STYLES).read_text()),
    }
    for theme in THEMES:
        outputs[Path(f"viz/strata-{theme}.mplstyle")] = render_mplstyle(resolved[theme], theme)
        outputs[Path(f"streamlit/{theme}/config.toml")] = render_streamlit(resolved[theme], theme)
        ghostty = render_ghostty(resolved[theme], tokens["terminal"]["ansi16"], theme)
        outputs[Path(f"terminal/strata-{theme}.ghostty")] = ghostty
        outputs[HOME_FILES / f".config/ghostty/themes/strata-{theme}"] = ghostty
    return outputs


def stale_outputs(root: Path = ROOT) -> list[Path]:
    """Exports whose file content differs from what the tokens would generate."""
    return [path for path, text in render_all(root).items()
            if not (root / path).is_file() or (root / path).read_text() != text]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true", help="report stale exports and exit 1 instead of writing")
    args = parser.parse_args(argv)
    if args.check:
        stale = stale_outputs()
        for path in stale:
            print(f"stale: {path} (run make themes)")
        return 1 if stale else 0
    for path, text in render_all().items():
        (ROOT / path).parent.mkdir(parents=True, exist_ok=True)
        (ROOT / path).write_text(text)
        print(f"wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
