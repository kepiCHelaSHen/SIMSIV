"""
Reproduction engine — conception, birth, child survival.

Paired agents attempt reproduction. In unrestricted mode, unpaired females
can also conceive with high-status males (extra-pair reproduction).

DD06 additions: birth interval, maternal age fertility decline, lifetime
birth cap, maternal health cost, grandparent survival bonus.
"""

from __future__ import annotations
import logging
import numpy as np
from models.agent import Agent, Sex, HERITABLE_TRAITS, breed

_log = logging.getLogger(__name__)


class ReproductionEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        females, males = society.get_mating_eligible()

        births = 0
        deaths_infant = 0

        # DD15: Precompute population trait means for heritability model
        living = society.get_living()
        pop_trait_means = {}
        if living:
            for trait in HERITABLE_TRAITS:
                vals = [getattr(a, trait) for a in living]
                pop_trait_means[trait] = float(np.mean(vals))

        for female in females:
            # DD06: Birth interval — skip if too soon after last birth
            if (female.last_birth_year is not None
                    and (society.year - female.last_birth_year) < config.birth_interval_years):
                continue

            # DD06: Lifetime birth cap
            if female.lifetime_births >= config.max_lifetime_births:
                continue

            # Conception chance based on fertility, resources, and health
            fertility_mod = female.fertility_base * 0.4 + 0.6  # range [0.6, 1.0]
            resource_mod = min(1.0, 0.5 + female.current_resources / 16.0)  # range [0.5, 1.0]
            # Health penalty only kicks in when seriously injured (below 0.5)
            health_mod = 1.0 if female.health > 0.5 else female.health * 2.0

            # DD13: Age-specific fertility curve
            # Adolescent subfertility (15-19)
            if female.age < 20:
                fertility_mod *= config.adolescent_fertility_fraction
            # Peak fertility around config.fertility_peak_age (default 24)
            elif female.age <= 28:
                pass  # full fertility
            # DD06: Maternal age fertility decline (past 30)
            elif female.age > 30:
                age_decline = (female.age - 30) * config.maternal_age_fertility_decline
                fertility_mod *= max(0.05, 1.0 - age_decline)

            # DD15: Maternal investment tradeoff — high investment = fewer but better-surviving offspring
            maternal_inv_mod = 1.0 - female.maternal_investment * 0.2  # [0.8, 1.0]
            conception_chance = config.base_conception_chance * fertility_mod * resource_mod * health_mod * maternal_inv_mod

            # DD27: Future-oriented agents wait for better conditions when resources low
            if (female.current_resources < 5.0
                    and female.future_orientation > 0.6):
                conception_chance *= 0.7

            # DD10: Birth timing sensitivity — higher conception in peak resource years
            if getattr(config, 'seasonal_cycle_enabled', False):
                phase = society.environment.seasonal_phase
                sensitivity = getattr(config, 'birth_timing_sensitivity', 0.2)
                conception_chance *= (1.0 + phase * sensitivity)

            # Paired females have higher conception (stable partnership)
            partner = None
            if female.is_bonded:
                partner = society.get_by_id(female.primary_partner_id)
                if partner and partner.alive:
                    # Partner health matters — but only if seriously injured
                    partner_health_mod = 1.0 if partner.health > 0.5 else 0.5 + partner.health
                    conception_chance *= 1.3 * partner_health_mod
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

            # ── Conception successful — determine genetic father ──────
            genetic_father = partner
            social_father = partner
            if female.epc_partner_id is not None:
                epc_male = society.get_by_id(female.epc_partner_id)
                if epc_male and epc_male.alive:
                    genetic_father = epc_male
                female.epc_partner_id = None  # consumed

            child = breed(female, genetic_father, rng, config, society.year,
                         id_counter=society.id_counter,
                         scarcity=society.environment.get_scarcity_level(),
                         pop_trait_means=pop_trait_means)
            # Social father also tracks child (for investment/kin support)
            if social_father and social_father.id != genetic_father.id:
                social_father.offspring_ids.append(child.id)
            society.add_agent(child)
            births += 1

            # DD06: Track reproduction state
            female.last_birth_year = society.year
            female.lifetime_births += 1

            # DD06: Maternal health cost
            female.health = max(0.1, female.health - config.maternal_health_cost)

            # DD13: Childbirth mortality risk
            cb_rate = config.childbirth_mortality_rate
            if female.health < 0.4:
                cb_rate *= 3.0  # high risk for unhealthy mothers
            # DD27: High endurance women survive childbirth better
            cb_rate *= max(0.5, 1.0 - female.endurance * 0.4)
            if rng.random() < cb_rate:
                female.die("childbirth", society.year)
                events.append({
                    "type": "death",
                    "year": society.year,
                    "agent_ids": [female.id],
                    "description": f"Agent {female.id} died: childbirth (age {female.age})",
                })
                events.append({
                    "type": "childbirth_death",
                    "year": society.year,
                    "agent_ids": [female.id, child.id],
                    "description": f"Mother {female.id} died in childbirth",
                })

            # ── Child survival check ─────────────────────────────────
            survival_chance = config.child_survival_base

            # Parental resources boost survival
            parental_resources = female.current_resources
            if social_father:
                investment_scale = social_father.paternity_confidence if config.infidelity_enabled else 1.0
                parental_resources += social_father.current_resources * 0.5 * investment_scale
            resource_factor = min(1.0, parental_resources / 12.0)
            survival_chance *= (0.6 + resource_factor * 0.4)

            # Pair bond stability helps
            if female.is_bonded_to(partner.id):
                survival_chance *= (1.0 + female.bond_strength_with(partner.id) * 0.2)

            # Environmental stress hurts
            scarcity = society.environment.get_scarcity_level()
            survival_chance *= (1.0 - scarcity * 0.4)

            # Kin network support (number of living relatives)
            kin_count = sum(1 for oid in female.offspring_ids
                           if (a := society.get_by_id(oid)) and a.alive and a.age > 10)
            kin_bonus = min(0.1, kin_count * 0.02)
            survival_chance += kin_bonus

            # DD15: High maternal investment boosts child survival
            survival_chance *= (1.0 + female.maternal_investment * 0.15)  # up to +15%
            # DD27: Conscientious parents invest more consistently
            survival_chance *= (0.8 + female.conscientiousness * 0.4)

            # DD06: Grandparent survival bonus
            for pid in female.parent_ids:
                if pid is not None:
                    gp = society.get_by_id(pid)
                    if gp and gp.alive:
                        survival_chance += config.grandparent_survival_bonus
                        break  # one grandparent bonus is enough

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
