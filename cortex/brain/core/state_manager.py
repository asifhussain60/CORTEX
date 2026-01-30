"""
State Manager: Cross-Phase State Consistency and Carryover.

Manages state consistency across all CORTEX phases, ensuring data integrity
and proper carryover between phases while maintaining isolation for 
concurrent operations.

CORE-011: All functions have type hints.
CORE-012: All public APIs have Google-style docstrings.
CORE-008: Implementation follows TDD specification.
"""

import threading
import logging
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from copy import deepcopy
import json


@dataclass
class OperationState:
    """
    Operation state across phases.
    
    Attributes:
        operation_id: Unique operation identifier
        user_intent: Original user intent
        current_phase: Current phase number (1-4)
        phase_outputs: Outputs from each phase
        metadata: Operation metadata
        timestamps: Phase timestamps
        priority: Operation priority
    """
    operation_id: str
    user_intent: str
    current_phase: int = 1
    phase_outputs: Dict[int, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamps: Dict[str, float] = field(default_factory=dict)
    priority: int = 0
    created_at: float = field(default_factory=lambda: datetime.now().timestamp())

    def get_phase_output(self, phase: int) -> Optional[Any]:
        """Get output from specific phase."""
        output = self.phase_outputs.get(phase)
        # Return deep copy to prevent external mutations
        return deepcopy(output) if output is not None else None

    def set_phase_output(self, phase: int, output: Any) -> None:
        """Set output for a phase."""
        self.phase_outputs[phase] = deepcopy(output)


class StateManager:
    """
    Manages state consistency across CORTEX phases.
    
    Maintains operation state across all 4 phases, ensuring:
    - State carryover between phases
    - Isolation between concurrent operations
    - Rollback capability
    - Audit trail integration
    """

    def __init__(self) -> None:
        """Initialize State Manager."""
        self.logger: logging.Logger = logging.getLogger(__name__)
        self._operations: Dict[str, OperationState] = {}
        self._operation_lock: threading.RLock = threading.RLock()
        self._phase_snapshots: Dict[str, List[Dict[str, Any]]] = {}
        self._rollback_journal: List[Dict[str, Any]] = []

    def create_operation(
        self,
        operation_id: str,
        user_intent: str,
        priority: int = 0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> OperationState:
        """
        Create new operation state.
        
        Args:
            operation_id: Unique operation ID
            user_intent: User's original intent
            priority: Operation priority (default 0)
            metadata: Optional metadata
            
        Returns:
            New OperationState
        """
        with self._operation_lock:
            state: OperationState = OperationState(
                operation_id=operation_id,
                user_intent=user_intent,
                priority=priority,
                metadata=metadata or {}
            )
            self._operations[operation_id] = state
            # Create initial snapshot for phase 1
            self._create_snapshot(operation_id, 1)
            self.logger.info(f"Created operation state: {operation_id}")
            return state

    def get_operation_state(self, operation_id: str) -> Optional[OperationState]:
        """
        Get operation state.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            OperationState or None if not found
        """
        with self._operation_lock:
            return self._operations.get(operation_id)

    def transition_phase(
        self,
        operation_id: str,
        from_phase: int,
        to_phase: int,
        phase_output: Any
    ) -> bool:
        """
        Transition operation to next phase.
        
        Args:
            operation_id: Operation ID
            from_phase: Current phase number
            to_phase: Target phase number
            phase_output: Output from current phase
            
        Returns:
            True if successful, False otherwise
        """
        with self._operation_lock:
            state: Optional[OperationState] = self._operations.get(operation_id)
            if state is None:
                return False

            # Validate phase transition
            if state.current_phase != from_phase:
                self.logger.warning(
                    f"Invalid phase transition for {operation_id}: "
                    f"expected {state.current_phase}, got {from_phase}"
                )
                return False

            # Save output from completed phase
            state.set_phase_output(from_phase, phase_output)
            state.timestamps[f"phase_{from_phase}_complete"] = datetime.now().timestamp()

            # Transition to next phase
            state.current_phase = to_phase
            state.timestamps[f"phase_{to_phase}_start"] = datetime.now().timestamp()

            # Create snapshot for rollback
            self._create_snapshot(operation_id, to_phase)

            self.logger.info(
                f"Transitioned {operation_id}: Phase {from_phase}→{to_phase}"
            )
            return True

    def _create_snapshot(self, operation_id: str, phase: int) -> None:
        """Create state snapshot for rollback."""
        state: Optional[OperationState] = self._operations.get(operation_id)
        if state is None:
            return

        snapshot: Dict[str, Any] = {
            "operation_id": operation_id,
            "phase": phase,
            "timestamp": datetime.now().timestamp(),
            "state": {
                "current_phase": state.current_phase,
                "user_intent": state.user_intent,
                "phase_outputs": deepcopy(state.phase_outputs),
                "metadata": deepcopy(state.metadata),
            }
        }

        if operation_id not in self._phase_snapshots:
            self._phase_snapshots[operation_id] = []

        self._phase_snapshots[operation_id].append(snapshot)

    def rollback_to_phase(
        self,
        operation_id: str,
        target_phase: int
    ) -> bool:
        """
        Rollback operation to target phase.
        
        Args:
            operation_id: Operation ID
            target_phase: Target phase to rollback to
            
        Returns:
            True if successful, False otherwise
        """
        with self._operation_lock:
            snapshots: Optional[List[Dict[str, Any]]] = self._phase_snapshots.get(
                operation_id
            )
            if snapshots is None or not snapshots:
                return False

            # Find snapshot matching target phase
            target_snapshot: Optional[Dict[str, Any]] = None
            for snapshot in snapshots:
                if snapshot["phase"] == target_phase:
                    target_snapshot = snapshot
                    break

            if target_snapshot is None:
                return False

            # Restore state
            state: Optional[OperationState] = self._operations.get(operation_id)
            if state is None:
                return False

            restored: Dict[str, Any] = target_snapshot["state"]
            state.current_phase = restored["current_phase"]
            state.phase_outputs = deepcopy(restored["phase_outputs"])
            state.metadata = deepcopy(restored["metadata"])

            # Log rollback
            self._rollback_journal.append({
                "operation_id": operation_id,
                "target_phase": target_phase,
                "timestamp": datetime.now().timestamp(),
            })

            self.logger.info(
                f"Rolled back {operation_id} to Phase {target_phase}"
            )
            return True

    def get_context_for_phase(
        self,
        operation_id: str,
        target_phase: int
    ) -> Optional[Dict[str, Any]]:
        """
        Get context/inputs for target phase.
        
        Args:
            operation_id: Operation ID
            target_phase: Target phase number
            
        Returns:
            Context dict with inputs from previous phases, or None
        """
        with self._operation_lock:
            state: Optional[OperationState] = self._operations.get(operation_id)
            if state is None:
                return None

            context: Dict[str, Any] = {
                "operation_id": operation_id,
                "user_intent": state.user_intent,
                "target_phase": target_phase,
                "priority": state.priority,
                "metadata": deepcopy(state.metadata),
            }

            # Include outputs from previous phases
            for phase in range(1, target_phase):
                output: Any = state.get_phase_output(phase)
                if output is not None:
                    context[f"phase_{phase}_output"] = output

            return context

    def update_metadata(
        self,
        operation_id: str,
        key: str,
        value: Any
    ) -> bool:
        """
        Update operation metadata.
        
        Args:
            operation_id: Operation ID
            key: Metadata key
            value: Metadata value
            
        Returns:
            True if successful
        """
        with self._operation_lock:
            state: Optional[OperationState] = self._operations.get(operation_id)
            if state is None:
                return False

            state.metadata[key] = value
            return True

    def complete_operation(self, operation_id: str) -> bool:
        """
        Mark operation as complete and clean up.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            True if successful
        """
        with self._operation_lock:
            if operation_id not in self._operations:
                return False

            state: OperationState = self._operations[operation_id]
            state.timestamps["completed"] = datetime.now().timestamp()

            # Optionally retain snapshots for audit trail
            # Keep operation state for 24 hours for debugging

            self.logger.info(f"Completed operation: {operation_id}")
            return True
    
    def track_governance_violation(
        self,
        operation_id: str,
        rule_id: str,
        severity: str,
        description: str
    ) -> bool:
        """
        Track governance rule violation (Layer 2: Runtime Monitoring).
        
        Records CORE rule violations in real-time during operation execution.
        Enables circuit breaker pattern (trip after 3+ violations).
        
        Args:
            operation_id: Operation ID
            rule_id: Governance rule ID (e.g., CORE-008)
            severity: Violation severity (CRITICAL, HIGH, MEDIUM, LOW)
            description: Human-readable violation description
            
        Returns:
            True if tracked successfully, False if operation not found
        
        AC-ID: REM-003-02 (Governance Defense-in-Depth Layer 2)
        """
        with self._operation_lock:
            state: Optional[OperationState] = self._operations.get(operation_id)
            if state is None:
                return False
            
            # Initialize violations list if not exists
            if "governance_violations" not in state.metadata:
                state.metadata["governance_violations"] = []
            
            violation_entry = {
                "rule_id": rule_id,
                "severity": severity,
                "description": description,
                "timestamp": datetime.now().timestamp(),
            }
            
            state.metadata["governance_violations"].append(violation_entry)
            
            self.logger.warning(
                f"Governance violation tracked for {operation_id}: "
                f"{rule_id} ({severity}) - {description}"
            )
            
            # Check circuit breaker threshold
            violation_count = len(state.metadata["governance_violations"])
            if violation_count >= 3:
                self.logger.error(
                    f"Circuit breaker threshold reached for {operation_id}: "
                    f"{violation_count} violations detected"
                )
                state.metadata["circuit_breaker_tripped"] = True
            
            return True
    
    def get_violation_count(self, operation_id: str) -> int:
        """
        Get governance violation count for operation (Layer 2).
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Number of governance violations, or 0 if operation not found
        
        AC-ID: REM-003-02 (Governance Defense-in-Depth Layer 2)
        """
        with self._operation_lock:
            state: Optional[OperationState] = self._operations.get(operation_id)
            if state is None:
                return 0
            
            violations = state.metadata.get("governance_violations", [])
            return len(violations)
    
    def is_circuit_breaker_tripped(self, operation_id: str) -> bool:
        """
        Check if circuit breaker tripped for operation (Layer 2).
        
        Circuit breaker trips after 3+ governance violations to prevent
        cascade failures.
        
        Args:
            operation_id: Operation ID
            
        Returns:
            True if circuit breaker tripped, False otherwise
        
        AC-ID: REM-003-02 (Governance Defense-in-Depth Layer 2)
        """
        with self._operation_lock:
            state: Optional[OperationState] = self._operations.get(operation_id)
            if state is None:
                return False
            
            return state.metadata.get("circuit_breaker_tripped", False)
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get state manager statistics.
        
        Returns:
            Dict with active operations, rollbacks, governance violations, etc.
        """
        with self._operation_lock:
            total_violations = 0
            circuit_breaker_tripped_count = 0
            
            for state in self._operations.values():
                violations = state.metadata.get("governance_violations", [])
                total_violations += len(violations)
                if state.metadata.get("circuit_breaker_tripped", False):
                    circuit_breaker_tripped_count += 1
            
            return {
                "active_operations": len(self._operations),
                "total_snapshots": sum(
                    len(snaps) for snaps in self._phase_snapshots.values()
                ),
                "total_rollbacks": len(self._rollback_journal),
                "phase_snapshots_entries": {
                    op_id: len(snaps)
                    for op_id, snaps in self._phase_snapshots.items()
                },
                "governance_violations_total": total_violations,  # NEW: REM-003-02
                "circuit_breakers_tripped": circuit_breaker_tripped_count,  # NEW: REM-003-02
            }


# Global state manager instance
_state_manager: Optional[StateManager] = None
_state_manager_lock: threading.Lock = threading.Lock()


def get_state_manager() -> StateManager:
    """
    Get global StateManager instance (singleton).
    
    Returns:
        StateManager instance
    """
    global _state_manager
    
    if _state_manager is None:
        with _state_manager_lock:
            if _state_manager is None:
                _state_manager = StateManager()
    
    return _state_manager


if __name__ == "__main__":
    # Example usage
    manager: StateManager = StateManager()
    
    # Create operation
    state: OperationState = manager.create_operation(
        "op_001",
        "Implement new feature",
        priority=1
    )
    
    print(f"Created operation: {state.operation_id}")
    
    # Transition through phases
    manager.transition_phase("op_001", 1, 2, {"intent": "IMPLEMENT"})
    
    # Get context for phase 2
    context: Optional[Dict[str, Any]] = manager.get_context_for_phase("op_001", 2)
    print(f"Phase 2 context: {json.dumps(context, default=str, indent=2)}")
