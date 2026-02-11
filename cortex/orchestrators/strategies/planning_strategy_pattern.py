"""
PlanningStrategyPattern - Base pattern for consolidating 2 planning orchestrators

Consolidates:
  - PlanningOrchestrator (phase/wave/track planning)
  - CodeLevelPlanner (method/class-level refactoring planning)

Authority: ENH-087 Track 2 + Phase 81 + CORE-035
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)

AC_START: AC-ENH090-S2-GREEN-001
Description: PlanningStrategyPattern base class + concrete implementations
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional, List

logger = logging.getLogger(__name__)


# ============================================================================
# ENUMS & TYPES
# ============================================================================

class PlanningLevel(Enum):
    """Planning scope hierarchy (CORE-042 Hierarchical Terminology)."""
    INITIATIVE = "initiative"      # I-prefix: Org-level (months)
    PHASE = "phase"                # P-prefix: Phase-level (weeks)
    WAVE = "wave"                  # W-prefix: Wave-level (weeks)
    TRACK = "track"                # T-prefix: Track-level (days)
    STAGE = "stage"                # S-prefix: Stage-level (hours)
    TASK = "task"                  # Task-level (minutes)
    METHOD = "method"              # Method-level (seconds)
    CLASS = "class"                # Class-level (seconds)


class PlanningOperationType(Enum):
    """Supported planning operations across consolidated orchestrators."""
    # From PlanningOrchestrator (macro planning)
    PLAN_INITIATIVE = "plan_initiative"
    PLAN_PHASE = "plan_phase"
    PLAN_WAVE = "plan_wave"
    PLAN_TRACK = "plan_track"
    PLAN_STAGE = "plan_stage"
    
    # From CodeLevelPlanner (micro planning)
    PLAN_METHOD_REFACTOR = "plan_method_refactor"
    PLAN_CLASS_REFACTOR = "plan_class_refactor"
    PLAN_DEPENDENCY_INJECTION = "plan_dependency_injection"


class RiskLevel(Enum):
    """Risk assessment levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class PlanningStep:
    """Single step in an execution plan."""
    
    step_number: int
    description: str
    estimated_effort_hours: float
    dependencies: List[int] = field(default_factory=list)  # Step numbers
    risk_level: RiskLevel = RiskLevel.LOW
    success_criteria: Optional[Dict[str, Any]] = None


@dataclass
class PlanningRequest:
    """Unified planning request contract."""
    
    operation: PlanningOperationType
    scope_name: str
    scope_level: PlanningLevel
    current_state: Dict[str, Any]
    target_state: Dict[str, Any]
    constraints: Optional[Dict[str, Any]] = None
    options: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Validate request structure."""
        if not self.scope_name:
            raise ValueError("scope_name is required")
        if self.current_state is None:
            raise ValueError("current_state is required")
        if self.target_state is None:
            raise ValueError("target_state is required")


@dataclass
class PlanningMetrics:
    """Planning operation metrics."""
    
    total_steps: int = 0
    estimated_effort_hours: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    confidence: float = 0.85
    parallel_tracks: int = 1
    critical_path_hours: float = 0.0


@dataclass
class PlanningResult:
    """Unified planning result contract."""
    
    success: bool
    operation: PlanningOperationType
    execution_plan: Optional[List[PlanningStep]] = None
    metrics: Optional[PlanningMetrics] = None
    error: Optional[str] = None
    strategy_used: Optional[str] = None
    
    def __post_init__(self):
        """Initialize metrics if not provided."""
        if self.metrics is None and self.success:
            self.metrics = PlanningMetrics()


# ============================================================================
# BASE STRATEGY CLASS
# ============================================================================

class PlanningStrategy(ABC):
    """
    Base class for planning strategies.
    
    Consolidates capabilities from 2 orchestrators via strategy pattern.
    Each strategy implementation handles a specific planning level range.
    """
    
    def __init__(self, name: str):
        """Initialize strategy.
        
        Args:
            name: Strategy name (e.g., 'MacroPlanningStrategy')
        """
        self.name = name
        self.supported_operations: List[PlanningOperationType] = []
        self.supported_levels: List[PlanningLevel] = []
    
    def can_handle(self, operation: PlanningOperationType) -> bool:
        """
        Check if strategy can handle this operation.
        
        Args:
            operation: Planning operation type
            
        Returns:
            True if strategy supports this operation
        """
        return operation in self.supported_operations
    
    def can_handle_level(self, level: PlanningLevel) -> bool:
        """
        Check if strategy supports this planning level.
        
        Args:
            level: Planning scope level
            
        Returns:
            True if strategy supports this level
        """
        return level in self.supported_levels
    
    @abstractmethod
    def execute(self, request: PlanningRequest) -> PlanningResult:
        """
        Execute planning operation.
        
        Args:
            request: Planning request
            
        Returns:
            Planning result with execution plan and metrics
            
        Raises:
            ValueError: If request is invalid
        """
        pass
    
    @abstractmethod
    def validate_request(self, request: PlanningRequest) -> bool:
        """
        Validate request parameters for this strategy.
        
        Args:
            request: Planning request
            
        Returns:
            True if parameters are valid
            
        Raises:
            ValueError: If parameters are invalid
        """
        pass
    
    def _calculate_effort(self, steps: List[PlanningStep]) -> float:
        """Calculate total effort from steps."""
        return sum(step.estimated_effort_hours for step in steps)


# ============================================================================
# CONCRETE STRATEGY 1: MACRO PLANNING
# ============================================================================

class MacroPlanningStrategy(PlanningStrategy):
    """
    Strategy for macro-level planning (Initiative→Phase→Wave→Track→Stage).
    
    Consolidates PlanningOrchestrator capabilities:
      - PLAN_INITIATIVE: Strategic initiative planning (months)
      - PLAN_PHASE: Phase execution planning (weeks)
      - PLAN_WAVE: Wave lifecycle planning (weeks)
      - PLAN_TRACK: Track scheduling (days)
      - PLAN_STAGE: Stage breakdown (hours)
    """
    
    def __init__(self):
        """Initialize MacroPlanningStrategy."""
        super().__init__("MacroPlanningStrategy")
        self.supported_operations = [
            PlanningOperationType.PLAN_INITIATIVE,
            PlanningOperationType.PLAN_PHASE,
            PlanningOperationType.PLAN_WAVE,
            PlanningOperationType.PLAN_TRACK,
            PlanningOperationType.PLAN_STAGE,
        ]
        self.supported_levels = [
            PlanningLevel.INITIATIVE,
            PlanningLevel.PHASE,
            PlanningLevel.WAVE,
            PlanningLevel.TRACK,
            PlanningLevel.STAGE,
        ]
    
    def validate_request(self, request: PlanningRequest) -> bool:
        """Validate macro planning request."""
        if not request.scope_name:
            raise ValueError("scope_name is required")
        
        # Validate hierarchy levels match
        level_hierarchy = [
            PlanningLevel.INITIATIVE,
            PlanningLevel.PHASE,
            PlanningLevel.WAVE,
            PlanningLevel.TRACK,
            PlanningLevel.STAGE,
        ]
        
        if request.scope_level not in level_hierarchy:
            raise ValueError(f"Invalid scope level for macro planning: {request.scope_level.value}")
        
        # Validate state transitions
        for key, value in request.current_state.items():
            if key not in request.target_state:
                raise ValueError(f"Target state missing key: {key}")
        
        return True
    
    def execute(self, request: PlanningRequest) -> PlanningResult:
        """Execute macro planning operation."""
        try:
            self.validate_request(request)
            
            # Build execution plan (step breakdown by scope level)
            steps = self._build_macro_plan(request)
            
            # Calculate metrics
            effort_hours = self._calculate_effort(steps)
            risk_level = self._assess_risk(request)
            
            metrics = PlanningMetrics(
                total_steps=len(steps),
                estimated_effort_hours=effort_hours,
                risk_level=risk_level,
                confidence=0.90,  # Macro planning is well-understood
                parallel_tracks=self._estimate_parallelism(request),
                critical_path_hours=effort_hours * 0.8  # Critical path heuristic
            )
            
            return PlanningResult(
                success=True,
                operation=request.operation,
                execution_plan=steps,
                metrics=metrics,
                strategy_used=self.name
            )
        except Exception as e:
            logger.exception(f"MacroPlanningStrategy failed: {e}")
            return PlanningResult(
                success=False,
                operation=request.operation,
                error=str(e),
                strategy_used=self.name
            )
    
    def _build_macro_plan(self, request: PlanningRequest) -> List[PlanningStep]:
        """Build macro-level execution plan."""
        steps = []
        
        # Estimate step count based on scope
        scope_level = request.scope_level
        if scope_level == PlanningLevel.INITIATIVE:
            step_count = 5  # Initiative has 5 phases
        elif scope_level == PlanningLevel.PHASE:
            step_count = 4  # Phase has 4 waves
        elif scope_level == PlanningLevel.WAVE:
            step_count = 5  # Wave has 5 tracks
        elif scope_level == PlanningLevel.TRACK:
            step_count = 4  # Track has 4 stages
        else:  # STAGE
            step_count = 3  # Stage has 3 subtasks
        
        effort_per_step = 10.0 / step_count
        
        for i in range(1, step_count + 1):
            # Each step (except first) depends on previous step for sequential execution
            dependencies = [i - 1] if i > 1 else []
            
            step = PlanningStep(
                step_number=i,
                description=f"Step {i}: {request.scope_name}",
                estimated_effort_hours=effort_per_step,
                dependencies=dependencies,
                risk_level=RiskLevel.LOW
            )
            steps.append(step)
        
        return steps
    
    def _assess_risk(self, request: PlanningRequest) -> RiskLevel:
        """Assess planning risk."""
        # Simple risk assessment based on scope
        if request.scope_level in [PlanningLevel.INITIATIVE]:
            return RiskLevel.MEDIUM
        elif request.scope_level in [PlanningLevel.PHASE, PlanningLevel.WAVE]:
            return RiskLevel.LOW
        else:
            return RiskLevel.LOW
    
    def _estimate_parallelism(self, request: PlanningRequest) -> int:
        """Estimate parallel execution tracks."""
        # Macro plans can have limited parallelism
        if request.scope_level == PlanningLevel.WAVE:
            return 3  # Waves can have 3-5 parallel tracks
        elif request.scope_level == PlanningLevel.TRACK:
            return 2  # Tracks have 2-3 parallel stages
        else:
            return 1


# ============================================================================
# CONCRETE STRATEGY 2: MICRO PLANNING
# ============================================================================

class MicroPlanningStrategy(PlanningStrategy):
    """
    Strategy for micro-level planning (Method/Class refactoring planning).
    
    Consolidates CodeLevelPlanner capabilities:
      - PLAN_METHOD_REFACTOR: Method-level refactoring planning
      - PLAN_CLASS_REFACTOR: Class-level refactoring planning
      - PLAN_DEPENDENCY_INJECTION: Dependency injection planning
    """
    
    def __init__(self):
        """Initialize MicroPlanningStrategy."""
        super().__init__("MicroPlanningStrategy")
        self.supported_operations = [
            PlanningOperationType.PLAN_METHOD_REFACTOR,
            PlanningOperationType.PLAN_CLASS_REFACTOR,
            PlanningOperationType.PLAN_DEPENDENCY_INJECTION,
        ]
        self.supported_levels = [
            PlanningLevel.METHOD,
            PlanningLevel.CLASS,
            PlanningLevel.TASK,
        ]
    
    def validate_request(self, request: PlanningRequest) -> bool:
        """Validate micro planning request."""
        if not request.scope_name:
            raise ValueError("scope_name is required")
        
        operation = request.operation
        current = request.current_state
        target = request.target_state
        
        if operation == PlanningOperationType.PLAN_METHOD_REFACTOR:
            if "cyclomatic_complexity" not in current:
                raise ValueError("Method refactoring requires current cyclomatic_complexity")
            if "cyclomatic_complexity" not in target:
                raise ValueError("Method refactoring requires target cyclomatic_complexity")
        
        elif operation == PlanningOperationType.PLAN_CLASS_REFACTOR:
            if "lines_of_code" not in current:
                raise ValueError("Class refactoring requires current lines_of_code")
        
        elif operation == PlanningOperationType.PLAN_DEPENDENCY_INJECTION:
            if "dependencies" not in current:
                raise ValueError("Dependency injection planning requires current dependencies")
        
        return True
    
    def execute(self, request: PlanningRequest) -> PlanningResult:
        """Execute micro planning operation."""
        try:
            self.validate_request(request)
            
            # Build execution plan
            steps = self._build_micro_plan(request)
            
            effort_hours = self._calculate_effort(steps)
            risk_level = self._assess_risk(request)
            
            metrics = PlanningMetrics(
                total_steps=len(steps),
                estimated_effort_hours=effort_hours,
                risk_level=risk_level,
                confidence=0.88,  # Micro planning has more unknowns
                parallel_tracks=1,  # Micro work is mostly sequential
                critical_path_hours=effort_hours
            )
            
            return PlanningResult(
                success=True,
                operation=request.operation,
                execution_plan=steps,
                metrics=metrics,
                strategy_used=self.name
            )
        except Exception as e:
            logger.exception(f"MicroPlanningStrategy failed: {e}")
            return PlanningResult(
                success=False,
                operation=request.operation,
                error=str(e),
                strategy_used=self.name
            )
    
    def _build_micro_plan(self, request: PlanningRequest) -> List[PlanningStep]:
        """Build micro-level execution plan."""
        steps = []
        operation = request.operation
        
        if operation == PlanningOperationType.PLAN_METHOD_REFACTOR:
            # Complexity reduction plan
            current_cc = request.current_state.get("cyclomatic_complexity", 5)
            target_cc = request.target_state.get("cyclomatic_complexity", 2)
            cc_reduction = current_cc - target_cc
            
            steps = [
                PlanningStep(
                    step_number=1,
                    description="Analyze method complexity",
                    estimated_effort_hours=0.5,
                    risk_level=RiskLevel.LOW
                ),
                PlanningStep(
                    step_number=2,
                    description=f"Reduce complexity by {cc_reduction}",
                    estimated_effort_hours=1.5,
                    dependencies=[1],
                    risk_level=RiskLevel.MEDIUM
                ),
                PlanningStep(
                    step_number=3,
                    description="Test and verify",
                    estimated_effort_hours=0.75,
                    dependencies=[2],
                    risk_level=RiskLevel.LOW
                ),
            ]
        
        elif operation == PlanningOperationType.PLAN_CLASS_REFACTOR:
            # Class size reduction plan
            steps = [
                PlanningStep(
                    step_number=1,
                    description="Analyze class structure",
                    estimated_effort_hours=1.0,
                    risk_level=RiskLevel.LOW
                ),
                PlanningStep(
                    step_number=2,
                    description="Extract responsibilities",
                    estimated_effort_hours=3.0,
                    dependencies=[1],
                    risk_level=RiskLevel.MEDIUM
                ),
                PlanningStep(
                    step_number=3,
                    description="Refactor and integrate",
                    estimated_effort_hours=2.0,
                    dependencies=[2],
                    risk_level=RiskLevel.MEDIUM
                ),
            ]
        
        elif operation == PlanningOperationType.PLAN_DEPENDENCY_INJECTION:
            # Dependency injection planning
            dep_count = len(request.current_state.get("dependencies", []))
            
            steps = [
                PlanningStep(
                    step_number=1,
                    description="Analyze dependencies",
                    estimated_effort_hours=1.0,
                    risk_level=RiskLevel.LOW
                ),
                PlanningStep(
                    step_number=2,
                    description=f"Inject {dep_count} dependencies",
                    estimated_effort_hours=2.0 * (dep_count / 5),
                    dependencies=[1],
                    risk_level=RiskLevel.MEDIUM
                ),
                PlanningStep(
                    step_number=3,
                    description="Test integration",
                    estimated_effort_hours=1.5,
                    dependencies=[2],
                    risk_level=RiskLevel.LOW
                ),
            ]
        
        return steps
    
    def _assess_risk(self, request: PlanningRequest) -> RiskLevel:
        """Assess planning risk for micro operations."""
        operation = request.operation
        
        if operation == PlanningOperationType.PLAN_METHOD_REFACTOR:
            current_cc = request.current_state.get("cyclomatic_complexity", 5)
            if current_cc > 10:
                return RiskLevel.HIGH
            return RiskLevel.MEDIUM
        
        elif operation == PlanningOperationType.PLAN_CLASS_REFACTOR:
            loc = request.current_state.get("lines_of_code", 100)
            if loc > 500:
                return RiskLevel.MEDIUM
            return RiskLevel.LOW
        
        else:  # Dependency injection
            return RiskLevel.LOW


# ============================================================================
# UNIFIED PLANNING ORCHESTRATOR (CONSOLIDATION)
# ============================================================================

class UnifiedPlanningOrchestrator:
    """
    Unified orchestrator consolidating 2 orchestrators via strategy pattern.
    
    Consolidates:
      - PlanningOrchestrator (macro planning)
      - CodeLevelPlanner (micro planning)
    
    Provides single entry point for all planning operations from initiative
    level down to method-level refactoring planning.
    """
    
    def __init__(self):
        """Initialize UnifiedPlanningOrchestrator with all strategies."""
        self.strategies: List[PlanningStrategy] = [
            MacroPlanningStrategy(),
            MicroPlanningStrategy(),
        ]
        logger.info(
            f"UnifiedPlanningOrchestrator initialized with {len(self.strategies)} strategies"
        )
    
    def plan_execution(self, request: PlanningRequest) -> PlanningResult:
        """
        Plan execution for given request using appropriate strategy.
        
        Args:
            request: Planning request
            
        Returns:
            Planning result with execution plan and metrics
            
        Raises:
            ValueError: If no strategy can handle the request
        """
        try:
            # Find strategy that can handle this operation
            for strategy in self.strategies:
                if strategy.can_handle(request.operation):
                    if strategy.can_handle_level(request.scope_level):
                        return strategy.execute(request)
            
            # No strategy found
            error_msg = (
                f"No strategy available for operation {request.operation.value} "
                f"at level {request.scope_level.value}"
            )
            logger.error(error_msg)
            return PlanningResult(
                success=False,
                operation=request.operation,
                error=error_msg
            )
        except Exception as e:
            # Graceful error handling
            error_msg = f"Planning orchestrator error: {str(e)}"
            logger.exception(error_msg)
            return PlanningResult(
                success=False,
                operation=request.operation,
                error=error_msg
            )
    
    def get_supported_operations(self) -> List[PlanningOperationType]:
        """Get all supported operations across all strategies."""
        operations = set()
        for strategy in self.strategies:
            operations.update(strategy.supported_operations)
        return sorted(list(operations), key=lambda x: x.value)
    
    def get_supported_levels(self) -> List[PlanningLevel]:
        """Get all supported planning levels across all strategies."""
        levels = set()
        for strategy in self.strategies:
            levels.update(strategy.supported_levels)
        return sorted(list(levels), key=lambda x: x.value)


# AC_COMPLETE: AC-ENH090-S2-GREEN-001 ✅ PlanningStrategyPattern implemented
