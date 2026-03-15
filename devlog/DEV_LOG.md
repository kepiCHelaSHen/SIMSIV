# SIMSIV — DEVELOPMENT LOG
# Simulation of Intersecting Social and Institutional Variables
# Path: D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md

================================================================================
HOW TO USE THIS LOG
================================================================================

Every session, every decision, every change gets logged here.
Format for each entry:

---
DATE: YYYY-MM-DD
SESSION: [number]
AUTHOR: [human / claude / both]
TYPE: [DESIGN / CODE / EXPERIMENT / DEBUG / REFACTOR / DECISION / QUESTION]
SUMMARY: [one line]
DETAILS:
  [full notes]
DECISIONS MADE:
  [bullet list of anything locked in]
FILES CHANGED:
  [list of files touched]
NEXT ACTIONS:
  [what needs to happen next]
---

================================================================================
LOG ENTRIES
================================================================================

---
DATE: 2026-03-14
SESSION: chain_runner_dd18_26
AUTHOR: claude
TYPE: CODE
SUMMARY: DD18-DD26 Chain Runner — Proximity, Migration, Leadership, Resource Types, Life Stages, Intelligence Audit, Epigenetics, Beliefs, Skills
DETAILS:
  Executed 9 deep dives (DD18-DD26) in continuous chain runner mode.

  DD18 (Proximity Tiers): Three-tier proximity model — household/neighborhood/band.
  Proximity-weighted conflict targeting, mate evaluation, cooperation sharing, gossip noise.
  Society gets household_of() and refresh_neighborhoods() methods.
  8 new config params, 4 new metrics.

  DD19 (Migration): Emigration push factors (resource stress, ostracism, unmated, overcrowding)
  and immigration pull factors (resource surplus, vacancy). Agents track origin_band_id,
  immigration_year, generation_in_band. Runs at step 6.3. 12 new config params, 4 new metrics.

  DD20 (Leadership): War leader (dominance-based) and peace chief (prestige-based) per faction.
  War leaders boost faction aggression, combat bonus, deterrence. Peace chiefs mediate
  intra-faction conflict, boost sharing. 9 new config params, 3 new metrics.

  DD21 (Resource Types): Three resource types — subsistence (perishable, 0.4 retention),
  tools (durable, 10% decay), prestige goods (5% decay). Tool production multiplier,
  intra-band trade, tool looting in conflict, prestige goods mate signal.
  11 new config params, 5 new metrics.

  DD22 (Life Stages): Five computed stages — CHILDHOOD/YOUTH/PRIME/MATURE/ELDER.
  Youth +25% conflict, mature -20%, elder -50%. Prime parenting +20%.
  Elder norm anchor slows institutional drift. Expanded memory for mature/elder.
  10 new config params, 6 new metrics.

  DD23 (Intelligence Audit): Diminishing returns on intelligence competitive weight:
  min(intel^0.7, 0.8) * 0.25. Prevents intelligence runaway (+0.05/100yr → stable).

  DD24 (Epigenetics): Transgenerational stress load from scarcity/epidemic/trauma.
  Epigenetic sigma boost amplifies offspring trait mutation. Trauma contagion spreads
  from high-trauma agents to contacts. Faction trauma buffer for strong factions.
  11 new config params, 4 new metrics.

  DD25 (Beliefs): 5 non-heritable belief dimensions [-1,+1]: hierarchy, cooperation_norm,
  violence_acceptability, tradition_adherence, kinship_obligation. Initialized from traits
  + parent beliefs at maturation. Evolves via social influence (prestige-biased),
  experience, and cultural mutation every 3 ticks. Effects on conflict (violence_acceptability),
  resources (cooperation_norm, kinship_obligation), mating (endogamy), institutions
  (belief aggregate drift). Ideological tension and belief revolution detection.
  7 new config params, 9 new metrics.

  DD26 (Skills): 4 non-heritable skill domains [0-1]: foraging, combat, social, craft.
  Initialized at maturation from intelligence + parent transmission. Grows through
  exercise, decays without use. Foraging multiplies effective intelligence in resource
  competition. Combat adds to power calculation. Social boosts gossip and mate assessment.
  Craft multiplies tool production. Faction-based mentoring system.
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
---

---
DATE: 2026-03-14
SESSION: chain_runner_dd17
AUTHOR: claude
TYPE: CODE
SUMMARY: DD17 Medical History and Pathology — heritable conditions, trauma, pathology engine
DETAILS:
  Created new pathology engine that runs at step 6.5 (between mortality and
  institutions). Added 5 heritable condition risks (cardiovascular, mental_illness,
  autoimmune, metabolic, degenerative) to HERITABLE_TRAITS, bringing total to 26.

  Condition activation is probability-based: base_risk * triggers.
  Triggers include age, resource stress, childhood trauma, scarcity, and conflict.
  Each condition has distinct behavioral effects wired into existing engines:
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
  - models/agent.py (5 condition risk traits, active_conditions set, trauma_score, medical_history, HERITABLE_TRAITS expanded to 26, TRAIT_HERITABILITY expanded, correlation matrix expanded, create_initial_population low-mean condition risks)
  - engines/pathology.py (NEW: condition activation, remission, effects, trauma)
  - engines/__init__.py (added PathologyEngine export)
  - simulation.py (added pathology engine at step 6.5)
  - engines/mortality.py (autoimmune → epidemic vulnerability)
  - engines/conflict.py (degenerative → flee threshold)
  - engines/resources.py (metabolic → resource penalty)
  - engines/mating.py (health signal → mate choice)
  - config.py (12 new params)
  - metrics/collectors.py (7 new metrics)
  - docs/deep_dive_17_medical.md (new)
  - STATUS.md, CHAIN_PROMPT.md (updated)
NEXT ACTIONS:
  - All deep dives DD14-DD17 complete
  - Phase C complete
  - Ready for v2 planning or further extensions
---

---
DATE: 2026-03-14
SESSION: chain_runner_dd16
AUTHOR: claude
TYPE: CODE
SUMMARY: DD16 Developmental Biology — genotype/phenotype split, nature vs nurture
DETAILS:
  Implemented the formal nature vs nurture model. Key architectural change:
  agents now have TWO layers — genotype (stored at birth, never modified) and
  phenotype (expressed values, modified at maturation by environment).

  breed() now reads genotype from parents (not phenotype), so environmental
  effects on parents don't permanently corrupt the gene pool. A cooperative
  person raised violently may behave aggressively, but their children inherit
  the cooperative genotype.

  Maturation event fires at age 15:
  1. Resource environment: well-resourced → +intelligence, +impulse_control;
     deprived → +aggression, +risk_tolerance
  2. Parental modeling: parent cooperation → child cooperation boost
  3. Orphan effect: +aggression, -trust capacity
  4. Childhood trauma: parent death before age 10 → behavioral instability
  5. Peer group: conformity_bias gates peer influence (30% of parental)
  6. Birth order: firstborn +conscientiousness, later-born +novelty/risk

  Orchid/dandelion mechanism: mental_health_baseline moderates sensitivity.
  Low mental_health (orchid): dramatic response to both good and bad environments.
  High mental_health (dandelion): stable regardless of environment.

  Childhood resource quality tracked as running average ages 0-5.
  All trait modifications capped at ±0.10 (significant but not overwhelming).

  Validation: 100 pop x 20yr seed 42 — stable at 116, Gini 0.32, violence 0.03.
DECISIONS MADE:
  - Genotype stored as dict, not 21 separate fields
  - Maturation placed in mortality engine (already handles aging)
  - Peer traits precomputed once per tick from children aged 5-16
  - Founding population skips maturation (no genotype stored)
  - Birth order counted from one parent only (avoids double-counting)
FILES CHANGED:
  - models/agent.py (genotype dict, developmental fields, breed() genotype reads)
  - engines/mortality.py (maturation event, childhood trauma, _apply_maturation method)
  - engines/resources.py (childhood_resource_quality tracking during ages 0-5)
  - config.py (7 new params: developmental_plasticity_enabled, childhood_resource_effect, parental_modeling_effect, orphan_aggression_boost, peer_influence_effect, critical_period_years, birth_order_effect)
  - metrics/collectors.py (3 new metrics: maturation_events, childhood_trauma_rate, avg_childhood_resource_quality)
  - docs/deep_dive_16_development.md (new)
  - STATUS.md, CHAIN_PROMPT.md (updated)
NEXT ACTIONS:
  - Proceed to DD17 (Medical History and Pathology)
---

---
DATE: 2026-03-14
SESSION: chain_runner_dd15
AUTHOR: claude
TYPE: CODE
SUMMARY: DD15 Extended Genomics — 21 heritable traits with h²-weighted inheritance
DETAILS:
  Expanded heritable trait system from 8 to 21 traits. Each trait has a per-trait
  heritability coefficient (h²) from behavioral genetics literature. Breed() now uses:
    child_val = h² * parent_midpoint + (1 - h²) * pop_mean + mutation
  This means low-h² traits (longevity_genes=0.25) regress strongly to population mean
  while high-h² traits (intelligence_proxy=0.65) track parents closely.

  New traits and their engine wiring:
  - longevity_genes → mortality (death age +10yr, health decay -40% past 50)
  - disease_resistance → mortality (epidemic vulnerability -50%)
  - physical_robustness → conflict (damage absorption -40%, combat power)
  - pain_tolerance → conflict (flee threshold boost, combat power)
  - mental_health_baseline → conflict (stress-aggression moderation -50%)
  - emotional_intelligence → mating, resources, reputation (trust +30%, gossip +30%, bluff detection +30%)
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
  - heritability_by_trait config param: empty dict = use defaults from TRAIT_HERITABILITY
  - All trait effects designed to be modest (small multipliers, not catastrophic)
  - Combat power weights redistributed from 0.25/0.20/0.25/0.15 to accommodate new traits
  - Dominance score computation weights redistributed similarly
FILES CHANGED:
  - models/agent.py (HERITABLE_TRAITS expansion, TRAIT_HERITABILITY dict, 21x21 correlation matrix, 13 new fields, breed() heritability model, is_fertile_with_config maturation)
  - engines/reproduction.py (pop_trait_means computation, maternal_investment wiring)
  - engines/mortality.py (longevity_genes, disease_resistance)
  - engines/conflict.py (impulse_control, mental_health, empathy, pain_tolerance, physical_robustness, dominance_drive)
  - engines/mating.py (emotional_intelligence)
  - engines/resources.py (empathy sharing, dominance_drive, emotional_intelligence trust/bluff)
  - engines/reputation.py (emotional_intelligence gossip)
  - engines/institutions.py (conformity_bias)
  - config.py (heritability_by_trait)
  - metrics/collectors.py (13 new trait means)
  - docs/deep_dive_15_genomics.md (new)
  - STATUS.md, CHAIN_PROMPT.md (updated)
NEXT ACTIONS:
  - Proceed to DD16 (Developmental Biology)
  - Then DD17 (Medical/Pathology)
---

---
DATE: 2026-03-13
SESSION: 001
AUTHOR: both
TYPE: DESIGN + SCAFFOLDING
SUMMARY: Project initiated. Directory scaffold built. Design Q&A session begun.
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
    - Time step: annual tick for v1 (revisit in Phase B deep dives)
    - Runtime: kill the compute — no hard ceiling, optimize later

  AGENT MODEL:
    - Traits ARE heritable (parent → offspring blend + Gaussian noise)
    - Heritable traits (v1): aggression, cooperation, attractiveness_base,
      status_drive, risk_tolerance, jealousy_sensitivity, fertility_base,
      intelligence_proxy
    - Non-heritable (earned): social_trust, reputation, pair_bond_status
    - Mutation: YES — Gaussian noise σ=0.05 per heritable trait per generation
    - Decision model: HYBRID — probabilistic weights with utility tiebreakers
    - Agent memory: YES — lightweight reputation ledger per agent pair
      (trust scores updated by cooperation/defection/conflict history)
    - Trait representation: CONTINUOUS (0.0-1.0) — not archetypes
    - Mate value: DYNAMIC — f(health, status, resources, age)

  MATING SYSTEM:
    - Default: UNRESTRICTED COMPETITION (null hypothesis baseline)
    - All variants configurable as experimental overlays
    - Deep dive on mating system = Phase B priority #1

  RESOURCE MODEL:
    - Deep dive in Phase B — v1 uses two-dimensional (survival + status)
    - Architecture must support future expansion

  CONFLICT MODEL:
    - Deep dive in Phase B — v1 implements all standard triggers
    - Architecture must be modular and replaceable

  INSTITUTIONS:
    - Deep dive in Phase B — v1 uses toggle/hybrid approach
    - Designed so institutions can strengthen/erode from agent outcomes

  OUTPUT:
    - CSV + matplotlib charts (PNG) + narrative text summary
    - All runs auto-compared to free-competition baseline
    - Prompts stored in prompts/ directory
    - Artifacts stored in artifacts/ directory

  PHILOSOPHY:
    - Skeleton-first: build working end-to-end sim, then do deep dives
    - Phase A = skeleton with defensible v1 defaults
    - Phase B = deep dive chains per subsystem, in this order:
        1. Mating system
        2. Resource model
        3. Conflict model
        4. Agent trait inheritance + mutation
        5. Institutions
        6. Offspring/household
        7. Memory/reputation

FILES CHANGED:
  - D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md (created, to be updated)
  - D:\EXPERIMENTS\SIM\devlog\DEV_LOG.md (this file, created)
  - All directories created (see scaffold)

NEXT ACTIONS:
  - Update CHAIN_PROMPT.md with all confirmed decisions
  - Write prompts/phase1_design.md
  - Write prompts/phase2_skeleton.md
  - Write prompts/iteration_template.md
  - Write prompts/debug_template.md
  - Write prompts/deep_dive_template.md
  - Begin Phase 1: System Design and Model Specification
---

---
DATE: 2026-03-13
SESSION: 002
AUTHOR: both
TYPE: CODE
SUMMARY: Full working skeleton built — models, 6 engines, metrics, charts, CLI.
DETAILS:
  - Built all core modules: agent.py, environment.py, society.py
  - Built all 6 engines: resources, conflict, institutions, mating, reproduction, mortality
  - Built metrics collector (25+ per-tick metrics), visualization (6-panel dashboard)
  - Built simulation.py (pure library, zero IO) and main.py (CLI entry point)
  - Added selection pressure fixes: conflict before mating, female choice penalizes
    aggression, cooperation resource networks, pair bond destabilization from violence
  - Calibrated fertility: base_conception_chance 0.3->0.5, threshold-based health modifier
  - Observed emergent boom-bust population cycles (30-40 year period)

DECISIONS MADE:
  - Tick order: env -> resources -> conflict -> mating -> reproduction -> mortality -> institutions -> metrics
  - Conflict before mating so violence = reproductive fitness cost
  - Health modifier on conception: threshold-based (full fertility above 0.5, penalty below)

FILES CHANGED:
  - All files in models/, engines/, metrics/, visualizations/
  - config.py, simulation.py, main.py, requirements.txt, .gitignore
  - CLAUDE.md, STATUS.md, MISSION.md

NEXT ACTIONS:
  - Fix remaining bugs from code review
  - Build experiment framework (scenarios, runner, summarizer)
---

---
DATE: 2026-03-14
SESSION: 003
AUTHOR: both
TYPE: CODE + DEBUG + EXPERIMENT
SUMMARY: Fixed all 5 bugs, built experiment framework, calibrated resource Gini, ran first definitive experiments.

DETAILS:
  Bug fixes (5/5):
  1. Inheritance now sees ALL deaths — institutions moved after mortality, death detection
     uses agent state (year_of_death == year) instead of event-type filtering
  2. Scarcity computed once per tick in Environment.tick(), stored as current_scarcity_level.
     All engines see identical value. Same-seed runs now fully deterministic.
  3. Global ID counter no longer resets in create_initial_population(). IDs auto-increment
     across runs — verified 0 collisions in multi-run test.
  4. Violence suppression: law_strength * (0.5 + punishment * 0.5). Law alone at 0.7
     now gives 0.35 suppression instead of 0.
  5. Config.__post_init__ wires mating_system="monogamy" -> monogamy_enforced=True.
  6. max_mates_per_male now enforced in mating engine via bond count check.

  Dead code removed:
  - Agent.is_fertile(), Agent.age_first_reproduction property, Agent.social_trust field
  - Added Agent import to institutions.py
  - Removed redundant import in society.py inject_migrants

  New metrics:
  - avg_lifespan (per-tick mean age at death)
  - mating_inequality (Gini of male offspring counts)
  - pop_growth_rate, civilization_stability (CSI), social_cohesion (SCI)

  Resource engine calibration:
  - Equal/competitive split: 70/30 -> 40/60
  - Competitive weights squared to amplify differences
  - Competitive weight factors: intelligence (0.3) + status (0.3) + age (0.2) + wealth (0.2)
  - Elite privilege: multiplicative -> additive with cap at 2x base per-agent share
  - Result: baseline Gini 0.13 -> 0.25 (realistic for pre-agricultural)
  - ELITE_POLYGYNY Gini 0.97 (blowout) -> 0.42 (realistic for stratified societies)

  Experiment framework built:
  - experiments/scenarios.py — 8 named scenario configs
  - experiments/runner.py — ExperimentRunner with run_scenario, run_all, parameter_sweep,
    compare_to_baseline, save_results
  - experiments/summarizer.py — NarrativeSummarizer + SimIntegrityChecker
  - Pair bond growth: diminishing returns (0.05 at 0, 0.01 at 0.8)
  - scarcity_event_probability added to config.py, wired into environment.py

  Priority #1 definitive run (5 seeds, 200 years, pop 500):
    FREE_COMPETITION:  Gini=0.237, violence=0.057, unmated_m=38%, child_surv=83%
    ENFORCED_MONOGAMY: violence -36%, unmated males -42%, pop +1.5%
    ELITE_POLYGYNY:    Gini +74% (0.41), violence +8%, child_surv +6%

  Female choice strength sweep (0.1-0.9, 3 seeds, 200 years):
    Signal exists but weak: aggression drops ~1.8% more at fcs=0.9 vs 0.1
    Cooperation rises ~4.5% across ALL settings (from resource networks, not choice)
    Suggests mating deep dive needed to strengthen sexual selection pressure

DECISIONS MADE:
  - Engine order updated: institutions now after mortality (for inheritance)
  - Resource Gini calibrated: 40/60 split, squared weights, capped elite bonus
  - Baseline Gini ~0.25 accepted as realistic for pre-agricultural society
  - Female choice mechanism flagged for strengthening in mating deep dive

FILES CHANGED:
  - models/agent.py — removed dead code, ID counter fix, reset_id_counter warning
  - models/environment.py — scarcity computed once per tick
  - models/society.py — cleaned imports
  - config.py — __post_init__, scarcity_event_probability
  - engines/conflict.py — suppression formula
  - engines/institutions.py — Agent import, state-based death detection
  - engines/mating.py — max_mates_per_male enforcement, bond diminishing returns
  - engines/resources.py — 40/60 split, squared weights, capped elite bonus
  - engines/mortality.py — (unchanged, benefits from scarcity fix)
  - metrics/collectors.py — avg_lifespan, mating_inequality, CSI, SCI, pop_growth_rate
  - simulation.py — reordered institutions after mortality
  - experiments/scenarios.py (new)
  - experiments/runner.py (new)
  - experiments/summarizer.py (new)
  - STATUS.md, AUTOSIM.md (new)

NEXT ACTIONS:
  - Mating deep dive (prompts/deep_dive_01_mating.md)
  - Strengthen female choice sexual selection mechanism
  - Investigate RESOURCE_SCARCITY and HIGH_VIOLENCE_COST population collapses
---

---
DATE: 2026-03-14
SESSION: 004
AUTHOR: both
TYPE: CODE
SUMMARY: Mating Deep Dive (DD01) — EPC, paternity, male competition, multi-bond support.
DETAILS:
  See STATUS.md DD01 section for full details.
  Structural migration from pair_bond_id to partner_ids list.
  Extra-pair copulation, paternity uncertainty, male contests, mourning.
  6 new metrics, 9 new config params.

FILES CHANGED:
  - models/agent.py — bond management overhaul
  - engines/mating.py — full rewrite (5-phase)
  - engines/reproduction.py — EPC-aware conception
  - engines/conflict.py — multi-bond rival detection
  - engines/mortality.py — simplified (bond cleanup centralized)
  - engines/institutions.py — state-based death detection
  - config.py — 9 DD01 params
  - metrics/collectors.py — 6 DD01 metrics

NEXT ACTIONS:
  - Resource deep dive (DD02)
---

---
DATE: 2026-03-14
SESSION: 005
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Resource Deep Dive (DD02) — aggression penalty, cooperation networks, wealth ceiling, child investment.

DETAILS:
  Full resource engine rewrite (8-phase architecture):
    Phase 0: Kin trust maintenance (parent-child trust +0.02/yr, bootstraps networks)
    Phase 1: Decay existing resources (configurable retention)
    Phase 2: Distribute survival resources (25% equal floor / 75% competitive)
    Phase 3: Child investment costs (parents pay per dependent child)
    Phase 4: Cooperation sharing (amplified mutual aid with trust growth)
    Phase 5: Status distribution (cooperation-weighted, network-boosted)
    Phase 6: Elite privilege (status compounding, capped)
    Phase 7: Taxation / redistribution (optional, gated by law_strength)
    Phase 8: Subsistence floor (minimum resource guarantee)

  Key design changes:
  - Competitive weights cubed (was squared) for stronger differentiation
  - Equal floor reduced 40% → 25% for larger competitive pool
  - Aggression production penalty: fighters get 18% fewer resources
  - Cooperation network bonus: 0.05/ally in competitive weight, cap 5
  - Kin trust: parent-child relationships seed cooperation networks organically
  - Child investment: 0.5 resources/child/year, scaled by paternity confidence
  - Wealth diminishing returns (power 0.7): soft ceiling
  - Subsistence floor: prevents scarcity death spirals
  - Configurable scarcity severity (0.6, was hardcoded 0.4)
  - Taxation system: top quartile taxed, redistributed to bottom quartile

  Results (3 seeds, 200yr, 500 pop):
    FREE_COMPETITION:  Gini 0.237 → 0.335 (+41%)
    ELITE_POLYGYNY:    Gini 0.411 → 0.468 (+14%)
    ENFORCED_MONOGAMY: Gini ~0.237 → 0.328 (differentiated from baseline)
    RESOURCE_SCARCITY: collapsed (~30) → 609 pop (FIXED)
    Cooperation networks: 0.5 → 3.3 avg allies

  Aggression-pays-cost signal confirmed:
    High agg quartile: 2.8 res, 0.8 offspring, 28% bonded
    Low agg quartile: 3.4 res, 1.0 offspring, 32% bonded

DECISIONS MADE:
  - Resource engine is 8-phase (kin trust → decay → distribute → child invest →
    share → status → elite → tax → floor)
  - Competitive weights cubed, not squared
  - Equal floor 25%, competitive 75%
  - Kin trust bootstraps cooperation networks (solves chicken-and-egg)
  - Scarcity severity configurable (default 0.6 instead of 0.4)
  - Child investment creates mating-resource inequality link
  - Taxation off by default, gated by law_strength

FILES CHANGED:
  - engines/resources.py — full rewrite (8-phase)
  - config.py — 12 DD02 params
  - models/environment.py — configurable scarcity_severity
  - metrics/collectors.py — 3 DD02 metrics
  - experiments/scenarios.py — updated RESOURCE_SCARCITY
  - docs/deep_dive_02_resources.md (new) — design decisions document
  - STATUS.md — updated
  - devlog/DEV_LOG.md — this entry

NEXT ACTIONS:
  - Deep Dive 03 — Conflict model
  - Consider DD02 parameter sweep for calibration refinement
  - Test RESOURCE_ABUNDANCE and HIGH_VIOLENCE_COST with DD02 changes
---

---
DATE: 2026-03-14
SESSION: 006
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Conflict Deep Dive (DD03) — network deterrence, flee response, scaled consequences, subordination, bystander trust.

DETAILS:
  Full conflict engine rewrite with 6 new mechanics:

  1. Network deterrence:
     - Precompute ally counts (trust > 0.5) per agent
     - Initiation suppression: total_p *= 1/(1 + allies * 0.05)
     - Target selection: weight *= 1/(1 + target_allies * deterrence_factor)
     - Agents embedded in dense trust networks fight less and are picked less

  2. Flee response:
     - Low risk_tolerance targets (< flee_threshold=0.3) can escape combat
     - Flee chance: (1 - risk_tolerance) * 0.5
     - Small status shift only (no violence) — creates avoidance niche
     - 72 flee events in baseline run

  3. Scaled consequences:
     - power_diff = |agg_power - tgt_power| / (total + 0.01)
     - scale_factor = 0.7 + power_diff * 1.6
     - Close fights (diff~0): 0.7x consequences
     - Stomps (diff~0.5): 1.5x consequences + higher death chance
     - Death: effective_death_chance = base * (0.5 + power_diff)

  4. Subordination:
     - Losers get conflict_cooldown = max(current, cooldown_years)
     - Cooldown decays 1/yr at tick start
     - During cooldown: initiation prob *= subordination_dampening (0.5)
     - 4.5% of population in cooldown at any time (baseline)

  5. Bystander trust:
     - Up to bystander_count (3) witnesses per conflict
     - Each: remember(aggressor, -0.08)
     - Allied witnesses (trust of target > 0.6): extra -0.1
     - Creates social cost of violence beyond direct combatants

  6. Violence death fix:
     - Pre-DD03: conflict engine only emitted "conflict" events, not "death"
     - Metrics counted deaths by type=="death" → showed 0 violence deaths
     - Fix: emit proper "death" event + "conflict" event on lethal outcome
     - Now: 159 violence deaths properly logged (baseline)

  Also added: resource advantage in combat (combat_resource_factor),
  strength assessment (cowardly aggressors avoid healthy targets),
  resource envy in targeting (richer targets = more tempting).

  Results (500 pop, 100yr):
    BASELINE:         Pop=623, v-deaths=159, flees=72, cooldown=4.5%
    STRICT_MONOGAMY:  Pop=912, v-deaths=118, flees=31
    ELITE_POLYGYNY:   Pop=1248, v-deaths=144, flees=32
    HIGH_VIOLENCE:    Pop=490, v-deaths=275, aggression=0.434 (vs 0.472 baseline)

  HIGH_VIOLENCE aggression 0.434 confirms violence creates real selection
  pressure when costs are high (0.038 drop from baseline).

  Deep dive prompts written for DD04-DD07:
    - deep_dive_04_genetics.md (inheritance, mutation, sexual dimorphism)
    - deep_dive_05_institutions.md (institutional drift, norm enforcement)
    - deep_dive_06_household.md (childhood, fertility, grandparents)
    - deep_dive_07_reputation.md (gossip, trust decay, social networks)

DECISIONS MADE:
  - Conflict engine adds 6 new mechanics (see details above)
  - Combat power: aggression(0.25) + status(0.20) + health(0.25) + risk(0.15) +
    resource_edge(0.1) + intelligence(0.05) + ally_bonus
  - Flee creates evolutionary niche, not just reduced conflict
  - Subordination creates temporary dominance hierarchies
  - Bystander effects make violence socially costly beyond the dyad
  - Violence death now properly tracked in metrics

FILES CHANGED:
  - engines/conflict.py — full rewrite (315 lines)
  - models/agent.py — added conflict_cooldown field
  - config.py — 9 DD03 params
  - metrics/collectors.py — 4 DD03 metrics
  - docs/deep_dive_03_conflict.md (new) — design decisions document
  - prompts/deep_dive_03_conflict.md (new) — deep dive prompt
  - prompts/deep_dive_04_genetics.md (new) — genetics prompt
  - prompts/deep_dive_05_institutions.md (new) — institutions prompt
  - prompts/deep_dive_06_household.md (new) — household prompt
  - prompts/deep_dive_07_reputation.md (new) — reputation prompt
  - STATUS.md — updated
  - devlog/DEV_LOG.md — this entry

NEXT ACTIONS:
  - Deep Dive 04 — Genetics (trait inheritance, mutation, selection visibility)
  - Consider HIGH_VIOLENCE parameter sweep to find aggression equilibrium
  - Run longer (200yr+) baseline to verify trait drift patterns
---

---
DATE: 2026-03-14
SESSION: 007
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Genetics Deep Dive (DD04) — parent weight variance, rare mutations, stress mutation, per-trait metrics.

DETAILS:
  Refined inheritance model and added trait evolution tracking:

  1. Parent weight variance:
     - breed() now uses random parent blend: w ~ clip(N(0.5, 0.1), 0.1, 0.9)
     - Each trait gets independent weight per child (not exact 50/50)
     - More realistic — recombination isn't perfectly symmetric
     - Slightly reduces selection speed but maintains variation

  2. Rare large mutations:
     - 5% chance per trait per birth of using sigma=0.15 (3x normal)
     - Maintains genetic diversity against selection pressure
     - Post-DD04 trait std ~0.09 (was ~0.07) — prevents trait fixation

  3. Stress-induced mutation:
     - During scarcity, mutation sigma amplified by up to 1.5x
     - sigma *= 1.0 + (stress_multiplier - 1.0) * scarcity_level
     - breed() now accepts scarcity parameter from environment
     - Increases variation under environmental pressure

  4. Population-derived migrant traits:
     - migrant_trait_source="population" (default) samples from current
       trait distribution instead of uniform [0.2, 0.8]
     - Prevents rescue migrants from diluting evolved populations
     - Falls back to uniform if pop < 5

  5. Per-trait evolution tracking:
     - All 8 heritable traits now tracked in metrics
     - trait_std for aggression and cooperation (diversity monitoring)
     - max_generation tracking (generational depth)
     - Total: 9 new metric columns

  Design decisions (NOT implemented, with reasoning):
  - Correlation enforcement in breed(): NO — natural decay is correct,
    emergent correlations from co-selection are the interesting signal
  - Sex-specific inheritance: NO — ~12 generations insufficient for
    dimorphism, cross-sex inheritance correctly dilutes differential selection
  - Trait expansion: NO — 8 traits sufficient, more would dilute selection
  - Per-trait heritability coefficients: NO — adds complexity without payoff
  - Logistic clip: NO — hard clip [0,1] is fine, overengineering otherwise

  Baseline analysis (200yr, seed=42):
    Pre-DD04: agg -0.046, coop +0.074, intel +0.079, std ~0.07
    Post-DD04: agg -0.036, coop +0.058, intel +0.071, std ~0.09
    Selection slightly slower (parent variance adds noise) but diversity higher.

  Scenario comparison (200yr):
    BASELINE:         agg -0.036, coop +0.058, intel +0.071
    STRICT_MONOGAMY:  agg -0.053, coop +0.074, intel +0.093 (best coop+intel)
    ELITE_POLYGYNY:   agg -0.086, coop +0.029, intel +0.080 (best anti-agg)
    HIGH_VIOLENCE:    agg -0.069, coop +0.059, intel +0.014 (stress kills intel)

  Key insight: each mating system creates distinctive trait evolution profiles.
  Monogamy selects for cooperation/intelligence. Polygyny selects hardest against
  aggression (intense male competition). Violence selects against aggression but
  also suppresses intelligence selection.

DECISIONS MADE:
  - Parent weight variance = 0.1 (random blend, not exact 50/50)
  - Rare mutation rate = 0.05 at 3x sigma (maintains diversity)
  - Stress mutation multiplier = 1.5 (scarcity amplifies variation)
  - Migrants from population distribution (not uniform)
  - Let correlations decay naturally (no enforcement in breed())
  - No sex-specific inheritance (insufficient generations)
  - No trait expansion (8 traits sufficient)

FILES CHANGED:
  - models/agent.py — breed() rewritten (parent variance, rare mutation, stress)
  - models/society.py — inject_migrants() population-derived traits
  - engines/reproduction.py — pass scarcity to breed()
  - config.py — 5 DD04 params
  - metrics/collectors.py — 9 DD04 metrics (all traits + diversity + generation)
  - docs/deep_dive_04_genetics.md (new) — design decisions document
  - STATUS.md — updated
  - devlog/DEV_LOG.md — this entry

NEXT ACTIONS:
  - Deep Dive 05 — Institutions (institutional drift, norm enforcement)
  - Consider longer runs (500yr+) to test trait fixation boundaries
  - Parameter sweep on rare_mutation_rate to optimize diversity/selection balance
---

---
DATE: 2026-03-14
SESSION: 008
AUTHOR: both
TYPE: CODE + EXPERIMENT
SUMMARY: Institutions Deep Dive (DD05) — institutional drift, norm enforcement, emergent formation, property rights, enhanced inheritance.

DETAILS:
  Full institution engine rewrite with 4 phases:

  1. Institutional drift:
     - law_strength evolves based on cooperation vs violence balance
     - coop_pressure = max(0, avg_coop - 0.4) * boost (default 2.0)
     - violence_pressure = violence_rate * decay (default 3.0)
     - Inertia creates path dependency (harder to change at extremes)
     - drift_rate = 0.0 by default (backward-compatible)
     - With drift_rate=0.02: law grows 0 -> 0.48 over 200yr
     - VPS and property_rights track law proportionally (0.7x and 0.5x)

  2. Norm enforcement:
     - Active polygyny detection under monogamy_enforced
     - Detection probability: law_strength * 0.5
     - Penalties: reputation and resources scaled by law_strength
     - In practice rare because mating engine prevents bond formation

  3. Emergent institution formation:
     - Violence punishment emerges after 5yr of violence_rate > 0.08
     - Mate limit reduces after 8yr of top-10%/bottom-50% offspring > 3x
     - 24 emergence events in EMERGENT scenario over 200yr
     - emergent_institutions_enabled = False by default

  4. Property rights:
     - Modulates conflict resource looting: loot = 0.5 * (1 - property_rights)
     - One-line change in conflict engine
     - Tracks law_strength when drift enabled

  Enhanced inheritance:
  - Changed inheritance_law_enabled default from False to True
    (resources no longer vanish on death — 5100 events in baseline)
  - Added "trust_weighted" inheritance model: proportional to trust
  - Added inheritance_prestige_fraction: heirs inherit status boost
  - Partners prioritized over offspring in heir list

  Two new scenarios:
  - STRONG_STATE: law=0.8, vps=0.7, prop_rights=0.5, tax=0.15, monogamy
  - EMERGENT_INSTITUTIONS: all start at 0, drift enabled, emergence enabled

  Results (500 pop, 200yr):
    BASELINE:          Pop=609, Gini=0.306, Vio=0.054, Law=0.000
    ENFORCED_MONOGAMY: Pop=740, Gini=0.317, Vio=0.033, Law=0.700
    STRONG_STATE:      Pop=1177, Gini=0.250, Vio=0.024, Law=0.800
    EMERGENT:          Pop=941, Gini=0.268, Vio=0.050, Law=0->0.484
    HIGH_VIOLENCE:     Pop=745, Gini=0.354, Vio=0.068, Law=0.000

  Key insight: institutions substitute for individual traits.
  STRONG_STATE has lower cooperation (0.527) than BASELINE (0.564)
  because institutions enforce cooperation externally, reducing
  selection pressure on the cooperation trait.

  Emergent institutions reproduce benefits of imposed institutions:
  pop +54%, Gini -12%, property rights self-organize.

DECISIONS MADE:
  - Institutional drift formula: cooperation vs violence balance with inertia
  - drift_rate=0.0 default (backward-compatible, opt-in)
  - VPS and property_rights track law proportionally
  - Norm enforcement: active polygyny detection, not just config flag
  - Emergent: violence_punishment after 5yr streak, mate_limit after 8yr
  - Property rights: one-line conflict engine change
  - inheritance_law_enabled default True (was False — resources shouldn't vanish)
  - Config values mutated in-place by institution engine (deliberate design)
  - No bride price, kinship norms, or age hierarchy (too complex for v1)

FILES CHANGED:
  - engines/institutions.py — full rewrite (4 phases, ~200 lines)
  - engines/conflict.py — property rights loot modifier (1 line)
  - config.py — 7 DD05 params + inheritance default change
  - metrics/collectors.py — 6 DD05 metrics
  - experiments/scenarios.py — 2 new scenarios (STRONG_STATE, EMERGENT)
  - docs/deep_dive_05_institutions.md (new) — design decisions
  - STATUS.md — updated
  - devlog/DEV_LOG.md — this entry

NEXT ACTIONS:
  - Deep Dive 06 — Offspring/Household
  - Consider EMERGENT scenario parameter sweep (drift_rate, inertia)
  - Test interaction between institutions and trait evolution (longer runs)
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Household Deep Dive (DD06) — birth interval, childhood mortality, orphan model, sibling trust, grandparent bonus.

DETAILS:
  Household layer added without formal household data structure.
  Uses existing partner_ids/offspring_ids/parent_ids for all relationships.

  1. Birth spacing and fertility decline:
     - birth_interval_years=2: minimum years between births (lactational amenorrhea)
     - maternal_age_fertility_decline=0.03: 3% fertility drop per year past 30
     - max_lifetime_births=12: hard cap on births per female
     - maternal_health_cost=0.03: cumulative health cost of reproduction
     - Result: avg 3.2 lifetime births, max ~8 (realistic pre-industrial)

  2. Annual childhood mortality:
     - childhood_mortality_annual=0.02 base risk for ages 1-15
     - Resource-dependent: poor families lose more children (factor 0.5-1.5)
     - Scarcity amplification: childhood mortality rises during scarcity
     - ~2-5 deaths/year in baseline (128 over 50yr at 200 pop)

  3. Orphan model:
     - orphan_mortality_multiplier=2.0: double mortality for parentless children
     - No formal adoption (subsistence floor still provides minimum resources)
     - Tracked in metrics: orphan_count, orphan_deaths

  4. Grandparent effects:
     - grandparent_survival_bonus=0.05: reduces infant and childhood mortality
     - Checks maternal grandparents for living status
     - Implements partial "grandmother hypothesis"

  5. Sibling trust:
     - sibling_trust_growth=0.01: co-living siblings build mutual trust
     - Added to resources.py Phase 0 alongside parent-child kin trust
     - Seeds within-family cooperation networks

  Design decisions NOT implemented (with reasoning):
  - Childhood development model: deferred (double-counts with genetic inheritance)
  - Formal household structure: unnecessary (implicit tracking sufficient)
  - Birth order effects: low payoff for complexity
  - Institutional orphan care: deferred (too complex for current model)
  - Extended kin mate value bonus: needs family prestige metric first

DECISIONS MADE:
  - Household is implicit — no new data structure needed
  - Birth interval 2yr (lactational amenorrhea analog)
  - Maternal age decline gradual (not binary window)
  - Grandparent bonus at birth AND during childhood
  - Sibling trust in resources Phase 0 (alongside kin trust)
  - 8 new config params, 6 new metrics

FILES CHANGED:
  - engines/reproduction.py — birth interval, age decline, birth cap, health cost
  - engines/mortality.py — childhood mortality, orphan multiplier, grandparent bonus
  - engines/resources.py — sibling trust growth in Phase 0
  - models/agent.py — last_birth_year, lifetime_births fields
  - config.py — 8 DD06 params
  - metrics/collectors.py — 6 DD06 metrics
  - docs/deep_dive_06_household.md (new) — design decisions
  - STATUS.md — updated
  - devlog/DEV_LOG.md — this entry

NEXT ACTIONS:
  - Deep Dive 07 — Reputation (gossip, trust decay, social networks)
  - Continue DD07-DD14 chain execution
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Reputation Deep Dive (DD07) — gossip, trust decay, dead cleanup, aggregate reputation.

DETAILS:
  New reputation engine (engines/reputation.py) with 4 phases:

  1. Trust decay:
     - All trust entries drift toward 0.5 at trust_decay_rate=0.01/yr
     - Extreme values decay slower: effective = rate * (1 - |dist| * 0.5)
     - Deep trust at 0.9 takes ~50yr to fade; mild trust at 0.6 fades in ~10yr

  2. Dead agent cleanup:
     - Removes dead agents from all living agents' ledgers each tick
     - Frees slots for new living connections (ledger cap 100)

  3. Gossip:
     - 10% of agents per tick share one random trust entry with one ally
     - Ally updates their ledger weighted by trust in gossiper
     - Gaussian noise (0.1 sigma) degrades info (telephone game)
     - O(n) cost — sampling-based, not quadratic

  4. Reputation update:
     - Public reputation = 70% aggregate trust + 30% existing
     - Replaces ad-hoc reputation updates; existing engines still affect
       individual trust entries which feed into aggregate

  Design decisions NOT implemented:
  - Transitive trust: too complex, gossip covers the use case
  - Explicit social graph: metrics sufficient, O(n^2) graph unnecessary
  - Homophily: no clear emergent payoff for added complexity
  - Social learning: deferred to institutional engine territory

FILES CHANGED:
  - engines/reputation.py (new) — 4-phase reputation engine
  - simulation.py — wired reputation engine as phase 8
  - config.py — 7 DD07 params
  - metrics/collectors.py — 5 DD07 metrics
  - docs/deep_dive_07_reputation.md (new) — design decisions
  - STATUS.md — updated
  - devlog/DEV_LOG.md — this entry

NEXT ACTIONS:
  - Deep Dive 08 — Prestige
  - Continue DD08-DD14 chain execution
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Prestige Deep Dive (DD08) — split current_status into prestige/dominance dual-track system.

DETAILS:
  Split single current_status into prestige_score and dominance_score:

  1. Prestige track:
     - Sources: cooperation (30%), intelligence (20%), existing prestige (20%),
       network (4%/ally), reputation (10%)
     - 60% of status pool allocated to prestige
     - Slow decay (1%/yr) — built reputation persists
     - Aggressor loses prestige (-0.02 per conflict initiated)

  2. Dominance track:
     - Sources: status_drive (30%), aggression (20%), existing dominance (30%),
       health (10%), risk_tolerance (10%)
     - 40% of status pool allocated to dominance
     - Fast decay (3%/yr) — requires ongoing enforcement
     - Conflict winners gain dominance, losers lose it

  3. Engine rewiring:
     - Combat: dominance_weight=0.7, prestige=0.3
     - Mate value: prestige_weight=0.6, dominance=0.4
     - Resource competition: prestige=0.7, dominance=0.3
     - Mating contests: dominance only (physical competition)
     - Prestige inheritance (DD05): transfers prestige, not dominance
     - Dominance deterrence: high-dominance agents less likely targeted

  4. Backward compatibility:
     - current_status remains as computed property (prestige*0.6 + dominance*0.4)
     - current_status setter distributes to both tracks
     - All external code (main.py, dashboard) works unchanged

FILES CHANGED:
  - models/agent.py — prestige_score, dominance_score fields; current_status property
  - engines/conflict.py — dominance in combat, deterrence, status shifts
  - engines/resources.py — dual-track status distribution
  - engines/mating.py — prestige in mate choice, dominance in contests
  - engines/institutions.py — prestige inheritance
  - config.py — 5 DD08 params
  - metrics/collectors.py — 5 DD08 metrics
  - docs/deep_dive_08_prestige.md (new) — design decisions

NEXT ACTIONS:
  - Deep Dive 09 — Disease
  - Continue DD09-DD14 chain execution
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Disease Deep Dive (DD09) — epidemic events with differential vulnerability.

DETAILS:
  Epidemic model added to environment + mortality engine:

  1. Epidemic trigger (environment.py):
     - Base probability 2%/yr after 20yr refractory period
     - Overcrowding multiplier above 80% capacity
     - Scarcity compounds risk (1.5x during famine)
     - Duration: 2 years peak then subsides

  2. Differential vulnerability (mortality.py):
     - Children (0-10): 3x mortality multiplier
     - Elderly (55+): 2x multiplier
     - Low health (<0.4): 2x multiplier
     - Low resources (<3.0): 1.5x multiplier
     - Intelligence: mild protective effect (0.7-1.0)
     - Base lethality: 15% per epidemic year

  3. Cross-seed validation (200 pop, 100yr):
     - Seed 42: 0 epidemics, final 487
     - Seed 123: 4 epi years, 301 deaths, final 77
     - Seed 456: 0 epidemics, final 669
     - Seed 789: 2 epi years, 187 deaths, final 145
     - Seed 999: 4 epi years, 179 deaths, final 178
     Population variance dramatically increased.

  Not implemented: immunity system, epidemic types, institutional response.

FILES CHANGED:
  - models/environment.py — epidemic state, trigger, overcrowding
  - engines/mortality.py — epidemic mortality with diff. vulnerability
  - config.py — 8 DD09 params
  - metrics/collectors.py — 2 DD09 metrics
  - docs/deep_dive_09_disease.md (new)

NEXT ACTIONS:
  - Deep Dive 10 — Seasons
  - Continue DD10-DD14 chain execution
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Seasons Deep Dive (DD10) — seasonal resource cycles, storage, birth timing.

DETAILS:
  1. Seasonal cycle: cosine wave modulation (amplitude=0.3, period=3yr default)
  2. Intelligence-mediated storage: effective_decay = base + intel * 0.2 (max 0.9)
  3. Storage cap: 20.0 max (prevents wealth runaway)
  4. Birth timing: conception ±20% with cycle phase
  5. Lean-phase conflict boost: +20% during trough
  6. Phase tracking: seasonal_phase metric for analysis

FILES CHANGED:
  - models/environment.py — seasonal phase, cycle modulation
  - engines/resources.py — storage intelligence bonus, storage cap
  - engines/reproduction.py — birth timing sensitivity
  - engines/conflict.py — lean-phase conflict boost
  - config.py — 7 DD10 params
  - metrics/collectors.py — 1 DD10 metric
  - docs/deep_dive_10_seasons.md (new)
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Coalitions Deep Dive (DD11) — coalition defense, third-party punishment, ostracism.

DETAILS:
  1. Coalition defense: allies intervene before combat (~95/50yr)
  2. Third-party punishment: altruistic punishment at personal cost (~2/50yr)
  3. Ostracism: low-reputation excluded from sharing (rare in baseline)

FILES CHANGED:
  - engines/conflict.py — coalition defense + third-party punishment
  - engines/resources.py — ostracism exclusion
  - config.py — 9 DD11 params
  - metrics/collectors.py — 3 DD11 metrics
  - docs/deep_dive_11_coalitions.md (new)
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Signaling Deep Dive (DD12) — resource display, dominance bluffing, detection.

DETAILS:
  1. Resource display: 5% of resources spent, builds prestige (honest signal)
  2. Dominance bluff: low-dom + risk-tolerant + aggressive agents attempt (5%/yr)
  3. Detection: intelligence-gated, 30% base * intel * distrust; ~55% detection rate
  4. Caught: -0.15 rep, -0.05 prestige; Success: +0.05 dominance

FILES CHANGED:
  - engines/resources.py — signaling phase
  - config.py — 6 DD12 params
  - metrics/collectors.py — 2 DD12 metrics
  - docs/deep_dive_12_signaling.md (new)
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Demographics Deep Dive (DD13) — sex-differential mortality, childbirth death, age-specific fertility.

DETAILS:
  1. Sex-differential mortality:
     - Males age 15-40: 1.8x background mortality rate (risk-taking analog)
     - Combined with existing same-sex conflict targeting

  2. Childbirth mortality:
     - 2% per-birth maternal mortality risk
     - 3x multiplier for unhealthy mothers (health < 0.4)
     - ~11 childbirth deaths per 50yr at 200 pop (realistic pre-industrial)

  3. Age-specific fertility curve:
     - Adolescent (15-19): 60% of peak fertility (subfecundity)
     - Peak (20-28): 100% fertility
     - Post-30 decline: DD06's 3%/yr decline

FILES CHANGED:
  - engines/mortality.py — sex-differential background mortality
  - engines/reproduction.py — childbirth mortality, age-specific fertility
  - config.py — 4 DD13 params
  - metrics/collectors.py — 4 DD13 metrics
  - docs/deep_dive_13_demographics.md (new)
---

---
DATE: 2026-03-14
SESSION: 009
AUTHOR: both
TYPE: CODE
SUMMARY: Factions Deep Dive (DD14) — emergent faction detection, in-group preference, out-group conflict.

DETAILS:
  Faction system added — the final deep dive in the Phase B chain.

  1. Faction detection (society.py):
     - Connected-component analysis on mutual trust graph
     - Mutual trust > 0.65 required for same-faction edge
     - BFS traversal, runs every 5 years (not every tick)
     - Components < 3 members = factionless
     - Persistent faction IDs via majority-overlap matching (>30%)
     - 74 faction formation events in 500-pop baseline

  2. Leader-based merge:
     - After component detection, check existing faction leaders
     - If two leaders mutually trust > 0.8, merge their factions
     - Represents political alliance bringing groups together

  3. Schism:
     - Factions > 50 members face probabilistic split
     - Split by trust affinity to two seed agents (prestige-based)
     - effective_p = 1 - (1 - 0.01)^interval per detection cycle

  4. In-group sharing (resources.py Phase 4):
     - Trust threshold reduced by 0.1 for same-faction members
     - Sharing rate boosted by 20% proportional to in-group allies
     - Result: faction members share more easily and generously

  5. Out-group conflict (conflict.py _select_target):
     - 1.5x targeting weight for inter-faction targets
     - Result: violence directed outward between factions
     - Inter-faction conflict rate ~20% at peak faction count

  6. Endogamy (mating.py _form_pairs):
     - 10% mate value bonus for same-faction males
     - Mild preference, not absolute barrier

  Results (500 pop, 100yr, seed=42):
    Peak factions: 45 (year 11) — many small kin-based clusters
    Consolidation: 45 → 1-2 factions by year 60 (trust networks grow)
    vs factions OFF: avg_trust +0.096, coop_network +1.5, violence -0.020
    Factionless fraction: ~38% (not everyone in a faction)

  Key insight: factions emerge naturally from kin trust (DD02/DD06) and
  gossip (DD07) without any explicit assignment. The in-group preference
  mechanics then amplify the existing trust clustering into socially
  meaningful groups.

DECISIONS MADE:
  - Factions EMERGE from trust network — never directly assigned
  - Connected-component analysis (efficient, O(n+e))
  - Detection every 5 years (not every tick — too expensive and volatile)
  - All faction preferences are SOFT modifiers (not absolute barriers)
  - No territory, no inter-group warfare (those are v2)
  - Faction leadership = highest prestige in group (no special mechanics)

FILES CHANGED:
  - models/agent.py — faction_id field
  - models/society.py — detect_factions method, faction tracking state
  - simulation.py — wired faction detection (phase 8.5)
  - engines/resources.py — in-group sharing bonus + lower trust threshold
  - engines/conflict.py — out-group targeting preference
  - engines/mating.py — endogamy preference
  - config.py — 11 DD14 params
  - metrics/collectors.py — 6 DD14 metrics
  - docs/deep_dive_14_factions.md (new) — design decisions

NEXT ACTIONS:
  - All Phase B deep dives (DD01-DD14) COMPLETE
  - Phase C or v2 planning
---

---
DATE: 2026-03-14
SESSION: cleanup
AUTHOR: claude
TYPE: REFACTOR
SUMMARY: Project cleanup — README, requirements, tick renumber, STATUS archive, docs reorganization
DETAILS:
  Archived historical results from STATUS.md into this log (below).
  Rewrote README.md with current state (26 traits, 9 engines, 26 deep dives).
  Updated requirements.txt with version pins (added scipy, streamlit).
  Renumbered simulation.py tick loop to clean steps 1-12 (no fractions).
  Replaced all getattr(config, field, default) with direct config field access.
  Moved AUTOSIM.md and MISSION.md to docs/.
  Created docs/deep_dive_01_mating.md (was missing from docs/).
  Created prompts/README.md (index of all 26 deep dive prompts).
  Updated CHAIN_PROMPT.md file tree and change log.
  Created sandbox/explore.py (IPython harness).
FILES CHANGED:
  README.md, requirements.txt, simulation.py, STATUS.md, devlog/DEV_LOG.md,
  CHAIN_PROMPT.md, docs/AUTOSIM.md, docs/MISSION.md, docs/deep_dive_01_mating.md,
  prompts/README.md, sandbox/explore.py
---

================================================================================
ARCHIVED STATUS.MD RESULTS (moved 2026-03-14)
================================================================================

Key results (Session 009, 200 pop x 50yr) — Post-DD06 household mechanics:
  - Childhood deaths: 128 total over 50yr (~2-5/yr at 200 pop)
  - Orphans: 12 among 245 children (~5%)
  - Avg lifetime births: 3.17, max observed 8 (below cap of 12)
  - Maternal health: avg 0.427 (visible cumulative cost of reproduction)
  - Birth interval working: 2yr minimum between births
  - Maternal age decline: gradual fertility reduction past 30
  - Grandparent bonus: reduces infant/childhood mortality when grandparent alive
  - Sibling trust: co-living siblings build mutual trust (+0.01/yr)
  - Population stable at ~440 (no collapse from added mortality)

Key results (Session 008, 500 pop x 200yr) — Post-DD05 institutional comparison:
  - BASELINE: Pop=609, Gini=0.306, Vio=0.054, Law=0.000 (anarchy), inheritance working (5100 events)
  - STRONG_STATE: Pop=1177, Gini=0.250, Vio=0.024 (lowest), Law=0.800, PropRights=0.5
  - EMERGENT: Pop=941, Gini=0.268, Vio=0.050, Law grows 0->0.484 organically, 24 emergence events
  - ENFORCED_MONOGAMY: Pop=740, Gini=0.317, Vio=0.033, Law=0.700 (static)
  - Emergent institutions: law_strength self-organizes from 0 to 0.48 over 200yr
  - Institutions substitute for traits: STRONG_STATE coop=0.527 (lower than BASELINE 0.564)
  - Inheritance now working by default: 5100 events/200yr (was 0 pre-DD05)

Key results (Session 007, 500 pop x 200yr) — Post-DD04 trait evolution:
  - BASELINE: agg -0.036, coop +0.058, intel +0.071, fert +0.014, std~0.09
  - STRICT_MONOGAMY: agg -0.053, coop +0.074, intel +0.093 (strongest coop+intel)
  - ELITE_POLYGYNY: agg -0.086, coop +0.029, intel +0.080 (strongest anti-aggression)
  - HIGH_VIOLENCE: agg -0.069, coop +0.059, intel +0.014 (stress reduces intel selection)
  - Trait diversity improved: std ~0.09 (was ~0.07 pre-DD04) due to rare mutations

Key results (Session 006, 500 pop x 100yr) — Post-DD03 four-scenario comparison:
  - BASELINE: Pop=623, Gini=0.345, violence=0.056, v-deaths=159, flees=72
  - STRICT_MONOGAMY: Pop=912, Gini=0.286, violence=0.051, v-deaths=118
  - ELITE_POLYGYNY: Pop=1248, Gini=0.327, violence=0.053, v-deaths=144
  - HIGH_VIOLENCE: Pop=490, Gini=0.367, violence=0.074, v-deaths=275

Key results (Session 005, 3 seeds x 200yr x 500 pop) — Post-DD02 four-way comparison:
  - FREE_COMPETITION: Gini=0.335, violence=0.057, unmated_m=41%, network=3.4
  - ENFORCED_MONOGAMY: Gini=0.328, violence -37%, unmated males -40%
  - ELITE_POLYGYNY: Gini=0.468, violence=0.064, unmated_m=43%
  - RESOURCE_SCARCITY: Gini=0.283, pop=609 (no longer collapses)
  - Aggression-pays-cost signal confirmed across all scenarios

================================================================================
END OF LOG
================================================================================
