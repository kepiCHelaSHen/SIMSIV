# Deep Dive 15: Extended Genomics

## Summary
Expanded heritable trait system from 8 to 21 traits with per-trait heritability
coefficients and scientifically grounded behavioral effects. Upgraded breed()
to use h²-weighted inheritance model.

## New Traits (13 added)

### Biological Robustness
| Trait | h² | Effect |
|-------|-----|--------|
| longevity_genes | 0.25 | Shifts age_death_base up to +10yr; reduces health decay 40% after age 50 |
| disease_resistance | 0.40 | Reduces epidemic vulnerability up to 50% |
| physical_robustness | 0.50 | Absorbs combat damage (up to 40% reduction); contributes to combat power |
| pain_tolerance | 0.45 | Raises effective risk_tolerance for flee check (+0.15); combat power component |

### Psychological
| Trait | h² | Effect |
|-------|-----|--------|
| mental_health_baseline | 0.40 | Moderates stress→aggression response (up to 50% reduction) |
| emotional_intelligence | 0.40 | Amplifies trust formation (+30%), gossip effectiveness (+30%), mate assessment (+30%), bluff detection (+30%) |
| impulse_control | 0.50 | Gates aggression→conflict translation (up to 60% reduction) |
| novelty_seeking | 0.40 | Correlated with risk_tolerance (+0.4), anti-correlated with conformity (-0.3) |

### Social
| Trait | h² | Effect |
|-------|-----|--------|
| empathy_capacity | 0.35 | Extends sharing radius (+15%), reduces conflict initiation (-30%) |
| conformity_bias | 0.35 | Accelerates institutional adoption (+30% cooperation factor) |
| dominance_drive | 0.50 | Independent dominance_score acquisition (+20% weight); combat power component |

### Reproductive Biology
| Trait | h² | Effect |
|-------|-----|--------|
| maternal_investment | 0.35 | Quality-quantity tradeoff: -20% conception, +15% child survival |
| sexual_maturation_rate | 0.60 | Modifies age_first_reproduction ±3 years |

## Heritability Model (breed())
```
child_val = h² * parent_midpoint + (1 - h²) * pop_mean + mutation
```
- `h²`: per-trait heritability coefficient
- `parent_midpoint`: weighted blend of parent values (with parent_weight_variance)
- `pop_mean`: current population mean for this trait
- `mutation`: Gaussian noise (stress-amplified per DD04)

Low h² traits (longevity_genes=0.25) regress strongly to population mean.
High h² traits (intelligence_proxy=0.65) track parents closely.

## Correlation Matrix
21x21 matrix built programmatically. Key new correlations:
- impulse_control ↔ aggression: -0.4
- emotional_intelligence ↔ cooperation: +0.3
- mental_health ↔ impulse_control: +0.3
- novelty_seeking ↔ risk_tolerance: +0.4
- dominance_drive ↔ aggression: +0.3
- conformity_bias ↔ novelty_seeking: -0.3
- longevity_genes ↔ mental_health: +0.2
- empathy ↔ cooperation: +0.2
- physical_robustness ↔ pain_tolerance: +0.3

## Engine Wiring
- **mortality.py**: longevity_genes (health decay, death age), disease_resistance (epidemics)
- **conflict.py**: impulse_control (aggression gate), mental_health (stress moderation), empathy (conflict suppression), pain_tolerance (flee threshold), physical_robustness (damage absorption, combat power), dominance_drive (combat power)
- **mating.py**: emotional_intelligence (trust-weighted mate assessment)
- **resources.py**: empathy_capacity (sharing), dominance_drive (dominance score), emotional_intelligence (trust formation, bluff detection)
- **reputation.py**: emotional_intelligence (gossip effectiveness)
- **reproduction.py**: maternal_investment (conception/survival tradeoff), sexual_maturation_rate (via is_fertile_with_config)
- **institutions.py**: conformity_bias (institutional drift acceleration)

## Config
- `heritability_by_trait`: dict (empty = use TRAIT_HERITABILITY defaults from agent.py)

## Metrics Added (13)
avg_longevity_genes, avg_disease_resistance, avg_physical_robustness, avg_pain_tolerance,
avg_mental_health, avg_emotional_intelligence, avg_impulse_control, avg_novelty_seeking,
avg_empathy, avg_conformity, avg_dominance_drive, avg_maternal_investment, avg_sexual_maturation
