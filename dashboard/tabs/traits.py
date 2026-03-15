"""SIMSIV Dashboard — Trait Evolution tab."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from dashboard.components.constants import (
    COLORS, TRAIT_ABBREV, TRAIT_DOMAINS, TRAIT_DOMAIN_COLORS, PLOT_TEMPLATE,
)
from dashboard.components.charts import add_band, standard_layout
from models.agent import HERITABLE_TRAITS, TRAIT_HERITABILITY


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    """Render the Trait Evolution tab."""

    st.subheader("Heritable Trait Means Over Time")
    if is_multi_run:
        st.caption("Shaded bands show \u00b11 standard deviation across seeds.")

    # Map trait column -> std column -> color
    trait_band_config = {
        "avg_aggression": ("trait_std_aggression", COLORS["violence"]),
        "avg_cooperation": ("trait_std_cooperation", COLORS["cooperation"]),
        "avg_intelligence": ("trait_std_intelligence", COLORS["population"]),
        "avg_risk_tolerance": ("trait_std_risk_tolerance", COLORS["belief"]),
    }

    trait_colors = {
        "avg_aggression": COLORS["violence"],
        "avg_cooperation": COLORS["cooperation"],
        "avg_attractiveness": COLORS["mating"],
        "avg_status_drive": COLORS["resources"],
        "avg_risk_tolerance": COLORS["belief"],
        "avg_jealousy": COLORS["status"],
        "avg_fertility": COLORS["intelligence"],
        "avg_intelligence": COLORS["population"],
    }

    def _std_col(col):
        return (df_std[col]
                if (is_multi_run and df_std is not None and col in df_std.columns)
                else None)

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
        fig.update_layout(**standard_layout("Traits (Group 1) with \u00b11\u03c3 Bands", 400))
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
        fig.update_layout(**standard_layout("Traits (Group 2) with \u00b11\u03c3 Bands", 400))
        st.plotly_chart(fig, use_container_width=True)

    # Trait diversity
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        for std_name, color in [("trait_std_aggression", COLORS["violence"]),
                                ("trait_std_cooperation", COLORS["cooperation"]),
                                ("trait_std_intelligence", COLORS["population"]),
                                ("trait_std_risk_tolerance", COLORS["belief"])]:
            if std_name in df.columns:
                label = std_name.replace("trait_std_", "").replace("_", " ").title() + " Std"
                fig.add_trace(go.Scatter(x=df["year"], y=df[std_name], name=label,
                                         line=dict(color=color)))
        fig.update_layout(**standard_layout("Trait Diversity (Std Dev)", 350))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["max_generation"],
                                 name="Max Generation", fill="tozeroy",
                                 line=dict(color="#7E57C2")))
        fig.update_layout(**standard_layout("Generational Depth", 350))
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
                         color_discrete_map={"male": COLORS["males"], "female": COLORS["females"]},
                         title=f"{t1} vs {t2}")
        fig.update_layout(**standard_layout(f"{t1} vs {t2}", 500))
        st.plotly_chart(fig, use_container_width=True)

    # ── Realized Heritability Section ────────────────────────────
    st.markdown("---")
    st.subheader("Realized Heritability Over Time (h\u00b2 = Var(genotype) / Var(phenotype))")
    st.caption(
        "Shows how much of each trait's variance is genetic vs environmental. "
        "h\u00b2=1.0 means all variation is genetic. h\u00b2<0.5 means environment "
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
            format_func=lambda t: TRAIT_ABBREV.get(t, t),
            key="h2_trait_select",
        )

        show_ref = st.checkbox("Show theoretical h\u00b2 reference lines", key="h2_ref_lines")

        fig = go.Figure()

        for trait in selected_h2_traits:
            col = f"h2_{trait}"
            if col not in df.columns:
                continue
            values = df[col].ffill().fillna(0.5)
            color = TRAIT_DOMAIN_COLORS.get(trait, COLORS["neutral"])

            fig.add_trace(go.Scatter(
                x=df["year"], y=values,
                name=TRAIT_ABBREV.get(trait, trait[:12]),
                line=dict(color=color, width=2),
                mode="lines",
                hovertemplate="Year %{x}<br>h\u00b2=%{y:.3f}<br>" + TRAIT_ABBREV.get(trait, trait),
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
                    annotation_text=f"Expected: {TRAIT_ABBREV.get(trait, trait)} h\u00b2={ref_h2}",
                    annotation_position="right",
                    annotation_font_size=9, annotation_font_color=color,
                )

        fig.add_hline(y=0.5, line_dash="dot", line_color="white",
                      annotation_text="Nature = Nurture (h\u00b2=0.5)",
                      annotation_position="right")

        fig.update_layout(
            title="Realized Heritability Over Time",
            xaxis_title="Year",
            yaxis_title="Realized h\u00b2 (Var genotype / Var phenotype)",
            yaxis=dict(range=[0, 1.05]),
            height=500, template=PLOT_TEMPLATE,
            margin=dict(l=40, r=40, t=40, b=40),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
        )
        st.plotly_chart(fig, use_container_width=True)

        # Aggregate h2 chart
        if "avg_h2_all_traits" in df.columns:
            fig2 = go.Figure()
            avg_h2 = df["avg_h2_all_traits"].ffill().fillna(0.5)
            fig2.add_trace(go.Scatter(
                x=df["year"], y=avg_h2,
                name="Mean h\u00b2 (all traits)",
                line=dict(color=COLORS["belief"], width=2),
                fill="tozeroy", fillcolor="rgba(255,213,79,0.15)",
            ))
            fig2.add_hline(y=0.5, line_dash="dot", line_color="white",
                           annotation_text="Above 0.5 = genetics dominating | Below 0.5 = environment dominating",
                           annotation_position="top right", annotation_font_size=10)
            fig2.update_layout(
                title="Mean Heritability Across All Traits",
                xaxis_title="Year",
                yaxis_title="Mean h\u00b2",
                yaxis=dict(range=[0, 1.05]),
                height=250, template=PLOT_TEMPLATE,
                margin=dict(l=40, r=40, t=40, b=40),
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.info(
            "Scientific interpretation: "
            "Rising h\u00b2 means genetic selection is concentrating variation \u2014 the trait is becoming fixed. "
            "Falling h\u00b2 means environmental factors (institutions, scarcity, development) "
            "are overriding genetic signal. "
            "Compare STRONG_STATE vs FREE_COMPETITION \u2014 institutions should reduce h\u00b2 "
            "for cooperation as enforcement replaces genetic selection pressure."
        )
