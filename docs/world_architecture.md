# SIMSIV — World Architecture Document
# The Complete Individual Model and Hierarchical Civilization Framework
# Location: D:\EXPERIMENTS\SIM\docs\world_architecture.md
# Last Updated: 2026-03-15
# Status: Band simulation COMPLETE — DD01-DD27 all done, 35 heritable traits
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
  Runtime: ~60-90 seconds for 500 agents / 200 years / 3 seeds

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
  3.  Conflict          — violence, deterrence, coalition defense, life stage modifiers
  4.  Mating            — pair bond formation, dissolution, infidelity
  5.  Reproduction      — h²-weighted inheritance, developmental plasticity
  6.  Mortality         — aging, health decay, natural death, childbirth death
  6.3 Migration         — voluntary emigration and immigration (DD19)
  6.5 Pathology         — condition activation, trauma accumulation (DD17)
  7.  Institutions      — inheritance, norm enforcement, institutional drift
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
3B. KEY EMERGENT FINDINGS
--------------------------------------------------------------------------------

1. Cooperation + intelligence reliably selected for across all scenarios
2. Aggression reliably selected against (5 independent fitness channels)
3. Institutions substitute for traits — STRONG_STATE cooperation trait lower
4. Emergent institutions self-organize: 0 → 0.48 law strength over 200yr
5. Monogamy reduces violence 37%, unmated males 40% vs free competition
6. Factions emerge naturally from kin trust clusters
7. Elite polygyny maximizes Gini (0.468) but not violence
8. Trait diversity maintained at σ~0.09 by rare mutations
9. !Kung validation: sim violence rate 0.018 matches ethnographic ~0.02

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
| 17  | Medical History           | Pathology engine, 5 conditions, trauma               |
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

Totals: ~257 config params, ~130 metrics per tick, 9 engines (+pathology),
        35 heritable traits, 5 beliefs, 4 skills, 14 files modified in DD27

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

THE TRIBE SIMULATOR (v2 — planned)
  Inputs: Clan fingerprints
  Tick: Generational (25yr)
  Computes: Cultural identity, territorial boundaries, warfare, norm standardization

THE CHIEFDOM SIMULATOR (v3 — planned)
  Hereditary leadership, tribute, monument building, ranked society

THE STATE SIMULATOR (v3+ — planned)
  Formal law, standing army, urban centers, writing analog, trade empire

================================================================================
SECTION 6 — TECHNICAL ARCHITECTURE
================================================================================

FILE STRUCTURE:
  D:\EXPERIMENTS\SIM\
  ├── config.py              — ~257 tunable parameters (grouped by DD)
  ├── simulation.py          — tick orchestrator (12 clean steps)
  ├── main.py               — CLI entry point
  ├── requirements.txt       — numpy, pandas, matplotlib, pyyaml, streamlit, scipy
  ├── models/
  │   ├── agent.py           — Agent dataclass (35 traits, beliefs, skills, etc.)
  │   ├── society.py         — Agent registry, faction detection, migration
  │   └── environment.py     — Scarcity, seasons, epidemics
  ├── engines/
  │   ├── resources.py       — 8-phase + DD21 types + DD27 trait effects
  │   ├── conflict.py        — Violence, deterrence, coalitions, DD27 strength/loyalty
  │   ├── mating.py          — Pair bonds, EPC, DD27 paternal_investment_preference
  │   ├── reproduction.py    — Conception, birth, developmental biology, DD27
  │   ├── mortality.py       — Aging, health, death, DD27 endurance effects
  │   ├── pathology.py       — Conditions, trauma, epigenetics, DD27 anxiety
  │   ├── institutions.py    — Inheritance, norms, drift, DD27 future_orientation
  │   └── reputation.py      — Gossip, trust, beliefs, skills, factions, DD27
  ├── metrics/
  │   └── collectors.py      — ~130 metrics per tick
  ├── experiments/
  │   ├── scenarios.py       — 10 named scenario configs
  │   ├── runner.py          — Multi-seed experiment execution
  │   └── summarizer.py      — Narrative summaries, integrity checks
  ├── autosim/
  │   ├── runner.py          — Mode A optimization (simulated annealing)
  │   ├── realism_score.py   — Composite score vs anthropological targets
  │   ├── targets.yaml       — Calibration targets (9 metrics, 35 tunable params)
  │   ├── program.md         — Agent instructions
  │   ├── journal.jsonl      — Experiment log
  │   └── best_config.yaml   — Best parameters found
  ├── dashboard/
  │   └── app.py             — Streamlit visual dashboard (9 tabs)
  ├── sandbox/
  │   └── explore.py         — IPython harness (all 35 traits in agent_df)
  ├── tests/
  │   └── test_smoke.py      — 5 pytest smoke tests (all passing)
  └── docs/
      ├── world_architecture.md  — THIS FILE
      ├── deep_dive_01-27.md     — Design rationale per subsystem
      ├── POST_AUTOSIM_TASKS.md  — Task list for next phase
      ├── AUTOSIM.md             — Autosim design document
      └── MISSION.md             — Project mission statement

ARCHITECTURE GUARANTEES:
  - Pure library: no IO, no print statements in engines
  - Deterministic: same seed = identical results
  - Modular: engines share no state except via Society
  - No circular imports: models never import engines
  - All randomness via seeded numpy.random.Generator
  - 35×35 correlation matrix verified positive semi-definite (PSD)

NAMED SCENARIOS (10):
  FREE_COMPETITION, ENFORCED_MONOGAMY, ELITE_POLYGYNY, HIGH_FEMALE_CHOICE,
  RESOURCE_ABUNDANCE, RESOURCE_SCARCITY, HIGH_VIOLENCE_COST,
  STRONG_PAIR_BONDING, STRONG_STATE, EMERGENT_INSTITUTIONS

================================================================================
SECTION 7 — WHAT THIS IS BUILDING TOWARD
================================================================================

The ultimate goal is a Civilization-style game where every person is a real
simulated individual with a genome, a developmental history, a medical biography,
skills earned through lived experience, cultural beliefs transmitted from their
community, and a complete life story from birth to death.

Social structures — bands, clans, tribes, chiefdoms, states — emerge from what
those individuals do. Nobody writes the story.

CURRENT STATE: Band simulator v1.0 complete — DD01-DD27 done, 35 heritable traits.
This is the most complex and important level. All other levels will be simpler.

WHAT MAKES THIS DIFFERENT:
  - Civ VI: civilizations, no real people inside them
  - The Sims: people, no civilization around them
  - Dwarf Fortress: personality, no emergent biology or evolution
  - SIMSIV: real people (35 heritable traits, developmental plasticity,
    medical histories, skills, beliefs, psychopathology spectrum) inside
    real societies (emergent institutions, factions, norms, cultural transmission)

================================================================================
SECTION 8 — OPEN QUESTIONS FOR V2 DESIGN
================================================================================

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

================================================================================
END OF DOCUMENT
================================================================================

Version: 3.0 (DD01-DD27 complete, 35 heritable traits)
Project: SIMSIV — D:\EXPERIMENTS\SIM
GitHub: https://github.com/kepiCHelaSHen/SIMSIV
