"""
Wave 8 Stage 1: Strategy Base Class

Base classes and models for planning execution strategies.

AC-ID: AC-WAVE-8-S1-001
Authority: Wave 8 Execution Activation
Coverage Target: ≥95%
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from enum import Enum


class ExecutionStatus(str, Enum):
    """Execution status enumeration."""
    SUCCESS = "success"
    FAILURE = "failure"
    SKIPPED = "skipped"
    PENDING = "pending"
    IN_PROGRESS = "in_progress"


@dataclass
class ExecutionContext:
    """
    Execution context for strategies.

    Attributes:
        strategy_type: Type of strategy (phase/wave/track)
        phase_id: Unique phase identifier (optional, defaults to wave_id or track_id)
        data: Context data dictionary
        wave_id: Wave identifier (optional, for wave strategies)
        track_id: Track identifier (optional, for track strategies)
        phase_name: Human-readable phase name (optional)
        status: Current phase status
        tasks: List of tasks in the phase
        dependencies: List of dependency phase IDs
        resources: Resource allocation map
        metadata: Additional context data
    """
    strategy_type: str
    phase_id: str = ""
    data: Dict[str, Any] = field(default_factory=dict)
    wave_id: Optional[str] = None
    track_id: Optional[str] = None
    phase_name: str = ""
    status: str = "ready"
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    resources: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Auto-populate phase_id from wave_id or track_id if not provided."""
        if not self.phase_id:
            self.phase_id = self.wave_id or self.track_id or "unknown"


@dataclass
class ExecutionResult:
    """
    Execution result from strategy.

    Attributes:
        success: True if execution succeeded
        phase_id: Phase identifier
        message: Result message
        status: Execution status
        output: Execution output data
        error: Error message (if failed)
        metrics: Execution metrics
    """
    success: bool
    phase_id: str = ""
    message: str = ""
    status: Optional[ExecutionStatus] = None
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ValidationResult:
    """
    Validation result from strategy.

    Attributes:
        passed: True if validation passed (matches test expectation)
        valid: Alias for passed (backward compatibility)
        errors: List of validation errors
        warnings: List of validation warnings
    """
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        """Alias for passed."""
        return self.passed


class ExecutionStrategy(ABC):
    """
    Base class for all planning execution strategies.

    All strategies must implement execute() and validate() methods.
    This enforces a consistent interface across all strategy types.

    Example:
        class CustomStrategy(ExecutionStrategy):
            def execute(self, context: ExecutionContext) -> ExecutionResult:
                # Implementation here
                pass

            def validate(self, context: ExecutionContext) -> ValidationResult:
                # Validation logic here
                pass
    """

    @abstractmethod
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """
        Execute strategy against provided context.

        Args:
            context: Execution context containing phase data

        Returns:
            ExecutionResult with success/failure and output data
        """
        pass

    @abstractmethod
    def validate(self, context: ExecutionContext) -> ValidationResult:
        """
        Validate strategy preconditions.

        Args:
            context: Execution context to validate

        Returns:
            ValidationResult with any errors/warnings
        """
        pass
