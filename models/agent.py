"""
Agent model — the core entity of the simulation.

Each agent has heritable traits (passed to offspring with mutation) and
non-heritable attributes (earned/contextual, built over lifetime).
"""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

import numpy as np


class Sex(Enum):
    MALE = "male"
    FEMALE = "female"


# Heritable trait names in canonical order (used for inheritance, mutation, correlation)
HERITABLE_TRAITS = [
    "aggression_propensity",
    "cooperation_propensity",
    "attractiveness_base",
    "status_drive",
    "risk_tolerance",
    "jealousy_sensitivity",
    "fertility_base",
    "intelligence_proxy",
]

# Correlation matrix for initial trait generation.
# Order matches HERITABLE_TRAITS above.
# Key correlations:
#   aggression <-> cooperation: -0.4 (antagonistic)
#   status_drive <-> risk_tolerance: +0.3 (ambitious risk-takers)
#   intelligence <-> cooperation: +0.2 (slight positive)
#   aggression <-> risk_tolerance: +0.3
TRAIT_CORRELATION = np.array([
    # agg   coop  attr  stat  risk  jeal  fert  intel
    [ 1.0, -0.4,  0.0,  0.2,  0.3,  0.2,  0.0,  0.0],  # aggression
    [-0.4,  1.0,  0.0,  0.0, -0.1,  0.0,  0.0,  0.2],  # cooperation
    [ 0.0,  0.0,  1.0,  0.1,  0.0,  0.0,  0.1,  0.0],  # attractiveness
    [ 0.2,  0.0,  0.1,  1.0,  0.3,  0.1,  0.0,  0.1],  # status_drive
    [ 0.3, -0.1,  0.0,  0.3,  1.0,  0.0,  0.0,  0.0],  # risk_tolerance
    [ 0.2,  0.0,  0.0,  0.1,  0.0,  1.0,  0.0,  0.0],  # jealousy
    [ 0.0,  0.0,  0.1,  0.0,  0.0,  0.0,  1.0,  0.0],  # fertility
    [ 0.0,  0.2,  0.0,  0.1,  0.0,  0.0,  0.0,  1.0],  # intelligence
])


_next_id = 0


def _new_id() -> int:
    global _next_id
    _next_id += 1
    return _next_id


def reset_id_counter():
    global _next_id
    _next_id = 0


@dataclass
class Agent:
    id: int = field(default_factory=_new_id)
    sex: Sex = Sex.MALE
    age: int = 0
    generation: int = 0

    # ── Heritable traits [0.0 - 1.0] ────────────────────────────────
    aggression_propensity: float = 0.5
    cooperation_propensity: float = 0.5
    attractiveness_base: float = 0.5
    status_drive: float = 0.5
    risk_tolerance: float = 0.5
    jealousy_sensitivity: float = 0.5
    fertility_base: float = 0.5
    intelligence_proxy: float = 0.5

    # ── Non-heritable (earned/contextual) ────────────────────────────
    health: float = 1.0
    social_trust: float = 0.5
    reputation: float = 0.5
    current_resources: float = 0.0
    current_status: float = 0.0

    # ── Relationships ────────────────────────────────────────────────
    pair_bond_id: Optional[int] = None
    pair_bond_strength: float = 0.0
    offspring_ids: list[int] = field(default_factory=list)
    parent_ids: tuple[Optional[int], Optional[int]] = (None, None)

    # ── Memory (sparse — only agents we've interacted with) ──────────
    reputation_ledger: dict[int, float] = field(default_factory=dict)

    # ── State flags ──────────────────────────────────────────────────
    alive: bool = True
    cause_of_death: Optional[str] = None
    year_of_death: Optional[int] = None

    @property
    def mate_value(self) -> float:
        """Dynamic mate value based on current state.
        Combines health, status, resources, attractiveness, with age penalty.
        """
        if not self.alive:
            return 0.0
        age_factor = 1.0
        if self.age < 15:
            age_factor = 0.1
        elif self.age > 50:
            age_factor = max(0.3, 1.0 - (self.age - 50) * 0.03)

        resource_component = min(self.current_resources / 20.0, 1.0)  # normalize
        return (
            self.health * 0.3
            + self.attractiveness_base * 0.25
            + self.current_status * 0.2
            + resource_component * 0.15
            + self.reputation * 0.1
        ) * age_factor

    def is_fertile(self, config) -> bool:
        if not self.alive or self.health < 0.2:
            return False
        if self.sex == Sex.FEMALE:
            return self.age_first_reproduction <= self.age <= config.age_max_reproduction_female
        return self.age >= config.age_first_reproduction and self.age <= config.age_max_reproduction_male

    @property
    def age_first_reproduction(self) -> int:
        return 15  # default; overridden by config in is_fertile

    def is_fertile_with_config(self, config) -> bool:
        if not self.alive or self.health < 0.2:
            return False
        if self.sex == Sex.FEMALE:
            return config.age_first_reproduction <= self.age <= config.age_max_reproduction_female
        return config.age_first_reproduction <= self.age <= config.age_max_reproduction_male

    def can_mate(self, config) -> bool:
        return self.alive and self.is_fertile_with_config(config)

    def get_heritable_traits(self) -> dict[str, float]:
        return {t: getattr(self, t) for t in HERITABLE_TRAITS}

    def remember(self, other_id: int, delta: float, max_memory: int = 100):
        """Update reputation ledger for another agent. Sparse, capped."""
        if other_id in self.reputation_ledger:
            old = self.reputation_ledger[other_id]
            self.reputation_ledger[other_id] = max(0.0, min(1.0, old + delta))
        else:
            if len(self.reputation_ledger) >= max_memory:
                # Evict the entry closest to neutral (0.5)
                worst_key = min(self.reputation_ledger,
                                key=lambda k: abs(self.reputation_ledger[k] - 0.5))
                del self.reputation_ledger[worst_key]
            self.reputation_ledger[other_id] = max(0.0, min(1.0, 0.5 + delta))

    def trust_of(self, other_id: int) -> float:
        """How much this agent trusts another. Default 0.5 if unknown."""
        return self.reputation_ledger.get(other_id, 0.5)

    def die(self, cause: str, year: int):
        self.alive = False
        self.cause_of_death = cause
        self.year_of_death = year
        self.pair_bond_id = None
        self.pair_bond_strength = 0.0

    def __repr__(self):
        status = "alive" if self.alive else f"dead({self.cause_of_death})"
        return (f"Agent(id={self.id}, {self.sex.value}, age={self.age}, "
                f"gen={self.generation}, health={self.health:.2f}, "
                f"res={self.current_resources:.1f}, {status})")


def create_initial_population(
    rng: np.random.Generator, config, count: int
) -> list[Agent]:
    """Create the founding population with correlated traits and realistic age distribution."""
    reset_id_counter()
    agents = []

    if config.correlated_traits:
        # Generate correlated trait values via multivariate normal
        mean = np.full(len(HERITABLE_TRAITS), 0.5)
        std = 0.15
        cov = TRAIT_CORRELATION * (std ** 2)
        raw_traits = rng.multivariate_normal(mean, cov, size=count)
        raw_traits = np.clip(raw_traits, 0.0, 1.0)
    else:
        raw_traits = rng.uniform(0.0, 1.0, size=(count, len(HERITABLE_TRAITS)))

    for i in range(count):
        sex = Sex.FEMALE if i < count // 2 else Sex.MALE
        age = rng.integers(0, config.init_max_age)

        a = Agent(
            sex=sex,
            age=int(age),
            generation=0,
        )

        for j, trait_name in enumerate(HERITABLE_TRAITS):
            setattr(a, trait_name, float(raw_traits[i, j]))

        # Scale initial health by age
        if age > 40:
            a.health = max(0.3, 1.0 - (age - 40) * 0.02)

        # Initial resources proportional to age (older = more accumulated)
        a.current_resources = float(rng.uniform(1, 5) + age * 0.2)
        a.current_status = float(rng.uniform(0, 0.3))

        agents.append(a)

    return agents


def breed(parent1: Agent, parent2: Agent, rng: np.random.Generator,
          config, year: int) -> Agent:
    """Create offspring from two parents. Blends heritable traits with mutation."""
    child_sex = Sex.FEMALE if rng.random() < 0.5 else Sex.MALE
    generation = max(parent1.generation, parent2.generation) + 1

    child = Agent(
        sex=child_sex,
        age=0,
        generation=generation,
        parent_ids=(parent1.id, parent2.id),
        health=1.0,
    )

    # Inherit traits: midpoint of parents + Gaussian mutation
    for trait_name in HERITABLE_TRAITS:
        p1_val = getattr(parent1, trait_name)
        p2_val = getattr(parent2, trait_name)
        child_val = (p1_val + p2_val) / 2.0 + rng.normal(0, config.mutation_sigma)
        setattr(child, trait_name, float(np.clip(child_val, 0.0, 1.0)))

    parent1.offspring_ids.append(child.id)
    parent2.offspring_ids.append(child.id)

    return child
