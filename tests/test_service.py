"""Domain contract tests shared by existing and future ARES interfaces."""
import json
import pytest

from src.ares_health.service import build_snapshot
from src.ares_health.synthetic import generate_scenario


@pytest.mark.parametrize("scenario", [
    "stable", "heart_rate_shift", "sleep_shift", "incomplete"
])
def test_snapshot_status_matches_revalidated_json_export(scenario):
    records = generate_scenario(scenario)
    snapshot = build_snapshot(records, scenario=scenario, include_report=True)
    assert snapshot["assessment"] == snapshot["review_report"]["assessment"]
    assert snapshot["review_flags"] == snapshot["review_report"]["review_flags"]
    assert snapshot["guidance"]["state"] == snapshot["assessment"]


def test_missing_values_are_json_null_not_nan():
    snapshot = build_snapshot(generate_scenario("incomplete"), scenario="incomplete")
    assert snapshot["observations"][-1]["resting_hr_bpm"] is None
    assert snapshot["observations"][-1]["sleep_hours"] is None
    assert snapshot["review_flags"] == []
    json.dumps(snapshot, allow_nan=False)


def test_summary_and_units_are_stable():
    snapshot = build_snapshot(generate_scenario(), scenario="stable")
    assert snapshot["summary"]["recorded_days"] == 21
    assert snapshot["summary"]["completeness_pct"] == 100.0
    assert len(snapshot["observations"]) == 21
    assert snapshot["observations"][0]["timestamp_utc"].endswith("Z")
    assert set(snapshot["observations"][0]) == {
        "timestamp_utc", "crew_id", "resting_hr_bpm",
        "sleep_hours", "activity_minutes", "source_type"
    }
    assert len(snapshot["descriptive_signals"]) == 3
    assert snapshot["methodology"]["reference_days"] == 7
    assert snapshot["methodology"]["recent_days"] == 4
    assert "activity_minutes" not in snapshot["methodology"]["illustrative_rules"]


def test_missing_measurements_reduces_completeness_without_mean():
    snapshot = build_snapshot(generate_scenario("incomplete"), scenario="incomplete")
    assert snapshot["summary"]["completeness_pct"] < 100.0
    assert snapshot["summary"]["review_flags"] == 0
    assert snapshot["quality_issues"]
    assert snapshot["analysis_limitations"] == []
    assert snapshot["descriptive_signals"] == []


def test_report_review_state_and_note_preserved():
    snapshot = build_snapshot(
        generate_scenario(), scenario="stable", include_report=True,
        review_state="Reviewed in demo", reviewer_note="Fictional scenario only",
    )
    assert snapshot["review_report"]["review_state"] == "Reviewed in demo"
    assert snapshot["review_report"]["reviewer_note"] == "Fictional scenario only"
