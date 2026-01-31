from app.api.schemas import AssessmentRequest, Scorecard
from app.core.engine import apply_rules_with_scoring
from app.rules.models import Rule


def test_scores_clamp_between_0_and_100():
    req = AssessmentRequest(
        workload_type="web_api",
        environment="prod",
        traffic_profile="low",
        availability_target="standard",
        rto_minutes=0,
        rpo_minutes=0,
        data_sensitivity="public",
        budget_priority="balanced",
        team_experience="mixed",
        constraints=[],
        notes=None,
        provider_hints={},
    )

    baseline = Scorecard(cost=95, security=5, reliability=50, performance=50, operations=50)

    rules = [
        Rule.model_validate(
            {
                "id": "CLAMP-UP",
                "title": "Clamp up",
                "category": "security",
                "priority": "P1",
                "confidence": 0.5,
                "when": {"any": [{"field": "environment", "op": "eq", "value": "prod"}]},
                "recommendation": "x",
                "rationale": "x",
                "tradeoffs": [],
                "score_delta": {"cost": 10, "security": 200},
            }
        ),
        Rule.model_validate(
            {
                "id": "CLAMP-DOWN",
                "title": "Clamp down",
                "category": "cost",
                "priority": "P1",
                "confidence": 0.5,
                "when": {"any": [{"field": "environment", "op": "eq", "value": "prod"}]},
                "recommendation": "y",
                "rationale": "y",
                "tradeoffs": [],
                "score_delta": {"security": -999, "cost": -999},
            }
        ),
    ]

    _, scores, _ = apply_rules_with_scoring(req, rules, baseline)

    assert scores.security == 0
    assert scores.cost == 0
