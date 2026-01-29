from __future__ import annotations

from fastapi import APIRouter
from .schemas import AssessmentRequest, AssessmentResponse, Scorecard, Recommendation

router = APIRouter()


def baseline_scores() -> Scorecard:
    # Day 1: static baseline, Day 3+: rules will adjust these
    return Scorecard(cost=70, security=70, reliability=70, performance=70, operations=70)


def stub_recommendations(req: AssessmentRequest) -> list[Recommendation]:
    # Day 1: deterministic placeholders to prove API plumbing works.
    recs: list[Recommendation] = []

    # Always recommend "least privilege" + "encryption"
    recs.append(
        Recommendation(
            id="SEC-001",
            title="Default to least-privilege access controls",
            category="security",
            priority="P0",
            confidence=0.80,
            recommendation="Use role-based access with least privilege and short-lived credentials. Separate duties between humans, services, and CI/CD.",
            rationale="Access control mistakes are one of the most common sources of cloud incidents.",
            tradeoffs=["Requires disciplined identity management and periodic access reviews."],
        )
    )

    recs.append(
        Recommendation(
            id="SEC-002",
            title="Encrypt data in transit and at rest",
            category="security",
            priority="P0",
            confidence=0.85,
            recommendation="Use TLS for all service-to-service traffic and encryption-at-rest for object, block, and database storage.",
            rationale="Encryption reduces breach impact and is commonly required for regulated or confidential data.",
            tradeoffs=["Key management introduces operational overhead."],
        )
    )

    # Simple condition-based advisory (still not YAML rules yet)
    if req.environment == "prod" and req.availability_target in {"high", "mission_critical"}:
        recs.append(
            Recommendation(
                id="REL-001",
                title="Design for multi-zone failure tolerance",
                category="reliability",
                priority="P0",
                confidence=0.75,
                recommendation="Use redundant instances across failure domains (zones/availability sets), health checks, and automated failover patterns.",
                rationale="High availability targets require tolerance to single-zone failures.",
                tradeoffs=["Higher cost due to redundancy.", "More moving parts to operate."],
            )
        )

    if req.traffic_profile == "spiky":
        recs.append(
            Recommendation(
                id="COST-001",
                title="Prefer elastic scaling patterns for spiky traffic",
                category="cost",
                priority="P1",
                confidence=0.70,
                recommendation="Use autoscaling or serverless-style execution to scale to zero/scale out rapidly, depending on latency needs.",
                rationale="Spiky demand penalizes fixed-capacity deployments with idle cost or poor responsiveness.",
                tradeoffs=["Cold starts (for some serverless patterns).", "Scaling complexity if stateful."],
            )
        )

    return recs


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/rules")
def rules():
    # Day 1: rules come on Day 2 (YAML loading)
    return {"count": 0, "rules": []}


@router.post("/assess", response_model=AssessmentResponse)
def assess(request: AssessmentRequest) -> AssessmentResponse:
    scores = baseline_scores()
    recs = stub_recommendations(request)

    # Sort by priority (P0 first), then confidence desc
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    recs_sorted = sorted(recs, key=lambda r: (priority_order.get(r.priority, 9), -r.confidence))

    return AssessmentResponse(
        normalized_input=request,
        scores=scores,
        recommendations=recs_sorted,
        meta={
            "engine_version": "0.1.0-day1",
            "cloud_agnostic": True,
        },
    )
