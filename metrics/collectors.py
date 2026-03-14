"""
Metrics collector — records per-tick stats for analysis and visualization.
"""

from __future__ import annotations
import numpy as np
import pandas as pd
from models.agent import Agent, Sex


def _gini(values: list[float]) -> float:
    """Compute Gini coefficient. 0 = perfect equality, 1 = perfect inequality."""
    if not values or len(values) < 2:
        return 0.0
    arr = np.array(sorted(values), dtype=float)
    if arr.sum() == 0:
        return 0.0
    n = len(arr)
    index = np.arange(1, n + 1)
    return float((2 * (index * arr).sum() / (n * arr.sum())) - (n + 1) / n)


class MetricsCollector:
    def __init__(self):
        self.rows: list[dict] = []

    def collect(self, society, year: int) -> dict:
        living = society.get_living()
        pop = len(living)

        if pop == 0:
            row = {"year": year, "population": 0}
            self.rows.append(row)
            return row

        males = [a for a in living if a.sex == Sex.MALE]
        females = [a for a in living if a.sex == Sex.FEMALE]

        # Count tick events
        births = sum(1 for e in society.tick_events if e.get("type") == "birth")
        deaths = sum(1 for e in society.tick_events if e.get("type") == "death")
        infant_deaths = sum(1 for e in society.tick_events if e.get("type") == "infant_death")
        conflicts = sum(1 for e in society.tick_events if e.get("type") == "conflict")
        bonds_formed = sum(1 for e in society.tick_events if e.get("type") == "pair_bond_formed")
        bonds_dissolved = sum(1 for e in society.tick_events if e.get("type") == "bond_dissolved")

        # Resources
        resources = [a.current_resources for a in living]
        statuses = [a.current_status for a in living]

        # Reproductive skew — gini of offspring count among adults
        offspring_counts = [len(a.offspring_ids) for a in living if a.age >= 15]

        # Unmated percentages
        unmated_males = sum(1 for m in males if m.pair_bond_id is None and m.age >= 15)
        unmated_females = sum(1 for f in females if f.pair_bond_id is None and f.age >= 15)
        adult_males = max(1, sum(1 for m in males if m.age >= 15))
        adult_females = max(1, sum(1 for f in females if f.age >= 15))

        # Elite reproductive advantage (top 10% vs bottom 10%)
        if offspring_counts and len(offspring_counts) >= 10:
            sorted_oc = sorted(offspring_counts)
            n = len(sorted_oc)
            bottom_10 = sorted_oc[:max(1, n // 10)]
            top_10 = sorted_oc[-max(1, n // 10):]
            avg_bottom = np.mean(bottom_10) or 0.01
            avg_top = np.mean(top_10)
            elite_advantage = float(avg_top / avg_bottom) if avg_bottom > 0 else 0.0
        else:
            elite_advantage = 1.0

        # Child survival rate
        child_survival = 0.0
        if births + infant_deaths > 0:
            child_survival = births / (births + infant_deaths)

        # Pair bond stability
        bonded = sum(1 for a in living if a.pair_bond_id is not None)
        bonded_pct = bonded / pop if pop > 0 else 0

        # Average health and age
        avg_health = float(np.mean([a.health for a in living]))
        avg_age = float(np.mean([a.age for a in living]))

        # Average traits
        avg_aggression = float(np.mean([a.aggression_propensity for a in living]))
        avg_cooperation = float(np.mean([a.cooperation_propensity for a in living]))

        row = {
            "year": year,
            "population": pop,
            "males": len(males),
            "females": len(females),
            "births": births,
            "deaths": deaths,
            "infant_deaths": infant_deaths,
            "conflicts": conflicts,
            "bonds_formed": bonds_formed,
            "bonds_dissolved": bonds_dissolved,
            "resource_gini": _gini(resources),
            "status_gini": _gini(statuses),
            "reproductive_skew": _gini(offspring_counts) if offspring_counts else 0.0,
            "unmated_male_pct": unmated_males / adult_males,
            "unmated_female_pct": unmated_females / adult_females,
            "elite_repro_advantage": elite_advantage,
            "child_survival_rate": child_survival,
            "pair_bonded_pct": bonded_pct,
            "violence_rate": conflicts / pop if pop > 0 else 0,
            "avg_resources": float(np.mean(resources)),
            "avg_status": float(np.mean(statuses)),
            "avg_health": avg_health,
            "avg_age": avg_age,
            "avg_aggression": avg_aggression,
            "avg_cooperation": avg_cooperation,
            "scarcity": society.environment.get_scarcity_level(),
        }
        self.rows.append(row)
        return row

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self.rows)

    def save_csv(self, path):
        self.to_dataframe().to_csv(path, index=False)

    def check_equilibrium(self, config) -> bool:
        """Check if key metrics have stabilized."""
        w = config.equilibrium_window
        if len(self.rows) < w + 1:
            return False

        recent = self.rows[-w:]
        keys = ["population", "resource_gini", "violence_rate", "reproductive_skew"]

        for key in keys:
            values = [r.get(key, 0) for r in recent]
            if not values or values[0] == 0:
                continue
            max_change = max(abs(v - values[0]) / (abs(values[0]) + 0.01) for v in values[1:])
            if max_change > config.equilibrium_threshold:
                return False
        return True
