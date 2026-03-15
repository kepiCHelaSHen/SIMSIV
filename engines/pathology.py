"""
Pathology engine — condition activation, trauma tracking, medical history.

DD17: Runs between mortality and institutions in tick order.
Manages heritable condition risks, activation/remission cycles,
accumulated trauma, and medical history logging.
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent


# Condition types and their effects
CONDITION_TYPES = [
    "cardiovascular",
    "mental_illness",
    "autoimmune",
    "metabolic",
    "degenerative",
]

# Map condition type to risk trait name
RISK_TRAITS = {
    "cardiovascular": "cardiovascular_risk",
    "mental_illness": "mental_illness_risk",
    "autoimmune": "autoimmune_risk",
    "metabolic": "metabolic_risk",
    "degenerative": "degenerative_risk",
}


class PathologyEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        if not getattr(config, 'pathology_enabled', False):
            return events

        living = society.get_living()
        if not living:
            return events

        scarcity = society.environment.get_scarcity_level()
        activations = 0
        remissions = 0

        for agent in living:
            if agent.age < 1:
                continue  # newborns skip

            # ── Phase 1: Condition activation checks ───────────────
            for ctype in CONDITION_TYPES:
                if ctype in agent.active_conditions:
                    continue  # already active

                risk_trait = RISK_TRAITS[ctype]
                base_risk = getattr(agent, risk_trait, 0.2)
                activation_p = config.condition_activation_base * base_risk

                # Trigger multipliers
                # Chronic resource stress
                if agent.current_resources < 3.0:
                    activation_p *= 2.0

                # Childhood trauma (DD16)
                if agent.childhood_trauma:
                    activation_p *= 1.5

                # Age past 40
                if agent.age > 40:
                    activation_p *= (1.0 + (agent.age - 40) * 0.05)

                # Recent conflict injury (approximated by low health)
                if agent.health < 0.5 and agent.conflict_cooldown > 0:
                    activation_p *= 1.3

                # Scarcity event
                if scarcity > 0.3:
                    activation_p *= 1.4

                # Metabolic paradox: high-resource environments activate metabolic risk
                if ctype == "metabolic" and agent.current_resources > 8.0:
                    activation_p *= 1.5

                # High trauma increases mental illness activation
                if ctype == "mental_illness" and agent.trauma_score > 0.4:
                    activation_p *= (1.0 + agent.trauma_score)

                # DD27: High anxiety baseline increases mental illness activation
                if ctype == "mental_illness":
                    activation_p *= (0.7 + agent.anxiety_baseline * 0.6)

                activation_p = min(0.3, activation_p)  # cap at 30%

                if rng.random() < activation_p:
                    agent.active_conditions.add(ctype)
                    activations += 1
                    self._log_medical(agent, society.year,
                                      "condition_activated", ctype, base_risk)

            # ── Phase 2: Condition remission checks ────────────────
            for ctype in list(agent.active_conditions):
                # Remission possible if resources adequate
                if agent.current_resources >= 3.0 and agent.health > 0.3:
                    remission_p = config.condition_remission_rate
                    # Worse conditions harder to remit
                    risk_trait = RISK_TRAITS[ctype]
                    remission_p *= max(0.3, 1.0 - getattr(agent, risk_trait, 0.2))
                    if rng.random() < remission_p:
                        agent.active_conditions.discard(ctype)
                        remissions += 1
                        self._log_medical(agent, society.year,
                                          "condition_remitted", ctype, 0.0)

            # ── Phase 3: Apply condition effects ───────────────────
            self._apply_condition_effects(agent, config, rng)

            # ── Phase 4: Trauma accumulation ───────────────────────
            # Chronic resource deprivation
            if agent.current_resources < 2.0:
                agent.trauma_score = min(1.0, agent.trauma_score + 0.02)

            # ── Phase 5: Trauma recovery ───────────────────────────
            if (agent.current_resources >= 3.0
                    and agent.trauma_score > 0):
                recovery = config.trauma_decay_rate
                # Kin support accelerates recovery
                kin_count = 0
                for oid in agent.offspring_ids:
                    other = society.get_by_id(oid)
                    if other and other.alive:
                        kin_count += 1
                for pid in agent.parent_ids:
                    if pid is not None:
                        parent = society.get_by_id(pid)
                        if parent and parent.alive:
                            kin_count += 1
                recovery *= (1.0 + min(3, kin_count) * 0.2)
                agent.trauma_score = max(0.0, agent.trauma_score - recovery)

        # ── Trauma from conflict losses (check tick events) ────────
        for event in society.tick_events:
            if event.get("type") == "conflict":
                outcome = event.get("outcome", {})
                loser_id = outcome.get("loser")
                if loser_id is not None:
                    loser = society.get_by_id(loser_id)
                    if loser and loser.alive:
                        loser.trauma_score = min(1.0,
                            loser.trauma_score + config.trauma_conflict_increment)

            # Trauma from kin death
            if event.get("type") == "death":
                for aid in event.get("agent_ids", []):
                    deceased = society.get_by_id(aid)
                    if deceased is None:
                        continue
                    # Trauma for partners
                    for pid in (deceased.death_partner_ids or deceased.partner_ids):
                        partner = society.get_by_id(pid)
                        if partner and partner.alive:
                            partner.trauma_score = min(1.0,
                                partner.trauma_score + config.trauma_grief_increment)
                    # Trauma for offspring
                    for oid in deceased.offspring_ids:
                        child = society.get_by_id(oid)
                        if child and child.alive:
                            child.trauma_score = min(1.0,
                                child.trauma_score + config.trauma_grief_increment)

        # ── DD24: Epigenetic stress load accumulation ────────────────
        if getattr(config, 'epigenetics_enabled', False):
            for agent in living:
                if agent.age < 15 or agent.age > 45:
                    continue  # only reproductive-age agents accumulate
                # Scarcity event
                if scarcity > 0.5:
                    agent.epigenetic_stress_load = min(1.0,
                        agent.epigenetic_stress_load
                        + getattr(config, 'epigenetic_scarcity_load', 0.3) * scarcity)
                # Epidemic
                if getattr(society.environment, 'in_epidemic', False):
                    agent.epigenetic_stress_load = min(1.0,
                        agent.epigenetic_stress_load
                        + getattr(config, 'epigenetic_epidemic_load', 0.2))
                # High trauma
                if agent.trauma_score > 0.7:
                    agent.epigenetic_stress_load = min(1.0,
                        agent.epigenetic_stress_load
                        + getattr(config, 'epigenetic_trauma_load', 0.25))
                # Natural decay in non-stressed conditions
                if scarcity < 0.2 and agent.trauma_score < 0.3:
                    agent.epigenetic_stress_load = max(0.0,
                        agent.epigenetic_stress_load - 0.1)

        # ── DD24: Trauma contagion ────────────────────────────────────
        contagion_events = 0
        if getattr(config, 'trauma_contagion_enabled', False):
            contagion_rate = getattr(config, 'trauma_contagion_rate', 0.1)
            spread_amount = getattr(config, 'trauma_spread_amount', 0.02)
            for agent in living:
                if agent.trauma_score < 0.6:
                    continue
                # Spread to close contacts (household first, then neighborhood)
                contacts = []
                if hasattr(society, 'household_of'):
                    for hid in society.household_of(agent):
                        if hid != agent.id:
                            contacts.append((hid, 2.0))  # 2x for household
                for nid in agent.neighborhood_ids:
                    if nid != agent.id and nid not in {c[0] for c in contacts}:
                        contacts.append((nid, 1.0))

                for contact_id, proximity_mult in contacts[:5]:
                    contact = society.get_by_id(contact_id)
                    if not contact or not contact.alive:
                        continue
                    spread_p = (contagion_rate * agent.trauma_score
                                * (1.0 - contact.mental_health_baseline * 0.5)
                                * (1.0 + contact.empathy_capacity * 0.3)
                                * max(0.5, 1.0 - contact.impulse_control * 0.3)
                                * proximity_mult)
                    if rng.random() < spread_p:
                        contact.trauma_score = min(1.0,
                            contact.trauma_score + spread_amount)
                        contagion_events += 1

        # ── DD24: Faction trauma buffer ───────────────────────────────
        if getattr(config, 'trauma_contagion_enabled', False):
            faction_buffer = getattr(config, 'faction_trauma_buffer', 0.02)
            for fid, fdata in getattr(society, 'factions', {}).items():
                members = [society.get_by_id(aid) for aid in fdata.get('members', [])]
                members = [a for a in members if a and a.alive]
                if not members:
                    continue
                avg_trust = 0.0
                trust_count = 0
                for m in members:
                    for other in members:
                        if other.id != m.id and other.id in m.reputation_ledger:
                            avg_trust += m.reputation_ledger[other.id]
                            trust_count += 1
                if trust_count > 0:
                    avg_trust /= trust_count
                if avg_trust > 0.65:
                    for m in members:
                        if m.trauma_score > 0:
                            m.trauma_score = max(0.0,
                                m.trauma_score - faction_buffer)

        if activations > 0 or remissions > 0 or contagion_events > 0:
            events.append({
                "type": "pathology_summary",
                "year": society.year,
                "agent_ids": [],
                "description": (f"Pathology: {activations} activations, "
                                f"{remissions} remissions"
                                + (f", {contagion_events} contagion" if contagion_events > 0 else "")),
            })

        return events

    def _apply_condition_effects(self, agent: Agent, config, rng):
        """Apply behavioral and health effects of active conditions."""
        if not agent.active_conditions:
            return

        if "cardiovascular" in agent.active_conditions:
            # Extra health decay after age 40
            if agent.age > 40:
                agent.health = max(0.0,
                    agent.health - config.cardiovascular_health_decay_boost)

        if "mental_illness" in agent.active_conditions:
            # Erratic behavioral output — random trait spikes
            noise = config.mental_illness_decision_noise
            if rng.random() < 0.3:  # 30% chance per tick of episode
                # Randomly spike either cooperation or aggression
                if rng.random() < 0.5:
                    agent.cooperation_propensity = min(1.0,
                        agent.cooperation_propensity + rng.normal(0, noise))
                else:
                    agent.aggression_propensity = min(1.0,
                        agent.aggression_propensity + rng.normal(0, noise))

        # autoimmune: handled in mortality.py epidemic section
        # metabolic: handled in resources.py competitive weights
        # degenerative: handled in conflict.py flee threshold

        # Trauma behavioral effects
        if agent.trauma_score > 0.5:
            # High trauma: trust formation slowed
            # (applied as reduced remember magnitude elsewhere)
            pass  # effect is passive through trauma_score checks

        if agent.trauma_score > 0.8:
            # Very high trauma: behavioral instability
            if rng.random() < 0.2:
                noise = config.mental_illness_decision_noise * 0.5
                agent.aggression_propensity = float(np.clip(
                    agent.aggression_propensity + rng.normal(0, noise), 0.0, 1.0))

    def _log_medical(self, agent: Agent, year: int, event: str,
                     condition: str, severity: float):
        """Log a medical history entry, bounded to 50."""
        entry = {"year": year, "event": f"{event}:{condition}",
                 "severity": round(severity, 3)}
        agent.medical_history.append(entry)
        if len(agent.medical_history) > 50:
            agent.medical_history.pop(0)
