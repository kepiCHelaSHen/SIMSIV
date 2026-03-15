# SIMSIV — PROMPT: DEEP DIVE 14 — IN-GROUP IDENTITY AND SOCIAL FACTIONS
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_14_factions.md
# Use: Send to Claude after DD13 is complete
# Priority: PHASE C, Sprint 7

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 14 on the SIMSIV faction and in-group identity model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (reputation_ledger, partner_ids, offspring_ids)
  4. D:\EXPERIMENTS\SIM\engines\resources.py (cooperation networks)
  5. D:\EXPERIMENTS\SIM\engines\conflict.py (targeting, coalition defense)
  6. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

Agents currently form bilateral trust relationships but have no group identity.
Real human populations spontaneously form identifiable subgroups — factions,
clans, bands — with in-group preference and out-group competition. This emerges
without explicit design from shared history, kinship, and cooperation patterns.
This deep dive creates the substrate for emergent faction formation within a
single population. It is also the critical precursor to v2 multi-tribe dynamics.

Note: This is a WITHIN-POPULATION model. Multi-tribe (separate populations with
      territory) remains v2. This is about spontaneous factional structure within
      a single mixed population.

================================================================================
DEEP DIVE 14: IN-GROUP IDENTITY AND SOCIAL FACTIONS
================================================================================

CURRENT STATE:
  - Cooperation: trust-based bilateral sharing (DD02)
  - Coalition defense and punishment (DD11)
  - Gossip networks (DD07)
  - No group identity, no faction tags, no in-group/out-group distinction
  - Network clusters likely exist implicitly (high-trust cliques) but
    are not tracked, measured, or behaviorally active
  - Cooperation is continuous (trust is a float) not categorical (in vs out)

CORE DESIGN PHILOSOPHY:
  Factions must EMERGE — do not assign agents to factions. Instead, detect
  natural clusters in the trust network and allow agents to treat cluster
  membership as a social signal. Over time, these clusters should harden
  into stable identities through preferential interaction, resource sharing
  within, and competition with other clusters.

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. FACTION DETECTION
   - How to detect emergent clusters from the trust network?
   - Lightweight approach: an agent's "faction" is their highest-trust
     connected component — the group of agents they trust above threshold
   - Should faction membership be computed periodically? (every 5 years)
     Not every tick — too expensive and too volatile
   - Should faction membership be stored on the agent? (faction_id: int or None)
   - Should factions have a maximum size? (natural human group size ~30-50)
   - Should very small clusters (< 3 members) be considered "factionless"?

B. IN-GROUP PREFERENCE MECHANICS
   Once faction membership is assigned, in-group preference affects:
   - Resource sharing: in-group agents share with lower trust threshold
   - Conflict targeting: out-group agents are more likely to be targeted
   - Mating preference: slight in-group mating preference (endogamy)
   - Coalition defense: stronger defense of in-group members
   - Status: in-group members boost each other's reputation

   Key design principle: in-group preference should be a SOFT modifier,
   not an absolute barrier. Inter-faction interactions still occur.
   The strength of in-group preference is modulated by a config parameter.

C. FACTION FORMATION DRIVERS
   What causes factions to form spontaneously?
   - Kinship: families naturally cluster (DD02 kin trust already seeds this)
   - Shared conflict history: agents who fought together or against the same
     enemy develop stronger mutual trust
   - Resource co-dependency: agents in the same cooperation network
   - Geographic proximity (non-spatial approximation: agents born in the same
     generation in the same population form initial cohort bonds)
   - Prestige centers: high-prestige agents attract followers who then
     form cohesive groups around them

D. FACTION COMPETITION
   Once factions exist, they should compete:
   - Resource competition: faction members cooperate to outcompete other factions
     in the status distribution (faction's combined competitive weight)
   - Conflict: higher probability of inter-faction conflict than intra-faction
   - Status: faction leader's prestige/dominance affects member outcomes
   - Elite capture: the highest-status member of a faction gets institutional
     advantages for the whole faction (precursor to political leadership)

E. FACTION DYNAMICS OVER TIME
   - Factions should split when they grow too large (schism)
   - Factions should merge when two clusters form strong inter-cluster trust
   - Factions should dissolve when their members die off
   - Faction "age" should affect stability: older factions are harder to split
   - Should faction history affect institutional behavior? (old factions
     develop stronger norms and enforcement)

F. MEASUREMENT AND METRICS
   - faction_count: number of active factions per tick
   - largest_faction_size: biggest faction's member count
   - faction_gini: inequality between factions in resource accumulation
   - inter_faction_conflict_rate: fraction of conflicts that are inter-faction
   - faction_stability: average faction age (how long factions persist)
   - faction_cooperation_surplus: cooperation network size within vs between factions

G. V2 PREPARATION
   This deep dive should be explicitly designed as the foundation for v2:
   - Faction data structure should be extensible to "tribe" with territory
   - Faction competition mechanics should generalize to inter-tribe raiding
   - Faction identity should be the unit that institutions eventually govern
   - Faction leadership should be the seed for formal political authority

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_14_factions.md — design decisions and faction detection algorithm
2. models/society.py — faction detection and assignment (periodic)
3. models/agent.py — faction_id field
4. engines/resources.py — in-group preference in sharing
5. engines/conflict.py — inter-faction targeting preference
6. engines/mating.py — mild endogamy preference
7. config.py additions — faction parameters
8. metrics/collectors.py — faction metrics (faction_count, largest_faction,
   inter_faction_conflict_rate, faction_stability)
9. DEV_LOG.md entry
10. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

factions_enabled: bool = True
faction_detection_interval: int = 5        # years between faction recomputation
faction_min_trust_threshold: float = 0.65  # trust level required for same faction
faction_min_size: int = 3                  # minimum viable faction size
faction_max_size: int = 50                 # split threshold (Dunbar-inspired)
in_group_sharing_bonus: float = 0.2        # fraction increase in sharing rate for in-group
in_group_trust_threshold_reduction: float = 0.1  # lower trust needed to share with in-group
out_group_conflict_multiplier: float = 1.5  # inter-faction conflict probability boost
endogamy_preference: float = 0.1           # in-group mate value boost
faction_schism_pressure: float = 0.01     # annual schism probability above max_size
faction_merge_trust: float = 0.8           # inter-leader trust required for merge

================================================================================
CONSTRAINTS
================================================================================

- Factions must EMERGE from trust network — never assign agents to factions directly
- Faction detection must be computationally efficient — use connected component
  analysis on the trust graph, not clustering algorithms
- In-group preference must be a SOFT modifier, not an absolute barrier
- Faction mechanics must not eliminate inter-faction cooperation entirely
- This must remain a WITHIN-POPULATION model — do not implement territory,
  migration between groups, or inter-group warfare (those are v2)
- faction_detection_interval = 5 minimum — don't recompute every tick
