# SIMSIV — PROMPT: DEEP DIVE 25 — BELIEF AND IDEOLOGY SYSTEM
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_25_beliefs.md
# Use: Send to Claude after DD24 is complete
# Priority: PHASE C, Sprint 18

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 25 on the SIMSIV belief and ideology system.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (conformity_bias, novelty_seeking from DD15)
  4. D:\EXPERIMENTS\SIM\engines\institutions.py (norm enforcement, institutional drift)
  5. D:\EXPERIMENTS\SIM\engines\reputation.py (gossip engine)
  6. D:\EXPERIMENTS\SIM\config.py
  7. D:\EXPERIMENTS\SIM\STATUS.md

Currently behavioral variation emerges from heritable traits and institutions.
But there is a missing layer between individual traits and institutional norms:
cultural beliefs. Beliefs are the cognitive representations agents hold about
how society should be organized — distinct from their behavioral tendencies
(traits) and from the enforced rules (institutions). A cooperative agent might
believe in egalitarianism. An aggressive agent might believe in hierarchy.
These beliefs spread through social networks, conflict with each other, and
drive institutional change in ways that traits alone cannot.

This is the "meme" layer of the simulation — cultural information that evolves
via social transmission, selection, and mutation, independently of genetic
evolution.

================================================================================
DEEP DIVE 25: BELIEF AND IDEOLOGY SYSTEM
================================================================================

FIVE BELIEF DIMENSIONS:

  Each agent holds values on 5 belief dimensions, each a float [-1.0 to +1.0]:

  HIERARCHY_BELIEF: float [-1.0 to +1.0]
    -1.0 = strong egalitarianism (all should be equal)
    +1.0 = strong hierarchy belief (natural ranking is correct and good)
    Initialized from: status_drive * 0.6 + dominance_score * 0.4 (roughly)
    Influences: acceptance of elite privilege, taxation resistance

  COOPERATION_NORM: float [-1.0 to +1.0]
    -1.0 = defection is acceptable / every agent for themselves
    +1.0 = strong prosocial norm (cooperation is sacred obligation)
    Initialized from: cooperation_propensity * 0.8 + reputation * 0.2
    Influences: how strongly agent enforces cooperation on others

  VIOLENCE_ACCEPTABILITY: float [-1.0 to +1.0]
    -1.0 = violence is never acceptable (pacifist)
    +1.0 = violence is an honorable resolution to disputes
    Initialized from: aggression_propensity * 0.7 + dominance_score * 0.3
    Influences: conflict initiation tolerance, punishment of violence

  TRADITION_ADHERENCE: float [-1.0 to +1.0]
    -1.0 = strong change orientation (innovator)
    +1.0 = strong tradition orientation (conservatism)
    Initialized from: conformity_bias * 0.8 - novelty_seeking * 0.4
    Influences: institutional change resistance, norm adoption speed

  KINSHIP_OBLIGATION: float [-1.0 to +1.0]
    -1.0 = universal (help strangers equally with kin)
    +1.0 = strong in-group only (kin first, strangers last)
    Initialized from: jealousy_sensitivity * 0.3 + faction_loyalty_proxy * 0.7
    Influences: resource sharing radius, faction loyalty, migrant acceptance

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. BELIEF INITIALIZATION
   At agent creation (maturation age 15 in DD16 context):
   - Base values from trait expressions (formulas above)
   - Parent modeling: beliefs influenced by average of both parents' beliefs
     (cultural transmission independent of genetic inheritance)
   - conformity_bias (DD15) determines how strongly parent beliefs override
     individual trait-derived initialization
   - novelty_seeking (DD15) adds noise to belief initialization
     (innovators start with more divergent beliefs)
   Formula:
   belief = conformity_bias * parent_avg_belief
           + (1 - conformity_bias) * trait_derived_belief
           + novelty_seeking * N(0, 0.15)

B. BELIEF EVOLUTION (CULTURAL TRANSMISSION)
   Run belief updates in a new phase of the reputation engine (every 3 ticks):

   Social influence:
   - Each agent is influenced by the beliefs of agents in their neighborhood tier
   - Influence weight: trust_of(other) * other.prestige_score (prestigious agents
     are more culturally influential — prestige bias transmission)
   - Update: belief += conformity_bias * (influential_neighbor_avg - belief) * 0.05
   - novelty_seeking opposes conformity (innovators resist social pressure)

   Experience-based belief update:
   - Agent wins conflict: violence_acceptability += 0.03 (violence worked for me)
   - Agent loses conflict and survives: violence_acceptability -= 0.05
   - Resource-sharing event: cooperation_norm += 0.02
   - Resource theft (conflict loot): hierarchy_belief += 0.02, cooperation_norm -= 0.02
   - Institutional punishment received: violence_acceptability -= 0.04
   - Witnessing leader's generosity (DD20 peace chief display): cooperation_norm += 0.02

   Belief mutation (cultural innovation):
   - novelty_seeking gates random belief shifts
   - Small annual noise: N(0, novelty_seeking * 0.03) per dimension per agent
   - This allows new belief variants to emerge even without external input

C. BELIEF EFFECTS ON ENGINES
   Beliefs modify behavior as soft multipliers on top of trait effects:

   Institutions engine:
   - High hierarchy_belief population: elite_privilege_multiplier drifts upward
   - High cooperation_norm population: law_strength drift rate accelerates
   - High violence_acceptability: violence_punishment_strength drifts downward
   - High tradition_adherence: institutional_inertia increases (harder to change)
   These are ADDITIONAL inputs to the institutional drift formula from DD05.

   Conflict engine:
   - High violence_acceptability agent: conflict initiation probability +10%
   - Low violence_acceptability agent: conflict initiation probability -15%
   - Third-party punishment (DD11): more likely when punisher has low violence_acceptability

   Mating engine:
   - High kinship_obligation: endogamy preference stronger (marry within faction)
   - Low kinship_obligation: band-wide mate search (outbreeding)

   Resources engine:
   - High cooperation_norm: sharing_rate boosted +10%
   - Low kinship_obligation: cooperation sharing extends beyond neighborhood tier
   - High hierarchy_belief: agents more accepting of taxation going to elites

D. BELIEF CONFLICT AND IDEOLOGY FORMATION
   When two agents with very different beliefs on a dimension interact:
   - abs(belief_A - belief_B) > 0.6 → "ideological tension"
   - Tension increases distrust: remember(other_id, -0.05 * tension)
   - Tension can trigger conflict independently of trait-driven aggression
     (ideological conflict — fights over how things should be)
   - Over time, factions should sort by belief alignment as well as trust/kin

   Dominant band ideology:
   - Computed as mean belief vector across all living adults
   - If ANY dimension reaches abs(mean) > 0.5, it becomes a "dominant ideology"
   - Dominant ideology is part of the band fingerprint (exported to clan level)
   - Emergent ideological types:
     * Egalitarian warrior band: low hierarchy, high violence_acceptability
     * Cooperative collective: high cooperation_norm, low hierarchy
     * Hierarchical tradition: high hierarchy, high tradition, high kinship
     * Innovative expansionist: low tradition, low kinship_obligation

E. BELIEF AND INSTITUTIONAL REVOLUTION
   When dominant ideology shifts significantly (>0.3 on any dimension in <10yr):
   - Log "belief_revolution" event
   - Triggers rapid institutional drift in the direction of new beliefs
   - Faction schism possible: agents who held old beliefs may leave or form counter-faction
   - This is the model's version of cultural revolutions, religious conversions,
     or ideological shifts — emergent, not scripted

F. METRICS
   - avg_hierarchy_belief, avg_cooperation_norm, avg_violence_acceptability,
     avg_tradition_adherence, avg_kinship_obligation (5 mean belief metrics)
   - belief_polarization: std of each belief dimension (how divided is the band)
   - dominant_ideology: categorical label for dashboard
   - belief_revolution_events: count per run
   - belief_fitness_correlation: correlation between cooperation_norm and reproductive success
     (does believing in cooperation actually help you?)

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_25_beliefs.md — design decisions and transmission formulas
2. models/agent.py — 5 belief fields (non-heritable floats [-1, 1])
3. engines/reputation.py — belief update phase (every 3 ticks)
4. engines/institutions.py — belief aggregate effects on institutional drift
5. engines/conflict.py — violence_acceptability effects
6. engines/resources.py — cooperation_norm and kinship_obligation effects
7. engines/mating.py — kinship_obligation endogamy effect
8. config.py additions — belief system parameters
9. metrics/collectors.py — 10 new belief metrics
10. DEV_LOG.md entry
11. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

beliefs_enabled: bool = True
belief_social_influence_rate: float = 0.05   # strength of conformity pressure per tick
belief_experience_update_rate: float = 0.03  # belief change from direct experience
belief_mutation_rate: float = 0.03           # novelty_seeking-scaled random drift
belief_ideological_tension_threshold: float = 0.6  # abs diff triggering tension
belief_revolution_threshold: float = 0.3     # shift magnitude triggering revolution event
belief_institutional_influence: float = 0.3  # weight of belief aggregate in inst drift
prestige_transmission_weight: float = 0.6    # how much more prestigious agents influence beliefs

================================================================================
CONSTRAINTS
================================================================================

- Beliefs are NON-HERITABLE — children initialize from parents via cultural
  transmission, not via breed(). Genotype does not include beliefs.
- Belief effects must be SOFT MULTIPLIERS on existing behavior — not overrides
- Run in reputation engine every 3 ticks (not every tick — performance)
- Backward compatibility: beliefs_enabled=False = current behavior
- Beliefs must diverge between scenarios: STRONG_STATE should produce
  more egalitarian and cooperation-norm beliefs than FREE_COMPETITION
- Run validation: in ELITE_POLYGYNY, expect hierarchy_belief to rise
  and cooperation_norm to diverge across factions
