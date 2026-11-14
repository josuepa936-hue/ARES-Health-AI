"""ARES Health AI — synthetic, non-clinical hackathon prototype."""
from __future__ import annotations

import streamlit as st
import plotly.express as px

from src.ares_health.analysis import quality_issues, review_changes
from src.ares_health.synthetic import SCENARIOS, generate_scenario

st.set_page_config(page_title="ARES Health AI | Demo", page_icon="🛰️", layout="wide")
st.title("ARES Health AI")
st.caption("Astronaut Risk Evaluation System · NASA Space Apps Challenge 2026")
st.warning(
    "SIMULATED DATA ONLY · Engineering demonstration, not a medical device. "
    "No health diagnosis or astronaut risk prediction is provided."
)

with st.sidebar:
    st.header("Mission simulation")
    selected = st.selectbox("Demo scenario", options=list(SCENARIOS))
    seed = st.number_input("Reproducibility seed", min_value=0, max_value=999999, value=2026, step=1)
    st.caption("Offline-capable prototype. No connection to real biosensors or NASA telemetry.")

records = generate_scenario(SCENARIOS[selected], seed=int(seed))
flags, blocked = review_changes(records)
issues = quality_issues(records)

st.subheader("Synthetic crew profile — SIM-001")
metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Days recorded", len(records))
metric_b.metric("Data quality issues", len(issues))
metric_c.metric("Changes for review", len(flags))

st.subheader("Physiological trends")
left, right = st.columns(2)
with left:
    plot_hr = px.line(records, x="timestamp_utc", y="resting_hr_bpm", markers=True,
                      title="Resting heart rate (synthetic)", labels={"timestamp_utc": "Date (UTC)", "resting_hr_bpm": "bpm"})
    st.plotly_chart(plot_hr, use_container_width=True)
with right:
    plot_sleep = px.line(records, x="timestamp_utc", y="sleep_hours", markers=True,
                         title="Sleep duration (synthetic)", labels={"timestamp_utc": "Date (UTC)", "sleep_hours": "Hours"})
    st.plotly_chart(plot_sleep, use_container_width=True)

st.subheader("Quality and review guidance")
if issues:
    st.error("Data quality prevents a reliable trend comparison in this demo.")
    for issue in issues:
        st.write(f"• {issue}")
elif blocked:
    st.info("Trend evaluation unavailable: " + "; ".join(blocked))
elif flags:
    for flag in flags:
        st.warning(flag.message)
else:
    st.info("No illustrative change rule was triggered. This is NOT evidence of medical health or safety.")

st.caption(
    "Reference = first 7 simulated days; comparison = latest 4 simulated days. "
    "Thresholds are software demonstration settings, not NASA standards or clinical limits."
)
with st.expander("Explore and export synthetic records"):
    st.dataframe(records, use_container_width=True, hide_index=True)
    st.download_button("Download demonstration CSV", records.to_csv(index=False).encode("utf-8"),
                       file_name=f"ares_{SCENARIOS[selected]}_synthetic.csv", mime="text/csv")

st.divider()
st.caption("ARES Health AI · Non-clinical concept · Scientific validation required before any real-world use")
