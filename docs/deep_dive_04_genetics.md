# Deep Dive 04 — Trait Inheritance and Genetics: Design Decisions

## Overview

DD04 refined the genetic model with parent weight variance, rare mutations,
stress-induced mutation, and population-derived migrant traits. It also added
per-trait evolution tracking metrics. The core finding: the existing selection
pressures (from DD01-DD03) create meaningful trait evolution, and DD04's changes
maintain higher genetic diversity while preserving selection signals.

## Design Decisions

### A. Inheritance Mechanism

**Decision**: Add parent weight variance; keep midpoint blend as base.

- Old: `child = (p1 + p2) / 2.0 + N(0, sigma)`
- New: `child = p1 * w + p2 * (1-w) + mutation` where `w ~ clip(N(0.5, variance), 0.1, 0.9)`
- `parent_weight_variance = 0.1` by default
- Each trait gets an independent random parent weight per child
- More genetically realistic — recombination isn't perfect 50/50
- This adds noise to inheritance, slightly reducing selection speed but
  maintaining more variation in the population

### B. Correlation Maintenance

**Decision**: Let correlations decay naturally. Do NOT enforce in breed().

Measured correlation decay over 200yr:
- agg-coop: -0.400 -> +0.065 (decayed to near zero)
- agg-risk: +0.300 -> -0.037 (decayed)
- intel-coop: +0.200 -> -0.057 (decayed)

This is actually correct behavior:
1. Initial correlations represent founder population structure
2. Selection creates NEW correlations (e.g., cooperation+intelligence co-selected)
3. Enforcing correlations in breed() would be artificial
4. Natural correlation dynamics are themselves an interesting emergent signal
5. Correlation tracking added to metrics so we can observe what emerges

### C. Mutation Model

**Decision**: Add rare large mutations and stress-induced amplification.

- Base sigma remains 0.05 (validated: ~3.5-7% trait shift per 200yr is reasonable)
- **Rare mutations**: 5% chance per trait per birth of using sigma=0.15 (3x normal)
  - Maintains genetic diversity against selection pressure
  - Prevents trait fixation at boundaries
  - Post-DD04 trait std ~0.09 (was ~0.07) — healthy improvement
- **Stress-induced mutation**: during scarcity, sigma *= 1.0 + (multiplier-1) * scarcity
  - `stress_mutation_multiplier = 1.5` (50% increase at max scarcity)
  - Increases variation under environmental pressure
  - Allows faster adaptation to changed conditions
- Hard clip [0, 1] retained — logistic transform would be overengineering

### D. Selection Pressure Visibility

**Decision**: Add per-trait mean tracking to metrics (all 8 traits).

New metrics columns:
- `avg_attractiveness`, `avg_status_drive`, `avg_risk_tolerance`, `avg_jealousy`,
  `avg_fertility`, `avg_intelligence` (aggression + cooperation already existed)
- `trait_std_aggression`, `trait_std_cooperation` (diversity tracking)
- `max_generation` (generational depth)

Selection pressure analysis (200yr baseline):

| Trait | Start | End | Delta | Direction |
|-------|-------|-----|-------|-----------|
| aggression | 0.503 | 0.466 | -0.036 | Selected against (violence cost, female choice, resource penalty) |
| cooperation | 0.499 | 0.557 | +0.058 | Selected for (resource networks, female choice, sharing) |
| intelligence | 0.500 | 0.571 | +0.071 | Selected for (competitive weight in resources) |
| fertility | 0.501 | 0.515 | +0.014 | Weakly selected for (more offspring) |
| attractiveness | 0.500 | 0.502 | +0.002 | Neutral (10% of mate_value, small effect) |
| status_drive | 0.498 | 0.471 | -0.027 | Selected against (risk-taking cost) |
| risk_tolerance | 0.500 | 0.496 | -0.004 | Near neutral |
| jealousy | 0.499 | 0.502 | +0.003 | Neutral |

### E. Sexual Dimorphism

**Decision**: No sex-specific inheritance or expression.

Sex differences at yr200 are negligible (all within +/-0.015). This is because:
1. Cross-sex inheritance (midpoint of both parents) dilutes sex-specific selection
2. Real sexual dimorphism takes far more generations to emerge
3. Differential selection IS happening (conflict affects males more) but
   cross-inheritance blends it back

The lack of dimorphism is actually the correct result for ~12 generations.

### F. Genetic Drift and Founder Effects

**Decision**: Population-derived migrant traits.

- Old: migrants get uniform [0.2, 0.8] traits (anti-selection injection)
- New: `migrant_trait_source = "population"` — traits sampled from current
  population's mean/std per trait
- Falls back to uniform if population < 5 (emergency edge case)
- Prevents migrants from diluting evolved trait distributions after 200yr of selection
- std floored at 0.03 to prevent migrant cloning in low-diversity populations

### G. Trait Expansion

**Decision**: No new traits. 8 is sufficient.

- Adding traits dilutes selection on existing ones
- Parenting investment emerges from cooperation + paternity confidence
- Social learning is DD07 territory (reputation system)
- Longevity is partially captured by health (non-heritable but resource-dependent)

## Results

### Trait Evolution by Scenario (200yr)

| Scenario | Agg delta | Coop delta | Intel delta | Fert delta | Agg std |
|----------|-----------|------------|-------------|------------|---------|
| BASELINE | -0.036 | +0.058 | +0.071 | +0.014 | 0.084 |
| STRICT_MONOGAMY | -0.053 | +0.074 | +0.093 | +0.011 | 0.091 |
| ELITE_POLYGYNY | -0.086 | +0.029 | +0.080 | +0.024 | 0.088 |
| HIGH_VIOLENCE | -0.069 | +0.059 | +0.014 | -0.007 | 0.087 |

### Key Findings

1. **ELITE_POLYGYNY has strongest anti-aggression selection** (-0.086):
   intense mate competition + female choice creates strong pressure
2. **STRICT_MONOGAMY drives strongest cooperation+intelligence selection**:
   cooperative traits dominate when mating is equalized
3. **HIGH_VIOLENCE reduces intelligence selection**: population under stress,
   survival trumps resource acquisition efficiency
4. **Trait diversity maintained**: std ~0.09 across all scenarios (was ~0.07
   pre-DD04), rare mutations prevent fixation
5. **Fertility is context-dependent**: rises under polygyny (reproductive
   advantage), falls under violence (population stress)

### Pre/Post DD04 Comparison (200yr baseline)

| Metric | Pre-DD04 | Post-DD04 |
|--------|----------|-----------|
| Agg delta | -0.046 | -0.036 |
| Coop delta | +0.074 | +0.058 |
| Intel delta | +0.079 | +0.071 |
| Agg std | 0.068 | 0.084 |
| Coop std | 0.072 | 0.092 |

Selection slightly slower (parent weight variance adds noise) but diversity
much higher (rare mutations). Net positive — more realistic evolution dynamics.

## New Config Parameters (5)

| Parameter | Default | Description |
|-----------|---------|-------------|
| parent_weight_variance | 0.1 | Per-trait random parent blend (0=exact 50/50) |
| rare_mutation_rate | 0.05 | Probability of large mutation per trait per birth |
| rare_mutation_sigma | 0.15 | Sigma for rare large mutations |
| stress_mutation_multiplier | 1.5 | Mutation sigma multiplier during scarcity |
| migrant_trait_source | "population" | Trait source for rescue migrants |

## New Metrics (8)

| Metric | Description |
|--------|-------------|
| avg_attractiveness | Population mean attractiveness_base |
| avg_status_drive | Population mean status_drive |
| avg_risk_tolerance | Population mean risk_tolerance |
| avg_jealousy | Population mean jealousy_sensitivity |
| avg_fertility | Population mean fertility_base |
| avg_intelligence | Population mean intelligence_proxy |
| trait_std_aggression | Population std of aggression_propensity |
| trait_std_cooperation | Population std of cooperation_propensity |
| max_generation | Highest generation number in living population |
