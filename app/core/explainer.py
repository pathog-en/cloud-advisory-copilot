from __future__ import annotations

from typing import Any, Dict, List


def build_score_explanation(scores: Dict[str, int], trace: Dict[str, Any]) -> Dict[str, Any]:
    explanations: List[Dict[str, Any]] = []

    matched_rules = {
        rule["id"]: rule
        for rule in trace.get("matched_rules", [])
    }

    for change in trace.get("score_changes", []):
        rule_id = change.get("rule_id")
        rule = matched_rules.get(rule_id, {})

        before = change.get("before", {})
        after = change.get("after", {})

        for category, after_score in after.items():
            before_score = before.get(category)

            if before_score == after_score:
                continue

            delta = after_score - before_score
            sign = "+" if delta > 0 else ""

            explanations.append(
                {
                    "category": category,
                    "rule_id": rule_id,
                    "rule_title": rule.get("title", "Matched rule"),
                    "message": (
                        f"{category.title()} changed by {sign}{delta} "
                        f"because the workload matched: {rule.get('title', 'a scoring rule')}."
                    ),
                    "score_change": f"{sign}{delta}",
                    "before": before_score,
                    "after": after_score,
                }
            )

    strongest = max(scores, key=scores.get)
    weakest = min(scores, key=scores.get)

    return {
        "summary": (
            f"This workload scored strongest in {strongest} "
            f"and has the most room to improve in {weakest}."
        ),
        "scores": scores,
        "explanations": explanations,
    }