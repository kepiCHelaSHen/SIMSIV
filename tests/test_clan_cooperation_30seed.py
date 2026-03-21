"""
30-seed stress test for clan cooperation foundation.

SIMSIV-V2 — Publication-quality variance analysis.
Seeds: 1-30.
Reports: mean, std, 95% CI, min, max, distribution shape.
"""

from __future__ import annotations

import sys
import time
import numpy as np
from scipy import stats as sp_stats

from models.clan.clan_simulation import ClanSimulation
from models.clan.clan_base import (
    compute_band_cooperation,
    compute_clan_cooperation,
)


def run_seed(seed: int, n_years: int = 50, n_bands: int = 3,
             pop_per_band: int = 30) -> dict:
    """Run a ClanSimulation and compute cooperation metrics at final year."""
    sim = ClanSimulation(
        seed=seed,
        n_years=n_years,
        n_bands=n_bands,
        population_per_band=pop_per_band,
    )
    sim.run()
    clan_coop = compute_clan_cooperation(sim.clan_society)

    return {
        "seed": seed,
        "clan_mean_cooperation": clan_coop["clan_mean_cooperation"],
        "clan_cooperation_variance": clan_coop["clan_cooperation_variance"],
        "mean_collective_action_capacity": clan_coop["mean_collective_action_capacity"],
        "mean_inter_band_trust": clan_coop["mean_inter_band_trust"],
        "total_population": sim.clan_society.total_population(),
    }


def report_metric(name: str, values: list[float]) -> dict:
    """Compute and print full statistics for a metric."""
    arr = np.array(values)
    n = len(arr)
    mean = float(np.mean(arr))
    std = float(np.std(arr, ddof=1))  # sample std
    se = std / np.sqrt(n)
    ci_95 = sp_stats.t.interval(0.95, df=n - 1, loc=mean, scale=se)
    median = float(np.median(arr))
    iqr = float(np.percentile(arr, 75) - np.percentile(arr, 25))
    skew = float(sp_stats.skew(arr))
    kurtosis = float(sp_stats.kurtosis(arr))
    shapiro_stat, shapiro_p = sp_stats.shapiro(arr)

    print(f"\n  {name}:")
    print(f"    n        = {n}")
    print(f"    mean     = {mean:.4f}")
    print(f"    median   = {median:.4f}")
    print(f"    std (s)  = {std:.4f}")
    print(f"    SE       = {se:.4f}")
    print(f"    95% CI   = [{ci_95[0]:.4f}, {ci_95[1]:.4f}]")
    print(f"    min      = {float(np.min(arr)):.4f}")
    print(f"    max      = {float(np.max(arr)):.4f}")
    print(f"    IQR      = {iqr:.4f}")
    print(f"    skewness = {skew:.4f}")
    print(f"    kurtosis = {kurtosis:.4f}")
    print(f"    Shapiro-Wilk: W={shapiro_stat:.4f}, p={shapiro_p:.4f}"
          f" ({'normal' if shapiro_p > 0.05 else 'non-normal'})")

    return {
        "mean": mean, "std": std, "se": se,
        "ci_lower": ci_95[0], "ci_upper": ci_95[1],
        "median": median, "min": float(np.min(arr)), "max": float(np.max(arr)),
        "shapiro_p": shapiro_p,
    }


def main():
    seeds = list(range(1, 31))
    results = []

    print("=" * 70)
    print("SIMSIV-V2 — 30-Seed Cooperation Stress Test")
    print("=" * 70)
    print(f"Seeds: 1-30")
    print(f"Simulation: 50 years, 3 bands, 30 agents/band")
    print()

    t0 = time.time()
    for i, seed in enumerate(seeds, 1):
        t_seed = time.time()
        r = run_seed(seed)
        elapsed = time.time() - t_seed
        results.append(r)
        print(f"  [{i:2d}/30] Seed {seed:3d}: "
              f"coop={r['clan_mean_cooperation']:.4f}, "
              f"CAC={r['mean_collective_action_capacity']:.4f}, "
              f"pop={r['total_population']:3d}  "
              f"({elapsed:.1f}s)")

    total_time = time.time() - t0
    print(f"\nTotal runtime: {total_time:.1f}s "
          f"(avg {total_time / len(seeds):.1f}s per seed)")

    # ── Full statistics ──────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("STATISTICAL ANALYSIS (n=30)")
    print("=" * 70)

    coop_stats = report_metric(
        "clan_mean_cooperation",
        [r["clan_mean_cooperation"] for r in results],
    )
    cac_stats = report_metric(
        "mean_collective_action_capacity",
        [r["mean_collective_action_capacity"] for r in results],
    )
    trust_stats = report_metric(
        "mean_inter_band_trust",
        [r["mean_inter_band_trust"] for r in results],
    )
    pop_stats = report_metric(
        "total_population",
        [float(r["total_population"]) for r in results],
    )

    # ── Anomaly check ────────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print("ANOMALY DETECTION (sigma threshold = 0.15)")
    print("=" * 70)

    for name, stats in [("cooperation", coop_stats), ("CAC", cac_stats)]:
        sigma = stats["std"]
        status = "STABLE" if sigma <= 0.15 else "ANOMALY"
        print(f"  {name}: sigma = {sigma:.4f} -> {status}")

    # ── Coefficient of variation ─────────────────────────────────────────
    print("\n" + "=" * 70)
    print("COEFFICIENT OF VARIATION (relative stability)")
    print("=" * 70)
    for name, stats in [("cooperation", coop_stats), ("CAC", cac_stats),
                         ("trust", trust_stats), ("population", pop_stats)]:
        cv = stats["std"] / stats["mean"] * 100 if stats["mean"] != 0 else 0
        print(f"  {name}: CV = {cv:.2f}%")

    # ── Raw data table for paper ─────────────────────────────────────────
    print("\n" + "=" * 70)
    print("RAW DATA (for paper appendix)")
    print("=" * 70)
    print(f"{'Seed':>4s} | {'Cooperation':>11s} | {'CAC':>8s} | "
          f"{'Trust':>8s} | {'Pop':>4s}")
    print("-" * 50)
    for r in results:
        print(f"{r['seed']:4d} | {r['clan_mean_cooperation']:11.4f} | "
              f"{r['mean_collective_action_capacity']:8.4f} | "
              f"{r['mean_inter_band_trust']:8.4f} | "
              f"{r['total_population']:4d}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
