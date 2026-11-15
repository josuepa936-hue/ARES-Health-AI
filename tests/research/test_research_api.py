import json

from fastapi.testclient import TestClient
import pytest

from src.ares_health.api import app
from src.ares_health import research

client = TestClient(app, client=('127.0.0.1', 12345))


def test_opt_in_and_synthetic_fallback(monkeypatch):
    monkeypatch.delenv('ARES_RESEARCH_ENABLED', raising=False)
    assert client.get('/api/research/ecg/demo').status_code == 503
    assert client.get('/api/demo').status_code == 200


def test_loopback_only_even_if_enabled(monkeypatch):
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    remote = TestClient(app, client=('198.51.100.10', 1))
    assert remote.get('/api/research/ecg/demo').status_code == 403


@pytest.mark.parametrize('record', ['101', '../100', 'https://example.com/100', '/etc/passwd'])
def test_only_allowlisted_record(record, monkeypatch):
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    assert client.get('/api/research/ecg/demo', params={'record': record}).status_code == 422


@pytest.mark.parametrize('content', [None, 'not JSON', '{}', 'x'*1_000_001])
def test_missing_corrupt_oversized_artifact(content, tmp_path, monkeypatch):
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    path = tmp_path/'benchmark.json'
    monkeypatch.setattr(research, 'ARTIFACT_PATH', path)
    if content is not None: path.write_text(content)
    assert client.get('/api/research/ecg/demo').status_code == 503


def test_abstention_is_explicit_without_metrics(tmp_path, monkeypatch):
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    path = tmp_path/'benchmark.json'; monkeypatch.setattr(research, 'ARTIFACT_PATH', path)
    data = research.envelope('abstained', ['Missing official files'])
    path.write_text(json.dumps(data))
    response = client.get('/api/research/ecg/demo')
    assert response.status_code == 200
    assert response.json()['status'] == 'abstained'
    assert response.json()['data_provenance'] == 'public_research_ecg'
    assert response.json()['metrics'] is None
    assert response.json()['waveform'] == []


def test_rejects_scores_in_abstention(tmp_path, monkeypatch):
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    path = tmp_path/'benchmark.json'; monkeypatch.setattr(research, 'ARTIFACT_PATH', path)
    data = research.envelope('abstained', ['bad quality'])
    data['detected_peaks'] = [{'sample': 400, 'mv': 1.0}]
    path.write_text(json.dumps(data))
    assert client.get('/api/research/ecg/demo').status_code == 503


def test_nonfinite_json_is_unavailable_not_server_error(tmp_path, monkeypatch):
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    path = tmp_path/'benchmark.json'; monkeypatch.setattr(research, 'ARTIFACT_PATH', path)
    data = research.envelope('abstained', ['bad input'])
    data['acquisition'] = {'invalid': float('nan')}
    path.write_text(json.dumps(data))
    assert client.get('/api/research/ecg/demo').status_code == 503


def test_overflowed_json_float_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    path = tmp_path/'benchmark.json'; monkeypatch.setattr(research, 'ARTIFACT_PATH', path)
    data = research.envelope('abstained', ['bad input'])
    data['acquisition'] = {'invalid': 'OVERFLOW'}
    path.write_text(json.dumps(data).replace('"OVERFLOW"', '1e9999'))
    assert client.get('/api/research/ecg/demo').status_code == 503
