# Evidence provenance — owner-provided validation report

Evidence class: **owner-reported manual acceptance**, not an independent audit.
Original filename: `ARES_v1_5_Offline_Validation_Report.md`.
Report date: November 15, 2026. Received as a user attachment in this conversation.
Original attachment SHA-256: `f210cbf5a1aeba9f854feb6c20bc9dcfc54f70eb6852ba92bf380463b6891ff6`.

The report text below is retained with trailing whitespace normalized. Statements
about screenshots, the Windows installation, Render dashboard and incognito access
are the owner's report; the referenced screenshots and Windows-generated JSON
were not supplied with this attachment for independent inspection. The separate
Linux isolation evidence remains distinct. Reproduction steps below are source
material, not a record that this agent executed them in Windows or submitted anything.

---

# ARES Health AI v1.5 — Offline Functional Validation Report

**Date:** 15 November 2026
**Project:** Astronaut Risk Evaluation System (ARES Health AI)
**Scope:** Manually observed core offline workflow on a Windows local installation
**Result:** 6/6 functional checks reported as passed by the project owner

## 1. Objective

Verify that the locally installed ARES Health AI v1.5 synthetic mission console continues to operate without an active Internet connection after initial dependency installation and React build.

## 2. Configuration and procedure

- **Environment:** Windows / PowerShell, local Python FastAPI server and precompiled React/Vite interface.
- **Start command:** `start-ares.cmd --skip-build` from the project root.
- **Local origin:** `http://127.0.0.1:8000/` (loopback only; not a public IP address).
- **Preparation:** Python dependencies were installed while online; `npm.cmd ci` completed and `npm.cmd run build` succeeded (2,005 modules transformed in the screenshot).
- **Manual offline step:** The owner disconnected the computer from the Internet, loaded/reloaded the localhost interface and exercised the core workflows while the local FastAPI process remained running.
- **Evidence basis:** The owner reported the six completed offline tests. Prior screenshots document the successful frontend build and local launch. A separate full offline traffic trace, automated network-isolation test, independent witness and offline-generated JSON artifact were **not** supplied for independent inspection.

## 3. Manual acceptance matrix

| ID | Test performed while offline | Owner-reported result |
|---|---|---|
| OFF-01 | Switch between stable and heart-rate-shift synthetic scenarios; inspect visualizations | PASS |
| OFF-02 | Load incomplete records; withhold trend interpretation and show `DATA_QUALITY_BLOCKED` | PASS |
| OFF-03 | Use the deterministic ARES Copilot to explain the selected scenario | PASS |
| OFF-04 | Review Mission Wellness educational/explanatory content | PASS |
| OFF-05 | Submit a fictional check-in and generate a review report | PASS |
| OFF-06 | Download JSON and inspect observation and review/audit content | PASS |

**Outcome:** 6 of 6 manually executed functional checks were reported as successful. This is acceptance evidence for the core local workflow, not proof that all application features operate without a network.

## 4. Online demonstration (separate validation track)

- **Public URL:** https://ares-health-ai.onrender.com/
- Render showed **Deploy succeeded | Live** for deployment source commit `e7e3a7c` on the `feat/render-public-demo` branch.
- The owner confirmed the public interface and functions, including scenarios, deterministic Copilot, Wellness, fictional check-in and report export. The URL also opened in an incognito browser without sign-in.
- An independent physical-mobile-device acceptance test was not reported. The public web version requires Internet access; it must not be described as browser-offline capable.

## 5. Limitations and boundaries

1. Offline use requires a prepared local installation, compiled frontend and running local Python/FastAPI server. A fresh installation may require Internet access to obtain tools/dependencies.
2. The browser-based Render URL does not operate offline. This validation applies to the **localhost deployment**, not a PWA or offline-cached hosted website.
3. External NASA OSDR, MIT-BIH and other live research downloads cannot be assumed available without a network; NASA literature links may not open offline.
4. The mission observations, scenarios and check-ins are explicitly **synthetic**. Illustrative comparison rules are not NASA medical limits. ARES does not diagnose, prescribe treatment or authorize clinical decisions.
5. The owner-reported offline checks do not certify absence of attempted external network calls or prove performance under all network failures; network inspection and repeat testing on another machine would strengthen the evidence.
6. No NASA endorsement, medical-device approval, flight qualification or spaceflight operational capability is asserted.
7. AI-assisted decorative imagery must be credited and labeled as required by the submission rules; third-party source rights and project licensing require separate review.

## 6. Reproduction procedure for reviewers

1. Install the documented supported versions of Python, Node.js and project dependencies while online.
2. Build the frontend with `npm.cmd ci` and `npm.cmd run build` from `frontend/`.
3. Start ARES with `start-ares.cmd --skip-build` from the repository root.
4. Confirm `http://127.0.0.1:8000/` works; disconnect Wi-Fi/Ethernet/VPN and reload that **localhost** URL.
5. Repeat tests OFF-01 through OFF-06 without reconnecting.
6. Save dated screenshots or a screen recording showing disabled network, a functioning localhost browser, the local server and the downloaded report. Do not disclose personal identifiers or medical information.

## 7. Release conclusion

**Owner-accepted result:** Core ARES Health AI v1.5 synthetic mission workflows were exercised successfully on a prepared Windows installation with the Internet disconnected. The application is an offline-capable **local prototype**, with a separate online demonstration hosted on Render. Further independent network-isolation and system/security validation would be necessary before making stronger reliability or mission-readiness claims.

**Submission note:** This validation report does **not** constitute submission to NASA Space Apps. The project owner must complete the official Project Tab, verify public demo/project links, source and AI credits, eligibility, licensing and confirmation of successful submission.
