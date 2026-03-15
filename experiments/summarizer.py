"""
Narrative summarizer and integrity checker for experiment results.
"""

from __future__ import annotations
from pathlib import Path

import numpy as np
import pandas as pd


DISCLAIMER = (
    "SIMSIV is a stylized model. Results reflect the consequences of the "
    "implemented rules, not claims about human societies. All metrics are "
    "artifacts of simplification. Do not over-interpret."
)


class SimIntegrityChecker:
    """Flag suspicious patterns that suggest model artifacts."""

    def check_all(self, metrics_df: pd.DataFrame, all_results: dict | None = None) -> list[str]:
        warnings = []
        warnings.extend(self.check_population_stability(metrics_df))
        warnings.extend(self.check_runaway_inequality(metrics_df))
        warnings.extend(self.check_model_collapse(metrics_df))
        warnings.extend(self.check_flat_metrics(metrics_df))
        if all_results:
            warnings.extend(self.check_seed_sensitivity(all_results))
        return warnings

    def check_population_stability(self, df: pd.DataFrame) -> list[str]:
        warnings = []
        min_pop = df["population"].min()
        if min_pop < 50:
            warnings.append(
                f"LOW POPULATION: dropped to {int(min_pop)} — results may reflect "
                f"extinction dynamics rather than social equilibrium."
            )
        return warnings

    def check_runaway_inequality(self, df: pd.DataFrame) -> list[str]:
        warnings = []
        max_gini = df["resource_gini"].max()
        if max_gini > 0.95:
            warnings.append(
                f"EXTREME INEQUALITY: resource Gini reached {max_gini:.3f}. "
                f"May indicate a model artifact (winner-take-all feedback loop)."
            )
        return warnings

    def check_model_collapse(self, df: pd.DataFrame) -> list[str]:
        warnings = []
        if df["population"].iloc[-1] == 0:
            warnings.append("MODEL COLLAPSE: population reached 0 (extinction).")
        return warnings

    def check_flat_metrics(self, df: pd.DataFrame) -> list[str]:
        """Warn if key metrics show suspiciously zero variance."""
        warnings = []
        if len(df) < 20:
            return warnings
        for col in ["resource_gini", "violence_rate", "reproductive_skew"]:
            if col in df.columns and df[col].std() < 0.001:
                warnings.append(
                    f"FLAT METRIC: {col} has near-zero variance ({df[col].std():.4f}). "
                    f"May indicate the metric is not sensitive to dynamics."
                )
        return warnings

    def check_seed_sensitivity(self, all_results: dict) -> list[str]:
        """Warn if results vary wildly across seeds within a scenario."""
        warnings = []
        for name, result in all_results.items():
            summaries = result.get("summaries", [])
            if len(summaries) < 2:
                continue
            for metric in ["avg_violence_rate", "avg_resource_gini", "final_population"]:
                vals = [s[metric] for s in summaries if metric in s]
                if not vals:
                    continue
                mean_val = np.mean(vals)
                std_val = np.std(vals)
                if mean_val > 0 and std_val / mean_val > 0.2:
                    warnings.append(
                        f"SEED SENSITIVE: {name}.{metric} has high variance "
                        f"(mean={mean_val:.3f}, std={std_val:.3f}, cv={std_val/mean_val:.1%}). "
                        f"Results may not be robust — use more seeds."
                    )
        return warnings


class NarrativeSummarizer:
    """Generate human-readable summaries of simulation results."""

    def __init__(self):
        self.checker = SimIntegrityChecker()

    def generate_run_summary(self, metrics_df: pd.DataFrame, config_name: str) -> str:
        """Narrative summary for a single scenario (averaged across seeds)."""
        lines = [f"## {config_name}\n"]

        # Group by year, average across seeds
        if "seed" in metrics_df.columns:
            df = metrics_df.groupby("year").mean(numeric_only=True).reset_index()
        else:
            df = metrics_df

        n_years = len(df)
        final = df.iloc[-1]
        early = df.iloc[:n_years // 5] if n_years >= 10 else df.iloc[:3]
        late = df.iloc[-n_years // 5:] if n_years >= 10 else df.iloc[-3:]

        # Population trajectory
        pop_start = df["population"].iloc[0]
        pop_end = final["population"]
        pop_peak = df["population"].max()
        pop_min = df["population"].min()
        growth = (pop_end - pop_start) / pop_start * 100 if pop_start > 0 else 0

        lines.append(f"**Population**: {int(pop_start)} -> {int(pop_end)} "
                      f"({growth:+.0f}%), peak {int(pop_peak)}, trough {int(pop_min)}")

        # Violence
        avg_violence_early = early["violence_rate"].mean()
        avg_violence_late = late["violence_rate"].mean()
        violence_trend = "declining" if avg_violence_late < avg_violence_early * 0.8 else \
                         "rising" if avg_violence_late > avg_violence_early * 1.2 else "stable"
        lines.append(f"**Violence**: {violence_trend} "
                      f"(early {avg_violence_early:.3f}, late {avg_violence_late:.3f})")

        # Inequality
        avg_gini = df["resource_gini"].mean()
        lines.append(f"**Resource Gini**: avg {avg_gini:.3f}")

        # Reproductive outcomes
        avg_skew = df["reproductive_skew"].mean()
        avg_unmated = df["unmated_male_pct"].mean()
        lines.append(f"**Reproductive skew**: {avg_skew:.3f}, "
                      f"unmated males: {avg_unmated:.1%}")

        # Child survival
        avg_survival = df["child_survival_rate"].mean()
        lines.append(f"**Child survival**: {avg_survival:.1%}")

        # Trait evolution
        agg_start = early["avg_aggression"].mean()
        agg_end = late["avg_aggression"].mean()
        coop_start = early["avg_cooperation"].mean()
        coop_end = late["avg_cooperation"].mean()
        lines.append(f"**Trait evolution**: aggression {agg_start:.3f}->{agg_end:.3f}, "
                      f"cooperation {coop_start:.3f}->{coop_end:.3f}")

        # Integrity warnings
        warnings = self.checker.check_all(df)
        if warnings:
            lines.append("\n**Warnings:**")
            for w in warnings:
                lines.append(f"- {w}")

        lines.append("")
        return "\n".join(lines)

    def generate_scenario_comparison(self, all_results: dict) -> str:
        """Comparative narrative across all scenarios."""
        lines = ["# SIMSIV Scenario Comparison Report\n"]
        lines.append(f"*{DISCLAIMER}*\n")

        # Per-scenario summaries
        for name, result in all_results.items():
            lines.append(self.generate_run_summary(result["metrics_df"], name))

        # Cross-scenario highlights
        lines.append("---\n## Cross-Scenario Highlights\n")

        # Find extremes
        scenario_stats = {}
        for name, result in all_results.items():
            summaries = result["summaries"]
            scenario_stats[name] = {
                k: np.mean([s[k] for s in summaries])
                for k in summaries[0] if isinstance(summaries[0][k], (int, float))
            }

        if scenario_stats:
            # Most violent
            most_violent = max(scenario_stats, key=lambda n: scenario_stats[n].get("avg_violence_rate", 0))
            least_violent = min(scenario_stats, key=lambda n: scenario_stats[n].get("avg_violence_rate", 0))
            lines.append(f"**Most violent**: {most_violent} "
                          f"({scenario_stats[most_violent]['avg_violence_rate']:.3f})")
            lines.append(f"**Least violent**: {least_violent} "
                          f"({scenario_stats[least_violent]['avg_violence_rate']:.3f})")

            # Most unequal
            most_unequal = max(scenario_stats, key=lambda n: scenario_stats[n].get("avg_resource_gini", 0))
            lines.append(f"**Highest inequality**: {most_unequal} "
                          f"(Gini {scenario_stats[most_unequal]['avg_resource_gini']:.3f})")

            # Best child survival
            best_survival = max(scenario_stats, key=lambda n: scenario_stats[n].get("avg_child_survival", 0))
            lines.append(f"**Best child survival**: {best_survival} "
                          f"({scenario_stats[best_survival]['avg_child_survival']:.1%})")

            # Highest unmated male pct
            most_unmated = max(scenario_stats, key=lambda n: scenario_stats[n].get("avg_unmated_male_pct", 0))
            lines.append(f"**Most unmated males**: {most_unmated} "
                          f"({scenario_stats[most_unmated]['avg_unmated_male_pct']:.1%})")

        # Integrity check across all
        all_warnings = self.checker.check_seed_sensitivity(all_results)
        if all_warnings:
            lines.append("\n## Integrity Warnings\n")
            for w in all_warnings:
                lines.append(f"- {w}")

        lines.append(f"\n---\n*{DISCLAIMER}*")
        return "\n".join(lines)

    def save_report(self, text: str, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
