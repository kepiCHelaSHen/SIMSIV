"""Sidebar configuration panel for SIMSIV dashboard."""

import streamlit as st
from experiments.scenarios import SCENARIOS


def _cfg_val(preset, key, default):
    return preset.get(key, default)


def render_sidebar() -> dict:
    """Render all sidebar widgets. Returns params dict."""
    st.sidebar.title("SIMSIV Control Panel")

    # Scenario presets (always visible)
    st.sidebar.markdown("### Scenario Presets")
    scenario_names = ["(Custom)"] + list(SCENARIOS.keys())
    chosen_scenario = st.sidebar.selectbox("Load preset", scenario_names, index=0)
    preset = SCENARIOS[chosen_scenario] if chosen_scenario != "(Custom)" else {}

    st.sidebar.markdown("---")
    st.sidebar.markdown("### Scale")
    population_size = st.sidebar.slider("Population", 50, 2000, _cfg_val(preset, "population_size", 500), step=50)
    years = st.sidebar.slider("Years", 10, 500, _cfg_val(preset, "years", 100), step=10)
    seed = st.sidebar.number_input("Random Seed", value=_cfg_val(preset, "seed", 42), step=1)

    # Mating
    with st.sidebar.expander("Mating", expanded=False):
        mating_system = st.selectbox("Mating system", ["unrestricted", "monogamy", "elite_polygyny"],
            index=["unrestricted", "monogamy", "elite_polygyny"].index(_cfg_val(preset, "mating_system", "unrestricted")))
        female_choice_strength = st.slider("Female choice strength", 0.0, 1.0, _cfg_val(preset, "female_choice_strength", 0.6), 0.05)
        male_competition_intensity = st.slider("Male competition", 0.0, 1.0, _cfg_val(preset, "male_competition_intensity", 0.7), 0.05)
        pair_bond_strength = st.slider("Pair bond strength", 0.0, 1.0, _cfg_val(preset, "pair_bond_strength", 0.5), 0.05)
        pair_bond_dissolution_rate = st.slider("Bond dissolution rate", 0.0, 0.5, _cfg_val(preset, "pair_bond_dissolution_rate", 0.1), 0.01)
        max_mates_per_male = st.slider("Max mates/male", 1, 20, _cfg_val(preset, "max_mates_per_male", 999 if mating_system == "unrestricted" else 1))
        infidelity_enabled = st.checkbox("Infidelity enabled", _cfg_val(preset, "infidelity_enabled", True))
        infidelity_base_rate = st.slider("Infidelity rate", 0.0, 0.3, _cfg_val(preset, "infidelity_base_rate", 0.05), 0.01)

    # Reproduction
    with st.sidebar.expander("Reproduction", expanded=False):
        base_conception_chance = st.slider("Conception chance", 0.05, 1.0, _cfg_val(preset, "base_conception_chance", 0.5), 0.05)
        mutation_sigma = st.slider("Mutation sigma", 0.0, 0.2, _cfg_val(preset, "mutation_sigma", 0.05), 0.01)
        child_survival_base = st.slider("Child survival base", 0.5, 1.0, _cfg_val(preset, "child_survival_base", 0.85), 0.01)
        birth_interval_years = st.slider("Birth interval (yrs)", 1, 5, _cfg_val(preset, "birth_interval_years", 2))
        max_lifetime_births = st.slider("Max lifetime births", 3, 20, _cfg_val(preset, "max_lifetime_births", 12))

    # Resources
    with st.sidebar.expander("Resources", expanded=False):
        resource_abundance = st.slider("Resource abundance", 0.2, 3.0, _cfg_val(preset, "resource_abundance", 1.0), 0.1)
        carrying_capacity = st.slider("Carrying capacity", 200, 3000, _cfg_val(preset, "carrying_capacity", 800), 50)
        tax_rate = st.slider("Tax rate", 0.0, 0.5, _cfg_val(preset, "tax_rate", 0.0), 0.01)
        elite_privilege_multiplier = st.slider("Elite privilege", 1.0, 5.0, _cfg_val(preset, "elite_privilege_multiplier", 1.0), 0.1)
        scarcity_severity = st.slider("Scarcity severity", 0.2, 1.0, _cfg_val(preset, "scarcity_severity", 0.6), 0.05)

    # Conflict
    with st.sidebar.expander("Conflict", expanded=False):
        conflict_base_probability = st.slider("Conflict base prob", 0.0, 0.2, _cfg_val(preset, "conflict_base_probability", 0.05), 0.01)
        violence_cost_health = st.slider("Violence health cost", 0.0, 0.5, _cfg_val(preset, "violence_cost_health", 0.15), 0.01)
        violence_death_chance = st.slider("Violence death chance", 0.0, 0.3, _cfg_val(preset, "violence_death_chance", 0.05), 0.01)

    # Institutions
    with st.sidebar.expander("Institutions", expanded=False):
        law_strength = st.slider("Law strength", 0.0, 1.0, _cfg_val(preset, "law_strength", 0.0), 0.05)
        violence_punishment_strength = st.slider("Violence punishment", 0.0, 1.0, _cfg_val(preset, "violence_punishment_strength", 0.0), 0.05)
        property_rights_strength = st.slider("Property rights", 0.0, 1.0, _cfg_val(preset, "property_rights_strength", 0.0), 0.05)
        institutional_drift_rate = st.slider("Inst. drift rate", 0.0, 0.1, _cfg_val(preset, "institutional_drift_rate", 0.0), 0.005)
        emergent_institutions_enabled = st.checkbox("Emergent institutions", _cfg_val(preset, "emergent_institutions_enabled", False))

    # Mortality
    with st.sidebar.expander("Mortality", expanded=False):
        age_death_base = st.slider("Mean death age", 40, 90, _cfg_val(preset, "age_death_base", 60))
        mortality_base = st.slider("Background mortality", 0.0, 0.1, _cfg_val(preset, "mortality_base", 0.02), 0.005)

    # Research Mode
    with st.sidebar.expander("Research Mode", expanded=False):
        research_mode = st.checkbox("Enable multi-seed", value=False)
        seeds_count = 3
        if research_mode:
            seeds_count = st.slider("Number of seeds", 3, 20, 5)
            st.caption(f"Seeds {int(seed)}..{int(seed) + seeds_count - 1}")

    st.sidebar.markdown("---")
    run_clicked = st.sidebar.button("Run Simulation", type="primary", use_container_width=True)

    # Export section
    if "df" in st.session_state and st.session_state["df"] is not None:
        st.sidebar.markdown("---")
        st.sidebar.markdown("### Export")
        df_export = st.session_state["df"]
        csv_bytes = df_export.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("Download metrics.csv", csv_bytes,
                                   file_name="simsiv_metrics.csv", mime="text/csv")
        cfg = st.session_state.get("config")
        if cfg:
            import yaml
            from dataclasses import asdict
            yaml_bytes = yaml.dump(asdict(cfg), default_flow_style=False).encode("utf-8")
            st.sidebar.download_button("Download config.yaml", yaml_bytes,
                                       file_name="simsiv_config.yaml", mime="text/yaml")

    # Last run config
    if "config" in st.session_state:
        with st.sidebar.expander("Last Run Config", expanded=False):
            cfg = st.session_state["config"]
            st.caption(f"Mating: {cfg.mating_system}")
            st.caption(f"Pop: {cfg.population_size} | Years: {cfg.years} | Seed: {cfg.seed}")
            st.caption(f"Law: {cfg.law_strength:.2f} | Resource: {cfg.resource_abundance:.2f}")

    return {
        "run_clicked": run_clicked, "research_mode": research_mode, "seeds_count": seeds_count,
        "population_size": population_size, "years": years, "seed": seed,
        "mating_system": mating_system, "female_choice_strength": female_choice_strength,
        "male_competition_intensity": male_competition_intensity,
        "pair_bond_strength": pair_bond_strength,
        "pair_bond_dissolution_rate": pair_bond_dissolution_rate,
        "max_mates_per_male": max_mates_per_male,
        "infidelity_enabled": infidelity_enabled, "infidelity_base_rate": infidelity_base_rate,
        "base_conception_chance": base_conception_chance, "mutation_sigma": mutation_sigma,
        "child_survival_base": child_survival_base, "birth_interval_years": birth_interval_years,
        "max_lifetime_births": max_lifetime_births,
        "resource_abundance": resource_abundance, "carrying_capacity": carrying_capacity,
        "tax_rate": tax_rate, "elite_privilege_multiplier": elite_privilege_multiplier,
        "scarcity_severity": scarcity_severity,
        "conflict_base_probability": conflict_base_probability,
        "violence_cost_health": violence_cost_health,
        "violence_death_chance": violence_death_chance,
        "law_strength": law_strength, "violence_punishment_strength": violence_punishment_strength,
        "property_rights_strength": property_rights_strength,
        "institutional_drift_rate": institutional_drift_rate,
        "emergent_institutions_enabled": emergent_institutions_enabled,
        "age_death_base": age_death_base, "mortality_base": mortality_base,
    }
