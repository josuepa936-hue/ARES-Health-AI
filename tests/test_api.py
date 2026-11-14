"""HTTP contract tests for the synthetic-only local API."""
from __future__ import annotations

import json
import pytest
from fastapi.testclient import TestClient

from src.ares_health.api import app
from src.ares_health.import_csv import MAX_CSV_BYTES
from src.ares_health.synthetic import generate_scenario

client = TestClient(app)
HEADERS = {
    "Content-Type": "text/csv",
    "X-Synthetic-Attestation": "true",
}


def fictional_csv(scenario="stable"):
    return generate_scenario(scenario).to_csv(index=False).encode("utf-8")


def test_service_status_is_not_medical_clearance():
    res = client.get("/api/status")
    assert res.status_code == 200
    data = res.json()
    assert data["data_provenance"] == "synthetic-only"
    assert data["clinical_validation"] is False
    assert data["nasa_approved"] is False


def test_scenarios_keep_stable_ids_for_future_frontend():
    res = client.get("/api/scenarios")
    assert res.status_code == 200
    assert [s["id"] for s in res.json()["scenarios"]] == [
        "stable", "heart_rate_shift", "sleep_shift", "incomplete"
    ]


def test_official_evidence_is_context_not_data():
    res = client.get("/api/evidence")
    assert res.status_code == 200
    refs = res.json()["references"]
    assert len(refs) >= 4
    assert all(r["url"].startswith("https://") for r in refs)
    assert "not imported" in res.json()["usage"]


@pytest.mark.parametrize("scenario, expected_state", [
    ("stable", "NO_DEMO_RULE_TRIGGERED"),
    ("heart_rate_shift", "CHANGE_FOR_REVIEW"),
    ("sleep_shift", "CHANGE_FOR_REVIEW"),
    ("incomplete", "DATA_QUALITY_BLOCKED"),
])
def test_synthetic_scenarios_match_existing_rules(scenario, expected_state):
    res = client.get("/api/demo", params={"scenario": scenario})
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["assessment"] == expected_state
    assert len(data["observations"]) == 21
    assert data["summary"]["crew_id"] == "SIM-001"
    assert data["simulation_only"] is True
    assert data["guidance"]["state"] == expected_state
    assert len(data["descriptive_signals"]) == (0 if scenario == "incomplete" else 3)
    assert "not a medical alert" in data["descriptive_statistics_notice"]


def test_malformed_or_unsupported_scenario_is_rejected():
    for query in [
        {"scenario": "clinical"},
        {"days": 2},
        {"days": 500},
        {"seed": -1},
        {"seed": 1000000},
    ]:
        assert client.get("/api/demo", params=query).status_code == 422


def test_demo_is_deterministic_and_json_never_contains_nan():
    first = client.get("/api/demo", params={"seed": 42})
    second = client.get("/api/demo", params={"seed": 42})
    assert first.text == second.text
    data = client.get("/api/demo", params={"scenario": "incomplete"})
    assert data.status_code == 200
    assert data.json()["observations"][-1]["resting_hr_bpm"] is None
    assert data.json()["review_flags"] == []
    json.loads(data.text, parse_constant=lambda value: pytest.fail(f"nonfinite {value}"))


def test_reviewer_can_export_fictional_report():
    res = client.post("/api/review", json={
        "scenario": "heart_rate_shift",
        "review_state": "Reviewed in demo",
        "reviewer_note": "Checked fictional observation windows.",
    })
    assert res.status_code == 200
    report = res.json()
    assert report["review_state"] == "Reviewed in demo"
    assert report["assessment"] == "CHANGE_FOR_REVIEW"
    assert report["data_provenance"] == "synthetic"
    assert report["review_flags"]


def test_export_rejects_unsafe_review_fields():
    for payload in [
        {"review_state": "Diagnosed"},
        {"reviewer_note": "x" * 501},
        {"scenario": "patient_id_123"},
        {"days": 3},
    ]:
        assert client.post("/api/review", json=payload).status_code == 422


def test_synthetic_csv_attestation_is_required():
    res = client.post(
        "/api/synthetic-csv",
        content=fictional_csv(),
        headers={"Content-Type": "text/csv"},
    )
    assert res.status_code == 400
    assert "Attestation" in res.json()["detail"]


def test_synthetic_csv_rejects_other_mime_type():
    res = client.post(
        "/api/synthetic-csv",
        content=fictional_csv(),
        headers={"Content-Type": "application/json", "X-Synthetic-Attestation": "true"},
    )
    assert res.status_code == 415


def test_synthetic_csv_is_limited_to_one_megabyte():
    res = client.post(
        "/api/synthetic-csv",
        content=b"x" * (MAX_CSV_BYTES + 1),
        headers=HEADERS,
    )
    assert res.status_code == 413


def test_synthetic_csv_import_matches_builtin_logic():
    res = client.post(
        "/api/synthetic-csv",
        content=fictional_csv("heart_rate_shift"),
        headers=HEADERS,
    )
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["scenario"] == "uploaded_synthetic_csv"
    assert data["assessment"] == "CHANGE_FOR_REVIEW"
    assert len(data["observations"]) == 21
    assert data["review_report"]["assessment"] == "CHANGE_FOR_REVIEW"


def test_synthetic_csv_rejects_fake_provenance():
    res = client.post(
        "/api/synthetic-csv",
        content=fictional_csv().replace(b"SIM-001", b"patientA"),
        headers=HEADERS,
    )
    assert res.status_code == 422
    assert res.json()["detail"]["status"] == "CSV_REJECTED"


def test_synthetic_csv_rejects_incomplete_observations():
    res = client.post(
        "/api/synthetic-csv", content=fictional_csv("incomplete"), headers=HEADERS,
    )
    assert res.status_code == 422
    assert "errors" in res.json()["detail"]


def test_browser_cors_allows_only_local_dev_origins():
    local = client.options("/api/demo", headers={
        "Origin": "http://localhost:5173",
        "Access-Control-Request-Method": "GET",
    })
    assert local.headers.get("access-control-allow-origin") == "http://localhost:5173"
    remote = client.options("/api/demo", headers={
        "Origin": "https://example.com",
        "Access-Control-Request-Method": "GET",
    })
    assert remote.headers.get("access-control-allow-origin") is None
