"""Tests for Phase 0 conflict.py remediation — getattr, events, rng."""
import numpy as np
import pytest
from config import Config
from simulation import Simulation


class _PoisonedConfig:
    """Wraps a real Config but raises AttributeError for a specified attribute.

    Unlike delattr on a dataclass (which falls through to the class default),
    this wrapper intercepts __getattribute__ and raises reliably.
    """

    def __init__(self, real_config: Config, blocked_attr: str):
        object.__setattr__(self, '_real', real_config)
        object.__setattr__(self, '_blocked', blocked_attr)

    def __getattribute__(self, name):
        if name == object.__getattribute__(self, '_blocked'):
            raise AttributeError(
                f"Config has no attribute '{name}' (poisoned for test)")
        return getattr(object.__getattribute__(self, '_real'), name)

    def __setattr__(self, name, value):
        setattr(object.__getattribute__(self, '_real'), name, value)


def test_missing_coalition_defense_config_raises():
    """Engine must crash if coalition_defense_enabled is missing from config."""
    config = Config(years=10, population_size=100, seed=42,
                    conflict_base_probability=0.3)
    sim = Simulation(config)
    sim.config = _PoisonedConfig(config, 'coalition_defense_enabled')
    with pytest.raises(AttributeError, match='coalition_defense_enabled'):
        sim.run()


def test_missing_leadership_config_raises():
    """Engine must crash if leadership_enabled is missing from config."""
    config = Config(years=10, population_size=100, seed=42,
                    conflict_base_probability=0.3)
    sim = Simulation(config)
    sim.config = _PoisonedConfig(config, 'leadership_enabled')
    with pytest.raises(AttributeError, match='leadership_enabled'):
        sim.run()


def test_missing_third_party_punishment_config_raises():
    """Engine must crash if third_party_punishment_enabled is missing."""
    config = Config(years=10, population_size=100, seed=42,
                    conflict_base_probability=0.3)
    sim = Simulation(config)
    sim.config = _PoisonedConfig(config, 'third_party_punishment_enabled')
    with pytest.raises(AttributeError, match='third_party_punishment_enabled'):
        sim.run()


def test_conflict_bond_break_emits_event():
    """Conflict-caused bond dissolution must emit bond_dissolved event
    with reason='conflict_break' and both agent UIDs."""
    config = Config(
        years=50,
        population_size=200,
        seed=77,
        pair_bond_strength=0.9,
        violence_death_chance=0.0,
        aggression_production_penalty=0.3,
        conflict_base_probability=0.3,
    )
    sim = Simulation(config)
    sim.run()

    conflict_count = sim.society.event_type_counts.get("conflict", 0)
    assert conflict_count > 0, "No conflicts occurred — test is not exercising the engine"

    bond_events = []
    for evt in sim.society._event_window:
        if (evt.get("type") == "bond_dissolved"
                and evt.get("outcome", {}).get("reason") == "conflict_break"):
            bond_events.append(evt)

    # With 200 agents, 50 years, no death, and strong bonds, conflict bond breaks
    # should occur. If zero, the event emission is broken.
    assert len(bond_events) > 0, (
        f"No conflict bond_dissolved events found despite {conflict_count} conflicts. "
        f"Event emission is broken.")

    for evt in bond_events:
        assert len(evt["agent_ids"]) == 2, "bond_dissolved must have 2 agent UIDs"
        assert evt["outcome"]["reason"] == "conflict_break"
        assert "fighter" in evt["outcome"]
        assert "partner" in evt["outcome"]


def test_bystander_selection_is_deterministic():
    """Same seed must produce identical bystander selection across runs."""
    results = []
    for _ in range(2):
        config = Config(years=10, population_size=80, seed=42)
        sim = Simulation(config)
        sim.run()
        conflicts = [e for e in sim.society._event_window
                     if e.get("type") == "conflict"]
        results.append(conflicts)

    assert len(results[0]) == len(results[1]), "Different conflict counts across same seed"
    for e1, e2 in zip(results[0], results[1]):
        assert e1["agent_ids"] == e2["agent_ids"], "Conflict agent_ids differ across same seed"
