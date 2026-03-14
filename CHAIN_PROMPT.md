# SIMSIV — CHAIN PROMPT MASTER FILE
# Simulation of Intersecting Social and Institutional Variables
# Root: D:\EXPERIMENTS\SIM
# Last Updated: 2026-03-13 | Session 001

================================================================================
PURPOSE OF THIS FILE
================================================================================

This is the LIVING MASTER DOCUMENT for SIMSIV development.
Pass this file in full at the start of every Claude session.

It contains:
  - All confirmed design decisions (authoritative)
  - Phase chain prompts (copy-paste ready)
  - Full question log with answers
  - File tree (target state)
  - Change log

If this file and any other file conflict, THIS FILE WINS.
Update this file whenever a design decision is locked in.

================================================================================
PROJECT IDENTITY
================================================================================

Name:       SIMSIV
Full name:  Simulation of Intersecting Social and Institutional Variables
Location:   D:\EXPERIMENTS\SIM\
Language:   Python 3.11+
Status:     PRE-SKELETON — Design phase complete, implementation not yet started

Purpose:
  Model how human social structures may emerge from first-principles interactions
  among reproduction, resource competition, status seeking, cooperation, jealousy,
  violence risk, pair bonding, and institutional constraints.

  This is a sandbox for DISCOVERY. Not political. Not moralizing.
  Interesting outcomes must EMERGE from rules — never be hardwired.

================================================================================
CONFIRMED DESIGN DECISIONS
================================================================================

--- SCALE ---
  Population size:       500 agents (default), scalable to 1000+
  Generations:           100 (default), no hard ceiling
  Time step:             Annual tick (1 year per simulation step)
  Runtime target:        No ceiling — maximize richness, optimize later
  Random seed:           Supported — all runs reproducible with seed
  Baseline run:          Configurable via CLI args and YAML config

--- AGENT MODEL ---

  Heritable traits (parent → offspring blend + Gaussian noise σ=0.05):
    aggression_propensity      float [0.0-1.0]  tendency toward conflict
    cooperation_propensity     float [0.0-1.0]  tendency toward alliance
    attractiveness_base        float [0.0-1.0]  baseline physical mate value
    status_drive               float [0.0-1.0]  motivation to seek dominance
    risk_tolerance             float [0.0-1.0]  willingness to take risks
    jealousy_sensitivity       float [0.0-1.0]  trigger threshold for jealousy
    fertility_base             float [0.0-1.0]  baseline reproductive capacity
    intelligence_proxy         float [0.0-1.0]  resource acquisition efficiency

  Non-heritable traits (earned/contextual, reset or built each lifecycle):
    social_trust               float [0.0-1.0]  generalized trust in others
    reputation                 float [0.0-1.0]  public standing score
    health                     float [0.0-1.0]  current health (decays with age)
    age                        int   years alive
    current_resources          float             survival + status wealth
    current_status             float             achieved dominance rank
    pair_bond_id               int or None       id of current mate
    offspring_ids              list[int]         ids of living offspring
    reputation_ledger          dict[int, float]  trust score per known agent

  Dynamic computed properties:
    mate_value = f(health, current_status, current_resources, age)
    is_fertile() = age within reproductive window AND health > threshold
    is_alive() = health > 0 AND age < max_lifespan

  Decision model:
    Hybrid probabilistic + utility tiebreaker
    Agents weigh options by probability weights, break ties by utility calc

  Memory model:
    Lightweight reputation ledger: dict mapping agent_id → trust_score
    Updated after every direct interaction (cooperation, conflict, mating)
    Enables emergent in-group/out-group dynamics

--- MATING SYSTEM ---
  Default (v1 skeleton):   Unrestricted competition — null hypothesis baseline
  Female choice:           Probabilistic weighted by mate_value
  Male competition:        Status + aggression weighted probabilistic contest
  Pair bond strength:      Configurable — affects dissolution rate
  Pair bond dissolution:   Probabilistic — rate configurable
  All variants:            Enforced monogamy, elite polygyny, high female
                           choice — implemented as experimental overlays
  Deep dive:               Mating = Phase B Sprint 1 priority

--- RESOURCE MODEL ---
  Dimensionality:          Two-dimensional (survival_resources + status_resources)
  Acquisition:             Status + intelligence scaled, env abundance modulated
  Inheritance:             Configurable (default: equal split to children)
  Ceiling:                 No hard cap in v1 (soft diminishing returns)
  Redistribution:          Configurable taxation parameter (default: off)
  Deep dive:               Resources = Phase B Sprint 2 priority

--- CONFLICT MODEL ---
  Default triggers:        Jealousy, resource pressure, status challenge,
                           retaliation memory, random stochastic
  Outcome resolution:      Probabilistic weighted by aggression + status
  Costs:                   Configurable — resources, status, health, death risk
  Institutional suppression: law_strength parameter modulates probability
  Deep dive:               Conflict = Phase B Sprint 3 priority

--- OFFSPRING AND HOUSEHOLD ---
  Child survival factors:  Parental resources, pair bond stability,
                           kin network support, random mortality, env stress
  Offspring trait model:   Blend of both parents + Gaussian mutation (σ=0.05)
  Reproductive window:     Age configurable (default 15-45 female, 15-65 male)
  Growth to agent:         Offspring enter pool at birth, become fertile at config age
  Paternal investment:     Separable from pair bond status (configurable)
  Deep dive:               Household = Phase B Sprint 6 priority

--- INSTITUTIONS ---
  v1 model:                Toggle-based with continuous strength (0.0-1.0)
  Institutional drift:     Institutions can strengthen/erode from agent outcomes
  v1 institutions:         Monogamy norm, violence punishment, inheritance law,
                           pair bond enforcement, elite privilege multiplier
  Deep dive:               Institutions = Phase B Sprint 5 priority

--- OUTPUT AND METRICS ---
  Per-run outputs:
    metrics.csv              one row per year, all metrics
    events.csv               all logged events
    final_agents.csv         agent states at run end
    summary.json             key stats, config, seed, version
    charts/                  all PNGs

  Key metrics:
    population_size, births, deaths
    resource_gini, status_gini
    reproductive_skew (offspring gini)
    unmated_male_pct, unmated_female_pct
    violence_rate (conflicts / population)
    pair_bond_stability_pct
    child_survival_rate
    avg_lifespan
    elite_repro_advantage (top 10% / bottom 10%)
    civilization_stability_index (CSI) — composite
    mating_inequality_index (MII) — gini of male offspring
    social_cohesion_index (SCI) — composite

  Comparison:              All experimental runs auto-compared to FREE_COMPETITION
                           baseline

--- PHILOSOPHY ---
  Calibration target:      Loosely calibrated to anthropological patterns
  Hypothesis priority:     Monogamy vs unmated male violence first
  Spatial model:           Non-spatial in v1 (proximity ignored)
  Sex ratio:               Fixed 50/50 in v1 (configurable later)
  Multi-tribe:             v2 feature

================================================================================
DEVELOPMENT STRATEGY
================================================================================

PHASE A — SKELETON BUILD (current priority):
  Goal: working end-to-end simulation with defensible v1 defaults
  Produces: interesting emergent output across 100 years
  All subsystems functional, all outputs generated
  No deep optimization yet

PHASE B — DEEP DIVE CHAINS (after skeleton verified):
  Each subsystem gets its own dedicated chain prompt
  Order:
    1. Mating system         → prompts/deep_dive_01_mating.md
    2. Resource model        → prompts/deep_dive_02_resources.md
    3. Conflict model        → prompts/deep_dive_03_conflict.md  [TBD]
    4. Trait inheritance     → prompts/deep_dive_04_genetics.md  [TBD]
    5. Institutions          → prompts/deep_dive_05_institutions.md [TBD]
    6. Offspring/household   → prompts/deep_dive_06_household.md [TBD]
    7. Memory/reputation     → prompts/deep_dive_07_reputation.md [TBD]

================================================================================
PROMPT LIBRARY — QUICK REFERENCE
================================================================================

  prompts/phase1_design.md          → Phase 1: System Design
  prompts/phase2_skeleton.md        → Phase 2: Skeleton Implementation
  prompts/phase3_experiments.md     → Phase 3: Experiment Framework
  prompts/phase4_roadmap.md         → Phase 4: Roadmap and Validation
  prompts/deep_dive_template.md     → Template for any deep dive
  prompts/deep_dive_01_mating.md    → Mating system deep dive
  prompts/deep_dive_02_resources.md → Resource model deep dive
  prompts/iteration_template.md     → Any targeted change or feature
  prompts/debug_template.md         → Bug diagnosis and fix

================================================================================
PHASE CHAIN PROMPTS (INLINE)
================================================================================

To execute any phase, copy the prompt from the prompts/ directory.
Prompts are stored separately to keep this file readable.
Always read this CHAIN_PROMPT.md FIRST in every session.

================================================================================
FILE TREE — TARGET STATE
================================================================================

D:\EXPERIMENTS\SIM\
│
├── CHAIN_PROMPT.md              ← THIS FILE — read first every session
├── README.md
├── requirements.txt
├── main.py
├── config.py
│
├── devlog\
│   └── DEV_LOG.md               ← all session logs, every decision
│
├── prompts\                     ← all Claude prompts, copy-paste ready
│   ├── phase1_design.md
│   ├── phase2_skeleton.md
│   ├── phase3_experiments.md
│   ├── phase4_roadmap.md
│   ├── deep_dive_template.md
│   ├── deep_dive_01_mating.md
│   ├── deep_dive_02_resources.md
│   ├── iteration_template.md
│   └── debug_template.md
│
├── artifacts\                   ← permanent record of important outputs
│   ├── design\                  ← design docs, memos, specs
│   ├── charts\                  ← significant charts worth keeping
│   └── exports\                 ← JSON summaries, key CSVs
│
├── docs\                        ← generated design documents
│   ├── design_memo.md
│   ├── rules_spec.md
│   ├── assumptions.md
│   ├── feature_split.md
│   ├── roadmap_v2_v3.md
│   ├── validation_strategy.md
│   ├── architecture_expansion.md
│   ├── agent_design_notes.md
│   ├── sprint_next.md
│   └── deep_dive_*.md           ← one per completed deep dive
│
├── models\
│   ├── __init__.py
│   ├── agent.py
│   ├── environment.py
│   └── society.py
│
├── engines\
│   ├── __init__.py
│   ├── mating.py
│   ├── resources.py
│   ├── conflict.py
│   ├── reproduction.py
│   └── institutions.py
│
├── metrics\
│   ├── __init__.py
│   └── collectors.py
│
├── experiments\
│   ├── __init__.py
│   ├── scenarios.py
│   ├── runner.py
│   └── summarizer.py
│
├── visualizations\
│   ├── __init__.py
│   └── plots.py
│
└── outputs\                     ← all run outputs (gitignore this)
    ├── runs\                    ← timestamped run directories
    ├── charts\                  ← latest charts
    └── reports\                 ← experiment reports

================================================================================
DESIGN Q&A — ANSWER LOG
================================================================================

Q1:  Population size?
     ANSWERED: 500 default, scalable to 1000+, maximize richness

Q2:  Generations?
     ANSWERED: 100+ default, no ceiling

Q3:  Time step?
     ANSWERED: Annual tick for v1

Q4:  Runtime target?
     ANSWERED: No ceiling — kill the compute

Q5:  Heritable traits?
     ANSWERED: YES — 8 core traits (see agent model above)

Q6:  Trait mutation?
     ANSWERED: YES — Gaussian noise σ=0.05 per heritable trait

Q7:  Decision model?
     ANSWERED: Hybrid probabilistic + utility tiebreaker

Q8:  Agent memory?
     ANSWERED: YES — reputation ledger per agent pair

Q9:  Trait representation?
     ANSWERED: Continuous float [0.0-1.0]

Q10: Mate value model?
     ANSWERED: Dynamic — f(health, status, resources, age)

Q11: Default mating system?
     ANSWERED: Unrestricted competition (null hypothesis)

Q12: Pair bond persistence?
     ANSWERED: Configurable dissolution rate (default moderate)

Q13: Infidelity model?
     ANSWERED: Yes — implemented in mating deep dive (DD01)

Q14: Female choice model?
     ANSWERED: Probabilistic weighted, configurable strength slider

Q15: Homosexual pair bonding?
     ANSWERED: Optional toggle, disabled by default, v1 optional

Q16: Widowhood?
     ANSWERED: Configurable mourning period then re-entry to pool

Q17: Resource dimensionality?
     ANSWERED: Two-dimensional (survival + status)

Q18: Resource acquisition?
     ANSWERED: Status + intelligence scaled, env modulated

Q19: Inheritance model?
     ANSWERED: Configurable (default equal split)

Q20: Wealth ceiling?
     ANSWERED: No hard cap, soft diminishing returns

Q21: Redistribution?
     ANSWERED: Configurable taxation parameter, default off

Q22: Conflict triggers?
     ANSWERED: All five — jealousy, resource, status, retaliation, random

Q23: Conflict outcomes?
     ANSWERED: Probabilistic weighted

Q24: Conflict costs?
     ANSWERED: Configurable mix of resources, status, health, death

Q25: Coalition fighting?
     ANSWERED: v2 feature — architecture must support it

Q26: Institutional conflict suppression?
     ANSWERED: YES — law_strength parameter (0.0-1.0)

Q27: Child survival factors?
     ANSWERED: All five — resources, bond stability, kin, random, env

Q28: Paternal investment?
     ANSWERED: Separable from pair bond status (configurable)

Q29: Orphaned children?
     ANSWERED: Reduced survival probability, kin absorption optional

Q30: Children grow up?
     ANSWERED: YES — enter pool at birth, fertile at config age (default 15)

Q31: Institution model?
     ANSWERED: Hybrid — toggle-based + can drift from agent outcomes

Q32: v1 institutions?
     ANSWERED: Monogamy norm, violence punishment, inheritance law,
               pair bond enforcement, elite privilege multiplier

Q33: Institutional strength variable?
     ANSWERED: YES — continuous 0.0-1.0

Q34: Cultural spread of institutions?
     ANSWERED: Phase B Sprint 5 — conformity-based spread

Q35: Key metrics?
     ANSWERED: Full list in OUTPUT section above

Q36: Output format?
     ANSWERED: CSV + PNG charts + narrative text summary

Q37: Auto-compare to baseline?
     ANSWERED: YES — all runs compared to FREE_COMPETITION

Q38: Calibration target?
     ANSWERED: Loosely calibrated to anthropological patterns

Q39: Fun mode?
     ANSWERED: YES — live progress output during runs (year + key stats)

Q40: First hypotheses to test?
     ANSWERED: Monogamy vs unmated male violence (priority #1)

Q41: Conclusions to avoid pushing toward?
     ANSWERED: None specified — maintain discovery orientation

Q42: Multi-tribe dynamics?
     ANSWERED: v2 feature — architecture must support it

Q43: Sex ratio?
     ANSWERED: Fixed 50/50 in v1, configurable later

Q44: Spatial component?
     ANSWERED: Non-spatial in v1

Q45: Reproductive age parameters?
     ANSWERED: YES — fully configurable (default 15-45F, 15-65M)

================================================================================
CHANGE LOG
================================================================================

2026-03-13 | Session 001 | DESIGN + SCAFFOLDING
  - Project initiated at D:\EXPERIMENTS\SIM
  - Full brief reviewed
  - CHAIN_PROMPT.md v1 created
  - 45 design questions posed
  - Design Q&A session — all 45 questions answered
  - All decisions locked into CONFIRMED DECISIONS section
  - Full directory scaffold created
  - DEV_LOG.md initialized
  - Prompt library created (8 prompt files)
  - CHAIN_PROMPT.md updated to v2 (this file)

NEXT SESSION OBJECTIVE:
  Execute Phase 1 using prompts/phase1_design.md
  Produce: design_memo.md, rules_spec.md, assumptions.md, feature_split.md

================================================================================
END OF CHAIN PROMPT
================================================================================
