from __future__ import annotations

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class Condition(BaseModel):
    field: str
    op: str  # eq | ne | in | contains | gte | lte
    value: Any


class WhenClause(BaseModel):
    all: List[Condition] = Field(default_factory=list)
    any: List[Condition] = Field(default_factory=list)


class Rule(BaseModel):
    id: str
    title: str
    category: str
    priority: str
    confidence: float = Field(ge=0.0, le=1.0)
    when: WhenClause
    recommendation: str
    rationale: str
    tradeoffs: List[str] = Field(default_factory=list)

    # optional future fields
    tags: List[str] = Field(default_factory=list)
    score_delta: Dict[str, int] = Field(default_factory=dict)
