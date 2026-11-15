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


## Experimental v1.2 NASA and MIT research branch

OpenAI ChatGPT helped integrate the NASA OSDR study metadata adapter,
opt-in public small-sample CSV access, React NASA research view, offline
provenance/security regression tests and documentation with the Codex-created
MIT-BIH ECG evaluation module. Codex assisted separately with the MIT-BIH
WFDB/NeuroKit2 pipeline and its synthetic-fixture tests. No real astronaut
data were accessed, and PhysioNet record 100 has **not** been successfully
downloaded and evaluated in the Codex environment. NASA OSD-87 is a mouse
retina study, not human mission monitoring. The team must independently
verify scientific and data license claims before publication.

A subsequent integration change added an explicit public AWS source for MIT-BIH that PhysioNet documents on its official dataset page. Acquisition remains opt-in and subject to the same SHA-256 manifest and waveform checks; no public-record benchmark score is claimed without a successful verified run.


## Version 1.3 integrated mission workflow

OpenAI ChatGPT assisted with the complete fictional end-to-end check-in
workflow, Python-controlled risk/context guidance, combined dataset-specific
timeline/report for CSV and manual input, typed React API integration, NASA
human spaceflight five-hazards navigator, high-contrast operational layout,
regression and real HTTP integration tests, and the final demo documentation.
All new user-entered values are expressly fictional, not real health records.
No autonomous medical triage, disease diagnosis, treatment recommendations,
real astronaut telemetry, clinical validations, or NASA endorsement were
implemented. The planned Figma-designed anatomical 3D asset remains separate
and must not be represented as complete. Human review and actual CI validation
remain necessary before merging or submitting.


The final v1.3 integration also added a PowerShell one-command launcher,
static compiled React asset serving through localhost FastAPI, strict
file-path restrictions, production distribution smoke tests, and
documentation for offline presentation. Compiled assets are produced
locally; no third-party hosted API or cloud patient-data service is required.

## Version 1.4 mission-control presentation

OpenAI Codex assisted with the React console redesign, accessible tabbed workflows,
API-connected telemetry/anatomical navigation, Recharts integration, regression and
real Chromium tests, screenshot review and documentation. OpenAI image generation
created an original clothed fictional anatomical-navigation illustration. It is
not a patient image, NASA asset or clinically certified anatomical model; generated
anatomy and decorative colors have no measurement or diagnostic meaning. No external
anatomical model/license was represented as available. The task's referenced image
attachments were not accessible, so Issue #13's written art direction was used.
Python domain logic, biomedical benchmarks, source provenance, validations and
report generation remain unchanged. Human visual/source review is required before
merging this draft against the v1.3 branch. No merging or clinical claim is authorized.

## Version 1.5 deterministic mission copilot and fictional review

OpenAI Codex assisted with implementing the bounded Python explanatory service,
strict canonical-context API schemas, evidence references, manual four-state
review/audit workflow, integrated JSON export, React dock integration and tests.
The runtime copilot is **deterministic and offline, not an LLM or generative AI**.
No generative model plugin, remote inference, diagnosis, medical triage, treatment,
clinical authorization or validation claim was added. Existing anatomy artwork
provenance and biomedical/research modules are preserved. Questions and notes are
fictional-only, transient user text; notes cannot instruct the analysis engine.
Codex implementation assistance must not be confused with a generative runtime
model. Human review remains required before merging this draft against v1.4.

## Issue #17 copilot reading and evidence presentation

OpenAI Codex assisted with inspecting the reported clipping/scroll defects,
implementing a native React dialog that preserves the conversation and draft,
response-start focus/announcements, responsive readable typography, progressive
evidence disclosure, unit/browser regression tests and documentation. Evidence
values are displayed from the existing Python API; no biomedical calculation,
threshold, clinical claim or runtime generative model was introduced. The existing
anatomical image and public research provenance were preserved. Before/after
screenshots are actual local Chromium renders of synthetic scenarios, not generated
mockups. Browser checks run on Linux at the requested desktop/mobile viewports;
they do not establish Windows execution, physical-device coverage or clinical
validation. Human review is required before merging against the v1.5 branch.

## Issue #19 cockpit and conversation balance

OpenAI Codex assisted with reproducing the Issue #17 layout regression, measuring
actual browser geometry, removing viewport-dependent telemetry compression,
introducing explicit full-cockpit navigation and document-flow docked reading,
preserving modal reading position, and implementing regression tests/documentation.
Actual local Chromium screenshots compare the Issue #17 base against this change
at three desktop sizes and one mobile viewport. No new generated image, biomedical
calculation, threshold, diagnosis, runtime generative model or research-data claim
was introduced. The existing anatomical illustration and its attribution remain
unchanged. Code assistance and software checks do not establish clinical validity;
human review is required before merging this draft against the Issue #17 branch.


## Issue #21 — Integrity and audit metadata

ChatGPT implemented an auditable comprehensive report adjustment directly in
GitHub: canonical root/nested four-state review statuses, legacy two-state
compatibility labeling, a shared `APP_VERSION` constant, UTC device-clock action
timestamps, strict backend timestamp validation, typed React contracts, and
additional tests. This does **not** change the biomedical domain rules or
constitute flight-qualified audit timestamps; existing user records remain
fictional and ephemeral. Changes require CI and human review before merging.
