"""Bounded read-only opt-in research API. No downloads or signal processing here."""
from __future__ import annotations
import json
import math
import os
from typing import Literal

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, ConfigDict, Field, FiniteFloat, ValidationError, model_validator

from src.ares_health import research

router = APIRouter()


class Point(BaseModel):
    sample: int = Field(ge=0, lt=research.SAMPLES)
    mv: FiniteFloat


class Metrics(BaseModel):
    tp: int = Field(ge=0, le=500)
    fp: int = Field(ge=0, le=500)
    fn: int = Field(ge=0, le=500)
    precision: FiniteFloat | None = Field(ge=0, le=1)
    recall: FiniteFloat | None = Field(ge=0, le=1)
    f1: FiniteFloat | None = Field(ge=0, le=1)
    mean_absolute_timing_error_ms: FiniteFloat | None = Field(ge=0, le=150)


class Match(BaseModel):
    reference_sample: int = Field(ge=research.GUARD, lt=research.SAMPLES-research.GUARD)
    detected_sample: int = Field(ge=research.GUARD, lt=research.SAMPLES-research.GUARD)
    absolute_error_ms: FiniteFloat = Field(ge=0, le=150)


class Discrepancy(BaseModel):
    type: Literal['FP', 'FN']
    sample: int = Field(ge=research.GUARD, lt=research.SAMPLES-research.GUARD)


class Artifact(BaseModel):
    model_config = ConfigDict(extra='forbid')
    schema_version: Literal['1.2-research']
    record: Literal['100']
    data_provenance: Literal['public_research_ecg']
    status: Literal['benchmarked', 'abstained']
    reasons: list[str] = Field(max_length=20)
    source: dict[str, str]
    protocol: dict[str, str | int]
    processing_versions: dict[str, str]
    quality: dict[str, str | list[str]]
    metrics: Metrics | None
    waveform: list[Point] = Field(max_length=1800)
    detected_peaks: list[Point] = Field(max_length=500)
    reference_peaks: list[Point] = Field(max_length=500)
    matches: list[Match] = Field(max_length=500)
    discrepancies: list[Discrepancy] = Field(max_length=1000)
    annotation_counts: dict[str, int] | None
    disclaimer: str
    acquisition: dict | None = None

    @model_validator(mode='after')
    def check_gate(self):
        if self.status == 'abstained':
            if self.metrics is not None or self.waveform or self.matches or self.discrepancies or self.detected_peaks or self.reference_peaks:
                raise ValueError('Abstention must withhold results.')
        else:
            if (self.metrics is None or not self.annotation_counts or not self.acquisition or
                self.quality.get('status') != 'engineering_gates_passed' or len(self.waveform) != 1800):
                raise ValueError('Incomplete benchmark artifact.')
            if (self.metrics.tp + self.metrics.fp != len(self.detected_peaks) or
                self.metrics.tp + self.metrics.fn != len(self.reference_peaks) or
                self.annotation_counts.get('scored_reference_beats') != len(self.reference_peaks) or
                self.metrics.tp != len(self.matches) or
                self.metrics.fp != sum(d.type == 'FP' for d in self.discrepancies) or
                self.metrics.fn != sum(d.type == 'FN' for d in self.discrepancies)):
                raise ValueError('Benchmark count mismatch.')
        if self.protocol != research.envelope('abstained', [])['protocol']:
            raise ValueError('Unsupported benchmark protocol.')
        return self


@router.get('/api/research/ecg/demo', response_model=Artifact, response_model_exclude_none=False)
def research_demo(request: Request, record: Literal['100'] = '100'):
    """Only serves a bounded previously prepared record-100 artifact on loopback."""
    if not request.client or request.client.host not in {'127.0.0.1', '::1'}:
        raise HTTPException(403, 'Research is localhost-only.')
    if os.environ.get('ARES_RESEARCH_ENABLED') != '1':
        raise HTTPException(503, 'Optional research mode is disabled. The synthetic mission demo remains available.')
    path = research.ARTIFACT_PATH
    try:
        if path.is_symlink() or path.stat().st_size > 1_000_000:
            raise ValueError('Unsafe artifact size/path.')
        with path.open('rb') as handle:
            raw = handle.read(1_000_001)
        if len(raw) > 1_000_000:
            raise ValueError('Oversized artifact.')
        def reject_constant(value):
            raise ValueError('Nonfinite JSON constant.')
        def finite_float(value):
            number = float(value)
            if not math.isfinite(number):
                raise ValueError('Nonfinite JSON number.')
            return number
        return Artifact.model_validate(json.loads(raw, parse_constant=reject_constant, parse_float=finite_float))
    except (OSError, ValueError, ValidationError, RecursionError):
        raise HTTPException(503, 'Research artifact missing or invalid. Run explicit official-record preparation; no download was attempted.') from None
