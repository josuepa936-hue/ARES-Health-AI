"""Optional offline WFDB/NeuroKit integration; all input here is synthetic."""
import hashlib
import json

import neurokit2 as nk
import numpy as np
import pytest
import wfdb

from scripts.prepare_research_ecg import prepare, verify
from src.ares_health.research import FS, analyze_segment, read_official_record


def fixture(directory):
    signal = nk.ecg_simulate(duration=60, sampling_rate=FS, heart_rate=70, random_state=2026)
    full = np.resize(signal, 650000)
    wfdb.wrsamp('100', fs=FS, units=['mV', 'mV'], sig_name=['MLII', 'V5'], p_signal=np.column_stack([full, full]), fmt=['212', '212'], adc_gain=[200, 200], baseline=[1024, 1024], write_dir=str(directory))
    wfdb.wrann('100', 'atr', sample=np.array([360, 720, 1080]), symbol=['N', 'N', 'N'], write_dir=str(directory))
    (directory/'SHA256SUMS.txt').write_text('\n'.join(f'{hashlib.sha256((directory/name).read_bytes()).hexdigest()}  {name}' for name in ('100.hea', '100.dat', '100.atr')))
    return signal


def test_real_libraries_clean_detect_and_parse_self_contained_wfdb(tmp_path):
    fixture(tmp_path)
    signal, samples, symbols = read_official_record(tmp_path)
    first = analyze_segment(signal, FS, samples, symbols)
    assert first['status'] == 'benchmarked', first['reasons']
    assert first == analyze_segment(signal, FS, samples, symbols)
    assert first['processing_versions']['wfdb'] == '4.3.1'
    assert first['processing_versions']['neurokit2'] == '0.2.12'
    assert len(first['detected_peaks']) > 10
    json.dumps(first, allow_nan=False)


def test_preparation_hashes_corruption_and_metadata_rejection(tmp_path):
    fixture(tmp_path)
    result = prepare(tmp_path, 'self-contained-test-fixture')
    assert result['acquisition']['sha256'] == verify(tmp_path)
    assert 'operator-supplied' in result['acquisition']['note']
    assert result['status'] == 'benchmarked'
    with (tmp_path/'100.dat').open('r+b') as handle:
        handle.write(b'bad')
    with pytest.raises(ValueError, match='manifest mismatch'): verify(tmp_path)


def test_wrong_sampling_rate_fails_before_waveform_read(tmp_path):
    fixture(tmp_path)
    header = tmp_path/'100.hea'
    header.write_text(header.read_text().replace('360', '250', 1))
    with pytest.raises(ValueError, match='metadata'): read_official_record(tmp_path)


def test_prepared_artifact_is_served_without_detector_or_download(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from src.ares_health.api import app
    from src.ares_health import research
    import urllib.request

    fixture(tmp_path)
    result = prepare(tmp_path, 'self-contained-test-fixture')
    path = tmp_path/'benchmark.json'
    path.write_text(json.dumps(result, allow_nan=False))
    monkeypatch.setattr(research, 'ARTIFACT_PATH', path)
    monkeypatch.setenv('ARES_RESEARCH_ENABLED', '1')
    def forbidden(*args, **kwargs): raise AssertionError('HTTP must not download/detect')
    monkeypatch.setattr(nk, 'ecg_clean', forbidden)
    monkeypatch.setattr(urllib.request, 'urlopen', forbidden)
    client = TestClient(app, client=('127.0.0.1', 1))
    first = client.get('/api/research/ecg/demo')
    assert first.status_code == 200, first.text
    assert first.json()['metrics'] == result['metrics']
    assert first.content == client.get('/api/research/ecg/demo').content
