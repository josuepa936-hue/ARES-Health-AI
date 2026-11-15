"""Regenerate offline fictional copilot test responses from Python, never JS algorithms."""

import json
from pathlib import Path
from src.ares_health.copilot import (
    canonical_context,
    answer,
    comprehensive_report,
    SUGGESTIONS,
)
from src.ares_health.copilot_models import (
    ScenarioContext,
    ComprehensiveRequest,
    CsvContext,
)
from src.ares_health.synthetic import generate_scenario

contexts = {
    key: ScenarioContext(kind="scenario", scenario=key)
    for key in ["stable", "heart_rate_shift", "sleep_shift", "incomplete"]
}
contexts["csv"] = CsvContext(
    kind="synthetic_csv",
    fictional_attestation=True,
    csv=generate_scenario().to_csv(index=False),
)
contexts["checkin"] = ScenarioContext(
    kind="scenario",
    scenario="stable",
    check_in={
        "fictional_attestation": True,
        "resting_hr_bpm": 140,
        "sleep_hours": 7,
        "activity_minutes": 45,
    },
)
fixtures = {}
for key, source in contexts.items():
    context = canonical_context(source)
    fixture = {
        "briefing": answer(context),
        "answers": {
            question: answer(context, question, 1)
            for question in [*SUGGESTIONS, "Give a treatment", "Tell a story"]
        },
    }
    fixture["report"] = comprehensive_report(
        context,
        ComprehensiveRequest(
            context=source,
            expected_context_ref=context["context_ref"],
            fictional_attestation=True,
        ),
    )
    fixture["reports"] = {}
    for state in [
        "PENDING_REVIEW",
        "IN_PROGRESS",
        "AWAITING_AUTHORIZED_REVIEW",
        "DOCUMENTED",
    ]:
        report = comprehensive_report(
            context,
            ComprehensiveRequest(
                context=source,
                expected_context_ref=context["context_ref"],
                fictional_attestation=True,
                audit_log=[
                    {"sequence": 1, "action": "review_state", "review_state": state}
                ],
            ),
        )
        fixture["reports"][state] = {
            key: report[key] for key in ("review_state", "fictional_review")
        }
    fixtures[key] = fixture
Path("frontend/src/test/copilot-fixtures.json").write_text(
    json.dumps(fixtures, indent=2, allow_nan=False) + "\n"
)
