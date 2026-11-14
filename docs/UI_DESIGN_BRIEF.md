# ARES Health AI — Next-Generation Interface Brief
## For Claude Design / Claude Artifacts

**Product:** ARES Health AI (Astronaut Risk Evaluation System)  
**Context:** NASA Space Apps Challenge 2026 — independent hackathon entry, **not** a NASA product  
**Language:** English for the interface, Spanish for team discussion  
**Design-only stage:** Do not change the existing Python backend or submit a production implementation without review.

### Product vision

Create an original, polished, high-fidelity, interactive **space mission health operations console**, not a generic Streamlit dashboard. It should feel like professional mission software: restrained, legible, calm, data-dense when appropriate, and unmistakably designed for astronaut-facing operations rather than entertainment or gaming.

**No copying NASA branding, mission patches, logos, astronauts' photos, proprietary UI screenshots, or licensed assets.** Use the ARES name and original visual elements.

### Visual language / design tokens

- Midnight graphite `#070D18`, slate `#101D2E`, blue-black `#172B42`.
- Accent teal `#68E1DB` for selection and key navigation, deep electric blue `#5D94FF` for data; amber `#FFC46B` for attention and muted coral `#FF887D` for blocked inputs.
- Dense but generous spacing; 8px spacing system and 12–20px panel radii.
- Large readable numerals; tabular number alignment, consistent units.
- Typeface: accessible sans serif; avoid ultra-thin type and tiny gray text.
- Visual hierarchy: operator workflow first, decorative effects second. Subtle transitions; no distracting floating widgets or luminous overload.
- States must use text + icon + color, never color alone.
- Never use green as a claim that an astronaut is medically healthy.

### Primary screens

1. **Mission Command** — top navigation, scenario and crew selection, explicit DEMO/SYNTHETIC label, recency and data provenance, four concise KPI panels; two focused charts; review findings queue with clear descriptions; sidebar where useful.
2. **Signals Explorer** — isolated metric focus, timeline with reference and recent windows, transparent comparative statistics, inspectable raw sample rows, chart tooltips with units, no diagnostic scoring.
3. **Crew Systems Atlas** — original interactive humanoid **schematic**, with 3 selectable systems only: cardiovascular (resting heart rate), sleep/recovery (hours), musculoskeletal/activity (daily activity minutes). Highlight the selected region and show related graphs/limitations on the right. Prefer accessible SVG with keyboard fallback; do not imply anatomical accuracy or that ARES measures bone density/radiation.
4. **Scientific Context** — curated links to official NASA HRP and Canadian Space Agency pages with clear distinction between the research motivating the concept and the synthetic data actually used.
5. **Review & Export** — traceable data-quality results and optional fictional review note; export synthetic CSV and JSON; show exactly why analysis was withheld if data incomplete.

### Existing functionality to preserve

The Python prototype on `main` already:
- Generates deterministic fictional daily heart rate, sleep and activity.
- Demonstrates four scenarios: stable, heart-rate shift, sleep shift, incomplete records.
- Accepts a restricted self-attested synthetic CSV with strict checks.
- Rejects malformed/missing/non-synthetic or invalid data before interpretation.
- Computes transparent illustrative rules: mean difference >=12 bpm for resting heart rate and >=1.5 hours sleep. These are **nonclinical demonstration settings**, not NASA thresholds.
- Creates explanatory review JSON and sample CSV exports.
- Links official NASA/CSA evidence; makes no medical diagnosis, treatment recommendation or astronaut-risk prediction.

### Interaction requirements

- Working nav between all screens; visual and keyboard interactions.
- Scenario switch should update dashboard, visible charts, state text, and atlas panels.
- When observations are missing/invalid, make the blocked state clear, display a specific issue, and hide misleading statistics.
- Chart hover details must label units and date/time (UTC).
- CSV upload should require explicit fictional-data attestation.
- Local-first: a standalone UI mockup may use hard-coded **representative fictitious** sample records, but must visually mark them as mock data and expose a clean adapter for Codex.
- Desktop-first 1440px wide, responsive for 768px tablets and 375px phones.
- Include accessible focus outlines and reduced-motion support.

### Claude deliverables

**First, produce two visually distinct design directions for the same Mission Command screen**, compare them on clarity, originality, hierarchy, and feasibility for a two-day hackathon. Recommend one; do not build a huge backend.

Then produce:
1. A high-fidelity **interactive React/TypeScript prototype** using Tailwind and accessible UI components, with a runnable preview (Artifact if supported).
2. Individual interactive screens for the five views with consistent design language.
3. A concise design-token sheet (colors, fonts, grids, spacing, corner radii, states).
4. A component list and responsive behavior notes.
5. Exportable React/TypeScript or equivalent source suitable for a Codex implementation handoff.
6. A small acceptance checklist and two or three screenshots/mockups showing the desktop layout.

### Guardrails

This is not clinical, NASA-operational, or real-person data. Do not fabricate medical risk labels, radiation measurements, blood glucose measurements, crew identities, or real mission status. Do not present a purely artistic landing page as a working application. Every screen must have a defined, demonstrable user action.

**Do not edit or merge GitHub `main`; design review comes before implementation.**
