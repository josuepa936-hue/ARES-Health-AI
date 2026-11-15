# ARES v1.5 — bounded public demonstration on Render

Deployment branch: `feat/render-public-demo`, based on main `aadd798`.
This work does not duplicate or modify `docs/issue-26-delivery-audit` / `8235188`.
No biomedical algorithms, thresholds, evaluation rules or existing history change.
No Render service has been created or published by this change.

## Deployment contract

Docker builds the committed React lockfile with Node 24, then runs the existing
FastAPI/static-file server with Python 3.12. Both base images are digest-pinned;
`requirements-deploy.lock` pins the Python environment verified with v1.5. The
original development requirements remain unchanged. Refresh pins intentionally
and rerun checks; version pins do not replace vulnerability monitoring.

The final image copies only src/, the compiled frontend and deployment scripts.
No Git metadata, .env, credentials, research artifacts, CSV uploads, datasets,
internal docs, source maps or application file-browser endpoint are published.
The process uses UID 10001, one Uvicorn worker, no trusted forwarded headers and
no application access/exception-content logs. PORT defaults to 10000 and is
supplied by Render. Render terminates HTTPS; the internal process binds 0.0.0.0.
There are no volumes, database, accounts, cookies or server-side session storage.
The entrypoint refuses to start without compiled UI assets.

## Public mode and limits

| Setting | Required value / behavior |
|---|---|
| `ARES_PUBLIC_DEMO` | `1`; enables public boundary, hides research/CSV UI, disables API docs |
| `ARES_RESEARCH_ENABLED` | `0`; public mode excludes research routes even if mistakenly set to 1 |
| `PORT` | Render-provided; do not hardcode a browser URL into the frontend |
| `RENDER_EXTERNAL_URL` | Render automatically supplies the service's public HTTPS origin |
| `ARES_PUBLIC_ORIGIN` | Optional exact HTTPS origin override for a custom domain; no path, wildcard or credentials. Takes precedence over RENDER_EXTERNAL_URL |

Public mode fails startup without an origin. HTTP origins are accepted **only
for literal loopback hosts** during local tests. All real public hosts require
an HTTPS configured origin. Do not expose the local test HTTP port publicly.
Host and Origin must match the configured origin; cross-site API fetches, frames
and CORS preflights are rejected. Top-level navigation to / from an external
project link is allowed so evaluators can enter the console. Health GET /api/status is a constant cheap probe exempt
from host/rate checks. This is not authentication: public clients can call the
allowlisted API directly and can forge Origin headers outside browsers.

- Allowed API: status, scenarios, evidence links, demo, timeline, risk-guide,
  fictional-check-in, deterministic copilot, wellness and comprehensive-report. UI and generated hashed /assets files use the same origin.
- Only JSON POST, no compressed bodies, maximum **64 KiB**, counted while streaming
  before existing middleware buffers it; **10-second** body receipt timeout.
  Duplicate keys, nonfinite numbers, unknown fields and coercions are rejected.
- Scenario work is limited to **12–60 fictional days** (default still 21). This
  caps public workload without changing evaluation windows or thresholds.
- **240 requests/minute per transport peer**, **1200/minute globally**, at most
  **4 active requests**, bounded rate state for 2048 peers. Excess returns 429
  or 503 with Retry-After. One instance / one worker is required for these budgets.
  Uvicorn also caps concurrent connections at 32. Health is exempt.
- Render may share proxy peer addresses, so visitors can share a peer budget.
  User-supplied X-Forwarded-For does not bypass it. These in-process limits reset
  on restart and are not distributed DDoS protection. Scaling needs a separately
  designed shared limiter / platform edge protection; do not silently add workers.
- Research, arbitrary synthetic CSV upload (including copilot CSV contexts),
  synthetic-template download, legacy /api/review, docs/OpenAPI, unknown routes and file paths are
  unavailable publicly. They remain unchanged in local development mode.
- Strict CSP (scripts/connect self only), frame denial, nosniff, no-referrer,
  restricted permissions, no-store and HTTPS HSTS protect the served responses.
  Inline styles are allowed for existing React/Recharts rendering; inline scripts
  are not. No external research fetch is necessary for mission mode.
- Public errors do not reflect inputs, validation payloads or exception details.

## Data policy and limitations

A persistent notice identifies an experimental fictional-data demo, not a medical
device or NASA-authorized system. Check-ins require boolean fictional attestation;
questions/review notes are bounded, transient demonstration text. **Software
cannot prove whether user-entered values/text are fictional.** Never enter names,
identifiers or real medical information. Arbitrary CSV intake is disabled to
reduce that exposure. No application payload logging or persistence is enabled;
Render's infrastructure metadata/logging policies remain the owner's responsibility.
No promise is made that arbitrary data sent to the Internet cannot reach hosting
infrastructure. The demo does not offer medical services or authenticated clinical
records. Reports download to the visitor's device; nothing is filed with NASA.

## Exact Render steps — owner action, no automatic publication

1. Review the deployment branch diff and tests. Push **this branch** to GitHub
   when approved: `git push -u origin feat/render-public-demo`. Do not push the
   audit branch again, force-push, or merge either branch automatically.
2. Sign in to Render and connect the GitHub repository through Render's normal
   integration. Choose only the access needed for this repository; do not paste
   tokens into files, chat or environment variables. No credentials are required
   by ARES itself.
3. Choose **New → Blueprint**, repository `josuepa936-hue/ARES-Health-AI`, branch
   `feat/render-public-demo`, blueprint path `render.yaml`. Inspect the plan and
   cost before applying: the example uses one **Starter** instance. Applying
   creates a service and publishes it; this is an owner action, not performed here.
   Alternative: create a Docker Web Service manually with that same branch,
   Dockerfile `./Dockerfile`, context `.`, health path `/api/status`, one instance,
   and automatic deploys disabled. Do not add a public Streamlit/Vite server.
4. Confirm ARES_PUBLIC_DEMO=1 and ARES_RESEARCH_ENABLED=0. Use Render's generated
   RENDER_EXTERNAL_URL initially; no secret or custom origin is needed. For a
   custom domain, configure it in Render and set ARES_PUBLIC_ORIGIN to its exact
   HTTPS origin before using it; only one origin is supported at a time.
5. Perform **Manual Deploy** for the reviewed commit (or approve the Blueprint's
   initial deploy). Check build success, health status and the generated HTTPS URL.
   The checked-in autoDeployTrigger is off. Do not enable deploy-on-push implicitly.
6. From an external desktop and mobile browser, open that URL and perform the
   post-deployment acceptance checks below. Do not announce availability until
   they pass. If they fail, do not hand the URL to evaluators; inspect status,
   public origin and limits without enabling input logging or publishing secrets.
7. Only after external verification, place the HTTPS URL in the project/demo
   materials. Official Space Apps Project Tab submission remains a separate,
   manual owner action. This deployment does not submit the project or confer
   NASA endorsement, operational use or clinical validation.

## Local Docker and verification

```sh
docker build -t ares-public-demo:local .
docker run --rm --name ares-public-local --read-only \
  --tmpfs /tmp:rw,noexec,nosuid,size=16m --cap-drop ALL \
  --security-opt no-new-privileges --memory 512m --cpus 2 \
  -p 127.0.0.1:18000:10000 -e PORT=10000 \
  -e ARES_PUBLIC_ORIGIN=http://127.0.0.1:18000 ares-public-demo:local
```

The cloud development proxy uses a private CA not trusted inside stock base
images. A session-only Dockerfile can mount the trusted combined CA bundle as a
BuildKit secret for npm NODE_EXTRA_CA_CERTS / pip PIP_CERT. Do not disable TLS,
change checksums, bake a session CA into the image or copy proxy credentials.
Render's normal trusted Internet build uses the checked-in Dockerfile unchanged.

With the container healthy, in a separate terminal from repository root:

```sh
.venv/bin/python -m pytest -q
npm --prefix frontend test
npm --prefix frontend run build
ARES_PUBLIC_TEST_URL=http://127.0.0.1:18000 .venv/bin/python -m pytest -q tests/test_public_demo.py
cd frontend
ARES_PUBLIC_TEST_URL=http://127.0.0.1:18000 npm run test:public:browser
```

The existing HTTP/Vite integration suite is a **development** check: it expects
ports 8000+5173 and local CSV/research routes, so it must not be pointed at public
mode. Public checks are separate and intentionally assert those routes are absent.
The workflow includes a Docker/public test step but does not deploy to Render.

## External acceptance after owner deploys

Run the public suites with ARES_PUBLIC_TEST_URL set to the **actual HTTPS URL**,
then manually verify a browser outside the cloud environment:

- Valid HTTPS, UI/assets from the same origin, public warning readable on desktop
  and 390 px mobile; no horizontal overflow or console/CSP errors.
- Stable, heart-rate-shift and incomplete scenarios; unchanged canonical findings;
  incomplete data withholds trend interpretation in charts, Copilot and Wellness.
- Attested fictional check-in, updated raw values and timeline, Copilot explanation,
  NASA literature link, manual review state and local comprehensive JSON download.
- No research/CSV controls, API docs or file/admin routes. Cross-origin requests,
  oversized/malformed JSON and bad attestations rejected without input reflection.
- Requests stay local to the app origin except explicit user navigation to cited
  literature. No real health data is used to test this demonstration.

An external HTTPS deployment/browser check cannot be performed before an owner
creates and supplies the public service URL. Local container success is not proof
of Render availability. See RENDER_VALIDATION.md for the actual run evidence.

## Release boundaries

Root project licensing and generated-artwork/dependency rights remain separate
owner review; no license is invented here. This branch uses current main docs,
not the unmerged audit changes. Only public HTTP/deployment/presentation boundaries
change; synthetic analysis, illustrative thresholds and deterministic evaluation
modules remain unchanged.
