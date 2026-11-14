"""Daily synthetic input contract and inclusive engineering-rule boundaries."""
import numpy as np
import pandas as pd
import pytest

from src.ares_health.analysis import quality_issues, review_changes
from src.ares_health.review import build_review_report
from src.ares_health.synthetic import generate_scenario


@pytest.mark.parametrize('column,value', [
    ('timestamp_utc', None), ('timestamp_utc', 'invalid'), ('timestamp_utc', 1234),
    ('crew_id', None), ('crew_id', ''), ('crew_id', '   '), ('crew_id', 'SIM-002'),
    ('source_type', None), ('source_type', 'unknown'),
    ('resting_hr_bpm', None), ('resting_hr_bpm', 'bad'), ('resting_hr_bpm', 0),
    ('resting_hr_bpm', -1), ('resting_hr_bpm', 251), ('resting_hr_bpm', True),
    ('sleep_hours', -1), ('sleep_hours', 25), ('sleep_hours', np.inf),
    ('sleep_hours', 1+2j), ('sleep_hours', []), ('sleep_hours', {}),
    ('sleep_hours', pd.NA), ('timestamp_utc', pd.NaT),
    ('activity_minutes', -1), ('activity_minutes', 1441), ('activity_minutes', -np.inf),
])
def test_invalid_values_block_analysis_and_export(column, value):
    frame = generate_scenario('heart_rate_shift').astype({column: object})
    frame.at[0, column] = value
    before = frame.copy(deep=True)
    assert quality_issues(frame)
    assert review_changes(frame)[0] == []
    stale_flags, _ = review_changes(generate_scenario('heart_rate_shift'))
    report = build_review_report(frame, scenario='invalid', flags=stale_flags, issues=[])
    assert report['assessment'] == 'DATA_QUALITY_BLOCKED'
    assert report['review_flags'] == []
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize('kind', ['duplicate', 'reversed', 'gap', 'intraday', 'empty', 'column', 'duplicate_column'])
def test_invalid_structure(kind):
    frame = generate_scenario()
    if kind == 'duplicate':
        frame.loc[1, 'timestamp_utc'] = frame.loc[0, 'timestamp_utc']
    elif kind == 'reversed':
        frame = frame.iloc[::-1]
    elif kind == 'gap':
        frame = frame.drop(index=8)
    elif kind == 'intraday':
        frame.loc[1, 'timestamp_utc'] = frame.loc[1, 'timestamp_utc'].replace(hour=1)
    elif kind == 'empty':
        frame = frame.iloc[:0]
    elif kind == 'column':
        frame = frame.drop(columns='sleep_hours')
    else:
        frame = pd.concat([frame, frame[['sleep_hours']]], axis=1)
    assert quality_issues(frame)
    assert review_changes(frame)[0] == []
    report = build_review_report(frame, scenario=kind, flags=[], issues=[])
    assert report['assessment'] == 'DATA_QUALITY_BLOCKED'


@pytest.mark.parametrize('count', [1, 4, 7, 10])
def test_insufficient_disjoint_windows(count):
    frame = generate_scenario().head(count)
    assert quality_issues(frame) == []
    flags, blocked = review_changes(frame)
    assert not flags and blocked
    report = build_review_report(frame, scenario='short', flags=[], issues=[])
    assert report['assessment'] == 'INSUFFICIENT_DATA'
    assert report['review_flags'] == []


@pytest.mark.parametrize('metric,threshold,base', [('resting_hr_bpm', 12, 64), ('sleep_hours', 1.5, 7.5)])
@pytest.mark.parametrize('direction', [-1, 1])
@pytest.mark.parametrize('offset,expected', [(-0.01, False), (0, True), (0.01, True)])
def test_threshold_boundaries_and_explanations(metric, threshold, base, direction, offset, expected):
    frame = generate_scenario().head(11).copy()
    frame['resting_hr_bpm'] = 64.0
    frame['sleep_hours'] = 7.5
    frame.loc[frame.index[-4:], metric] = base + direction * (threshold + offset)
    flags, blocked = review_changes(frame)
    assert not blocked
    assert bool(flags) == expected
    if expected:
        flag = flags[0]
        assert flag.metric == metric
        assert flag.delta == pytest.approx(direction * (threshold + offset))
        assert ('higher' if direction > 0 else 'lower') in flag.message
        assert 'Reference interval:' in flag.message
        assert 'recent interval:' in flag.message
        assert 'not a diagnosis' in flag.message


def test_iso_timestamp_normalization_and_input_preservation():
    frame = generate_scenario()
    frame['timestamp_utc'] = frame.timestamp_utc.map(lambda x: x.isoformat())
    frame.loc[1, 'timestamp_utc'] = '2026-11-02T02:00:00+02:00'
    before = frame.copy(deep=True)
    assert quality_issues(frame) == []
    assert review_changes(frame) == ([], [])
    pd.testing.assert_frame_equal(frame, before)


def test_valid_numeric_strings_and_sanity_bounds():
    frame = generate_scenario()
    frame['resting_hr_bpm'] = '250'
    frame['sleep_hours'] = '0'
    frame['activity_minutes'] = '1440'
    assert quality_issues(frame) == []


def test_csv_round_trip_and_strict_json_export():
    import io
    import json

    for scenario in ['stable', 'heart_rate_shift', 'sleep_shift', 'incomplete']:
        original = generate_scenario(scenario)
        restored = pd.read_csv(io.StringIO(original.to_csv(index=False)))
        flags, blocked = review_changes(restored)
        report = build_review_report(restored, scenario=scenario, flags=flags,
                                     issues=quality_issues(restored), blocked=blocked)
        assert json.loads(json.dumps(report, allow_nan=False)) == report
        assert report['observation_count'] == len(original)
        assert report['assessment'] == ('DATA_QUALITY_BLOCKED' if scenario == 'incomplete'
                                        else 'NO_DEMO_RULE_TRIGGERED' if scenario == 'stable'
                                        else 'CHANGE_FOR_REVIEW')


def test_caller_blockers_suppress_otherwise_valid_flags():
    frame = generate_scenario('heart_rate_shift')
    for issues, blocked in [(['Manual quality hold'], []), ([], ['Review unavailable'])]:
        report = build_review_report(frame, scenario='hold', flags=[], issues=issues, blocked=blocked)
        assert report['review_flags'] == []
        assert report['assessment'] in {'DATA_QUALITY_BLOCKED', 'INSUFFICIENT_DATA'}
