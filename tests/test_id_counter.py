"""Tests for per-simulation IdCounter isolation."""
import pytest
from models.agent import IdCounter
from config import Config
from simulation import Simulation


def test_counter_starts_at_one():
    c = IdCounter()
    assert c.next() == 1


def test_counter_monotonic():
    c = IdCounter()
    ids = [c.next() for _ in range(100)]
    assert ids == list(range(1, 101))


def test_counter_reset():
    c = IdCounter()
    c.next(); c.next()
    c.reset()
    assert c.next() == 1


def test_two_simulations_have_independent_counters():
    """Running two Simulation instances should not share ID state."""
    s1 = Simulation(Config(population_size=20, years=1, seed=1))
    s2 = Simulation(Config(population_size=20, years=1, seed=2))
    ids1 = list(s1.society.agents.keys())
    ids2 = list(s2.society.agents.keys())
    assert len(ids1) == len(set(ids1)), "Duplicate IDs in simulation 1"
    assert len(ids2) == len(set(ids2)), "Duplicate IDs in simulation 2"
    assert min(ids1) == 1
    assert min(ids2) == 1
