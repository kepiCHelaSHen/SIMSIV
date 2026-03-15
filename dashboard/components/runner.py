"""Simulation execution helpers for the SIMSIV dashboard."""

import streamlit as st
import pandas as pd
from config import Config
from simulation import Simulation


def build_config(params: dict, seed_val: int) -> Config:
    """Build a Config from sidebar params dict with a specific seed."""
    return Config(
        population_size=params["population_size"],
        years=params["years"],
        seed=seed_val,
        mating_system=params["mating_system"],
        female_choice_strength=params["female_choice_strength"],
        male_competition_intensity=params["male_competition_intensity"],
        pair_bond_strength=params["pair_bond_strength"],
        pair_bond_dissolution_rate=params["pair_bond_dissolution_rate"],
        max_mates_per_male=params["max_mates_per_male"],
        infidelity_enabled=params["infidelity_enabled"],
        infidelity_base_rate=params["infidelity_base_rate"],
        base_conception_chance=params["base_conception_chance"],
        mutation_sigma=params["mutation_sigma"],
        child_survival_base=params["child_survival_base"],
        birth_interval_years=params["birth_interval_years"],
        max_lifetime_births=params["max_lifetime_births"],
        resource_abundance=params["resource_abundance"],
        carrying_capacity=params["carrying_capacity"],
        tax_rate=params["tax_rate"],
        elite_privilege_multiplier=params["elite_privilege_multiplier"],
        scarcity_severity=params["scarcity_severity"],
        conflict_base_probability=params["conflict_base_probability"],
        violence_cost_health=params["violence_cost_health"],
        violence_death_chance=params["violence_death_chance"],
        law_strength=params["law_strength"],
        violence_punishment_strength=params["violence_punishment_strength"],
        property_rights_strength=params["property_rights_strength"],
        institutional_drift_rate=params["institutional_drift_rate"],
        emergent_institutions_enabled=params["emergent_institutions_enabled"],
        age_death_base=params["age_death_base"],
        mortality_base=params["mortality_base"],
    )


def run_single(params: dict) -> dict:
    """Run one simulation. Returns session state dict to merge."""
    config = build_config(params, int(params["seed"]))
    sim = Simulation(config)
    years = params["years"]
    rows = []
    progress = st.progress(0, text="Initializing...")
    for yr in range(1, years + 1):
        row = sim.tick()
        rows.append(row)
        if yr % max(1, years // 100) == 0 or yr == years:
            progress.progress(yr / years, text=f"Year {yr}/{years} -- Pop: {row.get('population', 0)}")
    progress.empty()
    return {
        "df": pd.DataFrame(rows),
        "df_std": None,
        "is_multi_run": False,
        "seeds_count": 1,
        "living": sim.society.get_living(),
        "society": sim.society,
        "config": config,
        "events": sim.society._event_window,
        "agent_names": {},
    }


def run_multi(params: dict) -> dict:
    """Run multiple seeds. Returns session state dict to merge."""
    seeds_count = params["seeds_count"]
    all_dfs = []
    last_sim = None
    progress = st.progress(0, text="Research Mode: initializing...")
    for i in range(seeds_count):
        seed_val = int(params["seed"]) + i
        progress.progress(i / seeds_count, text=f"Seed {seed_val} ({i+1}/{seeds_count})...")
        config = build_config(params, seed_val)
        sim = Simulation(config)
        rows = [sim.tick() for _ in range(params["years"])]
        df_i = pd.DataFrame(rows)
        df_i["seed"] = seed_val
        all_dfs.append(df_i)
        last_sim = sim
    progress.progress(1.0, text="Aggregating...")
    combined = pd.concat(all_dfs, ignore_index=True)
    numeric_cols = [c for c in combined.select_dtypes(include="number").columns if c != "seed"]
    df_mean = combined.groupby("year")[numeric_cols].mean().reset_index()
    df_std = combined.groupby("year")[numeric_cols].std().reset_index()
    progress.empty()
    return {
        "df": df_mean, "df_std": df_std,
        "is_multi_run": True, "seeds_count": seeds_count,
        "living": last_sim.society.get_living(),
        "society": last_sim.society,
        "config": last_sim.config,
        "events": last_sim.society._event_window,
        "agent_names": {},
    }
