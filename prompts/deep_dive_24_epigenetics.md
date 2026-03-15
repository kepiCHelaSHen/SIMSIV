# SIMSIV — PROMPT: DEEP DIVE 24 — TRANSGENERATIONAL EPIGENETICS AND SOCIAL PATHOLOGY SPREAD
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_24_epigenetics.md
# Use: Send to Claude after DD23 is complete
# Priority: PHASE C, Sprint 17

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 24 on transgenerational epigenetics and social pathology
spread in SIMSIV.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (breed(), genotype fields from DD16)
  4. D:\EXPERIMENTS\SIM\engines\reproduction.py (scarcity passed to breed())
  5. D:\EXPERIMENTS\SIM\engines\pathology.py (trauma mechanics from DD17)
  6. D:\EXPERIMENTS\SIM\engines\reputation.py (gossip engine from DD07)
  7. D:\EXPERIMENTS\SIM\config.py
  8. D:\EXPERIMENTS\SIM\STATUS.md

This deep dive adds two related systems:

PART A: TRANSGENERATIONAL EPIGENETICS
  Real science: severe environmental stress in one generation can increase
  heritable variation in the next — documented in Dutch Hunger Winter (1944-45),
  where children of starving mothers showed elevated metabolic disorders and
  stress responses. The mechanism: stress signals modify gene expression patterns
  that partially persist across generations.

PART B: SOCIAL PATHOLOGY SPREAD
  Extension of DD17 pathology: trauma doesn't just accumulate individually —
  it spreads socially through intimate networks. High-trauma agents transmit
  stress responses to people they're close to. This creates emergent "trauma
  epidemics" in violent or scarcity-stressed bands that can trigger institutional
  responses and faction dynamics.

================================================================================
PART A: TRANSGENERATIONAL EPIGENETICS
================================================================================

DESIGN:

  When an agent experiences severe environmental stress (scarcity, epidemic,
  high violence) during their reproductive years, their offspring inherit a
  slightly elevated mutation rate for 1-2 generations. This models:
  - Faster adaptation under pressure (evolutionary advantage)
  - But also: elevated birth defect risk, more behavioral variance
  - The stressed lineage is more variable — some offspring much better,
    some much worse than average (bet-hedging strategy)

IMPLEMENTATION:

A. EPIGENETIC FLAG ON AGENT
   New non-heritable field:
   epigenetic_stress_load: float = 0.0  # accumulated transgenerational stress
   epigenetic_generation_decay: int = 0  # generations since stress event

   Set when:
   - Agent experienced scarcity_level > 0.5 during ages 15-45 (reproductive window)
   - Agent survived an epidemic event
   - Agent's trauma_score (DD17) exceeded 0.7 during reproductive years
   - Parent had epigenetic_stress_load > 0 (decays each generation)

   epigenetic_stress_load accumulation:
   - Scarcity event: +0.3
   - Epidemic survival: +0.2
   - Trauma threshold crossed: +0.25
   - Inherited from parent: parent_load * 0.5 (halves each generation)
   - Maximum: 1.0
   - Decay: -0.1 per year in non-stressed conditions

B. EFFECT ON OFFSPRING IN BREED()
   When breeding, if either parent has epigenetic_stress_load > 0.2:
   - Mutation sigma multiplied by (1 + parent_load * epigenetic_sigma_boost)
   - Default boost: 0.3 → 30% increase in mutation at full stress load
   - mental_health_baseline (DD15) moderates: high MHB reduces the boost
     effective_boost = epigenetic_sigma_boost * (1 - parent_mhb * 0.5)
   - This creates a DISTRIBUTION of outcomes in stressed lineages:
     some offspring are notably better adapted, some notably worse

C. BET-HEDGING EMERGENCE
   The mathematical result: stressed lineages have HIGHER VARIANCE in offspring
   trait values. In stable environments this is disadvantageous (more bad outcomes).
   In unstable environments this is advantageous (more lucky matches).
   This should produce an emergent pattern: stressed bands recover faster
   after crises because their high-variance offspring include some excellent
   adapters. Measure this in post-scarcity recovery rate.

D. METRICS
   - avg_epigenetic_load: mean epigenetic_stress_load across living agents
   - epigenetic_lineages: count of agents with load > 0.2
   - trait_variance_stressed_vs_unstressed: compare offspring trait std
     between high-load and low-load parents

================================================================================
PART B: SOCIAL PATHOLOGY SPREAD
================================================================================

DESIGN:

  Trauma (from DD17) is not just individually accumulated — it spreads through
  intimate social contact. This models:
  - Secondary traumatization (witnessing others' suffering)
  - Chronic stress contagion in tight-knit groups
  - The "trauma epidemic" pattern seen in war-affected communities

IMPLEMENTATION:

A. TRAUMA CONTAGION IN REPUTATION ENGINE
   In the gossip phase of engines/reputation.py, add trauma contagion:

   For each agent with trauma_score > 0.6 (high trauma):
   - Get their trusted contacts (reputation_ledger trust > 0.6, household tier first)
   - For each contact: trauma_spread_chance = trauma_contagion_rate
                                              * agent.trauma_score
                                              * (1 - contact.mental_health_baseline)
   - If spread triggers: contact.trauma_score += trauma_spread_amount
     (default: +0.02 per tick — small but accumulates)

   Modulation:
   - empathy_capacity (DD15) INCREASES susceptibility (you feel others' pain more)
   - impulse_control (DD15) DECREASES susceptibility (emotional regulation)
   - Household tier contacts: 2x susceptibility (close proximity amplifies)
   - Faction membership: slight protection (group support buffer)

B. FACTION SUPPORT BUFFER
   Agents in strong factions (faction cohesion above threshold) have reduced
   trauma accumulation AND faster trauma recovery:
   - In faction with avg_trust > 0.65: trauma_decay_rate boosted +0.02/yr
   - Faction leader (peace chief from DD20) reduces faction member trauma
     by a small amount per year (pastoral/supportive role)
   - This creates emergent finding: strong factions are trauma buffers

C. INSTITUTIONAL RESPONSE TRIGGER
   When band-wide avg_trauma_score exceeds a threshold for 3+ consecutive years:
   - Institutions engine generates an "institutional response" event
   - law_strength receives an upward drift push (collective response to crisis)
   - This is a new emergent formation trigger in DD05's institutions engine
   - Models: communities develop norms against violence after trauma epidemics

D. TRAUMA EPIDEMIC EVENTS
   If more than 30% of the band has trauma_score > 0.6 simultaneously:
   - Log "trauma_epidemic" event
   - Faction schism probability increases (stressed groups fragment)
   - Migration pressure increases (stressed agents more likely to emigrate)
   - Mating success drops (high-trauma agents are less attractive — health signal)

E. METRICS
   - trauma_contagion_events: count of trauma spread events per tick
   - band_trauma_index: mean trauma_score across living adults
   - faction_trauma_differential: trauma difference between highest and
     lowest faction (measures faction support buffer effectiveness)
   - trauma_epidemic_active: bool flag for dashboard

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_24_epigenetics.md — design decisions for both parts
2. models/agent.py — epigenetic_stress_load, epigenetic_generation_decay fields
3. engines/reproduction.py — epigenetic sigma boost in breed() call
4. engines/pathology.py — epigenetic load accumulation from stress events
5. engines/reputation.py — trauma contagion in gossip phase
6. engines/institutions.py — trauma epidemic institutional response trigger
7. config.py additions — epigenetic and contagion parameters
8. metrics/collectors.py — 7 new metrics (4 epigenetic + 3 trauma epidemic)
9. DEV_LOG.md entry
10. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

epigenetics_enabled: bool = True
epigenetic_sigma_boost: float = 0.3          # max mutation rate increase from stress load
epigenetic_scarcity_load: float = 0.3        # load added from scarcity event
epigenetic_epidemic_load: float = 0.2        # load added from epidemic survival
epigenetic_trauma_load: float = 0.25         # load added from trauma threshold crossing
epigenetic_inheritance_fraction: float = 0.5 # fraction of load passed to offspring
trauma_contagion_enabled: bool = True
trauma_contagion_rate: float = 0.1           # base annual spread probability
trauma_spread_amount: float = 0.02           # trauma points transferred per event
trauma_epidemic_threshold: float = 0.3       # fraction of band in crisis to trigger epidemic
faction_trauma_buffer: float = 0.02          # annual trauma decay boost in strong factions

================================================================================
CONSTRAINTS
================================================================================

- Epigenetic effect must be MODERATE — not large enough to override genetic selection
- Trauma contagion must be SLOW — not an instant band-wide collapse
- Both systems must have enabled flags for backward compatibility
- Run validation: in RESOURCE_SCARCITY, expect elevated epigenetic loads
  and some trauma spread; band should still survive and recover
- Transgenerational effect must decay — third generation should be nearly normal
