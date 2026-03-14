"""
Institution engine — applies norm enforcement and institutional effects.

v1 institutions are toggle-based with continuous strength (0.0-1.0).
Institutions modulate behavior of other engines by modifying config-level parameters
or directly affecting agent state.
"""

from __future__ import annotations
import numpy as np


class InstitutionEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()

        # ── Monogamy enforcement ─────────────────────────────────────
        if config.monogamy_enforced and config.law_strength > 0:
            for agent in living:
                if agent.pair_bond_id is not None:
                    # Monogamy norm: penalize agents caught with multiple partners
                    # (checked during mating engine — here we just update reputation)
                    pass  # Actual enforcement happens in mating engine via config flag

        # ── Violence punishment ──────────────────────────────────────
        # This modifies conflict outcomes — tracked via config.violence_punishment_strength
        # The conflict engine reads this value directly

        # ── Inheritance execution ────────────────────────────────────
        # Handle deceased agents' resources this tick
        dead_this_tick = [e for e in society.tick_events if e.get("type") == "death"]
        for death_event in dead_this_tick:
            agent_ids = death_event.get("agent_ids", [])
            for aid in agent_ids:
                agent = society.get_by_id(aid)
                if agent and agent.current_resources > 0:
                    inheritance_events = self._distribute_inheritance(
                        agent, society, config
                    )
                    events.extend(inheritance_events)

        return events

    def _distribute_inheritance(self, deceased: Agent, society, config) -> list[dict]:
        """Distribute a deceased agent's resources to heirs."""
        events = []
        resources = deceased.current_resources
        if resources <= 0:
            return events

        if not config.inheritance_law_enabled:
            # Resources simply vanish (no inheritance system)
            deceased.current_resources = 0
            return events

        # Find living offspring
        heirs = [society.get_by_id(oid) for oid in deceased.offspring_ids]
        heirs = [h for h in heirs if h and h.alive]

        # Also consider pair bond partner
        partner = society.get_by_id(deceased.pair_bond_id) if deceased.pair_bond_id else None
        if partner and partner.alive:
            heirs.insert(0, partner)

        if not heirs:
            deceased.current_resources = 0
            return events

        if config.inheritance_model == "equal_split":
            share = resources / len(heirs)
            for heir in heirs:
                heir.current_resources += share
        elif config.inheritance_model == "primogeniture":
            # Eldest offspring (or partner if no offspring)
            heirs[0].current_resources += resources
        else:
            # "none" — resources vanish
            pass

        deceased.current_resources = 0
        events.append({
            "type": "inheritance",
            "year": society.year,
            "agent_ids": [deceased.id] + [h.id for h in heirs],
            "description": f"Agent {deceased.id} resources ({resources:.1f}) distributed to {len(heirs)} heirs",
        })
        return events
