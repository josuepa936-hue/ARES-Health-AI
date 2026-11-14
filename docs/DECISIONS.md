# Architecture decision records

## ADR-001 — Local-first instead of cloud-dependent

**Status:** proposed. **Why:** long-duration missions may have communication constraints; a laptop demonstration is easier to reproduce. **Tradeoff:** Streamlit localhost is not a flight-ready platform.

## ADR-002 — Explainable rules before ML

**Status:** proposed. **Why:** two-day event, tiny or simulated data, no defensible training/evaluation cohort. **Tradeoff:** only transparent deviations and flags, not disease prediction or clinical risk scores.

## ADR-003 — Synthetic records for early demonstrations

**Status:** proposed. **Why:** confidentiality and dataset mismatch risk. **Tradeoff:** cannot establish external validity; seek suitable open data carefully and cite exact provenance if integrated later.

## ADR-004 — English public materials, Spanish work coordination

**Status:** proposed. **Why:** platform accessibility for judges while supporting an international Spanish-speaking team.
