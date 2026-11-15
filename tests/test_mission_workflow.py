"""End-to-end fictional check-in and spaceflight risk explorer contract tests."""
import math

import pytest
from fastapi.testclient import TestClient

from src.ares_health.api import app
from src.ares_health.mission import fictional_checkin, risk_guide

client = TestClient(app)
BASE = {
    "fictional_attestation": True,
    "scenario": "stable",
    "seed": 2026,
    "days": 21,
    "resting_hr_bpm": 140.0,
    "sleep_hours": 7.0,
    "activity_minutes": 45,
    "concerns": ["fatigue"],
}


def test_single_fictional_checkin_updates_last_day_and_reuses_all_domain_rules():
    response = client.post("/api/mission/fictional-check-in", json=BASE)
    assert response.status_code == 200, response.text
    result = response.json()
    assert result["data_provenance"] == "synthetic"
    assert result["simulation_only"] is True
    assert result["scenario"] == "stable_fictional_checkin"
    assert result["summary"]["recorded_days"] == 21
    assert result["observations"][-1]["resting_hr_bpm"] == 140.0
    assert result["observations"][-1]["sleep_hours"] == 7.0
    assert result["observations"][-1]["activity_minutes"] == 45
    assert result["assessment"] == "CHANGE_FOR_REVIEW"
    assert result["assessment"] == result["guidance"]["state"]
    assert result["assessment"] == result["mission_timeline"]["assessment"]
    assert result["assessment"] == result["review_report"]["assessment"]
    assert result["review_flags"] == result["review_report"]["review_flags"]
    assert result["check_in"]["timestamp_utc"] == result["observations"][-1]["timestamp_utc"]
    assert result["decision_support"]["reported_concerns"] == ["fatigue"]
    assert result["decision_support"]["clinical_decision_support"] is False
    assert result["mission_timeline"]["events"]


def test_repeated_fictional_checkin_is_reproducible_and_not_persisted():
    a = client.post("/api/mission/fictional-check-in", json=BASE).json()
    b = client.post("/api/mission/fictional-check-in", json=BASE).json()
    assert a == b
    baseline = client.get("/api/demo?scenario=stable&seed=2026&days=21").json()
    assert baseline["observations"][-1] != a["observations"][-1]
    assert baseline["assessment"] == "NO_DEMO_RULE_TRIGGERED"


@pytest.mark.parametrize("overrides", [
    {"fictional_attestation": False},
    {"fictional_attestation": None},
    {"scenario": "real_astronaut"},
    {"resting_hr_bpm": -1},
    {"resting_hr_bpm": 0},
    {"resting_hr_bpm": 260},
    {"sleep_hours": -1},
    {"sleep_hours": 30},
    {"activity_minutes": -1},
    {"activity_minutes": 1441},
    {"concerns": ["disease_diagnosis"]},
    {"concerns": ["fatigue", "fatigue"]},
    {"concerns": ["headache"] * 5},
    {"crew_name": "Real Name"},
    {"days": 3},
])
def test_checkin_refuses_invalid_unsourced_or_identifiable_payload(overrides):
    payload = {**BASE, **overrides}
    assert client.post("/api/mission/fictional-check-in", json=payload).status_code == 422


def test_attestation_is_required_not_default_true():
    payload = dict(BASE)
    payload.pop("fictional_attestation")
    assert client.post("/api/mission/fictional-check-in", json=payload).status_code == 422


def test_input_is_strictly_json_safe():
    for metric in ["resting_hr_bpm", "sleep_hours"]:
        payload = {**BASE, metric: float("inf")}
        assert client.post("/api/mission/fictional-check-in", json=payload).status_code == 422


def test_incomplete_scenario_never_accidentally_overrides_quality_gate():
    payload = {**BASE, "scenario": "incomplete", "resting_hr_bpm": 63}
    result = client.post("/api/mission/fictional-check-in", json=payload).json()
    assert result["assessment"] == "DATA_QUALITY_BLOCKED"
    assert result["review_flags"] == []
    assert result["descriptive_signals"] == []
    assert not any(x["type"] == "trend_change" for x in result["mission_timeline"]["events"])


def test_reported_hypothetical_symptom_is_never_medical_triage():
    payload = {**BASE, "concerns": ["dizziness", "headache"]}
    data = client.post("/api/mission/fictional-check-in", json=payload).json()
    assert data["decision_support"]["reported_concerns"] == ["dizziness", "headache"]
    assert data["decision_support"]["clinical_decision_support"] is False
    assert "authorized" in data["decision_support"]["concerns_notice"]
    assert "medication dosing" in data["decision_support"]["mission_procedures"]


def test_spaceflight_risk_explorer_has_five_hazards_without_risk_scores():
    result = client.get("/api/mission/risk-guide")
    assert result.status_code == 200
    data = result.json()
    risks = data["risks"]
    assert len(risks) == 5
    assert {x["id"] for x in risks} == {
        "radiation", "gravity", "isolation", "distance", "environment",
    }
    assert all(x["reference_url"].startswith("https://www.nasa.gov/") for x in risks)
    assert all("ares_current_coverage" in x for x in risks)
    assert all("risk_score" not in x for x in risks)
    assert "not NASA operational health guidance" in data["disclaimer"]


def test_csv_import_now_gets_matching_own_timeline_and_review():
    from src.ares_health.synthetic import generate_scenario
    raw = generate_scenario("heart_rate_shift").to_csv(index=False).encode()
    response = client.post("/api/synthetic-csv", content=raw, headers={
        "Content-Type": "text/csv", "X-Synthetic-Attestation": "true",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["assessment"] == "CHANGE_FOR_REVIEW"
    assert data["mission_timeline"]["assessment"] == data["assessment"]
    assert data["mission_timeline"]["scenario"] == "uploaded_synthetic_csv"
    assert len(data["mission_timeline"]["events"]) >= 21
    assert data["review_report"]["scenario"] == "uploaded_synthetic_csv"
    assert data["simulation_only"] is True
