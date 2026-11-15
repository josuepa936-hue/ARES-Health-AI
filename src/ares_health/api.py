"""Local-only HTTP interface for the already-tested synthetic ARES engine.

Run with: python -m uvicorn src.ares_health.api:app --host 127.0.0.1 --port 8000
This service is NOT a medical API, an astronaut data feed, or a cloud service.
"""
from __future__ import annotations

from typing import Literal
import json
import math

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, ConfigDict

from src.ares_health.evidence import EVIDENCE
from src.ares_health.import_csv import MAX_CSV_BYTES, load_synthetic_csv
from src.ares_health.service import build_snapshot
from src.ares_health.synthetic import SCENARIOS, generate_scenario
from src.ares_health.timeline import build_timeline
from src.ares_health.mission import fictional_checkin, risk_guide
from src.ares_health.serve_ui import install_compiled_frontend
from src.ares_health.version import APP_VERSION
from src.ares_health.research_api import router as research_router
from src.ares_health.nasa_api import router as nasa_router
from src.ares_health.copilot_api import router as copilot_router

ScenarioId = Literal["stable", "heart_rate_shift", "sleep_shift", "incomplete"]
ReviewState = Literal["Pending review", "Reviewed in demo"]

app = FastAPI(
    title="ARES Health AI — Synthetic Mission API",
    description=(
        "Local educational software demo. Only fictional daily observations. "
        "No diagnosis, flight-medicine authorization, or NASA operational data."
    ),
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url=None,
)

# Local development UI only, not public internet or arbitrary hosted origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173", "http://127.0.0.1:5173",
        "http://localhost:3000", "http://127.0.0.1:3000",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "X-Synthetic-Attestation"],
)


def _finite_json_float(text: str) -> float:
    parsed = float(text)
    if not math.isfinite(parsed):
        raise ValueError("Nonfinite JSON number.")
    return parsed


def _reject_json_constant(_text: str) -> None:
    raise ValueError("Nonfinite JSON constant.")


@app.middleware("http")
async def checkin_json_guard(request: Request, call_next):
    """Reject nonstandard/nonfinite JSON before FastAPI error serialization.

    FastAPI's own 422 error may otherwise include Infinity in the rejected
    input, which cannot be encoded in strict JSON. This applies only to the
    tiny, expressly fictional check-in route. Other API behavior is unchanged.
    """
    if request.method == "POST" and request.url.path == "/api/mission/fictional-check-in":
        body = await request.body()
        if len(body) > 4096:
            return JSONResponse(status_code=413, content={"detail": "Fictional check-in exceeds 4 KB."})
        try:
            json.loads(body, parse_float=_finite_json_float,
                       parse_constant=_reject_json_constant)
        except (ValueError, UnicodeError, json.JSONDecodeError):
            return JSONResponse(
                status_code=422,
                content={"detail": "Invalid or nonfinite JSON for fictional check-in."},
            )
    return await call_next(request)


class ReviewRequest(BaseModel):
    """A fictional scenario reference, not an arbitrary health-data upload."""

    scenario: ScenarioId = "stable"
    seed: int = Field(default=2026, ge=0, le=999999)
    days: int = Field(default=21, ge=12, le=366)
    review_state: ReviewState = "Pending review"
    reviewer_note: str = Field(default="", max_length=500)


class FictionalCheckInRequest(BaseModel):
    """Explicitly fictional latest-day values, not a real health-data intake."""

    model_config = ConfigDict(extra="forbid")

    fictional_attestation: Literal[True]
    scenario: ScenarioId = "stable"
    seed: int = Field(default=2026, ge=0, le=999999)
    days: int = Field(default=21, ge=12, le=366)
    resting_hr_bpm: float = Field(gt=0, le=250, allow_inf_nan=False)
    sleep_hours: float = Field(ge=0, le=24, allow_inf_nan=False)
    activity_minutes: int = Field(ge=0, le=1440)
    concerns: list[Literal["fatigue", "headache", "dizziness", "sleepiness"]] = Field(
        default_factory=list, max_length=4
    )


@app.get("/api/mission/risk-guide")
def get_mission_risk_guide() -> dict:
    """Officially linked research background; no NASA risk score."""
    return risk_guide()


@app.post("/api/mission/fictional-check-in")
def submit_fictional_checkin(payload: FictionalCheckInRequest) -> dict:
    """Create a standalone evaluated snapshot, timeline and review in memory."""
    if len(set(payload.concerns)) != len(payload.concerns):
        raise HTTPException(422, "Do not repeat hypothetical concerns.")
    return fictional_checkin(
        scenario=payload.scenario, seed=payload.seed, days=payload.days,
        resting_hr_bpm=payload.resting_hr_bpm,
        sleep_hours=payload.sleep_hours,
        activity_minutes=payload.activity_minutes,
        concerns=payload.concerns,
    )


@app.get("/api/status")
def get_service_status() -> dict:
    """Service liveness, NOT a human-health assessment."""
    return {
        "status": "ready",
        "mode": "local-development",
        "data_provenance": "synthetic-only",
        "clinical_validation": False,
        "nasa_approved": False,
        "application_version": APP_VERSION,
    }


@app.get("/api/scenarios")
def list_scenarios() -> dict:
    return {
        "scenarios": [
            {"id": scenario_id, "label": label}
            for label, scenario_id in SCENARIOS.items()
        ],
        "data_provenance": "synthetic",
        "simulation_only": True,
    }


@app.get("/api/evidence")
def list_evidence() -> dict:
    from dataclasses import asdict
    return {
        "references": [asdict(item) for item in EVIDENCE],
        "usage": "Background research links only, not imported NASA/CSA health data.",
    }


@app.get("/api/demo")
def get_demo(
    scenario: ScenarioId = "stable",
    seed: int = Query(default=2026, ge=0, le=999999),
    days: int = Query(default=21, ge=12, le=366),
) -> dict:
    records = generate_scenario(scenario, seed=seed, days=days)
    return build_snapshot(records, scenario=scenario)


@app.get("/api/timeline")
def get_timeline(
    scenario: ScenarioId = "stable",
    seed: int = Query(default=2026, ge=0, le=999999),
    days: int = Query(default=21, ge=12, le=366),
) -> dict:
    """Return deterministic fictional observations and explainable demo events.

    Reuses domain validation and unchanged first-seven/latest-four rules.
    Quality failures suppress all trend interpretations; no clinical inference.
    """
    records = generate_scenario(scenario, seed=seed, days=days)
    return build_timeline(records, scenario=scenario)


@app.post("/api/review")
def export_fictional_review(request: ReviewRequest) -> dict:
    """Produce a report using the canonical engine and a fictional scenario."""
    records = generate_scenario(request.scenario, seed=request.seed, days=request.days)
    result = build_snapshot(
        records,
        scenario=request.scenario,
        include_report=True,
        review_state=request.review_state,
        reviewer_note=request.reviewer_note,
    )
    return result["review_report"]


@app.post("/api/synthetic-csv")
async def analyze_synthetic_csv(
    request: Request,
    x_synthetic_attestation: str | None = Header(
        default=None, alias="X-Synthetic-Attestation"
    ),
) -> dict:
    """Ingest a raw text/csv request, in memory, with a hard 1 MB stream limit.

    The required attestation is a user statement, never independent proof
    of synthetic provenance. No cloud transmission or filesystem storage.
    """
    if x_synthetic_attestation != "true":
        raise HTTPException(
            status_code=400,
            detail="A true X-Synthetic-Attestation header is required; never upload real medical data.",
        )
    media_type = request.headers.get("content-type", "").split(";", 1)[0].strip().lower()
    if media_type != "text/csv":
        raise HTTPException(status_code=415, detail="Expected Content-Type: text/csv.")

    length = request.headers.get("content-length")
    if length is not None:
        try:
            if int(length) > MAX_CSV_BYTES:
                raise HTTPException(status_code=413, detail="Synthetic CSV is larger than 1 MB.")
        except ValueError as exc:
            raise HTTPException(status_code=400, detail="Invalid Content-Length header.") from exc

    payload = bytearray()
    async for chunk in request.stream():
        if len(payload) + len(chunk) > MAX_CSV_BYTES:
            raise HTTPException(status_code=413, detail="Synthetic CSV is larger than 1 MB.")
        payload.extend(chunk)

    records, errors = load_synthetic_csv(bytes(payload))
    if errors or records is None:
        raise HTTPException(
            status_code=422,
            detail={"status": "CSV_REJECTED", "errors": errors},
        )
    snapshot = build_snapshot(
        records, scenario="uploaded_synthetic_csv", include_report=True
    )
    snapshot["mission_timeline"] = build_timeline(
        records, scenario="uploaded_synthetic_csv"
    )
    return snapshot


# Optional, read-only research namespace. Existing synthetic routes are unchanged.
app.include_router(research_router)
app.include_router(nasa_router)
app.include_router(copilot_router)

# Production demo mode: same-origin React + API at 127.0.0.1:8000.
# Dev mode still supports the independent Vite server on port 5173.
install_compiled_frontend(app)
