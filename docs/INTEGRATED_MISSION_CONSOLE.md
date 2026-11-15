# ARES Health AI v1.3 — Integrated Mission Demonstration

## What the complete demonstrable workflow does

ARES presents **one coherent local-first mission console** built in React + TypeScript,
backed by FastAPI, existing deterministic Python domain rules and optional,
separately labeled public MIT/NASA research spaces.

```text
Fictional scenario selection or attested fictional check-in or synthetic CSV
                               |
                   Canonical Python validation
                               |
                    Quality-gated trend analysis
                               |
              Observation graph + explainable mission timeline
                               |
                   Procedure-oriented review
                               |
              Exportable mission-review JSON report
                               |
          NASA/CSA science links + interactive NASA hazards
```

The check-in, CSV and built-in scenario **must not generate independent
biomedical assessments in React**. They use the same `build_snapshot()`,
`review_changes()`, `quality_issues()` and `build_timeline()` functions.
All values are fictitious except the two separately labeled read-only
public research sources.

### Functional end-to-end acceptance walkthrough

1. Start two local terminals (backend `127.0.0.1:8000`; Vite `127.0.0.1:5173`).
2. Open ARES mission console. Select *Stable observations*. See 21 days and
   `NO_DEMO_RULE_TRIGGERED`, charts, timeline and review export.
3. Switch to *Resting heart rate shift*. See `CHANGE_FOR_REVIEW`, first-seven
   vs latest-four explanation and an inspectable trend event. **The 12 bpm
   threshold is an engineering illustration, never a medical cutoff.**
4. Select *Incomplete records*. See `DATA_QUALITY_BLOCKED`: absent cells
   remain gaps, **no trend flags or descriptive statistics are inferred**.
5. Return to *Stable observations*. In **Fictional astronaut check-in**, enter
   resting HR 140 bpm, sleep 7 hours, activity 45 minutes, optionally choose
   hypothetical fatigue, and attest all data are fictional. Submit. The result
   should be `CHANGE_FOR_REVIEW`; the updated latest observation, graph,
   mission timeline and embedded review JSON all agree. No real readings are
   accepted or stored. This changes a **single last-day fictional value** and
   does not establish clinical severity.
6. Upload the included **synthetic CSV template** with the explicit fictional
   attestation. The backend validates the actual file and returns charts,
   its **own dataset-specific timeline**, and an embedded JSON report.
7. Select and explore the **five NASA human-spaceflight hazards**; see
   research context, which measurements ARES truly does not cover, the
   appropriate mission-procedure review, and official source links.
8. Open MIT-BIH ECG research and NASA OSDR in separate modes; clearly identify
   terrestrial research ECG and mouse-retina space-biology sample metadata.
   These are not astronaut data and do **not** calibrate mission alert rules.

### Data contract and refusal modes

- All check-in inputs must be **fictional**, must explicitly attest their
  provenance, and must meet existing non-clinical sanity ranges: HR (0,250] bpm,
  sleep [0,24] hours, integer activity [0,1440] minutes.
- Hypothetical concerns are limited to four explicit labels. They only affect
  **procedure-oriented explanatory text**, not the signal algorithm or
  assessment. No real medical details, names, identifiers or individual records.
- The latest sample is replaced **in memory only**; a new request reproduces
  the original seeded mission. No saving, account, remote API, live sensors or
  personal medical record capability is present.
- Dataset quality blocks all trend analysis; never interpret a blocked dataset
  as normal. No diagnoses, risk scores, treatments, dose recommendations,
  emergency severity estimation or NASA operational authorization.
- Both `/api/mission/fictional-check-in` and `/api/synthetic-csv` return
  their own `mission_timeline` alongside `review_report`.
- Frontend request cancellation, strict JSON validation, and existing
  raw CSV limits remain enforced.

### Current limitations and truthfulness

This is a **complete hackathon software demonstration workflow**, not a
medically complete autonomous astronaut healthcare system. It has neither
validated aerospace medical thresholds, clinically tested therapeutic guidance,
real-time wearable sensors, body camera input, diagnosis, a clinical emergency
workflow, flight surgeons linked to live systems, nor NASA endorsement.
An anatomical 3D interface designed in Figma can be integrated later without
rewriting the API, but is **not represented as already implemented**.

The original Streamlit and MIT/NASA research sections remain as fallbacks and
independent research evidence. Public terrestrial MIT-BIH beat-matching metrics
and NASA OSD-87 mouse specimen metadata must never be combined into a single
human medical accuracy number.

## One-server hackathon mode

This is the **recommended presentation mode**, requiring only one PowerShell
terminal and one browser address after dependencies are installed:

```powershell
.\\start-ares.ps1
```

The launcher uses `npm.cmd` to build the React production assets, then
starts the local FastAPI process on `127.0.0.1:8000`. Both the user
interface and backend API are accessible at the same origin,
`http://127.0.0.1:8000/`. The synthetic CSV template is served there,
too. Research modules remain opt-in and unhosted publicly.

For offline presentation with a previously generated `frontend/dist`:

```powershell
.\\start-ares.ps1 -SkipBuild
```

The source code and dependencies must already be present. The build output
is not a separate executable and does **not** include live astronaut sensors
or a hosted medical service.

## Start on Windows

```powershell
# Backend terminal, from repo root:
python -m pip install -r requirements.txt
python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000

# Separate frontend terminal, from repo root:
cd frontend
npm ci
npm run dev
```

The optional MIT/NASA research endpoints require a separate, explicit
`ARES_RESEARCH_ENABLED=1` and source-dependent local preparation; the complete
synthetic mission console does not require the public network.

## Test verification

```powershell
python -m pytest -q
cd frontend
npm test
npm run build
npm run test:integration
```

CI must run on Python 3.12 and 3.13, test React, type-check, compile production
assets and exercise the real Vite proxy + FastAPI workflow before merging.
Software test success demonstrates behavior, **not medical efficacy**.
