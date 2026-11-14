"""ARES Health AI — synthetic, non-clinical hackathon prototype."""
from __future__ import annotations

import json

import streamlit as st
import plotly.express as px

from src.ares_health.analysis import quality_issues, review_changes
from src.ares_health.synthetic import SCENARIOS, generate_scenario
from src.ares_health.review import build_review_report

st.set_page_config(page_title="ARES Health AI | Mission Control", page_icon="🛰️", layout="wide")
st.markdown("""
<style>
.ares-hero {
  background: linear-gradient(115deg, #142a57 0%, #173f66 60%, #12727d 100%);
  border: 1px solid rgba(193,228,255,.25);
  border-radius: 18px;
  padding: 26px 30px;
  color: white;
  margin-bottom: 18px;
}
.ares-hero h1 {font-size: 2.4rem; margin: 0 0 6px 0; color: white;}
.ares-hero p {margin: 0; color: #d6edf8;}
.ares-eyebrow {color: #a6e8f5; text-transform: uppercase; font-size: .78rem;
  letter-spacing: .13em; font-weight: 700; margin-bottom: 8px;}
.ares-pill {display: inline-block; border: 1px solid #9ad7dc; padding: 5px 12px;
  border-radius: 99px; font-size: .78rem; margin-top: 16px; color: white;}
</style>
""", unsafe_allow_html=True)
st.markdown("""
<div class="ares-hero">
  <div class="ares-eyebrow">Mission control · Prototype v0.5</div>
  <h1>ARES Health AI</h1>
  <p>Astronaut Risk Evaluation System · NASA Space Apps Challenge 2026</p>
  <span class="ares-pill">LOCAL DEMONSTRATION · SYNTHETIC DATA ONLY</span>
</div>
""", unsafe_allow_html=True)
st.warning(
    "SIMULATED DATA ONLY · Engineering demonstration, not a medical device. "
    "No health diagnosis or astronaut risk prediction is provided."
)

with st.sidebar:
    st.header("Mission simulation")
    selected = st.selectbox("Demo scenario", options=list(SCENARIOS))
    seed = st.number_input("Reproducibility seed", min_value=0, max_value=999999, value=2026, step=1)
    st.divider()
    st.caption("Profile: SIM-001 · Local simulation")
    st.caption("No external API or real NASA telemetry is connected.")

records = generate_scenario(SCENARIOS[selected], seed=int(seed))
flags, blocked = review_changes(records)
issues = quality_issues(records)

st.subheader("Mission status — SIM-001")
tracked = ["resting_hr_bpm", "sleep_hours", "activity_minutes"]
missing_cells = int(records[tracked].isna().sum().sum())
completeness = 100.0 * (1 - missing_cells / records[tracked].size)
metric_a, metric_b, metric_c, metric_d = st.columns(4)
metric_a.metric("Recorded days", len(records))
metric_b.metric("Data completeness", f"{completeness:.1f}%")
metric_c.metric("Quality findings", len(issues))
metric_d.metric("Review flags", len(flags))
if issues:
    st.error("DATA QUALITY BLOCKED — missing or invalid records prevent trend interpretation.")
elif blocked:
    st.info("INSUFFICIENT DATA — no reliable baseline comparison is available.")
elif flags:
    st.warning("CHANGES FOR REVIEW — illustrative trend rules detected a difference.")
else:
    st.success("NO DEMO RULE TRIGGERED — this does not establish medical safety.")

st.subheader("Physiological trends")
left, right = st.columns(2)
with left:
    plot_hr = px.line(records, x="timestamp_utc", y="resting_hr_bpm", markers=True,
                      title="Resting heart rate (synthetic)", labels={"timestamp_utc": "Date (UTC)", "resting_hr_bpm": "bpm"})
    plot_hr.update_layout(height=330, margin=dict(l=10, r=10, t=50, b=10))
    plot_hr.update_traces(connectgaps=False)
    st.plotly_chart(plot_hr, use_container_width=True)
with right:
    plot_sleep = px.line(records, x="timestamp_utc", y="sleep_hours", markers=True,
                         title="Sleep duration (synthetic)", labels={"timestamp_utc": "Date (UTC)", "sleep_hours": "Hours"})
    plot_sleep.update_layout(height=330, margin=dict(l=10, r=10, t=50, b=10))
    plot_sleep.update_traces(connectgaps=False)
    st.plotly_chart(plot_sleep, use_container_width=True)

plot_activity = px.line(
    records, x="timestamp_utc", y="activity_minutes", markers=True,
    title="Daily activity (synthetic)",
    labels={"timestamp_utc": "Date (UTC)", "activity_minutes": "Minutes per day"},
)
plot_activity.update_layout(height=290, margin=dict(l=10, r=10, t=50, b=10))
st.plotly_chart(plot_activity, use_container_width=True)

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
st.subheader("Mission review center")
st.caption("Document a demonstration review. This is not a medical assessment or onboard protocol.")
if issues:
    st.error("Review status: BLOCKED — correct data quality issues before interpreting trends.")
elif blocked:
    st.info("Review status: INSUFFICIENT DATA — no trend-based conclusions available.")
elif flags:
    st.warning("Review status: CHANGE FOR REVIEW — inspect the simulated trend and the explanation above.")
else:
    st.success("Review status: NO DEMO RULE TRIGGERED — this does not establish medical safety.")

with st.expander("Review workflow and exportable report", expanded=True):
    st.markdown("**Suggested engineering review steps**")
    st.markdown("""1. Check data provenance, units and missing records.
2. Compare reference and recent observations on the graphs.
3. Document findings; real missions require authorized procedures and qualified personnel.""")
    review_state = st.selectbox("Review log state", ["Pending review", "Reviewed in demo"])
    note = st.text_area(
        "Optional reviewer note (fictional scenario only)",
        placeholder="Example: Verified the synthetic data gap and withheld trend interpretation.",
        max_chars=500,
        help="Do not enter actual personal or medical information.",
    )
    report = build_review_report(
        records, scenario=SCENARIOS[selected], flags=flags,
        issues=issues, blocked=blocked, review_state=review_state, reviewer_note=note,
    )
    st.download_button(
        "Download review report (JSON)",
        data=json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8"),
        file_name=f"ares_review_{SCENARIOS[selected]}.json",
        mime="application/json",
    )

with st.expander("Data provenance and methodology"):
    st.markdown("""
**Source:** deterministic Python-generated synthetic records, not observations
from NASA astronauts, hospitals, or wearable devices.

**Demonstration method:** the first seven simulated days serve as the
illustrative reference, while the latest four days form the comparison.
A change of at least 12 bpm in resting heart rate or 1.5 hours in sleep
triggers a review flag. These are **engineering demo settings only**,
not medical cutoffs or NASA clinical standards.

**Limitations:** This software has not been medically validated or
qualified for use in spaceflight.
""")

with st.expander("Explore and export synthetic records"):
    st.dataframe(records, use_container_width=True, hide_index=True)
    st.download_button("Download demonstration CSV", records.to_csv(index=False).encode("utf-8"),
                       file_name=f"ares_{SCENARIOS[selected]}_synthetic.csv", mime="text/csv")

st.divider()
st.caption("ARES Health AI v0.5 · Synthetic engineering demonstration · Not NASA-approved or medically validated")
