# SIMSIV — Deep Dive 02: Resource Model — Design Decisions

## Summary

DD02 rewrites the resource engine to produce realistic inequality (Gini 0.30-0.50),
make aggression costly, amplify cooperation networks, link mating structure to
resource inequality, and fix the RESOURCE_SCARCITY population collapse.

## Design Decisions

### A. Resource Dimensionality
**Decision**: Keep two-dimensional (survival + status), tightly coupled.
- Survival resources: zero-sum-ish finite pool per tick
- Status resources: accumulate with decay (0.7 retention), amplify survival acquisition
- Status amplifies competitive weight for survival resources (0.25 weight)
- No direct conversion: status is social capital, not spendable wealth

### B. Acquisition Function
**Formula**: 8-phase resource engine.

**Competitive weight per agent**:
```
raw = intelligence*0.25 + status*0.25 + experience*0.15 + wealth^0.7*0.15 + network*0.05
adjusted = raw * (1.0 - aggression * penalty)
final = max(0.01, adjusted) ^ 3   # cubed for amplification
```

Key factors:
- Intelligence (0.25): core productivity driver
- Status (0.25): social capital amplifies resource access
- Experience (0.15): age/50, capped at 50 years
- Wealth (0.15): diminishing returns via power 0.7 (soft ceiling)
- Network (0.05/ally, max 5): cooperation clusters gain competitive advantage
- **Aggression penalty**: multiplicative (1 - agg*0.3), fighters are less efficient producers
- **Cube power**: stronger amplification than v1's square, pushes Gini from 0.25 to 0.33

Distribution split: 25% equal floor / 75% competitive (was 40/60 in v1).

### C. Inheritance Model
**Decision**: Inheritance stays in institutions engine (unchanged from v1).
New parental investment mechanism in resource engine creates the mating-inequality link:
- Parents pay `child_investment_per_year` (0.5) per dependent child per year
- Males scale investment by `paternity_confidence` when infidelity is enabled
- More children = higher resource drain = fitness cost for profligate breeders
- Creates differentiation: ELITE_POLYGYNY men drain resources on many offspring

### D. Redistribution / Taxation
**Decision**: Implemented, gated by institutional strength.
- `tax_rate` (default 0): fraction taken from top quartile earners
- Effective tax = `tax_rate * law_strength` (no governance = no enforcement)
- Redistributed equally to bottom quartile
- Default OFF — available for institutional deep dive experiments

### E. Resource Shocks and Scarcity
**Decision**: Softer scarcity model with configurable severity.
- `scarcity_severity` (default 0.6): resource multiplier during scarcity (was hardcoded 0.4)
- Subsistence floor (`subsistence_floor`, default 1.0): minimum resources after all calculations
- RESOURCE_SCARCITY scenario: abundance 0.6, severity 0.55, floor 2.5, events 10%/yr
- **Result**: Population sustains at 400-600 (was collapsing to ~30)

### F. Resource and Mate Value Interaction
**Decision**: No change to mate_value formula.
Resources already contribute 0.15 weight to mate_value. The new resource engine
creates natural differentiation through the competitive layer, which feeds into
mate_value via the resource component. Context-dependent female choice weights
(scarcity → more resource emphasis) deferred to mating deep dive.

### G. Wealth Ceiling
**Decision**: Soft ceiling via three mechanisms:
1. Diminishing returns: wealth component uses power 0.7 (rich get less marginal benefit)
2. Elite privilege cap: additive bonus capped at 2x per-agent share
3. Subsistence floor: minimum guarantee prevents complete destitution

## New Mechanisms

### Kin Trust Maintenance (Phase 0)
Parents and dependent children build mutual trust (+0.02/yr) through daily interaction.
This bootstraps cooperation networks organically through reproduction, solving the
chicken-and-egg problem where networks required pre-existing allies.
- Average network size grew from 0.5 to 3.3 allies
- Creates natural kin-based cooperation clusters

### Child Investment (Phase 3)
Parents pay resource cost per dependent child per year. Creates mating-resource
inequality link: agents with more children pay more. Key mechanism:
- Males with paternity uncertainty invest less (scaled by paternity_confidence)
- Creates tradeoff between reproduction quantity and resource quality
- Links mating structure (polygyny → more children) to resource drain

## Config Parameters Added (12 new)
| Parameter | Default | Purpose |
|---|---|---|
| resource_equal_floor | 0.25 | Fraction of survival pool as equal share |
| resource_decay_rate | 0.5 | Year-to-year resource retention |
| aggression_production_penalty | 0.3 | Competitive weight penalty for aggression |
| cooperation_network_bonus | 0.05 | Competitive weight bonus per ally |
| cooperation_sharing_rate | 0.08 | Max fraction shared with allies |
| cooperation_trust_threshold | 0.5 | Min trust to count as ally |
| cooperation_min_propensity | 0.25 | Min cooperation to participate |
| wealth_diminishing_power | 0.7 | Exponent for wealth diminishing returns |
| subsistence_floor | 1.0 | Minimum resources guarantee |
| tax_rate | 0.0 | Fraction taken from top earners |
| child_investment_per_year | 0.5 | Resource cost per dependent child |
| scarcity_severity | 0.6 | Resource multiplier during scarcity |

## Metrics Added (3 new)
| Metric | Description |
|---|---|
| resource_top10_share | Fraction of total resources held by top 10% |
| cooperation_network_size | Average # of trusted allies per living agent |
| resource_transfers | Cooperation sharing events per tick |

## Validation Results (3 seeds, 200yr, 500 pop)
| Scenario | Gini (v1) | Gini (DD02) | Violence | Pop |
|---|---|---|---|---|
| FREE_COMPETITION | 0.237 | **0.335** | 0.057 | 904 |
| ELITE_POLYGYNY | 0.411 | **0.468** | 0.064 | 830 |
| ENFORCED_MONOGAMY | ~0.237 | **0.328** | 0.036 | 1033 |
| RESOURCE_SCARCITY | (collapsed) | **0.283** | 0.057 | 609 |

Aggression-cooperation signal at year 200:
- High aggression quartile: 2.8 resources, 0.8 offspring, 28% bonded
- Low aggression quartile: 3.4 resources, 1.0 offspring, 32% bonded
- High cooperation quartile: 3.3 resources, 0.885 status
- Low cooperation quartile: 3.1 resources, 0.818 status
