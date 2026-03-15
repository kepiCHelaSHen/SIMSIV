# SIMSIV — PROMPT: DEEP DIVE 10 — SEASONAL RESOURCE CYCLES
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_10_seasons.md
# Use: Send to Claude after DD09 is complete
# Priority: PHASE C, Sprint 3

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 10 on the SIMSIV seasonal resource model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\environment.py (current resource model)
  4. D:\EXPERIMENTS\SIM\engines\resources.py
  5. D:\EXPERIMENTS\SIM\config.py
  6. D:\EXPERIMENTS\SIM\STATUS.md (latest results)

The current resource model varies randomly year to year (Gaussian noise around
abundance_multiplier). In reality, pre-industrial resource availability followed
predictable seasonal cycles — abundance in summer/harvest, scarcity in late
winter. This predictability fundamentally changes human social behavior: agents
can anticipate scarcity, store resources, time reproduction, and form seasonal
alliances in ways that random variation cannot produce. This deep dive adds a
seasonal cycle layer to the resource engine.

================================================================================
DEEP DIVE 10: SEASONAL RESOURCE CYCLES
================================================================================

CURRENT STATE:
  - Annual tick (1 year per step) — seasons not currently modeled
  - resource_abundance: flat multiplier with Gaussian noise (resource_volatility)
  - scarcity events: random shocks, more likely when overcrowded
  - No seasonal variation, no predictable cycles, no behavioral anticipation

NOTE ON TIME SCALE:
  The simulation uses annual ticks, not monthly. Seasons must be approximated
  as within-year phases that produce annual resource distributions, NOT as
  sub-annual ticks (which would require a major architecture change).
  The solution: model the EFFECT of seasons on annual resource outcomes,
  not the seasons themselves.

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. SEASONAL EFFECT MODEL
   Since ticks are annual, seasons affect:
   - Annual resource yield (good harvest years vs poor harvest years based on
     a configurable seasonal cycle pattern — not random, but cyclical)
   - Birth timing (births in "summer equivalent" have higher survival —
     model as survival bonus for births in high-resource years)
   - Conflict timing (more conflicts in lean years — resource stress amplifies
     baseline conflict probability in low-resource ticks)
   - Storage and smoothing (agents can buffer resources across years —
     currently all resources are consumed each tick)

B. RESOURCE STORAGE
   The most impactful addition. Currently agents retain 50% of resources each
   year (decay rate = 0.5). This implicit "storage" is unrealistic — real
   storage is intentional, costly, and limited.
   - Should there be an explicit storage cap per agent?
   - Should storage require investment? (building grain stores reduces current
     resources but protects future resources)
   - Should intelligence_proxy affect storage efficiency?
     (smarter agents preserve more across lean periods)
   - Should storage create new conflict targets?
     (raiding stored resources = high-value conflict trigger)

C. PREDICTABLE CYCLE EFFECTS
   Agents in a world with predictable cycles should behave differently:
   - Should bonded agents time reproduction to high-resource years?
     (conception_chance boosted in abundance years)
   - Should conflict spike in late-abundance / early-scarcity transitions?
     (agents compete to stock up before winter)
   - Should cooperation networks activate specifically during lean periods?
     (seasonal mutual aid — share during scarcity, repay during abundance)

D. MULTI-YEAR CYCLES
   Beyond annual seasons, consider:
   - 3-5 year cycles (drought cycles, locust cycles)
   - These would amplify the scarcity shock system already in place
   - Should multi-year cycles be configurable? (cycle_length: int)
   - Should agents "remember" past cycles and anticipate future ones?
     (intelligence_proxy mediates anticipatory behavior)

E. ENVIRONMENTAL MEMORY
   Currently environment has no state beyond current scarcity.
   - Should the environment track cumulative resource depletion?
     (overuse reduces future carrying capacity — tragedy of the commons)
   - Should vegetation/resource recovery be modeled? (fallow periods)
   - Should agent density affect long-term resource availability?

F. BEHAVIORAL ADAPTATION
   The most interesting emergent potential:
   - Storage creates wealth inequality (smart savers vs poor spenders)
   - Seasonal cooperation creates reciprocal obligation networks
   - Anticipatory reproduction shifts birth timing
   - Conflict peaks before lean periods (pre-emptive resource accumulation)
   All of these should EMERGE from the rules, not be hardcoded.

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_10_seasons.md — design decisions
2. models/environment.py — seasonal cycle state and resource multiplier
3. engines/resources.py — storage mechanics, seasonal cooperation
4. engines/reproduction.py — birth timing sensitivity to resource cycle
5. engines/conflict.py — seasonal conflict probability modulation
6. models/agent.py — storage capacity field if needed
7. config.py additions — seasonal parameters
8. metrics/collectors.py — seasonal metrics (cycle_phase, storage_gini,
   seasonal_conflict_spike)
9. DEV_LOG.md entry
10. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO ADD TO CONFIG
================================================================================

seasonal_cycle_enabled: bool = True        # enable predictable resource cycles
seasonal_amplitude: float = 0.3           # peak-to-trough resource variation
seasonal_cycle_length: int = 1            # years per full cycle (1=annual, 3=triennial)
resource_storage_cap: float = 20.0        # max resources an agent can store
storage_decay_rate: float = 0.3           # fraction of stored resources lost per year
storage_intelligence_bonus: float = 0.2   # intelligence reduces storage decay
seasonal_cooperation_boost: float = 0.3   # cooperation sharing rate multiplier in lean years
seasonal_conflict_boost: float = 0.2      # conflict probability boost in transition years
birth_timing_sensitivity: float = 0.2     # how much resource cycle affects conception chance
carrying_capacity_depletion_rate: float = 0.0  # annual CC reduction from overuse

================================================================================
CONSTRAINTS
================================================================================

- Annual tick architecture must not change — seasons affect annual outcomes,
  not sub-annual mechanics
- Storage must not create runaway wealth accumulation without bounds
- Seasonal effects must be SUBTLE enough to observe only over many years
  but REAL enough to show up in parameter sweeps
- Backward compatibility: seasonal_cycle_enabled=False must reproduce
  current behavior exactly
