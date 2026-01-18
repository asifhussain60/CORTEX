"""
Execution Sandbox Module (AC-HP-002-01)

Provides isolated execution environment with rollback, dry-run, state snapshots,
and atomic transaction support.

Implements CORE-015 (Sandbox Isolation) and CORE-016 (Transaction Support).
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime
from copy import deepcopy
from uuid import uuid4
import time


# =========================================================================
# DATA STRUCTURES
# =========================================================================

@dataclass
class StateSnapshot:
    """
    Represents a point-in-time snapshot of system state.
    
    Attributes:
        snapshot_id: Unique identifier for this snapshot
        phase_id: ID of the phase this snapshot belongs to
        state_data: Copy of the state at snapshot time
        timestamp: When the snapshot was taken
        metadata: Optional additional metadata
    """
    snapshot_id: str
    phase_id: str
    state_data: Dict[str, Any]
    timestamp: datetime
    metadata: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Ensure state_data is a deep copy."""
        self.state_data = deepcopy(self.state_data)


@dataclass
class SandboxTransaction:
    """
    Represents an atomic transaction within the sandbox.
    
    Attributes:
        transaction_id: Unique transaction identifier
        start_time: When transaction began
        status: Current transaction status (ACTIVE, COMMITTED, ROLLED_BACK)
        actions: List of actions in this transaction
        snapshots: Pre- and post-transaction snapshots
        metadata: Optional transaction metadata
    """
    transaction_id: str
    start_time: datetime
    status: str = 'ACTIVE'
    actions: List[Dict[str, Any]] = field(default_factory=list)
    snapshots: Dict[str, StateSnapshot] = field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class ExecutionResult:
    """
    Represents the result of sandbox execution.
    
    Attributes:
        execution_id: Unique execution identifier
        status: Execution status (SUCCESS, FAILED, PENDING)
        result_data: Result data from execution
        side_effects: List of captured side effects
        timestamp: When execution completed
        duration_ms: How long execution took
    """
    execution_id: str
    status: str
    result_data: Dict[str, Any] = field(default_factory=dict)
    side_effects: List[Dict[str, Any]] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)
    duration_ms: float = 0.0


# =========================================================================
# EXECUTION SANDBOX
# =========================================================================

class ExecutionSandbox:
    """
    Provides isolated execution environment with rollback, dry-run, and transactions.
    
    Key features:
    - Isolated execution prevents side effects from propagating
    - State snapshots for rollback capability
    - Dry-run mode shows effects without execution
    - Atomic transactions with commit/rollback
    - Side effect capture and management
    """

    def __init__(self):
        """Initialize execution sandbox."""
        self.current_state: Dict[str, Any] = {}
        self.snapshots: Dict[str, StateSnapshot] = {}
        self.transactions: Dict[str, SandboxTransaction] = {}
        self.execution_history: List[ExecutionResult] = []
        self.side_effects: List[Dict[str, Any]] = []
        self.active_transaction: Optional[SandboxTransaction] = None

    def initialize(self, initial_state: Dict[str, Any]) -> 'ExecutionSandbox':
        """
        Initialize sandbox with initial state.
        
        Args:
            initial_state: Initial state for sandbox
            
        Returns:
            Self for chaining
        """
        self.current_state = deepcopy(initial_state)
        return self

    def is_isolated(self) -> bool:
        """
        Check if sandbox is operating in isolated mode.
        
        Returns:
            True if sandbox is isolated (always True for this implementation)
        """
        return True

    def create_snapshot(
        self,
        phase_id: str,
        state_data: Dict[str, Any],
        reason: str = 'manual',
    ) -> StateSnapshot:
        """
        Create a snapshot of current state.
        
        Args:
            phase_id: Phase ID for this snapshot
            state_data: State data to snapshot
            reason: Reason for snapshot
            
        Returns:
            StateSnapshot object
        """
        snapshot_id = f'SS-{uuid4().hex[:8]}'
        snapshot = StateSnapshot(
            snapshot_id=snapshot_id,
            phase_id=phase_id,
            state_data=state_data,
            timestamp=datetime.now(),
            metadata={'reason': reason},
        )
        self.snapshots[snapshot_id] = snapshot
        return snapshot

    def execute(
        self,
        action: Dict[str, Any],
        transaction: Optional[SandboxTransaction] = None,
    ) -> ExecutionResult:
        """
        Execute an action within the sandbox.
        
        Args:
            action: Action to execute
            transaction: Optional transaction to associate with
            
        Returns:
            ExecutionResult with execution details
        """
        start_time = time.time()
        exec_id = f'EXEC-{uuid4().hex[:8]}'

        try:
            # Apply action to current state (isolated)
            result_data = self._apply_action(action, self.current_state)

            # Capture side effects
            side_effects = self._capture_side_effects(action, result_data)

            # If in transaction, add to transaction
            if transaction:
                transaction.actions.append(action)

            # Create execution result
            result = ExecutionResult(
                execution_id=exec_id,
                status='SUCCESS',
                result_data=result_data,
                side_effects=side_effects,
                timestamp=datetime.now(),
                duration_ms=(time.time() - start_time) * 1000,
            )

            self.execution_history.append(result)
            return result

        except Exception as e:
            return ExecutionResult(
                execution_id=exec_id,
                status='FAILED',
                result_data={'error': str(e)},
                side_effects=[],
                timestamp=datetime.now(),
                duration_ms=(time.time() - start_time) * 1000,
            )

    def dry_run(
        self,
        action: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Preview action execution without modifying state.
        
        Args:
            action: Action to preview
            
        Returns:
            Preview of expected effects and changes
        """
        # Create a copy of state for preview
        preview_state = deepcopy(self.current_state)

        # Simulate action on preview state
        expected_changes = self._apply_action(action, preview_state)
        side_effects = self._capture_side_effects(action, expected_changes)

        return {
            'action_id': action.get('action_id', 'unknown'),
            'status': 'PREVIEW',
            'effects': expected_changes,
            'side_effects': side_effects,
            'expected_state_changes': expected_changes,
            'preview_only': True,
            'would_modify_state': len(expected_changes) > 0,
        }

    def _apply_action(
        self,
        action: Dict[str, Any],
        state: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Apply action to state and return changes.
        
        Args:
            action: Action to apply
            state: State to modify
            
        Returns:
            Dictionary of changes made
        """
        changes = {}
        action_type = action.get('action_type', 'UNKNOWN')

        if action_type == 'MODIFY' or action_type == 'MODIFY_AC' or action_type == 'MODIFY_PHASE':
            changes_data = action.get('changes', {})
            for key, value in changes_data.items():
                old_value = state.get(key)
                state[key] = value
                changes[key] = {'old': old_value, 'new': value}

        elif action_type == 'CREATE_PHASE':
            phase_data = action.get('phase_data', {})
            state['created_phase'] = phase_data
            changes['created_phase'] = phase_data

        elif action_type == 'DELETE_FILE':
            # Simulate file deletion (doesn't actually delete)
            file_path = action.get('file', 'unknown')
            state['deleted_files'] = state.get('deleted_files', [])
            state['deleted_files'].append(file_path)
            changes['deleted_file'] = file_path

        elif action_type == 'VALIDATE':
            state['last_validation'] = datetime.now().isoformat()
            changes['validation'] = 'PASSED'

        elif action_type == 'VERIFY':
            constraints = action.get('constraints', [])
            state['verified_constraints'] = constraints
            changes['verification'] = 'PASSED'

        return changes

    def _capture_side_effects(
        self,
        action: Dict[str, Any],
        changes: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        Capture side effects from action execution.
        
        Args:
            action: Action being executed
            changes: Changes made by action
            
        Returns:
            List of captured side effects
        """
        side_effects = []

        # Log the side effect
        side_effect = {
            'action_id': action.get('action_id'),
            'action_type': action.get('action_type'),
            'timestamp': datetime.now().isoformat(),
            'changes': changes,
        }
        side_effects.append(side_effect)
        self.side_effects.append(side_effect)

        return side_effects

    def get_current_state(self) -> Dict[str, Any]:
        """
        Get current sandbox state.
        
        Returns:
            Deep copy of current state
        """
        return deepcopy(self.current_state)

    def get_side_effects(self) -> List[Dict[str, Any]]:
        """
        Get captured side effects.
        
        Returns:
            List of side effects
        """
        return deepcopy(self.side_effects)

    # =========================================================================
    # TRANSACTION SUPPORT
    # =========================================================================

    def begin_transaction(self) -> SandboxTransaction:
        """
        Begin a new atomic transaction.
        
        Returns:
            SandboxTransaction object
        """
        tx_id = f'TX-{uuid4().hex[:8]}'
        transaction = SandboxTransaction(
            transaction_id=tx_id,
            start_time=datetime.now(),
            status='ACTIVE',
        )
        # Create pre-transaction snapshot
        transaction.snapshots['pre'] = self.create_snapshot(
            phase_id=self.current_state.get('phase_id', 'unknown'),
            state_data=self.current_state,
            reason='pre-transaction',
        )
        self.transactions[tx_id] = transaction
        self.active_transaction = transaction
        return transaction

    def commit_transaction(
        self,
        transaction: SandboxTransaction,
        timeout_seconds: float = 30.0,
    ) -> Dict[str, Any]:
        """
        Commit a transaction.
        
        Args:
            transaction: Transaction to commit
            timeout_seconds: Timeout for commit
            
        Returns:
            Commit result
        """
        try:
            # Create post-transaction snapshot
            transaction.snapshots['post'] = self.create_snapshot(
                phase_id=self.current_state.get('phase_id', 'unknown'),
                state_data=self.current_state,
                reason='post-transaction',
            )
            transaction.status = 'COMMITTED'
            
            if self.active_transaction == transaction:
                self.active_transaction = None

            return {
                'transaction_id': transaction.transaction_id,
                'status': 'COMMITTED',
                'action_count': len(transaction.actions),
                'timestamp': datetime.now().isoformat(),
            }

        except Exception as e:
            transaction.status = 'FAILED'
            return {
                'transaction_id': transaction.transaction_id,
                'status': 'FAILED',
                'error': str(e),
            }

    def rollback_transaction(
        self,
        transaction: SandboxTransaction,
    ) -> Dict[str, Any]:
        """
        Rollback a transaction to pre-transaction state.
        
        Args:
            transaction: Transaction to rollback
            
        Returns:
            Rollback result
        """
        if 'pre' not in transaction.snapshots:
            return {'status': 'ERROR', 'message': 'No pre-transaction snapshot'}

        # Restore to pre-transaction state
        pre_snapshot = transaction.snapshots['pre']
        self.current_state = deepcopy(pre_snapshot.state_data)
        transaction.status = 'ROLLED_BACK'

        if self.active_transaction == transaction:
            self.active_transaction = None

        return {
            'transaction_id': transaction.transaction_id,
            'status': 'ROLLED_BACK',
            'actions_undone': len(transaction.actions),
            'timestamp': datetime.now().isoformat(),
        }

    def rollback_to_checkpoint(self, snapshot: StateSnapshot) -> Dict[str, Any]:
        """
        Rollback to a specific checkpoint/snapshot.
        
        Args:
            snapshot: Snapshot to rollback to
            
        Returns:
            Rollback result
        """
        self.current_state = deepcopy(snapshot.state_data)
        return {
            'snapshot_id': snapshot.snapshot_id,
            'status': 'ROLLED_BACK',
            'timestamp': datetime.now().isoformat(),
        }


# =========================================================================
# ROLLBACK HANDLER
# =========================================================================

class SandboxRollback:
    """
    Handles rollback operations for sandbox state recovery.
    """

    def __init__(self):
        """Initialize rollback handler."""
        self.rollback_history: List[Dict[str, Any]] = []

    def rollback_to_snapshot(self, snapshot: StateSnapshot) -> Dict[str, Any]:
        """
        Rollback to a specific snapshot.
        
        Args:
            snapshot: Snapshot to restore
            
        Returns:
            Restored state
        """
        if snapshot is None:
            raise ValueError('Cannot rollback to None snapshot')

        restored_state = deepcopy(snapshot.state_data)

        # Log rollback
        self.rollback_history.append({
            'snapshot_id': snapshot.snapshot_id,
            'timestamp': datetime.now().isoformat(),
            'reason': snapshot.metadata.get('reason') if snapshot.metadata else 'manual',
        })

        return restored_state

    def get_rollback_history(self) -> List[Dict[str, Any]]:
        """Get history of rollback operations."""
        return self.rollback_history.copy()


# =========================================================================
# MODULE EXPORTS
# =========================================================================

__all__ = [
    'StateSnapshot',
    'SandboxTransaction',
    'ExecutionResult',
    'ExecutionSandbox',
    'SandboxRollback',
]
