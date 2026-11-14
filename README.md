# ARES Health AI — NASA Space Apps Challenge 2026

**Astronaut Risk Evaluation System**  
**Track:** Create Health Monitoring Software for Astronauts on Space Missions  
**Event:** Universal Event · November 14–15, 2026  
**Stage:** Hackathon prototype v0.4 — enhanced dashboard, simulated monitoring and review reporting, **not** clinically validated.

## Mission

Design a local-first, explainable astronaut health-monitoring prototype that supports the collection of wellness indicators, visualizes time trends, checks data quality, and helps crew members review meaningful changes and consult relevant procedures. It does **not** diagnose disease or replace flight surgeons, medical protocols, or mission operations.

The challenge asks for software that gathers health indicators and enables astronauts to evaluate and act on their health status. Our scope prioritizes **clarity, auditability, and operational resilience** over unvalidated predictive claims.

## What is in this repository?

- `docs/PROJECT_CHARTER.md` — problem, target user, scope, success criteria.
- `docs/ARCHITECTURE.md` — planned software components and boundaries.
- `docs/DATA_DICTIONARY.csv` — proposed data fields and units.
- `docs/DATA_SOURCES.md` — NASA resources and provenance policy.
- `docs/VALIDATION_PLAN.md` — reproducible synthetic scenarios and tests.
- `docs/PROJECT_BACKLOG.md` — prioritized work for hackathon weekend.
- `docs/RESEARCH_LOG.md` — evidence table to fill in.
- `docs/SUBMISSION_CHECKLIST.md` — project-page and delivery checklist.
- `docs/TEAM_BRIEF.md` — roles and collaboration conventions.
- `app.py` — running Streamlit prototype with a mission-status overview, synthetic physiological trends (heart rate, sleep and activity), quality alerts, data provenance and a mission review center.
- `src/ares_health/synthetic.py` — deterministic sample scenarios with fictional profiles.
- `src/ares_health/analysis.py` — non-clinical data quality checks and transparent change rules.
- `src/ares_health/review.py` — exportable JSON review report with explicit provenance and limitations.
- `tests/` — unit tests for simulation, trend flags, and review report behavior.
- `docs/AI_USAGE.md` — AI assistance disclosure to expand before submission.

## Get started (Windows / PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

If PowerShell blocks activation, use `.venv\Scripts\python.exe -m pip install -r requirements.txt` and `.venv\Scripts\python.exe -m streamlit run app.py`.

## Key decisions

1. Use **synthetic test data**, clearly marked as synthetic, until a reviewed public dataset is selected.
2. Start with data-validation and transparent change rules; advanced ML is optional and requires separately justified validation.
3. Operate locally on a laptop without a mandatory cloud service; Streamlit is for the demonstration, not a flight-certified interface.
4. Maintain documentation and final submission materials in **English**, with Spanish as the working language when appropriate.
5. Do not confuse a successful synthetic test with clinical validation or spaceflight qualification.

## Verify prototype

```powershell
python -m pytest -q
python -m streamlit run app.py
```

Try **Stable observations**, **Resting heart rate shift**, **Shortened sleep**, and **Incomplete records**. Open **Mission review center** to export a JSON record of the simulated review. This is a software demonstration, not validation of medical efficacy.

## Hackathon timing

NASA Space Apps 2026 project-submission window is listed as **November 14, 9:00 AM to November 15, 11:59 PM local time**. Historical Space Apps guidance asks teams to begin building their actual solutions when the hackathon starts. The initial planning scaffold was created before the event; subsequent functional prototype code was developed during the hackathon. Confirm the organizer instructions and deadline before submission.

## Roles & contact

The team owns its decisions and must confirm contributor permission before adding identifiable names or outside content. NASA Space Apps participation **does not imply NASA affiliation, endorsement, or medical validation**.

## Sources

- Challenge: https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/
- Event schedule: https://www.spaceappschallenge.org/2026/
- NASA Human Research Roadmap: https://humanresearchroadmap.nasa.gov/risks/
- NASA OSDR: https://science.nasa.gov/biological-physical/data/osdr/
