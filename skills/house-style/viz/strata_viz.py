"""Strata for Python charts: matplotlib and plotly.

    import strata_viz
    strata_viz.use("night")          # or "paper"; registers fonts + applies mplstyle
    strata_viz.focus_colors(names, focus="Series A")   # one sun, the rest context
    fig.update_layout(template=strata_viz.plotly_template("paper"))
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
KIT = HERE.parent
COLORS: dict[str, dict[str, str]] = json.loads((KIT / "tokens" / "resolved.json").read_text())


def register_fonts() -> None:
    """Add the bundled Figtree and DM Mono TTFs to matplotlib's font manager."""
    from matplotlib import font_manager

    for ttf in (KIT / "assets" / "fonts" / "ttf").glob("*.ttf"):
        font_manager.fontManager.addfont(str(ttf))


def use(theme: str = "night") -> None:
    """Register fonts and apply the Strata matplotlib style for a theme."""
    import matplotlib.pyplot as plt

    register_fonts()
    plt.style.use(str(HERE / f"strata-{theme}.mplstyle"))


def series_colors(theme: str = "night") -> list[str]:
    """The six categorical colors in fixed order. Never cycle past six."""
    return [COLORS[theme][f"series-{i}"] for i in range(1, 7)]


def focus_colors(names: list[str], focus: str, theme: str = "night") -> dict[str, str]:
    """Focus mode: the focus series is sun, every other series is context."""
    return {n: COLORS[theme]["series-2" if n == focus else "series-context"] for n in names}


def sequential(theme: str = "night") -> list[str]:
    """Ridge ramp ordered low to high magnitude for the theme's ground."""
    steps = ["100", "200", "300", "400", "500", "600", "700", "800"]
    ramp = [COLORS[theme][f"ridge-{s}"] for s in steps]
    return ramp if theme == "paper" else ramp[::-1]


def diverging(theme: str = "night") -> list[str]:
    """Return theme-specific negative-to-positive colors, centered on zero."""
    scales = json.loads((KIT / "tokens" / "tokens.json").read_text())["chart_scales"]
    return [COLORS[theme][name] for name in scales[theme]["diverging"]]


def plotly_template(theme: str = "night") -> dict:
    """A plotly layout template dict using Strata colors and fonts."""
    c = COLORS[theme]
    axis = dict(gridcolor=c["line"], linecolor=c["line-strong"], zerolinecolor=c["line-strong"],
                tickfont=dict(family="DM Mono, monospace", size=11, color=c["ink-faint"]),
                title=dict(font=dict(color=c["ink-muted"], size=12)))
    return dict(layout=dict(
        paper_bgcolor=c["ground"], plot_bgcolor=c["ground"], colorway=series_colors(theme),
        font=dict(family="Avenir Next, Figtree, sans-serif", color=c["ink"], size=13),
        title=dict(font=dict(size=18, color=c["ink"]), x=0, xanchor="left"),
        xaxis=dict(axis, showgrid=False), yaxis=dict(axis, showline=False),
        legend=dict(font=dict(color=c["ink-muted"], size=12), bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=c["raised"], bordercolor=c["line-strong"], font=dict(color=c["ink"], family="DM Mono, monospace")),
        colorscale=dict(sequential=sequential(theme), diverging=diverging(theme)),
    ))
