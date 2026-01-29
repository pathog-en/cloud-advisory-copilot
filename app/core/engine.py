from __future__ import annotations

from typing import Any, Dict, List
from app.api.schemas import AssessmentRequest, Recommendation
from app.rules.models import Rule, Condition


def _get_field(req: AssessmentRequest, field: str) -> Any:
    # supports only top-level fields for now
    return getattr(req, field, None)


def _eval_condition(req: AssessmentRequest, c: Condition) -> bool:
    actual = _get_field(req, c.field)
    op = c.op
    expected = c.value

    if op == "eq":
        return actual == expected
    if op == "ne":
        return actual != expected
    if op == "in":
        return actual in expected
    if op == "contains":
        # intended for list[str] constraints and similar
        if actual is None:
            return False
        return expected in actual
    if op == "gte":
        return actual is not None and actual >= expected
    if op == "lte":
        return actual is not None and actual <= expected

    raise ValueError(f"Unsupported operator: {op}")


def rule_matches(req: AssessmentRequest, rule: Rule) -> bool:
    # ALL conditions must be true (if provided)
    if rule.when.all:
        if not all(_eval_condition(req, c) for c in rule.when.all):
            return False

    # ANY conditions must have at least one true (if provided)
    if rule.when.any:
        if not any(_eval_condition(req, c) for c in rule.when.any):
            return False

    # If both are empty, rule matches everything (not recommended, but allowed)
    if not rule.when.all and not rule.when.any:
        return True

    return True


def apply_rules(req: AssessmentRequest, rules: List[Rule]) -> List[Recommendation]:
    recs: List[Recommendation] = []
    for r in rules:
        if rule_matches(req, r):
            recs.append(
                Recommendation(
                    id=r.id,
                    title=r.title,
                    category=r.category,
                    priority=r.priority,
                    confidence=r.confidence,
                    recommendation=r.recommendation,
                    rationale=r.rationale,
                    tradeoffs=r.tradeoffs,
                )
            )

    # sort: P0 -> P1 -> P2, then confidence desc
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    recs.sort(key=lambda x: (priority_order.get(x.priority, 9), -x.confidence))
    return recs
