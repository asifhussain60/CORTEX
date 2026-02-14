"""
Stage Execution Strategy — Base Pattern for 4-Stage Pipeline.

Defines the StageContext data carrier and StageExecutionStrategy ABC
for the ENH-087 MasterOrchestrator strategy pipeline.

Each stage:
1. Receives a StageContext with accumulated metadata
2. Executes its specific logic
3. Returns updated StageContext via Result pattern

Authority: ENH-087 Track 1.1, CORE-008 (TDD), CORE-011, CORE-012
AC_START: AC-P1-STAGE-STRATEGY-BASE-001
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

from cortex.brain.core.result import Result


@dataclass
class StageContext:
    """
    Context carrier passed through the 4-stage execution pipeline.

    Accumulates metadata from each stage and carries the final result.
    Each stage reads from metadata and adds its own keys.

    Attributes:
        operation_name: Name of the operation being executed.
        parameters: Original operation parameters from caller.
        metadata: Accumulated metadata from all stages.
        result: Final result after pipeline completes (None during execution).
    """

    operation_name: str
    parameters: Dict[str, Any]
    metadata: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None


class StageExecutionStrategy(ABC):
    """
    Abstract base for pipeline stage strategies.

    Each stage in the 4-stage pipeline implements this interface:
    - Stage 1: Comprehension (LENS analysis)
    - Stage 2: Intent Classification
    - Stage 3: Compliance Validation
    - Stage 4: Domain Execution

    Subclasses must implement execute() which receives a StageContext
    and returns Result[StageContext] with updated metadata.
    """

    @abstractmethod
    def execute(self, context: StageContext) -> Result[StageContext]:
        """
        Execute this stage's logic.

        Args:
            context: StageContext with accumulated state from prior stages.

        Returns:
            Result[StageContext] with updated metadata, or Err on failure.
        """
        pass

    @property
    def stage_name(self) -> str:
        """Get human-readable stage name.

        Returns:
            Stage name string.
        """
        return self.__class__.__name__


# AC_COMPLETE: AC-P1-STAGE-STRATEGY-BASE-001
