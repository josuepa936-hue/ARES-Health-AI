"""Non-clinical quality checks and explainable demonstration rules."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from src.ares_health.validation import REQUIRED, parse_timestamps, quality_issues

# Engineering demonstration parameters ONLY. They are not medical thresholds.
METRICS = {
    "resting_hr_bpm": ("Resting heart rate", "bpm", 12.0),
    "sleep_hours": ("Sleep duration", "hours", 1.5),
}


@dataclass(frozen=True)
class ReviewFlag:
    metric: str
    baseline: float
    recent: float
    delta: float
    unit: str
    message: str


def review_changes(frame: pd.DataFrame) -> tuple[list[ReviewFlag], list[str]]:
    """Compare a 7-day reference with the latest 4 days, no diagnosis.

    A change is flagged when the absolute difference in segment means reaches or exceeds
    an explicitly illustrative threshold. Insufficient data yields no flags.
    """
    issues = quality_issues(frame)
    if issues:
        return [], issues
    ordered = frame.copy()
    ordered["timestamp_utc"] = parse_timestamps(frame["timestamp_utc"])
    if len(ordered) < 11:
        return [], ["Insufficient records: 7 baseline and 4 recent days required."]
    reference = ordered.head(7)
    recent = ordered.tail(4)
    flags: list[ReviewFlag] = []
    for key, (label, unit, threshold) in METRICS.items():
        baseline_value = float(pd.to_numeric(reference[key]).mean())
        recent_value = float(pd.to_numeric(recent[key]).mean())
        delta = recent_value - baseline_value
        if abs(delta) >= threshold:
            direction = "higher" if delta > 0 else "lower"
            msg = (
                f"{label}: recent 4-day mean is {abs(delta):.1f} {unit} {direction} "
                f"than the first 7-day reference ({baseline_value:.1f} → {recent_value:.1f} {unit}). "
                f"Reference interval: {reference.timestamp_utc.iloc[0].isoformat()} to "
                f"{reference.timestamp_utc.iloc[-1].isoformat()}; recent interval: "
                f"{recent.timestamp_utc.iloc[0].isoformat()} to {recent.timestamp_utc.iloc[-1].isoformat()}. "
                f"Review the underlying observations. This is not a diagnosis. Illustrative rule: ≥{threshold:g} {unit} change."
            )
            flags.append(ReviewFlag(key, baseline_value, recent_value, delta, unit, msg))
    return flags, []
