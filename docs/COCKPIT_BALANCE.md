# Cockpit and conversation balance — Issue #19

Base: `feat/ares-issue-17-copilot-readability` at `ebfd86c`.
Review branch: `feat/ares-issue-19-cockpit-balance`. Review against the base branch;
do not merge automatically. This is a React presentation/state-navigation change.
Python source, biomedical rules, API schemas, CSV validation, MIT-BIH, NASA OSDR,
synthetic context, timeline, audit and report logic remain unchanged.

## Cause and correction

Issue #17 assigned a 376–420px dock while allowing the mission grid to shrink to
zero. Its low-height media rules additionally hid sparklines and turned telemetry
into small horizontal rows. Reproducing the unmodified base in Chromium showed:

| Desktop viewport | Card height | Visible anatomy/image height | Main chart height |
|---|---:|---:|---:|
| 1920×820 | 62px | 119px | 45px |
| 1440×900 | 77px | 188px | 45px |
| 1366×768 | 45px | 67px | 45px |

`frontend/src/console/layout.css` now owns the cockpit sizing policy. The desktop
mission grid reserves at least 560px, each telemetry card at least 156px, anatomy
stage/frame at least 320px, and the primary graph 180px including its axis area.
Sparklines, units, comparison/withholding labels and UTC dates remain visible.
The illustration is contained in its frame; intrinsic image dimensions do not
force the row's height. Existing anatomy selection, zoom and source artwork remain.
Mobile retains its stacked layout with 200px telemetry cards, readable dates and
the existing full anatomy and graph.

The old viewport-height compression rules were removed from `copilot/reading.css`,
which continues to own reading typography and Focus behavior. Docked conversation,
suggestions and evidence flow naturally below the cockpit, with the document as
the single default vertical scroll surface. Long answers are never clipped or
given tiny fonts to fit a fixed dock. Other workspace tabs also grow naturally;
there is no competing default dock scrollbar. Explicit observation inspection
still uses its existing bounded table overlay when requested.

## Intentional interaction tradeoff

All mission panels and a long 14px conversation cannot fit simultaneously into
every 768–900px-high window. The default preserves useful cockpit geometry and
allows **vertical page scrolling** to read the dock below. This replaces Issue
#17's no-document-scroll constraint, which caused the regression. Horizontal
document overflow remains prohibited. Mobile already uses the same document-flow
approach. No panel is automatically made miniature when a conversation opens.

- **Full cockpit** explicitly collapses the workspace, scrolls back to the top
  and returns focus to the Copilot launch button. **Open workspace** restores the
  previous tab, conversation and draft. Neither action fetches/recalculates data
  nor changes scenario, selected physiology, assessment or review state.
  The top **ARES Copilot** launch button navigates directly to its dock and focuses
  the active tab so a conversation is never opened silently below the viewport.
- **Focus / expand conversation** retains Issue #17's native modal, 14px answer
  text, concise evidence, original IDs/sources and medical limitations. Its header
  explicitly says the cockpit is behind the reading dialog. Only the conversation
  reader scrolls in this mode; the background document is locked and inert.
- The dialog's document placeholder preserves reading position while it is in
  the browser top layer. Escape/restore returns to the same dock position and
  focus control. The full-size cockpit above is still available through **Full
  cockpit**. Focus mode changes neither the data nor the underlying cockpit size.
- New answers still start at the latest question/answer heading, with keyboard
  focus and a polite announcement. Docked mode moves the document to that turn;
  Focus moves only its reader. Opening evidence does not perform reply scrolling.

Startup remains unchanged (`npm ci`, `npm run build`, existing `start-ares.cmd`
or local FastAPI launcher). No package, external service or runtime model was added.

## Actual browser screenshots

Before images are actual renders of the unmodified Issue #17 build. After images
show Stable observations with Copilot selected and the cockpit at the top of the
page. Conversation captures include the complete document to show the intentional
relationship between full-size panels and readable docked answers. Focus images
show the same synthetic question in the explicit reading modal.

| Viewport | Before | Docked cockpit after | Conversation | Focus |
|---|---|---|---|---|
| 1920×820 | [Before](../frontend/screenshots/issue-19-before-1920.png) | [Cockpit](../frontend/screenshots/issue-19-after-1920.png) | [Conversation](../frontend/screenshots/issue-19-conversation-1920.png) | [Focus](../frontend/screenshots/issue-19-focus-1920.png) |
| 1440×900 | [Before](../frontend/screenshots/issue-19-before-1440.png) | [Cockpit](../frontend/screenshots/issue-19-after-1440.png) | [Conversation](../frontend/screenshots/issue-19-conversation-1440.png) | [Focus](../frontend/screenshots/issue-19-focus-1440.png) |
| 1366×768 | [Before](../frontend/screenshots/issue-19-before-1366.png) | [Cockpit](../frontend/screenshots/issue-19-after-1366.png) | [Conversation](../frontend/screenshots/issue-19-conversation-1366.png) | [Focus](../frontend/screenshots/issue-19-focus-1366.png) |
| 390×844 | [Before](../frontend/screenshots/issue-19-before-390.png) | [Cockpit](../frontend/screenshots/issue-19-after-390.png) | [Conversation](../frontend/screenshots/issue-19-conversation-390.png) | [Focus](../frontend/screenshots/issue-19-focus-390.png) |

Full cockpit restoration: [1920](../frontend/screenshots/issue-19-full-cockpit-1920.png),
[1440](../frontend/screenshots/issue-19-full-cockpit-1440.png),
[1366](../frontend/screenshots/issue-19-full-cockpit-1366.png),
[mobile](../frontend/screenshots/issue-19-full-cockpit-390.png).
Previously unreviewed contexts: [changed desktop](../frontend/screenshots/issue-19-heart_rate_shift-1440.png),
[blocked desktop](../frontend/screenshots/issue-19-incomplete-1440.png),
[changed mobile](../frontend/screenshots/issue-19-heart_rate_shift-390.png),
[blocked mobile](../frontend/screenshots/issue-19-incomplete-390.png).
All scenarios are fictional, seed 2026 / 21 days. Original Issue #17 screenshots
remain unchanged; its recurring regression captures now use the ignored
`frontend/screenshots/issue-19-regression/` artifact directory.

## Verification

`frontend/e2e/cockpit-balance.spec.ts` exercises all four viewport sizes and stable,
changed and blocked sources. It checks actual card/image/chart bounding boxes,
non-overlapping labels/dates and metrics, fully visible sparklines and axis labels,
contained panels, zero horizontal overflow, document-flow docked reading, API
values, readable answer-first navigation, native Focus/restore and reading-position
preservation. Collapsing/restoring the workspace must retain draft, conversation
and active scenario without new requests. Changed comparisons must equal Python
responses; blocked evidence must contain no averages. The existing review/CSV/
research/timeline/export/browser suites are also retained.

Run the existing full CI commands: Python compile/pytest on 3.12 and 3.13, optional
offline WFDB/NeuroKit checks, TypeScript/Vite build, React unit/component tests,
live Vite/FastAPI HTTP tests, one-server distribution smoke and Playwright. Browser
tests use compiled React + FastAPI on port 8014. The usual Chromium installation
or `ARES_CHROMIUM` override applies. No biomedical fixtures were regenerated.

### Final local results — 2026-11-15

| Check | Result |
|---|---|
| Python 3.12 compile + full pytest | `350 passed, 1 warning in 25.71s` |
| Python 3.13 compile + full pytest | `350 passed, 1 warning in 22.55s` |
| Optional offline WFDB/NeuroKit fixtures | `4 passed, 2 warnings in 9.72s` |
| React unit/component tests | `59 passed (59)` |
| Live Vite/FastAPI HTTP | `18 passed (18)` |
| Compiled React/FastAPI Playwright | `13 passed (1.3m)` |
| TypeScript + Vite production build | Passed |
| Fresh one-server distribution smoke | Passed |
| `pip check`, targeted Prettier, `git diff --check` | Passed |

The fresh one-server smoke started a separate FastAPI process and retrieved the
root document, compiled JS/CSS, status, canonical demo, risk guide and synthetic
CSV template. Automated axe WCAG AA checks passed in the audited default, docked,
focused evidence and review states. All four new viewport regressions passed for
stable, changed and blocked sources; all nine prior browser regressions passed.
The new component regression preserves the selected mission and draft across
full-cockpit/workspace toggles without new requests. Expensive chart/DOM suites
now use one Vitest worker to prevent constrained-runner CPU starvation; assertions
and timeouts remain unchanged. Existing dependency deprecation warnings remain.

These are local software checks, not a claim of completed GitHub Actions, medical
validation, physical mobile-device coverage or Windows execution. Captures use
actual Linux Chromium. No Python source or biomedical fixture was changed.
