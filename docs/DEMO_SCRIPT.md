# ARES Health AI — Demo Script (2–3 minutes)

**Language:** English  
**Application:** Streamlit local demo; synthetic records only  
**Audience:** NASA Space Apps Challenge 2026 reviewers

## Preparation

- Run `python -m pytest -q` and record the actual passing test count.
- Run `python -m streamlit run app.py`.
- Set screen zoom so the sidebar and main dashboard are readable.
- Have the built-in scenarios ready. Use the **synthetic sample CSV** supplied by the app.
- Do not show personal accounts, private notifications, emails or access tokens in the recording.

## Spoken walkthrough

**0:00–0:20 — Problem**

"Long-duration space missions create physiological and operational challenges. Astronauts may need understandable ways to review health observations when communication and medical resources are constrained. ARES Health AI explores how an offline-capable interface can support that review."

**0:20–0:45 — What we built**

"This is our ARES Health AI prototype, developed in Python with Streamlit. It includes synthetic health-data generation, a local CSV importer, data-quality checks, interactive charts, transparent change flags, and exportable review reports. All data shown are fictional."

**0:45–1:15 — A scenario with a change**

"Here is a simulated resting heart-rate shift. ARES compares the first seven fictional days with the latest four, shows the magnitude and date intervals, and suggests checking the observations. The rule is illustrative and does not diagnose any medical condition."

**1:15–1:40 — Safety and data quality**

"When we select incomplete records, ARES blocks interpretation. We intentionally prefer withholding an analysis rather than presenting a potentially misleading result."

**1:40–2:00 — CSV and reports**

"We can upload a synthetic CSV, validate its structure locally, visualize the imported records, and export an explanatory JSON report for review. Invalid CSV files are rejected."

**2:00–2:20 — Scientific evidence**

"Under Scientific Evidence, the dashboard links directly to NASA Human Research Program and Canadian Space Agency publications. The heart-rate, sleep and activity indicators are motivated by that research context, but those sources do not validate our numerical thresholds."

**2:20–2:40 — Limitations and vision**

"ARES is not medical or flight-certified software. It does not use NASA astronaut medical records or perform diagnosis. Future research would require clinically approved protocols, validated sensors and real-world validation. Our contribution is an accessible, auditable foundation for astronaut health-data review."

## After recording

- Link to the public GitHub repository and provide instructions to run the prototype locally.
- Add a video link or permitted upload in the event submission, if required.
- State exactly which tools and AI assistants were used.
- Confirm the official event deadlines and participant requirements before submission.
- Keep a copy of the test results and screenshots.
