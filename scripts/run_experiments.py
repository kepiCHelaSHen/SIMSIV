"""
SIMSIV — Scenario Experiment Suite
Runs named scenarios against the calibrated best_config baseline.

Usage:
    python scripts/run_experiments.py
    python scripts/run_experiments.py --seeds 10 --years 500
    python scripts/run_experiments.py --scenarios FREE_COMPETITION STRONG_STATE EMERGENT_INSTITUTIONS --seeds 10 --years 500
    python scripts/run_experiments.py --scenarios ENFORCED_MONOGAMY --seeds 3 --years 200
    python scripts/run_experiments.py --quick   (3 seeds, 100yr, fast check)
    python scripts/run_experiments.py --list    (show available scenario names)
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from simulation import Simulation
from experiments.scenarios import SCENARIOS

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT        = Path(__file__).parent.parent
BEST_CONFIG = ROOT / "autosim" / "best_config.yaml"
OUTPUT_ROOT = ROOT / "outputs" / "experiments"


def load_best_params() -> dict:
    with open(BEST_CONFIG) as f:
        data = yaml.safe_load(f)
    return data["parameters"]


def build_config(base_params: dict, overrides: dict, seed: int,
                 years: int, pop: int) -> Config:
    cfg_fields = set(Config.__dataclass_fields__.keys())
    kwargs = {k: v for k, v in base_params.items() if k in cfg_fields}
    for k, v in overrides.items():
        if k in cfg_fields:
            kwargs[k] = v
    kwargs["seed"]            = seed
    kwargs["years"]           = years
    kwargs["population_size"] = pop
    return Config(**kwargs)


def extract_summary(rows: list[dict], sim: Simulation) -> dict:
    df      = pd.DataFrame(rows)
    window  = min(30, len(df))
    last    = df.tail(window)
    living  = sim.society.get_living()

    def _mean(col):
        return float(last[col].mean()) if col in last.columns else float("nan")

    def _sum(col):
        return int(df[col].sum()) if col in df.columns else 0

    vio_deaths  = _sum("violence_deaths")
    male_deaths = _sum("male_deaths")
    births      = _sum("births")
    child_deaths= _sum("childhood_deaths")
    dissolved   = _sum("bonds_dissolved")
    formed      = _sum("bonds_formed")

    return {
        "final_population":      len(living),
        "total_births":          _sum("births"),
        "total_deaths":          _sum("deaths"),
        "total_conflicts":       _sum("conflicts"),
        "resource_gini":         _mean("resource_gini"),
        "reproductive_skew":     _mean("reproductive_skew"),
        "violence_rate":         _mean("violence_rate"),
        "violence_death_frac":   vio_deaths / max(1, male_deaths),
        "pair_bonded_pct":       _mean("pair_bonded_pct"),
        "unmated_male_pct":      _mean("unmated_male_pct"),
        "avg_lifetime_births":   _mean("avg_lifetime_births"),
        "child_survival":        1.0 - child_deaths / max(1, births),
        "bond_dissolution":      dissolved / max(1, formed),
        "avg_lifespan":          _mean("avg_lifespan"),
        "pop_growth_rate":       _mean("pop_growth_rate"),
        "avg_cooperation":       _mean("avg_cooperation"),
        "avg_aggression":        _mean("avg_aggression"),
        "avg_intelligence":      _mean("avg_intelligence"),
        "law_strength":          _mean("law_strength"),
        "civilization_stability":_mean("civilization_stability"),
        "social_cohesion":       _mean("social_cohesion"),
    }


def run_scenario(name: str, base_params: dict, overrides: dict,
                 seeds: list[int], years: int, pop: int) -> dict:
    seed_results = []

    for seed in seeds:
        t0  = time.time()
        cfg = build_config(base_params, overrides, seed, years, pop)
        sim = Simulation(cfg)
        rows = [sim.tick() for _ in range(years)]
        elapsed = time.time() - t0

        summary          = extract_summary(rows, sim)
        summary["seed"]  = seed
        summary["elapsed"] = round(elapsed, 1)
        seed_results.append(summary)

        survived = summary["final_population"] >= 20
        print(f"    seed={seed:<6} pop={summary['final_population']:>4}  "
              f"gini={summary['resource_gini']:.3f}  "
              f"viol={summary['violence_rate']:.3f}  "
              f"coop={summary['avg_cooperation']:.3f}  "
              f"{elapsed:.1f}s  {'OK' if survived else 'COLLAPSED'}")

    numeric_keys = [k for k in seed_results[0]
                    if isinstance(seed_results[0][k], (int, float))
                    and k not in ("seed", "elapsed")]
    agg = {}
    for k in numeric_keys:
        vals = [r[k] for r in seed_results
                if not (isinstance(r[k], float) and np.isnan(r[k]))]
        agg[k]          = float(np.mean(vals)) if vals else float("nan")
        agg[f"{k}_std"] = float(np.std(vals))  if vals else float("nan")

    agg["n_survived"] = sum(1 for r in seed_results
                            if r["final_population"] >= 20)
    agg["n_seeds"]    = len(seed_results)

    return {"scenario": name, "overrides": overrides,
            "seeds": seeds, "agg": agg, "per_seed": seed_results}


def print_comparison_table(all_results: dict[str, dict],
                            baseline: str = "FREE_COMPETITION"):
    if baseline not in all_results:
        baseline = next(iter(all_results))   # fallback to first scenario

    base      = all_results[baseline]["agg"]
    scenarios = list(all_results.keys())
    col_w     = 18

    header = f"  {'Metric':<28}"
    for s in scenarios:
        label = s.replace("_", " ")[:col_w]
        header += f"  {label:>{col_w}}"
    print(header)
    print("  " + "-" * (28 + (col_w + 2) * len(scenarios)))

    DISPLAY = [
        ("final_population",    "Final Population",  "{:.0f}"),
        ("resource_gini",       "Resource Gini",     "{:.3f}"),
        ("violence_rate",       "Violence Rate",     "{:.3f}"),
        ("violence_death_frac", "Violence Deaths",   "{:.1%}"),
        ("pair_bonded_pct",     "Bonded %",          "{:.1%}"),
        ("unmated_male_pct",    "Unmated Males",     "{:.1%}"),
        ("avg_lifetime_births", "Lifetime Births",   "{:.2f}"),
        ("child_survival",      "Child Survival",    "{:.1%}"),
        ("reproductive_skew",   "Repro Skew",        "{:.3f}"),
        ("avg_cooperation",     "Cooperation",       "{:.3f}"),
        ("avg_aggression",      "Aggression",        "{:.3f}"),
        ("avg_intelligence",    "Intelligence",      "{:.3f}"),
        ("avg_lifespan",        "Avg Lifespan",      "{:.1f}"),
        ("law_strength",        "Law Strength",      "{:.3f}"),
        ("pop_growth_rate",     "Pop Growth/yr",     "{:+.4f}"),
        ("bond_dissolution",    "Bond Dissolution",  "{:.3f}"),
    ]

    for col, label, fmt in DISPLAY:
        row      = f"  {label:<28}"
        base_val = base.get(col, float("nan"))
        for s in scenarios:
            val = all_results[s]["agg"].get(col, float("nan"))
            if isinstance(val, float) and np.isnan(val):
                cell = "N/A"
            else:
                try:
                    cell = fmt.format(val)
                except Exception:
                    cell = str(round(val, 3))
                if s != baseline and not (isinstance(base_val, float) and
                                          np.isnan(base_val)) and base_val != 0:
                    pct = (val - base_val) / abs(base_val) * 100
                    if abs(pct) >= 5:
                        cell += f" {'▲' if pct > 0 else '▼'}{abs(pct):.0f}%"
            row += f"  {cell:>{col_w}}"
        print(row)

    print()
    print("  (▲/▼ = % change vs baseline, shown when |change| ≥ 5%)")


def save_results(all_results: dict[str, dict], output_dir: Path):
    output_dir.mkdir(parents=True, exist_ok=True)

    for name, result in all_results.items():
        d = output_dir / name
        d.mkdir(exist_ok=True)
        with open(d / "per_seed.json", "w") as f:
            json.dump(result["per_seed"], f, indent=2, default=str)
        with open(d / "aggregate.json", "w") as f:
            json.dump(result["agg"], f, indent=2, default=str)

    rows = [{"scenario": n, **r["agg"]} for n, r in all_results.items()]
    pd.DataFrame(rows).to_csv(output_dir / "comparison.csv", index=False)

    report = {
        "timestamp": datetime.now().isoformat(),
        "scenarios": list(all_results.keys()),
        "results": {
            name: {"overrides": r["overrides"], "seeds": r["seeds"],
                   "aggregate": r["agg"]}
            for name, r in all_results.items()
        },
    }
    with open(output_dir / "full_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)

    print(f"\n  Results saved to: {output_dir}")
    print(f"    comparison.csv      ← flat table, all scenarios")
    print(f"    full_report.json    ← complete data")
    print(f"    <scenario>/         ← per-scenario detail")


def main():
    parser = argparse.ArgumentParser(description="SIMSIV Scenario Experiments")
    parser.add_argument("--scenarios", nargs="+", default=None,
                        help="Scenario names to run (default: all). "
                             "E.g. --scenarios FREE_COMPETITION STRONG_STATE")
    parser.add_argument("--seeds",    type=int, default=5,
                        help="Seeds per scenario (default: 5)")
    parser.add_argument("--years",    type=int, default=200,
                        help="Simulation years (default: 200)")
    parser.add_argument("--pop",      type=int, default=500,
                        help="Population size (default: 500)")
    parser.add_argument("--quick",    action="store_true",
                        help="Quick mode: 3 seeds × 100 years")
    parser.add_argument("--no-save",  action="store_true",
                        help="Skip saving results to disk")
    parser.add_argument("--list",     action="store_true",
                        help="List available scenario names and exit")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable scenarios:")
        for name, overrides in SCENARIOS.items():
            print(f"  {name}")
            for k, v in overrides.items():
                print(f"    {k} = {v}")
        return

    if args.quick:
        args.seeds = 3
        args.years = 100

    # Validate scenario names
    if args.scenarios:
        invalid = [s for s in args.scenarios if s not in SCENARIOS]
        if invalid:
            print(f"ERROR: Unknown scenario(s): {invalid}")
            print(f"Available: {list(SCENARIOS.keys())}")
            sys.exit(1)
        scenarios_to_run = {s: SCENARIOS[s] for s in args.scenarios}
    else:
        scenarios_to_run = SCENARIOS

    # Seed pool — avoids autosim training seeds {42, 137}
    seed_pool = [1001, 2002, 3003, 4004, 5005, 6006, 7007, 8008, 9009, 1337,
                 2468, 3579, 4680, 5791, 6802, 7913, 8024, 9135, 1246, 2357]
    seeds = seed_pool[:args.seeds]

    base_params = load_best_params()

    print("=" * 72)
    print("  SIMSIV — Scenario Experiment Suite")
    print("=" * 72)
    print(f"  Scenarios:  {len(scenarios_to_run)}")
    print(f"  Seeds:      {args.seeds}  {seeds}")
    print(f"  Years:      {args.years}")
    print(f"  Population: {args.pop}")
    print(f"  Base:       best_config.yaml (autosim score: 1.0000)")
    print()

    all_results: dict[str, dict] = {}
    t_total = time.time()

    for i, (name, overrides) in enumerate(scenarios_to_run.items(), 1):
        print(f"[{i}/{len(scenarios_to_run)}] {name}")
        for k, v in overrides.items():
            print(f"    override: {k} = {v}")
        result = run_scenario(name, base_params, overrides,
                              seeds, args.years, args.pop)
        all_results[name] = result
        print(f"    → {result['agg']['n_survived']}/{args.seeds} survived  "
              f"gini={result['agg']['resource_gini']:.3f}  "
              f"violence={result['agg']['violence_rate']:.3f}  "
              f"coop={result['agg']['avg_cooperation']:.3f}")
        print()

    total_elapsed = (time.time() - t_total) / 60
    print(f"Total elapsed: {total_elapsed:.1f} minutes")
    print()

    print("=" * 72)
    print("  SCENARIO COMPARISON (mean across seeds)")
    print("=" * 72)
    print_comparison_table(all_results)

    if not args.no_save:
        ts        = datetime.now().strftime("%Y%m%d_%H%M%S")
        tag       = "_".join(list(scenarios_to_run.keys())[:3]) \
                    if args.scenarios else "all_scenarios"
        out_dir   = OUTPUT_ROOT / f"{ts}_{tag}_s{args.seeds}_y{args.years}"
        save_results(all_results, out_dir)


if __name__ == "__main__":
    main()
