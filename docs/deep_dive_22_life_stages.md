# Deep Dive 22: Life Stage Social Roles

## Design Decisions

### Five computed life stages
Life stage is a computed property on Agent (never stored):
- **CHILDHOOD** (age < 15): Learning, trust building, developing traits
- **YOUTH** (15-24): Status competition peak, elevated conflict, intense bonding
- **PRIME** (25-44): Productive core, parenting peak, leadership eligibility
- **MATURE** (45-59): Advisory role, reduced competition, expanded social memory
- **ELDER** (60+): Norm anchor, dispute memory, institutional stability

### Youth phase effects
- Conflict initiation: +25% multiplier (young male effect)
- Female choosiness: +15% in youth (highly selective)
- Risk tolerance expression amplified (youth_risk_multiplier)

### Prime adult effects
- Parenting investment peak: +20% child investment expression
- Leadership eligibility (DD20 war leader requires PRIME or higher)

### Mature adult effects
- Conflict initiation: -20% (wisdom reduces aggression)
- Expanded social memory: ledger cap raised to 150 (from 100)

### Elder effects
- Conflict initiation: -50% (elders rarely fight)
- Norm anchor: respected elders slow institutional drift
- Peaceful presence: elder count in faction reduces out-group targeting
- High-reputation elders (reputation > 0.4) generate strongest effects

### Cohort effects (simplified)
- cohort_range_years (3) defines cohort membership
- Youth trust building multiplier (1.5x) for same-cohort peers

## Config parameters
10 new parameters controlling stage-specific modifiers.

## Metrics
- `youth_conflict_rate`: violence rate among youth specifically
- `elder_count`: living elders
- `life_stage_*_frac`: population distribution across stages
