# SIMSIV — PROMPT: DEEP DIVE 08 — PRESTIGE VS DOMINANCE
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_08_prestige.md
# Use: Send to Claude after DD01-DD07 are complete
# Priority: PHASE C, Sprint 1

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 08 on the SIMSIV status model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (current_status field)
  4. D:\EXPERIMENTS\SIM\engines\resources.py (status distribution)
  5. D:\EXPERIMENTS\SIM\engines\conflict.py (status in combat)
  6. D:\EXPERIMENTS\SIM\engines\mating.py (status in mate_value)
  7. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The current model has a single current_status float [0.0-1.0]. Anthropological
research is unambiguous: prestige (earned through skill, generosity, reputation)
and dominance (enforced through intimidation and force) are psychologically and
socially distinct systems with different evolutionary origins, different selection
pressures, and different social consequences. This deep dive splits the single
status track into two and wires them through all engines.

================================================================================
DEEP DIVE 08: PRESTIGE VS DOMINANCE
================================================================================

CURRENT STATE:
  - current_status: single float, blends all status sources
  - Status earned via: resource competition (intelligence + status_drive),
    conflict victories (+0.05), cooperation contribution
  - Status used in: mate_value, conflict power, resource competitive weight
  - No distinction between a respected elder and a feared bully —
    both have "high status" in the model

CORE DESIGN DECISION:
  Split current_status into:
  - prestige_score: float [0.0-1.0] — earned through cooperation, intelligence,
    resource generosity, skill display, successful parenting
  - dominance_score: float [0.0-1.0] — earned through conflict victories,
    aggression display, intimidation, resource hoarding

  These two tracks should:
  - Have DIFFERENT effects on mate_value (females weight prestige more than dominance)
  - Have DIFFERENT effects on conflict (dominance matters more in direct combat)
  - Have DIFFERENT effects on cooperation (prestige attracts cooperation, dominance repels it)
  - Have DIFFERENT decay rates (prestige is slow to build, slow to decay;
    dominance is faster to gain, faster to lose)
  - Be partially substitutable in some contexts (overall status = f(prestige, dominance))

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. PRESTIGE ACQUISITION
   - What behaviors earn prestige?
     * Cooperation network sharing (most important)
     * Successful child-rearing (large surviving offspring count)
     * Intelligence-driven resource efficiency
     * Reputation ledger: being trusted by many agents
     * Long partnership stability
   - Should prestige be observable? (agents can see others' prestige and update
     their trust accordingly — prestige is a public signal)
   - Should prestige have a "display" component? (generous acts witnessed by
     bystanders give bigger prestige gains than private generosity)

B. DOMINANCE ACQUISITION
   - What behaviors earn dominance?
     * Conflict victories (primary source)
     * Successful resource theft
     * Mating contest victories
     * Intimidation without fighting (aggression display)
   - Should dominance be visible as a deterrent?
     (high-dominance agents are targeted less — fear-based deterrence)
   - Should dominance decline faster when challenged and beaten?
     (unstable at the top — loss is more costly than gain)

C. INTERACTION EFFECTS
   - Can an agent have both high prestige AND high dominance?
     (warrior-chief archetype — historically exists but is rare)
   - Should there be a soft tradeoff? (high aggression reduces prestige gain rate)
   - Should dominance without prestige create social instability?
     (feared but not respected → coalition forms against you)
   - How do the two tracks combine for overall social standing?

D. ENGINE REWIRING
   Every engine that currently uses current_status needs to be updated:

   Resources engine:
   - Competitive weight: prestige matters more than dominance for resource acquisition
   - Status pool distribution: prestige-weighted, not dominance-weighted
   - Cooperation sharing: prestige agents attract more allies

   Conflict engine:
   - Combat power: dominance + aggression + health (prestige irrelevant in direct combat)
   - Target selection: high-dominance agents are feared (targeted less)
   - Victory: dominance gain for winner, dominance loss for loser
   - Reputation: prestige loss for aggressor (socially costly even if you win)

   Mating engine:
   - mate_value: prestige weighted more than dominance for female choice
   - Female choice aggression penalty already in place — link it to dominance explicitly
   - High-dominance males may intimidate potential rivals from competing

   Institutions engine:
   - Law strength boost when prestige agents dominate the population
   - Law strength erosion when dominance agents dominate

E. METRICS
   - prestige_gini: inequality in prestige distribution
   - dominance_gini: inequality in dominance distribution
   - prestige_dominance_correlation: are they converging or diverging over time?
   - population_type: dominant vs prestige-led society (composite metric)

F. MIGRATION COMPATIBILITY
   Current migrant injection uses uniform [0.2-0.8] for all traits.
   - Injected migrants should have prestige_score and dominance_score initialized
   - Should migrants start with lower prestige (strangers aren't trusted yet)
     but neutral dominance?

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_08_prestige.md — design decisions and math
2. models/agent.py — add prestige_score, dominance_score; keep current_status
   as a computed property for backward compatibility
3. engines/resources.py — rewire status distribution
4. engines/conflict.py — rewire combat power and reputation effects
5. engines/mating.py — rewire mate_value and female choice
6. engines/institutions.py — prestige/dominance population composition effects
7. config.py additions — new prestige/dominance parameters
8. metrics/collectors.py — new prestige/dominance metrics
9. DEV_LOG.md entry
10. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

prestige_weight_in_mate_value: float = 0.6    # fraction of status component from prestige
dominance_weight_in_combat: float = 0.7       # fraction of status in combat from dominance
prestige_decay_rate: float = 0.01             # annual prestige decay toward 0
dominance_decay_rate: float = 0.03            # annual dominance decay (faster)
prestige_display_multiplier: float = 1.5      # witnessed generosity → bigger prestige gain
dominance_deterrence_factor: float = 0.3      # high dominance → less likely targeted
prestige_cooperation_attraction: float = 0.2  # prestige bonus to cooperation network size

================================================================================
CONSTRAINTS
================================================================================

- current_status must remain as a computed property for full backward compatibility
  (current_status = prestige_score * w1 + dominance_score * w2)
- Do not change agent.py HERITABLE_TRAITS list — prestige and dominance are
  non-heritable earned stats, not genetic traits
- All engines must be updated consistently — partial rewiring will create
  contradictory behavior
- The two-track system must produce EMERGENT societal types, not hardwired ones
