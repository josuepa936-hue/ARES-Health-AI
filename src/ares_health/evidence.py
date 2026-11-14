"""Human-readable mission context grounded in linked NASA/CSA resources.

Research context only. No astronaut data, dosing, diagnoses or clinical
thresholds are provided by this module.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Sequence

from src.ares_health.analysis import ReviewFlag


@dataclass(frozen=True)
class EvidenceItem:
    indicator: str
    title: str
    organization: str
    url: str
    summary: str
    limitation: str


EVIDENCE: tuple[EvidenceItem, ...] = (
    EvidenceItem(
        "resting_hr_bpm",
        "Risk of Cardiovascular Adaptations",
        "NASA Human Research Program",
        "https://www.nasa.gov/reference/risk-of-cardiovascular-adaptations/",
        "Spaceflight stressors can change the cardiovascular system. The prototype displays "
        "a simulated resting heart-rate trend as one illustrative measurement.",
        "Heart-rate trends alone cannot identify cardiovascular disease or the need for treatment.",
    ),
    EvidenceItem(
        "sleep_hours",
        "Risk from Inadequate Sleep and Irregular Schedules",
        "NASA Human Research Program",
        "https://www.nasa.gov/reference/risk-from-inadequate-sleep-and-irregular-schedules/",
        "Sleep loss and irregular schedules are studied as human-spaceflight performance risks. "
        "ARES displays fictional sleep duration over time.",
        "Sleep duration alone does not measure sleep quality, circadian alignment or mental health.",
    ),
    EvidenceItem(
        "activity_minutes",
        "Risk of Reduced Cardiorespiratory and Musculoskeletal Fitness",
        "NASA Human Research Program",
        "https://www.nasa.gov/reference/risk-of-reduced-cardiorespiratory-and-musculoskeletal-fitness/",
        "NASA studies exercise and fitness in microgravity. ARES displays illustrative daily "
        "activity minutes to help users inspect a trend.",
        "Activity minutes alone cannot establish fitness, prescribed exercise adherence or injury risk.",
    ),
    EvidenceItem(
        "context_only",
        "Five Hazards of Human Spaceflight",
        "NASA Human Research Program",
        "https://www.nasa.gov/hrp/hazards/",
        "NASA describes radiation, isolation and confinement, distance from Earth, altered gravity, "
        "and hostile or closed environments as major spaceflight hazards.",
        "ARES does not measure these hazards or estimate exposure-related health risks.",
    ),
    EvidenceItem(
        "context_only",
        "Monitoring Radiation for Astronaut Health",
        "Canadian Space Agency",
        "https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp",
        "The Canadian Space Agency describes technology for monitoring astronaut radiation exposure.",
        "ARES has no radiation sensor, dosimeter, or radiation-exposure input. This is background only.",
    ),
)


@dataclass(frozen=True)
class CrewGuidance:
    state: str
    heading: str
    meaning: str
    review_steps: tuple[str, ...]


def get_crew_guidance(
    issues: Sequence[str],
    blocked: Sequence[str],
    flags: Sequence[ReviewFlag],
) -> CrewGuidance:
    """Translate an existing engineering result into plain-language review steps.

    Never suggests a diagnosis, treatment, an emergency severity level, or
    independent medical action based on fabricated thresholds.
    """
    if issues:
        return CrewGuidance(
            "DATA_QUALITY_BLOCKED",
            "Measurements need verification",
            "One or more required simulated observations are missing or invalid. "
            "ARES has intentionally withheld trend interpretation.",
            (
                "Inspect which fields and timestamps have a quality problem.",
                "Verify the source record and correct it outside ARES before retrying.",
                "Do not treat a blocked analysis as a healthy or unhealthy finding.",
            ),
        )
    if blocked:
        return CrewGuidance(
            "INSUFFICIENT_DATA",
            "Not enough consistent observations",
            "The demonstration cannot compare its reference and recent windows.",
            (
                "Review the available timestamps and sampling consistency.",
                "Continue the simulated data collection or choose a longer fictional dataset.",
                "Avoid interpreting an unavailable trend as a medical conclusion.",
            ),
        )
    if flags:
        return CrewGuidance(
            "CHANGE_FOR_REVIEW",
            "An illustrative trend changed",
            "One or more simulated means differ from the initial reference by a "
            "demonstration-only setting; this is not a medical risk estimate.",
            (
                "Read the flagged measurement, unit, baseline and recent window.",
                "Inspect the underlying observations and verify measurement context.",
                "For any real mission, follow approved flight-medical procedures and "
                "consult authorized personnel rather than relying on this prototype.",
            ),
        )
    return CrewGuidance(
        "NO_DEMO_RULE_TRIGGERED",
        "No illustrative change rule triggered",
        "The fictional values did not meet ARES demonstration rules. "
        "This does not demonstrate that a person is medically safe or healthy.",
        (
            "Review the sample data and any relevant trends.",
            "Confirm the observed measurements and limitations of the simulation.",
            "Do not use the absence of a flag as a medical clearance.",
        ),
    )
