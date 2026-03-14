"""
Reproduction engine — conception, birth, child survival.

Paired agents attempt reproduction. In unrestricted mode, unpaired females
can also conceive with high-status males (extra-pair reproduction).
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent, Sex, breed


class ReproductionEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        females, males = society.get_mating_eligible()

        births = 0
        deaths_infant = 0

        for female in females:
            # Conception chance based on fertility and resources
            fertility_mod = female.fertility_base * 0.5 + 0.5  # range [0.5, 1.0]
            resource_mod = min(1.0, female.current_resources / 8.0)  # well-resourced = better
            conception_chance = config.base_conception_chance * fertility_mod * resource_mod

            # Paired females have higher conception (stable partnership)
            partner = None
            if female.pair_bond_id is not None:
                partner = society.get_by_id(female.pair_bond_id)
                if partner and partner.alive:
                    conception_chance *= 1.3  # pair bond bonus
                else:
                    partner = None

            # Unrestricted mode: unpaired females can conceive with nearby high-status males
            if partner is None:
                if config.mating_system == "unrestricted" and males:
                    # Pick a male weighted by status
                    weights = np.array([m.mate_value for m in males])
                    total = weights.sum()
                    if total > 0:
                        weights /= total
                        partner = males[rng.choice(len(males), p=weights)]
                    conception_chance *= 0.5  # lower chance without pair bond

            if partner is None:
                continue

            if rng.random() > conception_chance:
                continue

            # ── Conception successful — create offspring ──────────────
            child = breed(female, partner, rng, config, society.year)
            society.add_agent(child)
            births += 1

            # ── Child survival check ─────────────────────────────────
            survival_chance = config.child_survival_base

            # Parental resources boost survival
            parental_resources = female.current_resources
            if partner:
                parental_resources += partner.current_resources * 0.5
            resource_factor = min(1.0, parental_resources / 12.0)
            survival_chance *= (0.6 + resource_factor * 0.4)

            # Pair bond stability helps
            if female.pair_bond_id == partner.id:
                survival_chance *= (1.0 + female.pair_bond_strength * 0.2)

            # Environmental stress hurts
            scarcity = society.environment.get_scarcity_level()
            survival_chance *= (1.0 - scarcity * 0.4)

            # Kin network support (number of living relatives)
            kin_count = sum(1 for oid in female.offspring_ids
                           if (a := society.get_by_id(oid)) and a.alive and a.age > 10)
            kin_bonus = min(0.1, kin_count * 0.02)
            survival_chance += kin_bonus

            survival_chance = min(0.98, max(0.1, survival_chance))

            if rng.random() > survival_chance:
                child.die("infant_mortality", society.year)
                deaths_infant += 1
                events.append({
                    "type": "infant_death",
                    "year": society.year,
                    "agent_ids": [child.id, female.id, partner.id],
                    "description": f"Infant {child.id} died (survival_chance={survival_chance:.2f})",
                })
            else:
                events.append({
                    "type": "birth",
                    "year": society.year,
                    "agent_ids": [child.id, female.id, partner.id],
                    "description": (f"Born: {child.id} ({child.sex.value}) "
                                    f"parents={female.id},{partner.id}"),
                })

            # Reproduction costs resources
            female.current_resources = max(0, female.current_resources - 2.0)

        if births > 0:
            events.append({
                "type": "reproduction_summary",
                "year": society.year,
                "agent_ids": [],
                "description": f"Births: {births}, Infant deaths: {deaths_infant}",
            })

        return events
