"""Violence tab — conflict rates, outcomes, aggression scatter, faction matrix."""

import numpy as np
import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from collections import defaultdict

from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import add_band, standard_layout


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    def _std(col):
        return df_std[col] if (is_multi_run and df_std is not None and col in df_std.columns) else None

    col1, col2 = st.columns(2)

    with col1:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["violence_rate"], name="Violence Rate",
            line=dict(color=COLORS["violence"])), secondary_y=False)
        add_band(fig, df["year"], df["violence_rate"],
                 _std("violence_rate"), COLORS["violence"], secondary_y=False)
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["conflicts"], name="Conflicts",
            line=dict(color="#FF8A65", dash="dot")), secondary_y=True)
        fig.update_layout(**standard_layout("Violence Over Time", 400))
        fig.update_yaxes(title_text="Rate", secondary_y=False)
        fig.update_yaxes(title_text="Count", secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["violence_deaths"], name="Violence Deaths",
            line=dict(color="#D32F2F"), fill="tozeroy"))
        add_band(fig, df["year"], df["violence_deaths"],
                 _std("violence_deaths"), "#D32F2F")
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["flee_events"], name="Flee Events",
            line=dict(color="#FFC107", dash="dash")))
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["punishment_events"], name="Punishments",
            line=dict(color="#7E57C2", dash="dot")))
        fig.update_layout(**standard_layout("Conflict Outcomes", 400))
        st.plotly_chart(fig, use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df["year"], y=df["agents_in_cooldown"],
            name="In Subordination Cooldown",
            fill="tozeroy", line=dict(color="#FF6F00")))
        fig.update_layout(**standard_layout("Subordination (Recent Losers)", 300))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Aggression vs resources scatter for living
        if living:
            scatter_data = pd.DataFrame({
                "Aggression": [a.aggression_propensity for a in living],
                "Resources": [a.current_resources for a in living],
                "Status": [a.current_status for a in living],
                "Sex": [a.sex.value for a in living],
            })
            fig = px.scatter(
                scatter_data, x="Aggression", y="Resources", color="Sex",
                size="Status", opacity=0.6,
                color_discrete_map={"male": COLORS["males"], "female": COLORS["females"]},
                title="Aggression vs Resources (Living Agents)")
            fig.update_layout(**standard_layout("Aggression vs Resources (Living Agents)", 300))
            st.plotly_chart(fig, use_container_width=True)

    # ── Inter-Faction Violence Matrix ─────────────────────────────
    with st.expander("Inter-Faction Violence Matrix"):
        # Build matrix from conflict events
        conflict_events = [
            e for e in sim_events
            if e.get("type") in ("conflict", "violence", "fight")
        ]
        if conflict_events:
            # Map agent_id -> faction_id for all agents in society
            agent_faction = {}
            for a in society.agents.values():
                agent_faction[a.id] = a.faction_id if a.faction_id is not None else -1

            # Count conflicts between faction pairs
            pair_counts = defaultdict(int)
            faction_set = set()
            for e in conflict_events:
                aids = e.get("agent_ids", [])
                if len(aids) >= 2:
                    f0 = agent_faction.get(aids[0], -1)
                    f1 = agent_faction.get(aids[1], -1)
                    faction_set.add(f0)
                    faction_set.add(f1)
                    key = (min(f0, f1), max(f0, f1))
                    pair_counts[key] += 1

            if faction_set and pair_counts:
                factions_sorted = sorted(faction_set)
                labels = [f"F{f}" if f >= 0 else "None" for f in factions_sorted]
                n = len(factions_sorted)
                matrix = np.zeros((n, n), dtype=int)
                idx_map = {f: i for i, f in enumerate(factions_sorted)}
                for (f0, f1), count in pair_counts.items():
                    i, j = idx_map[f0], idx_map[f1]
                    matrix[i][j] = count
                    matrix[j][i] = count

                fig = go.Figure(data=go.Heatmap(
                    z=matrix, x=labels, y=labels,
                    colorscale="Reds", showscale=True,
                    hovertemplate="Attacker: %{y}<br>Defender: %{x}<br>Conflicts: %{z}<extra></extra>"))
                fig.update_layout(
                    **standard_layout("Inter-Faction Conflict Counts", 400),
                    xaxis_title="Faction", yaxis_title="Faction")
                st.plotly_chart(fig, use_container_width=True)
                st.caption(f"Based on {len(conflict_events):,} conflict events. "
                           f"'None' = agents without a faction assignment.")
            else:
                st.info("No inter-faction conflicts recorded.")
        else:
            st.info("No conflict events found in this simulation run.")
