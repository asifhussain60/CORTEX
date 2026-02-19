"""
OrchestratorBase — 5-step lifecycle orchestrator implementation.

Lifecycle: setup → govern → execute → validate → teardown

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging


class LifecycleStage(Enum):
    """Orchestrator lifecycle stages."""
    
    SETUP = "setup"
    GOVERN = "govern"
    EXECUTE = "execute"
    VALIDATE = "validate"
    TEARDOWN = "teardown"


@dataclass
class ExecutionResult:
    """Result of orchestrator execution."""
    
    success: bool
    stage: LifecycleStage
    duration_ms: int
    error: Optional[str] = None
    output: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GovernanceDecision:
    """Result of governance gate evaluation."""
    
    allowed: bool
    reason: str
    violations: List[str] = field(default_factory=list)
    challenges: List[Dict[str, str]] = field(default_factory=list)


class OrchestratorBase(ABC):
    """Base class for all orchestrators with 5-step lifecycle."""
    
    def __init__(self, orchestrator_id: str) -> None:
        """Initialize orchestrator.
        
        Args:
            orchestrator_id: Unique identifier for this orchestrator.
        """
        self.orchestrator_id = orchestrator_id
        self.logger = logging.getLogger(f"cortex.orchestrators.{orchestrator_id}")
        self.execution_results: List[ExecutionResult] = []
        self._governance_decision: Optional[GovernanceDecision] = None
    
    def execute(self) -> ExecutionResult:
        """Execute the 5-step orchestrator lifecycle.
        
        Returns:
            ExecutionResult: Result of execution.
        """
        start_time = datetime.now()
        result = None
        
        try:
            # Step 1: Setup
            self.logger.debug(f"{self.orchestrator_id}: Entering SETUP phase")
            self.setup()
            
            # Step 2: Govern (governance gate)
            self.logger.debug(f"{self.orchestrator_id}: Entering GOVERN phase")
            governance_result = self.govern()
            
            if not governance_result.allowed:
                self.logger.warning(
                    f"{self.orchestrator_id}: Governance gate blocked execution: {governance_result.reason}"
                )
                result = ExecutionResult(
                    success=False,
                    stage=LifecycleStage.GOVERN,
                    duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    error=governance_result.reason,
                )
                return result
            
            # Step 3: Execute
            self.logger.debug(f"{self.orchestrator_id}: Entering EXECUTE phase")
            exec_output = self.execute_operation()
            
            # Step 4: Validate
            self.logger.debug(f"{self.orchestrator_id}: Entering VALIDATE phase")
            is_valid = self.validate(exec_output)
            
            if not is_valid:
                self.logger.error(f"{self.orchestrator_id}: Validation failed")
                result = ExecutionResult(
                    success=False,
                    stage=LifecycleStage.VALIDATE,
                    duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    error="Validation failed",
                    output=exec_output,
                )
            else:
                result = ExecutionResult(
                    success=True,
                    stage=LifecycleStage.EXECUTE,
                    duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    output=exec_output,
                )
        
        except Exception as e:
            self.logger.exception(f"{self.orchestrator_id}: Exception during execution")
            result = ExecutionResult(
                success=False,
                stage=LifecycleStage.EXECUTE,
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                error=str(e),
            )
        
        finally:
            # Step 5: Teardown (always runs)
            self.logger.debug(f"{self.orchestrator_id}: Entering TEARDOWN phase")
            self.teardown(result)
        
        self.execution_results.append(result)
        return result
    
    @abstractmethod
    def setup(self) -> None:
        """Setup phase: Initialize context, load templates, validate dependencies.
        
        Raises:
            Exception: If setup fails.
        """
        pass
    
    def govern(self) -> GovernanceDecision:
        """Governance phase: Evaluate CORE rules, governance gate.
        
        Returns:
            GovernanceDecision: Allow/block decision with reasoning.
        """
        # Default: allow execution
        # Subclasses can override to implement governance logic
        return GovernanceDecision(
            allowed=True,
            reason="No governance constraints",
        )
    
    @abstractmethod
    def execute_operation(self) -> Dict[str, Any]:
        """Execute phase: Primary orchestration logic.
        
        Returns:
            Dictionary with execution output.
        """
        pass
    
    def validate(self, output: Dict[str, Any]) -> bool:
        """Validate phase: Test results, regression check, coherence validation.
        
        Args:
            output: Output from execute phase.
            
        Returns:
            True if validation passes, False otherwise.
        """
        # Default: pass validation
        # Subclasses can override to implement validation logic
        return True
    
    def teardown(self, result: Optional[ExecutionResult] = None) -> None:
        """Teardown phase: Write SQLite audit, cleanup resources, sync state.
        
        This phase ALWAYS runs, even if execution failed.
        
        Args:
            result: Result of execution (may be None if setup failed).
        """
        # Write to SQLite audit database (CORE-027)
        from cortex.infrastructure.audit_db import get_audit_db, AuditEntry, EventType
        
        audit_db = get_audit_db()
        
        if result:
            entry = AuditEntry(
                event_type=EventType.ORCHESTRATOR_END.value,
                orchestrator_id=self.orchestrator_id,
                status="success" if result.success else "failed",
                duration_ms=result.duration_ms,
                error_message=result.error,
                metadata=result.output or {},
            )
            audit_db.log_event(entry)
            
            self.logger.info(
                f"{self.orchestrator_id}: Execution complete - "
                f"success={result.success}, duration_ms={result.duration_ms}"
            )
    
    def get_execution_history(self) -> List[ExecutionResult]:
        """Get the history of execution results.
        
        Returns:
            List of ExecutionResult objects.
        """
        return self.execution_results.copy()
    
    def get_latest_result(self) -> Optional[ExecutionResult]:
        """Get the most recent execution result.
        
        Returns:
            Most recent ExecutionResult or None if no executions.
        """
        return self.execution_results[-1] if self.execution_results else None
