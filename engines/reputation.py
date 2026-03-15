"""
Reputation engine — gossip, trust decay, dead agent cleanup, reputation computation.

DD07: Unifies scattered reputation logic into a dedicated engine that runs
once per tick after all other interactions have occurred.

Phases:
  1. Trust decay (slow drift toward neutral 0.5)
  2. Dead agent cleanup (remove dead agents from ledgers)
  3. Gossip (agents share trust info with allies)
  4. Reputation update (compute public reputation from aggregate trust)
"""

from __future__ import annotations
import numpy as np
from models.agent import Agent


class ReputationEngine:
    def run(self, society, config, rng: np.random.Generator) -> list[dict]:
        events = []
        living = society.get_living()
        if not living:
            return events

        # ── Phase 1: Trust decay ─────────────────────────────────────
        # All trust entries slowly drift toward neutral (0.5).
        # Extreme values (far from 0.5) decay slower — deep trust/distrust persists.
        decay_rate = getattr(config, 'trust_decay_rate', 0.01)
        if decay_rate > 0:
            for agent in living:
                for other_id in list(agent.reputation_ledger.keys()):
                    val = agent.reputation_ledger[other_id]
                    distance = abs(val - 0.5)
                    # Extreme values decay slower (diminishing decay)
                    effective_decay = decay_rate * (1.0 - distance * 0.5)
                    if val > 0.5:
                        agent.reputation_ledger[other_id] = max(0.5, val - effective_decay)
                    elif val < 0.5:
                        agent.reputation_ledger[other_id] = min(0.5, val + effective_decay)

        # ── Phase 2: Dead agent cleanup ──────────────────────────────
        # Remove dead agents from ledgers to free slots.
        if getattr(config, 'dead_agent_ledger_cleanup', True):
            for agent in living:
                dead_ids = []
                for other_id in agent.reputation_ledger:
                    other = society.get_by_id(other_id)
                    if other is None or not other.alive:
                        dead_ids.append(other_id)
                for did in dead_ids:
                    del agent.reputation_ledger[did]

        # ── Phase 3: Gossip ──────────────────────────────────────────
        # Agents share trust information with their allies.
        # Each agent picks one ally and shares one random trust entry.
        # The ally updates their own ledger based on the shared info,
        # weighted by how much they trust the gossiper. Includes noise.
        gossip_enabled = getattr(config, 'gossip_enabled', True)
        gossip_rate = getattr(config, 'gossip_rate', 0.1)
        gossip_noise = getattr(config, 'gossip_noise', 0.1)
        gossip_count = 0

        if gossip_enabled and gossip_rate > 0:
            trust_threshold = config.cooperation_trust_threshold

            for agent in living:
                if rng.random() > gossip_rate:
                    continue
                if not agent.reputation_ledger:
                    continue

                # Find allies (agents we trust above threshold)
                allies = []
                for other_id, trust in agent.reputation_ledger.items():
                    if trust > trust_threshold:
                        other = society.get_by_id(other_id)
                        if other and other.alive:
                            allies.append((other, trust))

                if not allies:
                    continue

                # Pick one ally to gossip with
                ally, ally_trust = allies[rng.choice(len(allies))]

                # Pick a random entry to share (not about the ally)
                candidates = [
                    (oid, val) for oid, val in agent.reputation_ledger.items()
                    if oid != ally.id
                ]
                if not candidates:
                    continue

                idx = rng.choice(len(candidates))
                subject_id, gossiper_opinion = candidates[idx]

                # Ally updates their ledger based on gossip
                # Weight by how much ally trusts the gossiper
                # DD15: Emotional intelligence amplifies gossip effectiveness
                ei_factor = 1.0 + agent.emotional_intelligence * 0.3
                gossip_weight = (ally.trust_of(agent.id) - 0.3) * 0.5 * ei_factor
                if gossip_weight <= 0:
                    continue

                # Add noise (telephone game)
                noisy_opinion = gossiper_opinion + rng.normal(0, gossip_noise)
                noisy_opinion = max(0.0, min(1.0, noisy_opinion))

                # Update ally's ledger: nudge toward gossiper's (noisy) opinion
                current = ally.trust_of(subject_id)
                delta = (noisy_opinion - current) * gossip_weight
                ally.remember(subject_id, delta)
                gossip_count += 1

        if gossip_count > 0:
            events.append({
                "type": "gossip_summary",
                "year": society.year,
                "agent_ids": [],
                "description": f"Gossip: {gossip_count} trust entries shared",
            })

        # ── Phase 4: Reputation update ───────────────────────────────
        # Compute public reputation as aggregate of how others see this agent.
        # Blends with existing reputation for stability.
        reputation_from_ledger = getattr(config, 'reputation_from_ledger', True)
        if reputation_from_ledger:
            # Build lookup: for each agent, collect trust values others have of them
            trust_received = {a.id: [] for a in living}
            for agent in living:
                for other_id, trust_val in agent.reputation_ledger.items():
                    if other_id in trust_received:
                        trust_received[other_id].append(trust_val)

            for agent in living:
                scores = trust_received[agent.id]
                if scores:
                    aggregate = float(np.mean(scores))
                    # Blend: 70% aggregate trust, 30% existing reputation (stability)
                    agent.reputation = agent.reputation * 0.3 + aggregate * 0.7
                # If no one has an opinion, reputation stays as-is

        return events
