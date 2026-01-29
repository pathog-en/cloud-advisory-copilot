from __future__ import annotations

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, conint


class WorkloadType(str, Enum):
    web_api = "web_api"
    batch = "batch"
    data_pipeline = "data_pipeline"
    ml_inference = "ml_inference"
    static_site = "static_site"


class Environment(str, Enum):
    dev = "dev"
    staging = "staging"
    prod = "prod"


class TrafficProfile(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    spiky = "spiky"


class AvailabilityTarget(str, Enum):
    standard = "standard"
    high = "high"
    mission_critical = "mission_critical"


class DataSensitivity(str, Enum):
    public = "public"
    internal = "internal"
    confidential = "confidential"
    regulated = "regulated"


class BudgetPriority(str, Enum):
    lowest_cost = "lowest_cost"
    balanced = "balanced"
    performance_first = "performance_first"


class TeamExperience(str, Enum):
    junior = "junior"
    mixed = "mixed"
    senior = "senior"


class AssessmentRequest(BaseModel):
    workload_type: WorkloadType
    environment: Environment
    traffic_profile: TrafficProfile

    availability_target: AvailabilityTarget = AvailabilityTarget.standard
    rto_minutes: conint(ge=0) = 0
    rpo_minutes: conint(ge=0) = 0

    data_sensitivity: DataSensitivity = DataSensitivity.internal
    budget_priority: BudgetPriority = BudgetPriority.balanced
    team_experience: TeamExperience = TeamExperience.mixed

    constraints: List[str] = Field(default_factory=list, description="Hard constraints, e.g. 'no k8s', 'single region'")
    notes: Optional[str] = Field(default=None, description="Optional free-form context")

    # reserved for future: cloud provider preference hints (cloud-agnostic by default)
    provider_hints: Dict[str, Any] = Field(default_factory=dict)


class Recommendation(BaseModel):
    id: str
    title: str
    category: str  # cost|security|reliability|performance|operations
    priority: str  # P0|P1|P2
    confidence: float = Field(ge=0.0, le=1.0)
    recommendation: str
    rationale: str
    tradeoffs: List[str] = Field(default_factory=list)


class Scorecard(BaseModel):
    cost: int = Field(ge=0, le=100)
    security: int = Field(ge=0, le=100)
    reliability: int = Field(ge=0, le=100)
    performance: int = Field(ge=0, le=100)
    operations: int = Field(ge=0, le=100)


class AssessmentResponse(BaseModel):
    normalized_input: AssessmentRequest
    scores: Scorecard
    recommendations: List[Recommendation]
    meta: Dict[str, Any] = Field(default_factory=dict)
