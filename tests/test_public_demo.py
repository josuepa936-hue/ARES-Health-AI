"""Exercise the real public server boundary; no domain algorithm is replaced."""
import asyncio
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time

import httpx
import pytest
from fastapi import FastAPI
from starlette.testclient import TestClient
from src.ares_health.public_demo import PublicDemoBoundary

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def public_url():
    external = os.getenv("ARES_PUBLIC_TEST_URL")
    if external:
        yield external.rstrip("/")
        return
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    url = f"http://127.0.0.1:{port}"
    process = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.ares_health.api:app", "--host", "127.0.0.1",
         "--port", str(port), "--no-access-log", "--no-proxy-headers"], cwd=ROOT,
        env={**os.environ, "ARES_PUBLIC_DEMO": "1", "ARES_PUBLIC_ORIGIN": url,
             "ARES_RESEARCH_ENABLED": "1"}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        deadline = time.monotonic() + 20
        while time.monotonic() < deadline:
            try:
                if httpx.get(url + "/api/status", timeout=1).status_code == 200:
                    break
            except httpx.HTTPError:
                pass
            if process.poll() is not None:
                pytest.fail("Public server did not start")
            time.sleep(.1)
        else:
            pytest.fail("Public server readiness timeout")
        yield url
    finally:
        process.terminate()
        process.wait(timeout=10)


@pytest.fixture
def client(public_url):
    with httpx.Client(base_url=public_url, timeout=15) as client:
        yield client


def test_public_status_and_headers(client):
    r = client.get('/api/status')
    assert r.json()['mode'] == 'public-demo'
    assert r.json()['clinical_validation'] is False
    assert r.headers['x-content-type-options'] == 'nosniff'
    assert "frame-ancestors 'none'" in r.headers['content-security-policy']
    assert r.headers['cache-control'] == 'no-store'


@pytest.mark.parametrize('path', ['/docs', '/openapi.json', '/redoc', '/api/research/nasa/study',
    '/api/research/ecg/demo', '/api/review', '/api/synthetic-csv', '/synthetic-template.csv',
    '/.env', '/.git/config', '/src/ares_health/api.py', '/requirements-deploy.lock', '/admin'])
def test_private_routes_unavailable(client, path):
    assert client.get(path).status_code == 404


def test_host_origin_and_cross_site_rejected(client):
    assert client.get('/api/demo', headers={'Host': 'attacker.invalid'}).status_code == 400
    for origin in ['https://attacker.invalid', 'null']:
        r = client.post('/api/mission/wellness', json={}, headers={'Origin': origin})
        assert r.status_code == 403
        assert 'access-control-allow-origin' not in r.headers
    assert client.get('/api/demo', headers={'Sec-Fetch-Site': 'cross-site'}).status_code == 403
    assert client.options('/api/mission/copilot').status_code == 405


def test_query_and_validation_errors_do_not_echo_input(client):
    for query in ['days=366', 'days=21&days=21', 'secret=PRIVATE_SENTINEL', 'scenario=PRIVATE_SENTINEL']:
        r = client.get('/api/demo?' + query)
        assert r.status_code == 422
        assert 'PRIVATE_SENTINEL' not in r.text
    assert client.get('/api/demo?' + 'a' * 1025).status_code == 414


@pytest.mark.parametrize('body', ['{"x":NaN}', '{"x":1e999}', '{"context":{},"context":{}}', '[' * 1100 + ']' * 1100])
def test_malformed_nonfinite_duplicate_and_nested_json(client, body):
    assert client.post('/api/mission/wellness', content=body,
                       headers={'Content-Type': 'application/json'}).status_code == 422


def test_streaming_size_and_encoding_limits(client):
    r = client.post('/api/mission/wellness', content=(b'x' * 10000 for _ in range(8)),
                    headers={'Content-Type': 'application/json'})
    assert r.status_code == 413
    assert client.post('/api/mission/comprehensive-report', content=b'x' * 65537,
                       headers={'Content-Type': 'application/json'}).status_code == 413
    assert client.post('/api/mission/comprehensive-report', json={}, headers={'Content-Encoding': 'gzip'}).status_code == 415
    assert client.post('/api/mission/comprehensive-report', content='test').status_code == 415


def test_no_csv_context_even_through_copilot(client):
    r = client.post('/api/mission/copilot', json={'context': {
        'kind': 'synthetic_csv', 'fictional_attestation': True, 'csv': 'PRIVATE_SENTINEL'}})
    assert r.status_code == 422
    assert 'PRIVATE_SENTINEL' not in r.text


def test_strict_fictional_checkin_and_model_fields(client):
    payload = {'fictional_attestation': True, 'resting_hr_bpm': 140,
               'sleep_hours': 7, 'activity_minutes': 45}
    assert client.post('/api/mission/fictional-check-in', json=payload).status_code == 200
    for key, value in [('fictional_attestation', 1), ('resting_hr_bpm', '140'), ('extra', 'PRIVATE_SENTINEL')]:
        r = client.post('/api/mission/fictional-check-in', json={**payload, key: value})
        assert r.status_code == 422
        assert 'PRIVATE_SENTINEL' not in r.text


def test_canonical_workflow_and_review_export(client):
    for scenario, state in [('stable', 'NO_DEMO_RULE_TRIGGERED'),
                            ('heart_rate_shift', 'CHANGE_FOR_REVIEW'),
                            ('incomplete', 'DATA_QUALITY_BLOCKED')]:
        snapshot = client.get('/api/demo', params={'scenario': scenario}).json()
        assert snapshot['assessment'] == state
        assert len(snapshot['observations']) == 21
    context = {'kind': 'scenario', 'scenario': 'stable', 'seed': 2026, 'days': 21}
    briefing = client.post('/api/mission/copilot', json={'context': context}).json()
    ref = briefing['context_ref']
    wellness = client.post('/api/mission/wellness', json={'context': context, 'expected_context_ref': ref})
    assert wellness.status_code == 200
    report = client.post('/api/mission/comprehensive-report', json={
        'context': context, 'expected_context_ref': ref, 'fictional_attestation': True,
        'questions': [], 'audit_log': []})
    assert report.status_code == 200
    assert report.json()['fictional_review']['clinical_authorization'] is False
    assert len(report.json()['evaluated_observations']) == 21
    assert client.post('/api/mission/wellness', json={'context': {**context, 'days': 366}}).status_code == 422


def test_rate_budget_not_bypassed_by_forwarded_headers():
    app = FastAPI()
    @app.get('/api/scenarios')
    async def scenarios():
        return {'ok': True}
    with TestClient(PublicDemoBoundary(app, 'https://demo.example', peer_limit=2),
                    base_url='https://demo.example') as client:
        assert client.get('/api/scenarios').status_code == 200
        assert client.get('/api/scenarios', headers={'X-Forwarded-For': '1.2.3.4'}).status_code == 200
        r = client.get('/api/scenarios', headers={'X-Forwarded-For': '5.6.7.8'})
        assert r.status_code == 429
        assert r.headers['retry-after'] == '60'
        assert client.get('/api/status').status_code == 200


def test_global_budget_and_concurrency_bound():
    async def run():
        started, release = asyncio.Event(), asyncio.Event()
        async def app(scope, receive, send):
            started.set()
            await release.wait()
            await send({'type': 'http.response.start', 'status': 200, 'headers': []})
            await send({'type': 'http.response.body', 'body': b'ok'})
        boundary = PublicDemoBoundary(app, 'https://demo.example', concurrent_limit=1)
        scope = {'type': 'http', 'path': '/api/scenarios', 'method': 'GET', 'query_string': b'',
                 'headers': [(b'host', b'demo.example')], 'client': ('peer', 1)}
        async def receive():
            return {'type': 'http.request', 'body': b''}
        messages = []
        async def send(message):
            messages.append(message)
        first = asyncio.create_task(boundary(scope, receive, send))
        await started.wait()
        await boundary(scope, receive, send)
        assert any(x.get('status') == 503 for x in messages)
        release.set()
        await first
        assert boundary.active == 0
        global_boundary = PublicDemoBoundary(app, 'https://demo.example', global_limit=1)
        assert global_boundary.rate_allowed('peer1')
        assert not global_boundary.rate_allowed('peer2')
    asyncio.run(run())


@pytest.mark.parametrize('origin', ['', 'http://public.example', 'https://public.example/path',
    'https://user:pass@public.example', 'https://public.example?secret=x'])
def test_invalid_public_origin_fails_closed(monkeypatch, origin):
    from src.ares_health.public_demo import public_origin
    monkeypatch.setenv('ARES_PUBLIC_ORIGIN', origin)
    monkeypatch.delenv('RENDER_EXTERNAL_URL', raising=False)
    with pytest.raises(RuntimeError):
        public_origin()


def test_render_origin_and_secure_headers(monkeypatch):
    from src.ares_health.public_demo import public_origin
    monkeypatch.delenv('ARES_PUBLIC_ORIGIN', raising=False)
    monkeypatch.setenv('RENDER_EXTERNAL_URL', 'https://demo.onrender.com')
    assert public_origin() == 'https://demo.onrender.com'
    app = FastAPI()
    @app.get('/api/scenarios')
    def fail():
        raise RuntimeError('PRIVATE_SENTINEL')
    with TestClient(PublicDemoBoundary(app, public_origin()),
                    base_url='https://demo.onrender.com', raise_server_exceptions=False) as client:
        r = client.get('/api/scenarios')
        assert r.status_code == 500
        assert 'PRIVATE_SENTINEL' not in r.text
        assert r.headers['strict-transport-security'] == 'max-age=31536000'


def test_external_project_link_can_open_demo_but_not_embed_or_fetch_api(client):
    navigation = {'Sec-Fetch-Site': 'cross-site', 'Sec-Fetch-Mode': 'navigate',
                  'Sec-Fetch-Dest': 'document'}
    # Python-only CI has no compiled frontend; the boundary must permit entry,
    # while Docker/browser validation additionally requires a rendered 200 UI.
    assert client.get('/', headers=navigation).status_code in (200, 503)
    assert client.get('/api/demo', headers=navigation).status_code == 403
    assert client.get('/', headers={**navigation, 'Sec-Fetch-Dest': 'iframe'}).status_code == 403
