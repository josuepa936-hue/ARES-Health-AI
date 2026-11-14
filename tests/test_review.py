"""Deterministic checks for review report, not medical evaluation."""
import json

import pytest

from src.ares_health.analysis import quality_issues, review_changes
from src.ares_health.review import build_review_report
from src.ares_health.synthetic import generate_scenario


def create_report(scenario):
    records = generate_scenario(scenario)
    flags, blocked = review_changes(records)
    return build_review_report(
        records, scenario=scenario, flags=flags,
        issues=quality_issues(records), blocked=blocked,
    )


def test_review_report_marks_stable_as_non_clinical():
    result = create_report("stable")
    assert result["assessment"] == "NO_DEMO_RULE_TRIGGERED"
    assert result["review_flags"] == []
    assert "No astronaut measurements" in result["disclaimer"]


def test_review_report_includes_change_explanation():
    result = create_report("heart_rate_shift")
    assert result["assessment"] == "CHANGE_FOR_REVIEW"
    assert any(item["metric"] == "resting_hr_bpm" for item in result["review_flags"])
    assert "baseline_mean" in result["review_flags"][0]


def test_missing_records_block_report_assessment():
    result = create_report("incomplete")
    assert result["assessment"] == "DATA_QUALITY_BLOCKED"
    assert result["data_quality_issues"]
    assert result["review_flags"] == []


def test_json_is_serializable_and_reproducible():
    assert json.dumps(create_report("sleep_shift"), sort_keys=True) == json.dumps(
        create_report("sleep_shift"), sort_keys=True
    )


def test_reject_invalid_review_status_and_oversize_note():
    frame = generate_scenario("stable")
    with pytest.raises(ValueError):
        build_review_report(frame, scenario="stable", flags=[], issues=[], review_state="Diagnosed")
    with pytest.raises(ValueError):
        build_review_report(frame, scenario="stable", flags=[], issues=[], reviewer_note="a" * 501)
