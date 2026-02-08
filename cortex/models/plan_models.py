"""
Pydantic v2 data models for plan specification and validation.

Models provide type-safe plan schema with IDE autocomplete and JSON Schema generation.
Authority: Phase 45 § Architecture Decisions § ADR-PLAN-004

CORE Rules:
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-030: Implementation Truth
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, field_validator


# ============================================================================
# ENUMS
# ============================================================================
class PlanStatus(str, Enum):
    """Plan lifecycle status."""

    PENDING = "pending"
    APPROVED = "approved"
    IN_PROGRESS = "in_progress"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PlanPriority(str, Enum):
    """Plan priority levels."""

    P0 = "P0"
    P1 = "P1"
    P2 = "P2"
    P3 = "P3"


class IntentType(str, Enum):
    """Plan intent classification."""

    IMPLEMENT = "IMPLEMENT"
    FIX = "FIX"
    REFACTOR = "REFACTOR"
    ANALYZE = "ANALYZE"
    DESIGN = "DESIGN"


class RiskLevel(str, Enum):
    """Risk assessment levels."""

    LOW = "low"
    LOW_MEDIUM = "low_medium"
    MEDIUM = "medium"
    MEDIUM_HIGH = "medium_high"
    HIGH = "high"


class StageType(str, Enum):
    """Stage types for plan breakdown."""

    FOUNDATION = "FOUNDATION"
    INTEGRATION = "INTEGRATION"
    INTELLIGENCE = "INTELLIGENCE"
    VISUALIZATION = "VISUALIZATION"
    FINALIZATION = "FINALIZATION"


class ChallengeType(str, Enum):
    """Challenge category types."""

    GOVERNANCE = "governance"
    ALTERNATIVE_PATH = "alternative_path"
    SCOPE_CREEP = "scope_creep"
    RISK_MISMATCH = "risk_mismatch"
    TECHNICAL_DEBT = "technical_debt"


class ExecutionGateType(str, Enum):
    """Execution gate types."""

    PRE_FLIGHT = "pre_flight"
    APPROVAL = "approval"
    DESIGN_REVIEW = "design_review"
    NOTIFY_AND_EXECUTE = "notify_and_execute"


# ============================================================================
# METADATA MODELS
# ============================================================================
class PlanMetadata(BaseModel):
    """Plan metadata and lifecycle information."""

    phase_id: str = Field(..., description="Unique phase/plan identifier")
    title: str = Field(..., description="Plan title")
    subtitle: str = Field(default="", description="Subtitle/tagline")
    author: str = Field(..., description="Plan author")
    created_date: datetime = Field(..., description="Creation timestamp")
    updated_date: datetime = Field(default_factory=datetime.utcnow, description="Last update timestamp")
    target_start: Optional[datetime] = Field(None, description="Planned start date")
    estimated_duration: str = Field(..., description="Duration estimate (e.g., '5 days')")
    estimated_hours: int = Field(..., description="Estimated hours of effort")
    test_target: int = Field(..., description="Target number of tests")
    coverage_target: int = Field(default=90, description="Target test coverage percentage")
    roi_score: float = Field(
        ..., ge=0.0, le=1.0, description="Return on investment score (0-1)"
    )
    risk_level: RiskLevel = Field(..., description="Overall risk assessment")
    status: PlanStatus = Field(default=PlanStatus.PENDING, description="Current status")


class PlanClassification(BaseModel):
    """Plan intent classification and routing."""

    intent: IntentType = Field(..., description="Primary intent type")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    scope: str = Field(..., description="Scope description (e.g., 'system', 'module')")
    impact: str = Field(..., description="Impact level (e.g., 'high', 'medium')")
    handler: str = Field(default="", description="Orchestrator handler name")
    rationale: str = Field(default="", description="Classification rationale")


class Overview(BaseModel):
    """Plan overview and success criteria."""

    vision: str = Field(..., description="Vision statement")
    outcome: str = Field(..., description="Expected outcome")
    success_criteria: List[str] = Field(
        default_factory=list, description="Success criteria list"
    )


# ============================================================================
# STAGE MODELS
# ============================================================================
class PlanTask(BaseModel):
    """Individual task within a stage."""

    task_id: str = Field(..., description="Task identifier")
    name: str = Field(..., description="Task name")
    description: Optional[str] = Field(None, description="Detailed description")
    acceptance_criteria: List[str] = Field(
        default_factory=list, description="Acceptance criteria"
    )
    handler: Optional[str] = Field(None, description="Responsible orchestrator/team")
    inputs: Dict[str, Any] = Field(default_factory=dict, description="Task inputs")
    outputs: Dict[str, Any] = Field(default_factory=dict, description="Task outputs")
    estimated_hours: Optional[int] = Field(None, description="Estimated effort")


class Deliverable(BaseModel):
    """Deliverable within a stage."""

    file: str = Field(..., description="File path or identifier")
    description: str = Field(..., description="Deliverable description")
    notes: Optional[str] = Field(None, description="Additional notes")
    classes: Optional[List[str]] = Field(None, description="Python classes if applicable")
    operations: Optional[List[str]] = Field(None, description="Operations/methods")
    templates: Optional[List[str]] = Field(None, description="Templates if applicable")


class TestSpec(BaseModel):
    """Test specification for a stage."""

    file: str = Field(..., description="Test file path")
    test_count: int = Field(..., description="Number of tests")
    description: str = Field(..., description="Test description")


class PlanStage(BaseModel):
    """Single stage in plan execution."""

    stage_id: str = Field(..., description="Stage identifier (e.g., 'S1')")
    stage_name: str = Field(..., description="Stage name")
    stage_type: StageType = Field(..., description="Stage type")
    estimated_hours: int = Field(..., description="Estimated effort in hours")
    status: PlanStatus = Field(default=PlanStatus.PENDING, description="Stage status")
    test_count: int = Field(..., description="Number of tests for stage")
    description: str = Field(..., description="Stage description")
    deliverables: List[Deliverable] = Field(
        default_factory=list, description="Stage deliverables"
    )
    tests: List[TestSpec] = Field(default_factory=list, description="Test specifications")
    acceptance_criteria: List[str] = Field(
        default_factory=list, description="Acceptance criteria"
    )
    dependencies: List[str] = Field(
        default_factory=list, description="Dependent stage IDs"
    )


# ============================================================================
# CHALLENGE & GATE MODELS
# ============================================================================
class Challenge(BaseModel):
    """Plan challenges and risks to address."""

    type: ChallengeType = Field(..., description="Challenge type")
    title: str = Field(..., description="Challenge title")
    description: str = Field(..., description="Challenge description")
    severity: str = Field(..., description="Severity level")
    recommendation: str = Field(..., description="Mitigation recommendation")
    can_proceed_without_addressing: bool = Field(
        default=False, description="Can proceed without addressing"
    )


class ExecutionGate(BaseModel):
    """Execution gate configuration."""

    gate_type: ExecutionGateType = Field(..., description="Gate type")
    requires_confirmation: bool = Field(default=False, description="Requires user confirmation")
    requires_design_review: bool = Field(default=False, description="Requires design review")
    impact_level: str = Field(..., description="Impact level")
    confidence_level: str = Field(..., description="Confidence level")
    reason: Optional[str] = Field(None, description="Gate reason/justification")


# ============================================================================
# ENRICHMENT MODEL
# ============================================================================
class EnrichmentData(BaseModel):
    """Enrichment data from LENS pipeline."""

    source: str = Field(..., description="Enrichment source (e.g., 'git', 'code', 'policy')")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] = Field(default_factory=dict, description="Enrichment data")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


# ============================================================================
# ROOT PLAN SPECIFICATION MODEL
# ============================================================================
class PlanSpec(BaseModel):
    """Complete plan specification."""

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "version": "1.0",
                    "metadata": {
                        "phase_id": "phase-45",
                        "title": "Enhanced Planning System",
                        "author": "Asif Hussain",
                        "created_date": "2026-02-08T16:00:00Z",
                        "estimated_duration": "5 days",
                        "estimated_hours": 18,
                        "test_target": 100,
                        "coverage_target": 90,
                        "roi_score": 0.89,
                        "risk_level": "low_medium",
                        "status": "pending",
                    },
                    "classification": {
                        "intent": "IMPLEMENT",
                        "confidence": 0.92,
                        "scope": "system",
                        "impact": "high",
                        "handler": "TDDOrchestrator",
                    },
                    "overview": {
                        "vision": "A unified planning system...",
                        "outcome": "Production-grade plan lifecycle...",
                        "success_criteria": ["Plan Discovery Rate: 99%"],
                    },
                    "stages": [],
                    "challenges": [],
                }
            ]
        }
    }

    version: str = Field(default="1.0", description="Schema version")
    metadata: PlanMetadata = Field(..., description="Plan metadata")
    classification: PlanClassification = Field(..., description="Intent classification")
    overview: Overview = Field(..., description="Overview and success criteria")
    stages: List[PlanStage] = Field(default_factory=list, description="Execution stages")
    challenges: List[Challenge] = Field(
        default_factory=list, description="Challenges and risks"
    )
    execution_gates: Optional[ExecutionGate] = Field(None, description="Execution gates")
    enrichment_data: List[EnrichmentData] = Field(
        default_factory=list, description="LENS enrichment data"
    )
    governance: Dict[str, Any] = Field(
        default_factory=dict, description="Governance rules and requirements"
    )
    dependencies: Dict[str, List[str]] = Field(
        default_factory=lambda: {"internal": [], "external": []},
        description="Plan dependencies",
    )

    @field_validator("metadata")
    @classmethod
    def validate_metadata(cls, v: PlanMetadata) -> PlanMetadata:
        """Validate metadata consistency."""
        if v.estimated_hours < 1:
            raise ValueError("estimated_hours must be >= 1")
        if v.test_target < 0:
            raise ValueError("test_target must be >= 0")
        return v

    @field_validator("stages")
    @classmethod
    def validate_stages(cls, v: List[PlanStage]) -> List[PlanStage]:
        """Validate stage dependencies are acyclic."""
        if not v:
            return v

        stage_ids = {stage.stage_id for stage in v}
        for stage in v:
            for dep in stage.dependencies:
                if dep not in stage_ids:
                    raise ValueError(f"Stage {stage.stage_id} depends on undefined {dep}")

        return v

    def total_tests(self) -> int:
        """Calculate total number of tests across all stages."""
        return sum(stage.test_count for stage in self.stages)

    def total_hours(self) -> int:
        """Calculate total effort across all stages."""
        return sum(stage.estimated_hours for stage in self.stages)

    def get_stage(self, stage_id: str) -> Optional[PlanStage]:
        """Get stage by ID."""
        return next((s for s in self.stages if s.stage_id == stage_id), None)

    def json_schema(self) -> Dict[str, Any]:
        """Generate JSON Schema for plan specification."""
        return self.model_json_schema()
