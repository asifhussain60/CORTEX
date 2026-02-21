"""
OrchestratorBase - 5-step lifecycle orchestrator implementation.

Lifecycle: setup -> govern -> execute -> validate -> teardown

Authority: CORE-008 (TDD) | CORE-011 (type hints) | CORE-012 (docstrings)
"""

from abc import ABC
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import inspect
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

    def __init__(self, orchestrator_id: str = "unnamed") -> None:
        """Initialize orchestrator."""
        self.orchestrator_id = orchestrator_id
        self.logger = logging.getLogger(f"cortex.orchestrators.{orchestrator_id}")
        self.execution_results: List[ExecutionResult] = []
        self._governance_decision: Optional[GovernanceDecision] = None

    def execute(self) -> ExecutionResult:
        """Execute the 5-step orchestrator lifecycle."""
        start_time = datetime.now()
        result = None

        # Universal activity log — START (CORE-049: silent, no opt-in required)
        try:
            from cortex.infrastructure.audit_db import get_audit_db, AuditEntry, EventType
            get_audit_db().log_event(AuditEntry(
                event_type=EventType.ORCHESTRATOR_START.value,
                orchestrator_id=self.orchestrator_id,
                status="started",
                metadata={"class": type(self).__name__},
            ))
        except Exception:
            pass  # audit must never block execution

        try:
            self.logger.debug(f"{self.orchestrator_id}: Entering SETUP phase")
            self.setup()

            self.logger.debug(f"{self.orchestrator_id}: Entering GOVERN phase")
            governance_result = self.govern()

            if governance_result is not None and hasattr(governance_result, 'allowed'):
                if not governance_result.allowed:
                    self.logger.warning(
                        f"{self.orchestrator_id}: Governance gate blocked: {governance_result.reason}"
                    )
                    result = ExecutionResult(
                        success=False,
                        stage=LifecycleStage.GOVERN,
                        duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                        error=governance_result.reason,
                    )
                    return result

            self.logger.debug(f"{self.orchestrator_id}: Entering EXECUTE phase")
            exec_output = self.execute_operation()

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
            self.logger.debug(f"{self.orchestrator_id}: Entering TEARDOWN phase")
            try:
                teardown_sig = inspect.signature(self.teardown)
                teardown_params = [p for p in teardown_sig.parameters if p != 'self']
                if len(teardown_params) > 0:
                    self.teardown(result)
                else:
                    self.teardown()
            except Exception:
                pass

        self.execution_results.append(result)
        return result

    def run(self) -> ExecutionResult:
        """Run the orchestrator lifecycle (simple 5-step).

        Calls subclass-defined methods directly. Exceptions propagate after teardown.
        """
        start_time = datetime.now()
        result = None
        exc_to_raise = None

        # Universal activity log — START
        try:
            from cortex.infrastructure.audit_db import get_audit_db, AuditEntry, EventType
            get_audit_db().log_event(AuditEntry(
                event_type=EventType.ORCHESTRATOR_START.value,
                orchestrator_id=self.orchestrator_id,
                status="started",
                metadata={"class": type(self).__name__, "via": "run"},
            ))
        except Exception:
            pass  # audit must never block execution

        try:
            self.setup()

            governance_result = self.govern()
            if governance_result is not None and hasattr(governance_result, 'allowed'):
                if not governance_result.allowed:
                    result = ExecutionResult(
                        success=False,
                        stage=LifecycleStage.GOVERN,
                        duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                        error=getattr(governance_result, 'reason', 'Governance blocked'),
                    )
                    return result

            # Determine which method to call for execute step
            exec_cls_method = type(self).execute_operation
            base_cls_method = OrchestratorBase.execute_operation
            exec_main = type(self).execute
            base_main = OrchestratorBase.execute

            if exec_cls_method is not base_cls_method:
                exec_output = self.execute_operation()
            elif exec_main is not base_main:
                exec_output = self.execute() or {}
            else:
                exec_output = self.execute_operation()

            validate_sig = inspect.signature(self.validate)
            validate_params = [p for p in validate_sig.parameters if p != 'self']
            if len(validate_params) > 0:
                is_valid = self.validate(exec_output)
            else:
                is_valid = self.validate()

            if is_valid is None or is_valid:
                result = ExecutionResult(
                    success=True,
                    stage=LifecycleStage.EXECUTE,
                    duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    output=exec_output if isinstance(exec_output, dict) else {},
                )
            else:
                result = ExecutionResult(
                    success=False,
                    stage=LifecycleStage.VALIDATE,
                    duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                    error="Validation failed",
                    output=exec_output if isinstance(exec_output, dict) else {},
                )
        except Exception as e:
            self.logger.exception(f"{self.orchestrator_id}: Exception during run()")
            exc_to_raise = e
            result = ExecutionResult(
                success=False,
                stage=LifecycleStage.EXECUTE,
                duration_ms=int((datetime.now() - start_time).total_seconds() * 1000),
                error=str(e),
            )
        finally:
            try:
                teardown_sig = inspect.signature(self.teardown)
                teardown_params = [p for p in teardown_sig.parameters if p != 'self']
                if len(teardown_params) > 0:
                    self.teardown(result)
                else:
                    self.teardown()
            except Exception:
                pass

        if result:
            self.execution_results.append(result)

        if exc_to_raise is not None:
            raise exc_to_raise

        return result

    def setup(self) -> None:
        """Setup phase: Initialize context, load templates, validate dependencies."""
        pass

    def govern(self) -> GovernanceDecision:
        """Governance phase: Evaluate CORE rules, governance gate."""
        return GovernanceDecision(allowed=True, reason="No governance constraints")

    def execute_operation(self) -> Dict[str, Any]:
        """Execute phase: Primary orchestration logic."""
        return {}

    def validate(self, output: Dict[str, Any] = None) -> bool:
        """Validate phase: Test results, regression check."""
        return True

    def teardown(self, result: Optional[ExecutionResult] = None) -> None:
        """Teardown phase: Write SQLite audit, cleanup resources, sync state."""
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
        """Get the history of execution results."""
        return self.execution_results.copy()

    def get_latest_result(self) -> Optional[ExecutionResult]:
        """Get the most recent execution result."""
        return self.execution_results[-1] if self.execution_results else None

    def health_check(self) -> Dict[str, Any]:
        """Return orchestrator health status.

        Returns:
            Dict with 'status', 'orchestrator', 'uptime_requests', and 'last_success' keys.
        """
        total = len(self.execution_results)
        successes = sum(1 for r in self.execution_results if r.success)
        last_success = None
        for r in reversed(self.execution_results):
            if r.success:
                last_success = True
                break
        return {
            "status": "healthy",
            "orchestrator": self.orchestrator_id,
            "uptime_requests": total,
            "success_count": successes,
            "last_success": last_success,
        }
