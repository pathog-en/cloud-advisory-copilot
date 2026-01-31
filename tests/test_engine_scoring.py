from app.api.schemas import AssessmentRequest, Scorecard
from app.core.engine import apply_rules_with_scoring
from app.rules.models import Rule


def test_scoring_deltas_apply_and_trace_present():
    # Baseline request that should trigger our test rules
    req = AssessmentRequest(
        workload_type="web_api",
        environment="prod",
        traffic_profile="spiky",
        availability_target="high",
        rto_minutes=15,
        rpo_minutes=5,
        data_sensitivity="confidential",
        budget_priority="balanced",
        team_experience="mixed",
        constraints=["no k8s"],
        notes="test",
        provider_hints={"trace": True},
    )

    baseline = Scorecard(cost=70, security=70, reliability=70, performance=70, operations=70)

    # Minimal in-memory rules (don’t depend on filesystem)
    rules = [
        Rule.model_validate(
            {
                "id": "SEC-TEST",
                "title": "Security bump",
                "category": "security",
                "priority": "P0",
                "confidence": 0.9,
                "when": {"any": [{"field": "data_sensitivity", "op": "in", "value": ["confidential"]}]},
                "recommendation": "Do security thing",
                "rationale": "Because",
                "tradeoffs": [],
                "score_delta": {"security": 10, "operations": -2},
            }
        ),
        Rule.model_validate(
            {
                "id": "REL-TEST",
                "title": "Reliability bump",
                "category": "reliability",
                "priority": "P0",
                "confidence": 0.8,
                "when": {
                    "all": [
                        {"field": "environment", "op": "eq", "value": "prod"},
                        {"field": "availability_target", "op": "in", "value": ["high", "mission_critical"]},
                    ]
                },
                "recommendation": "Do reliability thing",
                "rationale": "Because",
                "tradeoffs": [],
                "score_delta": {"reliability": 15, "cost": -5},
            }
        ),
    ]

    recs, scores, trace = apply_rules_with_scoring(req, rules, baseline)

    # Recommendations created
    assert [r.id for r in recs] == ["SEC-TEST", "REL-TEST"] or [r.id for r in recs] == ["REL-TEST", "SEC-TEST"]

    # Score deltas applied
    assert scores.security == 80
    assert scores.operations == 68
    assert scores.reliability == 85
    assert scores.cost == 65

    # Trace populated
    assert "matched_rules" in trace
    assert {r["id"] for r in trace["matched_rules"]} == {"SEC-TEST", "REL-TEST"}
    assert len(trace["score_changes"]) == 2
