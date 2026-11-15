# Render public demo — validation evidence

Validated locally on November 15, 2026, from `feat/render-public-demo`, based on
main `aadd7981eb3e6a91f06d7dec43906b56a1b41a73`. This is an independent deployment
branch. The documentation audit ref remains `8235188`; its changes are not copied
here. No deployment, credential change, history rewrite or automatic merge occurred.

## Completed checks

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
| Configuration / diff | YAML parsed by local Prettier; git diff --check passed. Render's own Blueprint validation has not run |

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
the runtime. The checked-in Dockerfile targets ordinary trusted Render builds.
It has not yet been executed by Render itself.

The container was run read-only with capabilities dropped and no-new-privileges.
`--memory 512m --cpus 2` were requested, but this environment's rootless Docker
reports **no cgroup driver**, so those CPU/memory limits were **not enforced**.
Observed process high-water RSS was approximately **211 MiB**, including the
maximum-workload smoke, but this is not a proven 512 MiB container budget or a
production capacity measurement. Verify plan resources and health on Render;
inspect current costs before creating the Starter service.

The workflow now includes Docker/public checks but has not been pushed or run
remotely in this task. Do not equate local results with GitHub Actions success
for this branch. Python 3.13, the entire existing visual-browser suite and optional
research-library benchmarks were not newly executed locally; required baseline
Python/frontend suites and the new public workflows did execute.

## Outstanding external acceptance

**No public HTTPS Render URL exists or was provided for this task.** The owner
explicitly requested no automatic publication. Therefore an external Internet
browser, real Render TLS, proxy headers, deployed resource limits and evaluator
access cannot yet be verified. This is a concrete deployment prerequisite, not
an application test claimed as passed.

Follow [the Render guide](RENDER_PUBLIC_DEMO.md): review and push the feature branch,
connect the repository, inspect costs/configuration, manually deploy, then run
public tests against the actual HTTPS origin and repeat desktop/mobile acceptance
from outside this cloud environment. Only then announce availability. Official
Space Apps submission and licensing/asset-rights decisions remain owner actions.

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
