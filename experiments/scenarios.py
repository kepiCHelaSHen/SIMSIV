"""
Scenario definitions — named config overrides for comparative experiments.

Each scenario is a dict of kwargs passed to Config().
FREE_COMPETITION is the null hypothesis; all others are compared against it.

NOTE ON INSTITUTIONAL DRIFT:
  Institutional drift is ENABLED by default (drift_rate=0.01, Phase F fix).
  This means FREE_COMPETITION accumulates law_strength ~0.48 by year 200.
  It is therefore "weak endogenous governance" not "zero governance."
  For testing the gene-culture coevolution substitution claim, use
  NO_INSTITUTIONS as the true null and STRONG_STATE as the treatment.
  FREE_COMPETITION remains the ecological/mating baseline.

NOTE ON INTER-GROUP COMPETITION:
  SIMSIV v1.0 is a single-band model. True between-group selection
  (Bowles & Gintis 2011, Choi & Bowles 2007, Henrich et al.) requires the
  clan simulator (v2). No proxy scenario is included because a within-band
  approximation would not be mechanistically equivalent to group selection
  and would invite reviewer critique. This limitation is acknowledged
  explicitly in docs/validation.md as Limitation L1, with v2 as the remedy.
  All findings from v1 scenarios reflect within-group dynamics only.
"""

SCENARIOS: dict[str, dict] = {

    "FREE_COMPETITION": {
        # Baseline — default calibrated config, no overrides.
        # NOTE: institutional drift is ON by default. This scenario develops
        # ~0.48 law_strength by year 200. It is therefore weak-endogenous-
        # governance, not zero-governance. Use NO_INSTITUTIONS for the true
        # zero-governance control in substitution claim testing.
    },

    "NO_INSTITUTIONS": {
        # True zero-governance control — drift disabled, law locked at zero.
        # Added 2026-03-15 following GPT review: FREE_COMPETITION is not a
        # clean null because institutional drift produces ~0.48 law_strength
        # by year 200. This scenario provides the genuine no-governance
        # baseline for the three-way substitution test:
        #   NO_INSTITUTIONS vs FREE_COMPETITION vs STRONG_STATE
        "law_strength": 0.0,
        "violence_punishment_strength": 0.0,
        "property_rights_strength": 0.0,
        "institutional_drift_rate": 0.0,
        "emergent_institutions_enabled": False,
        "institutional_inertia": 0.0,
    },

    "ENFORCED_MONOGAMY": {
        "mating_system": "monogamy",
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

    "STRONG_STATE": {
        # High fixed governance — starts strong, no drift needed.
        "law_strength": 0.8,
        "violence_punishment_strength": 0.7,
        "property_rights_strength": 0.5,
        "tax_rate": 0.15,
        "mating_system": "monogamy",
        "max_mates_per_male": 1,
        "inheritance_prestige_fraction": 0.1,
    },

    "EMERGENT_INSTITUTIONS": {
        # Zero start, high drift — institutions must self-organize from
        # the cooperation/violence balance in the population alone.
        "law_strength": 0.0,
        "violence_punishment_strength": 0.0,
        "property_rights_strength": 0.0,
        "institutional_drift_rate": 0.02,
        "institutional_inertia": 0.7,
        "emergent_institutions_enabled": True,
    },
}
