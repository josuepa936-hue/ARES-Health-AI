# ARES Health AI v0.8 — Advanced Mission Control Demo (2–3 minutes)

**Language:** English  
**Application:** Streamlit local demo; synthetic records only  
**Audience:** NASA Space Apps Challenge 2026 reviewers

## Preparation

- Run `python -m pytest -q` and record the actual passing test count.
- Run `python -m streamlit run app.py`.
- Set screen zoom so the sidebar and main dashboard are readable.
- Have the built-in scenarios ready. Use the **synthetic sample CSV** supplied by the app. Install SciPy from `requirements.txt` before testing.
- The v0.8 interface has five tabs: Mission Overview, Signals Lab, Body Systems, Scientific Evidence and Mission Review.
- Do not show personal accounts, private notifications, emails or access tokens in the recording.

## Spoken walkthrough

**0:00–0:22 — Mission challenge**

"Long-duration spaceflight brings cardiovascular, sleep, physical-conditioning and operational challenges. Astronauts may need accessible ways to inspect observations and communicate what warrants review. ARES explores how that could look as a local software prototype."

**0:22–0:48 — Mission Overview**

"ARES Health AI is a Python-based synthetic-data mission console. We can simulate daily resting heart rate, sleep duration and activity, or load a fictional CSV. This panel shows completeness, quality findings and transparent review flags."

**0:48–1:14 — Explainable trend change**

"Let's select a fictional heart-rate shift. ARES shows the reference and recent observations and explains the arithmetic behind the change. This is an engineering demonstration rule, not a medical diagnosis or risk prediction."

**1:14–1:38 — Signals Lab**

"In the Signals Lab, SciPy provides a robust spread estimate and a Theil–Sen descriptive trend slope. These help us examine patterns and verify our calculations. They do not independently trigger medical decisions."

**1:38–2:02 — Body Systems**

"Our original schematic provides navigation across cardiovascular, sleep and musculoskeletal indicators. It is an interface map, not medical anatomy or clinical screening."

**2:02–2:22 — Data quality and sources**

"With incomplete records, ARES blocks trend interpretation. Scientific Evidence links official NASA and Canadian Space Agency research, but this app does not read NASA health data or telemetry."

**2:22–2:42 — Review and limitations**

"Mission Review lets us document a simulated verification and export JSON or CSV results. ARES is a software demonstration using fictional data; it is neither medically validated nor approved for actual spaceflight use."

## Recording checklist

- Show the **four built-in scenarios**, especially the incomplete-data blocked state.
- Demonstrate **a synthetic CSV upload** and avoid exposing private files.
- Show the Signals Lab descriptive statistics and explain they are not medical algorithms.
- Select a body-system hotspot and show its research context.
- Download an example review JSON.
- Cite the actual test results and disclose ChatGPT/Codex assistance in the final entry.
- Never claim that NASA provided the measurements or has endorsed the prototype.

## After recording

- Link to the public GitHub repository and provide instructions to run the prototype locally.
- Add a video link or permitted upload in the event submission, if required.
- State exactly which tools and AI assistants were used.
- Confirm the official event deadlines and participant requirements before submission.
- Keep a copy of the test results and screenshots.
