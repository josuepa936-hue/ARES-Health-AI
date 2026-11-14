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

### User-approved visual direction — reference images supplied 14 November 2026

The user supplied two visual references directly in the ChatGPT design discussion:
- **Reference A — tactical biometrics control panel:** dark teal military/aerospace telemetry grid; center-left full-body human silhouette with highlighted sensor hotspots; dense, modular edge-aligned signal panels, fine grid lines, small uppercase UI labels, contrasting amber/cyan/red caution accents.
- **Reference B — cinematic space EVA monitoring:** a wide space-station/EVA scene surrounded by translucent glassy telemetric cards, strong typography and readable values, crew information panels, sophisticated dark-blue atmosphere and clear visual depth.

**Blend the two aesthetics, rather than copying either composition.**
Build a professional, distinctive **ARES Mission Bio-Telemetry Console** with:
1. A large, central **stylized anatomical figure/astronaut silhouette** (prefer an original SVG schematic, not a real person's likeness), with visually connected hotspots.
2. Compact, highly legible health telemetry around the silhouette and a coherent responsive grid. Use real existing metrics only: **synthetic resting heart rate (bpm), sleep duration (hours), and daily activity (minutes)**. Each card shows a sparkline, last observation, and explicit `SIMULATED` label. No fake blood oxygen, body temperature, blood pressure, nitrogen, suit pressure, radiation dose or bone mass values.
3. A dramatic **mission environment visual** as a secondary panel/section, using custom abstract vector artwork or licensed imagery only with verifiable rights; the image must never imply NASA endorsement or actual live streaming.
4. Distinct alert states with short text: `REVIEW DEMO CHANGE`, `DATA QUALITY BLOCKED`, `INSUFFICIENT DATA`, `NO RULE TRIGGERED`. Do not label a person medically `normal`, `healthy`, `critical`, or `safe`.
5. Visible scan/grid/target motifs used sparingly, precision borders, small section identifiers, 24h/UTC date labels for data, restrained animation, and operator-grade legibility.
6. On-click hotspot detail opens the related trend and brief NASA/CSA research context. Keyboard accessible alternate controls must always exist.
7. A fictional crew profile, e.g. `SIM-001` with avatar illustration or initials — **never real astronaut identities or photos**. The application must not present a real astronaut as monitored.
8. A one-click switch between `TACTICAL / Body Telemetry` and `MISSION / Overview` views, both powered by exactly the same validated synthetic dataset and existing safety state.
9. Responsive: desktop 1440px can use central silhouette + cards; mobile must stack panels logically and preserve readable content, avoiding minuscule text.

**Visual quality bar:** original premium UX; more like a credible aerospace operations interface than a typical Streamlit metrics dashboard. Avoid excessive glowing neon, misleading ECG traces generated from mere daily averages, and pseudo-real-time sensor pulses unless conspicuously labeled decorative simulation.

#### Claude first deliverable — revised

**Start with ONE interactive high-fidelity Mission Bio-Telemetry screen** combining the best qualities of Reference A and Reference B. Ask the designer to attach the two user-supplied screenshots in Claude; the brief URL alone does not embed the images. The first deliverable should show a coherent composition with a body-map and telemetric cards using the *actual* three available data fields. Request a preview at 1440×900 and a responsive mobile state. Design direction must be reviewed before implementing React/FastAPI integration.

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

**First, show one cohesive high-fidelity interactive screen following the user-provided tactical biometrics and cinematic EVA references.** The user has now chosen the visual direction. Explore alternatives only if needed to solve a concrete usability problem. Do not build a new backend until the design is approved.

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
