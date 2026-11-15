# Copilot reading and evidence — Issue #17

This UI-only change starts from `feat/ares-v1.5-mission-copilot` at `0eb4ac6`.
Review branch: `feat/ares-issue-17-copilot-readability`; target the v1.5 branch,
not main. The Python engine, API contracts, synthetic CSV checks, timeline,
research modules and comprehensive report implementation are unchanged.

## Reading behavior

- The existing three-column mission console and contextual dock remain. The dock
  reserves a useful reading height while Copilot is selected. On short desktop
  windows, telemetry uses a compact layout; the separate analytics panel contains
  its own long content rather than overlapping the dock. All original chart,
  observation inspection, quality-event and review controls remain available.
- **Focus / expand conversation** opens a native modal dialog over the console.
  It reuses the same component, input draft, turns and disclosures. Native modal
  behavior traps keyboard focus and makes the background inert. Escape or
  **Restore docked conversation** restores the dock and the expand button's focus.
  **Review workflow** exits focus mode and selects the existing review tab.
- Desktop dock and focus mode have exactly one conversation scroll owner:
  `.copilot-history`, labelled **Conversation reading area**. Evidence and suggested
  questions grow within that surface; the dialog and its outer dock do not scroll.
  Compact mobile uses natural document scrolling; expanded mobile locks the
  document and scrolls only the reader. The composer stays outside the reader.
- New replies collapse the initial briefing and scroll to the **start of the
  latest turn**, never to the end of the evidence list. The turn heading receives
  keyboard focus and a separate polite status announcement identifies the reply.
  Opening evidence does not trigger reply scrolling or reposition the reader.
- Normal response text is 14px with 1.65 line spacing; controls and labels are
  12–13px, technical secondary text approximately 11–12px. Questions, answers,
  canonical assessment and limitations have distinct labels. Suggested questions
  are a single-column disclosure instead of a competing scrollable right rail.
  Scrolling is immediate; reduced-motion preferences suppress animation.

## Evidence integrity

**View evidence** opens a digest before the original reference list. Baseline,
recent mean and signed difference come directly from the active snapshot's
`descriptive_signals`; React only formats the supplied numbers. Actual UTC window
bounds come from the response's original reference/recent observation timestamps.
Scenario and assessment must match before displaying snapshot comparisons.
There is no second trend detector, new threshold or statistical calculation.

Rule IDs/engineering thresholds and official scientific links remain visible in
the digest. **Detailed observations, UTC dates and timeline IDs** reveals all
original observations. **Medical limitations and context reference** retains the
canonical context hash and every limitation. Background links remain external
references; opening them requires connectivity, but the copilot does not.

`DATA_QUALITY_BLOCKED` and `INSUFFICIENT_DATA` responses show quality/abstention
text and no comparison averages, even if an inconsistent snapshot contains
descriptive values. No review state grants medical authorization or changes the
canonical assessment. Conversation, fictional review audit and JSON export retain
the original v1.5 offline behavior and bounds.

## Real browser captures

These are actual headless Chromium renders against local FastAPI and compiled
React, using only `heart_rate_shift` / `incomplete`, seed 2026 and 21 days. Before
images were captured from the unmodified v1.5 build at the base commit; they show
the old expanded evidence view. After images show focused reading after asking
**What changed?**, with evidence opened and the latest turn positioned at its start.
No generated visual mockup is used.

| Viewport | Before (v1.5) | After (focused answer) | Evidence digest | Blocked data |
|---|---|---|---|---|
| 1440×900 | [Before](../frontend/screenshots/issue-17-before-1440.png) | [Answer](../frontend/screenshots/issue-17-after-1440.png) | [Evidence](../frontend/screenshots/issue-17-evidence-1440.png) | [Blocked](../frontend/screenshots/issue-17-blocked-1440.png) |
| 1366×768 | [Before](../frontend/screenshots/issue-17-before-1366.png) | [Answer](../frontend/screenshots/issue-17-after-1366.png) | [Evidence](../frontend/screenshots/issue-17-evidence-1366.png) | [Blocked](../frontend/screenshots/issue-17-blocked-1366.png) |
| 390×844 | [Before](../frontend/screenshots/issue-17-before-390.png) | [Answer](../frontend/screenshots/issue-17-after-390.png) | [Evidence](../frontend/screenshots/issue-17-evidence-390.png) | [Blocked](../frontend/screenshots/issue-17-blocked-390.png) |

Restored desktop composition: [1440×900](../frontend/screenshots/issue-17-docked-1440.png)
and [1366×768](../frontend/screenshots/issue-17-docked-1366.png). The mobile reader
allows the full long answer and evidence to be read sequentially, rather than
shrinking text to fit all content into one screen. Existing v1.4/v1.5 screenshots
remain unchanged. Existing browser workflows write fresh regression captures into
`frontend/screenshots/issue-17-regression/` (ignored locally, retained by CI artifacts).

## Reproduce and verify

Startup is unchanged. Install existing Python requirements and `npm ci` in
`frontend`, then build React. On Windows use `start-ares.cmd`; on Linux:

```sh
cd frontend
npm run build
cd ..
.venv/bin/python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

For tests, run the existing commands from their respective directories:

```sh
# Repository root
.venv/bin/python -m compileall -q app.py src tests
.venv/bin/python -m pytest -q
.venv/bin/python -m pytest -q optional_checks/ecg_integration.py
# frontend
npm test
npm run build
# Start the compiled one-server app on port 8014 in a separate terminal first.
npm run test:browser
# With existing FastAPI:8000 and Vite:5173 running:
npm run test:integration
```

Playwright uses its installed Chromium (or `ARES_CHROMIUM` / system Chromium).
On a fresh machine install it with `npx playwright install chromium`. Browser
regressions in `frontend/e2e/readability.spec.ts` check all three requested sizes,
reply/question visibility, focus/keyboard restoration, a minimum compact reading
height, no horizontal overflow, analytics containment, actual API means/dates,
stable evidence disclosure, one scroll owner, a new reply after long expanded
evidence, source links and blocked-data abstention. Existing browser tests retain
check-in, CSV, timeline, manual audit/export, research separation and failure checks.
Unit tests cover progressive evidence, canonical values, unsafe blocked payloads,
source/limitation retention and keeping a draft when changing modes. Vitest bounds
concurrent DOM workers to two for constrained runners without relaxing assertions.

## Local verification results (2026-11-15 UTC)

| Check | Final result |
|---|---|
| Python 3.12 compile + full pytest | `350 passed, 1 warning in 25.23s` |
| Python 3.13 compile + full pytest | `350 passed, 1 warning in 30.25s` |
| Optional offline WFDB/NeuroKit fixture checks | `4 passed, 2 warnings in 7.01s` |
| React unit/component tests | `58 passed (58)` |
| Live Vite/FastAPI HTTP integration | `18 passed (18)` |
| Compiled React/FastAPI Playwright | `9 passed (51.7s)` |
| TypeScript + Vite production build | Passed |
| `pip check`, targeted Prettier, `git diff --check` | Passed |

The existing Starlette/httpx and optional-tool deprecation warnings remain; no
test failed in the final runs. DOM suites run separately from the browser suite
to avoid resource starvation on the cloud runner. The browser count includes the
six original workflow checks and three new viewport regressions. Automated axe
audits found zero violations in the tested default, docked Copilot, focused Copilot
with expanded evidence, and review states. These results reproduce the relevant
CI checks locally; they do not claim a completed GitHub Actions run.

These are software checks, not clinical validation. Chromium viewport testing on Linux does
not establish actual Windows, iOS/Safari or physical-device behavior. Automated axe
checks cover audited default/docked/focused/review states, not a complete manual
accessibility certification. The inherited optional public-record acquisition
limits remain documented in the research guides.
