"""
Conflict engine — models violence, deterrence, and dominance hierarchy.

Deep Dive 03 implementation:
- Network deterrence (allies suppress initiation and targeting)
- Flee response (low risk_tolerance targets can avoid combat)
- Scaled consequences (power differential affects cost magnitude)
- Subordination (recent losers enter cooldown, reducing future conflict)
- Bystander reputation updates (witnesses adjust trust toward aggressor)
- Resource advantage in combat resolution
- Proper violence death event logging
"""

from __future__ import annotations
import logging
import numpy as np
from models.agent import Agent, Sex

_log = logging.getLogger(__name__)


class ConflictEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()
        if len(living) < 2:
            return events

        # Phase 0: Decay conflict cooldowns (subordination wears off)
        for agent in living:
            if agent.conflict_cooldown > 0:
                agent.conflict_cooldown -= 1

        # Precompute ally counts for network deterrence
        ally_counts = {}
        for a in living:
            count = sum(1 for t in a.reputation_ledger.values() if t > 0.5)
            ally_counts[a.id] = count

        for agent in living:
            if not agent.alive:
                continue

            # ── Calculate conflict probability ───────────────────────
            # DD15: Impulse control gates aggression→conflict translation
            effective_aggression = agent.aggression_propensity * max(0.3, 1.0 - agent.impulse_control * 0.6)
            base_p = config.conflict_base_probability * effective_aggression

            # Jealousy trigger
            jealousy_boost = 0.0
            if agent.is_bonded and agent.sex == Sex.MALE:
                partner = society.get_by_id(agent.primary_partner_id)
                if partner and partner.alive:
                    if partner.attractiveness_base > 0.6:
                        jealousy_boost = (agent.jealousy_sensitivity
                                          * config.jealousy_conflict_multiplier * 0.1)

            # Resource pressure — DD15: mental_health_baseline moderates stress response
            resource_stress = max(0, 1.0 - agent.current_resources / 5.0) * 0.1
            resource_stress *= max(0.3, 1.0 - agent.mental_health_baseline * 0.5)

            # Status drive
            status_drive_boost = agent.status_drive * 0.05

            total_p = base_p + jealousy_boost + resource_stress + status_drive_boost

            # DD10: Seasonal conflict boost during lean cycle phase
            if getattr(config, 'seasonal_cycle_enabled', False):
                phase = society.environment.seasonal_phase
                if phase < 0:  # lean phase
                    boost = abs(phase) * getattr(config, 'seasonal_conflict_boost', 0.2)
                    total_p *= (1.0 + boost)

            # Institutional suppression
            suppression = config.law_strength * (
                0.5 + config.violence_punishment_strength * 0.5)
            total_p *= (1.0 - suppression * 0.8)

            # Cooperation dampens aggression
            total_p *= (1.0 - agent.cooperation_propensity * 0.3)

            # DD15: Empathy reduces conflict initiation
            total_p *= max(0.5, 1.0 - agent.empathy_capacity * 0.3)

            # Network deterrence: agents embedded in dense networks fight less
            own_allies = ally_counts.get(agent.id, 0)
            # DD27: Psychopathy reduces network deterrence (fearless)
            deterrence_mult = max(0.3, 1.0 - agent.psychopathy_tendency * 0.5)
            total_p *= 1.0 / (1.0 + own_allies * 0.05 * deterrence_mult)

            # Subordination: recent losers are less aggressive
            if agent.conflict_cooldown > 0:
                total_p *= config.subordination_dampening

            # DD22: Life stage conflict modifiers
            if getattr(config, 'life_stages_enabled', False):
                stage = agent.life_stage
                if stage == "YOUTH":
                    total_p *= config.youth_conflict_multiplier  # +25% for youth
                elif stage == "MATURE":
                    total_p *= config.mature_conflict_dampening  # -20% for mature
                elif stage == "ELDER":
                    total_p *= 0.5  # elders rarely initiate

            # DD27: Anxiety suppresses conflict initiation
            total_p *= max(0.3, 1.0 - agent.anxiety_baseline * 0.4)

            # DD25: Violence acceptability belief modifier
            if getattr(config, 'beliefs_enabled', False) and agent.age >= 15:
                va = agent.violence_acceptability
                if va > 0:
                    total_p *= (1.0 + va * 0.1)   # up to +10%
                else:
                    total_p *= (1.0 + va * 0.15)  # up to -15%

            # DD20: War leader inspiration — faction members fight more under active war leader
            if (config.leadership_enabled
                    and agent.faction_id is not None):
                leaders = society.faction_leaders.get(agent.faction_id)
                if leaders and leaders.get('war_leader') is not None:
                    total_p *= (1.0 + config.war_leader_aggression_boost)

            total_p = max(0.0, min(0.5, total_p))

            if rng.random() > total_p:
                continue

            # ── Select target ────────────────────────────────────────
            target = self._select_target(
                agent, living, society, config, rng, ally_counts)
            if target is None or not target.alive:
                continue

            # ── Flee check: target may avoid combat ──────────────────
            # DD15: Pain tolerance raises effective risk tolerance for flee check
            effective_risk = target.risk_tolerance + target.pain_tolerance * 0.15
            # DD17: Degenerative condition makes flee easier
            flee_thresh = config.flee_threshold
            if "degenerative" in target.active_conditions:
                flee_thresh += getattr(config, 'degenerative_flee_threshold_boost', 0.15)
            # DD27: Anxiety raises flee threshold (anxious agents flee more readily)
            flee_thresh += target.anxiety_baseline * config.anxiety_flee_boost
            if effective_risk < flee_thresh:
                flee_chance = (1.0 - effective_risk) * 0.5
                if rng.random() < flee_chance:
                    # Target flees — small dominance shift, no violence
                    agent.dominance_score = min(1.0,
                        agent.dominance_score + 0.02)
                    target.dominance_score = max(0.0,
                        target.dominance_score - 0.02)
                    events.append({
                        "type": "flee",
                        "year": society.year,
                        "agent_ids": [agent.id, target.id],
                        "description": (f"Agent {target.id} fled from "
                                        f"{agent.id}"),
                    })
                    continue

            # ── DD11: Coalition defense — target's allies may intervene ──
            if config.coalition_defense_enabled:
                defended = False
                trust_thresh = config.coalition_defense_trust_threshold
                for other in living:
                    if (other.id != agent.id and other.id != target.id
                            and other.alive
                            and other.trust_of(target.id) > trust_thresh
                            and other.cooperation_propensity > 0.4
                            and other.health > 0.3):
                        defense_p = (config.coalition_defense_probability
                                     * other.trust_of(target.id)
                                     * other.cooperation_propensity)
                        # DD27: Group loyalty boosts coalition defense
                        defense_p += other.group_loyalty * 0.3
                        if rng.random() < defense_p:
                            # Ally intervenes — aggressor deterred
                            agent.dominance_score = max(0.0,
                                agent.dominance_score - 0.03)
                            other.prestige_score = min(1.0,
                                other.prestige_score + 0.03)
                            other.remember(target.id, 0.05)
                            target.remember(other.id, 0.05)
                            agent.remember(other.id, -0.1)
                            events.append({
                                "type": "coalition_defense",
                                "year": society.year,
                                "agent_ids": [other.id, target.id, agent.id],
                                "description": (f"Agent {other.id} defended "
                                                f"{target.id} from {agent.id}"),
                            })
                            defended = True
                            break  # one defender is enough
                if defended:
                    continue  # conflict averted

            # ── DD20: Peace chief arbitration — intra-faction conflict mediation
            if (config.leadership_enabled
                    and agent.faction_id is not None
                    and agent.faction_id == target.faction_id):
                leaders = society.faction_leaders.get(agent.faction_id)
                if leaders and leaders.get('peace_chief') is not None:
                    chief = society.get_by_id(leaders['peace_chief'])
                    if (chief and chief.alive
                            and chief.id != agent.id and chief.id != target.id):
                        arb_p = (chief.prestige_score
                                 * config.peace_chief_arbitration_probability)
                        if rng.random() < arb_p:
                            # Mediation successful — conflict averted
                            chief.prestige_score = min(1.0,
                                chief.prestige_score + 0.02)
                            events.append({
                                "type": "leadership_arbitration",
                                "year": society.year,
                                "agent_ids": [chief.id, agent.id, target.id],
                                "description": (f"Peace chief {chief.id} mediated "
                                                f"conflict between {agent.id} and {target.id}"),
                            })
                            continue

            # ── Resolve conflict ─────────────────────────────────────
            conflict_events = self._resolve_conflict(
                agent, target, society, config, rng, living, ally_counts)
            events.extend(conflict_events)

        return events

    def _select_target(self, aggressor: Agent, living: list[Agent],
                       society, config, rng: np.random.Generator,
                       ally_counts: dict) -> Agent | None:
        """Pick a conflict target with network deterrence and proximity weighting."""
        candidates = [a for a in living
                      if a.id != aggressor.id and a.alive]
        if not candidates:
            return None

        # DD18: Precompute proximity sets for tier weighting
        proximity_enabled = getattr(config, 'proximity_tiers_enabled', False)
        if proximity_enabled:
            household = society.household_of(aggressor)
            neighborhood_set = set(aggressor.neighborhood_ids) | household
            hh_mult = getattr(config, 'household_interaction_multiplier', 4.0)
            nb_mult = getattr(config, 'neighborhood_interaction_multiplier', 2.0)

        weights = np.ones(len(candidates))
        for i, c in enumerate(candidates):
            # Cross-sex targeting is less common (0.3x weight)
            if c.sex != aggressor.sex:
                weights[i] *= 0.3
            # DD18: Apply proximity tier weight
            if proximity_enabled:
                if c.id in household:
                    weights[i] *= hh_mult
                elif c.id in neighborhood_set:
                    weights[i] *= nb_mult
                # else: band tier = 1.0x (default)
            # Low trust = more likely target
            trust = aggressor.trust_of(c.id)
            weights[i] *= (1.5 - trust)

            # Rival for same mate = high priority
            if (aggressor.is_bonded and c.is_bonded
                    and set(aggressor.partner_ids) & set(c.partner_ids)):
                weights[i] *= 3.0

            # DD08: Similar dominance = status challenge
            dom_diff = abs(aggressor.dominance_score - c.dominance_score)
            if dom_diff < 0.2:
                weights[i] *= 1.5

            # DD08: High-dominance targets are feared (deterrence)
            weights[i] *= 1.0 / (1.0 + c.dominance_score
                                  * config.dominance_deterrence_factor)

            # Resource envy: richer targets are more tempting
            if c.current_resources > aggressor.current_resources * 1.5:
                weights[i] *= 1.3

            # DD21: Tool envy — target with superior tools
            if (getattr(config, 'resource_types_enabled', False)
                    and c.current_tools > aggressor.current_tools * 1.5):
                weights[i] *= 1.4

            # Network deterrence: well-connected agents are harder targets
            target_allies = ally_counts.get(c.id, 0)
            weights[i] *= 1.0 / (1.0 + target_allies
                                  * config.network_deterrence_factor)

            # Strength assessment: cowardly aggressors avoid strong targets
            # DD27: Psychopathy sharpens prey selection (target weaker)
            strength_weight = 1.0 + aggressor.psychopathy_tendency * 0.4
            if aggressor.risk_tolerance < 0.4:
                if c.health > aggressor.health * 1.2:
                    weights[i] *= 0.5
            # High psychopathy targets weaker agents more
            if aggressor.psychopathy_tendency > 0.5 and c.health < aggressor.health * 0.8:
                weights[i] *= strength_weight

            # DD14: Out-group targeting preference
            if (getattr(config, 'factions_enabled', False)
                    and aggressor.faction_id is not None
                    and c.faction_id is not None
                    and aggressor.faction_id != c.faction_id):
                weights[i] *= getattr(config, 'out_group_conflict_multiplier', 1.0)

            # DD20: War leader deterrence — faction with war leader harder to target
            if (config.leadership_enabled
                    and c.faction_id is not None):
                c_leaders = society.faction_leaders.get(c.faction_id)
                if c_leaders and c_leaders.get('war_leader') is not None:
                    weights[i] *= (1.0 - config.war_leader_deterrence)

        # DD22: Elder presence in aggressor's faction reduces out-group conflict
        if getattr(config, 'life_stages_enabled', False):
            if aggressor.faction_id is not None:
                faction_data = society.factions.get(aggressor.faction_id)
                if faction_data:
                    elder_count = sum(
                        1 for aid in faction_data.get('members', [])
                        if (a := society.get_by_id(aid)) and a.alive
                        and a.life_stage == "ELDER" and a.reputation > 0.4)
                    if elder_count > 0:
                        for i, c in enumerate(candidates):
                            if (c.faction_id is not None
                                    and c.faction_id != aggressor.faction_id):
                                weights[i] *= (1.0 - config.elder_conflict_damping
                                               * min(3, elder_count))

        total = weights.sum()
        if total <= 0:
            return None
        weights /= total

        return candidates[rng.choice(len(candidates), p=weights)]

    def _resolve_conflict(self, aggressor: Agent, target: Agent,
                          society, config, rng,
                          living: list[Agent],
                          ally_counts: dict) -> list[dict]:
        """Resolve a conflict with scaled consequences."""
        events = []

        # DD08: Combat power — dominance matters more than prestige in combat
        resource_edge_a = min(aggressor.current_resources / 20.0, 1.0)
        resource_edge_t = min(target.current_resources / 20.0, 1.0)

        dom_weight = config.dominance_weight_in_combat
        pres_weight = 1.0 - dom_weight
        status_a = aggressor.dominance_score * dom_weight + aggressor.prestige_score * pres_weight
        status_t = target.dominance_score * dom_weight + target.prestige_score * pres_weight

        agg_power = (aggressor.aggression_propensity * 0.25       # DD03 spec
                     + status_a * 0.20                             # DD03 spec
                     + aggressor.health * 0.25                     # DD03 spec
                     + aggressor.risk_tolerance * 0.15             # DD03 spec
                     + resource_edge_a * config.combat_resource_factor
                     + aggressor.intelligence_proxy * 0.05         # DD03 spec
                     + aggressor.physical_robustness * 0.05        # DD15 additive
                     + aggressor.dominance_drive * 0.05            # DD15 additive
                     + aggressor.pain_tolerance * 0.03)            # DD15 additive
        tgt_power = (target.aggression_propensity * 0.25           # DD03 spec
                     + status_t * 0.20                             # DD03 spec
                     + target.health * 0.25                        # DD03 spec
                     + target.risk_tolerance * 0.15                # DD03 spec
                     + resource_edge_t * config.combat_resource_factor
                     + target.intelligence_proxy * 0.05            # DD03 spec
                     + target.physical_robustness * 0.05           # DD15 additive
                     + target.dominance_drive * 0.05               # DD15 additive
                     + target.pain_tolerance * 0.03)               # DD15 additive

        # DD27: Physical strength additive with sex differential
        for fighter, label in [(aggressor, 'agg'), (target, 'tgt')]:
            str_contrib = fighter.physical_strength * config.physical_strength_combat_weight
            if fighter.sex == Sex.MALE:
                str_contrib *= 1.4
            if label == 'agg':
                agg_power += str_contrib
            else:
                tgt_power += str_contrib

        # DD26: Combat skill contributes to power
        if getattr(config, 'skills_enabled', False):
            csw = config.combat_skill_weight
            agg_power += aggressor.combat_skill * csw
            tgt_power += target.combat_skill * csw

        # Small ally bonus (allies don't fight but boost confidence)
        agg_allies = min(ally_counts.get(aggressor.id, 0), 3) * 0.03
        tgt_allies = min(ally_counts.get(target.id, 0), 3) * 0.03
        agg_power += agg_allies
        tgt_power += tgt_allies

        # DD20: War leader combat bonus — fighting alongside faction war leader
        if config.leadership_enabled:
            for fighter, power_ref in [(aggressor, 'agg'), (target, 'tgt')]:
                if fighter.faction_id is not None:
                    leaders = society.faction_leaders.get(
                        fighter.faction_id)
                    if leaders and leaders.get('war_leader') is not None:
                        wl = society.get_by_id(leaders['war_leader'])
                        if wl and wl.alive and wl.faction_id == fighter.faction_id:
                            if power_ref == 'agg':
                                agg_power += config.war_leader_combat_bonus
                            else:
                                tgt_power += config.war_leader_combat_bonus

        # Probabilistic outcome
        agg_chance = agg_power / (agg_power + tgt_power + 0.01)

        aggressor_wins = rng.random() < agg_chance
        winner = aggressor if aggressor_wins else target
        loser = target if aggressor_wins else aggressor

        # Power differential for scaled consequences
        power_diff = abs(agg_power - tgt_power) / (agg_power + tgt_power + 0.01)
        # scale_factor: 0.7 for close fights, up to 1.5 for stomps
        scale_factor = 0.7 + power_diff * 1.6

        # ── Costs to loser ───────────────────────────────────────────
        loser_health_cost = config.violence_cost_health * scale_factor
        # DD15: Physical robustness absorbs damage
        loser_health_cost *= max(0.5, 1.0 - loser.physical_robustness * 0.4)
        loser.health = max(0.0, loser.health - loser_health_cost)
        resource_loss = loser.current_resources * config.violence_cost_resources * scale_factor
        loser.current_resources = max(0.0, loser.current_resources - resource_loss)

        # Winner takes some resources and gains status (scaled)
        # DD05: Property rights reduce looting
        loot_fraction = 0.5 * (1.0 - getattr(config, 'property_rights_strength', 0.0))
        winner.current_resources += resource_loss * loot_fraction

        # DD21: Tool looting — winner may take a tool from loser
        if (getattr(config, 'resource_types_enabled', False)
                and loser.current_tools >= 1.0
                and rng.random() < getattr(config, 'tool_conflict_loot_chance', 0.2)):
            loser.current_tools -= 1.0
            winner.current_tools = min(
                winner.current_tools + 1.0,
                getattr(config, 'tools_per_agent_cap', 10.0))

        # DD08: Victory/defeat shifts dominance (not prestige)
        dom_shift = config.winner_status_scale * (1.0 + power_diff)
        winner.dominance_score = min(1.0, winner.dominance_score + dom_shift)
        loser.dominance_score = max(0.0,
            loser.dominance_score - config.loser_status_scale * (1.0 + power_diff))
        # Aggressor loses prestige (violence is socially costly even if you win)
        aggressor.prestige_score = max(0.0, aggressor.prestige_score - 0.02)

        # Both suffer minor health cost (fighting is costly)
        winner.health = max(0.0, winner.health - config.violence_cost_health * 0.3)

        # ── Subordination: loser enters cooldown ─────────────────────
        loser.conflict_cooldown = max(
            loser.conflict_cooldown, config.subordination_cooldown_years)

        # ── Death check for loser ────────────────────────────────────
        death = False
        # Death chance scales with power differential (stomps are more lethal)
        effective_death_chance = config.violence_death_chance * (0.5 + power_diff)
        if rng.random() < effective_death_chance:
            loser.die("violence", society.year)
            death = True
            # Log violence death as proper death event for metrics
            events.append({
                "type": "death",
                "year": society.year,
                "agent_ids": [loser.id],
                "description": (f"Agent {loser.id} died: violence "
                                f"(age {loser.age})"),
            })

        # ── Reputation updates ───────────────────────────────────────
        # Aggressor reputation always suffers (violence is socially costly)
        aggressor.reputation = max(0.0, aggressor.reputation - 0.05)
        # Winner gets a small reputation bump if they won decisively
        if aggressor_wins and power_diff > 0.2:
            winner.reputation = min(1.0, winner.reputation + 0.02)

        aggressor.remember(target.id, -0.2)
        target.remember(aggressor.id, -0.3)

        # ── Bystander trust updates ──────────────────────────────────
        # Nearby agents witness the violence and judge the aggressor
        if config.bystander_trust_update and len(living) > 2:
            n_bystanders = min(config.bystander_count, len(living) - 2)
            bystander_pool = [a for a in living
                              if a.id != aggressor.id and a.id != target.id
                              and a.alive]
            if bystander_pool and n_bystanders > 0:
                n_select = min(n_bystanders, len(bystander_pool))
                bystander_indices = rng.choice(
                    len(bystander_pool), size=n_select, replace=False)
                bystanders = [bystander_pool[i] for i in bystander_indices]
                for bystander in bystanders:
                    # Witnesses distrust the aggressor
                    bystander.remember(aggressor.id, -0.08)
                    # If bystander is allied with target, stronger reaction
                    if bystander.trust_of(target.id) > 0.6:
                        bystander.remember(aggressor.id, -0.1)

        # ── Pair bond destabilization ────────────────────────────────
        for fighter in [aggressor, target]:
            if fighter.alive and fighter.is_bonded:
                for pid in list(fighter.partner_ids):
                    partner = society.get_by_id(pid)
                    if partner and partner.alive:
                        leave_chance = partner.jealousy_sensitivity * 0.1 * (1.0 + fighter.aggression_propensity * 0.5)
                        if rng.random() < leave_chance:
                            fighter.remove_bond(pid)
                            partner.remove_bond(fighter.id)
                            society._unindex_bond(fighter.id, pid)
                            partner.remember(fighter.id, -0.25)
                            events.append({
                                "type": "bond_dissolved",
                                "year": society.year,
                                "agent_ids": [fighter.id, pid],
                                "description": (
                                    f"Pair bond dissolved by conflict: "
                                    f"{fighter.id} & {pid}"),
                                "outcome": {
                                    "reason": "conflict_break",
                                    "fighter": fighter.id,
                                    "partner": pid,
                                },
                            })
                            break

        # ── Institutional punishment ─────────────────────────────────
        if config.violence_punishment_strength > 0:
            penalty = config.violence_punishment_strength * 0.1
            aggressor.reputation = max(0.0, aggressor.reputation - penalty)
            aggressor.current_resources = max(0.0,
                aggressor.current_resources - penalty * 5)
            events.append({
                "type": "punishment",
                "year": society.year,
                "agent_ids": [aggressor.id],
                "description": (f"Agent {aggressor.id} punished: "
                                f"rep -{penalty:.2f}, "
                                f"res -{penalty * 5:.1f}"),
            })

        events.append({
            "type": "conflict",
            "year": society.year,
            "agent_ids": [aggressor.id, target.id],
            "description": (f"Conflict: {aggressor.id} vs {target.id} → "
                            f"{'winner' if aggressor_wins else 'loser'}: "
                            f"{aggressor.id}"
                            f"{' (DEATH)' if death else ''}"),
            "outcome": {
                "aggressor": aggressor.id,
                "target": target.id,
                "winner": winner.id,
                "loser": loser.id,
                "death": death,
                "power_diff": round(power_diff, 3),
            },
        })

        # ── DD11: Third-party punishment ────────────────────────────
        # High-cooperation agents who trust the target punish the aggressor
        if config.third_party_punishment_enabled:
            willing_thresh = config.punishment_willingness_threshold
            for punisher in living:
                if (punisher.id != aggressor.id
                        and punisher.id != target.id
                        and punisher.alive
                        and punisher.cooperation_propensity >= willing_thresh
                        and punisher.trust_of(target.id) > 0.5
                        and punisher.trust_of(aggressor.id) < 0.5):
                    # Probability based on cooperation and distrust of aggressor
                    punish_p = (punisher.cooperation_propensity - 0.4) * 0.3
                    # DD27: Group loyalty boosts punishment of threats
                    punish_p += punisher.group_loyalty * 0.15
                    # DD25: Low violence_acceptability → more likely to punish violence
                    if getattr(config, 'beliefs_enabled', False):
                        punish_p *= max(0.5, 1.0 - punisher.violence_acceptability * 0.3)
                    if rng.random() < punish_p:
                        # Punisher pays a cost
                        cost = punisher.current_resources * config.punishment_cost_fraction
                        punisher.current_resources = max(0, punisher.current_resources - cost)
                        # Aggressor pays a penalty
                        penalty = config.punishment_severity
                        aggressor.current_resources = max(0,
                            aggressor.current_resources - penalty * 5)
                        aggressor.prestige_score = max(0.0,
                            aggressor.prestige_score - penalty)
                        # Trust updates
                        punisher.remember(aggressor.id, -0.15)
                        aggressor.remember(punisher.id, -0.1)
                        # Punisher gains prestige
                        punisher.prestige_score = min(1.0,
                            punisher.prestige_score + 0.02)
                        events.append({
                            "type": "third_party_punishment",
                            "year": society.year,
                            "agent_ids": [punisher.id, aggressor.id],
                            "description": (f"Agent {punisher.id} punished "
                                            f"{aggressor.id} (cost={cost:.1f})"),
                        })
                        break  # one punisher per conflict

        return events
