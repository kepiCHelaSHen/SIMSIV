"""
Mortality engine — aging, health decay, natural death, pair bond cleanup.
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent


class MortalityEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()

        for agent in living:
            agent.age += 1

            # Health decay — accelerates with age
            age_factor = max(0, agent.age - 30) * 0.002  # faster after 30
            decay = config.health_decay_per_year + age_factor
            agent.health = max(0.0, agent.health - decay)

            # Scarcity stress
            scarcity = society.environment.get_scarcity_level()
            if scarcity > 0:
                agent.health = max(0.0, agent.health - scarcity * 0.03)

            # Low resources hurt health
            if agent.current_resources < 2.0:
                agent.health = max(0.0, agent.health - 0.02)

            # ── Death checks ─────────────────────────────────────────
            died = False

            # Health death
            if agent.health <= config.min_health_survival:
                agent.die("health_failure", society.year)
                died = True

            # Age-based death (probability increases sharply past base age)
            if not died and agent.age > config.age_death_base - config.age_death_variance:
                years_past = agent.age - (config.age_death_base - config.age_death_variance)
                death_p = 0.01 * (years_past ** 1.5) / config.age_death_variance
                if rng.random() < death_p:
                    agent.die("old_age", society.year)
                    died = True

            # Background mortality (accidents, disease)
            if not died and rng.random() < config.mortality_base:
                agent.die("accident", society.year)
                died = True

            if died:
                # Clean up pair bond
                if agent.pair_bond_id is not None:
                    partner = society.get_by_id(agent.pair_bond_id)
                    if partner and partner.alive:
                        partner.pair_bond_id = None
                        partner.pair_bond_strength = 0.0
                events.append({
                    "type": "death",
                    "year": society.year,
                    "agent_ids": [agent.id],
                    "description": f"Agent {agent.id} died: {agent.cause_of_death} (age {agent.age})",
                })

        return events
