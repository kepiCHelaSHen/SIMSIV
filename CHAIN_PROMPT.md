# SIMSIV — CHAIN PROMPT MASTER FILE
# Simulation of Intersecting Social and Institutional Variables
# Root: D:\EXPERIMENTS\SIM
# Last Updated: 2026-03-15 | Phase G — Dashboard overhaul (in progress)

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
Status:     PHASE G — Dashboard overhaul in progress. Band simulator v1.0
            calibrated and validated. Scenario experiments running.
            Publication plan active — gene-culture coevolution claim.

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
  Generations:           200 (default), no hard ceiling
  Time step:             Annual tick (1 year per simulation step)
  Runtime target:        No ceiling — maximize richness, optimize later
  Random seed:           Supported — all runs reproducible with seed
  Baseline run:          Configurable via CLI args and YAML config

--- AGENT MODEL ---

  Heritable traits (35 total, h²-weighted inheritance + mutation σ=0.05):

  PHYSICAL PERFORMANCE (6):
    physical_strength      h²=0.60  force output, combat
    endurance              h²=0.50  sustained capacity, foraging
    physical_robustness    h²=0.50  damage absorption
    pain_tolerance         h²=0.45  flee threshold modifier
    longevity_genes        h²=0.25  lifespan extension
    disease_resistance     h²=0.40  epidemic resistance

  COGNITIVE (4):
    intelligence_proxy     h²=0.65  resource acquisition efficiency
    emotional_intelligence h²=0.40  trust/gossip effectiveness
    impulse_control        h²=0.50  aggression→action gate
    conscientiousness      h²=0.49  skill maintenance, compliance

  TEMPORAL (1):
    future_orientation     h²=0.40  time horizon — storage, institutions

  PERSONALITY (4):
    risk_tolerance         h²=0.48  willingness to take risks
    novelty_seeking        h²=0.40  exploration tendency
    anxiety_baseline       h²=0.40  threat sensitivity, flee boost
    mental_health_baseline h²=0.40  stress resilience, plasticity gate

  SOCIAL ARCHITECTURE (9):
    aggression_propensity  h²=0.44  tendency toward conflict
    cooperation_propensity h²=0.40  tendency toward alliance
    dominance_drive        h²=0.50  active dominance hierarchy seeking
    group_loyalty          h²=0.42  kin selection, sacrifice for group
    outgroup_tolerance     h²=0.40  openness to strangers
    empathy_capacity       h²=0.35  altruism radius
    conformity_bias        h²=0.35  norm adoption speed
    status_drive           h²=0.50  motivation to seek dominance
    jealousy_sensitivity   h²=0.45  trigger for jealousy-driven conflict

  REPRODUCTIVE BIOLOGY (5):
    fertility_base                  h²=0.50  baseline reproductive capacity
    sexual_maturation_rate          h²=0.60  age at first reproduction variance
    maternal_investment             h²=0.35  quality vs quantity offspring tradeoff
    paternal_investment_preference  h²=0.45  good genes vs good dad preference
    attractiveness_base             h²=0.50  baseline physical mate value

  PSYCHOPATHOLOGY SPECTRUM (6):
    psychopathy_tendency   h²=0.50  exploiter strategy (default 0.2)
    mental_illness_risk    h²=0.60  heritable psychiatric condition risk
    cardiovascular_risk    h²=0.50  heritable cardiovascular risk
    autoimmune_risk        h²=0.40  heritable immune dysfunction risk
    metabolic_risk         h²=0.45  heritable metabolic risk
    degenerative_risk      h²=0.35  heritable degenerative risk

  Non-heritable traits (earned/contextual, reset or built each lifecycle):
    reputation                 float [0.0-1.0]  public standing score
    health                     float [0.0-1.0]  current health (decays with age)
    age                        int   years alive
    current_resources          float             subsistence resources (DD21)
    current_tools              float             durable tools (DD21)
    current_prestige_goods     float             social-value goods (DD21)
    prestige_score             float             earned via cooperation/skill (DD08)
    dominance_score            float             earned via conflict/intimidation (DD08)
    current_status             float             computed: 0.6*prestige + 0.4*dominance
    partner_ids                list[int]         current mate(s)
    offspring_ids              list[int]         ids of living offspring
    reputation_ledger          dict[int, float]  trust score per known agent
    faction_id                 int or None       emergent faction membership (DD14)
    neighborhood_ids           list[int]         proximity tier contacts (DD18)
    Beliefs (DD25, 5 dims, float [-1, +1]):
      hierarchy_belief, cooperation_norm, violence_acceptability,
      tradition_adherence, kinship_obligation
    Skills (DD26, 4 domains, float [0, 1]):
      foraging_skill, combat_skill, social_skill, craft_skill
    Epigenetics (DD24):
      epigenetic_stress_load, epigenetic_generation_decay
    Medical (DD17):
      active_conditions, trauma_score, medical_history

--- MATING SYSTEM ---
  Default:             Unrestricted competition — null hypothesis baseline
  Female choice:       Probabilistic weighted by mate value
  Male competition:    Status + aggression weighted probabilistic contest
  Pair bond strength:  Configurable — affects dissolution rate
  Bond dissolution:    Probabilistic, driven by BOTH partners' quality
  EPC:                 Extra-pair copulation with detection and paternity uncertainty
  Social vs genetic:   Children's parent_ids point to social father (Phase F fix)

--- RESOURCE MODEL ---
  Dimensionality:      Three-type (subsistence + tools + prestige goods, DD21)
  Acquisition:         8-phase engine
  Equal floor:         Configurable (default 40%)
  Cooperation:         Network bonus, sharing threshold
  Aggression penalty:  0.6 (calibrated — higher than original default)
  Inheritance:         Configurable (default equal split)
  Subsistence floor:   1.17 (calibrated)

--- CONFLICT MODEL ---
  Triggers:            Jealousy, resource, status, random baseline
  Cross-sex targeting: Enabled at 0.3× weight (Phase F fix)
  Suppression:         Institutional (law_strength), cooperation, network deterrence
  Combat:              Power = aggression + status + health + risk + resource + allies
  Subordination:       Losers enter 2yr cooldown (50% dampening)
  Phase F fix:         Bond destabilization uses partner's jealousy, not fighter's aggression

--- INSTITUTIONS ---
  Default drift:       ENABLED — drift_rate=0.01 (Phase F fix from 0.0)
  Emergent:            ENABLED by default (Phase F fix)
  Law strength:        Self-organizes from cooperation/violence balance
  Property rights:     Modulates conflict looting
  Inheritance:         Default ON (equal split)

--- CALIBRATION STATUS (CURRENT) ---
  AutoSIM Run 3:       816 experiments, ~10.5 hours (2026-03-15)
  Best score:          1.000 (all 9 metrics simultaneously in range)
  Config:              autosim/best_config.yaml
  Validation:          10 held-out seeds × 200yr × 2 independent runs
                       Mean score 0.934, 0 collapses
  Key calibrated params:
    pair_bond_dissolution_rate: 0.02
    female_choice_strength:     0.34
    base_conception_chance:     0.80
    mortality_base:             0.006
    childhood_mortality_annual: 0.054
    epidemic_lethality_base:    0.254

--- PUBLICATION PLAN ---
  Central claim:       "Institutional governance systematically reduces
                        directional selection on heritable prosocial behavioral
                        traits — providing computational evidence that institutions
                        and genes are substitutes, not complements, in human
                        social evolution."
  Paper 1:             Methods paper → JASSS or PLOS ONE
  Paper 2:             Findings paper → Evolutionary Human Sciences
  Paper 3:             Gene-culture coevolution → Evolution and Human Behavior
  AI disclosure:       "Code development aided by Claude (Anthropic); all
                        hypotheses and interpretations are the author's own."
  arXiv preprint:      After scenario experiments complete + sensitivity analysis

--- SCENARIO EXPERIMENTS (FIRST RUN — 2026-03-15) ---
  Run:    5 seeds × 200yr × 10 scenarios
  Status: COMPLETE
  Key findings:
    - ENFORCED_MONOGAMY: violence ▼37%, unmated males ▼65% vs baseline
    - STRONG_STATE: Gini ▼40%, violence ▼49%
    - EMERGENT_INSTITUTIONS: law self-organizes to 0.829 from 0.0
    - Cooperation trait IDENTICAL across all scenarios at 200yr (~0.511)
      → 500yr run required to detect trait divergence (currently running)
    - RESOURCE_SCARCITY produces highest cooperation (0.536) — stress effect
    - ELITE_POLYGYNY near-zero pop growth despite highest lifespan — excluded
      males suppress overall birth rate

  Run 2 (currently running):
    3 key scenarios (FREE_COMPETITION, STRONG_STATE, EMERGENT_INSTITUTIONS)
    10 seeds × 500yr — tests the gene-culture coevolution central claim

--- OUTPUT AND METRICS ---
  Per-run outputs:
    metrics.csv, events.csv, final_agents.csv, summary.json, charts/
  Key metrics (~130 per tick):
    population, births, deaths, resource_gini, status_gini,
    reproductive_skew, violence_rate, pair_bond_stability_pct,
    child_survival_rate, avg_lifespan, cooperation, aggression,
    intelligence, law_strength, faction_count, and more

--- PHILOSOPHY ---
  Calibration target:   Calibrated against 9 anthropological benchmarks
  Hypothesis priority:  Gene-culture coevolution — institutions vs traits
  Spatial model:        Non-spatial in v1 (proximity tiers are abstract)
  Sex ratio:            Fixed 50/50 in v1 (configurable)
  Multi-band:           v2 feature

================================================================================
DEVELOPMENT STRATEGY
================================================================================

PHASE A — SKELETON BUILD (complete):
  Working end-to-end simulation, defensible v1 defaults

PHASE B — DEEP DIVE CHAINS DD01-DD14 (complete):
  Mating, Resources, Conflict, Genetics, Institutions, Household,
  Reputation, Prestige, Disease, Seasons, Coalitions, Signaling,
  Demographics, Factions

PHASE C — DEEP DIVE CHAINS DD15-DD26 (complete):
  Extended Genomics, Developmental Biology, Medical/Pathology,
  Proximity Tiers, Migration, Leadership, Resource Types, Life Stages,
  Intelligence Audit, Epigenetics, Beliefs, Skills

PHASE D — DD27 TRAIT COMPLETION (complete):
  9 new traits (26→35 total), 35×35 PSD-verified correlation matrix

PHASE E — ENGINEERING HARDENING (complete):
  14 fixes: IdCounter, event window, partner index, logging,
  Config validation, mating_system wiring, ledger cleanup,
  dashboard split, test suite expansion

PHASE F — MODEL QUALITY FIXES (complete):
  19 fixes across all engines: cross-sex conflict, mental illness trait
  mutation, institutional drift defaults, EPC kin networks, bond
  dissolution symmetry, elite privilege ratchet, age consistency,
  status setter, storage bonuses, and more

PHASE G — DASHBOARD OVERHAUL (in progress):
  Refactor app.py into tabs/ + components/, add Beliefs tab,
  Scenario Comparison tab, Lorenz curve, survivorship curve,
  inter-faction violence matrix, bond duration histogram,
  phase portrait, epidemic bands, export panel, KPI deltas
  Prompt: prompts/dashboard_overhaul.md

PHASE H — PAPER 1 FOUNDATION (next):
  Apply best_config defaults to config.py
  Run definitive scenario experiments (10 seeds × 500yr × 6 scenarios)
  Write docs/sensitivity_analysis.md
  Draft Paper 1 (methods paper)
  Tag v1.0-band-simulator, create Zenodo archive

PHASE I — V2 CLAN SIMULATOR (after Paper 1 draft):
  Formally specify band fingerprint
  Build models/clan/ as independent module
  Write docs/v2_clan_simulator.md

================================================================================
PROMPT LIBRARY — QUICK REFERENCE
================================================================================

  prompts/phase_e_engineering_hardening.md  → Phase E fixes (executed)
  prompts/dashboard_hall_of_fame.md          → Hall of Fame feature (executed)
  prompts/dashboard_overhaul.md              → Phase G dashboard (in progress)
  prompts/deep_dive_01_mating.md .. deep_dive_27_trait_completion.md
  prompts/iteration_template.md
  prompts/debug_template.md

================================================================================
FILE TREE — CURRENT STATE
================================================================================

D:\EXPERIMENTS\SIM\
│
├── CHAIN_PROMPT.md              ← THIS FILE
├── README.md
├── STATUS.md
├── requirements.txt             (plotly, pytest added Phase E)
├── .python-version              (3.11, added Phase E)
├── main.py
├── config.py                    ← ~257 params
├── simulation.py                ← tick loop (12 steps)
│
├── devlog\
│   ├── DEV_LOG.md               ← Phase E onwards
│   └── archive\
│       └── DEV_LOG_phase_a_to_d.md
│
├── prompts\                     ← 37 prompt files
│
├── docs\
│   ├── AI_COLLABORATOR_BRIEF.md ← Briefing for any AI collaborator
│   ├── validation.md            ← Full calibration + validation report
│   ├── world_architecture.md
│   ├── POST_AUTOSIM_TASKS.md
│   ├── autosim_learnings_pre_phase_e.md
│   ├── AUTOSIM.md
│   ├── MISSION.md
│   └── deep_dive_01_mating.md .. deep_dive_27_trait_completion.md
│
├── models\
│   ├── agent.py                 ← 35 heritable traits + 5 beliefs + 4 skills
│   ├── environment.py
│   └── society.py
│
├── engines\
│   ├── mating.py
│   ├── resources.py
│   ├── conflict.py
│   ├── reproduction.py
│   ├── mortality.py
│   ├── pathology.py
│   ├── institutions.py
│   └── reputation.py
│
├── metrics\
│   └── collectors.py            ← ~130 metrics per tick
│
├── experiments\
│   ├── scenarios.py             ← 10 named scenarios
│   ├── runner.py
│   └── summarizer.py
│
├── autosim\
│   ├── runner.py                ← simulated annealing optimizer
│   ├── realism_score.py
│   ├── targets.yaml             ← 9 calibration targets
│   ├── best_config.yaml         ← score 1.000 (Run 3, 816 experiments)
│   ├── journal.jsonl            ← Run 3 (clean restart post-Phase F)
│   └── archive\
│       ├── journal_run1_pre_phase_e.jsonl
│       └── journal_run2_pre_phase_f.jsonl
│
├── dashboard\
│   ├── app.py                   ← Phase G overhaul in progress
│   ├── tabs\                    ← Phase G: split tab modules
│   └── components\              ← Phase G: shared components
│
├── scripts\
│   ├── validate_best_config.py  ← held-out validation (NEW)
│   └── ec2_autosim.sh
│
├── tests\
│   ├── test_smoke.py
│   ├── test_id_counter.py       ← Phase E new
│   ├── test_config.py           ← Phase E new
│   └── test_society.py          ← Phase E new
│
├── sandbox\
│   └── explore.py
│
└── outputs\
    ├── runs\
    ├── experiments\             ← scenario experiment outputs
    └── reports\

================================================================================
DESIGN Q&A — ANSWER LOG (SUMMARY)
================================================================================

Q1-Q45: All answered — see original CHAIN_PROMPT for full Q&A history.
         Archived at devlog/archive/DEV_LOG_phase_a_to_d.md

Key locked decisions:
  Population 500, annual tick, 35 heritable traits, continuous [0,1] traits,
  hybrid probabilistic + utility decision model, reputation ledger memory,
  unrestricted competition default, two-dimensional resources (survival + status),
  8-phase resource engine, conflict before mating, institutions after mortality,
  equal split inheritance default, annual tick, non-spatial v1

================================================================================
CHANGE LOG
================================================================================

2026-03-15 | Phase G | DASHBOARD OVERHAUL (in progress)
  - prompts/dashboard_overhaul.md written (20-block executable prompt)
  - Refactors app.py into tabs/ + components/ modules
  - Adds: Beliefs tab, Scenario Comparison tab, Lorenz curve,
    survivorship curve, inter-faction violence matrix, bond duration
    histogram, phase portrait, epidemic annotation bands, export panel,
    KPI deltas, sidebar expanders

2026-03-15 | Phase H prep | PUBLICATION PLAN LOCKED
  - Central claim: institutions-substitute-for-traits (gene-culture coevolution)
  - Paper 1 target: JASSS / PLOS ONE (methods paper)
  - Paper 2 target: Evolutionary Human Sciences (findings)
  - Paper 3 target: Evolution and Human Behavior (coevolution claim)
  - arXiv preprint planned after scenario experiments + sensitivity analysis
  - AI disclosure language agreed: "Code development aided by Claude (Anthropic);
    all hypotheses and interpretations are the author's own."

2026-03-15 | SCENARIO EXPERIMENTS RUN 1
  - 5 seeds × 200yr × 10 scenarios using best_config.yaml baseline
  - Key findings logged in CONFIRMED DESIGN DECISIONS above
  - Run 2 in progress: 10 seeds × 500yr × 3 key scenarios

2026-03-15 | VALIDATION COMPLETE
  - scripts/validate_best_config.py written and run (2 passes)
  - 10 held-out seeds × 200yr: mean score 0.934, 0 collapses
  - docs/validation.md written (full calibration report with citations)
  - Verdict: MOSTLY ROBUST — suitable for scenario experiments

2026-03-15 | AUTOSIM RUN 3 COMPLETE
  - 816 experiments, ~10.5 hours, post-Phase F corrected model
  - Best score: 1.000 (all 9 metrics simultaneously in range)
  - autosim/best_config.yaml updated
  - Dramatic parameter reversals from Run 1 confirm Phase F fixes were material
  - Full analysis: docs/autosim_learnings_pre_phase_e.md (Run 1 learnings)

2026-03-15 | Phase F | MODEL QUALITY FIXES (19 fixes)
  - Critical: storage bonuses active, cross-sex conflict, mental illness
    no longer mutates traits, institutional drift enabled by default
  - High: EPC kin networks, bond dissolution symmetry, elite privilege
    bidirectional, age consistency, status setter fix, EPC survival fix
  - Medium: symmetric bond strengthening, wider fertility range,
    partner-driven destabilization, cooperation norm restriction, EPC gap fix,
    single cleanup pass, mate_value age curve peaks at 27
  - Full list: STATUS.md Phase E.1 section
  - All 22 tests passing after fixes

2026-03-15 | Phase E | ENGINEERING HARDENING (14 fixes)
  - P0: IdCounter per-simulation, event window cap
  - P1: _parent_* belief fields declared, Config.load() warns unknown keys
  - P2: Partner index, logging, mating_system wiring, ledger cleanup
  - P3: Dashboard split, .gitignore, .python-version, test suite expansion
  - Full prompt: prompts/phase_e_engineering_hardening.md

2026-03-15 | Phase D | DD27 TRAIT COMPLETION
  - 9 new traits (26→35): physical_strength, endurance, group_loyalty,
    outgroup_tolerance, future_orientation, conscientiousness,
    psychopathy_tendency (default 0.2), anxiety_baseline,
    paternal_investment_preference
  - 35×35 correlation matrix, PSD-verified via eigenvalue clipping

2026-03-14 | Phase C | DD15-DD26 COMPLETE
  - Extended genomics, developmental biology, medical/pathology,
    proximity tiers, migration, leadership, resource types, life stages,
    intelligence audit, epigenetics, beliefs, skills
  - 26 heritable traits, 5 belief dims, 4 skill domains

2026-03-14 | Phase B | DD01-DD14 COMPLETE
  - All core subsystems: mating, resources, conflict, genetics,
    institutions, household, reputation, prestige, disease, seasons,
    coalitions, signaling, demographics, factions

2026-03-13 | Phase A | DESIGN + SCAFFOLDING
  - Project initiated, 45 design questions answered, full scaffold created

NEXT SESSION OBJECTIVE:
  Wait for 10-seed × 500yr scenario run to complete.
  Analyze trait divergence across FREE_COMPETITION vs STRONG_STATE vs
  EMERGENT_INSTITUTIONS. This is the central finding test for Paper 1.
  Then: docs/sensitivity_analysis.md, begin Paper 1 draft.

================================================================================
END OF CHAIN PROMPT
================================================================================
