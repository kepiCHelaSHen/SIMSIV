"""
Resource engine — distributes survival and status resources each tick.

Resources are two-dimensional:
  - Survival resources: needed to stay alive and reproduce
  - Status resources: proxy for dominance, affects mate value
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent


class ResourceEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()
        if not living:
            return events

        env_multiplier = society.environment.get_resource_multiplier()
        pop_size = len(living)

        # Total resources available this tick, scaled by carrying capacity pressure
        capacity_ratio = pop_size / config.carrying_capacity
        crowding_penalty = max(0.3, 1.0 - max(0, capacity_ratio - 0.5) * 0.8)

        total_pool = config.base_resource_per_agent * pop_size * env_multiplier * crowding_penalty

        # Split into survival and status pools
        status_pool = total_pool * config.status_resource_fraction
        survival_pool = total_pool - status_pool

        # ── Survival resources: distributed somewhat equally ─────────
        # Everyone gets a base share; intelligence gives a bonus
        base_share = survival_pool / pop_size * 0.7  # 70% equal
        competitive_pool = survival_pool * 0.3  # 30% competitive

        # Intelligence-weighted competitive share
        intel_sum = sum(a.intelligence_proxy for a in living) or 1.0

        for agent in living:
            # Base survival resources
            share = base_share + competitive_pool * (agent.intelligence_proxy / intel_sum)

            # Resource decay — agents consume resources each year
            agent.current_resources *= 0.5  # retain half from last year
            agent.current_resources += share

        # ── Cooperation bonus: mutual aid among trusted allies ───────
        # Cooperative agents share resources with agents they trust,
        # creating a fitness advantage for cooperation networks.
        for agent in living:
            if agent.cooperation_propensity < 0.3:
                continue  # low-coop agents don't share
            # Find trusted allies
            allies = []
            for other_id, trust in agent.reputation_ledger.items():
                if trust > 0.6:
                    other = society.get_by_id(other_id)
                    if other and other.alive and other.cooperation_propensity > 0.3:
                        allies.append(other)
            if allies:
                # Share a small fraction of resources with needy allies
                share_rate = agent.cooperation_propensity * 0.05
                share_amount = agent.current_resources * share_rate
                if share_amount > 0.5:  # only share if you have enough
                    per_ally = share_amount / len(allies)
                    agent.current_resources -= share_amount
                    for ally in allies:
                        ally.current_resources += per_ally
                        # Strengthen mutual trust
                        agent.remember(ally.id, 0.03)
                        ally.remember(agent.id, 0.03)

        # ── Status resources: winner-take-more ───────────────────────
        # Status-driven agents compete; top agents get disproportionate share
        # Cooperation also contributes to status (social capital)
        status_scores = []
        for a in living:
            score = (a.status_drive * 0.35 + a.current_status * 0.25 +
                     a.cooperation_propensity * 0.15 +
                     a.aggression_propensity * 0.1 + a.intelligence_proxy * 0.15)
            status_scores.append((a, score))

        total_score = sum(s for _, s in status_scores) or 1.0

        for agent, score in status_scores:
            share = status_pool * (score / total_score)
            agent.current_status = max(0.0, min(1.0,
                agent.current_status * 0.7 + (share / (status_pool / pop_size + 0.01)) * 0.3
            ))

        # Elite privilege multiplier
        if config.elite_privilege_multiplier > 1.0:
            threshold = np.percentile(
                [a.current_status for a in living], 90
            )
            for a in living:
                if a.current_status >= threshold:
                    a.current_resources *= config.elite_privilege_multiplier

        return events
