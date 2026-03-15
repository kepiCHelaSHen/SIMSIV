# SIMSIV — Dashboard Overhaul (Phase G)
# Executable Chain Prompt — Run in Claude Code CLI
# Root: D:\EXPERIMENTS\SIM
# Target: dashboard/app.py + new dashboard/ submodules
# Authored: 2026-03-15

================================================================================
INSTRUCTIONS FOR CLAUDE CODE
================================================================================

You are refactoring and extending the SIMSIV Streamlit dashboard.
Read this entire file before writing a single line of code.
Work through every block in order. Each block is self-contained and numbered.

Start by reading these files in full:
  - D:\EXPERIMENTS\SIM\dashboard\app.py          (111KB — the current monolith)
  - D:\EXPERIMENTS\SIM\models\agent.py           (agent fields and properties)
  - D:\EXPERIMENTS\SIM\metrics\collectors.py     (what columns exist in df)
  - D:\EXPERIMENTS\SIM\experiments\scenarios.py  (scenario names and configs)

RULES:
  - Do not change any simulation logic, engines, models, or config files
  - Do not change any metric column names (breaks existing outputs)
  - Preserve ALL existing functionality — this is a refactor + addition, not a rewrite
  - Every new chart or panel must handle empty data gracefully (st.info() fallback)
  - All Plotly figures use template="plotly_dark" unless noted
  - Use COLORS dict (defined in block 1) everywhere instead of hardcoded hex strings
  - After completing all blocks, verify: streamlit run dashboard/app.py loads correctly

================================================================================
BLOCK 1 — CREATE DIRECTORY STRUCTURE + SHARED CONSTANTS
================================================================================

Create these directories:
  D:\EXPERIMENTS\SIM\dashboard\components\
  D:\EXPERIMENTS\SIM\dashboard\tabs\

CREATE D:\EXPERIMENTS\SIM\dashboard\components\__init__.py  (empty)
CREATE D:\EXPERIMENTS\SIM\dashboard\tabs\__init__.py  (empty)

CREATE D:\EXPERIMENTS\SIM\dashboard\components\constants.py:

  """Shared constants for SIMSIV dashboard."""

  PLOT_TEMPLATE = "plotly_dark"

  COLORS = {
      # Domains
      "population":   "#2196F3",
      "births":       "#4CAF50",
      "deaths":       "#F44336",
      "males":        "#42A5F5",
      "females":      "#EF5350",
      "children":     "#FFA726",
      "violence":     "#E53935",
      "cooperation":  "#43A047",
      "resources":    "#FF9800",
      "inequality":   "#FF7043",
      "status":       "#AB47BC",
      "health":       "#66BB6A",
      "intelligence": "#4ECDC4",
      "law":          "#1E88E5",
      "belief":       "#FFD54F",
      "faction":      "#43A047",
      "schism":       "#FF9800",
      "scarcity":     "#795548",
      "epidemic":     "#E53935",
      "age":          "#AB47BC",
      "mating":       "#F72585",
      "bond":         "#FF6B6B",
      "prestige":     "#FFD700",
      "dominance":    "#FF4500",
      "neutral":      "#888888",
      # Trait domains
      "physical":       "#FF6B35",
      "cognitive":      "#4ECDC4",
      "temporal":       "#FFE66D",
      "personality":    "#C77DFF",
      "social":         "#06D6A0",
      "reproductive":   "#F72585",
      "psychopathology":"#EF233C",
  }

  TRAIT_ABBREV = {
      "aggression_propensity": "Aggression",
      "cooperation_propensity": "Coop",
      "attractiveness_base": "Attract",
      "status_drive": "Status",
      "risk_tolerance": "Risk",
      "jealousy_sensitivity": "Jealousy",
      "fertility_base": "Fertility",
      "intelligence_proxy": "Intel",
      "longevity_genes": "Longevity",
      "disease_resistance": "Disease Res",
      "physical_robustness": "Robustness",
      "pain_tolerance": "Pain Tol",
      "mental_health_baseline": "MH Base",
      "emotional_intelligence": "Emot Intel",
      "impulse_control": "Impulse",
      "novelty_seeking": "Novelty",
      "empathy_capacity": "Empathy",
      "conformity_bias": "Conform",
      "dominance_drive": "Dominance",
      "maternal_investment": "Maternal",
      "sexual_maturation_rate": "Sex Mat",
      "cardiovascular_risk": "Cardio Risk",
      "mental_illness_risk": "Mental Risk",
      "autoimmune_risk": "Autoimmune",
      "metabolic_risk": "Metabolic",
      "degenerative_risk": "Degen Risk",
      "physical_strength": "Strength",
      "endurance": "Endurance",
      "group_loyalty": "Loyalty",
      "outgroup_tolerance": "Outgroup",
      "future_orientation": "Future Or",
      "conscientiousness": "Conscient",
      "psychopathy_tendency": "Psychopathy",
      "anxiety_baseline": "Anxiety",
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
      "psychopathology":["psychopathy_tendency", "mental_illness_risk", "cardiovascular_risk",
                         "autoimmune_risk", "metabolic_risk", "degenerative_risk"],
  }

  TRAIT_DOMAIN_COLORS = {}
  for domain, traits in TRAIT_DOMAINS.items():
      for t in traits:
          TRAIT_DOMAIN_COLORS[t] = COLORS[domain if domain in COLORS else "neutral"]

  TAB_NAMES = [
      "📊 Population", "💰 Economy", "⚔️ Violence", "💕 Mating",
      "🧬 Trait Evolution", "⚖️ Institutions", "💡 Beliefs",
      "👤 Agents", "🕸️ Social Network", "📅 Events",
      "🏆 Hall of Fame", "🌳 Dynasty Tree", "🔬 Genome Map",
      "🏁 Trait Race", "🔭 Science Report", "⚡ Compare",
  ]

================================================================================
BLOCK 2 — CREATE components/charts.py (shared chart utilities)
================================================================================

CREATE D:\EXPERIMENTS\SIM\dashboard\components\charts.py:

  """Shared chart helper functions for SIMSIV dashboard."""

  import numpy as np
  import pandas as pd
  import plotly.graph_objects as go
  from .constants import COLORS, PLOT_TEMPLATE


  def hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
      h = color_hex.lstrip("#")
      return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


  def add_band(fig, x, mean_series, std_series, color_hex, secondary_y=None):
      """Add a ±1σ shaded confidence band to a Plotly figure."""
      if std_series is None:
          return
      upper = mean_series + std_series
      lower = np.maximum(mean_series - std_series, 0)
      r, g, b = hex_to_rgb(color_hex)
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


  def add_epidemic_bands(fig, df: pd.DataFrame):
      """Add vertical red shaded bands for epidemic years to any time-series figure.

      Reads 'epidemic_active' column if present; falls back to 'epidemic_deaths' > 0.
      Call this on any time-series figure before st.plotly_chart().
      """
      epi_col = None
      if "epidemic_active" in df.columns:
          epi_col = "epidemic_active"
      elif "epidemic_deaths" in df.columns:
          epi_col = "epidemic_deaths"
      if epi_col is None:
          return

      in_epidemic = False
      start_yr = None
      for _, row in df.iterrows():
          active = bool(row[epi_col]) if epi_col == "epidemic_active" else row[epi_col] > 0
          yr = row["year"]
          if active and not in_epidemic:
              start_yr = yr
              in_epidemic = True
          elif not active and in_epidemic:
              fig.add_vrect(
                  x0=start_yr, x1=yr,
                  fillcolor="rgba(229,57,53,0.12)",
                  layer="below", line_width=0,
                  annotation_text="🦠", annotation_position="top left",
              )
              in_epidemic = False
      if in_epidemic and start_yr is not None:
          fig.add_vrect(
              x0=start_yr, x1=df["year"].iloc[-1],
              fillcolor="rgba(229,57,53,0.12)",
              layer="below", line_width=0,
          )


  def lorenz_curve(values: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
      """Compute Lorenz curve from an array of values.
      Returns (x, y) arrays where x = cumulative population fraction,
      y = cumulative wealth fraction.
      """
      sorted_vals = np.sort(values)
      n = len(sorted_vals)
      cumsum = np.cumsum(sorted_vals)
      total = cumsum[-1]
      if total == 0:
          return np.linspace(0, 1, n), np.linspace(0, 1, n)
      y = np.concatenate([[0], cumsum / total])
      x = np.linspace(0, 1, n + 1)
      return x, y


  def standard_layout(title: str, height: int = 400, **kwargs) -> dict:
      """Return a standard plotly layout dict."""
      return dict(
          title=title,
          height=height,
          template=PLOT_TEMPLATE,
          margin=dict(l=40, r=40, t=40, b=40),
          **kwargs,
      )

================================================================================
BLOCK 3 — CREATE components/biography.py
================================================================================

Extract ALL biography-related code from app.py into this module.

CREATE D:\EXPERIMENTS\SIM\dashboard\components\biography.py:

  Extract these from the existing app.py (find and copy, keeping logic identical):
    - _get_agent_name() function
    - _bar() helper (the text progress bar helper)
    - _format_event() helper
    - _render_biography() function

  Add at top:
    import streamlit as st
    import numpy as np
    from models.agent import HERITABLE_TRAITS, Sex
    from .constants import TRAIT_ABBREV, TRAIT_DOMAINS, TRAIT_DOMAIN_COLORS

  Change _get_agent_name() and _render_biography() to accept `society` and
  `events` as explicit parameters rather than reading from outer scope.
  Signature: _render_biography(agent_id: int, society, events: list)
  Signature: _get_agent_name(agent_id: int, society, agent=None) -> str

================================================================================
BLOCK 4 — CREATE components/kpi_bar.py
================================================================================

CREATE D:\EXPERIMENTS\SIM\dashboard\components\kpi_bar.py:

  """Summary KPI metrics bar shown at the top of every run."""

  import streamlit as st
  import pandas as pd


  def render_kpi_bar(df: pd.DataFrame, is_multi_run: bool, seeds_count: int):
      """Render the 8-column KPI summary row with deltas."""
      if df is None or len(df) == 0:
          return

      final = df.iloc[-1]
      first = df.iloc[0]

      def _delta(col):
          """Compute delta from first to final year for a metric."""
          try:
              return float(final[col]) - float(first[col])
          except Exception:
              return None

      if is_multi_run:
          st.caption(f"Research Mode: {seeds_count} seeds averaged. "
                     f"Shaded bands show ±1 standard deviation.")

      c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
      c1.metric("Final Pop",    f"{int(final['population']):,}",
                delta=f"{int(final['population']) - int(first['population']):+,}")
      c2.metric("Total Births", f"{int(df['births'].sum()):,}")
      c3.metric("Total Deaths", f"{int(df['deaths'].sum()):,}")
      c4.metric("Gini",         f"{final['resource_gini']:.3f}",
                delta=f"{_delta('resource_gini'):+.3f}" if _delta('resource_gini') is not None else None)
      c5.metric("Violence",     f"{final['violence_rate']:.3f}",
                delta=f"{_delta('violence_rate'):+.3f}" if _delta('violence_rate') is not None else None)
      c6.metric("Bonded %",     f"{final['pair_bonded_pct']:.1%}",
                delta=f"{_delta('pair_bonded_pct'):+.1%}" if _delta('pair_bonded_pct') is not None else None)
      c7.metric("CSI",          f"{final['civilization_stability']:.3f}")
      c8.metric("SCI",          f"{final['social_cohesion']:.3f}")

================================================================================
BLOCK 5 — CREATE components/sidebar.py
================================================================================

CREATE D:\EXPERIMENTS\SIM\dashboard\components\sidebar.py:

  Extract ALL st.sidebar.* code from app.py into this module.
  The module exposes one function: render_sidebar() -> dict
  which returns all config values as a plain dict.

  Key changes vs original:
    1. Wrap each section (Mating, Resources, Conflict, Institutions, Mortality)
       in st.sidebar.expander(section_name, expanded=False) to reduce clutter
    2. Keep Scale and Run button always visible (not in expander)
    3. Add a "📋 Current Run" expander at bottom showing last run config
       (reads from st.session_state["config"] if present)
    4. cfg_val(key, default) takes preset as explicit arg: cfg_val(preset, key, default)

  Returns dict with all slider/selectbox/checkbox values plus:
    "run_clicked": bool
    "research_mode": bool
    "seeds_count": int

================================================================================
BLOCK 6 — CREATE components/runner.py
================================================================================

CREATE D:\EXPERIMENTS\SIM\dashboard\components\runner.py:

  Extract simulation run logic from app.py into this module.

  """Simulation execution helpers for the SIMSIV dashboard."""

  import streamlit as st
  import pandas as pd
  from config import Config
  from simulation import Simulation

  # NOTE: Do NOT call reset_id_counter() — it is a deprecated no-op from Phase E.
  # Each Simulation() instance creates its own IdCounter automatically.

  def build_config(params: dict, seed_val: int) -> Config:
      """Build a Config from sidebar params dict with a specific seed."""
      return Config(
          population_size=params["population_size"],
          years=params["years"],
          seed=seed_val,
          mating_system=params["mating_system"],
          ... (all other params from the dict)
      )

  def run_single(params: dict) -> dict:
      """Run one simulation. Returns session state dict to merge."""
      config = build_config(params, int(params["seed"]))
      sim = Simulation(config)
      years = params["years"]
      rows = []
      progress = st.progress(0, text="Initializing...")
      for yr in range(1, years + 1):
          row = sim.tick()
          rows.append(row)
          if yr % max(1, years // 100) == 0 or yr == years:
              pct = yr / years
              progress.progress(pct, text=f"Year {yr}/{years} — Pop: {row.get('population', 0)}")
      progress.empty()
      return {
          "df": pd.DataFrame(rows),
          "df_std": None,
          "is_multi_run": False,
          "seeds_count": 1,
          "living": sim.society.get_living(),
          "society": sim.society,
          "config": config,
          "events": sim.society._event_window,
          "agent_names": {},  # reset name cache on new run
      }

  def run_multi(params: dict) -> dict:
      """Run multiple seeds. Returns session state dict to merge."""
      seeds_count = params["seeds_count"]
      all_dfs = []
      last_sim = None
      progress = st.progress(0, text="Research Mode: initializing...")
      for i in range(seeds_count):
          seed_val = int(params["seed"]) + i
          progress.progress(i / seeds_count,
                            text=f"Seed {seed_val} ({i+1}/{seeds_count})...")
          config = build_config(params, seed_val)
          sim = Simulation(config)
          rows = [sim.tick() for _ in range(params["years"])]
          df_i = pd.DataFrame(rows)
          df_i["seed"] = seed_val
          all_dfs.append(df_i)
          last_sim = sim
      progress.progress(1.0, text="Aggregating...")
      combined = pd.concat(all_dfs, ignore_index=True)
      numeric_cols = [c for c in combined.select_dtypes(include="number").columns if c != "seed"]
      df_mean = combined.groupby("year")[numeric_cols].mean().reset_index()
      df_std  = combined.groupby("year")[numeric_cols].std().reset_index()
      progress.empty()
      return {
          "df": df_mean, "df_std": df_std,
          "is_multi_run": True, "seeds_count": seeds_count,
          "living": last_sim.society.get_living(),
          "society": last_sim.society,
          "config": last_sim.config,
          "events": last_sim.society._event_window,
          "agent_names": {},
      }

================================================================================
BLOCK 7 — FIX CRITICAL BUGS IN EXISTING TAB CODE
================================================================================

These bugs exist in the current app.py and must be fixed when extracting tabs:

BUG 1: Mutable default argument in _find_founder() (Dynasty tab + Science Report)
  WRONG:  def _find_founder(agent_id, visited=None, memo={}):
  RIGHT:  def _find_founder(agent_id, agents_dict, visited=None):
          if visited is None: visited = set()
  Fix in BOTH places this function appears.

BUG 2: Mutable default argument in _count_descendants() (Dynasty tab)
  WRONG:  def _count_descendants(agent_id, memo={}):
  RIGHT:  def _count_descendants(agent_id, agents_dict, memo=None):
          if memo is None: memo = {}
  Pass agents_dict explicitly everywhere this is called.

BUG 3: reset_id_counter() call in run logic
  Remove it entirely. Each Simulation() auto-creates its own IdCounter.
  The function is a no-op stub — calling it is misleading.

BUG 4: Variable name `events` shadows Python built-in
  Rename all occurrences: events → sim_events throughout the entire file.

================================================================================
BLOCK 8 — EXTRACT ALL 14 EXISTING TABS TO tabs/ MODULES
================================================================================

For each tab, create a file in dashboard/tabs/ that exports a single
render(df, df_std, living, society, config, sim_events, is_multi_run) function.

Do NOT change any chart logic during extraction. Preserve everything exactly.
Only fix the bugs listed in Block 7 as you encounter them.

Files to create:
  tabs/population.py    ← tab_pop content
  tabs/economy.py       ← tab_econ content
  tabs/violence.py      ← tab_violence content
  tabs/mating.py        ← tab_mating content
  tabs/traits.py        ← tab_traits content
  tabs/institutions.py  ← tab_inst content
  tabs/agents.py        ← tab_agents content (imports biography component)
  tabs/network.py       ← tab_network content
  tabs/events.py        ← tab_events content
  tabs/life_stories.py  ← tab_lives content (imports biography + hall_of_fame)
  tabs/dynasty.py       ← tab_dynasty content
  tabs/genome.py        ← tab_genome content
  tabs/trait_race.py    ← tab_race content
  tabs/science.py       ← tab_science content

Each file imports from:
  from dashboard.components.constants import COLORS, TRAIT_ABBREV, TRAIT_DOMAINS, TRAIT_DOMAIN_COLORS, PLOT_TEMPLATE
  from dashboard.components.charts import add_band, add_epidemic_bands, standard_layout
  from dashboard.components.biography import _render_biography, _get_agent_name  (where needed)

================================================================================
BLOCK 9 — ADD EPIDEMIC BANDS TO TIME SERIES CHARTS
================================================================================

In EACH of these tab render functions, call add_epidemic_bands(fig, df) on
every time-series figure BEFORE st.plotly_chart():

  tabs/population.py:
    - Population Over Time figure
    - Health & Age figure
    - Population Growth Rate figure

  tabs/economy.py:
    - Inequality figure
    - Resources figure

  tabs/violence.py:
    - Violence Rate figure (all of them)

  tabs/mating.py:
    - Pair Bond Stability figure

Add a small legend note: st.caption("🦠 Red bands = epidemic years") above
any chart that has epidemic bands.

================================================================================
BLOCK 10 — ADD KPI DELTAS
================================================================================

In tabs/population.py, replace the plain st.metric() calls (if any exist there)
with the new kpi_bar component that already has deltas built in (Block 4).

The kpi_bar is already complete — just make sure the slim app.py calls it:
  from dashboard.components.kpi_bar import render_kpi_bar
  render_kpi_bar(df, is_multi_run, seeds_count)

================================================================================
BLOCK 11 — NEW TAB: Beliefs (tabs/beliefs.py)
================================================================================

CREATE D:\EXPERIMENTS\SIM\dashboard\tabs\beliefs.py

This tab visualizes the 5 belief dimensions that currently have ZERO dashboard
presence. Belief columns in df follow the naming pattern avg_* and are derived
from agent.hierarchy_belief, cooperation_norm, violence_acceptability,
tradition_adherence, kinship_obligation.

Check which belief columns are actually in df before rendering (some may not be
tracked in metrics). Use: [c for c in df.columns if any(b in c for b in
['hierarchy', 'cooperation_norm', 'violence_accept', 'tradition', 'kinship'])]

If no belief columns found, show:
  st.info("Belief metrics not available. Enable beliefs_enabled=True in config.")

Otherwise render:

PANEL 1: Belief Trajectories Over Time
  Line chart showing all 5 belief dimension means over time.
  Y-axis range [-1, +1]. Add hline at y=0 (neutral).
  Add epidemic bands.
  Colors: hierarchy=#FF7043, cooperation_norm=#43A047,
          violence_acceptability=#E53935, tradition_adherence=#AB47BC,
          kinship_obligation=#FFD54F

PANEL 2: Belief Distribution (Final Year) — living agents only
  For each belief dimension, show a histogram of current agent values.
  5 small charts in a row using st.columns(5).
  Shows whether beliefs are polarized, converged, or bimodal.

PANEL 3: Belief vs Law Strength Correlation
  Scatter: x=law_strength, y=cooperation_norm (from df)
  Add trendline. Shows whether institutions drive belief change or vice versa.
  Use st.columns(2) — second chart shows violence_acceptability vs law_strength.

PANEL 4: Faction Belief Divergence (from living agents)
  For each faction in society.factions, compute mean belief values.
  Show a grouped bar chart: factions on x-axis, 5 belief dims as bar groups.
  If fewer than 2 factions, show st.info("Need multiple factions for comparison.")

PANEL 5: Belief Revolution Events
  Filter sim_events for type == "belief_revolution".
  Show as a timeline table: Year | Belief Dimension | Magnitude | Direction.
  If none: st.info("No belief revolutions detected in this run.")

================================================================================
BLOCK 12 — ENHANCE tabs/economy.py: Lorenz Curve
================================================================================

In the existing Economy tab render function, ADD a new expander after the
existing Inequality chart:

  with st.expander("Lorenz Curve — Wealth Distribution Shape", expanded=False):
    st.caption(
        "Shows HOW wealth is distributed, not just how unequal. "
        "A curve hugging the diagonal = perfect equality. "
        "A curve hugging the bottom-right = extreme concentration."
    )

    if not living:
        st.info("No living agents.")
    else:
        resources = np.array([a.current_resources for a in living])
        tools = np.array([a.current_tools for a in living])
        prestige = np.array([a.current_prestige_goods for a in living])
        total_wealth = resources + tools * 3 + prestige * 5

        from dashboard.components.charts import lorenz_curve
        x_res, y_res = lorenz_curve(resources)
        x_tot, y_tot = lorenz_curve(total_wealth)

        fig = go.Figure()
        # Equality line
        fig.add_trace(go.Scatter(x=[0,1], y=[0,1], mode="lines",
                                 line=dict(color="white", dash="dash", width=1),
                                 name="Perfect Equality", showlegend=True))
        fig.add_trace(go.Scatter(x=x_res, y=y_res, mode="lines",
                                 line=dict(color=COLORS["resources"], width=2),
                                 name="Subsistence Resources", fill="tonexty",
                                 fillcolor="rgba(255,152,0,0.1)"))
        fig.add_trace(go.Scatter(x=x_tot, y=y_tot, mode="lines",
                                 line=dict(color=COLORS["inequality"], width=2),
                                 name="Total Wealth (weighted)"))
        fig.update_layout(
            title="Lorenz Curve (Final Year)",
            xaxis_title="Cumulative Population Fraction",
            yaxis_title="Cumulative Wealth Fraction",
            height=400, template=PLOT_TEMPLATE,
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Gini from curve
        gini_approx = 1 - 2 * np.trapz(y_tot, x_tot)
        st.caption(f"Computed Gini from Lorenz curve: **{gini_approx:.3f}**")

================================================================================
BLOCK 13 — ENHANCE tabs/population.py: Survivorship Curve
================================================================================

In the existing Population tab render function, ADD a new section after the
Age Pyramid:

  st.subheader("Survivorship Curve")
  st.caption(
      "What fraction of agents born in this simulation survived to each age? "
      "Pre-industrial pattern: steep early drop (child mortality), then plateau."
  )

  all_agents = list(society.agents.values())
  if len(all_agents) < 20:
      st.info("Need more agents for survivorship analysis.")
  else:
      max_age_seen = max((a.age for a in all_agents), default=0)
      age_bins = range(0, max_age_seen + 5, 5)
      survived = []
      for age_thresh in age_bins:
          n_survived = sum(
              1 for a in all_agents
              if a.age >= age_thresh or (not a.alive and a.age >= age_thresh)
          )
          survived.append(n_survived / len(all_agents))

      fig = go.Figure()
      fig.add_trace(go.Scatter(
          x=list(age_bins), y=survived, mode="lines",
          fill="tozeroy", line=dict(color=COLORS["health"], width=2),
          name="Survivorship",
      ))
      fig.add_hline(y=0.5, line_dash="dot", line_color="white", opacity=0.4,
                    annotation_text="50% survived", annotation_position="right")
      fig.update_layout(
          title="Survivorship Curve (All Agents)",
          xaxis_title="Age", yaxis_title="Fraction Surviving",
          yaxis=dict(range=[0, 1.05]),
          height=350, template=PLOT_TEMPLATE,
          margin=dict(l=40, r=40, t=40, b=40),
      )
      add_epidemic_bands(fig, df)
      st.plotly_chart(fig, use_container_width=True)

================================================================================
BLOCK 14 — ENHANCE tabs/violence.py: Inter-Faction Violence Matrix
================================================================================

In the existing Violence tab render function, ADD a new expander:

  with st.expander("Inter-Faction Violence Matrix", expanded=False):
    st.caption("Who attacks whom? Shows whether violence is internal or inter-group.")

    # Build matrix from events
    faction_pairs = {}
    for e in sim_events:
        if e.get("type") not in ("conflict", "violence_death"):
            continue
        agent_ids = e.get("agent_ids", [])
        if len(agent_ids) < 2:
            continue
        agg_id, tgt_id = agent_ids[0], agent_ids[1]
        agg = society.get_by_id(agg_id)
        tgt = society.get_by_id(tgt_id)
        if not agg or not tgt:
            continue
        agg_f = agg.faction_id if agg.faction_id is not None else "None"
        tgt_f = tgt.faction_id if tgt.faction_id is not None else "None"
        key = (str(agg_f), str(tgt_f))
        faction_pairs[key] = faction_pairs.get(key, 0) + 1

    if not faction_pairs:
        st.info("No faction conflict data in event window.")
    else:
        factions = sorted(set(
            [k[0] for k in faction_pairs] + [k[1] for k in faction_pairs]
        ))
        n = len(factions)
        matrix = np.zeros((n, n))
        fi = {f: i for i, f in enumerate(factions)}
        for (af, tf), count in faction_pairs.items():
            matrix[fi[af], fi[tf]] += count

        fig = go.Figure(go.Heatmap(
            z=matrix, x=factions, y=factions,
            colorscale=[[0, "#000000"], [1, COLORS["violence"]]],
            colorbar=dict(title="Conflicts"),
            hovertemplate="Aggressor: %{y}<br>Target: %{x}<br>Conflicts: %{z}<extra></extra>",
        ))
        fig.update_layout(
            title="Conflict Count: Row=Aggressor, Column=Target",
            height=400, template=PLOT_TEMPLATE,
            xaxis_title="Target Faction", yaxis_title="Aggressor Faction",
            margin=dict(l=80, r=40, t=40, b=80),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Internal vs inter-group summary
        internal = sum(v for (af, tf), v in faction_pairs.items() if af == tf)
        inter = sum(v for (af, tf), v in faction_pairs.items() if af != tf)
        total = internal + inter
        if total > 0:
            c1, c2 = st.columns(2)
            c1.metric("Internal Faction Conflicts", internal, f"{internal/total:.0%}")
            c2.metric("Inter-Faction Conflicts", inter, f"{inter/total:.0%}")

================================================================================
BLOCK 15 — ENHANCE tabs/mating.py: Bond Duration Histogram
================================================================================

In the existing Mating tab render function, ADD a new expander:

  with st.expander("Bond Duration Distribution", expanded=False):
    st.caption(
        "How long do pair bonds last before dissolution? "
        "Short = fluid; long = stable partnerships."
    )

    # Extract bond durations from events
    bond_formed = {}  # bond_key → year_formed
    durations = []
    for e in sim_events:
        yr = e.get("year", 0)
        etype = e.get("type", "")
        agent_ids = e.get("agent_ids", [])
        if len(agent_ids) < 2:
            continue
        key = tuple(sorted(agent_ids[:2]))
        if etype == "bond_formed":
            bond_formed[key] = yr
        elif etype in ("bond_dissolved", "bond_broken") and key in bond_formed:
            duration = yr - bond_formed.pop(key)
            if duration > 0:
                durations.append(duration)

    if len(durations) < 5:
        st.info("Not enough bond dissolution events recorded. "
                "Bond duration data accumulates with longer runs.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Histogram(
            x=durations, nbinsx=20,
            marker_color=COLORS["mating"], opacity=0.8, name="Bond Durations"
        ))
        fig.update_layout(
            title=f"Bond Duration Histogram (n={len(durations)} bonds)",
            xaxis_title="Duration (years)", yaxis_title="Count",
            height=350, template=PLOT_TEMPLATE,
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

        median_dur = float(np.median(durations))
        mean_dur = float(np.mean(durations))
        c1, c2, c3 = st.columns(3)
        c1.metric("Median Bond Duration", f"{median_dur:.1f} yrs")
        c2.metric("Mean Bond Duration", f"{mean_dur:.1f} yrs")
        c3.metric("Bonds Tracked", len(durations))

================================================================================
BLOCK 16 — ENHANCE tabs/institutions.py: Phase Portrait
================================================================================

In the existing Institutions tab render function, ADD a new expander:

  with st.expander("Phase Portrait — Law vs Violence", expanded=False):
    st.caption(
        "System dynamics: does law strength drive violence down, or does "
        "violence drive law up? Color = simulation year. "
        "Converging spiral = stable equilibrium. Orbit = limit cycle."
    )

    if "law_strength" not in df.columns or "violence_rate" not in df.columns:
        st.info("Institutional drift must be enabled for this chart.")
    elif df["law_strength"].std() < 0.01:
        st.info("Law strength is static. Enable institutional_drift_rate > 0 to see dynamics.")
    else:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["law_strength"], y=df["violence_rate"],
            mode="markers+lines",
            marker=dict(
                color=df["year"],
                colorscale="RdYlBu_r",
                size=5,
                showscale=True,
                colorbar=dict(title="Year"),
            ),
            line=dict(color="rgba(255,255,255,0.2)", width=1),
            hovertemplate="Year %{text}<br>Law: %{x:.3f}<br>Violence: %{y:.3f}<extra></extra>",
            text=df["year"].astype(str),
        ))
        # Mark start and end
        fig.add_trace(go.Scatter(
            x=[df["law_strength"].iloc[0]], y=[df["violence_rate"].iloc[0]],
            mode="markers", marker=dict(size=12, color="lime", symbol="star"),
            name="Start",
        ))
        fig.add_trace(go.Scatter(
            x=[df["law_strength"].iloc[-1]], y=[df["violence_rate"].iloc[-1]],
            mode="markers", marker=dict(size=12, color="red", symbol="x"),
            name="End",
        ))
        fig.update_layout(
            title="Phase Portrait: Law Strength vs Violence Rate",
            xaxis_title="Law Strength", yaxis_title="Violence Rate",
            height=450, template=PLOT_TEMPLATE,
            margin=dict(l=40, r=40, t=40, b=40),
        )
        st.plotly_chart(fig, use_container_width=True)

================================================================================
BLOCK 17 — NEW TAB: Scenario Comparison (tabs/compare.py)
================================================================================

CREATE D:\EXPERIMENTS\SIM\dashboard\tabs\compare.py

This is the highest-value new feature: run two scenarios and show delta charts.

  """Scenario comparison tab — run two configs side by side."""

  import streamlit as st
  import numpy as np
  import pandas as pd
  import plotly.graph_objects as go
  from config import Config
  from simulation import Simulation
  from experiments.scenarios import SCENARIOS
  from dashboard.components.constants import COLORS, PLOT_TEMPLATE


  def render(base_params: dict):
      """
      base_params: the sidebar config dict from the current session.
      The comparison tab runs an additional scenario and diffs the results.
      """
      st.subheader("⚡ Scenario Comparison")
      st.caption(
          "Run any two scenarios back-to-back and see the deltas. "
          "Answers questions like: 'How much does monogamy reduce violence?' "
          "and 'What does a strong state do to trait evolution?'"
      )

      # ── Scenario pickers ─────────────────────────────────────────
      col1, col2 = st.columns(2)
      with col1:
          st.markdown("**Scenario A (Baseline)**")
          scenario_a = st.selectbox("Scenario A", list(SCENARIOS.keys()),
                                    index=0, key="compare_scenario_a")
      with col2:
          st.markdown("**Scenario B (Comparison)**")
          scenario_b = st.selectbox("Scenario B", list(SCENARIOS.keys()),
                                    index=min(1, len(SCENARIOS)-1),
                                    key="compare_scenario_b")

      compare_years = st.slider("Simulation years", 50, 300, 150, 10, key="compare_years")
      compare_seeds = st.slider("Seeds per scenario", 1, 5, 2, key="compare_seeds")
      compare_pop = st.slider("Population", 100, 1000, 300, 50, key="compare_pop")
      run_compare = st.button("▶ Run Comparison", type="primary", key="run_compare_btn")

      if run_compare:
          # Run both scenarios
          results = {}
          for label, scenario_name in [("A", scenario_a), ("B", scenario_b)]:
              preset = SCENARIOS[scenario_name]
              all_dfs = []
              for i in range(compare_seeds):
                  seed_val = int(base_params.get("seed", 42)) + i
                  cfg_dict = {**preset, "population_size": compare_pop,
                              "years": compare_years, "seed": seed_val}
                  cfg = Config(**{k: v for k, v in cfg_dict.items()
                                  if k in Config.__dataclass_fields__})
                  sim = Simulation(cfg)
                  rows = [sim.tick() for _ in range(compare_years)]
                  all_dfs.append(pd.DataFrame(rows))
              combined = pd.concat(all_dfs, ignore_index=True)
              numeric_cols = combined.select_dtypes(include="number").columns.tolist()
              results[label] = combined.groupby("year")[numeric_cols].mean().reset_index()

          st.session_state["compare_results"] = results
          st.session_state["compare_labels"] = (scenario_a, scenario_b)

      # ── Display results ──────────────────────────────────────────
      if "compare_results" not in st.session_state:
          st.info("Choose two scenarios above and click Run Comparison.")
          return

      results = st.session_state["compare_results"]
      label_a, label_b = st.session_state["compare_labels"]
      df_a = results.get("A")
      df_b = results.get("B")

      if df_a is None or df_b is None:
          st.warning("Results incomplete — run comparison again.")
          return

      st.markdown(f"**Results: {label_a} vs {label_b}**")
      st.markdown("---")

      # ── Summary delta table ──────────────────────────────────────
      KEY_METRICS = [
          ("population",       "Final Population"),
          ("resource_gini",    "Resource Gini"),
          ("violence_rate",    "Violence Rate"),
          ("pair_bonded_pct",  "Bonded %"),
          ("avg_cooperation",  "Avg Cooperation"),
          ("avg_aggression",   "Avg Aggression"),
          ("avg_lifetime_births", "Lifetime Births"),
          ("avg_intelligence", "Avg Intelligence"),
          ("law_strength",     "Law Strength"),
          ("avg_lifespan",     "Avg Lifespan"),
      ]

      rows = []
      for col, label in KEY_METRICS:
          if col not in df_a.columns or col not in df_b.columns:
              continue
          val_a = float(df_a[col].iloc[-1])
          val_b = float(df_b[col].iloc[-1])
          delta = val_b - val_a
          pct = (delta / val_a * 100) if val_a != 0 else 0
          rows.append({
              "Metric": label,
              label_a: f"{val_a:.3f}",
              label_b: f"{val_b:.3f}",
              "Delta (B-A)": f"{delta:+.3f}",
              "Change %": f"{pct:+.1f}%",
          })

      if rows:
          st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

      # ── Side-by-side time series for key metrics ─────────────────
      st.markdown("### Time Series Comparison")

      CHART_METRICS = [
          ("population",      "Population",         COLORS["population"]),
          ("violence_rate",   "Violence Rate",      COLORS["violence"]),
          ("resource_gini",   "Resource Gini",      COLORS["inequality"]),
          ("avg_cooperation", "Avg Cooperation",    COLORS["cooperation"]),
          ("avg_aggression",  "Avg Aggression",     COLORS["violence"]),
          ("law_strength",    "Law Strength",       COLORS["law"]),
      ]

      for i in range(0, len(CHART_METRICS), 2):
          col1, col2 = st.columns(2)
          for j, colobj in enumerate([col1, col2]):
              if i + j >= len(CHART_METRICS):
                  break
              metric_col, metric_label, color = CHART_METRICS[i + j]
              with colobj:
                  if metric_col not in df_a.columns:
                      continue
                  fig = go.Figure()
                  fig.add_trace(go.Scatter(
                      x=df_a["year"], y=df_a[metric_col],
                      name=label_a, line=dict(color=color, width=2),
                  ))
                  fig.add_trace(go.Scatter(
                      x=df_b["year"], y=df_b[metric_col],
                      name=label_b, line=dict(color="#FFFFFF", width=2, dash="dash"),
                  ))
                  fig.update_layout(
                      title=metric_label, height=280, template=PLOT_TEMPLATE,
                      margin=dict(l=40, r=20, t=40, b=40),
                      legend=dict(orientation="h", yanchor="bottom", y=1.02),
                  )
                  st.plotly_chart(fig, use_container_width=True)

      # ── Delta chart — net effect of switching from A to B ───────
      st.markdown("### Net Effect of Scenario B vs A")
      st.caption("Positive = B produces more of this. Negative = B produces less.")

      delta_rows = []
      for col, label in KEY_METRICS:
          if col not in df_a.columns or col not in df_b.columns:
              continue
          val_a = float(df_a[col].iloc[-1])
          val_b = float(df_b[col].iloc[-1])
          if val_a == 0:
              continue
          pct = (val_b - val_a) / abs(val_a) * 100
          delta_rows.append({"Metric": label, "Change %": pct})

      if delta_rows:
          ddf = pd.DataFrame(delta_rows).sort_values("Change %")
          colors_bar = [COLORS["cooperation"] if v >= 0 else COLORS["violence"]
                        for v in ddf["Change %"]]
          fig = go.Figure(go.Bar(
              x=ddf["Change %"], y=ddf["Metric"],
              orientation="h", marker_color=colors_bar,
              text=[f"{v:+.1f}%" for v in ddf["Change %"]],
              textposition="outside",
          ))
          fig.add_vline(x=0, line_color="white", line_width=1)
          fig.update_layout(
              title=f"% Change from {label_a} → {label_b}",
              xaxis_title="% Change", height=400, template=PLOT_TEMPLATE,
              margin=dict(l=120, r=60, t=40, b=40),
          )
          st.plotly_chart(fig, use_container_width=True)

================================================================================
BLOCK 18 — NEW FEATURE: Export Panel in Sidebar
================================================================================

In dashboard/components/sidebar.py, add an export section at the BOTTOM of
the sidebar, below all sliders. Show it only when there is session state data.

  if "df" in st.session_state and st.session_state["df"] is not None:
      st.sidebar.markdown("---")
      st.sidebar.markdown("### 📥 Export")
      df_export = st.session_state["df"]

      # Metrics CSV
      csv_bytes = df_export.to_csv(index=False).encode("utf-8")
      st.sidebar.download_button(
          "Download metrics.csv", csv_bytes,
          file_name="simsiv_metrics.csv", mime="text/csv",
      )

      # Config YAML
      cfg = st.session_state.get("config")
      if cfg:
          import yaml
          from dataclasses import asdict
          yaml_bytes = yaml.dump(asdict(cfg), default_flow_style=False).encode("utf-8")
          st.sidebar.download_button(
              "Download config.yaml", yaml_bytes,
              file_name="simsiv_config.yaml", mime="text/yaml",
          )

      # Final agents CSV — living agents only
      society = st.session_state.get("society")
      if society:
          living = society.get_living()
          from models.agent import HERITABLE_TRAITS
          agent_rows = []
          for a in living:
              row = {"id": a.id, "sex": a.sex.value, "age": a.age,
                     "generation": a.generation, "health": round(a.health, 3),
                     "resources": round(a.current_resources, 2),
                     "prestige": round(a.prestige_score, 3),
                     "dominance": round(a.dominance_score, 3),
                     "offspring": len(a.offspring_ids),
                     "faction": a.faction_id}
              for t in HERITABLE_TRAITS:
                  row[t] = round(getattr(a, t, 0.5), 4)
              agent_rows.append(row)
          if agent_rows:
              import pandas as pd
              agents_csv = pd.DataFrame(agent_rows).to_csv(index=False).encode("utf-8")
              st.sidebar.download_button(
                  "Download agents.csv", agents_csv,
                  file_name="simsiv_agents.csv", mime="text/csv",
              )

================================================================================
BLOCK 19 — REWRITE app.py AS SLIM ROUTER
================================================================================

Rewrite D:\EXPERIMENTS\SIM\dashboard\app.py as a clean ~100-line router.

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

  # Tab modules
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
      with st.spinner("Running simulation..."):
          if params["research_mode"]:
              state = run_multi(params)
          else:
              state = run_single(params)
      for k, v in state.items():
          st.session_state[k] = v
      st.session_state["hof_data"] = None  # invalidate hall of fame cache

  if "df" not in st.session_state:
      st.info("Configure parameters in the sidebar and click **▶ Run Simulation** to begin.")
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
  with tabs[15]: tab_compare.render(params)

================================================================================
BLOCK 20 — POLISH: TAB SIDEBAR EXPANDERS + CURRENT RUN DISPLAY
================================================================================

In dashboard/components/sidebar.py, wrap these sections in expanders:

  with st.sidebar.expander("🧬 Mating", expanded=False):
      # all mating sliders

  with st.sidebar.expander("🍎 Reproduction", expanded=False):
      # all reproduction sliders

  with st.sidebar.expander("💰 Resources", expanded=False):
      # all resource sliders

  with st.sidebar.expander("⚔️ Conflict", expanded=False):
      # all conflict sliders

  with st.sidebar.expander("⚖️ Institutions", expanded=False):
      # all institution sliders

  with st.sidebar.expander("💀 Mortality", expanded=False):
      # all mortality sliders

  with st.sidebar.expander("🔬 Research Mode", expanded=False):
      # research mode toggle + seeds slider

Keep ALWAYS VISIBLE (not in expander):
  - Scenario Presets selector
  - Scale sliders (Population, Years, Seed)
  - ▶ Run Simulation button
  - 📥 Export section

Also add at very bottom of sidebar:
  if "config" in st.session_state:
      with st.sidebar.expander("📋 Last Run Config", expanded=False):
          cfg = st.session_state["config"]
          st.sidebar.caption(f"Mating: {cfg.mating_system}")
          st.sidebar.caption(f"Pop: {cfg.population_size} | Years: {cfg.years} | Seed: {cfg.seed}")
          st.sidebar.caption(f"Law: {cfg.law_strength:.2f} | Resource: {cfg.resource_abundance:.2f}")
          st.sidebar.caption(f"Conception: {cfg.base_conception_chance:.2f} | Mutation: {cfg.mutation_sigma:.3f}")

================================================================================
FINAL VERIFICATION CHECKLIST
================================================================================

After completing ALL blocks:

  [ ] streamlit run dashboard/app.py  — loads without import errors
  [ ] Run a simulation (any scenario, 100yr, 300 pop)
  [ ] All 16 tabs render without errors
  [ ] 📊 Population tab: epidemic bands on charts, survivorship curve present
  [ ] 💰 Economy tab: Lorenz curve expander works
  [ ] ⚔️ Violence tab: inter-faction violence matrix renders
  [ ] 💕 Mating tab: bond duration histogram expander works
  [ ] ⚖️ Institutions tab: phase portrait renders (try with drift_rate > 0)
  [ ] 💡 Beliefs tab: renders info message if no belief columns, or charts if present
  [ ] 🏆 Hall of Fame tab: all 14 cards attempt to render
  [ ] ⚡ Compare tab: scenario picker visible, run button works, delta table renders
  [ ] KPI bar shows deltas (▲/▼ arrows)
  [ ] Sidebar sections are collapsed by default (expanders)
  [ ] 📥 Export section visible after run, download buttons work
  [ ] 📋 Last Run Config expander shows correct values
  [ ] No mutable default argument bugs (memo={}) anywhere in codebase
  [ ] reset_id_counter() call removed from runner
  [ ] `events` renamed to `sim_events` throughout
  [ ] All figures use COLORS dict, not hardcoded hex strings

================================================================================
WHAT NOT TO CHANGE
================================================================================

  - models/, engines/, config.py, simulation.py — no simulation logic changes
  - metrics/collectors.py — no metric column name changes
  - autosim/ — no autosim changes
  - tests/ — do not break existing tests
  - Any existing chart logic — preserve all visualizations exactly during refactor

================================================================================
END OF PHASE G DASHBOARD OVERHAUL PROMPT
================================================================================
