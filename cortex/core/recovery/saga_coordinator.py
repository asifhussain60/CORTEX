"""Saga pattern coordinator for distributed transaction compensation.

Implements saga pattern with automatic compensation, crash recovery,
and fault tolerance for multi-step operations.
"""

from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import json
import time
import uuid
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class SagaStatus(str, Enum):
    """Saga execution status."""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    COMPENSATING = "COMPENSATING"
    COMPENSATED = "COMPENSATED"
    FAILED = "FAILED"
    STUCK = "STUCK"


class CompensationError(Exception):
    """Raised when compensation cannot be performed."""
    pass


class SagaTimeoutError(Exception):
    """Raised when saga or step exceeds timeout."""
    pass


@dataclass
class SagaStep:
    """Single step in saga with forward and compensation actions.
    
    Args:
        name: Step identifier
        forward_action: Function to execute step
        compensation_action: Function to undo step
        timeout_seconds: Maximum execution time
    """
    name: str
    forward_action: Callable[[], Any]
    compensation_action: Callable[[Any], None]
    timeout_seconds: float = 30.0
    
    def execute(self) -> Any:
        """Execute forward action with timeout.
        
        Returns:
            Result of forward action
            
        Raises:
            SagaTimeoutError: If execution exceeds timeout
        """
        start = time.time()
        try:
            result = self.forward_action()
            elapsed = time.time() - start
            
            if elapsed > self.timeout_seconds:
                raise SagaTimeoutError(
                    f"Step {self.name} exceeded timeout: {elapsed:.2f}s > {self.timeout_seconds}s"
                )
            
            return result
        except Exception as e:
            if not isinstance(e, SagaTimeoutError):
                logger.error(f"Step {self.name} failed: {e}")
            raise
    
    def compensate(self, result: Any) -> None:
        """Execute compensation action.
        
        Args:
            result: Result from forward action to be compensated
            
        Raises:
            CompensationError: If compensation cannot be performed
        """
        try:
            self.compensation_action(result)
        except Exception as e:
            logger.error(f"Compensation for {self.name} failed: {e}")
            raise CompensationError(f"Cannot compensate {self.name}: {e}") from e


@dataclass
class SagaState:
    """Persistent state of saga execution.
    
    Args:
        saga_id: Unique saga identifier
        steps: List of step names
        status: Current execution status
        completed_steps: Steps that completed successfully
        compensated_steps: Steps that were compensated
        current_step: Currently executing step
        step_results: Results from completed steps
        created_at: Saga creation timestamp
        updated_at: Last update timestamp
        audit_trail: Execution events for debugging
    """
    saga_id: str
    steps: List[str]
    status: SagaStatus = SagaStatus.PENDING
    completed_steps: List[str] = field(default_factory=list)
    compensated_steps: List[str] = field(default_factory=list)
    current_step: Optional[str] = None
    step_results: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    audit_trail: List[Dict[str, Any]] = field(default_factory=list)
    
    def start_step(self, step_name: str) -> None:
        """Mark step as started."""
        self.current_step = step_name
        self.status = SagaStatus.IN_PROGRESS
        self.updated_at = datetime.utcnow().isoformat()
        self._add_audit_event("step_started", {"step": step_name})
    
    def complete_step(self, step_name: str, result: Any) -> None:
        """Mark step as completed."""
        self.completed_steps.append(step_name)
        self.step_results[step_name] = result
        self.current_step = None
        self.updated_at = datetime.utcnow().isoformat()
        self._add_audit_event("step_completed", {"step": step_name})
    
    def start_compensation(self) -> None:
        """Mark saga as compensating."""
        self.status = SagaStatus.COMPENSATING
        self.updated_at = datetime.utcnow().isoformat()
        self._add_audit_event("compensation_started", {})
    
    def compensate_step(self, step_name: str) -> None:
        """Mark step as compensated."""
        self.compensated_steps.append(step_name)
        self.updated_at = datetime.utcnow().isoformat()
        self._add_audit_event("step_compensated", {"step": step_name})
        
        # Mark as compensated if all steps compensated
        if len(self.compensated_steps) == len(self.completed_steps):
            self.status = SagaStatus.COMPENSATED
    
    def mark_completed(self) -> None:
        """Mark saga as completed."""
        self.status = SagaStatus.COMPLETED
        self.updated_at = datetime.utcnow().isoformat()
        self._add_audit_event("saga_completed", {})
    
    def mark_failed(self, reason: str) -> None:
        """Mark saga as failed."""
        self.status = SagaStatus.FAILED
        self.updated_at = datetime.utcnow().isoformat()
        self._add_audit_event("saga_failed", {"reason": reason})
    
    def mark_stuck(self, reason: str) -> None:
        """Mark saga as stuck (cannot complete or compensate)."""
        self.status = SagaStatus.STUCK
        self.updated_at = datetime.utcnow().isoformat()
        self._add_audit_event("saga_stuck", {"reason": reason})
    
    def _add_audit_event(self, event: str, data: Dict[str, Any]) -> None:
        """Add event to audit trail."""
        self.audit_trail.append({
            "timestamp": datetime.utcnow().isoformat(),
            "event": event,
            **data
        })
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state to dictionary."""
        data = asdict(self)
        data["status"] = self.status.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SagaState":
        """Deserialize state from dictionary."""
        data["status"] = SagaStatus(data["status"])
        return cls(**data)


@dataclass
class SagaResult:
    """Result of saga execution.
    
    Args:
        success: Whether saga completed successfully
        saga_id: Saga identifier
        completed_steps: Steps that completed
        failed_step: Step that failed (if any)
        error: Error message (if failed)
    """
    success: bool
    saga_id: str
    completed_steps: List[str]
    failed_step: Optional[str] = None
    error: Optional[str] = None


class SagaCoordinator:
    """Coordinates saga execution with compensation and crash recovery.
    
    Args:
        storage_path: Directory to persist saga state
        max_compensation_retries: Maximum compensation retry attempts
        compensation_backoff_seconds: Initial backoff between retries
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        max_compensation_retries: int = 3,
        compensation_backoff_seconds: float = 1.0
    ):
        self.storage_path = storage_path or Path.home() / ".cortex" / "sagas"
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.max_compensation_retries = max_compensation_retries
        self.compensation_backoff_seconds = compensation_backoff_seconds
        self._active_sagas: Dict[str, List[SagaStep]] = {}
    
    def create_saga(self, steps: List[SagaStep]) -> str:
        """Create new saga.
        
        Args:
            steps: Ordered list of saga steps
            
        Returns:
            Saga identifier
        """
        saga_id = str(uuid.uuid4())
        step_names = [step.name for step in steps]
        
        state = SagaState(saga_id=saga_id, steps=step_names)
        state._add_audit_event("saga_created", {"step_count": len(steps)})
        state._add_audit_event("saga_started", {})
        
        self._save_state(saga_id, state)
        self._active_sagas[saga_id] = steps
        
        logger.info(f"Created saga {saga_id} with {len(steps)} steps")
        return saga_id
    
    def execute_saga(self, saga_id: str) -> SagaResult:
        """Execute saga with automatic compensation on failure.
        
        Args:
            saga_id: Saga to execute
            
        Returns:
            Saga execution result
        """
        state = self._load_state(saga_id)
        steps = self._active_sagas.get(saga_id, [])
        
        if not steps:
            raise ValueError(f"Saga {saga_id} not found in active sagas")
        
        try:
            # Execute steps
            for step in steps:
                if step.name in state.completed_steps:
                    continue  # Skip already completed
                
                state.start_step(step.name)
                self._save_state(saga_id, state)
                
                result = self._execute_step(saga_id, step, state)
                
                state.complete_step(step.name, result)
                self._save_state(saga_id, state)
            
            # All steps completed
            state.mark_completed()
            self._save_state(saga_id, state)
            
            return SagaResult(
                success=True,
                saga_id=saga_id,
                completed_steps=state.completed_steps
            )
        
        except (SagaTimeoutError, Exception) as e:
            # Step failed - compensate
            logger.warning(f"Saga {saga_id} failed: {e}, compensating...")
            
            try:
                self._compensate_saga(saga_id)
                state = self._load_state(saga_id)
                state.mark_failed(str(e))
                self._save_state(saga_id, state)
            except CompensationError as ce:
                state = self._load_state(saga_id)
                state.mark_stuck(str(ce))
                self._save_state(saga_id, state)
                raise
            
            # Re-raise timeout for test detection
            if isinstance(e, SagaTimeoutError):
                raise
            
            return SagaResult(
                success=False,
                saga_id=saga_id,
                completed_steps=state.completed_steps,
                failed_step=state.current_step,
                error=str(e)
            )
    
    def resume_saga(self, saga_id: str, steps: List[SagaStep]) -> SagaResult:
        """Resume saga after crash.
        
        Args:
            saga_id: Saga to resume
            steps: Saga step definitions
            
        Returns:
            Saga execution result
        """
        logger.info(f"Resuming saga {saga_id}")
        self._active_sagas[saga_id] = steps
        return self.execute_saga(saga_id)
    
    def get_audit_trail(self, saga_id: str) -> List[Dict[str, Any]]:
        """Get complete audit trail for saga.
        
        Args:
            saga_id: Saga identifier
            
        Returns:
            List of audit events
        """
        state = self._load_state(saga_id)
        return state.audit_trail
    
    def _execute_step(self, saga_id: str, step: SagaStep, state: SagaState) -> Any:
        """Execute single step with timeout handling."""
        try:
            return step.execute()
        except SagaTimeoutError:
            logger.error(f"Step {step.name} timed out in saga {saga_id}")
            raise
        except Exception as e:
            logger.error(f"Step {step.name} failed in saga {saga_id}: {e}")
            raise
    
    def _compensate_saga(self, saga_id: str) -> None:
        """Compensate completed steps in reverse order.
        
        Args:
            saga_id: Saga to compensate
            
        Raises:
            CompensationError: If compensation fails after retries
        """
        state = self._load_state(saga_id)
        steps = self._active_sagas[saga_id]
        step_map = {step.name: step for step in steps}
        
        state.start_compensation()
        self._save_state(saga_id, state)
        
        # Compensate in reverse order
        for step_name in reversed(state.completed_steps):
            if step_name in state.compensated_steps:
                continue  # Already compensated
            
            step = step_map[step_name]
            result = state.step_results.get(step_name)
            
            # Retry compensation with exponential backoff
            for attempt in range(self.max_compensation_retries):
                try:
                    step.compensate(result)
                    state.compensate_step(step_name)
                    self._save_state(saga_id, state)
                    break
                except CompensationError as ce:
                    if attempt == self.max_compensation_retries - 1:
                        logger.error(f"Compensation failed after {attempt + 1} attempts: {ce}")
                        # Mark saga as STUCK - non-compensatable failure
                        state.status = SagaStatus.STUCK
                        self._save_state(saga_id, state)
                        raise
                    
                    backoff = self.compensation_backoff_seconds * (2 ** attempt)
                    logger.warning(f"Compensation attempt {attempt + 1} failed, retrying in {backoff}s")
                    time.sleep(backoff)
        
        state.status = SagaStatus.COMPENSATED
        self._save_state(saga_id, state)
        logger.info(f"Saga {saga_id} fully compensated")
    
    def _save_state(self, saga_id: str, state: SagaState) -> None:
        """Persist saga state to disk."""
        state_file = self.storage_path / f"{saga_id}.json"
        state_file.write_text(json.dumps(state.to_dict(), indent=2))
    
    def _load_state(self, saga_id: str) -> SagaState:
        """Load saga state from disk."""
        state_file = self.storage_path / f"{saga_id}.json"
        if not state_file.exists():
            raise ValueError(f"Saga {saga_id} not found")
        
        data = json.loads(state_file.read_text())
        return SagaState.from_dict(data)
