"""Shared Streamlit theme — consistent CSS and chart colours across all pages."""

from __future__ import annotations

import streamlit as st

# ─── Colour Palette (dark-mode safe) ─────────────────────────────────
# Use palette tokens that work on both light and dark backgrounds.

BRAND_GREEN = "#22c55e"
BRAND_GREEN_DARK = "#16a34a"
ACCENT_RED = "#ef4444"
ACCENT_AMBER = "#f59e0b"
NEUTRAL_50 = "#fafafa"
NEUTRAL_700 = "#404040"

# Chart colour sequences — consistent across all Plotly figures
CHART_COLOURS = [BRAND_GREEN, "#3b82f6", ACCENT_AMBER, ACCENT_RED, "#8b5cf6", "#06b6d4"]
COMPARISON_PAIR = ["#64748b", BRAND_GREEN]  # Traditional (slate) vs Sustainable (green)
CARBON_PAIR = [ACCENT_RED, BRAND_GREEN]  # Baseline (red) vs Sustainable (green)
SAVINGS_COLOURS = [BRAND_GREEN, "#3b82f6", ACCENT_AMBER]  # Carbon · Water · Waste

# ─── Shared CSS ──────────────────────────────────────────────────────

_GLOBAL_CSS = """
<style>
/* ── Layout ────────────────────────────────────────────────── */
.main .block-container {
    padding-top: 1.2rem;
    max-width: 1400px;
}

/* ── Metric Cards — dark-mode safe via CSS variables ──────── */
[data-testid="stMetric"] {
    background: rgba(34, 197, 94, 0.08);      /* subtle green tint */
    border-left: 4px solid #22c55e;
    border-radius: 8px;
    padding: 14px 16px;
}
[data-testid="stMetric"] label {
    font-size: 0.82rem;
    opacity: 0.75;
    letter-spacing: 0.02em;
}

/* ── Section dividers ─────────────────────────────────────── */
hr {
    margin-top: 1.5rem;
    margin-bottom: 1.5rem;
    border-color: rgba(128, 128, 128, 0.2);
}

/* ── Tighter subheaders ───────────────────────────────────── */
h2, h3 {
    margin-top: 0.8rem !important;
}

/* ── Download Buttons — subtle styling ────────────────────── */
[data-testid="stDownloadButton"] > button {
    border: 1px solid rgba(34, 197, 94, 0.4);
    border-radius: 6px;
}
[data-testid="stDownloadButton"] > button:hover {
    border-color: #22c55e;
    background: rgba(34, 197, 94, 0.08);
}
</style>
"""


def apply_theme() -> None:
    """Inject the shared CSS into the current Streamlit page."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)
