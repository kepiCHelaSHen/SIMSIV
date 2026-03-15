# SIMSIV — CHAIN PROMPT MASTER FILE
# Simulation of Intersecting Social and Institutional Variables
# Root: D:\EXPERIMENTS\SIM
# Last Updated: 2026-03-14 | Phase C complete

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
Status:     PHASE C COMPLETE — All 26 deep dives done (DD01-DD26)

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

  Heritable traits (26 total, h²-weighted inheritance + mutation σ=0.05):
    (First 21 listed below; plus 5 DD17 condition risks: cardiovascular_risk,
     mental_illness_risk, autoimmune_risk, metabolic_risk, degenerative_risk)
    aggression_propensity      float [0.0-1.0]  h²=0.44  tendency toward conflict
    cooperation_propensity     float [0.0-1.0]  h²=0.40  tendency toward alliance
    attractiveness_base        float [0.0-1.0]  h²=0.50  baseline physical mate value
    status_drive               float [0.0-1.0]  h²=0.50  motivation to seek dominance
    risk_tolerance             float [0.0-1.0]  h²=0.48  willingness to take risks
    jealousy_sensitivity       float [0.0-1.0]  h²=0.45  trigger threshold for jealousy
    fertility_base             float [0.0-1.0]  h²=0.50  baseline reproductive capacity
    intelligence_proxy         float [0.0-1.0]  h²=0.65  resource acquisition efficiency
    longevity_genes            float [0.0-1.0]  h²=0.25  lifespan extension (DD15)
    disease_resistance         float [0.0-1.0]  h²=0.40  epidemic resistance (DD15)
    physical_robustness        float [0.0-1.0]  h²=0.50  combat damage absorption (DD15)
    pain_tolerance             float [0.0-1.0]  h²=0.45  flee threshold modifier (DD15)
    mental_health_baseline     float [0.0-1.0]  h²=0.40  stress resilience (DD15)
    emotional_intelligence     float [0.0-1.0]  h²=0.40  trust/gossip effectiveness (DD15)
    impulse_control            float [0.0-1.0]  h²=0.50  aggression→action gate (DD15)
    novelty_seeking            float [0.0-1.0]  h²=0.40  exploration tendency (DD15)
    empathy_capacity           float [0.0-1.0]  h²=0.35  altruism radius (DD15)
    conformity_bias            float [0.0-1.0]  h²=0.35  institutional adoption (DD15)
    dominance_drive            float [0.0-1.0]  h²=0.50  dominance acquisition (DD15)
    maternal_investment        float [0.0-1.0]  h²=0.35  quality-quantity tradeoff (DD15)
    sexual_maturation_rate     float [0.0-1.0]  h²=0.60  age at first reproduction (DD15)

  Non-heritable traits (earned/contextual, reset or built each lifecycle):
    reputation                 float [0.0-1.0]  public standing score
    health                     float [0.0-1.0]  current health (decays with age)
    age                        int   years alive
    current_resources          float             survival resources (DD21)
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
    origin_band_id             int               migration origin (DD19, 0=native)
    generation_in_band         int               generations since immigration (DD19)
    Beliefs (DD25, 5 dims, float [-1, +1], culturally transmitted):
      hierarchy_belief, cooperation_norm, violence_acceptability,
      tradition_adherence, kinship_obligation
    Skills (DD26, 4 domains, float [0, 1], acquired via experience):
      foraging_skill, combat_skill, social_skill, craft_skill
    Epigenetics (DD24):
      epigenetic_stress_load   float             transgenerational stress
      epigenetic_generation_decay  int            generations since stress
    Medical (DD17):
      active_conditions        set               currently active pathologies
      trauma_score             float [0.0-1.0]   accumulated trauma

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
  Acquisition:             8-phase engine: kin trust → decay → distribute → child invest →
                           share → status → elite → tax → floor
  Competitive weights:     Cubed (intelligence + status + experience + wealth^0.7 + network)
                           * (1 - aggression * penalty)
  Equal floor:             25% of survival pool distributed equally
  Cooperation networks:    Kin trust bootstraps networks, 0.05/ally competitive bonus
  Aggression penalty:      0.3 multiplicative penalty on competitive weight
  Child investment:        0.5 resources/child/year, scaled by paternity confidence
  Inheritance:             Configurable (default: equal split to children)
  Ceiling:                 Soft — wealth diminishing returns (power 0.7) + elite cap
  Redistribution:          Configurable taxation (top quartile → bottom quartile, gated by law_strength)
  Subsistence floor:       1.0 minimum resources (prevents death spirals)
  Scarcity:                Configurable severity (default 0.6, was hardcoded 0.4)
  Deep dive:               DD02 COMPLETE — Gini 0.237 → 0.335

--- CONFLICT MODEL ---
  Triggers:                Jealousy, resource pressure, status drive, random baseline
  Suppression:             Institutional (law_strength), cooperation propensity,
                           network deterrence (allies), subordination cooldown
  Target selection:        Trust-based + rival + status challenge + resource envy +
                           network deterrence + strength assessment
  Flee response:           Low risk_tolerance targets escape combat (threshold 0.3)
  Combat resolution:       Power = aggression(0.25) + status(0.20) + health(0.25) +
                           risk(0.15) + resource_edge + intelligence(0.05) + allies
  Scaled consequences:     Power differential scales costs (0.7x close, 1.5x stomp)
  Subordination:           Losers enter cooldown (2yr), reduced initiation by 50%
  Bystander effects:       Witnesses distrust aggressor (-0.08, allies -0.1 extra)
  Death scaling:           Lethality increases with power differential
  Deep dive:               DD03 COMPLETE — 159 v-deaths (was 0/bug), 72 flees

--- OFFSPRING AND HOUSEHOLD ---
  Child survival factors:  Parental resources, pair bond stability,
                           kin network support, random mortality, env stress
  Offspring trait model:   DD15: h²*parent_midpoint + (1-h²)*pop_mean + mutation
  Mutation:                Base sigma=0.05, rare 5% at sigma=0.15, stress-amplified (1.5x)
  Migrant traits:          Population-derived (match evolved distribution, not uniform)
  Selection signals:       Aggression down, cooperation+intelligence up across all scenarios
  Trait diversity:         std~0.09 maintained by rare mutations (was 0.07 pre-DD04)
  Reproductive window:     Age configurable (default 15-45 female, 15-65 male)
  Growth to agent:         Offspring enter pool at birth, become fertile at config age
  Paternal investment:     Separable from pair bond status (configurable)
  Deep dive (genetics):    DD04 COMPLETE — parent variance, rare mutation, stress mutation
  Deep dive (household):   DD06 COMPLETE — birth interval, childhood mortality, orphan model, grandparent bonus, sibling trust

--- INSTITUTIONS ---
  Model:                   4-phase engine: inheritance → norm enforcement → drift → emergence
  Institutional drift:     law_strength evolves from cooperation vs violence balance
                           coop_pressure = (avg_coop - 0.4) * boost, violence_pressure = vio_rate * decay
                           Inertia creates path dependency; drift_rate=0.0 default (opt-in)
  Norm enforcement:        Active polygyny detection with scaling penalties
  Emergent formation:      Violence punishment after 5yr high-violence streak
                           Mate limit reduction after 8yr inequality streak
  Property rights:         Modulates conflict looting: loot = 0.5 * (1 - property_rights)
  Inheritance:             Default ON; equal_split, primogeniture, trust_weighted models
                           Prestige inheritance (status to heirs, configurable fraction)
  Cross-engine:            Institution engine mutates config values for next tick
                           Other engines automatically respond via config reads
  Deep dive:               DD05 COMPLETE — emergent law 0→0.48 over 200yr

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
    3. Conflict model        → prompts/deep_dive_03_conflict.md  [COMPLETE]
    4. Trait inheritance     → prompts/deep_dive_04_genetics.md  [COMPLETE]
    5. Institutions          → prompts/deep_dive_05_institutions.md [COMPLETE]
    6. Offspring/household   → prompts/deep_dive_06_household.md [COMPLETE]
    7. Memory/reputation     → prompts/deep_dive_07_reputation.md [COMPLETE]
    8. Prestige/dominance    → prompts/deep_dive_08_prestige.md [COMPLETE]
    9. Disease/epidemics     → prompts/deep_dive_09_disease.md [COMPLETE]
   10. Seasonal cycles       → prompts/deep_dive_10_seasons.md [COMPLETE]
   11. Coalitions/punishment → prompts/deep_dive_11_coalitions.md [COMPLETE]
   12. Status signaling      → prompts/deep_dive_12_signaling.md [COMPLETE]
   13. Demographics          → prompts/deep_dive_13_demographics.md [COMPLETE]
   14. Factions/in-group     → prompts/deep_dive_14_factions.md [COMPLETE]
   15. Extended genomics     → prompts/deep_dive_15_genomics.md [COMPLETE]
   16. Developmental biology → prompts/deep_dive_16_development.md [COMPLETE]
   17. Medical/pathology     → prompts/deep_dive_17_medical.md [COMPLETE]
   18. Proximity tiers       → prompts/deep_dive_18_proximity.md [COMPLETE]
   19. Migration dynamics    → prompts/deep_dive_19_migration.md [COMPLETE]
   20. Leadership            → prompts/deep_dive_20_leadership.md [COMPLETE]
   21. Resource types        → prompts/deep_dive_21_resource_types.md [COMPLETE]
   22. Life stages           → prompts/deep_dive_22_life_stages.md [COMPLETE]
   23. Intelligence audit    → prompts/deep_dive_23_intelligence.md [COMPLETE]
   24. Epigenetics           → prompts/deep_dive_24_epigenetics.md [COMPLETE]
   25. Beliefs/ideology      → prompts/deep_dive_25_beliefs.md [COMPLETE]
   26. Skills/knowledge      → prompts/deep_dive_26_skills.md [COMPLETE]

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
  prompts/deep_dive_03_conflict.md  → Conflict model deep dive
  prompts/deep_dive_04_genetics.md  → Trait inheritance deep dive
  prompts/deep_dive_05_institutions.md → Institutions deep dive
  prompts/deep_dive_06_household.md → Offspring/household deep dive
  prompts/deep_dive_07_reputation.md → Memory/reputation deep dive
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
├── STATUS.md                    ← current status (trimmed, history in DEV_LOG)
├── requirements.txt
├── main.py
├── config.py                    ← ~250 params, flat dataclass
├── simulation.py                ← pure library core, tick loop (steps 1-12)
│
├── devlog\
│   └── DEV_LOG.md               ← all session logs + archived results
│
├── prompts\                     ← all Claude prompts, copy-paste ready
│   ├── README.md                ← index of all 26 deep dive prompts
│   ├── phase1_design.md
│   ├── phase2_skeleton.md
│   ├── phase3_experiments.md
│   ├── phase4_roadmap.md
│   ├── deep_dive_template.md
│   ├── deep_dive_01_mating.md .. deep_dive_26_skills.md
│   ├── run_remaining_dives.md
│   ├── iteration_template.md
│   └── debug_template.md
│
├── artifacts\                   ← permanent record of important outputs
│   ├── design\
│   ├── charts\
│   └── exports\
│
├── docs\                        ← design documents + moved project docs
│   ├── AUTOSIM.md               ← moved from root
│   ├── MISSION.md               ← moved from root
│   ├── deep_dive_01_mating.md .. deep_dive_26_skills.md
│   └── world_architecture.md
│
├── models\
│   ├── __init__.py
│   ├── agent.py                 ← 26 heritable traits + 5 beliefs + 4 skills
│   ├── environment.py
│   └── society.py               ← proximity tiers, factions, migration
│
├── engines\
│   ├── __init__.py
│   ├── mating.py
│   ├── resources.py
│   ├── conflict.py
│   ├── reproduction.py
│   ├── mortality.py             ← maturation triggers (beliefs, skills)
│   ├── pathology.py             ← conditions, trauma
│   ├── institutions.py
│   └── reputation.py            ← gossip, beliefs, skills, factions
│
├── metrics\
│   ├── __init__.py
│   └── collectors.py            ← ~120 metrics per tick
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
├── sandbox\
│   └── explore.py               ← IPython exploration harness
│
└── outputs\                     ← all run outputs (gitignore this)
    ├── runs\
    ├── charts\
    └── reports\

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
     ANSWERED: YES — 26 traits (21 core + 5 condition risks) with per-trait heritability (DD15+DD17 expanded from 8)

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

2026-03-14 | Session cleanup | PROJECT CLEANUP
  - README.md rewritten (26 traits, 9 engines, 26 deep dives, quick start)
  - requirements.txt updated (added scipy, streamlit, version pins)
  - simulation.py tick loop renumbered to clean steps 1-12 (was fractional)
  - Replaced all getattr(config, field, default) with direct config access
  - STATUS.md trimmed to 15 lines (historical results archived to DEV_LOG.md)
  - Moved AUTOSIM.md, MISSION.md to docs/
  - Created docs/deep_dive_01_mating.md (was missing)
  - Created prompts/README.md (index of all 26 deep dive prompts)
  - Updated CHAIN_PROMPT.md file tree
  - Created sandbox/explore.py (IPython harness)

2026-03-14 | Session chain_runner_dd18_26 | DD18-DD26 COMPLETE
  - Proximity tiers (DD18): household/neighborhood/band model
  - Migration (DD19): emigration push, immigration pull
  - Leadership (DD20): war leader + peace chief per faction
  - Resource types (DD21): subsistence/tools/prestige goods
  - Life stages (DD22): CHILDHOOD/YOUTH/PRIME/MATURE/ELDER
  - Intelligence audit (DD23): diminishing returns fix
  - Epigenetics (DD24): transgenerational stress, trauma contagion
  - Beliefs (DD25): 5 cultural belief dimensions, social influence, belief effects
  - Skills (DD26): 4 experiential skill domains, mentoring, cultural knowledge
  - ALL 26 DEEP DIVES COMPLETE

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
  Phase D or v2 planning — multi-band dynamics, performance optimization,
  or new experiment runs with full DD01-DD26 feature set.

================================================================================
END OF CHAIN PROMPT
================================================================================
