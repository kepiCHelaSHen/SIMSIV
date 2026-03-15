# SIMSIV — PROMPT: DEEP DIVE 04 — TRAIT INHERITANCE AND GENETICS
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_04_genetics.md
# Use: Send to Claude after DD01-DD03 are complete
# Priority: PHASE B, Sprint 4

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 04 on the SIMSIV trait inheritance and genetic model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py (breed(), create_initial_population(),
     HERITABLE_TRAITS, TRAIT_CORRELATION)
  4. D:\EXPERIMENTS\SIM\engines\reproduction.py
  5. D:\EXPERIMENTS\SIM\config.py
  6. D:\EXPERIMENTS\SIM\STATUS.md (post-DD02/DD03 results)

The current genetic model is simple: midpoint blending + Gaussian noise. This deep
dive evaluates whether the model captures enough evolutionary dynamics and whether
trait evolution rates match anthropological timescales.

================================================================================
DEEP DIVE 04: TRAIT INHERITANCE AND GENETICS
================================================================================

POST-DD02 DATA POINTS (use these to inform design):
  - Aggression drops ~2.7% over 200 years (with infidelity OFF)
  - Cooperation rises +5-7% over 200 years (from resource networks + female choice)
  - Mutation σ=0.05 per generation per trait — is this too fast, too slow, or right?
  - Trait correlations only applied at population initialization — offspring don't
    maintain correlations (midpoint + noise ignores correlation structure)
  - 8 heritable traits; trait range [0.0-1.0] with hard clip
  - "Sexy sons" effect observed: EPC weakens aggression selection because
    mate_value doesn't penalize aggression directly
  - No dominance/recessiveness, no epistasis, no sexual dimorphism in heritability

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. INHERITANCE MECHANISM
   Current: child_val = (parent1 + parent2) / 2.0 + N(0, σ)
   - Is midpoint blending + Gaussian noise realistic enough?
   - Should there be a random parent-weighted blend? (child gets 40-60% from
     each parent rather than always 50/50)
   - Should mutation magnitude be trait-dependent? (some traits more heritable
     than others — fertility_base is highly heritable, intelligence less so)
   - Should there be rare large mutations? (mixed Gaussian: 95% at σ=0.05,
     5% at σ=0.15 for occasional big jumps)
   - Should traits have different heritability coefficients? (h² values)

B. CORRELATION MAINTENANCE
   Current: TRAIT_CORRELATION applied only at population init.
   After generation 0, correlations decay because midpoint blending ignores them.
   - Should breed() enforce correlations on offspring?
     (e.g., if child has high aggression, adjust cooperation down slightly)
   - Or is the natural decay of correlations itself an interesting emergent dynamic?
   - Should new trait-trait correlations be able to EMERGE from selection pressure?
     (e.g., if cooperation+intelligence is selected for, those traits should
     become correlated in the population over time — which they would naturally
     if both are co-selected)
   - Decision question: is this worth the complexity cost?

C. MUTATION MODEL
   Current: σ=0.05, hard clip to [0.0-1.0].
   - Is σ=0.05 the right rate? Compare to anthropological timescales:
     200 sim-years ≈ 6-8 generations → 2-3% trait shift is very fast
     for biological evolution, reasonable for cultural transmission
   - Should mutation rate itself be heritable? (evolvability)
   - Should environmental stress increase mutation rate?
     (stress-induced variation — controversial in biology but useful in models)
   - Should clipping to [0.0-1.0] be replaced with soft bounds?
     (logistic transformation to keep traits in range without wall effects)

D. SELECTION PRESSURE VISIBILITY
   The sim has multiple selection channels. Verify and quantify them:
   - Female choice: penalizes aggression (-0.5 weight), rewards cooperation (+0.4)
   - Resource engine: aggression_production_penalty reduces competitive weight
   - Violence: aggressive agents take more damage, die more
   - Reproduction: bonded agents have 1.3x conception chance
   - Child survival: parental resources boost survival
   - Is there a way to measure realized selection differential per trait per gen?
   - Should there be a metrics output for trait evolution tracking?

E. SEXUAL DIMORPHISM IN TRAITS
   Current: identical trait distributions for males and females.
   - Should some traits have sex-specific expression? (aggression expressed
     differently in males vs females, even if heritable value is same)
   - Should sex-linked inheritance be modeled? (son inherits more from father
     for some traits, daughter more from mother)
   - Or is sex-blind inheritance + differential selection sufficient?
     (selection acts differently on males vs females through mating/conflict engines)

F. GENETIC DRIFT AND FOUNDER EFFECTS
   - In small populations (< 100), genetic drift dominates selection.
     Does the model handle this correctly?
   - After migrant injection (min_viable_population rescue), do injected
     agents' traits dilute the evolved population? Is this desirable?
   - Should migrants' traits be drawn from the current population distribution
     rather than uniform [0.2-0.8]?

G. TRAIT EXPANSION (OPTIONAL)
   Current 8 traits may be insufficient. Consider:
   - Parenting_investment: willingness to invest resources in offspring
     (currently derived from paternity_confidence, but not heritable)
   - Social_learning: speed of trust network formation
   - Longevity: heritable health resilience
   - Or: is 8 traits already enough, and adding more just dilutes selection?

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_04_genetics.md — design decisions and selection analysis
2. models/agent.py updates — if breed() or trait model changes
3. config.py additions — new genetic parameters
4. metrics/collectors.py additions — trait evolution tracking metrics
5. DEV_LOG.md entry
6. CHAIN_PROMPT.md update

================================================================================
NEW PARAMETERS TO CONSIDER FOR CONFIG
================================================================================

mutation_sigma_by_trait: dict[str,float]  # per-trait mutation rates (if trait-dependent)
heritability_by_trait: dict[str,float]    # h² values per trait
rare_mutation_rate: float = 0.05          # probability of large mutation per trait
rare_mutation_sigma: float = 0.15         # σ for rare large mutations
enforce_trait_correlations: bool = False   # maintain correlations in breed()
stress_mutation_multiplier: float = 1.0   # scarcity increases mutation rate
parent_weight_variance: float = 0.0       # 0 = exact 50/50, >0 = random parent weighting
migrant_trait_source: str = "uniform"     # "uniform" or "population" for rescue migrants
