"""Strict, local-only importer for clearly labeled SYNTHETIC daily CSV data.

CSV metadata cannot prove a dataset is fictional: users must also attest that
it contains no real personal, patient or astronaut health records.
"""
from __future__ import annotations

import csv
import io
import re

import pandas as pd

from src.ares_health.validation import REQUIRED, parse_timestamps, quality_issues

MAX_CSV_BYTES = 1_000_000
MAX_CSV_ROWS = 366
UTC_SUFFIX = re.compile(r"(?:Z|\+00:00)$")
SYNTHETIC_CREW = re.compile(r"^SIM-[A-Za-z0-9_-]{1,24}$")
MEASUREMENTS = ("resting_hr_bpm", "sleep_hours", "activity_minutes")


def load_synthetic_csv(payload: bytes) -> tuple[pd.DataFrame | None, list[str]]:
    """Read a small UTF-8 CSV safely, returning a validated frame or errors.

    No file is written to disk or uploaded to an external service by this
    function. It rejects unsupported structures before plotting or analysis.
    """
    if not isinstance(payload, bytes):
        return None, ["Expected an uploaded CSV file."]
    if not payload:
        return None, ["The CSV file is empty."]
    if len(payload) > MAX_CSV_BYTES:
        return None, [f"CSV exceeds the {MAX_CSV_BYTES:,}-byte demonstration limit."]
    if b"\x00" in payload:
        return None, ["NUL bytes are not supported in CSV files."]

    try:
        decoded = payload.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None, ["File must be UTF-8 encoded (UTF-8 BOM is supported)."]

    try:
        rows = list(csv.reader(io.StringIO(decoded, newline=""), strict=True))
    except csv.Error:
        return None, ["Malformed CSV quoting or structure."]

    if not rows:
        return None, ["CSV must have a header and at least one observation."]
    header = rows[0]
    if len(header) != len(set(header)):
        return None, ["Duplicate column headers are not allowed."]
    if len(header) != len(REQUIRED) or set(header) != set(REQUIRED):
        missing = sorted(set(REQUIRED) - set(header))
        extra = sorted(set(header) - set(REQUIRED))
        details = []
        if missing:
            details.append("missing: " + ", ".join(missing))
        if extra:
            details.append("unsupported: " + ", ".join(extra))
        return None, ["Columns must match the six documented demo fields"
                      + (" (" + "; ".join(details) + ")" if details else "") + "."]
    data_rows = rows[1:]
    if not data_rows:
        return None, ["CSV contains no observation rows."]
    if len(data_rows) > MAX_CSV_ROWS:
        return None, [f"CSV has more than {MAX_CSV_ROWS} observation rows."]
    for index, row in enumerate(data_rows, start=2):
        if len(row) != len(header):
            return None, [f"Row {index} has {len(row)} cells, expected {len(header)}."]

    raw = pd.DataFrame(data_rows, columns=header)
    issues = quality_issues(raw)

    if not raw["crew_id"].map(lambda value: bool(SYNTHETIC_CREW.fullmatch(value))).all():
        issues.append("Crew IDs must use fictional SIM- identifiers, such as SIM-001.")
    if not raw["timestamp_utc"].map(lambda value: bool(UTC_SUFFIX.search(value.strip()))).all():
        issues.append("Dates must include an explicit UTC timezone: Z or +00:00.")
    if issues:
        return None, list(dict.fromkeys(issues))

    normalized = raw.copy()
    normalized["timestamp_utc"] = parse_timestamps(raw["timestamp_utc"])
    for field in MEASUREMENTS:
        normalized[field] = pd.to_numeric(raw[field], errors="raise")
    return normalized, []
