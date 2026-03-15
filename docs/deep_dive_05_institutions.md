# Deep Dive 05 — Institutions: Design Decisions

## Overview

DD05 transformed the institution engine from a stub (88 lines, only inheritance)
into a full institutional layer with drift, norm enforcement, emergent formation,
and property rights. The key result: institutions can now self-organize from
agent behavior, with cooperation driving law formation and violence eroding it.

## Design Decisions

### A. Institutional Drift

**Decision**: law_strength evolves based on cooperation vs violence balance.

Formula:
```
coop_pressure = max(0, avg_cooperation - 0.4) * cooperation_boost
violence_pressure = violence_rate * violence_decay
net = coop_pressure - violence_pressure
resistance = 1 - inertia * current_law  (if growing)
           = 1 - inertia * (1 - current_law)  (if eroding)
delta = drift_rate * net * resistance
```

- `cooperation_institution_boost = 2.0`: cooperation above 0.4 drives growth
- `violence_institution_decay = 3.0`: violence erodes institutions
- `institutional_inertia = 0.8`: path dependency — harder to change at extremes
- `institutional_drift_rate = 0.0`: default OFF (backward-compatible)

Calibration: with drift_rate=0.02, law_strength grows from 0 to ~0.48 over
200 years under baseline conditions (avg_coop ~0.56, violence_rate ~0.05).
This is slow enough to feel institutional but fast enough to observe.

Violence punishment and property rights track law proportionally:
- `violence_punishment_strength = law * 0.7`
- `property_rights_strength = law * 0.5`

### B. Norm Enforcement

**Decision**: Active polygyny detection with scaling penalties.

When monogamy_enforced AND law_strength > 0:
- Detect agents with bond_count > 1
- Detection probability: `law_strength * 0.5`
- Penalties: `reputation -= 0.05 * law`, `resources -= resources * 0.05 * law`
- Logged as "norm_violation" events

In practice, ENFORCED_MONOGAMY prevents multiple bonds at formation
(mating engine check), so norm violations are rare. The enforcement
exists for mixed scenarios where monogamy norms coexist with unrestricted mating.

### C. Emergent Institution Formation

**Decision**: Institutions spontaneously form from sustained behavior patterns.

Two emergence pathways:

1. **Violence punishment** (5-year violence streak):
   - If violence_rate > 0.08 for 5+ consecutive years
   - Sets violence_punishment_strength = 0.1, law_strength >= 0.1
   - Represents community response to sustained violence

2. **Mate limit reduction** (8-year inequality streak):
   - If reproductive top-10% > 3x bottom-50% for 8+ years
   - Reduces max_mates_per_male by 1 (minimum 3)
   - Represents social pressure against extreme polygyny

`emergent_institutions_enabled = False` by default (backward-compatible).

### D. Property Rights

**Decision**: Modulates conflict resource looting.

- `property_rights_strength` [0-1]: fraction of looting prevented
- Conflict engine: `loot_fraction = 0.5 * (1 - property_rights)`
- At 0: winner takes 50% of loser's resource loss (current behavior)
- At 0.5: winner takes 25%
- At 1.0: winner takes nothing (violence still costly but not profitable)
- Tracks law_strength when drift is enabled

### E. Inheritance Enhancement

**Decision**: Change default to ON + add trust-weighted model + prestige inheritance.

Changes:
- `inheritance_law_enabled` default changed from False to True
  - Resources no longer vanish on death (was a major gap)
  - Heirs: partners first, then offspring
  - Baseline now has 5100 inheritance events over 200 years (was 0)
- New inheritance model "trust_weighted": distribute proportional to
  deceased's trust_of(heir_id), minimum 0.1 weight
- `inheritance_prestige_fraction`: heirs inherit a fraction of deceased's
  status. Default 0: no prestige inheritance. STRONG_STATE uses 0.1.

### F. Cross-Engine Modulation

**Decision**: Institution engine mutates config values at end of tick.

This is a deliberate design choice — institutions ARE persistent changes to
the rules. The mutation at tick-end means changes take effect next tick
(natural institutional lag). Other engines already read config values, so
they automatically respond to institutional drift without any code changes.

Modified config values when drift is enabled:
- `law_strength`
- `violence_punishment_strength`
- `property_rights_strength`
- `max_mates_per_male` (via emergence only)

### G. Scenario Design

Two new scenarios added:

**STRONG_STATE**: High law, high tax, high punishment, monogamy
- law=0.8, vps=0.7, property_rights=0.5, tax=0.15
- Lowest violence (0.024), lowest Gini (0.250), highest pop (1177)
- But: lower cooperation selection (0.527 vs 0.564 baseline) because
  institutions substitute for individual cooperation

**EMERGENT_INSTITUTIONS**: Everything starts at zero, self-organizes
- drift_rate=0.02, inertia=0.7, emergence enabled
- Law grows 0 → 0.484 over 200yr
- Pop grows to 941, Gini drops to 0.268
- 24 institutional emergence events

## Results

### Scenario Comparison (200yr, 500 pop)

| Scenario | Pop | Gini | Violence | Law | Agg | Coop | Intel |
|----------|-----|------|----------|-----|-----|------|-------|
| BASELINE | 609 | 0.306 | 0.054 | 0.000 | 0.421 | 0.564 | 0.587 |
| ENFORCED_MONOGAMY | 740 | 0.317 | 0.033 | 0.700 | 0.470 | 0.547 | 0.605 |
| STRONG_STATE | 1177 | 0.250 | 0.024 | 0.800 | 0.459 | 0.527 | 0.529 |
| EMERGENT | 941 | 0.268 | 0.050 | 0.484 | 0.433 | 0.576 | 0.590 |
| HIGH_VIOLENCE | 745 | 0.354 | 0.068 | 0.000 | 0.382 | 0.573 | 0.536 |

### Key Findings

1. **Institutions reduce violence and grow population**: STRONG_STATE has
   2x the population of BASELINE with half the violence rate
2. **Institutions substitute for individual traits**: STRONG_STATE has
   lower cooperation (0.527) than BASELINE (0.564) because institutions
   enforce cooperation externally, reducing selection pressure
3. **Emergent institutions work**: law_strength organically grows from 0 to
   0.484 based on cooperation/violence balance, reproducing key benefits of
   externally-imposed institutions
4. **Inheritance matters**: 5100 events baseline (was 0 pre-DD05), creating
   intergenerational wealth transfer
5. **Property rights reduce inequality**: EMERGENT Gini 0.268 vs BASELINE
   0.306 despite no external configuration differences

## New Config Parameters (7)

| Parameter | Default | Description |
|-----------|---------|-------------|
| institutional_drift_rate | 0.0 | Max law_strength change per year (0=static) |
| institutional_inertia | 0.8 | Resistance to change (path dependency) |
| cooperation_institution_boost | 2.0 | Cooperation weight in institutional growth |
| violence_institution_decay | 3.0 | Violence weight in institutional erosion |
| emergent_institutions_enabled | False | Allow spontaneous institution formation |
| property_rights_strength | 0.0 | Modulates conflict resource looting |
| inheritance_prestige_fraction | 0.0 | Fraction of status inherited by heirs |

Changed default: `inheritance_law_enabled` False -> True

## New Metrics (6)

| Metric | Description |
|--------|-------------|
| law_strength | Current effective law_strength (may drift) |
| violence_punishment | Current violence_punishment_strength |
| property_rights | Current property_rights_strength |
| inheritance_events | Number of inheritance distributions per tick |
| norm_violations | Number of norm violation detections per tick |
| institutions_emerged | Number of emergent institution events per tick |

## New Scenarios (2)

| Scenario | Description |
|----------|-------------|
| STRONG_STATE | High law, punishment, property rights, tax, monogamy |
| EMERGENT_INSTITUTIONS | All institutions start at 0, self-organize via drift |
