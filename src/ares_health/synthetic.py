"""Reproducible DEMONSTRATION data. No real astronaut records."""
from __future__ import annotations

import numpy as np
import pandas as pd

SCENARIOS = {
    "Stable observations": "stable",
    "Resting heart rate shift": "heart_rate_shift",
    "Shortened sleep": "sleep_shift",
    "Incomplete records": "incomplete",
}


def generate_scenario(scenario: str = "stable", *, seed: int = 2026, days: int = 21) -> pd.DataFrame:
    """Create entirely fictitious daily observations.

    These distributions are not validated astronaut reference ranges.
    """
    if scenario not in SCENARIOS.values():
        raise ValueError(f"Unknown synthetic scenario: {scenario}")
    if days < 12:
        raise ValueError("At least 12 days are needed to demonstrate a baseline")

    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-11-01", periods=days, freq="D", tz="UTC")
    heart_rate = rng.normal(64, 1.8, days)
    sleep = rng.normal(7.5, 0.25, days)
    activity = rng.normal(42, 5, days)

    if scenario == "heart_rate_shift":
        heart_rate[-4:] += 16
    elif scenario == "sleep_shift":
        sleep[-4:] -= 2.5
    elif scenario == "incomplete":
        heart_rate[-3:] = np.nan
        sleep[-2:] = np.nan

    return pd.DataFrame({
        "timestamp_utc": dates,
        "crew_id": "SIM-001",
        "resting_hr_bpm": np.round(heart_rate, 1),
        "sleep_hours": np.round(sleep, 2),
        "activity_minutes": np.round(np.maximum(activity, 0), 0).astype(int),
        "source_type": "synthetic",
    })
