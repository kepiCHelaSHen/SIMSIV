"""
SIMSIV Dashboard — Full Streamlit visualization of the simulation.

Run: streamlit run dashboard/app.py
"""

import sys
from pathlib import Path

# Ensure project root is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

from config import Config
from simulation import Simulation
from models.agent import HERITABLE_TRAITS, Sex, reset_id_counter
from experiments.scenarios import SCENARIOS

# ════════════════════════════════════════════════════════════════════
# Page config
# ════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="SIMSIV Dashboard",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ════════════════════════════════════════════════════════════════════
# Sidebar — Configuration
# ════════════════════════════════════════════════════════════════════

st.sidebar.title("SIMSIV Control Panel")

# Scenario presets
st.sidebar.markdown("### Scenario Presets")
scenario_names = ["(Custom)"] + list(SCENARIOS.keys())
chosen_scenario = st.sidebar.selectbox("Load preset", scenario_names, index=0)

# Build config from scenario or custom
if chosen_scenario != "(Custom)":
    preset = SCENARIOS[chosen_scenario]
else:
    preset = {}


def cfg_val(key, default):
    """Get value: preset overrides default."""
    return preset.get(key, default)


st.sidebar.markdown("---")
st.sidebar.markdown("### Scale")
population_size = st.sidebar.slider("Population", 50, 2000, cfg_val("population_size", 500), step=50)
years = st.sidebar.slider("Years", 10, 500, cfg_val("years", 100), step=10)
seed = st.sidebar.number_input("Random Seed", value=cfg_val("seed", 42), step=1)

st.sidebar.markdown("### Mating")
mating_system = st.sidebar.selectbox(
    "Mating system",
    ["unrestricted", "monogamy", "elite_polygyny"],
    index=["unrestricted", "monogamy", "elite_polygyny"].index(cfg_val("mating_system", "unrestricted")),
)
female_choice_strength = st.sidebar.slider("Female choice strength", 0.0, 1.0, cfg_val("female_choice_strength", 0.6), 0.05)
male_competition_intensity = st.sidebar.slider("Male competition intensity", 0.0, 1.0, cfg_val("male_competition_intensity", 0.7), 0.05)
pair_bond_strength = st.sidebar.slider("Pair bond strength", 0.0, 1.0, cfg_val("pair_bond_strength", 0.5), 0.05)
pair_bond_dissolution_rate = st.sidebar.slider("Bond dissolution rate", 0.0, 0.5, cfg_val("pair_bond_dissolution_rate", 0.1), 0.01)
max_mates_per_male = st.sidebar.slider("Max mates/male", 1, 20, cfg_val("max_mates_per_male", 999 if mating_system == "unrestricted" else 1))
infidelity_enabled = st.sidebar.checkbox("Infidelity enabled", cfg_val("infidelity_enabled", True))
infidelity_base_rate = st.sidebar.slider("Infidelity rate", 0.0, 0.3, cfg_val("infidelity_base_rate", 0.05), 0.01)

st.sidebar.markdown("### Reproduction")
base_conception_chance = st.sidebar.slider("Conception chance", 0.05, 1.0, cfg_val("base_conception_chance", 0.5), 0.05)
mutation_sigma = st.sidebar.slider("Mutation sigma", 0.0, 0.2, cfg_val("mutation_sigma", 0.05), 0.01)
child_survival_base = st.sidebar.slider("Child survival base", 0.5, 1.0, cfg_val("child_survival_base", 0.85), 0.01)
birth_interval_years = st.sidebar.slider("Birth interval (yrs)", 1, 5, cfg_val("birth_interval_years", 2))
max_lifetime_births = st.sidebar.slider("Max lifetime births", 3, 20, cfg_val("max_lifetime_births", 12))

st.sidebar.markdown("### Resources")
resource_abundance = st.sidebar.slider("Resource abundance", 0.2, 3.0, cfg_val("resource_abundance", 1.0), 0.1)
carrying_capacity = st.sidebar.slider("Carrying capacity", 200, 3000, cfg_val("carrying_capacity", 800), 50)
tax_rate = st.sidebar.slider("Tax rate", 0.0, 0.5, cfg_val("tax_rate", 0.0), 0.01)
elite_privilege_multiplier = st.sidebar.slider("Elite privilege", 1.0, 5.0, cfg_val("elite_privilege_multiplier", 1.0), 0.1)
scarcity_severity = st.sidebar.slider("Scarcity severity", 0.2, 1.0, cfg_val("scarcity_severity", 0.6), 0.05)

st.sidebar.markdown("### Conflict")
conflict_base_probability = st.sidebar.slider("Conflict base prob", 0.0, 0.2, cfg_val("conflict_base_probability", 0.05), 0.01)
violence_cost_health = st.sidebar.slider("Violence health cost", 0.0, 0.5, cfg_val("violence_cost_health", 0.15), 0.01)
violence_death_chance = st.sidebar.slider("Violence death chance", 0.0, 0.3, cfg_val("violence_death_chance", 0.05), 0.01)

st.sidebar.markdown("### Institutions")
law_strength = st.sidebar.slider("Law strength", 0.0, 1.0, cfg_val("law_strength", 0.0), 0.05)
violence_punishment_strength = st.sidebar.slider("Violence punishment", 0.0, 1.0, cfg_val("violence_punishment_strength", 0.0), 0.05)
property_rights_strength = st.sidebar.slider("Property rights", 0.0, 1.0, cfg_val("property_rights_strength", 0.0), 0.05)
institutional_drift_rate = st.sidebar.slider("Institutional drift rate", 0.0, 0.1, cfg_val("institutional_drift_rate", 0.0), 0.005)
emergent_institutions_enabled = st.sidebar.checkbox("Emergent institutions", cfg_val("emergent_institutions_enabled", False))

st.sidebar.markdown("### Mortality")
age_death_base = st.sidebar.slider("Mean death age", 40, 90, cfg_val("age_death_base", 60))
mortality_base = st.sidebar.slider("Background mortality", 0.0, 0.1, cfg_val("mortality_base", 0.02), 0.005)

st.sidebar.markdown("---")

# ════════════════════════════════════════════════════════════════════
# Run button
# ════════════════════════════════════════════════════════════════════

run_clicked = st.sidebar.button("▶ Run Simulation", type="primary", use_container_width=True)

# ════════════════════════════════════════════════════════════════════
# Main area
# ════════════════════════════════════════════════════════════════════

st.title("SIMSIV — Social Simulation Dashboard")
st.caption("Simulation of Intersecting Social and Institutional Variables")

if run_clicked:
    # Build config from sidebar
    config = Config(
        population_size=population_size,
        years=years,
        seed=int(seed),
        mating_system=mating_system,
        female_choice_strength=female_choice_strength,
        male_competition_intensity=male_competition_intensity,
        pair_bond_strength=pair_bond_strength,
        pair_bond_dissolution_rate=pair_bond_dissolution_rate,
        max_mates_per_male=max_mates_per_male,
        infidelity_enabled=infidelity_enabled,
        infidelity_base_rate=infidelity_base_rate,
        base_conception_chance=base_conception_chance,
        mutation_sigma=mutation_sigma,
        child_survival_base=child_survival_base,
        birth_interval_years=birth_interval_years,
        max_lifetime_births=max_lifetime_births,
        resource_abundance=resource_abundance,
        carrying_capacity=carrying_capacity,
        tax_rate=tax_rate,
        elite_privilege_multiplier=elite_privilege_multiplier,
        scarcity_severity=scarcity_severity,
        conflict_base_probability=conflict_base_probability,
        violence_cost_health=violence_cost_health,
        violence_death_chance=violence_death_chance,
        law_strength=law_strength,
        violence_punishment_strength=violence_punishment_strength,
        property_rights_strength=property_rights_strength,
        institutional_drift_rate=institutional_drift_rate,
        emergent_institutions_enabled=emergent_institutions_enabled,
        age_death_base=age_death_base,
        mortality_base=mortality_base,
    )

    reset_id_counter()
    sim = Simulation(config)

    # Run with progress bar
    progress = st.progress(0, text="Initializing...")
    metrics_rows = []

    for yr in range(1, years + 1):
        row = sim.tick()
        metrics_rows.append(row)
        if yr % max(1, years // 100) == 0 or yr == years:
            pct = yr / years
            progress.progress(pct, text=f"Year {yr}/{years} — Pop: {row.get('population', 0)}")

    progress.empty()

    df = pd.DataFrame(metrics_rows)
    living = sim.society.get_living()

    # Store in session state
    st.session_state["df"] = df
    st.session_state["living"] = living
    st.session_state["society"] = sim.society
    st.session_state["config"] = config
    st.session_state["events"] = sim.society.events

# ════════════════════════════════════════════════════════════════════
# Display results (from session state)
# ════════════════════════════════════════════════════════════════════

if "df" not in st.session_state:
    st.info("Configure parameters in the sidebar and click **Run Simulation** to begin.")
    st.stop()

df = st.session_state["df"]
living = st.session_state["living"]
society = st.session_state["society"]
config = st.session_state["config"]
events = st.session_state["events"]

# ── Summary KPIs ─────────────────────────────────────────────────

st.markdown("---")
final = df.iloc[-1]

c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
c1.metric("Final Pop", f"{int(final['population']):,}")
c2.metric("Total Births", f"{int(df['births'].sum()):,}")
c3.metric("Total Deaths", f"{int(df['deaths'].sum()):,}")
c4.metric("Gini", f"{final['resource_gini']:.3f}")
c5.metric("Violence", f"{final['violence_rate']:.3f}")
c6.metric("Bonded %", f"{final['pair_bonded_pct']:.1%}")
c7.metric("CSI", f"{final['civilization_stability']:.3f}")
c8.metric("SCI", f"{final['social_cohesion']:.3f}")

# ════════════════════════════════════════════════════════════════════
# Tabs
# ════════════════════════════════════════════════════════════════════

tab_pop, tab_econ, tab_violence, tab_mating, tab_traits, tab_inst, tab_agents, tab_network, tab_events = st.tabs([
    "Population", "Economy", "Violence", "Mating", "Trait Evolution",
    "Institutions", "Agents", "Social Network", "Events",
])

# ── TAB: Population ──────────────────────────────────────────────

with tab_pop:
    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df["year"], y=df["population"], name="Population",
                                 fill="tozeroy", line=dict(color="#2196F3")), secondary_y=False)
        fig.add_trace(go.Scatter(x=df["year"], y=df["births"], name="Births",
                                 line=dict(color="#4CAF50", dash="dot")), secondary_y=True)
        fig.add_trace(go.Scatter(x=df["year"], y=df["deaths"], name="Deaths",
                                 line=dict(color="#F44336", dash="dot")), secondary_y=True)
        fig.update_layout(title="Population Over Time", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        fig.update_yaxes(title_text="Population", secondary_y=False)
        fig.update_yaxes(title_text="Births / Deaths per Year", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["males"], name="Males",
                                 line=dict(color="#42A5F5")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["females"], name="Females",
                                 line=dict(color="#EF5350")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["children_count"], name="Children (<15)",
                                 line=dict(color="#FFA726", dash="dash")))
        fig.update_layout(title="Demographics", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Age pyramid
    st.subheader("Age & Sex Distribution (Final Year)")
    if living:
        ages_m = [a.age for a in living if a.sex == Sex.MALE]
        ages_f = [a.age for a in living if a.sex == Sex.FEMALE]
        bins = list(range(0, max(max(ages_m, default=0), max(ages_f, default=0)) + 10, 5))

        hist_m = np.histogram(ages_m, bins=bins)[0]
        hist_f = np.histogram(ages_f, bins=bins)[0]
        labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins)-1)]

        fig = go.Figure()
        fig.add_trace(go.Bar(y=labels, x=-hist_m, orientation="h", name="Males",
                             marker_color="#42A5F5", text=hist_m, textposition="auto"))
        fig.add_trace(go.Bar(y=labels, x=hist_f, orientation="h", name="Females",
                             marker_color="#EF5350", text=hist_f, textposition="auto"))
        fig.update_layout(title="Age Pyramid", barmode="overlay", height=450,
                          template="plotly_dark", margin=dict(l=40, r=40, t=40, b=40),
                          xaxis=dict(title="Count", tickvals=[]),
                          yaxis=dict(title="Age Group"))
        st.plotly_chart(fig, use_container_width=True)

    # Growth rate
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["pop_growth_rate"],
                                 line=dict(color="#FF9800"), fill="tozeroy"))
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        fig.update_layout(title="Population Growth Rate", height=300, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["avg_age"], name="Avg Age",
                                 line=dict(color="#AB47BC")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["avg_health"], name="Avg Health",
                                 line=dict(color="#66BB6A")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["avg_lifespan"], name="Avg Lifespan (at death)",
                                 line=dict(color="#FFEE58", dash="dot")))
        fig.update_layout(title="Health & Age", height=300, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

# ── TAB: Economy ─────────────────────────────────────────────────

with tab_econ:
    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df["year"], y=df["resource_gini"], name="Resource Gini",
                                 line=dict(color="#FF7043")), secondary_y=False)
        fig.add_trace(go.Scatter(x=df["year"], y=df["status_gini"], name="Status Gini",
                                 line=dict(color="#AB47BC", dash="dash")), secondary_y=False)
        fig.add_trace(go.Scatter(x=df["year"], y=df["resource_top10_share"],
                                 name="Top 10% Share", line=dict(color="#FFA726", dash="dot")),
                      secondary_y=True)
        fig.update_layout(title="Inequality", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        fig.update_yaxes(title_text="Gini", secondary_y=False)
        fig.update_yaxes(title_text="Top 10% Share", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["avg_resources"], name="Avg Resources",
                                 line=dict(color="#4CAF50")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["avg_status"], name="Avg Status",
                                 line=dict(color="#2196F3")))
        fig.update_layout(title="Average Resources & Status", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["cooperation_network_size"],
                                 name="Avg Network Size", line=dict(color="#26C6DA")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["resource_transfers"],
                                 name="Transfer Events", line=dict(color="#9CCC65", dash="dot")))
        fig.update_layout(title="Cooperation Networks", height=350, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Resource distribution of living agents
        if living:
            resources = [a.current_resources for a in living]
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=resources, nbinsx=50, marker_color="#FF7043"))
            fig.update_layout(title="Resource Distribution (Final Year)", height=350,
                              template="plotly_dark", xaxis_title="Resources",
                              yaxis_title="Agents", margin=dict(l=40, r=40, t=40, b=40))
            st.plotly_chart(fig, use_container_width=True)

    with st.expander("Scarcity Events"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["scarcity"], name="Scarcity Level",
                                 fill="tozeroy", line=dict(color="#E53935")))
        fig.update_layout(title="Environmental Scarcity", height=250, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

# ── TAB: Violence ────────────────────────────────────────────────

with tab_violence:
    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(x=df["year"], y=df["violence_rate"], name="Violence Rate",
                                 line=dict(color="#E53935")), secondary_y=False)
        fig.add_trace(go.Scatter(x=df["year"], y=df["conflicts"], name="Conflicts",
                                 line=dict(color="#FF8A65", dash="dot")), secondary_y=True)
        fig.update_layout(title="Violence Over Time", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        fig.update_yaxes(title_text="Rate", secondary_y=False)
        fig.update_yaxes(title_text="Count", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["violence_deaths"], name="Violence Deaths",
                                 line=dict(color="#D32F2F"), fill="tozeroy"))
        fig.add_trace(go.Scatter(x=df["year"], y=df["flee_events"], name="Flee Events",
                                 line=dict(color="#FFC107", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["punishment_events"], name="Punishments",
                                 line=dict(color="#7E57C2", dash="dot")))
        fig.update_layout(title="Conflict Outcomes", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["agents_in_cooldown"],
                                 name="In Subordination Cooldown",
                                 fill="tozeroy", line=dict(color="#FF6F00")))
        fig.update_layout(title="Subordination (Recent Losers)", height=300, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Aggression vs resources scatter for living
        if living:
            scatter_data = pd.DataFrame({
                "Aggression": [a.aggression_propensity for a in living],
                "Resources": [a.current_resources for a in living],
                "Status": [a.current_status for a in living],
                "Sex": [a.sex.value for a in living],
            })
            fig = px.scatter(scatter_data, x="Aggression", y="Resources", color="Sex",
                             size="Status", opacity=0.6,
                             color_discrete_map={"male": "#42A5F5", "female": "#EF5350"},
                             title="Aggression vs Resources (Living Agents)")
            fig.update_layout(height=300, template="plotly_dark",
                              margin=dict(l=40, r=40, t=40, b=40))
            st.plotly_chart(fig, use_container_width=True)

# ── TAB: Mating ──────────────────────────────────────────────────

with tab_mating:
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["pair_bonded_pct"],
                                 name="Pair Bonded %", line=dict(color="#E91E63")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["unmated_male_pct"],
                                 name="Unmated Males %", line=dict(color="#42A5F5", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["unmated_female_pct"],
                                 name="Unmated Females %", line=dict(color="#EF5350", dash="dot")))
        fig.update_layout(title="Mating Market", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["reproductive_skew"],
                                 name="Reproductive Skew", line=dict(color="#9C27B0")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["mating_inequality"],
                                 name="Mating Inequality (Male)", line=dict(color="#FF5722", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["elite_repro_advantage"],
                                 name="Elite Repro Advantage", line=dict(color="#FFEB3B", dash="dot"),
                                 yaxis="y2"))
        fig.update_layout(
            title="Reproductive Inequality", height=400, template="plotly_dark",
            margin=dict(l=40, r=40, t=40, b=40),
            yaxis2=dict(title="Elite Advantage", overlaying="y", side="right"),
        )
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["bonds_formed"], name="Bonds Formed",
                                 line=dict(color="#4CAF50")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["bonds_dissolved"], name="Bonds Dissolved",
                                 line=dict(color="#F44336", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["mating_contests"], name="Mating Contests",
                                 line=dict(color="#FFC107", dash="dot")))
        fig.update_layout(title="Bond Dynamics", height=350, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["avg_bond_strength"],
                                 name="Avg Bond Strength", line=dict(color="#E91E63")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["infidelity_rate"],
                                 name="Infidelity Rate", line=dict(color="#FF9800", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["paternity_uncertainty"],
                                 name="Paternity Uncertainty", line=dict(color="#9575CD", dash="dot")))
        fig.update_layout(title="Fidelity & Bonds", height=350, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Child survival and household
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["child_survival_rate"],
                                 name="Child Survival Rate", line=dict(color="#66BB6A")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["avg_maternal_health"],
                                 name="Maternal Health", line=dict(color="#EF5350", dash="dash")))
        fig.update_layout(title="Child Survival & Maternal Health", height=300, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["childhood_deaths"],
                                 name="Childhood Deaths", line=dict(color="#D32F2F")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["orphan_deaths"],
                                 name="Orphan Deaths", line=dict(color="#FF8A65", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["orphan_count"],
                                 name="Orphans", line=dict(color="#FFCA28", dash="dot")))
        fig.update_layout(title="Childhood Mortality & Orphans", height=300, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

# ── TAB: Trait Evolution ─────────────────────────────────────────

with tab_traits:
    st.subheader("Heritable Trait Means Over Time")
    col1, col2 = st.columns(2)

    trait_colors = {
        "avg_aggression": "#E53935",
        "avg_cooperation": "#43A047",
        "avg_attractiveness": "#E91E63",
        "avg_status_drive": "#FF9800",
        "avg_risk_tolerance": "#FFC107",
        "avg_jealousy": "#9C27B0",
        "avg_fertility": "#00BCD4",
        "avg_intelligence": "#2196F3",
    }

    with col1:
        fig = go.Figure()
        for col_name, color in list(trait_colors.items())[:4]:
            if col_name in df.columns:
                label = col_name.replace("avg_", "").replace("_", " ").title()
                fig.add_trace(go.Scatter(x=df["year"], y=df[col_name], name=label,
                                         line=dict(color=color)))
        fig.update_layout(title="Traits (Group 1)", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        for col_name, color in list(trait_colors.items())[4:]:
            if col_name in df.columns:
                label = col_name.replace("avg_", "").replace("_", " ").title()
                fig.add_trace(go.Scatter(x=df["year"], y=df[col_name], name=label,
                                         line=dict(color=color)))
        fig.update_layout(title="Traits (Group 2)", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Trait diversity
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        if "trait_std_aggression" in df.columns:
            fig.add_trace(go.Scatter(x=df["year"], y=df["trait_std_aggression"],
                                     name="Aggression Std", line=dict(color="#E53935")))
        if "trait_std_cooperation" in df.columns:
            fig.add_trace(go.Scatter(x=df["year"], y=df["trait_std_cooperation"],
                                     name="Cooperation Std", line=dict(color="#43A047")))
        fig.update_layout(title="Trait Diversity (Std Dev)", height=350, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["max_generation"],
                                 name="Max Generation", fill="tozeroy",
                                 line=dict(color="#7E57C2")))
        fig.update_layout(title="Generational Depth", height=350, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Trait distribution scatter (final year)
    st.subheader("Trait Distributions (Final Year)")
    if living:
        trait_data = {
            "Agent ID": [a.id for a in living],
            "Sex": [a.sex.value for a in living],
            "Age": [a.age for a in living],
        }
        for trait in HERITABLE_TRAITS:
            trait_data[trait.replace("_", " ").title()] = [getattr(a, trait) for a in living]

        tdf = pd.DataFrame(trait_data)
        nice_names = [c for c in tdf.columns if c not in ("Agent ID", "Sex", "Age")]

        col1, col2 = st.columns(2)
        with col1:
            t1 = st.selectbox("X axis trait", nice_names, index=0, key="trait_x")
        with col2:
            t2 = st.selectbox("Y axis trait", nice_names, index=1, key="trait_y")

        fig = px.scatter(tdf, x=t1, y=t2, color="Sex", size="Age", opacity=0.5,
                         color_discrete_map={"male": "#42A5F5", "female": "#EF5350"},
                         title=f"{t1} vs {t2}")
        fig.update_layout(height=500, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

# ── TAB: Institutions ────────────────────────────────────────────

with tab_inst:
    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["law_strength"],
                                 name="Law Strength", line=dict(color="#1E88E5")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["violence_punishment"],
                                 name="Violence Punishment", line=dict(color="#D32F2F", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["property_rights"],
                                 name="Property Rights", line=dict(color="#43A047", dash="dot")))
        fig.update_layout(title="Institutional Parameters", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["inheritance_events"],
                                 name="Inheritances", line=dict(color="#FFA726")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["norm_violations"],
                                 name="Norm Violations", line=dict(color="#E53935", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["institutions_emerged"],
                                 name="Emergences", line=dict(color="#7E57C2", dash="dot")))
        fig.update_layout(title="Institutional Events", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Composite indices
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["year"], y=df["civilization_stability"],
                             name="Civilization Stability Index", line=dict(color="#1E88E5", width=2)))
    fig.add_trace(go.Scatter(x=df["year"], y=df["social_cohesion"],
                             name="Social Cohesion Index", line=dict(color="#43A047", width=2)))
    fig.update_layout(title="Composite Stability Indices", height=350, template="plotly_dark",
                      margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig, use_container_width=True)

# ── TAB: Agents ──────────────────────────────────────────────────

with tab_agents:
    st.subheader(f"Living Agents ({len(living)})")

    if living:
        agent_records = []
        for a in living:
            agent_records.append({
                "ID": a.id,
                "Sex": a.sex.value,
                "Age": a.age,
                "Gen": a.generation,
                "Health": round(a.health, 3),
                "Resources": round(a.current_resources, 2),
                "Status": round(a.current_status, 3),
                "Agg": round(a.aggression_propensity, 3),
                "Coop": round(a.cooperation_propensity, 3),
                "Intel": round(a.intelligence_proxy, 3),
                "Attract": round(a.attractiveness_base, 3),
                "Fertility": round(a.fertility_base, 3),
                "Offspring": len(a.offspring_ids),
                "Bonds": a.bond_count,
                "Partners": ", ".join(str(p) for p in a.partner_ids) if a.partner_ids else "-",
                "Mate Value": round(a.mate_value, 3),
                "Reputation": round(a.reputation, 3),
                "Network": sum(1 for t in a.reputation_ledger.values() if t > 0.5),
            })

        agent_df = pd.DataFrame(agent_records)

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            sex_filter = st.multiselect("Sex", ["male", "female"], default=["male", "female"])
        with col2:
            age_range = st.slider("Age range", 0, 100, (0, 100))
        with col3:
            sort_col = st.selectbox("Sort by", agent_df.columns.tolist(), index=5)

        filtered = agent_df[
            agent_df["Sex"].isin(sex_filter) &
            (agent_df["Age"] >= age_range[0]) &
            (agent_df["Age"] <= age_range[1])
        ].sort_values(sort_col, ascending=False)

        st.dataframe(filtered, use_container_width=True, height=500)

        # Agent detail
        st.markdown("---")
        st.subheader("Agent Detail")
        agent_id = st.number_input("Enter Agent ID", value=int(filtered.iloc[0]["ID"]) if len(filtered) > 0 else 1, step=1)
        agent = society.get_by_id(agent_id)
        if agent and agent.alive:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Age", agent.age)
            c2.metric("Health", f"{agent.health:.3f}")
            c3.metric("Resources", f"{agent.current_resources:.2f}")
            c4.metric("Status", f"{agent.current_status:.3f}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Aggression", f"{agent.aggression_propensity:.3f}")
            c2.metric("Cooperation", f"{agent.cooperation_propensity:.3f}")
            c3.metric("Intelligence", f"{agent.intelligence_proxy:.3f}")
            c4.metric("Mate Value", f"{agent.mate_value:.3f}")

            st.write(f"**Sex**: {agent.sex.value} | **Generation**: {agent.generation} | "
                     f"**Offspring**: {len(agent.offspring_ids)} | **Bonds**: {agent.bond_count}")
            if agent.partner_ids:
                st.write(f"**Partners**: {agent.partner_ids}")
            if agent.reputation_ledger:
                top_trust = sorted(agent.reputation_ledger.items(), key=lambda x: x[1], reverse=True)[:10]
                worst_trust = sorted(agent.reputation_ledger.items(), key=lambda x: x[1])[:5]
                st.write(f"**Most trusted**: {top_trust}")
                st.write(f"**Least trusted**: {worst_trust}")
        elif agent:
            st.warning(f"Agent {agent_id} is dead (cause: {agent.cause_of_death}, age {agent.age})")
        else:
            st.warning(f"Agent {agent_id} not found")

# ── TAB: Social Network ─────────────────────────────────────────

with tab_network:
    st.subheader("Social Network Visualization")
    st.caption("Shows pair bonds and top trust relationships among a sample of agents.")

    max_nodes = st.slider("Max agents to display", 20, 200, 80, step=10)

    if living:
        # Sample agents if too many
        sample = living[:max_nodes] if len(living) <= max_nodes else list(
            np.random.default_rng(42).choice(living, size=max_nodes, replace=False))
        sample_ids = {a.id for a in sample}

        # Build node positions using a simple force-directed-ish layout (circular + jitter)
        rng_layout = np.random.default_rng(42)
        n = len(sample)
        angles = np.linspace(0, 2 * np.pi, n, endpoint=False)
        node_x = np.cos(angles) + rng_layout.normal(0, 0.1, n)
        node_y = np.sin(angles) + rng_layout.normal(0, 0.1, n)
        pos = {a.id: (node_x[i], node_y[i]) for i, a in enumerate(sample)}

        # Edges: pair bonds (thick) and trust links (thin)
        bond_x, bond_y = [], []
        trust_x, trust_y = [], []

        for a in sample:
            ax, ay = pos[a.id]
            # Pair bonds
            for pid in a.partner_ids:
                if pid in pos:
                    px_, py_ = pos[pid]
                    bond_x.extend([ax, px_, None])
                    bond_y.extend([ay, py_, None])
            # Trust links (top 3 only to reduce clutter)
            top_trust = sorted(
                ((oid, t) for oid, t in a.reputation_ledger.items() if oid in pos and t > 0.6),
                key=lambda x: x[1], reverse=True)[:3]
            for oid, _ in top_trust:
                ox, oy = pos[oid]
                trust_x.extend([ax, ox, None])
                trust_y.extend([ay, oy, None])

        fig = go.Figure()

        # Trust edges
        fig.add_trace(go.Scatter(x=trust_x, y=trust_y, mode="lines",
                                 line=dict(color="rgba(100,180,255,0.15)", width=0.5),
                                 hoverinfo="none", showlegend=True, name="Trust Link"))

        # Bond edges
        fig.add_trace(go.Scatter(x=bond_x, y=bond_y, mode="lines",
                                 line=dict(color="rgba(255,80,120,0.7)", width=2),
                                 hoverinfo="none", showlegend=True, name="Pair Bond"))

        # Nodes
        node_colors = ["#42A5F5" if a.sex == Sex.MALE else "#EF5350" for a in sample]
        node_sizes = [max(5, a.current_resources * 1.5) for a in sample]
        node_text = [
            f"ID:{a.id} {a.sex.value[0].upper()} age:{a.age}<br>"
            f"res:{a.current_resources:.1f} agg:{a.aggression_propensity:.2f}<br>"
            f"coop:{a.cooperation_propensity:.2f} bonds:{a.bond_count}"
            for a in sample
        ]

        fig.add_trace(go.Scatter(
            x=[pos[a.id][0] for a in sample],
            y=[pos[a.id][1] for a in sample],
            mode="markers",
            marker=dict(size=node_sizes, color=node_colors, line=dict(width=0.5, color="white")),
            text=node_text, hoverinfo="text", showlegend=False,
        ))

        fig.update_layout(
            height=700, template="plotly_dark",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Bond count distribution
    if living:
        bond_counts = [a.bond_count for a in living]
        fig = go.Figure()
        fig.add_trace(go.Histogram(x=bond_counts, nbinsx=max(1, max(bond_counts, default=1) + 1),
                                   marker_color="#E91E63"))
        fig.update_layout(title="Bond Count Distribution", height=300, template="plotly_dark",
                          xaxis_title="Number of Bonds", yaxis_title="Agents",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

# ── TAB: Events ──────────────────────────────────────────────────

with tab_events:
    st.subheader(f"Event Log ({len(events):,} total events)")

    event_types = sorted(set(e.get("type", "?") for e in events))
    selected_types = st.multiselect("Filter by type", event_types, default=event_types[:5] if len(event_types) > 5 else event_types)

    year_range = st.slider("Year range", 1, max(1, len(df)), (max(1, len(df) - 20), len(df)), key="event_year")

    filtered_events = [
        e for e in events
        if e.get("type") in selected_types
        and year_range[0] <= e.get("year", 0) <= year_range[1]
    ]

    st.write(f"Showing {len(filtered_events)} events")

    if filtered_events:
        event_df = pd.DataFrame(filtered_events[:2000])  # cap display
        if "outcome" in event_df.columns:
            event_df["outcome"] = event_df["outcome"].astype(str)
        if "agent_ids" in event_df.columns:
            event_df["agent_ids"] = event_df["agent_ids"].astype(str)
        st.dataframe(event_df, use_container_width=True, height=500)

    # Event type breakdown
    if events:
        type_counts = {}
        for e in events:
            t = e.get("type", "?")
            type_counts[t] = type_counts.get(t, 0) + 1

        fig = go.Figure()
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        fig.add_trace(go.Bar(
            x=[t[0] for t in sorted_types],
            y=[t[1] for t in sorted_types],
            marker_color="#26C6DA",
        ))
        fig.update_layout(title="Events by Type (All Years)", height=350, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40), xaxis_tickangle=-45)
        st.plotly_chart(fig, use_container_width=True)
