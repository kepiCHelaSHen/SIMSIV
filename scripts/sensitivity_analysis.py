"""
SIMSIV — Sensitivity Analysis from AutoSIM Journal
Computes how much each tunable parameter affects each calibration metric,
using linear regression across all accepted experiments in the autosim journal.

This generates Table 2 of Paper 1 — reviewers of ABM papers expect it.

Usage:
    python scripts/sensitivity_analysis.py
    python scripts/sensitivity_analysis.py --top 10   (show top 10 per metric)
    python scripts/sensitivity_analysis.py --output docs/sensitivity_analysis.md
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT         = Path(__file__).parent.parent
JOURNAL_PATH = ROOT / "autosim" / "journal.jsonl"
OUTPUT_PATH  = ROOT / "docs" / "sensitivity_analysis.md"

METRICS = [
    "resource_gini",
    "mating_inequality",
    "violence_death_fraction",
    "pop_growth_rate",
    "child_survival_to_15",
    "avg_lifetime_births",
    "bond_dissolution_rate",
    "avg_cooperation",
    "avg_aggression",
]

METRIC_LABELS = {
    "resource_gini":           "Resource Gini",
    "mating_inequality":       "Mating Inequality",
    "violence_death_fraction": "Violence Death Frac",
    "pop_growth_rate":         "Pop Growth Rate",
    "child_survival_to_15":    "Child Survival",
    "avg_lifetime_births":     "Lifetime Births",
    "bond_dissolution_rate":   "Bond Dissolution",
    "avg_cooperation":         "Avg Cooperation",
    "avg_aggression":          "Avg Aggression",
}


def load_journal(path: Path) -> pd.DataFrame:
    """Load autosim journal, keeping only completed experiment entries."""
    rows = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
            except json.JSONDecodeError:
                continue

            # Skip meta-entries
            if entry.get("action") in ("RUN_START",):
                continue
            if not entry.get("params") or not entry.get("metrics"):
                continue

            row = {"experiment_id": entry["experiment_id"],
                   "action":        entry["action"],
                   "score":         entry["score"]}
            row.update(entry["params"])
            row.update({f"metric_{k}": v
                        for k, v in entry["metrics"].items()})
            rows.append(row)

    return pd.DataFrame(rows)


def compute_sensitivity(df: pd.DataFrame,
                        params: list[str],
                        metrics: list[str],
                        top_n: int = None) -> dict:
    """
    For each metric, regress metric value against each parameter independently.
    Returns dict of {metric: [(param, r, r2, p, direction), ...]} sorted by |r|.
    """
    results = {}

    for metric in metrics:
        col = f"metric_{metric}"
        if col not in df.columns:
            continue

        y = df[col].dropna()
        if len(y) < 10:
            continue

        correlations = []
        for param in params:
            if param not in df.columns:
                continue
            x = df[param]
            # Align on same index
            valid = x.notna() & y.notna()
            if valid.sum() < 10:
                continue
            xi = x[valid].values
            yi = y[valid].values
            if xi.std() < 1e-8:   # constant param — no variation
                continue

            r, p = stats.pearsonr(xi, yi)
            results.setdefault(metric, []).append({
                "param":     param,
                "r":         round(r,  4),
                "r2":        round(r**2, 4),
                "p":         round(p,  6),
                "direction": "↑" if r > 0 else "↓",
                "strength":  abs(r),
            })

        if metric in results:
            results[metric].sort(key=lambda x: -x["strength"])
            if top_n:
                results[metric] = results[metric][:top_n]

    return results


def write_markdown(results: dict, df: pd.DataFrame,
                   params: list[str], output_path: Path):
    """Write sensitivity analysis as a markdown document."""
    lines = []
    lines.append("# SIMSIV — Sensitivity Analysis")
    lines.append("# Generated from AutoSIM Run 3 journal (816 experiments)")
    lines.append("# This is Table 2 of Paper 1.")
    lines.append(f"# Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")
    lines.append("## Overview")
    lines.append("")

    n_exp = len(df)
    n_accept = sum(1 for a in df["action"] if "ACCEPT" in str(a))
    lines.append(f"- Total experiments analyzed: {n_exp}")
    lines.append(f"- Accepted (improved or annealed): {n_accept}")
    lines.append(f"- Parameters analyzed: {len(params)}")
    lines.append(f"- Metrics analyzed: {len(results)}")
    lines.append("")
    lines.append("Sensitivity measured as Pearson correlation (r) between")
    lines.append("parameter value and metric value across all experiments.")
    lines.append("|r| ≥ 0.30 = meaningful influence. |r| ≥ 0.50 = strong influence.")
    lines.append("")

    # Summary table — top driver per metric
    lines.append("## Summary: Strongest Driver per Metric")
    lines.append("")
    lines.append("| Metric | Top Parameter | r | r² | Direction |")
    lines.append("|--------|--------------|---|----|-----------|")

    for metric, cors in results.items():
        if not cors:
            continue
        top = cors[0]
        label = METRIC_LABELS.get(metric, metric)
        lines.append(f"| {label} | `{top['param']}` | "
                     f"{top['r']:+.3f} | {top['r2']:.3f} | {top['direction']} |")
    lines.append("")

    # Full per-metric tables
    lines.append("## Full Sensitivity Tables (per metric)")
    lines.append("")
    lines.append("Only showing parameters with |r| ≥ 0.10.")
    lines.append("")

    for metric, cors in results.items():
        label = METRIC_LABELS.get(metric, metric)
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Rank | Parameter | r | r² | p-value | Direction |")
        lines.append("|------|-----------|---|----|---------|-----------|")

        shown = [c for c in cors if c["strength"] >= 0.10]
        for i, c in enumerate(shown, 1):
            p_str = f"{c['p']:.4f}" if c["p"] >= 0.0001 else "< 0.0001"
            lines.append(f"| {i} | `{c['param']}` | "
                         f"{c['r']:+.3f} | {c['r2']:.3f} | "
                         f"{p_str} | {c['direction']} |")
        lines.append("")

    # Global sensitivity table — which params matter most overall
    lines.append("## Global Parameter Importance")
    lines.append("(Mean |r| across all metrics — measures overall influence)")
    lines.append("")
    lines.append("| Rank | Parameter | Mean |r| | Max |r| | Metrics Influenced |")
    lines.append("|------|-----------|---------|---------|-------------------|")

    param_importance = {}
    for metric, cors in results.items():
        for c in cors:
            p = c["param"]
            if p not in param_importance:
                param_importance[p] = []
            param_importance[p].append(c["strength"])

    ranked = sorted(param_importance.items(),
                    key=lambda x: -np.mean(x[1]))

    for i, (param, strengths) in enumerate(ranked[:25], 1):
        mean_r = np.mean(strengths)
        max_r  = np.max(strengths)
        n_inf  = sum(1 for s in strengths if s >= 0.10)
        lines.append(f"| {i} | `{param}` | "
                     f"{mean_r:.3f} | {max_r:.3f} | {n_inf} |")
    lines.append("")

    lines.append("## Notes for Paper")
    lines.append("")
    lines.append("- This analysis uses Pearson r (linear correlation).")
    lines.append("  Some parameters may have nonlinear effects not captured here.")
    lines.append("- The optimizer's annealing accepts worse solutions, so the")
    lines.append("  parameter space explored is broader than pure gradient descent.")
    lines.append("- Parameters with very narrow ranges (< 0.05 spread) may show")
    lines.append("  artificially low r due to range restriction.")
    lines.append("- For publication, consider supplementing with OAT")
    lines.append("  (one-at-a-time) sweeps on the top 5 parameters per metric.")
    lines.append("")
    lines.append("## Calibration Context")
    lines.append("")
    lines.append("These sensitivities are derived from the calibration search")
    lines.append("trajectory, not from a designed sensitivity experiment.")
    lines.append("They show which parameters the optimizer had to move to")
    lines.append("achieve calibration — a pragmatic but imperfect proxy for")
    lines.append("true global sensitivity.")
    lines.append("")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Saved to: {output_path}")


def print_console_summary(results: dict, top_n: int = 5):
    """Print a readable console summary."""
    print("\n" + "=" * 70)
    print("  SENSITIVITY ANALYSIS — Top drivers per metric")
    print("=" * 70)

    for metric, cors in results.items():
        label = METRIC_LABELS.get(metric, metric)
        print(f"\n  {label}:")
        for c in cors[:top_n]:
            bar = "█" * int(c["strength"] * 20)
            print(f"    {c['direction']} {c['param']:<38} "
                  f"r={c['r']:+.3f}  {bar}")


def main():
    parser = argparse.ArgumentParser(description="SIMSIV Sensitivity Analysis")
    parser.add_argument("--top",    type=int, default=5,
                        help="Top N params per metric to show (default: 5)")
    parser.add_argument("--output", type=str,
                        default=str(OUTPUT_PATH),
                        help="Output markdown path")
    parser.add_argument("--min-r",  type=float, default=0.10,
                        help="Minimum |r| to include (default: 0.10)")
    args = parser.parse_args()

    print(f"Loading journal: {JOURNAL_PATH}")
    df = load_journal(JOURNAL_PATH)
    print(f"Loaded {len(df)} experiment entries")

    # Identify tunable parameters (columns that aren't metadata or metrics)
    exclude = {"experiment_id", "action", "score", "temperature",
               "delta", "survived", "elapsed_seconds", "timestamp"}
    params = [c for c in df.columns
              if c not in exclude
              and not c.startswith("metric_")
              and df[c].dtype in (float, int, "float64", "int64")
              and df[c].nunique() > 3]

    print(f"Parameters found: {len(params)}")
    print(f"Computing correlations...")

    results = compute_sensitivity(df, params, METRICS, top_n=None)

    print_console_summary(results, top_n=args.top)

    out = Path(args.output)
    write_markdown(results, df, params, out)
    print(f"\nFull analysis written to: {out}")
    print("This is Table 2 of Paper 1.")


if __name__ == "__main__":
    main()
