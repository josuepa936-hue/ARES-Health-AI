"""Non-clinical quality checks and explainable demonstration rules."""
from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

REQUIRED = ("timestamp_utc", "crew_id", "resting_hr_bpm", "sleep_hours", "activity_minutes", "source_type")
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


def quality_issues(frame: pd.DataFrame) -> list[str]:
    """Report missing, non-finite or structurally invalid observations."""
    problems: list[str] = []
    missing = [name for name in REQUIRED if name not in frame.columns]
    if missing:
        return ["Missing required columns: " + ", ".join(missing)]
    if frame.empty:
        return ["No records were supplied."]

    dt = pd.to_datetime(frame["timestamp_utc"], utc=True, errors="coerce")
    if dt.isna().any():
        problems.append("Some timestamps cannot be parsed.")
    if dt.duplicated().any():
        problems.append("Duplicate timestamps detected.")
    if frame["crew_id"].nunique(dropna=False) != 1:
        problems.append("The dataset must contain a single synthetic crew profile.")
    if frame["source_type"].isna().any() or not frame["source_type"].eq("synthetic").all():
        problems.append("Only clearly marked synthetic records are supported by this demo.")

    ranges = {
        "resting_hr_bpm": (0, 250),
        "sleep_hours": (0, 24),
        "activity_minutes": (0, 1440),
    }
    for column, (lower, upper) in ranges.items():
        values = pd.to_numeric(frame[column], errors="coerce")
        if values.isna().any():
            problems.append(f"Missing or nonnumeric {column}: {int(values.isna().sum())} rows.")
        invalid = values.notna() & ~values.between(lower, upper, inclusive="both")
        if column == "resting_hr_bpm":
            invalid = invalid | values.eq(0)
        if invalid.any():
            problems.append(f"Invalid {column} values: {int(invalid.sum())} rows.")
    return problems


def review_changes(frame: pd.DataFrame) -> tuple[list[ReviewFlag], list[str]]:
    """Compare a 7-day reference with the latest 4 days, no diagnosis.

    A change is flagged when the absolute difference in segment means exceeds
    an explicitly illustrative threshold. Insufficient data yields no flags.
    """
    issues = quality_issues(frame)
    if issues:
        return [], issues
    ordered = frame.sort_values("timestamp_utc")
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
                f"Review the underlying observations. Illustrative rule: ≥{threshold:g} {unit} change."
            )
            flags.append(ReviewFlag(key, baseline_value, recent_value, delta, unit, msg))
    return flags, []
