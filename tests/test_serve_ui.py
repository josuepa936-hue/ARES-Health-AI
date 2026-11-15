"""Compiled React served alongside the local API; no static file browser."""
from fastapi import FastAPI
from fastapi.testclient import TestClient

from src.ares_health.api import app
from src.ares_health.serve_ui import install_compiled_frontend


def test_without_frontend_build_gracefully_explains_install(tmp_path):
    local = FastAPI()
    install_compiled_frontend(local, tmp_path / "missing")
    response = TestClient(local).get("/")
    assert response.status_code == 503
    assert "npm ci" in response.json()["detail"]
    assert TestClient(local).get("/synthetic-template.csv").status_code == 503


def test_compiled_single_origin_ui_and_template_are_served(tmp_path):
    dist = tmp_path / "dist"
    assets = dist / "assets"
    assets.mkdir(parents=True)
    (dist / "index.html").write_text(
        '<!doctype html><html><script src="/assets/app.js"></script></html>',
        encoding="utf-8",
    )
    (assets / "app.js").write_text('console.log("ARES synthetic demo")', encoding="utf-8")
    (dist / "synthetic-template.csv").write_text(
        "timestamp_utc,source_type\n2026-11-01T00:00:00Z,synthetic\n",
        encoding="utf-8",
    )
    local = FastAPI()
    install_compiled_frontend(local, dist)
    client = TestClient(local)
    page = client.get("/")
    assert page.status_code == 200
    assert "text/html" in page.headers["content-type"]
    assert '/assets/app.js' in page.text
    script = client.get("/assets/app.js")
    assert script.status_code == 200
    assert 'ARES synthetic demo' in script.text
    csv = client.get("/synthetic-template.csv")
    assert csv.status_code == 200
    assert "synthetic" in csv.text


def test_unlisted_static_files_are_not_exposed(tmp_path):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<html>ARES</html>", encoding="utf-8")
    (tmp_path / "private.txt").write_text("PRIVATE")
    local = FastAPI()
    install_compiled_frontend(local, dist)
    client = TestClient(local)
    assert client.get("/private.txt").status_code == 404
    assert client.get("/assets/other.js").status_code == 404
    assert client.get("/api/mission/checkins").status_code == 404


def test_existing_real_api_endpoints_remain_live_under_single_origin():
    client = TestClient(app)
    assert client.get("/api/scenarios").status_code == 200
    assert client.get("/api/mission/risk-guide").status_code == 200
    assert client.get("/api/demo").status_code == 200
    assert client.get("/api/timeline").status_code == 200
