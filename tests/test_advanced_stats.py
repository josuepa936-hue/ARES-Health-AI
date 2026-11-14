"""V0.8 statistical exploration tests; not medical efficacy testing."""
import math

import pandas as pd
import pytest

from src.ares_health.advanced_stats import describe_signals, signal_records
from src.ares_health.synthetic import generate_scenario


def test_stable_returns_three_distinct_exploratory_signals():
    rows = describe_signals(generate_scenario("stable"))
    assert len(rows) == 3
    assert [r.metric for r in rows] == [
        "resting_hr_bpm", "sleep_hours", "activity_minutes"
    ]
    assert all(r.n == 21 for r in rows)
    assert all(math.isfinite(r.theil_sen_slope_per_day) for r in rows)


@pytest.mark.parametrize("scenario,metric,sign", [
    ("heart_rate_shift", "resting_hr_bpm", 1),
    ("sleep_shift", "sleep_hours", -1),
])
def test_shift_direction_is_explained(scenario, metric, sign):
    summaries = {x.metric: x for x in describe_signals(generate_scenario(scenario))}
    assert summaries[metric].delta * sign > 0


def test_invalid_data_prevents_misleading_statistics():
    assert describe_signals(generate_scenario("incomplete")) == []
    assert describe_signals(generate_scenario().head(7)) == []


def test_robust_spread_is_nonnegative_and_fixed_seed_reproducible():
    a = describe_signals(generate_scenario(seed=2026))
    b = describe_signals(generate_scenario(seed=2026))
    assert signal_records(a) == signal_records(b)
    assert all(x.robust_variability >= 0 for x in a)


def test_constant_values_have_zero_trend_and_dispersion():
    df = generate_scenario()
    df["resting_hr_bpm"] = 64
    summary = describe_signals(df)[0]
    assert summary.robust_variability == pytest.approx(0.0)
    assert summary.theil_sen_slope_per_day == pytest.approx(0.0)


def test_numeric_csv_columns_can_be_analyzed():
    df = generate_scenario()
    df["sleep_hours"] = df["sleep_hours"].astype(str)
    assert len(describe_signals(df)) == 3
