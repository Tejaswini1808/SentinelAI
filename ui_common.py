"""Shared bootstrap + styling helpers for the Streamlit UI. Every page imports
this and calls bootstrap() before importing anything from the backend `app`
package, since backend/app/config.py reads credentials from os.environ at
import time."""
import os
import sys
from pathlib import Path

import streamlit as st

_BACKEND_DIR = str(Path(__file__).parent / "backend")

CSS = """
<style>
.sentinel-badge {
    display: inline-block;
    padding: 0.15rem 0.6rem;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.02em;
    text-transform: uppercase;
}
.sentinel-badge-critical { background: #3b0d0d; color: #ff6b6b; border: 1px solid #ff6b6b44; }
.sentinel-badge-high { background: #3a1d0a; color: #ff9f43; border: 1px solid #ff9f4344; }
.sentinel-badge-medium { background: #3a330a; color: #feca57; border: 1px solid #feca5744; }
.sentinel-badge-low { background: #0a3a1e; color: #1dd1a1; border: 1px solid #1dd1a144; }
.sentinel-badge-falsepositive { background: #14213d; color: #54a0ff; border: 1px solid #54a0ff44; }
.sentinel-badge-blocked { background: #3b0d0d; color: #ff6b6b; border: 1px solid #ff6b6b44; }
.sentinel-badge-allowed { background: #0a3a1e; color: #1dd1a1; border: 1px solid #1dd1a144; }
.sentinel-chip {
    display: inline-block;
    padding: 0.1rem 0.5rem;
    margin: 0.1rem;
    border-radius: 6px;
    font-size: 0.72rem;
    background: #1a1f2e;
    color: #a3b3ff;
    border: 1px solid #2a3352;
}
.sentinel-card {
    background: #12151f;
    border: 1px solid #232838;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.8rem;
}
</style>
"""

_CLASSIFICATION_CLASS = {
    "Critical": "critical",
    "High": "high",
    "Medium": "medium",
    "Low": "low",
    "False Positive": "falsepositive",
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


def badge(text: str, kind: str) -> str:
    return f'<span class="sentinel-badge sentinel-badge-{kind}">{text}</span>'


def classification_badge(classification: str) -> str:
    kind = _CLASSIFICATION_CLASS.get(classification, "medium")
    return badge(classification, kind)


def chip(text: str) -> str:
    return f'<span class="sentinel-chip">{text}</span>'


def chips(items: list[str]) -> str:
    return " ".join(chip(i) for i in items)


def card(inner_html: str):
    st.markdown(f'<div class="sentinel-card">{inner_html}</div>', unsafe_allow_html=True)
