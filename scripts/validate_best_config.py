"""
Validation pass for best_config.yaml.

Runs the best calibrated config across many seeds and long durations to confirm
the perfect score (1.0) is robust and not a lucky artifact of 2-seed averaging.

Usage:
    python scripts/validate_best_config.py
    python scripts/validate_best_config.py --seeds 20 --years 300
    python scripts/validate_best_config.py --seeds 5 --years 200 --quick
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from simulation import Simulation
from autosim.realism_score import load_targets, extract_metrics, realism_score

BEST_CONFIG_PATH = Path(__file__).parent.parent / "autosim" / "best_config.yaml"
TARGETS_PATH     = Path(__file__).parent.parent / "autosim" / "targets.yaml"
OUTPUT_PATH      = Path(__file__).parent.parent / "autosim" / "validation_report.json"

# Default validation seeds — diverse, well-separated
DEFAULT_SEEDS = [42, 137, 271, 512, 999, 1024, 2048, 4096, 8192, 16384]

# Anthropological benchmark ranges (mirrors targets.yaml for display)
METRIC_LABELS = {
    "resource_gini":          ("Resource Gini",          "0.30–0.50"),
    "mating_inequality":      ("Mating Inequality",       "0.40–0.70"),
    "violence_death_fraction":("Violence Death Fraction", "0.05–0.15"),
    "pop_growth_rate":        ("Pop Growth Rate",         "0.00–0.01"),
    "child_survival_to_15":   ("Child Survival to 15",   "0.50–0.70"),
    "avg_lifetime_births":    ("Avg Lifetime Births",     "4.0–7.0"),
    "bond_dissolution_rate":  ("Bond Dissolution Rate",   "0.10–0.30"),
    "avg_cooperation":        ("Avg Cooperation",         "0.25–0.70"),
    "avg_aggression":         ("Avg Aggression",          "0.30–0.60"),
}


def load_best_config_params() -> dict:
    with open(BEST_CONFIG_PATH) as f:
        data = yaml.safe_load(f)
    return data["parameters"]


def build_config(params: dict, seed: int, years: int, pop: int) -> Config:
    cfg_fields = Config.__dataclass_fields__.keys()
    kwargs = {k: v for k, v in params.items() if k in cfg_fields}
    kwargs["seed"]            = seed
    kwargs["years"]           = years
    kwargs["population_size"] = pop
    return Config(**kwargs)


def run_one_seed(params: dict, seed: int, years: int, pop: int,
                 targets: dict, idx: int, total: int) -> dict:
    """Run a single validation seed. Returns result dict."""
    t0 = time.time()
    cfg = build_config(params, seed, years, pop)
    sim = Simulation(cfg)

    rows = []
    for _ in range(years):
        rows.append(sim.tick())

    elapsed = time.time() - t0
    metrics  = extract_metrics(rows, window=30)
    score, per_metric = realism_score(metrics, targets)

    final_pop = rows[-1].get("population", 0)
    survived  = final_pop >= 20

    print(f"  [{idx:>2}/{total}] seed={seed:<6}  score={score:.4f}  "
          f"pop={int(final_pop):>4}  {elapsed:.1f}s  "
          f"{'SURVIVED' if survived else '*** COLLAPSED ***'}")

    return {
        "seed":        seed,
        "score":       round(score, 6),
        "survived":    survived,
        "final_pop":   int(final_pop),
        "elapsed_s":   round(elapsed, 1),
        "metrics":     {k: round(v, 5) for k, v in metrics.items()},
        "per_metric":  {k: round(v, 5) for k, v in per_metric.items()},
    }


def print_summary(results: list[dict], years: int, pop: int, targets: dict):
    survived = [r for r in results if r["survived"]]
    scores   = [r["score"] for r in survived]

    print()
    print("=" * 72)
    print("  VALIDATION SUMMARY")
    print("=" * 72)
    print(f"  Seeds run:      {len(results)}")
    print(f"  Survived:       {len(survived)} / {len(results)}")
    print(f"  Collapsed:      {len(results) - len(survived)}")
    if scores:
        print(f"  Score — mean:   {np.mean(scores):.4f}")
        print(f"  Score — std:    {np.std(scores):.4f}")
        print(f"  Score — min:    {np.min(scores):.4f}")
        print(f"  Score — max:    {np.max(scores):.4f}")
        print(f"  Score — median: {np.median(scores):.4f}")
        perfect = sum(1 for s in scores if s >= 0.99)
        print(f"  Perfect (≥0.99):{perfect} / {len(scores)}")
    print()

    if not survived:
        print("  *** ALL RUNS COLLAPSED — config is not viable ***")
        return

    # Per-metric breakdown across all survived runs
    print(f"  {'Metric':<28} {'Target':<12} {'Mean':>8} {'Std':>8} "
          f"{'Min':>8} {'Max':>8} {'In Range':>10}")
    print("  " + "-" * 88)

    for key, (label, target_str) in METRIC_LABELS.items():
        (low, high, _) = targets.get(key, (None, None, 1.0))
        vals = [r["metrics"].get(key, float("nan")) for r in survived]
        vals = [v for v in vals if not np.isnan(v)]
        if not vals:
            continue
        mean = np.mean(vals)
        std  = np.std(vals)
        mn   = np.min(vals)
        mx   = np.max(vals)
        if low is not None:
            in_range = sum(1 for v in vals if low <= v <= high)
            in_range_str = f"{in_range}/{len(vals)}"
            flag = "✓" if in_range == len(vals) else ("⚠" if in_range > 0 else "✗")
        else:
            in_range_str = "?"
            flag = "?"
        print(f"  {flag} {label:<26} {target_str:<12} {mean:>8.3f} {std:>8.3f} "
              f"{mn:>8.3f} {mx:>8.3f} {in_range_str:>10}")

    print()

    # Fragility check — metrics near target edges
    print("  FRAGILITY CHECK (metrics within 10% of target boundary):")
    fragile = []
    for key, (label, _) in METRIC_LABELS.items():
        (low, high, _) = targets.get(key, (None, None, 1.0))
        if low is None:
            continue
        vals = [r["metrics"].get(key, float("nan")) for r in survived]
        vals = [v for v in vals if not np.isnan(v)]
        if not vals:
            continue
        mean = np.mean(vals)
        rng  = high - low
        margin = rng * 0.10
        if mean < low + margin or mean > high - margin:
            fragile.append((label, mean, low, high))

    if fragile:
        for label, mean, low, high in fragile:
            side = "FLOOR" if mean < (low + high) / 2 else "CEILING"
            print(f"    ⚠ {label}: mean={mean:.3f}  (near {side}: [{low:.3f}–{high:.3f}])")
    else:
        print("    ✓ No metrics dangerously close to boundaries")

    print()

    # Robustness verdict
    if not scores:
        verdict = "INVALID"
    elif np.min(scores) >= 0.95 and len(survived) == len(results):
        verdict = "✅ ROBUST — config is stable across all seeds"
    elif np.mean(scores) >= 0.90 and len(survived) / len(results) >= 0.8:
        verdict = "⚠ MOSTLY ROBUST — occasional outlier seeds"
    elif np.mean(scores) >= 0.80:
        verdict = "⚠ MARGINAL — significant seed variance, re-run autosim"
    else:
        verdict = "❌ NOT ROBUST — config does not generalize"

    print(f"  VERDICT: {verdict}")
    print("=" * 72)


def main():
    parser = argparse.ArgumentParser(description="Validate best_config.yaml")
    parser.add_argument("--seeds",  type=int, default=10,
                        help="Number of seeds to validate (default: 10)")
    parser.add_argument("--years",  type=int, default=200,
                        help="Simulation years per run (default: 200)")
    parser.add_argument("--pop",    type=int, default=500,
                        help="Population size (default: 500)")
    parser.add_argument("--quick",  action="store_true",
                        help="Quick mode: 5 seeds, 100 years (overrides --seeds/--years)")
    args = parser.parse_args()

    if args.quick:
        args.seeds = 5
        args.years = 100

    # Generate evenly-spaced seeds beyond the training seeds
    # Use seeds NOT in the autosim training set to test true generalization
    training_seeds = {42, 137, 271, 512, 999}
    validation_seeds = []
    rng = np.random.default_rng(7777)
    candidates = rng.integers(1000, 99999, size=1000).tolist()
    for s in candidates:
        if s not in training_seeds and s not in validation_seeds:
            validation_seeds.append(s)
        if len(validation_seeds) >= args.seeds:
            break

    print("=" * 72)
    print("  SIMSIV — Validation Pass")
    print("=" * 72)
    print(f"  Config:   {BEST_CONFIG_PATH}")
    print(f"  Seeds:    {args.seeds}  (held-out — not used in autosim training)")
    print(f"  Years:    {args.years}")
    print(f"  Pop:      {args.pop}")
    print()

    params  = load_best_config_params()
    targets = load_targets(TARGETS_PATH)

    print(f"  Best config score (autosim): "
          f"{yaml.safe_load(open(BEST_CONFIG_PATH))['autosim_best_score']:.4f}")
    print()
    print("  Running validation seeds...")
    print()

    results = []
    t_total = time.time()

    for i, seed in enumerate(validation_seeds, 1):
        result = run_one_seed(params, seed, args.years, args.pop,
                              targets, i, args.seeds)
        results.append(result)

    total_elapsed = time.time() - t_total
    print()
    print(f"  Total elapsed: {total_elapsed/60:.1f} minutes")

    print_summary(results, args.years, args.pop, targets)

    # Save full report
    report = {
        "config_path":    str(BEST_CONFIG_PATH),
        "autosim_score":  yaml.safe_load(open(BEST_CONFIG_PATH))["autosim_best_score"],
        "validation": {
            "seeds":       validation_seeds[:args.seeds],
            "years":       args.years,
            "pop":         args.pop,
            "n_runs":      len(results),
            "n_survived":  sum(1 for r in results if r["survived"]),
        },
        "scores": {
            "mean":   round(float(np.mean([r["score"] for r in results if r["survived"]])), 6)
                      if any(r["survived"] for r in results) else 0.0,
            "std":    round(float(np.std([r["score"] for r in results if r["survived"]])), 6)
                      if any(r["survived"] for r in results) else 0.0,
            "min":    round(float(np.min([r["score"] for r in results if r["survived"]])), 6)
                      if any(r["survived"] for r in results) else 0.0,
            "max":    round(float(np.max([r["score"] for r in results if r["survived"]])), 6)
                      if any(r["survived"] for r in results) else 0.0,
        },
        "per_seed": results,
    }

    with open(OUTPUT_PATH, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\n  Full report saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
