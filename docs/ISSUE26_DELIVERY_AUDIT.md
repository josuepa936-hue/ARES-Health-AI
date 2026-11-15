# Issue #26 — v1.5 delivery documentation audit

## Baseline and verified scope

Audited main `aadd7981eb3e6a91f06d7dec43906b56a1b41a73` on November 15,
2026, then created `docs/issue-26-delivery-audit` from fetched origin/main.
Only Markdown documentation changes are intended. No biomedical calculation,
threshold, frontend behavior, API/JSON contract, dataset integration, dependency
version, asset or Git history is changed.

| Finding verified on main | Correction |
|---|---|
| README opens with v1.3 feature-branch status | Current v1.5 single-server entry; prior README retained under history/ |
| Frontend README denies anatomy and presents old counts without context | Decorative generated 2D illustration distinguished from validated/3D anatomy; historical v1.1 counts labeled |
| Validation plan v0.5 says CSV import is absent | Current scope matrix and separate HTTP/browser prerequisites |
| Primary demo is 3–4 minutes / v1.3 | Under-30-second storyboard/narration; long walkthrough retained as supplemental |
| Scientific evidence v0.7 denies OSDR ingestion globally | Mission synthetic-only policy separated from optional OSD-87 mouse-study metadata/sample access |
| Architecture/API describe obsolete primary UI and future research branch | Current main status, canonical version and independently versioned schemas |
| API text says NASA redirects are refused | Document existing bounded two-hop approved NASA/S3 handling and 12/30-second timeouts from nasa_osdr.py |
| AI disclosure ends with pending integration statements | Current integrated status plus recorded tool/code/artwork attribution, retaining history |
| npm version 1.1.0 differs from APP_VERSION 1.5 | Explain tooling vs application version; manifests/lockfile untouched |
| No root LICENSE | Owner requested a separate licensing task; no license invented |

The referenced PNGs exist as binary files under frontend/screenshots; no missing
image claim is based on a text decoder error. Fresh Windows instructions were
checked against start-ares.cmd/start-ares.ps1; execution here is Linux only.

## Plain-English project summary for owner review

ARES Health AI is a local demonstration for reviewing fictional astronaut daily
observations. It validates synthetic check-ins and CSV files, explains illustrative
changes through charts and timelines, and exports reproducible JSON. Its offline
deterministic Copilot and Wellness guide provide research context. Independent
optional views explore terrestrial ECG and NASA mouse-study sources. It is not
a medical device, clinical validation, live astronaut monitoring or NASA endorsement.

## Organizer and history evidence

The public GO Team answers in [#1991](https://github.com/nasa/spaceapps/discussions/1991),
[#2199](https://github.com/nasa/spaceapps/discussions/2199) and
[#1813](https://github.com/nasa/spaceapps/discussions/1813) were read during this
audit: less-than-30-second video or max-seven-slide deck; separate public demo
and project links; minimum two Universal Event members for Global Judging,
maximum six; actual project work should start during the official hackathon.
These answers do not verify this team's registration, timezone or submission.

Git history records the initial scaffold `c4c117f` at November 13, 2026,
23:00:06 -06:00. Inspection shows a Streamlit **planning placeholder** stating
that no health metrics are processed and a namespace placeholder. Functional
synthetic.py / analysis.py commits `6509cb0` / `81bc1e1` record November 14,
13:13:44 / 13:13:46 -06:00. These are repository timestamps and content evidence,
not independent proof of authorship, work start time or event eligibility.
History is preserved; the owner must disclose prior preparation accurately and
seek organizer clarification if necessary.

## Verification

See the final local results below and [validation scope](VALIDATION_PLAN.md).
New local run on this branch: **377 Python tests passed** (one existing
Starlette/httpx deprecation warning), **62 frontend tests passed**, and
TypeScript/Vite production build passed. **19 live HTTP checks** through Vite
and **6 compiled-app Chromium checks** (console/copilot suites) also passed.
Dependency consistency and `git diff --check` passed. The 44-word narration is estimated at
22 seconds at 120 words/minute; the complete storyboard targets 27 seconds.
No finished recording was timed. All **60 local Markdown link targets** in changed/new documentation were checked
for existence with no missing target. The full browser suite, Python 3.13 matrix,
optional research-library integration and fresh Windows install were not rerun.

The three GO Team pages and Issue #26 were accessible via public GitHub HTML.
Direct NASA and PhysioNet URL checks returned proxy CONNECT 403; these are
network restrictions, not evidence of missing scientific pages. No new live
scientific-source or public-record performance verification is claimed.

Previous onboarding results and the Issue's account of PR #25 CI are separate
from this branch's new local run. No current GitHub Actions result is asserted.

## Human handoff

The [delivery checklist](SUBMISSION_CHECKLIST.md) remains unchecked: verify team
size/event timezone, public links, source and asset terms, license decision and
Project Tab confirmation. The short script is a plan, not a recorded/timed video.
No NASA Space Apps submission has been verified or performed by this audit.
