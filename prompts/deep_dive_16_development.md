# SIMSIV — PROMPT: DEEP DIVE 16 — DEVELOPMENTAL BIOLOGY (NATURE VS NURTURE)
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_16_development.md
# Use: Send to Claude after DD15 is complete
# Priority: PHASE C, Sprint 9

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 16 on the SIMSIV developmental model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py
  4. D:\EXPERIMENTS\SIM\engines\reproduction.py
  5. D:\EXPERIMENTS\SIM\engines\resources.py (child investment, childhood mortality)
  6. D:\EXPERIMENTS\SIM\engines\mortality.py (childhood death)
  7. D:\EXPERIMENTS\SIM\config.py
  8. D:\EXPERIMENTS\SIM\STATUS.md

Current model: traits are fixed at birth via genetic inheritance. Environment
affects survival but not trait expression. This misses one of the most important
findings in behavioral science: the same genotype produces very different
phenotypes depending on early environment. This deep dive adds developmental
plasticity — childhood environment modifies how genetic potential is expressed
in adulthood. This is the formal nature vs nurture model.

================================================================================
DEEP DIVE 16: DEVELOPMENTAL BIOLOGY
================================================================================

SCIENTIFIC FOUNDATION:

Behavioral genetics research finding (Minnesota Twin Study and others):
  - Heritability of most traits INCREASES with age
  - In childhood: ~40% heritable, 60% environment
  - In adulthood: ~60-80% heritable, 20-40% environment
  - The environment matters most EARLY and matters less as agents mature

Gene-environment interaction (GxE):
  - Some genotypes are highly sensitive to environment (orchid genotype)
  - Others are robust regardless of environment (dandelion genotype)
  - mental_health_baseline (DD15) is the key moderator of this

Critical periods:
  - 0-5 years: most plastic, highest environmental impact
  - 5-15 years: moderate plasticity, peer effects important
  - 15+: trait expression largely stabilized but still malleable

CURRENT STATE:
  - Children exist from age 0-15 doing nothing developmental
  - Traits are fixed at conception via breed()
  - DD06 added childhood mortality and parental investment costs
  - DD15 added heritability coefficients to breed()
  - No mechanism for childhood environment to modify trait expression

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. DEVELOPMENTAL TRAIT MODIFICATION
   At maturation (age 15), agent traits should be modified based on childhood:

   Resource environment effect:
   - Well-resourced childhood (parental resources > threshold): +bonus to
     intelligence_proxy, impulse_control, mental_health_baseline
   - Deprived childhood (parental resources < threshold): +bonus to
     aggression_propensity, risk_tolerance (stress response adaptation)
     -penalty to intelligence_proxy, impulse_control
   Science: childhood poverty → lower IQ, higher aggression is well-documented

   Parental trait environment effect:
   - Children raised by high-cooperation parents: cooperation_propensity boost
   - Children raised by aggressive parents: aggression_propensity boost
   - This is the social learning / modeling component of heritability
   Science: parental modeling separate from genetic transmission

   Orphan effect:
   - No parental trait modeling → traits drift toward population mean
   - Additional aggression boost (attachment theory — insecure attachment)
   - Reduced trust capacity (lower social_trust starting value)
   Science: orphan/neglect effects on adult behavior well-documented

   Birth order effect (optional):
   - Firstborn: slightly higher conscientiousness (intelligence_proxy proxy)
   - Later-born: slightly higher risk_tolerance, novelty_seeking
   Science: birth order effects are contested but real in some studies

B. CRITICAL PERIOD IMPLEMENTATION
   Since we use annual ticks, approximate critical periods as:
   - Age 0-5: apply developmental modifications at age 5
   - Age 5-15: apply peer group effects at maturation (age 15)
   - Store developmental_environment on the child agent as it grows

   What to track per child (new fields on Agent):
   - childhood_resource_quality: float — average parental resources during 0-5
   - childhood_trauma: bool — did agent experience parental death before age 10
   - parent_aggression: float — average of parents' aggression values
   - parent_cooperation: float — average of parents' cooperation values

C. PHENOTYPE VS GENOTYPE DISTINCTION
   After this deep dive, agents have TWO layers:
   - Genotype: the values passed to breed() — the raw genetic potential
   - Phenotype: the expressed values at maturity — genotype + developmental mods

   The distinction matters for:
   - What gets passed to offspring: GENOTYPE (not phenotype)
   - What affects behavior: PHENOTYPE
   - Selection pressure: on PHENOTYPE (which is correlated with genotype but not identical)

   This is scientifically critical: you can have a genetically cooperative person
   raised in a violent environment who behaves aggressively but whose children
   inherit the cooperative genotype. This is how environmental effects don't
   permanently corrupt a gene pool.

D. ORCHID VS DANDELION GENOTYPES
   mental_health_baseline (DD15) as the sensitivity moderator:
   - Low mental_health_baseline (orchid): high sensitivity to environment
     Good environment → dramatically better outcomes than average
     Bad environment → dramatically worse outcomes than average
   - High mental_health_baseline (dandelion): low sensitivity
     Outcomes relatively stable regardless of environment

   Implementation: developmental modification magnitude = base_effect * (1 - mental_health_baseline)
   This creates natural variation in developmental plasticity.

E. PEER GROUP EFFECTS (AGE 5-15)
   Current model: no peer interactions for children
   After this dive: at maturation, agent's traits influenced by:
   - Average traits of other children in the same generation in the population
   - conformity_bias (DD15) gates how much peer influence matters
   - Effect is weaker than parental effect (peer effect ≈ 30% of parental effect)

F. MEASURING NATURE VS NURTURE
   New metric: heritability_realized — computed each generation as the
   correlation between parent trait values and offspring adult trait values.
   This allows you to empirically measure in your simulation what % of
   variance in outcomes is explained by genetics vs environment.
   This is a SCIENTIFIC INSTRUMENT built into the game.

================================================================================
IMPLEMENTATION NOTES
================================================================================

STORAGE ON AGENT:
  Add developmental tracking fields (non-heritable, set during childhood):
  - childhood_resource_quality: float = 0.5  (updated annually 0-5)
  - childhood_trauma: bool = False            (set if parent dies before age 10)
  - developmental_parent_aggression: float = 0.5
  - developmental_parent_cooperation: float = 0.5
  - traits_finalized: bool = False            (set True at maturation)

MATURATION EVENT:
  Add to mortality.py or reproduction.py: when agent reaches age 15,
  apply developmental modifications and set traits_finalized = True.
  Log a "maturation" event with before/after trait values.

GENOTYPE STORAGE (IMPORTANT):
  Store original genotype values separately so breed() uses them:
  - genotype_[trait_name]: float for each heritable trait
  - Set at birth, never modified
  - breed() reads genotype values, not phenotype values
  - Phenotype values (the trait fields) are modified at maturation

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_16_development.md — design decisions, GxE formulas
2. models/agent.py — genotype storage, developmental fields, maturation flag
3. engines/reproduction.py — track childhood resource quality, maturation event
4. engines/mortality.py — childhood trauma flag on parent death
5. engines/resources.py — update childhood_resource_quality annually
6. config.py additions — developmental parameters
7. metrics/collectors.py — heritability_realized metric, developmental metrics
8. DEV_LOG.md entry
9. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

developmental_plasticity_enabled: bool = True
childhood_resource_effect: float = 0.05      # max trait modification from resource quality
parental_modeling_effect: float = 0.08       # max trait modification from parental traits
orphan_aggression_boost: float = 0.06        # aggression increase for orphans at maturation
peer_influence_effect: float = 0.03          # max trait modification from peer group
critical_period_years: int = 5               # age at which first developmental mods apply
birth_order_effect: float = 0.02             # birth order trait modification magnitude

================================================================================
CONSTRAINTS
================================================================================

- Developmental modifications must be SMALL (max ±0.10 per trait)
  — enough to matter statistically, not enough to override genetics
- Genotype must be stored separately and used in breed() — this is critical
- traits_finalized flag prevents re-application of developmental mods
- Existing behavior must be preserved: run validation comparing pre/post DD16
  key metrics (Gini, violence, cooperation) — should be within 10%
- The heritability_realized metric is the scientific payoff — implement carefully
