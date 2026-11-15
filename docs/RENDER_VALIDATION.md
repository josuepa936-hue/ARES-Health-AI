# Render public demo — validation evidence

Validated locally on November 15, 2026, from `feat/render-public-demo`, based on
main `aadd7981eb3e6a91f06d7dec43906b56a1b41a73`. This is an independent deployment
branch. The documentation audit ref remains `8235188`; its changes are not copied
here. During that local preparation, this agent did not deploy, change credentials,
rewrite history or merge. The separate owner-reported deployment is recorded below.

## Preserved prior local checks

| Check | Result |
|---|---|
| Entire Python suite | **410 passed**: original 377 plus 33 new public-boundary checks; one existing Starlette/httpx deprecation warning |
| Existing frontend component/unit tests | **62 passed** |
| TypeScript / Vite production build | Passed, including Docker build |
| Existing development Vite/API integration | **19 passed**; local CSV/research behavior preserved |
| Public test module targeting actual container | **33 passed** (25 live HTTP cases plus 8 isolated origin/rate/concurrency checks) |
| Public Chromium workflows | **4 passed**: 1440 px desktop, 390 px mobile, private-route/error checks and navigation from a different site |
| Canonical output comparison | All four scenarios and corresponding timelines exactly equal existing main API responses at seed 2026 / 21 days |
| Maximum allowed workload smoke | Four concurrent 60-day timeline requests returned 200 |
| Live rate boundary | Reached 429 within the 240-request peer budget; Retry-After present; forged X-Forwarded-For did not bypass; health still available |
| Container runtime | Python **3.12.16**, UID/GID **10001**, root-owned application source not writable |
| Port configuration | Default test with PORT=10000; separate successful run with **PORT=10007** and RENDER_EXTERNAL_URL fallback |
| Fail-closed deployment image | ARES_PUBLIC_DEMO=0 rejected at entrypoint; missing/invalid HTTPS origin covered by configuration checks |
| Files / output | Git, .env, data, research artifacts and node_modules absent from runtime /app; session CA mount absent; application output log empty after probes |
| Configuration / diff | YAML parsed by local Prettier; git diff --check passed. Render's Blueprint validation was not independently observed |

Desktop/mobile checks exercise scenarios, fictional check-in, telemetry, charts,
timeline, deterministic question/explanation, NASA-linked Wellness, manual review
state, actual comprehensive JSON download and withheld interpretation. They assert
no page errors, no CSP console errors and no document horizontal overflow. Captures
were inspected; these are Chromium viewport emulations, not physical iOS/Android
certification. A different-site entry page is fulfilled locally, with real browser
navigation to the container; it is not an already-published evaluator URL.

Public negative tests cover host/origin rejection, frames and cross-site API
fetches, unavailable docs/research/CSV/legacy/file/admin routes, chunked and declared
oversize bodies, compression rejection, malformed/nonfinite/deep/duplicate-key
JSON, strict boolean attestation, unknown fields, 60-day cap and error nonreflection.
No penetration-test certification or distributed DDoS protection is implied.

## Build and environment qualifications

Docker image `ares-public-demo:local` was built using digest-pinned Node 24 and
Python 3.12 bases and frozen frontend/Python dependencies. In this cloud session,
stock images did not trust the managed HTTPS proxy CA. The initial build failed
certificate verification; the corrected build used a temporary Dockerfile that
mounts the existing combined trust bundle as a BuildKit secret and sets
NODE_EXTRA_CA_CERTS / PIP_CERT only in dependency-install RUN steps. TLS and npm
integrity checks stayed enabled; no CA, proxy setting or credential was baked into
the runtime. The checked-in Dockerfile targets ordinary trusted Render builds. At the time of
that local test, Render execution was unverified. The owner now reports Render
deployment success below; this update did not independently inspect build logs.

The container was run read-only with capabilities dropped and no-new-privileges.
`--memory 512m --cpus 2` were requested, but this environment's rootless Docker
reports **no cgroup driver**, so those CPU/memory limits were **not enforced**.
Observed process high-water RSS was approximately **211 MiB**, including the
maximum-workload smoke, but this is not a proven 512 MiB container budget or a
production capacity measurement. Verify plan resources and health on Render;
inspect current costs before creating the Starter service.

The recorded local checks did not establish a remote CI result. The deployment
branch was subsequently published; no fresh GitHub Actions result was inspected
for this documentation update. Do not equate local results with remote CI success.
Python 3.13, the entire existing visual-browser suite and optional
research-library benchmarks were not newly executed locally; required baseline
Python/frontend suites and the new public workflows did execute.

## Public Render acceptance — owner report, November 15, 2026

Public demo URL: **https://ares-health-ai.onrender.com/**.
Evidence source: [owner-provided report](evidence/OWNER_OFFLINE_REPORT_2026-11-15.md),
section 4, plus the owner's statement in this conversation.

| Acceptance item | Recorded status | Provenance / limit |
|---|---|---|
| Deployment dashboard | Deploy succeeded / Live — owner reported | Report identifies source e7e3a7c on feat/render-public-demo; dashboard/build logs not independently inspected |
| Public HTTPS interface | Accessible — owner reported | URL supplied by owner; no independent TLS certificate assessment in this update |
| Incognito access without sign-in | PASS — owner reported | Does not by itself establish all endpoints, browsers or security properties |
| Scenarios, deterministic Copilot and Wellness | PASS — owner reported | Public functional checks described by owner; separate from earlier local container tests |
| Fictional check-in and report export | PASS — owner reported | No new deployed-service export artifact independently inspected |
| Physical mobile device | Not reported / unverified | Earlier 390 px Chromium emulation remains separate local evidence |
| Deployed security settings / resource limits | Not independently audited | Local boundary tests do not prove every live host setting or production capacity |

### Current agent verification limit

A normal HTTPS request to `/api/status` from this managed environment failed at
its outbound proxy: **curl (56), CONNECT tunnel failed, response 403**, with no
HTTP response from the application (curl status 000). This is a network-policy
restriction on the checking environment, not evidence that Render is unavailable.
No allowlist, credential or Render configuration was changed to bypass it.
The public site is therefore recorded as **owner-accepted**, not independently
revalidated here. Do not describe the prior local counts as new live Render tests.

### Modes and remaining owner actions

Render is an **ONLINE** demonstration. Loss of Internet to Render does not invoke
a browser-only offline engine. The independently prepared local server is the
**OFFLINE** modality, with owner-reported Windows acceptance and preserved Linux
isolation evidence in [OFFLINE_VALIDATION.md](OFFLINE_VALIDATION.md).

The deployment guide remains the reproduction/configuration reference, not a
claim that this agent created a service. Existing protected public-mode code and
configuration are unchanged. User-entered content must remain fictional; origin
and rate limits are not authentication or a clinical data service.

Official Space Apps submission, final public project/demo links, asset/AI credits,
eligibility, licensing and platform confirmation remain owner-controlled actions.
This acceptance record does not establish submission, NASA authorization or
medical/flight validation. See [the handoff matrix](TECHNICAL_ACCEPTANCE_MATRIX.md).

## Reviewable changes

- Dockerfile, .dockerignore, requirements-deploy.lock: isolated, pinned build/runtime.
- render.yaml, deploy/start.sh, deploy/logging.json: manual-deploy Blueprint,
  PORT/one-worker startup and no application content logging.
- src/ares_health/public_demo.py plus api.py / serve_ui.py: opt-in transport
  boundary, public route selection/errors and runtime HTML mode marker.
- frontend/src/publicDemo.ts, Workspace.tsx, App.tsx, style.css: public disclosure
  and hidden unsupported research/CSV controls; existing evaluation stays in Python.
- tests/test_public_demo.py, frontend/public-e2e/console.spec.ts,
  frontend/playwright.public.config.ts, frontend/package.json and CI workflow:
  boundary and public browser checks. No existing dependency declarations or npm lock
  versions change; package.json adds only a test command.
- README.md and frontend/README.md: scoped pointers to public-mode instructions;
  RENDER_PUBLIC_DEMO.md / this evidence document: setup, limits and owner handoff.

The analysis, validation, synthetic generator, statistics, timeline, review,
mission, copilot and Wellness domain modules are unchanged. No illustrative alert
thresholds, scientific claims or JSON evaluation contracts are modified.
