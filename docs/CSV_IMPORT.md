# ARES Health AI v0.6 — Synthetic CSV upload

This feature processes **synthetic-only** test records in memory on the local Streamlit server. It has **not** been validated for real health data, diagnosis or astronaut decision-making. Never upload real patient, astronaut, or personally identifiable health records.

## How to try the importer

1. Start the local app: `python -m streamlit run app.py`.
2. In the left sidebar, select **Upload synthetic CSV**.
3. Download the **sample synthetic CSV** and inspect it.
4. Upload that sample, then explicitly confirm it contains only fictional records.
5. The dashboard displays the data and computes illustrative trend review flags.
6. To demonstrate validation, try editing an exported copy to remove a measurement or timestamp. The importer should reject it with a clear explanation; no analysis or charts are shown for rejected uploads.

The built-in **Stable observations**, **Resting heart rate shift**, **Shortened sleep**, and **Incomplete records** scenarios remain available.

## Accepted CSV schema (six columns; header order may vary)

| Field | Example | Requirement |
|---|---|---|
| `timestamp_utc` | `2026-11-01 00:00:00+00:00` | Explicit UTC `Z` or `+00:00`, daily consecutive records |
| `crew_id` | `SIM-001` | Single fictional identifier matching `SIM-...` |
| `resting_hr_bpm` | `64.2` | Numeric, strictly positive and at most 250 (input sanity, not clinical limit) |
| `sleep_hours` | `7.6` | Numeric between 0 and 24 |
| `activity_minutes` | `42` | Numeric between 0 and 1440 |
| `source_type` | `synthetic` | Every row must be marked synthetic |

- CSV is UTF-8 with optional UTF-8 BOM.
- Maximum file size: 1,000,000 bytes; maximum observations: 366.
- Strictly six columns, with no duplicate headers or malformed rows.
- Dates must be valid, unique, ordered and spaced exactly 24 hours apart.
- Missing or nonnumeric values, invalid measurements, or inconsistent profiles block analysis.
- Valid files with fewer than 11 observations can be displayed but have **insufficient data** for the 7-day baseline and 4-day comparison.
- Self-declared `synthetic` provenance is a label, not proof. Users must explicitly attest fictional origin.

**Important:** ARES uses demonstration thresholds: 12 bpm resting HR difference and 1.5 hours sleep difference. These are not diagnostic criteria, NASA standards, or scientific claims about spaceflight risk.

## Verification

```powershell
python -m pytest -q
python -m streamlit run app.py
```

The feature does not call external APIs and the import function does not persist uploaded files on disk. Streamlit itself is a locally running web server, not flight hardware. Any data sharing that happens outside ARES is the responsibility of the user and hosting environment.
