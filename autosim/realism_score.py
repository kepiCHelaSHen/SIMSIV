"""
Realism scoring — compares simulation output against anthropological calibration targets.
"""

from __future__ import annotations
import numpy as np
from pathlib import Path
import yaml


def load_targets(path: str | Path | None = None) -> dict:
    """Load calibration targets from YAML. Returns {metric_name: (low, high, weight)}."""
    if path is None:
        path = Path(__file__).parent / "targets.yaml"
    with open(path) as f:
        data = yaml.safe_load(f)
    targets = {}
    for name, spec in data["targets"].items():
        targets[name] = (spec["low"], spec["high"], spec.get("weight", 1.0))
    return targets


def extract_metrics(rows: list[dict], window: int = 20) -> dict:
    """Extract aggregate metrics from the last `window` years of simulation output.

    Returns a dict with all target-relevant metrics, including derived ones.
    """
    if len(rows) < window:
        window = len(rows)
    if window == 0:
        return {}

    last = rows[-window:]

    # Direct averages
    result = {}
    for key in ("resource_gini", "mating_inequality", "pop_growth_rate",
                "avg_lifetime_births", "avg_cooperation", "avg_aggression",
                "pair_bonded_pct", "violence_rate", "population"):
        vals = [r.get(key, 0) for r in last]
        result[key] = float(np.mean(vals))

    # Derived: violence death fraction of male deaths
    total_vio = sum(r.get("violence_deaths", 0) for r in last)
    total_male_deaths = sum(r.get("male_deaths", 0) for r in last)
    result["violence_death_fraction"] = (
        total_vio / max(1, total_male_deaths))

    # Derived: child survival (1 - childhood_deaths / births)
    total_births = sum(r.get("births", 0) for r in last)
    total_child_deaths = sum(r.get("childhood_deaths", 0) for r in last)
    result["child_survival_to_15"] = (
        1.0 - total_child_deaths / max(1, total_births))

    # Derived: bond dissolution rate
    total_dissolved = sum(r.get("bonds_dissolved", 0) for r in last)
    total_formed = sum(r.get("bonds_formed", 0) for r in last)
    result["bond_dissolution_rate"] = (
        total_dissolved / max(1, total_formed))

    return result


def realism_score(metrics: dict, targets: dict | None = None) -> tuple[float, dict]:
    """Compute composite realism score.

    Args:
        metrics: dict from extract_metrics()
        targets: dict from load_targets(), or None to auto-load

    Returns:
        (composite_score, per_metric_scores) where composite is weighted average
        and per_metric_scores maps metric_name → individual score [0-1].
    """
    if targets is None:
        targets = load_targets()

    scores = {}
    weights = {}
    for metric_name, (low, high, weight) in targets.items():
        value = metrics.get(metric_name)
        if value is None:
            continue
        if low <= value <= high:
            scores[metric_name] = 1.0
        else:
            dist = min(abs(value - low), abs(value - high))
            range_size = high - low
            scores[metric_name] = max(0.0, 1.0 - dist / (range_size + 0.01))
        weights[metric_name] = weight

    if not scores:
        return 0.0, {}

    total_weight = sum(weights[k] for k in scores)
    composite = sum(scores[k] * weights[k] for k in scores) / total_weight
    return float(composite), scores
