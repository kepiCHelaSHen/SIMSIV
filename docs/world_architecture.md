# SIMSIV — World Architecture Document
# The Complete Individual Model and Hierarchical Civilization Framework
# Location: D:\EXPERIMENTS\SIM\docs\world_architecture.md
# Last Updated: 2026-03-14
# Status: Band simulation complete (DD01-DD14), DD15-DD17 in progress
#
# PURPOSE: This document is designed to be shared with any AI or human
# collaborator to give a complete picture of what has been built and
# where the project is going. It is the single authoritative reference
# for architecture decisions at all levels of the simulation hierarchy.

================================================================================
SECTION 1 — PROJECT IDENTITY AND PHILOSOPHY
================================================================================

SIMSIV (Simulation of Intersecting Social and Institutional Variables) is a
Python agent-based simulation that models how human social structures emerge
from first-principles interactions. It is not political, not ideological, and
not designed to prove any conclusion. It is a sandbox for discovery.

Core principle: ALL interesting outcomes must EMERGE from agent-level rules.
Nothing is hardwired. No civilization is scripted. No outcome is predetermined.

The simulation is designed as the engine for a Civilization-style game, but
the model is built first — game mechanics come later. The quality of the model
determines the quality of everything built on top of it.

TECHNICAL STACK:
  Python 3.11+, NumPy, Pandas, Matplotlib, PyYAML, Streamlit
  Location: D:\EXPERIMENTS\SIM
  Architecture: Pure library simulation, no IO in engines, tick returns data

SCALE:
  Default: 500 agents, 200 years, annual tick
  Practical ceiling: 2,000 agents (O(N²) bottlenecks in conflict/mating)
  Runtime: ~10 seconds for 500 agents / 200 years

================================================================================
SECTION 2 — THE HIERARCHICAL CIVILIZATION MODEL
================================================================================

The simulation is designed around a five-level hierarchy, each level running
its own simulator that consumes aggregate outputs from the level below.

LEVEL 1: BAND (currently being built)
  Population: 50-500 individual agents
  Model: Full SIMSIV engine — every person simulated individually
  Time step: Annual tick
  Key output: Band fingerprint (10-15 aggregate metrics)
  Anthropological analog: Hunter-gatherer band, kinship group

LEVEL 2: CLAN (planned — v2)
  Population: 5-15 bands (~750-7,500 people represented)
  Model: Band-level aggregate dynamics — no individual agents
  Inputs: Band fingerprints from member bands
  Simulates: Trade, raiding, intermarriage, cultural drift, merger/split
  Key output: Clan fingerprint
  Anthropological analog: Extended kinship network, ~150-500 people

LEVEL 3: TRIBE (planned — v2)
  Population: 5-15 clans (~3,750-37,500 people represented)
  Model: Clan-level aggregate dynamics
  Simulates: Territorial boundaries, inter-clan warfare, trade networks,
             cultural identity formation, norm standardization
  Key output: Tribe fingerprint
  Anthropological analog: Linguistically/culturally unified group

LEVEL 4: CHIEFDOM (planned — v3)
  Population: Multiple tribes (~20,000-200,000 people represented)
  Model: Tribe-level political dynamics
  Simulates: Hereditary leadership, surplus redistribution, tribute,
             monument building, ranked society, proto-state formation
  Key output: Chiefdom fingerprint
  Anthropological analog: Ranked society with hereditary hierarchy

LEVEL 5: STATE (planned — v3+)
  Population: Multiple chiefdoms (millions represented statistically)
  Model: Pure historical forces — no individual agent simulation
  Simulates: Laws, armies, cities, taxation, bureaucracy, writing, trade empires
  Key output: State profile for world map
  Anthropological analog: Civ VI starts here

CRITICAL DESIGN PRINCIPLE:
  Each level ONLY communicates with the level immediately above and below it.
  A band does not know about the tribe. The tribe does not know about individuals.
  Information flows UP as aggregate fingerprints.
  Pressure flows DOWN as environmental conditions (drought, war, disease at
  tribal level becomes resource scarcity at band level).

THE BAND FINGERPRINT (what gets exported upward):
  These 12 values summarize a band for the clan-level simulator:
  1.  avg_aggression_index        — how warlike is this band
  2.  avg_cooperation_index       — how tradeable / alliance-worthy
  3.  resource_level              — wealth and desperation
  4.  population_size             — fighting-age members
  5.  law_strength                — how organized / law-abiding
  6.  dominant_faction_type       — prestige-led vs dominance-led
  7.  avg_health_index            — disease burden, wellbeing
  8.  kinship_density             — how related are members (inbreeding coefficient proxy)
  9.  cultural_identity_score     — faction cohesion, norm strength
  10. avg_intelligence_index      — adaptive capacity
  11. reproductive_rate           — population growth trajectory
  12. institutional_stability     — is law_strength rising or falling

================================================================================
SECTION 3 — THE BAND SIMULATION (CURRENT BUILD — DD01-DD17)
================================================================================

The band simulation is the most complex level — it simulates every individual
person. All other levels are simpler. This is the core engine.

TICK EXECUTION ORDER (per annual step):
  1. Environment       — scarcity shocks, seasonal cycles, epidemic triggers
  2. Resources         — 8-phase distribution engine
  3. Conflict          — violence, deterrence, coalition defense
  4. Mating            — pair bond formation, dissolution, infidelity
  5. Reproduction      — conception, birth, paternity, infant survival
  6. Mortality         — aging, health decay, natural death, childbirth death
  7. Institutions      — inheritance, norm enforcement, institutional drift
  8. Reputation        — gossip, trust decay, aggregate reputation update
  8.5 Factions         — periodic connected-component detection (every 5yr)
  9. Pathology         — condition activation, trauma tracking [DD17 — planned]
  10. Metrics          — collect all 62+ stats for this year
  11. Equilibrium check

--------------------------------------------------------------------------------
3A. THE AGENT — WHAT EVERY PERSON IS
--------------------------------------------------------------------------------

Every agent is a simulated human being with:

HERITABLE TRAITS (passed to offspring via weighted midpoint + mutation):
  Current 8 traits (DD01-DD14 complete):
    aggression_propensity    [0.0-1.0]  h²~0.44  tendency toward conflict
    cooperation_propensity   [0.0-1.0]  h²~0.40  tendency toward alliance
    attractiveness_base      [0.0-1.0]  h²~0.50  baseline physical mate value
    status_drive             [0.0-1.0]  h²~0.50  motivation to seek dominance
    risk_tolerance           [0.0-1.0]  h²~0.48  willingness to take risks
    jealousy_sensitivity     [0.0-1.0]  h²~0.45  trigger for jealousy-driven conflict
    fertility_base           [0.0-1.0]  h²~0.50  baseline reproductive capacity
    intelligence_proxy       [0.0-1.0]  h²~0.65  resource acquisition efficiency

  Planned DD15 additions (14 new traits, total ~22):
    longevity_genes          [0.0-1.0]  h²~0.25  modifies lifespan +/- 10yr
    disease_resistance       [0.0-1.0]  h²~0.40  reduces epidemic vulnerability
    physical_robustness      [0.0-1.0]  h²~0.50  reduces conflict health damage
    pain_tolerance           [0.0-1.0]  h²~0.45  modifies flee threshold
    mental_health_baseline   [0.0-1.0]  h²~0.40  stress resistance, emotional stability
    emotional_intelligence   [0.0-1.0]  h²~0.40  speeds trust formation, gossip acuity
    impulse_control          [0.0-1.0]  h²~0.50  gates aggression trait → behavior
    novelty_seeking          [0.0-1.0]  h²~0.40  exploration, mating pool participation
    empathy_capacity         [0.0-1.0]  h²~0.35  extends cooperation altruism radius
    conformity_bias          [0.0-1.0]  h²~0.35  norm adoption speed
    dominance_drive          [0.0-1.0]  h²~0.50  active dominance hierarchy seeking
    maternal_investment      [0.0-1.0]  h²~0.35  quantity-quality offspring tradeoff
    sexual_maturation_rate   [0.0-1.0]  h²~0.60  age at first reproduction variance
    cardiovascular_risk      [0.0-1.0]  h²~0.50  heritable health condition risk [DD17]
    mental_illness_risk      [0.0-1.0]  h²~0.60  heritable psychiatric condition risk [DD17]
    autoimmune_risk          [0.0-1.0]  h²~0.40  heritable immune dysfunction risk [DD17]
    metabolic_risk           [0.0-1.0]  h²~0.45  heritable metabolic condition risk [DD17]
    degenerative_risk        [0.0-1.0]  h²~0.35  heritable degenerative condition risk [DD17]

INHERITANCE MODEL:
  child_val = h² * parent_midpoint + (1 - h²) * population_mean + mutation
  Parent weight: w ~ N(0.5, 0.1) — random blend, not always exact 50/50
  Mutation: 95% at sigma=0.05, 5% rare large jump at sigma=0.15
  Stress mutation: scarcity amplifies sigma by up to 1.5x
  Correlation matrix: 8x8 (expanding to ~22x22 in DD15) applied at population init
  Migrant traits: drawn from current population distribution (not uniform)

GENOTYPE vs PHENOTYPE (DD16 — planned):
  Genotype: raw genetic values, passed to offspring unchanged
  Phenotype: expressed values after developmental modification (age 0-15 effects)
  Developmental modifiers:
    + childhood resource quality → intelligence, impulse control boost
    + parental trait modeling → social learning component
    + trauma (parent death before age 10) → aggression boost, trust reduction
    + peer group effects (age 5-15) → conformity_bias weighted average
  mental_health_baseline gates plasticity (orchid vs dandelion genotypes)

NON-HERITABLE STATE (earned, not passed to offspring):
  health                    [0.0-1.0]  decays with age, damaged by conflict/starvation
  reputation                [0.0-1.0]  public standing — aggregate of how others see you
  prestige_score            [0.0-1.0]  earned through cooperation, generosity, networks
  dominance_score           [0.0-1.0]  earned through conflict victories, intimidation
  current_resources         float      survival + status wealth
  current_status            float      computed: prestige*w1 + dominance*w2 (backward compat)
  paternity_confidence      [0.0-1.0]  male's confidence in offspring paternity
  conflict_cooldown         int        years of post-combat subordination
  trauma_score              [0.0-1.0]  accumulated life trauma [DD17 planned]
  faction_id                int/None   which emergent faction agent belongs to

RELATIONSHIPS:
  partner_ids               list[int]  current mates (list — supports polygyny)
  pair_bond_strengths       dict       strength per partner [0.0-1.0]
  offspring_ids             list[int]  all children ever born (incl. dead)
  parent_ids                tuple      (mother_id, father_id) — genetic parents
  reputation_ledger         dict       sparse bilateral trust scores (cap 100 entries)
  epc_partner_id            int/None   extra-pair mate this tick (cleared each tick)
  last_partner_death_year   int/None   for widowhood mourning calculation
  faction_id                int/None   emergent group membership

REPRODUCTIVE BIOLOGY:
  last_birth_year           int/None   for birth spacing (2yr minimum)
  birth_count               int        total lifetime births
  childhood_resource_quality float     avg parental resources during age 0-5 [DD16]
  childhood_trauma          bool       did parent die before age 10 [DD16]

MEDICAL HISTORY (DD17 — planned):
  active_conditions         set[str]   currently active heritable conditions
  medical_history           list[dict] complete life medical log (max 50 entries)

LIVING BIOGRAPHY:
  Every agent has: year_of_birth (implicit from age), parent IDs, partner history,
  children list, cause_of_death, year_of_death, faction membership history,
  complete event log. This constitutes a readable life narrative.

DYNAMIC COMPUTED PROPERTIES:
  mate_value = (health*0.3 + attractiveness*0.25 + prestige*0.12 + dominance*0.08
               + resources_normalized*0.15 + reputation*0.1) * age_factor
  is_fertile = alive AND health > 0.2 AND age in reproductive window
  is_bonded = len(partner_ids) > 0
  is_in_mourning = last_partner_death_year within mourning_years of current_year

--------------------------------------------------------------------------------
3B. THE ENGINES — WHAT DRIVES BEHAVIOR
--------------------------------------------------------------------------------

ENGINE 1: ENVIRONMENT
  Scarcity shocks: 3% base annual probability, amplified by overcrowding
  Seasonal cycles: cosine wave modulation (configurable amplitude + period)
  Epidemic triggers: 2% base probability, 20yr refractory period
  Outputs: current_scarcity_level (computed ONCE per tick, used by all engines)

ENGINE 2: RESOURCES (8-phase)
  Phase 0: Kin trust maintenance (parents+children +0.02/yr, siblings +0.01/yr)
  Phase 1: Resource decay (50% retention, intel-mediated storage bonus up to +20%)
  Phase 2: Survival distribution (25% equal floor, 75% competitive)
    Competitive weight = (intel*0.25 + prestige*0.175 + dominance*0.075
                         + experience*0.15 + wealth^0.7*0.15 + network*0.05)^3
                         * (1 - aggression * 0.3)
  Phase 3: Child investment costs (0.5 res/child/yr, scaled by paternity confidence)
  Phase 4: Cooperation sharing (trust > 0.5, cooperation_propensity > 0.3, +0.05 trust)
  Phase 5: Status distribution (prestige pool 60%, dominance pool 40%)
  Phase 6: Elite privilege (top 10% status, additive bonus capped at 2x base)
  Phase 7: Taxation (top quartile → bottom quartile, gated by law_strength)
  Phase 8: Subsistence floor (minimum 1.0 resources — prevents death spirals)
  Signaling: Resource display (honest, 5% cost, builds prestige) [DD12]
  Ostracism: Low-reputation agents excluded from cooperation sharing [DD11]

ENGINE 3: CONFLICT
  Probability: base_p * aggression + jealousy_boost + resource_stress + status_drive
               * institutional_suppression * cooperation_damping * network_deterrence
               * subordination_factor * seasonal_lean_boost
  Target selection: low trust + rival + similar status + resource envy +
                    - network deterrence - dominance deterrence - strength assessment
  Flee: target risk_tolerance < flee_threshold → probabilistic escape
  Coalition defense: trusted allies (trust > 0.65) may intervene before combat [DD11]
  Combat power: aggression*0.25 + status(dom*0.7+pres*0.3)*0.20 + health*0.25
               + risk*0.15 + resource_edge + intel*0.05 + ally_bonus
  Scaled consequences: 0.7x close fights → 1.5x stomps
  Subordination: loser enters 2yr cooldown (50% reduced initiation)
  Bystanders: witnesses distrust aggressor -0.08 (allies -0.1 extra)
  Prestige cost: aggressors always lose prestige (-0.02) even when winning
  Third-party punishment: high-cooperation agents pay personal cost to punish [DD11]

ENGINE 4: MATING
  Phase 1: Clean stale bonds (dead partners → mourning state)
  Phase 2: Dissolve bonds (probability = base * strength_factor * resource_stress * quality_factor)
  Phase 3: Form pairs
    Female choosiness: age-adjusted (−0.01/yr over 30), resource desperation modifier
    Weights: mate_value * trust_bonus * aggression_penalty(0.5) * coop_bonus(0.4)
    Choosiness blends toward uniform distribution
    Male contest: 30% chance rival challenges, loser takes injury [DD01]
    High-status males: can hold multiple bonds (max_mates_per_male)
  Phase 4: Extra-pair copulation (EPC)
    Probability: infidelity_base * mate_value_gap * (1 - bond_strength)
    EPC male weighted by mate_value
    Detection: jealousy_sensitivity * jealousy_detection_rate
    Detected: paternity confidence drops -0.3, bond damaged
  Phase 5: Strengthen bonds (diminishing returns growth curve)
  Phase 6: Paternity confidence recovery +0.05/yr

ENGINE 5: REPRODUCTION
  Conception chance: base * fertility_mod * resource_mod * health_mod
  Pair bond bonus: 1.3x for bonded females
  Paternity: epc_partner_id consumed — genetic father may differ from social father
  Social father investment: paternity_confidence scales resource contribution
  Child survival: base * parental_resources * bond_stability * scarcity * kin_support
  Birth interval: minimum 2yr (lactational amenorrhea analog) [DD06/DD13]
  Age-specific fertility: subfertile 15-19 (60%), peak 20-28, decline 3%/yr post-30 [DD13]
  Childbirth mortality: 2% per birth, 3x for health < 0.4 [DD13]
  Birth timing: ±20% conception chance based on seasonal cycle phase [DD10]

ENGINE 6: MORTALITY
  Health decay: base_rate + age_acceleration (post-30: +0.002/yr)
  Scarcity health damage: scarcity_level * 0.03
  Starvation: resources < 2.0 → health -0.02/yr
  Health death: health <= min_health_survival (0.05)
  Age death: probability rises steeply past age 45 (configurable)
  Background mortality: 0.02/yr base (accidents, disease)
  Male differential: 1.8x background mortality age 15-40 [DD13]
  Childhood mortality: 0.02/yr base, resource-dependent, orphan multiplier 2x [DD06]
  Grandparent bonus: reduces infant/childhood mortality -0.05 [DD06]
  Epidemic mortality: differential vulnerability (children 3x, elderly 2x) [DD09]

ENGINE 7: INSTITUTIONS
  Phase 1: Inheritance distribution (all deaths this tick — violence + natural)
    Models: equal_split, primogeniture, trust_weighted
    Prestige inheritance: fraction of prestige passes to heirs
  Phase 2: Norm enforcement (polygyny detection → reputation + resource penalties)
  Phase 3: Institutional drift
    cooperation_pressure = (avg_cooperation - 0.4) * boost
    violence_pressure = violence_rate * decay
    net_pressure = coop_pressure - violence_pressure
    law_strength += drift_rate * net_pressure * (1 - inertia * |law_strength|)
  Phase 4: Emergent formation
    Violence streak (5yr high) → violence_punishment_strength increases
    Inequality streak (8yr high Gini) → max_mates_per_male decreases
  Property rights: modulate conflict looting (loot = 0.5 * (1 - property_rights))
  Taxation: top quartile → bottom quartile, gated by law_strength

ENGINE 8: REPUTATION
  Phase 1: Trust decay (−0.01/yr toward neutral, slower for extreme values)
  Phase 2: Dead agent cleanup (removes deceased from reputation ledgers)
  Phase 3: Gossip (10% chance per tick, share trust entries with trusted allies,
           noise 0.1 per hop — telephone game degradation)
  Phase 4: Aggregate reputation update
           reputation = 0.7 * mean(how_others_see_you) + 0.3 * existing_reputation

ENGINE 8.5: FACTION DETECTION (every 5yr)
  Algorithm: connected-component analysis on mutual trust graph
  Threshold: mutual trust > 0.65 for same faction
  Min size: 3 agents (smaller = factionless)
  Max size: 50 (schism pressure above this)
  In-group effects: lower sharing threshold (-0.1), sharing rate boost (+20%)
  Out-group effects: 1.5x conflict targeting weight
  Endogamy: mild same-faction mate value bonus (+10%)
  Merge: leader mutual trust > 0.8 triggers faction merger
  Schism: oversized factions split probabilistically (0.01/yr pressure)

ENGINE 9: PATHOLOGY (DD17 — planned)
  Condition activation: annual probability per heritable condition risk
  Triggers: resource stress, childhood trauma, age, recent injury, scarcity
  Active condition effects: health decay boost, behavioral instability,
                            epidemic vulnerability, resource penalty, etc.
  Trauma tracking: conflict loss +0.05, kin death +0.04, deprivation +0.02/yr
  Trauma effects: trust formation slowed, jealousy boosted, instability at >0.8
  Recovery: slow decay when resources adequate and socially connected

--------------------------------------------------------------------------------
3C. ENVIRONMENT MODEL
--------------------------------------------------------------------------------

  Resource multiplier: abundance_multiplier + volatility_noise (Gaussian)
  Scarcity events: overcrowding-amplified, 2-6yr duration, 20yr refractory [DD09]
  Seasonal cycles: cosine wave, configurable amplitude (0.3) and period (3yr) [DD10]
  Epidemics: 2% base probability, differential vulnerability, 20yr refractory [DD09]
  Carrying capacity: crowding penalty activates above 50% of max capacity
  Scarcity level: computed ONCE per tick in environment.tick() — all engines
                  read the same stored value (key reproducibility guarantee)

--------------------------------------------------------------------------------
3D. METRICS — WHAT THE BAND PRODUCES
--------------------------------------------------------------------------------

62 per-tick metrics collected annually:

DEMOGRAPHICS:
  population, males, females, births, deaths, infant_deaths, childhood_deaths
  orphan_count, children_count, max_generation, sex_ratio_reproductive
  male_deaths, female_deaths, childbirth_deaths

ECONOMICS:
  resource_gini, status_gini, avg_resources, avg_status
  resource_top10_share, cooperation_network_size, resource_transfers
  civilization_stability (CSI), social_cohesion (SCI)

REPRODUCTION:
  reproductive_skew, mating_inequality, unmated_male_pct, unmated_female_pct
  elite_repro_advantage, child_survival_rate, pair_bonded_pct
  infidelity_rate, epc_detected, paternity_uncertainty
  avg_bond_strength, mating_contests, avg_lifetime_births, avg_maternal_health

CONFLICT:
  conflicts, violence_rate, flee_events, violence_deaths
  punishment_events, agents_in_cooldown, coalition_defenses
  third_party_punishments, ostracized_count

SOCIAL:
  gossip_events, avg_ledger_size, avg_trust, distrust_fraction, avg_reputation
  bluff_attempts, bluff_detections
  faction_count, largest_faction_size, faction_size_gini
  faction_stability, inter_faction_conflict_rate, factionless_fraction

INSTITUTIONS:
  law_strength, violence_punishment, property_rights
  inheritance_events, norm_violations, institutions_emerged

TRAITS:
  avg_aggression, avg_cooperation, avg_risk_tolerance, avg_jealousy
  avg_attractiveness, avg_status_drive, avg_fertility, avg_intelligence
  aggression_std, cooperation_std, seasonal_phase

ENVIRONMENT:
  scarcity, epidemic_active, epidemic_deaths

STATUS/HEALTH:
  avg_prestige, avg_dominance, prestige_gini, dominance_gini
  prestige_dominance_corr, avg_health, avg_age, avg_lifespan, pop_growth_rate

--------------------------------------------------------------------------------
3E. KEY EMERGENT FINDINGS (from 14 completed deep dives)
--------------------------------------------------------------------------------

These patterns emerge without being programmed:

1. MONOGAMY SELECTS FOR COOPERATION AND INTELLIGENCE
   STRICT_MONOGAMY: cooperation +0.074, intelligence +0.093 over 200yr
   Mechanism: monogamous pair bonding reduces male-male competition, increasing
   selection pressure on parenting quality and resource acquisition

2. ELITE POLYGYNY SELECTS HARDEST AGAINST AGGRESSION
   ELITE_POLYGYNY: aggression -0.086 over 200yr
   Mechanism: high-status males with multiple mates — aggression costs prestige
   and resources, selecting against it even as it helps win competitions

3. INSTITUTIONS SUBSTITUTE FOR TRAITS
   STRONG_STATE: cooperation trait 0.527 vs BASELINE 0.564
   Mechanism: when law enforces cooperative behavior, individual selection
   pressure for cooperation genes relaxes. External enforcement crowds out
   internal motivation. This is a genuine social science finding.

4. EMERGENT INSTITUTIONS SELF-ORGANIZE
   Law strength grows 0 → 0.48 over 200yr from cooperation/violence balance alone
   Mechanism: cooperation-heavy populations generate institutional pressure;
   violence-heavy populations erode it. No central designer required.

5. FACTIONS EMERGE NATURALLY FROM KIN TRUST
   45 factions peak in 500-pop run, consolidating over time
   Mechanism: kin trust bootstraps cooperation networks; trust clusters naturally
   become factions through connected-component dynamics

6. AGGRESSION CONSISTENTLY SELECTED AGAINST ACROSS ALL SCENARIOS
   Multiple independent selection channels operate simultaneously:
   - Female mate choice penalizes aggression (-0.5 weight)
   - Resource engine: aggression_production_penalty reduces competitive weight
   - Conflict mortality: aggressive agents die more
   - Pair bond destabilization: violence loses mates
   - Prestige cost: aggressors lose social standing even when winning

7. COOPERATION NETWORKS CREATE ECONOMIC MOATS
   High-cooperation agents accumulate more resources through network effects,
   creating compounding advantage that pure aggression cannot overcome

8. VIOLENCE RATES RESPOND TO INSTITUTIONAL STRENGTH
   STRONG_STATE: violence 0.024 (lowest) vs BASELINE 0.054
   Mechanism: law_strength suppresses initiation probability through multiple
   channels — direct suppression, punishment, property rights reducing loot value

================================================================================
SECTION 4 — PLANNED DEEP DIVES (DD15-DD17)
================================================================================

DD15 — EXTENDED GENOMICS
  Expand heritable traits from 8 to ~22
  Add real heritability coefficients (h²) to inheritance model
  New traits: longevity, disease resistance, physical robustness, pain tolerance,
             mental health baseline, emotional intelligence, impulse control,
             novelty seeking, empathy capacity, conformity bias, dominance drive,
             maternal investment, sexual maturation rate
  Expand TRAIT_CORRELATION matrix to include new cross-trait correlations
  Status: Prompt written at prompts/deep_dive_15_genomics.md

DD16 — DEVELOPMENTAL BIOLOGY (NATURE VS NURTURE)
  Add developmental plasticity: childhood environment modifies trait expression
  Store genotype separately from phenotype (breed uses genotype)
  Childhood effects: resources, parental traits, orphan status, peer group
  mental_health_baseline moderates plasticity (orchid vs dandelion)
  New metric: heritability_realized — empirically measures nature vs nurture
  Status: Prompt written at prompts/deep_dive_16_development.md

DD17 — MEDICAL HISTORY AND PATHOLOGY
  New engine: engines/pathology.py
  Heritable condition risks (5 conditions, add to HERITABLE_TRAITS)
  Condition activation based on age, stress, trauma, lifestyle
  Trauma score accumulation and recovery
  Medical history log per agent (max 50 entries — part of life biography)
  Lineage health profiles observable across generations
  Status: Prompt written at prompts/deep_dive_17_medical.md

================================================================================
SECTION 5 — WORLD ARCHITECTURE (HIGHER LEVELS — PLANNED V2/V3)
================================================================================

DESIGN PHILOSOPHY FOR HIGHER LEVELS:
  Each level runs its own simulator that is simpler than the level below.
  Computational complexity decreases with each level.
  Information richness decreases going up.
  The individual biography only exists at the band level.
  At clan level and above, people are represented as statistics.

THE CLAN SIMULATOR (v2 — planned)
  Inputs: Band fingerprints from 5-15 member bands
  Runs: Band-level interaction model (not individual agents)

  What the clan simulator computes each tick:
  - Inter-band trade probability = f(resource_gap, cooperation_index, trust)
  - Raid probability = f(aggressor_aggression, target_resources, defender_network)
  - Intermarriage rate = f(faction_alignment, cultural_distance, resource_level)
  - Migration = f(resource_desperation, population_pressure, kinship_density)
  - Cultural drift = conformity_bias weighted average of member band norms
  - Alliance formation = f(shared_enemies, cooperation_index, historical_trust)

  What triggers band → clan recognition:
  NOT a building or tech unlock. A THRESHOLD CROSSING:
  - Multiple bands sharing territory with kinship links > threshold
  - Inter-band cooperation rate above threshold for N years
  - No sustained raiding between members for N years
  - Shared faction/identity score above threshold

  Clan fingerprint exported upward:
  Same 12 metrics as band fingerprint, now representing ~150-2000 people

THE TRIBE SIMULATOR (v2 — planned)
  Inputs: Clan fingerprints from 5-15 member clans
  Runs: Clan-level interaction model (even simpler)

  What the tribe simulator computes:
  - Cultural identity score (shared norms, language proxy, ritual alignment)
  - Territorial boundaries (spatial extent, defended perimeter)
  - Inter-clan warfare (aggregate power calculations)
  - Trade network structure (network graph of alliance-weighted exchanges)
  - Norm standardization (institutional drift toward mean across clans)

  What triggers clan → tribe recognition:
  - Shared cultural identity score above threshold
  - Regular inter-clan trade for N years
  - Coordinated response to external threat (shared conflict event)
  - Common institutional norms within tolerance range

THE CHIEFDOM SIMULATOR (v3 — planned)
  Inputs: Tribe fingerprints
  What emerges:
  - Hereditary leadership (band with highest avg prestige + resources + faction size)
  - Tribute flow (weaker tribes pay stronger tribes resources)
  - Monument/infrastructure (resource surplus above threshold → collective investment)
  - Ranked society (band-level Gini crystallizes into formal hierarchy)

THE STATE SIMULATOR (v3+ — planned)
  Inputs: Chiefdom fingerprints
  What emerges:
  - Formal law code (law_strength crystallizes from drift to fixed rules)
  - Standing army (specialist conflict agents — differentiated from producers)
  - Urban centers (high-density resource nodes with administrative function)
  - Writing analog (institutional memory — reduces institutional decay rate)
  - Trade empire (long-distance exchange networks)

================================================================================
SECTION 6 — TECHNICAL ARCHITECTURE
================================================================================

FILE STRUCTURE:
  D:\EXPERIMENTS\SIM\
  ├── config.py              — 107+ tunable parameters
  ├── simulation.py          — tick orchestrator
  ├── main.py               — CLI entry point
  ├── models/
  │   ├── agent.py           — Agent dataclass, breed(), create_initial_population()
  │   ├── society.py         — Agent registry, faction detection, migrant injection
  │   └── environment.py     — Scarcity, seasons, epidemics
  ├── engines/
  │   ├── resources.py       — 8-phase resource distribution
  │   ├── conflict.py        — Violence, deterrence, coalitions
  │   ├── mating.py          — Pair bonds, EPC, infidelity
  │   ├── reproduction.py    — Conception, birth, child survival
  │   ├── mortality.py       — Aging, health, death
  │   ├── institutions.py    — Inheritance, norms, drift, emergence
  │   └── reputation.py      — Gossip, trust decay, aggregate reputation
  ├── metrics/
  │   └── collectors.py      — 62+ metrics per tick
  ├── experiments/
  │   ├── scenarios.py       — 10 named scenario configs
  │   ├── runner.py          — Multi-seed experiment execution
  │   └── summarizer.py      — Narrative summaries, integrity checks
  ├── dashboard/
  │   └── app.py             — Streamlit visual dashboard
  └── prompts/
      └── deep_dive_*.md     — 17 deep dive implementation prompts (DD01-DD17)

ARCHITECTURE GUARANTEES:
  - Pure library: no IO, no print statements in engines
  - Deterministic: same seed = identical results (scarcity computed once per tick)
  - Modular: engines know nothing about each other, communicate via Society state
  - No circular imports: models never import engines
  - All randomness via seeded numpy.random.Generator

NAMED SCENARIOS (10 defined):
  FREE_COMPETITION      — baseline, unrestricted, null hypothesis
  ENFORCED_MONOGAMY     — mating_system="monogamy", law=0.7, punishment=0.5
  ELITE_POLYGYNY        — elite_privilege=3.0, max_mates=5
  HIGH_FEMALE_CHOICE    — female_choice_strength=0.95
  RESOURCE_ABUNDANCE    — resource_abundance=2.5, low volatility
  RESOURCE_SCARCITY     — resource_abundance=0.4, scarcity_prob=0.15
  HIGH_VIOLENCE_COST    — violence_cost_health=0.45, death_chance=0.15
  STRONG_PAIR_BONDING   — bond_strength=0.9, dissolution_rate=0.02
  STRONG_STATE          — law=0.8, punishment=0.7, property_rights=0.5, tax=0.15
  EMERGENT_INSTITUTIONS — all institutions start at 0, self-organize

================================================================================
SECTION 7 — WHAT THIS IS BUILDING TOWARD
================================================================================

The ultimate goal is a Civilization-style game where:

1. Every person in the game world is a real simulated individual with a genome,
   a developmental history, a medical biography, relationships, and a life story

2. Social structures — bands, clans, tribes, chiefdoms, states — emerge from
   what those individuals do, not from what the game designer scripted

3. The player interacts at multiple levels simultaneously:
   - Zoom in: see individual people living their lives
   - Zoom out: see civilizations rising and falling

4. Every war, every alliance, every cultural practice, every dynasty emerged
   from the rules — nobody wrote the story

5. Scale: ~3-5 million fully simulated individuals across a world map, with
   hundreds of millions represented statistically at higher levels

Current state: The band simulator (Level 1) is complete through DD14, with
DD15-DD17 in progress. This is the most complex and important level.
All other levels will be simpler to build because they operate on aggregates.

WHAT MAKES THIS DIFFERENT FROM EVERYTHING THAT EXISTS:
  - Civ VI simulates civilizations but has no real people inside them
  - The Sims simulates people but has no civilization around them
  - Dwarf Fortress has personality but no emergent biology
  - This simulation has real people (heritable traits, life histories, evolution)
    inside real societies (emergent institutions, factions, norms)
  - The people are real in a way no simulated people have ever been before

================================================================================
SECTION 8 — OPEN QUESTIONS AND FEEDBACK REQUESTED
================================================================================

These are areas where outside perspective would be valuable:

1. BAND FINGERPRINT DESIGN
   What are the 12 most important aggregate metrics for the clan simulator?
   Are there metrics we're not currently computing that would be critical?

2. BAND → CLAN TRANSITION CRITERIA
   What thresholds define when bands have become a clan?
   Should this be gradual (continuous) or threshold-based (discrete)?

3. CLAN SIMULATOR MECHANICS
   What are the most important dynamics to model at the clan level?
   What can safely be simplified away?

4. TEMPORAL SCALE MISMATCH
   Band sim runs at annual tick. Clan sim might run at decadal tick.
   How should we handle the time scale translation between levels?

5. CULTURAL IDENTITY
   How do we give bands a cultural fingerprint distinct enough to differentiate
   them when they meet? What are the right markers?

6. PLAYER INTERACTION MODEL
   At which level(s) should the player have agency?
   Should the player be able to influence individual agents, or only
   set institutional parameters for a band?

7. MISSING MECHANISMS
   What human social dynamics are most conspicuously absent from the current model?
   What would most change emergent outcomes if added?

================================================================================
END OF DOCUMENT
================================================================================

Version: 1.0
Project: SIMSIV — D:\EXPERIMENTS\SIM
Contact: See project repository
