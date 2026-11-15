# ARES Health AI — Local API Contract (application v1.5)

**Purpose:** Expose the shared synthetic Python engine to the current React v1.5 console. FastAPI also serves the compiled UI; Streamlit remains a standalone fallback.

Canonical `application_version` is `1.5` from `version.py`. Existing document
schemas (including `1.0-demo`, `1.0-timeline` and `1.5-demo`) are independent
format identifiers; this documentation correction changes no JSON contract.

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
React v1.5 console + decorative 2D navigation illustration
        |
     Typed functional UI    ← only controlled synthetic files and demo scenarios
        |
  local FastAPI /api/* (application v1.5)
        |
    service.py : canonical snapshot, strict JSON conversion
        |
    Existing domain: synthetic, validation, analysis, evidence, review
```

The Streamlit fallback uses these same domain modules directly. The compiled
React console is the current main presentation; no validated 3D organ model
is implemented. This API does not generate a medical diagnosis, determine astronaut fitness or provide real-time data.

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

## v1.1 React consumer (backend routes unchanged)

`frontend/` consumes scenarios, demo snapshots, timelines, evidence and review
reports with a typed fetch adapter and runtime Zod validation. Vite's loopback
port 5173 proxies `/api/*` to the existing loopback API on port 8000. Requests
for scenario demo/timeline are cancelled together when the source changes; late
responses cannot overwrite the current dataset. React never reimplements rules,
CSV schema validation or statistics. HTTP and contract failures clear stale results.

CSV files are sent as raw bytes after explicit synthetic attestation and a client
byte-size guard. The backend remains responsible for strict acceptance. Accepted
CSV responses use their embedded `review_report` for download; they are never
submitted to `/api/review` as a built-in scenario. Because `/api/timeline` only
supports generated scenarios, CSV timeline display is explicitly unavailable.
The UI clears the prior scenario timeline rather than inventing CSV events.
Review notes and returned reports remain in memory only. No endpoint or existing
Python report schema changes were required. See `frontend/README.md` for startup,
proxy configuration, errors, regression tests and limitations.

## v1.2 optional research namespace (present on main)

Existing synthetic routes and their accepted provenance remain unchanged.
`GET /api/research/ecg/demo?record=100` serves a separately prepared terrestrial
ECG artifact with `data_provenance=public_research_ecg`. It is disabled unless
`ARES_RESEARCH_ENABLED=1`, requires a loopback client, and accepts only literal
record `100`. No URL, file path, duration or upload parameter is exposed.

- HTTP 403: non-loopback client. HTTP 422: unsupported record.
- HTTP 503: disabled, missing/oversized/corrupt/nonfinite artifact; never initiates
  a download, detector or preparation task.
- HTTP 200: `status=benchmarked` with measured results, or `status=abstained` with
  reasons and no scores/waveform. Abstention is not medical clearance.
- Envelope: `schema_version=1.2-research`, record, source/version/citation,
  protocol, processing_versions, quality, annotation_counts, acquisition hashes,
  metrics, waveform, detected_peaks, reference_peaks, matches, discrepancies and
  disclaimer. Undefined metrics are null. All sample indices are original 360 Hz
  positions; display decimation does not affect full-resolution scoring.
- Metrics: TP/FP/FN, precision, recall, F1, mean absolute timing error in ms.
  No medical accuracy, specificity, classification or risk score is supplied.

See `RESEARCH_LAB.md` for the exact heartbeat-symbol list, scoring window,
matching tolerance/tie behavior, engineering quality gates, resource bounds,
provenance/license limitations and opt-in preparation. The public-record run is
currently unverified because PhysioNet is blocked; synthetic fixture metrics are
never represented as the public benchmark. React research loads independently
and cannot populate mission/CSV/timeline state.


## Separate experimental research endpoints — MIT + NASA v1.2

All research routes are **optional, localhost-only, disabled by default** and require
`ARES_RESEARCH_ENABLED=1`. They do not accept real patient uploads or replace the
original `/api/demo`, `/api/timeline`, `/api/synthetic-csv` or medical disclaimers.

- `GET /api/research/ecg/demo?record=100`: separately prepared, rigorously
  checked MIT-BIH record-100 benchmark or an explicit abstention; no remote
  downloading at request time, no unverified numerical performance claims.
- `GET /api/research/nasa/study`: on-demand, approved NASA OSDR **OSD-87**
  public metadata manifest, including only unrestricted and visible files,
  file categories, sizes and official study links. Source provenance:
  `public_space_biology_research`. Organism: *Mus musculus*, retina, STS-135.
- `GET /api/research/nasa/sample-table`: exact original columns and rows from
  the small OSD-87 microarray sample table, fetched **only if** the current
  official NASA catalog confirms that file is visible and unrestricted.

NASA requests are HTTPS-only and bounded: 12 seconds for the catalog, 30 seconds
for the sample. Redirects are limited to two hops and approved NASA/public S3
routes, including the exact OSD-87 GeneLab sample object. They do not permit
arbitrary file names/URLs, inaccessible human datasets, bulk raw omics
data or open access from outside loopback. Connectivity, file changes and
unverified data yield HTTP 503 with no invented results. See
[docs/MIT_NASA_RESEARCH.md](MIT_NASA_RESEARCH.md).


## Integrated mission console — v1.3

The new capabilities remain **local, stateless, fictional and non-clinical**.
All assessment, validation, statistical and trend functions continue to use
the existing Python domain engine, never a React approximation.

- `GET /api/mission/risk-guide` — five NASA Human Research Program hazards,
  candidate research indicators, actual ARES coverage limitations, approved
  procedure-review context and official research link. There are **no hazard
  probability, severity or astronaut medical risk scores**.
- `POST /api/mission/fictional-check-in` — explicitly attested fictional
  last-day measurement override of a deterministic scenario, in memory.
  Request JSON requires `fictional_attestation:true`, allowed scenario ID,
  `seed`, `days`, `resting_hr_bpm`, `sleep_hours`,
  `activity_minutes`, and optional `concerns` from the four hypothetical
  labels `fatigue`, `headache`, `dizziness`, `sleepiness`.
  Refuses extra patient identifiers, duplicate labels, nonfinite values,
  unsupported ranges and missing attestation with HTTP 422.
  Reply includes the canonical snapshot and `review_report` plus
  `mission_timeline`, `check_in` and `decision_support`.
  Concerns only influence a conservative procedure-review explanation;
  no treatment/triage or new numeric medical thresholds are implemented.
- `POST /api/synthetic-csv` — the previous strict raw CSV upload now
  **also includes its dataset-specific `mission_timeline`**, consistent with
  `assessment` and the embedded `review_report`. All existing validation
  and 1MB restrictions stay unchanged.

These additions replace the earlier limitation that imported CSV timelines
were unavailable in the v1.1 client. A compatible v1.3 React client is required
to display the new nested `mission_timeline`.

See [integrated mission demo](INTEGRATED_MISSION_CONSOLE.md).

## v1.5 deterministic mission copilot and comprehensive review

Two stateless offline POST routes extend the existing API without changing its
analysis, CSV, research or legacy report endpoints:

- `/api/mission/copilot`: controlled scenario/check-in or revalidated attested
  synthetic CSV context, bounded question/turn and optional expected context hash.
  Returns a deterministic briefing/answer with canonical assessment, exact
  observation/rule/timeline references, official hazard citations, limitations,
  suggestions and explicit `generative_model=false` identification.
- `/api/mission/comprehensive-report`: recalculates the same context, checks its
  expected hash, replays bounded user audit events and recomputes appropriate
  transcript answers. Adds integrated observations/comparisons, timeline, rules,
  citations, conversation and fictional review log to legacy report fields.

Manual states `PENDING_REVIEW`, `IN_PROGRESS`, `AWAITING_AUTHORIZED_REVIEW`,
`DOCUMENTED` do not change the analysis or authorize medical action. Their exact
state is in `fictional_review`; the legacy two-state field retains compatibility.
No review session is persisted. Source replacement/page reload resets browser
state. No arbitrary client assessment or assistant answer is accepted.

New route bounds: 1,300,000 body bytes, 1 MB CSV, 20 turns, 240-character questions,
64 contiguous audit events and 500-character notes. Finite JSON and explicit
boolean source/review attestations are enforced; errors are sanitized. 409 means
context mismatch, 413 body too large, 415 media type, 422 validation/source failure.
See `COPILOT_V15.md` for exact schemas, input examples, evidence semantics, audit
payloads, state mapping, offline guarantees, abstention and reproducible tests.


### v1.5 comprehensive export compatibility and timestamps (Issue #21)

`POST /api/mission/comprehensive-report` now emits canonical
`review_state` (four values) equal to
`fictional_review.review_state`. It also includes
`legacy_review_state` and `legacy_review_state_semantics` as an explicitly
labeled compatibility-only projection to the old two-state format. The
standalone `POST /api/review` route still uses its original binary values.

New `audit_log[*].recorded_at_utc` is a user-device UTC ISO-8601 string
ending in `Z`, strictly validated and nondecreasing. The field is optional
only for older clients; its absence is indicated by
`fictional_review.audit_timestamps_complete: false`. The timestamp source
is **the browser clock, not a trusted server or flight authority**.

The software version `application_version`,
`copilot_application_version`, `mission_timeline.application_version`
and the FastAPI version are `1.5`; schema identifiers `1.0-demo`,
`1.5-demo`, `1.0-timeline` are maintained independently. See
[release audit details](ISSUE21_RELEASE_AUDIT.md).
