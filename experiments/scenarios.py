"""
Scenario definitions — named config overrides for comparative experiments.

Each scenario is a dict of kwargs passed to Config().
FREE_COMPETITION is the null hypothesis; all others are compared against it.
"""

SCENARIOS: dict[str, dict] = {
    "FREE_COMPETITION": {
        # Baseline defaults — no overrides
    },

    "ENFORCED_MONOGAMY": {
        "mating_system": "monogamy",       # triggers monogamy_enforced=True via __post_init__
        "max_mates_per_male": 1,
        "law_strength": 0.7,
        "violence_punishment_strength": 0.5,
    },

    "ELITE_POLYGYNY": {
        "elite_privilege_multiplier": 3.0,
        "max_mates_per_male": 5,
    },

    "HIGH_FEMALE_CHOICE": {
        "female_choice_strength": 0.95,
        "male_competition_intensity": 0.9,
    },

    "RESOURCE_ABUNDANCE": {
        "resource_abundance": 2.5,
        "resource_volatility": 0.1,
    },

    "RESOURCE_SCARCITY": {
        "resource_abundance": 0.6,
        "resource_volatility": 0.3,
        "scarcity_event_probability": 0.10,
        "scarcity_severity": 0.55,
        "subsistence_floor": 2.5,
    },

    "HIGH_VIOLENCE_COST": {
        "violence_cost_health": 0.45,
        "violence_death_chance": 0.15,
        "mortality_base": 0.04,
    },

    "STRONG_PAIR_BONDING": {
        "pair_bond_strength": 0.9,
        "pair_bond_dissolution_rate": 0.02,
        "child_dependency_years": 10,
    },

    # DD05: Institutional scenarios
    "STRONG_STATE": {
        "law_strength": 0.8,
        "violence_punishment_strength": 0.7,
        "property_rights_strength": 0.5,
        "tax_rate": 0.15,
        "mating_system": "monogamy",
        "max_mates_per_male": 1,
        "inheritance_prestige_fraction": 0.1,
    },

    "EMERGENT_INSTITUTIONS": {
        # Everything starts at zero — institutions must self-organize
        "law_strength": 0.0,
        "violence_punishment_strength": 0.0,
        "property_rights_strength": 0.0,
        "institutional_drift_rate": 0.02,
        "institutional_inertia": 0.7,
        "emergent_institutions_enabled": True,
    },
}
