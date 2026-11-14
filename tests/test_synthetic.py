"""Behavioral tests; these do not establish clinical accuracy."""
from src.ares_health.analysis import quality_issues, review_changes
from src.ares_health.synthetic import generate_scenario


def test_stable_scenario_does_not_trigger_demo_rules():
    flags, issues = review_changes(generate_scenario("stable"))
    assert not issues
    assert flags == []


def test_heart_rate_shift_is_explained():
    flags, issues = review_changes(generate_scenario("heart_rate_shift"))
    assert not issues
    assert any(f.metric == "resting_hr_bpm" and "first 7-day" in f.message for f in flags)


def test_sleep_shift_is_explained():
    flags, issues = review_changes(generate_scenario("sleep_shift"))
    assert not issues
    assert any(f.metric == "sleep_hours" for f in flags)


def test_incomplete_data_blocks_rule_evaluation():
    frame = generate_scenario("incomplete")
    assert quality_issues(frame)
    flags, issues = review_changes(frame)
    assert flags == []
    assert issues


def test_repeatability():
    assert generate_scenario("stable", seed=5).equals(generate_scenario("stable", seed=5))
