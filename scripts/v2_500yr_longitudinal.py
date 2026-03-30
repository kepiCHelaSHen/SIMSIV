#!/usr/bin/env python
"""
500-Year Evolutionary Divergence Experiment
Protocol: Zenodo 19217024 (Stress Test Framework)
Hypothesis: 'Institutional Substitution' via Selection Gradients

Computes Selection Differential S_T for all 35 heritable traits across:
  - Scenario A (Control): NO_INSTITUTIONS (law_strength=0.0)
  - Scenario B (Treatment): STRONG_STATE (law_strength=0.8)

10 seeds per scenario, 500 years each.

Selection Differential: S_T = Mean(Parents.genotype[T]) - Mean(Eligible.genotype[T])
Response to Selection: R_T = h^2_T * S_T  (Breeder's Equation)

Outputs:
  selection_matrix_full.csv     - S for 35 traits x seeds x scenarios x years
  selection_matrix_10yr.csv     - Mean S at 10-year intervals
  metrics_full.csv              - Standard ~130 metrics per tick
  critic_validation_bundle.json - All checkpoint logs for Critic (Gemini) handoff
  critic_checkpoint_NNNN.json   - Individual 100-year checkpoint logs
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import Config
from experiments.scenarios import SCENARIOS
from models.agent import HERITABLE_TRAITS, TRAIT_HERITABILITY
from simulation import Simulation

# ── Experiment parameters ──────────────────────────────────────────────
N_SEEDS = 10
N_YEARS = 500
SEEDS = list(range(42, 42 + N_SEEDS))
SCENARIOS_TO_RUN = ["NO_INSTITUTIONS", "STRONG_STATE"]
SELECTION_LOG_INTERVAL = 10
HIGHLIGHT_INTERVAL = 100
OUTPUT_DIR = Path("outputs/experiments/v2_500yr_divergence")

# Institutional-substitution hypothesis target traits
SUBSTITUTION_TRAITS = [
    "cooperation_propensity",
    "impulse_control",
    "empathy_capacity",
    "aggression_propensity",
    "conformity_bias",
    "group_loyalty",
]


def compute_selection_differential(sim: Simulation) -> dict:
    """Compute S_T for all 35 heritable traits using genotype values.

    S_T = Mean(Parents.genotype[T]) - Mean(Eligible.genotype[T])

    Parents identified from birth events in tick_events (set during
    reproduction, available until next tick clears them).
    """
    year = sim.year

    # Extract unique parent IDs from this tick's birth events
    parent_ids: set[int] = set()
    for e in sim.society.tick_events:
        if e["type"] == "birth":
            # agent_ids = [child_id, mother_id, father_id]
            parent_ids.add(e["agent_ids"][1])
            parent_ids.add(e["agent_ids"][2])

    # Look up parent agents (get_by_id returns even dead-this-tick agents)
    parents = []
    for pid in parent_ids:
        agent = sim.society.get_by_id(pid)
        if agent is not None:
            parents.append(agent)

    # Mating-eligible population (baseline for selection differential)
    females_elig, males_elig = sim.society.get_mating_eligible()
    eligible = females_elig + males_elig

    row = {"year": year, "n_parents": len(parents), "n_eligible": len(eligible)}

    for trait in HERITABLE_TRAITS:
        if parents and eligible:
            # Use genotype (genetic value at birth), fallback to phenotype for Gen 0
            parent_geno = [a.genotype.get(trait, getattr(a, trait)) for a in parents]
            elig_geno = [a.genotype.get(trait, getattr(a, trait)) for a in eligible]

            S = float(np.mean(parent_geno) - np.mean(elig_geno))
            h2 = TRAIT_HERITABILITY.get(trait, 0.4)
            R = h2 * S

            row[f"S_{trait}"] = S
            row[f"R_{trait}"] = R
            row[f"mu_parent_{trait}"] = float(np.mean(parent_geno))
            row[f"mu_eligible_{trait}"] = float(np.mean(elig_geno))
        else:
            row[f"S_{trait}"] = None
            row[f"R_{trait}"] = None
            row[f"mu_parent_{trait}"] = None
            row[f"mu_eligible_{trait}"] = None

    return row


def run_scenario(scenario_name: str, seeds: list[int], n_years: int) -> tuple[list, list]:
    """Run one scenario across seeds. Returns (metrics_rows, selection_rows)."""
    overrides = SCENARIOS[scenario_name]
    all_metrics: list[dict] = []
    all_selection: list[dict] = []

    for i, seed in enumerate(seeds):
        print(f"\n  Seed {seed} ({i + 1}/{len(seeds)})")

        cfg = Config(seed=seed, years=n_years, population_size=500, **overrides)
        sim = Simulation(cfg)

        for year in range(1, n_years + 1):
            row = sim.tick()
            row["seed"] = seed
            row["scenario"] = scenario_name

            # Selection differential — computed from tick_events before next tick clears them
            sel = compute_selection_differential(sim)
            sel["seed"] = seed
            sel["scenario"] = scenario_name

            all_metrics.append(row)
            all_selection.append(sel)

            if year % 100 == 0:
                pop = row.get("population", "?")
                S_coop = sel.get("S_cooperation_propensity") or 0.0
                S_agg = sel.get("S_aggression_propensity") or 0.0
                print(
                    f"    Year {year}: pop={pop}, "
                    f"S_coop={S_coop:+.5f}, S_agg={S_agg:+.5f}"
                )

            if sim.finished:
                print(f"    Ended at year {year} (pop={sim.society.population_size()})")
                break

    return all_metrics, all_selection


def generate_validation_log(
    sel_a: list[dict], sel_b: list[dict], year: int
) -> dict:
    """Build a Critic-handoff validation log for one checkpoint year."""
    log = {
        "checkpoint_year": year,
        "timestamp": datetime.now().isoformat(),
        "protocol": "Zenodo 19217024",
        "hypothesis": "Institutional Substitution",
        "scenarios": {"A_NO_INSTITUTIONS": {}, "B_STRONG_STATE": {}},
        "divergence": {},
        "verdict": {},
    }

    for trait in HERITABLE_TRAITS:
        col = f"S_{trait}"
        h2 = TRAIT_HERITABILITY.get(trait, 0.4)

        vals_a = [r[col] for r in sel_a if r["year"] == year and r[col] is not None]
        vals_b = [r[col] for r in sel_b if r["year"] == year and r[col] is not None]

        if vals_a:
            mean_a = float(np.mean(vals_a))
            log["scenarios"]["A_NO_INSTITUTIONS"][trait] = {
                "S_mean": mean_a,
                "S_std": float(np.std(vals_a)),
                "S_positive_frac": float(np.mean([1 if v > 0 else 0 for v in vals_a])),
                "R_predicted": mean_a * h2,
            }

        if vals_b:
            mean_b = float(np.mean(vals_b))
            log["scenarios"]["B_STRONG_STATE"][trait] = {
                "S_mean": mean_b,
                "S_std": float(np.std(vals_b)),
                "S_positive_frac": float(np.mean([1 if v > 0 else 0 for v in vals_b])),
                "R_predicted": mean_b * h2,
            }

        if vals_a and vals_b:
            delta = float(np.mean(vals_a) - np.mean(vals_b))
            log["divergence"][trait] = {
                "delta_S": delta,
                "direction": "A > B" if delta > 0 else "B > A",
                "magnitude": abs(delta),
            }

    # Verdict on substitution-hypothesis target traits
    for trait in SUBSTITUTION_TRAITS:
        if trait not in log["divergence"]:
            continue
        d = log["divergence"][trait]
        # Without institutions, agents must self-organise: expect stronger
        # selection on prosocial traits (A > B).  For aggression the
        # prediction is the same — violence is costlier when the state
        # doesn't punish rivals for you, so aggression is selected harder.
        expected = "A > B"
        log["verdict"][trait] = {
            "expected": expected,
            "observed": d["direction"],
            "consistent": d["direction"] == expected,
            "delta_S": d["delta_S"],
        }

    return log


def print_highlight(sel_a: list[dict], sel_b: list[dict], year: int) -> None:
    """Console comparison of substitution-target traits at a checkpoint."""
    print(f"\n{'=' * 80}")
    print(f"  Year {year} | S_cooperation (A vs B) | S_aggression (A vs B)")
    print(f"{'=' * 80}")
    print(
        f"  {'Trait':<30} {'S(A:NoInst)':>12} {'S(B:State)':>12}"
        f" {'delta(A-B)':>10} {'Signal':>8}"
    )
    print(f"  {'-' * 72}")

    for trait in SUBSTITUTION_TRAITS:
        col = f"S_{trait}"
        vals_a = [r[col] for r in sel_a if r["year"] == year and r[col] is not None]
        vals_b = [r[col] for r in sel_b if r["year"] == year and r[col] is not None]

        mean_a = float(np.mean(vals_a)) if vals_a else float("nan")
        mean_b = float(np.mean(vals_b)) if vals_b else float("nan")
        delta = mean_a - mean_b if vals_a and vals_b else float("nan")

        if np.isnan(delta):
            signal = "NO DATA"
        elif delta > 0.001:
            signal = "SUB"
        elif delta < -0.001:
            signal = "FAIL"
        else:
            signal = "FLAT"

        print(
            f"  {trait:<30} {mean_a:>+12.5f} {mean_b:>+12.5f}"
            f" {delta:>+10.5f} {signal:>8}"
        )

    print(f"{'=' * 80}\n")


def main() -> None:
    t0 = time.time()

    print("=" * 80)
    print("  500-YEAR EVOLUTIONARY DIVERGENCE EXPERIMENT")
    print("  Protocol: Zenodo 19217024 | Hypothesis: Institutional Substitution")
    print(f"  Seeds: {N_SEEDS} | Years: {N_YEARS} | Traits: {len(HERITABLE_TRAITS)}")
    print(f"  Scenarios: {', '.join(SCENARIOS_TO_RUN)}")
    print("=" * 80)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n{'-' * 40}")
    print(f"  SCENARIO A: NO_INSTITUTIONS (law=0.0)")
    print(f"{'-' * 40}")
    metrics_a, selection_a = run_scenario("NO_INSTITUTIONS", SEEDS, N_YEARS)

    print(f"\n{'-' * 40}")
    print(f"  SCENARIO B: STRONG_STATE (law=0.8)")
    print(f"{'-' * 40}")
    metrics_b, selection_b = run_scenario("STRONG_STATE", SEEDS, N_YEARS)

    # ── Post-hoc analysis ──────────────────────────────────────────────
    print(f"\n{'=' * 80}")
    print(f"  POST-HOC: Selection Gradient Comparison")
    print(f"{'=' * 80}")

    validation_logs = []
    for checkpoint in range(HIGHLIGHT_INTERVAL, N_YEARS + 1, HIGHLIGHT_INTERVAL):
        print_highlight(selection_a, selection_b, checkpoint)
        vlog = generate_validation_log(selection_a, selection_b, checkpoint)
        validation_logs.append(vlog)

        vlog_path = OUTPUT_DIR / f"critic_checkpoint_{checkpoint:04d}.json"
        with open(vlog_path, "w") as f:
            json.dump(vlog, f, indent=2)

    # ── Save datasets ──────────────────────────────────────────────────
    print(f"\nSaving to {OUTPUT_DIR}/ ...")

    # Full selection matrix (every tick)
    df_sel = pd.DataFrame(selection_a + selection_b)
    df_sel.to_csv(OUTPUT_DIR / "selection_matrix_full.csv", index=False)

    # Full simulation metrics
    df_met = pd.DataFrame(metrics_a + metrics_b)
    df_met.to_csv(OUTPUT_DIR / "metrics_full.csv", index=False)

    # 10-year summary (mean S across seeds)
    sel_summary = []
    for scenario_name, sel_data in [
        ("NO_INSTITUTIONS", selection_a),
        ("STRONG_STATE", selection_b),
    ]:
        df_s = pd.DataFrame(sel_data)
        for yr in range(SELECTION_LOG_INTERVAL, N_YEARS + 1, SELECTION_LOG_INTERVAL):
            chunk = df_s[df_s["year"] == yr]
            if chunk.empty:
                continue
            entry: dict = {"scenario": scenario_name, "year": yr}
            for trait in HERITABLE_TRAITS:
                col = f"S_{trait}"
                vals = chunk[col].dropna()
                if len(vals) > 0:
                    entry[f"S_{trait}_mean"] = float(vals.mean())
                    entry[f"S_{trait}_std"] = float(vals.std())
            sel_summary.append(entry)

    pd.DataFrame(sel_summary).to_csv(
        OUTPUT_DIR / "selection_matrix_10yr.csv", index=False
    )

    # Critic validation bundle
    with open(OUTPUT_DIR / "critic_validation_bundle.json", "w") as f:
        json.dump(validation_logs, f, indent=2)

    elapsed = time.time() - t0
    n_traits = len(HERITABLE_TRAITS)
    print(f"\nDone in {elapsed:.0f}s ({elapsed / 60:.1f}m)")
    print(f"  selection_matrix_full.csv     {n_traits} traits x {N_SEEDS} seeds x 2 scenarios x {N_YEARS}yr")
    print(f"  selection_matrix_10yr.csv     Mean S at 10-year intervals")
    print(f"  metrics_full.csv              ~130 metrics per tick")
    print(f"  critic_validation_bundle.json All checkpoint logs for Critic handoff")


if __name__ == "__main__":
    main()
