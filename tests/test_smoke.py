"""
Smoke tests — fast sanity checks that the core simulation runs without crashing.
"""

import sys
import os
import tempfile

import numpy as np
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from simulation import Simulation
from models.agent import Agent, Sex, breed, create_initial_population, HERITABLE_TRAITS
from metrics.collectors import _gini


def test_breed_trait_range():
    """All heritable traits on a child must be in [0.0, 1.0]."""
    rng = np.random.default_rng(7)
    config = Config(years=1, population_size=50, seed=7)
    pop = create_initial_population(rng, config, 50)
    pop_means = {t: float(np.mean([getattr(a, t) for a in pop])) for t in HERITABLE_TRAITS}

    parent1 = pop[0]
    parent2 = pop[25]
    # Force extreme traits to stress-test clipping
    for t in HERITABLE_TRAITS:
        setattr(parent1, t, 0.99)
        setattr(parent2, t, 0.01)
    parent1.genotype = {t: getattr(parent1, t) for t in HERITABLE_TRAITS}
    parent2.genotype = {t: getattr(parent2, t) for t in HERITABLE_TRAITS}

    for _ in range(20):
        child = breed(parent1, parent2, rng, config, year=1,
                      pop_trait_means=pop_means)
        for t in HERITABLE_TRAITS:
            val = getattr(child, t)
            assert 0.0 <= val <= 1.0, f"{t}={val} out of range"


def test_gini_correctness():
    """Gini of perfectly equal values is 0; extreme inequality approaches 1."""
    assert _gini([1.0, 1.0, 1.0, 1.0]) == 0.0
    assert _gini([]) == 0.0
    assert _gini([0, 0, 0, 100]) > 0.7
    # Uniform distribution should have moderate Gini
    uniform = list(range(1, 101))
    g = _gini(uniform)
    assert 0.3 < g < 0.4, f"Uniform 1-100 Gini={g}"


def test_config_yaml_roundtrip():
    """Config should survive save → load without data loss."""
    original = Config(
        years=77,
        population_size=123,
        seed=999,
        aggression_production_penalty=0.42,
        beliefs_enabled=False,
        skill_learning_rate_base=0.05,
    )
    with tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w") as f:
        path = f.name
    try:
        original.save(path)
        loaded = Config.load(path)
        assert loaded.years == 77
        assert loaded.population_size == 123
        assert loaded.seed == 999
        assert abs(loaded.aggression_production_penalty - 0.42) < 1e-9
        assert loaded.beliefs_enabled is False
        assert abs(loaded.skill_learning_rate_base - 0.05) < 1e-9
    finally:
        os.unlink(path)


def test_simulation_10_tick():
    """Simulation runs 10 ticks without crashing and returns metrics."""
    config = Config(years=10, population_size=50, seed=42)
    sim = Simulation(config)
    sim.run()

    assert sim.year == 10
    assert sim.finished is True
    assert len(sim.metrics.rows) == 10
    # Every row should have population key
    for row in sim.metrics.rows:
        assert "population" in row
        assert row["population"] >= 0


def test_get_living_count():
    """society.get_living() count must match population_size() and exclude dead agents."""
    config = Config(years=5, population_size=80, seed=13)
    sim = Simulation(config)
    sim.run()

    living = sim.society.get_living()
    pop_size = sim.society.population_size()
    assert len(living) == pop_size

    # All returned agents should be alive
    for a in living:
        assert a.alive is True

    # Dead agents should not appear in get_living
    all_agents = list(sim.society.agents.values())
    dead = [a for a in all_agents if not a.alive]
    living_ids = {a.id for a in living}
    for d in dead:
        assert d.id not in living_ids
