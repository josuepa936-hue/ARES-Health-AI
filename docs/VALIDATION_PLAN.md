# Validation plan — non-clinical prototype

## Objectives

Evaluate software behavior, robustness, and explainability using synthetic fixtures. Do **not** treat synthetic test results as estimates of sensitivity, specificity, prediction accuracy, or health outcomes in astronauts.

## Scenario matrix (fixtures to create during the event)

| ID | Synthetic scenario | Expected software behavior |
|---|---|---|
| S1 | Stable, complete observations | show charts, explain no rule-based changes; not 'medically healthy' |
| S2 | Consistent shift from that profile's illustrative heart-rate baseline | flag deviation for *review* with the actual comparison shown |
| S3 | Multi-day shortened sleep relative to an illustrative baseline | explain sleep trend with reference interval and uncertainty |
| S4 | Missing data + duplicated timestamps | conspicuous data-quality warning; never silently fill with reassuring values |
| S5 | Physically impossible value / incorrect unit | reject or quarantine record and explain data issue |
| S6 | Insufficient baseline observations | mark baseline unavailable and withhold trend-based alert |

## Test categories

**Unit tests:** parsing, required columns, duplicates, missingness, time ordering, baseline availability, rule explanations.

**Integration tests:** input CSV -> validated records -> visualization -> report.

**Manual UX tests:** a reviewer can tell whether data are synthetic, what triggered a flag, and what the software cannot infer.

**Offline test:** app runs on localhost after dependencies are installed, with internet disabled; no external APIs are needed.

## Acceptance thresholds (engineering only)

- All seeded fixtures have expected deterministic behavior (pass/fail).
- No scenario with a missing baseline is given a falsely confident trend assessment.
- Every review flag includes the metric, time, baseline or reference, and rationale.
- No personal or human-derived confidential data enter the sample repository.
- No false claim that tests establish medical efficacy or astronaut suitability.

## Evidence to save

- Local screenshots/video (captured during the event)
- Reproducible fixture generator and tests
- `pytest` test results
- Known limitations and future validation needs
