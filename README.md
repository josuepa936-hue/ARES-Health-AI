# ARES Health AI — NASA Space Apps Challenge 2026

**Astronaut Risk Evaluation System**  
**Track:** Create Health Monitoring Software for Astronauts on Space Missions  
**Event:** Universal Event · November 14–15, 2026  
**Stage:** Functional React integration v1.1 with the stable Streamlit v0.7 fallback and v1.0 API — scientific evidence, plain-language guidance, synthetic CSV import, monitoring and review reporting, **not** clinically validated.

## Local API foundation

The current **Streamlit v0.7** interface remains the reliable standalone demo.
`src/ares_health/service.py` provides canonical strict-JSON snapshots, and
`src/ares_health/api.py` exposes local FastAPI endpoints used by the functional
React client. The future approved Figma visual design remains separate. The backend also
includes **SciPy descriptive statistics** (median, robust MAD and Theil–Sen
slope) for valid fictional records only. This is not medical risk scoring. **The new visual
design is not integrated yet.**

```powershell
python -m pip install -r requirements.txt
python -m pytest -q
python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` to inspect and test API endpoints in your browser.
The API only accepts synthetic data, limits CSV uploads and has no authentication;
**do not host it publicly**. See [API contract](docs/API_CONTRACT.md) and
[architecture](docs/ARCHITECTURE.md).

## Mission Timeline & Explainability (v1.0 backend)

`GET /api/timeline` adds a deterministic history of fictional observations,
dataset quality findings and explained daily trend comparisons. Query parameters
match `/api/demo` (`scenario`, `seed`, `days`). Existing validation and the
illustrative 12 bpm / 1.5 hour rules are reused; any quality failure suppresses
all trend interpretations. Events do not estimate clinical onset or diagnose
health conditions. The Streamlit interface and CSV/report workflows are unchanged.
See [timeline API contract](docs/API_CONTRACT.md#mission-timeline--explainability--v10)
for event fields, ordering, blocking and reproducibility guarantees.

## Functional React integration (v1.1)

A standalone `frontend/` Vite + React + TypeScript client now consumes the local
FastAPI API for scenarios, three physiological charts, quality gating, timeline
filters, strict synthetic CSV import, review JSON export and NASA/CSA references.
All values and biomedical calculations remain in Python. No final Figma styling,
anatomical model or 3D interface is included; Streamlit remains available unchanged.

Start the loopback backend as above, then run `cd frontend`, `npm install`, and
`npm run dev` in a second terminal. Vite uses port 5173 and proxies `/api` to
127.0.0.1:8000. See [frontend startup and functional walkthrough](frontend/README.md)
for exact PowerShell steps, test commands, configuration and limitations.

## Mission

Design a local-first, explainable astronaut health-monitoring prototype that supports the collection of wellness indicators, visualizes time trends, checks data quality, and helps crew members review meaningful changes and consult relevant procedures. It does **not** diagnose disease or replace flight surgeons, medical protocols, or mission operations.

The challenge asks for software that gathers health indicators and enables astronauts to evaluate and act on their health status. Our scope prioritizes **clarity, auditability, and operational resilience** over unvalidated predictive claims.

## What is in this repository?

- `docs/PROJECT_CHARTER.md` — problem, target user, scope, success criteria.
- `docs/ARCHITECTURE.md` — planned software components and boundaries.
- `docs/DATA_DICTIONARY.csv` — proposed data fields and units.
- `docs/DATA_SOURCES.md` — NASA resources and provenance policy.
- `docs/VALIDATION_PLAN.md` — reproducible synthetic scenarios and tests.
- `docs/PROJECT_BACKLOG.md` — prioritized work for hackathon weekend.
- `docs/RESEARCH_LOG.md` — evidence table to fill in.
- `docs/SUBMISSION_CHECKLIST.md` — project-page and delivery checklist.
- `docs/TEAM_BRIEF.md` — roles and collaboration conventions.
- `app.py` — running Streamlit prototype with a mission-status overview, synthetic physiological trends (heart rate, sleep and activity), quality alerts, data provenance and a mission review center.
- `src/ares_health/synthetic.py` — deterministic sample scenarios with fictional profiles.
- `src/ares_health/analysis.py` — non-clinical data quality checks and transparent change rules.
- `src/ares_health/import_csv.py` — local synthetic-only CSV import with strict validation and explicit user attestation in the app.
- `docs/CSV_IMPORT.md` — accepted CSV contract and how to test accepted/rejected uploads.
- `src/ares_health/review.py` — exportable JSON review report with explicit provenance and limitations.
- `tests/` — unit tests for simulation, trend flags, and review report behavior.
- `docs/AI_USAGE.md` — AI assistance disclosure to expand before submission.
- `src/ares_health/evidence.py` — curated NASA/CSA references and non-clinical review explanations.
- `docs/SCIENTIFIC_EVIDENCE.md` — claims, research context and limitations with official source URLs.
- `docs/DEMO_SCRIPT.md` — 2–3-minute English demonstration narration.

## Get started (Windows / PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py`.

## Implemented through v0.6

Shared validation blocks trend interpretation for missing or invalid measurements, invalid or duplicate UTC timestamps, out-of-order records, gaps in daily sampling, invalid schema, blank/mixed profiles and unsupported provenance. Measurements must be finite numeric values (numeric strings accepted, booleans rejected) within illustrative input sanity bounds; see `docs/ARCHITECTURE.md`.

Trend rules require at least 11 consecutive daily observations: the first 7 form the reference and the last 4 form the comparison. Longer series omit intervening days from these means. Absolute changes **at or above 12 bpm or 1.5 hours** trigger review flags in either direction. Explanations include means, direction, units and UTC intervals. These thresholds are unchanged engineering demonstration settings.

Quality failures block interpretation; short valid series report insufficient data. JSON export revalidates records and recomputes flags so stale caller flags cannot produce a misleading report. Charts, Mission Review Center, CSV and JSON downloads remain available. **v0.6 adds strict local synthetic CSV import** (UTF-8; six required columns; fictional SIM- identifier; explicit UTC; one-day spacing; max 1 MB/366 rows), a downloadable synthetic example, safe rejection of invalid files, and a separate selection from the built-in demo scenarios. Real telemetry, database persistence and clinical prediction are not implemented. See `docs/CSV_IMPORT.md`.

## Linux / cloud development

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m pytest -q
.venv/bin/python -m streamlit run app.py --server.headless=true --browser.gatherUsageStats=false
```

Python 3.12 is verified. Dependencies use version ranges rather than a lockfile. No API credentials or external services are required. Tests cover quality failures, inclusive rule boundaries, report safeguards and all four dashboard scenarios. See `docs/VALIDATION_PLAN.md` for scope and limits.

## New in v0.7

The Streamlit dashboard includes **What should I review?** guidance for four mutually exclusive states: data quality blocked, insufficient data, simulated change for review, and no demo rule triggered. A **NASA / CSA research** tab lists official research links for the three illustrative indicators and selected spaceflight hazards. This is an educational context layer, not NASA health data or a medically validated decision system. All instructions emphasize verifying data and consulting authorized procedures rather than advising treatment.

The new tests are in `tests/test_evidence.py`. Run the complete suite locally before merging this branch or publishing the final version.

## Key decisions

1. Use **synthetic test data**, clearly marked as synthetic, until a reviewed public dataset is selected.
2. Start with data-validation and transparent change rules; advanced ML is optional and requires separately justified validation.
3. Operate locally on a laptop without a mandatory cloud service; Streamlit is for the demonstration, not a flight-certified interface.
4. Maintain documentation and final submission materials in **English**, with Spanish as the working language when appropriate.
5. Do not confuse a successful synthetic test with clinical validation or spaceflight qualification.

## Verify prototype

```powershell
python -m pytest -q
python -m streamlit run app.py
```

Try **Stable observations**, **Resting heart rate shift**, **Shortened sleep**, and **Incomplete records**. For CSV ingestion, select **Upload synthetic CSV** in the sidebar, download the synthetic template, upload it and attest that no real health records are included. Open **Mission review center** to export a JSON record of the simulated review. This is a software demonstration, not validation of medical efficacy.

## Hackathon timing

NASA Space Apps 2026 project-submission window is listed as **November 14, 9:00 AM to November 15, 11:59 PM local time**. Historical Space Apps guidance asks teams to begin building their actual solutions when the hackathon starts. The initial planning scaffold was created before the event; subsequent functional prototype code was developed during the hackathon. Confirm the organizer instructions and deadline before submission.

## Roles & contact

The team owns its decisions and must confirm contributor permission before adding identifiable names or outside content. NASA Space Apps participation **does not imply NASA affiliation, endorsement, or medical validation**.

## Sources

- Challenge: https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/
- Event schedule: https://www.spaceappschallenge.org/2026/
- NASA Human Research Roadmap: https://humanresearchroadmap.nasa.gov/risks/
- NASA OSDR: https://science.nasa.gov/biological-physical/data/osdr/
