"""SIMSIV Dashboard — Institutions tab."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import add_band, standard_layout


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    """Render the Institutions tab."""

    def _std_col(col):
        return (df_std[col]
                if (is_multi_run and df_std is not None and col in df_std.columns)
                else None)

    col1, col2 = st.columns(2)

    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["law_strength"],
                                 name="Law Strength", line=dict(color=COLORS["law"])))
        add_band(fig, df["year"], df["law_strength"], _std_col("law_strength"), COLORS["law"])
        fig.add_trace(go.Scatter(x=df["year"], y=df["violence_punishment"],
                                 name="Violence Punishment", line=dict(color="#D32F2F", dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["property_rights"],
                                 name="Property Rights", line=dict(color=COLORS["cooperation"], dash="dot")))
        fig.update_layout(**standard_layout("Institutional Parameters", 400))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df["year"], y=df["inheritance_events"],
                                 name="Inheritances", line=dict(color="#FFA726")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["norm_violations"],
                                 name="Norm Violations", line=dict(color=COLORS["violence"], dash="dash")))
        fig.add_trace(go.Scatter(x=df["year"], y=df["institutions_emerged"],
                                 name="Emergences", line=dict(color="#7E57C2", dash="dot")))
        fig.update_layout(**standard_layout("Institutional Events", 400))
        st.plotly_chart(fig, use_container_width=True)

    # Composite indices
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df["year"], y=df["civilization_stability"],
                             name="Civilization Stability Index", line=dict(color=COLORS["law"], width=2)))
    add_band(fig, df["year"], df["civilization_stability"], _std_col("civilization_stability"), COLORS["law"])
    fig.add_trace(go.Scatter(x=df["year"], y=df["social_cohesion"],
                             name="Social Cohesion Index", line=dict(color=COLORS["cooperation"], width=2)))
    add_band(fig, df["year"], df["social_cohesion"], _std_col("social_cohesion"), COLORS["cooperation"])
    fig.update_layout(**standard_layout("Composite Stability Indices", 350))
    st.plotly_chart(fig, use_container_width=True)

    # Trait evolution under institutional pressure
    st.markdown("---")
    st.subheader("Trait Evolution Under Institutional Pressure")
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Scatter(x=df["year"], y=df["avg_cooperation"], name="Cooperation",
                             line=dict(color=COLORS["cooperation"], width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["year"], y=df["avg_aggression"], name="Aggression",
                             line=dict(color=COLORS["violence"], width=2)), secondary_y=False)
    fig.add_trace(go.Scatter(x=df["year"], y=df["law_strength"], name="Law Strength",
                             line=dict(color=COLORS["belief"], width=2, dash="dash")), secondary_y=True)
    fig.update_yaxes(title_text="Trait Value", secondary_y=False)
    fig.update_yaxes(title_text="Law Strength", secondary_y=True)
    fig.update_layout(title="Institutions Substitute for Traits", height=350,
                      template=PLOT_TEMPLATE, margin=dict(l=40, r=40, t=40, b=40))
    st.plotly_chart(fig, use_container_width=True)

    # Phase Portrait expander
    with st.expander("Phase Portrait -- Law vs Violence", expanded=False):
        st.caption("System dynamics: does law drive violence down, or violence drive law up?")
        if "law_strength" in df.columns and df["law_strength"].std() > 0.01:
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df["law_strength"], y=df["violence_rate"], mode="markers+lines",
                marker=dict(color=df["year"], colorscale="RdYlBu_r", size=5,
                            showscale=True, colorbar=dict(title="Year")),
                line=dict(color="rgba(255,255,255,0.2)", width=1),
                hovertemplate="Year %{text}<br>Law: %{x:.3f}<br>Violence: %{y:.3f}<extra></extra>",
                text=df["year"].astype(str),
            ))
            fig.add_trace(go.Scatter(x=[df["law_strength"].iloc[0]], y=[df["violence_rate"].iloc[0]],
                                     mode="markers", marker=dict(size=12, color="lime", symbol="star"), name="Start"))
            fig.add_trace(go.Scatter(x=[df["law_strength"].iloc[-1]], y=[df["violence_rate"].iloc[-1]],
                                     mode="markers", marker=dict(size=12, color="red", symbol="x"), name="End"))
            fig.update_layout(**standard_layout("Phase Portrait: Law vs Violence", 450),
                              xaxis_title="Law Strength", yaxis_title="Violence Rate")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Enable institutional_drift_rate > 0 for phase portrait dynamics.")
