"""Deterministic mission history for fictional daily observations only.

Trend events describe evaluations of growing prefixes, not clinical events or
estimated change onsets. Whole-dataset validation gates every interpretation.
"""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from src.ares_health.analysis import METRICS, review_changes
from src.ares_health.review import DISCLAIMER, build_review_report
from src.ares_health.service import MEASUREMENT_COLUMNS, serialize_records
from src.ares_health.validation import REQUIRED, parse_timestamps, quality_issues
from src.ares_health.version import APP_VERSION


def _observations(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Reuse canonical JSON formatting, safely withholding malformed cells.

    Structural failures yield no observations. Unusable numeric values become
    null; finite out-of-range values remain visible, accompanied by blockers.
    No source record is altered or filled for analysis.
    """
    if not frame.columns.is_unique or any(name not in frame for name in REQUIRED):
        return []
    display = frame.copy(deep=True)
    for name in MEASUREMENT_COLUMNS:
        unsupported = display[name].map(
            lambda value: isinstance(value, (bool, np.bool_, complex, np.complexfloating))
        )
        display[name] = pd.to_numeric(display[name].mask(unsupported), errors="coerce")
    return serialize_records(display)


def build_timeline(frame: pd.DataFrame, *, scenario: str) -> dict[str, Any]:
    """Build a strict-JSON-safe, clock-free history without changing domain rules.

    Valid prefixes are evaluated starting at 11 observations using the existing
    first-seven/latest-four comparison. Any quality failure anywhere suppresses
    all trend evaluations. Quality findings apply to the dataset and have no
    invented timestamp. Display sorting never repairs data for interpretation.
    """
    issues = quality_issues(frame)
    report = build_review_report(frame, scenario=scenario, flags=[], issues=issues)
    observations = _observations(frame)
    events: list[dict[str, Any]] = []

    def append(kind: str, timestamp: str | None, index: int | None,
               explanation: str, details: dict[str, Any]) -> None:
        events.append({
            "id": f"event-{len(events) + 1:06d}",
            "type": kind,
            "timestamp_utc": timestamp,
            "observation_index": index,
            "explanation": explanation,
            "details": details,
        })

    # Keep original positions for traceability, including when display order differs.
    ordered = sorted(enumerate(observations), key=lambda pair: (
        pair[1]["timestamp_utc"] is None,
        pd.Timestamp(pair[1]["timestamp_utc"]) if pair[1]["timestamp_utc"] else 0,
        pair[0]
    ))
    for index, observation in ordered:
        timestamp = observation["timestamp_utc"]
        append("observation", timestamp, index,
               "Fictional daily observation; values are not a medical assessment.", observation)
        if issues:
            continue
        prefix = frame.iloc[:index + 1]
        flags, blocked = review_changes(prefix)
        if index == 0 or index == 10:
            append("analysis_status", timestamp, index,
                   blocked[0] if blocked else (
                       "Seven reference days and four recent days are available for illustrative comparisons."
                   ), {"state": "INSUFFICIENT_DATA" if blocked else "COMPARISON_AVAILABLE"})
        dates = parse_timestamps(prefix["timestamp_utc"])
        for flag in flags:
            append("trend_change", timestamp, index, flag.message, {
                "metric": flag.metric,
                "baseline_mean": flag.baseline,
                "recent_mean": flag.recent,
                "difference": flag.delta,
                "unit": flag.unit,
                "illustrative_threshold": METRICS[flag.metric][2],
                "reference_start_utc": dates.iloc[0].isoformat().replace("+00:00", "Z"),
                "reference_end_utc": dates.iloc[6].isoformat().replace("+00:00", "Z"),
                "recent_start_utc": dates.iloc[-4].isoformat().replace("+00:00", "Z"),
                "recent_end_utc": timestamp,
            })

    for issue in issues:
        append("data_quality", None, None, issue, {
            "scope": "dataset", "state": "DATA_QUALITY_BLOCKED",
            "effect": "All trend interpretations are withheld for this dataset.",
        })
    return {
        "schema_version": "1.0-timeline",
        "application": "ARES Health AI",
        "application_version": APP_VERSION,
        "scenario": scenario,
        "data_provenance": "synthetic",
        "simulation_only": True,
        "assessment": report["assessment"],
        "observation_count": len(frame),
        "events": events,
        "quality_issues": issues,
        "analysis_limitations": report["analysis_limitations"],
        "methodology": {
            "reference_days": 7, "recent_days": 4,
            "illustrative_rules": {
                key: {"absolute_difference": threshold, "unit": unit}
                for key, (_, unit, threshold) in METRICS.items()
            },
            "note": (
                "Trend events evaluate each available prefix, not onset or diagnosis. "
                "Repeated flags describe overlapping comparison windows. "
                "The assessment describes the final dataset. Any quality failure "
                "suppresses every trend event, including earlier prefixes."
            ),
        },
        "disclaimer": DISCLAIMER,
    }
