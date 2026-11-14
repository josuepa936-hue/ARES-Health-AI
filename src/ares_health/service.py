"""Shared, side-effect-free snapshots for ARES's synthetic demo interfaces.

Streamlit and any future React frontend can consume the exact same domain
rules. Dataframes remain in-memory; no astronaut records or external services.
"""
from __future__ import annotations

from dataclasses import asdict
import math
from typing import Any

import pandas as pd

from src.ares_health.analysis import METRICS, review_changes
from src.ares_health.advanced_stats import describe_signals, signal_records
from src.ares_health.evidence import get_crew_guidance
from src.ares_health.review import build_review_report
from src.ares_health.validation import REQUIRED, parse_timestamps, quality_issues

MEASUREMENT_COLUMNS = ("resting_hr_bpm", "sleep_hours", "activity_minutes")
SCHEMA_VERSION = "1.0-demo"


def serialize_records(frame: pd.DataFrame) -> list[dict[str, Any]]:
    """Make valid or incomplete fictional observations strict-JSON safe.

    Missing values become JSON null rather than NaN; UTC timestamps are ISO 8601.
    The six-field daily data contract remains unchanged.
    """
    timestamps = parse_timestamps(frame["timestamp_utc"])
    output: list[dict[str, Any]] = []
    for index, (_, source) in enumerate(frame.iterrows()):
        record: dict[str, Any] = {}
        for column in REQUIRED:
            value = source[column]
            if column == "timestamp_utc":
                dt = timestamps.iloc[index]
                record[column] = None if pd.isna(dt) else dt.isoformat().replace("+00:00", "Z")
            elif column in MEASUREMENT_COLUMNS:
                if pd.isna(value):
                    record[column] = None
                else:
                    number = float(value)
                    record[column] = number if math.isfinite(number) else None
            else:
                record[column] = None if pd.isna(value) else str(value)
        output.append(record)
    return output


def build_snapshot(
    frame: pd.DataFrame,
    *,
    scenario: str,
    include_report: bool = False,
    review_state: str = "Pending review",
    reviewer_note: str = "",
) -> dict[str, Any]:
    """Single canonical, non-clinical interface payload.

    It delegates all quality and trend decisions to the existing modules.
    No descriptive statistic bypasses data-quality failures.
    """
    issues = quality_issues(frame)
    flags, blocked = review_changes(frame)
    limitations = [] if issues else blocked
    guidance = get_crew_guidance(issues, limitations, flags)
    report = build_review_report(
        frame, scenario=scenario, flags=flags, issues=issues,
        blocked=limitations, review_state=review_state, reviewer_note=reviewer_note,
    )
    missing_cells = sum(int(frame[name].isna().sum()) for name in MEASUREMENT_COLUMNS)
    total_cells = len(frame) * len(MEASUREMENT_COLUMNS)
    completeness = round(100 * (1 - missing_cells / total_cells), 2) if total_cells else 0.0
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "application": "ARES Health AI",
        "scenario": scenario,
        "data_provenance": "synthetic",
        "simulation_only": True,
        "assessment": report["assessment"],
        "summary": {
            "recorded_days": len(frame),
            "completeness_pct": completeness,
            "quality_findings": len(issues),
            "review_flags": len(report["review_flags"]),
            "crew_id": str(frame["crew_id"].iloc[0]),
        },
        "observations": serialize_records(frame),
        "quality_issues": issues,
        "analysis_limitations": limitations,
        "review_flags": report["review_flags"],
        "descriptive_signals": signal_records(describe_signals(frame)),
        "descriptive_statistics_notice": (
            "Exploratory statistics only; not clinically validated, not a medical alert, "
            "and never computed when data quality blocks interpretation."
        ),
        "guidance": asdict(guidance),
        "methodology": {
            "reference_days": 7,
            "recent_days": 4,
            "illustrative_rules": {
                key: {"absolute_difference": threshold, "unit": unit}
                for key, (_, unit, threshold) in METRICS.items()
            },
            "note": (
                "Engineering demonstration settings, not NASA clinical thresholds. "
                "Intermediate days do not participate in the two means."
            ),
        },
        "disclaimer": report["disclaimer"],
    }
    if include_report:
        result["review_report"] = report
    return result
