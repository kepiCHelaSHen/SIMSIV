# SIMSIV — PROMPT: PHASE 2 — SKELETON IMPLEMENTATION
# File: D:\EXPERIMENTS\SIM\prompts\phase2_skeleton.md
# Use: Paste this entire prompt to Claude to execute Phase 2

================================================================================
CONTEXT INJECTION — READ FIRST
================================================================================

You are implementing SIMSIV — Simulation of Intersecting Social and
Institutional Variables. This is a Python-based emergent social simulation
sandbox modeling how human social structures emerge from first-principles.

Before doing ANYTHING, read the following files in full:
  1. D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md
  2. D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md
  3. D:\EXPERIMENTS\SIM\docs\design_memo.md
  4. D:\EXPERIMENTS\SIM\docs\rules_spec.md
  5. D:\EXPERIMENTS\SIM\docs\assumptions.md
  6. D:\EXPERIMENTS\SIM\docs\feature_split.md

These files are your specification. Code must match them exactly.

================================================================================
PHASE 2 TASK: SKELETON IMPLEMENTATION
================================================================================

Build the working Python skeleton. Every module must be functional and runnable.
This is a skeleton — not a toy. Defaults must be defensible and produce
interesting emergent output. No placeholder functions. No stub-only code.

--------------------------------------------------------------------------------
ARCHITECTURE REQUIREMENTS
--------------------------------------------------------------------------------

All files go in D:\EXPERIMENTS\SIM\

config.py
  - All tunable parameters as a Config dataclass or dict
  - YAML load/save support
  - Random seed field
  - Sensible defaults matching rules_spec.md
  - Inline comments explaining each parameter

models/__init__.py         (empty, marks package)
models/agent.py
  - Agent dataclass with ALL attributes from rules_spec.md
  - All heritable traits: aggression_propensity, cooperation_propensity,
    attractiveness_base, status_drive, risk_tolerance, jealousy_sensitivity,
    fertility_base, intelligence_proxy
  - All earned traits: social_trust, reputation, health, age,
    current_resources, current_status, pair_bond_id, offspring_ids,
    reputation_ledger (dict of agent_id -> float)
  - Dynamic mate_value property = f(health, status, resources, age)
  - Helper methods: is_fertile(), is_alive(), can_mate()
  - __repr__ for readable logging

models/environment.py
  - Environment dataclass
  - Parameters: total_resources, resource_volatility, carrying_capacity,
    mortality_pressure, climate_stress, scarcity_event_probability,
    current_season (if seasonal), abundance_multiplier
  - Method: tick() — updates environment state each year
  - Method: get_scarcity_level() -> float
  - Method: trigger_shock() — random adverse event

models/society.py
  - Society class holding list of agents + environment + institutions
  - Methods: get_living_agents(), get_mating_eligible(), get_by_id()
  - Methods: add_agent(), remove_agent(), age_all_agents()
  - Method: tick() — advances one year, calls all engines in order
  - Maintains year counter and generation counter
  - Maintains event log for this tick

engines/__init__.py        (empty)
engines/mating.py
  - MatingEngine class
  - Default: unrestricted competition
  - Female mate choice: probabilistic weighted by mate_value
  - Male competition: status + resource weighted contest
  - Pair bond formation with configurable strength
  - Pair bond dissolution with configurable probability
  - Method: run(society, config) -> list of new pair bond events

engines/resources.py
  - ResourceEngine class
  - Acquisition: status + intelligence scaled per agent
  - Environmental scarcity modifies acquisition
  - Baseline survival resources distributed to all living agents
  - Method: run(society, config) -> updates agent resources

engines/conflict.py
  - ConflictEngine class
  - Triggers: jealousy (rival mate detected), resource pressure,
    status challenge, retaliation from memory, random stochastic
  - Outcome: probabilistic weighted by aggression + status + coalition
  - Costs: configurable mix of resources, status, health, death risk
  - Institutional suppression: law_strength parameter reduces probability
  - Method: run(society, config) -> list of conflict events

engines/reproduction.py
  - ReproductionEngine class
  - Reproduction attempt if pair bond exists or unrestricted mode
  - Fertility window check (age-based)
  - Child survival: function of parental resources + bond stability + kin
  - Offspring inherits blended parent traits + Gaussian mutation (σ=0.05)
  - Offspring enters agent pool at age 0, becomes fertile at config age
  - Method: run(society, config) -> list of new Agent objects

engines/institutions.py
  - InstitutionEngine class
  - Toggle-based in v1 with continuous strength (0.0-1.0)
  - Monogamy norm enforcement
  - Violence punishment
  - Inheritance law execution
  - Method: run(society, config) -> list of institutional events
  - Method: apply_inheritance(deceased_agent, society, config)

metrics/__init__.py        (empty)
metrics/collectors.py
  - MetricsCollector class
  - Collects per-tick metrics:
      population_size, births, deaths, conflicts, pair_bonds_formed,
      pair_bonds_dissolved, resource_gini, status_gini,
      reproductive_skew (gini of offspring count),
      unmated_male_pct, unmated_female_pct,
      child_survival_rate, avg_lifespan,
      violence_rate (conflicts / population),
      avg_resources, max_resources, min_resources,
      elite_repro_advantage (top 10% repro / bottom 10% repro)
  - Method: collect(society, year) -> dict
  - Method: to_dataframe() -> pandas DataFrame
  - Method: save_csv(path)
  - Method: summary_stats() -> dict

visualizations/__init__.py (empty)
visualizations/plots.py
  - PlotEngine class
  - plot_population_over_time(df, output_path)
  - plot_resource_inequality(df, output_path) — Gini curve
  - plot_reproductive_skew(df, output_path)
  - plot_violence_rate(df, output_path)
  - plot_unmated_male_pct(df, output_path)
  - plot_child_survival(df, output_path)
  - plot_composite_dashboard(df, output_path) — 6-panel figure
  - All charts: clean style, labeled axes, title, saved as PNG

main.py
  - CLI entry point: python main.py [--config config.yaml] [--seed N]
                                    [--scenario NAME] [--years N]
                                    [--population N] [--output-dir PATH]
  - Loads config (default or from file)
  - Initializes society with random agents
  - Runs simulation loop
  - Collects metrics each tick
  - Saves CSV, charts, JSON summary, run metadata
  - Prints live progress: year counter + key stats each tick
  - Prints final summary on completion

requirements.txt
  - numpy>=1.24
  - pandas>=2.0
  - matplotlib>=3.7
  - pyyaml>=6.0
  - dataclasses (stdlib)
  - typing (stdlib)
  - argparse (stdlib)

--------------------------------------------------------------------------------
IMPLEMENTATION STANDARDS
--------------------------------------------------------------------------------

1. Every file has a module docstring explaining its purpose
2. Every class has a docstring
3. Every public method has a docstring with args and returns
4. Type hints on all function signatures
5. No magic numbers — all constants referenced from config
6. Random calls use numpy.random.Generator seeded from config.seed
7. All engines receive (society, config) and return event lists
8. Events are dicts with keys: type, year, agent_ids, description, outcome
9. Logging via Python logging module — INFO level by default
10. No circular imports — models know nothing about engines
11. Fail loudly — raise descriptive exceptions, don't silently swallow errors

--------------------------------------------------------------------------------
SIMULATION LOOP ORDER (per annual tick)
--------------------------------------------------------------------------------

Each year, in this exact order:
  1. environment.tick()          — update resources, trigger shocks
  2. resources_engine.run()      — agents acquire resources
  3. institutions_engine.run()   — apply norm enforcement
  4. mating_engine.run()         — mate search, bond formation/dissolution
  5. reproduction_engine.run()   — reproduction attempts, births
  6. conflict_engine.run()       — conflict events, costs
  7. society.age_all_agents()    — increment ages, apply mortality
  8. metrics.collect()           — record all metrics for this year
  9. log_tick_summary()          — print one-line progress to stdout

--------------------------------------------------------------------------------
BASELINE SCENARIO DEFAULTS
--------------------------------------------------------------------------------

population_size: 500
years: 100
seed: 42
mating_system: "unrestricted"
female_choice_strength: 0.6
male_competition_intensity: 0.7
pair_bond_strength: 0.5
pair_bond_dissolution_rate: 0.1
resource_abundance: 1.0
resource_volatility: 0.2
carrying_capacity: 800
mortality_base: 0.02
violence_cost_multiplier: 1.0
law_strength: 0.0
elite_privilege_multiplier: 1.0
child_dependency_years: 5
age_first_reproduction: 15
age_max_reproduction_female: 45
age_max_reproduction_male: 65
age_death_base: 60
age_death_variance: 15
mutation_rate: 0.05
inheritance_model: "equal_split"
monogamy_enforced: false
polygyny_allowed: true
max_mates_per_male: 999  (unrestricted default)

================================================================================
OUTPUT REQUIREMENTS
================================================================================

Every run produces:
  outputs/runs/[timestamp]_[seed]/
    ├── metrics.csv          (one row per year, all metrics)
    ├── events.csv           (all logged events)
    ├── final_agents.csv     (state of all agents at run end)
    ├── summary.json         (key stats, config, seed, version)
    └── charts/
        ├── population.png
        ├── resource_gini.png
        ├── reproductive_skew.png
        ├── violence_rate.png
        ├── unmated_males.png
        ├── child_survival.png
        └── dashboard.png    (6-panel composite)

================================================================================
QUALITY BAR
================================================================================

- Must run without errors: python main.py
- Must produce all output files
- Simulation must show emergent dynamics — not flat lines
- Code must be readable by a non-expert Python developer
- No TODO comments in delivered code
- No placeholder functions

================================================================================
AFTER IMPLEMENTATION
================================================================================

Update devlog: D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md with a new entry
Copy dashboard.png to: D:\EXPERIMENTS\SIM\artifacts\charts\
Copy summary.json to: D:\EXPERIMENTS\SIM\artifacts\exports\
