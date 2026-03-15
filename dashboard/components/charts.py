"""Shared chart helper functions for SIMSIV dashboard."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from .constants import COLORS, PLOT_TEMPLATE


def hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    h = color_hex.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def add_band(fig, x, mean_series, std_series, color_hex, secondary_y=None):
    """Add a +/-1 sigma shaded confidence band to a Plotly figure."""
    if std_series is None:
        return
    upper = mean_series + std_series
    lower = np.maximum(mean_series - std_series, 0)
    r, g, b = hex_to_rgb(color_hex)
    band = go.Scatter(
        x=list(x) + list(x[::-1]),
        y=list(upper) + list(lower[::-1]),
        fill="toself",
        fillcolor=f"rgba({r},{g},{b},0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False, hoverinfo="skip",
    )
    if secondary_y is not None:
        fig.add_trace(band, secondary_y=secondary_y)
    else:
        fig.add_trace(band)


def add_epidemic_bands(fig, df: pd.DataFrame):
    """Add vertical red shaded bands for epidemic years."""
    epi_col = None
    if "epidemic_active" in df.columns:
        epi_col = "epidemic_active"
    elif "epidemic_deaths" in df.columns:
        epi_col = "epidemic_deaths"
    if epi_col is None:
        return

    in_epidemic = False
    start_yr = None
    for _, row in df.iterrows():
        active = bool(row[epi_col]) if epi_col == "epidemic_active" else row[epi_col] > 0
        yr = row["year"]
        if active and not in_epidemic:
            start_yr = yr
            in_epidemic = True
        elif not active and in_epidemic:
            fig.add_vrect(x0=start_yr, x1=yr, fillcolor="rgba(229,57,53,0.12)",
                          layer="below", line_width=0)
            in_epidemic = False
    if in_epidemic and start_yr is not None:
        fig.add_vrect(x0=start_yr, x1=df["year"].iloc[-1],
                      fillcolor="rgba(229,57,53,0.12)", layer="below", line_width=0)


def lorenz_curve(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Compute Lorenz curve. Returns (x, y) cumulative fractions."""
    sorted_vals = np.sort(values)
    n = len(sorted_vals)
    cumsum = np.cumsum(sorted_vals)
    total = cumsum[-1]
    if total == 0:
        return np.linspace(0, 1, n), np.linspace(0, 1, n)
    y = np.concatenate([[0], cumsum / total])
    x = np.linspace(0, 1, n + 1)
    return x, y


def standard_layout(title: str, height: int = 400, **kwargs) -> dict:
    return dict(title=title, height=height, template=PLOT_TEMPLATE,
                margin=dict(l=40, r=40, t=40, b=40), **kwargs)
