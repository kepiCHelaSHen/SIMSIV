"""SIMSIV Dashboard — Social Network tab."""

from collections import defaultdict

import numpy as np
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import standard_layout


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    """Render the Social Network tab."""

    st.subheader("Social Network \u2014 Prestige & Factions")
    st.caption("Top agents by prestige score. Node color = faction. "
               "Node size = prestige. Edges = trust > 0.5 within faction.")

    max_nodes = st.slider("Max agents to display", 20, 300, 150, step=10)

    if living:
        # ── Compute prestige scores ──────────────────────────────────
        # prestige_score is already an agent attribute (DD08)
        scored = [(a, a.prestige_score) for a in living]
        scored.sort(key=lambda x: x[1], reverse=True)
        sample = [a for a, _ in scored[:max_nodes]]
        sample_ids = {a.id for a in sample}

        # ── Faction clustering ───────────────────────────────────────
        # Use existing faction_id from agents. For agents without one,
        # derive mini-factions from trust graph connected components.
        faction_map = {}
        for a in sample:
            faction_map[a.id] = a.faction_id

        # For agents without faction_id, cluster by trust connectivity
        unfactioned = [a for a in sample if a.faction_id is None]
        if unfactioned:
            # Build adjacency from trust > 0.5
            adj = defaultdict(set)
            uf_ids = {a.id for a in unfactioned}
            for a in unfactioned:
                for oid, trust in a.reputation_ledger.items():
                    if trust > 0.5 and oid in uf_ids:
                        adj[a.id].add(oid)
                        adj[oid].add(a.id)

            # BFS connected components
            visited = set()
            next_faction = max((f for f in faction_map.values() if f is not None), default=0) + 100

            for a in unfactioned:
                if a.id in visited:
                    continue
                # BFS
                component = []
                queue = [a.id]
                while queue:
                    nid = queue.pop(0)
                    if nid in visited:
                        continue
                    visited.add(nid)
                    component.append(nid)
                    for neighbor in adj.get(nid, []):
                        if neighbor not in visited:
                            queue.append(neighbor)
                for nid in component:
                    faction_map[nid] = next_faction
                next_faction += 1

        # Assign colors per faction
        unique_factions = sorted(set(f for f in faction_map.values() if f is not None))
        faction_palette = px.colors.qualitative.Set3 + px.colors.qualitative.Pastel
        faction_color = {}
        for i, fid in enumerate(unique_factions):
            faction_color[fid] = faction_palette[i % len(faction_palette)]
        # Fallback for None
        faction_color[None] = COLORS["neutral"]

        # ── Layout: circular by faction, jittered ────────────────────
        rng_layout = np.random.default_rng(42)
        n = len(sample)

        # Group by faction for layout clustering
        faction_groups = defaultdict(list)
        for i, a in enumerate(sample):
            faction_groups[faction_map.get(a.id)].append(i)

        node_x = np.zeros(n)
        node_y = np.zeros(n)
        angle_offset = 0.0
        for fid, indices in faction_groups.items():
            # Place faction members in a cluster
            center_angle = angle_offset
            cx = 2.0 * np.cos(center_angle)
            cy = 2.0 * np.sin(center_angle)
            for j, idx in enumerate(indices):
                a_angle = j * 2 * np.pi / max(len(indices), 1)
                r = 0.3 + rng_layout.uniform(0, 0.4)
                node_x[idx] = cx + r * np.cos(a_angle)
                node_y[idx] = cy + r * np.sin(a_angle)
            angle_offset += 2 * np.pi / max(len(faction_groups), 1)

        pos = {sample[i].id: (node_x[i], node_y[i]) for i in range(n)}

        # ── Edges: trust > 0.5, within same faction ──────────────────
        edge_x, edge_y = [], []

        for a in sample:
            ax, ay = pos[a.id]
            a_faction = faction_map.get(a.id)
            for oid, trust in a.reputation_ledger.items():
                if trust > 0.5 and oid in sample_ids and oid > a.id:  # avoid duplicates
                    o_faction = faction_map.get(oid)
                    if a_faction == o_faction:  # within faction only
                        ox, oy = pos[oid]
                        edge_x.extend([ax, ox, None])
                        edge_y.extend([ay, oy, None])

        # ── Also show pair bonds (cross-faction OK) ──────────────────
        bond_x, bond_y = [], []
        for a in sample:
            ax, ay = pos[a.id]
            for pid in a.partner_ids:
                if pid in pos and pid > a.id:
                    px_, py_ = pos[pid]
                    bond_x.extend([ax, px_, None])
                    bond_y.extend([ay, py_, None])

        fig = go.Figure()

        # Trust edges (within faction)
        fig.add_trace(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(color="rgba(100,180,255,0.2)", width=0.8),
            hoverinfo="none", showlegend=True, name="Trust Link (in-faction)"))

        # Pair bond edges
        if bond_x:
            fig.add_trace(go.Scatter(
                x=bond_x, y=bond_y, mode="lines",
                line=dict(color="rgba(255,80,120,0.7)", width=2),
                hoverinfo="none", showlegend=True, name="Pair Bond"))

        # Nodes -- colored by faction, sized by prestige
        node_colors_list = [faction_color.get(faction_map.get(a.id), COLORS["neutral"]) for a in sample]
        node_sizes_list = [max(5, a.prestige_score * 30 + 4) for a in sample]
        node_text = [
            f"ID:{a.id} {a.sex.value[0].upper()} age:{a.age}<br>"
            f"prestige:{a.prestige_score:.2f} dom:{a.dominance_score:.2f}<br>"
            f"faction:{faction_map.get(a.id, '?')} bonds:{a.bond_count}<br>"
            f"coop:{a.cooperation_propensity:.2f} agg:{a.aggression_propensity:.2f}"
            for a in sample
        ]

        fig.add_trace(go.Scatter(
            x=[pos[a.id][0] for a in sample],
            y=[pos[a.id][1] for a in sample],
            mode="markers",
            marker=dict(size=node_sizes_list, color=node_colors_list,
                        line=dict(width=0.5, color="white")),
            text=node_text, hoverinfo="text", showlegend=False,
        ))

        fig.update_layout(
            height=750, template=PLOT_TEMPLATE,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, scaleanchor="x"),
            margin=dict(l=20, r=20, t=20, b=20),
        )
        st.plotly_chart(fig, width="stretch")

    # Bond count distribution + faction distribution
    if living:
        col1, col2 = st.columns(2)
        with col1:
            bond_counts = [a.bond_count for a in living]
            fig = go.Figure()
            fig.add_trace(go.Histogram(x=bond_counts,
                                       nbinsx=max(1, max(bond_counts, default=1) + 1),
                                       marker_color=COLORS["mating"]))
            fig.update_layout(**standard_layout("Bond Count Distribution", 300),
                              xaxis_title="Number of Bonds", yaxis_title="Agents")
            st.plotly_chart(fig, width="stretch")

        with col2:
            # Faction size distribution
            faction_counts = defaultdict(int)
            for a in living:
                fid = a.faction_id if a.faction_id is not None else "None"
                faction_counts[fid] += 1
            sorted_factions = sorted(faction_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=[str(f[0]) for f in sorted_factions],
                y=[f[1] for f in sorted_factions],
                marker_color="#7E57C2",
            ))
            fig.update_layout(**standard_layout("Faction Sizes (Top 20)", 300),
                              xaxis_title="Faction ID", yaxis_title="Members")
            st.plotly_chart(fig, width="stretch")
