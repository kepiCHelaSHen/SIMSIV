"""
Mortality engine — aging, health decay, natural death, pair bond cleanup.

DD06 additions: annual childhood mortality (resource-dependent), orphan
mortality multiplier, grandparent survival bonus for children.
"""

from __future__ import annotations
import logging
import numpy as np
from models.agent import Agent, Sex, HERITABLE_TRAITS

_log = logging.getLogger(__name__)


class MortalityEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()
        childhood_deaths = 0

        # DD16: Precompute peer trait averages for developmental peer effects
        children_traits = None
        if getattr(config, 'developmental_plasticity_enabled', False):
            children_near_maturity = [a for a in living if 5 <= a.age <= 16]
            if children_near_maturity:
                children_traits = {}
                for trait in ['aggression_propensity', 'cooperation_propensity',
                              'risk_tolerance', 'intelligence_proxy']:
                    children_traits[trait] = float(np.mean(
                        [getattr(a, trait) for a in children_near_maturity]))

        for agent in living:
            # NOTE: age was already incremented at start of tick in simulation.py

            # DD16: Maturation event at age 15
            if (agent.age == 15
                    and not agent.traits_finalized
                    and agent.genotype
                    and getattr(config, 'developmental_plasticity_enabled', False)):
                self._apply_maturation(agent, society, config, rng, children_traits)
                events.append({
                    "type": "maturation",
                    "year": society.year,
                    "agent_ids": [agent.id],
                    "description": (f"Agent {agent.id} matured: "
                                    f"trauma={agent.childhood_trauma}, "
                                    f"resource_q={agent.childhood_resource_quality:.2f}"),
                })

            # DD25: Belief initialization at maturation (age 15)
            if agent.age == 15 and getattr(config, 'beliefs_enabled', False):
                self._initialize_beliefs(agent, rng)

            # DD26: Skill initialization at maturation (age 15)
            if agent.age == 15 and getattr(config, 'skills_enabled', False):
                self._initialize_skills(agent, society, config)

            # Health decay — accelerates with age
            age_factor = max(0, agent.age - 30) * 0.002  # faster after 30
            decay = config.health_decay_per_year + age_factor
            # DD15: Longevity genes reduce health decay after age 50
            if agent.age > 50:
                decay *= max(0.5, 1.0 - agent.longevity_genes * 0.4)  # up to 40% slower
            # DD27: Endurance slows health decay
            decay *= max(0.7, 1.0 - agent.endurance * 0.15)
            # DD27: Conscientiousness maintains health through consistent behavior
            decay *= max(0.75, 1.0 - agent.conscientiousness * 0.12)
            agent.health = max(0.0, agent.health - decay)

            # Scarcity stress
            scarcity = society.environment.get_scarcity_level()
            if scarcity > 0:
                agent.health = max(0.0, agent.health - scarcity * 0.03)

            # Low resources hurt health
            if agent.current_resources < 2.0:
                agent.health = max(0.0, agent.health - 0.02)

            # ── DD06: Annual childhood mortality (ages 1-15) ─────────
            if agent.age <= 15 and agent.age > 0:
                child_death_p = config.childhood_mortality_annual

                # Resource-dependent: children in poor families die more
                parental_resources = 0.0
                has_living_parent = False
                has_living_grandparent = False
                for pid in agent.parent_ids:
                    if pid is not None:
                        parent = society.get_by_id(pid)
                        if parent and parent.alive:
                            has_living_parent = True
                            parental_resources += parent.current_resources
                            # Check grandparents
                            for gpid in parent.parent_ids:
                                if gpid is not None:
                                    gp = society.get_by_id(gpid)
                                    if gp and gp.alive:
                                        has_living_grandparent = True

                # Low parental resources increase risk
                if has_living_parent:
                    resource_factor = max(0.5, min(1.5, 1.5 - parental_resources / 10.0))
                    child_death_p *= resource_factor
                else:
                    # DD06: Orphan mortality multiplier
                    child_death_p *= config.orphan_mortality_multiplier

                # DD06: Grandparent survival bonus (reduces mortality)
                if has_living_grandparent:
                    child_death_p *= max(0.3, 1.0 - config.grandparent_survival_bonus)

                # Scarcity increases childhood mortality
                if scarcity > 0:
                    child_death_p *= (1.0 + scarcity * 0.5)

                if rng.random() < child_death_p:
                    agent.die("childhood_mortality", society.year)
                    childhood_deaths += 1
                    events.append({
                        "type": "death",
                        "year": society.year,
                        "agent_ids": [agent.id],
                        "description": (f"Agent {agent.id} died: childhood_mortality "
                                        f"(age {agent.age}, orphan={not has_living_parent})"),
                    })
                    events.append({
                        "type": "childhood_death",
                        "year": society.year,
                        "agent_ids": [agent.id],
                        "description": f"Child {agent.id} died at age {agent.age}",
                    })
                    continue  # skip adult death checks

            # ── DD09: Epidemic mortality ──────────────────────────────
            if society.environment.in_epidemic and agent.age > 0:
                epi_base = config.epidemic_lethality_base
                epi_risk = epi_base

                # Age-differential vulnerability
                if agent.age <= 10:
                    epi_risk *= config.epidemic_child_vulnerability
                elif agent.age >= 55:
                    epi_risk *= config.epidemic_elder_vulnerability

                # Health vulnerability
                if agent.health < config.epidemic_health_threshold:
                    epi_risk *= 2.0

                # Low resources (malnutrition) increases risk
                if agent.current_resources < 3.0:
                    epi_risk *= 1.5

                # Intelligence as resilience proxy (mild)
                epi_risk *= max(0.7, 1.0 - agent.intelligence_proxy * 0.3)

                # DD15: Disease resistance reduces epidemic vulnerability
                epi_risk *= max(0.4, 1.0 - agent.disease_resistance * 0.5)

                # DD17: Autoimmune condition increases epidemic vulnerability
                if "autoimmune" in agent.active_conditions:
                    epi_risk *= getattr(config, 'autoimmune_epidemic_vulnerability', 2.0)

                if rng.random() < epi_risk:
                    agent.die("epidemic", society.year)
                    events.append({
                        "type": "death",
                        "year": society.year,
                        "agent_ids": [agent.id],
                        "description": (f"Agent {agent.id} died: epidemic "
                                        f"(age {agent.age})"),
                    })
                    events.append({
                        "type": "epidemic_death",
                        "year": society.year,
                        "agent_ids": [agent.id],
                        "description": f"Epidemic death: agent {agent.id}, age {agent.age}",
                    })
                    continue  # skip other death checks

            # ── Death checks ─────────────────────────────────────────
            died = False

            # Health death
            if agent.health <= config.min_health_survival:
                agent.die("health_failure", society.year)
                died = True

            # Age-based death (probability increases sharply past base age)
            # DD15: Longevity genes shift effective death age up to +10 years
            effective_death_base = config.age_death_base + int(agent.longevity_genes * 10)
            if not died and agent.age > effective_death_base - config.age_death_variance:
                years_past = agent.age - (effective_death_base - config.age_death_variance)
                death_p = 0.01 * (years_past ** 1.5) / config.age_death_variance
                if rng.random() < death_p:
                    agent.die("old_age", society.year)
                    died = True

            # Background mortality (accidents, disease)
            # DD13: Sex-differential mortality — males age 15-40 face higher risk
            bg_rate = config.mortality_base
            if (agent.sex == Sex.MALE
                    and 15 <= agent.age <= 40):
                bg_rate *= config.male_risk_mortality_multiplier
            if not died and rng.random() < bg_rate:
                agent.die("accident", society.year)
                died = True

            if died:
                # DD16: Flag childhood trauma for children under 10
                for oid in agent.offspring_ids:
                    child = society.get_by_id(oid)
                    if child and child.alive and child.age < 10:
                        child.childhood_trauma = True

                # Bond cleanup handled by mating engine's _clean_stale_bonds next tick
                events.append({
                    "type": "death",
                    "year": society.year,
                    "agent_ids": [agent.id],
                    "description": f"Agent {agent.id} died: {agent.cause_of_death} (age {agent.age})",
                })

        return events

    def _apply_maturation(self, agent: Agent, society, config,
                          rng: np.random.Generator,
                          peer_traits: dict | None):
        """DD16: Apply developmental modifications at maturation (age 15).

        Genotype is stored separately; phenotype (trait fields) is modified.
        Orchid/dandelion: mental_health_baseline moderates sensitivity.
        """
        res_effect = config.childhood_resource_effect
        parent_effect = config.parental_modeling_effect
        peer_effect = config.peer_influence_effect

        # Orchid/dandelion: low mental_health = high sensitivity to environment
        sensitivity = max(0.2, 1.0 - agent.mental_health_baseline * 0.6)

        # ── Resource environment effect ─────────────────────────────
        # Well-resourced → +intelligence, +impulse_control, +mental_health
        # Deprived → +aggression, +risk_tolerance, -intelligence, -impulse_control
        res_q = agent.childhood_resource_quality
        res_deviation = (res_q - 0.5) * 2.0  # [-1.0, 1.0]

        def _modify(trait_name: str, delta: float):
            """Apply bounded developmental modification to phenotype."""
            current = getattr(agent, trait_name)
            # Clamp modification to ±0.10
            clamped = max(-0.10, min(0.10, delta * sensitivity))
            setattr(agent, trait_name,
                    float(np.clip(current + clamped, 0.0, 1.0)))

        _modify('intelligence_proxy', res_deviation * res_effect)
        _modify('impulse_control', res_deviation * res_effect)
        _modify('mental_health_baseline', res_deviation * res_effect * 0.5)
        # Deprived environments boost aggression and risk tolerance
        _modify('aggression_propensity', -res_deviation * res_effect * 0.8)
        _modify('risk_tolerance', -res_deviation * res_effect * 0.5)

        # ── Parental trait modeling ─────────────────────────────────
        # Children raised by cooperative parents get cooperation boost
        parent_coop_dev = agent.developmental_parent_cooperation - 0.5
        _modify('cooperation_propensity', parent_coop_dev * parent_effect)
        # Children raised by aggressive parents get aggression boost
        parent_agg_dev = agent.developmental_parent_aggression - 0.5
        _modify('aggression_propensity', parent_agg_dev * parent_effect)

        # ── Orphan effect ───────────────────────────────────────────
        has_living_parent = False
        for pid in agent.parent_ids:
            if pid is not None:
                parent = society.get_by_id(pid)
                if parent and parent.alive:
                    has_living_parent = True
                    break

        if not has_living_parent:
            _modify('aggression_propensity', config.orphan_aggression_boost)
            # Reduced trust capacity (lower social trust starting value)
            agent.reputation = max(0.0, agent.reputation - 0.1)

        # ── Childhood trauma effect ─────────────────────────────────
        if agent.childhood_trauma:
            _modify('aggression_propensity', 0.03 * sensitivity)
            _modify('mental_health_baseline', -0.03 * sensitivity)
            _modify('impulse_control', -0.02 * sensitivity)

        # ── Peer group effects (30% of parental effect) ─────────────
        if peer_traits and peer_effect > 0:
            conformity = agent.conformity_bias
            for trait in ['aggression_propensity', 'cooperation_propensity',
                          'risk_tolerance', 'intelligence_proxy']:
                if trait in peer_traits:
                    peer_dev = peer_traits[trait] - getattr(agent, trait)
                    # Conformity gates how much peer influence matters
                    _modify(trait, peer_dev * peer_effect * conformity)

        # ── Birth order effect (optional) ───────────────────────────
        bo_effect = config.birth_order_effect
        if bo_effect > 0:
            # Count older siblings
            older_sibs = 0
            for pid in agent.parent_ids:
                if pid is not None:
                    parent = society.get_by_id(pid)
                    if parent:
                        for oid in parent.offspring_ids:
                            sib = society.get_by_id(oid)
                            if sib and sib.id != agent.id and sib.age > agent.age:
                                older_sibs += 1
                        break  # count from one parent only

            if older_sibs == 0:
                # Firstborn: slightly higher conscientiousness proxy
                _modify('intelligence_proxy', bo_effect * 0.5)
                _modify('impulse_control', bo_effect * 0.5)
            elif older_sibs >= 2:
                # Later-born: higher risk_tolerance, novelty_seeking
                _modify('risk_tolerance', bo_effect)
                _modify('novelty_seeking', bo_effect)

        agent.traits_finalized = True

    def _initialize_beliefs(self, agent, rng):
        """DD25: Initialize beliefs at maturation (age 15).

        Formula: belief = conformity_bias * parent_avg_belief
                        + (1 - conformity_bias) * trait_derived_belief
                        + novelty_seeking * N(0, 0.15)
        """
        import numpy as np
        cb = agent.conformity_bias

        belief_specs = {
            'hierarchy_belief': agent.status_drive * 0.6 + agent.dominance_score * 0.4 - 0.3,
            'cooperation_norm': agent.cooperation_propensity * 0.8 + agent.reputation * 0.2 - 0.3,
            'violence_acceptability': agent.aggression_propensity * 0.7 + agent.dominance_score * 0.3 - 0.3,
            'tradition_adherence': agent.conformity_bias * 0.8 - agent.novelty_seeking * 0.4,
            'kinship_obligation': agent.jealousy_sensitivity * 0.3 + 0.2,
        }

        for bfield, trait_derived in belief_specs.items():
            parent_avg = getattr(agent, f'_parent_{bfield}', None)
            if parent_avg is None:
                parent_avg = 0.0
            belief = cb * parent_avg + (1.0 - cb) * trait_derived
            noise = agent.novelty_seeking * rng.normal(0, 0.15)
            setattr(agent, bfield, float(np.clip(belief + noise, -1.0, 1.0)))

    def _initialize_skills(self, agent, society, config):
        """DD26: Initialize skills at maturation. Base from intelligence + parent transmission."""
        base = agent.intelligence_proxy * 0.2
        agent.foraging_skill = base
        agent.combat_skill = base
        agent.social_skill = base
        agent.craft_skill = base if getattr(config, 'resource_types_enabled', False) else 0.0

        # Parent skill transmission
        transmission = config.skill_parent_transmission
        # conformity_bias increases transmission fraction
        transmission *= (0.8 + agent.conformity_bias * 0.4)
        for pid in agent.parent_ids:
            if pid is None:
                continue
            parent = society.get_by_id(pid)
            if parent and parent.alive:
                agent.foraging_skill = min(1.0,
                    agent.foraging_skill + parent.foraging_skill * transmission * 0.5)
                agent.combat_skill = min(1.0,
                    agent.combat_skill + parent.combat_skill * transmission * 0.5)
                agent.social_skill = min(1.0,
                    agent.social_skill + parent.social_skill * transmission * 0.5)
                if getattr(config, 'resource_types_enabled', False):
                    agent.craft_skill = min(1.0,
                        agent.craft_skill + parent.craft_skill * transmission * 0.5)
