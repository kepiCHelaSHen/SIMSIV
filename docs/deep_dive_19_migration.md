# Deep Dive 19: Migration Dynamics

## Design Decisions

### Emigration (push factors)
Agents leave the band when conditions are unfavorable:
- Resource stress: resources < emigration_resource_threshold (3.0)
- Social exclusion: reputation < emigration_reputation_threshold (0.2)
- Mating failure: unmated male aged 18-35 with high status_drive for 5+ years
- Overcrowding: population > 90% carrying capacity
- Family anchor: bonded agents with dependent children are 70% less likely to leave
- Children (age < 15) never emigrate alone

Emigrating agents are marked dead with cause="emigration" and removed from
partner bonds. Their traits leave the population's gene pool.

### Immigration (pull factors)
New agents arrive from an implicit external pool:
- Resource surplus: band average > immigration_resource_threshold → 1.5x rate
- Population vacancy: lower pop/capacity → higher rate
- Cooperation: higher average cooperation → more welcoming → higher rate
- Maximum 3 immigrants per tick (diminishing returns)

### Immigrant trait generation
Three modes (configurable via immigrant_trait_source):
- `population_mean`: traits drawn from current band's trait distribution
- `external`: drawn from N(0.5, 0.15) with optional aggression offset
- `random`: uniform [0, 1]

### Gene flow
Immigration maintains genetic diversity by introducing external alleles.
Without migration, isolated bands drift toward trait homogeneity.
Target: 1-3% population turnover per year under normal conditions.

### Tracking
- `origin_band_id`: 0=native, 1=immigrant
- `immigration_year`: year of arrival
- `generation_in_band`: 0=immigrant, increments for children (min of parents + 1)

## Config parameters
- `migration_enabled: bool = True`
- `base_emigration_rate: float = 0.005`
- `base_immigration_rate: float = 0.008`
- `emigration_resource_threshold: float = 3.0`
- `emigration_reputation_threshold: float = 0.2`
- `emigration_unmated_years: int = 5`
- `emigration_family_anchor: float = 0.3`
- `immigration_resource_threshold: float = 8.0`
- `immigrant_trait_source: str = "population_mean"`
- `external_trait_aggression_offset: float = 0.0`
- `immigrant_initial_trust: float = 0.4`
- `overcrowding_emigration_threshold: float = 0.9`

## Metrics
- `emigration_count`, `immigration_count`: per-tick flows
- `immigrant_fraction`: fraction of living population who are immigrants
- `avg_generation_in_band`: cultural integration depth
