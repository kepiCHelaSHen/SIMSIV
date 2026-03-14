"""
SIMSIV Configuration
All tunable parameters in one place. Sensible defaults for baseline (FREE_COMPETITION).
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml


@dataclass
class Config:
    # ── Scale ────────────────────────────────────────────────────────
    population_size: int = 500
    years: int = 100
    seed: int = 42

    # ── Agent initialization ─────────────────────────────────────────
    # Initial age distribution: uniform 0 to this value
    init_max_age: int = 50
    # Trait correlation: if True, use correlated multivariate normal for initial traits
    correlated_traits: bool = True

    # ── Mating ───────────────────────────────────────────────────────
    mating_system: str = "unrestricted"  # "unrestricted", "monogamy", "elite_polygyny"
    female_choice_strength: float = 0.6  # 0=random, 1=pure best-available
    male_competition_intensity: float = 0.7
    pair_bond_strength: float = 0.5
    pair_bond_dissolution_rate: float = 0.1  # per year probability of bond breaking
    max_mates_per_male: int = 999  # effectively unlimited for unrestricted
    mating_pool_fraction: float = 0.5  # fraction of eligible agents who attempt mating each tick

    # ── Reproduction ─────────────────────────────────────────────────
    age_first_reproduction: int = 15
    age_max_reproduction_female: int = 45
    age_max_reproduction_male: int = 65
    child_dependency_years: int = 5
    base_conception_chance: float = 0.3  # per mating attempt per year
    mutation_sigma: float = 0.05  # Gaussian noise on heritable traits
    child_survival_base: float = 0.85  # baseline child survival to adulthood

    # ── Resources ────────────────────────────────────────────────────
    resource_abundance: float = 1.0  # multiplier on base per-agent resources
    resource_volatility: float = 0.2  # year-to-year random variation
    carrying_capacity: int = 800
    base_resource_per_agent: float = 10.0  # base survival resources per tick
    status_resource_fraction: float = 0.3  # fraction of total resources as status-type
    inheritance_model: str = "equal_split"  # "equal_split", "primogeniture", "none"

    # ── Conflict ─────────────────────────────────────────────────────
    violence_cost_health: float = 0.15  # health cost per conflict (to loser)
    violence_cost_resources: float = 0.1  # resource fraction lost by loser
    violence_death_chance: float = 0.05  # chance of death per conflict (loser)
    conflict_base_probability: float = 0.05  # random baseline conflict chance per agent
    jealousy_conflict_multiplier: float = 2.0  # multiplier when jealousy triggers conflict

    # ── Mortality ────────────────────────────────────────────────────
    age_death_base: int = 60  # mean natural death age
    age_death_variance: int = 15  # standard deviation of natural death age
    mortality_base: float = 0.02  # background annual death rate (accidents, disease)
    health_decay_per_year: float = 0.01  # base health decay rate
    min_health_survival: float = 0.05  # below this health, agent dies

    # ── Institutions ─────────────────────────────────────────────────
    monogamy_enforced: bool = False
    law_strength: float = 0.0  # 0=anarchy, 1=perfect enforcement
    elite_privilege_multiplier: float = 1.0  # resource multiplier for top-status agents
    inheritance_law_enabled: bool = False
    violence_punishment_strength: float = 0.0  # 0=none, 1=severe

    # ── Population safety ────────────────────────────────────────────
    min_viable_population: int = 20  # inject migrants if below this

    # ── Equilibrium detection ────────────────────────────────────────
    equilibrium_window: int = 10  # years of stable metrics to flag equilibrium
    equilibrium_threshold: float = 0.01  # max relative change to count as stable

    def save(self, path: Path):
        with open(path, "w") as f:
            yaml.dump(asdict(self), f, default_flow_style=False, sort_keys=False)

    @classmethod
    def load(cls, path: Path) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
