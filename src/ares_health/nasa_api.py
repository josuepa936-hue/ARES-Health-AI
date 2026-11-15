"""Opt-in, localhost-only NASA OSDR research routes; never clinical/crew data."""
from __future__ import annotations

import csv
import json
import os
from urllib.error import URLError
from fastapi import APIRouter, HTTPException, Request

from src.ares_health import nasa_osdr

router = APIRouter()


def _research_gate(request: Request) -> None:
    if not request.client or request.client.host not in {"127.0.0.1", "::1"}:
        raise HTTPException(403, "NASA research mode is local-only.")
    if os.environ.get("ARES_RESEARCH_ENABLED") != "1":
        raise HTTPException(503, "Optional research mode is disabled; the synthetic demo remains available.")


def _unavailable() -> HTTPException:
    return HTTPException(
        503,
        "Official NASA OSDR public dataset is currently inaccessible or invalid; "
        "no study result was invented. Check connectivity or NASA study availability.",
    )


@router.get("/api/research/nasa/study")
def nasa_study_catalog(request: Request) -> dict:
    """Read vetted public NASA OSD-87 file metadata over HTTPS on request."""
    _research_gate(request)
    try:
        return nasa_osdr.load_file_catalog()
    except (OSError, URLError, TimeoutError, ValueError, UnicodeError, TypeError, KeyError, json.JSONDecodeError):
        raise _unavailable() from None


@router.get("/api/research/nasa/sample-table")
def nasa_sample_table(request: Request) -> dict:
    """Preview a tiny public mouse experimental sample table, not a human record."""
    _research_gate(request)
    try:
        return nasa_osdr.load_sample_table()
    except (OSError, URLError, TimeoutError, ValueError, UnicodeError, TypeError, KeyError, csv.Error, json.JSONDecodeError):
        raise _unavailable() from None
