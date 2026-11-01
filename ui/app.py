"""Streamlit shell for the treasury dashboard.

The page loads and renders headings plus empty chart slots.  Wiring the data is
part of the challenge; see ISSUE-07.
"""

from __future__ import annotations

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Noyyal treasury", layout="wide")
st.title("Noyyal Knits - 13-week treasury")
st.caption("Forecast fan, buffer curve and Friday wage coverage")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Closing balance fan")
    placeholder = pd.DataFrame(
        {"week_start": pd.date_range("2026-08-03", periods=13, freq="7D")}
    )
    st.line_chart(placeholder.set_index("week_start"), height=260)
    st.info("ISSUE-07: plot closing_p10 / p50 / p90 from the current submission.")

with col2:
    st.subheader("Minimum-cash target")
    st.line_chart(placeholder.set_index("week_start"), height=260)
    st.info("ISSUE-07: plot min_cash_target_inr and the simulated shortfall probability.")

st.subheader("Friday wage coverage")
st.empty()
st.caption("ISSUE-07: show cash + undrawn CC against that Friday's wages.")
