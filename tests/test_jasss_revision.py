"""Tests for JASSS Major Revision architectural requirements."""
import numpy as np
import pytest
import yaml
from config import Config
from models.agent import Agent, Sex, breed, create_initial_population, IdCounter, HERITABLE_TRAITS


def test_config_defaults_match_autosim_best():
    cfg = Config()
    with open("autosim/best_config.yaml") as f:
        best = yaml.safe_load(f)["parameters"]
    mismatches = []
    for param, best_val in best.items():
        cfg_val = getattr(cfg, param, "MISSING")
        if cfg_val == "MISSING":
            mismatches.append(f"{param}: MISSING")
        elif abs(float(cfg_val) - float(best_val)) > 0.0001:
            mismatches.append(f"{param}: config={cfg_val}, best={best_val}")
    assert not mismatches, f"{len(mismatches)} mismatches:\n" + "\n".join(mismatches)


def test_ma_offspring_inherit_exact_genotype():
    rng = np.random.default_rng(42)
    config = Config(years=1, population_size=50, seed=42)
    idc = IdCounter()
    pop = create_initial_population(rng, config, 50, idc)
    pop_means = {t: float(np.mean([getattr(a, t) for a in pop])) for t in HERITABLE_TRAITS}
    parent1 = pop[0]
    parent1._is_ma = True
    parent1.aggression_propensity = 1.0
    parent1.cooperation_propensity = 0.0
    parent1.genotype = {t: getattr(parent1, t) for t in HERITABLE_TRAITS}
    parent2 = pop[25]
    for _ in range(20):
        child = breed(parent1, parent2, rng, config, year=1, id_counter=idc, pop_trait_means=pop_means)
        assert child.aggression_propensity == 1.0, f"MA aggression mutated: {child.aggression_propensity}"
        assert child.cooperation_propensity == 0.0, f"MA cooperation mutated: {child.cooperation_propensity}"
        assert getattr(child, '_is_ma', False), "MA flag not propagated"


def test_normal_offspring_still_mutate():
    rng = np.random.default_rng(42)
    config = Config(years=1, population_size=50, seed=42)
    idc = IdCounter()
    pop = create_initial_population(rng, config, 50, idc)
    pop_means = {t: float(np.mean([getattr(a, t) for a in pop])) for t in HERITABLE_TRAITS}
    parent1 = pop[0]
    parent2 = pop[25]
    children_agg = []
    for _ in range(20):
        child = breed(parent1, parent2, rng, config, year=1, id_counter=idc, pop_trait_means=pop_means)
        children_agg.append(child.aggression_propensity)
    assert np.std(children_agg) > 0.01, "No mutation in normal offspring"


from collections import deque
from models.society import Society


def test_event_window_is_deque():
    cfg = Config(population_size=30, years=1, seed=1)
    rng = np.random.default_rng(1)
    soc = Society(cfg, rng)
    assert isinstance(soc._event_window, deque)
    assert soc._event_window.maxlen == 500


from simulation import Simulation


def test_selection_differential_metrics_exist():
    config = Config(years=20, population_size=100, seed=42)
    sim = Simulation(config)
    sim.run()
    last = sim.metrics.rows[-1]
    for key in ["mu_pop_cooperation", "mu_eligible_cooperation",
                "mu_parents_cooperation", "selection_differential_S"]:
        assert key in last, f"Missing metric: {key}"
    if last["mu_parents_cooperation"] is not None and last["mu_eligible_cooperation"] is not None:
        expected_S = last["mu_parents_cooperation"] - last["mu_eligible_cooperation"]
        assert abs(last["selection_differential_S"] - expected_S) < 0.001
