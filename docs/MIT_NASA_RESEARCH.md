# ARES Research Integrations — MIT-BIH + NASA OSDR (v1.2 development)

**This research work is NOT astronaut health monitoring, a medical device, or a validated clinical solution.** The original fictional mission simulator, its CSV import restrictions, alerts and timeline are separate and unchanged.

## Two independent sources

| Research mode | Source | What it actually measures | What ARES demonstrates |
|---|---|---|---|
| MIT terrestrial ECG | [PhysioNet MIT-BIH Arrhythmia Database 1.0.0](https://physionet.org/content/mitdb/1.0.0/) | Two-channel terrestrial ECG with expert-reviewed heartbeat annotations | WFDB + NeuroKit2 R-peak detection, strict quality checks, beat matching and TP/FP/FN, precision, recall, F1 and timing error |
| NASA space biology | [NASA OSD-87 — STS-135 mouse retina](https://osdr.nasa.gov/bio/repo/data/studies/OSD-87) | **Mus musculus (mouse)** retinal tissue, DNA microarray and sample metadata from spaceflight research | Official public file catalog, category counts and on-demand preview of a small sample table; not physiological trend detection |

These are **different datasets and different research questions**. Neither provides live astronaut vital signs. Do not merge these records or draw clinical conclusions from their combined existence.

## NASA data connection (implemented)

NASA's [OSDR Public API](https://api.nasa.gov/) documents:
- Public study files: `GET https://osdr.nasa.gov/osdr/data/osd/files/87`
- Study web page: `https://osdr.nasa.gov/bio/repo/data/studies/OSD-87`

The public catalog is confirmed to expose OSD-87 file descriptions including `GLDS-87_array_SampleTable_GLmicroarray.csv` (a small study file) as of November 14, 2026. The study is **mouse retinal research following STS-135**, not astronaut telemetry. The page describes the sample organism and study context. A current file manifest is fetched live on user request, so file counts may differ if NASA updates the data.

NASA research endpoints:
- `GET /api/research/nasa/study` — on-demand official JSON manifest; returns only visible unrestricted files, their names, sizes, categories and vetted original NASA download links, plus explicit provenance.
- `GET /api/research/nasa/sample-table` — on-demand small original experimental sample CSV; only `GLDS-87_array_SampleTable_GLmicroarray.csv`, and only if the current public catalog still declares it visible/unrestricted. Returns its original columns and rows, not derived physiology.

**Guardrails:**
- Both endpoints require the existing `ARES_RESEARCH_ENABLED=1` setting and a loopback client. No API keys or personal data.
- One allowlisted study. Requests cannot choose arbitrary URLs, accession numbers, patient files, or huge omics downloads.
- HTTPS-only NASA host, no redirects, 12-second timeout; manifest maximum 256,000 bytes, sample CSV maximum 16,384 bytes, at most 64 rows. Missing or blocked network access produces HTTP **503** with no fabricated fallback observations.
- Public file catalog always excludes items marked `restricted` or not `visible`. No attempt to access controlled NASA human data.
- Category counts refer to **files**, not medical risk, astronaut count or biological measurement. The sample preview displays data *as published*, without a medical interpretation.

### Running both research views locally

On the v1.2 research branch, from the repo root (PowerShell):

```powershell
python -m pip install -r requirements.txt
$env:ARES_RESEARCH_ENABLED="1"
python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
```

In a second terminal:

```powershell
cd frontend
npm ci
npm run dev
```

Open `http://127.0.0.1:5173`. Switch to **NASA space biology** and select **Load NASA mouse sample table**. If access is blocked, the UI correctly reports the official resource unavailable. It must not show invented data.

For the MIT ECG experiment, install the separate optional tools into a research environment:

```powershell
python -m pip install -r requirements-research.txt
python -m scripts.prepare_research_ecg --download --acknowledge-license
```

Only run the latter command after reviewing the official source terms and citation. If the execution environment returns 403, try the **official public AWS distribution**
linked directly by [PhysioNet](https://physionet.org/content/mitdb/1.0.0/)
without changing the checksum or quality validation:

```powershell
python -m scripts.prepare_research_ecg --aws-public --acknowledge-license
```

Or use the official files and checksum manifest you obtained yourself, as documented in [RESEARCH_LAB.md](RESEARCH_LAB.md). Do not disable security protections or claim a measured F1 until actual MIT-BIH record 100 has been acquired and scored successfully.

**No MIT-BIH record 100 performance scores have yet been independently confirmed.** The four offline optional WFDB/NeuroKit integration tests use synthetic fixtures, not the published MIT waveform.

## Reproducible tests

```powershell
python -m pytest -q
cd frontend
npm test
npm run build
```

GitHub Actions also runs Python 3.12, 3.13, React tests and live frontend-backend integration. NASA endpoint tests use small **fictional mouse IDs**, mocking the HTTP source so CI does not rely on NASA uptime or copyrighted downloads. The live NASA network fetch, full official MIT benchmark, licensing review and human-spaceflight applicability remain separate checks.

## Scientific interpretation

The NASA OSDR study does not establish that a spaceflight crew member has an elevated ECG-related risk, and the MIT-BIH terrestrial ECG dataset does not provide evidence that an algorithm works in a spacecraft. ARES currently demonstrates software-level interoperability, provenance and reproducible signal-processing evaluation. Clinical and mission validation require separate data, methods and expert authorization.

Primary official sources: [NASA OSDR Public API](https://api.nasa.gov/), [OSD-87](https://osdr.nasa.gov/bio/repo/data/studies/OSD-87), [NASA controlled-access procedures](https://www.nasa.gov/reference/osdr-tutorials-requesting-controlled-access-datasets/), [MIT-BIH](https://physionet.org/content/mitdb/1.0.0/).
