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
    # Original 8 (DD01-DD04)
    "aggression_propensity",     # 0
    "cooperation_propensity",    # 1
    "attractiveness_base",       # 2
    "status_drive",              # 3
    "risk_tolerance",            # 4
    "jealousy_sensitivity",      # 5
    "fertility_base",            # 6
    "intelligence_proxy",        # 7
    # DD15: Biological robustness
    "longevity_genes",           # 8
    "disease_resistance",        # 9
    "physical_robustness",       # 10
    "pain_tolerance",            # 11
    # DD15: Psychological
    "mental_health_baseline",    # 12
    "emotional_intelligence",    # 13
    "impulse_control",           # 14
    "novelty_seeking",           # 15
    # DD15: Social
    "empathy_capacity",          # 16
    "conformity_bias",           # 17
    "dominance_drive",           # 18
    # DD15: Reproductive biology
    "maternal_investment",       # 19
    "sexual_maturation_rate",    # 20
    # DD17: Heritable condition risks
    "cardiovascular_risk",       # 21
    "mental_illness_risk",       # 22
    "autoimmune_risk",           # 23
    "metabolic_risk",            # 24
    "degenerative_risk",         # 25
]

# DD15: Per-trait heritability coefficients (h²)
# child_val = h² * parent_midpoint + (1 - h²) * pop_mean + mutation
TRAIT_HERITABILITY = {
    "aggression_propensity": 0.44,
    "cooperation_propensity": 0.40,
    "attractiveness_base": 0.50,
    "status_drive": 0.50,
    "risk_tolerance": 0.48,
    "jealousy_sensitivity": 0.45,
    "fertility_base": 0.50,
    "intelligence_proxy": 0.65,
    "longevity_genes": 0.25,
    "disease_resistance": 0.40,
    "physical_robustness": 0.50,
    "pain_tolerance": 0.45,
    "mental_health_baseline": 0.40,
    "emotional_intelligence": 0.40,
    "impulse_control": 0.50,
    "novelty_seeking": 0.40,
    "empathy_capacity": 0.35,
    "conformity_bias": 0.35,
    "dominance_drive": 0.50,
    "maternal_investment": 0.35,
    "sexual_maturation_rate": 0.60,
    # DD17: Condition risk heritability
    "cardiovascular_risk": 0.50,
    "mental_illness_risk": 0.60,
    "autoimmune_risk": 0.40,
    "metabolic_risk": 0.45,
    "degenerative_risk": 0.35,
}


def _build_correlation_matrix() -> np.ndarray:
    """Build 21x21 trait correlation matrix programmatically.

    Original 8x8 block preserved exactly. New correlations from
    behavioral genetics literature added for DD15 traits.
    """
    n = len(HERITABLE_TRAITS)
    idx = {name: i for i, name in enumerate(HERITABLE_TRAITS)}
    C = np.eye(n)

    def _set(a: str, b: str, val: float):
        C[idx[a], idx[b]] = val
        C[idx[b], idx[a]] = val

    # ── Original 8x8 correlations (unchanged) ──────────────────────
    _set("aggression_propensity", "cooperation_propensity", -0.4)
    _set("aggression_propensity", "status_drive", 0.2)
    _set("aggression_propensity", "risk_tolerance", 0.3)
    _set("aggression_propensity", "jealousy_sensitivity", 0.2)
    _set("cooperation_propensity", "risk_tolerance", -0.1)
    _set("cooperation_propensity", "intelligence_proxy", 0.2)
    _set("attractiveness_base", "status_drive", 0.1)
    _set("attractiveness_base", "fertility_base", 0.1)
    _set("status_drive", "risk_tolerance", 0.3)
    _set("status_drive", "jealousy_sensitivity", 0.1)
    _set("status_drive", "intelligence_proxy", 0.1)

    # ── DD15: New trait correlations ───────────────────────────────
    # From prompt specification:
    _set("impulse_control", "aggression_propensity", -0.4)
    _set("emotional_intelligence", "cooperation_propensity", 0.3)
    _set("mental_health_baseline", "impulse_control", 0.3)
    _set("novelty_seeking", "risk_tolerance", 0.4)
    _set("dominance_drive", "aggression_propensity", 0.3)
    _set("conformity_bias", "novelty_seeking", -0.3)
    _set("longevity_genes", "mental_health_baseline", 0.2)
    # Additional biologically plausible correlations:
    _set("empathy_capacity", "cooperation_propensity", 0.2)
    _set("empathy_capacity", "aggression_propensity", -0.2)
    _set("dominance_drive", "status_drive", 0.3)
    _set("impulse_control", "intelligence_proxy", 0.2)
    _set("physical_robustness", "pain_tolerance", 0.3)
    _set("maternal_investment", "empathy_capacity", 0.2)
    _set("emotional_intelligence", "empathy_capacity", 0.3)

    # ── DD17: Condition risk correlations ─────────────────────────
    _set("cardiovascular_risk", "aggression_propensity", 0.15)
    _set("cardiovascular_risk", "status_drive", 0.1)
    _set("mental_illness_risk", "mental_health_baseline", -0.3)
    _set("mental_illness_risk", "impulse_control", -0.2)
    _set("degenerative_risk", "physical_robustness", -0.2)

    return C


# Correlation matrix for initial trait generation (21x21).
TRAIT_CORRELATION = _build_correlation_matrix()


_next_id = 0


def _new_id() -> int:
    global _next_id
    _next_id += 1
    return _next_id


def reset_id_counter():
    """Reset the global ID counter to 0.

    WARNING: Only use between completely independent sessions. Never call
    during multi-run experiments — IDs will collide across scenarios.
    """
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
    # DD15: Biological robustness traits
    longevity_genes: float = 0.5
    disease_resistance: float = 0.5
    physical_robustness: float = 0.5
    pain_tolerance: float = 0.5
    # DD15: Psychological traits
    mental_health_baseline: float = 0.5
    emotional_intelligence: float = 0.5
    impulse_control: float = 0.5
    novelty_seeking: float = 0.5
    # DD15: Social traits
    empathy_capacity: float = 0.5
    conformity_bias: float = 0.5
    dominance_drive: float = 0.5
    # DD15: Reproductive biology traits
    maternal_investment: float = 0.5
    sexual_maturation_rate: float = 0.5
    # DD17: Heritable condition risks [0.0-1.0]
    cardiovascular_risk: float = 0.2
    mental_illness_risk: float = 0.2
    autoimmune_risk: float = 0.2
    metabolic_risk: float = 0.2
    degenerative_risk: float = 0.2

    # ── Non-heritable (earned/contextual) ────────────────────────────
    health: float = 1.0
    reputation: float = 0.5
    current_resources: float = 0.0
    prestige_score: float = 0.0   # DD08: earned through cooperation, skill, generosity
    dominance_score: float = 0.0  # DD08: earned through conflict victories, intimidation

    # ── Relationships ────────────────────────────────────────────────
    partner_ids: list[int] = field(default_factory=list)
    pair_bond_strengths: dict[int, float] = field(default_factory=dict)
    offspring_ids: list[int] = field(default_factory=list)
    parent_ids: tuple[Optional[int], Optional[int]] = (None, None)

    # ── Infidelity / paternity ─────────────────────────────────────
    epc_partner_id: Optional[int] = None  # extra-pair mate this tick (cleared each tick)
    paternity_confidence: float = 1.0  # male's confidence in paternity [0-1]
    last_partner_death_year: Optional[int] = None
    death_partner_ids: list[int] = field(default_factory=list)  # snapshot at death

    # ── Memory (sparse — only agents we've interacted with) ──────────
    reputation_ledger: dict[int, float] = field(default_factory=dict)

    # ── Reproduction state ─────────────────────────────────────────
    last_birth_year: Optional[int] = None  # DD06: year of most recent birth
    lifetime_births: int = 0               # DD06: total births for this agent

    # ── Conflict state ─────────────────────────────────────────────
    conflict_cooldown: int = 0  # years of subordination remaining (decays 1/yr)

    # ── DD17: Medical state (non-heritable) ─────────────────────────
    active_conditions: set = field(default_factory=set)   # currently active conditions
    trauma_score: float = 0.0                             # accumulated trauma [0.0-1.0]
    medical_history: list = field(default_factory=list)    # list of {year, event, severity}

    # ── DD16: Developmental biology (nature vs nurture) ─────────────
    genotype: dict = field(default_factory=dict)  # original genetic values at birth
    childhood_resource_quality: float = 0.5       # avg parental resources 0-5
    childhood_trauma: bool = False                 # parent died before age 10
    developmental_parent_aggression: float = 0.5   # avg of parents' aggression
    developmental_parent_cooperation: float = 0.5  # avg of parents' cooperation
    traits_finalized: bool = False                 # set True at maturation (age 15)

    # ── Faction membership ─────────────────────────────────────────
    faction_id: Optional[int] = None  # DD14: emergent faction assignment

    # ── State flags ──────────────────────────────────────────────────
    alive: bool = True
    cause_of_death: Optional[str] = None
    year_of_death: Optional[int] = None

    @property
    def current_status(self) -> float:
        """Backward-compatible combined status (DD08: weighted blend)."""
        return self.prestige_score * 0.6 + self.dominance_score * 0.4

    @current_status.setter
    def current_status(self, value: float):
        """Backward-compatible setter: distribute to both tracks."""
        self.prestige_score = value * 0.6
        self.dominance_score = value * 0.4

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
        # DD08: prestige weighted more than dominance in mate value
        status_component = self.prestige_score * 0.6 + self.dominance_score * 0.4
        return (
            self.health * 0.3
            + self.attractiveness_base * 0.25
            + status_component * 0.2
            + resource_component * 0.15
            + self.reputation * 0.1
        ) * age_factor

    # ── Bond management ──────────────────────────────────────────
    @property
    def is_bonded(self) -> bool:
        return len(self.partner_ids) > 0

    @property
    def bond_count(self) -> int:
        return len(self.partner_ids)

    @property
    def primary_partner_id(self) -> Optional[int]:
        if not self.partner_ids:
            return None
        return self.partner_ids[0]

    @property
    def primary_bond_strength(self) -> float:
        pid = self.primary_partner_id
        return self.pair_bond_strengths.get(pid, 0.0) if pid is not None else 0.0

    def bond_strength_with(self, partner_id: int) -> float:
        return self.pair_bond_strengths.get(partner_id, 0.0)

    def is_bonded_to(self, partner_id: int) -> bool:
        return partner_id in self.partner_ids

    def add_bond(self, partner_id: int, strength: float):
        if partner_id not in self.partner_ids:
            self.partner_ids.append(partner_id)
        self.pair_bond_strengths[partner_id] = strength

    def remove_bond(self, partner_id: int):
        if partner_id in self.partner_ids:
            self.partner_ids.remove(partner_id)
        self.pair_bond_strengths.pop(partner_id, None)

    def remove_all_bonds(self):
        self.partner_ids.clear()
        self.pair_bond_strengths.clear()

    def is_in_mourning(self, current_year: int, mourning_years: int) -> bool:
        return (self.last_partner_death_year is not None
                and (current_year - self.last_partner_death_year) < mourning_years)

    def is_fertile_with_config(self, config) -> bool:
        if not self.alive or self.health < 0.2:
            return False
        # DD15: sexual_maturation_rate modifies age_first_reproduction ±3 years
        maturation_offset = int((self.sexual_maturation_rate - 0.5) * 6)  # range -3 to +3
        effective_first = max(12, config.age_first_reproduction - maturation_offset)
        if self.sex == Sex.FEMALE:
            return effective_first <= self.age <= config.age_max_reproduction_female
        return effective_first <= self.age <= config.age_max_reproduction_male

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
        self.death_partner_ids = list(self.partner_ids)  # snapshot for inheritance

    def __repr__(self):
        status = "alive" if self.alive else f"dead({self.cause_of_death})"
        return (f"Agent(id={self.id}, {self.sex.value}, age={self.age}, "
                f"gen={self.generation}, health={self.health:.2f}, "
                f"res={self.current_resources:.1f}, {status})")


def create_initial_population(
    rng: np.random.Generator, config, count: int
) -> list[Agent]:
    """Create the founding population with correlated traits and realistic age distribution."""
    agents = []

    if config.correlated_traits:
        # Generate correlated trait values via multivariate normal
        # DD17: Condition risk traits start with lower mean (0.2) for healthy population
        condition_risk_traits = {"cardiovascular_risk", "mental_illness_risk",
                                 "autoimmune_risk", "metabolic_risk", "degenerative_risk"}
        mean = np.array([0.2 if t in condition_risk_traits else 0.5
                         for t in HERITABLE_TRAITS])
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
        # DD08: initialize prestige and dominance separately
        a.prestige_score = float(rng.uniform(0, 0.2))
        a.dominance_score = float(rng.uniform(0, 0.2))

        agents.append(a)

    return agents


def breed(parent1: Agent, parent2: Agent, rng: np.random.Generator,
          config, year: int, scarcity: float = 0.0,
          pop_trait_means: dict[str, float] | None = None) -> Agent:
    """Create offspring from two parents.

    DD15 heritability model:
      child_val = h² * parent_midpoint + (1 - h²) * pop_mean + mutation
    DD04 additions: parent weight variance, rare large mutations,
    stress-induced mutation amplification.
    """
    child_sex = Sex.FEMALE if rng.random() < 0.5 else Sex.MALE
    generation = max(parent1.generation, parent2.generation) + 1

    child = Agent(
        sex=child_sex,
        age=0,
        generation=generation,
        parent_ids=(parent1.id, parent2.id),
        health=1.0,
    )

    # Mutation sigma: amplified during environmental stress
    base_sigma = config.mutation_sigma
    if scarcity > 0 and hasattr(config, 'stress_mutation_multiplier'):
        sigma = base_sigma * (1.0 + (config.stress_mutation_multiplier - 1.0) * scarcity)
    else:
        sigma = base_sigma

    # Parent weight variance: 0 = exact 50/50, >0 = random blend per trait
    pwv = getattr(config, 'parent_weight_variance', 0.0)

    # Rare mutation parameters
    rare_rate = getattr(config, 'rare_mutation_rate', 0.0)
    rare_sigma = getattr(config, 'rare_mutation_sigma', 0.15)

    # DD15: Per-trait heritability coefficients
    heritability = getattr(config, 'heritability_by_trait', None) or TRAIT_HERITABILITY

    for trait_name in HERITABLE_TRAITS:
        # DD16: Read genotype (not phenotype) from parents for inheritance
        p1_val = parent1.genotype.get(trait_name, getattr(parent1, trait_name))
        p2_val = parent2.genotype.get(trait_name, getattr(parent2, trait_name))

        # Parent weighting: random blend around 0.5
        if pwv > 0:
            w1 = np.clip(0.5 + rng.normal(0, pwv), 0.1, 0.9)
        else:
            w1 = 0.5
        blend = p1_val * w1 + p2_val * (1.0 - w1)

        # DD15: Heritability-gated inheritance
        h2 = heritability.get(trait_name, 0.5)
        pop_mean = 0.5  # fallback
        if pop_trait_means and trait_name in pop_trait_means:
            pop_mean = pop_trait_means[trait_name]
        genetic_val = h2 * blend + (1.0 - h2) * pop_mean

        # Mutation: rare large jumps or normal noise
        if rare_rate > 0 and rng.random() < rare_rate:
            mutation = rng.normal(0, rare_sigma)
        else:
            mutation = rng.normal(0, sigma)

        child_val = genetic_val + mutation
        setattr(child, trait_name, float(np.clip(child_val, 0.0, 1.0)))

    # DD16: Store genotype (original genetic values, never modified)
    child.genotype = {t: getattr(child, t) for t in HERITABLE_TRAITS}

    # DD16: Store parental trait environment for developmental modeling
    child.developmental_parent_aggression = (
        getattr(parent1, 'aggression_propensity', 0.5)
        + getattr(parent2, 'aggression_propensity', 0.5)) / 2.0
    child.developmental_parent_cooperation = (
        getattr(parent1, 'cooperation_propensity', 0.5)
        + getattr(parent2, 'cooperation_propensity', 0.5)) / 2.0

    parent1.offspring_ids.append(child.id)
    parent2.offspring_ids.append(child.id)

    return child
