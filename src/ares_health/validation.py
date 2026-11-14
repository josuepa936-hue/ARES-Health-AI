"""Validate the single-profile, daily synthetic demonstration data contract."""
from __future__ import annotations

import numpy as np
import pandas as pd

REQUIRED = ("timestamp_utc", "crew_id", "resting_hr_bpm", "sleep_hours", "activity_minutes", "source_type")
# Input sanity bounds only, never clinical decision thresholds.
RANGES = {"resting_hr_bpm": (0, 250), "sleep_hours": (0, 24), "activity_minutes": (0, 1440)}


def parse_timestamps(values: pd.Series) -> pd.Series:
    """Normalize datetime objects and mixed ISO strings to UTC; reject numeric epochs."""
    normalized = values.map(lambda value: None if isinstance(value, (int, float, bool, np.number)) else value)
    return pd.to_datetime(normalized, utc=True, errors="coerce", format="mixed")


def quality_issues(frame: pd.DataFrame) -> list[str]:
    """Return blocking findings without mutating, sorting, or filling source records."""
    if not frame.columns.is_unique:
        return ["Duplicate column names are unsupported."]
    missing = [name for name in REQUIRED if name not in frame.columns]
    if missing:
        return ["Missing required columns: " + ", ".join(missing)]
    if frame.empty:
        return ["No records were supplied."]
    problems: list[str] = []
    dt = parse_timestamps(frame["timestamp_utc"])
    if dt.isna().any():
        problems.append("Missing or invalid timestamps detected.")
    if dt.dropna().duplicated().any():
        problems.append("Duplicate timestamps detected.")
    if dt.notna().all():
        if not dt.is_monotonic_increasing:
            problems.append("Records must be in chronological UTC order.")
        elif not dt.diff().dropna().dt.total_seconds().eq(86400).all():
            problems.append("Daily records must be spaced exactly one day apart; gaps or multiple observations per day are unsupported.")
    crew = frame["crew_id"]
    if not crew.map(lambda value: isinstance(value, str) and bool(value.strip())).all() or crew.nunique(dropna=False) != 1:
        problems.append("The dataset must contain a single nonblank synthetic crew profile.")
    if not frame["source_type"].eq("synthetic").fillna(False).all():
        problems.append("Only clearly marked synthetic records are supported by this demo.")
    for column, (lower, upper) in RANGES.items():
        raw = frame[column]
        unsupported = raw.map(lambda value: isinstance(value, (bool, np.bool_, complex, np.complexfloating)))
        values = pd.to_numeric(raw.mask(unsupported), errors="coerce")
        if values.isna().any():
            problems.append(f"Missing or nonnumeric {column}: {int(values.isna().sum())} rows.")
        invalid = values.notna() & ~values.between(lower, upper)
        invalid |= unsupported
        if column == "resting_hr_bpm":
            invalid |= values.eq(0)
        if invalid.any():
            problems.append(f"Invalid {column} values: {int(invalid.sum())} rows.")
    return problems
