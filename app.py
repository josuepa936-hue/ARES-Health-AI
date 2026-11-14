"""ARES Health AI — synthetic, non-clinical hackathon prototype."""
from __future__ import annotations

import json

import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from src.ares_health.analysis import quality_issues, review_changes
from src.ares_health.synthetic import SCENARIOS, generate_scenario
from src.ares_health.review import build_review_report
from src.ares_health.evidence import EVIDENCE, get_crew_guidance
from src.ares_health.import_csv import load_synthetic_csv
from src.ares_health.advanced_stats import SIGNALS, describe_signals
from src.ares_health.mission_viz import make_body_map, make_signal_chart, SYSTEMS, SYSTEM_METRICS

st.set_page_config(
    page_title="ARES Health AI | Advanced Mission Control",
    page_icon="🛰️", layout="wide",
    initial_sidebar_state="expanded",
)
st.markdown("""
<style>
[data-testid="stAppViewContainer"] {background: #081221;}
[data-testid="stSidebar"] {background: #0D1B2F; border-right: 1px solid #24354F;}
.ares-hero {
  background: radial-gradient(circle at 92% -22%, rgba(56,212,221,.23), transparent 48%),
  linear-gradient(112deg, #13294F 0%, #102F47 60%, #143B48 100%);
  border: 1px solid rgba(113,219,239,.28); border-radius: 22px;
  padding: 34px 36px 30px 36px; color: #F1FAFF; margin-bottom: 20px;
  box-shadow: 0 18px 45px rgba(2,8,18,.26);
}
.ares-hero h1 {font-size: 2.7rem; letter-spacing: -1px; line-height: 1.08;
  margin: 0 0 8px 0; color: #F4FBFF; font-weight: 800;}
.ares-hero p {color: #C3E0E9; margin: 0; font-size: 1.02rem;}
.ares-eyebrow {color: #7BE1E9; text-transform: uppercase; font-size: .74rem;
  letter-spacing: .17em; font-weight: 800; margin-bottom: 12px;}
.ares-pills {margin-top: 22px; display: flex; flex-wrap: wrap; gap: 9px;}
.ares-pill {display: inline-block; border: 1px solid rgba(132,224,232,.45);
  padding: 5px 12px; border-radius: 99px; font-size: .72rem;
  color: #CBF7F9; background: rgba(6,24,39,.42);}
.ares-mini {font-size: .82rem; color: #9EB5C9;}
div[data-testid="stMetric"] {border: 1px solid #223954;
  background: linear-gradient(180deg, #13263D, #0E1E32); border-radius: 16px;
  padding: 16px 18px;}
div[data-testid="stMetric"] [data-testid="stMetricValue"] {color: #EBF8FF;}
div[data-testid="stTabs"] button {font-weight: 650;}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="ares-hero">
  <div class="ares-eyebrow">Mission operations / Synthetic prototype v0.8</div>
  <h1>ARES <span style="color:#78E4E8">Health AI</span></h1>
  <p>Astronaut Risk Evaluation System · Human-Centered Mission Intelligence</p>
  <div class="ares-pills">
    <span class="ares-pill">NASA Space Apps 2026 challenge entry</span>
    <span class="ares-pill">Local-first analysis</span>
    <span class="ares-pill">SYNTHETIC DATA ONLY</span>
  </div>
</div>
""", unsafe_allow_html=True)
st.caption("Independent educational prototype. Not NASA-approved, not a medical device, and not a clinical decision system.")

with st.sidebar:
    st.markdown("### 🛰️ Mission Simulator")
    mode = st.radio("Data source", ["Built-in simulation", "Upload synthetic CSV"])
    if mode == "Built-in simulation":
        selected = st.selectbox("Demo scenario", options=list(SCENARIOS))
        seed = st.number_input(
            "Reproducibility seed", min_value=0, max_value=999999, value=2026, step=1
        )
        scenario_id = SCENARIOS[selected]
        records = generate_scenario(scenario_id, seed=int(seed))
    else:
        scenario_id = "uploaded_synthetic_csv"
        st.caption("Up to 1 MB and 366 daily rows. Synthetic records only.")
        st.download_button(
            "Download sample synthetic CSV",
            generate_scenario("stable").to_csv(index=False).encode("utf-8"),
            file_name="ares_synthetic_template.csv", mime="text/csv",
        )
        uploaded = st.file_uploader("Upload synthetic CSV", type=["csv"])
        attested = st.checkbox(
            "I confirm this CSV contains only fictional data, not real health records.",
            value=False,
        )
        if uploaded is None:
            st.info("Select a synthetic CSV to continue.")
            st.stop()
        if not attested:
            st.warning("Confirm fictional provenance before processing.")
            st.stop()
        records, upload_errors = load_synthetic_csv(uploaded.getvalue())
        if upload_errors:
            st.error("CSV rejected. No analysis was performed.")
            for error in upload_errors:
                st.write("- " + error)
            st.stop()
        st.success("Synthetic CSV validated locally.")
    st.divider()
    st.caption("SIMULATED CREW · No connected sensors or external clinical services.")
    st.caption("No NASA astronaut health records or live telemetry are imported.")

flags, blocked = review_changes(records)
issues = quality_issues(records)
guidance = get_crew_guidance(issues, blocked, flags)
stats = describe_signals(records)
stats_by_metric = {x.metric: x for x in stats}
crew_label = str(records["crew_id"].iloc[0])
tracked = ["resting_hr_bpm", "sleep_hours", "activity_minutes"]
missing_cells = int(records[tracked].isna().sum().sum())
completeness = 100.0 * (1.0 - missing_cells / records[tracked].size)

st.subheader(f"Mission status — {crew_label}")
if mode == "Upload synthetic CSV":
    st.info("User-attested synthetic CSV: fictional provenance is NOT independently verifiable.")
metric_a, metric_b, metric_c, metric_d = st.columns(4)
metric_a.metric("Recorded days", len(records))
metric_b.metric("Data completeness", f"{completeness:.1f}%")
metric_c.metric("Quality findings", len(issues))
metric_d.metric("Review flags", len(flags))

if issues:
    st.error("DATA QUALITY BLOCKED — source observations require verification.")
elif blocked:
    st.info("INSUFFICIENT DATA — no reference-window comparison available.")
elif flags:
    st.warning("CHANGES FOR REVIEW — demonstration rule(s) triggered, not a medical risk estimate.")
else:
    st.success("NO DEMO RULE TRIGGERED — this is not medical clearance.")

overview_tab, lab_tab, systems_tab, evidence_tab, review_tab = st.tabs([
    "🛰️ Mission Overview", "📈 Signals Lab", "🧍 Body Systems",
    "📚 Scientific Evidence", "📋 Mission Review",
])

with overview_tab:
    st.subheader("Live-style mission snapshot")
    st.caption("Historical fictional daily observations; not actual live astronaut telemetry.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Resting heart rate — synthetic**")
        st.plotly_chart(
            make_signal_chart(records, "resting_hr_bpm", stats_by_metric.get("resting_hr_bpm")),
            width="stretch", key="overview_hr",
        )
    with c2:
        st.markdown("**Sleep duration — synthetic**")
        st.plotly_chart(
            make_signal_chart(records, "sleep_hours", stats_by_metric.get("sleep_hours")),
            width="stretch", key="overview_sleep",
        )
    st.markdown("**Daily activity — synthetic**")
    st.plotly_chart(
        make_signal_chart(records, "activity_minutes", stats_by_metric.get("activity_minutes")),
        width="stretch", key="overview_activity",
    )
    st.markdown("#### What the system found")
    st.write(guidance.meaning)
    if issues:
        for item in issues:
            st.warning(item)
    elif blocked:
        for item in blocked:
            st.info(item)
    elif flags:
        for flag in flags:
            st.info(flag.message)
    else:
        st.caption("No review flag in this fictional scenario; this does not establish health.")

with lab_tab:
    st.subheader("Signals Laboratory")
    st.caption(
        "Exploratory statistics computed with SciPy, Pandas and NumPy. "
        "They do NOT produce medical classifications or modify the existing review rules."
    )
    focus = st.selectbox(
        "Explore a physiological signal",
        options=list(SIGNALS),
        format_func=lambda k: SIGNALS[k][0],
    )
    current = stats_by_metric.get(focus)
    st.plotly_chart(make_signal_chart(records, focus, current), width="stretch", key="lab_signal")
    if current is None:
        st.error("Descriptive statistics are withheld because data are invalid or insufficient.")
    else:
        a, b, c, d = st.columns(4)
        a.metric("Reference mean", f"{current.baseline_mean:.2f} {current.unit}")
        b.metric("Recent mean", f"{current.recent_mean:.2f} {current.unit}")
        c.metric("Difference (demo)", f"{current.delta:+.2f} {current.unit}")
        d.metric("Theil–Sen slope/day", f"{current.theil_sen_slope_per_day:+.3f}")
        st.markdown("**Exploratory signal overview**")
        st.dataframe(
            pd.DataFrame([{
                "Signal": x.label,
                "Unit": x.unit,
                "Reference": round(x.baseline_mean, 2),
                "Recent": round(x.recent_mean, 2),
                "Change": round(x.delta, 2),
                "Median": round(x.full_median, 2),
                "Robust spread (MAD)": round(x.robust_variability, 2),
                "Theil–Sen / day": round(x.theil_sen_slope_per_day, 3),
            } for x in stats]),
            hide_index=True, width="stretch",
        )
        st.caption(
            "Robust spread = Gaussian-scaled median absolute deviation; "
            "slope = Theil–Sen descriptive estimate. Small synthetic samples "
            "are not evidence of clinical significance."
        )

with systems_tab:
    st.subheader("Interactive Body Systems Atlas")
    st.caption(
        "Original schematic navigation — not a diagnostic anatomical map. "
        "Click an indicator marker or use the selector to explore a system."
    )
    left, right = st.columns([1, 1.1])
    with left:
        selected_system = st.selectbox("Explore body system", options=list(SYSTEMS))
        selection = st.plotly_chart(
            make_body_map(selected_system),
            width="stretch", key="ares_body_map",
            on_select="rerun", selection_mode="points",
        )
        try:
            clicked_points = selection.selection.points
            if clicked_points and clicked_points[0].get("curve_number") == 0:
                selected_idx = int(clicked_points[0]["point_index"])
                if 0 <= selected_idx < len(SYSTEMS):
                    selected_system = SYSTEMS[selected_idx]
        except (AttributeError, KeyError, TypeError, ValueError):
            pass
    with right:
        metric_key = SYSTEM_METRICS[selected_system]
        signal = SIGNALS[metric_key]
        st.markdown(f"### {selected_system}")
        st.write(f"**Tracked example:** {signal[0]} ({signal[1]})")
        summary = stats_by_metric.get(metric_key)
        if summary is not None:
            st.metric("Recent vs reference (demo)", f"{summary.delta:+.2f} {summary.unit}")
        else:
            st.warning("No descriptive comparison available for invalid/insufficient observations.")
        relevant = [f for f in flags if f.metric == metric_key]
        if issues:
            st.error("Interpretation blocked by data quality.")
        elif relevant:
            for f in relevant:
                st.warning(f.message)
        elif metric_key == "activity_minutes":
            st.info("Activity is visualized but has no demo review threshold.")
        else:
            st.info("No illustrative rule triggered for this signal.")
        for item in EVIDENCE:
            if item.indicator == metric_key:
                st.markdown(f"**Research context:** {item.title}")
                st.write(item.summary)
                st.caption(item.limitation)
                st.markdown(f"[Official source]({item.url})")
                break
        st.caption("Radiation exposure, bone density, and psychological diagnoses are not measured.")

with evidence_tab:
    st.subheader("Scientific Evidence Center")
    st.info(
        "These are external research references, not NASA measurements or validation "
        "of ARES clinical accuracy."
    )
    for item in EVIDENCE:
        with st.expander(f"{item.title} · {item.organization}"):
            st.write(item.summary)
            st.caption("Limitation: " + item.limitation)
            st.markdown(f"[Read the official publication]({item.url})")
    st.markdown("### Why interpretation must remain conservative")
    st.write(
        "The first seven synthetic days define an illustrative baseline and the final "
        "four define the recent window. A change of at least 12 bpm or 1.5 hours "
        "triggers an engineering review flag. These values are not NASA medical cutoffs."
    )

with review_tab:
    st.subheader("Mission review center")
    st.caption("Review an entirely fictional scenario. No diagnosis or autonomous treatment advice.")
    st.markdown(f"### {guidance.heading}")
    st.write(guidance.meaning)
    st.markdown("**Suggested non-clinical verification steps:**")
    for i, step in enumerate(guidance.review_steps, start=1):
        st.write(f"{i}. {step}")
    if issues:
        for issue in issues:
            st.error(issue)
    elif flags:
        for flag in flags:
            st.warning(flag.message)
    st.divider()
    review_state = st.selectbox("Review log state", ["Pending review", "Reviewed in demo"])
    note = st.text_area(
        "Optional reviewer note (fictional scenario only)",
        placeholder="Example: Confirmed synthetic input quality and reviewed comparison windows.",
        max_chars=500,
        help="Never enter real medical, personal or astronaut data.",
    )
    report = build_review_report(
        records, scenario=scenario_id, flags=flags,
        issues=issues, blocked=blocked, review_state=review_state, reviewer_note=note,
    )
    x, y = st.columns(2)
    with x:
        st.download_button(
            "Download review report (JSON)",
            data=json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False).encode("utf-8"),
            file_name=f"ares_review_{scenario_id}.json",
            mime="application/json", width="stretch",
        )
    with y:
        st.download_button(
            "Download demonstration CSV",
            records.to_csv(index=False).encode("utf-8"),
            file_name=f"ares_{scenario_id}.csv",
            mime="text/csv", width="stretch",
        )
    with st.expander("Inspect source records"):
        st.dataframe(records, hide_index=True, width="stretch")
    with st.expander("Methodology and limitations"):
        st.write(
            "Synthetic deterministic records only. CSV inputs are self-attested and checked "
            "for structure and quality, not independently verified as fictional. "
            "Software tests are not clinical validation. All engineering thresholds "
            "are illustrative; real mission decisions require authorized medical procedures."
        )

st.divider()
st.caption(
    "ARES Health AI v0.8 · Independent synthetic engineering demonstration · "
    "No real astronaut monitoring, NASA approval, diagnosis, or medical clearance."
)
