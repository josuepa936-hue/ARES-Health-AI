"""Offline engineering fixtures only; no public-record results are asserted."""
import json
import sys
from types import SimpleNamespace

import numpy as np
import pytest

from src.ares_health.research import FS, SAMPLES, analyze_segment, match_beats, select_annotations, signal_quality


def fixture_signal():
    t = np.arange(SAMPLES)/FS
    signal = .03*np.sin(2*np.pi*t)
    for sample in range(FS, SAMPLES, FS):
        signal += np.exp(-((np.arange(SAMPLES)-sample)/8)**2)
    return signal


@pytest.mark.parametrize('reference,detected,tp,fp,fn', [
    ([100, 200], [100, 200], 2, 0, 0), ([100], [46], 1, 0, 0),
    ([100], [45], 0, 1, 1), ([100], [154], 1, 0, 0), ([100], [155], 0, 1, 1),
    ([100], [99, 101], 1, 1, 0), ([100], [100, 100], 1, 1, 0),
    ([100, 200], [150], 1, 0, 1), ([], [], 0, 0, 0), ([100], [], 0, 0, 1),
    ([], [100], 0, 1, 0),
])
def test_matching_counts_and_inclusive_tolerance(reference, detected, tp, fp, fn):
    result = match_beats(reference, detected)
    assert result['metrics']['tp'] == tp
    assert result['metrics']['fp'] == fp
    assert result['metrics']['fn'] == fn
    assert len(result['matches']) == tp
    assert tp+fp == len(detected) and tp+fn == len(reference)
    json.dumps(result, allow_nan=False)


def test_metrics_timing_and_undefined_values():
    scores = match_beats([100, 300], [109, 400])['metrics']
    assert scores == {'tp': 1, 'fp': 1, 'fn': 1, 'precision': .5, 'recall': .5, 'f1': .5, 'mean_absolute_timing_error_ms': 25.0}
    assert match_beats([], [])['metrics']['precision'] is None
    assert match_beats([], [])['metrics']['recall'] is None
    assert match_beats([], [])['metrics']['f1'] is None
    assert match_beats([100], [])['metrics']['mean_absolute_timing_error_ms'] is None


@pytest.mark.parametrize('reference,detected', [([2, 1], [1]), ([1, 1], [1]), ([1], [-1]), ([1], [1.5]), ([True], [1])])
def test_malformed_indices_fail(reference, detected):
    with pytest.raises(ValueError): match_beats(reference, detected)


def test_annotation_symbols_and_half_open_boundaries():
    reference, counts = select_annotations([0, 100, 360, 1000, 21239, 21240], ['+', '?', 'N', '~', 'V', 'N'])
    assert reference == [360, 21239]
    assert counts == {'segment_annotations': 6, 'excluded_nonbeat_annotations': 3, 'unscored_boundary_beats': 1, 'scored_reference_beats': 2}


@pytest.mark.parametrize('samples,symbols', [([1], []), ([21600], ['N']), ([-1], ['N']), ([1, 1], ['N', 'N']), ([2, 1], ['N', 'N'])])
def test_annotation_parsing_failure(samples, symbols):
    with pytest.raises(ValueError): select_annotations(samples, symbols)


@pytest.mark.parametrize('kind', ['missing', 'inf', 'flat', 'dropout', 'mains', 'amplitude', 'length', 'sampling'])
def test_quality_abstains_without_filling_or_detection(kind, monkeypatch):
    signal = fixture_signal(); fs = FS
    if kind == 'missing': signal[800] = np.nan
    elif kind == 'inf': signal[800] = np.inf
    elif kind == 'flat': signal[:] = 0
    elif kind == 'dropout': signal[700:800] = 0
    elif kind == 'mains': signal += 5*np.sin(2*np.pi*50*np.arange(SAMPLES)/FS)
    elif kind == 'amplitude': signal[10] = 11
    elif kind == 'length': signal = signal[:100]
    else: fs = 250
    monkeypatch.setitem(sys.modules, 'neurokit2', SimpleNamespace())
    result = analyze_segment(signal, fs, [360], ['N'])
    assert result['status'] == 'abstained' and result['reasons']
    assert result['metrics'] is None and result['waveform'] == []
    json.dumps(result, allow_nan=False)


def test_success_uses_full_resolution_but_downsamples_display(monkeypatch):
    signal = fixture_signal(); original = signal.copy()
    detections = np.array([100, 360, 720, 1000, 21300])
    def detect(cleaned, **kwargs):
        assert len(cleaned) == SAMPLES and kwargs['correct_artifacts'] is False
        return None, {'ECG_R_Peaks': detections}
    monkeypatch.setitem(sys.modules, 'neurokit2', SimpleNamespace(ecg_clean=lambda data, **kw: data, ecg_peaks=detect))
    first = analyze_segment(signal, FS, [100, 360, 720, 1100, 21400], ['N']*5)
    assert first == analyze_segment(signal, FS, [100, 360, 720, 1100, 21400], ['N']*5)
    assert first['metrics']['tp'] == 2
    assert first['metrics']['fp'] == 1 and first['metrics']['fn'] == 1
    assert len(first['waveform']) == 1800
    assert first['annotation_counts']['unscored_boundary_beats'] == 2
    assert first['annotation_counts']['unscored_boundary_detections'] == 2
    np.testing.assert_array_equal(signal, original)


def test_detector_failure_abstains(monkeypatch):
    def broken(*args, **kwargs): raise ValueError('fixture failure')
    monkeypatch.setitem(sys.modules, 'neurokit2', SimpleNamespace(ecg_clean=broken))
    result = analyze_segment(fixture_signal(), FS, [360], ['N'])
    assert result['status'] == 'abstained' and result['metrics'] is None
