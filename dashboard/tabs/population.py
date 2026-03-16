"""Population tab — demographics, age pyramid, survivorship, growth."""

import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from models.agent import Sex
from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import add_band, add_epidemic_bands, standard_layout


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    def _std(col):
        return df_std[col] if (is_multi_run and df_std is not None and col in df_std.columns) else None

    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["population"], name="Population",
            fill="tozeroy", line=dict(color=COLORS["population"])), secondary_y=False)
        add_band(fig, df["year"], df["population"], _std("population"),
                 COLORS["population"], secondary_y=False)
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["births"], name="Births",
            line=dict(color=COLORS["births"], dash="dot")), secondary_y=True)
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["deaths"], name="Deaths",
            line=dict(color=COLORS["deaths"], dash="dot")), secondary_y=True)
        fig.update_layout(**standard_layout("Population Over Time", 400))
        fig.update_yaxes(title_text="Population", secondary_y=False)
        fig.update_yaxes(title_text="Births / Deaths per Year", secondary_y=True)
        add_epidemic_bands(fig, df)
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["males"], name="Males",
            line=dict(color=COLORS["males"])))
        add_band(fig, df["year"], df["males"], _std("males"), COLORS["males"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["females"], name="Females",
            line=dict(color=COLORS["females"])))
        add_band(fig, df["year"], df["females"], _std("females"), COLORS["females"])
        if "children_count" in df.columns:
            fig.add_trace(go.Scatter(
                x=df["year"], y=df["children_count"], name="Children (<15)",
                line=dict(color=COLORS["children"], dash="dash")))
        fig.update_layout(**standard_layout("Demographics", 400))
        st.plotly_chart(fig, width="stretch")

    # ── Age pyramid ───────────────────────────────────────────────
    st.subheader("Age & Sex Distribution (Final Year)")
    if living:
        ages_m = [a.age for a in living if a.sex == Sex.MALE]
        ages_f = [a.age for a in living if a.sex == Sex.FEMALE]
        max_age = max(max(ages_m, default=0), max(ages_f, default=0))
        bins = list(range(0, max_age + 10, 5))

        hist_m = np.histogram(ages_m, bins=bins)[0]
        hist_f = np.histogram(ages_f, bins=bins)[0]
        labels = [f"{bins[i]}-{bins[i+1]}" for i in range(len(bins) - 1)]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=labels, x=-hist_m, orientation="h", name="Males",
            marker_color=COLORS["males"], text=hist_m, textposition="auto"))
        fig.add_trace(go.Bar(
            y=labels, x=hist_f, orientation="h", name="Females",
            marker_color=COLORS["females"], text=hist_f, textposition="auto"))
        fig.update_layout(
            **standard_layout("Age Pyramid", 450),
            barmode="overlay",
            xaxis=dict(title="Count", tickvals=[]),
            yaxis=dict(title="Age Group"))
        st.plotly_chart(fig, width="stretch")

    # ── Survivorship curve ────────────────────────────────────────
    st.subheader("Survivorship Curve")
    st.caption("What fraction of agents survived to each age? Pre-industrial: steep early drop.")
    all_agents = list(society.agents.values())
    if len(all_agents) >= 20:
        max_age_seen = max((a.age for a in all_agents), default=0)
        age_bins = list(range(0, max_age_seen + 5, 5))
        survived = [sum(1 for a in all_agents if a.age >= thresh) / len(all_agents)
                    for thresh in age_bins]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=age_bins, y=survived, mode="lines", fill="tozeroy",
            line=dict(color=COLORS["health"], width=2), name="Survivorship"))
        fig.add_hline(y=0.5, line_dash="dot", line_color="white", opacity=0.4,
                      annotation_text="50% survived", annotation_position="right")
        fig.update_layout(
            **standard_layout("Survivorship Curve", 350),
            xaxis_title="Age", yaxis_title="Fraction Surviving",
            yaxis=dict(range=[0, 1.05]))
        add_epidemic_bands(fig, df)
        st.plotly_chart(fig, width="stretch")

    # ── Growth rate & health ──────────────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["pop_growth_rate"],
            line=dict(color=COLORS["resources"]), fill="tozeroy"))
        add_band(fig, df["year"], df["pop_growth_rate"],
                 _std("pop_growth_rate"), COLORS["resources"])
        fig.add_hline(y=0, line_dash="dash", line_color="white", opacity=0.5)
        fig.update_layout(**standard_layout("Population Growth Rate", 300))
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["avg_age"], name="Avg Age",
            line=dict(color=COLORS["age"])))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["avg_health"], name="Avg Health",
            line=dict(color=COLORS["health"])))
        add_band(fig, df["year"], df["avg_health"],
                 _std("avg_health"), COLORS["health"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["avg_lifespan"], name="Avg Lifespan (at death)",
            line=dict(color="#FFEE58", dash="dot")))
        fig.update_layout(**standard_layout("Health & Age", 300))
        add_epidemic_bands(fig, df)
        st.plotly_chart(fig, width="stretch")
