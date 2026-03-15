"""
Experiment runner — runs scenarios across multiple seeds, collects results.
"""

from __future__ import annotations
import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

from config import Config
from simulation import Simulation
from experiments.scenarios import SCENARIOS


class ExperimentRunner:
    def __init__(self, years: int = 200, population: int = 500,
                 output_root: Path | None = None):
        self.years = years
        self.population = population
        self.output_root = output_root or Path("outputs/reports")
        self.results: dict[str, dict] = {}  # scenario_name -> {seeds, metrics_dfs, summaries}

    def run_scenario(self, name: str, seeds: list[int] | None = None,
                     quiet: bool = False) -> dict:
        """Run a single scenario across multiple seeds. Returns results dict."""
        if name not in SCENARIOS:
            raise ValueError(f"Unknown scenario: {name}. Available: {list(SCENARIOS.keys())}")

        seeds = seeds or [42, 43, 44]
        overrides = SCENARIOS[name]
        run_dfs = []
        run_summaries = []

        for seed in seeds:
            cfg_kwargs = {
                **overrides,
                "seed": seed,
                "years": self.years,
                "population_size": self.population,
            }
            cfg = Config(**cfg_kwargs)
            sim = Simulation(cfg)

            if not quiet:
                print(f"  {name} seed={seed} ...", end=" ", flush=True)

            sim.run()
            df = sim.metrics.to_dataframe()
            df["seed"] = seed
            df["scenario"] = name
            run_dfs.append(df)

            # Summary stats from final state
            living = sim.society.get_living()
            summary = {
                "seed": seed,
                "scenario": name,
                "final_population": len(living),
                "total_births": int(df["births"].sum()),
                "total_deaths": int(df["deaths"].sum()),
                "total_conflicts": int(df["conflicts"].sum()),
                "avg_resource_gini": round(float(df["resource_gini"].mean()), 4),
                "avg_violence_rate": round(float(df["violence_rate"].mean()), 4),
                "avg_reproductive_skew": round(float(df["reproductive_skew"].mean()), 4),
                "avg_unmated_male_pct": round(float(df["unmated_male_pct"].mean()), 4),
                "avg_child_survival": round(float(df["child_survival_rate"].mean()), 4),
                "avg_aggression": round(float(df["avg_aggression"].mean()), 4),
                "avg_cooperation": round(float(df["avg_cooperation"].mean()), 4),
                "equilibrium_reached": bool(df.get("equilibrium", pd.Series([False])).any()),
            }
            run_summaries.append(summary)

            if not quiet:
                print(f"pop={len(living)}, gini={summary['avg_resource_gini']:.3f}, "
                      f"violence={summary['avg_violence_rate']:.3f}")

        result = {
            "scenario": name,
            "seeds": seeds,
            "config_overrides": overrides,
            "metrics_df": pd.concat(run_dfs, ignore_index=True),
            "summaries": run_summaries,
        }
        self.results[name] = result
        return result

    def run_all_scenarios(self, seeds: list[int] | None = None,
                          quiet: bool = False) -> dict[str, dict]:
        """Run all defined scenarios."""
        seeds = seeds or [42, 43, 44]
        print(f"Running {len(SCENARIOS)} scenarios x {len(seeds)} seeds "
              f"({self.years} years, pop {self.population})")
        print("=" * 60)

        for name in SCENARIOS:
            print(f"\n[{name}]")
            self.run_scenario(name, seeds, quiet=quiet)

        print("\n" + "=" * 60)
        print("All scenarios complete.")
        return self.results

    def run_parameter_sweep(self, param_name: str, values: list,
                            seeds: list[int] | None = None,
                            quiet: bool = False) -> dict:
        """Sweep a single parameter across values, holding all else at baseline."""
        seeds = seeds or [42, 43, 44]
        sweep_results = {}

        print(f"Parameter sweep: {param_name} = {values}")
        print(f"Seeds: {seeds}, {self.years} years, pop {self.population}")
        print("=" * 60)

        for val in values:
            label = f"{param_name}={val}"
            if not quiet:
                print(f"\n[{label}]")

            run_dfs = []
            for seed in seeds:
                cfg = Config(
                    seed=seed,
                    years=self.years,
                    population_size=self.population,
                    **{param_name: val},
                )
                sim = Simulation(cfg)
                if not quiet:
                    print(f"  seed={seed} ...", end=" ", flush=True)
                sim.run()
                df = sim.metrics.to_dataframe()
                df["seed"] = seed
                df["param_value"] = val
                run_dfs.append(df)
                if not quiet:
                    pop = len(sim.society.get_living())
                    print(f"pop={pop}")

            sweep_results[val] = pd.concat(run_dfs, ignore_index=True)

        return {"param": param_name, "values": values, "seeds": seeds,
                "results": sweep_results}

    def save_results(self, tag: str = "") -> Path:
        """Save all collected results to disk."""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        label = f"{ts}_{tag}" if tag else ts
        report_dir = self.output_root / label
        report_dir.mkdir(parents=True, exist_ok=True)

        for name, result in self.results.items():
            scenario_dir = report_dir / name
            scenario_dir.mkdir(exist_ok=True)

            # Metrics CSV (all seeds combined)
            result["metrics_df"].to_csv(scenario_dir / "metrics.csv", index=False)

            # Per-seed summaries
            with open(scenario_dir / "summaries.json", "w") as f:
                json.dump(result["summaries"], f, indent=2)

        # Cross-scenario comparison CSV
        comparison = self._build_comparison_table()
        if comparison is not None:
            comparison.to_csv(report_dir / "scenario_comparison.csv", index=False)

        print(f"Results saved to: {report_dir}")
        return report_dir

    def _build_comparison_table(self) -> pd.DataFrame | None:
        """Build a summary table comparing all scenarios (mean across seeds)."""
        if not self.results:
            return None

        rows = []
        for name, result in self.results.items():
            summaries = result["summaries"]
            if not summaries:
                continue

            # Average across seeds
            avg = {}
            keys = [k for k in summaries[0] if isinstance(summaries[0][k], (int, float))]
            for k in keys:
                vals = [s[k] for s in summaries]
                avg[k] = round(sum(vals) / len(vals), 4)
            avg["scenario"] = name
            avg["n_seeds"] = len(summaries)
            rows.append(avg)

        return pd.DataFrame(rows)

    def compare_to_baseline(self, baseline: str = "FREE_COMPETITION") -> pd.DataFrame | None:
        """Compare all scenarios to baseline, showing % difference."""
        comparison = self._build_comparison_table()
        if comparison is None or baseline not in self.results:
            return None

        baseline_row = comparison[comparison["scenario"] == baseline].iloc[0]
        numeric_cols = comparison.select_dtypes(include="number").columns

        diff_rows = []
        for _, row in comparison.iterrows():
            if row["scenario"] == baseline:
                continue
            diff = {"scenario": row["scenario"]}
            for col in numeric_cols:
                base_val = baseline_row[col]
                if base_val != 0:
                    diff[col] = round((row[col] - base_val) / abs(base_val) * 100, 1)
                else:
                    diff[col] = 0.0
            diff_rows.append(diff)

        return pd.DataFrame(diff_rows)
