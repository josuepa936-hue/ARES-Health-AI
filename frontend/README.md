# ARES Health AI v1.3 — integrated mission console

This standalone Vite + React + TypeScript client consumes the existing FastAPI
v1.0 API. Python remains the only source of physiological values, validation,
trend rules, statistics, assessments, guidance and reports. The integrated high-contrast operations console is a usable demonstration
interface, **not the final Figma anatomical or 3D design**.
There is no anatomical model, 3D, authentication, database or external telemetry.

## Single-server production demonstration

From the repository root, **after installing Python requirements**, run:

```powershell
.\\start-ares.ps1
```

The launcher compiles React and serves the UI, `/api/*`, static assets
and the fictional CSV template from FastAPI on **127.0.0.1:8000**.
Open http://127.0.0.1:8000/ in one browser window. The two-terminal
Vite workflow below remains available for developers; it is **not** required
for the presentation. Do not expose the unauthenticated service publicly.

## Start on Windows (PowerShell)

Install Node.js 24 LTS (verified; minimum 22.12) and Python 3.12+. From the
repository root, open two separate PowerShell terminals.

Terminal 1 — backend:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

Terminal 2 — frontend, starting from the repository root:

```powershell
cd frontend
npm install
npm run dev
```

Open the locally reported Vite address on port **5173** in your browser.
Vite binds to **127.0.0.1**, requires port 5173 (no silent fallback), and proxies
`/api/*` to **http://127.0.0.1:8000**. Run both services independently; starting
React does not start Python. Keep the unauthenticated API on loopback. Existing
Streamlit still runs independently with `python -m streamlit run app.py`.

Linux/macOS equivalents: `python3 -m venv .venv`, `.venv/bin/python -m pip install
-r requirements.txt`, `.venv/bin/python -m uvicorn src.ares_health.api:app --host
127.0.0.1 --port 8000`; then `cd frontend`, `npm install`, `npm run dev` in another
terminal. Use `npm ci` for a reproducible install from the committed lockfile.

### Optional direct local API URL

By default the adapter uses same-origin `/api` and the Vite proxy. For a direct
local API connection, create `frontend/.env.local` containing:

```text
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Restart Vite after changing it. The base URL must exclude `/api`; requests append
that prefix. Only use a trusted **local** endpoint. Existing backend CORS permits
localhost/127.0.0.1 browser origins on ports 5173 and 3000. `npm run build` checks
TypeScript and creates static files; it does not package or start FastAPI. The
development proxy belongs to Vite dev mode, not an arbitrary static web host.
Do not publish this unauthenticated fictional-data demo as a medical service.

## Integrated v1.3 workflow

The default mission tab now includes the **Fictional astronaut check-in**
to replace only the most recent fictional day, followed by the actual Python
assessment, matching timeline, procedure-oriented explanations and embedded
review JSON. It accepts **only** explicitly attested fictional data.
The **Five hazards of human spaceflight** navigator gives source-linked NASA
context, measurement coverage and limitations without inventing hazard scores.
MIT ECG and NASA space biology remain separate, opt-in research modes.

See [complete end-to-end demonstration](../docs/INTEGRATED_MISSION_CONSOLE.md).

## Functional walkthrough

1. The permanent synthetic-only disclosure stays visible. Scenarios and NASA/CSA
   reference links are fetched from the API. Select any of the four scenarios;
   requests use seed 2026 and 21 days. Older requests and review exports are
   cancelled/invalidated when switching sources. No fallback readings are made up.
2. Mission overview shows API metadata, assessment, guidance and explainable
   findings. Three separate charts display raw values with units and UTC dates;
   the expandable table gives accessible exact observations. Missing values
   break lines instead of being filled. Chart scaling is presentation only.
3. Incomplete records show quality errors, missing cells and no trend findings or
   advanced statistics. No frontend calculation reconstructs blocked values or
   infers health status. API descriptive statistics are optional details on
   available analyses only.
4. Mission timeline renders API IDs/explanations and lets you filter the four
   event types. Repeated trends are overlapping comparisons, not estimated onset
   of a medical event. No extra alerts are calculated in React.
5. Download the local fictional CSV template, explicitly attest fictional-only
   content, and upload. Raw bytes are sent as `text/csv` with the required
   attestation header; files over **1,000,000 bytes** are blocked before sending.
   Python performs all schema/provenance/measurement validation and its rejection
   messages are displayed. Never upload real health information.
6. CSV analysis replaces the built-in dataset and includes its own backend
   `mission_timeline` plus embedded review report. Both are derived from the
   uploaded, strictly validated synthetic rows. It never submits CSV as a built-in scenario.
   To return to a built-in scenario, choose one or reload the selected scenario.
7. For built-in scenarios, submit the allowed review state and an optional
   fictional note (max 500 characters) to `/api/review`, then download the returned
   JSON. Editing review inputs invalidates the export until resubmission.
8. Scientific links, summaries and limitations come from `/api/evidence`.
   These are research context, not NASA telemetry or clinical validation.

All application state stays in memory. There is no localStorage, analytics,
external data fetch, service worker or automatic data persistence. A selected
local file and notes are sent only on explicit upload/review submission. Downloads
are user initiated. Reloading the page discards active data and starts a demo.

## Tests and build

From `frontend/`:

```powershell
npm test
npm run build
```

With both local services running as above:

```powershell
npm run test:integration
```

The unit/component suite uses backend-generated fictional JSON fixtures, not a
second signal generator. Tests cover scenario changes, quality gating, timeline
filters, loading/empty/error states, cancellation/stale-response protection, CSV
attestation/size/errors, and returned JSON downloads. Real HTTP tests exercise
the typed adapter through Vite to FastAPI, all four scenarios, CSV acceptance and
rejection, official evidence links and scenario reviews. These checks complement
component rendering tests; they are not a full browser visual/keyboard audit.
GitHub Actions runs both suites, the build, and the unchanged Python suite.

From the repository root, preserve the backend regression check:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

To refresh fixtures/template after an intentional backend contract change, run
`python -m frontend.scripts.export_test_fixtures` from the repository root with
backend dependencies installed. The template is produced by the Python stable
scenario generator (seed 2026, 21 days). Review fixture diffs rather than using
fixture refreshes to hide unexpected behavior. Run `npm run format` for formatting.

## Error behavior and limits

Malformed success payloads fail runtime schema validation and display an error.
Connection errors, non-JSON responses, structured FastAPI/CSV errors, and empty
results have distinct messages. No old mission/report remains visible after a
failed replacement request. Failed scientific references can be retried separately
from mission data. Cancellation ignores late responses even if a transport does
not honor abort immediately. No medical thresholds or new statistics are defined
in this project; all clinical interpretations are outside scope.

### Verified implementation results

Local verification on Node 24 / Python 3.12: **177 Python tests**, **32 frontend
unit/component tests**, and **8 live HTTP integration tests** passed. The
TypeScript/production build passed. Python emits one existing Starlette/httpx
deprecation warning. CI configuration is included; these results describe local
runs, not a completed GitHub Actions run. Final visual design and full browser
visual testing remain outside this integration milestone.

## Optional v1.2 research tab (future research)

The default mission app and its state remain unchanged. **Optional research lab**
lazily loads a separate view labelled PUBLIC TERRESTRIAL RESEARCH ECG. It reads
only `/api/research/ecg/demo?record=100`; it never uploads or generates ECG data.
The backend must be explicitly enabled and have a prepared artifact. Disabled,
unavailable and abstained results show no scores. The view displays backend
metrics, source/citation, versions, raw display waveform, exact peak/reference
markers and a discrepancy table. It does no beat detection or scoring in React.

See `docs/RESEARCH_LAB.md` from the repository root for separate optional install,
official-file acquisition, license review, quality protocol and enablement. The
public-case benchmark is currently blocked, so this work stays future research;
the synthetic mission app remains the hackathon fallback. No final Figma/anatomy/
3D design is part of this view.


## Experimental NASA OSDR view (research branch only)

The third workspace mode, **NASA space biology**, provides a separate
on-demand read-only explorer of the public OSD-87 (STS-135 mouse retina)
NASA study catalog and the explicitly authorized small sample table.
Research needs `$env:ARES_RESEARCH_ENABLED="1"` in the backend terminal.
The backend may return HTTP 503 when NASA cannot be contacted; no
data are invented. No astronauts' medical data are acquired.

The MIT ECG lab remains a distinct opt-in view; it does not merge MIT
observations with spaceflight mouse study data. This is **not** the Figma
interface redesign. See [study sources and caveats](../docs/MIT_NASA_RESEARCH.md).
