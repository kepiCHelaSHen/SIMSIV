# SIMSIV — PROMPT: DEEP DIVE 18 — PROXIMITY TIERS AND SOCIAL NETWORK STRUCTURE
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_18_proximity.md
# Use: Send to Claude after DD17 is complete
# Priority: PHASE C, Sprint 11

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 18 on the SIMSIV proximity and social network model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py
  4. D:\EXPERIMENTS\SIM\models\society.py
  5. D:\EXPERIMENTS\SIM\engines\resources.py (cooperation sharing)
  6. D:\EXPERIMENTS\SIM\engines\conflict.py (target selection)
  7. D:\EXPERIMENTS\SIM\engines\mating.py (mate search pool)
  8. D:\EXPERIMENTS\SIM\STATUS.md

Currently every agent in a 500-person band can potentially interact with every
other agent. This produces unrealistically high mixing and overly dense social
networks. Real human groups interact primarily within small proximity-defined
subgroups — households, work groups, neighborhoods — with interactions becoming
rarer as social distance increases. This deep dive adds a three-tier proximity
structure that shapes who interacts with whom without requiring full 2D spatial
coordinates.

================================================================================
DEEP DIVE 18: PROXIMITY TIERS
================================================================================

DESIGN PHILOSOPHY:
  NOT a spatial model — we are not adding x,y coordinates to agents.
  Instead: a soft probabilistic interaction distance model.
  Three tiers define interaction probability, not interaction possibility.
  Any agent can still interact with any other — but probability falls off
  sharply outside your immediate tier.

THE THREE TIERS:

  TIER 1 — HOUSEHOLD (3-8 agents)
    Who: immediate family + bonded pair + dependent children
    Dynamically computed from: partner_ids + offspring_ids (under dependency age)
                               + parent_ids (if still alive and nearby)
    Interaction multiplier: 4x base probability for all interactions
    Always current — rebuilds each tick from relationship state

  TIER 2 — NEIGHBORHOOD (15-50 agents)
    Who: extended kin + trusted allies (reputation_ledger trust > 0.5)
         + same faction members
    Interaction multiplier: 2x base probability
    Soft boundary — changes as trust relationships evolve
    Computed from: kin links + ledger trust + faction_id match

  TIER 3 — BAND (full population)
    Who: everyone else
    Interaction multiplier: 1x base probability (current default behavior)
    Unchanged from current model

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. INTERACTION PROBABILITY WEIGHTING
   Each engine that selects targets or partners should weight by proximity tier:
   - Conflict target selection: 4x household, 2x neighborhood, 1x band
     Exception: jealousy conflicts target specific rivals regardless of tier
   - Cooperation sharing: only share within tier 2 (neighborhood) or closer
     Except: high cooperation_propensity agents reach into tier 3 occasionally
   - Mating: females evaluate tier 2 males first; tier 3 males enter pool only
     if tier 2 candidates are insufficient (mating market constraint)
   - Gossip: trust information spreads within tiers (slower cross-tier)
   - Resource display: witnessed primarily within tier 2

B. HOUSEHOLD COMPUTATION
   Household is dynamically computed each tick. Not stored — derived.
   household_of(agent) returns:
     - agent.partner_ids (all current partners)
     - [a.id for a in agents if agent.id in a.partner_ids] (symmetric)
     - [oid for oid in agent.offspring_ids if agents[oid].age < child_dependency_years]
     - [pid for pid in agent.parent_ids if pid and agents[pid].alive]
   Size range: 1 (isolated) to ~12 (large polygynous household)
   This is the most accurate tier — always reflects current relationship state

C. NEIGHBORHOOD COMPUTATION
   Neighborhood computed periodically (every 3 years — not every tick).
   neighborhood_of(agent) returns up to neighborhood_size_max agents:
     Priority order:
     1. Agents in agent.reputation_ledger with trust > 0.5
     2. Agents in same faction (faction_id match)
     3. Agents who share parent_ids with agent (siblings, cousins)
     4. Fill remaining slots randomly from band
   Cap at neighborhood_size_max (default 40)
   Store as agent.neighborhood_ids: list[int] (refreshed every 3yr)

D. EFFECTS ON EACH ENGINE

   Resources:
   - Kin trust maintenance: already household-appropriate (parent-child only)
   - Cooperation sharing: restrict to neighborhood_ids + household
     (currently shares with anyone trusted — now only with nearby trusted)
   - This makes cooperation networks more realistic and slower to form

   Conflict:
   - Target selection weights: multiply by tier_weight for each candidate
   - Most conflicts occur within neighborhood (resource envy, rivalry)
   - Cross-tier conflicts are rare but still possible (traveling agents, raids)
   - Jealousy conflicts remain targeted regardless of tier

   Mating:
   - Female evaluates neighborhood males first (full weight)
   - Band males available at 0.3x weight (less visible, less known)
   - This creates local mate markets — small bands have fewer choices
   - Endogamy naturally increases (marry who you know)

   Gossip:
   - Trust information propagates within tier first (lower noise within tier)
   - Cross-tier gossip: 2x noise multiplier (information degrades faster)

E. EFFECTS ON FACTION FORMATION
   Proximity becomes a third driver of faction formation (alongside trust and kin):
   - Agents who are in each other's neighborhoods consistently over 5yr
     get a proximity_faction_bond bonus that contributes to connected component
   - This means geographic clusters of neighbors form factions even without
     strong trust ties — just by repeated proximity
   - Makes factions more realistic: you're in a faction partly because of
     who lives near you, not just who you trust

F. ISOLATION AND CONNECTIVITY METRICS
   New metrics to track:
   - avg_household_size: mean household size across all agents
   - avg_neighborhood_size: mean neighborhood size
   - network_clustering_coefficient: fraction of agent's neighbors who
     are also neighbors with each other (how cliquey is the network)
   - cross_tier_conflict_rate: fraction of conflicts that are cross-neighborhood
   - local_mate_rate: fraction of pair bonds formed within neighborhood

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_18_proximity.md — design decisions
2. models/agent.py — neighborhood_ids field, household computation method
3. models/society.py — neighborhood refresh logic (every 3yr)
4. engines/resources.py — cooperation sharing restricted to neighborhood
5. engines/conflict.py — tier-weighted target selection
6. engines/mating.py — neighborhood-first mate search
7. engines/reputation.py — tier-differentiated gossip noise
8. config.py additions — proximity parameters
9. metrics/collectors.py — 4 new proximity metrics
10. DEV_LOG.md entry
11. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

proximity_tiers_enabled: bool = True
household_interaction_multiplier: float = 4.0
neighborhood_interaction_multiplier: float = 2.0
neighborhood_size_max: int = 40
neighborhood_refresh_interval: int = 3       # years between recomputation
neighborhood_trust_threshold: float = 0.5    # min trust to be in neighborhood
band_mate_weight: float = 0.3               # mate weight for out-of-neighborhood males
cross_tier_gossip_noise_multiplier: float = 2.0

================================================================================
CONSTRAINTS
================================================================================

- NO x,y coordinates — proximity is purely relational (based on relationships)
- Household must be computed dynamically each tick (relationships change)
- Neighborhood computation every 3yr (not every tick — performance)
- All cross-tier interactions must remain POSSIBLE — just less probable
- Backward compatibility: proximity_tiers_enabled=False = current behavior
- Run validation: cooperation network size should decrease slightly (more local)
  faction formation should remain similar or increase slightly
