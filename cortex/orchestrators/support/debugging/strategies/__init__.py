"""
Debugging Strategies Module

Collection of marker injection strategies for different debug scenarios.

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Stage 2

AC-ID: AC-WAVE-R-S2-003
"""

from cortex.orchestrators.support.debugging.strategies.debug_strategy_base import (
    AbstractInjectionStrategy,
    MarkerContext,
    InjectionResult,
)
from cortex.orchestrators.support.debugging.strategies.test_failure_strategy import TestFailureStrategy
from cortex.orchestrators.support.debugging.strategies.refactor_regression_strategy import RefactorRegressionStrategy
from cortex.orchestrators.support.debugging.strategies.governance_violation_strategy import GovernanceViolationStrategy

__all__ = [
    "AbstractInjectionStrategy",
    "MarkerContext",
    "InjectionResult",
    "TestFailureStrategy",
    "RefactorRegressionStrategy",
    "GovernanceViolationStrategy",
]
