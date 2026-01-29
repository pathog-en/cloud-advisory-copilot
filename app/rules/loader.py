from __future__ import annotations

from pathlib import Path
from typing import List
import yaml

from .models import Rule

RULES_DIR = Path(__file__).resolve().parents[2] / "rules"


def load_rules() -> List[Rule]:
    rules: List[Rule] = []
    if not RULES_DIR.exists():
        return rules

    for path in sorted(RULES_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or []
        if not isinstance(data, list):
            raise ValueError(f"{path.name} must contain a YAML list of rules")
        for item in data:
            rules.append(Rule.model_validate(item))

    return rules
