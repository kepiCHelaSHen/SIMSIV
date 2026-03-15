# SIMSIV — PROMPT: DEEP DIVE 19 — MIGRATION DYNAMICS
# File: D:\EXPERIMENTS\SIM\prompts\deep_dive_19_migration.md
# Use: Send to Claude after DD18 is complete
# Priority: PHASE C, Sprint 12

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are doing Deep Dive 19 on the SIMSIV migration model.

Before doing ANYTHING, read:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\models\agent.py
  4. D:\EXPERIMENTS\SIM\models\society.py (inject_migrants — current emergency only)
  5. D:\EXPERIMENTS\SIM\config.py
  6. D:\EXPERIMENTS\SIM\STATUS.md

Currently the only population movement is emergency migrant injection to prevent
extinction — random agents appear with population-derived traits when the band
falls below min_viable_population. There is no voluntary migration driven by
agent motivations. This is a major gap: migration historically drives gene flow,
cultural diffusion, demographic change, and is the primary mechanism by which
bands exchange people. Within the band-level simulation, voluntary emigration
and immigration between an implicit pool of "other bands" must be modeled.

Note: full inter-band migration (individual agents actually moving between named
bands on a map) is a v2 feature. This deep dive models voluntary migration to/from
an implicit external pool — the world outside this band — to capture gene flow
and cultural diffusion at the band level without requiring the map layer.

================================================================================
DEEP DIVE 19: MIGRATION DYNAMICS
================================================================================

CORE CONCEPT:
  The band exists within a larger world. Occasionally:
  - Agents leave the band (emigration) — motivated by push factors
  - New agents arrive from outside (immigration) — motivated by pull factors
  - Both bring genetic and cultural material

  The "external world" is modeled as an implicit pool with configurable
  trait distributions — not a specific named band, just "elsewhere."

QUESTIONS TO RESOLVE AND IMPLEMENT:

A. EMIGRATION — WHY AGENTS LEAVE

  Push factors (increase emigration probability):
  - Resource stress: current_resources < emigration_resource_threshold
  - Social exclusion: reputation < emigration_reputation_threshold (ostracized)
  - Mating failure: adult male, unmated for N consecutive years, high status_drive
    (young males leaving to find mates elsewhere — documented in ethnography)
  - Conflict loser: agent with high conflict_cooldown + high resource loss
  - Subordination: repeatedly losing to same dominant agents
  - Overcrowding: population > carrying_capacity threshold

  Emigration probability formula:
  p_emigrate = base_emigration_rate
               + resource_stress_weight * max(0, threshold - resources)
               + mating_failure_weight * (1 if unmated_years > N else 0)
               + ostracism_weight * (1 if reputation < threshold else 0)
               + overcrowding_weight * max(0, pop/carrying_capacity - 0.9)

  Who emigrates:
  - Young males (15-30) most likely to emigrate for mating reasons
  - Any agent can emigrate for resource reasons
  - Bonded agents with children are much less likely to emigrate
    (family anchor: emigration_family_anchor multiplier reduces probability)
  - Emigrating agent takes their traits, leaves their relationships

B. IMMIGRATION — WHY AGENTS ARRIVE

  Pull factors (increase immigration probability):
  - Band has surplus resources (resource_level > immigration_resource_threshold)
  - Band has low population relative to carrying capacity
  - Band has high cooperation index (welcoming reputation)
  - Band has mating opportunities (high unmated female percentage)

  Immigration probability formula:
  p_immigrate = base_immigration_rate
                * resource_surplus_factor
                * (1 + cooperation_index * 0.5)
                * population_vacancy_factor

  Who arrives:
  - Trait distribution of immigrants: pulled from an external pool
    The external pool has configurable trait distribution:
    Option A: population_mean — immigrants match current band average
    Option B: external_mean — immigrants from a "different culture"
              with configurable trait offsets (e.g., more aggressive outside world)
    Option C: random uniform — strangers from unknown backgrounds

  Immigrant social integration:
  - Arrive with trust = 0.4 toward all existing members (stranger, not enemy)
  - Arrive with no faction membership (factionless until integrated)
  - Integration rate: builds trust at DD07 rates through interaction
  - High emotional_intelligence immigrants integrate faster
  - High conformity_bias immigrants adopt local norms faster

C. GENE FLOW EFFECTS
  Migration is the primary mechanism for maintaining genetic diversity.
  Without migration, isolated bands drift toward homogeneity.
  With migration, external alleles enter the population.

  This is especially important for:
  - Preventing fixation of extreme traits (aggression → 0 or → 1)
  - Maintaining rare mutation diversity
  - Modeling real pre-state gene flow patterns
    (hunter-gatherer bands exchanged ~10-20% of members per generation)

D. CULTURAL DIFFUSION EFFECTS
  Immigrants carry their trait values into the new band.
  If immigrant traits differ from host band average, this creates:
  - Gradual trait mean shift (if many immigrants)
  - Increased trait variance (immigrants add diversity)
  - Potential faction formation around cultural clusters
    (immigrants with different backgrounds may form their own faction)
  - conformity_bias moderates how fast immigrants adopt local norms

E. TRACKING MIGRATION
  New agent fields:
  - origin_band_id: int = 0 — 0 = founding member, >0 = immigrant from that band
    (For band-level sim: 0 = native, 1 = immigrant from external pool)
  - immigration_year: int = None — year they arrived
  - generation_in_band: int — how many generations since immigration event
    in their lineage (0 = immigrant themselves, 1 = child of immigrant, etc.)

  This enables:
  - Tracking assimilation over generations
  - Measuring cultural integration speed
  - Identifying persistent immigrant subcultures

F. SEASONAL AND STRESS MIGRATION
  Migration rates should vary with conditions:
  - Scarcity events: emigration rate spikes, immigration rate falls
  - Epidemic events: emigration spikes (fleeing disease)
  - Post-conflict: defeated faction members more likely to emigrate
  - Seasonal: more migration in resource-abundant seasons

G. METRICS
  New metrics:
  - emigration_count: agents leaving per year
  - immigration_count: agents arriving per year
  - immigrant_fraction: fraction of living population who are immigrants
  - avg_generation_in_band: cultural integration depth
  - trait_import_delta: mean trait difference between immigrants and band avg
    (measures cultural divergence of incoming migrants)

================================================================================
DELIVERABLES
================================================================================

1. docs/deep_dive_19_migration.md — design decisions
2. models/agent.py — origin_band_id, immigration_year, generation_in_band fields
3. models/society.py — emigration and immigration processing methods
4. simulation.py — migration step in tick loop (after mortality, before institutions)
5. config.py additions — migration parameters
6. metrics/collectors.py — 5 new migration metrics
7. DEV_LOG.md entry
8. CHAIN_PROMPT.md + STATUS.md update

================================================================================
NEW CONFIG PARAMETERS
================================================================================

migration_enabled: bool = True
base_emigration_rate: float = 0.005          # annual base emigration probability per agent
base_immigration_rate: float = 0.008         # annual base immigration probability (band level)
emigration_resource_threshold: float = 3.0   # below this resources → push factor
emigration_reputation_threshold: float = 0.2 # below this reputation → push factor
emigration_unmated_years: int = 5            # years unmated before mating-push emigration
emigration_family_anchor: float = 0.3        # multiplier reducing emigration if bonded+children
immigration_resource_threshold: float = 8.0  # above this resources → pull factor
immigrant_trait_source: str = "population_mean"  # "population_mean", "external", "random"
external_trait_aggression_offset: float = 0.0   # trait offset for "external" immigrants
immigrant_initial_trust: float = 0.4        # starting trust level toward all band members
overcrowding_emigration_threshold: float = 0.9  # fraction of carrying capacity triggering push

================================================================================
CONSTRAINTS
================================================================================

- Migration must be RARE enough not to overwhelm band identity
  (target: 1-3% population turnover per year in normal conditions)
- Immigrants must be socially plausible — not random stat blocks
- Full inter-band migration (agents moving between named bands) is v2
- The external pool is implicit — no second band object created
- Emigrating agents are removed from society.agents (they leave)
- Backward compatibility: migration_enabled=False = current behavior
- Run validation: trait diversity should increase slightly with migration enabled
