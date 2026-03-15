"""Genome Map tab — Agent x Trait heatmap and trait correlation matrix."""

import streamlit as st
import numpy as np
import plotly.graph_objects as go

from models.agent import HERITABLE_TRAITS
from data.names import namer
from dashboard.components.constants import TRAIT_ABBREV


# ── Helpers ─────────────────────────────────────────────────────────

def _get_agent_name(agent_id, society, agent=None):
    """Get full name for an agent, caching in session state."""
    cache = st.session_state.setdefault("agent_names", {})
    if agent_id not in cache:
        sex = "male"
        if agent:
            sex = agent.sex.value if hasattr(agent.sex, "value") else str(agent.sex)
        else:
            a = society.get_by_id(agent_id)
            if a:
                sex = a.sex.value if hasattr(a.sex, "value") else str(a.sex)
        cache[agent_id] = namer.get_full_name(agent_id, sex=sex)
    return cache[agent_id]


# ── Main render ─────────────────────────────────────────────────────

def render(df, df_std, living, society, config, sim_events, is_multi_run, seeds_count=1, **kwargs):
    """Render the Genome Map tab."""
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
        return
    if not living:
        st.warning("No living agents.")
        return

    st.subheader("Agent \u00d7 Trait Heatmap")

    # Faction filter
    all_factions = sorted(set(a.faction_id for a in living if a.faction_id is not None))
    selected_factions = st.multiselect(
        "Filter by faction (empty = all)", all_factions,
        default=[], key="genome_faction_filter")

    if selected_factions:
        display_agents = [a for a in living if a.faction_id in selected_factions]
    else:
        display_agents = list(living)

    # Sort by faction then prestige
    display_agents.sort(key=lambda a: (a.faction_id if a.faction_id is not None else 9999,
                                       -a.prestige_score))

    # Limit to 300 agents for performance
    if len(display_agents) > 300:
        display_agents = display_agents[:300]
        st.caption(f"Showing top 300 of {len(living)} agents.")

    trait_names = list(HERITABLE_TRAITS)
    abbrevs = [TRAIT_ABBREV.get(t, t[:10]) for t in trait_names]

    # Build matrix
    matrix = np.array([[getattr(a, t, 0.5) for t in trait_names] for a in display_agents])
    agent_labels = [_get_agent_name(a.id, society, a) for a in display_agents]
    faction_labels = [str(a.faction_id) if a.faction_id is not None else "None" for a in display_agents]

    hover_text = []
    for i, a in enumerate(display_agents):
        row_hover = []
        for j, t in enumerate(trait_names):
            row_hover.append(
                f"{agent_labels[i]}<br>Faction: {faction_labels[i]}<br>"
                f"{TRAIT_ABBREV.get(t, t)}: {matrix[i, j]:.3f}")
        hover_text.append(row_hover)

    fig = go.Figure(go.Heatmap(
        z=matrix, x=abbrevs, y=agent_labels,
        colorscale=[[0, "#1565C0"], [0.5, "#FFFFFF"], [1, "#C62828"]],
        zmin=0, zmax=1,
        text=hover_text, hoverinfo="text",
        colorbar=dict(title="Trait Value"),
    ))

    # Draw horizontal lines between faction groups
    prev_faction = None
    for i, a in enumerate(display_agents):
        fid = a.faction_id
        if prev_faction is not None and fid != prev_faction:
            fig.add_hline(y=i - 0.5, line_width=1, line_color="rgba(255,255,255,0.3)")
        prev_faction = fid

    fig.update_layout(
        height=max(400, len(display_agents) * 4 + 100),
        template="plotly_dark",
        margin=dict(l=120, r=40, t=40, b=80),
        title="Agent \u00d7 Trait Heatmap (sorted by faction, prestige)",
        xaxis=dict(tickangle=-45),
        yaxis=dict(showticklabels=len(display_agents) <= 80),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Chart 2: Trait correlation heatmap
    st.subheader("Trait Co-evolution Correlation (Living Population)")
    if len(living) >= 10:
        corr_matrix_data = np.array([[getattr(a, t, 0.5) for t in trait_names] for a in living])
        corr = np.corrcoef(corr_matrix_data, rowvar=False)

        fig = go.Figure(go.Heatmap(
            z=corr, x=abbrevs, y=abbrevs,
            colorscale=[[0, "#1565C0"], [0.5, "#FFFFFF"], [1, "#C62828"]],
            zmin=-1, zmax=1,
            colorbar=dict(title="Correlation"),
        ))
        fig.update_layout(
            height=700, template="plotly_dark",
            margin=dict(l=100, r=40, t=40, b=100),
            title="Trait Co-evolution Correlation (Living Population)",
            xaxis=dict(tickangle=-45),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Need at least 10 living agents for correlation matrix.")
