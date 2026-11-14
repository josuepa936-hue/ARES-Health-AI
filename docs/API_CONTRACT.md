# ARES Health AI — Local API Contract (v1.0)

**Purpose:** Expose the existing synthetic, explainable Python domain engine to a later React/Figma-driven user interface without changing the stable Streamlit app.

**Not production-ready medical infrastructure.** This is a laptop-local, fictional-data-only service. It has no authorization, rate limiter, persistent data store, clinical validation, onboard sensor integrations, NASA telemetry, or medical treatment recommendations. **Never expose Uvicorn to a public network**.

## Start locally

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

- API documentation: http://127.0.0.1:8000/docs
- OpenAPI document: http://127.0.0.1:8000/openapi.json
- Existing Streamlit app still runs separately with `python -m streamlit run app.py`.
- The API currently responds only to local browser origins on port `5173` or `3000` (both localhost and 127.0.0.1). CORS is not authentication, and **binding to loopback is essential**.

## Routes and data contract

| Route | Method | Description |
|---|---|---|
| `/api/status` | GET | Status of the software service; **not** a human-health status |
| `/api/scenarios` | GET | Stable IDs and labels for four fictional cases |
| `/api/timeline` | GET | Deterministic fictional observations, quality findings and prefix-based trend explanations |
| `/api/demo` | GET | Synthetic daily records, quality states, flags and guidance for `scenario`, `seed`, `days` |
| `/api/evidence` | GET | Official NASA/CSA research **reference links**; no NASA or CSA data ingested |
| `/api/review` | POST JSON | Original defensive report for a selected built-in fictional scenario and optional demo reviewer note |
| `/api/synthetic-csv` | POST raw text/csv | In-memory validated CSV (max 1,000,000 bytes), explicit fictional-data attestation, returns a snapshot + report |

`GET /api/demo` query defaults: `scenario=stable`, `seed=2026` (0–999,999), `days=21` (12–366). Allowed scenario IDs:
`stable`, `heart_rate_shift`, `sleep_shift`, `incomplete`.

The JSON snapshot contains:
- `schema_version`, `application`, `scenario`, `data_provenance="synthetic"`, `simulation_only=true`.
- `assessment` and `summary` (days, completeness %, issue/flag counts, fictional crew ID).
- `observations[]` with the exact six existing fields: `timestamp_utc`, `crew_id`, `resting_hr_bpm`, `sleep_hours`, `activity_minutes`, `source_type`. UTC timestamps are ISO 8601 strings ending `Z`; missing measurements become JSON `null`, not `NaN`.
- `quality_issues[]`, `analysis_limitations[]`, `review_flags[]`, `guidance`, `methodology`, `disclaimer`.
- `descriptive_signals[]`: three SciPy statistical summaries (means, median, Gaussian-scaled MAD and Theil–Sen slope per day), **empty when data are invalid or insufficient**. These are descriptive and do not generate additional alerts. `descriptive_statistics_notice` explains the limitation.
- `review_report` when using `POST /api/synthetic-csv` (also returned on `POST /api/review` as the full body).

### Scenario example

```powershell
Invoke-RestMethod "http://127.0.0.1:8000/api/demo?scenario=heart_rate_shift&seed=2026&days=21"
```

### Review example

```powershell
$body = @{ scenario="stable"; review_state="Reviewed in demo"; reviewer_note="Checked fictional data." } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/api/review" -ContentType "application/json" -Body $body
```

### CSV example

A client must send raw UTF-8 bytes with `Content-Type: text/csv` and `X-Synthetic-Attestation: true`. This is **not** a multipart form upload. The API only accepts the six-column existing contract, `SIM-` identifiers, UTC dates and synthetic provenance. The attestation is not proof and no real health records should be submitted.

```javascript
const file = document.querySelector('input[type=file]').files[0];
const response = await fetch('http://127.0.0.1:8000/api/synthetic-csv', {
  method: 'POST',
  headers: {
    'Content-Type': 'text/csv',
    'X-Synthetic-Attestation': 'true'
  },
  body: await file.arrayBuffer()
});
const data = await response.json();
if (!response.ok) throw new Error(JSON.stringify(data.detail));
```

HTTP failures:
- `400`: missing/false synthetic attestation, or malformed Content-Length.
- `413`: more than 1 MB.
- `415`: media type other than text/csv.
- `422`: invalid route parameters or CSV rejected after strict checks.

### Frontend workflow

```text
Figma-approved interface (future)
        |
     React UI    ← only controlled synthetic files and demo scenarios
        |
  local FastAPI /api/* (v1.0)
        |
    service.py : canonical snapshot, strict JSON conversion
        |
    Existing domain: synthetic, validation, analysis, evidence, review
```

The current Streamlit app uses these same domain modules directly; `main` remains the working fallback. The Figma design is **not** connected yet. This API does not generate a medical diagnosis, determine astronaut fitness or provide real-time data.

## Verification

```powershell
python -m pytest -q
python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

Automated tests cover all four scenarios, normalized JSON for missing data, deterministic reports, strict CSV size/provenance and local CORS. GitHub Actions runs Python 3.12/3.13. Passing tests only establishes software behavior, never clinical efficacy.

## Mission Timeline & Explainability — v1.0

`GET /api/timeline?scenario=heart_rate_shift&seed=2026&days=21`

This is a stateless generated-scenario endpoint. It accepts the same scenario IDs,
defaults and limits as `/api/demo`: scenario `stable`, seed 2026 (0–999999), days
21 (12–366). Invalid parameters return HTTP 422 using FastAPI's existing `detail`
format. A valid request for `incomplete` returns HTTP 200 with a blocked quality
assessment, not a transport error. No uploaded file, patient identifier, wall-clock
time, authentication token or stored mission state is used. The existing strict
`POST /api/synthetic-csv` contract is unchanged and does not accept invalid data
to manufacture a timeline. The pure `timeline.build_timeline` function can consume
validated synthetic CSV frames in Python; no CSV timeline upload route is added.

### Response envelope

| Field | Contract |
|---|---|
| `schema_version` | `1.0-timeline` (separate from snapshot/report schemas) |
| `application`, `application_version` | `ARES Health AI`, `1.0` |
| `scenario` | Selected fictional scenario ID |
| `data_provenance`, `simulation_only` | `synthetic`, `true` |
| `assessment` | Canonical **final dataset** assessment from the defensive report module |
| `observation_count` | Number of source rows |
| `events` | Ordered events described below |
| `quality_issues` | Canonical dataset validation findings |
| `analysis_limitations` | Canonical final-analysis availability limitations |
| `methodology` | Reference/recent window sizes, unchanged rules, explanation of historical evaluations |
| `disclaimer` | Existing synthetic-only, non-clinical report disclaimer |

All events have these fields:

- `id`: deterministic response-local `event-000001`, etc.; sequential in output
  order. These are not cross-request database identities.
- `type`: `observation`, `analysis_status`, `trend_change` or `data_quality`.
- `timestamp_utc`: ISO 8601 UTC ending `Z`, or `null` when no event time can be
  attributed. It is never the server's current time.
- `observation_index`: zero-based source row **position**, or `null` for
  dataset-wide quality events; unrelated to a Pandas index label.
- `explanation`: English human-readable description using existing rule explanations.
- `details`: event-specific object, below.

| Type | Details and semantics |
|---|---|
| `observation` | The existing six-field observation contract, using the canonical JSON serializer. Missing, nonnumeric, boolean, complex or nonfinite measurements are `null` for display. Finite out-of-range measurements remain visible. Display conversion never repairs input for analysis. |
| `analysis_status` | `state=INSUFFICIENT_DATA` at the first valid observation; `state=COMPARISON_AVAILABLE` at observation 11. Availability is not medical clearance. |
| `trend_change` | `metric`, `baseline_mean`, `recent_mean`, signed `difference`, `unit`, `illustrative_threshold`, and `reference_start_utc`, `reference_end_utc`, `recent_start_utc`, `recent_end_utc`. Numerical values are unrounded domain means/differences. |
| `data_quality` | `scope=dataset`, `state=DATA_QUALITY_BLOCKED`, and an `effect` explanation. One event per canonical finding, with `timestamp_utc=null` and `observation_index=null`; findings are not claimed to originate on a specific day. |

### Ordering, history and blocking

Observation events are ordered chronologically by normalized UTC instant, with
source position breaking ties. Unparseable timestamps are last. Each valid
observation is followed by its status/trend events; metrics follow existing rule
order (heart rate, then sleep). Dataset quality findings follow observations in
canonical validation order. Structural failures (missing/duplicate columns) yield
no observation events. Empty input yields a quality finding. Source frames remain
unchanged; sorting is only for display and cannot bypass chronology validation.

For a valid dataset, every prefix of at least 11 observations is evaluated by the
existing `review_changes` function: first seven reference days versus latest four
recent days. Flags retain inclusive absolute differences of **12 bpm** and **1.5
hours**, in either direction. Activity has no change rule. Intermediate days do
not enter either mean. Trend event time is the comparison window's last day,
**not** an estimated physiological change onset. A continuing flag may appear
on successive days because windows overlap; this is not a set of independent
clinical events. Earlier flags may remain in the timeline even if the final
assessment has no flag. Stable scenarios do not manufacture trend-change events.

Any quality failure anywhere in the dataset withholds **all** status/comparison
and trend-change events, including earlier otherwise-valid prefixes. Observations
are still visible where structurally possible. No reassuring retrospective
interpretation is inferred from incomplete data. Short valid input passed to the
domain function has insufficient-data status without flags (the HTTP generator
retains its existing minimum of 12 days).

### Strict JSON and reproducibility

Identical inputs produce identical payloads, ordering and IDs. No NaN or Infinity
is emitted. Missing/unusable measurements and unparseable timestamps use JSON
`null`; no imputation is performed. The endpoint uses the same domain rules and
final assessment as the snapshot/report APIs. Existing snapshot and report fields
and CSV acceptance/rejection rules remain unchanged. This addition makes no UI
changes, diagnoses, clinical validation claims or new medical thresholds.

### Regression coverage

`tests/test_timeline.py` checks deterministic serialization, preserved source
frames, per-prefix rule parity, inclusive boundaries in both directions,
insufficient baselines, invalid/missing/nonfinite input, structural failures,
chronology and blocking. `tests/test_api.py` covers all scenarios, parameter
limits, strict JSON, OpenAPI route registration and HTTP/domain parity. Run the
full existing suite with `python -m pytest -q`, including CSV and dashboard tests.
