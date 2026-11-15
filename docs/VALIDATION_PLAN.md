# Software validation — v0.5

All fixtures are synthetic. Tests assess software behavior, not medical accuracy or astronaut health outcomes.

Run from the repository root:

```sh
python -m pytest -q
```

## Implemented automated checks

- Stable observations produce no demonstration flags; seeded generation is repeatable.
- Heart-rate and sleep changes produce explanations containing means, direction, UTC comparison intervals, units and the inclusive illustrative threshold.
- Both directions and values below, exactly at and above the 12 bpm / 1.5 hour thresholds are covered.
- Empty dataframes, missing or duplicate columns, invalid/missing/numeric timestamps, duplicate instants, reversed chronology, daily gaps and intraday observations block interpretation.
- Missing, nonnumeric, boolean, infinite, negative and out-of-range measurements block interpretation.
- Blank, missing or mixed crew identities and unsupported/missing provenance block interpretation.
- Valid numeric strings, supported sanity-bound endpoints and UTC-normalized ISO timestamps are accepted.
- Short valid series cannot form overlapping baseline/recent windows: reports indicate insufficient data and contain no flags.
- Validation and analysis preserve source dataframes.
- JSON reports independently revalidate input, suppress stale caller flags, remain deterministic and serializable, and validate review-state/note constraints.
- Streamlit AppTest exercises all four scenarios, quality/flag counts, Mission Review Center inputs and both export controls.

## Limits and further checks

The application exports CSV; CSV import and an ingestion pipeline are not implemented. Export-control presence is automated; browser download interaction and visual layout remain manual checks. The software does not infer physical units from values or validate the authenticity of a synthetic source label. Offline browser behavior and real telemetry are outside this automated suite. No clinical evidence or medical performance measures are claimed.

## v0.5 verification result

On Python 3.12, `python -m pytest -q` completed with **64 passed**. Dependency consistency (`python -m pip check`) and `git diff --check` also passed. These are software checks using fictional records only.

## v1.2 optional research checks

Offline unit tests cover inclusive one-to-one sample matching, TP/FP/FN and
undefined ratios, annotation selection/boundaries, missingness, wrong duration/fs,
flat/dropout/mains/amplitude exclusions, strict JSON and endpoint opt-in/loopback/
record/artifact bounds. Optional WFDB/NeuroKit tests write only self-contained
synthetic records, exercise calibration/checksum metadata and real deterministic
processing, and verify HTTP does not trigger acquisition/detection. Frontend
checks cover research provenance, abstention, displayed metrics/markers, retry,
cancellation and mission-mode isolation. Existing suites remain required.

A measured benchmark against the official public record is a **separate check**;
it is currently blocked by PhysioNet access. Dataset-license review is also pending.
No offline fixture result is a clinical or public-record performance claim.
