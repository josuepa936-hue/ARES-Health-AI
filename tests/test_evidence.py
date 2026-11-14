"""Tests for evidence accuracy, deterministic guidance states and limitations."""
from urllib.parse import urlparse

from src.ares_health.analysis import review_changes
from src.ares_health.evidence import EVIDENCE, get_crew_guidance
from src.ares_health.synthetic import generate_scenario
from src.ares_health.validation import quality_issues


def guidance_for(scenario):
    frame = generate_scenario(scenario)
    flags, blocked = review_changes(frame)
    return get_crew_guidance(quality_issues(frame), blocked, flags)


def test_guidance_for_stable_is_not_medical_clearance():
    guidance = guidance_for("stable")
    assert guidance.state == "NO_DEMO_RULE_TRIGGERED"
    assert "not demonstrate" in guidance.meaning
    assert "medical clearance" in " ".join(guidance.review_steps)


def test_guidance_for_missed_measurements_blocks_interpretation():
    guidance = guidance_for("incomplete")
    assert guidance.state == "DATA_QUALITY_BLOCKED"
    assert "withheld" in guidance.meaning


def test_guidance_for_heart_rate_change_is_not_diagnosis():
    guidance = guidance_for("heart_rate_shift")
    assert guidance.state == "CHANGE_FOR_REVIEW"
    assert "not a medical risk estimate" in guidance.meaning
    assert "approved flight-medical procedures" in " ".join(guidance.review_steps)


def test_guidance_for_sleep_change():
    assert guidance_for("sleep_shift").state == "CHANGE_FOR_REVIEW"


def test_guidance_for_insufficient_data():
    guidance = get_crew_guidance([], ["Too few days"], [])
    assert guidance.state == "INSUFFICIENT_DATA"


def test_quality_failure_takes_priority_over_flags():
    frame = generate_scenario("heart_rate_shift")
    flags, _ = review_changes(frame)
    guidance = get_crew_guidance(["A missing observation"], [], flags)
    assert guidance.state == "DATA_QUALITY_BLOCKED"


def test_evidence_has_official_sources_and_explicit_limitations():
    assert len(EVIDENCE) >= 4
    assert {e.indicator for e in EVIDENCE} >= {
        "resting_hr_bpm", "sleep_hours", "activity_minutes", "context_only"
    }
    for item in EVIDENCE:
        parsed = urlparse(item.url)
        assert parsed.scheme == "https"
        assert parsed.hostname in {"www.nasa.gov", "www.asc-csa.gc.ca"}
        assert item.summary and item.limitation and item.title
    assert any("radiation" in item.limitation.lower() for item in EVIDENCE)


def test_all_guidance_has_steps_without_treatment_prescriptions():
    for scenario in ["stable", "incomplete", "heart_rate_shift", "sleep_shift"]:
        guidance = guidance_for(scenario)
        assert len(guidance.review_steps) >= 2
        assert not any(token in (" ".join(guidance.review_steps)).lower()
                       for token in ("take medication", "prescribe", "mg/day"))
