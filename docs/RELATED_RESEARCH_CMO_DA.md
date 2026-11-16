# Related Research: NASA Crew Medical Officer Digital Assistant (CMO-DA)

## Scope and independence

This section is a **literature comparison**, not an integration or medical
feature. **ARES does not use or connect to the original CMO-DA software. There
is no official collaboration between ARES and NASA or Google. ARES does not
provide medical diagnosis or treatment.** The NASA–Google collaboration described
by the source below concerns CMO-DA, not ARES.

No CMO-DA code, model, clinical dataset, API, service call or dependency is added.
ARES's deterministic engine, illustrative thresholds, protected public mode and
prepared local offline workflow remain unchanged. Citation links are optional
external reading; they are not fetched by the application to generate results.

## Official source and evidence provenance

**[G1] Google Cloud, Public Sector:**
[Google and NASA testing AI for medical care in space](https://cloud.google.com/blog/topics/public-sector/how-google-and-nasa-are-testing-ai-for-medical-care-in-space).

The project owner supplied this official Google URL and the article's relevant
text in this conversation. The discussion below paraphrases that supplied text.
A direct request to the official URL from this environment failed at the outbound
proxy with **CONNECT 403**, before an application response. The full page was
therefore not independently retrieved here; author, publication date and a newer
project status were not established. The event date mentioned in the article is
not treated as its publication date or as the date of a completed validation.

This is the sole external source used for **CMO-DA-specific claims**. Google's
article reports work with NASA; that is not a second independently reviewed NASA
publication. The NASA homepage linked from the supplied text is not used as
technical evidence for an architecture. No third-party reporting, inferred model
specification or unverified clinical claim is used. ARES implementation statements
below are checked against this repository's code and validation records.

## What CMO-DA is described as

Google describes CMO-DA as a **proof of concept for an automated Clinical Decision
Support System (CDSS)**, developed through work between Google and NASA. The
article describes a multimodal interface using AI, natural-language processing
and machine learning, informed by spaceflight literature. Its intended users
include a designated crew medical officer or flight surgeon. [G1]

The motivating problem is medical support during extended exploration missions,
including situations where a physician is not onboard or real-time communication
with Earth-based medical experts is limited. The stated research goal is to
explore assistance with interpreting symptoms, diagnoses and treatment options,
with greater crew autonomy for prospective Moon/Mars exploration. [G1]

These are **research objectives and source-reported prototype capabilities**.
They are not evidence here that a deployed system can independently diagnose or
treat a crew safely, replace clinicians, or has received medical/flight approval.
No such functions are implemented or offered by ARES.

## Agent approach: documented scope and unknowns

The supplied official text describes an **automated CDSS** and a **multimodal
interface**. It does **not** specify a multi-agent architecture, an agent count,
agent roles, orchestration, model identities, tools, memory or an agent framework.
Multimodal input/output is not evidence of multi-agent orchestration. [G1]

Consequently, this section does not attribute particular clinical agents, a
coordinator, a named model, an agent framework/protocol or a deployed offline
inference architecture to CMO-DA. An agent-based architectural account
would require additional public NASA/Google documentation describing those
components explicitly. The documented clinical-assistance autonomy objective
must not be presented as proof of a particular software-agent implementation.

ARES's implemented Copilot is a deterministic explanatory layer over recomputed
canonical synthetic context (`ENGINE = "deterministic-offline"`). It is not an
LLM or a clinical agent team. The name "Copilot" and educational Wellness content
do not imply the CMO-DA architecture, autonomy or clinical capabilities.

## Reported evaluation and experimental status

The article reports initial trials across medical scenarios using the **Objective
Structured Clinical Examination (OSCE)** framework and describes early results
as promising. It also describes work with medical doctors to test and refine
the prototype at the time of that report. [G1]

The supplied text provides no numerical accuracy score, sample size or completed
clinical/flight qualification. This section does not invent those details,
convert "promising" into established reliability, or assert a current operational
release. Source-reported OSCE use is not equivalent to ARES's synthetic software
tests, and neither evidence track establishes medical approval of ARES.

## Comparison with implemented ARES v1.5

| Aspect | CMO-DA in the supplied official text [G1] | Implemented ARES v1.5 |
|---|---|---|
| Purpose | Experimental medical decision support for prospective exploration crews under constrained access to experts | Independent educational review of explicitly fictional daily observations |
| Clinical ambition | Research toward symptom/diagnostic/treatment-option assistance and greater crew autonomy | No diagnosis, treatment, triage or medical clearance; illustrative comparisons and explanations only |
| Processing | AI/NLP/ML and a multimodal interface are described; specific models and agent orchestration are not specified | Seeded synthetic data, strict validation and deterministic Python rules; no LLM or remote clinical model |
| Conversation | Medical-assistance interface described at proof-of-concept level | Bounded deterministic intent handling over canonical observations, windows, timeline and source links |
| Data/provenance | Spaceflight literature is described; exact training/evaluation datasets and sizes are not supplied | Fictional scenarios/check-ins; NASA literature is background context, not astronaut telemetry or validated thresholds |
| Evaluation | Initial medical scenarios and source-reported OSCE-based evaluation; no quantitative results supplied here | Prior software suites and disconnected Linux checks, plus separately attributed owner manual acceptance; not clinical validation |
| Connectivity | Constrained Earth communication motivates the project; the excerpt does not establish a particular deployed offline stack | Prepared local React + FastAPI/Python works without external Internet; the separate Render URL needs a server connection |
| Human review | Intended to assist a crew medical officer or flight surgeon; no clinician-replacement claim is established here | Manually recorded fictional review/audit states; DOCUMENTED is not medical authorization and no personnel are contacted |
| Relationship | Google reports NASA–Google work on CMO-DA | No official NASA/Google collaboration; no use of or connection to original CMO-DA software |

ARES facts are supported by [the deterministic Copilot implementation](../src/ares_health/copilot.py),
[offline operation](OFFLINE_OPERATION.md), [validation provenance](OFFLINE_VALIDATION.md)
and [public-mode boundaries](RENDER_PUBLIC_DEMO.md). Optional MIT-BIH/OSDR
research views remain separate from mission observations; they are not CMO-DA
integrations and do not add clinical capability.

## Effect on operation and presentation

This addition changes documentation only. It introduces no runtime fetch,
background research download, cloud inference, new dependency, clinical model,
agent, biomedical rule or deployment setting. The prepared local server still
supplies the core workflow offline. Reading the external article needs Internet;
computing ARES results does not. No Render browser-only/PWA offline fallback is
claimed. [Short presentation wording](CMO_DA_PRESENTATION_EN.md) preserves these
boundaries without converting CMO-DA research claims into ARES features.

## Validation of this documentation change

On branch `docs/cmo-da-related-research`, based on documentation commit e7fb184,
the newly executed checks passed: **410 Python tests**, **62 frontend tests** and
the TypeScript/Vite production build. Python emitted the existing Starlette/httpx
deprecation warning. Local Markdown link targets and diff whitespace were checked.
These results assess ARES software, not CMO-DA or clinical performance.

Only Markdown files change. Application source, models, dependencies, offline
harnesses, deployment configuration and public security controls are unchanged.
The prior disconnected **8 HTTP + 2 Chromium** results remain separately recorded
in OFFLINE_VALIDATION.md; they were not relabeled as new runs for this addition.
No deployment, merge, push or new remote CI result is claimed.
