"""Regression tests for optional, grounded and offline wellness procedures."""
import json

import pytest
from fastapi.testclient import TestClient

from src.ares_health.api import app
from src.ares_health.copilot import canonical_context
from src.ares_health.copilot_models import ScenarioContext
from src.ares_health.wellness import build_wellness

client = TestClient(app)


def source(scenario="stable"):
    return {"kind": "scenario", "scenario": scenario, "seed": 2026, "days": 21}


@pytest.mark.parametrize(
    "scenario,expected",
    [
        ("stable", "NO_DEMO_RULE_TRIGGERED"),
        ("heart_rate_shift", "CHANGE_FOR_REVIEW"),
        ("sleep_shift", "CHANGE_FOR_REVIEW"),
        ("incomplete", "DATA_QUALITY_BLOCKED"),
    ],
)
def test_wellness_is_canonical_educational_context(scenario, expected):
    response = client.post("/api/mission/wellness", json={"context": source(scenario)})
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["assessment"] == expected
    assert data["provenance"] == "synthetic"
    assert data["demo_only"] is True
    assert data["clinical_decision_support"] is False
    assert data["automated_reminders"] is False
    assert len(data["topics"]) == 3
    assert {t["metric"] for t in data["topics"]} == {
        "resting_hr_bpm", "sleep_hours", "activity_minutes"
    }
    assert all(t["source_url"].startswith("https://www.nasa.gov/") for t in data["topics"])
    assert all("review_step" in t and "limitation" in t for t in data["topics"])
    json.dumps(data, allow_nan=False)


def test_wellness_same_context_as_copilot_not_new_assessment():
    body = {"context": source("heart_rate_shift")}
    briefing = client.post("/api/mission/copilot", json=body).json()
    wellness = client.post("/api/mission/wellness", json={
        **body, "expected_context_ref": briefing["context_ref"]
    }).json()
    assert wellness["context_ref"] == briefing["context_ref"]
    assert wellness["assessment"] == briefing["assessment"]
    assert wellness["topics"][0]["illustrative_flag"] is True


def test_incomplete_quality_never_has_trend_or_fabricated_mean():
    guide = client.post("/api/mission/wellness", json={"context": source("incomplete")}).json()
    assert all(t["comparison"] == "withheld" for t in guide["topics"])
    assert all(not t["illustrative_flag"] for t in guide["topics"])
    assert "no" in guide["summary"].lower() or "data" in guide["summary"].lower()
    assert not any("baseline_mean" in t or "recent_mean" in t for t in guide["topics"])


def test_stale_context_and_injected_untrusted_fields_rejected():
    old = client.post("/api/mission/copilot", json={"context": source("stable")}).json()
    result = client.post("/api/mission/wellness", json={
        "context": source("heart_rate_shift"),
        "expected_context_ref": old["context_ref"],
    })
    assert result.status_code == 409
    injected = client.post("/api/mission/wellness", json={
        "context": {**source(), "assessment": "NO_DEMO_RULE_TRIGGERED"},
    })
    assert injected.status_code == 422


def test_wellness_no_personal_upload_or_unattested_csv():
    response = client.post("/api/mission/wellness", json={
        "context": {"kind": "synthetic_csv", "csv": "private data"}
    })
    assert response.status_code == 422


def test_fictional_checkin_context_is_recomputed():
    body = {
        "context": {
            **source(),
            "check_in": {
                "fictional_attestation": True,
                "resting_hr_bpm": 140,
                "sleep_hours": 7,
                "activity_minutes": 45,
                "concerns": [],
            },
        },
    }
    guide = client.post("/api/mission/wellness", json=body).json()
    briefing = client.post("/api/mission/copilot", json=body).json()
    assert guide["context_ref"] == briefing["context_ref"]
    assert guide["assessment"] == briefing["assessment"]


def test_core_is_bounded_deterministic_and_does_not_need_a_model():
    context = canonical_context(ScenarioContext.model_validate(source()))
    assert build_wellness(context) == build_wellness(context)
    assert len(build_wellness(context)["topics"]) == 3
