"""tdd_orchestrator — subpackage for Phase 103-c decomposition.

Re-exports all public symbols so that existing imports continue to work
unchanged after the god-object split.

Structure:
  tdd_models.py          — TDDPhase enum + 5 dataclasses + TDDKnowledgeLoader
  tdd_execution_mixin.py — RED/GREEN/REFACTOR phase execution mixin
  tdd_metrics_mixin.py   — multi-cycle, quality gates, convergence mixin
  tdd_batch_mixin.py     — batched test runner + Chat progress mixin
  _coordinator.py        — slim TDDOrchestrator coordinator class
"""

from cortex.orchestrators.core.tdd_orchestrator.tdd_models import (
    TDDPhase,
    TDDDisciplineRule,
    SuccessCriteria,
    CycleMetrics,
    GateResult,
    TDDImplementationGuidance,
    TDDKnowledgeLoader,
)
from cortex.orchestrators.core.tdd_orchestrator.tdd_execution_mixin import TDDExecutionMixin
from cortex.orchestrators.core.tdd_orchestrator.tdd_metrics_mixin import TDDMetricsMixin
from cortex.orchestrators.core.tdd_orchestrator.tdd_batch_mixin import TDDBatchMixin
from cortex.orchestrators.core.tdd_orchestrator._coordinator import (
    TDDOrchestrator,
    get_tdd_orchestrator,
)

__all__ = [
    "TDDPhase",
    "TDDDisciplineRule",
    "SuccessCriteria",
    "CycleMetrics",
    "GateResult",
    "TDDImplementationGuidance",
    "TDDKnowledgeLoader",
    "TDDExecutionMixin",
    "TDDMetricsMixin",
    "TDDBatchMixin",
    "TDDOrchestrator",
    "get_tdd_orchestrator",
]
