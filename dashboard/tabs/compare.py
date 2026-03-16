"""Scenario comparison tab — run two configs side by side."""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from config import Config
from simulation import Simulation
from experiments.scenarios import SCENARIOS
from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import standard_layout


def render(df=None, df_std=None, living=None, society=None, config=None,
           sim_events=None, is_multi_run=False, base_params=None, **kwargs):
    st.subheader("Scenario Comparison")
    st.caption("Run any two scenarios back-to-back and see the deltas.")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Scenario A (Baseline)**")
        scenario_a = st.selectbox("Scenario A", list(SCENARIOS.keys()), index=0, key="cmp_a")
    with col2:
        st.markdown("**Scenario B (Comparison)**")
        scenario_b = st.selectbox("Scenario B", list(SCENARIOS.keys()),
                                  index=min(1, len(SCENARIOS)-1), key="cmp_b")

    compare_years = st.slider("Years", 50, 300, 150, 10, key="cmp_years")
    compare_seeds = st.slider("Seeds", 1, 5, 2, key="cmp_seeds")
    compare_pop = st.slider("Population", 100, 1000, 300, 50, key="cmp_pop")
    run_compare = st.button("Run Comparison", type="primary", key="cmp_run")

    if run_compare:
        results = {}
        progress = st.progress(0, text="Running comparisons...")
        total = compare_seeds * 2
        step = 0
        for label, scenario_name in [("A", scenario_a), ("B", scenario_b)]:
            preset = SCENARIOS[scenario_name]
            all_dfs = []
            for i in range(compare_seeds):
                seed_val = 42 + i
                step += 1
                progress.progress(step / total, text=f"{scenario_name} seed {seed_val}...")
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
        progress.empty()
        st.session_state["compare_results"] = results
        st.session_state["compare_labels"] = (scenario_a, scenario_b)

    if "compare_results" not in st.session_state:
        st.info("Choose two scenarios above and click Run Comparison.")
        return

    results = st.session_state["compare_results"]
    label_a, label_b = st.session_state["compare_labels"]
    df_a, df_b = results.get("A"), results.get("B")
    if df_a is None or df_b is None:
        return

    st.markdown(f"**{label_a} vs {label_b}**")
    st.markdown("---")

    # Summary delta table
    KEY_METRICS = [
        ("population", "Final Population"), ("resource_gini", "Resource Gini"),
        ("violence_rate", "Violence Rate"), ("pair_bonded_pct", "Bonded %"),
        ("avg_cooperation", "Avg Cooperation"), ("avg_aggression", "Avg Aggression"),
        ("avg_lifetime_births", "Lifetime Births"), ("avg_intelligence", "Avg Intelligence"),
        ("law_strength", "Law Strength"), ("avg_lifespan", "Avg Lifespan"),
    ]

    rows = []
    for col, label in KEY_METRICS:
        if col not in df_a.columns or col not in df_b.columns:
            continue
        va, vb = float(df_a[col].iloc[-1]), float(df_b[col].iloc[-1])
        delta = vb - va
        pct = (delta / va * 100) if va != 0 else 0
        rows.append({"Metric": label, label_a: f"{va:.3f}", label_b: f"{vb:.3f}",
                      "Delta": f"{delta:+.3f}", "Change %": f"{pct:+.1f}%"})
    if rows:
        st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True)

    # Side-by-side charts
    st.markdown("### Time Series Comparison")
    CHART_METRICS = [
        ("population", "Population", COLORS["population"]),
        ("violence_rate", "Violence Rate", COLORS["violence"]),
        ("resource_gini", "Resource Gini", COLORS["inequality"]),
        ("avg_cooperation", "Cooperation", COLORS["cooperation"]),
        ("avg_aggression", "Aggression", COLORS["violence"]),
        ("law_strength", "Law Strength", COLORS["law"]),
    ]

    for i in range(0, len(CHART_METRICS), 2):
        col1, col2 = st.columns(2)
        for j, colobj in enumerate([col1, col2]):
            if i + j >= len(CHART_METRICS):
                break
            mc, ml, color = CHART_METRICS[i + j]
            with colobj:
                if mc not in df_a.columns:
                    continue
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=df_a["year"], y=df_a[mc],
                                         name=label_a, line=dict(color=color, width=2)))
                fig.add_trace(go.Scatter(x=df_b["year"], y=df_b[mc],
                                         name=label_b, line=dict(color="#FFFFFF", width=2, dash="dash")))
                fig.update_layout(**standard_layout(ml, 280),
                                  legend=dict(orientation="h", yanchor="bottom", y=1.02))
                st.plotly_chart(fig, width="stretch")

    # Delta bar chart
    st.markdown("### Net Effect (B vs A)")
    delta_rows = []
    for col, label in KEY_METRICS:
        if col not in df_a.columns or col not in df_b.columns:
            continue
        va, vb = float(df_a[col].iloc[-1]), float(df_b[col].iloc[-1])
        if va == 0:
            continue
        delta_rows.append({"Metric": label, "Change %": (vb - va) / abs(va) * 100})
    if delta_rows:
        ddf = pd.DataFrame(delta_rows).sort_values("Change %")
        bar_colors = [COLORS["cooperation"] if v >= 0 else COLORS["violence"] for v in ddf["Change %"]]
        fig = go.Figure(go.Bar(x=ddf["Change %"], y=ddf["Metric"], orientation="h",
                                marker_color=bar_colors,
                                text=[f"{v:+.1f}%" for v in ddf["Change %"]], textposition="outside"))
        fig.add_vline(x=0, line_color="white", line_width=1)
        fig.update_layout(**standard_layout(f"% Change: {label_a} -> {label_b}", 400),
                          margin=dict(l=120, r=60, t=40, b=40))
        st.plotly_chart(fig, width="stretch")
