# ARES Health AI — Local API Contract (v0.9-dev)

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
  local FastAPI /api/* (v0.9-dev)
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
