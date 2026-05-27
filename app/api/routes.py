from __future__ import annotations

import time
import logging

from fastapi import APIRouter
from prometheus_client import Counter, Histogram

from .schemas import AssessmentRequest, AssessmentResponse, Scorecard
from app.rules.loader import load_rules
from app.core.engine import apply_rules_with_scoring
from app.core.reporting import generate_markdown_report


router = APIRouter()

logger = logging.getLogger(__name__)

ASSESS_REQUESTS_TOTAL = Counter(
    "cloud_advisory_assess_requests_total",
    "Total number of /assess requests",
)

ASSESS_LATENCY_SECONDS = Histogram(
    "cloud_advisory_assess_latency_seconds",
    "Latency for /assess requests in seconds",
)

REPORT_REQUESTS_TOTAL = Counter(
    "cloud_advisory_report_requests_total",
    "Total number of /report requests",
)

REPORT_LATENCY_SECONDS = Histogram(
    "cloud_advisory_report_latency_seconds",
    "Latency for /report requests in seconds",
)


def baseline_scores() -> Scorecard:
    return Scorecard(
        cost=70,
        security=70,
        reliability=70,
        performance=70,
        operations=70,
    )


@router.get("/health")
def health():
    logger.info("Health endpoint hit")
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
    ASSESS_REQUESTS_TOTAL.inc()
    start = time.time()

    logger.info("Assess endpoint hit")

    rules = load_rules()
    baseline = baseline_scores()

    recs, updated_scores, trace = apply_rules_with_scoring(
        request,
        rules,
        baseline,
    )

    include_trace = (
        isinstance(request.provider_hints, dict)
        and request.provider_hints.get("trace") is True
    )

    duration = time.time() - start
    ASSESS_LATENCY_SECONDS.observe(duration)

    logger.info("Assess completed in %.3fs", duration)

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
    REPORT_REQUESTS_TOTAL.inc()
    start = time.time()

    logger.info("Report endpoint hit")

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

    duration = time.time() - start
    REPORT_LATENCY_SECONDS.observe(duration)

    logger.info("Report completed in %.3fs", duration)

    return {
        "format": "markdown",
        "report": markdown,
    }