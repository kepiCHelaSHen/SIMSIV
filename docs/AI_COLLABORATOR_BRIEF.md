# SIMSIV — AI Collaborator Brief
# For: Any AI assistant joining this project
# From: The SIMSIV development team
# Date: 2026-03-15
# Version: 1.1 (updated with scenario experiment results and publication claim)

================================================================================
READ THIS FIRST — WHAT THIS DOCUMENT IS
================================================================================

This is a complete briefing for an AI collaborator joining the SIMSIV project.
It covers what has been built, what is planned, how we intend to publish, and
the core scientific question we want your input on.

Read this document in full before accessing any code or offering any suggestions.
The project is large and has a specific intellectual direction — understanding
that direction first prevents wasted effort on both sides.

The canonical source of truth for architectural decisions is:
  D:\EXPERIMENTS\SIM\CHAIN_PROMPT.md

The canonical source for validation and calibration:
  D:\EXPERIMENTS\SIM\docs\validation.md

The canonical source for architecture:
  D:\EXPERIMENTS\SIM\docs\world_architecture.md

================================================================================
SECTION 1 — WHAT SIMSIV IS
================================================================================

SIMSIV (Simulation of Intersecting Social and Institutional Variables) is a
Python agent-based simulation that models how human social structures emerge
from first-principles interactions among individual agents. Every agent is a
complete simulated person with a genome, developmental history, medical
biography, earned skills, culturally transmitted beliefs, and a complete life
story from birth to death.

The central commitment: ALL interesting outcomes must EMERGE from agent-level
rules. Nothing is hardwired. No civilization is scripted. No outcome is
predetermined.

This is simultaneously:
  1. A scientific instrument for studying gene-culture coevolution
  2. The engine for a planned Civilization-style game
  3. A platform for publishing peer-reviewed research on human social evolution

The project is not political and not moralizing. It is a sandbox for discovery.

TECHNICAL STACK:
  Python 3.11+, NumPy, Pandas, Matplotlib, Streamlit, PyYAML, SciPy
  Location: D:\EXPERIMENTS\SIM
  ~12,000 lines of code across 30+ files

================================================================================
SECTION 2 — WHAT HAS BEEN BUILT (CURRENT STATE)
================================================================================

The band-level simulator (v1.0) is COMPLETE. It simulates 50–500 individual
agents across hundreds of years at annual time resolution.

--------------------------------------------------------------------------------
2A. THE AGENT — 35 HERITABLE TRAITS
--------------------------------------------------------------------------------

Every agent carries 35 heritable traits organized into 7 domains:

  PHYSICAL (6):    physical_strength, endurance, physical_robustness,
                   pain_tolerance, longevity_genes, disease_resistance

  COGNITIVE (4):   intelligence_proxy (h²=0.65), emotional_intelligence,
                   impulse_control, conscientiousness

  TEMPORAL (1):    future_orientation

  PERSONALITY (4): risk_tolerance, novelty_seeking, anxiety_baseline,
                   mental_health_baseline

  SOCIAL (9):      aggression_propensity, cooperation_propensity,
                   dominance_drive, group_loyalty, outgroup_tolerance,
                   empathy_capacity, conformity_bias, status_drive,
                   jealousy_sensitivity

  REPRODUCTIVE (5): fertility_base, sexual_maturation_rate,
                    maternal_investment, paternal_investment_preference,
                    attractiveness_base

  PSYCHOPATHOLOGY (6): psychopathy_tendency (default 0.2), mental_illness_risk,
                        cardiovascular_risk, autoimmune_risk, metabolic_risk,
                        degenerative_risk

All traits are continuous float [0.0–1.0]. Each has an empirically grounded
heritability coefficient (h²) from behavioral genetics literature. A 35×35
correlation matrix with 100+ empirically grounded cross-trait correlations is
verified positive semi-definite.

INHERITANCE MODEL:
  child_val = h² × parent_midpoint + (1 − h²) × population_mean + mutation
  Parent weight: random blend w ~ N(0.5, 0.1) per trait (not exact 50/50)
  Mutation: 95% at σ=0.05, 5% rare large jump at σ=0.15
  Stress mutation: scarcity amplifies σ by up to 1.5×
  Epigenetic boost: stressed parents increase offspring mutation σ

GENOTYPE vs PHENOTYPE:
  Genotype stored at birth and passed to offspring unchanged.
  Phenotype modified at age 15 by developmental environment.
  mental_health_baseline gates plasticity magnitude (orchid/dandelion model).
  This means environmental effects on parents do NOT contaminate the gene pool.

NON-HERITABLE STATE (per agent):
  health, reputation, prestige_score, dominance_score
  current_resources (3 types: subsistence, tools, prestige goods)
  paternity_confidence, conflict_cooldown, trauma_score
  epigenetic_stress_load, faction_id

CULTURAL BELIEFS (5 dimensions, [-1, +1], socially transmitted):
  hierarchy_belief, cooperation_norm, violence_acceptability,
  tradition_adherence, kinship_obligation

SKILLS (4 domains, [0, 1], acquired through experience):
  foraging_skill, combat_skill, social_skill, craft_skill

LIFE STAGE (computed): CHILDHOOD / YOUTH / PRIME / MATURE / ELDER

--------------------------------------------------------------------------------
2B. THE SIMULATION ENGINE — 9 ENGINES, 12-STEP ANNUAL TICK
--------------------------------------------------------------------------------

Every year, 9 engines execute in this order:

  1.  Environment   — scarcity shocks, seasonal cycles (3yr), epidemic triggers
  2.  Resources     — 8-phase distribution: kin trust maintenance → decay →
                      equal floor + competitive distribution → child investment
                      → cooperation sharing → status distribution → elite
                      privilege → taxation → subsistence floor
  3.  Conflict      — initiation probability (aggression, jealousy, status drive,
                      resource stress), target selection (network deterrence,
                      faction membership, resource envy), flee response,
                      combat resolution, scaled consequences, subordination
                      cooldown, bystander trust updates, coalition defense,
                      third-party punishment. Cross-sex targeting enabled at
                      0.3× weight.
  4.  Mating        — pair bond formation (female choice weighted by mate value),
                      male competition contests, EPC (extra-pair copulation),
                      paternity uncertainty, bond dissolution (both partners
                      drive dissolution based on their own mate value assessment),
                      bond strengthening
  5.  Reproduction  — h²-weighted inheritance, developmental plasticity,
                      birth spacing (min 2yr), maternal health cost, age-specific
                      fertility curve, childbirth mortality. Children's parent_ids
                      point to social father (not genetic father).
  6.  Mortality     — aging, health decay, natural death, sex-differential
                      mortality (males 1.8–2.1× risk age 15–40), epidemic
                      differential vulnerability, maturation event at age 15
  6.3 Migration     — voluntary emigration (resource stress, ostracism, unmated
                      males), immigration (resource pull)
  6.5 Pathology     — condition activation (5 types), trauma accumulation,
                      epigenetic stress load. Mental illness uses trauma_score
                      for behavioral effects — does NOT mutate heritable traits.
  7.  Institutions  — inheritance distribution, norm enforcement, institutional
                      drift (cooperation/violence balance drives law_strength,
                      ENABLED by default at drift_rate=0.01),
                      emergent formation (violence punishment emerges after 5yr
                      high-violence streak, ENABLED by default)
  8.  Reputation    — gossip (trust propagation, Gaussian noise), trust decay,
                      belief updating (prestige-biased social influence +
                      experience + mutation), skill learning and decay,
                      faction detection (BFS on trust graph), neighborhood
                      refresh
  9.  Metrics       — ~130 metrics collected per tick

KEY DESIGN PRINCIPLES:
  - Pure library: no IO inside engines, sim.tick() returns a pure data dict
  - Deterministic: same seed → identical results
  - Modular: engines share no state except via Society object
  - No circular imports: models never import engines

--------------------------------------------------------------------------------
2C. CALIBRATION STATUS
--------------------------------------------------------------------------------

The model has been calibrated against 9 anthropological benchmarks using
simulated annealing (AutoSIM Mode A, 816 experiments, ~10.5 hours, Run 3).

Best calibration score: 1.000 (all 9 metrics simultaneously in target range)

Held-out validation (10 seeds not used in training, 200yr × 500pop × 2 runs):
  Mean score: 0.934 (across 2 independent validation runs)
  Collapses: 0/20 runs
  Robust metrics (10/10 seeds in range): Resource Gini, Mating Inequality,
    Avg Cooperation, Avg Aggression
  Fragile metrics (near target boundary): Violence Death Fraction (~0.04–0.05,
    target floor 0.05), Avg Lifetime Births (~3.97, target floor 4.0),
    Pop Growth Rate (high variance), Bond Dissolution Rate (~0.10–0.11, floor 0.10)

The fragile metrics are structurally explained in docs/validation.md. The most
significant issue is that the model lacks inter-group warfare, which suppresses
the violence death fraction below ethnographic totals (which include inter-band
raiding). This is a v2 design problem, not a v1 model failure.

IMPORTANT — TWO PREVIOUS CALIBRATION RUNS EXIST:
  Run 1 (pre-Phase E/F bugs): best score 0.9852 — SUPERSEDED, parameters biased
  Run 2 (mid-Phase F, stopped): best score 0.8979 — DISCARDED
  Run 3 (post-all-fixes, current): best score 1.000 — CURRENT CALIBRATION

--------------------------------------------------------------------------------
2D. WHAT HAS BEEN OBSERVED EMERGING (WITHOUT BEING SCRIPTED)
--------------------------------------------------------------------------------

These are documented findings from scenario experiments (5 seeds × 200yr × 10
scenarios, run 2026-03-15) and baseline runs. All are emergent — not scripted.

  1. Cooperation and intelligence are reliably selected for across all seeds
     and scenarios. Multiple fitness channels reward both traits independently.

  2. Aggression is reliably selected against — the fitness cost consistently
     exceeds the benefit across diverse conditions.

  3. PRELIMINARY — Gene-culture coevolution hypothesis (the paper's central
     claim, currently being tested):
     At 200 years, cooperation trait values are IDENTICAL across FREE_COMPETITION
     (0.511), STRONG_STATE (0.512), and EMERGENT_INSTITUTIONS (0.511). Trait
     divergence between governed and ungoverned societies requires longer
     timescales. A 10-seed × 500yr run is currently running to test whether
     the cooperation trait rises faster in FREE_COMPETITION (where genetic
     cooperation does all the fitness work) than in STRONG_STATE (where
     governance substitutes for genetic cooperation). This is the paper's
     central hypothesis, not yet a confirmed finding.

  4. Institutions suppress behavior without (yet) changing traits:
     STRONG_STATE produces 49% less violence and 40% lower Gini than
     FREE_COMPETITION at 200yr, but cooperation TRAIT is unchanged. The
     behavioral effect is immediate; the evolutionary effect takes centuries.

  5. Monogamy reduces violence 37% and unmated males 65% vs free competition.
     This replicates across both calibration eras (pre- and post-Phase F).

  6. Law strength self-organizes: EMERGENT_INSTITUTIONS reaches law_strength
     0.829 by year 200 starting from 0.0 — purely from cooperation/violence
     balance feedback.

  7. Resource stress induces cooperation: RESOURCE_SCARCITY produces the
     highest cooperation trait (0.536) of any scenario — consistent with
     interdependence theory (cooperation is fitness-critical under stress).

  8. Elite polygyny demographic paradox: ELITE_POLYGYNY produces the highest
     average lifespan but near-zero population growth — excluded males suppress
     overall birth rates enough to cancel the elite fertility advantage.

  9. Factions emerge from kin trust networks via connected-component detection
     on the trust graph — not assigned, not scripted.

  10. Trait diversity maintained at σ~0.09 by rare large mutations (5%
      probability, 3× sigma) even under strong directional selection.

================================================================================
SECTION 3 — WHAT IS PLANNED
================================================================================

--------------------------------------------------------------------------------
3A. THE FIVE-LEVEL HIERARCHY (FULL BUILD)
--------------------------------------------------------------------------------

SIMSIV is designed as a five-level nested simulation. Only Level 1 is complete.

  LEVEL 1: BAND (COMPLETE — v1.0)
    50–500 individual agents, annual tick, full biographical simulation
    Output: Band fingerprint (15 aggregate metrics exported upward)

  LEVEL 2: CLAN (planned — v2)
    5–15 bands (~750–7,500 people represented as statistics)
    Tick: Decadal (10yr per clan tick)
    Dynamics: Trade, raiding, intermarriage, cultural drift, merger/split
    Key challenge: temporal bridging (1yr band ticks → 10yr clan ticks)
    Key challenge: band fingerprint adequacy (does 15 values carry enough state?)

  LEVEL 3: TRIBE (planned — v2)
    5–15 clans, generational tick (25yr)
    Dynamics: Territorial boundaries, inter-clan warfare, norm standardization

  LEVEL 4: CHIEFDOM (planned — v3)
    Multiple tribes, hereditary leadership, tribute, ranked society

  LEVEL 5: STATE (planned — v3+)
    Multiple chiefdoms, formal law, armies, cities, trade empires

CRITICAL PRINCIPLE: Each level only communicates with adjacent levels.
Information flows UP as fingerprints. Pressure flows DOWN as environmental
conditions. Individual biography only exists at the band level.

--------------------------------------------------------------------------------
3B. THE PUBLICATION PLAN
--------------------------------------------------------------------------------

CENTRAL CLAIM (locked):
  "Institutional governance systematically reduces directional selection on
   heritable prosocial behavioral traits — providing computational evidence
   that institutions and genes are substitutes, not complements, in human
   social evolution."

  This engages directly with the Camp A (Bowles/Gintis: institutions and traits
  co-evolve upward together) vs Camp B (North: institutions substitute for
  internal motivation) debate in human behavioral evolution.

  PAPER 1 — Methods paper (band simulator)
    Title: "SIMSIV: A calibrated agent-based framework for studying
            gene-culture coevolution in pre-state societies"
    Target: JASSS (Journal of Artificial Societies and Social Simulation)
            OR PLOS ONE
    Status: Validation complete. Scenario experiments in progress.
            Sensitivity analysis needed. Writing can begin now.
    Contribution: Architecture, calibration methodology, validation approach.
                  35-trait h²-weighted model with PSD-verified correlation
                  matrix, simulated annealing calibration against 9
                  anthropological benchmarks, held-out seed validation.

  PAPER 2 — Findings paper (scenario experiments)
    Title: TBD — mating system effects + institutional emergence
    Target: Evolutionary Human Sciences OR Behavioral Ecology
    Status: Run 1 (5 seeds × 200yr) complete. Run 2 (10 seeds × 500yr) running.
    Contribution: Controlled scenario comparisons with statistical analysis.

  PAPER 3 — Gene-culture coevolution
    Title: TBD — institution-substitutes-for-traits finding
    Target: Evolution and Human Behavior OR Nature Human Behaviour
    Status: Central finding being tested in 500yr run currently running.
    Contribution: If the 500yr run shows cooperation trait divergence across
                  governance regimes, this is Paper 3's core result.

  PAPER 4 — Hierarchical emergence (requires clan simulator)
  PAPER 5 — Full hierarchy (requires tribe/chiefdom/state)

  AI DISCLOSURE: "Code development aided by Claude (Anthropic); all
                  hypotheses and interpretations are the author's own."

  AFFILIATION: "Independent Researcher" — non-academic status is not a
               barrier in ABM/evolutionary anthropology fields.

  PREPRINT: arXiv first (after scenario experiments + sensitivity analysis),
            then JASSS submission. Do not preprint prematurely — wait until
            the sensitivity analysis table exists.

--------------------------------------------------------------------------------
3C. IMMEDIATE NEXT STEPS (IN ORDER)
--------------------------------------------------------------------------------

  CURRENTLY RUNNING:
    10 seeds × 500yr × 3 scenarios (FREE_COMPETITION, STRONG_STATE,
    EMERGENT_INSTITUTIONS) — testing the central coevolution claim.

  WHEN THAT RUN COMPLETES:
  1. Analyze trait divergence: does cooperation_propensity rise faster in
     FREE_COMPETITION than STRONG_STATE over 500 years? This is the finding.

  2. Write docs/sensitivity_analysis.md
     Regression of parameter values against per-metric scores across 816
     autosim experiments. This becomes Table 2 in Paper 1.

  3. Phase G dashboard overhaul (prompts/dashboard_overhaul.md)
     Run in Claude Code CLI when scenario run finishes.

  4. Apply best_config.yaml defaults to config.py
     So the default config IS the calibrated config going forward.

  5. Tag v1.0-band-simulator on git, create Zenodo archive for DOI.

  6. Draft Paper 1 (can happen concurrently with above steps).

  AFTER PAPER 1 DRAFT:
  7. Design and build clan simulator (v2)
     Write docs/v2_clan_simulator.md first.

  8. Run high-fidelity calibration (200 experiments × 5 seeds × 300yr)

================================================================================
SECTION 4 — THE CORE RESEARCH QUESTION
================================================================================

The central question driving every design decision in this project:

  "How do individual-level heritable behavioral traits interact with cultural
   institutions to produce the social structures observed across human
   prehistory, and can this process be modeled bottom-up from first principles
   without scripting outcomes?"

The paper-ready version of this question (sharpened for peer review):

  "We ask whether the directional selection of prosocial behavioral traits in
   human band-level societies depends on institutional context, and whether
   the observed coevolution of traits and institutions can be reproduced by a
   calibrated agent-based model operating from individual-level rules alone."

Embedded sub-questions:

  Q1: SELECTION DYNAMICS
      Do cooperation and intelligence have fitness advantages in band societies?
      Under what conditions is aggression selected for vs against?

  Q2: GENE-CULTURE COEVOLUTION (THE PAPER'S CENTRAL HYPOTHESIS)
      Does institutional governance reduce directional selection on prosocial
      genes? The preliminary scenario data is consistent with this — behavioral
      outcomes (violence, Gini) diverge immediately across governance regimes,
      but cooperation TRAITS are identical at 200yr. The prediction: at 500yr,
      cooperation trait should be higher in FREE_COMPETITION (where genetics
      does the cooperative work) than in STRONG_STATE (where governance does it).

  Q3: MATING SYSTEM EFFECTS
      How do mating systems affect trait evolution, violence, and reproductive
      inequality? Monogamy-reduces-violence result is robust across both
      calibration eras.

  Q4: DEMOGRAPHIC CONSTRAINTS
      Does the mortality structure finding (low adult mortality + high childhood
      mortality + lethal epidemics) have implications for historical demography?

  Q5: EMERGENCE WITHOUT SCRIPTING
      Can institutional self-organization genuinely emerge from individual rules?
      EMERGENT_INSTITUTIONS reaching law_strength 0.829 from 0.0 says yes.

================================================================================
SECTION 5 — INVITATION FOR INPUT
================================================================================

We are actively seeking input from AI collaborators on the following:

--------------------------------------------------------------------------------
5A. RESEARCH QUESTION FRAMING
--------------------------------------------------------------------------------

  QUESTIONS FOR YOU:
  - The central claim is: institutions and genes are substitutes, not complements.
    Camp A (Bowles/Gintis) says they co-evolve upward together. Camp B (North)
    says institutions substitute for internal motivation. Our 200yr data shows
    behavioral divergence without trait divergence — consistent with Camp B
    in the short run. Is this framing correct? Are there nuances we are missing?
  - What is the most falsifiable version of this claim — what data from
    real pre-state societies would disconfirm it?
  - Are there papers in the gene-culture coevolution literature we should cite
    that directly address this Camp A vs Camp B question?
  - How should we handle the 200yr vs 500yr timescale question? At 200yr
    traits don't diverge. If they don't diverge at 500yr either, what does
    that mean for our claim?

--------------------------------------------------------------------------------
5B. PUBLICATION STRATEGY
--------------------------------------------------------------------------------

  QUESTIONS FOR YOU:
  - JASSS for Paper 1 (methods), Evolutionary Human Sciences for Paper 2
    (findings). Are these the right venues?
  - The 500yr scenario run will tell us if the coevolution finding is real.
    If it IS real and strong, should Paper 1 and Paper 2 be combined into a
    single higher-impact paper rather than split?
  - What additional analyses would a reviewer at Evolution and Human Behavior
    require beyond what we have?
  - Are there existing ABM papers on gene-culture coevolution that we need
    to explicitly position against?

--------------------------------------------------------------------------------
5C. SCIENTIFIC VALIDITY CONCERNS
--------------------------------------------------------------------------------

  QUESTIONS FOR YOU:
  - Applying modern h² estimates to pre-industrial populations: defensible
    with caveats, or a fundamental problem?
  - The violence death fraction consistently comes in below target (0.04 vs
    floor 0.05) because the model lacks inter-group warfare. For Papers 1 and 2,
    how should this limitation be characterized?
  - Institutional drift is now ENABLED by default (drift_rate=0.01). This
    means all scenarios, including FREE_COMPETITION, develop some law_strength
    over time (it reaches 0.476 in the first scenario run). Does this affect
    the experimental design of the gene-culture coevolution test?
  - The model calibrates at N=500. What does the literature say about whether
    cooperation/conflict dynamics are size-dependent in this range?

--------------------------------------------------------------------------------
5D. THEORETICAL GAPS
--------------------------------------------------------------------------------

  QUESTIONS FOR YOU:
  - Kin selection: is the absence of explicit Hamilton's rule calculations
    a significant theoretical gap, or is it adequately captured through the
    trust-building between kin?
  - Reciprocal altruism via the reputation ledger: mechanistically equivalent
    to standard models, or missing something important?
  - Conformist vs prestige-biased transmission: Henrich & Boyd treat these
    separately. Our conformity_bias trait feeds into belief updating, but is
    it properly distinguished from prestige-biased transmission?
  - Ostrom on institutional emergence: does our institutional drift mechanism
    capture what Ostrom's common-pool resource theory predicts?

--------------------------------------------------------------------------------
5E. METHODOLOGICAL SUGGESTIONS
--------------------------------------------------------------------------------

  QUESTIONS FOR YOU:
  - The 500yr scenario run uses 10 seeds. What statistical test should we
    apply to determine if cooperation trait divergence is significant?
    Mann-Whitney U on year-500 values? Time-series comparison?
  - Should we run out-of-sample predictions — calibrate on forager benchmarks,
    then predict chiefdom-level outcomes and compare to archaeological data?
  - We have ~257 config parameters but only tune 36. How do we address
    reviewer concerns about the other 221 being set "arbitrarily"?
  - The sensitivity analysis table: what is the best way to present this
    for an ABM paper audience? OAT (one-at-a-time) or global sensitivity?

================================================================================
SECTION 6 — FIRST SCENARIO EXPERIMENT RESULTS (2026-03-15)
================================================================================

Run: 5 seeds × 200yr × 10 scenarios, using calibrated best_config.yaml

  Scenario              Coop   Violence  Gini   Unmated♂  Law
  ──────────────────────────────────────────────────────────────
  FREE_COMPETITION      0.511  0.017     0.329  25.1%     0.476
  ENFORCED_MONOGAMY     0.511  0.011▼37% 0.329   8.8%▼65% 0.921
  ELITE_POLYGYNY        0.509  0.020▲18% 0.379  30.8%▲23% 0.459
  HIGH_FEMALE_CHOICE    0.526  0.018     0.333  30.7%     0.485
  RESOURCE_ABUNDANCE    0.506  0.015▼9%  0.318  27.4%     0.469
  RESOURCE_SCARCITY     0.536  0.020     0.289  29.9%     0.483
  HIGH_VIOLENCE_COST    0.512  0.021     0.329  22.9%     0.451
  STRONG_PAIR_BONDING   0.513  0.013▼22% 0.305  26.8%     0.493
  STRONG_STATE          0.512  0.009▼49% 0.197  11.7%▼53% 0.981
  EMERGENT_INSTITUTIONS 0.511  0.010▼39% 0.333  30.3%     0.829

KEY OBSERVATIONS:
  - Cooperation trait is 0.509–0.536 across ALL scenarios at 200yr.
    No scenario produces meaningful trait divergence at this timescale.
    This is the motivation for the 500yr run now running.
  - STRONG_STATE dramatically suppresses violence (▼49%) and inequality
    (▼40%) without changing the cooperation TRAIT. Behavior changes
    immediately; genetics takes centuries.
  - RESOURCE_SCARCITY produces the highest cooperation — stress-induced
    cooperation is a genuine emergent finding.
  - ELITE_POLYGYNY paradox: highest lifespan, near-zero population growth.
  - All 50 runs (10 scenarios × 5 seeds) survived to year 200.

================================================================================
SECTION 7 — HOW TO ENGAGE WITH THIS PROJECT
================================================================================

CONTEXT YOU NEED BEFORE SUGGESTING ANYTHING:
  - Read CHAIN_PROMPT.md (master design doc, all locked decisions)
  - Read docs/validation.md (calibration and validation detail)
  - Read docs/world_architecture.md (full system design)

WHAT HELPS:
  - Specific, actionable suggestions with reasoning and citations
  - Honest critique of scientific validity concerns
  - Input on the research question framing and publication strategy
  - Theoretical literature we may have missed
  - Statistical methods for analyzing the scenario experiment data

WHAT DOESN'T HELP:
  - Suggesting changes to the fundamental architecture without reading
    the documents above first
  - Repeating design decisions that were already considered and locked
  - Moralizing about what the simulation "should" show
  - Suggesting the simulation is inappropriate because it models
    heritable behavioral traits (it is grounded in behavioral genetics
    literature and is not making political claims)

WHAT NOT TO CHANGE WITHOUT EXPLICIT INSTRUCTION:
  - models/, engines/, config.py, simulation.py — simulation logic
  - metrics/collectors.py — metric column names (breaks existing outputs)
  - autosim/targets.yaml — calibration targets (changes all previous results)
  - Any file in docs/ — documents may be shared with reviewers

================================================================================
SECTION 8 — KEY FILES FOR CONTEXT
================================================================================

  D:\EXPERIMENTS\SIM\
  ├── CHAIN_PROMPT.md              ← Master design doc. Read first.
  ├── docs\validation.md           ← Calibration and validation. Essential.
  ├── docs\world_architecture.md   ← Full system architecture
  ├── docs\AI_COLLABORATOR_BRIEF.md ← This file
  ├── config.py                    ← All 257 parameters
  ├── simulation.py                ← Tick orchestrator
  ├── models\agent.py              ← Agent data model (35 traits)
  ├── models\society.py            ← Agent registry, factions, migration
  ├── autosim\best_config.yaml     ← Current calibrated parameters (score 1.000)
  ├── autosim\targets.yaml         ← Calibration targets with sources
  └── autosim\validation_report.json ← Held-out validation results

================================================================================
END OF BRIEF
================================================================================

Project: SIMSIV — D:\EXPERIMENTS\SIM
Status:  Band simulator v1.0 complete. Calibrated (score 1.000). Validated
         (0.934 mean on held-out seeds). Scenario experiments running.
         Publication plan active.
Contact: Share this document at the start of any new AI session.
