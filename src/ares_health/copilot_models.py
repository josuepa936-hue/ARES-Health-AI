"""Bounded synthetic context and explicit user-controlled review contracts."""

from __future__ import annotations
from datetime import datetime, timezone
import re
from typing import Annotated, Literal
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictBool,
    StrictInt,
    field_validator,
    model_validator,
)

ScenarioId = Literal["stable", "heart_rate_shift", "sleep_shift", "incomplete"]
WorkflowState = Literal[
    "PENDING_REVIEW", "IN_PROGRESS", "AWAITING_AUTHORIZED_REVIEW", "DOCUMENTED"
]
ReviewAction = Literal[
    "source_units", "timestamp_context", "mission_protocol", "authorized_review"
]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class Attested(StrictModel):
    fictional_attestation: Literal[True]

    @field_validator("fictional_attestation", mode="before")
    @classmethod
    def true_boolean(cls, value):
        if value is not True:
            raise ValueError("Explicit fictional-data attestation is required.")
        return value


class CheckInValues(Attested):
    resting_hr_bpm: float = Field(gt=0, le=250, allow_inf_nan=False)
    sleep_hours: float = Field(ge=0, le=24, allow_inf_nan=False)
    activity_minutes: StrictInt = Field(ge=0, le=1440)
    concerns: list[Literal["fatigue", "headache", "dizziness", "sleepiness"]] = Field(
        default_factory=list, max_length=4
    )

    @field_validator("concerns")
    @classmethod
    def unique_concerns(cls, values):
        if len(values) != len(set(values)):
            raise ValueError("Repeated hypothetical concern.")
        return values


class ScenarioContext(StrictModel):
    kind: Literal["scenario"]
    scenario: ScenarioId
    seed: StrictInt = Field(default=2026, ge=0, le=999999)
    days: StrictInt = Field(default=21, ge=12, le=366)
    check_in: CheckInValues | None = None


class CsvContext(Attested):
    kind: Literal["synthetic_csv"]
    csv: str = Field(max_length=1_000_000, strict=True)


ContextInput = Annotated[ScenarioContext | CsvContext, Field(discriminator="kind")]


class Question(StrictModel):
    turn: StrictInt = Field(ge=1, le=20)
    question: str = Field(min_length=1, max_length=240, strict=True)

    @field_validator("question")
    @classmethod
    def nonblank_question(cls, value):
        if not value.strip():
            raise ValueError("A recorded conversation question must not be blank.")
        return value


class CopilotRequest(StrictModel):
    context: ContextInput
    expected_context_ref: str | None = Field(
        default=None, pattern=r"^ctx-[0-9a-f]{64}$"
    )
    question: str = Field(default="", max_length=240, strict=True)
    turn: StrictInt = Field(default=0, ge=0, le=20)

    @model_validator(mode="after")
    def question_turn(self):
        if bool(self.question.strip()) != bool(self.turn):
            raise ValueError("Briefing uses turn 0; questions use turns 1–20.")
        return self


class AuditEvent(StrictModel):
    sequence: StrictInt = Field(ge=1, le=64)
    # Optional solely to accept old v1.5 export clients. New UI always records
    # the user's device UTC at click time; this is NOT a trusted server clock.
    recorded_at_utc: str | None = Field(default=None, max_length=32, strict=True)
    action: Literal[
        "source_units",
        "timestamp_context",
        "mission_protocol",
        "authorized_review",
        "review_state",
        "note",
    ]
    checked: StrictBool | None = None
    review_state: WorkflowState | None = None
    note: str | None = Field(default=None, max_length=500, strict=True)

    @field_validator("recorded_at_utc")
    @classmethod
    def valid_client_utc(cls, value):
        if value is None:
            return None
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{1,6})?Z", value):
            raise ValueError("Audit time must be a UTC ISO-8601 string ending in Z.")
        try:
            date = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            raise ValueError("Invalid UTC audit timestamp.") from None
        if date.tzinfo != timezone.utc:
            raise ValueError("Audit timestamp must be UTC.")
        return value

    @model_validator(mode="after")
    def event_shape(self):
        expected = (
            "review_state"
            if self.action == "review_state"
            else "note" if self.action == "note" else "checked"
        )
        for field in ("checked", "review_state", "note"):
            if (getattr(self, field) is not None) != (field == expected):
                raise ValueError("Audit event payload does not match action.")
        return self


class ComprehensiveRequest(Attested):
    context: ContextInput
    expected_context_ref: str = Field(pattern=r"^ctx-[0-9a-f]{64}$")
    questions: list[Question] = Field(default_factory=list, max_length=20)
    audit_log: list[AuditEvent] = Field(default_factory=list, max_length=64)

    @model_validator(mode="after")
    def ordered_events(self):
        if [event.sequence for event in self.audit_log] != list(
            range(1, len(self.audit_log) + 1)
        ):
            raise ValueError("Audit sequences must be contiguous from 1.")
        if [turn.turn for turn in self.questions] != list(
            range(1, len(self.questions) + 1)
        ):
            raise ValueError("Conversation turns must be contiguous from 1.")
        # Old clients can omit timestamps. Any timestamps actually supplied
        # must preserve user-entered event order, not invented server time.
        stamps = [
            datetime.fromisoformat(event.recorded_at_utc.replace("Z", "+00:00"))
            for event in self.audit_log if event.recorded_at_utc is not None
        ]
        if stamps != sorted(stamps):
            raise ValueError("Audit timestamps must be nondecreasing.")
        return self
