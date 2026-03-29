"""
Squazzoni N-Test: Population Scaling Validation
Non-Linear Dynamics Specialist Protocol

Proves that selection differential S remains positive and stable
across population scales N=[250, 500, 1000].

Addresses the "Population Size" objection for JASSS review:
- Does cooperation equilibrium hold at large N?
- Does S (Breeder's Equation) remain positive?
- Is extinction risk scale-dependent?
"""
import sys
import os
import json
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import Config
from simulation import Simulation

POPULATION_TIERS = [250, 500, 1000]
N_SEEDS = 10
YEARS = 200


def run_trial(pop_size, seed):
    """Run single trial, return key metrics across all ticks."""
    cfg = Config(years=YEARS, population_size=pop_size, seed=seed)
    sim = Simulation(cfg)
    sim.run()

    rows = sim.metrics.rows
    if not rows:
        return None

    # Per-tick S values for stability analysis
    s_values = [r.get("selection_differential_S") for r in rows if r.get("selection_differential_S") is not None]
    coop_values = [r.get("mu_pop_cooperation") for r in rows if r.get("mu_pop_cooperation") is not None]

    last = rows[-1]
    pop_trajectory = [r.get("population", 0) for r in rows]
    min_pop = min(pop_trajectory) if pop_trajectory else 0
    extinction_risk = 1 if min_pop < 20 else 0

    return {
        "seed": seed,
        "pop_size": pop_size,
        "final_pop": sim.society.population_size(),
        "min_pop": min_pop,
        "extinction_risk": extinction_risk,
        "avg_cooperation": last.get("mu_pop_cooperation"),
        "final_S": last.get("selection_differential_S"),
        "mean_S": float(np.mean(s_values)) if s_values else None,
        "std_S": float(np.std(s_values)) if s_values else None,
        "S_positive_fraction": float(np.mean([1 if s > 0 else 0 for s in s_values])) if s_values else None,
        "mean_cooperation": float(np.mean(coop_values)) if coop_values else None,
        "std_cooperation": float(np.std(coop_values)) if coop_values else None,
        "mu_eligible": last.get("mu_eligible_cooperation"),
        "mu_parents": last.get("mu_parents_cooperation"),
    }


def main():
    seeds = list(range(42, 42 + N_SEEDS))

    print("SQUAZZONI N-TEST: Population Scaling Validation")
    print(f"Tiers: {POPULATION_TIERS}, Seeds: {N_SEEDS}, Years: {YEARS}")
    print("=" * 70)

    all_results = {}

    for n in POPULATION_TIERS:
        t0 = time.time()
        tier_results = []

        for seed in seeds:
            result = run_trial(n, seed)
            if result:
                tier_results.append(result)

        elapsed = time.time() - t0
        all_results[str(n)] = tier_results

        s_vals = [r["mean_S"] for r in tier_results if r["mean_S"] is not None]
        coops = [r["mean_cooperation"] for r in tier_results if r["mean_cooperation"] is not None]
        s_pos = [r["S_positive_fraction"] for r in tier_results if r["S_positive_fraction"] is not None]
        ext = sum(r["extinction_risk"] for r in tier_results)

        print(f"\nN={n} ({elapsed:.0f}s):")
        print(f"  Cooperation:  mean={np.mean(coops):.4f}  std={np.std(coops):.4f}")
        print(f"  S (mean):     mean={np.mean(s_vals):.6f}  std={np.std(s_vals):.6f}")
        print(f"  S positive:   {np.mean(s_pos):.1%} of ticks")
        print(f"  Extinction:   {ext}/{len(tier_results)} seeds")

    # Summary table
    print("\n" + "=" * 70)
    print("SQUAZZONI SCALING TABLE")
    print("=" * 70)
    print(f"{'N':>6} {'Coop':>8} {'Coop_std':>9} {'S_mean':>10} {'S_std':>10} "
          f"{'S_pos%':>7} {'Extinct':>8}")
    print("-" * 60)

    for n in POPULATION_TIERS:
        tr = all_results[str(n)]
        s_vals = [r["mean_S"] for r in tr if r["mean_S"] is not None]
        coops = [r["mean_cooperation"] for r in tr if r["mean_cooperation"] is not None]
        s_pos = [r["S_positive_fraction"] for r in tr if r["S_positive_fraction"] is not None]
        ext = sum(r["extinction_risk"] for r in tr)
        print(f"{n:>6} {np.mean(coops):>8.4f} {np.std(coops):>9.4f} "
              f"{np.mean(s_vals):>10.6f} {np.std(s_vals):>10.6f} "
              f"{np.mean(s_pos):>6.1%} {ext:>5}/{len(tr)}")

    # Verdict
    print("\n" + "=" * 70)
    s_at_1000 = [r["mean_S"] for r in all_results["1000"] if r["mean_S"] is not None]
    s_positive = np.mean(s_at_1000) > 0
    s_stable = np.std(s_at_1000) < 0.01
    ext_1000 = sum(r["extinction_risk"] for r in all_results["1000"])

    if s_positive and s_stable and ext_1000 == 0:
        print("VERDICT: S POSITIVE AND STABLE AT N=1000. SQUAZZONI OBJECTION REJECTED.")
    elif s_positive:
        print("VERDICT: S POSITIVE but variance elevated. Partial pass.")
    else:
        print("VERDICT: S NOT POSITIVE AT N=1000. OBJECTION STANDS.")
    print("=" * 70)

    with open("archive/squazzoni_n_test.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print("\nData saved: archive/squazzoni_n_test.json")


if __name__ == "__main__":
    main()
