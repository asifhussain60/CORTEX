from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime


# ---- Helpers ----
def _require(condition: bool, message: str):
    if not condition:
        raise ValueError(message)


# ---- Common Metadata ----
@dataclass
class Meta:
    schema_version: str
    last_updated: datetime = field(default_factory=datetime.utcnow)
    generator_version: Optional[str] = None
    validation_status: Optional[Literal["unknown", "valid", "invalid"]] = "unknown"


# ---- Plan Ledger ----
@dataclass
class Artifacts:
    tasks: List[str] = field(default_factory=list)
    risks: List[str] = field(default_factory=list)
    decisions: List[str] = field(default_factory=list)
    constraints: List[str] = field(default_factory=list)
    metrics_estimates: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PlanLedgerEntry:
    id: str
    timestamp: datetime
    actor: str
    plan_type: Literal["feature", "arch", "refactor"]
    status: Literal["draft", "approved", "superseded"]
    supersedes: Optional[str] = None
    reasoning_refs: List[str] = field(default_factory=list)
    artifacts: Artifacts = field(default_factory=Artifacts)
    confidence: float = 0.5

    def __post_init__(self):
        _require(self.id is not None and self.id != "", "PlanLedgerEntry.id is required")
        _require(0.0 <= float(self.confidence) <= 1.0, "confidence must be in [0,1]")


@dataclass
class PlanLedger:
    meta: Meta
    entries: List[PlanLedgerEntry]

    def __post_init__(self):
        _require(len(self.entries) > 0, "entries must not be empty")


# ---- Active Plans ----
@dataclass
class FeaturePlan:
    id: str
    summary: str
    current_revision: str
    linked_operation: Optional[str] = None
    modules: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    test_matrix_ref: Optional[str] = None


@dataclass
class ArchitecturePlan:
    id: str
    context: str
    boundaries: List[str] = field(default_factory=list)
    patterns: List[str] = field(default_factory=list)
    tradeoffs: Optional[str] = None
    approved_revision: Optional[str] = None


@dataclass
class RefactorPlan:
    id: str
    target_module: str
    smells_detected: List[str] = field(default_factory=list)
    objectives: List[str] = field(default_factory=list)
    impact_scope: Optional[str] = None
    rollback_strategy: Optional[str] = None


@dataclass
class ActivePlans:
    meta: Meta
    feature_plans: List[FeaturePlan] = field(default_factory=list)
    architecture_plans: List[ArchitecturePlan] = field(default_factory=list)
    refactor_plans: List[RefactorPlan] = field(default_factory=list)


# ---- Decision Graph ----
@dataclass
class Decision:
    id: str
    question: str
    options: List[str]
    chosen_option: str
    justification: str
    supporting_evidence: List[str] = field(default_factory=list)
    risk_profile: Optional[str] = None
    revisit_trigger: Optional[str] = None

    def __post_init__(self):
        if self.options:
            _require(self.chosen_option in self.options, "chosen_option must be one of options")


@dataclass
class DecisionGraph:
    meta: Meta
    decisions: List[Decision]


# ---- Reasoning Chain (JSONL entries validated individually) ----
@dataclass
class ReasoningChainEntry:
    plan_id: str
    step_index: int
    model_version: str
    input_context_hash: str
    output_summary: str
    tokens_in: int
    tokens_out: int

    def __post_init__(self):
        _require(self.step_index >= 0, "step_index must be >= 0")
        _require(self.tokens_in >= 0 and self.tokens_out >= 0, "tokens must be >= 0")


# ---- Test Alignment ----
@dataclass
class RequiredTests:
    unit: List[str] = field(default_factory=list)
    integration: List[str] = field(default_factory=list)
    e2e: List[str] = field(default_factory=list)
    visual: List[str] = field(default_factory=list)
    performance: List[str] = field(default_factory=list)


@dataclass
class TestAlignmentItem:
    plan_id: str
    required_tests: RequiredTests = field(default_factory=RequiredTests)
    coverage_targets: Dict[str, float] = field(default_factory=dict)
    enforcement_status: Literal["none", "warn", "block"] = "warn"


@dataclass
class TestAlignment:
    meta: Meta
    plans: List[TestAlignmentItem] = field(default_factory=list)


# ---- Metrics Forecast ----
@dataclass
class PlanForecast:
    plan_id: str
    predicted_complexity: float
    uncertainty_band: Optional[List[float]] = None
    historical_similarity_refs: List[str] = field(default_factory=list)
    variance_from_actual: Optional[float] = None

    def __post_init__(self):
        _require(self.predicted_complexity >= 0, "predicted_complexity must be >= 0")


@dataclass
class MetricsForecast:
    meta: Meta
    forecasts: List[PlanForecast] = field(default_factory=list)


__all__ = [
    "Meta",
    "Artifacts",
    "PlanLedgerEntry",
    "PlanLedger",
    "FeaturePlan",
    "ArchitecturePlan",
    "RefactorPlan",
    "ActivePlans",
    "Decision",
    "DecisionGraph",
    "ReasoningChainEntry",
    "RequiredTests",
    "TestAlignmentItem",
    "TestAlignment",
    "PlanForecast",
    "MetricsForecast",
]
