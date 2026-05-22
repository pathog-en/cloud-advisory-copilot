from __future__ import annotations

from fastapi import APIRouter
from .schemas import AssessmentRequest, AssessmentResponse, Scorecard

from app.rules.loader import load_rules
from app.core.engine import apply_rules_with_scoring
from app.core.reporting import generate_markdown_report


router = APIRouter()


def baseline_scores() -> Scorecard:
    # Day 3: baseline + rule-driven deltas
    return Scorecard(
        cost=70,
        security=70,
        reliability=70,
        performance=70,
        operations=70,
    )


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/rules")
def rules():
    rules = load_rules()
    return {
        "count": len(rules),
        "rules": [
            {
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "priority": r.priority,
                "confidence": r.confidence,
            }
            for r in rules
        ],
    }


@router.post("/assess", response_model=AssessmentResponse)
def assess(request: AssessmentRequest) -> AssessmentResponse:
    rules = load_rules()
    baseline = baseline_scores()

    # 🔑 Day 3 engine call (THIS is where Step 5.1 is used)
    recs, updated_scores, trace = apply_rules_with_scoring(
        request,
        rules,
        baseline,
    )

    # Trace is opt-in (keeps default response clean)
    include_trace = (
        isinstance(request.provider_hints, dict)
        and request.provider_hints.get("trace") is True
    )

    return AssessmentResponse(
        normalized_input=request,
        scores=updated_scores,
        recommendations=recs,
        meta={
            "engine_version": "0.3.0-day3",
            "cloud_agnostic": True,
            "rules_loaded": len(rules),
            "trace_enabled": include_trace,
        },
        trace=trace if include_trace else None,
    )

@router.post("/report")
def report(request: AssessmentRequest):
    rules = load_rules()
    baseline = baseline_scores()

    recs, updated_scores, _ = apply_rules_with_scoring(
        request,
        rules,
        baseline,
    )

    markdown = generate_markdown_report(
        input_data=request,
        scores=updated_scores,
        recommendations=recs,
    )

    return {
        "format": "markdown",
        "report": markdown,
    }
