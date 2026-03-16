"""Beliefs tab — visualizes 5 cultural belief dimensions."""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import add_epidemic_bands, standard_layout


BELIEF_COLS = {
    "avg_hierarchy_belief": ("Hierarchy", "#FF7043"),
    "avg_cooperation_norm": ("Cooperation Norm", "#43A047"),
    "avg_violence_acceptability": ("Violence Accept.", "#E53935"),
    "avg_tradition_adherence": ("Tradition", "#AB47BC"),
    "avg_kinship_obligation": ("Kinship", "#FFD54F"),
}


def render(df, df_std, living, society, config, sim_events, is_multi_run, **kwargs):
    st.subheader("Cultural Beliefs")

    available = [c for c in BELIEF_COLS if c in df.columns]
    if not available:
        st.info("Belief metrics not available. Enable beliefs_enabled=True in config.")
        return

    # Panel 1: Trajectories
    fig = go.Figure()
    for col in available:
        label, color = BELIEF_COLS[col]
        fig.add_trace(go.Scatter(x=df["year"], y=df[col], name=label,
                                 line=dict(color=color, width=2)))
    fig.add_hline(y=0, line_dash="dot", line_color="white", opacity=0.4)
    fig.update_layout(**standard_layout("Belief Trajectories Over Time", 400),
                      yaxis=dict(range=[-1.05, 1.05]), yaxis_title="Belief Value")
    add_epidemic_bands(fig, df)
    st.plotly_chart(fig, width="stretch")

    # Panel 2: Distribution (final year)
    st.subheader("Belief Distribution (Living Agents)")
    if living:
        belief_fields = ["hierarchy_belief", "cooperation_norm", "violence_acceptability",
                         "tradition_adherence", "kinship_obligation"]
        cols = st.columns(min(5, len(belief_fields)))
        for i, bf in enumerate(belief_fields):
            with cols[i % 5]:
                vals = [getattr(a, bf, 0.0) for a in living]
                fig = go.Figure()
                fig.add_trace(go.Histogram(x=vals, nbinsx=20,
                                           marker_color=list(BELIEF_COLS.values())[i][1]))
                fig.update_layout(title=bf.replace("_", " ").title()[:15], height=200,
                                  template=PLOT_TEMPLATE, margin=dict(l=20, r=20, t=30, b=20),
                                  xaxis=dict(range=[-1, 1]))
                st.plotly_chart(fig, width="stretch")

    # Panel 3: Belief vs Law
    st.subheader("Beliefs vs Institutions")
    if "law_strength" in df.columns and "avg_cooperation_norm" in df.columns:
        col1, col2 = st.columns(2)
        for colobj, y_col, title in [(col1, "avg_cooperation_norm", "Coop Norm vs Law"),
                                      (col2, "avg_violence_acceptability", "Violence Accept. vs Law")]:
            with colobj:
                if y_col not in df.columns:
                    continue
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=df["law_strength"], y=df[y_col], mode="markers",
                    marker=dict(color=df["year"], colorscale="RdYlBu_r", size=5,
                                showscale=(y_col == "avg_cooperation_norm"),
                                colorbar=dict(title="Year"))))
                if df["law_strength"].std() > 0.01:
                    z = np.polyfit(df["law_strength"], df[y_col], 1)
                    p = np.poly1d(z)
                    x_line = np.linspace(df["law_strength"].min(), df["law_strength"].max(), 50)
                    fig.add_trace(go.Scatter(x=x_line, y=p(x_line), mode="lines",
                                             line=dict(color="white", dash="dash"), showlegend=False))
                fig.update_layout(**standard_layout(title, 300), xaxis_title="Law Strength")
                st.plotly_chart(fig, width="stretch")

    # Panel 4: Faction belief divergence
    if living:
        with st.expander("Faction Belief Divergence", expanded=False):
            faction_ids = sorted(set(a.faction_id for a in living if a.faction_id is not None))
            if len(faction_ids) < 2:
                st.info("Need multiple factions for comparison.")
            else:
                belief_fields = ["hierarchy_belief", "cooperation_norm", "violence_acceptability",
                                 "tradition_adherence", "kinship_obligation"]
                rows = []
                for fid in faction_ids[:10]:
                    members = [a for a in living if a.faction_id == fid]
                    row = {"Faction": str(fid)}
                    for bf in belief_fields:
                        row[bf.replace("_", " ").title()] = float(np.mean([getattr(a, bf, 0) for a in members]))
                    rows.append(row)
                bdf = pd.DataFrame(rows)
                fig = go.Figure()
                for i, bf in enumerate(belief_fields):
                    label = bf.replace("_", " ").title()
                    if label in bdf.columns:
                        fig.add_trace(go.Bar(x=bdf["Faction"], y=bdf[label], name=label[:12],
                                             marker_color=list(BELIEF_COLS.values())[i][1]))
                fig.update_layout(**standard_layout("Mean Beliefs by Faction", 400),
                                  barmode="group", xaxis_title="Faction ID")
                st.plotly_chart(fig, width="stretch")

    # Panel 5: Revolution events
    with st.expander("Belief Revolution Events", expanded=False):
        revolutions = [e for e in sim_events if e.get("type") == "belief_revolution"]
        if not revolutions:
            st.info("No belief revolutions detected in this run.")
        else:
            rev_df = pd.DataFrame(revolutions)
            st.dataframe(rev_df, width="stretch")
