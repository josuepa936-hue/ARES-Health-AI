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
