"""
Mating engine — mate search, pair bond formation, dissolution, infidelity.

Deep Dive 01 implementation:
- Enhanced female choice (age-dependent, strong aggression penalty)
- Male competition with contest injury risk
- Extra-pair copulation (EPC) with detection and paternity uncertainty
- Widowhood mourning period
- Multi-bond support (polygyny via partner_ids list)
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent, Sex


class MatingEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []

        # Clear per-tick EPC flags
        for a in society.get_living():
            a.epc_partner_id = None

        # Phase 1: Clean stale bonds (dead partners)
        events.extend(self._clean_stale_bonds(society, config, rng))

        # Phase 2: Dissolve living-pair bonds
        events.extend(self._dissolve_bonds(society, config, rng))

        # Phase 3: Form new pairs
        events.extend(self._form_pairs(society, config, rng))

        # Phase 4: Extra-pair copulation
        if config.infidelity_enabled:
            events.extend(self._process_infidelity(society, config, rng))

        # Phase 5: Strengthen surviving bonds
        self._strengthen_bonds(society, config)

        return events

    # ── Phase 1: Clean stale bonds ─────────────────────────────────

    def _clean_stale_bonds(self, society, config, rng) -> list[dict]:
        """Remove bonds where partner is dead. Sets mourning state."""
        events = []
        for agent in society.get_living():
            for pid in list(agent.partner_ids):
                partner = society.get_by_id(pid)
                if not partner or not partner.alive:
                    agent.remove_bond(pid)
                    agent.last_partner_death_year = society.year
        return events

    # ── Phase 2: Dissolve bonds ────────────────────────────────────

    def _dissolve_bonds(self, society, config, rng) -> list[dict]:
        events = []
        processed = set()

        for agent in society.get_living():
            for pid in list(agent.partner_ids):
                pair_key = (min(agent.id, pid), max(agent.id, pid))
                if pair_key in processed:
                    continue
                processed.add(pair_key)

                partner = society.get_by_id(pid)
                if not partner or not partner.alive:
                    continue

                bond_str = agent.bond_strength_with(pid)
                base_rate = config.pair_bond_dissolution_rate

                # Strong bonds resist dissolution
                strength_factor = 1.0 - bond_str * 0.5

                # Resource stress
                combined_res = agent.current_resources + partner.current_resources
                resource_stress = max(0, 1.0 - combined_res / 10.0)

                # Partner quality: low mate value increases dissolution
                female = agent if agent.sex == Sex.FEMALE else partner
                male = partner if agent.sex == Sex.FEMALE else agent
                quality_factor = max(0, 0.5 - male.mate_value) * 0.3

                dissolution_chance = base_rate * strength_factor * (
                    1.0 + resource_stress * 0.5 + quality_factor
                )
                dissolution_chance = min(0.5, dissolution_chance)

                if rng.random() < dissolution_chance:
                    agent.remove_bond(pid)
                    partner.remove_bond(agent.id)
                    agent.remember(pid, -0.15)
                    partner.remember(agent.id, -0.15)
                    events.append({
                        "type": "bond_dissolved",
                        "year": society.year,
                        "agent_ids": [agent.id, pid],
                        "description": f"Pair bond dissolved: {agent.id} & {pid}",
                    })

        return events

    # ── Phase 3: Form new pairs ────────────────────────────────────

    def _form_pairs(self, society, config, rng) -> list[dict]:
        events = []
        females, males = society.get_mating_eligible()

        # Filter by bond capacity and mourning
        if config.monogamy_enforced:
            females = [f for f in females if not f.is_bonded
                       and not f.is_in_mourning(society.year, config.widowhood_mourning_years)]
            males = [m for m in males if not m.is_bonded
                     and not m.is_in_mourning(society.year, config.widowhood_mourning_years)]
        else:
            females = [f for f in females
                       if f.bond_count < config.max_mates_per_female
                       and not f.is_in_mourning(society.year, config.widowhood_mourning_years)]
            available_males = [m for m in males
                               if not m.is_bonded
                               and not m.is_in_mourning(society.year, config.widowhood_mourning_years)]
            # High-status bonded males can pursue additional bonds
            for m in males:
                if (m.is_bonded
                        and m.bond_count < config.max_mates_per_male
                        and (m.prestige_score + m.dominance_score) > 0.7
                        and rng.random() < 0.2):
                    available_males.append(m)
            males = available_males

        if not females or not males:
            return events

        # Subsample seeking pool
        n_f = max(1, int(len(females) * config.mating_pool_fraction))
        n_m = max(1, int(len(males) * config.mating_pool_fraction))
        seeking_females = list(rng.choice(females, size=min(n_f, len(females)), replace=False))
        seeking_males = list(rng.choice(males, size=min(n_m, len(males)), replace=False))

        paired_this_tick = set()
        rng.shuffle(seeking_females)

        for female in seeking_females:
            if female.id in paired_this_tick:
                continue

            candidates = [m for m in seeking_males
                          if m.id not in paired_this_tick and m.id != female.id
                          and not female.is_bonded_to(m.id)]
            if not candidates:
                break

            # DD18: Proximity-weighted mate evaluation
            proximity_enabled = getattr(config, 'proximity_tiers_enabled', False)
            if proximity_enabled:
                female_household = society.household_of(female)
                female_neighborhood = set(female.neighborhood_ids) | female_household
                band_weight = getattr(config, 'band_mate_weight', 0.3)

            # ── Female choice: age-dependent choosiness ────────────
            choosiness = config.female_choice_strength
            # DD22: Youth females are more choosy
            if (getattr(config, 'life_stages_enabled', False)
                    and female.life_stage == "YOUTH"):
                choosiness = min(1.0, choosiness * 1.15)
            if female.age > 30:
                choosiness += config.female_choosiness_age_effect * (female.age - 30)
            choosiness = max(0.1, min(1.0, choosiness))

            # Resource desperation: poor females are less choosy
            if female.current_resources < 3.0:
                choosiness *= 0.7

            weights = np.array([m.mate_value for m in candidates], dtype=float)

            for i, m in enumerate(candidates):
                # Trust bonus — DD15: emotional intelligence amplifies trust reading
                trust = female.trust_of(m.id)
                ei_boost = 1.0 + female.emotional_intelligence * 0.3  # [1.0, 1.3]
                # DD26: Social skill sharpens female's character assessment
                social_boost = 1.0
                if getattr(config, 'skills_enabled', False):
                    social_boost = 1.0 + female.social_skill * 0.2
                weights[i] *= (0.6 + trust * 0.8) * ei_boost * social_boost

                # Aggression penalty (STRONG — key sexual selection driver)
                agg_penalty = 1.0 - m.aggression_propensity * 0.5  # [0.5, 1.0]
                weights[i] *= agg_penalty

                # Cooperation bonus (STRONG)
                coop_bonus = 1.0 + m.cooperation_propensity * 0.4  # [1.0, 1.4]
                weights[i] *= coop_bonus

                # DD17: Active conditions reduce attractiveness signal
                if getattr(config, 'pathology_enabled', False) and m.active_conditions:
                    visibility = getattr(config, 'health_signal_visibility', 0.5)
                    # More conditions = stronger signal; EI helps detect
                    condition_penalty = len(m.active_conditions) * visibility * 0.1
                    ei_detect = 1.0 + female.emotional_intelligence * 0.3
                    weights[i] *= max(0.5, 1.0 - condition_penalty * ei_detect)

                # DD21: Prestige goods boost mate attractiveness signal
                if getattr(config, 'resource_types_enabled', False):
                    pg_signal = getattr(config, 'prestige_goods_mate_signal', 0.05)
                    weights[i] *= (1.0 + m.current_prestige_goods * pg_signal)

                # DD14: Endogamy preference (mild same-faction bonus)
                if (getattr(config, 'factions_enabled', False)
                        and female.faction_id is not None
                        and m.faction_id == female.faction_id):
                    endogamy = getattr(config, 'endogamy_preference', 0.0)
                    # DD25: High kinship_obligation amplifies endogamy
                    if (getattr(config, 'beliefs_enabled', False)
                            and female.age >= 15):
                        endogamy *= (1.0 + max(0, female.kinship_obligation) * 0.5)
                    weights[i] *= (1.0 + endogamy)

                # DD18: Proximity tier weight — neighborhood males preferred
                if proximity_enabled:
                    if m.id in female_neighborhood:
                        pass  # full weight (neighborhood = 1.0x for mate choice)
                    else:
                        weights[i] *= band_weight  # band tier = reduced visibility

            # Apply choosiness (blend toward uniform)
            if choosiness < 1.0:
                uniform = np.ones_like(weights) / len(weights)
                total_w = weights.sum()
                if total_w > 0:
                    weights = weights / total_w
                weights = choosiness * weights + (1 - choosiness) * uniform

            total = weights.sum()
            if total <= 0:
                continue
            weights /= total

            chosen_male = candidates[rng.choice(len(candidates), p=weights)]

            # ── Male contest: injury risk from competition ─────────
            if config.male_contest_injury_risk > 0 and len(candidates) > 1:
                # A random rival may challenge; loser takes injury
                rival_idx = rng.integers(0, len(candidates))
                rival = candidates[rival_idx]
                if rival.id != chosen_male.id and rng.random() < 0.3:
                    # DD08: Contest uses dominance (not prestige)
                    chosen_power = (chosen_male.dominance_score * 0.4
                                    + chosen_male.health * 0.3
                                    + chosen_male.aggression_propensity * 0.3)
                    rival_power = (rival.dominance_score * 0.4
                                   + rival.health * 0.3
                                   + rival.aggression_propensity * 0.3)
                    chosen_wins = rng.random() < chosen_power / (chosen_power + rival_power + 0.01)

                    if chosen_wins:
                        loser = rival
                    else:
                        loser = chosen_male
                        chosen_male = rival  # rival takes the bond

                    loser.health = max(0.0, loser.health - config.male_contest_injury_risk)

                    events.append({
                        "type": "mating_contest",
                        "year": society.year,
                        "agent_ids": [chosen_male.id, loser.id],
                        "description": f"Mating contest: winner={chosen_male.id}",
                    })

            # ── Form bond ──────────────────────────────────────────
            initial_strength = config.pair_bond_strength * rng.uniform(0.5, 1.0)
            female.add_bond(chosen_male.id, initial_strength)
            chosen_male.add_bond(female.id, initial_strength)

            female.remember(chosen_male.id, 0.1)
            chosen_male.remember(female.id, 0.1)

            paired_this_tick.add(female.id)
            if chosen_male.bond_count >= config.max_mates_per_male:
                paired_this_tick.add(chosen_male.id)

            events.append({
                "type": "pair_bond_formed",
                "year": society.year,
                "agent_ids": [female.id, chosen_male.id],
                "description": (f"Pair bond: {female.id}(F) & {chosen_male.id}(M) "
                                f"strength={initial_strength:.2f}"),
            })

        return events

    # ── Phase 4: Extra-pair copulation ─────────────────────────────

    def _process_infidelity(self, society, config, rng) -> list[dict]:
        """Bonded females may seek extra-pair copulation if partner is below potential."""
        events = []
        females, males = society.get_mating_eligible()

        if not males:
            return events

        # Precompute male mate values for EPC selection
        male_values = np.array([m.mate_value for m in males])
        male_total = male_values.sum()
        if male_total <= 0:
            return events

        for female in females:
            if not female.is_bonded:
                continue

            partner_id = female.primary_partner_id
            partner = society.get_by_id(partner_id)
            if not partner or not partner.alive:
                continue

            # EPC probability: base * mate_value_gap * (1 - bond_strength)
            partner_value = partner.mate_value
            best_available = male_values.max()
            if partner_value <= 0:
                gap = 1.0
            else:
                gap = max(0, best_available - partner_value) / partner_value
            gap = min(2.0, gap)

            bond_str = female.bond_strength_with(partner_id)
            epc_chance = config.infidelity_base_rate * gap * (1.0 - bond_str * 0.5)

            if rng.random() > epc_chance:
                continue

            # Select EPC male (weighted by mate_value, exclude current partner)
            epc_candidates = [m for m in males if m.id != partner_id]
            if not epc_candidates:
                continue
            epc_weights = np.array([m.mate_value for m in epc_candidates])
            epc_total = epc_weights.sum()
            if epc_total <= 0:
                continue
            epc_weights /= epc_total
            epc_male = epc_candidates[rng.choice(len(epc_candidates), p=epc_weights)]

            female.epc_partner_id = epc_male.id

            events.append({
                "type": "epc_occurred",
                "year": society.year,
                "agent_ids": [female.id, epc_male.id, partner_id],
                "description": f"EPC: {female.id}(F) with {epc_male.id}(M), partner={partner_id}",
            })

            # Detection
            detection_chance = config.jealousy_detection_rate * partner.jealousy_sensitivity
            if rng.random() < detection_chance:
                # Partner detects infidelity
                partner.paternity_confidence = max(0.1, partner.paternity_confidence - 0.3)
                partner.remember(female.id, -0.2)
                partner.remember(epc_male.id, -0.3)
                female.reputation = max(0.0, female.reputation - 0.05)

                # Bond damage
                damage = 0.2 + partner.jealousy_sensitivity * 0.2
                new_str = bond_str - damage
                if new_str <= 0:
                    female.remove_bond(partner_id)
                    partner.remove_bond(female.id)
                else:
                    female.pair_bond_strengths[partner_id] = new_str
                    partner.pair_bond_strengths[female.id] = new_str

                events.append({
                    "type": "epc_detected",
                    "year": society.year,
                    "agent_ids": [partner_id, female.id, epc_male.id],
                    "description": (f"EPC detected by {partner_id}, "
                                    f"paternity_conf={partner.paternity_confidence:.2f}"),
                })

        return events

    # ── Phase 5: Strengthen bonds ──────────────────────────────────

    def _strengthen_bonds(self, society, config):
        """Surviving bonds grow stronger (diminishing returns)."""
        for agent in society.get_living():
            for pid in agent.partner_ids:
                strength = agent.pair_bond_strengths.get(pid, 0.0)
                growth = 0.05 * (1.0 - strength * 0.8)
                agent.pair_bond_strengths[pid] = min(1.0, strength + growth)

        # Paternity confidence slowly recovers (if no new incidents)
        for agent in society.get_living():
            if agent.sex == Sex.MALE and agent.paternity_confidence < 1.0:
                agent.paternity_confidence = min(1.0, agent.paternity_confidence + 0.05)
