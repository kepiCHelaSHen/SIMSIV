"""
AutoSIM Runner — Mode A parameter optimization.

Hill-climbing optimizer that perturbs config parameters, runs multi-seed
simulations, scores against anthropological targets, and keeps improvements.

Usage:
    python -m autosim.runner --experiments 100
    python -m autosim.runner --experiments 3 --smoke-test
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import os
import copy
from dataclasses import asdict
from pathlib import Path

import numpy as np
import yaml

# Ensure project root on path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import Config
from simulation import Simulation
from autosim.realism_score import load_targets, extract_metrics, realism_score


# ── Constants ──────────────────────────────────────────────────────────
AUTOSIM_DIR = Path(__file__).parent
JOURNAL_PATH = AUTOSIM_DIR / "journal.jsonl"
BEST_CONFIG_PATH = AUTOSIM_DIR / "best_config.yaml"
TARGETS_PATH = AUTOSIM_DIR / "targets.yaml"

SIM_YEARS = 200
SIM_POP = 500
SEED_COUNT = 3
SEEDS = [42, 137, 271]
METRIC_WINDOW = 20  # average last N years


def load_tunable_parameters() -> dict:
    """Load tunable parameter definitions from targets.yaml."""
    with open(TARGETS_PATH) as f:
        data = yaml.safe_load(f)
    return data.get("tunable_parameters", {})


def run_simulation(config: Config) -> list[dict]:
    """Run one simulation, return metrics rows."""
    sim = Simulation(config)
    sim.run()
    return sim.metrics.rows


def score_config(config_overrides: dict, tunable: dict,
                 targets: dict) -> tuple[float, dict, dict, bool]:
    """Run multi-seed simulation with given parameter overrides.

    Returns: (score, per_metric_scores, avg_metrics, survived)
    """
    all_metrics = []
    survived = True

    for seed in SEEDS:
        cfg = Config(years=SIM_YEARS, population_size=SIM_POP, seed=seed)
        # Apply overrides
        for param, value in config_overrides.items():
            setattr(cfg, param, value)

        rows = run_simulation(cfg)

        # Check survival: population must be > 20 at end
        final_pop = rows[-1].get("population", 0) if rows else 0
        if final_pop < 20:
            survived = False

        metrics = extract_metrics(rows, METRIC_WINDOW)
        all_metrics.append(metrics)

    if not all_metrics:
        return 0.0, {}, {}, False

    # Average metrics across seeds
    avg_metrics = {}
    all_keys = set()
    for m in all_metrics:
        all_keys.update(m.keys())
    for key in all_keys:
        vals = [m.get(key, 0) for m in all_metrics]
        avg_metrics[key] = float(np.mean(vals))

    score, per_metric = realism_score(avg_metrics, targets)

    # Penalty for population collapse
    if not survived:
        score *= 0.5

    return score, per_metric, avg_metrics, survived


def propose_perturbation(current: dict, tunable: dict,
                         rng: np.random.Generator,
                         n_params: int = 2,
                         step_scale: float = 0.15) -> dict:
    """Propose a new parameter configuration by perturbing current values.

    Randomly selects n_params parameters and perturbs each by a fraction
    of its allowed range.
    """
    candidate = dict(current)
    param_names = list(tunable.keys())
    chosen = rng.choice(param_names, size=min(n_params, len(param_names)),
                        replace=False)

    for param in chosen:
        spec = tunable[param]
        low, high = spec["low"], spec["high"]
        range_size = high - low
        current_val = candidate.get(param, spec["default"])

        # Gaussian perturbation scaled to parameter range
        delta = rng.normal(0, step_scale * range_size)
        new_val = float(np.clip(current_val + delta, low, high))
        candidate[param] = round(new_val, 6)

    return candidate


def format_changes(current: dict, previous: dict, tunable: dict) -> str:
    """Format parameter changes as human-readable string."""
    changes = []
    for param in sorted(current.keys()):
        cur = current[param]
        prev = previous.get(param, tunable[param]["default"])
        if abs(cur - prev) > 1e-8:
            changes.append(f"  {param}: {prev:.4f} -> {cur:.4f}")
    return "\n".join(changes) if changes else "  (no changes)"


def run_experiments(n_experiments: int, smoke_test: bool = False):
    """Run the full autosim experiment loop."""
    rng = np.random.default_rng(2026)
    targets = load_targets()
    tunable = load_tunable_parameters()

    # Start from defaults
    best_params = {p: spec["default"] for p, spec in tunable.items()}
    best_score = -1.0
    best_metrics = {}
    best_per_metric = {}

    # Score baseline first
    print("=" * 70)
    print("AutoSIM Mode A -- Parameter Optimization")
    print(f"Target: {n_experiments} experiments, {SIM_YEARS}yr x {SIM_POP}pop x {SEED_COUNT} seeds")
    print("=" * 70)
    print("\nScoring baseline configuration...")
    t0 = time.time()
    best_score, best_per_metric, best_metrics, survived = score_config(
        best_params, tunable, targets)
    elapsed = time.time() - t0
    print(f"Baseline score: {best_score:.4f} ({elapsed:.1f}s)")
    print("Per-metric breakdown:")
    for m, s in sorted(best_per_metric.items()):
        t_low, t_high, _ = targets[m]
        val = best_metrics.get(m, 0)
        status = "OK" if s >= 0.99 else "XX"
        print(f"  [{status}] {m:30s} = {val:.4f}  (target {t_low:.2f}-{t_high:.2f}, score {s:.3f})")

    # Save baseline to journal
    _log_experiment(0, best_params, best_params, best_score,
                    best_per_metric, best_metrics, survived,
                    "baseline", 0.0, elapsed)
    # Save baseline as best config
    _save_best_config(best_params, best_score, best_metrics)

    # ── Optimization loop ─────────────────────────────────────────────
    accepted = 0
    rejected = 0
    streak = 0  # consecutive rejections

    for exp_id in range(1, n_experiments + 1):
        t0 = time.time()

        # Adaptive: more params perturbed and bigger steps after long streaks
        n_params = 2 if streak < 10 else 3 if streak < 20 else 4
        step_scale = 0.15 if streak < 10 else 0.25 if streak < 20 else 0.35

        # Every 10th experiment, try a bigger random jump
        if exp_id % 10 == 0:
            n_params = min(5, len(tunable))
            step_scale = 0.30

        candidate = propose_perturbation(best_params, tunable, rng,
                                         n_params=n_params,
                                         step_scale=step_scale)
        score, per_metric, metrics, survived = score_config(
            candidate, tunable, targets)
        elapsed = time.time() - t0

        # Accept if better
        improved = score > best_score
        if improved:
            action = "ACCEPT"
            delta = score - best_score
            best_params = candidate
            best_score = score
            best_per_metric = per_metric
            best_metrics = metrics
            accepted += 1
            streak = 0
            _save_best_config(best_params, best_score, best_metrics)
        else:
            action = "REJECT"
            delta = score - best_score
            rejected += 1
            streak += 1

        _log_experiment(exp_id, candidate, best_params, score,
                        per_metric, metrics, survived, action, delta, elapsed)

        # Progress output
        marker = "^" if improved else "."
        pop = metrics.get("population", 0)
        print(f"[{exp_id:3d}/{n_experiments}] {marker} score={score:.4f} "
              f"(best={best_score:.4f}, d={delta:+.4f}) "
              f"pop={pop:.0f} {elapsed:.1f}s "
              f"[{accepted}up {rejected}dn]")

    # ── Final summary ─────────────────────────────────────────────────
    print("\n" + "=" * 70)
    print(f"AutoSIM COMPLETE -- {n_experiments} experiments")
    print(f"Accepted: {accepted}, Rejected: {rejected}")
    print(f"Best score: {best_score:.4f}")
    print("=" * 70)
    print("\nBest parameter values (changes from default):")
    for param in sorted(best_params.keys()):
        default = tunable[param]["default"]
        val = best_params[param]
        if abs(val - default) > 1e-6:
            print(f"  {param}: {default} -> {val:.6f}")

    print("\nFinal per-metric scores:")
    for m, s in sorted(best_per_metric.items()):
        t_low, t_high, _ = targets[m]
        val = best_metrics.get(m, 0)
        status = "OK" if s >= 0.99 else "XX"
        print(f"  [{status}] {m:30s} = {val:.4f}  (target {t_low:.2f}-{t_high:.2f})")

    print(f"\nJournal: {JOURNAL_PATH}")
    print(f"Best config: {BEST_CONFIG_PATH}")


def _log_experiment(exp_id: int, params: dict, best_params: dict,
                    score: float, per_metric: dict, metrics: dict,
                    survived: bool, action: str, delta: float,
                    elapsed: float):
    """Append experiment to journal.jsonl."""
    entry = {
        "experiment_id": exp_id,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "action": action,
        "score": round(score, 6),
        "delta": round(delta, 6),
        "survived": survived,
        "elapsed_seconds": round(elapsed, 2),
        "params": {k: round(v, 6) for k, v in params.items()},
        "metrics": {k: round(v, 6) for k, v in metrics.items()},
        "per_metric_scores": {k: round(v, 4) for k, v in per_metric.items()},
    }
    with open(JOURNAL_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


def _save_best_config(params: dict, score: float, metrics: dict):
    """Save current best parameters to YAML."""
    data = {
        "autosim_best_score": round(score, 6),
        "autosim_key_metrics": {k: round(v, 4)
                                for k, v in metrics.items()
                                if k in ("resource_gini", "violence_death_fraction",
                                         "child_survival_to_15", "avg_lifetime_births",
                                         "pop_growth_rate", "bond_dissolution_rate",
                                         "avg_cooperation", "avg_aggression",
                                         "mating_inequality", "population")},
        "parameters": {k: round(v, 6) for k, v in params.items()},
    }
    with open(BEST_CONFIG_PATH, "w") as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def main():
    parser = argparse.ArgumentParser(description="AutoSIM Mode A runner")
    parser.add_argument("--experiments", type=int, default=100,
                        help="Number of experiments to run")
    parser.add_argument("--smoke-test", action="store_true",
                        help="Run 3 experiments as smoke test")
    args = parser.parse_args()

    n = 3 if args.smoke_test else args.experiments

    # Clear journal for fresh run
    if JOURNAL_PATH.exists():
        JOURNAL_PATH.unlink()

    run_experiments(n)


if __name__ == "__main__":
    main()
