"""Timeline regression checks use only deterministic fictional records."""
import json

import numpy as np
import pandas as pd
import pytest

from src.ares_health.analysis import review_changes
from src.ares_health.service import build_snapshot
from src.ares_health.synthetic import generate_scenario
from src.ares_health.timeline import build_timeline


@pytest.mark.parametrize('scenario', ['stable', 'heart_rate_shift', 'sleep_shift', 'incomplete'])
def test_timeline_reproducible_json_and_canonical_final_assessment(scenario):
    frame = generate_scenario(scenario)
    original = frame.copy(deep=True)
    first = build_timeline(frame, scenario=scenario)
    assert json.dumps(first, allow_nan=False) == json.dumps(build_timeline(frame, scenario=scenario), allow_nan=False)
    snapshot = build_snapshot(frame, scenario=scenario)
    assert first['assessment'] == snapshot['assessment']
    assert [event['details'] for event in first['events'] if event['type'] == 'observation'] == snapshot['observations']
    assert len({event['id'] for event in first['events']}) == len(first['events'])
    assert first['simulation_only'] is True
    assert 'No astronaut measurements' in first['disclaimer']
    pd.testing.assert_frame_equal(frame, original)


@pytest.mark.parametrize('scenario', ['stable', 'heart_rate_shift', 'sleep_shift'])
def test_every_trend_matches_existing_prefix_rule(scenario):
    frame = generate_scenario(scenario)
    timeline = build_timeline(frame, scenario=scenario)
    trends = [event for event in timeline['events'] if event['type'] == 'trend_change']
    expected = []
    for end in range(11, len(frame) + 1):
        flags, _ = review_changes(frame.iloc[:end])
        expected.extend((end - 1, flag) for flag in flags)
    assert len(trends) == len(expected)
    for event, (index, flag) in zip(trends, expected):
        assert event['observation_index'] == index
        assert event['explanation'] == flag.message
        assert event['details']['metric'] == flag.metric
        assert event['details']['difference'] == flag.delta
        assert event['details']['baseline_mean'] == flag.baseline
        assert event['details']['recent_mean'] == flag.recent
        assert event['details']['recent_end_utc'] == event['timestamp_utc']
        assert event['details']['reference_start_utc'] == '2026-11-01T00:00:00Z'
        assert event['details']['reference_end_utc'] == '2026-11-07T00:00:00Z'
        assert event['details']['recent_start_utc'] == frame.iloc[index - 3].timestamp_utc.isoformat().replace('+00:00', 'Z')
    assert [event['details']['state'] for event in timeline['events'] if event['type'] == 'analysis_status'] == [
        'INSUFFICIENT_DATA', 'COMPARISON_AVAILABLE'
    ]


@pytest.mark.parametrize('metric,threshold,base', [('resting_hr_bpm', 12, 64), ('sleep_hours', 1.5, 7.5)])
@pytest.mark.parametrize('direction', [-1, 1])
@pytest.mark.parametrize('offset,flagged', [(-0.01, False), (0, True), (0.01, True)])
def test_timeline_preserves_inclusive_thresholds(metric, threshold, base, direction, offset, flagged):
    frame = generate_scenario().head(11).copy()
    frame['resting_hr_bpm'] = 64.0
    frame['sleep_hours'] = 7.5
    frame.loc[7:, metric] = base + direction * (threshold + offset)
    trends = [event for event in build_timeline(frame, scenario='boundary')['events'] if event['type'] == 'trend_change']
    assert bool(trends) == flagged
    if flagged:
        assert trends[0]['details']['illustrative_threshold'] == threshold
        assert ('higher' if direction > 0 else 'lower') in trends[0]['explanation']


@pytest.mark.parametrize('kind', ['missing', 'nan', 'infinity', 'text', 'boolean', 'complex', 'duplicate', 'timestamp', 'reversed', 'gap', 'schema', 'duplicate_column', 'empty'])
def test_quality_failures_block_all_interpretations_and_remain_json_safe(kind):
    frame = generate_scenario('heart_rate_shift')
    if kind in {'missing', 'nan', 'infinity', 'text', 'boolean', 'complex'}:
        value = {'missing': None, 'nan': np.nan, 'infinity': np.inf, 'text': 'invalid', 'boolean': True, 'complex': 1+2j}[kind]
        frame = frame.astype({'sleep_hours': object})
        frame.at[20, 'sleep_hours'] = value
    elif kind == 'duplicate':
        frame.at[20, 'timestamp_utc'] = frame.at[19, 'timestamp_utc']
    elif kind == 'timestamp':
        frame.at[20, 'timestamp_utc'] = pd.NaT
    elif kind == 'reversed':
        frame = frame.iloc[::-1]
    elif kind == 'gap':
        frame = frame.drop(index=8)
    elif kind == 'schema':
        frame = frame.drop(columns='sleep_hours')
    elif kind == 'duplicate_column':
        frame = pd.concat([frame, frame[['sleep_hours']]], axis=1)
    else:
        frame = frame.iloc[:0]
    before = frame.copy(deep=True)
    result = build_timeline(frame, scenario='invalid_synthetic')
    assert result['assessment'] == 'DATA_QUALITY_BLOCKED'
    assert all(event['type'] not in {'trend_change', 'analysis_status'} for event in result['events'])
    findings = [event for event in result['events'] if event['type'] == 'data_quality']
    assert [event['explanation'] for event in findings] == result['quality_issues']
    assert all(event['timestamp_utc'] is None and event['details']['scope'] == 'dataset' for event in findings)
    json.dumps(result, allow_nan=False)
    pd.testing.assert_frame_equal(frame, before)


@pytest.mark.parametrize('days', [1, 7, 10])
def test_short_baseline_never_creates_trends(days):
    result = build_timeline(generate_scenario().head(days), scenario='short')
    assert result['assessment'] == 'INSUFFICIENT_DATA'
    assert result['analysis_limitations']
    assert not any(event['type'] == 'trend_change' for event in result['events'])


def test_display_order_preserves_original_indices_without_repairing_analysis():
    frame = generate_scenario().iloc[::-1]
    result = build_timeline(frame, scenario='reversed')
    observations = [event for event in result['events'] if event['type'] == 'observation']
    assert [event['observation_index'] for event in observations] == list(range(20, -1, -1))
    assert [event['timestamp_utc'] for event in observations] == sorted(event['timestamp_utc'] for event in observations)
    assert result['assessment'] == 'DATA_QUALITY_BLOCKED'


def test_fractional_timestamp_sorting_uses_instants_and_does_not_enable_analysis():
    frame = generate_scenario().head(3).copy()
    frame['timestamp_utc'] = ['2026-11-01T00:00:00.1Z', '2026-11-01T00:00:00Z', None]
    events = build_timeline(frame, scenario='invalid_cadence')['events']
    observations = [event for event in events if event['type'] == 'observation']
    assert [event['observation_index'] for event in observations] == [1, 0, 2]
    assert not any(event['type'] == 'trend_change' for event in events)
