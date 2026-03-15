"""
Society model — holds all agents, environment, and coordinates the simulation tick.
"""

from __future__ import annotations
from typing import Optional

import numpy as np

import logging

from .agent import Agent, Sex, HERITABLE_TRAITS, IdCounter, create_initial_population
from .environment import Environment
from config import Config

_log = logging.getLogger(__name__)


class Society:
    def __init__(self, config: Config, rng: np.random.Generator):
        self.config = config
        self.rng = rng
        self.year = 0
        self.agents: dict[int, Agent] = {}
        self.environment = Environment(config, rng)
        self._event_window: list[dict] = []        # rolling buffer, last N events
        self._event_window_size: int = 500          # configurable cap
        self.event_type_counts: dict[str, int] = {} # running totals by type
        self.tick_events: list[dict] = []  # events from current tick only
        self.equilibrium_flagged: bool = False
        self.equilibrium_year: Optional[int] = None

        # Per-simulation ID generator (Fix #1)
        self.id_counter = IdCounter()

        # DD14: Faction tracking
        self.factions: dict[int, dict] = {}
        self._next_faction_id: int = 1
        self._last_faction_detection: int = -999

        # DD18: Proximity tiers — neighborhood refresh tracking
        self._last_neighborhood_refresh: int = -999

        # DD20: Leadership tracking
        self.faction_leaders: dict[int, dict] = {}

        # Reverse partnership index (Fix #5)
        self._partner_index: dict[int, set[int]] = {}

        # Initialize population
        pop = create_initial_population(rng, config, config.population_size, self.id_counter)
        for a in pop:
            self.agents[a.id] = a
            for pid in a.partner_ids:
                self._index_bond(a.id, pid)

    def get_living(self) -> list[Agent]:
        return [a for a in self.agents.values() if a.alive]

    def get_living_by_sex(self, sex: Sex) -> list[Agent]:
        return [a for a in self.agents.values() if a.alive and a.sex == sex]

    def get_mating_eligible(self) -> tuple[list[Agent], list[Agent]]:
        """Returns (eligible_females, eligible_males)."""
        females = [a for a in self.agents.values()
                   if a.alive and a.sex == Sex.FEMALE and a.can_mate(self.config)]
        males = [a for a in self.agents.values()
                 if a.alive and a.sex == Sex.MALE and a.can_mate(self.config)]
        return females, males

    def get_by_id(self, agent_id: int) -> Optional[Agent]:
        return self.agents.get(agent_id)

    def add_agent(self, agent: Agent):
        self.agents[agent.id] = agent

    def population_size(self) -> int:
        return len(self.get_living())

    def add_event(self, event: dict):
        if "year" not in event:
            event["year"] = self.year
        self.tick_events.append(event)
        # Rolling window — trim from front when over cap
        self._event_window.append(event)
        if len(self._event_window) > self._event_window_size:
            self._event_window.pop(0)
        # Accumulate type counts (never trimmed — cheap summary)
        etype = event.get("type", "unknown")
        self.event_type_counts[etype] = self.event_type_counts.get(etype, 0) + 1

    # ── Partnership index (Fix #5) ─────────────────────────────────

    def _index_bond(self, a_id: int, b_id: int):
        """Record a bond in the reverse index (both directions)."""
        self._partner_index.setdefault(a_id, set()).add(b_id)
        self._partner_index.setdefault(b_id, set()).add(a_id)

    def _unindex_bond(self, a_id: int, b_id: int):
        """Remove a bond from the reverse index (both directions)."""
        self._partner_index.get(a_id, set()).discard(b_id)
        self._partner_index.get(b_id, set()).discard(a_id)

    def get_partners_of(self, agent_id: int) -> set[int]:
        """O(1) lookup: all agent IDs that have agent_id as a partner."""
        return self._partner_index.get(agent_id, set())

    # ── Dead ledger cleanup (Fix #8) ──────────────────────────────

    def purge_dead_from_ledgers(self, dead_ids: set[int]):
        """Remove dead agent IDs from all living agents' reputation ledgers."""
        if not dead_ids:
            return
        for agent in self.get_living():
            for did in dead_ids:
                agent.reputation_ledger.pop(did, None)
        # Clean partner index
        for did in dead_ids:
            self._partner_index.pop(did, None)
        for partners in self._partner_index.values():
            partners -= dead_ids

    def inject_migrants(self, count: int):
        """Emergency population injection to prevent extinction.

        DD04: migrant_trait_source="population" draws traits from current
        population distribution instead of uniform [0.2, 0.8], preventing
        migrants from diluting evolved trait distributions.
        """
        living = self.get_living()
        use_pop = (getattr(self.config, 'migrant_trait_source', 'uniform') == 'population'
                   and len(living) >= 5)

        # Precompute population trait stats for population-derived migrants
        if use_pop:
            trait_means = {}
            trait_stds = {}
            for trait in HERITABLE_TRAITS:
                vals = [getattr(a, trait) for a in living]
                trait_means[trait] = float(np.mean(vals))
                trait_stds[trait] = max(0.03, float(np.std(vals)))

        for i in range(count):
            sex = Sex.FEMALE if i < count // 2 else Sex.MALE
            a = Agent(id=self.id_counter.next(), sex=sex, age=int(self.rng.integers(18, 35)), generation=0)
            for trait in HERITABLE_TRAITS:
                if use_pop:
                    val = self.rng.normal(trait_means[trait], trait_stds[trait])
                    setattr(a, trait, float(np.clip(val, 0.0, 1.0)))
                else:
                    setattr(a, trait, float(self.rng.uniform(0.2, 0.8)))
            total_res = float(self.rng.uniform(3, 8))
            a.current_resources = total_res * 0.6  # DD21
            a.current_tools = total_res * 0.3
            a.current_prestige_goods = total_res * 0.1
            a.health = float(self.rng.uniform(0.7, 1.0))
            self.add_agent(a)
        self.add_event({
            "type": "migration",
            "year": self.year,
            "description": f"{count} migrants injected (population rescue)",
        })

    # ── DD18: Proximity tier helpers ──────────────────────────────

    def household_of(self, agent: Agent) -> set[int]:
        """Return set of agent IDs in same household (tier 1).

        Household = current partners + dependent children + living parents.
        Dynamically computed each time (not stored).
        """
        hh = {agent.id}
        # Partners (symmetric)
        for pid in agent.partner_ids:
            p = self.get_by_id(pid)
            if p and p.alive:
                hh.add(pid)
        # Dependent children
        child_dep = getattr(self.config, 'child_dependency_years', 5)
        for oid in agent.offspring_ids:
            child = self.get_by_id(oid)
            if child and child.alive and child.age < child_dep:
                hh.add(oid)
        # Living parents
        for pid in agent.parent_ids:
            if pid is not None:
                parent = self.get_by_id(pid)
                if parent and parent.alive:
                    hh.add(pid)
        # Reverse partner lookup via index (O(1) instead of O(N))
        for pid in self.get_partners_of(agent.id):
            p = self.get_by_id(pid)
            if p and p.alive:
                hh.add(pid)
        return hh

    def refresh_neighborhoods(self, config, rng):
        """Recompute neighborhood_ids for all living agents (DD18).

        Called periodically (every neighborhood_refresh_interval years).
        Neighborhood = trusted allies + same-faction + siblings, capped.
        """
        interval = getattr(config, 'neighborhood_refresh_interval', 3)
        if self.year - self._last_neighborhood_refresh < interval:
            return
        self._last_neighborhood_refresh = self.year

        trust_thresh = getattr(config, 'neighborhood_trust_threshold', 0.5)
        max_size = getattr(config, 'neighborhood_size_max', 40)
        living = self.get_living()
        living_ids = {a.id for a in living}

        for agent in living:
            candidates = set()

            # 1. Agents in ledger with trust > threshold
            for other_id, trust_val in agent.reputation_ledger.items():
                if trust_val > trust_thresh and other_id in living_ids:
                    candidates.add(other_id)

            # 2. Same faction members
            if agent.faction_id is not None:
                for a in living:
                    if a.id != agent.id and a.faction_id == agent.faction_id:
                        candidates.add(a.id)

            # 3. Siblings (shared parent_ids)
            if agent.parent_ids != (None, None):
                for a in living:
                    if a.id == agent.id:
                        continue
                    for pid in agent.parent_ids:
                        if pid is not None and pid in a.parent_ids:
                            candidates.add(a.id)
                            break

            # Remove self
            candidates.discard(agent.id)

            # Cap at max_size; if over, keep trusted first
            if len(candidates) > max_size:
                scored = []
                for cid in candidates:
                    trust = agent.reputation_ledger.get(cid, 0.5)
                    scored.append((cid, trust))
                scored.sort(key=lambda x: x[1], reverse=True)
                candidates = {cid for cid, _ in scored[:max_size]}

            agent.neighborhood_ids = list(candidates)

    # ── DD19: Migration ──────────────────────────────────────────

    def process_migration(self, config, rng) -> list[dict]:
        """Process emigration and immigration for this tick (DD19).

        Returns list of events.
        """
        events = []
        if not getattr(config, 'migration_enabled', False):
            return events

        # ── Emigration ──────────────────────────────────────────
        living = self.get_living()
        pop = len(living)
        if pop == 0:
            return events

        emigrated = []
        for agent in living:
            p = config.base_emigration_rate

            # Push: resource stress
            if agent.current_resources < config.emigration_resource_threshold:
                stress = max(0, config.emigration_resource_threshold - agent.current_resources)
                p += 0.01 * stress

            # Push: ostracism
            if agent.reputation < config.emigration_reputation_threshold:
                p += 0.02

            # Push: mating failure (young unmated males)
            if (agent.sex == Sex.MALE and agent.age >= 18 and not agent.is_bonded
                    and agent.age <= 35 and agent.status_drive > 0.4):
                years_adult = agent.age - max(15, getattr(config, 'age_first_reproduction', 15))
                if years_adult >= config.emigration_unmated_years:
                    p += 0.03

            # Push: overcrowding
            cap_ratio = pop / config.carrying_capacity
            if cap_ratio > config.overcrowding_emigration_threshold:
                p += 0.01 * (cap_ratio - config.overcrowding_emigration_threshold)

            # Anchor: bonded with children = much less likely to leave
            if agent.is_bonded and agent.offspring_ids:
                has_dep = any(
                    (c := self.get_by_id(oid)) and c.alive
                    and c.age < config.child_dependency_years
                    for oid in agent.offspring_ids
                )
                if has_dep:
                    p *= config.emigration_family_anchor

            # Children don't emigrate alone
            if agent.age < 15:
                continue

            p = max(0.0, min(0.2, p))
            if rng.random() < p:
                emigrated.append(agent)

        for agent in emigrated:
            agent.die("emigration", self.year)
            # Remove from partners
            for pid in list(agent.partner_ids):
                partner = self.get_by_id(pid)
                if partner and partner.alive:
                    partner.remove_bond(agent.id)
            events.append({
                "type": "emigration",
                "year": self.year,
                "agent_ids": [agent.id],
                "description": f"Agent {agent.id} emigrated (age {agent.age})",
            })

        # ── Immigration ─────────────────────────────────────────
        living = self.get_living()  # refresh after emigration
        pop = len(living)
        if pop == 0:
            return events

        avg_res = float(np.mean([a.current_resources for a in living]))
        cap_ratio = pop / config.carrying_capacity

        p_imm = config.base_immigration_rate
        # Pull: resource surplus
        if avg_res > config.immigration_resource_threshold:
            p_imm *= 1.5
        # Pull: population vacancy
        vacancy = max(0, 1.0 - cap_ratio)
        p_imm *= (1.0 + vacancy * 0.5)
        # Pull: cooperation
        avg_coop = float(np.mean([a.cooperation_propensity for a in living]))
        p_imm *= (1.0 + avg_coop * 0.5)
        # DD27: Outgroup tolerance modulates immigration pull
        avg_outgroup_tol = float(np.mean([a.outgroup_tolerance for a in living]))
        p_imm *= (0.7 + avg_outgroup_tol * 0.6)

        p_imm = max(0.0, min(0.1, p_imm))

        # Number of immigrants this tick (Poisson-like)
        n_immigrants = 0
        while rng.random() < p_imm and n_immigrants < 3:
            n_immigrants += 1
            p_imm *= 0.3  # diminishing returns for multiple immigrants

        if n_immigrants > 0:
            trait_source = getattr(config, 'immigrant_trait_source', 'population_mean')

            # Precompute population trait stats
            if trait_source == 'population_mean' and len(living) >= 5:
                trait_stats = {}
                for trait in HERITABLE_TRAITS:
                    vals = [getattr(a, trait) for a in living]
                    trait_stats[trait] = (float(np.mean(vals)),
                                         max(0.05, float(np.std(vals))))

            for _ in range(n_immigrants):
                sex = Sex.FEMALE if rng.random() < 0.5 else Sex.MALE
                age = int(rng.integers(18, 35))
                a = Agent(id=self.id_counter.next(), sex=sex, age=age, generation=0)

                for trait in HERITABLE_TRAITS:
                    if trait_source == 'population_mean' and len(living) >= 5:
                        mean, std = trait_stats[trait]
                        val = rng.normal(mean, std)
                    elif trait_source == 'external':
                        val = rng.normal(0.5, 0.15)
                        if trait == 'aggression_propensity':
                            val += getattr(config, 'external_trait_aggression_offset', 0.0)
                    else:  # random
                        val = rng.uniform(0.0, 1.0)
                    setattr(a, trait, float(np.clip(val, 0.0, 1.0)))

                total_res = float(rng.uniform(3, 8))
                a.current_resources = total_res * 0.6  # DD21
                a.current_tools = total_res * 0.3
                a.current_prestige_goods = total_res * 0.1
                a.health = float(rng.uniform(0.7, 1.0))
                a.prestige_score = float(rng.uniform(0, 0.1))
                a.dominance_score = float(rng.uniform(0, 0.1))

                # DD19: Migration tracking
                a.origin_band_id = 1
                a.immigration_year = self.year
                a.generation_in_band = 0

                # Set initial trust toward existing members
                init_trust = getattr(config, 'immigrant_initial_trust', 0.4)
                sample_size = min(10, len(living))
                if sample_size > 0:
                    contacts = rng.choice(living, size=sample_size, replace=False)
                    for contact in contacts:
                        a.remember(contact.id, init_trust - 0.5)  # delta from 0.5

                self.add_agent(a)
                events.append({
                    "type": "immigration",
                    "year": self.year,
                    "agent_ids": [a.id],
                    "description": f"Immigrant {a.id} arrived (age {age}, {sex.value})",
                })

        return events

    def detect_factions(self, config, rng) -> list[dict]:
        """Detect emergent factions from trust network (DD14).

        Uses connected-component analysis on the mutual trust graph.
        Called periodically (every faction_detection_interval years).
        """
        events = []

        interval = config.faction_detection_interval
        if self.year - self._last_faction_detection < interval:
            return events
        self._last_faction_detection = self.year

        living = self.get_living()
        if not living:
            self.factions.clear()
            return events

        threshold = config.faction_min_trust_threshold
        min_size = config.faction_min_size
        max_size = config.faction_max_size
        living_ids = {a.id for a in living}

        # ── Phase 1: Connected components on mutual trust graph ────
        visited = set()
        components = []

        for agent in living:
            if agent.id in visited:
                continue
            component = []
            queue = [agent.id]
            while queue:
                aid = queue.pop(0)
                if aid in visited:
                    continue
                visited.add(aid)
                component.append(aid)
                a = self.get_by_id(aid)
                if not a:
                    continue
                for other_id, trust_val in a.reputation_ledger.items():
                    if (trust_val > threshold
                            and other_id in living_ids
                            and other_id not in visited):
                        other = self.get_by_id(other_id)
                        if other and other.trust_of(aid) > threshold:
                            queue.append(other_id)
            components.append(component)

        # ── Phase 2: Leader-based merge (political alliance) ──────
        # If leaders of existing factions in separate components have
        # high mutual trust, merge those components.
        if self.factions:
            comp_idx = {}
            for idx, comp in enumerate(components):
                for aid in comp:
                    comp_idx[aid] = idx

            leader_pairs = [(fid, fdata['leader_id'])
                            for fid, fdata in self.factions.items()
                            if fdata['leader_id'] in living_ids]
            merge_trust = config.faction_merge_trust
            merged_indices = set()

            for i in range(len(leader_pairs)):
                for j in range(i + 1, len(leader_pairs)):
                    _, lid_i = leader_pairs[i]
                    _, lid_j = leader_pairs[j]
                    if lid_i not in comp_idx or lid_j not in comp_idx:
                        continue
                    ci, cj = comp_idx[lid_i], comp_idx[lid_j]
                    if ci == cj or ci in merged_indices or cj in merged_indices:
                        continue
                    a_i = self.get_by_id(lid_i)
                    a_j = self.get_by_id(lid_j)
                    if (a_i and a_j
                            and a_i.trust_of(lid_j) > merge_trust
                            and a_j.trust_of(lid_i) > merge_trust):
                        # Merge component cj into ci
                        components[ci].extend(components[cj])
                        for aid in components[cj]:
                            comp_idx[aid] = ci
                        components[cj] = []
                        merged_indices.add(cj)

            components = [c for c in components if c]

        # ── Phase 3: Filter by min_size + schism ──────────────────
        valid = []
        factionless = set()
        effective_schism_p = 1.0 - (1.0 - config.faction_schism_pressure) ** interval

        for comp in components:
            if len(comp) < min_size:
                factionless.update(comp)
                continue

            if len(comp) > max_size and rng.random() < effective_schism_p:
                # Split by trust affinity to two seed agents
                seed1 = max(comp, key=lambda aid: (
                    self.get_by_id(aid).prestige_score
                    if self.get_by_id(aid) else 0))
                seed2 = min(
                    (aid for aid in comp if aid != seed1),
                    key=lambda aid: (
                        self.get_by_id(aid).trust_of(seed1)
                        if self.get_by_id(aid) else 0))

                g1, g2 = [], []
                for aid in comp:
                    a = self.get_by_id(aid)
                    if not a:
                        continue
                    if a.trust_of(seed1) >= a.trust_of(seed2):
                        g1.append(aid)
                    else:
                        g2.append(aid)

                for g in (g1, g2):
                    if len(g) >= min_size:
                        valid.append(g)
                    else:
                        factionless.update(g)

                events.append({
                    "type": "faction_schism",
                    "year": self.year,
                    "agent_ids": [],
                    "description": (f"Faction schism: {len(comp)} split "
                                    f"into {len(g1)}/{len(g2)}"),
                })
            else:
                valid.append(comp)

        # ── Phase 4: Match to existing factions by overlap ────────
        old = dict(self.factions)
        new_factions = {}
        used = set()

        for comp in valid:
            comp_set = set(comp)
            best_fid = None
            best_overlap = 0
            for fid, fdata in old.items():
                if fid in used:
                    continue
                overlap = len(comp_set & set(fdata['members']))
                if overlap > best_overlap and overlap > len(comp) * 0.3:
                    best_overlap = overlap
                    best_fid = fid

            if best_fid is not None:
                fid = best_fid
                used.add(fid)
                formed = old[fid]['formed_year']
            else:
                fid = self._next_faction_id
                self._next_faction_id += 1
                formed = self.year
                events.append({
                    "type": "faction_formed",
                    "year": self.year,
                    "agent_ids": comp[:3],
                    "description": f"Faction {fid} formed ({len(comp)} members)",
                })

            leader = max(comp, key=lambda aid: (
                self.get_by_id(aid).prestige_score
                if self.get_by_id(aid) else 0))

            new_factions[fid] = {
                'members': list(comp),
                'leader_id': leader,
                'formed_year': formed,
            }

            for aid in comp:
                a = self.get_by_id(aid)
                if a:
                    a.faction_id = fid

        # Clear faction_id for factionless agents
        for aid in factionless:
            a = self.get_by_id(aid)
            if a and a.alive:
                a.faction_id = None

        # Clear for agents in dissolved factions
        for fid, fdata in old.items():
            if fid not in new_factions:
                for aid in fdata['members']:
                    a = self.get_by_id(aid)
                    if a and a.alive and a.faction_id == fid:
                        a.faction_id = None

        self.factions = new_factions

        # DD20: Update faction leaders after re-detection
        if getattr(config, 'leadership_enabled', False):
            self._update_faction_leaders(config)

        return events

    def _update_faction_leaders(self, config):
        """Select war leaders and peace chiefs for each faction (DD20).

        War leader: highest dominance_score in faction.
        Peace chief: highest prestige_score in faction.
        Must exceed faction average * leadership_minimum_threshold.
        """
        threshold = getattr(config, 'leadership_minimum_threshold', 1.2)
        age_limit = getattr(config, 'leadership_age_limit', 55)
        new_leaders = {}

        for fid, fdata in self.factions.items():
            members = [self.get_by_id(aid) for aid in fdata.get('members', [])]
            members = [a for a in members if a and a.alive]
            if not members:
                continue

            eligible = [a for a in members
                        if not (a.age > age_limit and a.health < 0.5)]

            if not eligible:
                continue

            # War leader: highest dominance
            avg_dom = float(np.mean([a.dominance_score for a in members]))
            war_candidates = [a for a in eligible
                              if a.dominance_score > avg_dom * threshold]
            war_leader = None
            if war_candidates:
                war_leader = max(war_candidates, key=lambda a: a.dominance_score)

            # Peace chief: highest prestige
            avg_pres = float(np.mean([a.prestige_score for a in members]))
            peace_candidates = [a for a in eligible
                                if a.prestige_score > avg_pres * threshold]
            peace_chief = None
            if peace_candidates:
                peace_chief = max(peace_candidates, key=lambda a: a.prestige_score)

            new_leaders[fid] = {
                'war_leader': war_leader.id if war_leader else None,
                'peace_chief': peace_chief.id if peace_chief else None,
                'established_year': self.year,
            }

        self.faction_leaders = new_leaders
