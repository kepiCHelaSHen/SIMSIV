# SIMSIV — PROMPT: DEEP DIVE 17 — MEDICAL HISTORY AND PATHOLOGY
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_17_medical.md
# Use: Send to Claude after DD16 is complete
# Priority: PHASE C, Sprint 10

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 17 on the SIMSIV medical history and pathology model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py
  4. D:\EXPERIMENTS\SIM\engines\mortality.py
  5. D:\EXPERIMENTS\SIM\engines\reproduction.py
  6. D:\EXPERIMENTS\SIM\models\environment.py (epidemic model from DD09)
  7. D:\EXPERIMENTS\SIM\config.py
  8. D:\EXPERIMENTS\SIM\STATUS.md

Current mortality model: background rate, age-based death, violence, childbirth,
epidemic events (DD09), childhood mortality (DD06). This is a population-level
model with no individual medical history. Real humans have heritable conditions
that run in families, accumulate damage over lifetimes, and create distinctly
different life trajectories for different lineages. This deep dive adds individual
medical histories that are tracked, heritable, and behaviorally consequential.

================================================================================
DEEP DIVE 17: MEDICAL HISTORY AND PATHOLOGY
================================================================================

CORE CONCEPT:
  Each agent accumulates a medical history over their lifetime.
  Some conditions are heritable (run in families).
  Some are acquired (result of lifestyle, trauma, environment).
  Conditions affect behavior, reproduction, survival, and mate choice.
  Lineages develop recognizable health profiles over generations.

SCIENTIFIC GROUNDING:
  Pre-industrial disease burden was dominated by:
  - Infectious disease (partially covered by DD09 epidemics)
  - Nutritional deficiencies (partially covered by resource system)
  - Heritable conditions: cardiovascular disease (h²~0.50), mental illness
    (h²~0.40-0.80), autoimmune conditions (h²~0.30-0.60), metabolic disorders
  - Trauma accumulation: injuries, chronic pain from repeated conflict
  - Reproductive costs: maternal depletion from multiple pregnancies

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. HERITABLE CONDITIONS MODEL

  Implement as a probability-based system, not binary flags.
  Each agent has a condition_risk: dict[str, float] — probability of developing
  each condition over their lifetime, modified by genetics and environment.

  Heritable conditions to model:

  cardiovascular_risk: float [0.0-1.0]
    Heritability: ~0.50
    Effect: accelerated health decay after age 40, reduced combat stamina
    Trigger: high stress (resource deprivation) activates earlier
    Lineage signal: families with high aggression + status_drive develop this more

  mental_illness_risk: float [0.0-1.0]
    Heritability: ~0.60
    Effect: erratic behavioral output — high mental_illness active agents
    occasionally make suboptimal decisions (random cooperation/aggression spikes)
    Trigger: childhood trauma, chronic resource stress
    Distinguishes from mental_health_baseline (DD15) which is resilience, not illness
    Lineage signal: observable family clusters of instability

  autoimmune_risk: float [0.0-1.0]
    Heritability: ~0.40
    Effect: increased epidemic vulnerability despite average disease_resistance
    Counter-intuitive: immune system overactivity
    Trigger: stress events activate autoimmune episodes

  metabolic_risk: float [0.0-1.0]
    Heritability: ~0.45
    Effect: reduced resource acquisition efficiency when active
    Trigger: abundance conditions paradoxically activate (feast-famine cycle mismatch)
    Interesting: high-resource environments activate this more

  degenerative_risk: float [0.0-1.0]
    Heritability: ~0.35
    Effect: accelerated health decay after age 50, reduced mobility (flee threshold)
    Trigger: cumulative trauma (multiple conflict injuries)

B. CONDITION ACTIVATION MODEL
  Conditions have risk scores (heritable) but are not always active.
  Activation probability each year = base_risk * trigger_multipliers

  Trigger multipliers:
  - Chronic resource stress: * 2.0 (sustained deprivation)
  - Childhood trauma (DD16): * 1.5 permanent modifier
  - Age past 40: * (1 + years_past_40 * 0.05)
  - Recent conflict injury: * 1.3 (2 years post-injury)
  - Scarcity event: * 1.4

  Once activated, conditions persist for configurable duration and then
  may remit (if resources are adequate) or become chronic (if sustained stress).

C. ACCUMULATED TRAUMA MODEL
  Separate from heritable conditions — purely acquired.
  trauma_score: float [0.0-1.0] — accumulates from:
  - Each conflict loss: +0.05
  - Each significant health loss event: +0.03
  - Witnessing partner/offspring death: +0.04
  - Chronic resource deprivation: +0.02/year below threshold

  Trauma effects:
  - High trauma: mental_illness activation more likely
  - High trauma: trust formation slowed (reduced memory update magnitude)
  - High trauma: jealousy_sensitivity boosted
  - Very high trauma (>0.8): behavioral instability (random decision spikes)

  Trauma recovery:
  - Slow decay when resources adequate and social connected: -0.01/year
  - Kin support accelerates recovery (DD06 kin network effect)

D. MEDICAL HISTORY TRACKING
  Each agent should have a medical_history: list[dict] — a log of significant
  health events in their life:
  - {year: int, event: str, severity: float}
  Events to log: condition_activated, condition_remitted, injury, chronic_onset,
  trauma_threshold_crossed

  This creates the individual biography component — you can look at any agent
  and see their complete medical narrative.

  Keep history bounded: max 50 entries per agent (discard oldest when full).

E. MATE CHOICE AND MEDICAL HISTORY
  Female choice should incorporate health signals:
  - Current health is already in mate_value
  - Add: visible_health_signals — agents with active conditions have reduced
    attractiveness_base expression (not the heritable value, but the signal)
  - High emotional_intelligence (DD15) enables better detection of hidden conditions
  - This creates selection pressure against heritable conditions

F. HERITABILITY OF CONDITIONS
  When breeding (breed() in agent.py):
  - Each condition risk is heritable: child_risk = parent_midpoint + mutation
  - Heritability varies by condition (see values above)
  - Child inherits risk, not activated state — parents with chronic conditions
    pass elevated risk to children, not the condition itself

G. LINEAGE HEALTH PROFILES
  Over generations, lineages should develop recognizable health profiles.
  A lineage with high cardiovascular_risk + high status_drive + high aggression
  will show: short male lifespans, high early reproductive success, then early death.
  A lineage with high mental_illness_risk + childhood trauma will show:
  erratic behavior patterns, disrupted pair bonds, lower cooperation network size.

  These lineage patterns should be VISIBLE in the dashboard — a dynasty tracker
  showing health profile evolution across generations.

================================================================================
IMPLEMENTATION NOTES
================================================================================

AGENT FIELDS TO ADD:
  # Heritable condition risks (new heritable traits — add to HERITABLE_TRAITS)
  cardiovascular_risk: float = 0.2
  mental_illness_risk: float = 0.2
  autoimmune_risk: float = 0.2
  metabolic_risk: float = 0.2
  degenerative_risk: float = 0.2

  # Active condition states (non-heritable)
  active_conditions: set[str] = field(default_factory=set)
  trauma_score: float = 0.0
  medical_history: list[dict] = field(default_factory=list)

NOTE: condition risks ARE heritable (add to HERITABLE_TRAITS with low defaults
of 0.2 so baseline population is mostly healthy). Active conditions are NOT
heritable — children inherit risk, not state.

NEW ENGINE: engines/pathology.py
  A new lightweight engine that runs between mortality and institutions:
  - Checks activation conditions for each agent
  - Applies condition effects to health, behavior parameters
  - Logs medical history entries
  - Manages trauma accumulation and recovery

TICK ORDER UPDATE:
  Add pathology engine between mortality (step 6) and institutions (step 7).

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_17_medical.md — design decisions and condition formulas
2. models/agent.py — condition risk traits, active_conditions, trauma_score,
   medical_history fields
3. engines/pathology.py — NEW engine: condition activation, trauma tracking
4. engines/mortality.py — condition effects on health decay and death probability
5. engines/mating.py — health signal effects on attractiveness expression
6. simulation.py — add pathology engine to tick loop
7. config.py additions — condition parameters
8. metrics/collectors.py — medical metrics (active_conditions_count,
   avg_trauma_score, condition_prevalence by type)
9. DEV_LOG.md entry
10. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

pathology_enabled: bool = True
condition_activation_base: float = 0.02      # annual base activation probability
condition_remission_rate: float = 0.15       # annual remission probability if resources adequate
trauma_decay_rate: float = 0.01              # annual trauma recovery rate
trauma_conflict_increment: float = 0.05      # trauma added per conflict loss
trauma_grief_increment: float = 0.04         # trauma added per kin death
cardiovascular_health_decay_boost: float = 0.005  # extra health decay when active
mental_illness_decision_noise: float = 0.15  # random trait spike magnitude when active
autoimmune_epidemic_vulnerability: float = 2.0    # multiplier during epidemic
metabolic_resource_penalty: float = 0.15     # resource acquisition reduction when active
degenerative_flee_threshold_boost: float = 0.15   # flee more easily when degenerated
health_signal_visibility: float = 0.5        # how visible active conditions are to mates

================================================================================
CONSTRAINTS
================================================================================

- Condition prevalence must be LOW in healthy populations (~5-15% active at any time)
- Pathology engine must be computationally lightweight — simple probability checks
- Medical history list must be bounded (max 50 entries) to control memory
- Condition effects must be MODEST — not catastrophic for individuals
  (conditions reduce fitness, they don't instantly kill)
- Backward compatibility: pathology_enabled=False reproduces pre-DD17 behavior
- Run validation: post-DD17 population dynamics should remain stable
  (conditions create individual differences, not population collapse)
