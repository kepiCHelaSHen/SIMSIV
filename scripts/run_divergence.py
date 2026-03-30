#!/usr/bin/env python
"""
500-Year Evolutionary Divergence — Paired-Seed Design (v2)
Protocol: Zenodo 19217024 | Critic fixes applied

Fixes from adversarial audit:
  1. PAIRED SEEDS: Each seed runs BOTH scenarios, enabling paired t-test
     (eliminates inter-seed variance, ~2x statistical power)
  2. POPULATION NORMALIZATION: S values divided by sqrt(N_eligible) to
     remove small-population drift inflation
  3. CUMULATIVE TRAIT DISPLACEMENT: R_total = mean_trait(yr500) - mean_trait(yr1)
     as the primary outcome metric (integrates selection over full run)
  4. CARRYING CAPACITY: Explicitly locked at 800 for both scenarios
     (already the default, now made explicit in overrides)
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from experiments.scenarios import SCENARIOS
from models.agent import HERITABLE_TRAITS, TRAIT_HERITABILITY
from simulation import Simulation

# ── Experiment parameters ──────────────────────────────────────────────
N_SEEDS = 10
N_YEARS = 500
SEEDS = list(range(101, 101 + N_SEEDS))  # [101..110] fresh seeds
SCENARIOS_TO_RUN = ["NO_INSTITUTIONS", "STRONG_STATE"]
HIGHLIGHT_INTERVAL = 100
OUTPUT_DIR = Path("outputs/experiments/v2_paired_divergence")

SUBSTITUTION_TRAITS = [
    "cooperation_propensity",
    "impulse_control",
    "empathy_capacity",
    "aggression_propensity",
    "conformity_bias",
    "group_loyalty",
]


def compute_selection_differential(sim: Simulation) -> dict:
    """Compute S_T (raw and population-normalized) for all 35 traits.

    S_T     = Mean(Parents.genotype[T]) - Mean(Eligible.genotype[T])
    S_norm  = S_T / sqrt(N_eligible)  (removes drift-inflation from small N)
    """
    year = sim.year

    parent_ids: set[int] = set()
    for e in sim.society.tick_events:
        if e["type"] == "birth":
            parent_ids.add(e["agent_ids"][1])
            parent_ids.add(e["agent_ids"][2])

    parents = []
    for pid in parent_ids:
        agent = sim.society.get_by_id(pid)
        if agent is not None:
            parents.append(agent)

    females_elig, males_elig = sim.society.get_mating_eligible()
    eligible = females_elig + males_elig
    n_elig = len(eligible)

    row = {"year": year, "n_parents": len(parents), "n_eligible": n_elig}

    for trait in HERITABLE_TRAITS:
        if parents and eligible:
            parent_geno = [a.genotype.get(trait, getattr(a, trait)) for a in parents]
            elig_geno = [a.genotype.get(trait, getattr(a, trait)) for a in eligible]

            S = float(np.mean(parent_geno) - np.mean(elig_geno))
            S_norm = S / np.sqrt(n_elig) if n_elig > 0 else 0.0

            row[f"S_{trait}"] = S
            row[f"Sn_{trait}"] = float(S_norm)
        else:
            row[f"S_{trait}"] = None
            row[f"Sn_{trait}"] = None

    return row


def snapshot_trait_means(sim: Simulation) -> dict[str, float]:
    """Capture population mean genotype for all 35 traits at current tick."""
    living = sim.society.get_living()
    if not living:
        return {t: float("nan") for t in HERITABLE_TRAITS}
    means = {}
    for trait in HERITABLE_TRAITS:
        vals = [a.genotype.get(trait, getattr(a, trait)) for a in living]
        means[trait] = float(np.mean(vals))
    return means


def run_paired_seed(seed: int, n_years: int) -> dict:
    """Run one seed through BOTH scenarios. Returns paired results."""
    result = {"seed": seed}

    for scenario_name in SCENARIOS_TO_RUN:
        overrides = dict(SCENARIOS[scenario_name])
        overrides["carrying_capacity"] = 800  # explicit lock

        cfg = Config(seed=seed, years=n_years, population_size=500, **overrides)
        sim = Simulation(cfg)

        # Snapshot year-1 trait means (after first tick initializes everything)
        first_row = sim.tick()
        trait_means_yr1 = snapshot_trait_means(sim)
        sel_yr1 = compute_selection_differential(sim)

        metrics_rows = [first_row]
        selection_rows = [sel_yr1]

        for year in range(2, n_years + 1):
            row = sim.tick()
            sel = compute_selection_differential(sim)
            metrics_rows.append(row)
            selection_rows.append(sel)

            if sim.finished:
                break

        # Snapshot final trait means
        trait_means_final = snapshot_trait_means(sim)

        # Cumulative trait displacement: R_total = mean(yr_final) - mean(yr_1)
        displacement = {}
        for trait in HERITABLE_TRAITS:
            displacement[trait] = trait_means_final[trait] - trait_means_yr1[trait]

        # Tag all rows
        for r in metrics_rows:
            r["seed"] = seed
            r["scenario"] = scenario_name
        for r in selection_rows:
            r["seed"] = seed
            r["scenario"] = scenario_name

        result[scenario_name] = {
            "metrics": metrics_rows,
            "selection": selection_rows,
            "trait_means_yr1": trait_means_yr1,
            "trait_means_final": trait_means_final,
            "displacement": displacement,
            "final_pop": sim.society.population_size(),
            "final_year": sim.year,
        }

    return result


def paired_analysis(all_results: list[dict]) -> dict:
    """Compute paired-seed statistics across scenarios."""
    analysis = {"n_seeds": len(all_results), "traits": {}}

    for trait in HERITABLE_TRAITS:
        h2 = TRAIT_HERITABILITY.get(trait, 0.4)

        # Paired differences: displacement_A - displacement_B for each seed
        disp_A = []
        disp_B = []
        cum_S_A = []
        cum_S_B = []

        for r in all_results:
            dA = r["NO_INSTITUTIONS"]["displacement"][trait]
            dB = r["STRONG_STATE"]["displacement"][trait]
            disp_A.append(dA)
            disp_B.append(dB)

            # Cumulative mean S (normalized) per seed
            sels_A = r["NO_INSTITUTIONS"]["selection"]
            sels_B = r["STRONG_STATE"]["selection"]
            sA_vals = [s[f"Sn_{trait}"] for s in sels_A if s[f"Sn_{trait}"] is not None]
            sB_vals = [s[f"Sn_{trait}"] for s in sels_B if s[f"Sn_{trait}"] is not None]
            cum_S_A.append(np.mean(sA_vals) if sA_vals else 0.0)
            cum_S_B.append(np.mean(sB_vals) if sB_vals else 0.0)

        disp_A = np.array(disp_A)
        disp_B = np.array(disp_B)
        paired_diff_disp = disp_A - disp_B

        cum_S_A = np.array(cum_S_A)
        cum_S_B = np.array(cum_S_B)
        paired_diff_S = cum_S_A - cum_S_B

        # Paired t-tests
        if len(paired_diff_disp) > 1 and np.std(paired_diff_disp) > 0:
            t_disp, p_disp = stats.ttest_rel(disp_A, disp_B)
        else:
            t_disp, p_disp = 0.0, 1.0

        if len(paired_diff_S) > 1 and np.std(paired_diff_S) > 0:
            t_S, p_S = stats.ttest_rel(cum_S_A, cum_S_B)
        else:
            t_S, p_S = 0.0, 1.0

        # Effect size (paired Cohen's d)
        d_std = np.std(paired_diff_disp, ddof=1)
        cohens_d = float(np.mean(paired_diff_disp) / d_std) if d_std > 0 else 0.0

        analysis["traits"][trait] = {
            "displacement_A_mean": float(np.mean(disp_A)),
            "displacement_B_mean": float(np.mean(disp_B)),
            "paired_diff_mean": float(np.mean(paired_diff_disp)),
            "paired_diff_std": float(np.std(paired_diff_disp, ddof=1)),
            "t_displacement": float(t_disp),
            "p_displacement": float(p_disp),
            "cohens_d": cohens_d,
            "cum_Sn_A_mean": float(np.mean(cum_S_A)),
            "cum_Sn_B_mean": float(np.mean(cum_S_B)),
            "t_Sn": float(t_S),
            "p_Sn": float(p_S),
            "h2": h2,
        }

    return analysis


def print_highlight_paired(all_results: list[dict], year: int) -> None:
    """Print paired-seed comparison at a checkpoint year."""
    print(f"\n{'=' * 80}")
    print(f"  Year {year} | Paired-Seed S_norm Comparison")
    print(f"{'=' * 80}")
    print(
        f"  {'Trait':<30} {'Sn(A)':>10} {'Sn(B)':>10}"
        f" {'d(A-B)':>10} {'p_pair':>8} {'Sig':>5}"
    )
    print(f"  {'-' * 75}")

    for trait in SUBSTITUTION_TRAITS:
        col = f"Sn_{trait}"
        paired_A = []
        paired_B = []
        for r in all_results:
            sA = [s[col] for s in r["NO_INSTITUTIONS"]["selection"]
                  if s["year"] == year and s[col] is not None]
            sB = [s[col] for s in r["STRONG_STATE"]["selection"]
                  if s["year"] == year and s[col] is not None]
            # Only include seeds with data in BOTH scenarios (paired requirement)
            if sA and sB:
                paired_A.append(sA[0])
                paired_B.append(sB[0])

        if len(paired_A) >= 2:
            arr_A, arr_B = np.array(paired_A), np.array(paired_B)
            t, p = stats.ttest_rel(arr_A, arr_B)
            mean_A, mean_B = float(np.mean(arr_A)), float(np.mean(arr_B))
            delta = mean_A - mean_B
            sig = "***" if p < 0.001 else "**" if p < 0.01 else "*" if p < 0.05 else ""
        else:
            mean_A = mean_B = delta = float("nan")
            p = 1.0
            sig = ""

        print(
            f"  {trait:<30} {mean_A:>+10.6f} {mean_B:>+10.6f}"
            f" {delta:>+10.6f} {p:>8.4f} {sig:>5}"
        )

    print(f"{'=' * 80}\n")


def main() -> None:
    t0 = time.time()

    print("=" * 80)
    print("  500-YEAR DIVERGENCE v2: PAIRED-SEED + POP-NORMALIZED")
    print("  Protocol: Zenodo 19217024 | Critic fixes applied")
    print(f"  Seeds: {SEEDS[0]}-{SEEDS[-1]} ({N_SEEDS}) | Years: {N_YEARS}")
    print(f"  Design: Paired (same seed, both scenarios)")
    print(f"  carrying_capacity: 800 (locked both scenarios)")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    all_results = []
    all_metrics = []
    all_selection = []

    for i, seed in enumerate(SEEDS):
        print(f"\n--- Seed {seed} ({i + 1}/{N_SEEDS}) ---")

        result = run_paired_seed(seed, N_YEARS)
        all_results.append(result)

        for sc in SCENARIOS_TO_RUN:
            pop = result[sc]["final_pop"]
            d_coop = result[sc]["displacement"]["cooperation_propensity"]
            d_agg = result[sc]["displacement"]["aggression_propensity"]
            print(
                f"  {sc:20s}: pop={pop:>4}, "
                f"R_coop={d_coop:+.5f}, R_agg={d_agg:+.5f}"
            )
            all_metrics.extend(result[sc]["metrics"])
            all_selection.extend(result[sc]["selection"])

    # ── Paired analysis ────────────────────────────────────────────────
    print(f"\n{'=' * 80}")
    print(f"  PAIRED ANALYSIS: Cumulative Trait Displacement (R_total)")
    print(f"{'=' * 80}")

    analysis = paired_analysis(all_results)

    # Print displacement results sorted by significance
    print(
        f"\n  {'Trait':<35} {'R(A)':>9} {'R(B)':>9}"
        f" {'d(A-B)':>9} {'t':>7} {'p':>8} {'d_cohen':>7} {'Sig':>5}"
    )
    print(f"  {'-' * 90}")

    sorted_traits = sorted(
        analysis["traits"].items(), key=lambda x: x[1]["p_displacement"]
    )
    for trait, ta in sorted_traits:
        sig = "***" if ta["p_displacement"] < 0.001 else \
              "**" if ta["p_displacement"] < 0.01 else \
              "*" if ta["p_displacement"] < 0.05 else ""
        print(
            f"  {trait:<35} {ta['displacement_A_mean']:>+9.5f}"
            f" {ta['displacement_B_mean']:>+9.5f}"
            f" {ta['paired_diff_mean']:>+9.5f}"
            f" {ta['t_displacement']:>7.2f}"
            f" {ta['p_displacement']:>8.4f}"
            f" {ta['cohens_d']:>+7.2f}"
            f" {sig:>5}"
        )

    # Checkpoint highlights
    for checkpoint in range(HIGHLIGHT_INTERVAL, N_YEARS + 1, HIGHLIGHT_INTERVAL):
        print_highlight_paired(all_results, checkpoint)

    # ── Population comparison ──────────────────────────────────────────
    pop_A = [r["NO_INSTITUTIONS"]["final_pop"] for r in all_results]
    pop_B = [r["STRONG_STATE"]["final_pop"] for r in all_results]
    t_pop, p_pop = stats.ttest_rel(pop_A, pop_B)
    print(f"  Population at year 500: A={np.mean(pop_A):.0f} vs B={np.mean(pop_B):.0f}"
          f" (paired t={t_pop:.2f}, p={p_pop:.4f})")

    # ── Save outputs ───────────────────────────────────────────────────
    print(f"\nSaving to {OUTPUT_DIR}/ ...")

    pd.DataFrame(all_selection).to_csv(
        OUTPUT_DIR / "selection_matrix_full.csv", index=False
    )
    pd.DataFrame(all_metrics).to_csv(
        OUTPUT_DIR / "metrics_full.csv", index=False
    )

    # Displacement table
    disp_rows = []
    for r in all_results:
        seed = r["seed"]
        for sc in SCENARIOS_TO_RUN:
            row = {"seed": seed, "scenario": sc, "final_pop": r[sc]["final_pop"]}
            for trait in HERITABLE_TRAITS:
                row[f"yr1_{trait}"] = r[sc]["trait_means_yr1"][trait]
                row[f"yr500_{trait}"] = r[sc]["trait_means_final"][trait]
                row[f"disp_{trait}"] = r[sc]["displacement"][trait]
            disp_rows.append(row)
    pd.DataFrame(disp_rows).to_csv(
        OUTPUT_DIR / "trait_displacement.csv", index=False
    )

    # Analysis JSON for Critic
    analysis["population"] = {
        "A_mean": float(np.mean(pop_A)),
        "B_mean": float(np.mean(pop_B)),
        "t_paired": float(t_pop),
        "p_paired": float(p_pop),
    }
    analysis["metadata"] = {
        "protocol": "Zenodo 19217024",
        "design": "paired-seed",
        "n_seeds": N_SEEDS,
        "n_years": N_YEARS,
        "seeds": SEEDS,
        "carrying_capacity": 800,
        "normalization": "S / sqrt(N_eligible)",
        "primary_metric": "cumulative_trait_displacement",
        "timestamp": datetime.now().isoformat(),
    }
    with open(OUTPUT_DIR / "paired_analysis.json", "w") as f:
        json.dump(analysis, f, indent=2, default=str)

    # Critic validation bundle (checkpoint snapshots)
    validation_logs = []
    for checkpoint in range(HIGHLIGHT_INTERVAL, N_YEARS + 1, HIGHLIGHT_INTERVAL):
        vlog = {
            "checkpoint_year": checkpoint,
            "timestamp": datetime.now().isoformat(),
            "design": "paired-seed",
            "traits": {},
        }
        for trait in HERITABLE_TRAITS:
            col_raw = f"S_{trait}"
            col_norm = f"Sn_{trait}"
            pairs_raw = []
            pairs_norm = []
            for r in all_results:
                vA = [s[col_raw] for s in r["NO_INSTITUTIONS"]["selection"]
                      if s["year"] == checkpoint and s[col_raw] is not None]
                vB = [s[col_raw] for s in r["STRONG_STATE"]["selection"]
                      if s["year"] == checkpoint and s[col_raw] is not None]
                nA = [s[col_norm] for s in r["NO_INSTITUTIONS"]["selection"]
                      if s["year"] == checkpoint and s[col_norm] is not None]
                nB = [s[col_norm] for s in r["STRONG_STATE"]["selection"]
                      if s["year"] == checkpoint and s[col_norm] is not None]
                if vA and vB:
                    pairs_raw.append((vA[0], vB[0]))
                if nA and nB:
                    pairs_norm.append((nA[0], nB[0]))

            if len(pairs_raw) >= 2:
                arr_A = np.array([p[0] for p in pairs_raw])
                arr_B = np.array([p[1] for p in pairs_raw])
                t, p = stats.ttest_rel(arr_A, arr_B)
                vlog["traits"][trait] = {
                    "S_A_mean": float(np.mean(arr_A)),
                    "S_B_mean": float(np.mean(arr_B)),
                    "delta": float(np.mean(arr_A) - np.mean(arr_B)),
                    "t_paired": float(t),
                    "p_paired": float(p),
                }
        validation_logs.append(vlog)

    with open(OUTPUT_DIR / "critic_validation_bundle.json", "w") as f:
        json.dump(validation_logs, f, indent=2)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.0f}s ({elapsed / 60:.1f}m)")
    print(f"  selection_matrix_full.csv      S + Sn for 35 traits (paired)")
    print(f"  metrics_full.csv               ~130 metrics per tick")
    print(f"  trait_displacement.csv          R_total per seed per scenario")
    print(f"  paired_analysis.json           Paired t-tests + effect sizes")
    print(f"  critic_validation_bundle.json  Checkpoint logs for Critic")


if __name__ == "__main__":
    main()
