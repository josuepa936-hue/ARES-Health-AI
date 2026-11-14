"""Plotly mission visualization regression checks."""
import pandas as pd
import pytest
from src.ares_health.advanced_stats import describe_signals
from src.ares_health.mission_viz import (
    SYSTEMS, SYSTEM_METRICS, make_body_map, make_signal_chart,
)
from src.ares_health.synthetic import generate_scenario


def test_each_supported_signal_has_valid_chart():
    frame = generate_scenario()
    summaries = {x.metric: x for x in describe_signals(frame)}
    for metric in ["resting_hr_bpm", "sleep_hours", "activity_minutes"]:
        fig = make_signal_chart(frame, metric, summaries[metric])
        assert len(fig.data) == 2
        assert fig.layout.height == 380


def test_missing_data_never_connected_or_assigned_fake_baseline():
    frame = generate_scenario("incomplete")
    assert not describe_signals(frame)
    fig = make_signal_chart(frame, "resting_hr_bpm")
    assert len(fig.data) == 1
    assert fig.data[0].connectgaps is False
    assert pd.isna(fig.data[0].y[-1])


def test_plot_rejects_unknown_metric():
    with pytest.raises(ValueError):
        make_signal_chart(generate_scenario(), "glucose_mg_dl")


def test_schematic_has_only_three_described_hotspots():
    for selected in SYSTEMS:
        fig = make_body_map(selected)
        assert len(fig.data) == 1
        assert tuple(fig.data[0].customdata) == SYSTEMS
        assert len(fig.data[0].x) == 3
        assert len(fig.layout.shapes) >= 5
        assert SYSTEM_METRICS[selected]


def test_schematic_rejects_unsupported_system():
    with pytest.raises(ValueError):
        make_body_map("Radiation dose")
