"""SIMSIV Dashboard — Agents tab."""

import streamlit as st
import pandas as pd

from dashboard.components.constants import COLORS, PLOT_TEMPLATE


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    """Render the Agents tab."""

    st.subheader(f"Living Agents ({len(living)})")

    if living:
        agent_records = []
        for a in living:
            agent_records.append({
                "ID": a.id,
                "Sex": a.sex.value,
                "Age": a.age,
                "Gen": a.generation,
                "Health": round(a.health, 3),
                "Resources": round(a.current_resources, 2),
                "Status": round(a.current_status, 3),
                "Prestige": round(a.prestige_score, 3),
                "Dominance": round(a.dominance_score, 3),
                "Agg": round(a.aggression_propensity, 3),
                "Coop": round(a.cooperation_propensity, 3),
                "Intel": round(a.intelligence_proxy, 3),
                "Attract": round(a.attractiveness_base, 3),
                "Fertility": round(a.fertility_base, 3),
                "Offspring": len(a.offspring_ids),
                "Bonds": a.bond_count,
                "Partners": ", ".join(str(p) for p in a.partner_ids) if a.partner_ids else "-",
                "Mate Value": round(a.mate_value, 3),
                "Reputation": round(a.reputation, 3),
                "Network": sum(1 for t in a.reputation_ledger.values() if t > 0.5),
                "Faction": a.faction_id if a.faction_id is not None else "-",
            })

        agent_df = pd.DataFrame(agent_records)

        # Filters
        col1, col2, col3 = st.columns(3)
        with col1:
            sex_filter = st.multiselect("Sex", ["male", "female"], default=["male", "female"])
        with col2:
            age_range = st.slider("Age range", 0, 100, (0, 100))
        with col3:
            sort_col = st.selectbox("Sort by", agent_df.columns.tolist(), index=5)

        filtered = agent_df[
            agent_df["Sex"].isin(sex_filter) &
            (agent_df["Age"] >= age_range[0]) &
            (agent_df["Age"] <= age_range[1])
        ].sort_values(sort_col, ascending=False)

        st.dataframe(filtered, width="stretch", height=500)

        # Agent detail
        st.markdown("---")
        st.subheader("Agent Detail")
        agent_id = st.number_input("Enter Agent ID", value=int(filtered.iloc[0]["ID"]) if len(filtered) > 0 else 1, step=1)
        agent = society.get_by_id(agent_id)
        if agent and agent.alive:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Age", agent.age)
            c2.metric("Health", f"{agent.health:.3f}")
            c3.metric("Resources", f"{agent.current_resources:.2f}")
            c4.metric("Status", f"{agent.current_status:.3f}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Aggression", f"{agent.aggression_propensity:.3f}")
            c2.metric("Cooperation", f"{agent.cooperation_propensity:.3f}")
            c3.metric("Intelligence", f"{agent.intelligence_proxy:.3f}")
            c4.metric("Mate Value", f"{agent.mate_value:.3f}")

            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Prestige", f"{agent.prestige_score:.3f}")
            c2.metric("Dominance", f"{agent.dominance_score:.3f}")
            c3.metric("Faction", agent.faction_id if agent.faction_id is not None else "None")
            c4.metric("Life Stage", agent.life_stage)

            st.write(f"**Sex**: {agent.sex.value} | **Generation**: {agent.generation} | "
                     f"**Offspring**: {len(agent.offspring_ids)} | **Bonds**: {agent.bond_count}")
            if agent.partner_ids:
                st.write(f"**Partners**: {agent.partner_ids}")
            if agent.reputation_ledger:
                top_trust = sorted(agent.reputation_ledger.items(), key=lambda x: x[1], reverse=True)[:10]
                worst_trust = sorted(agent.reputation_ledger.items(), key=lambda x: x[1])[:5]
                st.write(f"**Most trusted**: {top_trust}")
                st.write(f"**Least trusted**: {worst_trust}")
        elif agent:
            st.warning(f"Agent {agent_id} is dead (cause: {agent.cause_of_death}, age {agent.age})")
        else:
            st.warning(f"Agent {agent_id} not found")
