# Deep Dive 16: Developmental Biology (Nature vs Nurture)

## Summary
Added genotype/phenotype distinction and developmental plasticity. Childhood
environment modifies how genetic potential is expressed at maturation (age 15).
Implements the formal nature vs nurture model.

## Core Concept
- **Genotype**: genetic values set at birth via breed(), stored in `agent.genotype` dict
- **Phenotype**: expressed trait values, modified at maturation by environment
- breed() reads **genotype** from parents (not phenotype)
- Selection acts on **phenotype** (which correlates with but isn't identical to genotype)

## Developmental Tracking Fields (non-heritable)
| Field | Default | Description |
|-------|---------|-------------|
| genotype | {} | Original genetic values at birth, never modified |
| childhood_resource_quality | 0.5 | Running average of parental resources during ages 0-5 |
| childhood_trauma | False | Set if parent dies before agent reaches age 10 |
| developmental_parent_aggression | 0.5 | Average of parents' aggression at birth |
| developmental_parent_cooperation | 0.5 | Average of parents' cooperation at birth |
| traits_finalized | False | Set True at maturation (age 15) |

## Maturation Event (Age 15)
When agent reaches age 15 and genotype exists, developmental modifications are applied:

### Orchid/Dandelion Sensitivity
```
sensitivity = max(0.2, 1.0 - mental_health_baseline * 0.6)
```
Low mental_health_baseline (orchid) = high environmental sensitivity.
High mental_health_baseline (dandelion) = stable regardless.

### Resource Environment
- Well-resourced childhood: +intelligence, +impulse_control, +mental_health
- Deprived childhood: +aggression, +risk_tolerance, -intelligence, -impulse_control

### Parental Modeling
- High-cooperation parents → cooperation boost in child
- High-aggression parents → aggression boost in child

### Orphan Effect
- No living parent at maturation → aggression boost, reputation penalty (-0.1)

### Childhood Trauma
- Parent died before age 10 → +aggression, -mental_health, -impulse_control

### Peer Group (30% of parental effect)
- conformity_bias gates how much peer influence matters
- Pulls traits toward generation average

### Birth Order
- Firstborn: +intelligence, +impulse_control
- Later-born (3rd+): +risk_tolerance, +novelty_seeking

## Constraints
- All modifications capped at ±0.10 per trait
- Sensitivity multiplier further scales effects
- traits_finalized prevents re-application
- Founding population (no genotype) skips maturation

## Config Parameters (7 new)
| Parameter | Default | Description |
|-----------|---------|-------------|
| developmental_plasticity_enabled | True | Enable developmental modifications |
| childhood_resource_effect | 0.05 | Max trait mod from resource quality |
| parental_modeling_effect | 0.08 | Max trait mod from parental traits |
| orphan_aggression_boost | 0.06 | Aggression increase for orphans |
| peer_influence_effect | 0.03 | Max trait mod from peer group |
| critical_period_years | 5 | Age at which resource tracking ends |
| birth_order_effect | 0.02 | Birth order trait modification magnitude |

## Metrics Added (3)
- maturation_events: count of agents maturing this tick
- childhood_trauma_rate: fraction of children with trauma flag
- avg_childhood_resource_quality: mean resource quality among children

## Engine Wiring
- **mortality.py**: Maturation event at age 15, childhood trauma detection on parent death
- **resources.py**: Childhood resource quality tracking during ages 0-5
- **agent.py breed()**: Genotype storage, parent genotype reads, developmental parent traits
