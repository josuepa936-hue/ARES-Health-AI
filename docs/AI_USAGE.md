# AI usage disclosure — ARES Health AI

OpenAI ChatGPT was used to assist with software architecture, generating and revising prototype code, and writing technical explanations. The team is responsible for reviewing, testing, attributing, and validating all code and scientific claims. Sample datasets were generated with deterministic Python code; they are entirely synthetic and do not represent measurements from astronauts or NASA systems.

All thresholds used by the demonstration are illustrative engineering parameters, not evidence-based clinical or aerospace medical cutoffs. The system does not diagnose conditions or replace medical protocols.

At submission, review and expand this disclosure to reflect actual tools and materials used.

## Version 0.5 implementation

OpenAI Codex assisted with repository inspection, the shared synthetic-data validation module, trend explanations, defensive report generation, dashboard regression checks, automated tests and documentation. Validation used deterministic fictional fixtures and the repository's pytest suite, including Streamlit AppTest. No real patient or astronaut information was used. Human reviewers remain responsible for approving the implementation and checking its limitations before merging; test results establish software behavior only.

## Version 0.6 implementation

OpenAI ChatGPT assisted with the strict synthetic CSV ingestion module, validation tests, UI integration, and documentation. The importer deliberately rejects data lacking a fictional identifier, explicit synthetic provenance, valid UTC dates, or complete measurements. Each uploaded file also requires a human attestation. This is a software proof of concept rather than an independent verification of the synthetic provenance or clinical usefulness.

## Version 0.7 implementation

OpenAI ChatGPT was used to help summarize and structure official publicly available NASA/Canadian Space Agency research context, draft conservative non-clinical explanatory text, create new UI sections, write automated checks and prepare a narration script. The included links are official organizational sources, not data ingested or validated by NASA on behalf of this prototype. Human project authors must confirm source alignment, run the tests and approve the text before submission.

## Version 0.9 API foundation (experimental branch)

OpenAI ChatGPT helped organize a domain-service-API split, write a local FastAPI HTTP adapter, design strict synthetic CSV upload checks, prepare API regression tests and create architectural documentation. GitHub Actions was configured to test Python 3.12 and 3.13. Figma Make and Claude were explored for visual interface concepts, but **their designs have not been integrated into this software release**. All code and medical claims require human review. No new medical algorithms, real astronaut records or medical treatment recommendations are implemented.

The v0.9 backend additionally reuses a previously developed and tested SciPy descriptive-statistics module from the unmerged v0.8 visual prototype. The unapproved v0.8 UI is **not** included. These statistical summaries do not alter the domain review thresholds or provide clinical prediction.

## Version 1.0 Mission Timeline & Explainability

OpenAI Codex assisted with inspecting the v0.9 backend, implementing the pure
synthetic mission timeline module and GET /api/timeline adapter, writing regression
tests, and documenting the API contract. The implementation delegates validation,
illustrative trend rules and final assessments to the existing domain modules.
Tests use deterministic fictional observations only; no patient or astronaut
records, new clinical thresholds, diagnoses, or external medical evidence were
introduced. No Streamlit UI changes were made. Human review remains required
before merge; passing software tests is not medical validation.

## Version 1.1 functional React integration

OpenAI Codex assisted with reading Issue #7, implementing the standalone
Vite/React/TypeScript API client and accessible functional components, adding
runtime response validation and request cancellation, creating tests and CI,
and documenting startup and limitations. Backend-generated fictional fixtures
and a Python-generated local synthetic template were used; no real health records
or biomedical algorithms were added to React. The existing Python domain modules,
Streamlit behavior, clinical disclaimers and demonstration thresholds are unchanged.
The work does not implement the future Figma design, anatomical model or 3D UI.
Human review is required before merging; passing integration tests demonstrates
software behavior, not medical safety or clinical validation.

## Version 1.2 Biomedical Research Lab (isolated future research)

OpenAI Codex assisted with Issue #9 review, optional WFDB/NeuroKit preparation,
fixed-protocol heartbeat matching and engineering quality gates, bounded read-only
research API, minimal separate React view, offline fixtures, CI and documentation.
The original mission algorithms and thresholds are unchanged. Generated ECG/WFDB
fixtures are synthetic software tests, not real-record benchmark evidence.
PhysioNet access was denied, so the official record benchmark and source/license
review remain unverified and are explicitly documented as blockers. No diagnoses,
arrhythmia classifier, HRV health inference, astronaut risk scoring, volunteer
records or treatment recommendations were developed. Human source/license and
scientific review are required before this draft can advance; software tests and
algorithm benchmarking do not establish clinical or spaceflight qualification.
