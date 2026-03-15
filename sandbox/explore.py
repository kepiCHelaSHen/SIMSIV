"""
IPython exploration harness for SIMSIV.

Usage:
    ipython -i sandbox/explore.py
    ipython -i sandbox/explore.py -- --years 50 --pop 200 --seed 42

Drops you into a live IPython session with a completed simulation run
and all key objects available for inspection.
"""

import sys
import os
import argparse

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import numpy as np
import pandas as pd
from config import Config
from simulation import Simulation
from models.agent import Agent
from models.society import Society


def parse_args():
    parser = argparse.ArgumentParser(description="SIMSIV exploration harness")
    parser.add_argument("--years", type=int, default=20, help="Simulation years (default: 20)")
    parser.add_argument("--pop", type=int, default=100, help="Initial population (default: 100)")
    parser.add_argument("--seed", type=int, default=1, help="Random seed (default: 1)")
    parser.add_argument("--scenario", type=str, default=None, help="Scenario name (optional)")
    return parser.parse_args()


def run(years=20, pop=100, seed=1, scenario=None):
    """Run a simulation and return (sim, df) tuple."""
    config = Config(years=years, population_size=pop, seed=seed)

    if scenario:
        from experiments.scenarios import apply_scenario
        apply_scenario(config, scenario)

    sim = Simulation(config)
    rows = []

    def collect(year, row):
        rows.append(row)
        if year % 5 == 0:
            alive = sim.society.population_size()
            print(f"  yr {year:3d}  pop {alive:4d}")

    print(f"Running: {years}yr, pop={pop}, seed={seed}" +
          (f", scenario={scenario}" if scenario else ""))
    sim.run(callback=collect)

    df = pd.DataFrame(rows)
    print(f"Done. Final pop: {sim.society.population_size()}, {len(df)} rows collected.\n")
    return sim, df


def agents(sim):
    """Return list of all living agents."""
    return list(sim.society.agents.values())


def agent_df(sim):
    """Return a DataFrame of all living agents with key traits."""
    records = []
    for a in sim.society.agents.values():
        records.append({
            "id": a.id, "age": a.age, "sex": a.sex.value,
            "life_stage": a.life_stage,
            "health": round(a.health, 3),
            "resources": round(a.current_resources, 2),
            "agg": round(a.aggression_propensity, 3),
            "coop": round(a.cooperation_propensity, 3),
            "intel": round(a.intelligence_proxy, 3),
            "status": round(a.current_status, 3),
            "prestige": round(a.prestige_score, 3),
            "dominance": round(a.dominance_score, 3),
            "reputation": round(a.reputation, 3),
            "trauma": round(a.trauma_score, 3),
            "faction_id": a.faction_id,
            "bonded": a.is_bonded,
            "offspring": len(a.offspring_ids),
            "foraging": round(a.foraging_skill, 3),
            "social": round(a.social_skill, 3),
            "hierarchy_belief": round(a.hierarchy_belief, 3),
            "cooperation_norm": round(a.cooperation_norm, 3),
        })
    return pd.DataFrame(records).set_index("id")


if __name__ == "__main__":
    args = parse_args()
    sim, df = run(years=args.years, pop=args.pop, seed=args.seed, scenario=args.scenario)

    # Convenience aliases
    soc = sim.society
    cfg = sim.config
    pop = agents(sim)
    adf = agent_df(sim)

    print("Available objects:")
    print("  sim   — Simulation instance")
    print("  soc   — Society (sim.society)")
    print("  cfg   — Config (sim.config)")
    print("  df    — Metrics DataFrame (one row per year)")
    print("  pop   — List of living agents")
    print("  adf   — Agent DataFrame (key traits)")
    print()
    print("Helpers:  agents(sim), agent_df(sim), run(years, pop, seed, scenario)")
