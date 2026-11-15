# Offline demonstration validation — ARES v1.5

Tested November 15, 2026, on `feat/render-public-demo`, based on
`e7e3a7ca498cc480e483bbdd934d453bf67c81a9`. Only documentation, offline test
harnesses, test commands and CI steps were added for this requirement. The
biomedical algorithms, thresholds, evaluation engine, production Dockerfile,
Render configuration and public-mode boundary are unchanged. Main and the
separate audit branch are not modified.

## Consolidated acceptance record — November 15, 2026

Two separate evidence tracks are retained here:

1. **Prior agent-executed Linux automation:** the disconnected-container HTTP and
   functional Chromium checks below, with actual artifacts inspected at that time.
2. **Owner-reported Windows manual acceptance:** the supplied report documents
   six checks as passed. This update transcribes that evidence; it is not a new
   independent Windows audit or a rerun of the earlier automated tests.

Source: [owner-provided report and provenance](evidence/OWNER_OFFLINE_REPORT_2026-11-15.md).
The exact Windows version, browser/version, Python/Node versions and local source
commit were not specified. Do not infer the local Windows commit from the separately
reported Render deployment commit. No Windows network trace, independent witness
or Windows-generated JSON file was supplied for inspection. Screenshots mentioned
in the report were not reattached or independently inspected in this update.
These limits do not erase the separate, already-executed Linux isolation evidence.

### Windows manual acceptance — reported by the owner

Reported date: **November 15, 2026**. Environment: **Windows / PowerShell**,
preinstalled Python dependencies and compiled React/Vite. The owner reports
`npm.cmd ci` and `npm.cmd run build` completed online, then launched
`start-ares.cmd --skip-build` at **http://127.0.0.1:8000/**. Internet was disconnected
and the local interface loaded/reloaded while the FastAPI process remained running.
The report mentions a build screenshot with 2,005 transformed modules; this is a
reported preparation detail, not newly inspected build evidence.

| ID | Offline manual check described in the supplied report | Recorded result | Evidence class |
|---|---|---|---|
| OFF-01 | Switch stable / heart-rate-shift synthetic scenarios; inspect visualizations | PASS — owner reported | Manual, Windows |
| OFF-02 | Load incomplete records; withhold interpretation and show DATA_QUALITY_BLOCKED | PASS — owner reported | Manual, Windows |
| OFF-03 | Use deterministic Copilot to explain the selected scenario | PASS — owner reported | Manual, Windows |
| OFF-04 | Review Mission Wellness educational/explanatory content | PASS — owner reported | Manual, Windows |
| OFF-05 | Submit fictional check-in and generate a review report | PASS — owner reported | Manual, Windows |
| OFF-06 | Download JSON and inspect observation and review/audit content | PASS — owner reported | Manual, Windows |

**Owner-reported outcome: 6/6 passed.** This supports acceptance of the described
core local demonstration workflow, not every feature or every possible failure.
The owner report alone does not establish absence of attempted external requests;
the network-isolated automation below is a separate Linux evidence track.

### Two modalities and scoped closure

- **OFFLINE:** prepared local React + FastAPI/Python, loopback only, local server
  running. Dependency installation/builds happen beforehand. Manual Windows
  acceptance is owner reported; automated Linux isolation was actually executed.
- **ONLINE:** https://ares-health-ai.onrender.com/ is the separate Render demo.
  Owner reports deployment Live from e7e3a7c and anonymous/incognito access and
  core functions. See [public acceptance record](RENDER_VALIDATION.md). The hosted
  URL still requires Internet; no PWA/browser-only offline backend is implemented.

Documentation now records technical acceptance **within this demonstration scope**.
It does not certify medical efficacy, security completeness, arbitrary platforms,
flight readiness or official Space Apps submission. See the
[compliance and handoff matrix](TECHNICAL_ACCEPTANCE_MATRIX.md).

## Preserved prior automated evidence

The following sections retain the previously executed results; they were not
reclassified as Windows tests or rerun merely to document the owner's report.

## Actual isolation and preparation

Python dependencies, Node/npm packages, compiled React and system Chromium/fonts
were installed **before** disconnecting the test. The runtime was started with
`docker run --network none`, no port mapping, and ARES_PUBLIC_DEMO=0. The local
server and a fresh browser both ran inside that same isolated container, using
only 127.0.0.1:8000. No frontend or API responses were mocked. No package install
or download occurred during the disconnected run.

Evidence collected:

- Docker network mode: **none**; container exited **0**.
- `/sys/class/net`: **lo only**; `/proc/net/route`: header only, no external route.
- Outbound TCP probe: **OSError 101 / ENETUNREACH**.
- Local API status: **local-development**, not public-demo.
- Actual served HTML lacks the public-mode marker; local research navigation is
  present, independently of Render's protected UI configuration.

A shell `unshare` probe was unavailable because uid_map is read-only in this
managed environment. Docker provided the required isolated network instead;
no host firewall, proxy, global network setting or credential was changed.
An initial Docker start failed **before tests ran** because the VFS image store
exhausted disk space. Only obsolete images/cache records created by this task
were removed; after recovering space the isolated run completed successfully.
These preparation failures are resolved, not counted as passing tests.

## Automated HTTP test: 8 passed

Explicit target: `offline_checks/http_workflow.py`, executed in the disconnected
container, not included in or silently skipped from the normal pytest count.

- Only loopback exists and outbound networking is physically unavailable.
- Compiled entry page, JavaScript and CSS load locally; entry resource references
  contain no remote URL, and CSS has no external import/font/resource dependency.
- All four scenarios return expected canonical states and 21 observations;
  timelines match assessments, with no trend interpretation for incomplete data.
- Fictional check-in, Copilot answer, three NASA-cited Wellness topics and
  comprehensive report complete through actual HTTP.
- The report contains 21 fictional observations, DOCUMENTED review state and
  `clinical_authorization: false`.
- With research explicitly enabled, NASA catalog/sample endpoints and missing
  MIT artifact return **503**, only error detail, no fabricated study/benchmark.
  The main scenario remains available afterward.

## Functional real-browser test: 2 passed

Explicit target: `frontend/offline-e2e/workflow.spec.ts`, Chromium at **1440 px**
and **390 px**, each with a fresh context inside the network-isolated container.
This is an automated functional UI walkthrough, not a manual Wi-Fi-disconnection
exercise or physical mobile-device certification.

Both runs performed cold navigation to local React, changed scenarios, viewed
Recharts and the local body illustration, submitted an attested fictional check-in,
inspected timeline events, asked the deterministic Copilot a question, read
Wellness summaries/NASA links, manually documented review and downloaded the
actual comprehensive JSON. Both verified **21 observations**, DOCUMENTED and
no clinical authorization in the downloaded file.

Each run opened unavailable NASA and MIT research views, observed the error
without substituted results, then returned to the unchanged fictional session.
A browser reload also succeeded locally and reset to the normal stable scenario.

Network observation files for both widths recorded:

- **0 attempted external browser requests** (including core assets/fonts/AI/cloud).
- **0 JavaScript page errors**.
- **2 unavailable research responses** during each browser research detour.
- Successful reload, local JSON export and no document horizontal overflow.

Browser routing rejects remote requests as defense in depth; Docker's OS-level
network isolation independently covers Chromium, Node and backend traffic.
NASA may attempt its optional outbound lookup on explicit selection, but no
external connection is possible; the error is an honest unavailable result.
The browser has no need to retrieve literature pages merely to show their links.
Captures and exported fictional JSON were read back after the run.

## Additional regression checks

- Normal Python suite: **410 passed**, one existing Starlette/httpx deprecation
  warning. Public-mode checks remain included and passing.
- Normal frontend suite: **62 passed**.
- TypeScript/Vite production build: passed.
- New YAML/TypeScript harness syntax parsed by local tooling; diff check passed.
- CI now prepares dependencies while connected and runs the isolated container
  with --network none. No new remote CI result is claimed before pushing/running.

## What this does and does not establish

This demonstrates the **prepared local React/FastAPI/Python workflow** continuing
without external communication, including a cold server/browser start. Mandatory
CDNs, downloaded web fonts, AI APIs and cloud services were not needed. System
fonts, code, compiled images/chunks and Python libraries were already on disk.

It does not make the Render URL available offline. There is no implemented PWA,
service-worker backend substitute, browser Python engine or automatic failover
from Render. If Internet is lost, an evaluator using only Render loses its
server connection; use the independently prepared local installation.

Installation/builds and obtaining official research files require connectivity.
Following NASA/CSA/PhysioNet citation links also requires it. MIT artifacts may
be readable locally if independently prepared and verified, but none was bundled
or benchmarked here. The optional NASA/MIT research failures do not block the
fictional mission workflow or authorize fabricated research data.

Local server availability, power, hardware, OS/browser compatibility and dependency
integrity remain prerequisites. Windows now has the separate owner-reported manual
acceptance above; Windows and physical phones were not independently tested by
this agent. Session state remains transient; only user-initiated exports are saved.
No clinical validation, actual communications-to-Earth experiment, live astronaut
monitoring, flight qualification, NASA endorsement or official submission is claimed.

See [offline operation/reproduction](OFFLINE_OPERATION.md) and the
[English technical brief](OFFLINE_TECHNICAL_BRIEF_EN.md).
