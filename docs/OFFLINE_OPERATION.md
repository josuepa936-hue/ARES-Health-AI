# ARES v1.5 — independent online and offline demonstration modes

Both modes use the same unchanged synthetic Python evaluation engine. Offline
means a **prepared local server plus browser**, not a cached copy of Render.
This is an experimental fictional-data prototype, not medical equipment,
NASA-authorized software or evidence of flight operational readiness.

| Mode | Where UI / API run | Connectivity during use |
|---|---|---|
| ONLINE | Render serves compiled React and FastAPI together over HTTPS, with ARES_PUBLIC_DEMO=1 | The visitor needs Internet access to the remote server |
| OFFLINE | A prepared computer serves compiled React and FastAPI on 127.0.0.1, with ARES_PUBLIC_DEMO unset/0 | No external connection is needed for the core; loopback and the local Python server must remain available |

The public Render configuration and entrypoint are unchanged. The offline test
image described below is a **separate test harness**, never a Render deployment
image. Do not turn off protected public mode on an Internet-facing service.

## Prepare before disconnecting

Install Python 3.12 and compatible Node (Node 24 verified, minimum >=22.12), Git
and a browser. From the existing checkout, on Linux:

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-deploy.lock
cd frontend
npm ci
VITE_API_BASE_URL= npm run build
cd ..
.venv/bin/python -m pytest -q
```

Downloads, installation and compilation require connectivity initially. Retain
`.venv/`, `frontend/dist/` and the source tree. Node/npm and node_modules are only
needed to rebuild/develop; the compiled UI does not require a live Node server.
The explicit empty VITE_API_BASE_URL in the build selects same-origin /api;
never prepare the offline bundle with a Render/cloud API URL override.

Windows uses `py -m venv .venv` and `.\.venv\Scripts\python.exe` instead. After
installing Python requirements and running `npm ci` / `npm run build` in frontend/,
`.\start-ares.cmd --skip-build` serves the prepared UI without rebuilding or
installing. Confirm there is no remote VITE_API_BASE_URL in environment or local
Vite configuration before building. These Windows instructions follow the
existing launcher. Six Windows manual checks are now reported as passed by the
owner; the independent isolated execution was on Linux. See
[the separate acceptance records](OFFLINE_VALIDATION.md).

## Run after disconnecting

With Internet disabled, start from repository root:

```sh
ARES_PUBLIC_DEMO=0 ARES_RESEARCH_ENABLED=0 .venv/bin/python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/` in the local browser. On Windows set
`$env:ARES_PUBLIC_DEMO="0"` and `$env:ARES_RESEARCH_ENABLED="0"`, then run
`.\start-ares.cmd --skip-build`. Keep the local process running. Disconnecting
Wi-Fi does not normally disable loopback. A browser's DevTools “Offline” switch
can block **localhost too** and is not equivalent to disconnecting the computer's
Internet interface while keeping its local server reachable.

Verify stable/changed/incomplete scenarios, attest a fictional check-in, inspect
charts and timeline, ask the deterministic Copilot “What changed?”, expand
Wellness and export a comprehensive fictional JSON report. All mission values
and dates are simulated. Reload resets transient review/conversation state;
reports persist only when explicitly downloaded by the user. There is no automatic
cloud upload, synchronization queue or clinical authorization.

## What is bundled, and what is not

- React/TypeScript, Recharts, lucide icons, CSS and the decorative 2D image are
  compiled into local frontend/dist assets. There is no mandatory CDN, web-font
  download, remote JavaScript loader or external rendering service in core use.
  Fonts use system fallbacks; appearance can vary by OS.
- The default adapter uses same-origin /api. Python generates fictional scenarios,
  validates check-ins, evaluates unchanged illustrative rules, constructs timelines
  and JSON, and computes explanations locally.
- Copilot is deterministic and not an LLM. It does not invoke an AI API, require
  a model download, access a cloud inference service or need an API key at runtime.
- Wellness's educational summaries and NASA citation URLs are already in the
  repository. Displaying these is offline; following a citation to read the live
  NASA/CSA publication needs connectivity. No offline article archive is bundled.
- Optional NASA OSDR metadata/sample fetches need Internet. When unavailable, the
  API returns 503 and the research view explains the failure without inventing
  study records. Return to the mission view to continue the local session.
- MIT-BIH acquisition requires connectivity and separate source/license review.
  Its research endpoint reads a bounded **previously prepared local artifact**;
  that could be read offline if independently prepared/verified. No real artifact
  or public-record performance score is bundled or validated by this offline test.
- No real astronaut records, live telemetry or operational Earth/spacecraft link
  is involved in this demonstration.

## Reproducible disconnected tests

Preparation needs Internet and Docker. First build the protected deployment image
from Dockerfile, as documented in [the Render guide](RENDER_PUBLIC_DEMO.md), then
build the **test-only** image with its own installed Chromium/Node/test tools:

```sh
docker build -t ares-public-demo:local .
docker build -f offline_checks/Dockerfile -t ares-offline-validation:local .
docker run --name ares-offline-check --network none --shm-size=256m ares-offline-validation:local
mkdir -p offline-results
docker cp ares-offline-check:/results/. offline-results/
docker inspect --format '{{.HostConfig.NetworkMode}}' ares-offline-check
docker rm ares-offline-check
```

Do not use --rm before copying the evidence. If a run fails, copy /results and
inspect the logs; do not label it passed. Use a different container name or remove
only your prior test container when repeating. The test image explicitly launches
local uvicorn rather than the protected Render entrypoint.

The test runner refuses to run unless **lo is the only network interface** and
an outbound TCP probe fails with **ENETUNREACH**. It starts a fresh local server
only after isolation, executes a real HTTP pytest target, then starts Chromium
with fresh contexts. Browser routing also rejects non-loopback requests; core
requests are not mocked. HTTP cache/service-worker installation is not relied on
for startup. The browser records attempted remote requests and exercises actual
local JSON downloads, research failures, recovery and page reloads.

The HTTP target is `offline_checks/http_workflow.py`; it is run explicitly, not
silently skipped or counted in the normal pytest regression suite. The browser
target is `frontend/offline-e2e/workflow.spec.ts` with
`frontend/playwright.offline.config.ts`. `npm run test:offline:browser` is intended
inside the prepared isolated harness; its interface check fails outside it.
GitHub Actions includes preparation followed by docker run --network none, but
no remote CI result is claimed until that workflow actually runs.

For this managed cloud's private TLS proxy, build preparation used the existing
trusted CA bundle as a temporary BuildKit secret, never disabled verification.
The test Dockerfile accepts optional secret id `proxy_ca`; the original protected
Dockerfile's session trust adaptation is documented in the Render guide. No trust
bundle, credentials or host network interface is needed during the disconnected run.
The private proxy is unreachable too. No host firewall/global network setting is changed.

See [offline validation evidence](OFFLINE_VALIDATION.md) for actual results and
[short English explanation](OFFLINE_TECHNICAL_BRIEF_EN.md) for presentation copy.

## Limits that must accompany a demo claim

Opening a Render URL once does **not** make it offline-capable. There is no PWA,
service-worker offline cache, browser-hosted Python engine or serverless fallback
that replaces a lost Render connection. Browser memory/cache cannot substitute
for the FastAPI process. To demonstrate during an Internet interruption, switch
to the independently prepared local copy. The local computer, installed packages,
compiled assets, browser and loopback interface must remain usable. Local hardware,
OS, dependency failures and clinical validity are separate questions, not solved
by this connectivity test.
