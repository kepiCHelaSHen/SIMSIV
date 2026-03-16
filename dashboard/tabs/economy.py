"""Economy tab — inequality, resources, cooperation, Lorenz curve."""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import add_band, standard_layout, lorenz_curve


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    def _std(col):
        return df_std[col] if (is_multi_run and df_std is not None and col in df_std.columns) else None

    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["resource_gini"], name="Resource Gini",
            line=dict(color=COLORS["inequality"])), secondary_y=False)
        add_band(fig, df["year"], df["resource_gini"],
                 _std("resource_gini"), COLORS["inequality"], secondary_y=False)
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["status_gini"], name="Status Gini",
            line=dict(color=COLORS["status"], dash="dash")), secondary_y=False)
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["resource_top10_share"],
            name="Top 10% Share", line=dict(color=COLORS["children"], dash="dot")),
            secondary_y=True)
        fig.update_layout(**standard_layout("Inequality", 400))
        fig.update_yaxes(title_text="Gini", secondary_y=False)
        fig.update_yaxes(title_text="Top 10% Share", secondary_y=True)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["avg_resources"], name="Avg Resources",
            line=dict(color=COLORS["births"])))
        add_band(fig, df["year"], df["avg_resources"],
                 _std("avg_resources"), COLORS["births"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["avg_status"], name="Avg Status",
            line=dict(color=COLORS["population"])))
        fig.update_layout(**standard_layout("Average Resources & Status", 400))
        st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["cooperation_network_size"],
            name="Avg Network Size", line=dict(color="#26C6DA")))
        add_band(fig, df["year"], df["cooperation_network_size"],
                 _std("cooperation_network_size"), "#26C6DA")
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["resource_transfers"],
            name="Transfer Events", line=dict(color="#9CCC65", dash="dot")))
        fig.update_layout(**standard_layout("Cooperation Networks", 350))
        st.plotly_chart(fig, width="stretch")

    with col2:
        # Resource distribution of living agents
        if living:
            resources = [a.current_resources for a in living]
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=resources, nbinsx=50, marker_color=COLORS["inequality"]))
            fig.update_layout(
                **standard_layout("Resource Distribution (Final Year)", 350),
                xaxis_title="Resources", yaxis_title="Agents")
            st.plotly_chart(fig, width="stretch")

    with st.expander("Scarcity Events"):
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["scarcity"], name="Scarcity Level",
            fill="tozeroy", line=dict(color=COLORS["violence"])))
        fig.update_layout(**standard_layout("Environmental Scarcity", 250))
        st.plotly_chart(fig, width="stretch")

    # ── Lorenz curve ──────────────────────────────────────────────
    with st.expander("Lorenz Curve (Final Year)"):
        if living:
            resources = np.array([a.current_resources for a in living])
            lx, ly = lorenz_curve(resources)
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=lx, y=ly, mode="lines",
                line=dict(color=COLORS["inequality"], width=2),
                name="Lorenz Curve"))
            fig.add_trace(go.Scatter(
                x=[0, 1], y=[0, 1], mode="lines",
                line=dict(color=COLORS["neutral"], dash="dash", width=1),
                name="Perfect Equality"))
            fig.update_layout(
                **standard_layout("Lorenz Curve — Resource Distribution", 350),
                xaxis_title="Cumulative Share of Agents",
                yaxis_title="Cumulative Share of Resources",
                xaxis=dict(range=[0, 1]),
                yaxis=dict(range=[0, 1]))
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No living agents to compute Lorenz curve.")
