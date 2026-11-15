> Historical README preserved from aadd798 (before Issue #26). Version, branch,
> timing and verification statements below describe earlier milestones; they
> are not current delivery status. Use [current README](../../README.md).

# ARES Health AI — NASA Space Apps Challenge 2026

**Astronaut Risk Evaluation System**
**Track:** Create Health Monitoring Software for Astronauts on Space Missions
**Event:** Universal Event · November 14–15, 2026
**Stage:** Integrated v1.3 hackathon demonstration console (feature branch), plus read-only optional MIT/NASA research views, stable Streamlit fallback. **Not medically or spaceflight validated.**

## Integrated mission workflow — v1.3

**ARES now provides an end-to-end fictional mission interaction:** choose a
scenario, enter an explicitly fictional last-day check-in or import a strict
synthetic CSV, process it through the same guarded Python engine, inspect the
measurements/charts, read its dataset-specific mission timeline and procedural
explanation, explore NASA's five human-spaceflight hazards, and export a
reproducible JSON review report.

React now has a cohesive dark mission-console interface and mode navigation
between **Mission**, **MIT-BIH ECG research** and **NASA space-biology research**.
The latter are separate, real public research sources, **never joined into a
fictional crew history or used as validated astronaut-health thresholds**.

See [complete mission demonstration and walkthrough](../../docs/INTEGRATED_MISSION_CONSOLE.md).

### Single-command Windows demonstration (React + FastAPI)

Instead of starting two separate servers, run from repository root:

```powershell
.\\start-ares.ps1
# Or double-click start-ares.cmd on Windows
```

The launcher builds the production React interface if dependencies are
available, then serves both the React application and all local API routes
at **http://127.0.0.1:8000/**. The synthetic sample CSV is available at
the same address. Node.js 22.12+ and installed Python project dependencies
are prerequisites. Use `.\\start-ares.ps1 -SkipBuild` when a matching
`frontend/dist` has already been compiled and you are demonstrating
offline. Do **not** deploy this unauthenticated demo to the public Internet.
No real medical record intake, clinical treatment guidance, 3D anatomical
Figma asset or NASA approval is claimed.

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
**do not host it publicly**. See [API contract](../../docs/API_CONTRACT.md) and
[architecture](../../docs/ARCHITECTURE.md).

## Mission Timeline & Explainability (v1.0 backend)

`GET /api/timeline` adds a deterministic history of fictional observations,
dataset quality findings and explained daily trend comparisons. Query parameters
match `/api/demo` (`scenario`, `seed`, `days`). Existing validation and the
illustrative 12 bpm / 1.5 hour rules are reused; any quality failure suppresses
all trend interpretations. Events do not estimate clinical onset or diagnose
health conditions. The Streamlit interface and CSV/report workflows are unchanged.
See [timeline API contract](../../docs/API_CONTRACT.md#mission-timeline--explainability--v10)
for event fields, ordering, blocking and reproducibility guarantees.

## Functional React integration (v1.1)

A standalone `frontend/` Vite + React + TypeScript client now consumes the local
FastAPI API for scenarios, three physiological charts, quality gating, timeline
filters, strict synthetic CSV import, review JSON export and NASA/CSA references.
All values and biomedical calculations remain in Python. No final Figma styling,
anatomical model or 3D interface is included; Streamlit remains available unchanged.

Start the loopback backend as above, then run `cd frontend`, `npm install`, and
`npm run dev` in a second terminal. Vite uses port 5173 and proxies `/api` to
127.0.0.1:8000. See [frontend startup and functional walkthrough](../../frontend/README.md)
for exact PowerShell steps, test commands, configuration and limitations.

## Research integrations — MIT + NASA (experimental v1.2 branch)

Two **independent, optional** research views are now prepared:

- **MIT-BIH ECG Lab:** WFDB/NeuroKit beat-detection benchmark against expert-reviewed
  terrestrial ECG annotations. The official record-100 acquisition remains
  blocked by HTTP 403 in Codex's environment; **no public-record performance
  metric is claimed**.
- **NASA OSDR Research:** public study OSD-87, a mouse retina spaceflight study
  from STS-135. NASA's file catalog and a small public sample CSV are loaded
  on demand with strict limits. **This is not astronaut health monitoring**.

The synthetic mission app remains separate from public research datasets. See
[MIT + NASA research documentation](../../docs/MIT_NASA_RESEARCH.md) and
[MIT benchmark protocol](../../docs/RESEARCH_LAB.md). The entire feature remains
in its own research mode; source validation and local verification remain separately documented.

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

## Optional Biomedical Research Lab (v1.2 draft, future work)

An isolated opt-in research view and offline WFDB/NeuroKit pipeline benchmark
heartbeat detection for an allowlisted public terrestrial ECG case, separately
from synthetic mission data. No diagnosis, classification, HRV inference or risk
scoring is added. Existing mission/CSV/timeline routes and Streamlit remain the
submission fallback. **The official PhysioNet run and source/license review are
blocked by network access and are not claimed complete.** See
[research protocol, provenance and preparation](../../docs/RESEARCH_LAB.md) for exact
bounds, abstention behavior, citations, optional tooling and draft scope gate.

## v1.4 mission-control redesign (draft against PR #12)

The React console now has a compact three-column desktop layout: API telemetry,
interactive original anatomical illustration, and dated signal analysis. Check-in,
CSV, timeline, reports, NASA risks and sources live in a contextual tabbed workspace.
MIT-BIH and NASA OSDR remain separate research modes. All Python functionality and
source provenance are preserved. No new medical logic is implemented in React.

After checkout, run `cd frontend`, `npm ci`, `cd ..`, then `start-ares.cmd` on Windows.
The one-server app remains on 127.0.0.1:8000. See [design, asset provenance, tests and
real browser captures](../../docs/CONSOLE_V14.md). The anatomical art is an original
AI-generated navigation illustration, not a clinically certified anatomy model.

## v1.5 offline interactive mission copilot

The existing console now includes **ARES Copilot**, a deterministic Python-grounded
assistant (not an LLM). It briefs the active fictional mission, answers bounded
review questions with observation/rule/timeline evidence and NASA source links,
and refuses medical treatment/clearance or quality overrides. No external model,
secret or network service is required for the core workflow.

**Review & Export** records manual actions, fictional notes and four review states:
PENDING_REVIEW, IN_PROGRESS, AWAITING_AUTHORIZED_REVIEW and DOCUMENTED. These never
alter analysis or grant medical authorization. One integrated JSON export contains
canonical measurements, comparisons, timeline, rules, citations, appropriate
conversation and the user-recorded audit log. Everything stays in browser memory
until explicit export; new missions/page reload reset it. The v1.4 anatomy and
existing mission/research modules remain intact. See [v1.5 workflow, API, limits
and screenshots](../../docs/COPILOT_V15.md). Startup remains `start-ares.cmd` after the
existing Python setup and `cd frontend; npm ci; npm run build` steps.

### Copilot reading improvements (Issue #17)

**Focus / expand conversation** opens the same conversation in a keyboard-accessible
reading dialog; Escape restores the dock and vitals. Replies start at the new
question and answer, with readable text and one conversation scroll surface.
**View evidence** reveals Python-provided comparisons and actual UTC windows before
optional original observation IDs, rules and scientific source links. Blocked data
never display comparison averages. The deterministic backend, synthetic-data
restrictions, manual review audit and comprehensive JSON export are unchanged.
See [behavior, real before/after screenshots and verification](../../docs/COPILOT_READING.md).

### Cockpit balance correction (Issue #19)

Opening Copilot now preserves full-height telemetry, sparklines, anatomy and the
main chart. The docked conversation continues below the cockpit using page scroll;
it no longer takes height away from the mission panels. **Full cockpit** collapses
the workspace and returns to telemetry without discarding the conversation or
draft. Focus reading, evidence and keyboard navigation remain available. This
intentionally permits vertical page scrolling on short desktop windows. See
[layout tradeoffs, four-viewport browser captures and verification](../../docs/COCKPIT_BALANCE.md).


### Comprehensive report integrity — Issue #21

The v1.5 comprehensive report now has **one canonical four-state review status**,
consistent at the root and in `fictional_review`. The original binary status is
clearly labeled `legacy_review_state` for compatibility; the separate old
review endpoint remains unchanged. New fictitious actions include **UTC timestamps
from the user's browser** (not independently verified); older clients may
omit the timestamp and the report will disclose this gap. All report, timeline,
API and copilot application-version fields now come from the same Python
`APP_VERSION` constant. Document schemas retain their independent versions.

See [audit consistency and demonstration steps](../../docs/ISSUE21_RELEASE_AUDIT.md).


### ARES Mission Wellness & Procedures (candidate feature)

Within the existing **ARES Copilot** panel, an expandable guide now presents
three educational spaceflight research topics: cardiovascular observation,
sleep/circadian schedules, and movement/exercise. Each topic links an official
NASA Human Research Program reference, explains an observation to review,
provides a fictional routine example, and states its evidence limits.
The guide is recalculated by the Python backend for the **active synthetic
mission**, and refuses trend interpretation when data quality blocks it.

A **Document a fictional review** button opens the **existing** user-controlled
review/audit workflow; it never performs a real medical action or starts a
scheduled reminder. This is not a treatment engine or an LLM.

See [Mission Wellness & Procedures](../../docs/MISSION_WELLNESS.md) for scientific
links, acceptance tests, provenance and limitations.
