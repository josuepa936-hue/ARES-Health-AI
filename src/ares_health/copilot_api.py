"""Bounded, stateless offline copilot routes; assessments are always recalculated."""

from __future__ import annotations
import json
import math
from fastapi import APIRouter, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.routing import APIRoute

from src.ares_health.copilot import answer, canonical_context, comprehensive_report
from src.ares_health.copilot_models import CopilotRequest, ComprehensiveRequest

MAX_BODY = 1_300_000


def finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise ValueError("Nonfinite JSON number.")
    return number


def reject_constant(_value):
    raise ValueError("Nonfinite JSON constant.")


class BoundedCopilotRoute(APIRoute):
    def get_route_handler(self):
        handler = super().get_route_handler()

        async def bounded(request: Request):
            if (
                request.headers.get("content-type", "").split(";")[0].strip().lower()
                != "application/json"
            ):
                raise HTTPException(415, "Expected application/json.")
            chunks = []
            size = 0
            async for chunk in request.stream():
                size += len(chunk)
                if size > MAX_BODY:
                    raise HTTPException(
                        413, "Copilot JSON exceeds its bounded input limit."
                    )
                chunks.append(chunk)
            body = b"".join(chunks)
            try:
                json.loads(
                    body, parse_float=finite_float, parse_constant=reject_constant
                )
            except (ValueError, UnicodeError, RecursionError):
                raise HTTPException(422, "Invalid or nonfinite copilot JSON.") from None
            # Cache the bounded body for FastAPI's normal typed Body parsing. This
            # route-local Request cache does not affect any existing API route.
            request._body = body
            try:
                return await handler(request)
            except RequestValidationError as exc:
                raise HTTPException(
                    422,
                    detail=[
                        {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
                        for e in exc.errors()
                    ],
                ) from None

        return bounded


router = APIRouter(route_class=BoundedCopilotRoute)


def checked_context(payload):
    try:
        context = canonical_context(payload.context)
    except ValueError as exc:
        raise HTTPException(422, str(exc)) from None
    if (
        payload.expected_context_ref
        and payload.expected_context_ref != context["context_ref"]
    ):
        raise HTTPException(
            409,
            "Mission context changed. Reset conversation/review and request a new briefing.",
        )
    return context


@router.post("/api/mission/copilot")
def mission_copilot(payload: CopilotRequest) -> dict:
    return answer(checked_context(payload), payload.question, payload.turn)


@router.post("/api/mission/comprehensive-report")
def mission_comprehensive_report(payload: ComprehensiveRequest) -> dict:
    return comprehensive_report(checked_context(payload), payload)
