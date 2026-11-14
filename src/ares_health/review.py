"""Exportable operator review record for *synthetic* ARES demonstrations.

This module does not advise, diagnose, triage, or predict actual health risks.
"""
from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from src.ares_health.analysis import ReviewFlag, review_changes
from src.ares_health.validation import parse_timestamps, quality_issues

VALID_STATES = frozenset({"Pending review", "Reviewed in demo"})
DISCLAIMER = (
    "Synthetic engineering demonstration only. No astronaut measurements, "
    "medical diagnosis, NASA-approved thresholds, or clinical validation."
)


def build_review_report(
    frame: pd.DataFrame,
    *,
    scenario: str,
    flags: Sequence[ReviewFlag],
    issues: Sequence[str],
    blocked: Sequence[str] = (),
    review_state: str = "Pending review",
    reviewer_note: str = "",
) -> dict[str, Any]:
    """Return a deterministic report, independently validating its source records.

    ``flags`` is retained for caller compatibility; export uses recomputed flags.
    Supplied issues/limitations may block interpretation but cannot bypass checks.
    """
    if review_state not in VALID_STATES:
        raise ValueError("Unexpected review state")
    if len(reviewer_note) > 500:
        raise ValueError("Reviewer note must be at most 500 characters")
    # Revalidate at the export boundary, including callers supplying stale flags.
    actual_issues = quality_issues(frame)
    actual_flags, actual_blocked = review_changes(frame)
    issues = list(dict.fromkeys([*actual_issues, *issues]))
    blocked = list(dict.fromkeys([*(actual_blocked if not actual_issues else ()), *blocked]))
    flags = [] if issues or blocked else actual_flags
    if issues:
        assessment = "DATA_QUALITY_BLOCKED"
    elif blocked:
        assessment = "INSUFFICIENT_DATA"
    elif flags:
        assessment = "CHANGE_FOR_REVIEW"
    else:
        assessment = "NO_DEMO_RULE_TRIGGERED"

    date_value = None
    if frame.columns.is_unique and "timestamp_utc" in frame.columns and not frame.empty:
        valid_dates = parse_timestamps(frame["timestamp_utc"]).dropna()
        if not valid_dates.empty:
            date_value = valid_dates.max().isoformat()

    return {
        "schema_version": "1.0-demo",
        "application_version": "0.9-dev",
        "application": "ARES Health AI",
        "project": "NASA Space Apps Challenge 2026 — prototype",
        "scenario": scenario,
        "data_provenance": "synthetic",
        "observation_count": int(len(frame)),
        "last_observation_utc": date_value,
        "assessment": assessment,
        "data_quality_issues": list(issues),
        "analysis_limitations": list(blocked),
        "review_flags": [
            {
                "metric": item.metric,
                "baseline_mean": round(item.baseline, 3),
                "recent_mean": round(item.recent, 3),
                "difference": round(item.delta, 3),
                "unit": item.unit,
                "explanation": item.message,
            }
            for item in flags
        ],
        "review_state": review_state,
        "reviewer_note": reviewer_note.strip(),
        "suggested_demonstration_workflow": [
            "Inspect source, units and missing values",
            "Review displayed individual reference and recent observations",
            "Document the finding; in a real mission, use approved procedures and qualified personnel",
        ],
        "methodology": "First 7 synthetic days compared with last 4; illustrative absolute-mean-difference rules.",
        "disclaimer": DISCLAIMER,
    }
