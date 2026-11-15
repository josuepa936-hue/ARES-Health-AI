# ARES Mission Wellness & Procedures — Educational module

This module is part of the **same** local React/FastAPI mission console, under
**ARES Copilot**. It is *not* an LLM, medical device, treatment recommender,
scheduled alarm, or NASA operational implementation.

## User journey

1. Load one of the four synthetic mission scenarios or perform a fictional
   check-in / attested synthetic CSV import.
2. Open **ARES Copilot → Mission Wellness & Procedures**.
3. Read the canonical Python assessment, and three educational topics
   (cardiovascular, sleep and scheduling, movement/exercise).
4. For each topic, review the source-limited research background, one simple
   fictional measurement/context check, an illustrative routine entry, an
   explicit limitation, and the official NASA scientific reference.
5. Optionally choose **Document a fictional review**, which opens the
   **existing** four-state review and JSON audit export workflow. No checkbox
   is marked and no person is contacted by the guide.

The UI is a collapsed disclosure by default to preserve the cockpit, human
anatomy and charts. It uses accessible normal text sizes and a responsive
one-column layout on narrower viewports.

## Endpoints and contracts

`POST /api/mission/wellness`: body is strictly typed with
`context: {kind:'scenario',scenario,seed,days,check_in?}` or attested synthetic
CSV; optional `expected_context_ref` from the active copilot briefing.
Returns `context_ref`, `assessment`, `summary`, exactly three
`topics`, synthetic provenance, `demo_only: true`,
`clinical_decision_support: false`, `automated_reminders: false`, and a
limits disclaimer. All values are recreated by the canonical domain engine.
Stale context produces HTTP 409; unsupported fields, non-attested uploads and
invalid data are rejected.

The topic `comparison` field is either `available` or `withheld`. It only
describes the availability of the **illustrative** comparison, not a clinical
status. For `DATA_QUALITY_BLOCKED` or `INSUFFICIENT_DATA`, every topic has
`comparison: withheld` and `illustrative_flag: false`. No means or fabricated
normative ranges are supplied by this module. Existing Python rules, review
reports and standalone datasets are unchanged.

## Research anchors

- Sleep, circadian schedule and planned rest: NASA Human Research Program,
  [Risk from Inadequate Sleep and Irregular Schedules](https://www.nasa.gov/reference/risk-from-inadequate-sleep-and-irregular-schedules/)
- Exercise in microgravity: NASA Human Research Program,
  [Risk of Reduced Cardiorespiratory and Musculoskeletal Fitness](https://www.nasa.gov/reference/risk-of-reduced-cardiorespiratory-and-musculoskeletal-fitness/)
- Cardiovascular adaptation: NASA Human Research Program,
  [Risk of Cardiovascular Adaptations](https://www.nasa.gov/reference/risk-of-cardiovascular-adaptations/)

These are references to **published research topics**, not evidence that the
simulated measurements or suggestions were validated by NASA. No automatic
dosage, exercise duration, treatment or risk score is generated.

## Regression checks

```powershell
python -m pytest tests/copilot/test_wellness.py -q
python -m pytest -q
cd frontend
npm test
npm run build
# With the local FastAPI server running:
npm run test:integration
```

Verify stable, heart-rate change, sleep change, incomplete data and fictional
check-in, plus scene changes not carrying over a stale wellness context. The
new features should be merged only after user-local testing and PR review.

No actual automated reminders, third-party medical-device interfaces,
gamification, or astronaut environment sensor support are provided.
