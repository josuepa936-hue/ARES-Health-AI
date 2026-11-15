"""Official NASA OSDR file-catalog and small mouse-research sample table.

This is an opt-in public *space-biology* research adapter, NOT astronaut health
telemetry. Exactly one NASA dataset is allowlisted; no user-supplied URLs,
public file uploads, diagnosis, risk scoring or bulk omics downloading.
"""
from __future__ import annotations

import csv
import io
import json
from collections import Counter
from urllib.parse import parse_qs, urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

STUDY = "OSD-87"
STUDY_ID = 87
STUDY_TITLE = (
    "Spaceflight effects on the mouse retina: Histological, gene expression "
    "and epigenetic changes after flight on STS-135"
)
STUDY_PAGE = "https://osdr.nasa.gov/bio/repo/data/studies/OSD-87"
MANIFEST_API = "https://osdr.nasa.gov/osdr/data/osd/files/87"
SAMPLE_FILENAME = "GLDS-87_array_SampleTable_GLmicroarray.csv"
ORIGIN = "https://osdr.nasa.gov"
MAX_MANIFEST_BYTES = 256_000
MAX_SAMPLE_BYTES = 16_384
DISCLAIMER = (
    "Public NASA research on mouse retinal tissue after spaceflight; NOT "
    "individual astronaut health data, medical validation, exposure "
    "dosimetry, clinical diagnosis or NASA operational endorsement."
)


# NASA's published public S3 distribution, never an arbitrary redirect target.
NASA_S3_HOSTS = frozenset({
    "nasa-osdr.s3.amazonaws.com",
    "nasa-osdr.s3.us-west-2.amazonaws.com",
})
# Real OSD-87 redirect observed from the official NASA API on Nov 15, 2026.
# Authorize exactly this small public sample file, not the entire S3 bucket.
GENELAB_SAMPLE_HOST = "genelab-repo-prod.s3.amazonaws.com"
GENELAB_SAMPLE_PATH = "/genelab-data/GLDS-87/array/GLDS-87_array_SampleTable_GLmicroarray.csv"
MAX_REDIRECTS = 2


def _approved_research_url(url: str, *, sample: bool) -> bool:
    """Only known NASA study resources or NASA-published S3 bucket paths."""
    p = urlsplit(url)
    if p.scheme != "https" or p.username or p.password or p.port or p.fragment:
        return False
    if p.hostname == "osdr.nasa.gov":
        if sample:
            return (
                p.path == "/geode-py/ws/studies/OSD-87/download"
                and parse_qs(p.query) == {"source": ["datamanager"], "file": [SAMPLE_FILENAME]}
            )
        return p.path == "/osdr/data/osd/files/87" and not p.query
    if not sample:
        return False
    if p.hostname in NASA_S3_HOSTS:
        # The final file name is fixed, and it must remain inside NASA's study.
        return (
            p.path.startswith("/OSD-87/")
            and p.path.rsplit("/", 1)[-1] == SAMPLE_FILENAME
        )
    if p.hostname == "s3.us-west-2.amazonaws.com":
        return (
            p.path.startswith("/nasa-osdr/OSD-87/")
            and p.path.rsplit("/", 1)[-1] == SAMPLE_FILENAME
        )
    if p.hostname == GENELAB_SAMPLE_HOST:
        return p.path == GENELAB_SAMPLE_PATH
    return False


def _bounded_download(url: str, limit: int) -> bytes:
    """Bounded official NASA fetch, including narrowly approved S3 redirects."""
    sample = url != MANIFEST_API
    if not _approved_research_url(url, sample=sample):
        raise ValueError("The research adapter only accesses explicitly approved NASA URLs.")
    class RestrictedRedirect(HTTPRedirectHandler):
        redirects = 0
        def redirect_request(self, req, fp, code, msg, headers, newurl):
            self.redirects += 1
            if self.redirects > MAX_REDIRECTS or not _approved_research_url(newurl, sample=sample):
                raise ValueError("NASA file download redirected to an unapproved destination.")
            return super().redirect_request(req, fp, code, msg, headers, newurl)

    req = Request(url, headers={
        "User-Agent": "ARES-Research-Prototype/1.2",
        "Accept": "text/csv" if sample else "application/json",
    })
    opener = build_opener(RestrictedRedirect())
    with opener.open(req, timeout=12) as response:
        final_url = response.geturl()
        if not _approved_research_url(final_url, sample=sample):
            raise ValueError("NASA file response came from an unapproved destination.")
        header_size = response.headers.get("Content-Length")
        if header_size is not None:
            try:
                if int(header_size) > limit:
                    raise ValueError("NASA OSDR response exceeds the byte limit.")
            except ValueError as exc:
                if "exceeds" in str(exc):
                    raise
                raise ValueError("Malformed NASA response Content-Length.") from exc
        data = response.read(limit + 1)
    if len(data) > limit:
        raise ValueError("NASA OSDR response exceeds the byte limit.")
    return data


def _official_download_url(relative: str, file_name: str) -> str:
    """Allow only the exact official per-study download route and file name."""
    parsed = urlsplit(relative)
    expected = "/geode-py/ws/studies/OSD-87/download"
    query = parse_qs(parsed.query, keep_blank_values=True)
    if (
        parsed.scheme or parsed.netloc or parsed.fragment or parsed.path != expected
        or query.get("source") != ["datamanager"] or query.get("file") != [file_name]
        or set(query) != {"source", "file"}
    ):
        raise ValueError("Unsafe NASA study file URL.")
    return ORIGIN + relative


def parse_file_catalog(raw: bytes) -> dict:
    """Defensive parser; publish only visible, unrestricted file metadata."""
    def nonfinite(value: str) -> None:
        raise ValueError("Nonfinite JSON constant.")
    payload = json.loads(raw.decode("utf-8-sig"), parse_constant=nonfinite)
    if not isinstance(payload, dict) or payload.get("success") is not True:
        raise ValueError("NASA returned an invalid file catalog.")
    studies = payload.get("studies")
    study = studies.get(STUDY) if isinstance(studies, dict) else None
    files = study.get("study_files") if isinstance(study, dict) else None
    count = study.get("file_count") if isinstance(study, dict) else None
    if not isinstance(files, list) or len(files) > 25 or type(count) is not int or count < len(files):
        raise ValueError("Malformed or truncated NASA study manifest.")
    public_files = []
    for file in files:
        if not isinstance(file, dict):
            raise ValueError("Malformed NASA file entry.")
        # Restrictions and visibility default to denied on missing metadata.
        if file.get("restricted") is not False or file.get("visible") is not True:
            continue
        name, category, size, path = (
            file.get("file_name"), file.get("category"), file.get("file_size"), file.get("remote_url")
        )
        if (
            not isinstance(name, str) or not name.startswith("GLDS-87_") and not name.startswith("OSD-87_")
            or not isinstance(category, str) or not 0 < len(category) < 120
            or type(size) is not int or size < 0 or size > 1_000_000_000
            or not isinstance(path, str) or len(path) > 700
        ):
            raise ValueError("Invalid NASA public file metadata.")
        url = _official_download_url(path, name)
        public_files.append({
            "file_name": name,
            "category": category,
            "size_bytes": size,
            "file_url": url,
        })
    categories = Counter(file["category"] for file in public_files)
    return {
        "schema_version": "1.2-osdr",
        "accession": STUDY,
        "study_title": STUDY_TITLE,
        "source_organization": "NASA Open Science Data Repository",
        "study_url": STUDY_PAGE,
        "api_url": MANIFEST_API,
        "organism": "Mus musculus (mouse)",
        "tissue": "retina",
        "mission_context": "STS-135",
        "data_provenance": "public_space_biology_research",
        "file_catalog_count": count,
        "visible_public_files": len(public_files),
        "file_categories": [
            {"category": category, "count": amount} for category, amount in sorted(categories.items())
        ],
        "files": public_files,
        "sample_preview_available": any(
            file["file_name"] == SAMPLE_FILENAME and file["size_bytes"] <= MAX_SAMPLE_BYTES
            for file in public_files
        ),
        "disclaimer": DISCLAIMER,
    }


def load_file_catalog() -> dict:
    """Actual NASA HTTP catalog request; no cache or invented offline result."""
    return parse_file_catalog(_bounded_download(MANIFEST_API, MAX_MANIFEST_BYTES))


def parse_sample_table(raw: bytes, catalog: dict) -> dict:
    """Read the published small experimental sample table without deriving health metrics."""
    if not catalog.get("sample_preview_available") or catalog.get("accession") != STUDY:
        raise ValueError("Approved public table absent from NASA catalog.")
    text = raw.decode("utf-8-sig")
    if "\x00" in text:
        raise ValueError("Binary content is not a sample CSV.")
    reader = csv.DictReader(io.StringIO(text, newline=""), strict=True)
    fields = reader.fieldnames
    if not fields or not (1 <= len(fields) <= 20) or any(not x or len(x) > 100 for x in fields):
        raise ValueError("Invalid NASA sample table columns.")
    if len(set(fields)) != len(fields):
        raise ValueError("Duplicate NASA sample table columns.")
    rows: list[dict[str, str]] = []
    for row in reader:
        if len(rows) >= 64 or None in row or any(value is None or len(value) > 256 for value in row.values()):
            raise ValueError("Malformed or oversized NASA sample table.")
        rows.append(row)
    if not rows:
        raise ValueError("NASA sample table contains no rows.")
    return {
        "schema_version": "1.2-osdr-samples",
        "accession": STUDY,
        "file_name": SAMPLE_FILENAME,
        "data_provenance": "public_space_biology_research",
        "sample_count": len(rows),
        "column_names": fields,
        "rows": rows,
        "reference_url": STUDY_PAGE,
        "disclaimer": DISCLAIMER + " Values shown are the published table, not clinical observations.",
    }


def load_sample_table() -> dict:
    """Opt-in public CSV preview, after checking NASA current access metadata."""
    catalog = load_file_catalog()
    target = next(
        (entry for entry in catalog["files"] if entry["file_name"] == SAMPLE_FILENAME), None
    )
    if not target or target["size_bytes"] > MAX_SAMPLE_BYTES:
        raise ValueError("Approved public NASA sample CSV is unavailable.")
    return parse_sample_table(_bounded_download(target["file_url"], MAX_SAMPLE_BYTES), catalog)
