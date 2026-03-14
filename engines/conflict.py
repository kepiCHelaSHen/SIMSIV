"""
Conflict engine — models violence from jealousy, resource pressure,
status challenges, retaliation, and random aggression.
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent, Sex


class ConflictEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()
        if len(living) < 2:
            return events

        conflicts = 0

        for agent in living:
            if not agent.alive:  # might have died earlier this tick
                continue

            # ── Calculate conflict probability ───────────────────────
            base_p = config.conflict_base_probability * agent.aggression_propensity

            # Jealousy trigger: bonded agent whose partner is attractive to others
            jealousy_boost = 0.0
            if agent.pair_bond_id is not None and agent.sex == Sex.MALE:
                partner = society.get_by_id(agent.pair_bond_id)
                if partner and partner.alive:
                    if partner.attractiveness_base > 0.6:
                        jealousy_boost = (agent.jealousy_sensitivity *
                                          config.jealousy_conflict_multiplier * 0.1)

            # Resource pressure: low resources increase aggression
            resource_stress = max(0, 1.0 - agent.current_resources / 5.0) * 0.1

            # Status drive: ambitious agents challenge more
            status_drive_boost = agent.status_drive * 0.05

            total_p = base_p + jealousy_boost + resource_stress + status_drive_boost

            # Institutional suppression — law reduces conflict probability
            suppression = config.law_strength * config.violence_punishment_strength
            total_p *= (1.0 - suppression * 0.8)

            # Cooperation dampens aggression
            total_p *= (1.0 - agent.cooperation_propensity * 0.3)

            total_p = max(0.0, min(0.5, total_p))

            if rng.random() > total_p:
                continue

            # ── Select target ────────────────────────────────────────
            target = self._select_target(agent, living, society, rng)
            if target is None or not target.alive:
                continue

            # ── Resolve conflict ─────────────────────────────────────
            event = self._resolve_conflict(agent, target, society, config, rng)
            if event:
                events.append(event)
                conflicts += 1

        return events

    def _select_target(self, aggressor: Agent, living: list[Agent],
                       society, rng: np.random.Generator) -> Agent | None:
        """Pick a conflict target. Biased toward rivals and low-trust agents."""
        candidates = [a for a in living
                      if a.id != aggressor.id and a.alive and a.sex == aggressor.sex]
        if not candidates:
            return None

        weights = np.ones(len(candidates))
        for i, c in enumerate(candidates):
            # Low trust = more likely target
            trust = aggressor.trust_of(c.id)
            weights[i] *= (1.5 - trust)

            # Rival for same mate = high priority
            if (aggressor.pair_bond_id is not None and
                c.pair_bond_id is not None and
                aggressor.pair_bond_id == c.pair_bond_id):
                weights[i] *= 3.0

            # Similar status = status challenge
            status_diff = abs(aggressor.current_status - c.current_status)
            if status_diff < 0.2:
                weights[i] *= 1.5

        total = weights.sum()
        if total <= 0:
            return None
        weights /= total

        return candidates[rng.choice(len(candidates), p=weights)]

    def _resolve_conflict(self, aggressor: Agent, target: Agent,
                          society, config, rng) -> dict | None:
        """Resolve a conflict. Returns event dict."""
        # Combat power: aggression + status + health + risk tolerance
        agg_power = (aggressor.aggression_propensity * 0.3 +
                     aggressor.current_status * 0.25 +
                     aggressor.health * 0.25 +
                     aggressor.risk_tolerance * 0.2)
        tgt_power = (target.aggression_propensity * 0.3 +
                     target.current_status * 0.25 +
                     target.health * 0.25 +
                     target.risk_tolerance * 0.2)

        # Probabilistic outcome
        agg_chance = agg_power / (agg_power + tgt_power + 0.01)

        aggressor_wins = rng.random() < agg_chance
        winner = aggressor if aggressor_wins else target
        loser = target if aggressor_wins else aggressor

        # ── Costs to loser ───────────────────────────────────────────
        loser.health = max(0.0, loser.health - config.violence_cost_health)
        resource_loss = loser.current_resources * config.violence_cost_resources
        loser.current_resources = max(0, loser.current_resources - resource_loss)

        # Winner takes some resources and gains status
        winner.current_resources += resource_loss * 0.5
        winner.current_status = min(1.0, winner.current_status + 0.05)
        loser.current_status = max(0.0, loser.current_status - 0.05)

        # Both suffer minor health cost (fighting is costly)
        winner.health = max(0.0, winner.health - config.violence_cost_health * 0.3)

        # Death check for loser
        death = False
        if rng.random() < config.violence_death_chance:
            loser.die("violence", society.year)
            death = True
            # Break pair bond
            if loser.pair_bond_id is not None:
                partner = society.get_by_id(loser.pair_bond_id)
                if partner:
                    partner.pair_bond_id = None
                    partner.pair_bond_strength = 0.0

        # ── Reputation updates ───────────────────────────────────────
        # Both fighters' public reputation suffers (violence is socially costly)
        aggressor.reputation = max(0.0, aggressor.reputation - 0.05)
        aggressor.remember(target.id, -0.2)
        target.remember(aggressor.id, -0.3)

        # ── Pair bond destabilization ────────────────────────────────
        # Violence threatens pair bonds — partner may leave
        for fighter in [aggressor, target]:
            if fighter.alive and fighter.pair_bond_id is not None:
                partner = society.get_by_id(fighter.pair_bond_id)
                if partner and partner.alive:
                    # Partner's tolerance depends on fighter's aggression history
                    leave_chance = fighter.aggression_propensity * 0.15
                    if rng.random() < leave_chance:
                        fighter.pair_bond_id = None
                        fighter.pair_bond_strength = 0.0
                        partner.pair_bond_id = None
                        partner.pair_bond_strength = 0.0
                        partner.remember(fighter.id, -0.25)

        # Institutional punishment for aggressor
        if config.violence_punishment_strength > 0:
            penalty = config.violence_punishment_strength * 0.1
            aggressor.reputation = max(0, aggressor.reputation - penalty)
            aggressor.current_resources = max(0,
                aggressor.current_resources - penalty * 5)

        return {
            "type": "conflict",
            "year": society.year,
            "agent_ids": [aggressor.id, target.id],
            "description": (f"Conflict: {aggressor.id} vs {target.id} → "
                            f"{'winner' if aggressor_wins else 'loser'}: {aggressor.id}"
                            f"{' (DEATH)' if death else ''}"),
            "outcome": {
                "aggressor": aggressor.id,
                "target": target.id,
                "winner": winner.id,
                "loser": loser.id,
                "death": death,
            },
        }
