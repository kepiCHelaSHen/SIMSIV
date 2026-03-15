# SIMSIV — World Architecture Document
# The Complete Individual Model and Hierarchical Civilization Framework
# Location: D:\EXPERIMENTS\SIM\docs\world_architecture.md
# Last Updated: 2026-03-14
# Status: Band simulation COMPLETE — DD01-DD26 all done
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
  A band does not know about the tribe. The tribe does not know about individuals.
  Information flows UP as aggregate fingerprints.
  Pressure flows DOWN as environmental conditions (drought, war, disease at
  tribal level becomes resource scarcity at band level).

THE BAND FINGERPRINT (what gets exported upward — 15 values):
  1.  avg_aggression_index        — how warlike is this band
  2.  avg_cooperation_index       — how tradeable / alliance-worthy
  3.  resource_level              — wealth and desperation
  4.  population_size             — fighting-age members
  5.  law_strength                — how organized / law-abiding
  6.  dominant_faction_type       — prestige-led vs dominance-led
  7.  avg_health_index            — disease burden, wellbeing
  8.  kinship_density             — how related are members
  9.  cultural_identity_score     — faction cohesion, dominant belief vector
  10. avg_intelligence_index      — adaptive capacity
  11. reproductive_rate           — population growth trajectory
  12. institutional_stability     — is law_strength rising or falling
  13. has_war_leader              — bool: formal military coordination exists
  14. leadership_quality          — combined prestige+dominance of leaders / band avg
  15. big_man_present             — bool: proto-chiefdom signal (cross-faction influence)

================================================================================
SECTION 3 — THE BAND SIMULATION (DD01-DD26 COMPLETE)
================================================================================

The band simulation is the most complex level — it simulates every individual
person. All 26 deep dives are complete. This is the v1.0 core engine.

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
  9.  Metrics           — collect all ~120 stats for this year
  10. Equilibrium check

--------------------------------------------------------------------------------
3A. THE AGENT — WHAT EVERY PERSON IS
--------------------------------------------------------------------------------

Every agent is a simulated human being with:

HERITABLE TRAITS — 26 total (passed to offspring via h²-weighted inheritance):
  Original 8 (DD01-DD04):
    aggression_propensity    [0.0-1.0]  h²~0.44  tendency toward conflict
    cooperation_propensity   [0.0-1.0]  h²~0.40  tendency toward alliance
    attractiveness_base      [0.0-1.0]  h²~0.50  baseline physical mate value
    status_drive             [0.0-1.0]  h²~0.50  motivation to seek dominance
    risk_tolerance           [0.0-1.0]  h²~0.48  willingness to take risks
    jealousy_sensitivity     [0.0-1.0]  h²~0.45  trigger for jealousy-driven conflict
    fertility_base           [0.0-1.0]  h²~0.50  baseline reproductive capacity
    intelligence_proxy       [0.0-1.0]  h²~0.65  resource acquisition efficiency

  DD15 — Biological robustness (4):
    longevity_genes          [0.0-1.0]  h²~0.25  modifies lifespan +/- 10yr
    disease_resistance       [0.0-1.0]  h²~0.40  reduces epidemic vulnerability
    physical_robustness      [0.0-1.0]  h²~0.50  reduces conflict health damage
    pain_tolerance           [0.0-1.0]  h²~0.45  modifies flee threshold

  DD15 — Psychological (4):
    mental_health_baseline   [0.0-1.0]  h²~0.40  stress resistance, orchid/dandelion gate
    emotional_intelligence   [0.0-1.0]  h²~0.40  speeds trust formation, gossip acuity
    impulse_control          [0.0-1.0]  h²~0.50  gates aggression trait → actual behavior
    novelty_seeking          [0.0-1.0]  h²~0.40  exploration, migration drive

  DD15 — Social (3):
    empathy_capacity         [0.0-1.0]  h²~0.35  extends cooperation altruism radius
    conformity_bias          [0.0-1.0]  h²~0.35  norm adoption speed
    dominance_drive          [0.0-1.0]  h²~0.50  active dominance hierarchy seeking

  DD15 — Reproductive biology (2):
    maternal_investment      [0.0-1.0]  h²~0.35  quantity vs quality offspring tradeoff
    sexual_maturation_rate   [0.0-1.0]  h²~0.60  age at first reproduction variance

  DD17 — Heritable condition risks (5):
    cardiovascular_risk      [0.0-1.0]  h²~0.50  heritable cardiovascular condition risk
    mental_illness_risk      [0.0-1.0]  h²~0.60  heritable psychiatric condition risk
    autoimmune_risk          [0.0-1.0]  h²~0.40  heritable immune dysfunction risk
    metabolic_risk           [0.0-1.0]  h²~0.45  heritable metabolic condition risk
    degenerative_risk        [0.0-1.0]  h²~0.35  heritable degenerative condition risk

INHERITANCE MODEL (DD15):
  child_val = h² * parent_midpoint + (1 - h²) * population_mean + mutation
  Parent weight: w ~ N(0.5, 0.1) — random blend, not always exact 50/50
  Mutation: 95% at sigma=0.05, 5% rare large jump at sigma=0.15
  Stress mutation: scarcity amplifies sigma by up to 1.5x (DD04)
  Epigenetic boost: stressed parents increase offspring mutation sigma (DD24)
  Correlation matrix: 26x26 built programmatically from behavioral genetics lit
  Migrant traits: drawn from current population distribution (not uniform)

GENOTYPE vs PHENOTYPE (DD16):
  Genotype: raw genetic values stored at birth, passed to offspring unchanged
  Phenotype: expressed values after developmental modification at age 15
  Developmental modifiers (capped ±0.10 per trait):
    + childhood resource quality → intelligence, impulse control boost
    + parental trait modeling → social learning (cooperation, aggression)
    + trauma (parent death before age 10) → aggression boost, trust reduction
    + peer group effects (age 5-15) → conformity_bias weighted average
    + birth order effects → small risk/conscientiousness adjustments
  mental_health_baseline gates plasticity magnitude (orchid vs dandelion)
  breed() reads genotype — selection operates on genetic potential, not
  environmentally modified phenotype

NON-HERITABLE STATE (earned, not passed to offspring):
  health                    [0.0-1.0]  decays with age, damaged by conflict/starvation
  reputation                [0.0-1.0]  public standing — aggregate of how others see you
  prestige_score            [0.0-1.0]  earned through cooperation, generosity, networks
  dominance_score           [0.0-1.0]  earned through conflict victories, intimidation
  current_resources         float      subsistence resources (DD21: food/shelter)
  current_tools             float      durable tools (DD21: multiplies subsistence)
  current_prestige_goods    float      social goods (DD21: boosts mate value/prestige)
  paternity_confidence      [0.0-1.0]  male's confidence in paternity
  conflict_cooldown         int        years of post-combat subordination
  trauma_score              [0.0-1.0]  accumulated life trauma (DD17/DD24)
  epigenetic_stress_load    [0.0-1.0]  transgenerational stress accumulation (DD24)
  faction_id                int/None   which emergent faction agent belongs to

CULTURAL BELIEFS — 5 dimensions, non-heritable (DD25):
  Transmitted via social learning, experience, and prestige bias.
  Range: [-1.0 to +1.0] for all dimensions.
  hierarchy_belief         [-1=egalitarian → +1=hierarchical]
  cooperation_norm         [-1=defection acceptable → +1=prosocial obligation]
  violence_acceptability   [-1=pacifist → +1=violence is honorable]
  tradition_adherence      [-1=innovator → +1=conservative]
  kinship_obligation       [-1=universalist → +1=in-group only]

SKILLS — 4 domains, non-heritable, experiential (DD26):
  Grow through practice, decay without use, transmit via mentoring.
  Range: [0.0 to 1.0] for all domains.
  foraging_skill    — resource acquisition efficiency multiplier
  combat_skill      — combat power additive bonus
  social_skill      — trust formation and gossip effectiveness
  craft_skill       — tool production multiplier (active if DD21 enabled)

RELATIONSHIPS:
  partner_ids               list[int]  current mates (supports polygyny)
  pair_bond_strengths       dict       strength per partner [0.0-1.0]
  offspring_ids             list[int]  all children ever born (incl. dead)
  parent_ids                tuple      (mother_id, father_id) — genetic parents
  reputation_ledger         dict       sparse bilateral trust scores (cap 100)
  neighborhood_ids          list[int]  proximity tier — refreshed every 3yr (DD18)
  epc_partner_id            int/None   extra-pair mate this tick (cleared each tick)

MEDICAL HISTORY (DD17):
  active_conditions         set[str]   currently active heritable conditions
  trauma_score              float      accumulated life trauma [0.0-1.0]
  medical_history           list[dict] life medical log (max 50 entries)

MIGRATION TRACKING (DD19):
  origin_band_id            int        0=native, 1=immigrant from external pool
  immigration_year          int/None   year arrived (None = native)
  generation_in_band        int        cultural integration depth

DEVELOPMENTAL TRACKING (DD16):
  genotype                  dict       original genetic values, never modified
  childhood_resource_quality float     avg parental resources during age 0-5
  childhood_trauma          bool       parent died before age 10
  traits_finalized          bool       set True at maturation (age 15)

LIFE STAGE — computed property (DD22):
  CHILDHOOD  (age < 15)    — learning, trait development, high mortality risk
  YOUTH      (age 15-24)   — high risk-taking, intense status competition, coalition building
  PRIME      (age 25-44)   — peak production, parenting, faction leadership eligible
  MATURE     (age 45-59)   — advisory role, elevated social memory, elder transition
  ELDER      (age 60+)     — norm anchor, institutional stability, cultural memory

DYNAMIC COMPUTED PROPERTIES:
  mate_value = (health*0.3 + attractiveness*0.25 + prestige*0.12 + dominance*0.08
               + resources_norm*0.15 + reputation*0.1) * age_factor
               + prestige_goods * prestige_goods_mate_signal
  life_stage = computed from age (never stored)
  is_fertile = alive AND health > 0.2 AND age in reproductive window
  is_bonded = len(partner_ids) > 0

LIVING BIOGRAPHY:
  Every agent that has ever lived has: year_of_birth, parent IDs, complete
  partner history with years, all children ever born, cause_of_death,
  year_of_death, faction membership, complete medical history, all conflict
  events, all cooperation events, skill trajectory, belief evolution.
  This constitutes a readable life narrative — the raw material for the
  biography tab planned for the dashboard.

--------------------------------------------------------------------------------
3B. THE ENGINES — WHAT DRIVES BEHAVIOR
--------------------------------------------------------------------------------

ENGINE 1: ENVIRONMENT
  Scarcity shocks: 3% base annual probability, amplified by overcrowding
  Seasonal cycles: cosine wave modulation (amplitude 0.3, period 3yr) [DD10]
  Epidemic triggers: 2% base probability, 20yr refractory period [DD09]
  Scarcity computed ONCE per tick — all engines read the same value (determinism guarantee)

ENGINE 2: RESOURCES (8-phase + DD21 resource types)
  Three resource types: subsistence (food/shelter), tools (durable multipliers),
                        prestige goods (social value, near-permanent)
  Phase 0:  Kin trust maintenance (parents+children +0.02/yr, siblings +0.01/yr)
  Phase 0b: Childhood quality tracking (resource environment during age 0-5)
  Phase 1:  Resource decay (type-specific: subsistence 0.4, tools 0.1, prestige 0.05)
            Intelligence-mediated storage bonus up to +20% [DD10]
  Phase 2:  Survival distribution (25% equal floor, 75% competitive)
            Competitive weight = (intel*0.25 + prestige*0.175 + dominance*0.075
                                 + experience*0.15 + wealth^0.7*0.15 + network*0.05
                                 + foraging_skill*multiplier)^3
                                 * (1 - aggression * 0.3)
                                 * (1 - metabolic_condition_penalty)
  Phase 3:  Child investment costs (0.5 res/child/yr, scaled by paternity confidence)
  Phase 4:  Cooperation sharing (neighborhood-tier first [DD18], trust > 0.5,
            empathy_capacity and emotional_intelligence modulate)
            Ostracism: low-reputation agents excluded [DD11]
  Phase 5:  Status distribution (prestige pool 60%, dominance pool 40%)
  Phase 6:  Elite privilege (top 10% status, additive bonus capped at 2x base)
  Phase 7:  Taxation (top quartile → bottom quartile, gated by law_strength)
  Phase 8:  Subsistence floor (minimum resources — prevents death spirals)
  Signaling: Resource display (honest, 5% cost, builds prestige) [DD12]
  Beliefs effect: cooperation_norm belief modulates sharing rate [DD25]
  Life stage: mature/elder agents have reduced resource appetite, youth peak

ENGINE 3: CONFLICT
  Probability: base_p * aggression * impulse_control_gate [DD15]
               + jealousy_boost + resource_stress + status_drive
               * institutional_suppression * cooperation_damping
               * network_deterrence * subordination_factor
               * seasonal_lean_boost * life_stage_modifier [DD22]
               * violence_acceptability_belief [DD25]
  Proximity weighting: household 4x, neighborhood 2x, band 1x [DD18]
  Target selection: low trust + rival + similar status + resource envy
                    - network deterrence - dominance deterrence
  Flee: pain_tolerance and risk_tolerance gate escape probability [DD15]
  Coalition defense: trusted neighborhood allies intervene [DD11/DD18]
  War leader bonus: faction combat coordination boost [DD20]
  Combat power: aggression*0.25 + status(dom*0.7+pres*0.3)*0.20 + health*0.25
               + risk*0.15 + resource_edge + intel*0.05 + ally_bonus
               + combat_skill*0.15 [DD26]
  Scaled consequences: 0.7x close fights → 1.5x stomps
  Trauma accumulation: conflict loss adds to trauma_score [DD17]
  Skill gain: combat_skill grows from wins (more from beating skilled opponents)
  Third-party punishment: high-cooperation agents punish at personal cost [DD11]

ENGINE 4: MATING
  Phase 1: Clean stale bonds (dead partners → mourning state)
  Phase 2: Dissolve bonds (probability = base * strength_factor * resource_stress)
  Phase 3: Form pairs
    Female choosiness: age-adjusted, resource desperation modifier
    Neighborhood-first search: band-wide candidates at 0.3x weight [DD18]
    Weights: mate_value * trust_bonus * aggression_penalty(0.5) * coop_bonus(0.4)
             * prestige_goods_signal [DD21] * social_skill_assessment [DD26]
    kinship_obligation belief modulates endogamy preference [DD25]
    Male contest: 30% chance rival challenges, combat_skill matters [DD26]
  Phase 4: Extra-pair copulation
    Probability: infidelity_base * mate_value_gap * (1 - bond_strength)
    Detection: jealousy_sensitivity * jealousy_detection_rate
  Phase 5: Strengthen bonds
  Leadership: peace chief arbitration reduces intra-faction conflict [DD20]

ENGINE 5: REPRODUCTION
  Conception: base * fertility_mod * resource_mod * health_mod * seasonal_phase
  h²-weighted inheritance with DD15 heritability model
  Epigenetic sigma boost if parents have stress load [DD24]
  Developmental tracking begins at birth (childhood_resource_quality updated annually)
  Maturation at age 15: developmental modifications applied, genotype preserved
  Birth interval: 2yr minimum; age-specific fertility curve [DD06/DD13]
  Skill transmission: child starts at parent_skill * 0.3 at maturation [DD26]
  Belief initialization: conformity_bias-weighted blend of parent beliefs [DD25]

ENGINE 6: MORTALITY
  Health decay: base_rate + age_acceleration (post-30: +0.002/yr)
  Longevity genes modulate maximum lifespan [DD15]
  Scarcity health damage, starvation damage
  Male differential: 1.8x background mortality age 15-40 [DD13]
  Childhood mortality: resource-dependent, orphan 2x, grandparent -0.05 [DD06]
  Epidemic mortality: faction disease_resistance buffering [DD09/DD15]
  Active condition effects: cardiovascular/degenerative accelerate health decay [DD17]

ENGINE 6.3: MIGRATION (DD19)
  Emigration push factors: resource stress, ostracism, mating failure, subordination
  Youth males most likely to emigrate for mating reasons
  Family anchor: bonded agents with children much less likely to emigrate
  Immigration pull factors: resource surplus, low population, high cooperation
  Immigrant integration: trust=0.4 toward all, factionless until integrated
  Seasonal multiplier: migration more likely in lean seasons [DD10]

ENGINE 6.5: PATHOLOGY (DD17/DD24)
  Condition activation: annual probability = base * trigger_multipliers
  Triggers: age, resource stress, childhood trauma, recent injury, scarcity
  Active condition effects: health decay boost, behavioral instability,
                             epidemic vulnerability, resource penalty
  Trauma accumulation: conflict loss +0.05, kin death +0.04, deprivation +0.02/yr
  Trauma contagion: high-trauma agents spread trauma to trusted contacts [DD24]
  Epigenetic load: accumulates from scarcity/epidemics/trauma events [DD24]
  Recovery: slow decay when resources adequate and socially connected
  Institutional response: band-wide trauma epidemic → law_strength drift boost

ENGINE 7: INSTITUTIONS
  Phase 1: Inheritance (all deaths this tick — violence + natural)
    Resource types inherit differently: tools primary, subsistence mostly consumed
    Prestige goods → heirs gain prestige_score boost
  Phase 2: Norm enforcement
  Phase 3: Institutional drift
    cooperation_pressure = (avg_cooperation - 0.4) * boost
    violence_pressure = violence_rate * decay
    belief_influence: cooperation_norm and violence_acceptability beliefs
                      add to drift pressure [DD25]
    Elder presence: respected elders slow institutional decay [DD22]
  Phase 4: Emergent formation
  Peace chief: arbitration, cooperation coordination, norm transmission [DD20]
  Trauma epidemic: triggers additional law_strength drift toward stronger norms [DD24]

ENGINE 8: REPUTATION
  Phase 1: Trust decay toward neutral
  Phase 2: Dead agent cleanup
  Phase 3: Gossip — within proximity tier first (lower noise), cross-tier 2x noise [DD18]
  Phase 4: Aggregate reputation update
  Phase 5: Belief evolution (every 3 ticks) [DD25]
    Social influence: prestige-weighted neighbor beliefs
    Experience update: wins/losses/sharing shift beliefs
    Cultural mutation: novelty_seeking-scaled random drift
    Ideological tension: large belief divergence generates distrust
  Phase 6: Skill updates [DD26]
    Foraging: above-average yield → skill growth
    Social: cooperation events, new bonds, accurate gossip
    Combat: updated in conflict engine
    Mentoring: high-skilled faction members transmit to low-skilled
    Elder teaching: age 55+ high social_skill agents boost young members
  Phase 7: Faction detection (every 5yr) — connected-component analysis
  Phase 8: Neighborhood refresh (every 3yr) [DD18]
    Priority: trust > 0.5 ledger entries + same faction + shared parents

LEADERSHIP LAYER (DD20) — runs within faction detection:
  War leader: highest dominance_score in faction
    Effects: conflict initiation boost, coalition defense, combat power bonus,
             targeting deterrence for faction members
  Peace chief: highest prestige_score in faction
    Effects: dispute arbitration, cooperation boost, norm transmission,
             elder-style institutional stability
  Big man: cross-faction high trust → proto-chiefdom signal in fingerprint
  Tenure: must demonstrate competence or role passes to next highest

--------------------------------------------------------------------------------
3C. ENVIRONMENT MODEL
--------------------------------------------------------------------------------

  Resource multiplier: abundance_multiplier + volatility_noise (Gaussian)
  Scarcity events: overcrowding-amplified, 2-6yr duration, 20yr refractory [DD09]
  Seasonal cycles: cosine wave, amplitude 0.3, period 3yr [DD10]
    - Affects: resource production, birth timing, conflict probability, migration
  Epidemics: 2% base, differential vulnerability, faction disease_resistance buffer [DD09]
  Carrying capacity: crowding penalty above 50% of max capacity
  Epigenetic triggers: severe scarcity adds to agent epigenetic_stress_load [DD24]

--------------------------------------------------------------------------------
3D. PROXIMITY TIERS (DD18)
--------------------------------------------------------------------------------

Three-tier relational proximity model (no spatial coordinates):

  HOUSEHOLD (3-8 agents):
    Who: partners + dependent children + living parents
    Computed dynamically each tick from relationship state
    Interaction multiplier: 4x for all engines
    Cooperation sharing: highest rate, lowest ostracism threshold

  NEIGHBORHOOD (up to 40 agents):
    Who: trust > 0.5 ledger entries + same faction members + shared-parent kin
    Computed every 3 years
    Interaction multiplier: 2x for all engines
    Primary arena: most conflict, most cooperation, most gossip

  BAND (full population):
    Who: everyone else
    Interaction multiplier: 1x (current default behavior for out-of-neighborhood)
    Mate search: band-level males available at 0.3x weight

--------------------------------------------------------------------------------
3E. METRICS — WHAT THE BAND PRODUCES (~120 per tick)
--------------------------------------------------------------------------------

DEMOGRAPHICS: population, males, females, births, deaths, infant_deaths,
  childhood_deaths, orphan_count, children_count, max_generation,
  sex_ratio_reproductive, male_deaths, female_deaths, childbirth_deaths,
  life_stage_distribution (fraction in each stage)

ECONOMICS: resource_gini, status_gini, avg_resources, avg_tools,
  avg_prestige_goods, resource_top10_share, cooperation_network_size,
  resource_transfers, trade_events, tool_gini, civilization_stability (CSI),
  social_cohesion (SCI)

REPRODUCTION: reproductive_skew, mating_inequality, unmated_male_pct,
  unmated_female_pct, elite_repro_advantage, child_survival_rate,
  pair_bonded_pct, infidelity_rate, epc_detected, paternity_uncertainty,
  avg_bond_strength, mating_contests, avg_lifetime_births, avg_maternal_health,
  local_mate_rate (fraction of bonds formed within neighborhood)

CONFLICT: conflicts, violence_rate, flee_events, violence_deaths,
  punishment_events, agents_in_cooldown, coalition_defenses,
  third_party_punishments, ostracized_count, youth_conflict_rate,
  cross_tier_conflict_rate

SOCIAL: gossip_events, avg_ledger_size, avg_trust, distrust_fraction,
  avg_reputation, bluff_attempts, bluff_detections, faction_count,
  largest_faction_size, faction_size_gini, faction_stability,
  inter_faction_conflict_rate, factionless_fraction, avg_household_size,
  avg_neighborhood_size, network_clustering_coefficient

INSTITUTIONS: law_strength, violence_punishment, property_rights,
  inheritance_events, norm_violations, institutions_emerged

TRAITS (26): avg and std for all 26 heritable traits

BELIEFS (5): avg_hierarchy_belief, avg_cooperation_norm,
  avg_violence_acceptability, avg_tradition_adherence,
  avg_kinship_obligation, belief_polarization (std per dimension),
  dominant_ideology (categorical), belief_revolution_events

SKILLS (4): avg_foraging_skill, avg_combat_skill, avg_social_skill,
  avg_craft_skill, skill_gini (per domain), mentor_events,
  specialist_count, skill_age_correlation

MIGRATION: emigration_count, immigration_count, immigrant_fraction,
  avg_generation_in_band, trait_import_delta

LEADERSHIP: war_leader_count, peace_chief_count, leadership_interventions,
  big_man_present, faction_leader_turnover

PATHOLOGY/EPIGENETICS: active_conditions_count, avg_trauma_score,
  condition_prevalence (by type), trauma_contagion_events, band_trauma_index,
  trauma_epidemic_active, avg_epigenetic_load, epigenetic_lineages

ENVIRONMENT: scarcity, epidemic_active, epidemic_deaths, seasonal_phase

STATUS/HEALTH: avg_prestige, avg_dominance, prestige_gini, dominance_gini,
  prestige_dominance_corr, avg_health, avg_age, avg_lifespan, pop_growth_rate

--------------------------------------------------------------------------------
3F. KEY EMERGENT FINDINGS (calibrated results)
--------------------------------------------------------------------------------

All findings emerge without being programmed. Selected from multi-seed runs:

1. COOPERATION AND INTELLIGENCE CONSISTENTLY SELECTED FOR
   Across all tested scenarios, cooperation and intelligence trend upward.
   Multiple independent selection channels operate simultaneously.

2. AGGRESSION CONSISTENTLY SELECTED AGAINST
   Female mate choice (-0.5 weight), resource penalty (production penalty),
   conflict mortality, prestige cost, bond destabilization — all punish aggression
   independently. The effect is robust across all mating system scenarios.

3. INSTITUTIONS SUBSTITUTE FOR TRAITS
   STRONG_STATE: cooperation trait 0.527 vs BASELINE 0.564
   When law enforces cooperative behavior, genetic selection pressure relaxes.
   External enforcement crowds out internal motivation. Genuine finding in
   institutional economics, emergent in simulation.

4. EMERGENT INSTITUTIONS SELF-ORGANIZE
   Law strength: 0 → 0.48 over 200yr in EMERGENT_INSTITUTIONS scenario
   Driven purely by cooperation/violence balance. No designer required.

5. MONOGAMY REDUCES VIOLENCE AND UNMATED MALES
   ENFORCED_MONOGAMY: violence -37%, unmated males -40% vs FREE_COMPETITION

6. ELITE POLYGYNY MAXIMIZES INEQUALITY
   Gini 0.468 — highest of all scenarios — but not highest violence.
   Resource privilege effect dominates mating competition effect.

7. FACTIONS EMERGE FROM KIN TRUST CLUSTERS
   Connected-component detection on trust graph produces 45 peak factions in
   500-pop run, consolidating over time. Not assigned, not scripted.

8. !KUNG VALIDATION
   Baseline violence rate 0.018 vs real !Kung San ~0.02.
   Not tuned for — emerged from calibrated parameters.

================================================================================
SECTION 4 — COMPLETED DEEP DIVES SUMMARY
================================================================================

All 26 deep dives complete. Design docs in docs/deep_dive_*.md.

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
| 15  | Extended Genomics         | 13 new traits, real h² model, 26x26 correlation matrix|
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

Totals: ~250 config params, ~120 metrics per tick, 9 engines (+pathology)

================================================================================
SECTION 5 — WORLD ARCHITECTURE (HIGHER LEVELS — PLANNED V2/V3)
================================================================================

DESIGN PHILOSOPHY FOR HIGHER LEVELS:
  Each level runs its own simulator simpler than the level below.
  Computational complexity decreases going up.
  Individual biography only exists at band level.
  At clan level and above, people are represented as statistics.

THE CLAN SIMULATOR (v2 — planned)
  Inputs: Band fingerprints from 5-15 member bands (15 values each)
  Tick: Decadal (10yr per clan tick = ~10 band annual ticks)

  What the clan simulator computes:
  - Inter-band trade probability = f(resource_gap, cooperation_index, trust)
  - Raid probability = f(aggressor_aggression, target_resources, defender_network)
  - Intermarriage rate = f(faction_alignment, cultural_distance, resource_level)
  - Migration flow = f(resource_desperation, population_pressure, kinship_density)
  - Cultural drift = conformity_bias weighted avg of member band belief vectors
  - Alliance formation = f(shared_enemies, cooperation_index, historical_trust)
  - Leadership recognition = f(big_man signals from member bands)

  Band → Clan transition (not a building — a threshold crossing):
  - Multiple bands sharing territory with kinship links above threshold
  - Inter-band cooperation rate above threshold for N years
  - No sustained raiding between members for N years
  - Shared cultural identity (belief vector similarity) above threshold

  Clan fingerprint: same 15 metrics as band, now representing 150-2000 people

THE TRIBE SIMULATOR (v2 — planned)
  Inputs: Clan fingerprints from 5-15 member clans
  Tick: Generational (25yr per tribe tick)

  What the tribe simulator computes:
  - Cultural identity score (shared beliefs, language proxy, ritual alignment)
  - Territorial boundaries (spatial extent, defended perimeter)
  - Inter-clan warfare (aggregate power calculations)
  - Trade network structure (alliance-weighted exchange graph)
  - Norm standardization (institutional drift toward mean across clans)

  Clan → Tribe transition:
  - Shared cultural identity above threshold
  - Regular inter-clan trade for N years
  - Coordinated response to external threat
  - Common institutional norms within tolerance range

THE CHIEFDOM SIMULATOR (v3 — planned)
  Inputs: Tribe fingerprints
  What emerges:
  - Hereditary leadership (band with highest prestige + resources + faction size)
  - Tribute flow (weaker tribes pay stronger tribes resources)
  - Monument/infrastructure (surplus above threshold → collective investment)
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
  ├── config.py              — ~250 tunable parameters (grouped by DD)
  ├── simulation.py          — tick orchestrator (12 clean numbered steps)
  ├── main.py               — CLI entry point
  ├── requirements.txt       — numpy, pandas, matplotlib, pyyaml, streamlit, scipy
  ├── models/
  │   ├── agent.py           — Agent dataclass (26 traits, beliefs, skills, etc.)
  │   ├── society.py         — Agent registry, faction detection, migration
  │   └── environment.py     — Scarcity, seasons, epidemics
  ├── engines/
  │   ├── resources.py       — 8-phase resource distribution + DD21 types
  │   ├── conflict.py        — Violence, deterrence, coalitions, life stages
  │   ├── mating.py          — Pair bonds, EPC, infidelity, proximity
  │   ├── reproduction.py    — Conception, birth, developmental biology
  │   ├── mortality.py       — Aging, health, death, maturation
  │   ├── pathology.py       — Conditions, trauma, epigenetics (DD17/DD24)
  │   ├── institutions.py    — Inheritance, norms, drift, emergence, leadership
  │   └── reputation.py      — Gossip, trust, beliefs, skills, factions
  ├── metrics/
  │   └── collectors.py      — ~120 metrics per tick
  ├── experiments/
  │   ├── scenarios.py       — 10 named scenario configs
  │   ├── runner.py          — Multi-seed experiment execution
  │   └── summarizer.py      — Narrative summaries, integrity checks
  ├── autosim/
  │   ├── runner.py          — Mode A parameter optimization loop
  │   ├── realism_score.py   — Composite score vs anthropological targets
  │   ├── targets.yaml       — Calibration targets with sources
  │   ├── program.md         — Agent instructions
  │   ├── journal.jsonl      — Experiment log (all 100 experiments)
  │   └── best_config.yaml   — Best parameters found
  ├── dashboard/
  │   └── app.py             — Streamlit visual dashboard (9 tabs)
  ├── sandbox/
  │   └── explore.py         — IPython harness for live exploration
  ├── tests/
  │   └── test_smoke.py      — 5 pytest smoke tests (all passing)
  ├── docs/
  │   ├── world_architecture.md  — THIS FILE
  │   ├── deep_dive_01-26.md     — Design rationale per subsystem
  │   ├── AUTOSIM.md             — Autosim design document
  │   └── MISSION.md             — Project mission statement
  ├── devlog/
  │   └── DEV_LOG.md         — Complete development history
  └── prompts/
      ├── README.md          — Index of all 26 deep dive prompts
      └── deep_dive_*.md     — 26 implementation prompts

ARCHITECTURE GUARANTEES:
  - Pure library: no IO, no print statements in engines
  - Deterministic: same seed = identical results
  - Modular: engines share no state except via Society
  - No circular imports: models never import engines
  - All randomness via seeded numpy.random.Generator

NAMED SCENARIOS (10 defined):
  FREE_COMPETITION      — baseline, unrestricted, null hypothesis
  ENFORCED_MONOGAMY     — mating_system="monogamy", law=0.7
  ELITE_POLYGYNY        — elite_privilege=3.0, max_mates=5
  HIGH_FEMALE_CHOICE    — female_choice_strength=0.95
  RESOURCE_ABUNDANCE    — resource_abundance=2.5
  RESOURCE_SCARCITY     — resource_abundance=0.4, scarcity_prob=0.15
  HIGH_VIOLENCE_COST    — violence_cost_health=0.45, death_chance=0.15
  STRONG_PAIR_BONDING   — bond_strength=0.9, dissolution_rate=0.02
  STRONG_STATE          — law=0.8, tax=0.15, property_rights=0.5
  EMERGENT_INSTITUTIONS — all institutions start at 0, self-organize

================================================================================
SECTION 7 — WHAT THIS IS BUILDING TOWARD
================================================================================

The ultimate goal is a Civilization-style game where:

1. Every person in the game world is a real simulated individual with a genome,
   a developmental history, a medical biography, skills earned through experience,
   cultural beliefs transmitted from their community, relationships, and a
   complete life story from birth to death

2. Social structures — bands, clans, tribes, chiefdoms, states — emerge from
   what those individuals do, not from what the game designer scripted

3. The player interacts at multiple levels simultaneously:
   - Zoom in: see individual people living their lives
   - Zoom out: see civilizations rising and falling

4. Every war, every alliance, every cultural practice, every dynasty emerged
   from the rules — nobody wrote the story

5. Scale: ~3-5 million fully simulated individuals across a world map, with
   hundreds of millions represented statistically at higher levels

CURRENT STATE: Band simulator v1.0 complete — all 26 deep dives done.
This is the most complex and important level. All other levels will be simpler
to build because they operate on aggregate fingerprints rather than individuals.

WHAT MAKES THIS DIFFERENT FROM EVERYTHING THAT EXISTS:
  - Civ VI simulates civilizations but has no real people inside them
  - The Sims simulates people but has no civilization around them
  - Dwarf Fortress has personality but no emergent biology or evolution
  - SIMSIV has real people (26 heritable traits, developmental plasticity,
    medical histories, skills, beliefs, living biographies) inside real
    societies (emergent institutions, factions, norms, cultural transmission)

The people are real in a way no simulated people have ever been before.
The civilizations they build will be real in a way no simulated civilizations
have ever been before.

================================================================================
SECTION 8 — OPEN QUESTIONS FOR V2 DESIGN
================================================================================

These are the unresolved design questions for the clan/tribe simulators:

1. TEMPORAL SCALE TRANSLATION
   Band sim runs at annual tick. Clan sim should run at decadal tick.
   How do we handle the 10:1 compression? Does one clan tick consume
   10 band ticks, or do bands run continuously and export snapshots?

2. BAND FINGERPRINT COMPLETENESS
   Does the 15-value fingerprint capture enough for realistic clan dynamics?
   What interactions would require individual agent data to model correctly
   (and therefore can't be abstracted without information loss)?

3. BAND → CLAN TRANSITION THRESHOLDS
   What exact metric values trigger clan recognition?
   Should this be sharp (threshold crossing) or gradual (continuous)?

4. CULTURAL DIVERGENCE TRACKING
   Two bands with the same starting population will evolve different belief
   vectors and trait distributions. How do we quantify "cultural distance"
   for the clan simulator's cultural drift mechanics?

5. PLAYER INTERACTION LAYER
   At which hierarchy levels should the player have direct agency?
   Band level (individual decisions), clan level (inter-band policy),
   tribe level (territorial strategy), or all three simultaneously?

6. PERFORMANCE ARCHITECTURE FOR V2
   Thousands of bands running simultaneously on a world map requires
   parallel execution. What's the right parallelization strategy?
   Process-per-band? Thread pool? GPU vectorization?

================================================================================
END OF DOCUMENT
================================================================================

Version: 2.0 (DD01-DD26 complete)
Project: SIMSIV — D:\EXPERIMENTS\SIM
GitHub: https://github.com/kepiCHelaSHen/SIMSIV
