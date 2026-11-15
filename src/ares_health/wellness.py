"""Evidence-linked educational mission wellness review. No clinical recommendations.

All state is derived from the canonical Python snapshot, not browser-supplied
clinical assertions. It is not a scheduled reminder or a medical protocol.
"""
from __future__ import annotations

from src.ares_health.evidence import EVIDENCE

SOURCES = {item.indicator: item for item in EVIDENCE if item.indicator != "context_only"}

TOPICS = (
    (
        "cardiovascular",
        "resting_hr_bpm",
        "Cardiovascular observation",
        "NASA studies cardiovascular adaptation to spaceflight, but a resting heart-rate trend alone cannot determine illness or treatment.",
        "Check the fictional measurement source, unit, timestamp, and reference interval. Record any uncertainty for review.",
        "In a simulated check-in, verify that the measurement context is documented.",
    ),
    (
        "sleep",
        "sleep_hours",
        "Sleep and schedule",
        "NASA studies disrupted sleep and circadian schedules during spaceflight; light-dark timing and planned rest are relevant research topics.",
        "Review the fictional sleep log and schedule context. For any real mission, follow its approved rest and crew-support procedures.",
        "In a simulated routine, record sleep duration and whether a schedule change should be documented.",
    ),
    (
        "movement",
        "activity_minutes",
        "Movement and exercise context",
        "NASA studies exercise countermeasures to reduced cardiorespiratory and musculoskeletal fitness in microgravity.",
        "Review fictional activity entries and their provenance. The number of minutes does not establish fitness or prescribe exercise.",
        "In a simulated routine, document activity observations and consult the mission's approved exercise plan.",
    ),
)

STATES = {
    "NO_DEMO_RULE_TRIGGERED": (
        "No illustrative rule was triggered. This is not medical clearance. "
        "Reviewing fictional observations remains an educational exercise."
    ),
    "CHANGE_FOR_REVIEW": (
        "One or more demonstration-only changes merit record review. "
        "Inspect the flagged metric and timestamps; do not infer clinical severity."
    ),
    "DATA_QUALITY_BLOCKED": (
        "Data quality blocks interpretation. Verify missing or invalid source records "
        "before considering a comparison; no normality or trend is inferred."
    ),
    "INSUFFICIENT_DATA": (
        "There are too few consistent fictional observations to compare windows. "
        "Review sampling dates, not a purported health trend."
    ),
}


def build_wellness(context: dict) -> dict:
    snapshot = context["snapshot"]
    status = snapshot["assessment"]
    if status not in STATES:
        raise ValueError("Unsupported canonical mission assessment.")
    blocked = status in ("DATA_QUALITY_BLOCKED", "INSUFFICIENT_DATA")
    flagged = {flag["metric"] for flag in snapshot.get("review_flags", [])}
    topics = []
    for topic_id, metric, title, research, review, routine in TOPICS:
        reference = SOURCES[metric]
        topics.append({
            "id": topic_id,
            "metric": metric,
            "title": title,
            "research_context": research,
            "review_step": (
                "Comparison unavailable: verify source completeness and measurement quality. "
                "Do not infer a trend from missing data."
                if blocked else review
            ),
            "routine_example": routine,
            "comparison": "withheld" if blocked else "available",
            "illustrative_flag": bool(not blocked and metric in flagged),
            "source_title": reference.title,
            "source_url": reference.url,
            "source_organization": reference.organization,
            "limitation": reference.limitation,
        })
    return {
        "context_ref": context["context_ref"],
        "scenario": snapshot["scenario"],
        "assessment": status,
        "summary": STATES[status],
        "topics": topics,
        "provenance": "synthetic",
        "demo_only": True,
        "clinical_decision_support": False,
        "automated_reminders": False,
        "disclaimer": (
            "Education and fictional workflow only. No diagnosis, treatment, exercise "
            "prescription, operational medical clearance or NASA endorsement. "
            "A real mission requires approved flight-medical procedures and authorized personnel."
        ),
    }
