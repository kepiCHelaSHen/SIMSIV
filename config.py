"""
SIMSIV Configuration
All tunable parameters in one place. Sensible defaults for baseline (FREE_COMPETITION).
"""

from dataclasses import dataclass, field, asdict
from pathlib import Path
import yaml


@dataclass
class Config:
    # ── Scale ────────────────────────────────────────────────────────
    population_size: int = 500
    years: int = 100
    seed: int = 42

    # ── Agent initialization ─────────────────────────────────────────
    # Initial age distribution: uniform 0 to this value
    init_max_age: int = 50
    # Trait correlation: if True, use correlated multivariate normal for initial traits
    correlated_traits: bool = True

    # ── Mating ───────────────────────────────────────────────────────
    mating_system: str = "unrestricted"  # "unrestricted", "monogamy", "elite_polygyny"
    female_choice_strength: float = 0.6  # 0=random, 1=pure best-available
    male_competition_intensity: float = 0.7
    pair_bond_strength: float = 0.5
    pair_bond_dissolution_rate: float = 0.1  # per year probability of bond breaking
    max_mates_per_male: int = 999  # effectively unlimited for unrestricted
    mating_pool_fraction: float = 0.7  # fraction of eligible agents who attempt mating each tick
    max_mates_per_female: int = 1  # default monandrous
    female_choosiness_age_effect: float = -0.01  # choosiness per year past 30
    male_contest_injury_risk: float = 0.05  # health damage to loser in mating contest
    infidelity_enabled: bool = True
    infidelity_base_rate: float = 0.05  # annual EPC probability for bonded females
    jealousy_detection_rate: float = 0.4  # base probability of detecting infidelity
    paternity_certainty_threshold: float = 0.7  # below this, male reduces investment
    widowhood_mourning_years: int = 1  # years before re-entering mating pool

    # ── Reproduction ─────────────────────────────────────────────────
    age_first_reproduction: int = 15
    age_max_reproduction_female: int = 45
    age_max_reproduction_male: int = 65
    child_dependency_years: int = 5
    base_conception_chance: float = 0.5  # per mating attempt per year (pre-industrial ~5-7 children/woman)
    mutation_sigma: float = 0.05  # Gaussian noise on heritable traits
    child_survival_base: float = 0.85  # baseline child survival to adulthood

    # DD04: Genetics deep dive
    parent_weight_variance: float = 0.1  # 0=exact 50/50, >0=random parent weighting per trait
    rare_mutation_rate: float = 0.05     # probability per trait of using large mutation
    rare_mutation_sigma: float = 0.15    # sigma for rare large mutations
    stress_mutation_multiplier: float = 1.5  # mutation sigma multiplier during scarcity
    migrant_trait_source: str = "population"  # "uniform" or "population" for rescue migrants

    # DD06: Household deep dive
    birth_interval_years: int = 2              # minimum years between births per female
    childhood_mortality_annual: float = 0.02   # annual death risk for children 0-15
    orphan_mortality_multiplier: float = 2.0   # mortality multiplier for parentless children
    grandparent_survival_bonus: float = 0.05   # child survival bonus if grandparent alive
    sibling_trust_growth: float = 0.01         # annual trust growth between co-living siblings
    max_lifetime_births: int = 12              # hard cap on births per female
    maternal_health_cost: float = 0.03         # health cost per birth to mother
    maternal_age_fertility_decline: float = 0.03  # fertility decline per year past 30 (female)

    # ── Resources ────────────────────────────────────────────────────
    resource_abundance: float = 1.0  # multiplier on base per-agent resources
    resource_volatility: float = 0.2  # year-to-year random variation
    carrying_capacity: int = 800
    base_resource_per_agent: float = 10.0  # base survival resources per tick
    status_resource_fraction: float = 0.3  # fraction of total resources as status-type
    inheritance_model: str = "equal_split"  # "equal_split", "primogeniture", "none"

    # DD02: Resource model deep dive
    resource_equal_floor: float = 0.25  # fraction of survival pool as equal share
    resource_decay_rate: float = 0.5  # fraction of resources retained year-to-year
    aggression_production_penalty: float = 0.3  # competitive weight penalty for aggression
    cooperation_network_bonus: float = 0.05  # competitive weight bonus per trusted ally
    cooperation_sharing_rate: float = 0.08  # max fraction shared with allies
    cooperation_trust_threshold: float = 0.5  # min trust to share / count as ally
    cooperation_min_propensity: float = 0.25  # min cooperation to participate in sharing
    wealth_diminishing_power: float = 0.7  # exponent for diminishing returns on wealth
    subsistence_floor: float = 1.0  # minimum resources after all calculations
    tax_rate: float = 0.0  # fraction taken from top earners (0 = no redistribution)
    child_investment_per_year: float = 0.5  # resources per dependent child per year
    scarcity_severity: float = 0.6  # resource multiplier during scarcity events

    # ── Conflict ─────────────────────────────────────────────────────
    violence_cost_health: float = 0.15  # health cost per conflict (to loser)
    violence_cost_resources: float = 0.1  # resource fraction lost by loser
    violence_death_chance: float = 0.05  # chance of death per conflict (loser)
    conflict_base_probability: float = 0.05  # random baseline conflict chance per agent
    jealousy_conflict_multiplier: float = 2.0  # multiplier when jealousy triggers conflict

    # DD03: Conflict deep dive
    flee_threshold: float = 0.3           # risk_tolerance below this → chance to flee
    network_deterrence_factor: float = 0.1  # per ally, reduces targeting weight
    bystander_trust_update: bool = True   # witnesses to violence update trust
    bystander_count: int = 3              # max witnesses per conflict
    subordination_cooldown_years: int = 2 # years of reduced aggression after losing
    subordination_dampening: float = 0.5  # conflict prob multiplier during cooldown
    combat_resource_factor: float = 0.1   # resource advantage weight in combat
    winner_status_scale: float = 0.05     # base status gain for winner (scaled by differential)
    loser_status_scale: float = 0.05      # base status loss for loser (scaled by differential)

    # ── Mortality ────────────────────────────────────────────────────
    age_death_base: int = 60  # mean natural death age
    age_death_variance: int = 15  # standard deviation of natural death age
    mortality_base: float = 0.02  # background annual death rate (accidents, disease)
    health_decay_per_year: float = 0.01  # base health decay rate
    min_health_survival: float = 0.05  # below this health, agent dies

    # ── Institutions ─────────────────────────────────────────────────
    monogamy_enforced: bool = False
    law_strength: float = 0.0  # 0=anarchy, 1=perfect enforcement
    elite_privilege_multiplier: float = 1.0  # resource multiplier for top-status agents
    inheritance_law_enabled: bool = True  # DD05: changed default True (resources shouldn't vanish)
    violence_punishment_strength: float = 0.0  # 0=none, 1=severe

    # DD05: Institutions deep dive
    institutional_drift_rate: float = 0.0      # max change in law_strength per year (0=static)
    institutional_inertia: float = 0.8         # resistance to change (0=fluid, 1=rigid)
    cooperation_institution_boost: float = 2.0   # cooperation weight in drift (applied to coop-0.4)
    violence_institution_decay: float = 3.0    # violence weight in drift (applied to violence_rate)
    emergent_institutions_enabled: bool = False  # allow spontaneous institution formation
    property_rights_strength: float = 0.0      # modulates conflict resource transfer (0=free loot, 1=protected)
    inheritance_prestige_fraction: float = 0.0  # fraction of deceased's status inherited by heirs

    # DD08: Prestige vs Dominance
    prestige_decay_rate: float = 0.01            # annual prestige decay
    dominance_decay_rate: float = 0.03           # annual dominance decay (faster)
    prestige_weight_in_mate_value: float = 0.6   # fraction of status from prestige in mate choice
    dominance_weight_in_combat: float = 0.7      # fraction of status from dominance in combat
    dominance_deterrence_factor: float = 0.3     # high dominance → less likely targeted

    # DD07: Reputation deep dive
    gossip_enabled: bool = True               # enable gossip/information spread
    gossip_rate: float = 0.1                  # probability per agent per tick of gossiping
    gossip_noise: float = 0.1                 # information degradation per hop
    trust_decay_rate: float = 0.01            # annual decay toward neutral (0.5)
    reputation_from_ledger: bool = True       # compute reputation from aggregate trust
    dead_agent_ledger_cleanup: bool = True    # remove dead agents from ledgers each tick
    max_reputation_ledger_size: int = 100     # configurable ledger cap

    # DD13: Demographics
    male_risk_mortality_multiplier: float = 1.8   # extra male mortality age 15-40
    childbirth_mortality_rate: float = 0.02       # per-birth female mortality risk
    adolescent_fertility_fraction: float = 0.6    # fertility multiplier age 15-19
    fertility_peak_age: int = 24                  # age of peak fertility

    # DD12: Status signaling
    signaling_enabled: bool = True
    resource_display_fraction: float = 0.05       # fraction of resources spent on display
    resource_display_prestige_boost: float = 0.03 # prestige gain from display
    bluff_base_probability: float = 0.05          # annual bluff attempt rate
    bluff_detection_base: float = 0.3             # base detection probability
    bluff_caught_reputation_loss: float = 0.15    # reputation hit if caught

    # DD11: Coalitions and third-party punishment
    third_party_punishment_enabled: bool = True
    punishment_willingness_threshold: float = 0.6  # min cooperation to punish
    punishment_cost_fraction: float = 0.05         # punisher's resource cost
    punishment_severity: float = 0.1               # resource loss on punished agent
    coalition_defense_enabled: bool = True
    coalition_defense_probability: float = 0.3     # base chance ally intervenes
    coalition_defense_trust_threshold: float = 0.65 # trust required to intervene
    ostracism_enabled: bool = True
    ostracism_reputation_threshold: float = 0.25   # below this = ostracized

    # DD10: Seasonal resource cycles
    seasonal_cycle_enabled: bool = True         # enable predictable resource cycles
    seasonal_amplitude: float = 0.3            # peak-to-trough resource variation
    seasonal_cycle_length: int = 3             # years per full cycle (1=annual, 3=triennial)
    resource_storage_cap: float = 20.0         # max resources an agent can store
    storage_intelligence_bonus: float = 0.2    # intelligence reduces storage decay
    seasonal_conflict_boost: float = 0.2       # conflict boost during lean cycle phase
    birth_timing_sensitivity: float = 0.2      # how much cycle affects conception

    # DD09: Disease and epidemics
    epidemic_base_probability: float = 0.02       # annual chance of epidemic starting
    epidemic_lethality_base: float = 0.15         # base mortality during epidemic year
    epidemic_duration_years: int = 2              # peak epidemic duration
    epidemic_child_vulnerability: float = 3.0     # mortality multiplier for age 0-10
    epidemic_elder_vulnerability: float = 2.0     # mortality multiplier for age 55+
    epidemic_health_threshold: float = 0.4        # below this health = extra vulnerable
    epidemic_refractory_period: int = 20          # min years between epidemics
    epidemic_overcrowding_multiplier: float = 2.0 # above 80% capacity → 2x risk

    # DD17: Medical history and pathology
    pathology_enabled: bool = True
    condition_activation_base: float = 0.02      # annual base activation probability
    condition_remission_rate: float = 0.15       # annual remission probability if resources adequate
    trauma_decay_rate: float = 0.01              # annual trauma recovery rate
    trauma_conflict_increment: float = 0.05      # trauma added per conflict loss
    trauma_grief_increment: float = 0.04         # trauma added per kin death
    cardiovascular_health_decay_boost: float = 0.005  # extra health decay when active
    mental_illness_decision_noise: float = 0.15  # random trait spike magnitude when active
    autoimmune_epidemic_vulnerability: float = 2.0    # multiplier during epidemic
    metabolic_resource_penalty: float = 0.15     # resource acquisition reduction when active
    degenerative_flee_threshold_boost: float = 0.15   # flee more easily when degenerated
    health_signal_visibility: float = 0.5        # how visible active conditions are to mates

    # DD16: Developmental biology (nature vs nurture)
    developmental_plasticity_enabled: bool = True
    childhood_resource_effect: float = 0.05      # max trait modification from resource quality
    parental_modeling_effect: float = 0.08        # max trait modification from parental traits
    orphan_aggression_boost: float = 0.06         # aggression increase for orphans at maturation
    peer_influence_effect: float = 0.03           # max trait modification from peer group
    critical_period_years: int = 5                # age at which first developmental mods apply
    birth_order_effect: float = 0.02              # birth order trait modification magnitude

    # DD15: Extended genomics — per-trait heritability
    # child_val = h² * parent_midpoint + (1 - h²) * pop_mean + mutation
    # None = use default TRAIT_HERITABILITY from agent.py
    heritability_by_trait: dict = field(default_factory=lambda: {})

    # DD14: Factions and in-group identity
    factions_enabled: bool = True
    faction_detection_interval: int = 5          # years between faction recomputation
    faction_min_trust_threshold: float = 0.65    # mutual trust required for same faction
    faction_min_size: int = 3                    # clusters below this = factionless
    faction_max_size: int = 50                   # schism pressure above this (Dunbar-inspired)
    in_group_sharing_bonus: float = 0.2          # sharing rate boost for in-group allies
    in_group_trust_threshold_reduction: float = 0.1  # lower trust needed for in-group sharing
    out_group_conflict_multiplier: float = 1.5   # inter-faction conflict targeting boost
    endogamy_preference: float = 0.1             # same-faction mate value boost
    faction_schism_pressure: float = 0.01        # annual schism probability above max_size
    faction_merge_trust: float = 0.8             # inter-leader trust required for faction merge

    # DD18: Proximity tiers
    proximity_tiers_enabled: bool = True
    household_interaction_multiplier: float = 4.0
    neighborhood_interaction_multiplier: float = 2.0
    neighborhood_size_max: int = 40
    neighborhood_refresh_interval: int = 3       # years between recomputation
    neighborhood_trust_threshold: float = 0.5    # min trust to be in neighborhood
    band_mate_weight: float = 0.3               # mate weight for out-of-neighborhood males
    cross_tier_gossip_noise_multiplier: float = 2.0

    # DD19: Migration dynamics
    migration_enabled: bool = True
    base_emigration_rate: float = 0.005          # annual base emigration probability per agent
    base_immigration_rate: float = 0.008         # annual base immigration probability (band level)
    emigration_resource_threshold: float = 3.0   # below this resources → push factor
    emigration_reputation_threshold: float = 0.2 # below this reputation → push factor
    emigration_unmated_years: int = 5            # years unmated before mating-push emigration
    emigration_family_anchor: float = 0.3        # multiplier reducing emigration if bonded+children
    immigration_resource_threshold: float = 8.0  # above this resources → pull factor
    immigrant_trait_source: str = "population_mean"  # "population_mean", "external", "random"
    external_trait_aggression_offset: float = 0.0   # trait offset for "external" immigrants
    immigrant_initial_trust: float = 0.4        # starting trust level toward all band members
    overcrowding_emigration_threshold: float = 0.9  # fraction of carrying capacity triggering push

    # DD20: Leadership
    leadership_enabled: bool = True
    war_leader_aggression_boost: float = 0.2     # faction member aggression boost when active
    war_leader_combat_bonus: float = 0.05        # combat power boost alongside leader
    war_leader_deterrence: float = 0.2           # reduction in being targeted by rivals
    peace_chief_arbitration_probability: float = 0.4  # chance to intervene in intra-faction conflict
    peace_chief_sharing_boost: float = 0.1       # cooperation sharing rate boost
    leadership_minimum_threshold: float = 1.2    # must exceed avg * this to be recognized
    war_leader_tenure_years: int = 5             # years before must re-demonstrate
    peace_chief_tenure_years: int = 5            # years before must re-demonstrate
    leadership_age_limit: int = 55              # age above which health-declining leaders step down

    # DD21: Resource type differentiation
    resource_types_enabled: bool = True
    subsistence_decay_rate: float = 0.4          # higher decay than tools
    tools_decay_rate: float = 0.1                # very durable
    prestige_goods_decay_rate: float = 0.05      # nearly permanent
    tool_production_multiplier: float = 0.3      # tools boost subsistence production
    tools_per_agent_cap: float = 10.0            # max tools any agent can hold
    prestige_goods_per_agent_cap: float = 5.0    # max prestige goods
    intraband_trade_probability: float = 0.1     # annual trade attempt probability
    tool_subsistence_exchange_rate: float = 3.0  # 1 tool = 3 subsistence
    prestige_goods_mate_signal: float = 0.05     # prestige goods → attractiveness boost
    tool_conflict_loot_chance: float = 0.2       # chance winner takes a tool

    # DD22: Life stage social roles
    life_stages_enabled: bool = True
    youth_conflict_multiplier: float = 1.25      # elevated conflict initiation for youth
    youth_risk_multiplier: float = 1.4           # amplified risk tolerance expression
    youth_trust_building_multiplier: float = 1.5 # faster trust with same-cohort peers
    prime_parenting_multiplier: float = 1.2      # peak parenting investment expression
    mature_conflict_dampening: float = 0.8       # reduced conflict initiation for mature adults
    mature_ledger_cap: int = 150                 # expanded social memory for mature+
    elder_norm_anchor_strength: float = 0.3      # elder effect on institutional inertia
    elder_conflict_damping: float = 0.15         # elder presence reduces out-group conflict
    cohort_range_years: int = 3                  # age range defining a cohort

    # DD24: Epigenetics and social pathology spread
    epigenetics_enabled: bool = True
    epigenetic_sigma_boost: float = 0.3          # max mutation rate increase from stress load
    epigenetic_scarcity_load: float = 0.3        # load added from scarcity event
    epigenetic_epidemic_load: float = 0.2        # load added from epidemic survival
    epigenetic_trauma_load: float = 0.25         # load added from trauma threshold crossing
    epigenetic_inheritance_fraction: float = 0.5 # fraction of load passed to offspring
    trauma_contagion_enabled: bool = True
    trauma_contagion_rate: float = 0.1           # base annual spread probability
    trauma_spread_amount: float = 0.02           # trauma points transferred per event
    trauma_epidemic_threshold: float = 0.3       # fraction of band in crisis to trigger epidemic
    faction_trauma_buffer: float = 0.02          # annual trauma decay boost in strong factions

    # DD26: Skill acquisition and cultural knowledge
    skills_enabled: bool = True
    skill_learning_rate_base: float = 0.01          # base annual skill gain rate
    skill_foraging_decay: float = 0.02              # annual foraging skill decay
    skill_combat_decay: float = 0.03                # annual combat skill decay
    skill_social_decay: float = 0.01                # annual social skill decay
    skill_craft_decay: float = 0.02                 # annual craft skill decay
    skill_parent_transmission: float = 0.30         # fraction of parent skill to child at maturation
    skill_mentor_transfer_rate: float = 0.05        # annual transfer from mentor to apprentice
    skill_age_learning_decline_start: int = 45      # age at which learning slows
    combat_skill_weight: float = 0.15               # combat skill contribution to power
    skill_learning_intelligence_multiplier: float = 0.6  # how much intel boosts learning

    # DD25: Belief and ideology system
    beliefs_enabled: bool = True
    belief_social_influence_rate: float = 0.05   # strength of conformity pressure per tick
    belief_experience_update_rate: float = 0.03  # belief change from direct experience
    belief_mutation_rate: float = 0.03           # novelty_seeking-scaled random drift
    belief_ideological_tension_threshold: float = 0.6  # abs diff triggering tension
    belief_revolution_threshold: float = 0.3     # shift magnitude triggering revolution event
    belief_institutional_influence: float = 0.3  # weight of belief aggregate in inst drift
    prestige_transmission_weight: float = 0.6    # how much more prestigious agents influence beliefs

    # ── Environment ─────────────────────────────────────────────
    scarcity_event_probability: float = 0.03  # base annual chance of scarcity shock

    # ── Population safety ────────────────────────────────────────────
    min_viable_population: int = 20  # inject migrants if below this

    # ── Equilibrium detection ────────────────────────────────────────
    equilibrium_window: int = 10  # years of stable metrics to flag equilibrium
    equilibrium_threshold: float = 0.01  # max relative change to count as stable

    def __post_init__(self):
        # Wire mating_system string to enforcement flags
        if self.mating_system == "monogamy" and not self.monogamy_enforced:
            self.monogamy_enforced = True

    def save(self, path: Path):
        with open(path, "w") as f:
            yaml.dump(asdict(self), f, default_flow_style=False, sort_keys=False)

    @classmethod
    def load(cls, path: Path) -> "Config":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
