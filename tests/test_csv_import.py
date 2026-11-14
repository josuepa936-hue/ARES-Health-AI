"""CSV importer security, schema, and deterministic integration tests."""
from __future__ import annotations

import pytest

from src.ares_health.analysis import review_changes
from src.ares_health.import_csv import MAX_CSV_BYTES, load_synthetic_csv
from src.ares_health.review import build_review_report
from src.ares_health.synthetic import generate_scenario


def synthetic_csv(scenario="stable") -> bytes:
    return generate_scenario(scenario).to_csv(index=False).encode("utf-8")


@pytest.mark.parametrize("scenario", ["stable", "heart_rate_shift", "sleep_shift"])
def test_valid_synthetic_scenario_imports_and_analyzes(scenario):
    frame, issues = load_synthetic_csv(synthetic_csv(scenario))
    assert issues == []
    assert frame is not None
    assert len(frame) == 21
    assert frame["timestamp_utc"].dt.tz is not None
    flags, blocked = review_changes(frame)
    assert blocked == []
    assert bool(flags) == (scenario != "stable")
    report = build_review_report(
        frame, scenario="uploaded_synthetic_csv", flags=flags, issues=[]
    )
    assert report["assessment"] != "DATA_QUALITY_BLOCKED"


def test_valid_bom_and_reordered_columns():
    data = generate_scenario().loc[:, [
        "crew_id", "timestamp_utc", "sleep_hours", "resting_hr_bpm",
        "activity_minutes", "source_type",
    ]]
    frame, errors = load_synthetic_csv(("\ufeff" + data.to_csv(index=False)).encode("utf-8"))
    assert not errors
    assert frame is not None and len(frame) == 21


@pytest.mark.parametrize("payload,expected", [
    (b"", "empty"),
    (b"not really csv", "Columns"),
    (b"\xff\xfe", "UTF-8"),
    (b"x\x00y", "NUL"),
    (b"a,b\n\"unterminated", "Malformed"),
    (b"timestamp_utc,crew_id,resting_hr_bpm,sleep_hours,activity_minutes,source_type\n", "no observation"),
])
def test_reject_malformed_inputs(payload, expected):
    frame, errors = load_synthetic_csv(payload)
    assert frame is None
    assert any(expected.lower() in error.lower() for error in errors)


def test_reject_oversize():
    frame, errors = load_synthetic_csv(b"x" * (MAX_CSV_BYTES + 1))
    assert frame is None and "limit" in errors[0]


@pytest.mark.parametrize("mutation,expected", [
    (lambda s: s.replace("crew_id,", "crew_id,crew_id,"), "Duplicate column"),
    (lambda s: s.replace("crew_id,", "person_id,"), "Columns"),
    (lambda s: s.replace("synthetic", "verified_open"), "synthetic"),
    (lambda s: s.replace("SIM-001", "actual-patient"), "SIM-"),
    (lambda s: s.replace("+00:00", ""), "UTC"),
    (lambda s: s.replace("2026-11-02", "2026-11-01"), "Duplicate"),
    (lambda s: s.replace("2026-11-02", "2026-11-04"), "Duplicate"),
])
def test_reject_bad_provenance_or_structure(mutation, expected):
    source = synthetic_csv().decode()
    frame, errors = load_synthetic_csv(mutation(source).encode())
    assert frame is None
    assert any(expected.lower() in error.lower() for error in errors)


def test_reject_extra_cells_and_missing_cells():
    rows = synthetic_csv().decode().splitlines()
    rows[1] += ",EXTRA"
    assert load_synthetic_csv(("\n".join(rows)+"\n").encode())[0] is None
    rows = synthetic_csv().decode().splitlines()
    rows[1] = ",".join(rows[1].split(",")[:-1])
    assert load_synthetic_csv(("\n".join(rows)+"\n").encode())[0] is None


def test_reject_incomplete_measurement_without_interpreting():
    frame, errors = load_synthetic_csv(synthetic_csv("incomplete"))
    assert frame is None
    assert any("missing" in error.lower() for error in errors)


def test_does_not_write_uploaded_files(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())
    frame, errors = load_synthetic_csv(synthetic_csv())
    assert frame is not None and errors == []
    assert set(tmp_path.iterdir()) == before
