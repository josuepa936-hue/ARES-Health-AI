"""Exploratory statistical descriptions for fictional daily mission records.

None of these statistics is a medical risk score, diagnosis, or alert trigger.
The pre-existing transparent demonstration flags remain the sole rule engine.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import numpy as np
import pandas as pd
from scipy.stats import median_abs_deviation, theilslopes

from src.ares_health.validation import quality_issues

SIGNALS = {
    "resting_hr_bpm": ("Resting heart rate", "bpm", "Cardiovascular", "#37C7F4"),
    "sleep_hours": ("Sleep duration", "hours", "Sleep & Recovery", "#A9A0FF"),
    "activity_minutes": ("Daily activity", "min/day", "Musculoskeletal", "#5BE5B2"),
}


@dataclass(frozen=True)
class SignalSummary:
    metric: str
    label: str
    unit: str
    system: str
    color: str
    baseline_mean: float
    recent_mean: float
    delta: float
    full_median: float
    robust_variability: float
    theil_sen_slope_per_day: float
    n: int

    def as_record(self) -> dict:
        return asdict(self)


def describe_signals(frame: pd.DataFrame) -> list[SignalSummary]:
    """Return descriptive results only when ALL source observations are valid.

    Baseline: first seven days. Recent: last four days.
    Robust spread: median absolute deviation normalized to a Gaussian scale.
    Trend: Theil–Sen slope estimated against day indices.
    """
    if quality_issues(frame) or len(frame) < 11:
        return []
    results = []
    for key, (label, unit, system, color) in SIGNALS.items():
        data = pd.to_numeric(frame[key], errors="raise").to_numpy(dtype=float)
        if not np.isfinite(data).all():
            return []
        baseline = float(np.mean(data[:7]))
        recent = float(np.mean(data[-4:]))
        robust_spread = float(median_abs_deviation(data, scale="normal"))
        slope = float(theilslopes(data, np.arange(len(data), dtype=float)).slope)
        results.append(
            SignalSummary(
                metric=key, label=label, unit=unit, system=system, color=color,
                baseline_mean=baseline, recent_mean=recent, delta=recent - baseline,
                full_median=float(np.median(data)),
                robust_variability=robust_spread,
                theil_sen_slope_per_day=slope,
                n=len(data),
            )
        )
    return results


def signal_records(items: list[SignalSummary]) -> list[dict]:
    """Simple dict rows for plotting and optional later review exports."""
    return [item.as_record() for item in items]
