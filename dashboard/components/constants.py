"""Shared constants for SIMSIV dashboard."""

PLOT_TEMPLATE = "plotly_dark"

COLORS = {
    "population": "#2196F3", "births": "#4CAF50", "deaths": "#F44336",
    "males": "#42A5F5", "females": "#EF5350", "children": "#FFA726",
    "violence": "#E53935", "cooperation": "#43A047", "resources": "#FF9800",
    "inequality": "#FF7043", "status": "#AB47BC", "health": "#66BB6A",
    "intelligence": "#4ECDC4", "law": "#1E88E5", "belief": "#FFD54F",
    "faction": "#43A047", "schism": "#FF9800", "scarcity": "#795548",
    "epidemic": "#E53935", "age": "#AB47BC", "mating": "#F72585",
    "bond": "#FF6B6B", "prestige": "#FFD700", "dominance": "#FF4500",
    "neutral": "#888888",
    # Trait domains
    "physical": "#FF6B35", "cognitive": "#4ECDC4", "temporal": "#FFE66D",
    "personality": "#C77DFF", "social": "#06D6A0", "reproductive": "#F72585",
    "psychopathology": "#EF233C",
}

TRAIT_ABBREV = {
    "aggression_propensity": "Aggression", "cooperation_propensity": "Coop",
    "attractiveness_base": "Attract", "status_drive": "Status",
    "risk_tolerance": "Risk", "jealousy_sensitivity": "Jealousy",
    "fertility_base": "Fertility", "intelligence_proxy": "Intel",
    "longevity_genes": "Longevity", "disease_resistance": "Disease Res",
    "physical_robustness": "Robustness", "pain_tolerance": "Pain Tol",
    "mental_health_baseline": "MH Base", "emotional_intelligence": "Emot Intel",
    "impulse_control": "Impulse", "novelty_seeking": "Novelty",
    "empathy_capacity": "Empathy", "conformity_bias": "Conform",
    "dominance_drive": "Dominance", "maternal_investment": "Maternal",
    "sexual_maturation_rate": "Sex Mat", "cardiovascular_risk": "Cardio Risk",
    "mental_illness_risk": "Mental Risk", "autoimmune_risk": "Autoimmune",
    "metabolic_risk": "Metabolic", "degenerative_risk": "Degen Risk",
    "physical_strength": "Strength", "endurance": "Endurance",
    "group_loyalty": "Loyalty", "outgroup_tolerance": "Outgroup",
    "future_orientation": "Future Or", "conscientiousness": "Conscient",
    "psychopathy_tendency": "Psychopathy", "anxiety_baseline": "Anxiety",
    "paternal_investment_preference": "Pat Invest",
}

TRAIT_DOMAINS = {
    "physical":       ["physical_strength", "endurance", "physical_robustness",
                       "pain_tolerance", "longevity_genes", "disease_resistance"],
    "cognitive":      ["intelligence_proxy", "emotional_intelligence",
                       "impulse_control", "conscientiousness"],
    "temporal":       ["future_orientation"],
    "personality":    ["risk_tolerance", "novelty_seeking", "anxiety_baseline",
                       "mental_health_baseline"],
    "social":         ["aggression_propensity", "cooperation_propensity", "dominance_drive",
                       "group_loyalty", "outgroup_tolerance", "empathy_capacity",
                       "conformity_bias", "status_drive", "jealousy_sensitivity"],
    "reproductive":   ["fertility_base", "sexual_maturation_rate", "maternal_investment",
                       "paternal_investment_preference", "attractiveness_base"],
    "psychopathology": ["psychopathy_tendency", "mental_illness_risk", "cardiovascular_risk",
                        "autoimmune_risk", "metabolic_risk", "degenerative_risk"],
}

TRAIT_DOMAIN_COLORS = {}
for domain, traits in TRAIT_DOMAINS.items():
    for t in traits:
        TRAIT_DOMAIN_COLORS[t] = COLORS.get(domain, COLORS["neutral"])

TAB_NAMES = [
    "Population", "Economy", "Violence", "Mating",
    "Trait Evolution", "Institutions", "Beliefs",
    "Agents", "Social Network", "Events",
    "Hall of Fame", "Dynasty Tree", "Genome Map",
    "Trait Race", "Science Report", "Compare",
]
