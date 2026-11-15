# ARES v1.2 Biomedical Research Lab — isolated future research

This optional branch benchmarks a detector on a specified public **terrestrial**
ECG case. It is separate from the synthetic mission workflow, not medical
validation, NASA endorsement, astronaut monitoring or spaceflight qualification.
No diagnosis, arrhythmia classification, risk/stress score, HRV interpretation,
treatment recommendation, volunteer test or personal ECG upload is implemented.
The verified v1.1 mission workflow remains the hackathon submission fallback.

## Source and current verification status

Approved source: PhysioNet **MIT-BIH Arrhythmia Database 1.0.0**, record **100**,
channel **MLII**, **360 Hz**. The source database supplies expert-reviewed beat
annotations (`100.atr`). We use their heartbeat positions as a detector reference,
not as disease labels. No subject demographics, header comments, medications or
annotation class labels are exported. Source approval is limited to this case;
it is not permission for arbitrary patient records.

**Public-record benchmark is not yet verified in this environment.** PhysioNet
HTTPS requests were denied by the environment proxy (CONNECT HTTP 403). No public
record was downloaded or scored, and no record-100 TP/FP/FN results are claimed.
The preparation attempt wrote an explicit abstention artifact with no scores.
A GitHub WFDB test-data header was inspected during investigation; it contained
parser-test modifications and was **not** used as the approved dataset. Self-
contained synthetic WFDB/ECG fixtures exercise actual library processing, but
are never described as evidence from the public record.

To complete source verification, allow `physionet.org` through environment
network settings, review the current official source/license page, and rerun
preparation, or supply the official files and official checksum manifest locally.
Do not weaken TLS, file checksums, calibration checks or signal-quality gates.
Public record/license review and a measured benchmark remain draft-PR blockers.

## Reproducible opt-in preparation

Research tools are optional; normal installation and API startup do not download
ECG files or import WFDB/NeuroKit. Normal `requirements.txt` remains unchanged.
Use a separate environment when protecting the submission installation:

```powershell
py -m venv .venv-research
.\.venv-research\Scripts\python.exe -m pip install -r requirements-research.txt
# Only after reviewing source terms/citation and authorizing this research use:
.\.venv-research\Scripts\python.exe -m scripts.prepare_research_ecg --download --acknowledge-license
```

For official files already downloaded by the operator:

```powershell
.\.venv-research\Scripts\python.exe -m scripts.prepare_research_ecg --official-files C:\approved\mitdb-1.0.0 --acknowledge-license
```

Only `100.hea`, `100.dat`, `100.atr`, and `SHA256SUMS.txt` are read. All must be
regular bounded files. The script reads fixed HTTPS URLs, bounds each response,
verifies all three data-file SHA-256 hashes against the official manifest, and
records hashes including the manifest hash. A supplied local manifest verifies
integrity relative to that manifest, **not independent authenticity**; acquisition
metadata states this limitation. No mirror or arbitrary remote URL is accepted.
A TLS-authenticated official download and its matching manifest are the intended
source-authentication path, not a cryptographic signature.

WFDB verifies record name-specific metadata (650000 samples, two channels MLII/V5,
360 Hz, mV units, format 212, fixed data filename) before waveform allocation.
Both digital signal checksums are compared modulo 65536, accommodating signed
and unsigned header representations without bypassing verification. Calibration
gains must be finite and positive. Missing files, malformed metadata, corrupted
bytes or library failures abstain. Failed preparation replaces any stale success
artifact. Data obtained by the download option lives in a temporary directory;
only the processed artifact is retained in ignored `.ares-research/benchmark.json`.
No waveform, annotation file or measured artifact is committed or redistributed.

Pinned processing tools: **WFDB 4.3.1**, **NeuroKit2 0.2.12**. Compatible baseline
NumPy/SciPy versions remain constrained by the existing requirements; exact
Python, WFDB, NeuroKit2, NumPy and SciPy versions are recorded in each artifact.
Repeat within the same environment for bitwise JSON reproducibility; pin those
recorded transitive versions too before cross-environment comparisons. There is
no timestamp, randomness or user-adjustable processing parameter in the artifact.

## Fixed segment, signal gates and exclusions

- Read/calibrate full record with WFDB, then process the **first 60 seconds**:
  original samples `[0, 21600)` from channel MLII only. No resampling or missing-
  value imputation. No HRV is computed.
- Require exactly 360 Hz, one channel and 21600 finite mV samples.
- Abstain if any absolute sample exceeds **10 mV**, any aligned one-second window
  has SD below **0.01 mV**, or there are 90 consecutive equal sample differences
  (a constant plateau of at least 250 ms).
- Abstain if 49–51 Hz plus 59–61 Hz power exceeds **40%** of 0.5–100 Hz power
  using SciPy's periodogram. These conservative engineering exclusions are **not
  validated clinical quality limits**, do not catch every artifact, and may
  reject usable signals. The mission thresholds are untouched.
- Clean with `nk.ecg_clean(method='neurokit', sampling_rate=360)` and detect with
  `nk.ecg_peaks(method='neurokit', correct_artifacts=False)`. Nonfinite cleaned
  output, malformed candidates or more than 500 scored reference/candidate peaks
  abstain. Candidate/reference caps bound resources, not physiological normality.
- Exclude the first/last second from scoring to reduce filter/detector edge effects:
  half-open original sample interval **[360, 21240)**. Both reference and detector
  candidates are cropped by this same interval; no cross-boundary matches occur.
  Counts of unscored boundary beats and candidates are returned separately. This
  guard does not prove that all edge effects have disappeared.
- Count only WFDB heartbeat symbols
  `N L R B A a J S V r F e j n E / f Q`. They are selection codes, never predicted
  classes. Rhythm changes (`+`), comments, noise markers (`~`), learning (`?`) and
  all other symbols are excluded and counted. Annotation timestamps must be
  valid segment indices; heartbeat references must be unique and ordered.

## Matching protocol and metrics

Indices remain in **original 360 Hz samples**. An inclusive tolerance of **54
samples = ±150 ms** is selected for this engineering comparison, not as a clinical
standard. Walk sorted reference and candidate lists from earliest to latest:
match the earliest eligible pair, otherwise count the earlier out-of-tolerance
candidate as FP or reference as FN. Each reference/candidate is consumed once.
This ordered interval matching maximizes match count, but does **not** optimize
nearest-neighbor timing or minimize timing error. Duplicate detector candidates
can become extra FP; reference duplicates are invalid. Ties follow sample order.

- TP: matched pairs. FP: unmatched candidates. FN: unmatched reference heartbeats.
- Precision: `TP/(TP+FP)`. Recall: `TP/(TP+FN)` for this annotation selection only.
- F1: `2TP/(2TP+FP+FN)`.
- Mean absolute timing error: mean `abs(detected-reference)*1000/360` over TP only.
- Undefined denominators or no matched timing pairs return JSON `null`, not NaN
  or invented zero. Zero matches with a valid reference is a measured detector
  failure (recall/F1 zero), not reassurance. A missing reference abstains.
- `annotation_counts` accounts for all annotations in the 60-second segment,
  excluded non-beat symbols, boundary beats/candidates, and scored reference beats.
  The discrepancy table lists FP/FN **sample positions**, not clinical labels.

No specificity or single “medical accuracy” percentage is reported. Results are
specific to this record/channel/segment/algorithm/protocol and cannot estimate
clinical efficacy, generalization, health state or astronaut applicability.

## Bounded optional HTTP/view

```powershell
$env:ARES_RESEARCH_ENABLED="1"
.\.venv-research\Scripts\python.exe -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
# Separate terminal, from frontend/: npm install; npm run dev
```

Open the frontend's **Optional research lab** button. It loads only on explicit
selection, labels `public_research_ecg` prominently, displays source/version,
quality/abstention, detector/reference markers, FP/FN discrepancies and measured
metrics. Returning to **Synthetic mission demo** preserves its separate state.
No public-research waveform can enter the synthetic CSV or mission endpoints.

`GET /api/research/ecg/demo?record=100` is read-only and opt-in. It refuses remote
clients even when enabled, reads only the fixed local artifact (max 1 MB), rejects
malformed/nonfinite/inconsistent artifacts, and never performs acquisition or
signal processing. It returns at most 1800 raw waveform display samples (every
12th sample, a visual decimation **not an analysis signal**), 500 markers per
set, 500 matches and 1000 discrepancies. Scores always use the full-resolution
signal; markers retain exact original indices and amplitudes. Sparse display
can miss morphology and is unsuitable for interpreting ECG shape. There is no
upload, arbitrary path/URL, duration parameter, remote service or medical action.
The operator must still bind both unauthenticated services to loopback.

## Evidence, citations and license review

- Moody GB, Mark RG. *The impact of the MIT-BIH Arrhythmia Database*. IEEE Eng Med
  Biol Mag. 2001;20(3):45–50. https://doi.org/10.1109/51.932724
- Goldberger AL et al. *PhysioBank, PhysioToolkit, and PhysioNet: Components of a
  New Research Resource for Complex Physiologic Signals*. Circulation.
  2000;101:e215–e220. https://doi.org/10.1161/01.CIR.101.23.e215
- Dataset/version: https://physionet.org/content/mitdb/1.0.0/
  and https://doi.org/10.13026/C2F305
- WFDB: https://wfdb.io/software/python.html
- NeuroKit ECG: https://neuropsychology.github.io/NeuroKit/functions/ecg.html
- NASA OSDR context: https://science.nasa.gov/biological-physical/data/osdr/
  (not a data source for this ECG benchmark, not endorsement).

**License review remains pending direct source access.** Consult the current
license/attribution and usage requirements on the official versioned dataset
page before running preparation or redistributing any derived waveform. The
acknowledgement flag records an operator declaration, not automated legal review.
Library licensing is separate from dataset licensing; preserve their upstream
notices. No public data are bundled in the PR and no claim of completed source
license verification is made here.

## Validation and delivery gate

Run the existing suite without optional dependencies: `python -m pytest -q`.
With research tools installed, also run
`python -m pytest -q optional_checks/ecg_integration.py`.
These offline integrations write small synthetic test records through real WFDB
and run real NeuroKit cleaning/detection. They verify processing mechanics and
reproducibility, **not** public-record performance. Frontend tests/build and the
existing 8 live synthetic HTTP checks remain required. CI adds a separate offline
research job; mandatory CI never downloads PhysioNet. Official preparation is a
separate opt-in acquisition/benchmark check requiring source access.

Software tests establish behavior. Algorithm benchmarking measures a detector
against selected reference annotations. Neither establishes clinical validation
or spaceflight applicability. Keep this branch/draft PR as future research until
official source/license review and a measured record-100 run are completed; do
not delay the hackathon submission or replace the verified mission baseline.

### Local verification evidence

On Python 3.12 / Node 24, the full default Python suite passed **224 tests**
(including all original 177). The separate actual-library offline suite passed
**4 tests**, React passed **37 tests**, and live Vite/FastAPI HTTP checks passed
**9 tests** (including all original 8). TypeScript/production build, compileall,
pip check and diff checks passed. Known dependency deprecations (Starlette/httpx,
NeuroKit's SciPy import) remain warnings. These local checks do not establish that
a remote GitHub Actions matrix has completed; GitHub API access is denied here.
