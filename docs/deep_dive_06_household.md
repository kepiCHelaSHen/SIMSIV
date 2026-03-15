# SIMSIV — Deep Dive 06: Offspring and Household

## Design Decisions

### A. Childhood Development Model
**Decision: NOT IMPLEMENTED (deferred)**
- Children remain inert 0-15 (consume resources, face mortality risk)
- Nurture effects (parental traits → childhood outcomes) deferred to avoid
  double-counting with genetic inheritance
- Childhood quality → adult health is an interesting idea but adds complexity
  without clear emergent payoff in current model
- Dependency period kept at 5 years (configurable) — extending to 10-15 would
  require rebalancing resource engine child investment costs

### B. Child Mortality Model
**Decision: IMPLEMENTED — annual resource-dependent childhood mortality**
- `childhood_mortality_annual = 0.02` base annual death risk for ages 1-15
- Resource-dependent: low parental resources increase risk (factor 0.5-1.5)
- Orphan mortality multiplier: 2x base rate when no living parent
- Scarcity amplification: childhood mortality rises during scarcity events
- Grandparent survival bonus: reduces childhood mortality when grandparent alive
- Result: ~2-5 childhood deaths per year in 200-pop baseline

### C. Household Structure
**Decision: IMPLICIT — no formal household data structure**
- Existing partner_ids, offspring_ids, parent_ids are sufficient
- Formal household groups would add complexity without clear emergent benefit
- "Household" effects are captured through:
  - Parent-child kin trust (resources.py Phase 0)
  - Sibling trust growth (DD06 addition)
  - Child investment costs (resources.py Phase 3)
  - Orphan mortality penalty (mortality.py)

### D. Sibling Relationships
**Decision: IMPLEMENTED — sibling trust growth via co-living**
- `sibling_trust_growth = 0.01` annual trust growth between dependent siblings
- Siblings of the same parent who are both under dependency age build trust
- Seeds cooperation networks within family units
- No birth order effects (would require tracking order, low payoff)
- No sibling competition (resource competition already handled in Phase 3)

### E. Fertility and Birth Spacing
**Decision: IMPLEMENTED — birth interval, age decline, lifetime cap, health cost**
- `birth_interval_years = 2`: minimum years between births per female
  (models lactational amenorrhea in pre-industrial populations)
- `maternal_age_fertility_decline = 0.03`: fertility drops 3% per year past 30
  (replaces binary fertile window with gradual decline)
- `max_lifetime_births = 12`: hard cap on births per female
- `maternal_health_cost = 0.03`: health cost per birth to mother
  (cumulative — 12 births would cost 0.36 health)
- Result: avg lifetime births ~3.2, max observed ~8 (realistic for pre-industrial)

### F. Grandparent and Extended Kin Effects
**Decision: PARTIALLY IMPLEMENTED — grandparent survival bonus only**
- `grandparent_survival_bonus = 0.05`: reduces infant and childhood mortality
  when at least one maternal grandparent is alive ("grandmother hypothesis")
- Extended kin conflict deterrence already handled via cooperation networks (DD03)
- Kin group mate value bonus deferred (would need family prestige metric)

### G. Orphan Model
**Decision: IMPLEMENTED — increased mortality, no formal adoption**
- Orphan mortality multiplier: 2x base childhood mortality rate
- No formal adoption mechanism (would require complex kin search)
- Orphans still receive subsistence floor resources (resources.py Phase 8)
- Institutional orphan care (law_strength-gated) deferred to avoid complexity

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| birth_interval_years | 2 | Min years between births per female |
| childhood_mortality_annual | 0.02 | Annual death risk for children 0-15 |
| orphan_mortality_multiplier | 2.0 | Mortality multiplier for parentless children |
| grandparent_survival_bonus | 0.05 | Child survival bonus if grandparent alive |
| sibling_trust_growth | 0.01 | Annual trust growth between co-living siblings |
| max_lifetime_births | 12 | Hard cap on births per female |
| maternal_health_cost | 0.03 | Health cost per birth to mother |
| maternal_age_fertility_decline | 0.03 | Fertility decline per year past 30 |

## Metrics Added
| Metric | Description |
|--------|-------------|
| childhood_deaths | Deaths of children ages 1-15 per tick |
| orphan_deaths | Childhood deaths where child had no living parent |
| children_count | Living children (age <= 15) |
| orphan_count | Living children with no living parent |
| avg_lifetime_births | Mean births among fertile-age females |
| avg_maternal_health | Mean health of females who have given birth |

## Files Changed
- `engines/reproduction.py` — birth interval, age decline, birth cap, health cost, grandparent bonus
- `engines/mortality.py` — annual childhood mortality, orphan multiplier, grandparent bonus
- `engines/resources.py` — sibling trust growth in Phase 0
- `models/agent.py` — last_birth_year, lifetime_births fields
- `config.py` — 8 DD06 parameters
- `metrics/collectors.py` — 6 DD06 metrics

## Validation Results (200 pop, 50yr, seed=42)
- Childhood deaths: 128 total (~2-5/yr)
- Orphans: 12 among 245 children (~5%)
- Avg lifetime births: 3.17, max 8 (below cap of 12)
- Maternal health: avg 0.427 (visible health cost of reproduction)
- Population stable at ~440 (no collapse from added mortality)
