"""Science Report tab — 6 analytical panels."""

from collections import defaultdict

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

from models.agent import HERITABLE_TRAITS
from data.names import namer
from dashboard.components.constants import TRAIT_ABBREV, TRAIT_DOMAIN_COLORS


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
    """Render the Science Report tab."""
    if df is None or len(df) == 0:
        st.info("Run a simulation first.")
        return

    st.title("Science Report")

    # ── PANEL 1: Trait Fitness Correlations ──────────────────────────
    with st.expander("Selection Pressure \u2014 Trait Correlation with Reproductive Success", expanded=True):
        st.caption(
            "Positive = trait increases offspring count. Negative = trait reduces fitness. "
            "This shows what evolution is actually selecting for in this run."
        )

        all_agents_list = list(society.agents.values())
        parents = [a for a in all_agents_list if len(a.offspring_ids) > 0]

        if len(parents) < 20:
            st.warning("Not enough parents (need 20+) to compute fitness correlations.")
        else:
            fitness_vals = np.array([len(a.offspring_ids) for a in parents])
            corr_records = []
            for trait in HERITABLE_TRAITS:
                t_vals = np.array([getattr(a, trait, 0.5) for a in parents])
                if np.std(t_vals) < 1e-8:
                    continue
                r = float(np.corrcoef(t_vals, fitness_vals)[0, 1])
                corr_records.append({"Trait": TRAIT_ABBREV.get(trait, trait),
                                     "trait_key": trait, "Correlation": r})

            if corr_records:
                cdf = pd.DataFrame(corr_records).sort_values("Correlation", key=abs, ascending=True)
                colors = ["#4ECDC4" if v >= 0 else "#FF6B6B" for v in cdf["Correlation"]]

                fig = go.Figure(go.Bar(
                    x=cdf["Correlation"], y=cdf["Trait"], orientation="h",
                    marker_color=colors,
                ))
                fig.add_vline(x=0, line_color="white", line_width=1)
                fig.update_layout(title="Trait Selection Pressure (end of simulation)",
                                  xaxis_title="Pearson r with offspring count",
                                  height=600, template="plotly_dark",
                                  margin=dict(l=120, r=40, t=40, b=40))
                st.plotly_chart(fig, width="stretch")

            # Time-series selection pressure (rolling 20yr)
            if len(df) >= 25 and "avg_lifetime_births" in df.columns:
                st.subheader("Selection Pressure Over Time (rolling 20yr window)")
                # Use top 6 correlated traits
                top6 = sorted(corr_records, key=lambda x: abs(x["Correlation"]), reverse=True)[:6]
                trait_col_map_sp = {
                    "aggression_propensity": "avg_aggression",
                    "cooperation_propensity": "avg_cooperation",
                    "intelligence_proxy": "avg_intelligence",
                }
                for t in HERITABLE_TRAITS:
                    for prefix in [f"avg_{t}", f"avg_{t.split('_')[0]}"]:
                        if prefix in df.columns and t not in trait_col_map_sp:
                            trait_col_map_sp[t] = prefix
                            break

                fig = go.Figure()
                births_series = df["avg_lifetime_births"]
                for rec in top6:
                    trait = rec["trait_key"]
                    col = trait_col_map_sp.get(trait)
                    if col and col in df.columns:
                        # Rolling correlation
                        rolling_r = df[col].rolling(20, min_periods=10).corr(births_series)
                        color = TRAIT_DOMAIN_COLORS.get(trait, "#888")
                        fig.add_trace(go.Scatter(
                            x=df["year"], y=rolling_r,
                            name=TRAIT_ABBREV.get(trait, trait[:10]),
                            line=dict(color=color, width=2),
                        ))
                fig.add_hline(y=0, line_dash="dot", line_color="white", opacity=0.5)
                fig.update_layout(title="Rolling 20yr Correlation with Lifetime Births",
                                  yaxis_title="Pearson r", height=350,
                                  template="plotly_dark",
                                  margin=dict(l=40, r=40, t=40, b=40))
                st.plotly_chart(fig, width="stretch")

    # ── PANEL 2: Institutional Impact ────────────────────────────────
    with st.expander("Institutional Effects on Evolution", expanded=False):
        st.caption("Shows how law_strength correlates with trait evolution and social outcomes.")

        col1, col2, col3 = st.columns(3)
        pairs = [
            (col1, "violence_rate", "Institutions \u2192 Violence", "#E53935"),
            (col2, "avg_cooperation", "Institutions \u2192 Cooperation", "#43A047"),
            (col3, "resource_gini", "Institutions \u2192 Inequality", "#FF9800"),
        ]
        for col, metric, title, _color in pairs:
            with col:
                if metric in df.columns:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["law_strength"], y=df[metric], mode="markers",
                        marker=dict(color=df["year"], colorscale="RdYlBu_r",
                                    size=5, showscale=(metric == "violence_rate"),
                                    colorbar=dict(title="Year")),
                        hovertemplate="Law=%{x:.2f}<br>Value=%{y:.3f}<br>Year=%{marker.color}",
                    ))
                    # Trendline
                    if df["law_strength"].std() > 0.01:
                        z = np.polyfit(df["law_strength"], df[metric], 1)
                        p = np.poly1d(z)
                        x_line = np.linspace(df["law_strength"].min(), df["law_strength"].max(), 50)
                        fig.add_trace(go.Scatter(x=x_line, y=p(x_line), mode="lines",
                                                 line=dict(color="white", dash="dash", width=1),
                                                 showlegend=False))
                    fig.update_layout(title=title, height=300, template="plotly_dark",
                                      xaxis_title="Law Strength", yaxis_title=metric,
                                      margin=dict(l=40, r=20, t=40, b=40))
                    st.plotly_chart(fig, width="stretch")

        # Correlation table
        corr_metrics = ["violence_rate", "avg_cooperation", "resource_gini",
                        "avg_aggression", "avg_lifetime_births"]
        corr_rows = []
        for m in corr_metrics:
            if m in df.columns and df["law_strength"].std() > 0.01:
                r = float(np.corrcoef(df["law_strength"], df[m])[0, 1])
                direction = "Positive" if r > 0.05 else ("Negative" if r < -0.05 else "Neutral")
                corr_rows.append({"Metric": m, "Correlation with Law Strength": round(r, 3),
                                  "Direction": direction})
        if corr_rows:
            st.dataframe(pd.DataFrame(corr_rows), width="stretch")

    # ── PANEL 3: Genetic Diversity ───────────────────────────────────
    with st.expander("Gene Pool Diversity Over Time", expanded=False):
        st.caption("Tracks whether the population is diversifying, stabilizing, or converging.")

        std_cols = [c for c in df.columns if c.startswith("trait_std_")]
        if std_cols:
            mean_diversity = df[std_cols].mean(axis=1)

            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df["year"], y=mean_diversity,
                                     name="Mean Genetic Variance",
                                     line=dict(color="#FFD54F", width=2)))
            if "trait_std_aggression" in df.columns:
                fig.add_trace(go.Scatter(x=df["year"], y=df["trait_std_aggression"],
                                         name="Aggression Variance",
                                         line=dict(color="#E53935", dash="dash")))
            if "trait_std_cooperation" in df.columns:
                fig.add_trace(go.Scatter(x=df["year"], y=df["trait_std_cooperation"],
                                         name="Cooperation Variance",
                                         line=dict(color="#43A047", dash="dash")))

            fig.add_hline(y=0.09, line_dash="dot", line_color="cyan", opacity=0.6,
                          annotation_text="Empirical baseline (~0.09)",
                          annotation_position="right")
            # Danger zone below 0.05
            fig.add_hrect(y0=0, y1=0.05, fillcolor="red", opacity=0.08,
                          annotation_text="Low diversity warning", annotation_position="top left")
            fig.update_layout(title="Genetic Diversity Over Time", height=350,
                              template="plotly_dark", yaxis_title="Trait Std Dev",
                              margin=dict(l=40, r=40, t=40, b=40))
            st.plotly_chart(fig, width="stretch")

            # Diversity stats
            current_div = float(mean_diversity.iloc[-1])
            initial_div = float(mean_diversity.iloc[0])
            delta = current_div - initial_div
            c1, c2 = st.columns(2)
            c1.metric("Current Mean Trait Variance", f"{current_div:.4f}",
                      delta=f"{delta:+.4f} from year 1")
            trend = "Increasing" if delta > 0.005 else ("Declining" if delta < -0.005 else "Stable")
            c2.metric("Diversity Trend", trend)
        else:
            st.info("No trait standard deviation columns available.")

    # ── PANEL 4: Founder Effect & Lineage Dominance ──────────────────
    with st.expander("Genetic Dominance \u2014 Top Founding Lineages", expanded=False):
        st.caption("Which founding genomes came to dominate the population.")

        all_agents_dict = society.agents

        # Count living descendants per founder
        founder_counts = defaultdict(int)
        for a in living:
            fid = _find_founder(a.id, all_agents_dict)
            founder_counts[fid] += 1

        top_founders = sorted(founder_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        total_living = len(living)

        if top_founders:
            f_names = []
            f_pcts = []
            f_colors = []
            table_rows = []
            for fid, count in top_founders:
                fa = all_agents_dict.get(fid)
                name = _get_agent_name(fid, society, fa)
                pct = count / total_living * 100
                coop = getattr(fa, "cooperation_propensity", 0.5) if fa else 0.5
                gen = getattr(fa, "generation", 0) if fa else 0
                top_trait = max(HERITABLE_TRAITS[:8],
                               key=lambda t: getattr(fa, t, 0.5)) if fa else "?"
                f_names.append(name)
                f_pcts.append(pct)
                f_colors.append(coop)
                table_rows.append({
                    "Founder": name, "Descendants": count,
                    "% Population": f"{pct:.1f}%",
                    "Dominant Trait": TRAIT_ABBREV.get(top_trait, top_trait),
                    "Generation": gen,
                })

            fig = go.Figure(go.Bar(
                x=f_pcts, y=f_names, orientation="h",
                marker=dict(color=f_colors,
                            colorscale=[[0, "#E53935"], [0.5, "#FFFFFF"], [1, "#1E88E5"]],
                            showscale=True, colorbar=dict(title="Coop")),
            ))
            fig.update_layout(title="Top 10 Lineages by Living Descendants",
                              xaxis_title="% of Living Population",
                              height=350, template="plotly_dark",
                              margin=dict(l=140, r=40, t=40, b=40))
            st.plotly_chart(fig, width="stretch")
            st.dataframe(pd.DataFrame(table_rows), width="stretch")
        else:
            st.info("No lineage data available.")

    # ── PANEL 5: Agent Archetypes ────────────────────────────────────
    with st.expander("Emergent Population Archetypes", expanded=False):
        st.caption("K-means clustering on agent traits reveals natural phenotype clusters.")

        try:
            from sklearn.cluster import KMeans
            from sklearn.decomposition import PCA
            _has_sklearn = True
        except ImportError:
            _has_sklearn = False

        if not _has_sklearn:
            st.warning("Install scikit-learn for archetypes: `pip install scikit-learn`")
        elif len(living) < 20:
            st.warning("Need at least 20 living agents for clustering.")
        else:
            n_clusters = st.slider("Number of archetypes", 2, 8, 4, key="n_archetypes")
            core_8 = HERITABLE_TRAITS[:8]
            X = np.array([[getattr(a, t, 0.5) for t in core_8] for a in living])

            try:
                km = KMeans(n_clusters=n_clusters, n_init=10, random_state=42)
                labels = km.fit_predict(X)
                centers = km.cluster_centers_
            except OSError:
                st.warning("sklearn KMeans failed (Windows threadpool issue). "
                           "Try: `pip install --upgrade threadpoolctl scikit-learn`")
                labels = None
                centers = None

            if labels is not None:
                # Name archetypes
                archetype_names = []
                for ci in range(n_clusters):
                    m_agg = centers[ci][0]
                    m_coop = centers[ci][1]
                    m_intel = centers[ci][7]
                    m_risk = centers[ci][4]
                    m_status = centers[ci][3]
                    m_fert = centers[ci][6]
                    cluster_agents = [living[i] for i in range(len(living)) if labels[i] == ci]
                    m_psych = float(np.mean([getattr(a, "psychopathy_tendency", 0.2) for a in cluster_agents]))
                    m_maternal = float(np.mean([getattr(a, "maternal_investment", 0.5) for a in cluster_agents]))

                    if m_agg > 0.6 and m_coop < 0.4:
                        name = "Warrior"
                    elif m_coop > 0.6 and m_agg < 0.4:
                        name = "Diplomat"
                    elif m_intel > 0.6 and m_risk < 0.4:
                        name = "Scholar"
                    elif m_risk > 0.6 and m_status > 0.6:
                        name = "Opportunist"
                    elif m_fert > 0.6 and m_maternal > 0.6:
                        name = "Caregiver"
                    elif m_psych > 0.4:
                        name = "Predator"
                    else:
                        name = f"Type {ci + 1}"
                    archetype_names.append(name)

                # Radar chart
                core_abbrevs = [TRAIT_ABBREV.get(t, t[:6]) for t in core_8]
                arc_colors = px.colors.qualitative.Set2
                fig = go.Figure()
                for ci in range(n_clusters):
                    vals = list(centers[ci]) + [centers[ci][0]]
                    fig.add_trace(go.Scatterpolar(
                        r=vals, theta=core_abbrevs + [core_abbrevs[0]],
                        fill="toself", name=archetype_names[ci],
                        line=dict(color=arc_colors[ci % len(arc_colors)]),
                        opacity=0.7,
                    ))
                fig.update_layout(
                    polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
                    title="Archetype Trait Profiles", height=400,
                    template="plotly_dark",
                    margin=dict(l=60, r=60, t=60, b=40),
                )
                st.plotly_chart(fig, width="stretch")

                # Population counts
                col1, col2 = st.columns(2)
                with col1:
                    counts = [int(np.sum(labels == ci)) for ci in range(n_clusters)]
                    fig = go.Figure(go.Bar(
                        x=archetype_names, y=counts,
                        marker_color=[arc_colors[i % len(arc_colors)] for i in range(n_clusters)],
                    ))
                    fig.update_layout(title="Population by Archetype", height=250,
                                      template="plotly_dark",
                                      margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, width="stretch")

                # PCA scatter
                with col2:
                    pca = PCA(n_components=2)
                    X2 = pca.fit_transform(X)
                    repro = [len(a.offspring_ids) for a in living]
                    pca_df = pd.DataFrame({
                        "PC1": X2[:, 0], "PC2": X2[:, 1],
                        "Archetype": [archetype_names[l] for l in labels],
                        "Offspring": repro,
                    })
                    fig = px.scatter(pca_df, x="PC1", y="PC2", color="Archetype",
                                     size="Offspring", opacity=0.6,
                                     color_discrete_sequence=arc_colors,
                                     title="PCA \u2014 Trait Space")
                    fig.update_layout(height=250, template="plotly_dark",
                                      margin=dict(l=40, r=40, t=40, b=40))
                    st.plotly_chart(fig, width="stretch")

    # ── PANEL 6: Civilization Timeline ────────────────────────────────
    with st.expander("Civilization Timeline \u2014 Major Events", expanded=False):
        st.caption("Automatically extracted from simulation event logs.")

        timeline_events = []

        # Extract categorized events
        for e in sim_events:
            yr = e.get("year", 0)
            etype = e.get("type", "")
            desc = e.get("description", "")

            if "epidemic" in etype and "death" not in etype:
                timeline_events.append((yr, "Epidemic", "Epidemic outbreak"))
            elif etype == "institution_emerged":
                timeline_events.append((yr, "Institution", f"Institution formed: {desc}"))
            elif etype == "belief_revolution":
                timeline_events.append((yr, "Belief", "Belief revolution"))
            elif "faction" in etype and "formed" in desc.lower():
                timeline_events.append((yr, "Faction", "Faction formed"))
            elif "faction" in etype and "schism" in desc.lower():
                timeline_events.append((yr, "Schism", "Faction schism"))
            elif etype == "scarcity_start":
                timeline_events.append((yr, "Scarcity", "Resource scarcity"))

        # Population crises/booms from metrics
        for i in range(1, len(df)):
            prev_pop = df.iloc[i - 1]["population"]
            curr_pop = df.iloc[i]["population"]
            if prev_pop > 0:
                change = (curr_pop - prev_pop) / prev_pop
                yr = int(df.iloc[i]["year"])
                if change < -0.10:
                    timeline_events.append((yr, "Crisis", f"Population dropped {change:.0%}"))
                elif change > 0.15:
                    timeline_events.append((yr, "Boom", f"Population surged {change:.0%}"))

        # Law strength milestones
        crossed_03 = False
        crossed_06 = False
        for _, row in df.iterrows():
            ls = row.get("law_strength", 0)
            yr = int(row["year"])
            if ls >= 0.3 and not crossed_03:
                timeline_events.append((yr, "Law", "Law emerged (strength > 0.3)"))
                crossed_03 = True
            if ls >= 0.6 and not crossed_06:
                timeline_events.append((yr, "Strong Law", "Strong institutions (strength > 0.6)"))
                crossed_06 = True

        timeline_events.sort(key=lambda x: x[0])

        # Deduplicate nearby events of same type
        filtered_tl = []
        last_by_type = {}
        for yr, cat, desc in timeline_events:
            if cat in last_by_type and yr - last_by_type[cat] < 3:
                continue
            last_by_type[cat] = yr
            filtered_tl.append((yr, cat, desc))

        if filtered_tl:
            cat_icons = {
                "Epidemic": "\U0001f9a0", "Institution": "\u2696\ufe0f", "Belief": "\U0001f4a1",
                "Faction": "\U0001f91d", "Schism": "\U0001f4a5", "Scarcity": "\U0001f335",
                "Crisis": "\u2620\ufe0f", "Boom": "\U0001f331", "Law": "\U0001f4dc", "Strong Law": "\U0001f3db\ufe0f",
            }
            cat_y = {cat: i for i, cat in enumerate(sorted(set(c for _, c, _ in filtered_tl)))}
            cat_colors = {
                "Epidemic": "#E53935", "Institution": "#1E88E5", "Belief": "#FFD54F",
                "Faction": "#43A047", "Schism": "#FF9800", "Scarcity": "#795548",
                "Crisis": "#F44336", "Boom": "#66BB6A", "Law": "#42A5F5",
                "Strong Law": "#1565C0",
            }

            fig = go.Figure()
            for yr, cat, desc in filtered_tl:
                fig.add_trace(go.Scatter(
                    x=[yr], y=[cat_y.get(cat, 0)],
                    mode="markers+text",
                    marker=dict(size=12, color=cat_colors.get(cat, "#888")),
                    text=[cat_icons.get(cat, "\u2022")],
                    textposition="top center",
                    hovertemplate=f"Year {yr}<br>{cat}: {desc}<extra></extra>",
                    showlegend=False,
                ))
            fig.update_layout(
                title="Civilization Timeline",
                yaxis=dict(tickvals=list(cat_y.values()), ticktext=list(cat_y.keys())),
                xaxis_title="Year", height=400, template="plotly_dark",
                margin=dict(l=100, r=40, t=40, b=40),
            )
            st.plotly_chart(fig, width="stretch")

            # Text timeline
            st.markdown("#### Event Log")
            for yr, cat, desc in filtered_tl:
                icon = cat_icons.get(cat, "\u2022")
                st.markdown(f"**Year {yr}** \u2014 {icon} {desc}")
        else:
            st.info("No major events detected. Try a longer simulation or enable institutional drift.")
