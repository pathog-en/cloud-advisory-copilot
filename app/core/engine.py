from __future__ import annotations

from typing import Any, Dict, List, Tuple
from copy import deepcopy

from app.api.schemas import AssessmentRequest, Recommendation, Scorecard
from app.rules.models import Rule, Condition


def _get_field(req: AssessmentRequest, field: str) -> Any:
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
        if actual is None:
            return False
        return expected in actual
    if op == "gte":
        return actual is not None and actual >= expected
    if op == "lte":
        return actual is not None and actual <= expected

    raise ValueError(f"Unsupported operator: {op}")


def rule_matches(req: AssessmentRequest, rule: Rule) -> bool:
    if rule.when.all and not all(_eval_condition(req, c) for c in rule.when.all):
        return False
    if rule.when.any and not any(_eval_condition(req, c) for c in rule.when.any):
        return False
    if not rule.when.all and not rule.when.any:
        return True
    return True


def _clamp(n: int, lo: int = 0, hi: int = 100) -> int:
    return max(lo, min(hi, n))


def apply_rules_with_scoring(
    req: AssessmentRequest,
    rules: List[Rule],
    baseline: Scorecard,
) -> Tuple[List[Recommendation], Scorecard, Dict[str, Any]]:
    """
    Returns: (recommendations, updated_scores, trace)
    """
    recs: List[Recommendation] = []
    trace: Dict[str, Any] = {"matched_rules": [], "score_changes": []}

    # Start from baseline (copy so caller doesn't mutate)
    scores = deepcopy(baseline).model_dump()

    for r in rules:
        if not rule_matches(req, r):
            continue

        # recommendation
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

        trace["matched_rules"].append(
            {
                "id": r.id,
                "title": r.title,
                "category": r.category,
                "priority": r.priority,
                "confidence": r.confidence,
                "when": r.when.model_dump(),
                "score_delta": r.score_delta,
            }
        )

        # scoring
        if r.score_delta:
            before = scores.copy()
            for k, delta in r.score_delta.items():
                if k in scores and isinstance(delta, int):
                    scores[k] = _clamp(int(scores[k]) + delta)
            after = scores.copy()
            trace["score_changes"].append({"rule_id": r.id, "before": before, "after": after})

    # sort recs
    priority_order = {"P0": 0, "P1": 1, "P2": 2}
    recs.sort(key=lambda x: (priority_order.get(x.priority, 9), -x.confidence))

    updated_scores = Scorecard(**scores)
    return recs, updated_scores, trace
