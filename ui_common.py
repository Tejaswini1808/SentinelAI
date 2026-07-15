"""Shared bootstrap + styling helpers for the Streamlit UI. Every page imports
this and calls bootstrap() before importing anything from the backend `app`
package, since backend/app/config.py reads credentials from os.environ at
import time.

Colors follow the dataviz skill's validated dark-mode status palette (fixed,
never themed) — status color is always paired with an icon + label, never
color alone.
"""
import os
import sys
from pathlib import Path

import streamlit as st

_BACKEND_DIR = str(Path(__file__).parent / "backend")

CSS = """
<style>
:root {
    --surface-1: #1a1a19;
    --page-plane: #0d0d0d;
    --ink-primary: #ffffff;
    --ink-secondary: #c3c2b7;
    --ink-muted: #898781;
    --border-hairline: rgba(255, 255, 255, 0.10);
    --status-good: #0ca30c;
    --status-warning: #fab219;
    --status-serious: #ec835a;
    --status-critical: #d03b3b;
    --accent-blue: #3987e5;
}

/* Hero banner */
.sentinel-hero {
    background: linear-gradient(135deg, #14213d 0%, #1a1a19 60%, #2a0d0d 100%);
    border: 1px solid var(--border-hairline);
    border-radius: 14px;
    padding: 1.8rem 2rem;
    margin-bottom: 1.2rem;
}
.sentinel-hero h1 { margin: 0 0 0.3rem 0; font-size: 2rem; }
.sentinel-hero p.subtitle { color: var(--ink-secondary); font-size: 1.05rem; margin: 0 0 0.9rem 0; }

/* Stat tile: label (sentence case, no colon) + big semibold value */
.sentinel-stat-row { display: flex; gap: 0.8rem; flex-wrap: wrap; margin-bottom: 0.8rem; }
.sentinel-stat-tile {
    flex: 1;
    min-width: 160px;
    background: var(--surface-1);
    border: 1px solid var(--border-hairline);
    border-radius: 10px;
    padding: 0.9rem 1.1rem;
}
.sentinel-stat-label { color: var(--ink-muted); font-size: 0.8rem; margin-bottom: 0.3rem; }
.sentinel-stat-value { color: var(--ink-primary); font-size: 1.7rem; font-weight: 600; line-height: 1.1; word-break: break-word; }
.sentinel-stat-sub { color: var(--ink-secondary); font-size: 0.78rem; margin-top: 0.2rem; }

/* Status badges — icon + label + color, never color alone */
.sentinel-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.3rem;
    padding: 0.2rem 0.65rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
}
.sentinel-badge-critical { background: color-mix(in srgb, var(--status-critical) 20%, transparent); color: var(--status-critical); border: 1px solid var(--status-critical); }
.sentinel-badge-serious  { background: color-mix(in srgb, var(--status-serious) 20%, transparent); color: var(--status-serious); border: 1px solid var(--status-serious); }
.sentinel-badge-warning  { background: color-mix(in srgb, var(--status-warning) 20%, transparent); color: var(--status-warning); border: 1px solid var(--status-warning); }
.sentinel-badge-good     { background: color-mix(in srgb, var(--status-good) 20%, transparent); color: var(--status-good); border: 1px solid var(--status-good); }
.sentinel-badge-info     { background: color-mix(in srgb, var(--accent-blue) 20%, transparent); color: var(--accent-blue); border: 1px solid var(--accent-blue); }

.sentinel-chip {
    display: inline-block;
    padding: 0.12rem 0.55rem;
    margin: 0.12rem;
    border-radius: 6px;
    font-size: 0.72rem;
    background: var(--surface-1);
    color: var(--accent-blue);
    border: 1px solid var(--border-hairline);
}
.sentinel-card {
    background: var(--surface-1);
    border: 1px solid var(--border-hairline);
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
</style>
"""

# (badge_kind, icon) — status color is always paired with an icon + label.
_CLASSIFICATION_STYLE = {
    "Critical": ("critical", "🛑"),
    "High": ("serious", "⚠️"),
    "Medium": ("warning", "🟡"),
    "Low": ("good", "🟢"),
    "False Positive": ("info", "ℹ️"),
}


def bootstrap():
    if _BACKEND_DIR not in sys.path:
        sys.path.insert(0, _BACKEND_DIR)

    try:
        secrets = dict(st.secrets)
    except Exception:
        secrets = {}
    for key, value in secrets.items():
        if isinstance(value, str) and not os.environ.get(key):
            os.environ[key] = value

    st.markdown(CSS, unsafe_allow_html=True)


def badge(text: str, kind: str, icon: str = "") -> str:
    prefix = f"{icon} " if icon else ""
    return f'<span class="sentinel-badge sentinel-badge-{kind}">{prefix}{text}</span>'


def classification_badge(classification: str) -> str:
    kind, icon = _CLASSIFICATION_STYLE.get(classification, ("warning", "🟡"))
    return badge(classification, kind, icon)


def grounding_badge(is_grounded: bool, score: float) -> str:
    kind, icon = ("good", "✅") if is_grounded else ("critical", "🚫")
    return badge(f"grounding {score:.2f}", kind, icon)


def chip(text: str) -> str:
    return f'<span class="sentinel-chip">{text}</span>'


def chips(items: list[str]) -> str:
    return " ".join(chip(i) for i in items)


def card(inner_html: str):
    st.markdown(f'<div class="sentinel-card">{inner_html}</div>', unsafe_allow_html=True)


def stat_row(tiles: list[tuple[str, str, str]]):
    """tiles: list of (label, value, sub_caption)."""
    html = '<div class="sentinel-stat-row">'
    for label, value, sub in tiles:
        sub_html = f'<div class="sentinel-stat-sub">{sub}</div>' if sub else ""
        html += (
            f'<div class="sentinel-stat-tile">'
            f'<div class="sentinel-stat-label">{label}</div>'
            f'<div class="sentinel-stat-value">{value}</div>'
            f"{sub_html}</div>"
        )
    html += "</div>"
    st.markdown(html, unsafe_allow_html=True)


def hero(title: str, subtitle: str, chip_list: list[str] | None = None):
    chips_html = chips(chip_list) if chip_list else ""
    st.markdown(
        f'<div class="sentinel-hero"><h1>{title}</h1><p class="subtitle">{subtitle}</p>{chips_html}</div>',
        unsafe_allow_html=True,
    )
