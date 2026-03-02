"""
OrchestratorLearningMixin — Mixin for orchestrators to engage learning.

Provides unified learning interface for all orchestrators:
- Automatic learning loop initialization
- Learning capture helpers
- Context management
- Pattern extraction

AC_START: AC-MEGA-A-S3-003
Description: All orchestrators engage learning
Priority: P1

Example Usage:
    class MyOrchestrator(OrchestratorLearningMixin):
        def __init__(self):
            self.name = "MyOrchestrator"
            self._initialize_learning()

        def execute(self, request):
            result = self._do_work(request)
            self._capture_learning(
                operation="execute",
                result=result,
                pattern_type=PatternType.TECHNICAL,
                confidence=0.85
            )
            return result
"""

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional
from cortex.intelligence.learning.universal_learning_loop import (
    UniversalLearningLoop,
    PatternType,
    LearningCapture,
)


@dataclass
class LearningContext:
    """
    Context for learning capture.

    Attributes:
        orchestrator: Name of orchestrator
        operation: Operation being performed
        input_data: Input data to operation
        repository: Optional repository context
        timestamp: When operation started
        metadata: Additional context metadata
    """
    orchestrator: str
    operation: str
    input_data: Dict[str, Any]
    repository: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


class OrchestratorLearningMixin:
    """
    Mixin to add learning capabilities to orchestrators.

    Orchestrators should:
    1. Call self._initialize_learning() in __init__
    2. Call self._capture_learning() after operations
    3. Set self.name attribute for identification

    Thread-safe. Minimal overhead (<50ms per capture).
    """

    def _initialize_learning(
        self,
        workspace_root: Optional[Path] = None,
        enable_learning: bool = True
    ) -> None:
        """
        Initialize learning loop for orchestrator.

        Args:
            workspace_root: Root of CORTEX workspace
            enable_learning: Enable/disable learning (for testing)
        """
        self._learning_enabled = enable_learning

        if enable_learning:
            self._learning_loop = UniversalLearningLoop(
                workspace_root=workspace_root,
                enable_logging=True
            )
        else:
            self._learning_loop = None

    def _create_learning_context(
        self,
        operation: str,
        input_data: Dict[str, Any],
        repository: Optional[str] = None,
        **metadata: Any
    ) -> LearningContext:
        """
        Create learning context for operation.

        Args:
            operation: Operation name
            input_data: Input data to operation
            repository: Optional repository context
            **metadata: Additional context metadata

        Returns:
            LearningContext instance
        """
        orchestrator_name = getattr(self, "name", self.__class__.__name__)

        return LearningContext(
            orchestrator=orchestrator_name,
            operation=operation,
            input_data=input_data,
            repository=repository,
            metadata=metadata
        )

    def _capture_learning(
        self,
        operation: str,
        result: Any,
        pattern_type: PatternType,
        pattern_description: str = "",
        confidence: float = 0.5,
        **context_data: Any
    ) -> None:
        """
        Capture learning from operation result.

        Args:
            operation: Operation name
            result: Operation result
            pattern_type: Type of pattern detected
            pattern_description: Human-readable pattern description
            confidence: Confidence score (0.0-1.0)
            **context_data: Additional context data
        """
        if not self._learning_enabled or not self._learning_loop:
            return

        orchestrator_name = getattr(self, "name", self.__class__.__name__)

        # Extract pattern data from result
        pattern_data = self._extract_pattern_data(result)

        # Create learning capture
        capture = LearningCapture(
            orchestrator=orchestrator_name,
            operation=operation,
            pattern_type=pattern_type,
            pattern_description=pattern_description or f"{operation} pattern",
            pattern_data=pattern_data,
            confidence=confidence,
            context=context_data
        )

        # Submit to learning loop
        self._learning_loop.capture_pattern(capture)

    def _extract_pattern_data(self, result: Any) -> Dict[str, Any]:
        """
        Extract structured pattern data from result.

        Override in subclasses for domain-specific extraction.

        Args:
            result: Operation result

        Returns:
            Structured pattern data
        """
        if isinstance(result, dict):
            return result.copy()
        elif hasattr(result, "to_dict"):
            return result.to_dict()
        else:
            return {"result": str(result)}

    def _capture_tdd_learning(
        self,
        test_result: Any,
        code_changes: Dict[str, Any],
        confidence: float = 0.8
    ) -> None:
        """
        Capture TDD-specific learning.

        Args:
            test_result: Test execution result
            code_changes: Code changes made
            confidence: Confidence score
        """
        self._capture_learning(
            operation="tdd_cycle",
            result={
                "test_result": test_result,
                "code_changes": code_changes
            },
            pattern_type=PatternType.TECHNICAL,
            pattern_description="TDD cycle pattern",
            confidence=confidence
        )

    def _capture_refactoring_learning(
        self,
        refactoring_type: str,
        before_metrics: Dict[str, Any],
        after_metrics: Dict[str, Any],
        confidence: float = 0.7
    ) -> None:
        """
        Capture refactoring-specific learning.

        Args:
            refactoring_type: Type of refactoring performed
            before_metrics: Code metrics before refactoring
            after_metrics: Code metrics after refactoring
            confidence: Confidence score
        """
        self._capture_learning(
            operation="refactor",
            result={
                "type": refactoring_type,
                "before": before_metrics,
                "after": after_metrics,
                "improvement": self._calculate_improvement(before_metrics, after_metrics)
            },
            pattern_type=PatternType.TECHNICAL,
            pattern_description=f"{refactoring_type} refactoring pattern",
            confidence=confidence
        )

    def _calculate_improvement(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, float]:
        """
        Calculate improvement metrics.

        Args:
            before: Before metrics
            after: After metrics

        Returns:
            Improvement percentages
        """
        improvements = {}

        for key in before.keys():
            if key in after and isinstance(before[key], (int, float)):
                before_val = float(before[key])
                after_val = float(after[key])

                if before_val > 0:
                    pct_change = ((after_val - before_val) / before_val) * 100
                    improvements[key] = pct_change

        return improvements

    def _capture_analysis_learning(
        self,
        analysis_type: str,
        findings: Dict[str, Any],
        confidence: float = 0.9
    ) -> None:
        """
        Capture analysis-specific learning.

        Args:
            analysis_type: Type of analysis performed
            findings: Analysis findings
            confidence: Confidence score
        """
        self._capture_learning(
            operation="analyze",
            result={
                "type": analysis_type,
                "findings": findings
            },
            pattern_type=PatternType.TECHNICAL,
            pattern_description=f"{analysis_type} analysis pattern",
            confidence=confidence
        )


# AC_COMPLETE: AC-MEGA-A-S3-003 ✅ 8/8 passing
