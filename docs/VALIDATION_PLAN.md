# Software validation — current main v1.5

Tests establish software behavior, not medical accuracy, astronaut outcomes or
NASA acceptance. All mission fixtures are fictional. Research HTTP tests mock
external responses; successful fixtures do not prove live source availability.

## Scope matrix

| Area | Existing checks | Prerequisites / limits |
|---|---|---|
| Synthetic engine | Seed reproducibility, first-seven/last-four windows, inclusive 12 bpm / 1.5 hour boundaries, data integrity and JSON safeguards | Root pytest suite; no clinical calibration |
| Strict synthetic CSV | Accepted six-column attested files; rejected schema, dates, provenance, size and numeric failures | Implemented importer; attestation does not prove authenticity |
| Streamlit fallback | AppTest scenario and review/export controls | Python dependencies; not browser-download evidence |
| FastAPI mission | Scenarios, check-in, CSV, timeline, evidence, status and export contracts | In-process TestClient plus live HTTP checks |
| Copilot / Wellness / audit | Deterministic explanations, quality abstention, canonical values, manual four-state audit and device-clock timestamps | No LLM, clinical authorization or personnel contact |
| React | Component/adapter states, cancellation, quality gating, source isolation, review/export | `npm test`; mocked API fixtures |
| TypeScript / production UI | Type check and compiled distribution | `npm run build` |
| Live Vite/FastAPI | Actual typed adapter through proxy, canonical scenarios, CSV and reports | API **8000** + Vite **5173** before `npm run test:integration` |
| Compiled browser UI | Desktop/mobile workflow, downloads, recovery, Copilot and automated accessibility assertions | Built UI + FastAPI; Playwright default **8014** or explicit `ARES_E2E_ORIGIN` |
| Optional research | Bounded artifacts, beat matching, opt-in and provenance/security gates, mocked OSDR responses | Default pytest; optional WFDB/NeuroKit fixtures run separately via `optional_checks/ecg_integration.py` |

## Commands

From repository root on Linux (Windows uses `.\.venv\Scripts\python.exe`):

```sh
.venv/bin/python -m pip check
.venv/bin/python -m pytest -q
cd frontend
npm test
npm run build
```

Live HTTP suite: start `.venv/bin/python -m uvicorn src.ares_health.api:app --host
127.0.0.1 --port 8000` from root and `npm run dev` from frontend/ in separate
terminals. Wait until `http://127.0.0.1:5173/api/status` reports `ready`, then run
`npm run test:integration` in frontend/. Neither test command starts the servers.

Browser suite: build, then start the compiled app on **8014** and run
`npm run test:browser` in frontend/. Alternatively point it to an existing compiled
app on 8000:

```sh
ARES_E2E_ORIGIN=http://127.0.0.1:8000 npm run test:browser -- e2e/console.spec.ts e2e/copilot.spec.ts
```

The selected two suites write ignored screenshots/results; other suites can
refresh tracked captures. Inspect changes and preserve existing files.
[Frontend instructions](../frontend/README.md) include Windows environment-variable
syntax and browser installation. See [README](../README.md) for fresh setup.

## Evidence and limits

The Issue #26 audit runs on Linux with Python 3.12 / Node 24; results are recorded
in [the audit report](ISSUE26_DELIVERY_AUDIT.md). CI configuration additionally
covers Python 3.13 and offline research tools. Local runs do not establish that
this PR's GitHub Actions jobs passed. The Issue #26 report of PR #25 CI success
is prior evidence, not a new CI run. Historical counts (64 in v0.5; 177/32/8 in
v1.1) describe earlier snapshots and are not current acceptance counts.

The full browser suite, independent Windows fresh install, optional real-library
research suite and official public-record ECG benchmark are separate checks;
record unrun checks as unrun. License/source review and live NASA sample access
remain separate. No fixture run proves sensitivity, specificity, clinical safety,
spaceflight qualification, submission or Global Judging eligibility.
