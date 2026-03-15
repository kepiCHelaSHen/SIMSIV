# SIMSIV — Deep Dive 09: Disease and Epidemic Events

## Core Design
Epidemics are sudden, clustered, and differentially lethal. They trigger
from the environment model and are processed in the mortality engine with
age/health/resource-dependent vulnerability.

## Design Decisions

### A. Epidemic Trigger
- Base probability 2%/yr (after refractory period of 20yr)
- Overcrowding multiplier: above 80% capacity, risk scales with overcrowding * 2.0
- Scarcity compounds risk: 1.5x during active scarcity (malnutrition → disease)
- Duration: 2 years peak (configurable), then subsides
- Refractory period: minimum 20yr between epidemics (susceptible population rebuilds)
- NOT implemented: distinct epidemic types (childhood vs plague vs famine fever) —
  single model with differential vulnerability captures the key dynamics

### B. Differential Vulnerability
- Children (0-10): 3x base mortality (most vulnerable)
- Elderly (55+): 2x base mortality
- Low health (<0.4): 2x multiplier
- Low resources (<3.0): 1.5x multiplier (malnutrition)
- Intelligence: mild protective effect (0.7-1.0 multiplier)
- Base lethality: 15% per epidemic year for adult population

### C. Social Consequences
- Orphan surge: handled by DD06 orphan mortality multiplier
- Inheritance cascade: existing DD05 inheritance engine handles mass deaths
- Status reshuffling: natural consequence of deaths across all strata
- NOT implemented: immunity system (adds complexity, low emergent payoff for
  single-tribe model), institutional epidemic response

### D. Immunity
- NOT IMPLEMENTED (deferred)
- Reasoning: immunity requires per-agent tracking + herd threshold math
- Single epidemic model without immunity still produces correct population dynamics
- Can be added later if epidemic patterns need more realism

### E. Calibration
Results across 5 seeds (200 pop, 100yr):
- Seed 42: 0 epidemics, final pop 487
- Seed 123: 4 epidemic years, 301 deaths, final pop 77
- Seed 456: 0 epidemics, final pop 669
- Seed 789: 2 epidemic years, 187 deaths, final pop 145
- Seed 999: 4 epidemic years, 179 deaths, final pop 178

Population variance dramatically increased — exactly the desired effect.
Epidemics are sudden shocks (116→67 in 2 years in the 100-pop test).

## Parameters Added
| Parameter | Default | Description |
|-----------|---------|-------------|
| epidemic_base_probability | 0.02 | Annual chance of epidemic starting |
| epidemic_lethality_base | 0.15 | Base mortality per epidemic year |
| epidemic_duration_years | 2 | Peak epidemic duration |
| epidemic_child_vulnerability | 3.0 | Mortality multiplier for age 0-10 |
| epidemic_elder_vulnerability | 2.0 | Mortality multiplier for age 55+ |
| epidemic_health_threshold | 0.4 | Below this health = extra vulnerable |
| epidemic_refractory_period | 20 | Min years between epidemics |
| epidemic_overcrowding_multiplier | 2.0 | Above 80% capacity → scaled risk |

## Metrics Added
| Metric | Description |
|--------|-------------|
| epidemic_active | 1 if epidemic active this year, 0 otherwise |
| epidemic_deaths | Deaths attributed to epidemic this tick |

## Files Changed
- `models/environment.py` — epidemic state, trigger logic, overcrowding/scarcity compound
- `engines/mortality.py` — epidemic mortality with differential vulnerability
- `config.py` — 8 DD09 parameters
- `metrics/collectors.py` — 2 DD09 metrics
