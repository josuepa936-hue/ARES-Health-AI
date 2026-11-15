# ARES v1.5 — Review report and audit consistency (Issue #21)

## Change summary
The **comprehensive** report is an auditable, fictional session export. Its
`review_state` and `fictional_review.review_state` now share the exact same
four-state value: `PENDING_REVIEW`, `IN_PROGRESS`,
`AWAITING_AUTHORIZED_REVIEW`, or `DOCUMENTED`.

A distinct `legacy_review_state` field represents only the older binary
summary. `legacy_review_state_semantics` warns that this is *not* the current
workflow status. In particular, an `IN_PROGRESS` case is not silently
represented as the current state `Pending review`. Existing **standalone**
`POST /api/review` reports still expose the original `Pending review` /
`Reviewed in demo` values and continue to use the 1.0-demo report schema.

## Schema versions versus software version

- `application_version`: `1.5`, from `src/ares_health/version.py`,
  in the root review report, timeline, API docs and status route
- `copilot_application_version`: `1.5`, sourced from that same constant
- `schema_version`: `1.0-demo` (original JSON report schema identifier)
- `copilot_schema_version`: `1.5-demo` (integrated copilot extension)
- `mission_timeline.schema_version`: `1.0-timeline` (timeline data schema)

Updating the software version **does not** imply that these preexisting
document-format schema versions should be changed. Copilot context hashes are
over a canonical snapshot and timeline; version changes may correctly change
the context hash, requiring a new briefing. Old exported reports remain
historical artifacts and must not be rewritten.

## Audit times and user control

Every **newly recorded** action in the React workflow receives
`recorded_at_utc: new Date().toISOString()` at the moment it is clicked.
This timestamp comes from the **user's device clock**, is not server-verified,
and must not be described as flight or institution-grade audit evidence.
It is unrelated to simulated observation dates, which may be future dates.

The Python request model validates UTC ISO-8601 timestamps ending with
`Z`, supports up to microseconds, and rejects descending event dates. The
audit log remains ordered by contiguous sequence numbers. Duplicate
millisecond UTC times are allowed for multiple fast clicks.

For older v1.5 clients that omit the field, the endpoint does not invent a
time: it leaves the field absent and sets
`fictional_review.audit_timestamps_complete = false`. The
`audit_timestamp_source` text documents the origin of captured times.
Data are never saved server-side; reload still resets the audit.

## User-acceptance test

1. Open local ARES and select Stable observations.
2. Enter fictional note `cardiovascular` and click Record.
3. Check source/units, change state to IN_PROGRESS.
4. Attest all entries are fictional and build comprehensive JSON.
5. Confirm root and nested `review_state` are both `IN_PROGRESS`;
   `legacy_review_state` exists as a compatibility-only field.
6. Confirm three audit events with contiguous sequences 1, 2, 3 and
   `recorded_at_utc` strings supplied by the device clock.
7. Confirm unchanged `assessment: NO_DEMO_RULE_TRIGGERED`,
   `clinical_authorization: false`, 21 synthetic observations and
   no change to comparison thresholds, NASA research or MIT-BIH.
8. Confirm `application_version: 1.5` throughout; schema versions still
   reflect independently versioned formats.

**Limitations:** this is demonstrator-only, no clinical reliability,
autonomous health assessment, server-authenticated timestamp, medical
personnel contacted, or NASA operational endorsement.
