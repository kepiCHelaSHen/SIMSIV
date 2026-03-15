# Deep Dive 27: Trait Completion (9 New Heritable Traits)

**Status**: Implemented
**Trait count**: 26 -> 35 (scientifically complete ceiling)

## New Traits

### Group 1: Physical Performance (indices 26-27)
- **physical_strength** (h2=0.60, default=0.5): Force output, distinct from physical_robustness (damage absorption). Sex differential: males express 1.4x in combat, females 0.6x in foraging.
  - conflict.py: combat power additive (config.physical_strength_combat_weight=0.12)
  - resources.py: competitive weight +0.08 (sex differential)
  - mating.py: male mate value +0.05

- **endurance** (h2=0.50, default=0.5): Aerobic capacity, sustained output. No sex differential.
  - resources.py: foraging bonus (config.endurance_foraging_bonus=0.06)
  - mortality.py: health decay *max(0.7, 1.0 - endurance*0.15)
  - reproduction.py: childbirth mortality *max(0.5, 1.0 - endurance*0.4)

### Group 2: Social Architecture (indices 28-29)
- **group_loyalty** (h2=0.42, default=0.5): Kin selection coefficient. Sacrifice for group even without expected reciprocation.
  - conflict.py: coalition defense +0.3, third-party punishment +0.15
  - resources.py: in-faction sharing *1.2 when group_loyalty > 0.6
  - institutions.py: norm compliance bonus +0.1

- **outgroup_tolerance** (h2=0.40, default=0.5): Constitutional openness to strangers. Inversely correlated with group_loyalty (-0.35).
  - mating.py: out-of-neighborhood mate search weight increased
  - resources.py: sharing trust threshold lowered (config.outgroup_tolerance_sharing_threshold=0.15)
  - reputation.py: faster trust extension to immigrants
  - society.py: immigration pull factor *(0.7 + avg_outgroup_tolerance*0.6)

### Group 3: Temporal and Cognitive (indices 30-31)
- **future_orientation** (h2=0.40, default=0.5): Time preference inverted for clarity (1.0=patient/future-focused, 0.0=impulsive/now). Distinct from impulse_control (restraining actions).
  - resources.py: storage multiplier *(0.6 + future_orientation*0.8), competitive weight +0.10
  - reproduction.py: birth spacing when resources low and future_orientation > 0.6
  - mating.py: bond dissolution resistance *max(0.5, 1.0 - future_orientation*0.3)
  - institutions.py: institutional drift boost +0.05

- **conscientiousness** (h2=0.49, default=0.5): Big Five dimension. Organized, disciplined, reliable. Distinct from impulse_control and future_orientation.
  - reputation.py: skill decay *max(0.4, 1.0 - conscientiousness*0.5) (config.conscientiousness_skill_decay_modifier=0.5)
  - reproduction.py: child investment *(0.8 + conscientiousness*0.4)
  - mortality.py: health decay *max(0.75, 1.0 - conscientiousness*0.12)
  - institutions.py: norm compliance bonus +0.08

### Group 4: Psychopathology Spectrum (indices 32-33)
- **psychopathy_tendency** (h2=0.50, default=0.2): Reduced empathy, fearlessness, strategic manipulation. Default 0.2 (most people are not psychopathic). Distinct from aggression_propensity (reactive/emotional).
  - resources.py: sharing penalty *max(0.2, 1.0 - psychopathy*0.6) when > 0.6 (config.psychopathy_sharing_penalty=0.6)
  - conflict.py: reduced network deterrence, sharpened prey selection
  - mating.py: enhanced bond formation (charm), accelerated dissolution
  - reputation.py: initial reputation boost but amplified damage

- **anxiety_baseline** (h2=0.40, default=0.5): Threat sensitivity disposition. Distinct from mental_health_baseline (resilience under stress).
  - conflict.py: flee threshold boost (config.anxiety_flee_boost=0.10), conflict initiation suppression *max(0.3, 1.0 - anxiety*0.4)
  - mating.py: female choosiness boost +0.15
  - resources.py: hoarding bonus +0.10 (storage retention)
  - pathology.py: mental_illness activation *(0.7 + anxiety*0.6)

### Group 5: Evolutionary Psychology (index 34)
- **paternal_investment_preference** (h2=0.45, default=0.5): Female preference for high-investment vs high-genetic-quality males (Gangestad & Simpson trade-off).
  - mating.py: female mate choice reweighting (investment vs genetic signals)
  - mating.py: EPC chance *(1.5 - paternal_investment_preference)
  - mating.py: male bond dissolution resistance +0.2

## Config Parameters Added
- physical_strength_combat_weight: 0.12
- endurance_foraging_bonus: 0.06
- anxiety_flee_boost: 0.10
- psychopathy_sharing_penalty: 0.6
- outgroup_tolerance_sharing_threshold: 0.15
- future_orientation_storage_multiplier: 0.8
- conscientiousness_skill_decay_modifier: 0.5

## Metrics Added
avg_physical_strength, avg_endurance, avg_group_loyalty, avg_outgroup_tolerance,
avg_future_orientation, avg_conscientiousness, avg_psychopathy_tendency,
avg_anxiety_baseline, avg_paternal_investment_preference, psychopathy_std

## Correlation Matrix
35 new correlation pairs added. Matrix forced to positive-semidefinite via eigenvalue clipping.

## Validation Results
1. Psychopathy selection: mean stays at 0.207 (target 0.2-0.35) -- PASS
2. Sex differential: male combat contribution 1.37x female -- PASS
3. Institutional emergence: avg law_strength 0.498 with emergent institutions -- PASS
4. Paternal investment: mate choice correctly reweighted by preference -- PASS
