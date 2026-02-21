"""
Marker Injection Engine - Strategy Pattern for Debug Marker Placement

Purpose:
    Smart marker placement logic using Strategy Pattern. Different strategies
    for TEST_FAILURE (traceback parsing), REFACTOR_REGRESSION (git diff),
    and GOVERNANCE_VIOLATION (rule location).

Authority:
    - ENH-089 (EventBus-Driven Debugger)
    - WAVE-R Execution Plan Stage 2

AC-ID: AC-WAVE-R-004

Note (CORE-035):
    AbstractInjectionStrategy, TestFailureStrategy, RefactorRegressionStrategy,
    and GovernanceViolationStrategy are canonical in cortex.orchestrators.support.debugging.strategies.
    This module re-exports them for backwards compatibility with MarkerInjectionEngine's
    internal strategy registry.
"""

from typing import Dict, Any, Optional
from datetime import datetime
from jinja2 import Template

# CORE-035: Import canonical strategy classes — do NOT redefine them here.
from cortex.orchestrators.support.debugging.strategies import (
    AbstractInjectionStrategy,
    MarkerContext,
    InjectionResult,
    TestFailureStrategy,
    RefactorRegressionStrategy,
    GovernanceViolationStrategy,
)

__all__ = [
    "MarkerInjectionEngine",
    "AbstractInjectionStrategy",
    "MarkerContext",
    "InjectionResult",
    "TestFailureStrategy",
    "RefactorRegressionStrategy",
    "GovernanceViolationStrategy",
]


class MarkerInjectionEngine:
    """
    
    Uses Strategy Pattern to support multiple injection strategies:
    - test_failure: Parse traceback, inject at failure point
    - refactor_regression: Parse git diff, inject at changed lines
    - governance_violation: Inject at violation location
    
    Example:
        >>> engine = MarkerInjectionEngine()
        >>> engine.inject(
        ...     strategy="test_failure",
        ...     session_id="session-test_failure-20260213",
        ...     file_path="example.py",
        ...     line_number=100,
        ...     context={"test_name": "test_example", "failure_reason": "AssertionError"}
        ... )
        True
    """
    
    # Marker template (Jinja2)
    MARKER_TEMPLATE = Template(
        "# === CORTEX DEBUG MARKER [{{ trigger_type }}] ===\n"
        "# session_id: {{ session_id }}\n"
        "# trigger_type: {{ trigger_type }}\n"
        "# context: {{ context }}\n"
        "# timestamp: {{ timestamp }}\n"
        "# === END MARKER ===\n"
    )
    
    def __init__(self) -> None:
        """Initialize MarkerInjectionEngine with strategies."""
        self.strategies: Dict[str, AbstractInjectionStrategy] = {
            "test_failure": TestFailureStrategy(),
            "refactor_regression": RefactorRegressionStrategy(),
            "governance_violation": GovernanceViolationStrategy()
        }
    
    def inject(
        self,
        strategy: str,
        session_id: str,
        file_path: str,
        context: Optional[Dict[str, Any]] = None,
        **kwargs
    ) -> bool:
        """
        Inject debug markers using specified strategy.

        Bridges the engine's dict-based public API to the canonical
        MarkerContext dataclass expected by each strategy.

        Args:
            strategy: Strategy name (test_failure | refactor_regression | governance_violation)
            session_id: Debug session identifier
            file_path: Target file path
            context: Context information for marker (dict — converted to MarkerContext)
            **kwargs: Strategy-specific parameters (e.g., line_number for test_failure)

        Returns:
            True if injection successful, False otherwise
        """
        if strategy not in self.strategies:
            raise ValueError(f"Unknown strategy: {strategy}. Available: {list(self.strategies.keys())}")

        context = context or {}
        line_number = int(kwargs.get("line_number", 0))

        # Build canonical MarkerContext from the dict-based arguments
        marker_context = MarkerContext(
            trigger_type=strategy,
            session_id=session_id,
            file_path=file_path,
            line_number=line_number,
            additional_context=context,
        )

        # Delegate to canonical strategy — returns InjectionResult
        strategy_obj = self.strategies[strategy]
        result: InjectionResult = strategy_obj.inject(marker_context)
        return result.success
    
    def format_marker(
        self,
        session_id: str,
        event_type: str,
        context_summary: str,
        original_code: str
    ) -> str:
        """
        Format marker using template.
        
        Args:
            session_id: Debug session identifier
            event_type: Trigger type (TEST_FAILURE | REFACTOR_REGRESSION | GOVERNANCE_VIOLATION)
            context_summary: Brief description of issue
            original_code: Original code to wrap
        
        Returns:
            Formatted marker string
        """
        return self.MARKER_TEMPLATE.render(
            session_id=session_id,
            trigger_type=event_type,
            context=context_summary,
            timestamp=datetime.now().isoformat()
        )


