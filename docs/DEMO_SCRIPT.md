# ARES Health AI — Integrated Space Apps Demonstration Script

**Target duration:** 3–4 minutes, in English.
**Software:** Local FastAPI + React v1.3 mission console, with independent optional
MIT ECG and NASA space-biology research views.
**Data policy:** Mission-mode readings are 100% fictional. Research-mode sources
are public MIT-BIH terrestrial ECG and NASA OSDR OSD-87 mouse research.
**Not:** diagnostic software, NASA endorsement, medical-device approval or
flight-qualified astronaut monitoring.

## Prepare the laptop

1. `git status` clean and project on a verified submission branch/commit.
2. Run `python -m pytest -q` and `cd frontend; npm test; npm run build`.
3. Preferred production presentation: from repo root run `.\\start-ares.ps1` (or
   `.\\start-ares.ps1 -SkipBuild` with a prebuilt `frontend/dist`).
   This serves React and FastAPI together on `http://127.0.0.1:8000/`.
4. Developer fallback: use separate `uvicorn` and `npm run dev` terminals
   only if you specifically need Vite development mode.
5. Open the local production address on port 8000. Do not expose browser personal info,
   notifications, passwords, API keys or terminal accounts.
6. The MIT/NASA tabs require optional research mode. Prepare these separately;
   do **not** rely on NASA network availability for the core demonstration.

## 0:00–0:25 — Mission context

“Human space exploration creates operational and physiological challenges.
Astronauts need understandable ways to review observations, spot data problems,
and know which approved procedures to consult. ARES is an independent,
local-first *research and demonstration prototype* for that workflow.”

## 0:25–0:50 — One integrated tool

“This is the ARES mission console built with React and FastAPI. It provides one
coherent sequence: choose a fictional crew scenario, submit a fictional check-in,
inspect quality-gated charts and timelines, review procedure-oriented
explanations, and export a JSON report. All mission-mode values are synthetic.”

## 0:50–1:20 — Actual check-in and assessment

“Here I select stable fictional observations. I enter a hypothetical latest-day
resting heart rate of 140 bpm, seven hours of sleep and 45 minutes of activity.
I explicitly certify these are *fictional* values. ARES uses the existing Python
engine to recalculate the demonstration-only comparison and explain the change.
These settings are not clinical danger thresholds and cannot diagnose disease.”

## 1:20–1:45 — Verification and missing data

“The underlying 21-day series, exact UTC dates and explainable events are visible.
When I select the incomplete-records scenario instead, ARES blocks trend
interpretation and preserves missing readings as gaps. It never fills in missing
measurements or infers medical clearance.”

## 1:45–2:05 — Local CSV and review report

“We can also import a small fictional CSV with explicit source attestation.
The actual data are validated by Python. Accepted files generate their own
mission timeline and a JSON review report. Invalid uploads are rejected.”

## 2:05–2:35 — NASA risk explorer and review

“We connect the NASA Human Research Program's five spaceflight hazards to
candidate observations, what this prototype can measure and what it cannot.
ARES does not choose treatments or determine medical severity. A real crew
must follow its mission's approved procedures and consult flight medical
professionals.”

## 2:35–3:20 — Research transparency (optional if demonstrable)

“An independent research area measures ECG R-peak detection on MIT-BIH
terrestrial research ECG and compares its output with expert annotations.
A separate NASA OSDR explorer accesses published mouse-retina experiment
metadata from the STS-135 study. These are **different sources and questions**;
neither is live astronaut telemetry or a validation of our fictional mission
alert thresholds.”

Show only source access and benchmark results that are actually available
and verified at presentation time. If NASA network access fails, skip the
file download rather than replacing it with fictional research data.

## 3:20–3:40 — Limitations and close

“ARES offers an integrated, auditable prototype for *reviewing* fictional
astronaut health observations and exploring public biomedical research.
It is not a medical device, a diagnosis tool or a flight-qualified system.
Clinical evaluation, validated sensors, mission-specific procedures and
expert authorization are necessary before real-world use.”

## Submission checklist

- Record and link the *working* React application, not just a Figma mockup.
- Credit NASA/CSA/PhysioNet sources and AI tool assistance.
- Include stable GitHub commit, environment startup instructions, actual
  automated test logs and precise limitations.
- Confirm event instructions, submission fields, team requirements and deadline
  through the official NASA Space Apps Challenge site.
- **Do not** claim the prototype is medically precise on astronauts,
  clinically validated or endorsed by NASA.
