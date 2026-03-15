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
from models.agent import HERITABLE_TRAITS, TRAIT_HERITABILITY, Sex, reset_id_counter
from experiments.scenarios import SCENARIOS
from data.names import namer

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
        st.session_state["events"] = last_sim.society._event_window

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
        st.session_state["events"] = sim.society._event_window

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
# Shared constants and helpers (must be before tabs)
# ════════════════════════════════════════════════════════════════════

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

TRAIT_DOMAIN_COLORS = {}
_physical = ["physical_strength", "endurance", "physical_robustness", "pain_tolerance", "longevity_genes", "disease_resistance"]
_cognitive = ["intelligence_proxy", "emotional_intelligence", "impulse_control", "conscientiousness"]
_temporal = ["future_orientation"]
_personality = ["risk_tolerance", "novelty_seeking", "anxiety_baseline", "mental_health_baseline"]
_social = ["aggression_propensity", "cooperation_propensity", "dominance_drive", "group_loyalty",
           "outgroup_tolerance", "empathy_capacity", "conformity_bias", "status_drive", "jealousy_sensitivity"]
_reproductive = ["fertility_base", "sexual_maturation_rate", "maternal_investment",
                 "paternal_investment_preference", "attractiveness_base"]
_psychopath = ["psychopathy_tendency", "mental_illness_risk", "cardiovascular_risk",
               "autoimmune_risk", "metabolic_risk", "degenerative_risk"]
for t in _physical: TRAIT_DOMAIN_COLORS[t] = "#FF6B35"
for t in _cognitive: TRAIT_DOMAIN_COLORS[t] = "#4ECDC4"
for t in _temporal: TRAIT_DOMAIN_COLORS[t] = "#FFE66D"
for t in _personality: TRAIT_DOMAIN_COLORS[t] = "#C77DFF"
for t in _social: TRAIT_DOMAIN_COLORS[t] = "#06D6A0"
for t in _reproductive: TRAIT_DOMAIN_COLORS[t] = "#F72585"
for t in _psychopath: TRAIT_DOMAIN_COLORS[t] = "#EF233C"


def _get_agent_name(agent_id, agent=None):
    """Get full name for an agent, caching in session state."""
    cache = st.session_state.setdefault("agent_names", {})
    if agent_id not in cache:
        sex = "male"
        if agent:
            sex = agent.sex.value if hasattr(agent.sex, "value") else str(agent.sex)
        else:
            a = society.get_by_id(agent_id)
            if a:
                sex = a.sex.value if hasattr(a.sex, "value") else str(a.sex)
        cache[agent_id] = namer.get_full_name(agent_id, sex=sex)
    return cache[agent_id]


# ════════════════════════════════════════════════════════════════════
# Tabs
# ════════════════════════════════════════════════════════════════════

tab_pop, tab_econ, tab_violence, tab_mating, tab_traits, tab_inst, tab_agents, tab_network, tab_events, tab_lives, tab_dynasty, tab_genome, tab_race, tab_science = st.tabs([
    "Population", "Economy", "Violence", "Mating", "Trait Evolution",
    "Institutions", "Agents", "Social Network", "Events",
    "Life Stories", "Dynasty Tree", "Genome Map", "Trait Race", "Science Report",
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

    # ── Realized Heritability Section ────────────────────────────
    st.markdown("---")
    st.subheader("Realized Heritability Over Time (h² = Var(genotype) / Var(phenotype))")
    st.caption(
        "Shows how much of each trait's variance is genetic vs environmental. "
        "h²=1.0 means all variation is genetic. h²<0.5 means environment "
        "is shaping traits more than genes. Watch how institutions and "
        "scenarios change which traits are genetically vs environmentally driven."
    )

    # Check if h2 columns exist
    h2_cols_available = [c for c in df.columns if c.startswith("h2_") and c != "avg_h2_all_traits"]

    if not h2_cols_available:
        st.info("No heritability data available. Heritability requires agents with finalized "
                "traits (age >= 15) and populated genotypes. Run a longer simulation.")
    else:
        default_h2 = [t for t in [
            "aggression_propensity", "cooperation_propensity",
            "intelligence_proxy", "group_loyalty",
            "future_orientation", "psychopathy_tendency",
        ] if f"h2_{t}" in df.columns]

        selected_h2_traits = st.multiselect(
            "Select traits to display",
            HERITABLE_TRAITS,
            default=default_h2,
            format_func=lambda t: TRAIT_ABBREV.get(t, t) if "TRAIT_ABBREV" in dir() else t,
            key="h2_trait_select",
        )

        show_ref = st.checkbox("Show theoretical h² reference lines", key="h2_ref_lines")

        fig = go.Figure()

        for trait in selected_h2_traits:
            col = f"h2_{trait}"
            if col not in df.columns:
                continue
            values = df[col].ffill().fillna(0.5)
            color = TRAIT_DOMAIN_COLORS.get(trait, "#888888")

            fig.add_trace(go.Scatter(
                x=df["year"], y=values,
                name=TRAIT_ABBREV.get(trait, trait[:12]),
                line=dict(color=color, width=2),
                mode="lines",
                hovertemplate="Year %{x}<br>h²=%{y:.3f}<br>" + TRAIT_ABBREV.get(trait, trait),
            ))

            # Rolling std band (5-year window)
            if len(values) >= 5:
                rolling_std = values.rolling(window=5, min_periods=1).std().fillna(0)
                add_band(fig, df["year"], values, rolling_std, color)

            # Theoretical reference line
            if show_ref and trait in TRAIT_HERITABILITY:
                ref_h2 = TRAIT_HERITABILITY[trait]
                fig.add_hline(
                    y=ref_h2, line_dash="dash", line_width=1,
                    line_color=color, opacity=0.4,
                    annotation_text=f"Expected: {TRAIT_ABBREV.get(trait, trait)} h²={ref_h2}",
                    annotation_position="right",
                    annotation_font_size=9, annotation_font_color=color,
                )

        fig.add_hline(y=0.5, line_dash="dot", line_color="white",
                      annotation_text="Nature = Nurture (h²=0.5)",
                      annotation_position="right")

        fig.update_layout(
            title="Realized Heritability Over Time",
            xaxis_title="Year",
            yaxis_title="Realized h² (Var genotype / Var phenotype)",
            yaxis=dict(range=[0, 1.05]),
            height=500, template="plotly_dark",
            margin=dict(l=40, r=40, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Aggregate h² chart
        if "avg_h2_all_traits" in df.columns:
            fig2 = go.Figure()
            avg_h2 = df["avg_h2_all_traits"].ffill().fillna(0.5)
            fig2.add_trace(go.Scatter(
                x=df["year"], y=avg_h2,
                name="Mean h² (all traits)",
                line=dict(color="#FFD54F", width=2),
                fill="tozeroy", fillcolor="rgba(255,213,79,0.15)",
            ))
            fig2.add_hline(y=0.5, line_dash="dot", line_color="white",
                           annotation_text="Above 0.5 = genetics dominating | Below 0.5 = environment dominating",
                           annotation_position="top right", annotation_font_size=10)
            fig2.update_layout(
                title="Mean Heritability Across All Traits",
                xaxis_title="Year",
                yaxis_title="Mean h²",
                yaxis=dict(range=[0, 1.05]),
                height=250, template="plotly_dark",
                margin=dict(l=40, r=40, t=40, b=40),
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.info(
            "Scientific interpretation: "
            "Rising h² means genetic selection is concentrating variation — the trait is becoming fixed. "
            "Falling h² means environmental factors (institutions, scarcity, development) "
            "are overriding genetic signal. "
            "Compare STRONG_STATE vs FREE_COMPETITION — institutions should reduce h² "
            "for cooperation as enforcement replaces genetic selection pressure."
        )

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

    # Trait evolution under institutional pressure
    st.markdown("---")
    st.subheader("Trait Evolution Under Institutional Pressure")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df["year"], y=df["avg_cooperation"], name="Cooperation",
                             line=dict(color="#43A047", width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["year"], y=df["avg_aggression"], name="Aggression",
                             line=dict(color="#E53935", width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["year"], y=df["law_strength"], name="Law Strength",
                             line=dict(color="#FFD54F", width=2, dash="dash")), secondary_y=True)
    fig.update_yaxes(title_text="Trait Value", secondary_y=False)
    fig.update_yaxes(title_text="Law Strength", secondary_y=True)
    fig.update_layout(title="Institutions Substitute for Traits", height=350,
                      template="plotly_dark", margin=dict(l=40, r=40, t=40, b=40))
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



def _render_biography(agent_id):
    """Render a rich biography card for an agent using Streamlit components."""
    a = society.get_by_id(agent_id)
    if not a:
        st.warning(f"Agent {agent_id} not found.")
        return

    name = _get_agent_name(agent_id, a)
    sex_str = a.sex.value.capitalize()
    sex_icon = "\u2640" if a.sex.value == "female" else "\u2642"

    if a.alive:
        birth_year = max(1, society.year - a.age)
        status_line = f"Born Year {birth_year} \u00b7 Age {a.age} \u00b7 Still Alive"
        status_icon = "\U0001f7e2"
    else:
        birth_year = (a.year_of_death - a.age) if a.year_of_death else "?"
        cause = a.cause_of_death or "unknown"
        status_line = f"Born Year {birth_year} \u00b7 Died Year {a.year_of_death} \u00b7 {cause}"
        status_icon = "\U0001f480"

    p1, p2 = a.parent_ids
    p1_name = _get_agent_name(p1) if p1 is not None else "Unknown"
    p2_name = _get_agent_name(p2) if p2 is not None else "Unknown"
    parents_str = f"{p1_name} \u00d7 {p2_name}" if (p1 is not None or p2 is not None) else "Unknown (Founder)"

    child_names = []
    for cid in list(a.offspring_ids)[:5]:
        child = society.get_by_id(cid)
        if child:
            child_names.append(_get_agent_name(cid, child))
    children_str = ", ".join(child_names) if child_names else "None"
    if len(a.offspring_ids) > 5:
        children_str += f" (+{len(a.offspring_ids) - 5} more)"

    trait_vals = [(t, getattr(a, t, 0.5)) for t in HERITABLE_TRAITS]
    trait_vals.sort(key=lambda x: x[1], reverse=True)
    top5 = trait_vals[:5]
    bottom3 = trait_vals[-3:]

    blocks = "\u2581\u2582\u2583\u2584\u2585\u2586\u2587\u2588"
    def _bar(val):
        idx = min(int(val * len(blocks)), len(blocks) - 1)
        return blocks[idx]

    agent_events = [e for e in events if agent_id in e.get("agent_ids", [])]
    agent_events.sort(key=lambda e: e.get("year", 0))

    event_icons = {
        "birth": "\U0001f476", "death": "\U0001f480", "pair_bond_formed": "\U0001f491",
        "bond_dissolved": "\U0001f494", "conflict": "\u2694\ufe0f",
        "epc_occurred": "\U0001f48b", "epc_detected": "\U0001f440",
        "mating_contest": "\U0001f94a", "flee": "\U0001f3c3",
        "punishment": "\u2696\ufe0f", "inheritance": "\U0001f4b0",
        "institution_emerged": "\U0001f3db\ufe0f", "maturation": "\U0001f331",
        "childhood_death": "\U0001f622", "infant_death": "\U0001f622",
    }

    def _format_event(e):
        etype = e.get("type", "")
        yr = e.get("year", "?")
        desc = e.get("description", "")
        icon = event_icons.get(etype, "\u00b7")
        if desc:
            return f"**Yr {yr}** {icon} {desc}"
        return f"**Yr {yr}** {icon} {etype.replace('_', ' ').title()}"

    partner_names = []
    for pid in a.partner_ids:
        partner = society.get_by_id(pid)
        if partner:
            partner_names.append(_get_agent_name(pid, partner))

    faction_str = f"Faction {a.faction_id}" if a.faction_id is not None else "No faction"
    conditions_str = ", ".join(a.active_conditions) if a.active_conditions else "None"
    life_stage = getattr(a, "life_stage", "Unknown")

    with st.container(border=True):
        st.markdown(f"## {sex_icon} {name}")
        st.markdown(f"{status_icon} {status_line}")
        st.markdown(f"*{sex_str} \u00b7 Generation {a.generation} \u00b7 {life_stage} \u00b7 {faction_str}*")
        st.markdown("---")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**\U0001f9ec Lineage**")
            st.markdown(f"Parents: {parents_str}")
            st.markdown(f"Children ({len(a.offspring_ids)}): {children_str}")
            if partner_names:
                st.markdown(f"Partner(s): {', '.join(partner_names)}")
            st.markdown("")
            st.markdown("**\U0001f4ca Status**")
            st.markdown(f"Reputation: {a.reputation:.2f} \u00b7 Health: {a.health:.2f}")
            st.markdown(f"Resources: {a.current_resources:.1f} \u00b7 Trauma: {a.trauma_score:.2f}")
            if conditions_str != "None":
                st.markdown(f"\u2695\ufe0f Conditions: {conditions_str}")

        with col2:
            st.markdown("**\U0001f4aa Dominant Traits**")
            domain_icons = {
                "physical": "\U0001f7e0", "cognitive": "\U0001f535", "temporal": "\U0001f7e1",
                "personality": "\U0001f7e3", "social": "\U0001f7e2", "reproductive": "\U0001fa77",
                "psychopath": "\U0001f534",
            }
            for t, v in top5:
                bar = _bar(v)
                d_icon = "\u26aa"
                if t in _physical: d_icon = "\U0001f7e0"
                elif t in _cognitive: d_icon = "\U0001f535"
                elif t in _temporal: d_icon = "\U0001f7e1"
                elif t in _personality: d_icon = "\U0001f7e3"
                elif t in _social: d_icon = "\U0001f7e2"
                elif t in _reproductive: d_icon = "\U0001fa77"
                elif t in _psychopath: d_icon = "\U0001f534"
                st.markdown(f"{d_icon} {TRAIT_ABBREV.get(t, t)}: **{v:.2f}** {bar}")
            st.markdown("")
            st.markdown("**\U0001f4c9 Weakest Traits**")
            for t, v in bottom3:
                st.markdown(f"\u00b7 {TRAIT_ABBREV.get(t, t)}: {v:.2f} {_bar(v)}")

        st.markdown("---")
        st.markdown("**\U0001f4d6 Life Events**")
        if agent_events:
            sig_events = [e for e in agent_events
                          if e.get("type", "") not in ("resource_transfers",)]
            display_events = sig_events[:20] if len(sig_events) > 5 else agent_events[:20]
            for e in display_events:
                st.markdown(_format_event(e))
            if len(agent_events) > 20:
                st.caption(f"... and {len(agent_events) - 20} more events")
        else:
            st.markdown("*No recorded events*")

        st.markdown("---")
        st.markdown("**\U0001f6e0 Skills**")
        sk1, sk2, sk3, sk4 = st.columns(4)
        sk1.metric("Foraging", f"{getattr(a, 'foraging_skill', 0):.2f}")
        sk2.metric("Combat", f"{getattr(a, 'combat_skill', 0):.2f}")
        sk3.metric("Social", f"{getattr(a, 'social_skill', 0):.2f}")
        sk4.metric("Craft", f"{getattr(a, 'craft_skill', 0):.2f}")


# ── TAB: Life Stories ────────────────────────────────────────────

with tab_lives:
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
    else:
        st.subheader("Featured Lives")

        all_agents = list(society.agents.values())
        all_ids = [a.id for a in all_agents]

        # Shuffle button updates the seed for featured agents
        col_title, col_shuffle = st.columns([4, 1])
        with col_shuffle:
            if st.button("Shuffle", key="shuffle_featured"):
                st.session_state["featured_seed"] = st.session_state.get("featured_seed", 42) + 1

        feat_seed = st.session_state.get("featured_seed", 42)
        rng_feat = np.random.default_rng(feat_seed)
        featured_ids = list(rng_feat.choice(all_ids, size=min(3, len(all_ids)), replace=False))

        cols = st.columns(3)
        for i, aid in enumerate(featured_ids):
            with cols[i]:
                _render_biography(int(aid))

        st.markdown("---")
        st.subheader("View Any Agent")

        col_sel, col_btn = st.columns([3, 1])
        with col_sel:
            selected_id = st.selectbox(
                "Select agent ID",
                sorted(all_ids),
                format_func=lambda x: f"{x} — {_get_agent_name(x)}",
                key="life_story_select",
            )
        with col_btn:
            if st.button("Random Agent", key="random_agent_btn"):
                selected_id = int(np.random.default_rng().choice(all_ids))

        if selected_id:
            _render_biography(int(selected_id))

# ── TAB: Dynasty Tree ────────────────────────────────────────────

with tab_dynasty:
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
    else:
        st.subheader("Dynasty Tree — Lineage Sunburst")

        # Build lineage: find founding ancestors and count descendants
        all_agents_dict = society.agents

        def _count_descendants(agent_id, memo={}):
            if agent_id in memo:
                return memo[agent_id]
            a = all_agents_dict.get(agent_id)
            if not a:
                memo[agent_id] = 0
                return 0
            total = len(a.offspring_ids)
            for oid in a.offspring_ids:
                total += _count_descendants(oid, memo)
            memo[agent_id] = total
            return total

        # Find generation-0 agents (founders)
        founders = [a for a in all_agents_dict.values() if a.generation == 0 and a.offspring_ids]
        founder_desc = [(a, _count_descendants(a.id, {})) for a in founders]
        founder_desc.sort(key=lambda x: x[1], reverse=True)
        top_founders = founder_desc[:8]

        if not top_founders:
            st.warning("No lineages found (no generation-0 agents with offspring).")
        else:
            labels = [f"{_get_agent_name(a.id, a)} line — {d} total descendants"
                      for a, d in top_founders]
            chosen_label = st.selectbox("Select lineage", labels, key="dynasty_select")
            chosen_idx = labels.index(chosen_label)
            root_agent, _ = top_founders[chosen_idx]

            # Build sunburst data by BFS from root (unique IDs to avoid Plotly collisions)
            sb_ids, sb_parents, sb_labels, sb_values, sb_colors = [], [], [], [], []

            queue = [(root_agent.id, "")]
            visited_sb = set()
            while queue:
                aid, parent_id_str = queue.pop(0)
                if aid in visited_sb:
                    continue
                visited_sb.add(aid)
                a = all_agents_dict.get(aid)
                if not a:
                    continue
                name = _get_agent_name(aid, a)
                unique_id = f"{name}_{aid}"
                sb_ids.append(unique_id)
                sb_parents.append(parent_id_str)
                sb_labels.append(name)
                sb_values.append(max(1, len(a.offspring_ids)))
                sb_colors.append(getattr(a, "cooperation_propensity", 0.5))
                for oid in a.offspring_ids:
                    queue.append((oid, unique_id))

            if len(sb_ids) == 0:
                st.warning("No lineage data to display.")
            else:
                if len(sb_ids) > 2000:
                    st.warning(f"Lineage has {len(sb_ids)} nodes — showing first 2000.")
                    sb_ids = sb_ids[:2000]
                    sb_parents = sb_parents[:2000]
                    sb_labels = sb_labels[:2000]
                    sb_values = sb_values[:2000]
                    sb_colors = sb_colors[:2000]

                fig = go.Figure(go.Sunburst(
                    ids=sb_ids, labels=sb_labels, parents=sb_parents,
                    values=sb_values,
                    marker=dict(
                        colors=sb_colors,
                        colorscale=[[0, "#E53935"], [0.5, "#FFFFFF"], [1, "#1E88E5"]],
                        showscale=True, colorbar=dict(title="Coop"),
                    ),
                    branchvalues="total",
                    hovertemplate="<b>%{label}</b><br>Offspring: %{value}<extra></extra>",
                ))
                fig.update_layout(height=650, template="plotly_dark",
                                  margin=dict(l=20, r=20, t=30, b=20),
                                  title=f"Lineage of {_get_agent_name(root_agent.id, root_agent)}")
                st.plotly_chart(fig, use_container_width=True)

        # Animated scatter: reproductive success by generation
        st.subheader("Reproductive Success Across Generations")
        scatter_records = []
        for a in all_agents_dict.values():
            birth_year = max(1, society.year - a.age) if a.alive else (
                a.year_of_death - a.age if a.year_of_death else 1)
            top_trait_name = max(HERITABLE_TRAITS, key=lambda t: getattr(a, t, 0.5))
            scatter_records.append({
                "Name": _get_agent_name(a.id, a),
                "Birth Year": int(birth_year),
                "Lifetime Births": a.lifetime_births,
                "Cooperation": round(a.cooperation_propensity, 3),
                "Offspring": len(a.offspring_ids),
                "Generation": a.generation,
                "Faction": a.faction_id if a.faction_id is not None else -1,
                "Top Trait": TRAIT_ABBREV.get(top_trait_name, top_trait_name),
            })
        sdf = pd.DataFrame(scatter_records)
        if len(sdf) > 0 and sdf["Generation"].nunique() > 1:
            fig = px.scatter(
                sdf, x="Birth Year", y="Lifetime Births",
                color="Cooperation", size="Offspring",
                animation_frame="Generation",
                hover_data=["Name", "Faction", "Top Trait"],
                color_continuous_scale=[[0, "#E53935"], [0.5, "#FFFFFF"], [1, "#1E88E5"]],
                title="Reproductive Success by Generation",
            )
            fig.update_layout(height=500, template="plotly_dark",
                              margin=dict(l=40, r=40, t=40, b=40))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Not enough generational data for animation.")

# ── TAB: Genome Map ──────────────────────────────────────────────

with tab_genome:
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
    elif not living:
        st.warning("No living agents.")
    else:
        st.subheader("Agent × Trait Heatmap")

        # Faction filter
        all_factions = sorted(set(a.faction_id for a in living if a.faction_id is not None))
        selected_factions = st.multiselect(
            "Filter by faction (empty = all)", all_factions,
            default=[], key="genome_faction_filter")

        if selected_factions:
            display_agents = [a for a in living if a.faction_id in selected_factions]
        else:
            display_agents = list(living)

        # Sort by faction then prestige
        display_agents.sort(key=lambda a: (a.faction_id if a.faction_id is not None else 9999,
                                           -a.prestige_score))

        # Limit to 300 agents for performance
        if len(display_agents) > 300:
            display_agents = display_agents[:300]
            st.caption(f"Showing top 300 of {len(living)} agents.")

        trait_names = list(HERITABLE_TRAITS)
        abbrevs = [TRAIT_ABBREV.get(t, t[:10]) for t in trait_names]

        # Build matrix
        matrix = np.array([[getattr(a, t, 0.5) for t in trait_names] for a in display_agents])
        agent_labels = [_get_agent_name(a.id, a) for a in display_agents]
        faction_labels = [str(a.faction_id) if a.faction_id is not None else "None" for a in display_agents]

        hover_text = []
        for i, a in enumerate(display_agents):
            row_hover = []
            for j, t in enumerate(trait_names):
                row_hover.append(
                    f"{agent_labels[i]}<br>Faction: {faction_labels[i]}<br>"
                    f"{TRAIT_ABBREV.get(t, t)}: {matrix[i, j]:.3f}")
            hover_text.append(row_hover)

        fig = go.Figure(go.Heatmap(
            z=matrix, x=abbrevs, y=agent_labels,
            colorscale=[[0, "#1565C0"], [0.5, "#FFFFFF"], [1, "#C62828"]],
            zmin=0, zmax=1,
            text=hover_text, hoverinfo="text",
            colorbar=dict(title="Trait Value"),
        ))

        # Draw horizontal lines between faction groups
        prev_faction = None
        for i, a in enumerate(display_agents):
            fid = a.faction_id
            if prev_faction is not None and fid != prev_faction:
                fig.add_hline(y=i - 0.5, line_width=1, line_color="rgba(255,255,255,0.3)")
            prev_faction = fid

        fig.update_layout(
            height=max(400, len(display_agents) * 4 + 100),
            template="plotly_dark",
            margin=dict(l=120, r=40, t=40, b=80),
            title="Agent × Trait Heatmap (sorted by faction, prestige)",
            xaxis=dict(tickangle=-45),
            yaxis=dict(showticklabels=len(display_agents) <= 80),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Chart 2: Trait correlation heatmap
        st.subheader("Trait Co-evolution Correlation (Living Population)")
        if len(living) >= 10:
            corr_matrix_data = np.array([[getattr(a, t, 0.5) for t in trait_names] for a in living])
            corr = np.corrcoef(corr_matrix_data, rowvar=False)

            fig = go.Figure(go.Heatmap(
                z=corr, x=abbrevs, y=abbrevs,
                colorscale=[[0, "#1565C0"], [0.5, "#FFFFFF"], [1, "#C62828"]],
                zmin=-1, zmax=1,
                colorbar=dict(title="Correlation"),
            ))
            fig.update_layout(
                height=700, template="plotly_dark",
                margin=dict(l=100, r=40, t=40, b=100),
                title="Trait Co-evolution Correlation (Living Population)",
                xaxis=dict(tickangle=-45),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Need at least 10 living agents for correlation matrix.")

# ── TAB: Trait Race ──────────────────────────────────────────────

with tab_race:
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
    else:
        st.subheader("Trait Race — Animated Bar Chart")

        # Build trait mean columns from df (use avg_ prefix columns)
        trait_col_map = {
            "aggression_propensity": "avg_aggression",
            "cooperation_propensity": "avg_cooperation",
            "attractiveness_base": "avg_attractiveness",
            "status_drive": "avg_status_drive",
            "risk_tolerance": "avg_risk_tolerance",
            "jealousy_sensitivity": "avg_jealousy",
            "fertility_base": "avg_fertility",
            "intelligence_proxy": "avg_intelligence",
        }
        # DD15+ traits use avg_{trait_name} pattern from metrics
        for t in HERITABLE_TRAITS:
            if t not in trait_col_map:
                col_candidate = f"avg_{t.replace('_propensity', '').replace('_proxy', '').replace('_base', '')}"
                # Check multiple naming patterns
                for candidate in [f"avg_{t}", col_candidate]:
                    if candidate in df.columns:
                        trait_col_map[t] = candidate
                        break

        # Sample every 5 years if > 100 years
        if len(df) > 100:
            race_df = df[df["year"] % 5 == 0].copy()
        else:
            race_df = df.copy()

        # Build long-form data for animation
        race_records = []
        for _, row in race_df.iterrows():
            yr = int(row["year"])
            trait_vals = []
            for t in HERITABLE_TRAITS:
                col = trait_col_map.get(t)
                if col and col in race_df.columns:
                    val = float(row[col])
                else:
                    val = 0.5  # default
                trait_vals.append((t, val))

            # Sort by value descending for this frame
            trait_vals.sort(key=lambda x: x[1], reverse=True)
            for rank, (t, v) in enumerate(trait_vals):
                race_records.append({
                    "Year": yr,
                    "Trait": TRAIT_ABBREV.get(t, t[:12]),
                    "Value": round(v, 4),
                    "Color": TRAIT_DOMAIN_COLORS.get(t, "#888888"),
                    "Domain": next((d for d, ts in [
                        ("Physical", _physical), ("Cognitive", _cognitive),
                        ("Temporal", _temporal), ("Personality", _personality),
                        ("Social", _social), ("Reproductive", _reproductive),
                        ("Psychopathology", _psychopath),
                    ] if t in ts), "Other"),
                })

        rdf = pd.DataFrame(race_records)

        if len(rdf) > 0:
            fig = px.bar(
                rdf, x="Value", y="Trait", color="Domain",
                animation_frame="Year", orientation="h",
                range_x=[0, 1],
                color_discrete_map={
                    "Physical": "#FF6B35", "Cognitive": "#4ECDC4",
                    "Temporal": "#FFE66D", "Personality": "#C77DFF",
                    "Social": "#06D6A0", "Reproductive": "#F72585",
                    "Psychopathology": "#EF233C", "Other": "#888888",
                },
                title="Trait Race — Mean Values Over Time",
            )
            fig.update_layout(
                height=800, template="plotly_dark",
                margin=dict(l=120, r=40, t=60, b=40),
                yaxis=dict(categoryorder="total ascending"),
            )
            st.plotly_chart(fig, use_container_width=True)

        # Static multi-line chart for 6 key traits with bands
        st.subheader("Key Trait Trajectories (±1σ)")
        key_traits = [
            ("avg_cooperation", "trait_std_cooperation", "#06D6A0", "Cooperation"),
            ("avg_aggression", "trait_std_aggression", "#E53935", "Aggression"),
            ("avg_intelligence", "trait_std_intelligence", "#4ECDC4", "Intelligence"),
        ]
        # Add DD27 traits if columns exist
        for col, label, color in [
            ("avg_group_loyalty", "Loyalty", "#06D6A0"),
            ("avg_future_orientation", "Future Or", "#FFE66D"),
            ("avg_psychopathy_tendency", "Psychopathy", "#EF233C"),
        ]:
            if col in df.columns:
                std_col = col.replace("avg_", "trait_std_") if col.replace("avg_", "trait_std_") in df.columns else None
                # Try psychopathy_std specifically
                if col == "avg_psychopathy_tendency" and "psychopathy_std" in df.columns:
                    std_col = "psychopathy_std"
                key_traits.append((col, std_col, color, label))

        fig = go.Figure()
        for mean_col, std_col, color, label in key_traits:
            if mean_col not in df.columns:
                continue
            fig.add_trace(go.Scatter(
                x=df["year"], y=df[mean_col], name=label,
                line=dict(color=color, width=2)))
            # Band from trait std column or multi-run std
            band_std = None
            if std_col and std_col in df.columns:
                band_std = df[std_col]
            elif is_multi_run and df_std is not None and mean_col in df_std.columns:
                band_std = df_std[mean_col]
            if band_std is not None:
                add_band(fig, df["year"], df[mean_col], band_std, color)

        fig.update_layout(
            title="Key Trait Trajectories with ±1σ Bands", height=450,
            template="plotly_dark", margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, use_container_width=True)

# ── TAB: Science Report ──────────────────────────────────────────

with tab_science:
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
    else:
        st.title("Science Report")

        # ── PANEL 1: Trait Fitness Correlations ──────────────────
        with st.expander("Selection Pressure — Trait Correlation with Reproductive Success", expanded=True):
            st.caption(
                "Positive = trait increases offspring count. Negative = trait reduces fitness. "
                "This shows what evolution is actually selecting for in this run."
            )

            all_agents_list = list(society.agents.values())
            parents = [a for a in all_agents_list if len(a.offspring_ids) > 0]

            if len(parents) < 20:
                st.warning("Not enough parents (need 20+) to compute fitness correlations.")
            else:
                fitness_vals = np.array([len(a.offspring_ids) for a in parents])
                corr_records = []
                for trait in HERITABLE_TRAITS:
                    t_vals = np.array([getattr(a, trait, 0.5) for a in parents])
                    if np.std(t_vals) < 1e-8:
                        continue
                    r = float(np.corrcoef(t_vals, fitness_vals)[0, 1])
                    corr_records.append({"Trait": TRAIT_ABBREV.get(trait, trait),
                                         "trait_key": trait, "Correlation": r})

                if corr_records:
                    cdf = pd.DataFrame(corr_records).sort_values("Correlation", key=abs, ascending=True)
                    colors = ["#4ECDC4" if v >= 0 else "#FF6B6B" for v in cdf["Correlation"]]

                    fig = go.Figure(go.Bar(
                        x=cdf["Correlation"], y=cdf["Trait"], orientation="h",
                        marker_color=colors,
                    ))
                    fig.add_vline(x=0, line_color="white", line_width=1)
                    fig.update_layout(title="Trait Selection Pressure (end of simulation)",
                                      xaxis_title="Pearson r with offspring count",
                                      height=600, template="plotly_dark",
                                      margin=dict(l=120, r=40, t=40, b=40))
                    st.plotly_chart(fig, use_container_width=True)

                # Time-series selection pressure (rolling 20yr)
                if len(df) >= 25 and "avg_lifetime_births" in df.columns:
                    st.subheader("Selection Pressure Over Time (rolling 20yr window)")
                    # Use top 6 correlated traits
                    top6 = sorted(corr_records, key=lambda x: abs(x["Correlation"]), reverse=True)[:6]
                    trait_col_map_sp = {
                        "aggression_propensity": "avg_aggression",
                        "cooperation_propensity": "avg_cooperation",
                        "intelligence_proxy": "avg_intelligence",
                    }
                    for t in HERITABLE_TRAITS:
                        for prefix in [f"avg_{t}", f"avg_{t.split('_')[0]}"]:
                            if prefix in df.columns and t not in trait_col_map_sp:
                                trait_col_map_sp[t] = prefix
                                break

                    fig = go.Figure()
                    births_series = df["avg_lifetime_births"]
                    for rec in top6:
                        trait = rec["trait_key"]
                        col = trait_col_map_sp.get(trait)
                        if col and col in df.columns:
                            # Rolling correlation
                            rolling_r = df[col].rolling(20, min_periods=10).corr(births_series)
                            color = TRAIT_DOMAIN_COLORS.get(trait, "#888")
                            fig.add_trace(go.Scatter(
                                x=df["year"], y=rolling_r,
                                name=TRAIT_ABBREV.get(trait, trait[:10]),
                                line=dict(color=color, width=2),
                            ))
                    fig.add_hline(y=0, line_dash="dot", line_color="white", opacity=0.5)
                    fig.update_layout(title="Rolling 20yr Correlation with Lifetime Births",
                                      yaxis_title="Pearson r", height=350,
                                      template="plotly_dark",
                                      margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, use_container_width=True)

        # ── PANEL 2: Institutional Impact ────────────────────────
        with st.expander("Institutional Effects on Evolution", expanded=False):
            st.caption("Shows how law_strength correlates with trait evolution and social outcomes.")

            col1, col2, col3 = st.columns(3)
            pairs = [
                (col1, "violence_rate", "Institutions → Violence", "#E53935"),
                (col2, "avg_cooperation", "Institutions → Cooperation", "#43A047"),
                (col3, "resource_gini", "Institutions → Inequality", "#FF9800"),
            ]
            for col, metric, title, _color in pairs:
                with col:
                    if metric in df.columns:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=df["law_strength"], y=df[metric], mode="markers",
                            marker=dict(color=df["year"], colorscale="RdYlBu_r",
                                        size=5, showscale=(metric == "violence_rate"),
                                        colorbar=dict(title="Year")),
                            hovertemplate="Law=%{x:.2f}<br>Value=%{y:.3f}<br>Year=%{marker.color}",
                        ))
                        # Trendline
                        if df["law_strength"].std() > 0.01:
                            z = np.polyfit(df["law_strength"], df[metric], 1)
                            p = np.poly1d(z)
                            x_line = np.linspace(df["law_strength"].min(), df["law_strength"].max(), 50)
                            fig.add_trace(go.Scatter(x=x_line, y=p(x_line), mode="lines",
                                                     line=dict(color="white", dash="dash", width=1),
                                                     showlegend=False))
                        fig.update_layout(title=title, height=300, template="plotly_dark",
                                          xaxis_title="Law Strength", yaxis_title=metric,
                                          margin=dict(l=40, r=20, t=40, b=40))
                        st.plotly_chart(fig, use_container_width=True)

            # Correlation table
            corr_metrics = ["violence_rate", "avg_cooperation", "resource_gini",
                            "avg_aggression", "avg_lifetime_births"]
            corr_rows = []
            for m in corr_metrics:
                if m in df.columns and df["law_strength"].std() > 0.01:
                    r = float(np.corrcoef(df["law_strength"], df[m])[0, 1])
                    direction = "Positive" if r > 0.05 else ("Negative" if r < -0.05 else "Neutral")
                    corr_rows.append({"Metric": m, "Correlation with Law Strength": round(r, 3),
                                      "Direction": direction})
            if corr_rows:
                st.dataframe(pd.DataFrame(corr_rows), use_container_width=True)

        # ── PANEL 3: Genetic Diversity ───────────────────────────
        with st.expander("Gene Pool Diversity Over Time", expanded=False):
            st.caption("Tracks whether the population is diversifying, stabilizing, or converging.")

            std_cols = [c for c in df.columns if c.startswith("trait_std_")]
            if std_cols:
                mean_diversity = df[std_cols].mean(axis=1)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df["year"], y=mean_diversity,
                                         name="Mean Genetic Variance",
                                         line=dict(color="#FFD54F", width=2)))
                if "trait_std_aggression" in df.columns:
                    fig.add_trace(go.Scatter(x=df["year"], y=df["trait_std_aggression"],
                                             name="Aggression Variance",
                                             line=dict(color="#E53935", dash="dash")))
                if "trait_std_cooperation" in df.columns:
                    fig.add_trace(go.Scatter(x=df["year"], y=df["trait_std_cooperation"],
                                             name="Cooperation Variance",
                                             line=dict(color="#43A047", dash="dash")))

                fig.add_hline(y=0.09, line_dash="dot", line_color="cyan", opacity=0.6,
                              annotation_text="Empirical baseline (~0.09)",
                              annotation_position="right")
                # Danger zone below 0.05
                fig.add_hrect(y0=0, y1=0.05, fillcolor="red", opacity=0.08,
                              annotation_text="Low diversity warning", annotation_position="top left")
                fig.update_layout(title="Genetic Diversity Over Time", height=350,
                                  template="plotly_dark", yaxis_title="Trait Std Dev",
                                  margin=dict(l=40, r=40, t=40, b=40))
                st.plotly_chart(fig, use_container_width=True)

                # Diversity stats
                current_div = float(mean_diversity.iloc[-1])
                initial_div = float(mean_diversity.iloc[0])
                delta = current_div - initial_div
                c1, c2 = st.columns(2)
                c1.metric("Current Mean Trait Variance", f"{current_div:.4f}",
                          delta=f"{delta:+.4f} from year 1")
                trend = "Increasing" if delta > 0.005 else ("Declining" if delta < -0.005 else "Stable")
                c2.metric("Diversity Trend", trend)
            else:
                st.info("No trait standard deviation columns available.")

        # ── PANEL 4: Founder Effect & Lineage Dominance ──────────
        with st.expander("Genetic Dominance — Top Founding Lineages", expanded=False):
            st.caption("Which founding genomes came to dominate the population.")

            all_agents_dict = society.agents

            def _find_founder(agent_id, visited=None):
                if visited is None:
                    visited = set()
                if agent_id in visited:
                    return agent_id
                visited.add(agent_id)
                a = all_agents_dict.get(agent_id)
                if not a or a.parent_ids == (None, None):
                    return agent_id
                p1, p2 = a.parent_ids
                # Follow mother line for simplicity
                if p1 is not None and p1 in all_agents_dict:
                    return _find_founder(p1, visited)
                if p2 is not None and p2 in all_agents_dict:
                    return _find_founder(p2, visited)
                return agent_id

            # Count living descendants per founder
            founder_counts = defaultdict(int)
            for a in living:
                fid = _find_founder(a.id)
                founder_counts[fid] += 1

            top_founders = sorted(founder_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            total_living = len(living)

            if top_founders:
                f_names = []
                f_pcts = []
                f_colors = []
                table_rows = []
                for fid, count in top_founders:
                    fa = all_agents_dict.get(fid)
                    name = _get_agent_name(fid, fa)
                    pct = count / total_living * 100
                    coop = getattr(fa, "cooperation_propensity", 0.5) if fa else 0.5
                    gen = getattr(fa, "generation", 0) if fa else 0
                    top_trait = max(HERITABLE_TRAITS[:8],
                                   key=lambda t: getattr(fa, t, 0.5)) if fa else "?"
                    f_names.append(name)
                    f_pcts.append(pct)
                    f_colors.append(coop)
                    table_rows.append({
                        "Founder": name, "Descendants": count,
                        "% Population": f"{pct:.1f}%",
                        "Dominant Trait": TRAIT_ABBREV.get(top_trait, top_trait),
                        "Generation": gen,
                    })

                fig = go.Figure(go.Bar(
                    x=f_pcts, y=f_names, orientation="h",
                    marker=dict(color=f_colors,
                                colorscale=[[0, "#E53935"], [0.5, "#FFFFFF"], [1, "#1E88E5"]],
                                showscale=True, colorbar=dict(title="Coop")),
                ))
                fig.update_layout(title="Top 10 Lineages by Living Descendants",
                                  xaxis_title="% of Living Population",
                                  height=350, template="plotly_dark",
                                  margin=dict(l=140, r=40, t=40, b=40))
                st.plotly_chart(fig, use_container_width=True)
                st.dataframe(pd.DataFrame(table_rows), use_container_width=True)
            else:
                st.info("No lineage data available.")

        # ── PANEL 5: Agent Archetypes ────────────────────────────
        with st.expander("Emergent Population Archetypes", expanded=False):
            st.caption("K-means clustering on agent traits reveals natural phenotype clusters.")

            try:
                from sklearn.cluster import KMeans
                from sklearn.decomposition import PCA
                _has_sklearn = True
            except ImportError:
                _has_sklearn = False

            if not _has_sklearn:
                st.warning("Install scikit-learn for archetypes: `pip install scikit-learn`")
            elif len(living) < 20:
                st.warning("Need at least 20 living agents for clustering.")
            else:
                n_clusters = st.slider("Number of archetypes", 2, 8, 4, key="n_archetypes")
                core_8 = HERITABLE_TRAITS[:8]
                X = np.array([[getattr(a, t, 0.5) for t in core_8] for a in living])

                km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
                labels = km.fit_predict(X)
                centers = km.cluster_centers_

                # Name archetypes
                archetype_names = []
                for ci in range(n_clusters):
                    m_agg = centers[ci][0]
                    m_coop = centers[ci][1]
                    m_intel = centers[ci][7]
                    m_risk = centers[ci][4]
                    m_status = centers[ci][3]
                    m_fert = centers[ci][6]
                    # Check extended traits if available
                    cluster_agents = [living[i] for i in range(len(living)) if labels[i] == ci]
                    m_psych = float(np.mean([getattr(a, "psychopathy_tendency", 0.2) for a in cluster_agents]))
                    m_maternal = float(np.mean([getattr(a, "maternal_investment", 0.5) for a in cluster_agents]))

                    if m_agg > 0.6 and m_coop < 0.4:
                        name = "Warrior"
                    elif m_coop > 0.6 and m_agg < 0.4:
                        name = "Diplomat"
                    elif m_intel > 0.6 and m_risk < 0.4:
                        name = "Scholar"
                    elif m_risk > 0.6 and m_status > 0.6:
                        name = "Opportunist"
                    elif m_fert > 0.6 and m_maternal > 0.6:
                        name = "Caregiver"
                    elif m_psych > 0.4:
                        name = "Predator"
                    else:
                        name = f"Type {ci + 1}"
                    archetype_names.append(name)

                # Radar chart
                core_abbrevs = [TRAIT_ABBREV.get(t, t[:6]) for t in core_8]
                arc_colors = px.colors.qualitative.Set2
                fig = go.Figure()
                for ci in range(n_clusters):
                    vals = list(centers[ci]) + [centers[ci][0]]  # close the polygon
                    fig.add_trace(go.Scatterpolar(
                        r=vals, theta=core_abbrevs + [core_abbrevs[0]],
                        fill="toself", name=archetype_names[ci],
                        line=dict(color=arc_colors[ci % len(arc_colors)]),
                        opacity=0.7,
                    ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title="Archetype Trait Profiles", height=400,
                    template="plotly_dark",
                    margin=dict(l=60, r=60, t=60, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Population counts
                col1, col2 = st.columns(2)
                with col1:
                    counts = [int(np.sum(labels == ci)) for ci in range(n_clusters)]
                    fig = go.Figure(go.Bar(
                        x=archetype_names, y=counts,
                        marker_color=[arc_colors[i % len(arc_colors)] for i in range(n_clusters)],
                    ))
                    fig.update_layout(title="Population by Archetype", height=250,
                                      template="plotly_dark",
                                      margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, use_container_width=True)

                # PCA scatter
                with col2:
                    pca = PCA(n_components=2)
                    X2 = pca.fit_transform(X)
                    repro = [len(a.offspring_ids) for a in living]
                    pca_df = pd.DataFrame({
                        "PC1": X2[:, 0], "PC2": X2[:, 1],
                        "Archetype": [archetype_names[l] for l in labels],
                        "Offspring": repro,
                    })
                    fig = px.scatter(pca_df, x="PC1", y="PC2", color="Archetype",
                                     size="Offspring", opacity=0.6,
                                     color_discrete_sequence=arc_colors,
                                     title="PCA — Trait Space")
                    fig.update_layout(height=250, template="plotly_dark",
                                      margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, use_container_width=True)

        # ── PANEL 6: Civilization Timeline ────────────────────────
        with st.expander("Civilization Timeline — Major Events", expanded=False):
            st.caption("Automatically extracted from simulation event logs.")

            timeline_events = []

            # Extract categorized events
            for e in events:
                yr = e.get("year", 0)
                etype = e.get("type", "")
                desc = e.get("description", "")

                if "epidemic" in etype and "death" not in etype:
                    timeline_events.append((yr, "Epidemic", f"Epidemic outbreak"))
                elif etype == "institution_emerged":
                    timeline_events.append((yr, "Institution", f"Institution formed: {desc}"))
                elif etype == "belief_revolution":
                    timeline_events.append((yr, "Belief", f"Belief revolution"))
                elif "faction" in etype and "formed" in desc.lower():
                    timeline_events.append((yr, "Faction", f"Faction formed"))
                elif "faction" in etype and "schism" in desc.lower():
                    timeline_events.append((yr, "Schism", f"Faction schism"))
                elif etype == "scarcity_start":
                    timeline_events.append((yr, "Scarcity", f"Resource scarcity"))

            # Population crises/booms from metrics
            for i in range(1, len(df)):
                prev_pop = df.iloc[i - 1]["population"]
                curr_pop = df.iloc[i]["population"]
                if prev_pop > 0:
                    change = (curr_pop - prev_pop) / prev_pop
                    yr = int(df.iloc[i]["year"])
                    if change < -0.10:
                        timeline_events.append((yr, "Crisis", f"Population dropped {change:.0%}"))
                    elif change > 0.15:
                        timeline_events.append((yr, "Boom", f"Population surged {change:.0%}"))

            # Law strength milestones
            crossed_03 = False
            crossed_06 = False
            for _, row in df.iterrows():
                ls = row.get("law_strength", 0)
                yr = int(row["year"])
                if ls >= 0.3 and not crossed_03:
                    timeline_events.append((yr, "Law", "Law emerged (strength > 0.3)"))
                    crossed_03 = True
                if ls >= 0.6 and not crossed_06:
                    timeline_events.append((yr, "Strong Law", "Strong institutions (strength > 0.6)"))
                    crossed_06 = True

            timeline_events.sort(key=lambda x: x[0])

            # Deduplicate nearby events of same type
            filtered_tl = []
            last_by_type = {}
            for yr, cat, desc in timeline_events:
                if cat in last_by_type and yr - last_by_type[cat] < 3:
                    continue
                last_by_type[cat] = yr
                filtered_tl.append((yr, cat, desc))

            if filtered_tl:
                cat_icons = {
                    "Epidemic": "🦠", "Institution": "⚖️", "Belief": "💡",
                    "Faction": "🤝", "Schism": "💥", "Scarcity": "🌵",
                    "Crisis": "☠️", "Boom": "🌱", "Law": "📜", "Strong Law": "🏛️",
                }
                cat_y = {cat: i for i, cat in enumerate(sorted(set(c for _, c, _ in filtered_tl)))}
                cat_colors = {
                    "Epidemic": "#E53935", "Institution": "#1E88E5", "Belief": "#FFD54F",
                    "Faction": "#43A047", "Schism": "#FF9800", "Scarcity": "#795548",
                    "Crisis": "#F44336", "Boom": "#66BB6A", "Law": "#42A5F5",
                    "Strong Law": "#1565C0",
                }

                fig = go.Figure()
                for yr, cat, desc in filtered_tl:
                    fig.add_trace(go.Scatter(
                        x=[yr], y=[cat_y.get(cat, 0)],
                        mode="markers+text",
                        marker=dict(size=12, color=cat_colors.get(cat, "#888")),
                        text=[cat_icons.get(cat, "•")],
                        textposition="top center",
                        hovertemplate=f"Year {yr}<br>{cat}: {desc}<extra></extra>",
                        showlegend=False,
                    ))
                fig.update_layout(
                    title="Civilization Timeline",
                    yaxis=dict(tickvals=list(cat_y.values()), ticktext=list(cat_y.keys())),
                    xaxis_title="Year", height=400, template="plotly_dark",
                    margin=dict(l=100, r=40, t=40, b=40),
                )
                st.plotly_chart(fig, use_container_width=True)

                # Text timeline
                st.markdown("#### Event Log")
                for yr, cat, desc in filtered_tl:
                    icon = cat_icons.get(cat, "•")
                    st.markdown(f"**Year {yr}** — {icon} {desc}")
            else:
                st.info("No major events detected. Try a longer simulation or enable institutional drift.")
