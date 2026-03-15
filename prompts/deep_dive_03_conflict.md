# SIMSIV — PROMPT: DEEP DIVE 03 — CONFLICT MODEL
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_03_conflict.md
# Use: Send to Claude after DD01 mating and DD02 resources are complete
# Priority: PHASE B, Sprint 3

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 03 on the SIMSIV conflict engine.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\engines\conflict.py (current implementation)
  4. D:\EXPERIMENTS\SIM\models\agent.py
  5. D:\EXPERIMENTS\SIM\config.py (all conflict-related params)
  6. D:\EXPERIMENTS\SIM\STATUS.md (post-DD02 results)

The skeleton conflict engine is functional but simplistic. This deep dive replaces
it with a richer model that creates proper selection pressure against aggression,
feeds back into mating and resource outcomes, and produces scenario differentiation
on violence metrics.

================================================================================
DEEP DIVE 03: CONFLICT MODEL
================================================================================

POST-DD02 DATA POINTS (use these to inform design):
  - Baseline violence_rate = 0.057 (57 conflicts per 1000 agents per year)
  - HIGH_VIOLENCE_COST scenario (violence_death_chance=0.15) collapses pop to ~71
  - ENFORCED_MONOGAMY reduces violence by 37% (strongest institutional effect)
  - Aggression quartile analysis: high-agg agents get 18% fewer resources,
    20% fewer offspring — but this cost comes mostly from the resource engine
    (DD02 aggression penalty), NOT from conflict consequences themselves
  - Conflict is currently same-sex only (males fight males, females fight females)
  - No coalition support, no defensive alliances, no reputation-aware deterrence
  - Winner/loser effects are flat (0.05 status change) regardless of magnitude

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. CONFLICT TRIGGER MODEL
   The current trigger model sums independent probabilities. Design a richer model:
   - Should triggers be evaluated in priority order (jealousy > resource > status > random)?
   - How should trust-network density suppress conflict? (agents embedded in dense
     cooperative networks should fight less — social cost of defection is higher)
   - Should resource inequality between two specific agents trigger conflict?
     (envious attack on wealthier neighbor vs abstract resource stress)
   - How should past conflict history affect future probability?
     (grudge escalation vs war-weariness / learned helplessness)
   - Should there be a "provocation" model where being attacked increases
     future aggression temporarily? (retaliation spiral)

B. TARGET SELECTION
   Current model: same-sex only, biased by low trust, shared mates, similar status.
   - Should cross-sex conflict be possible? (domestic violence, or keep it out?)
   - Should target selection consider relative strength? (cowards pick weak targets,
     risk-tolerant agents challenge stronger ones)
   - Should agents in cooperative networks be harder to target? (ally deterrence)
   - Should there be opportunistic vs premeditated distinction?
     (low-risk: steal from the weak; high-risk: challenge a rival for status)

C. COMBAT RESOLUTION
   Current model: weighted coin flip based on aggression + status + health + risk.
   - Should combat power include resource advantage? (better-fed fighters win more)
   - Should cooperation networks provide backup? (allies join the fight)
   - Should there be a "flee" option for the target? (risk_tolerance gates fight/flee)
   - Should combat have multiple rounds or escalation? (or keep single-resolution?)
   - Should intelligence affect combat? (tactical advantage)

D. CONSEQUENCES AND COSTS
   Current model: flat health cost, flat resource transfer, flat status shift.
   - Should costs scale with combatant power differential? (stomps vs close fights)
   - Should the winner's reputation go UP in some contexts? (dominance display)
   - Should bystanders update their trust ledgers? (witnesses to violence)
   - Should there be a "wound recovery" period that reduces combat effectiveness?
   - Should repeated losing create a "subordination" effect that reduces
     future conflict probability? (dominance hierarchy formation)

E. DETERRENCE AND INSTITUTIONAL FEEDBACK
   Current: law_strength * (0.5 + punishment * 0.5) reduces probability.
   - Should deterrence be proportional to the agent's resources? (rich have more to lose)
   - Should institutional punishment be event-based? (actual fines, exile, etc.)
   - Should high law_strength create a visible suppression effect in metrics?
   - Should there be a "feud" dynamic where conflict between two agents
     spills over to their kin networks?

F. VIOLENCE AND MATING FEEDBACK LOOP
   DD01 created pair bond destabilization from violence. Strengthen this:
   - Should female mate choice explicitly penalize agents with recent conflict history?
     (it already penalizes aggression trait, but not behavioral history)
   - Should violence casualties create orphans with worse outcomes?
   - Should widow(er)s of violence victims get sympathy bonuses?

G. HIGH_VIOLENCE_COST SCENARIO FIX
   Current scenario collapses to ~71 agents (violence_death_chance=0.15,
   violence_cost_health=0.45, mortality_base=0.04).
   - Should high violence costs cause FASTER selection against aggression
     rather than population collapse?
   - Consider whether the scenario params are simply too extreme,
     or whether the engine needs structural fixes to handle high-lethality settings

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_03_conflict.md — design decisions and formulas
2. engines/conflict.py — full replacement implementation
3. config.py additions — all new conflict parameters with defaults
4. metrics/collectors.py additions — new conflict-relevant metrics
5. DEV_LOG.md entry
6. CHAIN_PROMPT.md update
7. STATUS.md update

================================================================================
NEW PARAMETERS TO CONSIDER FOR CONFIG
================================================================================

retaliation_memory_boost: float        # trust penalty translates to future conflict boost
network_deterrence_factor: float       # allies reduce being targeted
flee_threshold: float                  # risk_tolerance below this → flee instead of fight
bystander_reputation_update: bool      # witnesses update trust ledgers
winner_reputation_boost: float         # status benefit to winner (context-dependent)
subordination_decay: float             # repeated losers become less aggressive over time
conflict_resource_threshold: float     # resource gap that triggers envious attack
provocation_aggression_boost: float    # being attacked boosts aggression temporarily
combat_ally_support: bool              # allies can join (v2 prep)
violence_wound_recovery_years: int     # years before full combat effectiveness returns

================================================================================
CONSTRAINTS
================================================================================

- Do not break any other engine
- Do not change model/agent.py attributes without documenting in DEV_LOG
- Do not change the simulation loop order without explicit permission
- All new parameters must have defaults that produce sane behavior
- New behavior must produce emergent output — no hardcoded outcomes
- The PRIMARY goal is making violence a credible, calibrated selection pressure
  that produces emergent dominance hierarchies and realistic aggression evolution
