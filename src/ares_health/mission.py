"""Integrated fictional mission workflow: check-in, review and spaceflight context.

No independently validated thresholds, diagnosis, treatment or operational
flight clearance. All data stay fictional/in-memory and analytical decisions
are delegated to the already-tested domain engine.
"""
from __future__ import annotations

from typing import Any
from src.ares_health.service import build_snapshot
from src.ares_health.synthetic import generate_scenario
from src.ares_health.timeline import build_timeline

NASA_HAZARDS_URL = "https://www.nasa.gov/hrp/hazards/"
SYMPTOMS = ("fatigue", "headache", "dizziness", "sleepiness")
RISKS: tuple[dict[str, Any], ...] = (
    {
        "id": "radiation",
        "title": "Space radiation",
        "body_region": "whole_body",
        "spaceflight_context": "Exposure to space radiation is a major NASA human-spaceflight hazard.",
        "candidate_observations": ["dosimetry", "mission exposure records"],
        "ares_current_coverage": "Context only; ARES has no dosimeter or radiation sensor.",
        "crew_review": "Review mission environmental monitoring and approved radiation procedures with authorized personnel.",
        "reference_url": NASA_HAZARDS_URL,
    },
    {
        "id": "gravity",
        "title": "Altered gravity",
        "body_region": "musculoskeletal",
        "spaceflight_context": "Altered gravity affects the body's adaptation during space missions.",
        "candidate_observations": ["daily activity", "exercise records", "fitness assessments"],
        "ares_current_coverage": "Fictional activity minutes only; not bone mass or strength.",
        "crew_review": "Review the fictional activity history and consult the mission exercise protocol.",
        "reference_url": NASA_HAZARDS_URL,
    },
    {
        "id": "isolation",
        "title": "Isolation and confinement",
        "body_region": "head",
        "spaceflight_context": "Isolation and confinement can influence behavior, sleep and performance.",
        "candidate_observations": ["sleep diary", "crew-reported concerns"],
        "ares_current_coverage": "Fictional sleep duration and hypothetical check-in concerns; no mental-health assessment.",
        "crew_review": "Review sleep schedules and support resources defined by the mission, not this prototype.",
        "reference_url": NASA_HAZARDS_URL,
    },
    {
        "id": "distance",
        "title": "Distance from Earth",
        "body_region": "whole_body",
        "spaceflight_context": "Greater distance introduces constraints on communication and medical support.",
        "candidate_observations": ["communication status", "mission procedures"],
        "ares_current_coverage": "No communication-delay or telemedicine capability in ARES.",
        "crew_review": "Use the actual mission's communication and flight-medical escalation procedures.",
        "reference_url": NASA_HAZARDS_URL,
    },
    {
        "id": "environment",
        "title": "Hostile or closed environments",
        "body_region": "cardiovascular",
        "spaceflight_context": "Closed environments introduce environmental and habitability considerations.",
        "candidate_observations": ["environmental sensor readings", "crew observations"],
        "ares_current_coverage": "Fictional resting heart rate is shown; cabin air and temperature are not measured.",
        "crew_review": "Consult environmental monitoring, mission safety instructions and approved flight medical procedures.",
        "reference_url": NASA_HAZARDS_URL,
    },
)


def risk_guide() -> dict[str, Any]:
    """Public background/context, not a calibrated hazard assessment."""
    return {
        "source": "NASA Human Research Program — Five Hazards of Human Spaceflight",
        "reference_url": NASA_HAZARDS_URL,
        "risks": list(RISKS),
        "disclaimer": (
            "Educational NASA hazard context, not NASA operational health guidance "
            "or patient-specific recommendations. No hazard risk score is calculated."
        ),
    }


def _decision_support(assessment: str, concerns: list[str]) -> dict[str, Any]:
    """Explain an engineering assessment without medical triage."""
    if assessment == "DATA_QUALITY_BLOCKED":
        next_step = "Verify missing/invalid records before interpreting any trend."
    elif assessment == "CHANGE_FOR_REVIEW":
        next_step = "Review measurement context and discuss any mission concern with authorized flight-medical personnel."
    elif assessment == "INSUFFICIENT_DATA":
        next_step = "Continue fictional observation collection; no comparison is available."
    else:
        next_step = "Review the observations; absence of a demo flag is not medical clearance."
    if concerns:
        note = (
            "Hypothetical concerns were reported. ARES does not assess their severity. "
            "In an actual mission, follow authorized flight-medical and emergency procedures."
        )
    else:
        note = "No hypothetical concern selected; this does not indicate medical fitness."
    return {
        "assessment": assessment,
        "review_action": next_step,
        "reported_concerns": list(concerns),
        "concerns_notice": note,
        "mission_procedures": (
            "If a real crew member needs assistance, use approved mission medical procedures "
            "and contact the designated flight surgeon or authorized personnel. "
            "Do not use ARES to select treatments, emergency severity, or medication dosing."
        ),
        "clinical_decision_support": False,
    }


def fictional_checkin(
    *,
    scenario: str,
    seed: int,
    days: int,
    resting_hr_bpm: float,
    sleep_hours: float,
    activity_minutes: int,
    concerns: list[str],
) -> dict[str, Any]:
    """Apply an attested fictional check-in to the latest deterministic demo day.

    Never adds patient data, persists records or extrapolates medical status.
    Earlier 20 observations remain reproducibly generated and unchanged.
    """
    if any(value not in SYMPTOMS for value in concerns) or len(concerns) != len(set(concerns)):
        raise ValueError("Invalid or repeated hypothetical concern.")
    frame = generate_scenario(scenario, seed=seed, days=days).copy(deep=True)
    final = frame.index[-1]
    frame.at[final, "resting_hr_bpm"] = resting_hr_bpm
    frame.at[final, "sleep_hours"] = sleep_hours
    frame.at[final, "activity_minutes"] = activity_minutes
    result = build_snapshot(frame, scenario=f"{scenario}_fictional_checkin", include_report=True)
    result["mission_timeline"] = build_timeline(frame, scenario=result["scenario"])
    result["check_in"] = {
        "timestamp_utc": result["observations"][-1]["timestamp_utc"],
        "fictional_attestation": True,
        "mode": "fictional_latest_day_override",
        "reported_concerns": list(concerns),
        "notice": (
            "Only the latest fictional observation was replaced in memory. "
            "These are not real astronaut or personal health records."
        ),
    }
    result["decision_support"] = _decision_support(result["assessment"], concerns)
    return result
