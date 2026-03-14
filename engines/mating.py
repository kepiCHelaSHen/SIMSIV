"""
Mating engine — mate search, pair bond formation and dissolution.

Default: unrestricted competition (null hypothesis).
Female choice: probabilistic weighted by mate_value.
Male competition: status + aggression weighted contest.
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent, Sex


class MatingEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []

        # ── Dissolve existing pair bonds ─────────────────────────────
        events.extend(self._dissolve_bonds(society, config, rng))

        # ── New pair formation ───────────────────────────────────────
        events.extend(self._form_pairs(society, config, rng))

        return events

    def _dissolve_bonds(self, society, config, rng) -> list[dict]:
        events = []
        living = society.get_living()

        for agent in living:
            if agent.pair_bond_id is None:
                continue
            partner = society.get_by_id(agent.pair_bond_id)

            # Dissolve if partner is dead
            if partner is None or not partner.alive:
                agent.pair_bond_id = None
                agent.pair_bond_strength = 0.0
                continue

            # Only process from one side (lower id dissolves for the pair)
            if agent.id > partner.id:
                continue

            # Dissolution probability — modified by bond strength and satisfaction
            base_rate = config.pair_bond_dissolution_rate
            # Stronger bonds dissolve less
            strength_factor = 1.0 - agent.pair_bond_strength * 0.5
            # Resource stress increases dissolution
            resource_stress = max(0, 1.0 - (agent.current_resources + partner.current_resources) / 10.0)
            dissolution_chance = base_rate * strength_factor * (1.0 + resource_stress * 0.5)

            if rng.random() < dissolution_chance:
                agent.pair_bond_id = None
                agent.pair_bond_strength = 0.0
                partner.pair_bond_id = None
                partner.pair_bond_strength = 0.0

                # Negative memory of dissolution
                agent.remember(partner.id, -0.15)
                partner.remember(agent.id, -0.15)

                events.append({
                    "type": "bond_dissolved",
                    "year": society.year,
                    "agent_ids": [agent.id, partner.id],
                    "description": f"Pair bond dissolved: {agent.id} & {partner.id}",
                })

        return events

    def _form_pairs(self, society, config, rng) -> list[dict]:
        events = []
        females, males = society.get_mating_eligible()

        # Filter to unpaired (or allow extra-pair if unrestricted)
        if config.monogamy_enforced:
            females = [f for f in females if f.pair_bond_id is None]
            males = [m for m in males if m.pair_bond_id is None]
        else:
            # In unrestricted mode, unpaired agents seek bonds
            # Paired agents may still mate (handled in reproduction) but don't form new bonds
            females = [f for f in females if f.pair_bond_id is None]
            # Males can pursue regardless in unrestricted mode, but limit pool
            available_males = [m for m in males if m.pair_bond_id is None]
            # Some paired high-status males also enter the pool
            for m in males:
                if m.pair_bond_id is not None and m.current_status > 0.7 and rng.random() < 0.2:
                    available_males.append(m)
            males = available_males

        if not females or not males:
            return events

        # Subsample — not everyone seeks a mate every year
        n_seeking_f = max(1, int(len(females) * config.mating_pool_fraction))
        n_seeking_m = max(1, int(len(males) * config.mating_pool_fraction))
        seeking_females = list(rng.choice(females, size=min(n_seeking_f, len(females)), replace=False))
        seeking_males = list(rng.choice(males, size=min(n_seeking_m, len(males)), replace=False))

        # Track who paired this tick to avoid double-pairing
        paired_this_tick = set()

        # Each seeking female evaluates available males
        rng.shuffle(seeking_females)
        for female in seeking_females:
            if female.id in paired_this_tick:
                continue

            candidates = [m for m in seeking_males
                          if m.id not in paired_this_tick and m.id != female.id]
            if not candidates:
                break

            # ── Female choice: weighted by mate_value ────────────────
            weights = np.array([m.mate_value for m in candidates])

            # Trust bonus — prefer known cooperative males
            for i, m in enumerate(candidates):
                trust = female.trust_of(m.id)
                weights[i] *= (0.7 + trust * 0.6)  # range [0.7, 1.3]

                # Aggression penalty — females avoid overtly aggressive males
                # High aggression is risky for pair bond stability and offspring safety
                agg_penalty = 1.0 - m.aggression_propensity * 0.3  # range [0.7, 1.0]
                coop_bonus = 1.0 + m.cooperation_propensity * 0.2  # range [1.0, 1.2]
                weights[i] *= agg_penalty * coop_bonus

            # Apply female choice strength (0=random, 1=deterministic best)
            if config.female_choice_strength < 1.0:
                # Soften weights — blend toward uniform
                uniform = np.ones_like(weights) / len(weights)
                total_w = weights.sum()
                if total_w > 0:
                    weights = weights / total_w
                weights = (config.female_choice_strength * weights +
                           (1 - config.female_choice_strength) * uniform)

            total = weights.sum()
            if total <= 0:
                continue
            weights /= total

            chosen_male = candidates[rng.choice(len(candidates), p=weights)]

            # ── Male competition: does he accept / compete? ──────────
            # In unrestricted mode, males always accept.
            # Male competition affects *which* male wins if multiple pursue same female.
            # Simplified for v1: female choice dominates.

            # Form pair bond
            female.pair_bond_id = chosen_male.id
            chosen_male.pair_bond_id = female.id
            initial_strength = config.pair_bond_strength * rng.uniform(0.5, 1.0)
            female.pair_bond_strength = initial_strength
            chosen_male.pair_bond_strength = initial_strength

            # Positive memory
            female.remember(chosen_male.id, 0.1)
            chosen_male.remember(female.id, 0.1)

            paired_this_tick.add(female.id)
            paired_this_tick.add(chosen_male.id)

            events.append({
                "type": "pair_bond_formed",
                "year": society.year,
                "agent_ids": [female.id, chosen_male.id],
                "description": (f"Pair bond: {female.id}(F) & {chosen_male.id}(M) "
                                f"strength={initial_strength:.2f}"),
            })

        # ── Strengthen existing bonds ────────────────────────────────
        for agent in society.get_living():
            if agent.pair_bond_id is not None and agent.id not in paired_this_tick:
                agent.pair_bond_strength = min(1.0, agent.pair_bond_strength + 0.05)

        return events
