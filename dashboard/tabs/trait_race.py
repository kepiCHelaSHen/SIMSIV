"""Trait Race tab — Animated bar chart race and key trait trajectories."""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from models.agent import HERITABLE_TRAITS
from dashboard.components.constants import (
    TRAIT_ABBREV, TRAIT_DOMAINS, TRAIT_DOMAIN_COLORS,
)
from dashboard.components.charts import add_band


# ── Domain sets for domain classification ───────────────────────────
_physical = TRAIT_DOMAINS["physical"]
_cognitive = TRAIT_DOMAINS["cognitive"]
_temporal = TRAIT_DOMAINS["temporal"]
_personality = TRAIT_DOMAINS["personality"]
_social = TRAIT_DOMAINS["social"]
_reproductive = TRAIT_DOMAINS["reproductive"]
_psychopath = TRAIT_DOMAINS["psychopathology"]


# ── Main render ─────────────────────────────────────────────────────

def render(df, df_std, living, society, config, sim_events, is_multi_run, seeds_count=1, **kwargs):
    """Render the Trait Race tab."""
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
        return

    st.subheader("Trait Race \u2014 Animated Bar Chart")

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
            title="Trait Race \u2014 Mean Values Over Time",
        )
        fig.update_layout(
            height=800, template="plotly_dark",
            margin=dict(l=120, r=40, t=60, b=40),
            yaxis=dict(categoryorder="total ascending"),
        )
        st.plotly_chart(fig, use_container_width=True)

    # Static multi-line chart for 6 key traits with bands
    st.subheader("Key Trait Trajectories (\u00b11\u03c3)")
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
        title="Key Trait Trajectories with \u00b11\u03c3 Bands", height=450,
        template="plotly_dark", margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig, use_container_width=True)
