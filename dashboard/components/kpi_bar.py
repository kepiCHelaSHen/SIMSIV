"""Summary KPI metrics bar shown at the top of every run."""

import streamlit as st
import pandas as pd


def render_kpi_bar(df: pd.DataFrame, is_multi_run: bool, seeds_count: int):
    if df is None or len(df) == 0:
        return

    final = df.iloc[-1]
    first = df.iloc[0]

    def _delta(col):
        try:
            return float(final[col]) - float(first[col])
        except Exception:
            return None

    if is_multi_run:
        st.caption(f"Research Mode: {seeds_count} seeds averaged. "
                   f"Shaded bands show +/-1 standard deviation.")

    c1, c2, c3, c4, c5, c6, c7, c8 = st.columns(8)
    c1.metric("Final Pop", f"{int(final['population']):,}",
              delta=f"{int(final['population']) - int(first['population']):+,}")
    c2.metric("Total Births", f"{int(df['births'].sum()):,}")
    c3.metric("Total Deaths", f"{int(df['deaths'].sum()):,}")
    d = _delta('resource_gini')
    c4.metric("Gini", f"{final['resource_gini']:.3f}",
              delta=f"{d:+.3f}" if d is not None else None)
    d = _delta('violence_rate')
    c5.metric("Violence", f"{final['violence_rate']:.3f}",
              delta=f"{d:+.3f}" if d is not None else None)
    d = _delta('pair_bonded_pct')
    c6.metric("Bonded %", f"{final['pair_bonded_pct']:.1%}",
              delta=f"{d:+.1%}" if d is not None else None)
    c7.metric("CSI", f"{final['civilization_stability']:.3f}")
    c8.metric("SCI", f"{final['social_cohesion']:.3f}")
