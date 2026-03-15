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
                # DD26: Social skill boosts gossip effectiveness
                social_factor = 1.0
                if getattr(config, 'skills_enabled', False):
                    social_factor = 0.9 + agent.social_skill * 0.2
                gossip_weight = (ally.trust_of(agent.id) - 0.3) * 0.5 * ei_factor * social_factor
                if gossip_weight <= 0:
                    continue

                # Add noise (telephone game)
                # DD18: Cross-tier gossip has more noise (information degrades)
                effective_noise = gossip_noise
                if getattr(config, 'proximity_tiers_enabled', False):
                    neighborhood_set = set(agent.neighborhood_ids)
                    if ally.id not in neighborhood_set:
                        effective_noise *= getattr(
                            config, 'cross_tier_gossip_noise_multiplier', 2.0)
                noisy_opinion = gossiper_opinion + rng.normal(0, effective_noise)
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

        # ── Phase 5 (DD25): Belief evolution (every 3 ticks) ──────────
        if (getattr(config, 'beliefs_enabled', False)
                and society.year % 3 == 0):
            belief_events = self._evolve_beliefs(living, society, config, rng)
            events.extend(belief_events)

        # ── Phase 6 (DD26): Skill decay, experience growth, mentoring ─
        if getattr(config, 'skills_enabled', False):
            skill_events = self._update_skills(living, society, config, rng)
            events.extend(skill_events)

        return events

    def _evolve_beliefs(self, living: list[Agent], society, config,
                        rng: np.random.Generator) -> list[dict]:
        """DD25: Update beliefs via social influence, experience, and mutation."""
        events = []
        belief_fields = ['hierarchy_belief', 'cooperation_norm',
                         'violence_acceptability', 'tradition_adherence',
                         'kinship_obligation']

        influence_rate = config.belief_social_influence_rate
        prestige_weight = config.prestige_transmission_weight

        # ── Social influence: neighborhood prestige-biased ──────────
        for agent in living:
            if agent.age < 15:
                continue
            cb = agent.conformity_bias
            ns = agent.novelty_seeking

            # Find influential neighbors
            if hasattr(agent, 'neighborhood_ids') and agent.neighborhood_ids:
                neighbors = []
                for nid in agent.neighborhood_ids:
                    other = society.get_by_id(nid)
                    if other and other.alive and other.age >= 15:
                        trust = agent.trust_of(nid)
                        weight = trust * (0.4 + other.prestige_score * prestige_weight)
                        neighbors.append((other, weight))
            else:
                neighbors = []

            if neighbors:
                total_w = sum(w for _, w in neighbors)
                if total_w > 0:
                    for bfield in belief_fields:
                        weighted_avg = sum(
                            getattr(o, bfield, 0.0) * w
                            for o, w in neighbors) / total_w
                        current = getattr(agent, bfield)
                        # Conformity drives toward group; novelty resists
                        effective_rate = influence_rate * cb * max(0.2, 1.0 - ns * 0.5)
                        delta = effective_rate * (weighted_avg - current)
                        setattr(agent, bfield,
                                float(np.clip(current + delta, -1.0, 1.0)))

        # ── Experience-based belief update ──────────────────────────
        exp_rate = config.belief_experience_update_rate
        for event in society.tick_events:
            etype = event.get("type")
            outcome = event.get("outcome", {})

            if etype == "conflict":
                winner_id = outcome.get("winner")
                loser_id = outcome.get("loser")
                agg_id = outcome.get("aggressor")
                winner = society.get_by_id(winner_id) if winner_id else None
                loser = society.get_by_id(loser_id) if loser_id else None

                if winner and winner.alive:
                    winner.violence_acceptability = float(np.clip(
                        winner.violence_acceptability + exp_rate, -1.0, 1.0))
                    # Resource loot → hierarchy belief up, cooperation down
                    winner.hierarchy_belief = float(np.clip(
                        winner.hierarchy_belief + exp_rate * 0.67, -1.0, 1.0))
                    winner.cooperation_norm = float(np.clip(
                        winner.cooperation_norm - exp_rate * 0.67, -1.0, 1.0))
                if loser and loser.alive:
                    loser.violence_acceptability = float(np.clip(
                        loser.violence_acceptability - exp_rate * 1.67, -1.0, 1.0))

            elif etype == "resource_transfers":
                # Sharing events boost cooperation norm for participants
                # (we can't identify exact participants from summary event,
                # so we apply a small boost to all cooperative agents)
                pass  # handled via cooperation sharing in resources engine

            elif etype == "punishment":
                for aid in event.get("agent_ids", []):
                    agent = society.get_by_id(aid)
                    if agent and agent.alive:
                        agent.violence_acceptability = float(np.clip(
                            agent.violence_acceptability - exp_rate * 1.33, -1.0, 1.0))

            elif etype == "leadership_arbitration":
                # Witnessing peace chief generosity
                for aid in event.get("agent_ids", []):
                    agent = society.get_by_id(aid)
                    if agent and agent.alive:
                        agent.cooperation_norm = float(np.clip(
                            agent.cooperation_norm + exp_rate * 0.67, -1.0, 1.0))

        # ── Cooperation sharing: direct experience update ───────────
        # Agents who shared resources this tick get a cooperation_norm boost
        for agent in living:
            if agent.age < 15:
                continue
            if (agent.cooperation_propensity > 0.3
                    and agent.current_resources > 3.0):
                # Proxy for having participated in sharing
                agent.cooperation_norm = float(np.clip(
                    agent.cooperation_norm + exp_rate * 0.33
                    * agent.cooperation_propensity, -1.0, 1.0))

        # ── Belief mutation (cultural innovation) ───────────────────
        mutation_rate = config.belief_mutation_rate
        for agent in living:
            if agent.age < 15:
                continue
            ns = agent.novelty_seeking
            for bfield in belief_fields:
                noise = rng.normal(0, ns * mutation_rate)
                current = getattr(agent, bfield)
                setattr(agent, bfield,
                        float(np.clip(current + noise, -1.0, 1.0)))

        # ── Ideological tension: distrust between belief-distant agents ──
        tension_thresh = config.belief_ideological_tension_threshold
        tension_conflicts = 0
        for agent in living:
            if agent.age < 15:
                continue
            for nid in agent.neighborhood_ids[:10]:  # limit for performance
                other = society.get_by_id(nid)
                if not other or not other.alive or other.age < 15:
                    continue
                max_tension = 0.0
                for bfield in belief_fields:
                    diff = abs(getattr(agent, bfield) - getattr(other, bfield))
                    if diff > max_tension:
                        max_tension = diff
                if max_tension > tension_thresh:
                    # Ideological tension → distrust
                    agent.remember(nid, -0.05 * (max_tension - tension_thresh))
                    tension_conflicts += 1

        # ── Belief revolution detection ─────────────────────────────
        # Track band-level belief means vs historical (stored on society)
        adults = [a for a in living if a.age >= 15]
        if adults:
            current_means = {}
            for bfield in belief_fields:
                current_means[bfield] = float(np.mean(
                    [getattr(a, bfield) for a in adults]))

            prev_means = getattr(society, '_belief_means_history', None)
            if prev_means is not None:
                for bfield in belief_fields:
                    shift = abs(current_means[bfield] - prev_means.get(bfield, 0.0))
                    if shift > config.belief_revolution_threshold:
                        events.append({
                            "type": "belief_revolution",
                            "year": society.year,
                            "agent_ids": [],
                            "description": (f"Belief revolution: {bfield} shifted "
                                            f"{shift:.2f} (threshold "
                                            f"{config.belief_revolution_threshold})"),
                        })
            society._belief_means_history = current_means

        return events

    def _update_skills(self, living: list[Agent], society, config,
                       rng: np.random.Generator) -> list[dict]:
        """DD26: Skill decay, experience-based growth, and mentoring."""
        events = []
        mentor_count = 0
        resource_types = getattr(config, 'resource_types_enabled', False)
        intel_mult = config.skill_learning_intelligence_multiplier
        decline_start = config.skill_age_learning_decline_start

        # Compute band average resource gain for foraging skill threshold
        avg_resources = float(np.mean(
            [a.current_resources for a in living])) if living else 5.0

        for agent in living:
            if agent.age < 15:
                continue

            # Age learning rate modifier
            age_lr = 1.0
            if agent.age > decline_start:
                age_lr = max(0.3, 1.0 - (agent.age - decline_start) * 0.03)

            lr = config.skill_learning_rate_base * age_lr

            # ── Foraging skill growth ──────────────────────────────
            if agent.current_resources > avg_resources * 1.1:
                gain = lr * (1.0 - agent.foraging_skill * 0.8)
                gain *= (0.7 + agent.intelligence_proxy * intel_mult)
                agent.foraging_skill = min(1.0, agent.foraging_skill + gain)

            # ── Social skill growth ────────────────────────────────
            # Agents with active cooperation networks grow social skill
            allies = sum(1 for t in agent.reputation_ledger.values() if t > 0.5)
            if allies > 2:
                gain = lr * 0.5 * (1.0 - agent.social_skill * 0.8)
                gain *= (0.8 + agent.emotional_intelligence * 0.4)
                agent.social_skill = min(1.0, agent.social_skill + gain)
            # Bond formation boost
            if agent.is_bonded:
                agent.social_skill = min(1.0, agent.social_skill + lr * 0.3)

            # ── Craft skill growth (only if resource types enabled) ──
            if resource_types and agent.current_tools > 0.5:
                gain = lr * (1.0 - agent.craft_skill * 0.8)
                gain *= (0.7 + agent.intelligence_proxy * intel_mult)
                agent.craft_skill = min(1.0, agent.craft_skill + gain)

            # ── Skill decay ────────────────────────────────────────
            agent.foraging_skill = max(0.0,
                agent.foraging_skill - config.skill_foraging_decay)
            agent.combat_skill = max(0.0,
                agent.combat_skill - config.skill_combat_decay)
            agent.social_skill = max(0.0,
                agent.social_skill - config.skill_social_decay)
            if resource_types:
                agent.craft_skill = max(0.0,
                    agent.craft_skill - config.skill_craft_decay)

        # ── Combat skill growth from conflict events ──────────────
        for event in society.tick_events:
            if event.get("type") != "conflict":
                continue
            outcome = event.get("outcome", {})
            winner_id = outcome.get("winner")
            loser_id = outcome.get("loser")
            winner = society.get_by_id(winner_id) if winner_id else None
            loser = society.get_by_id(loser_id) if loser_id else None

            if winner and winner.alive:
                opp_skill = loser.combat_skill if loser else 0.0
                gain = 0.02 * max(0.1, opp_skill - winner.combat_skill + 0.3)
                winner.combat_skill = min(1.0, winner.combat_skill + gain)
            if loser and loser.alive:
                loser.combat_skill = min(1.0, loser.combat_skill + 0.005)

        # ── Mentoring within factions ─────────────────────────────
        transfer_rate = config.skill_mentor_transfer_rate
        skill_domains = ['foraging_skill', 'combat_skill', 'social_skill']
        if resource_types:
            skill_domains.append('craft_skill')

        factions = getattr(society, 'factions', {})
        for fid, fdata in factions.items():
            members = [society.get_by_id(aid) for aid in fdata.get('members', [])]
            members = [a for a in members if a and a.alive and a.age >= 15]
            if len(members) < 2:
                continue

            for skill in skill_domains:
                mentors = [a for a in members if getattr(a, skill) > 0.6]
                apprentices = [a for a in members if getattr(a, skill) < 0.4]
                for mentor in mentors[:3]:  # limit mentors per domain
                    for apprentice in apprentices[:3]:
                        if mentor.id == apprentice.id:
                            continue
                        transfer = getattr(mentor, skill) * transfer_rate
                        current = getattr(apprentice, skill)
                        setattr(apprentice, skill, min(1.0, current + transfer))
                        mentor_count += 1

            # Elder teaching: social skill from elders to youth
            elders = [a for a in members
                      if a.life_stage == "ELDER" and a.social_skill > 0.5]
            youth = [a for a in members if a.life_stage == "YOUTH"]
            for elder in elders[:2]:
                for young in youth[:3]:
                    young.social_skill = min(1.0, young.social_skill + 0.03)
                    mentor_count += 1

        if mentor_count > 0:
            events.append({
                "type": "mentor_events",
                "year": society.year,
                "agent_ids": [],
                "description": f"Mentoring: {mentor_count} skill transfers",
            })

        return events
