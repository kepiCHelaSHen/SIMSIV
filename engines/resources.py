"""
Resource engine — distributes survival and status resources each tick.

Deep Dive 02 implementation:
- Aggression production penalty (fighters less resource-efficient)
- Cooperation network competitive bonus (amplified mutual aid)
- Diminishing returns on wealth (soft ceiling)
- Child investment costs (parental resource drain per dependent)
- Configurable taxation / redistribution
- Subsistence floor (prevents scarcity death spirals)
- Status compounding (cooperation-weighted, network-boosted)

Resources are two-dimensional:
  - Survival resources: finite pool per tick, competitively distributed
  - Status resources: proxy for dominance, amplifies survival acquisition
"""

from __future__ import annotations
import logging
import numpy as np
from models.agent import Agent, Sex

_log = logging.getLogger(__name__)


class ResourceEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()
        if not living:
            return events

        env_multiplier = society.environment.get_resource_multiplier()
        pop_size = len(living)

        # Total resources available this tick, scaled by carrying capacity
        capacity_ratio = pop_size / config.carrying_capacity
        crowding_penalty = max(0.3, 1.0 - max(0, capacity_ratio - 0.5) * 0.8)

        total_pool = config.base_resource_per_agent * pop_size * env_multiplier * crowding_penalty

        status_pool = total_pool * config.status_resource_fraction
        survival_pool = total_pool - status_pool

        # ── Phase 0: Kin trust maintenance ─────────────────────────────
        # Parents and dependent children build mutual trust through daily
        # interaction. This seeds cooperation networks organically through
        # reproduction, solving the chicken-and-egg bootstrap problem.
        for agent in living:
            for oid in agent.offspring_ids:
                child = society.get_by_id(oid)
                if (child and child.alive
                        and child.age < config.child_dependency_years):
                    agent.remember(oid, 0.02)
                    child.remember(agent.id, 0.02)

        # DD06: Sibling trust growth — co-living siblings build mutual trust
        sibling_trust = config.sibling_trust_growth
        if sibling_trust > 0:
            for agent in living:
                if not agent.offspring_ids:
                    continue
                # Gather living dependent children of this parent
                deps = []
                for oid in agent.offspring_ids:
                    child = society.get_by_id(oid)
                    if (child and child.alive
                            and child.age < config.child_dependency_years):
                        deps.append(child)
                # Each pair of siblings builds trust
                for i in range(len(deps)):
                    for j in range(i + 1, len(deps)):
                        deps[i].remember(deps[j].id, sibling_trust)
                        deps[j].remember(deps[i].id, sibling_trust)

        # ── Phase 0b: DD16 — Update childhood resource quality ────────
        # Track parental resources during critical period (ages 0-5)
        crit_years = getattr(config, 'critical_period_years', 5)
        if getattr(config, 'developmental_plasticity_enabled', False):
            for agent in living:
                if agent.age <= crit_years and not agent.traits_finalized:
                    parental_res = 0.0
                    n_parents = 0
                    for pid in agent.parent_ids:
                        if pid is not None:
                            parent = society.get_by_id(pid)
                            if parent and parent.alive:
                                parental_res += parent.current_resources
                                n_parents += 1
                    if n_parents > 0:
                        avg_res = parental_res / n_parents
                        # Running average: blend new observation with existing
                        quality = min(1.0, avg_res / 10.0)  # normalize: 10+ = 1.0
                        alpha = 1.0 / max(1, agent.age + 1)
                        agent.childhood_resource_quality = (
                            agent.childhood_resource_quality * (1.0 - alpha)
                            + quality * alpha)

        # ── Phase 1: Decay existing resources ──────────────────────────
        # DD10: Intelligence-mediated storage efficiency
        storage_intel_bonus = getattr(config, 'storage_intelligence_bonus', 0.0)
        storage_cap = getattr(config, 'resource_storage_cap', 20.0)
        resource_types = getattr(config, 'resource_types_enabled', False)
        fo_storage_mult = config.future_orientation_storage_multiplier
        for agent in living:
            # Smarter agents preserve more (better storage)
            effective_decay = config.resource_decay_rate
            if storage_intel_bonus > 0:
                effective_decay += agent.intelligence_proxy * storage_intel_bonus
                effective_decay = min(0.9, effective_decay)  # can't keep more than 90%
            # DD27: Future-oriented agents save more resources
            effective_decay *= (0.6 + agent.future_orientation * fo_storage_mult)
            effective_decay = min(0.95, effective_decay)
            # DD27: Anxious agents hoard as safety buffer
            effective_decay += agent.anxiety_baseline * 0.10
            effective_decay = min(0.95, effective_decay)

            if resource_types:
                # DD21: Type-specific decay, modified by agent storage ability
                base_sub_decay = getattr(config, 'subsistence_decay_rate', 0.4)
                # Apply intelligence/future_orientation storage bonuses to subsistence
                sub_retention = base_sub_decay + (effective_decay - config.resource_decay_rate)
                sub_retention = max(base_sub_decay, min(0.95, sub_retention))
                agent.current_resources *= sub_retention
                agent.current_tools *= (1.0 - getattr(config, 'tools_decay_rate', 0.1))
                agent.current_prestige_goods *= (1.0 - getattr(config, 'prestige_goods_decay_rate', 0.05))
                # Caps
                agent.current_tools = min(agent.current_tools,
                                          getattr(config, 'tools_per_agent_cap', 10.0))
                agent.current_prestige_goods = min(agent.current_prestige_goods,
                                                   getattr(config, 'prestige_goods_per_agent_cap', 5.0))
            else:
                agent.current_resources *= effective_decay
            # DD10: Storage cap prevents runaway accumulation
            if storage_cap > 0:
                agent.current_resources = min(agent.current_resources, storage_cap)

        # ── Phase 2: Distribute survival resources ─────────────────────
        # Equal floor guarantees subsistence; competitive layer rewards
        # intelligence, status, experience, wealth, and cooperation networks.
        # Aggression penalizes production efficiency.
        per_agent = survival_pool / pop_size
        base_share = per_agent * config.resource_equal_floor
        competitive_pool = survival_pool * (1.0 - config.resource_equal_floor)

        # Precompute cooperation network sizes (trusted cooperative allies)
        network_sizes = {}
        for a in living:
            count = 0
            for other_id, trust in a.reputation_ledger.items():
                if trust > config.cooperation_trust_threshold:
                    other = society.get_by_id(other_id)
                    if (other and other.alive
                            and other.cooperation_propensity > config.cooperation_min_propensity):
                        count += 1
            network_sizes[a.id] = count

        # Competitive weights: multi-factor with aggression penalty
        # DD08: prestige matters more than dominance for resource acquisition
        comp_weights = np.zeros(pop_size)
        for i, a in enumerate(living):
            # DD23: Diminishing returns on intelligence in competitive weight
            # DD26: Foraging skill multiplies effective intelligence
            effective_intel = a.intelligence_proxy
            if getattr(config, 'skills_enabled', False):
                effective_intel *= (0.6 + a.foraging_skill * 0.8)
            intelligence = min(effective_intel ** 0.7, 0.8) * 0.25
            status = (a.prestige_score * 0.7 + a.dominance_score * 0.3) * 0.25
            experience = min(a.age, 50) / 50.0 * 0.15

            # Wealth with diminishing returns (prevents runaway accumulation)
            wealth_raw = min(a.current_resources / 20.0, 1.0)
            wealth = (wealth_raw ** config.wealth_diminishing_power) * 0.15

            # Cooperation network bonus — cooperative clusters gain advantage
            network = min(network_sizes[a.id], 5) * config.cooperation_network_bonus

            # DD27: Physical strength competitive weight (sex differential)
            str_bonus = a.physical_strength * 0.08
            if a.sex == Sex.FEMALE:
                str_bonus *= 0.6  # endurance-based tasks favor different physiology
            raw_weight = intelligence + status + experience + wealth + network + str_bonus
            # DD27: Endurance foraging bonus
            raw_weight += a.endurance * config.endurance_foraging_bonus
            # DD27: Future-oriented agents use resources more efficiently
            raw_weight += a.future_orientation * 0.10

            # DD21: Tools multiply subsistence production
            if resource_types:
                tool_mult = 1.0 + a.current_tools * getattr(
                    config, 'tool_production_multiplier', 0.3)
                raw_weight *= tool_mult

            # Aggression production penalty: fighters are less efficient
            agg_penalty = 1.0 - a.aggression_propensity * config.aggression_production_penalty
            raw_weight *= agg_penalty

            # DD17: Metabolic condition reduces resource acquisition
            if "metabolic" in a.active_conditions:
                raw_weight *= (1.0 - getattr(config, 'metabolic_resource_penalty', 0.15))

            # Cube to amplify differences (stronger than v1's square)
            comp_weights[i] = max(0.01, raw_weight) ** 3

        comp_total = comp_weights.sum() or 1.0

        for i, agent in enumerate(living):
            share = base_share + competitive_pool * (comp_weights[i] / comp_total)
            agent.current_resources += share

        # ── Phase 3: Child investment costs ────────────────────────────
        # Parents pay per dependent child per year. Creates mating-resource
        # inequality link: agents with more children pay more.
        # Males with paternity uncertainty invest less.
        for agent in living:
            dependents = 0
            for oid in agent.offspring_ids:
                child = society.get_by_id(oid)
                if child and child.alive and child.age < config.child_dependency_years:
                    dependents += 1
            if dependents > 0:
                cost_per_child = config.child_investment_per_year
                # DD22: Prime adults invest more in children
                if (getattr(config, 'life_stages_enabled', False)
                        and agent.life_stage == "PRIME"):
                    cost_per_child *= getattr(config, 'prime_parenting_multiplier', 1.2)
                if agent.sex == Sex.MALE and config.infidelity_enabled:
                    cost_per_child *= agent.paternity_confidence
                total_cost = cost_per_child * dependents
                # Can't spend more than half resources on children
                actual_cost = min(total_cost, agent.current_resources * 0.5)
                agent.current_resources = max(0.0, agent.current_resources - actual_cost)

        # ── Phase 4: Cooperation sharing (amplified mutual aid) ────────
        # Cooperative agents share resources with trusted allies.
        # DD11: Ostracized agents (low reputation) excluded from sharing.
        total_transfers = 0.0
        ostracism_enabled = getattr(config, 'ostracism_enabled', False)
        ostracism_thresh = getattr(config, 'ostracism_reputation_threshold', 0.25)
        # DD14: In-group sharing preferences
        factions_active = getattr(config, 'factions_enabled', False)
        in_group_trust_red = getattr(config, 'in_group_trust_threshold_reduction', 0.0)
        in_group_bonus = getattr(config, 'in_group_sharing_bonus', 0.0)
        # DD18: Proximity tier filtering for sharing
        proximity_enabled = getattr(config, 'proximity_tiers_enabled', False)
        for agent in living:
            if agent.cooperation_propensity < config.cooperation_min_propensity:
                continue
            # DD11: Ostracized agents can't participate in sharing
            if ostracism_enabled and agent.reputation < ostracism_thresh:
                continue
            allies = []
            # DD18: Precompute household + neighborhood for proximity filter
            if proximity_enabled:
                household = society.household_of(agent)
                neighborhood_set = set(agent.neighborhood_ids) | household
            for other_id, trust in agent.reputation_ledger.items():
                other = society.get_by_id(other_id)
                if not (other and other.alive
                        and other.cooperation_propensity > config.cooperation_min_propensity):
                    continue
                # DD18: Restrict sharing to household + neighborhood
                # High cooperation agents can still share with band (tier 3)
                # DD25: Low kinship_obligation extends sharing beyond neighborhood
                if proximity_enabled and other_id not in neighborhood_set:
                    coop_thresh = 0.7
                    if (getattr(config, 'beliefs_enabled', False)
                            and agent.age >= 15
                            and agent.kinship_obligation < 0):
                        coop_thresh -= abs(agent.kinship_obligation) * 0.2
                    if agent.cooperation_propensity < coop_thresh:
                        continue
                # DD14: Lower trust threshold for same-faction members
                eff_thresh = config.cooperation_trust_threshold
                # DD27: Outgroup tolerance lowers sharing trust threshold
                eff_thresh = max(0.25, eff_thresh
                                 - agent.outgroup_tolerance
                                 * config.outgroup_tolerance_sharing_threshold)
                if (factions_active and agent.faction_id is not None
                        and other.faction_id == agent.faction_id):
                    eff_thresh -= in_group_trust_red
                if trust > eff_thresh:
                    allies.append(other)
            if not allies:
                continue

            share_rate = agent.cooperation_propensity * config.cooperation_sharing_rate
            # DD15: Empathy extends sharing to non-kin (broader altruism radius)
            share_rate *= (1.0 + agent.empathy_capacity * 0.15)
            # DD25: cooperation_norm belief boosts sharing rate
            if getattr(config, 'beliefs_enabled', False) and agent.age >= 15:
                share_rate *= (1.0 + agent.cooperation_norm * 0.1)
            # DD20: Peace chief sharing boost — faction with peace chief shares more
            if (getattr(config, 'leadership_enabled', False)
                    and agent.faction_id is not None):
                leaders = getattr(society, 'faction_leaders', {}).get(agent.faction_id)
                if leaders and leaders.get('peace_chief') is not None:
                    share_rate *= (1.0 + config.peace_chief_sharing_boost)
            # DD14: Boost sharing rate for agents with in-group allies
            if factions_active and in_group_bonus > 0 and agent.faction_id is not None:
                n_in = sum(1 for a in allies if a.faction_id == agent.faction_id)
                if n_in > 0:
                    share_rate *= (1.0 + in_group_bonus * n_in / len(allies))
                # DD27: Group loyalty amplifies in-faction sharing
                if agent.group_loyalty > 0.6 and n_in > 0:
                    share_rate *= 1.2
            # DD27: Psychopathy reduces sharing (exploiter strategy)
            if agent.psychopathy_tendency > 0.6:
                share_rate *= max(0.2, 1.0 - agent.psychopathy_tendency
                                  * config.psychopathy_sharing_penalty)
            share_amount = agent.current_resources * share_rate
            if share_amount > 0.5:  # only share if meaningful
                per_ally = share_amount / len(allies)
                agent.current_resources -= share_amount
                total_transfers += share_amount
                for ally in allies:
                    ally.current_resources += per_ally
                    # Sharing strengthens trust (amplified from v1's 0.03)
                    # DD15: Emotional intelligence speeds trust formation
                    ei_trust = 0.05 * (1.0 + agent.emotional_intelligence * 0.3)
                    agent.remember(ally.id, ei_trust)
                    ally.remember(agent.id, 0.05)

        if total_transfers > 0:
            events.append({
                "type": "resource_transfers",
                "year": society.year,
                "agent_ids": [],
                "description": f"Cooperation: {total_transfers:.1f} resources shared",
            })

        # ── Phase 5: Status distribution (DD08: prestige + dominance) ──
        # Prestige: earned through cooperation, intelligence, networks, parenting
        # Dominance: earned through status_drive, aggression, existing dominance
        prestige_scores = []
        dominance_scores = []
        for a in living:
            p_score = (a.cooperation_propensity * 0.30
                       + a.intelligence_proxy * 0.20
                       + a.prestige_score * 0.20
                       + min(network_sizes[a.id], 5) * 0.04
                       + a.reputation * 0.10)
            d_score = (a.status_drive * 0.20
                       + a.aggression_propensity * 0.15
                       + a.dominance_score * 0.25
                       + a.health * 0.10
                       + a.risk_tolerance * 0.10
                       + a.dominance_drive * 0.20)   # DD15
            prestige_scores.append((a, p_score))
            dominance_scores.append((a, d_score))

        # Prestige pool (larger share — cooperation is social capital)
        prestige_pool = status_pool * 0.6
        dominance_pool = status_pool * 0.4

        total_p = sum(s for _, s in prestige_scores) or 1.0
        total_d = sum(s for _, s in dominance_scores) or 1.0

        for i, agent in enumerate(living):
            _, p_score = prestige_scores[i]
            _, d_score = dominance_scores[i]

            p_share = prestige_pool * (p_score / total_p)
            d_share = dominance_pool * (d_score / total_d)

            p_norm = p_share / (prestige_pool / pop_size + 0.01)
            d_norm = d_share / (dominance_pool / pop_size + 0.01)

            # DD08: prestige decays slower than dominance
            p_decay = 1.0 - config.prestige_decay_rate
            d_decay = 1.0 - config.dominance_decay_rate

            agent.prestige_score = max(0.0, min(1.0,
                agent.prestige_score * p_decay * 0.7 + p_norm * 0.3))
            agent.dominance_score = max(0.0, min(1.0,
                agent.dominance_score * d_decay * 0.7 + d_norm * 0.3))

        # ── Phase 6: Elite privilege (status compounding) ──────────────
        # Top-status agents get additive bonus, capped to prevent runaway
        if config.elite_privilege_multiplier > 1.0:
            threshold = np.percentile(
                [a.prestige_score + a.dominance_score for a in living], 90
            )
            bonus_cap = per_agent * 2.0
            for a in living:
                if (a.prestige_score + a.dominance_score) >= threshold:
                    bonus = min(bonus_cap,
                                a.current_resources
                                * (config.elite_privilege_multiplier - 1.0))
                    a.current_resources += bonus

        # ── Phase 7: Taxation / redistribution ─────────────────────────
        # Gated by law_strength: only societies with governance can tax
        if config.tax_rate > 0 and config.law_strength > 0:
            effective_tax = config.tax_rate * config.law_strength
            resource_values = sorted(
                [(a, a.current_resources) for a in living],
                key=lambda x: x[1], reverse=True)

            # Tax from top quartile
            top_n = max(1, pop_size // 4)
            tax_collected = 0.0
            for agent, res in resource_values[:top_n]:
                tax = res * effective_tax
                agent.current_resources -= tax
                tax_collected += tax

            # Redistribute to bottom quartile
            if tax_collected > 0:
                bottom_n = max(1, pop_size // 4)
                per_recipient = tax_collected / bottom_n
                for agent, _ in resource_values[-bottom_n:]:
                    agent.current_resources += per_recipient

                events.append({
                    "type": "taxation",
                    "year": society.year,
                    "agent_ids": [],
                    "description": (f"Tax: {tax_collected:.1f} collected, "
                                    f"redistributed to {bottom_n} agents"),
                })

        # ── DD12: Status signaling phase ──────────────────────────────
        # Agents with surplus resources can invest in public display (honest
        # signal) or attempt dominance bluffs (dishonest signal).
        signaling_enabled = getattr(config, 'signaling_enabled', False)
        bluff_attempts = 0
        bluff_detections = 0
        display_events = 0

        if signaling_enabled:
            display_frac = config.resource_display_fraction
            display_prestige = config.resource_display_prestige_boost
            bluff_prob = config.bluff_base_probability
            bluff_detect_base = config.bluff_detection_base
            bluff_rep_loss = config.bluff_caught_reputation_loss

            for a in living:
                # Honest signal: resource display (costs resources, gains prestige)
                if a.current_resources > 5.0 and a.cooperation_propensity > 0.3:
                    display_cost = a.current_resources * display_frac
                    a.current_resources -= display_cost
                    a.prestige_score = min(1.0,
                        a.prestige_score + display_prestige * (display_cost / 3.0))
                    display_events += 1

                # Dishonest signal: dominance bluff (low-quality agents try to
                # appear tougher; detected by intelligent observers)
                if (a.risk_tolerance > 0.5
                        and a.dominance_score < 0.3
                        and a.aggression_propensity > 0.4
                        and rng.random() < bluff_prob):
                    bluff_attempts += 1
                    # Detection: nearby intelligent agents may see through it
                    detected = False
                    for observer in rng.choice(living, size=min(3, len(living)),
                                               replace=False):
                        if observer.id == a.id:
                            continue
                        # DD15: Emotional intelligence boosts bluff detection
                        detect_p = (bluff_detect_base
                                    * observer.intelligence_proxy
                                    * (1.0 + observer.emotional_intelligence * 0.3)
                                    * (1.0 + (0.5 - observer.trust_of(a.id))))
                        if rng.random() < detect_p:
                            detected = True
                            observer.remember(a.id, -0.1)
                            break

                    if detected:
                        bluff_detections += 1
                        a.reputation = max(0.0, a.reputation - bluff_rep_loss)
                        a.prestige_score = max(0.0, a.prestige_score - 0.05)
                    else:
                        # Successful bluff: temporary dominance boost
                        a.dominance_score = min(1.0, a.dominance_score + 0.05)

            if bluff_attempts > 0:
                events.append({
                    "type": "signaling_summary",
                    "year": society.year,
                    "agent_ids": [],
                    "description": (f"Signals: {display_events} displays, "
                                    f"{bluff_attempts} bluffs, "
                                    f"{bluff_detections} detected"),
                })

        # ── Phase 7b (DD21): Tool production + prestige generation + trade ──
        if resource_types:
            trade_count = 0
            for a in living:
                # Tool production: intelligence + status_drive
                tool_gain = (a.intelligence_proxy * 0.5
                             + a.status_drive * 0.3
                             + min(a.age, 50) / 50.0 * 0.2) * 0.2
                # DD26: Craft skill multiplies tool production
                if getattr(config, 'skills_enabled', False):
                    tool_gain *= (0.5 + a.craft_skill * 1.0)
                a.current_tools = min(
                    a.current_tools + tool_gain,
                    getattr(config, 'tools_per_agent_cap', 10.0))

                # Prestige goods: generated from generous sharing (proxy: cooperation * trust)
                if a.cooperation_propensity > 0.5 and a.current_resources > 3.0:
                    pg_gain = (a.cooperation_propensity - 0.5) * 0.1
                    a.current_prestige_goods = min(
                        a.current_prestige_goods + pg_gain,
                        getattr(config, 'prestige_goods_per_agent_cap', 5.0))
                    # Prestige goods also boost prestige_score
                    a.prestige_score = min(1.0,
                        a.prestige_score + a.current_prestige_goods * 0.005)

            # Intra-band trade: tool surplus ↔ subsistence surplus
            trade_prob = getattr(config, 'intraband_trade_probability', 0.1)
            exchange_rate = getattr(config, 'tool_subsistence_exchange_rate', 3.0)
            for a in living:
                if rng.random() > trade_prob:
                    continue
                if a.current_tools < 1.0 or a.current_resources < 2.0:
                    continue
                # Find a trade partner in neighborhood who needs tools
                candidates = []
                for other_id in a.neighborhood_ids if proximity_enabled else []:
                    other = society.get_by_id(other_id)
                    if (other and other.alive
                            and other.current_tools < a.current_tools * 0.5
                            and other.current_resources > exchange_rate):
                        trust = a.trust_of(other_id)
                        if trust > 0.4:
                            candidates.append(other)
                if not candidates:
                    continue
                partner = candidates[rng.choice(len(candidates))]
                # Trade: 1 tool for exchange_rate subsistence
                a.current_tools -= 1.0
                a.current_resources += exchange_rate
                partner.current_tools += 1.0
                partner.current_resources -= exchange_rate
                # Trust boost from trade
                a.remember(partner.id, 0.03)
                partner.remember(a.id, 0.03)
                trade_count += 1

            if trade_count > 0:
                events.append({
                    "type": "trade_summary",
                    "year": society.year,
                    "agent_ids": [],
                    "description": f"Trade: {trade_count} tool-subsistence exchanges",
                })

        # ── Phase 8: Subsistence floor ─────────────────────────────────
        # Prevents death spirals: even the poorest get minimum resources
        for agent in living:
            if agent.current_resources < config.subsistence_floor:
                agent.current_resources = config.subsistence_floor

        return events
