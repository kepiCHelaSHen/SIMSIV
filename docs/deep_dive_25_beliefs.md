# Deep Dive 25: Belief and Ideology System

## Design Decisions

### Five belief dimensions (non-heritable, culturally transmitted)
Each agent holds values on 5 belief dimensions, each a float [-1.0, +1.0]:
- **hierarchy_belief**: egalitarian (-1) ↔ hierarchical (+1)
- **cooperation_norm**: defection (-1) ↔ prosocial (+1)
- **violence_acceptability**: pacifist (-1) ↔ violence is honorable (+1)
- **tradition_adherence**: innovator (-1) ↔ conservative (+1)
- **kinship_obligation**: universalist (-1) ↔ in-group only (+1)

### Belief initialization
At maturation (age 15), beliefs are set via:
```
belief = conformity_bias * parent_avg_belief
       + (1 - conformity_bias) * trait_derived_belief
       + novelty_seeking * N(0, 0.15)
```
Trait-derived formulas:
- hierarchy = status_drive * 0.6 + dominance_score * 0.4 - 0.3
- cooperation_norm = cooperation_propensity * 0.8 + reputation * 0.2 - 0.3
- violence_acceptability = aggression_propensity * 0.7 + dominance_score * 0.3 - 0.3
- tradition_adherence = conformity_bias * 0.8 - novelty_seeking * 0.4
- kinship_obligation = jealousy_sensitivity * 0.3 + 0.2

Parent beliefs are passed at birth (via breed()) as `_parent_*` attributes.

### Belief evolution (every 3 ticks in reputation engine)
Three forces update beliefs:

**Social influence**: Neighborhood-weighted, prestige-biased.
- Weight = trust(other) * (0.4 + other.prestige_score * prestige_transmission_weight)
- Update: belief += conformity_bias * max(0.2, 1 - novelty_seeking * 0.5) * influence_rate * (avg - current)

**Experience-based**: Direct events modify beliefs:
- Conflict win: violence_acceptability += 0.03, hierarchy += 0.02, cooperation_norm -= 0.02
- Conflict loss: violence_acceptability -= 0.05
- Punishment received: violence_acceptability -= 0.04
- Leadership arbitration: cooperation_norm += 0.02

**Cultural mutation**: novelty_seeking gates random drift: N(0, novelty_seeking * 0.03) per dimension.

### Belief effects on engines

**Conflict**: violence_acceptability > 0 → +10% initiation; < 0 → -15%. Low VA → more likely third-party punisher.

**Resources**: cooperation_norm boosts sharing rate +10%. Low kinship_obligation lowers cooperation threshold for band-tier sharing.

**Mating**: High kinship_obligation amplifies endogamy preference (marry within faction).

**Institutions**: Beliefs aggregate into institutional drift:
- High cooperation_norm → accelerates law_strength growth
- High violence_acceptability → undermines punishment
- High tradition_adherence → increases institutional inertia
- High hierarchy_belief → drifts elite_privilege upward

### Ideological tension
When agents with abs(belief_diff) > 0.6 interact → distrust grows.

### Belief revolution
When any dimension's band mean shifts > 0.3 between tracking intervals → logged as revolution event.

### Dominant ideology labels
Computed from band-mean beliefs:
- Egalitarian warrior: low hierarchy + high violence
- Cooperative collective: high cooperation + low hierarchy
- Hierarchical tradition: high hierarchy + high tradition
- Innovative expansionist: low tradition + low kinship

## Config parameters
7 new parameters controlling belief system dynamics.

## Metrics
- `avg_hierarchy_belief`, `avg_cooperation_norm`, `avg_violence_acceptability`, `avg_tradition_adherence`, `avg_kinship_obligation`
- `belief_polarization`: average std across dimensions
- `dominant_ideology`: categorical label
- `belief_revolution_events`: count per tick
- `belief_fitness_correlation`: cooperation_norm vs offspring count
