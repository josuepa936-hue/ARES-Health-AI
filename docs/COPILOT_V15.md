# ARES v1.5 — offline mission copilot and fictional review workflow

Based on v1.4 branch `feat/ares-v1.4-mission-control-redesign` at `871915c`.
This feature must be reviewed against that branch, not merged automatically.

## What this is

ARES Copilot is an **offline deterministic explanatory service** with a bounded
English/Spanish intent parser. It is **not an LLM or generative model**. There is
no model plugin, API credential, remote inference, retrieval request or invented
medical protocol. All physiological facts come from recalculated canonical Python
snapshots, existing rules, reports and timeline. NASA/CSA references come from the
existing local evidence and NASA five-hazard guide. Reference links can be opened
by a user when online; opening them is not required to operate the copilot.

The original mission console, anatomical illustration/attribution, scenario,
check-in, CSV validation, timeline, scientific context, MIT-BIH and NASA OSDR
research remain available. Public terrestrial ECG and mouse-retina research are
never converted into synthetic crew evidence, risk scores or medical claims.

## User journey

1. Open the one-server console with the existing `start-ares.cmd` workflow.
   Select a scenario, make an attested fictional check-in, or import an attested
   valid synthetic CSV. Python evaluates the actual source as before.
2. The **ARES Copilot · briefing ready** button or **ARES Copilot** dock tab opens
   the automatic briefing while vitals, anatomy and charts remain visible. It
   distinguishes no-trigger, demonstration change, and blocked/insufficient states.
   Missing input never produces a reassuring comparison or numerical averages.
3. Choose a contextual question chip or type a bounded fictional question.
   Supported topics are changes, reference windows, dates/values, quality and
   verification, next review, NASA background, documentation and unmonitored
   domains. Unsupported topics abstain; unsafe/override requests refuse. This
   conservative keyword parser may refuse benign wording; it is not a general
   language-understanding system or comprehensive clinical safety classifier.
4. **Why this response** expands exact observation timestamps, metrics, units,
   window membership, matching timeline IDs, rule IDs/metadata and official source
   URLs where relevant. Refusals and workflow-policy explanations add no
   physiological claim and explain their policy limitation rather than inventing
   scientific citations. A context hash identifies the recalculated data source.
5. In **Review & Export**, manually record fictional source/unit verification,
   timestamp/context verification, approved-protocol reading and a hypothetical
   request for authorized clinical review. Checking a box is a user declaration,
   not evidence that a real protocol was read or anyone was contacted.
6. Select one of four **user-controlled** review states. Record an optional
   fictional note, explicitly attest the review is fictional, build the integrated
   report and download its JSON. Editing a note requires **Record fictional note**
   before export; unrecorded edits disable build/download. New answers, confirmed
   actions, state changes and recorded notes invalidate an older report.

No review action/state changes the analysis, quality findings, threshold flags,
measurement values or interpretation availability. No state grants authorization.
There is no diagnosis, triage, medication, treatment, clinical fitness or medical
urgency decision.

## Four-state workflow and audit

| State | Meaning in this demonstration |
|---|---|
| `PENDING_REVIEW` | Initial state; no review action is inferred |
| `IN_PROGRESS` | User has manually labelled a fictional review as in progress |
| `AWAITING_AUTHORIZED_REVIEW` | User-recorded fictional wait; no real referral/message is sent |
| `DOCUMENTED` | User-labelled documentation status; **not clinical clearance** |

Transitions are manual, reversible and recorded in sequence. No checklist or
conversation automatically advances state. The app does not claim that a status
proves action completion. Checking and unchecking are separate audit events;
notes and state edits are also recorded. Logical sequence numbers preserve event
order; they are **not authenticated institutional timestamps**. Evaluation UTC
observation timestamps remain exact source timestamps.

The log is bounded to 64 events, notes to 500 characters, and conversation to 20
successful turns of at most 240 characters. A full log can be exported; starting
or resetting a mission discards it. Source/scenario/check-in/CSV replacement and
page reload reset conversation, draft notes, review actions, attestation and state.
Changing only the displayed chart metric does not change evaluation context.
Reset/retry is explicitly labelled as a reset. Browser memory is the only session
store: no localStorage, database, institutional case status or server transcript.
The JSON export is an explicit user-initiated file download.

## Canonical context and request integrity

`copilot_models.py` defines discriminated, extra-forbidden context schemas:

- `kind=scenario`, one of the four supported IDs, seed 0–999999 and 12–366 days.
  Optional `check_in` contains the existing bounded three fictional measurements,
  explicit boolean attestation and unique allowed hypothetical concerns.
- `kind=synthetic_csv`, explicit true boolean attestation and UTF-8 CSV text. The
  existing importer is reused unchanged: max 1,000,000 bytes, exact six columns,
  fictional SIM profile, synthetic provenance, UTC chronology, daily cadence and
  existing measurement checks. Arbitrary client assessments, responses, research
  data kinds and unknown fields are not accepted.

Every request rebuilds from this source. Check-ins reuse `fictional_checkin`;
scenarios/CSV reuse `build_snapshot` and `build_timeline`. Comparison means/deltas
are selected from the canonical descriptive output, not reimplemented. Display
text rounds computed values to three decimals; exports retain the canonical
precision. No value such as a specific bpm difference is hardcoded as a finding.
Existing first-seven/latest-four window and inclusive 12 bpm / 1.5 hour rules are
unchanged; activity still has no change rule.

`context_ref=ctx-<sha256>` hashes canonical snapshot/timeline JSON. It is a
reproducibility/scope marker, **not an authentication token or signed provenance
proof**. Subsequent turns and export submit the expected hash; mismatch returns
409. Browser scope keys and AbortController guards additionally reset/ignore stale
responses, including a repeat evaluation of identical data. Notes/questions never
become instructions for the context builder or analysis engine.

## API

### `POST /api/mission/copilot`

```json
{
  "context": {"kind":"scenario","scenario":"stable","seed":2026,"days":21},
  "question":"What changed?",
  "turn":1
}
```

Empty question with turn 0 requests a briefing. Questions require turns 1–20.
Send `expected_context_ref` from the briefing on subsequent turns. The response
contains `answer`, bounded `intent`, `context_ref`, canonical `scenario` and
`assessment`, `turn`, `engine=deterministic-offline`, `generative_model=false`,
`demo_only=true`, `provenance=synthetic`, `evidence_refs`, `limitations`,
`supported_actions` and `suggested_questions`.

Observation evidence links exact original UTC values and timeline IDs; rule
evidence comes from existing metadata. Blocked/insufficient answers expose quality
findings/limitations only, without window averages or fabricated observations.
NASA answers expose existing official URLs and explicit coverage limitations.

### `POST /api/mission/comprehensive-report`

Submit the same context, mandatory `expected_context_ref`,
`fictional_attestation=true`, ordered `questions` (`turn`, `question` only), and
ordered `audit_log` entries:

```json
{
  "sequence":1,
  "action":"review_state",
  "review_state":"IN_PROGRESS"
}
```

Other action entries use `action=source_units|timestamp_context|mission_protocol|
authorized_review` and `checked=true|false`. Notes use `action=note` with `note`.
Payload fields must match the action; sequences and turns must be contiguous from
1. No client-provided assistant answer, result or medical authorization is trusted.

Export recomputes all included answers in the active context and replays user
review declarations. Unsupported/unsafe turns are omitted (and counted) rather
than embedding their raw requests in a supposedly appropriate review transcript.
The briefing is separate from user turns. Notes are literal user text, never
instructions; React text rendering/JSON download do not evaluate HTML/scripts.

The result is **one** comprehensive report retaining the legacy `1.0-demo` fields
and adding `copilot_schema_version=1.5-demo`, UI version, context ref, evaluated
measurements, exact comparisons/window dates, quality findings, full timeline/IDs,
rule metadata, NASA guide, scientific citations, deterministic briefing/transcript,
limitations and `fictional_review` audit/state/actions/note. No numerical
comparisons appear for a blocked dataset. Existing `/api/review` is unchanged for
backward compatibility; production console export now uses the comprehensive
endpoint, avoiding duplicate independent review controls.

The legacy report's two-state `review_state` stays schema-compatible:
`DOCUMENTED` maps to user-recorded `Reviewed in demo`; the other manual states map
to `Pending review`. The exact four-state status is in `fictional_review`.
`clinical_authorization` is always false. This mapping never affects assessment.

### Bounds and errors

Only the two new routes use a bounded route handler: streaming stops at
1,300,000 request-body bytes before normal typed FastAPI parsing. JSON requires
`application/json`, finite numbers and valid Unicode. Errors expose sanitized
validation paths/messages, not raw CSV/question bodies. Defaults for existing API
routes and their middleware remain unchanged.

- 413 oversized body; 415 unsupported media type.
- 422 malformed/nonfinite JSON, unsupported fields/kinds, invalid source/CSV,
  excessive turns/events/notes, malformed audit or non-boolean attestation.
- 409 expected context differs from canonical recalculation.

## Tests, browser review and startup

Existing root/frontend README startup still applies; no new dependencies, secrets
or external services are needed for runtime. Compile React and use the existing
one-server launcher (127.0.0.1:8000). Cloud browser tests use supported local port
8014. Python remains the only physiological calculation source.

```powershell
python -m pytest -q
python -m pytest -q optional_checks/ecg_integration.py
cd frontend
npm ci
npm test
npm run build
# With one-server FastAPI on 127.0.0.1:8014:
npm run test:browser
# With the existing local FastAPI + Vite services:
npm run test:integration
```

`frontend/scripts/export_copilot_fixtures.py` refreshes self-contained fictional
fixtures from Python. Frontend mocks never implement a second biomedical engine.
Backend tests cover exact values/dates, refusal/injection, quality abstention,
source/schema mismatch, finite JSON/stream bounds, manual state invariance, audit
replay, export coherence and blocked interpretations. Browser tests use actual
compiled React + FastAPI and explicit fictional inputs; core requests remain local.

v1.5 browser images are named `copilot-v15-*` and `mission-v15-*` in
`frontend/screenshots/`. Desktop images use 1440×900; mobile viewport images use
390×844, with separate full-page captures. Original v1.4 images/asset attribution
remain intact. Captures are real Chromium renders, not generated UI mockups.
Automated axe checks cover default console, active Copilot and Review views; they
are not a complete manual accessibility certification. No universal laptop FPS
or Windows batch execution on Linux is claimed. No PDF/HTML export or generative
plugin was added; they are optional scope and not required for the offline core.

## Local verification results

- Python **3.12 and 3.13**: **350 passed on each**, including all original tests.
- Offline WFDB/NeuroKit biomedical fixtures (Python 3.12): **4 passed**.
- React unit/component suite: **54 passed**.
- Live Vite/FastAPI HTTP integration: **18 passed**.
- Actual compiled one-server Playwright suite: **6 passed**, with real desktop
  and mobile captures; additional screenshot-focused rerun passed.
- Automated axe WCAG AA checks passed on default console, active Copilot and
  Review views (zero detected violations on audited states).
- TypeScript/production build, compileall, pip check and diff checks passed.

Known upstream Starlette/httpx and NeuroKit/SciPy deprecation warnings remain
non-failing. These are local verification results; GitHub Actions status is not
claimed while this environment's GitHub API access returns Forbidden. The
existing CI matrix/screenshot artifact job automatically includes the new tests.
