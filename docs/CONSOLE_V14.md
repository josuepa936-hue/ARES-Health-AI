# ARES v1.4 — Mission control redesign

This branch is based on `feat/ares-v1.3-integrated-mission-console` at `ee99851`
(PR #12), not main. The draft review must target that branch. Neither PR is merged
by this implementation. No Python source, FastAPI endpoint, biomedical threshold,
MIT-BIH/NASA OSDR processing, validation, timeline, CSV or report schema is changed.

## Functional composition

At 1440×900 the app is one command center, with an API-backed status/scenario bar,
three telemetry indicators, anatomical navigation, an interactive analysis panel,
and a docked contextual workspace visible in the first screen. This is a React
implementation, not an image used as a UI. CSS grid, domain-specific presenters,
Recharts and Lucide icons replace the prior vertically stacked layout. No remote
font or CDN asset is needed for the compiled mission interface.

- `MissionCommandBar`: actual source/profile/observation UTC timestamp, scenario,
  request reload and disclosure/asset information. No fabricated live mission time.
- `TelemetryCard`: latest raw API value, full-dataset sparkline with missing-value
  breaks, last valid timestamp, and API-supplied comparison delta only when analysis
  is available. A missing latest observation stays `—`; it is not replaced with an
  older valid measurement. CSV lengths/profile IDs are reflected from the response.
- `BodyViewer`: keyboard-operable heart-rate, sleep-context and activity hotspots
  select the same metric as the telemetry rail and analysis tabs. Other body regions
  explicitly report NOT MONITORED. No organ health, radiation or neurological sensor
  coverage is inferred from the anatomical illustration. Enlarge/reset is presentation
  only; hotspot selection never creates an analysis or medical risk.
- `MetricPanel`: actual dated samples, units, hover/keyboard chart tooltips, separate
  reference/recent means and exact existing rule explanation. No JS mean, threshold,
  imputation, detector or risk algorithm. Missing data are gaps; blocked analysis
  withholds means/deltas/flags/statistics. Raw values remain inspectable in a table.
- `ContextDock`: keyboard tabs (arrows/Home/End), accessible panels and collapse control
  for Check-in, Mission Timeline, Review & Export, Spaceflight Risks, Research Sources.
  Components stay mounted so drafts/filter state are preserved when tabs change.
- Check-in uses the original attested Python endpoint, updating all columns, source,
  timeline and embedded report together. CSV uses its own response timeline/report.
  Backend procedural guidance and limitations remain available in the review drawer.
- MIT ECG and NASA mouse-retina OSD-87 stay in distinct, explicitly labeled research
  modes. They never fill synthetic crew cards, anatomy status or mission scores.

Rapid mission changes retain the existing abort/sequence guards. Loading, failure
and quality-blocked states clear old results rather than inventing observations.
The persistent footer and information panel state fictional-only, nonmedical use.

## Anatomy artwork and licenses

`frontend/src/console/crew-anatomy.png` is an **original AI-generated illustration**
created with OpenAI's image tool during this implementation. It depicts a fully
clothed fictional human with anatomical overlays; it is not a patient, NASA image,
third-party stock/model asset, or actual sensor visualization. Output use is governed
by the user's applicable OpenAI terms (https://openai.com/policies/terms-of-use/).
No third-party anatomical license or clinical accuracy certification is claimed.

A vetted licensed clinical-grade anatomical model was not available in this task.
This is the issue's polished illustration fallback, **not a validated anatomical
reference**. Muscle/organ appearance and color are decorative, may be imperfect,
and never encode health/severity. The amber in the source artwork is decorative;
UI amber badges are reserved for API demonstration changes. No primitive mannequin
or borrowed model substitutes for the asset. A future licensed model can replace
this image while preserving the independent domain controls and attribution.
The original reference screenshots mentioned by the user were not attached as
accessible files in this task; visual direction follows Issue #13's written brief.

Runtime libraries: Recharts (MIT), Lucide React (ISC), React (MIT), Zod (MIT), Vite
(MIT). Test tooling adds Playwright (Apache-2.0) and axe-core Playwright integration
(MPL-2.0). Their upstream notices remain in installed packages. The generated asset
has its own provenance; these software licenses do not license an external anatomy
asset. No third-party anatomical asset was bundled.

## Windows / one-server startup

From the repository root after switching to this branch, synchronize the new locked
frontend dependencies once (Node 22.12+; Node 24 verified):

```powershell
cd frontend
npm ci
cd ..
.\start-ares.cmd
```

The existing launcher builds React and serves it with FastAPI on
`http://127.0.0.1:8000/`. Keep that window open. With a verified existing build:

```powershell
.\start-ares.cmd --skip-build
```

Install Python requirements as documented in the root README if this is a fresh
checkout. The unchanged research enablement/preparation procedures still apply;
missing research artifacts show their existing unavailable/abstention states.
No Vite process is required for this one-server workflow. Runtime anatomy and JS
assets are hashed files served by the existing `/assets` mount.

## Reproducible verification and captures

```powershell
python -m pytest -q
python -m pytest -q optional_checks/ecg_integration.py
cd frontend
npm test
npm run build
# Use a second terminal to run the single server on a chosen local test port:
# python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8014
$env:ARES_E2E_ORIGIN="http://127.0.0.1:8014"
npx playwright install chromium
npm run test:browser
```

Playwright uses installed system Chromium when available, an explicit
`ARES_CHROMIUM` path when configured, or its managed Chromium installation.
Cloud browser checks used port 8014 to avoid reserved/conflicting desktop ports;
this validates the same one-server compiled distribution. Windows port 8000 startup
is documented and its launcher retained; the Windows batch executable was not run
on Linux. The original Vite/API HTTP suite remains available as `npm run
test:integration` with its documented local services.

Actual browser captures are in `frontend/screenshots/`:
- `mission-desktop.png`: 1440×900 stable scenario composition.
- `mission-change.png`: heart-rate-shift API state and explanation.
- `mission-blocked.png`: quality failure and withheld interpretation.
- `mission-mobile.png`: exact 390×844 viewport capture.
- `mission-mobile-full.png`: full-page mobile composition from that viewport.

These are Chromium screenshots of the compiled React/FastAPI app, not generated
mockups. Playwright covers real scenario switching, blocked data, anatomical/metric
selection, 140 bpm / 7 h / 45 min attested check-in, updated timeline, JSON download,
CSV, NASA hazards, research modes, retry/late-response handling and mobile keyboard
interaction. An automated axe WCAG AA check is included; it is not a substitute
for a complete manual accessibility audit. CI retains screenshots/failure traces.

No 45 FPS guarantee on ordinary laptop hardware is claimed. There is no animated
3D scene, continuous polling, or chart tweening. Browser screenshots and functional
checks establish rendering/behavior on this Linux Chromium environment, not a
universal performance certification. No screencast was recorded.

## Verified local results

Python 3.12 / Node 24 / headless system Chromium:
- 295 Python regression tests passed; no Python source or test changes.
- 4 offline biomedical fixture tests passed.
- 46 React unit/component tests passed (the prior 44 retained/adapted to tabbed UX).
- 12 live HTTP integration tests passed with the existing FastAPI/Vite protocol.
- 4 Playwright browser tests passed on the actual compiled one-server app,
  including desktop/mobile workflow and automated axe WCAG AA checks (zero detected
  violations on the audited default desktop state).
- TypeScript/production build, dependency consistency and diff checks passed.

Existing dependency deprecation warnings remain non-failing. CI now also runs
Playwright and retains review artifacts; remote GitHub Actions status is not
claimed because this environment's GitHub API requests return HTTP 403.
