# Research sources and data provenance

## Official starting points

1. NASA challenge: https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/
2. NASA Human Research Roadmap risks: https://humanresearchroadmap.nasa.gov/risks/
3. NASA Human Research Roadmap evidence: https://humanresearchroadmap.nasa.gov/Evidence/
4. NASA Human Research Program spaceflight risks: https://www.nasa.gov/hrp/risks/
5. NASA OSDR overview: https://science.nasa.gov/biological-physical/data/osdr/
6. NASA OSDR FAQ: https://science.nasa.gov/reference/osdr-faq/
7. NASA OSDR data search: https://osdr.nasa.gov/bio/repo

## Important dataset caveat

OSDR is multi-modal, but much of its content is from organisms and biological experiments, not continuous wearable health monitoring from humans. Some human spaceflight data have controlled-access components. **Do not imply the proposed dashboard's sample heart-rate and sleep records come from NASA.** Mission records remain synthetic. Separate opt-in research modes use the versioned MIT-BIH terrestrial ECG source and NASA OSD-87 mouse-study catalog/sample table; neither feeds the mission engine. See [scientific evidence](SCIENTIFIC_EVIDENCE.md) and [research access and limits](MIT_NASA_RESEARCH.md). Availability and dataset terms must be verified separately before demonstrating or redistributing research data.

## Provenance policy

Every dataset or figure in the submission should disclose:
- Dataset name, source URL, author/agency, date accessed, license, and accession if relevant.
- Whether records are synthetic, open human data, analog study, or animal/model organism.
- Units, sampling frequency, missingness, and what use cases the data do **not** support.
- Any preprocessing, normalization, exclusions, and limitations.

## Scientific review policy

A NASA description of a health risk is **not** a validated clinical rule for astronaut monitoring. Source-backed claims and parameter choices must be documented separately.
