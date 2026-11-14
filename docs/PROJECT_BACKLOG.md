# Work plan — 2026-11-10 to 2026-11-15

## Before event: research + coordination only

- [ ] Verify team page, event, and chosen challenge.
- [ ] Agree on MVP and assign 1–3 primary roles.
- [ ] Check NASA resources and add carefully attributed scientific references.
- [ ] Confirm working language, repo permissions, file naming, and communication channel.
- [ ] Agree on how pre-event scaffolding will be disclosed, subject to current rules.

## Saturday Nov 14: build

**P0 (must finish)**
- [ ] Generate clearly tagged synthetic daily records for 6 scenarios.
- [ ] Add CSV validation (timestamps, units, missingness, duplicates).
- [ ] Add chart page for heart-rate and sleep trends.
- [ ] Add explainable relative-change flags (illustrative, documented).
- [ ] Include always-visible data provenance + non-medical disclaimer.

**P1 (if ahead of schedule)**
- [ ] Add activity and symptom logs.
- [ ] Add local export of observation and review history.
- [ ] Add accessibility pass for contrast and label clarity.

## Sunday Nov 15: test + submit

- [ ] Run S1–S6 scenarios and document actual results.
- [ ] Execute offline demo and sanity checks.
- [ ] Write a short English project story: problem, data, method, demo, limitations.
- [ ] Capture screenshots / 90–120 second demo video (as permitted).
- [ ] Add credited NASA resources, code repo, documentation, team credits.
- [ ] Complete official Project Tab submission before **11:59 PM local time**.

## De-scope order when solo

1. Drop ML (it is optional, not a requirement).
2. Drop SQLite and real-time sensors.
3. Keep only 2 metrics: resting heart rate and sleep duration.
4. Keep 4 test scenarios, provenance, charts, readable flags.
5. Prioritize submission over polish.

## Team roles

- Team lead / science and data (you): scope, literature, QA, presentation.
- Developer: app integration and code tests.
- Data/UX collaborator: synthetic scenarios, visualizations and clarity.

One person may cover multiple roles; avoid assigning responsibility to people who have not agreed to join.
