# Scientific Evidence Center — ARES Health AI v1.5

## Purpose and boundaries

ARES Health AI is a local, explanatory software demonstration for the NASA Space Apps Challenge 2026. It generates or imports **synthetic** daily measurements and illustrates a transparent comparison of trends.

**Important:** This project uses NASA and Canadian Space Agency **public research publications as background references**. Mission mode does **not** ingest astronaut medical records, NASA telemetry, radiation measurements or live sensor feeds. The separate optional NASA OSDR research mode can read public OSD-87 mouse-study metadata and a bounded sample table on explicit request; these are never mission observations. Literature context does **not** validate the thresholds or clinical accuracy of the application.

## Why these three synthetic variables?

| Variable | Reason for inclusion | What it cannot establish | Official reference |
|---|---|---|---|
| Resting heart rate (bpm) | Cardiovascular adaptations are among the physiological concerns investigated for spaceflight. A simple scalar trend is easy to demonstrate and review. | No diagnosis of arrhythmia, cardiovascular disease, or risk severity can be inferred from this variable alone. | [NASA: Risk of Cardiovascular Adaptations](https://www.nasa.gov/reference/risk-of-cardiovascular-adaptations/) |
| Sleep duration (hours) | Irregular schedules, circadian disruption and sleep loss can affect crew health/performance. Time-based trends are interpretable. | This does not measure actual sleep quality, workload, or behavioral health. | [NASA: Risk from Inadequate Sleep and Irregular Schedules](https://www.nasa.gov/reference/risk-from-inadequate-sleep-and-irregular-schedules/) |
| Daily activity (minutes) | Exercise and fitness are important research and countermeasure domains during microgravity exposure. | Minutes alone are not evidence of fitness, exercise intensity or compliance with a mission exercise prescription. This metric is displayed but does not trigger a change rule. | [NASA: Risk of Reduced Cardiorespiratory and Musculoskeletal Fitness](https://www.nasa.gov/reference/risk-of-reduced-cardiorespiratory-and-musculoskeletal-fitness/) |

## Other spaceflight hazards (context, NOT monitored)

NASA identifies **space radiation, isolation and confinement, distance from Earth, altered gravity, and hostile or closed environments** as five major hazards of human spaceflight. ARES currently **does not track these exposures or predict their medical consequences**.

- [NASA: Five Hazards of Human Spaceflight](https://www.nasa.gov/hrp/hazards/)
- [NASA: Risks of Human Spaceflight](https://www.nasa.gov/hrp/risks/)
- [Canadian Space Agency: Monitoring Radiation for Astronaut Health](https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp)
- [Canadian Space Agency: Why Do We Conduct Science Experiments in Space?](https://www.asc-csa.gc.ca/eng/iss/science/why-do-we-conduct-science-experiments-in-space.asp)

These literature resources are **external reading material**, not inputs to the mission engine. Separate research data sources and access limits are listed below.

## How ARES processes the simulated data

1. Generate deterministic fictional observations or import a limited local synthetic CSV file.
2. Validate structure, dates, provenance labels, and allowed numeric ranges. Invalid or incomplete data block interpretation.
3. Use the **first seven** simulated days for the reference average and the **last four** for a recent average.
4. Produce a **review flag** when the illustrative absolute mean difference reaches 12 bpm for resting heart rate or 1.5 hours for sleep. These are **engineering demonstration settings**, not validated clinical limits or NASA medical criteria.
5. Present the input data, transparent explanations, and conservative next steps such as reviewing the source and consulting authorized mission medical personnel in any real operational situation.

The software **does not prescribe a treatment, give emergency triage recommendations, or classify a person as healthy or unhealthy**. A missing flag is not medical clearance.

## Scientific limitations and future validation

- Simulated observations do not capture human biological variation or sensor uncertainty.
- The reference window and review settings were chosen for demonstration, not derived from published clinical studies.
- No clinical sensitivity/specificity or clinical outcomes can be claimed. Optional terrestrial ECG detector benchmarking is a separate engineering protocol, not validation of mission thresholds.
- The sample activity metric is visualization only; it does not drive an alert.
- A production use case would require appropriate validated sensors, clinical expertise, review of spaceflight-specific standards, privacy protections, mission-authorized escalation protocols, and comprehensive testing.
- The event is independent of NASA operational medical systems; participation in Space Apps does not imply NASA endorsement.

## Separate public research sources

| Source | Use and limits |
|---|---|
| [PhysioNet MIT-BIH Arrhythmia Database 1.0.0](https://physionet.org/content/mitdb/1.0.0/) ([dataset DOI](https://doi.org/10.13026/C2F305)) | Terrestrial ECG with reference annotations; optional record-100 detector experiment, not astronaut data or mission calibration |
| [NASA OSDR OSD-87](https://osdr.nasa.gov/bio/repo/data/studies/OSD-87) | STS-135 **mouse retinal tissue** research; catalog and small original sample table, not human vital signs |
| [NASA OSDR overview](https://science.nasa.gov/biological-physical/data/osdr/) | Repository context, not evidence for clinical rules |

The code enables these views only with `ARES_RESEARCH_ENABLED=1`. MIT requires
separate WFDB/NeuroKit dependencies and a verified local artifact; NASA requires
network access to the approved NASA/public storage routes. Unavailable sources
produce unavailable/abstained results, never invented research measurements.
Record-100 performance and dataset-license review remain unverified here.
See [MIT/NASA research](MIT_NASA_RESEARCH.md), [protocol and citations](RESEARCH_LAB.md)
and [provenance policy](DATA_SOURCES.md). Dataset terms, software dependencies
and generated artwork have separate attribution requirements.

The NASA/CSA sources explain research topics; **none** validates the first-seven /
last-four windows, 12 bpm / 1.5 hour settings or fictional source authenticity.
Copilot and Wellness reuse canonical synthetic results and these research links;
they do not provide individualized treatment or medical clearance.

## Source verification

The earlier literature review recorded URL checks on November 14, 2026. The
Issue #26 audit checked references against repository source; live scientific
source access is restricted in this environment, so this is not a new claim
that every external URL or study file was reachable. The content above is a short, independently written synthesis; it is not a reproduction of original articles.

## Reproducible software verification

```powershell
python -m pytest -q
python -m streamlit run app.py
```

**Testing scope:** These tests verify deterministic synthetic data behavior, validation logic, report safety, and the application flow. They are not clinical performance tests.
