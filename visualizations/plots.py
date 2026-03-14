"""
Visualization — generate charts from simulation metrics.
"""

from __future__ import annotations
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_dashboard(df: pd.DataFrame, output_dir: Path):
    """Generate a 6-panel dashboard and individual charts."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Individual plots
    _plot_single(df, "population", "Population Over Time", output_dir / "population.png")
    _plot_single(df, "resource_gini", "Resource Inequality (Gini)", output_dir / "resource_gini.png",
                 ylim=(0, 1))
    _plot_single(df, "reproductive_skew", "Reproductive Skew (Gini)", output_dir / "reproductive_skew.png",
                 ylim=(0, 1))
    _plot_single(df, "violence_rate", "Violence Rate", output_dir / "violence_rate.png")
    _plot_single(df, "unmated_male_pct", "Unmated Males %", output_dir / "unmated_males.png",
                 ylim=(0, 1))
    _plot_single(df, "child_survival_rate", "Child Survival Rate", output_dir / "child_survival.png",
                 ylim=(0, 1))

    # Composite dashboard
    fig, axes = plt.subplots(2, 3, figsize=(16, 10))
    fig.suptitle("SIMSIV Dashboard", fontsize=14, fontweight="bold")

    panels = [
        ("population", "Population"),
        ("resource_gini", "Resource Gini"),
        ("reproductive_skew", "Reproductive Skew"),
        ("violence_rate", "Violence Rate"),
        ("unmated_male_pct", "Unmated Males %"),
        ("avg_aggression", "Avg Aggression"),
    ]

    for ax, (col, title) in zip(axes.flat, panels):
        if col in df.columns:
            ax.plot(df["year"], df[col], linewidth=1.2, color="#2c3e50")
            ax.fill_between(df["year"], df[col], alpha=0.15, color="#3498db")
        ax.set_title(title, fontsize=10)
        ax.set_xlabel("Year", fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(output_dir / "dashboard.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def _plot_single(df: pd.DataFrame, column: str, title: str, path: Path,
                 ylim: tuple = None):
    if column not in df.columns:
        return
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(df["year"], df[column], linewidth=1.5, color="#2c3e50")
    ax.fill_between(df["year"], df[column], alpha=0.15, color="#3498db")
    ax.set_title(title, fontsize=12)
    ax.set_xlabel("Year")
    ax.set_ylabel(column)
    if ylim:
        ax.set_ylim(ylim)
    ax.grid(True, alpha=0.3)
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
