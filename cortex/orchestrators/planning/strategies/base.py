"""
Wave 8 Stage 1: Strategy Base Classes and Models

Provides abstract base class and data models for all execution strategies.
Authority: Wave 8 Execution Activation
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime


@dataclass
class ExecutionContext:
    """
    Context passed to execution strategies.
    
    AC_START: AC-WAVE8-STAGE1-BASE-001
    Provides unified interface for all strategy types (phase, wave, track).
    """
    strategy_type: str  # "phase", "wave", or "track"
    phase_id: Optional[str] = None
    wave_id: Optional[str] = None
    track_id: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def __post_init__(self):
        """Validate context on creation."""
        if self.strategy_type not in ("phase", "wave", "track"):
            raise ValueError(f"Invalid strategy_type: {self.strategy_type}")


@dataclass
class ExecutionResult:
    """
    Result of strategy execution.
    
    AC_START: AC-WAVE8-STAGE1-BASE-002
    Standard result format across all strategies.
    """
    success: bool
    phase_id: Optional[str] = None
    wave_id: Optional[str] = None
    track_id: Optional[str] = None
    message: str = ""
    error: Optional[str] = None
    data: Dict[str, Any] = field(default_factory=dict)
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    rollback_executed: bool = False
    timestamp: datetime = field(default_factory=datetime.utcnow)


@dataclass
class ValidationResult:
    """
    Result of strategy validation.
    
    AC_START: AC-WAVE8-STAGE1-BASE-003
    Pre-execution validation to catch issues early.
    """
    passed: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)

    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.passed = False

    def add_warning(self, warning: str) -> None:
        """Add validation warning (non-blocking)."""
        self.warnings.append(warning)


class ExecutionStrategy(ABC):
    """
    Abstract base class for all execution strategies.
    
    AC_START: AC-WAVE8-STAGE1-BASE-004
    Provides common interface for PhaseExecutionStrategy, WaveOrchestrationStrategy,
    and TrackParallelizationStrategy. Enables composition and delegation patterns.
    
    Example:
        >>> phase_strategy = PhaseExecutionStrategy()
        >>> context = ExecutionContext(strategy_type="phase", phase_id="P1")
        >>> result = phase_strategy.execute(context)
        >>> if result.success:
        ...     print("Phase executed successfully")
    """

    def __init__(self):
        """Initialize strategy with logging and audit trail."""
        self._execution_log: List[Dict[str, Any]] = []
        self._metrics: Dict[str, Any] = {}

    @abstractmethod
    def execute(self, context: ExecutionContext) -> ExecutionResult:
        """
        Execute the strategy against provided context.
        
        Must be implemented by concrete strategies.
        
        Args:
            context: ExecutionContext with strategy-specific data
            
        Returns:
            ExecutionResult indicating success/failure
            
        Raises:
            ValueError: If context is invalid
            RuntimeError: If execution fails
        """
        pass

    @abstractmethod
    def validate(self) -> ValidationResult:
        """
        Validate strategy preconditions.
        
        Should check all prerequisites before execution.
        
        Returns:
            ValidationResult with pass/fail status
        """
        pass

    def log_execution(self, event: str, data: Dict[str, Any]) -> None:
        """
        Log execution event for audit trail.
        
        AC_START: AC-WAVE8-STAGE1-BASE-005
        """
        self._execution_log.append({
            "event": event,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        })

    def record_metric(self, name: str, value: float) -> None:
        """
        Record execution metric.
        
        AC_START: AC-WAVE8-STAGE1-BASE-006
        """
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)

    def get_execution_log(self) -> List[Dict[str, Any]]:
        """Return execution log for audit trail."""
        return self._execution_log.copy()

    def get_metrics(self) -> Dict[str, Any]:
        """Return collected metrics."""
        return self._metrics.copy()

    # AC_COMPLETE: AC-WAVE8-STAGE1-BASE-001 through AC-WAVE8-STAGE1-BASE-006
