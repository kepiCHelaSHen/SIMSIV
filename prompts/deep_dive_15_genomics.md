# SIMSIV — PROMPT: DEEP DIVE 15 — EXTENDED GENOMICS
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_15_genomics.md
# Use: Send to Claude after DD14 factions is complete
# Priority: PHASE C, Sprint 8

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 15 on the SIMSIV genomics model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (HERITABLE_TRAITS, TRAIT_CORRELATION, breed())
  4. D:\EXPERIMENTS\SIM\engines\reproduction.py
  5. D:\EXPERIMENTS\SIM\engines\mortality.py
  6. D:\EXPERIMENTS\SIM\config.py
  7. D:\EXPERIMENTS\SIM\STATUS.md

The current model has 8 heritable traits. Real human phenotypes are driven by
hundreds of polygenic traits with known heritability coefficients and known
interactions. This deep dive expands the heritable trait system to capture
the biological substrate of human individual differences more completely —
longevity, disease resistance, physical robustness, mental health spectrum,
emotional intelligence, and constitutional health — all with scientifically
grounded heritability values.

This is NOT about adding complexity for its own sake. Every new trait must:
  1. Have a known real-world heritability coefficient
  2. Have a clear behavioral or biological effect in the simulation
  3. Not duplicate what existing traits already model

================================================================================
DEEP DIVE 15: EXTENDED GENOMICS
================================================================================

CURRENT HERITABLE TRAITS (8):
  aggression_propensity    h² ~0.44
  cooperation_propensity   h² ~0.40
  attractiveness_base      h² ~0.50
  status_drive             h² ~0.50
  risk_tolerance           h² ~0.48
  jealousy_sensitivity     h² ~0.45
  fertility_base           h² ~0.50
  intelligence_proxy       h² ~0.65

NEW TRAITS TO ADD (target: 20-25 total):

A. BIOLOGICAL ROBUSTNESS TRAITS

  longevity_genes: float [0.0-1.0]   h² ~0.25
    Effect: modifies age_death_base — high longevity agents live ~10yr longer
    Interaction: amplifies health decay resistance after age 50
    Science: ~25% heritable, major polygenic contribution (APOE, FOXO3, etc.)

  disease_resistance: float [0.0-1.0]  h² ~0.40
    Effect: reduces epidemic vulnerability multiplier
    Interaction: partially protective during DD09 epidemic events
    Science: immune system variation is substantially heritable

  physical_robustness: float [0.0-1.0]  h² ~0.50
    Effect: reduces health damage from conflict (separate from aggression)
    Interaction: modifies violence_cost_health — robust agents absorb more damage
    Science: physical resilience / musculoskeletal robustness

  pain_tolerance: float [0.0-1.0]  h² ~0.45
    Effect: modifies flee_threshold — high tolerance agents fight through pain
    Interaction: reduces health-based fertility penalty threshold
    Science: pain sensitivity is well-documented heritable trait

B. PSYCHOLOGICAL TRAITS

  mental_health_baseline: float [0.0-1.0]  h² ~0.40
    Effect: baseline resistance to stress-induced behavioral changes
    High value = stable under pressure, low value = volatile/erratic
    Interaction: modulates how resource stress affects aggression and cooperation
    Science: neuroticism/emotional stability component (~40% heritable)

  emotional_intelligence: float [0.0-1.0]  h² ~0.40
    Effect: speeds trust network formation — high EI agents build trust faster
    Interaction: multiplies gossip effectiveness (better at reading social signals)
    Distinguishes from intelligence_proxy (which is resource acquisition / g-factor)
    Science: EI has distinct heritable component from general intelligence

  impulse_control: float [0.0-1.0]  h² ~0.50
    Effect: modulates translation of aggression_propensity to actual conflict
    High impulse control: aggressive trait doesn't always result in action
    Low impulse control: even mildly aggressive agents act on small provocations
    Science: inhibitory control is well-documented heritable (~50%)
    This directly addresses the aggression trait vs behavior gap

  novelty_seeking: float [0.0-1.0]  h² ~0.40
    Effect: drives exploration behavior — in v2 will affect migration
    Current effect: modifies mating pool participation, risk-taking in contests
    Interaction: partially correlated with risk_tolerance but distinct
    Science: DRD4 novelty seeking — well-documented (~40% heritable)

C. SOCIAL TRAITS

  empathy_capacity: float [0.0-1.0]  h² ~0.35
    Effect: amplifies cooperation sharing with non-kin (extends altruism radius)
    Interaction: reduces aggression against agents with shared history
    Distinguishes from cooperation_propensity (which is behavioral tendency)
    Science: empathy has heritable component distinct from prosocial behavior

  conformity_bias: float [0.0-1.0]  h² ~0.35
    Effect: modulates how strongly agents adopt prevalent norms
    High conformity: agents match surrounding agents' behavior more
    Low conformity: agents maintain heritable traits despite social pressure
    Interaction: key driver of institutional adoption speed (DD05)
    Science: conformity tendency has documented heritable component

  dominance_drive: float [0.0-1.0]  h² ~0.50
    Effect: independent contribution to dominance_score acquisition
    Distinguishes from status_drive (which mixes prestige + dominance seeking)
    High value: agent actively pursues dominance hierarchy position
    Science: dominance motivation distinct from general status-seeking

D. REPRODUCTIVE BIOLOGY TRAITS

  maternal_investment: float [0.0-1.0]  h² ~0.35
    Effect: heritable tendency to invest heavily in fewer offspring vs many
    High value: lower conception rate but significantly higher child survival
    Low value: higher conception rate but lower per-child investment
    This is the quantity-quality tradeoff made heritable
    Science: maternal behavior has heritable component in all mammals

  sexual_maturation_rate: float [0.0-1.0]  h² ~0.60
    Effect: modifies age_first_reproduction — high value agents mature earlier
    Range: ±3 years around config default
    Interaction: earlier maturity → more lifetime reproductive opportunities
    but lower resource accumulation at first mating
    Science: age at puberty is ~60% heritable

================================================================================
IMPLEMENTATION NOTES
================================================================================

HERITABILITY COEFFICIENTS:
  Each trait should have a configurable h² value that gates how much of the
  parent-midpoint vs random drift contributes to the offspring value.
  child_val = h² * parent_midpoint + (1 - h²) * population_mean + mutation

  This is more scientifically accurate than the current pure midpoint model.
  Add to config as heritability_by_trait dict with defaults matching real values.

CORRELATION MATRIX EXPANSION:
  Expand TRAIT_CORRELATION to include new traits with known correlations:
  - impulse_control negatively correlates with aggression_propensity (-0.4)
  - emotional_intelligence positively correlates with cooperation (+0.3)
  - mental_health_baseline positively correlates with impulse_control (+0.3)
  - novelty_seeking positively correlates with risk_tolerance (+0.4)
  - dominance_drive positively correlates with aggression_propensity (+0.3)
  - conformity_bias negatively correlates with novelty_seeking (-0.3)
  - longevity_genes positively correlates with mental_health_baseline (+0.2)

BEHAVIORAL EFFECTS INTEGRATION:
  Each new trait should modify existing engine behavior via small multipliers.
  Do NOT create new behavioral systems for each trait — wire into existing engines.
  Keep total computational overhead modest.

BACKWARD COMPATIBILITY:
  All existing 8 traits must remain unchanged.
  New traits default to 0.5 for existing populations.
  New trait effects must be small enough that existing calibration holds.
  Run validation: post-DD15 Gini, violence rate, and cooperation should be
  within 10% of pre-DD15 values.

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_15_genomics.md — trait list, heritability values, effect formulas
2. models/agent.py — new trait fields, expanded HERITABLE_TRAITS, expanded TRAIT_CORRELATION
3. engines/ — targeted modifications to wire new traits into existing behavior
4. config.py — heritability_by_trait dict, any new behavior parameters
5. metrics/collectors.py — track new trait means and diversity
6. DEV_LOG.md entry
7. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

heritability_by_trait: dict  # h² per trait, defaults to 0.5 for existing traits
# Individual heritability defaults:
# longevity_genes: 0.25, disease_resistance: 0.40, physical_robustness: 0.50
# pain_tolerance: 0.45, mental_health_baseline: 0.40, emotional_intelligence: 0.40
# impulse_control: 0.50, novelty_seeking: 0.40, empathy_capacity: 0.35
# conformity_bias: 0.35, dominance_drive: 0.50
# maternal_investment: 0.35, sexual_maturation_rate: 0.60

================================================================================
CONSTRAINTS
================================================================================

- Add traits incrementally — test after each group of 3-4 new traits
- Total HERITABLE_TRAITS should reach 20-22 (not 30+ — diminishing returns)
- Each trait MUST have a measurable behavioral effect — no dead fields
- Heritability model upgrade is the most important part — do this first
- Backward compatibility is mandatory — existing scenarios must still run
