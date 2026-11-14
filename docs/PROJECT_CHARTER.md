# Project charter — ARES Health AI

## Problem

Long-duration spaceflight changes the operational context of health monitoring: altered gravity, isolation, limited resources, and potentially delayed communications. Astronauts need tools to **observe their indicators, detect data-quality problems, understand trends, and know when to follow established procedures**.

## Intended user / context

An astronaut reviewing a health-and-wellness dashboard on a local mission device. Secondary audience: a mission support or medical team reviewing a report. Both roles are **conceptual**; this is a student hackathon prototype and not an operational crew system.

## Product statement

> An offline-capable, transparent health trend monitoring demonstrator using synthetic records and reproducible scenarios to support review—not medical diagnosis—during long-duration missions.

## Core user story

"As a crew member, I want to see whether my logged indicators have changed from my own previous pattern, understand data gaps, and receive a clear reason to review a measurement or a pre-defined protocol."

## MVP boundary

**In scope:** CSV-based synthetic daily logs; quality flags; trends; baseline comparison; explanation of deviations; contextual 'review data / consult procedure' steps; exportable evidence of tests.

**Out of scope:** medical diagnosis; treatment recommendations; clinical risk prediction; claims of astronaut validation; live wearable integrations; radiation dosimetry; mental-health diagnosis; medical certification; inaccessible NASA datasets.

## Proposed indicators

- Daily resting heart rate (bpm), *if measurement context is consistent*.
- Sleep duration (hours) and self-reported sleep quality (optional).
- Physical activity duration (minutes), with appropriate caveats.
- Symptom report as a qualitative flag, never an automatic diagnosis.

## Success criteria (engineering, not clinical)

1. A local user can load an explicitly synthetic data file and view a trend chart.
2. Incomplete, malformed, duplicated, or implausible values are flagged, not silently accepted.
3. Every generated alert names the input, rule, baseline, and uncertainty/limitation.
4. At least four reproducible synthetic scenarios produce documented expected application behavior.
5. The demo functions without a cloud login and includes a clear non-medical disclaimer.
6. The public project materials explain exactly which parts were implemented during the hackathon.

## Research questions

- Can the software distinguish data-quality failures from actual changes in an individual's logs?
- Can a user understand a review flag and its basis within a few seconds?
- What information can be reported when no adequate personal baseline exists?
- Which NASA research findings justify the design, without over-claiming clinical performance?

## Ethical and safety guardrails

Use synthetic data. No real person should make health decisions using the prototype. Missing data must never be interpreted as 'healthy'. Relative changes are not equivalent to diagnosis. Formal medical assessment would require expert review and validation beyond the hackathon.
