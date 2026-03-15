"""
SIMSIV Dashboard — Full Streamlit visualization of the simulation.

Run: python -m streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
from collections import defaultdict

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
# Helpers
# ════════════════════════════════════════════════════════════════════

def _hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    h = color_hex.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def add_band(fig, x, mean_series, std_series, color_hex, secondary_y=None):
    """Add a ±1σ shaded confidence band to a figure."""
    if std_series is None:
        return
    upper = mean_series + std_series
    lower = np.maximum(mean_series - std_series, 0)
    r, g, b = _hex_to_rgb(color_hex)
    band = go.Scatter(
        x=list(x) + list(x[::-1]),
        y=list(upper) + list(lower[::-1]),
        fill="toself",
        fillcolor=f"rgba({r},{g},{b},0.15)",
        line=dict(color="rgba(0,0,0,0)"),
        showlegend=False,
        hoverinfo="skip",
    )
    if secondary_y is not None:
        fig.add_trace(band, secondary_y=secondary_y)
    else:
        fig.add_trace(band)


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

# ── Research Mode ────────────────────────────────────────────────

st.sidebar.markdown("---")
st.sidebar.markdown("### Research Mode")
research_mode = st.sidebar.checkbox("Enable Research Mode (multi-seed)", value=False)
seeds_count = 3
if research_mode:
    seeds_count = st.sidebar.slider("Number of seeds", 3, 20, 5)
    st.sidebar.caption(f"Will run {seeds_count} simulations with seeds {int(seed)}..{int(seed) + seeds_count - 1}")

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


def _build_config(seed_val: int) -> Config:
    """Build a Config from sidebar values with a specific seed."""
    return Config(
        population_size=population_size,
        years=years,
        seed=seed_val,
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


def _run_one(seed_val: int) -> tuple[pd.DataFrame, "Simulation"]:
    """Run a single simulation and return (metrics_df, sim)."""
    config = _build_config(seed_val)
    reset_id_counter()
    sim = Simulation(config)
    rows = []
    for _ in range(years):
        rows.append(sim.tick())
    return pd.DataFrame(rows), sim


if run_clicked:
    if research_mode:
        # ── Multi-run mode ───────────────────────────────────────
        all_dfs = []
        progress = st.progress(0, text="Research Mode: initializing...")
        last_sim = None

        for i in range(seeds_count):
            seed_val = int(seed) + i
            progress.progress(
                (i) / seeds_count,
                text=f"Research Mode: running seed {seed_val} ({i+1}/{seeds_count})...")
            df_i, sim_i = _run_one(seed_val)
            df_i["seed"] = seed_val
            all_dfs.append(df_i)
            last_sim = sim_i

        progress.progress(1.0, text="Aggregating results...")

        combined = pd.concat(all_dfs, ignore_index=True)
        numeric_cols = combined.select_dtypes(include="number").columns.tolist()
        if "seed" in numeric_cols:
            numeric_cols.remove("seed")

        df_mean = combined.groupby("year")[numeric_cols].mean().reset_index()
        df_std = combined.groupby("year")[numeric_cols].std().reset_index()

        progress.empty()

        st.session_state["df"] = df_mean
        st.session_state["df_std"] = df_std
        st.session_state["is_multi_run"] = True
        st.session_state["seeds_count"] = seeds_count
        st.session_state["living"] = last_sim.society.get_living()
        st.session_state["society"] = last_sim.society
        st.session_state["config"] = last_sim.config
        st.session_state["events"] = last_sim.society.events

    else:
        # ── Single run mode ──────────────────────────────────────
        config = _build_config(int(seed))
        reset_id_counter()
        sim = Simulation(config)

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

        st.session_state["df"] = df
        st.session_state["df_std"] = None
        st.session_state["is_multi_run"] = False
        st.session_state["seeds_count"] = 1
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
df_std = st.session_state.get("df_std")
is_multi_run = st.session_state.get("is_multi_run", False)
living = st.session_state["living"]
society = st.session_state["society"]
config = st.session_state["config"]
events = st.session_state["events"]

# ── Summary KPIs ─────────────────────────────────────────────────

st.markdown("---")
if is_multi_run:
    st.caption(f"Research Mode: {st.session_state['seeds_count']} seeds averaged. "
               f"Shaded bands show ±1 standard deviation.")

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


def _std_col(col_name):
    """Get std series for a column, or None if not multi-run."""
    if is_multi_run and df_std is not None and col_name in df_std.columns:
        return df_std[col_name]
    return None


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
        add_band(fig, df["year"], df["population"], _std_col("population"), "#2196F3", secondary_y=False)
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
        add_band(fig, df["year"], df["males"], _std_col("males"), "#42A5F5")
        fig.add_trace(go.Scatter(x=df["year"], y=df["females"], name="Females",
                                 line=dict(color="#EF5350")))
        add_band(fig, df["year"], df["females"], _std_col("females"), "#EF5350")
        if "children_count" in df.columns:
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
        max_age = max(max(ages_m, default=0), max(ages_f, default=0))
        bins = list(range(0, max_age + 10, 5))

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
        add_band(fig, df["year"], df["pop_growth_rate"], _std_col("pop_growth_rate"), "#FF9800")
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
        add_band(fig, df["year"], df["avg_health"], _std_col("avg_health"), "#66BB6A")
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
        add_band(fig, df["year"], df["resource_gini"], _std_col("resource_gini"), "#FF7043", secondary_y=False)
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
        add_band(fig, df["year"], df["avg_resources"], _std_col("avg_resources"), "#4CAF50")
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
        add_band(fig, df["year"], df["cooperation_network_size"], _std_col("cooperation_network_size"), "#26C6DA")
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
        add_band(fig, df["year"], df["violence_rate"], _std_col("violence_rate"), "#E53935", secondary_y=False)
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
        add_band(fig, df["year"], df["violence_deaths"], _std_col("violence_deaths"), "#D32F2F")
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
        add_band(fig, df["year"], df["pair_bonded_pct"], _std_col("pair_bonded_pct"), "#E91E63")
        fig.add_trace(go.Scatter(x=df["year"], y=df["unmated_male_pct"],
                                 name="Unmated Males %", line=dict(color="#42A5F5", dash="dash")))
        add_band(fig, df["year"], df["unmated_male_pct"], _std_col("unmated_male_pct"), "#42A5F5")
        fig.add_trace(go.Scatter(x=df["year"], y=df["unmated_female_pct"],
                                 name="Unmated Females %", line=dict(color="#EF5350", dash="dot")))
        fig.update_layout(title="Mating Market", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["reproductive_skew"],
                                 name="Reproductive Skew", line=dict(color="#9C27B0")))
        add_band(fig, df["year"], df["reproductive_skew"], _std_col("reproductive_skew"), "#9C27B0")
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
        add_band(fig, df["year"], df["child_survival_rate"], _std_col("child_survival_rate"), "#66BB6A")
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

# ── TAB: Trait Evolution (with variance bands) ───────────────────

with tab_traits:
    st.subheader("Heritable Trait Means Over Time")
    if is_multi_run:
        st.caption("Shaded bands show ±1 standard deviation across seeds.")

    # Map trait column -> std column -> color
    trait_band_config = {
        "avg_aggression": ("trait_std_aggression", "#E53935"),
        "avg_cooperation": ("trait_std_cooperation", "#43A047"),
        "avg_intelligence": ("trait_std_intelligence", "#2196F3"),
        "avg_risk_tolerance": ("trait_std_risk_tolerance", "#FFC107"),
    }

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

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        for col_name, color in list(trait_colors.items())[:4]:
            if col_name in df.columns:
                label = col_name.replace("avg_", "").replace("_", " ").title()
                fig.add_trace(go.Scatter(x=df["year"], y=df[col_name], name=label,
                                         line=dict(color=color)))
                # Variance bands from trait std columns (single or multi-run)
                if col_name in trait_band_config:
                    std_col, band_color = trait_band_config[col_name]
                    if std_col in df.columns:
                        add_band(fig, df["year"], df[col_name], df[std_col], band_color)
                    elif is_multi_run:
                        add_band(fig, df["year"], df[col_name], _std_col(col_name), band_color)
        fig.update_layout(title="Traits (Group 1) with ±1σ Bands", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        for col_name, color in list(trait_colors.items())[4:]:
            if col_name in df.columns:
                label = col_name.replace("avg_", "").replace("_", " ").title()
                fig.add_trace(go.Scatter(x=df["year"], y=df[col_name], name=label,
                                         line=dict(color=color)))
                # Variance bands for the subset that has std cols
                if col_name in trait_band_config:
                    std_col, band_color = trait_band_config[col_name]
                    if std_col in df.columns:
                        add_band(fig, df["year"], df[col_name], df[std_col], band_color)
                    elif is_multi_run:
                        add_band(fig, df["year"], df[col_name], _std_col(col_name), band_color)
        fig.update_layout(title="Traits (Group 2) with ±1σ Bands", height=400, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

    # Trait diversity
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        for std_name, color in [("trait_std_aggression", "#E53935"),
                                ("trait_std_cooperation", "#43A047"),
                                ("trait_std_intelligence", "#2196F3"),
                                ("trait_std_risk_tolerance", "#FFC107")]:
            if std_name in df.columns:
                label = std_name.replace("trait_std_", "").replace("_", " ").title() + " Std"
                fig.add_trace(go.Scatter(x=df["year"], y=df[std_name], name=label,
                                         line=dict(color=color)))
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
        add_band(fig, df["year"], df["law_strength"], _std_col("law_strength"), "#1E88E5")
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
    add_band(fig, df["year"], df["civilization_stability"], _std_col("civilization_stability"), "#1E88E5")
    fig.add_trace(go.Scatter(x=df["year"], y=df["social_cohesion"],
                             name="Social Cohesion Index", line=dict(color="#43A047", width=2)))
    add_band(fig, df["year"], df["social_cohesion"], _std_col("social_cohesion"), "#43A047")
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
                "Prestige": round(a.prestige_score, 3),
                "Dominance": round(a.dominance_score, 3),
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
                "Faction": a.faction_id if a.faction_id is not None else "-",
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

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Prestige", f"{agent.prestige_score:.3f}")
            c2.metric("Dominance", f"{agent.dominance_score:.3f}")
            c3.metric("Faction", agent.faction_id if agent.faction_id is not None else "None")
            c4.metric("Life Stage", agent.life_stage)

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

# ── TAB: Social Network (enhanced with prestige/faction/trust) ───

with tab_network:
    st.subheader("Social Network — Prestige & Factions")
    st.caption("Top agents by prestige score. Node color = faction. "
               "Node size = prestige. Edges = trust > 0.5 within faction.")

    max_nodes = st.slider("Max agents to display", 20, 300, 150, step=10)

    if living:
        # ── Compute prestige scores ──────────────────────────────────
        # prestige_score is already an agent attribute (DD08)
        scored = [(a, a.prestige_score) for a in living]
        scored.sort(key=lambda x: x[1], reverse=True)
        sample = [a for a, _ in scored[:max_nodes]]
        sample_ids = {a.id for a in sample}

        # ── Faction clustering ───────────────────────────────────────
        # Use existing faction_id from agents. For agents without one,
        # derive mini-factions from trust graph connected components.
        faction_map = {}
        for a in sample:
            faction_map[a.id] = a.faction_id

        # For agents without faction_id, cluster by trust connectivity
        unfactioned = [a for a in sample if a.faction_id is None]
        if unfactioned:
            # Build adjacency from trust > 0.5
            adj = defaultdict(set)
            uf_ids = {a.id for a in unfactioned}
            for a in unfactioned:
                for oid, trust in a.reputation_ledger.items():
                    if trust > 0.5 and oid in uf_ids:
                        adj[a.id].add(oid)
                        adj[oid].add(a.id)

            # BFS connected components
            visited = set()
            next_faction = max((f for f in faction_map.values() if f is not None), default=0) + 100

            for a in unfactioned:
                if a.id in visited:
                    continue
                # BFS
                component = []
                queue = [a.id]
                while queue:
                    nid = queue.pop(0)
                    if nid in visited:
                        continue
                    visited.add(nid)
                    component.append(nid)
                    for neighbor in adj.get(nid, []):
                        if neighbor not in visited:
                            queue.append(neighbor)
                for nid in component:
                    faction_map[nid] = next_faction
                next_faction += 1

        # Assign colors per faction
        unique_factions = sorted(set(f for f in faction_map.values() if f is not None))
        faction_palette = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel
        faction_color = {}
        for i, fid in enumerate(unique_factions):
            faction_color[fid] = faction_palette[i % len(faction_palette)]
        # Fallback for None
        faction_color[None] = "#666666"

        # ── Layout: circular by faction, jittered ────────────────────
        rng_layout = np.random.default_rng(42)
        n = len(sample)

        # Group by faction for layout clustering
        faction_groups = defaultdict(list)
        for i, a in enumerate(sample):
            faction_groups[faction_map.get(a.id)].append(i)

        node_x = np.zeros(n)
        node_y = np.zeros(n)
        angle_offset = 0.0
        for fid, indices in faction_groups.items():
            # Place faction members in a cluster
            center_angle = angle_offset
            cx = 2.0 * np.cos(center_angle)
            cy = 2.0 * np.sin(center_angle)
            for j, idx in enumerate(indices):
                a_angle = j * 2 * np.pi / max(len(indices), 1)
                r = 0.3 + rng_layout.uniform(0, 0.4)
                node_x[idx] = cx + r * np.cos(a_angle)
                node_y[idx] = cy + r * np.sin(a_angle)
            angle_offset += 2 * np.pi / max(len(faction_groups), 1)

        pos = {sample[i].id: (node_x[i], node_y[i]) for i in range(n)}

        # ── Edges: trust > 0.5, within same faction ──────────────────
        edge_x, edge_y = [], []
        edge_widths = []  # for per-edge width (collected for bulk trace)

        for a in sample:
            ax, ay = pos[a.id]
            a_faction = faction_map.get(a.id)
            for oid, trust in a.reputation_ledger.items():
                if trust > 0.5 and oid in sample_ids and oid > a.id:  # avoid duplicates
                    o_faction = faction_map.get(oid)
                    if a_faction == o_faction:  # within faction only
                        ox, oy = pos[oid]
                        edge_x.extend([ax, ox, None])
                        edge_y.extend([ay, oy, None])

        # ── Also show pair bonds (cross-faction OK) ──────────────────
        bond_x, bond_y = [], []
        for a in sample:
            ax, ay = pos[a.id]
            for pid in a.partner_ids:
                if pid in pos and pid > a.id:
                    px_, py_ = pos[pid]
                    bond_x.extend([ax, px_, None])
                    bond_y.extend([ay, py_, None])

        fig = go.Figure()

        # Trust edges (within faction)
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(color="rgba(100,180,255,0.2)", width=0.8),
            hoverinfo="none", showlegend=True, name="Trust Link (in-faction)"))

        # Pair bond edges
        if bond_x:
            fig.add_trace(go.Scatter(
                x=bond_x, y=bond_y, mode="lines",
                line=dict(color="rgba(255,80,120,0.7)", width=2),
                hoverinfo="none", showlegend=True, name="Pair Bond"))

        # Nodes — colored by faction, sized by prestige
        node_colors_list = [faction_color.get(faction_map.get(a.id), "#666") for a in sample]
        node_sizes_list = [max(5, a.prestige_score * 30 + 4) for a in sample]
        node_text = [
            f"ID:{a.id} {a.sex.value[0].upper()} age:{a.age}<br>"
            f"prestige:{a.prestige_score:.2f} dom:{a.dominance_score:.2f}<br>"
            f"faction:{faction_map.get(a.id, '?')} bonds:{a.bond_count}<br>"
            f"coop:{a.cooperation_propensity:.2f} agg:{a.aggression_propensity:.2f}"
            for a in sample
        ]

        fig.add_trace(go.Scatter(
            x=[pos[a.id][0] for a in sample],
            y=[pos[a.id][1] for a in sample],
            mode="markers",
            marker=dict(size=node_sizes_list, color=node_colors_list,
                        line=dict(width=0.5, color="white")),
            text=node_text, hoverinfo="text", showlegend=False,
        ))

        fig.update_layout(
            height=750, template="plotly_dark",
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Bond count distribution + faction distribution
    if living:
        col1, col2 = st.columns(2)
        with col1:
            bond_counts = [a.bond_count for a in living]
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=bond_counts,
                                       nbinsx=max(1, max(bond_counts, default=1) + 1),
                                       marker_color="#E91E63"))
            fig.update_layout(title="Bond Count Distribution", height=300, template="plotly_dark",
                              xaxis_title="Number of Bonds", yaxis_title="Agents",
                              margin=dict(l=40, r=40, t=40, b=40))
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Faction size distribution
            faction_counts = defaultdict(int)
            for a in living:
                fid = a.faction_id if a.faction_id is not None else "None"
                faction_counts[fid] += 1
            sorted_factions = sorted(faction_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[str(f[0]) for f in sorted_factions],
                y=[f[1] for f in sorted_factions],
                marker_color="#7E57C2",
            ))
            fig.update_layout(title="Faction Sizes (Top 20)", height=300, template="plotly_dark",
                              xaxis_title="Faction ID", yaxis_title="Members",
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
