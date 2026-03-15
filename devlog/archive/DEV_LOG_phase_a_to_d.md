# SIMSIV — DEV LOG ARCHIVE (Phase A through D)
# Archived: 2026-03-15
# Covers: Project inception (Session 001) through DD27 trait completion
# Source: Original DEV_LOG.md recovered from user

================================================================================
DATE: 2026-03-14
SESSION: chain_runner_dd18_26
AUTHOR: claude
TYPE: CODE
SUMMARY: DD18-DD26 Chain Runner — Proximity, Migration, Leadership, Resource
         Types, Life Stages, Intelligence Audit, Epigenetics, Beliefs, Skills
================================================================================

DETAILS:
Executed 9 deep dives (DD18-DD26) in continuous chain runner mode.

DD18 (Proximity Tiers):
  Three-tier proximity model — household/neighborhood/band.
  Proximity-weighted conflict targeting, mate evaluation, cooperation sharing,
  gossip noise. Society gets household_of() and refresh_neighborhoods() methods.
  8 new config params, 4 new metrics.

DD19 (Migration):
  Emigration push factors (resource stress, ostracism, unmated, overcrowding)
  and immigration pull factors (resource surplus, vacancy). Agents track
  origin_band_id, immigration_year, generation_in_band. Runs at step 6.3.
  12 new config params, 4 new metrics.

DD20 (Leadership):
  War leader (dominance-based) and peace chief (prestige-based) per faction.
  War leaders boost faction aggression, combat bonus, deterrence. Peace chiefs
  mediate intra-faction conflict, boost sharing.
  9 new config params, 3 new metrics.

DD21 (Resource Types):
  Three resource types — subsistence (perishable, 0.4 retention), tools
  (durable, 10% decay), prestige goods (5% decay). Tool production multiplier,
  intra-band trade, tool looting in conflict, prestige goods mate signal.
  11 new config params, 5 new metrics.

DD22 (Life Stages):
  Five computed stages — CHILDHOOD/YOUTH/PRIME/MATURE/ELDER.
  Youth +25% conflict, mature -20%, elder -50%. Prime parenting +20%.
  Elder norm anchor slows institutional drift. Expanded memory for mature/elder.
  10 new config params, 6 new metrics.

DD23 (Intelligence Audit):
  Diminishing returns on intelligence competitive weight:
  min(intel^0.7, 0.8) * 0.25. Prevents intelligence runaway (+0.05/100yr → stable).

DD24 (Epigenetics):
  Transgenerational stress load from scarcity/epidemic/trauma. Epigenetic sigma
  boost amplifies offspring trait mutation. Trauma contagion spreads from
  high-trauma agents to contacts. Faction trauma buffer for strong factions.
  11 new config params, 4 new metrics.

DD25 (Beliefs):
  5 non-heritable belief dimensions [-1,+1]: hierarchy, cooperation_norm,
  violence_acceptability, tradition_adherence, kinship_obligation. Initialized
  from traits + parent beliefs at maturation. Evolves via social influence
  (prestige-biased), experience, and cultural mutation every 3 ticks. Effects
  on conflict (violence_acceptability), resources (cooperation_norm,
  kinship_obligation), mating (endogamy), institutions (belief aggregate drift).
  Ideological tension and belief revolution detection.
  7 new config params, 9 new metrics.

DD26 (Skills):
  4 non-heritable skill domains [0-1]: foraging, combat, social, craft.
  Initialized at maturation from intelligence + parent transmission. Grows
  through exercise, decays without use. Foraging multiplies effective
  intelligence in resource competition. Combat adds to power calculation.
  Social boosts gossip and mate assessment. Craft multiplies tool production.
  Faction-based mentoring system.
  11 new config params, 11 new metrics.

DECISIONS MADE:
  - All 26 deep dives now complete (DD01-DD26)
  - 26 heritable traits, 5 belief dimensions, 4 skill domains
  - Tick order: env(1)→res(2)→conflict(3)→mating(4)→repro(5)→mortality(6)→
    migration(6.3)→pathology(6.5)→institutions(7)→reputation(8)→factions(8.5)→
    neighborhoods(8.6)→metrics(9)→equilibrium(10)

FILES CHANGED:
  models/agent.py, models/society.py, config.py, simulation.py,
  engines/resources.py, engines/conflict.py, engines/mating.py,
  engines/reputation.py, engines/institutions.py, engines/mortality.py,
  engines/pathology.py, metrics/collectors.py,
  docs/deep_dive_18_proximity.md through docs/deep_dive_26_skills.md

NEXT ACTIONS:
  - Phase D or v2 planning
  - Multi-band / inter-band dynamics
  - Performance optimization for large populations

================================================================================
DATE: 2026-03-14
SESSION: chain_runner_dd17
AUTHOR: claude
TYPE: CODE
SUMMARY: DD17 Medical History and Pathology — heritable conditions, trauma,
         pathology engine
================================================================================

DETAILS:
Created new pathology engine that runs at step 6.5 (between mortality and
institutions). Added 5 heritable condition risks (cardiovascular, mental_illness,
autoimmune, metabolic, degenerative) to HERITABLE_TRAITS, bringing total to 26.

Condition activation is probability-based: base_risk * triggers. Triggers include
age, resource stress, childhood trauma, scarcity, and conflict. Each condition
has distinct behavioral effects wired into existing engines:
  - Cardiovascular: extra health decay after 40
  - Mental illness: erratic behavior (random cooperation/aggression spikes)
  - Autoimmune: 2x epidemic vulnerability despite disease_resistance
  - Metabolic: 15% resource acquisition penalty
  - Degenerative: increased flee threshold (+0.15)

Accumulated trauma tracks damage from conflict losses, kin deaths, and chronic
deprivation. High trauma (>0.4) amplifies mental illness activation. Very high
trauma (>0.8) causes behavioral instability. Recovery is slow (0.01/yr) and
accelerated by kin support.

Medical history bounded to 50 entries per agent.

Mate choice: active conditions reduce attractiveness signal (not the heritable
value). Emotional intelligence enables better detection.

Initial population condition risks centered at 0.2 mean (not 0.5) via modified
create_initial_population multivariate normal means.

Validation: 100 pop x 20yr seed 42 — stable at 112, Gini 0.35, violence 0.03.

DECISIONS MADE:
  - Condition risks are heritable traits (in HERITABLE_TRAITS) with low defaults (0.2)
  - Active conditions, trauma, medical history are non-heritable state
  - Pathology engine runs after mortality (sees deaths for trauma) and before institutions
  - Condition effects designed as small multipliers into existing engines
  - Mental illness effect: stochastic (30% chance per tick of behavioral spike)
  - Metabolic paradox: high-resource environments increase metabolic activation

FILES CHANGED:
  models/agent.py, engines/pathology.py (NEW), engines/__init__.py,
  simulation.py, engines/mortality.py, engines/conflict.py,
  engines/resources.py, engines/mating.py, config.py,
  metrics/collectors.py, docs/deep_dive_17_medical.md (new),
  STATUS.md, CHAIN_PROMPT.md

================================================================================
DATE: 2026-03-14
SESSION: chain_runner_dd16
AUTHOR: claude
TYPE: CODE
SUMMARY: DD16 Developmental Biology — genotype/phenotype split, nature vs nurture
================================================================================

DETAILS:
Implemented the formal nature vs nurture model. Key architectural change: agents
now have TWO layers — genotype (stored at birth, never modified) and phenotype
(expressed values, modified at maturation by environment).

breed() now reads genotype from parents (not phenotype), so environmental effects
on parents don't permanently corrupt the gene pool. A cooperative person raised
violently may behave aggressively, but their children inherit the cooperative
genotype.

Maturation event fires at age 15:
  - Resource environment: well-resourced → +intelligence, +impulse_control;
    deprived → +aggression, +risk_tolerance
  - Parental modeling: parent cooperation → child cooperation boost
  - Orphan effect: +aggression, -trust capacity
  - Childhood trauma: parent death before age 10 → behavioral instability
  - Peer group: conformity_bias gates peer influence (30% of parental)
  - Birth order: firstborn +conscientiousness, later-born +novelty/risk

Orchid/dandelion mechanism: mental_health_baseline moderates sensitivity.
Low mental_health (orchid): dramatic response to both good and bad environments.
High mental_health (dandelion): stable regardless of environment.

Childhood resource quality tracked as running average ages 0-5. All trait
modifications capped at ±0.10 (significant but not overwhelming).

Validation: 100 pop x 20yr seed 42 — stable at 116, Gini 0.32, violence 0.03.

DECISIONS MADE:
  - Genotype stored as dict, not 21 separate fields
  - Maturation placed in mortality engine (already handles aging)
  - Peer traits precomputed once per tick from children aged 5-16
  - Founding population skips maturation (no genotype stored)
  - Birth order counted from one parent only (avoids double-counting)

FILES CHANGED:
  models/agent.py, engines/mortality.py, engines/resources.py,
  config.py (7 new params), metrics/collectors.py (3 new metrics),
  docs/deep_dive_16_development.md (new), STATUS.md, CHAIN_PROMPT.md

================================================================================
DATE: 2026-03-14
SESSION: chain_runner_dd15
AUTHOR: claude
TYPE: CODE
SUMMARY: DD15 Extended Genomics — 21 heritable traits with h²-weighted inheritance
================================================================================

DETAILS:
Expanded heritable trait system from 8 to 21 traits. Each trait has a per-trait
heritability coefficient (h²) from behavioral genetics literature. breed() now uses:
  child_val = h² * parent_midpoint + (1 - h²) * pop_mean + mutation

This means low-h² traits (longevity_genes=0.25) regress strongly to population
mean while high-h² traits (intelligence_proxy=0.65) track parents closely.

New traits and their engine wiring:
  - longevity_genes → mortality (death age +10yr, health decay -40% past 50)
  - disease_resistance → mortality (epidemic vulnerability -50%)
  - physical_robustness → conflict (damage absorption -40%, combat power)
  - pain_tolerance → conflict (flee threshold boost, combat power)
  - mental_health_baseline → conflict (stress-aggression moderation -50%)
  - emotional_intelligence → mating, resources, reputation
    (trust +30%, gossip +30%, bluff detection +30%)
  - impulse_control → conflict (aggression→action gate -60%)
  - novelty_seeking → correlation matrix only (risk_tolerance +0.4, conformity -0.3)
  - empathy_capacity → conflict (-30%), resources (sharing +15%)
  - conformity_bias → institutions (adoption speed +30%)
  - dominance_drive → resources (dominance score +20%), conflict (combat power)
  - maternal_investment → reproduction (-20% conception, +15% child survival)
  - sexual_maturation_rate → agent (is_fertile_with_config ±3 years)

21x21 correlation matrix built programmatically preserving original 8x8 block.
Validation: 100 pop x 20yr seed 42 — pop stable at 122, Gini 0.30, violence 0.03.

DECISIONS MADE:
  - Heritability model: h²-weighted midpoint + population mean regression
  - heritability_by_trait config param: empty dict = use defaults
  - All trait effects modest (small multipliers, not catastrophic)
  - Combat power weights redistributed to accommodate new traits

FILES CHANGED:
  models/agent.py, engines/reproduction.py, engines/mortality.py,
  engines/conflict.py, engines/mating.py, engines/resources.py,
  engines/reputation.py, engines/institutions.py,
  config.py, metrics/collectors.py, docs/deep_dive_15_genomics.md (new),
  STATUS.md, CHAIN_PROMPT.md

================================================================================
DATE: 2026-03-13
SESSION: 001
AUTHOR: both
TYPE: DESIGN + SCAFFOLDING
SUMMARY: Project initiated. Directory scaffold built. Design Q&A session begun.
================================================================================

DETAILS:
  - Project SIMSIV formally initialized at D:\EXPERIMENTS\SIM
  - Full project brief reviewed and internalized
  - CHAIN_PROMPT.md created as living master document
  - 45 design questions posed across 9 categories
  - Design Q&A session conducted (see decisions below)
  - Full directory scaffold created
  - DEV_LOG.md initialized (this file)
  - prompts/ directory created for prompt library
  - artifacts/ directory created for design artifacts, charts, exports
  - devlog/ directory created for this log

DECISIONS MADE:
  SCALE:
    - Population: maximize for richness, target 500-1000 agents
    - Generations: maximize, target 100+
    - Time step: annual tick for v1
    - Runtime: no hard ceiling

  AGENT MODEL:
    - Traits ARE heritable (parent → offspring blend + Gaussian noise)
    - Heritable traits (v1): aggression, cooperation, attractiveness_base,
      status_drive, risk_tolerance, jealousy_sensitivity, fertility_base,
      intelligence_proxy
    - Non-heritable: social_trust, reputation, pair_bond_status
    - Mutation: YES — Gaussian noise σ=0.05 per heritable trait per generation
    - Decision model: HYBRID — probabilistic weights with utility tiebreakers
    - Agent memory: YES — lightweight reputation ledger per agent pair
    - Trait representation: CONTINUOUS (0.0-1.0)
    - Mate value: DYNAMIC — f(health, status, resources, age)

  MATING SYSTEM:
    - Default: UNRESTRICTED COMPETITION (null hypothesis baseline)
    - All variants configurable as experimental overlays
    - Deep dive = Phase B priority #1

  PHILOSOPHY:
    - Skeleton-first: build working end-to-end sim, then do deep dives
    - Phase A = skeleton with defensible v1 defaults
    - Phase B = deep dive chains per subsystem

FILES CHANGED:
  - D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md (created)
  - D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md (created)
  - All directories created (scaffold)

================================================================================
DATE: 2026-03-13
SESSION: 002
AUTHOR: both
TYPE: CODE
SUMMARY: Full working skeleton built — models, 6 engines, metrics, charts, CLI.
================================================================================

DETAILS:
  - Built all core modules: agent.py, environment.py, society.py
  - Built all 6 engines: resources, conflict, institutions, mating,
    reproduction, mortality
  - Built metrics collector (25+ per-tick metrics), visualization (6-panel)
  - Built simulation.py (pure library, zero IO) and main.py (CLI)
  - Added selection pressure fixes: conflict before mating, female choice
    penalizes aggression, cooperation resource networks, pair bond
    destabilization from violence
  - Calibrated fertility: base_conception_chance 0.3→0.5
  - Observed emergent boom-bust population cycles (30-40 year period)

DECISIONS MADE:
  - Tick order: env→resources→conflict→mating→reproduction→mortality→
    institutions→metrics
  - Conflict before mating so violence = reproductive fitness cost
  - Health modifier on conception: threshold-based

FILES CHANGED:
  All files in models/, engines/, metrics/, visualizations/,
  config.py, simulation.py, main.py, requirements.txt, .gitignore,
  CLAUDE.md, STATUS.md, MISSION.md

================================================================================
DATE: 2026-03-14
SESSION: 003
AUTHOR: both
TYPE: CODE + DEBUG + EXPERIMENT
SUMMARY: Fixed all 5 bugs, built experiment framework, calibrated resource
         Gini, ran first definitive experiments.
================================================================================

DETAILS:
  Bug fixes (5/5):
    1. Inheritance now sees ALL deaths — institutions moved after mortality
    2. Scarcity computed once per tick in Environment.tick() — deterministic
    3. Global ID counter no longer resets — 0 collisions in multi-run test
    4. Violence suppression: law_strength * (0.5 + punishment * 0.5)
    5. Config.post_init wires mating_system="monogamy" → monogamy_enforced=True
       max_mates_per_male now enforced in mating engine

  Resource engine calibration:
    - Equal/competitive split: 70/30 → 40/60
    - Competitive weights squared to amplify differences
    - Result: baseline Gini 0.13 → 0.25 (realistic pre-agricultural)
    - ELITE_POLYGYNY Gini 0.97 → 0.42

  Experiment framework built:
    - experiments/scenarios.py — 8 named scenario configs
    - experiments/runner.py — ExperimentRunner
    - experiments/summarizer.py — NarrativeSummarizer + SimIntegrityChecker

  Priority #1 definitive run (5 seeds, 200yr, pop 500):
    FREE_COMPETITION:    Gini=0.237, violence=0.057, unmated_m=38%, child_surv=83%
    ENFORCED_MONOGAMY:  violence -36%, unmated males -42%, pop +1.5%
    ELITE_POLYGYNY:     Gini +74% (0.41), violence +8%, child_surv +6%

DECISIONS MADE:
  - Engine order: institutions now after mortality (for inheritance)
  - Resource Gini calibrated: 40/60 split, squared weights, capped elite bonus
  - Baseline Gini ~0.25 accepted for pre-agricultural society

FILES CHANGED:
  models/agent.py, models/environment.py, models/society.py, config.py,
  engines/conflict.py, engines/institutions.py, engines/mating.py,
  engines/resources.py, metrics/collectors.py, simulation.py,
  experiments/scenarios.py (new), experiments/runner.py (new),
  experiments/summarizer.py (new), STATUS.md, AUTOSIM.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 004
AUTHOR: both
TYPE: CODE
SUMMARY: Mating Deep Dive (DD01) — EPC, paternity, male competition,
         multi-bond support.
================================================================================

DETAILS:
  Structural migration from pair_bond_id to partner_ids list. Extra-pair
  copulation, paternity uncertainty, male contests, mourning period.
  6 new metrics, 9 new config params.

FILES CHANGED:
  models/agent.py, engines/mating.py (full rewrite, 5-phase),
  engines/reproduction.py, engines/conflict.py, engines/mortality.py,
  engines/institutions.py, config.py, metrics/collectors.py

================================================================================
DATE: 2026-03-14
SESSION: 005
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Resource Deep Dive (DD02) — aggression penalty, cooperation networks,
         wealth ceiling, child investment.
================================================================================

DETAILS:
  Full resource engine rewrite (8-phase architecture):
    Phase 0: Kin trust maintenance (parent-child trust +0.02/yr)
    Phase 1: Decay existing resources
    Phase 2: Distribute survival resources (25% equal / 75% competitive)
    Phase 3: Child investment costs
    Phase 4: Cooperation sharing (amplified mutual aid)
    Phase 5: Status distribution (cooperation-weighted)
    Phase 6: Elite privilege (capped)
    Phase 7: Taxation / redistribution (optional)
    Phase 8: Subsistence floor

  Key design changes:
    - Competitive weights cubed (stronger differentiation)
    - Equal floor reduced 40%→25%
    - Aggression production penalty: fighters get 18% fewer resources
    - Cooperation network bonus: 0.05/ally, cap 5
    - Wealth diminishing returns (power 0.7)
    - Subsistence floor prevents death spirals
    - Configurable scarcity severity (0.6, was hardcoded 0.4)

  Results (3 seeds, 200yr, 500 pop):
    FREE_COMPETITION:   Gini 0.237→0.335 (+41%)
    ELITE_POLYGYNY:     Gini 0.411→0.468
    ENFORCED_MONOGAMY:  Gini ~0.328
    RESOURCE_SCARCITY:  collapsed→609 pop (FIXED)
    Cooperation networks: 0.5→3.3 avg allies

  Aggression-pays-cost confirmed:
    High agg quartile: 2.8 res, 0.8 offspring, 28% bonded
    Low agg quartile:  3.4 res, 1.0 offspring, 32% bonded

FILES CHANGED:
  engines/resources.py (full rewrite, 8-phase), config.py (12 DD02 params),
  models/environment.py, metrics/collectors.py,
  experiments/scenarios.py, docs/deep_dive_02_resources.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 006
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Conflict Deep Dive (DD03) — network deterrence, flee response, scaled
         consequences, subordination, bystander trust.
================================================================================

DETAILS:
  Full conflict engine rewrite with 6 new mechanics:
    1. Network deterrence: ally counts suppress initiation + targeting
    2. Flee response: low risk_tolerance targets escape (72 flee events baseline)
    3. Scaled consequences: power differential scales cost magnitude
    4. Subordination: losers enter cooldown (2yr, 50% dampening)
    5. Bystander trust: witnesses update trust toward aggressor (-0.08)
    6. Violence death fix: proper "death" events now emitted (was 0, now 159)

  Also: resource advantage in combat, strength assessment, resource envy targeting.

  Results (500 pop, 100yr):
    BASELINE:        Pop=623, v-deaths=159, flees=72, cooldown=4.5%
    STRICT_MONOGAMY: Pop=912, v-deaths=118
    ELITE_POLYGYNY:  Pop=1248, v-deaths=144
    HIGH_VIOLENCE:   Pop=490, v-deaths=275, aggression=0.434 (vs 0.472 baseline)

FILES CHANGED:
  engines/conflict.py (full rewrite, 315 lines), models/agent.py
  (conflict_cooldown field), config.py (9 params),
  metrics/collectors.py (4 metrics), docs/deep_dive_03_conflict.md (new),
  prompts/deep_dive_03-07.md (new batch)

================================================================================
DATE: 2026-03-14
SESSION: 007
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Genetics Deep Dive (DD04) — parent weight variance, rare mutations,
         stress mutation, per-trait metrics.
================================================================================

DETAILS:
  Inheritance model refinements:
    - Parent weight variance: random blend w ~ clip(N(0.5, 0.1), 0.1, 0.9)
    - Rare large mutations: 5% chance, sigma=0.15 (3x normal) per trait
    - Stress-induced mutation: scarcity amplifies sigma up to 1.5x
    - Population-derived migrant traits (not uniform [0.2, 0.8])
    - Per-trait evolution tracking: all 8 traits + diversity + generation

  Post-DD04 trait std ~0.09 (was ~0.07) — prevents trait fixation.

  Scenario comparison (200yr):
    BASELINE:       agg -0.036, coop +0.058, intel +0.071
    STRICT_MONOGAMY: agg -0.053, coop +0.074, intel +0.093
    ELITE_POLYGYNY:  agg -0.086, coop +0.029, intel +0.080
    HIGH_VIOLENCE:   agg -0.069, coop +0.059, intel +0.014

FILES CHANGED:
  models/agent.py, models/society.py, engines/reproduction.py,
  config.py (5 params), metrics/collectors.py (9 metrics),
  docs/deep_dive_04_genetics.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 008
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Institutions Deep Dive (DD05) — institutional drift, norm enforcement,
         emergent formation, property rights, enhanced inheritance.
================================================================================

DETAILS:
  Full institution engine rewrite (4 phases):
    1. Institutional drift: law evolves from cooperation vs violence balance
       - drift_rate=0.0 default (backward-compatible)
       - With drift_rate=0.02: law grows 0→0.48 over 200yr
    2. Norm enforcement: active polygyny detection
    3. Emergent formation: violence_punishment after 5yr, mate_limit after 8yr
    4. Property rights: modulates conflict looting

  inheritance_law_enabled default changed False→True (resources no longer vanish).
  Added "trust_weighted" inheritance model and inheritance_prestige_fraction.

  Results (500 pop, 200yr):
    BASELINE:           Pop=609, Gini=0.306, Vio=0.054, Law=0.000
    ENFORCED_MONOGAMY:  Pop=740, Gini=0.317, Vio=0.033
    STRONG_STATE:       Pop=1177, Gini=0.250, Vio=0.024
    EMERGENT:           Pop=941, Gini=0.268, Vio=0.050, Law=0→0.484
    HIGH_VIOLENCE:      Pop=745, Gini=0.354

  Key insight: STRONG_STATE has lower cooperation (0.527) than BASELINE (0.564)
  — institutions substitute for individual traits.

FILES CHANGED:
  engines/institutions.py (full rewrite), engines/conflict.py,
  config.py (7 params), metrics/collectors.py (6 metrics),
  experiments/scenarios.py (2 new: STRONG_STATE, EMERGENT),
  docs/deep_dive_05_institutions.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Household Deep Dive (DD06) — birth interval, childhood mortality,
         orphan model, sibling trust, grandparent bonus.
================================================================================

DETAILS:
  Household layer added without formal household data structure.

  Birth spacing and fertility decline:
    - birth_interval_years=2 (lactational amenorrhea)
    - maternal_age_fertility_decline=0.03 (3%/yr past 30)
    - max_lifetime_births=12 (hard cap)
    - maternal_health_cost=0.03 (cumulative health cost)
    - Result: avg 3.2 lifetime births, max ~8

  Annual childhood mortality:
    - childhood_mortality_annual=0.02 base risk ages 1-15
    - Resource-dependent: poor families lose more children
    - ~128 deaths over 50yr at 200 pop

  Orphan model:
    - orphan_mortality_multiplier=2.0 (double mortality)
    - No formal adoption (subsistence floor provides minimum)

  Grandparent effects:
    - grandparent_survival_bonus=0.05 reduces infant + childhood mortality
    - Implements partial "grandmother hypothesis"

  Sibling trust:
    - sibling_trust_growth=0.01: co-living siblings build mutual trust
    - Added to resources.py Phase 0

FILES CHANGED:
  engines/reproduction.py, engines/mortality.py, engines/resources.py,
  models/agent.py, config.py (8 params), metrics/collectors.py (6 metrics),
  docs/deep_dive_06_household.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Reputation Deep Dive (DD07) — gossip, trust decay, dead cleanup,
         aggregate reputation.
================================================================================

DETAILS:
  New reputation engine (4 phases):
    1. Trust decay: entries drift toward 0.5 at 0.01/yr (extreme values decay slower)
    2. Dead agent cleanup: removes dead IDs from all ledgers each tick
    3. Gossip: 10% of agents share one trust entry with one ally per tick,
       Gaussian noise (sigma=0.1) degrades info
    4. Reputation update: public rep = 70% aggregate trust + 30% existing

FILES CHANGED:
  engines/reputation.py (new), simulation.py, config.py (7 params),
  metrics/collectors.py (5 metrics), docs/deep_dive_07_reputation.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Prestige Deep Dive (DD08) — split current_status into
         prestige/dominance dual-track system.
================================================================================

DETAILS:
  Split single current_status into prestige_score and dominance_score:
    - Prestige: cooperation, intelligence, network, reputation sources
      Slow decay (1%/yr). Aggressor loses prestige per conflict.
    - Dominance: status_drive, aggression, conflict victories
      Fast decay (3%/yr). Requires ongoing enforcement.

  Engine rewiring:
    - Combat: dominance_weight=0.7, prestige=0.3
    - Mate value: prestige_weight=0.6, dominance=0.4
    - Resource competition: prestige=0.7, dominance=0.3

  Backward compatible: current_status remains as computed property.

FILES CHANGED:
  models/agent.py, engines/conflict.py, engines/resources.py,
  engines/mating.py, engines/institutions.py, config.py (5 params),
  metrics/collectors.py (5 metrics), docs/deep_dive_08_prestige.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Disease Deep Dive (DD09) — epidemic events with differential vulnerability.
================================================================================

DETAILS:
  Epidemic model:
    - Base probability 2%/yr after 20yr refractory period
    - Overcrowding multiplier above 80% capacity
    - Duration: 2 years peak
    - Children (0-10): 3x mortality, Elderly (55+): 2x, Low health: 2x
    - Base lethality: 15% per epidemic year

  Cross-seed validation (200 pop, 100yr):
    Seed 42:  0 epidemics, final 487
    Seed 123: 4 epi years, 301 deaths, final 77
    Seed 456: 0 epidemics, final 669
    Seed 789: 2 epi years, 187 deaths, final 145

FILES CHANGED:
  models/environment.py, engines/mortality.py, config.py (8 params),
  metrics/collectors.py (2 metrics), docs/deep_dive_09_disease.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Seasons Deep Dive (DD10) — seasonal resource cycles, storage,
         birth timing.
================================================================================

DETAILS:
  - Seasonal cycle: cosine wave (amplitude=0.3, period=3yr default)
  - Intelligence-mediated storage: effective_decay = base + intel * 0.2
  - Storage cap: 20.0 max
  - Birth timing: conception ±20% with cycle phase
  - Lean-phase conflict boost: +20% during trough

FILES CHANGED:
  models/environment.py, engines/resources.py, engines/reproduction.py,
  engines/conflict.py, config.py (7 params), metrics/collectors.py,
  docs/deep_dive_10_seasons.md (new)

================================================================================
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Coalitions DD11, Signaling DD12, Demographics DD13, Factions DD14
================================================================================

DD11 (Coalitions):
  Coalition defense: allies intervene before combat (~95/50yr)
  Third-party punishment: altruistic punishment at personal cost (~2/50yr)
  Ostracism: low-reputation excluded from sharing

DD12 (Signaling):
  Resource display: 5% of resources spent, builds prestige
  Dominance bluff: low-dom + risk + aggression agents attempt (5%/yr)
  ~55% detection rate. Caught: -0.15 rep, -0.05 prestige

DD13 (Demographics):
  Sex-differential mortality: males 15-40 at 1.8x background rate
  Childbirth mortality: 2% per birth, 3x if health < 0.4
  Age-specific fertility: adolescent 60%, peak 20-28 at 100%, post-30 decline

DD14 (Factions):
  Emergent connected-component detection on mutual trust graph
  Mutual trust > 0.65 required for same-faction edge
  Runs every 5 years. Components < 3 = factionless.
  74 faction formation events in 500-pop baseline
  Peak factions: 45 (year 11) → consolidates to 1-2 by year 60
  In-group sharing bonus (+20%), out-group conflict boost (1.5x),
  endogamy preference (+10% mate value), leader-based merge,
  schism above 50 members

FILES CHANGED (DD11-DD14):
  engines/conflict.py, engines/resources.py, engines/mating.py,
  models/agent.py, models/society.py, simulation.py, config.py,
  metrics/collectors.py, docs/deep_dive_11-14.md (new files)

================================================================================
DATE: 2026-03-14
SESSION: cleanup
AUTHOR: claude
TYPE: REFACTOR
SUMMARY: Project cleanup — README, requirements, tick renumber, STATUS archive,
         docs reorganization
================================================================================

DETAILS:
  - Archived historical results from STATUS.md into this log
  - Rewrote README.md with current state (26 traits, 9 engines, 26 deep dives)
  - Updated requirements.txt with version pins (added scipy, streamlit)
  - Renumbered simulation.py tick loop to clean steps 1-12 (no fractions)
  - Replaced all getattr(config, field, default) with direct config field access
  - Moved AUTOSIM.md and MISSION.md to docs/
  - Created docs/deep_dive_01_mating.md (was missing)
  - Created prompts/README.md (index of all 26 deep dive prompts)
  - Updated CHAIN_PROMPT.md file tree and change log
  - Created sandbox/explore.py (IPython harness)

FILES CHANGED:
  README.md, requirements.txt, simulation.py, STATUS.md, devlog/DEV_LOG.md,
  CHAIN_PROMPT.md, docs/AUTOSIM.md, docs/MISSION.md, docs/deep_dive_01_mating.md,
  prompts/README.md, sandbox/explore.py

================================================================================
ARCHIVED STATUS.MD RESULTS (moved 2026-03-14)
================================================================================

Post-DD06 (Session 009, 200 pop x 50yr):
  - Childhood deaths: 128 total over 50yr (~2-5/yr at 200 pop)
  - Orphans: 12 among 245 children (~5%)
  - Avg lifetime births: 3.17, max observed 8 (below cap of 12)
  - Maternal health: avg 0.427 (visible cumulative cost of reproduction)
  - Birth interval working: 2yr minimum between births
  - Population stable at ~440 (no collapse from added mortality)

Post-DD05 (Session 008, 500 pop x 200yr):
  - BASELINE: Pop=609, Gini=0.306, Vio=0.054, Law=0.000
  - STRONG_STATE: Pop=1177, Gini=0.250, Vio=0.024, Law=0.800
  - EMERGENT: Pop=941, Gini=0.268, Law grows 0→0.484 organically, 24 events
  - ENFORCED_MONOGAMY: Pop=740, Gini=0.317, Vio=0.033
  - Institutions substitute for traits: STRONG_STATE coop=0.527 < BASELINE 0.564
  - Inheritance working by default: 5100 events/200yr (was 0 pre-DD05)

Post-DD04 (Session 007, 500 pop x 200yr):
  - BASELINE: agg -0.036, coop +0.058, intel +0.071, fert +0.014, std~0.09
  - STRICT_MONOGAMY: agg -0.053, coop +0.074, intel +0.093
  - ELITE_POLYGYNY: agg -0.086, coop +0.029, intel +0.080
  - HIGH_VIOLENCE: agg -0.069, coop +0.059, intel +0.014
  - Trait diversity improved: std ~0.09 (was ~0.07) due to rare mutations

Post-DD03 (Session 006, 500 pop x 100yr):
  - BASELINE: Pop=623, Gini=0.345, violence=0.056, v-deaths=159, flees=72
  - STRICT_MONOGAMY: Pop=912, Gini=0.286, violence=0.051, v-deaths=118
  - ELITE_POLYGYNY: Pop=1248, Gini=0.327, violence=0.053, v-deaths=144
  - HIGH_VIOLENCE: Pop=490, Gini=0.367, violence=0.074, v-deaths=275

Post-DD02 (Session 005, 3 seeds x 200yr x 500 pop):
  - FREE_COMPETITION: Gini=0.335, violence=0.057, unmated_m=41%, network=3.4
  - ENFORCED_MONOGAMY: Gini=0.328, violence -37%, unmated males -40%
  - ELITE_POLYGYNY: Gini=0.468, violence=0.064, unmated_m=43%
  - RESOURCE_SCARCITY: Gini=0.283, pop=609 (no longer collapses)
  - Aggression-pays-cost signal confirmed across all scenarios

================================================================================
DATE: 2026-03-15
SESSION: DD27
AUTHOR: claude
TYPE: CODE
SUMMARY: Trait completion — 26 to 35 heritable traits (scientific ceiling)
================================================================================

DETAILS:
  Added 9 new heritable traits in 5 groups:
    G1: physical_strength (h²=0.60), endurance (h²=0.50)
    G2: group_loyalty (h²=0.42), outgroup_tolerance (h²=0.40)
    G3: future_orientation (h²=0.40), conscientiousness (h²=0.49)
    G4: psychopathy_tendency (h²=0.50, default=0.2), anxiety_baseline (h²=0.40)
    G5: paternal_investment_preference (h²=0.45)

  35 new correlation pairs. 7 new config parameters. 10 new metrics.
  Behavioral effects wired into 8 engines + society.py.
  Correlation matrix forced PSD via eigenvalue clipping.

  Validation results (all PASS):
    - Psychopathy selection: mean 0.207 across 5 seeds x 200yr (stays low)
    - Sex differential: male combat 1.37x female (1.4x multiplier verified)
    - Institutions: avg law_strength 0.498 with emergent institutions
    - All 5 smoke tests pass, backward compatible

DECISIONS MADE:
  - future_discounting inverted to future_orientation (1.0=patient)
  - psychopathy_tendency defaults to 0.2 (realistic population distribution)
  - Correlation matrix PSD fix: eigenvalue clipping, diagonal re-normalization
  - physical_strength sex differential in combat only (not genetic values)

FILES CHANGED:
  models/agent.py, config.py, metrics/collectors.py, sandbox/explore.py,
  engines/conflict.py, engines/resources.py, engines/mating.py,
  engines/reproduction.py, engines/mortality.py, engines/reputation.py,
  engines/institutions.py, engines/pathology.py, models/society.py,
  docs/deep_dive_27_trait_completion.md

NEXT ACTIONS:
  - Apply autosim best_config parameters before next optimization run
  - Consider DD28: environmental heterogeneity (spatial resources)

================================================================================
END OF ARCHIVE
================================================================================
