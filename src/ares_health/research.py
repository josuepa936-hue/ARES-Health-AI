"""Optional terrestrial ECG benchmark, never a mission/clinical inference module.

Heavy optional dependencies are imported only during explicit offline preparation.
All sample indices refer to the original 360 Hz segment, never display resampling.
"""
from __future__ import annotations

import importlib.metadata
import platform
from pathlib import Path

import numpy as np
from scipy.signal import periodogram

FS = 360
SAMPLES = 60 * FS
GUARD = FS
TOLERANCE = 54  # +/-150 ms, inclusive; engineering protocol, not clinical standard
BEAT_SYMBOLS = frozenset({'N', 'L', 'R', 'B', 'A', 'a', 'J', 'S', 'V', 'r', 'F', 'e', 'j', 'n', 'E', '/', 'f', 'Q'})
ARTIFACT_PATH = Path(__file__).resolve().parents[2] / '.ares-research' / 'benchmark.json'
DISCLAIMER = ('Public terrestrial ECG research benchmark only; not synthetic mission data, '
              'diagnosis, clinical validation, NASA endorsement or spaceflight qualification.')


def versions() -> dict[str, str]:
    result = {'python': platform.python_version()}
    for name in ('wfdb', 'neurokit2', 'numpy', 'scipy'):
        try:
            result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            result[name] = 'not-installed'
    return result


def envelope(status: str, reasons: list[str]) -> dict:
    return {
        'schema_version': '1.2-research', 'record': '100',
        'data_provenance': 'public_research_ecg', 'status': status, 'reasons': reasons,
        'source': {
            'dataset': 'MIT-BIH Arrhythmia Database', 'version': '1.0.0',
            'url': 'https://physionet.org/content/mitdb/1.0.0/',
            'doi': 'https://doi.org/10.13026/C2F305',
            'context': 'Public de-identified terrestrial research; no personal uploads.',
        },
        'protocol': {'sampling_rate_hz': FS, 'channel': 'MLII', 'segment_start_sample': 0,
                     'segment_end_sample_exclusive': SAMPLES, 'scoring_start_sample': GUARD,
                     'scoring_end_sample_exclusive': SAMPLES - GUARD,
                     'tolerance_samples': TOLERANCE, 'tolerance_ms': 150,
                     'cleaning': 'neurokit', 'detector': 'neurokit',
                     'matching': 'ordered earliest-feasible one-to-one, inclusive tolerance',
                     'display_stride': 12},
        'processing_versions': versions(), 'quality': {'status': 'not_evaluated', 'checks': []},
        'metrics': None, 'waveform': [], 'detected_peaks': [], 'reference_peaks': [],
        'matches': [], 'discrepancies': [], 'annotation_counts': None,
        'disclaimer': DISCLAIMER,
    }


def match_beats(reference: list[int], detected: list[int], tolerance: int = TOLERANCE) -> dict:
    """Max-cardinality ordered matching; earliest eligible pair, not nearest-time optimization.

    Duplicate detections remain separate candidates (extras become FP). Reference
    beats must be unique. Timing is absolute sample difference for matched pairs.
    Undefined ratios/MAE use None, not NaN or a reassuring invented zero.
    """
    for values in (reference, detected):
        if any(not isinstance(n, (int, np.integer)) or isinstance(n, (bool, np.bool_)) or n < 0 for n in values):
            raise ValueError('Peak indices must be nonnegative integer samples.')
        if any(a > b for a, b in zip(values, values[1:])):
            raise ValueError('Peak indices must be ordered.')
    if len(set(reference)) != len(reference) or tolerance < 0:
        raise ValueError('Reference beats must be unique and tolerance nonnegative.')
    i = j = 0
    pairs, discrepancies = [], []
    while i < len(reference) and j < len(detected):
        r, d = int(reference[i]), int(detected[j])
        if abs(r - d) <= tolerance:
            pairs.append({'reference_sample': r, 'detected_sample': d, 'absolute_error_ms': abs(r-d)*1000/FS})
            i += 1; j += 1
        elif d < r:
            discrepancies.append({'type': 'FP', 'sample': d}); j += 1
        else:
            discrepancies.append({'type': 'FN', 'sample': r}); i += 1
    discrepancies.extend({'type': 'FN', 'sample': int(n)} for n in reference[i:])
    discrepancies.extend({'type': 'FP', 'sample': int(n)} for n in detected[j:])
    tp = len(pairs); fp = len(detected)-tp; fn = len(reference)-tp
    return {'metrics': {'tp': tp, 'fp': fp, 'fn': fn,
                        'precision': tp/(tp+fp) if tp+fp else None,
                        'recall': tp/(tp+fn) if tp+fn else None,
                        'f1': 2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,
                        'mean_absolute_timing_error_ms': sum(p['absolute_error_ms'] for p in pairs)/tp if tp else None},
            'matches': pairs, 'discrepancies': sorted(discrepancies, key=lambda p: (p['sample'], p['type']))}


def select_annotations(samples: list[int], symbols: list[str]) -> tuple[list[int], dict]:
    if len(samples) != len(symbols) or any(not isinstance(n, (int, np.integer)) or isinstance(n, (bool, np.bool_)) or n < 0 or n >= SAMPLES for n in samples):
        raise ValueError('Malformed annotation sample positions.')
    beats = [int(n) for n, symbol in zip(samples, symbols) if symbol in BEAT_SYMBOLS]
    if beats != sorted(set(beats)):
        raise ValueError('Heartbeat annotations must be unique and ordered.')
    scored = [n for n in beats if GUARD <= n < SAMPLES-GUARD]
    return scored, {'segment_annotations': len(samples),
                    'excluded_nonbeat_annotations': len(samples)-len(beats),
                    'unscored_boundary_beats': len(beats)-len(scored),
                    'scored_reference_beats': len(scored)}


def signal_quality(signal: np.ndarray, fs: int) -> list[str]:
    """Conservative engineering exclusions, not a validated ECG quality classifier."""
    if fs != FS:
        return ['Expected exactly 360 Hz; no automatic resampling.']
    if signal.ndim != 1 or len(signal) != SAMPLES:
        return ['Expected exactly 60 seconds of one-channel MLII ECG.']
    if not np.isfinite(signal).all():
        return ['Missing/nonfinite samples: abstain without interpolation.']
    reasons = []
    if np.max(np.abs(signal)) > 10:
        reasons.append('Amplitude exceeds the engineering 10 mV input bound.')
    if any(np.std(window) < 0.01 for window in signal.reshape(60, FS)):
        reasons.append('One-second flat/near-flat window (SD <0.01 mV).')
    constant = np.abs(np.diff(signal)) < 1e-12
    if np.convolve(constant.astype(int), np.ones(90, dtype=int), 'valid').max() >= 90:
        reasons.append('Constant plateau of at least 250 ms; possible dropout/clipping.')
    freq, power = periodogram(signal, fs=FS)
    total = power[(freq >= .5) & (freq <= 100)].sum()
    mains = power[((freq >= 49) & (freq <= 51)) | ((freq >= 59) & (freq <= 61))].sum()
    if total > 0 and mains/total > .4:
        reasons.append('50/60 Hz bands exceed 40% of 0.5–100 Hz spectral power.')
    return reasons


def analyze_segment(signal: np.ndarray, fs: int, samples: list[int], symbols: list[str]) -> dict:
    """Full-resolution NK cleaning/detection and fixed-window annotation comparison."""
    result = envelope('abstained', [])
    reasons = signal_quality(signal, fs)
    if reasons:
        result['reasons'] = reasons; result['quality']['status'] = 'failed'; return result
    try:
        reference, counts = select_annotations(samples, symbols)
        if not reference:
            raise ValueError('No scorable expert-reviewed heartbeat annotations.')
        import neurokit2 as nk
        cleaned = np.asarray(nk.ecg_clean(signal, sampling_rate=FS, method='neurokit'))
        if not np.isfinite(cleaned).all():
            raise ValueError('Cleaning produced nonfinite values.')
        _, info = nk.ecg_peaks(cleaned, sampling_rate=FS, method='neurokit', correct_artifacts=False)
        raw_peaks = np.asarray(info['ECG_R_Peaks'])
        if raw_peaks.ndim != 1 or not np.issubdtype(raw_peaks.dtype, np.integer):
            raise ValueError('Malformed detector output.')
        if len(raw_peaks) > 500 or len(reference) > 500 or np.any(raw_peaks < 0) or np.any(raw_peaks >= SAMPLES):
            raise ValueError('Detector/reference output exceeds fixed benchmark bounds.')
        detected = [int(n) for n in raw_peaks if GUARD <= n < SAMPLES-GUARD]
        benchmark = match_beats(reference, detected)
    except (ImportError, ValueError, TypeError, ArithmeticError, KeyError, IndexError, RuntimeError) as exc:
        result['reasons'] = [f'Cannot benchmark: {type(exc).__name__}: {exc}']
        result['quality']['status'] = 'abstained'; return result
    result.update(benchmark)
    result.update(status='benchmarked', annotation_counts={**counts, 'unscored_boundary_detections': len(raw_peaks)-len(detected)})
    result['quality'] = {'status': 'engineering_gates_passed', 'checks': [
        '360 Hz, 60 s, finite mV samples', 'No flat one-second window or 250 ms plateau',
        'Amplitude and mains-interference engineering bounds',
        'These checks do not establish clinical signal quality or exclude all artifacts.']}
    result['waveform'] = [{'sample': n, 'mv': float(signal[n])} for n in range(0, SAMPLES, 12)]
    result['detected_peaks'] = [{'sample': n, 'mv': float(signal[n])} for n in detected]
    result['reference_peaks'] = [{'sample': n, 'mv': float(signal[n])} for n in reference]
    return result


def read_official_record(directory: Path) -> tuple[np.ndarray, list[int], list[str]]:
    """Read only the approved full WFDB record, check metadata and digital checksums.

    Header comments/demographics and annotation labels are never exported to HTTP.
    """
    import wfdb
    record = wfdb.rdheader(str(directory / '100'))
    if (record.fs != FS or record.sig_len != 650000 or record.n_sig != 2 or
            record.sig_name != ['MLII', 'V5'] or record.units != ['mV', 'mV'] or
            record.fmt != ['212', '212'] or record.file_name != ['100.dat', '100.dat']):
        raise ValueError('Record 100 metadata does not match the approved MIT-BIH case.')
    record = wfdb.rdrecord(str(directory / '100'), physical=False)
    for i in range(2):
        checksum = (int(record.d_signal[:, i].sum(dtype=np.int64)) + 32768) % 65536 - 32768
        if checksum % 65536 != record.checksum[i] % 65536:
            raise ValueError('WFDB digital waveform checksum mismatch.')
    if not all(np.isfinite(record.adc_gain)) or min(record.adc_gain) <= 0:
        raise ValueError('Invalid calibration metadata.')
    physical = record.dac(inplace=False)[:SAMPLES, 0]
    annotations = wfdb.rdann(str(directory / '100'), 'atr', sampfrom=0, sampto=SAMPLES, shift_samps=False)
    return physical, annotations.sample.tolist(), annotations.symbol
