"""
SIMSIV Dashboard — Streamlit entry point.
Run: python -m streamlit run dashboard/app.py
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from dashboard.components.constants import TAB_NAMES
from dashboard.components.sidebar import render_sidebar
from dashboard.components.runner import run_single, run_multi
from dashboard.components.kpi_bar import render_kpi_bar

import dashboard.tabs.population   as tab_population
import dashboard.tabs.economy      as tab_economy
import dashboard.tabs.violence     as tab_violence
import dashboard.tabs.mating       as tab_mating
import dashboard.tabs.traits       as tab_traits
import dashboard.tabs.institutions as tab_institutions
import dashboard.tabs.beliefs      as tab_beliefs
import dashboard.tabs.agents       as tab_agents
import dashboard.tabs.network      as tab_network
import dashboard.tabs.events       as tab_events
import dashboard.tabs.life_stories as tab_life_stories
import dashboard.tabs.dynasty      as tab_dynasty
import dashboard.tabs.genome       as tab_genome
import dashboard.tabs.trait_race   as tab_trait_race
import dashboard.tabs.science      as tab_science
import dashboard.tabs.compare      as tab_compare

st.set_page_config(
    page_title="SIMSIV",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.title("SIMSIV — Social Simulation Dashboard")
st.caption("Simulation of Intersecting Social and Institutional Variables")

# Sidebar — returns params dict with run_clicked flag
params = render_sidebar()

if params["run_clicked"]:
    if params["research_mode"]:
        state = run_multi(params)
    else:
        state = run_single(params)
    for k, v in state.items():
        st.session_state[k] = v
    st.session_state.pop("hof_data", None)  # invalidate hall of fame cache

if "df" not in st.session_state:
    st.info("Configure parameters in the sidebar and click **Run Simulation** to begin.")
    st.stop()

# Unpack session state
df          = st.session_state["df"]
df_std      = st.session_state.get("df_std")
is_multi    = st.session_state.get("is_multi_run", False)
seeds_count = st.session_state.get("seeds_count", 1)
living      = st.session_state["living"]
society     = st.session_state["society"]
config      = st.session_state["config"]
sim_events  = st.session_state["events"]

# KPI bar
st.markdown("---")
render_kpi_bar(df, is_multi, seeds_count)
st.markdown("---")

# Tab router
tabs = st.tabs(TAB_NAMES)
ctx = dict(df=df, df_std=df_std, living=living, society=society,
           config=config, sim_events=sim_events, is_multi_run=is_multi,
           seeds_count=seeds_count)

with tabs[0]:  tab_population.render(**ctx)
with tabs[1]:  tab_economy.render(**ctx)
with tabs[2]:  tab_violence.render(**ctx)
with tabs[3]:  tab_mating.render(**ctx)
with tabs[4]:  tab_traits.render(**ctx)
with tabs[5]:  tab_institutions.render(**ctx)
with tabs[6]:  tab_beliefs.render(**ctx)
with tabs[7]:  tab_agents.render(**ctx)
with tabs[8]:  tab_network.render(**ctx)
with tabs[9]:  tab_events.render(**ctx)
with tabs[10]: tab_life_stories.render(**ctx)
with tabs[11]: tab_dynasty.render(**ctx)
with tabs[12]: tab_genome.render(**ctx)
with tabs[13]: tab_trait_race.render(**ctx)
with tabs[14]: tab_science.render(**ctx)
with tabs[15]: tab_compare.render(**ctx, base_params=params)
