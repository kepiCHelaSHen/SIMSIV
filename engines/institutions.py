"""
Institution engine — norm enforcement, institutional drift, inheritance.

Deep Dive 05 implementation:
- Institutional drift: law_strength evolves from cooperation/violence balance
- Norm enforcement: active polygyny detection with scaling penalties
- Emergent formation: institutions spontaneously form from sustained behavior
- Property rights: modulates conflict resource transfer
- Enhanced inheritance: trust-weighted option, prestige inheritance
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent, Sex


class InstitutionEngine:
    def __init__(self):
        # Track consecutive years for emergent institution triggers
        self._violence_streak = 0
        self._inequality_streak = 0

    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()

        if len(living) < 2:
            return events

        # Phase 1: Inheritance distribution
        dead_this_tick = [a for a in society.agents.values()
                         if not a.alive and a.year_of_death == society.year
                         and a.current_resources > 0]
        for agent in dead_this_tick:
            events.extend(self._distribute_inheritance(
                agent, society, config))

        # Phase 2: Norm enforcement (active detection + penalties)
        events.extend(self._enforce_norms(living, society, config, rng))

        # Phase 3: Institutional drift (law_strength evolves)
        events.extend(self._drift_institutions(living, society, config))

        # Phase 4: Emergent institution formation
        if getattr(config, 'emergent_institutions_enabled', False):
            events.extend(self._check_emergence(living, society, config))

        return events

    # ── Phase 1: Inheritance ────────────────────────────────────────

    def _distribute_inheritance(self, deceased: Agent,
                                society, config) -> list[dict]:
        """Distribute resources to heirs. DD05: trust-weighted + prestige."""
        events = []
        resources = deceased.current_resources
        if resources <= 0:
            return events

        if not config.inheritance_law_enabled:
            deceased.current_resources = 0
            return events

        # Find heirs: partners first, then offspring
        heirs = []
        for pid in (deceased.death_partner_ids or deceased.partner_ids):
            partner = society.get_by_id(pid)
            if partner and partner.alive and partner not in heirs:
                heirs.append(partner)

        for oid in deceased.offspring_ids:
            heir = society.get_by_id(oid)
            if heir and heir.alive and heir not in heirs:
                heirs.append(heir)

        if not heirs:
            deceased.current_resources = 0
            return events

        if config.inheritance_model == "equal_split":
            share = resources / len(heirs)
            for heir in heirs:
                heir.current_resources += share

        elif config.inheritance_model == "primogeniture":
            heirs[0].current_resources += resources

        elif config.inheritance_model == "trust_weighted":
            # DD05: distribute proportional to deceased's trust of each heir
            weights = []
            for heir in heirs:
                trust = deceased.trust_of(heir.id)
                weights.append(max(0.1, trust))
            total_w = sum(weights)
            for heir, w in zip(heirs, weights):
                heir.current_resources += resources * w / total_w

        else:
            # "none" — resources vanish
            deceased.current_resources = 0
            return events

        # DD05/DD08: Prestige inheritance — heirs inherit prestige (not dominance)
        prestige_frac = getattr(config, 'inheritance_prestige_fraction', 0.0)
        if prestige_frac > 0 and deceased.prestige_score > 0.2:
            status_share = deceased.prestige_score * prestige_frac / len(heirs)
            for heir in heirs:
                heir.prestige_score = min(1.0,
                    heir.prestige_score + status_share)

        deceased.current_resources = 0
        events.append({
            "type": "inheritance",
            "year": society.year,
            "agent_ids": [deceased.id] + [h.id for h in heirs],
            "description": (f"Agent {deceased.id} resources ({resources:.1f}) "
                            f"to {len(heirs)} heirs"),
        })
        return events

    # ── Phase 2: Norm enforcement ───────────────────────────────────

    def _enforce_norms(self, living: list[Agent], society,
                       config, rng) -> list[dict]:
        """Detect norm violations and apply penalties scaled by law_strength."""
        events = []
        law = config.law_strength
        if law <= 0:
            return events

        # Monogamy enforcement: penalize agents with multiple bonds
        if config.monogamy_enforced:
            for agent in living:
                if agent.bond_count > 1:
                    # Detection probability scales with law_strength
                    if rng.random() < law * 0.5:
                        penalty_rep = 0.05 * law
                        penalty_res = agent.current_resources * 0.05 * law
                        agent.reputation = max(0.0,
                            agent.reputation - penalty_rep)
                        agent.current_resources = max(0.0,
                            agent.current_resources - penalty_res)
                        events.append({
                            "type": "norm_violation",
                            "year": society.year,
                            "agent_ids": [agent.id],
                            "description": (
                                f"Agent {agent.id}: polygyny violation "
                                f"(rep -{penalty_rep:.3f}, "
                                f"res -{penalty_res:.1f})"),
                        })

        return events

    # ── Phase 3: Institutional drift ────────────────────────────────

    def _drift_institutions(self, living: list[Agent], society,
                            config) -> list[dict]:
        """Law_strength evolves based on cooperation vs violence balance."""
        events = []
        drift_rate = getattr(config, 'institutional_drift_rate', 0.0)
        if drift_rate <= 0:
            return events

        inertia = getattr(config, 'institutional_inertia', 0.8)
        coop_boost = getattr(config, 'cooperation_institution_boost', 0.01)
        vio_decay = getattr(config, 'violence_institution_decay', 0.02)

        pop = len(living)
        avg_coop = float(np.mean([a.cooperation_propensity for a in living]))
        # DD15: Conformity bias accelerates institutional adoption
        avg_conformity = float(np.mean([a.conformity_bias for a in living]))

        conflicts = sum(1 for e in society.tick_events
                        if e.get("type") == "conflict")
        violence_rate = conflicts / pop if pop > 0 else 0

        # Cooperation above threshold drives growth; violence drives decay
        # DD15: Conformity amplifies cooperation's institutional effect
        coop_factor = max(0, avg_coop - 0.4) * coop_boost * (1.0 + avg_conformity * 0.3)
        violence_factor = violence_rate * vio_decay

        # Inertia: harder to change when already at extremes
        current_law = config.law_strength
        if coop_factor > violence_factor:
            # Growing: inertia resists increase from already-high levels
            resistance = 1.0 - inertia * current_law
        else:
            # Eroding: inertia resists decrease from already-low levels
            resistance = 1.0 - inertia * (1.0 - current_law)

        delta_law = (drift_rate * (coop_factor - violence_factor)
                     * max(0.05, resistance))
        delta_law = max(-drift_rate, min(drift_rate, delta_law))

        new_law = max(0.0, min(1.0, current_law + delta_law))

        if abs(delta_law) > 0.0005:
            config.law_strength = new_law
            # Violence punishment tracks law proportionally
            config.violence_punishment_strength = new_law * 0.7
            # Property rights track law
            if hasattr(config, 'property_rights_strength'):
                config.property_rights_strength = min(
                    1.0, new_law * 0.5)

            events.append({
                "type": "institutional_drift",
                "year": society.year,
                "agent_ids": [],
                "description": (
                    f"Law drift: {current_law:.3f} -> {new_law:.3f} "
                    f"(coop={coop_factor:.4f}, "
                    f"vio={violence_factor:.4f})"),
            })

        return events

    # ── Phase 4: Emergent institution formation ─────────────────────

    def _check_emergence(self, living: list[Agent], society,
                         config) -> list[dict]:
        """Institutions spontaneously form from sustained behavior patterns."""
        events = []
        pop = len(living)

        # Track violence rate for punishment emergence
        conflicts = sum(1 for e in society.tick_events
                        if e.get("type") == "conflict")
        violence_rate = conflicts / pop if pop > 0 else 0

        if violence_rate > 0.08:
            self._violence_streak += 1
        else:
            self._violence_streak = max(0, self._violence_streak - 1)

        # After 5 consecutive high-violence years, punishment emerges
        if (self._violence_streak >= 5
                and config.violence_punishment_strength < 0.1):
            config.violence_punishment_strength = 0.1
            config.law_strength = max(config.law_strength, 0.1)
            self._violence_streak = 0
            events.append({
                "type": "institution_emerged",
                "year": society.year,
                "agent_ids": [],
                "description": ("Violence punishment emerged "
                                "(sustained high violence)"),
            })

        # Track mating inequality for monogamy pressure
        if not config.monogamy_enforced:
            males = [a for a in living
                     if a.sex == Sex.MALE and a.age >= 15]
            if len(males) >= 10:
                offspring_counts = [len(m.offspring_ids) for m in males]
                sorted_oc = sorted(offspring_counts)
                n = len(sorted_oc)
                bottom_half = sorted_oc[:n // 2]
                top_10 = sorted_oc[-max(1, n // 10):]
                bottom_avg = float(np.mean(bottom_half)) if bottom_half else 0
                top_avg = float(np.mean(top_10))

                if bottom_avg > 0 and top_avg / bottom_avg > 3.0:
                    self._inequality_streak += 1
                else:
                    self._inequality_streak = max(
                        0, self._inequality_streak - 1)

                # After 8 years of high inequality, reduce mate limit
                if (self._inequality_streak >= 8
                        and config.max_mates_per_male > 3):
                    config.max_mates_per_male = max(
                        3, config.max_mates_per_male - 1)
                    self._inequality_streak = 0
                    events.append({
                        "type": "institution_emerged",
                        "year": society.year,
                        "agent_ids": [],
                        "description": (
                            f"Mate limit reduced to "
                            f"{config.max_mates_per_male} "
                            f"(sustained inequality)"),
                    })

        return events
