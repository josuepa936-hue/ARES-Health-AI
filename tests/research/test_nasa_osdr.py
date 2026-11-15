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


@pytest.mark.parametrize("url, sample, expected", [
    (nasa_osdr.MANIFEST_API, False, True),
    ("https://osdr.nasa.gov/geode-py/ws/studies/OSD-87/download?source=datamanager&file=" + nasa_osdr.SAMPLE_FILENAME, True, True),
    ("https://nasa-osdr.s3.us-west-2.amazonaws.com/OSD-87/version-1/" + nasa_osdr.SAMPLE_FILENAME, True, True),
    ("https://nasa-osdr.s3.amazonaws.com/OSD-87/version-1/" + nasa_osdr.SAMPLE_FILENAME, True, True),
    ("https://s3.us-west-2.amazonaws.com/nasa-osdr/OSD-87/version-1/" + nasa_osdr.SAMPLE_FILENAME, True, True),
    ("https://nasa-osdr.s3.us-west-2.amazonaws.com/OSD-87/version-1/" + nasa_osdr.SAMPLE_FILENAME, False, False),
    ("https://genelab-repo-prod.s3.amazonaws.com/genelab-data/GLDS-87/array/" + nasa_osdr.SAMPLE_FILENAME, True, True),
    ("https://genelab-repo-prod.s3.amazonaws.com/genelab-data/GLDS-87/array/" + nasa_osdr.SAMPLE_FILENAME, False, False),
    ("https://genelab-repo-prod.s3.amazonaws.com/genelab-data/GLDS-87/array/unapproved.csv", True, False),
    ("https://genelab-repo-prod.s3.amazonaws.com/genelab-data/GLDS-88/array/" + nasa_osdr.SAMPLE_FILENAME, True, False),
    ("https://genelab-repo-prod.s3.amazonaws.com.evil.example/genelab-data/GLDS-87/array/" + nasa_osdr.SAMPLE_FILENAME, True, False),
    ("http://genelab-repo-prod.s3.amazonaws.com/genelab-data/GLDS-87/array/" + nasa_osdr.SAMPLE_FILENAME, True, False),
    ("https://evil.example/OSD-87/" + nasa_osdr.SAMPLE_FILENAME, True, False),
    ("http://nasa-osdr.s3.us-west-2.amazonaws.com/OSD-87/" + nasa_osdr.SAMPLE_FILENAME, True, False),
    ("https://nasa-osdr.s3.us-west-2.amazonaws.com/OSD-999/" + nasa_osdr.SAMPLE_FILENAME, True, False),
    ("https://nasa-osdr.s3.us-west-2.amazonaws.com/OSD-87/not-approved.csv", True, False),
    ("https://osdr.nasa.gov/geode-py/ws/studies/OSD-88/download?source=datamanager&file=" + nasa_osdr.SAMPLE_FILENAME, True, False),
    ("https://user:secret@osdr.nasa.gov/osdr/data/osd/files/87", False, False),
])
def test_only_allowlisted_nasa_study_and_public_aws_redirects(url, sample, expected):
    assert nasa_osdr._approved_research_url(url, sample=sample) is expected


def test_bad_redirect_error_is_specific_without_exposing_external_host(monkeypatch):
    monkeypatch.setenv("ARES_RESEARCH_ENABLED", "1")
    def failed(_url, _limit):
        raise ValueError("NASA file download redirected to an unapproved destination.")
    monkeypatch.setattr(nasa_osdr, "_bounded_download", failed)
    reply = client.get("/api/research/nasa/sample-table")
    assert reply.status_code == 503
    assert "unapproved redirect" in reply.json()["detail"]
    assert "no study result was invented" in reply.json()["detail"]


def test_nasa_http_rejection_is_transparent_but_not_a_fake_study(monkeypatch):
    from urllib.error import HTTPError
    monkeypatch.setenv("ARES_RESEARCH_ENABLED", "1")
    def failed(_url, _limit):
        raise HTTPError(nasa_osdr.MANIFEST_API, 403, "Forbidden", {}, None)
    monkeypatch.setattr(nasa_osdr, "_bounded_download", failed)
    reply = client.get("/api/research/nasa/sample-table")
    assert reply.status_code == 503
    assert "HTTP 403" in reply.json()["detail"]
    assert reply.json().get("study") is None


def test_gene_lab_redirect_is_exact_single_file_not_a_bucket_allowance():
    source = (
        "https://genelab-repo-prod.s3.amazonaws.com"
        "/genelab-data/GLDS-87/array/"
        "GLDS-87_array_SampleTable_GLmicroarray.csv"
    )
    assert nasa_osdr._approved_research_url(source, sample=True)
    assert not nasa_osdr._approved_research_url(
        source.replace("GLDS-87_array_SampleTable_GLmicroarray.csv", "secret.txt"),
        sample=True,
    )
    assert not nasa_osdr._approved_research_url(
        source.replace("genelab-repo-prod.s3.amazonaws.com", "genelab-repo-prod.s3.amazonaws.com.evil.test"),
        sample=True,
    )


def test_catalog_and_sample_file_have_different_bounded_timeouts(monkeypatch):
    calls = []
    class FakeResponse:
        headers = {}
        def __init__(self, url):
            self.url = url
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def geturl(self):
            return self.url
        def read(self, max_size):
            return b"Sample,Condition\\nMOUSE_R1,flight\\n"
    class FakeOpener:
        def open(self, req, timeout):
            calls.append((req.full_url, timeout))
            return FakeResponse(req.full_url)
    monkeypatch.setattr(nasa_osdr, "build_opener", lambda handler: FakeOpener())
    nasa_osdr._bounded_download(nasa_osdr.MANIFEST_API, nasa_osdr.MAX_MANIFEST_BYTES)
    sample_url = "https://" + nasa_osdr.GENELAB_SAMPLE_HOST + nasa_osdr.GENELAB_SAMPLE_PATH
    nasa_osdr._bounded_download(sample_url, nasa_osdr.MAX_SAMPLE_BYTES)
    assert calls == [
        (nasa_osdr.MANIFEST_API, nasa_osdr.MANIFEST_TIMEOUT_SECONDS),
        (sample_url, nasa_osdr.SAMPLE_TIMEOUT_SECONDS),
    ]
    assert nasa_osdr.SAMPLE_TIMEOUT_SECONDS <= 30


def test_sample_storage_timeout_has_specific_but_safe_http_error(monkeypatch):
    monkeypatch.setenv("ARES_RESEARCH_ENABLED", "1")
    def fake_download(url, _limit):
        if url == nasa_osdr.MANIFEST_API:
            return response(EXAMPLE_FILE)
        raise TimeoutError("simulated public S3 request timed out")
    monkeypatch.setattr(nasa_osdr, "_bounded_download", fake_download)
    reply = client.get("/api/research/nasa/sample-table")
    assert reply.status_code == 503
    assert "sample storage timed out after 30 seconds" in reply.json()["detail"]
    assert "no study result was invented" in reply.json()["detail"]
