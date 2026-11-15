"""Offline deterministic explanations. No model, network, storage or medical inference."""

from __future__ import annotations
from dataclasses import asdict
import copy
import hashlib
import json
import unicodedata

from src.ares_health.copilot_models import (
    CsvContext,
    ScenarioContext,
    ComprehensiveRequest,
)
from src.ares_health.evidence import EVIDENCE
from src.ares_health.import_csv import load_synthetic_csv
from src.ares_health.mission import fictional_checkin, risk_guide
from src.ares_health.service import build_snapshot
from src.ares_health.synthetic import generate_scenario
from src.ares_health.timeline import build_timeline

ENGINE = "deterministic-offline"
LIMITATIONS = [
    "Deterministic explanatory rules, not a generative model or LLM.",
    "Synthetic demonstration only; no diagnosis, treatment, triage or medical clearance.",
    "NASA references are research context, not validation or operational instructions.",
    "Review states/actions are user-controlled fictional records, never clinical authorization.",
]
ACTIONS = ["source_units", "timestamp_context", "mission_protocol", "authorized_review"]
SUGGESTIONS = [
    "What changed?",
    "Compared with what baseline?",
    "Which dates and values support this?",
    "Why can't this be interpreted?",
    "What should I review next?",
    "What is the relevant NASA hazard background?",
    "How do I document review?",
    "What is still not monitored?",
]
UNITS = {"resting_hr_bpm": "bpm", "sleep_hours": "hours", "activity_minutes": "min/day"}


def canonical_context(source: ScenarioContext | CsvContext) -> dict:
    """Rebuild from controlled inputs; never trust an uploaded assessment or answer."""
    if isinstance(source, CsvContext):
        frame, errors = load_synthetic_csv(source.csv.encode("utf-8"))
        if errors or frame is None:
            raise ValueError("CSV_REJECTED: " + "; ".join(errors))
        snapshot = build_snapshot(
            frame, scenario="uploaded_synthetic_csv", include_report=True
        )
        timeline = build_timeline(frame, scenario=snapshot["scenario"])
    elif source.check_in:
        values = source.check_in.model_dump(exclude={"fictional_attestation"})
        snapshot = fictional_checkin(
            scenario=source.scenario, seed=source.seed, days=source.days, **values
        )
        timeline = snapshot["mission_timeline"]
    else:
        frame = generate_scenario(source.scenario, seed=source.seed, days=source.days)
        snapshot = build_snapshot(frame, scenario=source.scenario, include_report=True)
        timeline = build_timeline(frame, scenario=snapshot["scenario"])
    digest = hashlib.sha256(
        json.dumps(
            {"snapshot": snapshot, "timeline": timeline},
            sort_keys=True,
            allow_nan=False,
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    return {"snapshot": snapshot, "timeline": timeline, "context_ref": "ctx-" + digest}


def normalize(question: str) -> str:
    return "".join(
        c
        for c in unicodedata.normalize("NFKD", question.casefold())
        if not unicodedata.combining(c)
    )


def parse_intent(question: str) -> str:
    """Conservative bounded English/Spanish keyword parser; unsupported questions abstain.

    Unsafe/instruction-override vocabulary takes precedence. This is not a general
    conversational model or a comprehensive semantic safety classifier.
    """
    text = normalize(question)
    if not text.strip():
        return "briefing"
    if any(
        word in text
        for word in (
            "diagnos",
            "treat",
            "medicat",
            "dose",
            "dosis",
            "tratam",
            "urgenc",
            "emergency",
            "triage",
            "healthy",
            "medically safe",
            "fitness",
            "clearance",
            "ignore",
            "override",
            "system prompt",
            "ignora",
            "anula",
            "saludable",
            "medicamente",
            "autoriza",
            "medicacion",
        )
    ):
        return "refusal"
    categories = [
        ("unmonitored", ("not monitored", "unmonitored", "no monitore", "no se mide")),
        ("document_review", ("document", "registro", "registrar", "audit")),
        ("hazards", ("nasa", "hazard", "spaceflight", "peligro")),
        (
            "quality",
            (
                "missing",
                "can't",
                "cannot",
                "quality",
                "verify",
                "blocked",
                "calidad",
                "falta",
                "bloque",
                "no puede",
            ),
        ),
        ("baseline", ("baseline", "reference", "compar", "referencia")),
        (
            "observations",
            (
                "dates",
                "values",
                "support",
                "evidence",
                "fechas",
                "valores",
                "evidencia",
            ),
        ),
        ("changes", ("changed", "change", "cambio", "cambi")),
        ("next_review", ("next", "review", "siguiente", "revisar")),
    ]
    for intent, words in categories:
        if any(word in text for word in words):
            return intent
    return "unsupported"


def evidence(context: dict, include_windows: bool) -> list[dict]:
    snapshot, timeline = context["snapshot"], context["timeline"]
    refs = []
    if snapshot["assessment"] in {"DATA_QUALITY_BLOCKED", "INSUFFICIENT_DATA"}:
        for index, text in enumerate(
            snapshot["quality_issues"] + snapshot["analysis_limitations"]
        ):
            refs.append(
                {
                    "id": f"quality:{index}",
                    "kind": "quality",
                    "text": text,
                    "timestamp_utc": None,
                }
            )
        return refs
    if include_windows:
        observations = snapshot["observations"]
        ids = {
            event["observation_index"]: event["id"]
            for event in timeline["events"]
            if event["type"] == "observation"
        }
        for index in [*range(7), *range(len(observations) - 4, len(observations))]:
            for metric, unit in UNITS.items():
                row = observations[index]
                refs.append(
                    {
                        "id": f"observation:{index}:{metric}",
                        "kind": "observation",
                        "timestamp_utc": row["timestamp_utc"],
                        "metric": metric,
                        "value": row[metric],
                        "unit": unit,
                        "window": "reference" if index < 7 else "recent",
                        "timeline_id": ids[index],
                    }
                )
        for metric, rule in snapshot["methodology"]["illustrative_rules"].items():
            refs.append(
                {
                    "id": f"rule:{metric}:mean_difference",
                    "kind": "rule",
                    "metric": metric,
                    "text": "Inclusive illustrative absolute-mean-difference rule; not clinical.",
                    **rule,
                }
            )
    return refs


def source_refs() -> list[dict]:
    return [
        {
            "id": f'nasa-hazard:{risk["id"]}',
            "kind": "source",
            "title": risk["title"],
            "url": risk["reference_url"],
            "text": risk["spaceflight_context"] + " " + risk["ares_current_coverage"],
        }
        for risk in risk_guide()["risks"]
    ]


def comparisons(context: dict) -> list[dict]:
    snapshot = context["snapshot"]
    if snapshot["assessment"] in {"DATA_QUALITY_BLOCKED", "INSUFFICIENT_DATA"}:
        return []
    obs = snapshot["observations"]
    return [
        {
            key: signal[key]
            for key in (
                "metric",
                "label",
                "unit",
                "baseline_mean",
                "recent_mean",
                "delta",
            )
        }
        | {
            "reference_start_utc": obs[0]["timestamp_utc"],
            "reference_end_utc": obs[6]["timestamp_utc"],
            "recent_start_utc": obs[-4]["timestamp_utc"],
            "recent_end_utc": obs[-1]["timestamp_utc"],
        }
        for signal in snapshot["descriptive_signals"]
    ]


def answer(context: dict, question: str = "", turn: int = 0) -> dict:
    snapshot = context["snapshot"]
    intent = parse_intent(question)
    blocked = snapshot["assessment"] in {"DATA_QUALITY_BLOCKED", "INSUFFICIENT_DATA"}
    refs = []
    if intent == "refusal":
        text = (
            "I cannot provide diagnosis, treatment, triage, medical clearance or override data quality. "
            "Use approved mission protocols and authorized flight-medical personnel; ARES does not supply those protocols."
        )
    elif intent == "unsupported":
        text = "This offline deterministic copilot supports only the listed mission-review questions. Choose a suggested question; no unsupported facts are generated."
    elif intent == "unmonitored":
        text = (
            "Only fictional resting heart rate, sleep duration and activity minutes are observed. "
            "Organ health, radiation, cabin conditions, mental health and medical fitness are not monitored. "
            "MIT-BIH terrestrial ECG and NASA mouse-retina OSD-87 research are separate sources, not crew measurements."
        )
        refs = source_refs()
    elif intent == "document_review":
        text = (
            "Confirm fictional review actions manually and choose PENDING_REVIEW, IN_PROGRESS, "
            "AWAITING_AUTHORIZED_REVIEW or DOCUMENTED. States never alter analysis or grant medical authorization. "
            "Notes and audit events stay in browser memory until explicit export; reload resets them."
        )
    elif intent == "hazards":
        text = (
            "NASA background: "
            + "; ".join(
                r["title"] + ": " + r["ares_current_coverage"]
                for r in risk_guide()["risks"]
            )
            + " These are not individual hazard scores or clinical guidance."
        )
        refs = source_refs()
    elif blocked:
        text = (
            "Trend interpretation is withheld. "
            + " ".join(snapshot["quality_issues"] + snapshot["analysis_limitations"])
            + " Verify the original fictional source, units and UTC timestamps; correct records outside ARES and resubmit. "
            "No reference/recent averages, reassuring health conclusions or comparison are available."
        )
        refs = evidence(context, False)
    elif intent == "quality":
        text = "The active dataset has no blocking quality finding. This is a software input check, not evidence of health or clinical signal quality. Review source, units and UTC timestamps."
        refs = evidence(context, True)
    elif intent == "next_review":
        text = (
            snapshot["guidance"]["meaning"]
            + " "
            + " ".join(snapshot["guidance"]["review_steps"])
        )
        refs = evidence(context, True) + source_refs()
    else:
        prefix = (
            "Change flagged for demonstration review, not diagnosis or medical risk grading. "
            if snapshot["assessment"] == "CHANGE_FOR_REVIEW"
            else "No demonstration rule triggered; this is not medical clearance. "
        )
        if intent == "briefing":
            text = (
                prefix
                + f"Evaluated {snapshot['summary']['recorded_days']} fictional daily observations through "
                f"{snapshot['observations'][-1]['timestamp_utc']}. Ask what changed or open the evidence trace."
            )
            refs = evidence(context, True)
        else:
            pieces = []
            for row in comparisons(context):
                pieces.append(
                    f"{row['label']}: reference {row['baseline_mean']:.3f} {row['unit']} "
                    f"[{row['reference_start_utc']} to {row['reference_end_utc']}]; "
                    f"recent {row['recent_mean']:.3f} {row['unit']} "
                    f"[{row['recent_start_utc']} to {row['recent_end_utc']}]; "
                    f"difference {row['delta']:+.3f} {row['unit']}."
                )
            text = (
                prefix
                + " ".join(pieces)
                + " First seven versus latest four daily observations; intermediate days are not in these means. Activity has no change rule."
            )
            refs = evidence(context, True)
    return {
        "answer": text,
        "intent": intent,
        "context_ref": context["context_ref"],
        "scenario": snapshot["scenario"],
        "assessment": snapshot["assessment"],
        "turn": turn,
        "engine": ENGINE,
        "generative_model": False,
        "demo_only": True,
        "provenance": "synthetic",
        "evidence_refs": refs,
        "limitations": LIMITATIONS,
        "supported_actions": ACTIONS,
        "suggested_questions": SUGGESTIONS,
    }


def comprehensive_report(context: dict, payload: ComprehensiveRequest) -> dict:
    """Recompute every exported assistant answer; replay manual events without clinical state changes."""
    report = copy.deepcopy(context["snapshot"]["review_report"])
    states = {
        "review_state": "PENDING_REVIEW",
        "note": "",
        "actions": {action: False for action in ACTIONS},
    }
    for event in payload.audit_log:
        if event.action == "review_state":
            states["review_state"] = event.review_state
        elif event.action == "note":
            states["note"] = event.note
        else:
            states["actions"][event.action] = event.checked
    transcript = []
    omitted = 0
    for item in payload.questions:
        response = answer(context, item.question, item.turn)
        if response["intent"] in {"refusal", "unsupported"}:
            omitted += 1
        else:
            transcript.append(
                {"turn": item.turn, "question": item.question, "response": response}
            )
    # Preserve legacy report field semantics; the new four-state workflow is separate.
    report["review_state"] = (
        "Reviewed in demo"
        if states["review_state"] == "DOCUMENTED"
        else "Pending review"
    )
    report.update(
        copilot_schema_version="1.5-demo",
        copilot_application_version="1.5",
        context_ref=context["context_ref"],
        reviewer_note=states["note"],
        evaluated_observations=context["snapshot"]["observations"],
        comparisons=comparisons(context),
        rule_metadata=context["snapshot"]["methodology"],
        mission_timeline=context["timeline"],
        risk_context=risk_guide(),
        scientific_references=[asdict(item) for item in EVIDENCE],
        copilot={
            "engine": ENGINE,
            "generative_model": False,
            "briefing": answer(context),
            "transcript": transcript,
            "omitted_unsupported_or_unsafe_turns": omitted,
        },
        fictional_review={
            **states,
            "audit_log": [
                event.model_dump(exclude_none=True) for event in payload.audit_log
            ],
            "fictional_attestation": True,
            "storage": "ephemeral browser state; not saved on server",
            "clinical_authorization": False,
            "notice": "User-recorded demonstration actions only. DOCUMENTED is not clinical clearance; authorized review checkbox does not contact personnel.",
        },
        limitations=LIMITATIONS,
    )
    return report
