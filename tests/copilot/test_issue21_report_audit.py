"""Issue #21: comprehensive export status, metadata, UTC audit and legacy compatibility."""
import copy
import json

import pytest
from fastapi.testclient import TestClient

from src.ares_health.api import app
from src.ares_health.version import APP_VERSION

client = TestClient(app)
SOURCE = {"kind": "scenario", "scenario": "stable", "seed": 2026, "days": 21}
TIMES = [
    "2026-11-15T07:00:00.111Z",
    "2026-11-15T07:00:01.222Z",
    "2026-11-15T07:00:02.333Z",
]


def payload(*, state="IN_PROGRESS"):
    briefing = client.post("/api/mission/copilot", json={"context": SOURCE}).json()
    return {
        "context": SOURCE,
        "fictional_attestation": True,
        "expected_context_ref": briefing["context_ref"],
        "questions": [{"turn": 1, "question": "What changed?"}],
        "audit_log": [
            {"sequence": 1, "action": "note", "note": "cardiovascular",
             "recorded_at_utc": TIMES[0]},
            {"sequence": 2, "action": "source_units", "checked": True,
             "recorded_at_utc": TIMES[1]},
            {"sequence": 3, "action": "review_state", "review_state": state,
             "recorded_at_utc": TIMES[2]},
        ],
    }


@pytest.mark.parametrize("status", [
    "PENDING_REVIEW", "IN_PROGRESS", "AWAITING_AUTHORIZED_REVIEW", "DOCUMENTED",
])
def test_comprehensive_report_has_one_canonical_review_state(status):
    response = client.post("/api/mission/comprehensive-report", json=payload(state=status))
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["review_state"] == status == data["fictional_review"]["review_state"]
    assert data["assessment"] == "NO_DEMO_RULE_TRIGGERED"
    assert data["fictional_review"]["clinical_authorization"] is False
    assert data["fictional_review"]["actions"]["source_units"] is True
    assert data["reviewer_note"] == "cardiovascular"
    assert data["legacy_review_state"] == (
        "Reviewed in demo" if status == "DOCUMENTED" else "Pending review"
    )
    assert "Compatibility-only" in data["legacy_review_state_semantics"]
    assert data["fictional_review"]["audit_log"] == payload(state=status)["audit_log"]
    assert data["fictional_review"]["audit_timestamps_complete"] is True
    assert "not independently authenticated" in data["fictional_review"]["audit_timestamp_source"]
    json.dumps(data, allow_nan=False)


def test_application_version_consistent_but_schema_versions_stay_independent():
    data = client.post("/api/mission/comprehensive-report", json=payload()).json()
    assert data["application_version"] == APP_VERSION
    assert data["copilot_application_version"] == APP_VERSION
    assert data["mission_timeline"]["application_version"] == APP_VERSION
    assert data["schema_version"] == "1.0-demo"
    assert data["copilot_schema_version"] == "1.5-demo"
    assert data["mission_timeline"]["schema_version"] == "1.0-timeline"
    assert client.get("/openapi.json").json()["info"]["version"] == APP_VERSION
    assert client.get("/api/status").json()["application_version"] == APP_VERSION
    standalone = client.post("/api/review", json={"scenario": "stable"}).json()
    assert standalone["application_version"] == APP_VERSION
    assert standalone["review_state"] == "Pending review"
    assert "fictional_review" not in standalone
    assert "legacy_review_state" not in standalone


def test_older_client_without_audit_time_still_exports_honestly():
    older = payload()
    for item in older["audit_log"]:
        del item["recorded_at_utc"]
    data = client.post("/api/mission/comprehensive-report", json=older).json()
    assert data["fictional_review"]["audit_timestamps_complete"] is False
    assert all("recorded_at_utc" not in e for e in data["fictional_review"]["audit_log"])
    assert data["review_state"] == "IN_PROGRESS"


@pytest.mark.parametrize("invalid", [
    "2026-11-15T07:00:01+00:00",
    "2026-11-15",
    "2026-11-15T07:00:01",
    "2026-02-30T07:00:01Z",
    "2026-11-15T07:00:01-06:00",
    "2026-11-15T07:00:01.1234567Z",
    "tomorrow", 123, True,
])
def test_invalid_or_non_utc_device_audit_time_rejected(invalid):
    bad = payload()
    bad["audit_log"][0]["recorded_at_utc"] = invalid
    result = client.post("/api/mission/comprehensive-report", json=bad)
    assert result.status_code == 422, result.text


def test_decreasing_audit_timestamps_rejected_without_reordering():
    bad = payload()
    bad["audit_log"][1]["recorded_at_utc"] = "2026-11-15T06:00:00.001Z"
    response = client.post("/api/mission/comprehensive-report", json=bad)
    assert response.status_code == 422


def test_legacy_binary_review_endpoint_still_supports_older_clients():
    data = client.post("/api/review", json={
        "scenario": "heart_rate_shift", "review_state": "Reviewed in demo",
    }).json()
    assert data["review_state"] == "Reviewed in demo"
    assert data["assessment"] == "CHANGE_FOR_REVIEW"
    assert data["application_version"] == APP_VERSION
