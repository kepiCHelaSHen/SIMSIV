# SIMSIV — World Architecture Document
# The Complete Individual Model and Hierarchical Civilization Framework
# Location: D:\EXPERIMENTS\SIM\docs\world_architecture.md
# Last Updated: 2026-03-15
# Status: Band simulation COMPLETE — DD01-DD27 all done, 35 heritable traits,
#         AutoSIM calibration score 1.000, validation passed, scenario experiments
#         running, publication plan active.
#
# PURPOSE: This document is the single authoritative reference for what has
# been built and where the project is going. Share with any AI or human
# collaborator to give a complete picture of the architecture.

================================================================================
SECTION 1 — PROJECT IDENTITY AND PHILOSOPHY
================================================================================

SIMSIV (Simulation of Intersecting Social and Institutional Variables) is a
Python agent-based simulation grounded in behavioral genetics, evolutionary
anthropology, and institutional economics. It models how human social structures
emerge from first-principles interactions among reproduction, resource competition,
status seeking, cooperation, jealousy, violence, pair bonding, and institutional
constraints.

Core principle: ALL interesting outcomes must EMERGE from agent-level rules.
Nothing is hardwired. No civilization is scripted. No outcome is predetermined.

The simulation is designed as the engine for a Civilization-style game, but the
model is built first. The quality of the model determines the quality of
everything built on top of it.

TECHNICAL STACK:
  Python 3.11+, NumPy, Pandas, Matplotlib, PyYAML, Streamlit, SciPy
  Location: D:\EXPERIMENTS\SIM
  Architecture: Pure library simulation, no IO in engines, tick() returns data

SCALE:
  Default: 500 agents, 200 years, annual tick
  Practical ceiling: 2,000 agents (O(N²) bottlenecks in conflict/mating)
  Runtime: ~35-90 seconds per seed for 500 agents / 200 years (seed-dependent)

================================================================================
SECTION 2 — THE HIERARCHICAL CIVILIZATION MODEL
================================================================================

The simulation is designed around a five-level hierarchy, each level running
its own simulator that consumes aggregate outputs from the level below.

LEVEL 1: BAND — COMPLETE (v1.0)
  Population: 50-500 individual agents
  Model: Full SIMSIV engine — every person simulated individually
  Time step: Annual tick
  Key output: Band fingerprint (15 aggregate metrics exported upward)
  Anthropological analog: Hunter-gatherer band, kinship group

LEVEL 2: CLAN — planned (v2)
  Population: 5-15 bands (~750-7,500 people represented)
  Model: Band-level aggregate dynamics — no individual agents
  Inputs: Band fingerprints from member bands
  Simulates: Trade, raiding, intermarriage, cultural drift, merger/split
  Key output: Clan fingerprint
  Anthropological analog: Extended kinship network, ~150-500 people

LEVEL 3: TRIBE — planned (v2)
  Population: 5-15 clans (~3,750-37,500 people represented)
  Model: Clan-level aggregate dynamics
  Simulates: Territorial boundaries, inter-clan warfare, trade networks,
             cultural identity formation, norm standardization
  Key output: Tribe fingerprint
  Anthropological analog: Linguistically/culturally unified group

LEVEL 4: CHIEFDOM — planned (v3)
  Population: Multiple tribes (~20,000-200,000 people represented)
  Model: Tribe-level political dynamics
  Simulates: Hereditary leadership, surplus redistribution, tribute,
             monument building, ranked society, proto-state formation
  Key output: Chiefdom fingerprint
  Anthropological analog: Ranked society with hereditary hierarchy

LEVEL 5: STATE — planned (v3+)
  Population: Multiple chiefdoms (millions represented statistically)
  Model: Pure historical forces — no individual agent simulation
  Simulates: Laws, armies, cities, taxation, bureaucracy, writing, trade empires
  Key output: State profile for world map
  Anthropological analog: This is where Civ VI starts

CRITICAL DESIGN PRINCIPLE:
  Each level ONLY communicates with the level immediately above and below it.
  Information flows UP as aggregate fingerprints.
  Pressure flows DOWN as environmental conditions.

THE BAND FINGERPRINT (15 values exported upward):
  1.  avg_aggression_index
  2.  avg_cooperation_index
  3.  resource_level
  4.  population_size
  5.  law_strength
  6.  dominant_faction_type
  7.  avg_health_index
  8.  kinship_density
  9.  cultural_identity_score
  10. avg_intelligence_index
  11. reproductive_rate
  12. institutional_stability
  13. has_war_leader
  14. leadership_quality
  15. big_man_present

================================================================================
SECTION 3 — THE BAND SIMULATION (DD01-DD27 COMPLETE)
================================================================================

The band simulation is the most complex level — it simulates every individual
person. All 27 deep dives are complete. This is the v1.0 core engine.

TICK EXECUTION ORDER (per annual step):
  1.  Environment       — scarcity shocks, seasonal cycles, epidemic triggers
  2.  Resources         — 8-phase distribution engine (3 resource types)
  3.  Conflict          — violence, deterrence, coalition defense, life stage
                          modifiers. Cross-sex targeting enabled at 0.3× weight.
  4.  Mating            — pair bond formation, dissolution (both partners drive
                          it), infidelity. Children's parent_ids → social father.
  5.  Reproduction      — h²-weighted inheritance, developmental plasticity
  6.  Mortality         — aging, health decay, natural death, childbirth death
  6.3 Migration         — voluntary emigration and immigration (DD19)
  6.5 Pathology         — condition activation, trauma accumulation (DD17).
                          Mental illness uses trauma_score — does NOT mutate traits.
  7.  Institutions      — inheritance, norm enforcement, institutional drift
                          (ENABLED by default, drift_rate=0.01), emergent
                          formation (ENABLED by default)
  8.  Reputation        — gossip, trust decay, belief updates, skill learning,
                          faction detection, neighborhood refresh
  9.  Metrics           — collect all ~130 stats for this year
  10. Equilibrium check

--------------------------------------------------------------------------------
3A. THE AGENT — 35 HERITABLE TRAITS (SCIENTIFICALLY COMPLETE)
--------------------------------------------------------------------------------

HERITABLE TRAITS — 35 total, organized by domain:

  PHYSICAL PERFORMANCE (6):
    physical_strength      [0.0-1.0]  h²~0.60  force output, combat, mate value
    endurance              [0.0-1.0]  h²~0.50  sustained capacity, foraging, childbirth
    physical_robustness    [0.0-1.0]  h²~0.50  damage absorption
    pain_tolerance         [0.0-1.0]  h²~0.45  flee threshold modifier
    longevity_genes        [0.0-1.0]  h²~0.25  lifespan extension
    disease_resistance     [0.0-1.0]  h²~0.40  epidemic vulnerability reduction

  COGNITIVE (4):
    intelligence_proxy     [0.0-1.0]  h²~0.65  resource acquisition efficiency
    emotional_intelligence [0.0-1.0]  h²~0.40  trust formation, gossip acuity
    impulse_control        [0.0-1.0]  h²~0.50  gates aggression → actual behavior
    conscientiousness      [0.0-1.0]  h²~0.49  skill maintenance, parenting, compliance

  TEMPORAL (1):
    future_orientation     [0.0-1.0]  h²~0.40  time horizon — storage, institutions, birth spacing

  PERSONALITY / TEMPERAMENT (4):
    risk_tolerance         [0.0-1.0]  h²~0.48  willingness to take risks
    novelty_seeking        [0.0-1.0]  h²~0.40  exploration, migration drive
    anxiety_baseline       [0.0-1.0]  h²~0.40  threat sensitivity, flee boost
    mental_health_baseline [0.0-1.0]  h²~0.40  stress resilience, plasticity gate

  SOCIAL ARCHITECTURE (9):
    aggression_propensity  [0.0-1.0]  h²~0.44  tendency toward conflict
    cooperation_propensity [0.0-1.0]  h²~0.40  tendency toward alliance
    dominance_drive        [0.0-1.0]  h²~0.50  active dominance hierarchy seeking
    group_loyalty          [0.0-1.0]  h²~0.42  kin selection — sacrifice for group
    outgroup_tolerance     [0.0-1.0]  h²~0.40  constitutional openness to strangers
    empathy_capacity       [0.0-1.0]  h²~0.35  altruism radius extension
    conformity_bias        [0.0-1.0]  h²~0.35  norm adoption speed
    status_drive           [0.0-1.0]  h²~0.50  motivation to seek dominance
    jealousy_sensitivity   [0.0-1.0]  h²~0.45  trigger for jealousy-driven conflict

  REPRODUCTIVE BIOLOGY (5):
    fertility_base                   [0.0-1.0]  h²~0.50  baseline reproductive capacity
    sexual_maturation_rate           [0.0-1.0]  h²~0.60  age at first reproduction variance
    maternal_investment              [0.0-1.0]  h²~0.35  quality vs quantity offspring tradeoff
    paternal_investment_preference   [0.0-1.0]  h²~0.45  good genes vs good dad female preference
    attractiveness_base              [0.0-1.0]  h²~0.50  baseline physical mate value

  PSYCHOPATHOLOGY SPECTRUM (6):
    psychopathy_tendency   [0.0-1.0]  h²~0.50  exploiter strategy (default 0.2)
    mental_illness_risk    [0.0-1.0]  h²~0.60  heritable psychiatric condition risk
    cardiovascular_risk    [0.0-1.0]  h²~0.50  heritable cardiovascular condition risk
    autoimmune_risk        [0.0-1.0]  h²~0.40  heritable immune dysfunction risk
    metabolic_risk         [0.0-1.0]  h²~0.45  heritable metabolic condition risk
    degenerative_risk      [0.0-1.0]  h²~0.35  heritable degenerative condition risk

INHERITANCE MODEL (DD15, DD27):
  child_val = h² * parent_midpoint + (1 - h²) * population_mean + mutation
  Parent weight: w ~ N(0.5, 0.1) — random blend, not always exact 50/50
  Mutation: 95% at sigma=0.05, 5% rare large jump at sigma=0.15
  Stress mutation: scarcity amplifies sigma by up to 1.5x (DD04)
  Epigenetic boost: stressed parents increase offspring mutation sigma (DD24)
  Correlation matrix: 35×35 built programmatically, PSD-verified
  breed() reads genotype — selection operates on genetic potential

GENOTYPE vs PHENOTYPE (DD16):
  Genotype: raw genetic values stored at birth, passed to offspring unchanged
  Phenotype: expressed values after developmental modification at age 15
  mental_health_baseline gates plasticity magnitude (orchid vs dandelion)

NON-HERITABLE STATE:
  health, reputation, prestige_score, dominance_score
  current_resources, current_tools, current_prestige_goods
  paternity_confidence, conflict_cooldown, trauma_score
  epigenetic_stress_load, faction_id

CULTURAL BELIEFS (DD25) — 5 dimensions [-1.0 to +1.0]:
  hierarchy_belief, cooperation_norm, violence_acceptability,
  tradition_adherence, kinship_obligation

SKILLS (DD26) — 4 domains [0.0 to 1.0]:
  foraging_skill, combat_skill, social_skill, craft_skill

LIFE STAGE (DD22) — computed from age:
  CHILDHOOD / YOUTH / PRIME / MATURE / ELDER

PROXIMITY TIERS (DD18):
  HOUSEHOLD (3-8) → NEIGHBORHOOD (up to 40) → BAND (full population)

MIGRATION (DD19):
  origin_band_id, immigration_year, generation_in_band

MEDICAL (DD17):
  active_conditions, trauma_score, medical_history (max 50 entries)

--------------------------------------------------------------------------------
3B. KEY EMERGENT FINDINGS (from scenario experiments, 2026-03-15)
--------------------------------------------------------------------------------

Source: 5 seeds × 200yr × 10 scenarios using calibrated best_config.yaml.
All findings are emergent — not scripted.

1. Cooperation + intelligence reliably selected for across all scenarios.
   Multiple independent fitness channels reward both traits.

2. Aggression reliably selected against (5 independent fitness cost channels).

3. PRELIMINARY — Gene-culture coevolution hypothesis (paper's central claim,
   currently being tested at 500yr):
   At 200yr, cooperation trait is IDENTICAL across FREE_COMPETITION (0.511),
   STRONG_STATE (0.512), and EMERGENT_INSTITUTIONS (0.511). Institutional
   governance suppresses violent BEHAVIOR immediately, but changes the underlying
   cooperation TRAIT on a centuries-long timescale. A 10-seed × 500yr run is
   currently running to test whether trait divergence appears at longer scales.
   This is the paper's central hypothesis — not yet a confirmed finding.

4. Emergent institutions self-organize: law_strength rises from 0 → 0.829
   over 200yr in EMERGENT_INSTITUTIONS scenario, driven purely by
   cooperation/violence balance feedback. No top-down scripting.

5. Monogamy reduces violence 37%, unmated males 65% vs free competition.
   Both replicate consistently across multiple calibration eras.

6. Factions emerge naturally from kin trust clusters via BFS graph traversal.

7. Elite polygyny demographic paradox: highest average lifespan (19.6yr) but
   near-zero population growth (+0.01%/yr). Excluded males suppress overall
   birth rates, canceling the elite fertility advantage. Gini rises to 0.379.

8. Resource scarcity induces cooperation: RESOURCE_SCARCITY produces the
   highest cooperation trait (0.536) of any scenario — consistent with
   interdependence theory.

9. Trait diversity maintained at σ~0.09 by rare large mutations (5% at 3×σ)
   even under strong directional selection.

10. STRONG_STATE suppresses violence ▼49% and Gini ▼40% vs baseline, with
    law self-organizing to 0.981 from a starting value of 0.8. Institutional
    effects on behavior are immediate; evolutionary effects take centuries.

--------------------------------------------------------------------------------
3C. CALIBRATION STATUS (CURRENT — as of 2026-03-15)
--------------------------------------------------------------------------------

AutoSIM Run 3 (816 experiments, ~10.5 hours, post-Phase E + Phase F fixes):
  Best score: 1.000 (all 9 metrics simultaneously in anthropological target range)
  Config file: autosim/best_config.yaml
  Previous runs: Run 1 (0.9852, pre-fixes, superseded), Run 2 (discarded)

Key calibrated parameters:
  pair_bond_dissolution_rate: 0.02    female_choice_strength:     0.34
  base_conception_chance:     0.80    mortality_base:             0.006
  childhood_mortality_annual: 0.054   epidemic_lethality_base:    0.254
  male_risk_mortality_multiplier: 2.12  aggression_production_penalty: 0.60

Held-out validation (10 seeds × 200yr × 500pop × 2 independent runs):
  Mean score: 0.934   Collapses: 0/20
  Robust (10/10): Resource Gini, Mating Inequality, Avg Cooperation, Avg Aggression
  Fragile (near boundary): Violence Death Fraction, Avg Lifetime Births,
    Pop Growth Rate, Bond Dissolution Rate
  Verdict: MOSTLY ROBUST — suitable for scenario experiments and publication

Full calibration report with citations: docs/validation.md

================================================================================
SECTION 4 — COMPLETED DEEP DIVES (DD01-DD27)
================================================================================

| DD  | System                    | Key Addition                                          |
|-----|---------------------------|-------------------------------------------------------|
| 01  | Mating                    | Multi-bond, EPC, paternity, male contests             |
| 02  | Resources                 | 8-phase engine, kin trust, aggression penalty         |
| 03  | Conflict                  | Network deterrence, flee, subordination               |
| 04  | Genetics                  | Parent variance, rare mutations, stress mutation      |
| 05  | Institutions              | Drift, emergence, property rights                     |
| 06  | Household                 | Birth spacing, childhood mortality, orphans           |
| 07  | Reputation                | Gossip, trust decay, aggregate reputation             |
| 08  | Prestige/Dominance        | Dual-track status system                              |
| 09  | Disease                   | Epidemics, differential vulnerability                 |
| 10  | Seasons                   | Resource cycles, storage                              |
| 11  | Coalitions                | Defense, third-party punishment, ostracism            |
| 12  | Signaling                 | Resource display, dominance bluffing                  |
| 13  | Demographics              | Sex-differential mortality, fertility curve           |
| 14  | Factions                  | Emergent connected-component detection                |
| 15  | Extended Genomics         | 13 new traits, real h² model, 26×26 correlation matrix|
| 16  | Developmental Biology     | Genotype/phenotype, childhood plasticity              |
| 17  | Medical History           | Pathology engine, 5 conditions, trauma                |
| 18  | Proximity Tiers           | Household/neighborhood/band interaction weighting     |
| 19  | Migration                 | Voluntary emigration/immigration                      |
| 20  | Leadership                | War leader + peace chief per faction                  |
| 21  | Resource Types            | Subsistence/tools/prestige goods differentiation      |
| 22  | Life Stages               | Youth/prime/mature/elder roles                        |
| 23  | Intelligence Audit        | Feedback loop check, diminishing returns              |
| 24  | Epigenetics               | Transgenerational stress, trauma contagion            |
| 25  | Beliefs                   | 5 cultural belief dimensions, ideology emergence      |
| 26  | Skills                    | 4 skill domains, mentoring, transmission              |
| 27  | Trait Completion          | 9 new traits (26→35), 35×35 correlation matrix, PSD  |

Phase E fixes (14): IdCounter, event window, partner index, logging, Config
  validation, mating_system wiring, ledger cleanup, dashboard, test suite

Phase F fixes (19): cross-sex conflict, mental illness trait separation,
  institutional drift defaults, EPC kin networks, bond dissolution symmetry,
  elite privilege ratchet, age consistency, status setter, storage bonuses,
  fertility range widening, cooperation norm restriction, and more

Totals: ~257 config params, ~130 metrics per tick, 9 engines,
        35 heritable traits, 5 beliefs, 4 skills, 22 tests passing

================================================================================
SECTION 5 — WORLD ARCHITECTURE (HIGHER LEVELS — PLANNED V2/V3)
================================================================================

DESIGN PHILOSOPHY FOR HIGHER LEVELS:
  Each level runs its own simulator simpler than the level below.
  Individual biography only exists at band level.
  At clan level and above, people are represented as statistics.

THE CLAN SIMULATOR (v2 — planned)
  Inputs: Band fingerprints from 5-15 member bands
  Tick: Decadal (10yr per clan tick)
  Computes: Trade, raids, intermarriage, cultural drift, alliances
  Transition: Threshold crossing — shared territory + cooperation + peace + identity
  Key open question: Does the 15-value band fingerprint carry enough state?
    Should it include variance metrics (mean + std) per key trait?

THE TRIBE SIMULATOR (v2 — planned)
  Inputs: Clan fingerprints
  Tick: Generational (25yr)
  Computes: Cultural identity, territorial boundaries, warfare, norm standardization

THE CHIEFDOM SIMULATOR (v3 — planned)
  Hereditary leadership, tribute, monument building, ranked society

THE STATE SIMULATOR (v3+ — planned)
  Formal law, standing army, urban centers, writing analog, trade empire

NOTE: v2 architecture document will be written AFTER Paper 1 is drafted.
The act of writing Paper 1's limitations section will clarify exactly what
v2 needs to specify. See docs/AI_COLLABORATOR_BRIEF.md Section 5D for the
open design questions that v2 must answer.

================================================================================
SECTION 6 — PUBLICATION PLAN
================================================================================

CENTRAL CLAIM (locked, 2026-03-15):
  "Institutional governance systematically reduces directional selection on
   heritable prosocial behavioral traits — providing computational evidence
   that institutions and genes are substitutes, not complements, in human
   social evolution."

PAPER 1 — Methods paper
  Title: "SIMSIV: A calibrated agent-based framework for studying
          gene-culture coevolution in pre-state societies"
  Target: JASSS (Journal of Artificial Societies and Social Simulation) or PLOS ONE
  Status: Validation complete. 200yr scenario experiments complete.
          500yr run in progress. Sensitivity analysis needed. Can begin writing.

PAPER 2 — Findings paper
  Target: Evolutionary Human Sciences or Behavioral Ecology
  Status: Awaiting 500yr scenario results for full analysis.

PAPER 3 — Gene-culture coevolution
  Target: Evolution and Human Behavior or Nature Human Behaviour
  Status: Central finding being tested in 500yr run currently running.

PAPER 4+ — Hierarchical emergence (requires v2/v3)

AI DISCLOSURE: "Code development aided by Claude (Anthropic); all hypotheses
               and interpretations are the author's own."
AFFILIATION:   "Independent Researcher"
PREPRINT:      arXiv after scenario experiments + sensitivity analysis complete.

================================================================================
SECTION 7 — TECHNICAL ARCHITECTURE (CURRENT FILE STRUCTURE)
================================================================================

  D:\EXPERIMENTS\SIM\
  ├── CHAIN_PROMPT.md        ← Master design doc — read first in any new session
  ├── STATUS.md              ← Current project status
  ├── README.md
  ├── config.py              ← ~257 tunable parameters (grouped by DD)
  ├── simulation.py          ← tick orchestrator (12 clean steps)
  ├── main.py                ← CLI entry point
  ├── requirements.txt       ← numpy, pandas, matplotlib, pyyaml, streamlit, scipy,
  │                             plotly, pytest
  ├── .python-version        ← 3.11
  │
  ├── models/
  │   ├── agent.py           ← Agent dataclass (35 traits, beliefs, skills, etc.)
  │   ├── society.py         ← Agent registry, faction detection, migration
  │   └── environment.py     ← Scarcity, seasons, epidemics
  │
  ├── engines/
  │   ├── resources.py       ← 8-phase + DD21 types + DD27 trait effects
  │   ├── conflict.py        ← Violence, deterrence, coalitions, cross-sex (Phase F)
  │   ├── mating.py          ← Pair bonds, EPC, symmetric dissolution (Phase F)
  │   ├── reproduction.py    ← Conception, birth, developmental biology
  │   ├── mortality.py       ← Aging, health, death
  │   ├── pathology.py       ← Conditions, trauma, epigenetics (Phase F: no trait mutation)
  │   ├── institutions.py    ← Inheritance, norms, drift (Phase F: enabled by default)
  │   └── reputation.py      ← Gossip, trust, beliefs, skills, factions
  │
  ├── metrics/
  │   └── collectors.py      ← ~130 metrics per tick
  │
  ├── experiments/
  │   ├── scenarios.py       ← 10 named scenario configs
  │   ├── runner.py          ← Multi-seed experiment execution
  │   └── summarizer.py      ← Narrative summaries, integrity checks
  │
  ├── autosim/
  │   ├── runner.py          ← Mode A optimization (simulated annealing)
  │   ├── realism_score.py   ← Composite score vs anthropological targets
  │   ├── targets.yaml       ← 9 calibration targets with sources
  │   ├── best_config.yaml   ← Score 1.000 (Run 3, 816 experiments, post-Phase F)
  │   ├── journal.jsonl      ← Run 3 experiment log (~1.61MB, 816 entries)
  │   └── archive/
  │       ├── journal_run1_pre_phase_e.jsonl
  │       └── journal_run2_pre_phase_f.jsonl
  │
  ├── dashboard/
  │   ├── app.py             ← Streamlit dashboard (Phase G overhaul in progress)
  │   ├── tabs/              ← Phase G: per-tab modules (16 tabs planned)
  │   └── components/        ← Phase G: shared constants, charts, sidebar, runner
  │
  ├── scripts/
  │   ├── validate_best_config.py  ← Held-out validation script (NEW Phase F)
  │   └── ec2_autosim.sh
  │
  ├── tests/
  │   ├── test_smoke.py      ← Core simulation smoke tests
  │   ├── test_id_counter.py ← Per-simulation IdCounter isolation (Phase E)
  │   ├── test_config.py     ← Config validation (Phase E)
  │   └── test_society.py    ← Society/event window/partner index (Phase E)
  │   (22 test cases total, all passing)
  │
  ├── docs/
  │   ├── world_architecture.md    ← THIS FILE
  │   ├── AI_COLLABORATOR_BRIEF.md ← Briefing for any AI or human collaborator
  │   ├── validation.md            ← Full calibration + validation report (citations)
  │   ├── POST_AUTOSIM_TASKS.md
  │   ├── autosim_learnings_pre_phase_e.md
  │   ├── AUTOSIM.md
  │   ├── MISSION.md
  │   └── deep_dive_01_mating.md .. deep_dive_27_trait_completion.md (27 files)
  │
  ├── devlog/
  │   ├── DEV_LOG.md               ← Phase E onwards
  │   └── archive/DEV_LOG_phase_a_to_d.md
  │
  ├── prompts/                     ← Build prompts (~37 files)
  │   ├── dashboard_overhaul.md    ← Phase G (20-block executable prompt)
  │   └── phase_e_engineering_hardening.md, deep_dive_*.md, etc.
  │
  ├── sandbox/
  │   └── explore.py
  │
  └── outputs/
      ├── experiments/             ← Scenario experiment outputs
      └── reports/

ARCHITECTURE GUARANTEES:
  - Pure library: no IO, no print statements in engines
  - Deterministic: same seed = identical results
  - Modular: engines share no state except via Society
  - No circular imports: models never import engines
  - All randomness via seeded numpy.random.Generator
  - 35×35 correlation matrix verified positive semi-definite (PSD)
  - Per-simulation IdCounter: N parallel simulations produce non-colliding IDs
  - Event window capped at 500: no OOM on long runs

NAMED SCENARIOS (10):
  FREE_COMPETITION, ENFORCED_MONOGAMY, ELITE_POLYGYNY, HIGH_FEMALE_CHOICE,
  RESOURCE_ABUNDANCE, RESOURCE_SCARCITY, HIGH_VIOLENCE_COST,
  STRONG_PAIR_BONDING, STRONG_STATE, EMERGENT_INSTITUTIONS

================================================================================
SECTION 8 — WHAT THIS IS BUILDING TOWARD
================================================================================

The ultimate goal is a Civilization-style game where every person is a real
simulated individual with a genome, a developmental history, a medical biography,
skills earned through lived experience, cultural beliefs transmitted from their
community, and a complete life story from birth to death.

Social structures — bands, clans, tribes, chiefdoms, states — emerge from what
those individuals do. Nobody writes the story.

CURRENT STATE: Band simulator v1.0 complete — DD01-DD27 done, 35 heritable traits,
calibrated to score 1.000, validated at 0.934 on held-out seeds.
This is the most complex and important level. All other levels will be simpler.

WHAT MAKES THIS DIFFERENT:
  - Civ VI: civilizations, no real people inside them
  - The Sims: people, no civilization around them
  - Dwarf Fortress: personality, no emergent biology or evolution
  - SIMSIV: real people (35 heritable traits, developmental plasticity,
    medical histories, skills, beliefs, psychopathology spectrum) inside
    real societies (emergent institutions, factions, norms, cultural transmission)

================================================================================
SECTION 9 — OPEN QUESTIONS FOR V2 DESIGN
================================================================================

These will be answered in docs/v2_clan_simulator.md, written after Paper 1 draft.

1. TEMPORAL SCALE TRANSLATION
   Band ticks at 1yr. Clan should tick at 10yr. How to bridge?

2. BAND FINGERPRINT COMPLETENESS
   Does 15 values capture enough state for realistic clan dynamics?
   Should fingerprint include variance metrics (mean + std per key trait)?

3. BAND → CLAN TRANSITION THRESHOLDS
   Sharp (threshold crossing) or gradual (continuous)?

4. CULTURAL DIVERGENCE METRIC
   How do we quantify belief vector distance between bands for cultural drift?

5. OUTGROUP_TOLERANCE IN INTER-BAND DYNAMICS
   New in DD27 — high-outgroup-tolerance bands should be more tradeable
   and less raiding-prone. How does this feed into the clan fingerprint?

6. PLAYER INTERACTION LAYER
   At which levels does the player have agency?

7. PERFORMANCE ARCHITECTURE FOR V2
   Thousands of bands in parallel — process pool? GPU vectorization?

8. CALIBRATION TARGETS FOR LEVELS 2-5
   What archaeological or ethnographic data validates clan/tribe dynamics?
   This must be answered before building — no level should be built without
   calibration targets.

================================================================================
END OF DOCUMENT
================================================================================

Version: 3.1 (Phase E + F complete, calibrated score 1.000, scenario experiments
          running, publication plan active)
Project: SIMSIV — D:\EXPERIMENTS\SIM
GitHub:  https://github.com/kepiCHelaSHen/SIMSIV
Updated: 2026-03-15
