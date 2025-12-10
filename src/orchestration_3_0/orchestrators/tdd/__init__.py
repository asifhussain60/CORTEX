"""
TDD Orchestrator Package
Consolidates 4 legacy TDD files (4,023 LOC) → 6 components (2,000 LOC)

Components:
- tdd_orchestrator: Main orchestrator (500 LOC)
- phase_validator: DoR/DoD validation (200 LOC)
- test_generator: RED phase test generation (400 LOC)
- implementation_engine: GREEN phase minimal implementation (300 LOC)
- refactoring_engine: REFACTOR phase code improvement (400 LOC)
- metrics_collector: TDD metrics tracking (200 LOC)
"""

from .tdd_orchestrator import TDDOrchestrator
from .phase_validator import PhaseValidator, ValidationResult

__all__ = [
    "TDDOrchestrator",
    "PhaseValidator",
    "ValidationResult",
]
