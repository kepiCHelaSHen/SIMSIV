"""
4-Milestone × 30-Seed Battery Test for SIMSIV-V2 White Paper.

Milestones:
  1. Cooperation (clan_mean_cooperation, CAC)
  2. Trade (clan_mean_trade_capacity)
  3. Coalition Defence (clan_mean_defence_capacity)
  4. Selection Pressure (clan_prosocial_composite, selection_ratio)

30 seeds (1-30), 50 years, 3 bands, 30 agents/band.
Reports: mean, std, 95% CI, CV, Shapiro-Wilk normality for each metric.
"""

from __future__ import annotations

import sys
import time
import numpy as np
from scipy import stats as sp_stats

from models.clan.clan_simulation import ClanSimulation
from models.clan.clan_base import (
    compute_clan_cooperation,
    compute_clan_trade_openness,
    compute_clan_defence_capacity,
    compute_clan_selection_potential,
)


def run_seed(seed: int) -> dict:
    """Run one 50-year simulation and collect all 4 milestone metrics."""
    sim = ClanSimulation(
        seed=seed, n_years=50, n_bands=3, population_per_band=30,
    )
    sim.run()
    cs = sim.clan_society

    coop = compute_clan_cooperation(cs)
    trade = compute_clan_trade_openness(cs)
    defence = compute_clan_defence_capacity(cs)
    selection = compute_clan_selection_potential(cs)

    return {
        "seed": seed,
        # M1: Cooperation
        "clan_mean_cooperation": coop["clan_mean_cooperation"],
        "mean_CAC": coop["mean_collective_action_capacity"],
        # M2: Trade
        "clan_mean_trade_capacity": trade["clan_mean_trade_capacity"],
        # M3: Defence
        "clan_mean_defence_capacity": defence["clan_mean_defence_capacity"],
        # M4: Selection
        "clan_prosocial_composite": selection["clan_prosocial_composite"],
        "between_band_variance": selection["between_band_variance"],
        "within_band_variance": selection["within_band_variance"],
        "selection_ratio": selection["selection_ratio"],
        # Demographics
        "total_population": sim.clan_society.total_population(),
    }


def stat_summary(name: str, values: list[float]) -> dict:
    """Compute and return statistics for a metric."""
    arr = np.array(values)
    n = len(arr)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1))
    se = std / np.sqrt(n)
    ci_95 = sp_stats.t.interval(0.95, df=n - 1, loc=mean, scale=se)
    shapiro_stat, shapiro_p = sp_stats.shapiro(arr)
    cv = (std / mean * 100) if mean != 0 else 0.0

    return {
        "name": name, "n": n, "mean": mean, "std": std, "se": se,
        "ci_lower": ci_95[0], "ci_upper": ci_95[1],
        "min": float(np.min(arr)), "max": float(np.max(arr)),
        "cv": cv, "shapiro_w": shapiro_stat, "shapiro_p": shapiro_p,
        "normal": shapiro_p > 0.05,
    }


def print_stat(s: dict) -> None:
    """Pretty-print one metric's statistics."""
    print(f"  {s['name']}:")
    print(f"    mean={s['mean']:.4f}  std={s['std']:.4f}  "
          f"95%CI=[{s['ci_lower']:.4f}, {s['ci_upper']:.4f}]  "
          f"CV={s['cv']:.1f}%")
    print(f"    range=[{s['min']:.4f}, {s['max']:.4f}]  "
          f"Shapiro p={s['shapiro_p']:.3f} "
          f"({'normal' if s['normal'] else 'non-normal'})")


def main():
    seeds = list(range(1, 31))
    results = []

    print("=" * 74)
    print("SIMSIV-V2 — 4-Milestone × 30-Seed Battery Test")
    print("=" * 74)

    t0 = time.time()
    for i, seed in enumerate(seeds, 1):
        ts = time.time()
        r = run_seed(seed)
        elapsed = time.time() - ts
        results.append(r)
        print(f"  [{i:2d}/30] seed={seed:2d}  "
              f"coop={r['clan_mean_cooperation']:.3f}  "
              f"trade={r['clan_mean_trade_capacity']:.3f}  "
              f"defence={r['clan_mean_defence_capacity']:.3f}  "
              f"prosocial={r['clan_prosocial_composite']:.3f}  "
              f"pop={r['total_population']:3d}  "
              f"({elapsed:.1f}s)")

    total_time = time.time() - t0
    print(f"\nTotal: {total_time:.1f}s ({total_time/30:.1f}s/seed)")

    # ── Statistics per metric ────────────────────────────────────────────
    metrics = {
        "M1: clan_mean_cooperation": [r["clan_mean_cooperation"] for r in results],
        "M1: mean_CAC": [r["mean_CAC"] for r in results],
        "M2: trade_capacity": [r["clan_mean_trade_capacity"] for r in results],
        "M3: defence_capacity": [r["clan_mean_defence_capacity"] for r in results],
        "M4: prosocial_composite": [r["clan_prosocial_composite"] for r in results],
        "M4: selection_ratio": [r["selection_ratio"] for r in results],
        "Demographics: population": [float(r["total_population"]) for r in results],
    }

    print("\n" + "=" * 74)
    print("STATISTICAL RESULTS (n=30)")
    print("=" * 74)

    all_stats = {}
    for name, vals in metrics.items():
        s = stat_summary(name, vals)
        all_stats[name] = s
        print_stat(s)

    # ── Anomaly detection ────────────────────────────────────────────────
    print("\n" + "=" * 74)
    print("ANOMALY DETECTION (threshold: sigma > 0.15)")
    print("=" * 74)

    anomaly_metrics = [
        "M1: clan_mean_cooperation", "M1: mean_CAC",
        "M2: trade_capacity", "M3: defence_capacity",
        "M4: prosocial_composite",
    ]
    any_anomaly = False
    for name in anomaly_metrics:
        s = all_stats[name]
        status = "STABLE" if s["std"] <= 0.15 else "ANOMALY"
        if status == "ANOMALY":
            any_anomaly = True
        print(f"  {name}: sigma={s['std']:.4f} -> {status}")

    # ── Summary table (paper-ready) ──────────────────────────────────────
    print("\n" + "=" * 74)
    print("PAPER-READY SUMMARY TABLE")
    print("=" * 74)
    print(f"{'Milestone':<12s} {'Metric':<25s} {'Mean':>7s} {'sigma':>7s} "
          f"{'95% CI':>18s} {'CV%':>6s} {'Normal':>7s}")
    print("-" * 86)
    for name in anomaly_metrics + ["Demographics: population"]:
        s = all_stats[name]
        milestone = name.split(":")[0]
        metric = name.split(": ")[1]
        ci = f"[{s['ci_lower']:.4f}, {s['ci_upper']:.4f}]"
        norm = "Yes" if s["normal"] else "No"
        print(f"{milestone:<12s} {metric:<25s} {s['mean']:7.4f} {s['std']:7.4f} "
              f"{ci:>18s} {s['cv']:5.1f}% {norm:>7s}")

    print("\n" + ("RESULT: ALL STABLE" if not any_anomaly
                  else "RESULT: ANOMALY DETECTED"))
    return 0 if not any_anomaly else 1


if __name__ == "__main__":
    sys.exit(main())
