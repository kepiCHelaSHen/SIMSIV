"""SIMSIV Dashboard — Events tab."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from dashboard.components.constants import COLORS, PLOT_TEMPLATE
from dashboard.components.charts import standard_layout


def render(df, df_std, living, society, config, sim_events,
           is_multi_run, seeds_count=1, **kwargs):
    """Render the Events tab."""

    st.subheader(f"Event Log ({len(sim_events):,} total events)")

    event_types = sorted(set(e.get("type", "?") for e in sim_events))
    selected_types = st.multiselect("Filter by type", event_types,
                                    default=event_types[:5] if len(event_types) > 5 else event_types)

    year_range = st.slider("Year range", 1, max(1, len(df)),
                           (max(1, len(df) - 20), len(df)), key="event_year")

    filtered_events = [
        e for e in sim_events
        if e.get("type") in selected_types
        and year_range[0] <= e.get("year", 0) <= year_range[1]
    ]

    st.write(f"Showing {len(filtered_events)} events")

    if filtered_events:
        event_df = pd.DataFrame(filtered_events[:2000])  # cap display
        if "outcome" in event_df.columns:
            event_df["outcome"] = event_df["outcome"].astype(str)
        if "agent_ids" in event_df.columns:
            event_df["agent_ids"] = event_df["agent_ids"].astype(str)
        st.dataframe(event_df, width="stretch", height=500)

    # Event type breakdown
    if sim_events:
        type_counts = {}
        for e in sim_events:
            t = e.get("type", "?")
            type_counts[t] = type_counts.get(t, 0) + 1

        fig = go.Figure()
        sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
        fig.add_trace(go.Bar(
            x=[t[0] for t in sorted_types],
            y=[t[1] for t in sorted_types],
            marker_color="#26C6DA",
        ))
        fig.update_layout(**standard_layout("Events by Type (All Years)", 350),
                          xaxis_tickangle=-45)
        st.plotly_chart(fig, width="stretch")
