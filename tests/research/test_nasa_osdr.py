"""Offline NASA OSDR adapter tests. Fixtures contain invented mouse sample IDs.

No real NASA endpoint or human records are downloaded during CI.
"""
import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from src.ares_health import nasa_osdr
from src.ares_health.api import app

client = TestClient(app, client=("127.0.0.1", 12345))
EXAMPLE_FILE = {
    "file_name": nasa_osdr.SAMPLE_FILENAME,
    "category": "GeneLab Processed Microarray Data Files",
    "file_size": 290,
    "restricted": False,
    "visible": True,
    "remote_url": (
        "/geode-py/ws/studies/OSD-87/download?"
        "source=datamanager&file=" + nasa_osdr.SAMPLE_FILENAME
    ),
}
SECRET_FILE = {
    **EXAMPLE_FILE,
    "file_name": "GLDS-87_restricted.csv",
    "restricted": True,
    "remote_url": "/geode-py/ws/studies/OSD-87/download?source=datamanager&file=GLDS-87_restricted.csv",
}
SAMPLE_BYTES = b"Sample,Condition\nMOUSE_R1,flight\nMOUSE_R2,control\n"


def response(*files) -> bytes:
    return json.dumps({
        "hits": 1, "success": True, "input": "87",
        "studies": {"OSD-87": {"file_count": len(files), "study_files": list(files)}},
    }).encode()


def test_catalog_provenance_and_restricted_file_filtering():
    data = nasa_osdr.parse_file_catalog(response(EXAMPLE_FILE, SECRET_FILE))
    assert data["accession"] == "OSD-87"
    assert data["data_provenance"] == "public_space_biology_research"
    assert "Mus musculus" in data["organism"]
    assert data["mission_context"] == "STS-135"
    assert data["visible_public_files"] == 1
    assert data["file_catalog_count"] == 2
    assert data["file_categories"][0]["count"] == 1
    assert data["sample_preview_available"] is True
    assert len(data["files"]) == 1
    assert data["files"][0]["file_url"].startswith("https://osdr.nasa.gov/")


@pytest.mark.parametrize("case", [
    {"file_name": "OSD-999_fake.csv"},
    {"remote_url": "https://evil.example/oversized"},
    {"remote_url": "/geode-py/ws/studies/OSD-87/download?source=other&file=GLDS-87_array_SampleTable_GLmicroarray.csv"},
    {"remote_url": "/geode-py/ws/studies/OSD-87/download?source=datamanager&file=GLDS-87_wrong.csv"},
    {"file_size": -1},
    {"file_size": 2_000_000_000},
])
def test_invalid_nasa_file_metadata_rejected(case):
    bad = {**EXAMPLE_FILE, **case}
    with pytest.raises(ValueError):
        nasa_osdr.parse_file_catalog(response(bad))


def test_missing_restriction_flag_defaults_to_not_public():
    entry = dict(EXAMPLE_FILE)
    del entry["restricted"]
    data = nasa_osdr.parse_file_catalog(response(entry))
    assert data["files"] == []
    assert data["sample_preview_available"] is False


def test_invalid_catalog_cannot_be_mistaken_for_public_dataset():
    for raw in [b"{}", b'{"success":false}', b'{"success":true,"studies":{}}', b'{"success":true,"studies":{"OSD-87":{"file_count":0,"study_files":[]}},"value":NaN}']:
        with pytest.raises((ValueError, TypeError, KeyError)):
            nasa_osdr.parse_file_catalog(raw)


def test_small_mouse_sample_table_uses_source_values_without_derived_health_claims():
    catalog = nasa_osdr.parse_file_catalog(response(EXAMPLE_FILE))
    preview = nasa_osdr.parse_sample_table(SAMPLE_BYTES, catalog)
    assert preview["sample_count"] == 2
    assert preview["column_names"] == ["Sample", "Condition"]
    assert preview["rows"][0]["Sample"] == "MOUSE_R1"
    assert "mouse" in preview["disclaimer"].lower()
    assert "astronaut" in preview["disclaimer"].lower()
    assert preview["data_provenance"] == "public_space_biology_research"


def test_sample_table_cannot_be_read_without_approved_manifest():
    with pytest.raises(ValueError):
        nasa_osdr.parse_sample_table(SAMPLE_BYTES, {"accession": "OSD-87", "sample_preview_available": False})


def test_reject_malformed_sample_table():
    catalog = nasa_osdr.parse_file_catalog(response(EXAMPLE_FILE))
    for raw in [b"", b"Sample,Condition\nX", b"Sample,Sample\nX,Y\n", b"Sample,Condition\nX,Y,EXTRA\n", b"\x00"]:
        with pytest.raises((ValueError, UnicodeError)):
            nasa_osdr.parse_sample_table(raw, catalog)


def test_nasa_routes_are_disabled_by_default(monkeypatch):
    monkeypatch.delenv("ARES_RESEARCH_ENABLED", raising=False)
    for url in ["/api/research/nasa/study", "/api/research/nasa/sample-table"]:
        assert client.get(url).status_code == 503
    assert client.get("/api/demo").status_code == 200


def test_research_only_accessible_from_loopback(monkeypatch):
    monkeypatch.setenv("ARES_RESEARCH_ENABLED", "1")
    remote = TestClient(app, client=("198.51.100.5", 1234))
    assert remote.get("/api/research/nasa/study").status_code == 403


def test_offline_mock_nasa_endpoints_are_bound_and_distinct(monkeypatch):
    monkeypatch.setenv("ARES_RESEARCH_ENABLED", "1")
    requested = []
    def fake_download(url, limit):
        requested.append(url)
        return response(EXAMPLE_FILE, SECRET_FILE) if url == nasa_osdr.MANIFEST_API else SAMPLE_BYTES
    monkeypatch.setattr(nasa_osdr, "_bounded_download", fake_download)
    study = client.get("/api/research/nasa/study")
    assert study.status_code == 200, study.text
    assert study.json()["visible_public_files"] == 1
    table = client.get("/api/research/nasa/sample-table")
    assert table.status_code == 200, table.text
    assert table.json()["sample_count"] == 2
    assert len(requested) == 3
    assert requested.count(nasa_osdr.MANIFEST_API) == 2
    assert client.get("/api/demo").json()["data_provenance"] == "synthetic"


def test_network_failure_is_visible_as_unavailable_not_fake_results(monkeypatch):
    monkeypatch.setenv("ARES_RESEARCH_ENABLED", "1")
    def failed(_url, _limit):
        raise TimeoutError("official endpoint unreachable")
    monkeypatch.setattr(nasa_osdr, "_bounded_download", failed)
    response = client.get("/api/research/nasa/study")
    assert response.status_code == 503
    assert "no study result was invented" in response.json()["detail"]


def test_excessive_catalog_response_is_rejected_before_processing(monkeypatch):
    def excessive(_url, limit):
        assert limit == nasa_osdr.MAX_MANIFEST_BYTES
        raise ValueError("Response too large")
    monkeypatch.setattr(nasa_osdr, "_bounded_download", excessive)
    with pytest.raises(ValueError):
        nasa_osdr.load_file_catalog()
