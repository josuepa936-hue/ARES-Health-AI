# ARES Health AI modules — v0.5

- `synthetic.py`: deterministic fictional daily scenarios.
- `validation.py`: shared schema, provenance, identity, UTC chronology, daily cadence and measurement sanity checks.
- `analysis.py`: validated reference/recent comparisons and explainable review flags; re-exports `quality_issues` for compatibility.
- `review.py`: revalidated deterministic JSON reports, review state and fictional notes.

No CSV ingestion, database, real telemetry or clinical prediction is implemented. See `docs/ARCHITECTURE.md` for contracts, units, unchanged demonstration thresholds and limitations.
