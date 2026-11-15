# ARES Health AI — v1.5

Astronaut Risk Evaluation System: a local FastAPI + React demonstration console
for reviewing **fictional** daily observations, quality-gated trends, timelines,
and reproducible JSON reports. The deterministic offline Copilot and Mission
Wellness guide explain existing results and NASA research context; the runtime
Copilot is **not an LLM**. Streamlit remains a standalone fallback.

This is not a medical device, clinical validation, flight-qualified monitoring or
NASA endorsement. No real medical records, astronaut telemetry or sensor feeds
are accepted. Mission dates are simulated and can be later than the presentation
date. Heart rate (bpm), sleep (hours) and activity (minutes) are fictional values;
the 12 bpm / 1.5 hour comparison settings are engineering examples, not clinical
limits. Activity has no change rule.

## Install and run from a fresh clone

Requires Python 3.12+ and Node >=22.12 (Node 24 used in local verification),
Git and Internet access to Python/npm package registries during installation.
No API keys, database or external service are needed for the mission console.
Python requirements use ranges; only frontend dependencies have a lockfile.

Windows, from PowerShell:

```powershell
git clone https://github.com/josuepa936-hue/ARES-Health-AI.git
cd ARES-Health-AI
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
cd frontend
npm ci
cd ..
.\start-ares.cmd
```

The launcher builds React and serves UI, API and synthetic CSV together at
`http://127.0.0.1:8000/`. Keep the terminal open; Ctrl+C stops it.
`.\start-ares.ps1` is the PowerShell alternative. If script execution is blocked,
use `.\start-ares.cmd`; no execution-policy change is required. With an existing
matching build, use `.\start-ares.cmd --skip-build` or
`.\start-ares.ps1 -SkipBuild`. These launchers do not install Python dependencies.

Linux / cloud:

```sh
git clone https://github.com/josuepa936-hue/ARES-Health-AI.git
cd ARES-Health-AI
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cd frontend
npm ci
npm run build
cd ..
.venv/bin/python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

In an existing cloud checkout, skip cloning and use that isolated checkout.
Keep this unauthenticated service on loopback; a public demonstration video or
slide link is separate from hosting this API. Local checks: `/api/status` returns
`ready`, `/` renders the compiled UI, and `/synthetic-template.csv` downloads the
fictional template. If `/` returns 503, build frontend/dist and restart FastAPI.

## Development and verification

Run `.venv/bin/python -m pytest -q` from the root (Windows:
`.\.venv\Scripts\python.exe -m pytest -q`). In `frontend/`, run `npm test` and
`npm run build`. See [validation matrix](docs/VALIDATION_PLAN.md) and
[frontend instructions](frontend/README.md) for HTTP/browser prerequisites:

| Workflow | Required processes / port |
|---|---|
| Compiled console | FastAPI on 8000 after frontend build |
| React development | FastAPI 8000 plus `npm run dev` in frontend on 5173 |
| `npm run test:integration` | Both FastAPI 8000 and Vite 5173 |
| `npm run test:browser` | Compiled FastAPI on 8014 by default, or set `ARES_E2E_ORIGIN` to the running compiled app |

Streamlit fallback: `.venv/bin/python -m streamlit run app.py` from the root.
The console includes a decorative generated **2D anatomical illustration** with
interactive navigation overlays, not a validated organ model or 3D anatomy.
Canonical application version is `APP_VERSION = "1.5"` in
`src/ares_health/version.py`. The private frontend tooling package still has
version `1.1.0`; JSON schema versions are independently versioned identifiers.

## Sources and optional research

Mission observations are generated or imported as strict, attested synthetic
CSV. NASA/CSA literature provides background, not validated alert thresholds.
Separate opt-in research views read MIT-BIH **terrestrial ECG** artifacts and
NASA OSDR **OSD-87 mouse retina** metadata/sample tables. They never become
astronaut observations. Research access, dataset terms and real-record benchmark
results require separate verification; core operation does not depend on them.

- [Scientific evidence and limits](docs/SCIENTIFIC_EVIDENCE.md)
- [Dataset provenance](docs/DATA_SOURCES.md) and [research setup](docs/MIT_NASA_RESEARCH.md)
- [Architecture](docs/ARCHITECTURE.md), [API contract](docs/API_CONTRACT.md)
- [AI and artwork disclosure](docs/AI_USAGE.md)

## Delivery preparation

Use the [official short demo script](docs/DEMO_SCRIPT.md), with the
[expanded walkthrough](docs/DEMO_WALKTHROUGH.md) only as supplemental material.
[Submission checklist](docs/SUBMISSION_CHECKLIST.md) and
[Issue #26 delivery audit](docs/ISSUE26_DELIVERY_AUDIT.md) track human actions:
public final-project and separate demo links, credits/license decisions, team
eligibility, event timezone and Project Tab confirmation. Submission is **not
verified**; a merged PR is not a NASA Space Apps submission.

No root LICENSE is present. No MIT/Apache license or third-party asset permission
is implied. The owner requested licensing in a separate task and must confirm applicable credits/terms.

The [pre-audit README](docs/history/README_PRE_ISSUE26.md) preserves historical
milestones and then-current claims; use the instructions above for current main.
