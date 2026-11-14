# Codex Implementation Handoff — AFTER UI Direction Approval

This document is a **task brief**, not permission to rewrite the live application yet.

## Objective

Implement a reviewed Claude-designed ARES Health AI frontend **without breaking the existing tested Python core**. The stable Streamlit v0.7 application on GitHub `main` is the fallback and must remain runnable.

## Development workflow

1. Start from the latest `main` and create a dedicated implementation branch, e.g. `feat/ares-react-console`.
2. Read `docs/UI_DESIGN_BRIEF.md` and consume the user-approved Claude prototype/source/screenshots. If the design artifact is not available to Codex, request its exported React/TypeScript source or an accessible link rather than guessing.
3. Add a self-contained `frontend/` React + TypeScript + Tailwind implementation. Favor lightweight accessible components, responsiveness and low setup overhead.
4. Keep Streamlit and its existing endpoints/logic untouched. Expose only the minimal needed synthetic Python functions through a local FastAPI adapter under `src/ares_health/api.py` if the team approves this integration. Separate this adapter from validation and analytical rules.
5. Avoid introducing auth, databases, third-party secrets, remote analytics, live health telemetry, heavy 3D dependencies, or paid APIs during the hackathon.
6. Do not alter the thresholds or claim medical validation. No real clinical or astronaut records. No automated treatment guidance.
7. Test navigation, all four synthetic scenarios, blocked/missing-data handling, CSV restriction, review JSON and CSV exports, and accessible fallbacks.
8. Add `frontend` scripts and automated tests; keep the existing Python `pytest` suite green. Document reproducible local startup for both backend and frontend.
9. Disclose Codex and Claude contributions in `docs/AI_USAGE.md`.
10. Open a PR for review and do **not** merge it automatically. Provide screenshots, local commands, test evidence, and tradeoffs.

## Feature/data contract (from existing stable Python code)

- `generate_scenario(scenario, seed=2026, days=21)` produces synthetic daily observations.
- `quality_issues(frame)` blocks invalid inputs; `review_changes(frame)` computes explanatory demo flags.
- `load_synthetic_csv(bytes)` enforces limits, schema, provenance and timestamps.
- `get_crew_guidance(issues, blocked, flags)` returns conservative explanations and review steps.
- `build_review_report(...)` revalidates source data and creates deterministic review JSON.

### Proposed minimum API (only if using FastAPI)

- `GET /api/scenarios` — static labels/IDs.
- `GET /api/demo?scenario=...&seed=...` — synthetic records, provenance, quality issues, flags, guidance.
- `POST /api/synthetic-csv` — restricted synthetic upload; require user assertion that records are fictional; reject malformed content.
- `POST /api/review` — preserve original safeguards, only synthetic records.
- Do not claim these endpoints already exist or include them in product demos until implemented/tested.

## Frontend acceptance criteria

- The design reflects the user-approved Claude prototype closely (not a generic dashboard).
- Mission screen accessible with readable text, units, responsive layout, contrast and keyboard navigation.
- Three systems atlas hotspots correspond only to implemented measurements.
- An incomplete or invalid scenario never appears as normal or healthy.
- Clear research vs data separation; all supplied data identified as synthetic.
- No regression in existing pytest tests; new unit and UI tests pass.
- A clear fallback path to v0.7 is documented.
- No merge without human visual signoff.

## Important deadline tradeoff

For NASA Space Apps 2026, submit the **tested stable working version** if a new frontend cannot be fully integrated and demonstrated before the official submission deadline. Preserve the new interface as a separate concept/preview rather than falsely claiming functionality.
