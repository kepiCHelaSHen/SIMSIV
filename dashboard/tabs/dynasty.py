"""Dynasty Tree tab — Lineage sunburst and reproductive success scatter."""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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


def _count_descendants(agent_id, all_agents_dict, memo=None):
    """Count total descendants recursively. Uses explicit memo dict (no mutable default)."""
    if memo is None:
        memo = {}
    if agent_id in memo:
        return memo[agent_id]
    a = all_agents_dict.get(agent_id)
    if not a:
        memo[agent_id] = 0
        return 0
    total = len(a.offspring_ids)
    for oid in a.offspring_ids:
        total += _count_descendants(oid, all_agents_dict, memo)
    memo[agent_id] = total
    return total


def _find_founder(agent_id, all_agents_dict, visited=None):
    """Walk the maternal lineage to find the founding ancestor."""
    if visited is None:
        visited = set()
    if agent_id in visited:
        return agent_id
    visited.add(agent_id)
    a = all_agents_dict.get(agent_id)
    if not a or a.parent_ids == (None, None):
        return agent_id
    p1, p2 = a.parent_ids
    if p1 is not None and p1 in all_agents_dict:
        return _find_founder(p1, all_agents_dict, visited)
    if p2 is not None and p2 in all_agents_dict:
        return _find_founder(p2, all_agents_dict, visited)
    return agent_id


# ── Main render ─────────────────────────────────────────────────────

def render(df, df_std, living, society, config, sim_events, is_multi_run, seeds_count=1, **kwargs):
    """Render the Dynasty Tree tab."""
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
        return

    st.subheader("Dynasty Tree \u2014 Lineage Sunburst")

    all_agents_dict = society.agents

    # Find generation-0 agents (founders)
    founders = [a for a in all_agents_dict.values() if a.generation == 0 and a.offspring_ids]
    founder_desc = [(a, _count_descendants(a.id, all_agents_dict, {})) for a in founders]
    founder_desc.sort(key=lambda x: x[1], reverse=True)
    top_founders = founder_desc[:8]

    if not top_founders:
        st.warning("No lineages found (no generation-0 agents with offspring).")
    else:
        labels = [f"{_get_agent_name(a.id, society, a)} line \u2014 {d} total descendants"
                  for a, d in top_founders]
        chosen_label = st.selectbox("Select lineage", labels, key="dynasty_select")
        chosen_idx = labels.index(chosen_label)
        root_agent, _ = top_founders[chosen_idx]

        # Build sunburst data by BFS from root (unique IDs to avoid Plotly collisions)
        sb_ids, sb_parents, sb_labels, sb_values, sb_colors = [], [], [], [], []

        queue = [(root_agent.id, "")]
        visited_sb = set()
        while queue:
            aid, parent_id_str = queue.pop(0)
            if aid in visited_sb:
                continue
            visited_sb.add(aid)
            a = all_agents_dict.get(aid)
            if not a:
                continue
            name = _get_agent_name(aid, society, a)
            unique_id = f"{name}_{aid}"
            sb_ids.append(unique_id)
            sb_parents.append(parent_id_str)
            sb_labels.append(name)
            sb_values.append(max(1, len(a.offspring_ids)))
            sb_colors.append(getattr(a, "cooperation_propensity", 0.5))
            for oid in a.offspring_ids:
                queue.append((oid, unique_id))

        if len(sb_ids) == 0:
            st.warning("No lineage data to display.")
        else:
            if len(sb_ids) > 2000:
                st.warning(f"Lineage has {len(sb_ids)} nodes \u2014 showing first 2000.")
                sb_ids = sb_ids[:2000]
                sb_parents = sb_parents[:2000]
                sb_labels = sb_labels[:2000]
                sb_values = sb_values[:2000]
                sb_colors = sb_colors[:2000]

            fig = go.Figure(go.Sunburst(
                ids=sb_ids, labels=sb_labels, parents=sb_parents,
                values=sb_values,
                marker=dict(
                    colors=sb_colors,
                    colorscale=[[0, "#E53935"], [0.5, "#FFFFFF"], [1, "#1E88E5"]],
                    showscale=True, colorbar=dict(title="Coop"),
                ),
                branchvalues="total",
                hovertemplate="<b>%{label}</b><br>Offspring: %{value}<extra></extra>",
            ))
            fig.update_layout(height=650, template="plotly_dark",
                              margin=dict(l=20, r=20, t=30, b=20),
                              title=f"Lineage of {_get_agent_name(root_agent.id, society, root_agent)}")
            st.plotly_chart(fig, width="stretch")

    # Animated scatter: reproductive success by generation
    st.subheader("Reproductive Success Across Generations")
    scatter_records = []
    for a in all_agents_dict.values():
        birth_year = max(1, society.year - a.age) if a.alive else (
            a.year_of_death - a.age if a.year_of_death else 1)
        top_trait_name = max(HERITABLE_TRAITS, key=lambda t: getattr(a, t, 0.5))
        scatter_records.append({
            "Name": _get_agent_name(a.id, society, a),
            "Birth Year": int(birth_year),
            "Lifetime Births": a.lifetime_births,
            "Cooperation": round(a.cooperation_propensity, 3),
            "Offspring": len(a.offspring_ids),
            "Generation": a.generation,
            "Faction": a.faction_id if a.faction_id is not None else -1,
            "Top Trait": TRAIT_ABBREV.get(top_trait_name, top_trait_name),
        })
    sdf = pd.DataFrame(scatter_records)
    if len(sdf) > 0 and sdf["Generation"].nunique() > 1:
        fig = px.scatter(
            sdf, x="Birth Year", y="Lifetime Births",
            color="Cooperation", size="Offspring",
            animation_frame="Generation",
            hover_data=["Name", "Faction", "Top Trait"],
            color_continuous_scale=[[0, "#E53935"], [0.5, "#FFFFFF"], [1, "#1E88E5"]],
            title="Reproductive Success by Generation",
        )
        fig.update_layout(height=500, template="plotly_dark",
                          margin=dict(l=40, r=40, t=40, b=40))
        st.plotly_chart(fig, width="stretch")
    else:
        st.info("Not enough generational data for animation.")
