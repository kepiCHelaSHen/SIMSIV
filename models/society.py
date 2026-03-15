"""
Society model — holds all agents, environment, and coordinates the simulation tick.
"""

from __future__ import annotations
from typing import Optional

import numpy as np

from .agent import Agent, Sex, HERITABLE_TRAITS, create_initial_population
from .environment import Environment
from config import Config


class Society:
    def __init__(self, config: Config, rng: np.random.Generator):
        self.config = config
        self.rng = rng
        self.year = 0
        self.agents: dict[int, Agent] = {}
        self.environment = Environment(config, rng)
        self.events: list[dict] = []  # all events across all years
        self.tick_events: list[dict] = []  # events from current tick only
        self.equilibrium_flagged: bool = False
        self.equilibrium_year: Optional[int] = None

        # DD14: Faction tracking
        self.factions: dict[int, dict] = {}
        self._next_faction_id: int = 1
        self._last_faction_detection: int = -999

        # Initialize population
        pop = create_initial_population(rng, config, config.population_size)
        for a in pop:
            self.agents[a.id] = a

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
        self.events.append(event)

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
            a = Agent(sex=sex, age=int(self.rng.integers(18, 35)), generation=0)
            for trait in HERITABLE_TRAITS:
                if use_pop:
                    val = self.rng.normal(trait_means[trait], trait_stds[trait])
                    setattr(a, trait, float(np.clip(val, 0.0, 1.0)))
                else:
                    setattr(a, trait, float(self.rng.uniform(0.2, 0.8)))
            a.current_resources = float(self.rng.uniform(3, 8))
            a.health = float(self.rng.uniform(0.7, 1.0))
            self.add_agent(a)
        self.add_event({
            "type": "migration",
            "year": self.year,
            "description": f"{count} migrants injected (population rescue)",
        })

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
        return events
