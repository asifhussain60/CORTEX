"""
Phase Manager for CORTEX 4.0 Orchestrators

Manages orchestrator phases with:
- Phase registration and execution
- Phase transitions with validation
- State tracking and history
- Rollback capabilities
- Phase dependencies

Supports multi-phase orchestrators like:
- Planning System (analyze → plan → validate → execute)
- Maintenance (healthcheck → align → cleanup → optimize)
- TDD Workflow (RED → GREEN → REFACTOR)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional


logger = logging.getLogger(__name__)


class PhaseStatus(Enum):
    """Status of a phase execution."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PhaseResult:
    """Result of phase execution."""
    phase_name: str
    status: PhaseStatus
    success: bool
    message: str
    data: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    execution_time_seconds: float = 0.0
    
    def complete(self, success: bool = True, message: str = ""):
        """Mark phase as complete."""
        self.end_time = datetime.now()
        self.execution_time_seconds = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.status = PhaseStatus.COMPLETED if success else PhaseStatus.FAILED
        if message:
            self.message = message


@dataclass
class PhaseTransition:
    """Phase transition definition."""
    from_phase: str
    to_phase: str
    condition: Optional[Callable[[], bool]] = None
    automatic: bool = True
    
    def can_transition(self) -> bool:
        """Check if transition is allowed."""
        if self.condition is None:
            return True
        return self.condition()


class RecoveryStrategy(Enum):
    """Recovery strategies for failed phases."""
    RETRY = "retry"              # Retry the failed phase
    SKIP = "skip"                # Skip and continue to next phase
    ROLLBACK = "rollback"        # Rollback to previous phase
    ABORT = "abort"              # Abort orchestrator execution
    MANUAL = "manual"            # Require manual intervention


@dataclass
class Phase:
    """Phase definition."""
    name: str
    func: Callable[[], PhaseResult]
    dependencies: List[str] = field(default_factory=list)
    required: bool = True
    recovery_strategy: RecoveryStrategy = RecoveryStrategy.ABORT
    max_retries: int = 0
    description: str = ""


class PhaseManager:
    """
    Manages phases for orchestrators with multi-phase workflows.
    
    Features:
    - Phase registration with dependencies
    - Sequential or DAG-based execution
    - Phase transitions with validation
    - State tracking and history
    - Rollback capabilities
    - Recovery strategies
    
    Usage:
        manager = PhaseManager()
        manager.register_phase("analyze", analyze_func, required=True)
        manager.register_phase("plan", plan_func, dependencies=["analyze"])
        manager.register_phase("execute", execute_func, dependencies=["plan"])
        
        result = manager.execute_all()
    """
    
    def __init__(self):
        """Initialize phase manager."""
        self.phases: Dict[str, Phase] = {}
        self.phase_history: List[PhaseResult] = []
        self.current_phase: Optional[str] = None
        self.transitions: List[PhaseTransition] = []
        self.phase_order: List[str] = []
        
        logger.debug("PhaseManager initialized")
    
    def register_phase(
        self,
        phase_name: str,
        phase_func: Callable[[], PhaseResult],
        dependencies: List[str] = None,
        required: bool = True,
        recovery_strategy: RecoveryStrategy = RecoveryStrategy.ABORT,
        max_retries: int = 0,
        description: str = ""
    ) -> None:
        """
        Register a phase with the manager.
        
        Args:
            phase_name: Unique phase identifier
            phase_func: Function to execute for this phase
            dependencies: List of phase names that must complete first
            required: Whether phase must succeed for orchestrator to continue
            recovery_strategy: How to handle phase failure
            max_retries: Maximum retry attempts on failure
            description: Human-readable phase description
        """
        if phase_name in self.phases:
            logger.warning(f"Phase '{phase_name}' already registered, overwriting")
        
        phase = Phase(
            name=phase_name,
            func=phase_func,
            dependencies=dependencies or [],
            required=required,
            recovery_strategy=recovery_strategy,
            max_retries=max_retries,
            description=description
        )
        
        self.phases[phase_name] = phase
        
        # Update phase order (topological sort would go here for DAG)
        if phase_name not in self.phase_order:
            self.phase_order.append(phase_name)
        
        logger.info(f"Registered phase: {phase_name} (required={required}, deps={dependencies})")
    
    def execute_phase(self, phase_name: str) -> PhaseResult:
        """
        Execute a specific phase.
        
        Args:
            phase_name: Name of phase to execute
        
        Returns:
            PhaseResult with execution details
        
        Raises:
            ValueError: If phase not registered
        """
        if phase_name not in self.phases:
            raise ValueError(f"Phase '{phase_name}' not registered")
        
        phase = self.phases[phase_name]
        
        # Check dependencies
        for dep in phase.dependencies:
            if not self._is_phase_completed(dep):
                error_msg = f"Dependency '{dep}' not completed for phase '{phase_name}'"
                logger.error(error_msg)
                return PhaseResult(
                    phase_name=phase_name,
                    status=PhaseStatus.FAILED,
                    success=False,
                    message=error_msg,
                    errors=[error_msg]
                )
        
        # Execute phase with retry logic
        logger.info(f"🎭 Phase transition: {self.current_phase or 'START'} → {phase_name}")
        self.current_phase = phase_name
        
        attempts = 0
        max_attempts = phase.max_retries + 1
        
        while attempts < max_attempts:
            attempts += 1
            
            try:
                # Execute phase function
                result = phase.func()
                result.phase_name = phase_name
                
                # Record result
                self.phase_history.append(result)
                
                if result.success:
                    logger.info(f"✅ Phase '{phase_name}' completed successfully")
                    return result
                else:
                    logger.warning(f"⚠️ Phase '{phase_name}' failed (attempt {attempts}/{max_attempts})")
                    
                    if attempts < max_attempts:
                        logger.info(f"Retrying phase '{phase_name}'...")
                        continue
                    else:
                        return result
            
            except Exception as e:
                logger.error(f"Exception in phase '{phase_name}': {e}", exc_info=True)
                
                result = PhaseResult(
                    phase_name=phase_name,
                    status=PhaseStatus.FAILED,
                    success=False,
                    message=f"Phase failed with exception: {str(e)}",
                    errors=[str(e)]
                )
                result.complete(success=False)
                self.phase_history.append(result)
                
                if attempts < max_attempts:
                    logger.info(f"Retrying phase '{phase_name}' after exception...")
                    continue
                else:
                    return result
        
        # Should never reach here, but return last result as fallback
        return self.phase_history[-1]
    
    def execute_all(self) -> List[PhaseResult]:
        """
        Execute all registered phases in order.
        
        Returns:
            List of PhaseResult for each executed phase
        """
        logger.info(f"Executing {len(self.phase_order)} phases: {', '.join(self.phase_order)}")
        
        results = []
        
        for phase_name in self.phase_order:
            phase = self.phases[phase_name]
            result = self.execute_phase(phase_name)
            results.append(result)
            
            # Handle failure based on recovery strategy
            if not result.success and phase.required:
                strategy = phase.recovery_strategy
                
                if strategy == RecoveryStrategy.ABORT:
                    logger.error(f"Required phase '{phase_name}' failed, aborting")
                    break
                elif strategy == RecoveryStrategy.SKIP:
                    logger.warning(f"Phase '{phase_name}' failed, skipping to next phase")
                    continue
                elif strategy == RecoveryStrategy.ROLLBACK:
                    logger.warning(f"Phase '{phase_name}' failed, attempting rollback")
                    rollback_result = self.rollback_phase()
                    if not rollback_result:
                        logger.error("Rollback failed, aborting")
                        break
        
        logger.info(f"🎭 Phase execution complete: {len(results)} phases executed")
        return results
    
    def transition(self, from_phase: str, to_phase: str, condition: Optional[Callable] = None) -> bool:
        """
        Define a phase transition.
        
        Args:
            from_phase: Source phase
            to_phase: Target phase
            condition: Optional condition that must be true for transition
        
        Returns:
            True if transition defined successfully
        """
        transition = PhaseTransition(
            from_phase=from_phase,
            to_phase=to_phase,
            condition=condition
        )
        
        self.transitions.append(transition)
        logger.debug(f"Defined transition: {from_phase} → {to_phase}")
        
        return True
    
    def get_current_phase(self) -> Optional[str]:
        """
        Get name of currently executing phase.
        
        Returns:
            Current phase name or None if no phase is executing
        """
        return self.current_phase
    
    def rollback_phase(self) -> bool:
        """
        Rollback to previous phase.
        
        Returns:
            True if rollback successful
        """
        if len(self.phase_history) < 2:
            logger.warning("Cannot rollback: insufficient phase history")
            return False
        
        # Remove current failed phase
        failed_phase = self.phase_history.pop()
        
        # Get previous phase
        previous_phase = self.phase_history[-1]
        
        logger.info(f"Rolling back from '{failed_phase.phase_name}' to '{previous_phase.phase_name}'")
        self.current_phase = previous_phase.phase_name
        
        return True
    
    def get_phase_history(self) -> List[PhaseResult]:
        """
        Get history of all executed phases.
        
        Returns:
            List of PhaseResult in execution order
        """
        return self.phase_history.copy()
    
    def get_phase_status(self, phase_name: str) -> Optional[PhaseStatus]:
        """
        Get status of a specific phase.
        
        Args:
            phase_name: Name of phase
        
        Returns:
            PhaseStatus or None if phase hasn't been executed
        """
        for result in reversed(self.phase_history):
            if result.phase_name == phase_name:
                return result.status
        return None
    
    def _is_phase_completed(self, phase_name: str) -> bool:
        """
        Check if phase has completed successfully.
        
        Args:
            phase_name: Name of phase to check
        
        Returns:
            True if phase completed successfully
        """
        status = self.get_phase_status(phase_name)
        return status == PhaseStatus.COMPLETED
    
    def reset(self) -> None:
        """Reset phase manager state."""
        self.phase_history.clear()
        self.current_phase = None
        logger.info("PhaseManager state reset")
    
    def __repr__(self) -> str:
        """String representation."""
        return f"PhaseManager(phases={len(self.phases)}, current={self.current_phase})"
