"""Mating tab — pair bonds, reproductive skew, fidelity, bond duration."""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import add_band, standard_layout


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    def _std(col):
        return df_std[col] if (is_multi_run and df_std is not None and col in df_std.columns) else None

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["pair_bonded_pct"],
            name="Pair Bonded %", line=dict(color=COLORS["mating"])))
        add_band(fig, df["year"], df["pair_bonded_pct"],
                 _std("pair_bonded_pct"), COLORS["mating"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["unmated_male_pct"],
            name="Unmated Males %", line=dict(color=COLORS["males"], dash="dash")))
        add_band(fig, df["year"], df["unmated_male_pct"],
                 _std("unmated_male_pct"), COLORS["males"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["unmated_female_pct"],
            name="Unmated Females %", line=dict(color=COLORS["females"], dash="dot")))
        fig.update_layout(**standard_layout("Mating Market", 400))
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["reproductive_skew"],
            name="Reproductive Skew", line=dict(color="#9C27B0")))
        add_band(fig, df["year"], df["reproductive_skew"],
                 _std("reproductive_skew"), "#9C27B0")
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["mating_inequality"],
            name="Mating Inequality (Male)",
            line=dict(color="#FF5722", dash="dash")))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["elite_repro_advantage"],
            name="Elite Repro Advantage",
            line=dict(color=COLORS["prestige"], dash="dot"),
            yaxis="y2"))
        fig.update_layout(
            **standard_layout("Reproductive Inequality", 400),
            yaxis2=dict(title="Elite Advantage", overlaying="y", side="right"))
        st.plotly_chart(fig, width="stretch")

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["bonds_formed"], name="Bonds Formed",
            line=dict(color=COLORS["births"])))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["bonds_dissolved"], name="Bonds Dissolved",
            line=dict(color=COLORS["deaths"], dash="dash")))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["mating_contests"], name="Mating Contests",
            line=dict(color="#FFC107", dash="dot")))
        fig.update_layout(**standard_layout("Bond Dynamics", 350))
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["avg_bond_strength"],
            name="Avg Bond Strength", line=dict(color=COLORS["mating"])))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["infidelity_rate"],
            name="Infidelity Rate", line=dict(color=COLORS["resources"], dash="dash")))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["paternity_uncertainty"],
            name="Paternity Uncertainty", line=dict(color="#9575CD", dash="dot")))
        fig.update_layout(**standard_layout("Fidelity & Bonds", 350))
        st.plotly_chart(fig, width="stretch")

    # ── Child survival and household ──────────────────────────────
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["child_survival_rate"],
            name="Child Survival Rate", line=dict(color=COLORS["health"])))
        add_band(fig, df["year"], df["child_survival_rate"],
                 _std("child_survival_rate"), COLORS["health"])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["avg_maternal_health"],
            name="Maternal Health", line=dict(color=COLORS["females"], dash="dash")))
        fig.update_layout(**standard_layout("Child Survival & Maternal Health", 300))
        st.plotly_chart(fig, width="stretch")

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["childhood_deaths"],
            name="Childhood Deaths", line=dict(color="#D32F2F")))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["orphan_deaths"],
            name="Orphan Deaths", line=dict(color="#FF8A65", dash="dash")))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["orphan_count"],
            name="Orphans", line=dict(color="#FFCA28", dash="dot")))
        fig.update_layout(**standard_layout("Childhood Mortality & Orphans", 300))
        st.plotly_chart(fig, width="stretch")

    # ── Bond Duration Histogram ───────────────────────────────────
    with st.expander("Bond Duration Histogram"):
        # Estimate bond durations from bond-dissolution events
        dissolution_events = [
            e for e in sim_events
            if e.get("type") in ("bond_dissolved", "bond_broken", "divorce",
                                  "pair_bond_dissolved")
        ]
        durations = []
        for e in dissolution_events:
            dur = e.get("duration") or e.get("bond_duration") or e.get("years_bonded")
            if dur is not None:
                durations.append(float(dur))

        # Fallback: compute from living bonded agents using current year
        if not durations and living:
            current_year = int(df["year"].iloc[-1]) if len(df) > 0 else 0
            for a in living:
                if hasattr(a, "partner_ids") and a.partner_ids:
                    # Use bond strength as a proxy — stronger bonds tend to be older
                    for pid in a.partner_ids:
                        strength = a.pair_bond_strengths.get(pid, 0.0)
                        # Estimate: each year of bonding adds ~0.05 strength (rough heuristic)
                        if strength > 0:
                            durations.append(strength * 20.0)

        if durations:
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=durations, nbinsx=30,
                marker_color=COLORS["mating"],
                opacity=0.85))
            fig.update_layout(
                **standard_layout("Bond Duration Distribution", 300),
                xaxis_title="Duration (years)",
                yaxis_title="Count")
            st.plotly_chart(fig, width="stretch")
            st.caption(f"Based on {len(durations):,} bond observations. "
                       f"Mean duration: {np.mean(durations):.1f} years, "
                       f"Median: {np.median(durations):.1f} years.")
        else:
            st.info("No bond duration data available yet. "
                    "Run more years for dissolution events to accumulate.")
