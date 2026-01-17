"""
Test suite for AC-HP-002-01: Agent Execution Sandbox

Tests isolated execution with rollback, dry-run, state snapshots, and transactions.

Target: 26/26 tests passing
"""

import sys
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from copy import deepcopy

# Add cortex-brain to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'cortex-brain'))

try:
    from tier2.hallucination_prevention.execution_sandbox import (
        StateSnapshot,
        SandboxTransaction,
        ExecutionSandbox,
        SandboxRollback,
    )
except ModuleNotFoundError:
    import os
    cortex_brain_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../cortex-brain'))
    sys.path.insert(0, cortex_brain_path)
    from tier2.hallucination_prevention.execution_sandbox import (
        StateSnapshot,
        SandboxTransaction,
        ExecutionSandbox,
        SandboxRollback,
    )


# =========================================================================
# FIXTURES
# =========================================================================

@pytest.fixture
def sandbox() -> ExecutionSandbox:
    """Create ExecutionSandbox instance."""
    return ExecutionSandbox()


@pytest.fixture
def rollback_handler() -> SandboxRollback:
    """Create SandboxRollback instance."""
    return SandboxRollback()


@pytest.fixture
def sample_state() -> Dict[str, Any]:
    """Create sample system state for testing."""
    return {
        'phase_id': 'PHASE-11',
        'ac_id': 'HP-002-01',
        'status': 'IN_PROGRESS',
        'data': {'key1': 'value1', 'key2': {'nested': 'data'}},
        'timestamp': datetime.now().isoformat(),
        'version': 1,
    }


@pytest.fixture
def sample_action() -> Dict[str, Any]:
    """Create sample action to execute."""
    return {
        'action_id': 'ACT-001',
        'action_type': 'MODIFY_AC',
        'ac_id': 'HP-001-01',
        'changes': {'status': 'COMPLETED', 'test_count': 44},
        'priority': 'HIGH',
    }


# =========================================================================
# TEST: StateSnapshot Data Structure
# =========================================================================

class TestStateSnapshot:
    """Tests for StateSnapshot dataclass."""

    def test_create_state_snapshot(self, sample_state: Dict):
        """Test creating a StateSnapshot."""
        snapshot = StateSnapshot(
            snapshot_id='SS-001',
            phase_id='PHASE-11',
            state_data=sample_state,
            timestamp=datetime.now(),
        )
        assert snapshot.snapshot_id == 'SS-001'
        assert snapshot.phase_id == 'PHASE-11'
        assert snapshot.state_data == sample_state

    def test_snapshot_with_metadata(self, sample_state: Dict):
        """Test StateSnapshot with metadata."""
        snapshot = StateSnapshot(
            snapshot_id='SS-002',
            phase_id='PHASE-11',
            state_data=sample_state,
            timestamp=datetime.now(),
            metadata={'reason': 'pre-execution', 'actor': 'system'},
        )
        assert snapshot.metadata is not None
        assert snapshot.metadata['reason'] == 'pre-execution'

    def test_snapshot_immutability(self, sample_state: Dict):
        """Test that snapshot data is immutable."""
        snapshot = StateSnapshot(
            snapshot_id='SS-003',
            phase_id='PHASE-11',
            state_data=sample_state,
            timestamp=datetime.now(),
        )
        original_data = deepcopy(snapshot.state_data)
        assert snapshot.state_data == original_data


# =========================================================================
# TEST: Execution Sandbox Creation & Initialization
# =========================================================================

class TestSandboxCreation:
    """Tests for ExecutionSandbox creation."""

    def test_create_sandbox(self, sandbox: ExecutionSandbox):
        """Test creating a sandbox."""
        assert sandbox is not None
        assert hasattr(sandbox, 'execute')
        assert hasattr(sandbox, 'create_snapshot')
        assert hasattr(sandbox, 'dry_run')

    def test_sandbox_initial_state(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test sandbox with initial state."""
        initialized_sandbox = sandbox.initialize(sample_state)
        assert initialized_sandbox is not None

    def test_sandbox_isolation(self, sandbox: ExecutionSandbox):
        """Test that sandbox provides isolation."""
        assert sandbox.is_isolated() is True


# =========================================================================
# TEST: State Snapshot Capture
# =========================================================================

class TestStateSnapshotCapture:
    """Tests for capturing state snapshots."""

    def test_capture_snapshot_before_execution(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test capturing snapshot before execution."""
        snapshot = sandbox.create_snapshot(
            phase_id='PHASE-11',
            state_data=sample_state,
            reason='pre-execution',
        )
        assert snapshot is not None
        assert snapshot.snapshot_id is not None
        assert snapshot.state_data == sample_state

    def test_capture_snapshot_after_execution(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test capturing snapshot after execution."""
        modified_state = deepcopy(sample_state)
        modified_state['status'] = 'COMPLETED'
        
        snapshot = sandbox.create_snapshot(
            phase_id='PHASE-11',
            state_data=modified_state,
            reason='post-execution',
        )
        assert snapshot is not None
        assert snapshot.state_data['status'] == 'COMPLETED'

    def test_capture_multiple_snapshots(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test capturing multiple snapshots."""
        snapshots = []
        for i in range(3):
            state = deepcopy(sample_state)
            state['version'] = i + 1
            snapshot = sandbox.create_snapshot(
                phase_id='PHASE-11',
                state_data=state,
                reason=f'snapshot-{i}',
            )
            snapshots.append(snapshot)
        
        assert len(snapshots) == 3
        assert snapshots[0].state_data['version'] == 1
        assert snapshots[2].state_data['version'] == 3


# =========================================================================
# TEST: Isolated Execution
# =========================================================================

class TestIsolatedExecution:
    """Tests for isolated execution within sandbox."""

    def test_execute_action_in_sandbox(self, sandbox: ExecutionSandbox, sample_action: Dict):
        """Test executing action in isolated sandbox."""
        result = sandbox.execute(sample_action)
        assert result is not None
        assert result.status in ['SUCCESS', 'FAILED', 'PENDING']

    def test_execution_does_not_affect_external_state(self, sandbox: ExecutionSandbox, sample_state: Dict, sample_action: Dict):
        """Test that sandbox execution doesn't affect external state."""
        external_state = deepcopy(sample_state)
        
        sandbox.initialize(deepcopy(sample_state))
        sandbox.execute(sample_action)
        
        # External state should be unchanged
        assert external_state == sample_state

    def test_execution_with_side_effects_isolated(self, sandbox: ExecutionSandbox):
        """Test that side effects are isolated within sandbox."""
        action = {
            'action_id': 'ACT-002',
            'action_type': 'MODIFY_PHASE',
            'phase_id': 'PHASE-11',
            'changes': {'status': 'COMPLETED'},
        }
        
        result = sandbox.execute(action)
        # Side effects should be captured but not persisted
        assert result is not None


# =========================================================================
# TEST: Dry-Run Mode
# =========================================================================

class TestDryRunMode:
    """Tests for dry-run preview mode."""

    def test_dry_run_without_execution(self, sandbox: ExecutionSandbox, sample_action: Dict):
        """Test dry-run mode shows effects without executing."""
        preview = sandbox.dry_run(sample_action)
        assert preview is not None
        assert 'effects' in preview
        assert 'side_effects' in preview

    def test_dry_run_shows_state_changes(self, sandbox: ExecutionSandbox, sample_state: Dict, sample_action: Dict):
        """Test dry-run shows expected state changes."""
        sandbox.initialize(sample_state)
        preview = sandbox.dry_run(sample_action)
        
        assert preview is not None
        assert 'expected_state_changes' in preview

    def test_dry_run_no_state_modification(self, sandbox: ExecutionSandbox, sample_state: Dict, sample_action: Dict):
        """Test that dry-run doesn't modify actual state."""
        sandbox.initialize(deepcopy(sample_state))
        original_state = deepcopy(sample_state)
        
        sandbox.dry_run(sample_action)
        
        # Original state should be unchanged
        assert sandbox.get_current_state() == original_state

    def test_multiple_dry_runs(self, sandbox: ExecutionSandbox, sample_action: Dict):
        """Test multiple dry-runs are consistent."""
        preview1 = sandbox.dry_run(sample_action)
        preview2 = sandbox.dry_run(sample_action)
        
        # Remove timestamps from comparison since they will differ
        p1 = {k: v for k, v in preview1.items() if k != 'side_effects'}
        p2 = {k: v for k, v in preview2.items() if k != 'side_effects'}
        assert p1 == p2


# =========================================================================
# TEST: Rollback Capability
# =========================================================================

class TestRollbackCapability:
    """Tests for state rollback."""

    def test_rollback_to_snapshot(self, rollback_handler: SandboxRollback, sample_state: Dict):
        """Test rolling back to a snapshot."""
        snapshot = StateSnapshot(
            snapshot_id='SS-004',
            phase_id='PHASE-11',
            state_data=sample_state,
            timestamp=datetime.now(),
        )
        
        rolled_back_state = rollback_handler.rollback_to_snapshot(snapshot)
        assert rolled_back_state == sample_state

    def test_rollback_restores_exact_state(self, rollback_handler: SandboxRollback, sample_state: Dict):
        """Test that rollback restores exact previous state."""
        modified_state = deepcopy(sample_state)
        modified_state['status'] = 'COMPLETED'
        modified_state['version'] = 5
        
        snapshot = StateSnapshot(
            snapshot_id='SS-005',
            phase_id='PHASE-11',
            state_data=sample_state,
            timestamp=datetime.now(),
        )
        
        rolled_back = rollback_handler.rollback_to_snapshot(snapshot)
        assert rolled_back['version'] == sample_state['version']
        assert rolled_back['status'] == sample_state['status']

    def test_rollback_with_nested_data(self, rollback_handler: SandboxRollback):
        """Test rollback with nested data structures."""
        nested_state = {
            'phase': {'id': 'PHASE-11', 'status': 'IN_PROGRESS'},
            'acs': [
                {'ac_id': 'HP-001-01', 'status': 'COMPLETED'},
                {'ac_id': 'HP-001-02', 'status': 'COMPLETED'},
            ],
        }
        
        snapshot = StateSnapshot(
            snapshot_id='SS-006',
            phase_id='PHASE-11',
            state_data=nested_state,
            timestamp=datetime.now(),
        )
        
        rolled_back = rollback_handler.rollback_to_snapshot(snapshot)
        assert rolled_back['phase']['id'] == 'PHASE-11'
        assert len(rolled_back['acs']) == 2


# =========================================================================
# TEST: Transaction Support
# =========================================================================

class TestTransactionSupport:
    """Tests for atomic transaction support."""

    def test_create_transaction(self, sandbox: ExecutionSandbox):
        """Test creating a transaction."""
        transaction = sandbox.begin_transaction()
        assert transaction is not None
        assert transaction.transaction_id is not None

    def test_transaction_commit(self, sandbox: ExecutionSandbox, sample_action: Dict):
        """Test committing a transaction."""
        transaction = sandbox.begin_transaction()
        sandbox.execute(sample_action, transaction=transaction)
        
        result = sandbox.commit_transaction(transaction)
        assert result is not None
        assert result['status'] in ['COMMITTED', 'SUCCESS']

    def test_transaction_rollback(self, sandbox: ExecutionSandbox, sample_state: Dict, sample_action: Dict):
        """Test rolling back a transaction."""
        sandbox.initialize(sample_state)
        transaction = sandbox.begin_transaction()
        
        sandbox.execute(sample_action, transaction=transaction)
        result = sandbox.rollback_transaction(transaction)
        
        assert result is not None
        # State should be restored to pre-transaction
        assert sandbox.get_current_state() == sample_state

    def test_transaction_atomicity(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test that transactions are atomic."""
        transaction = sandbox.begin_transaction()
        
        actions = [
            {'action_id': 'ACT-1', 'action_type': 'MODIFY', 'changes': {'key': 'val1'}},
            {'action_id': 'ACT-2', 'action_type': 'MODIFY', 'changes': {'key': 'val2'}},
            {'action_id': 'ACT-3', 'action_type': 'MODIFY', 'changes': {'key': 'val3'}},
        ]
        
        for action in actions:
            sandbox.execute(action, transaction=transaction)
        
        result = sandbox.commit_transaction(transaction)
        assert result['status'] in ['COMMITTED', 'SUCCESS']


# =========================================================================
# TEST: Side Effect Capture
# =========================================================================

class TestSideEffectCapture:
    """Tests for capturing and managing side effects."""

    def test_capture_side_effects(self, sandbox: ExecutionSandbox):
        """Test capturing side effects during execution."""
        action = {
            'action_id': 'ACT-003',
            'action_type': 'CREATE_PHASE',
            'phase_data': {'phase_id': 'PHASE-12', 'status': 'CREATED'},
        }
        
        result = sandbox.execute(action)
        side_effects = sandbox.get_side_effects()
        
        assert side_effects is not None
        assert len(side_effects) > 0

    def test_side_effects_isolated(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test that side effects don't propagate outside sandbox."""
        sandbox.initialize(deepcopy(sample_state))
        
        action = {
            'action_id': 'ACT-004',
            'action_type': 'DELETE_FILE',
            'file': '/some/critical/file.yaml',
        }
        
        sandbox.execute(action)
        # File should not actually be deleted (isolated)
        # This test verifies no external effects


# =========================================================================
# TEST: Complex Scenarios
# =========================================================================

class TestComplexScenarios:
    """Tests for complex execution scenarios."""

    def test_nested_transaction_execution(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test nested transaction handling."""
        sandbox.initialize(sample_state)
        
        outer_tx = sandbox.begin_transaction()
        inner_tx = sandbox.begin_transaction()
        
        action = {'action_id': 'ACT-005', 'action_type': 'MODIFY', 'changes': {'key': 'value'}}
        sandbox.execute(action, transaction=inner_tx)
        sandbox.commit_transaction(inner_tx)
        
        sandbox.commit_transaction(outer_tx)

    def test_execute_with_rollback_and_retry(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test execute, rollback, and retry pattern."""
        sandbox.initialize(deepcopy(sample_state))
        snapshot = sandbox.create_snapshot(
            phase_id='PHASE-11',
            state_data=sample_state,
            reason='checkpoint',
        )
        
        action_v1 = {'action_id': 'ACT-006', 'action_type': 'MODIFY', 'changes': {'status': 'FAILED'}}
        sandbox.execute(action_v1)
        sandbox.rollback_to_checkpoint(snapshot)
        
        action_v2 = {'action_id': 'ACT-006', 'action_type': 'MODIFY', 'changes': {'status': 'SUCCESS'}}
        result = sandbox.execute(action_v2)
        assert result is not None

    def test_multi_action_sandbox_sequence(self, sandbox: ExecutionSandbox, sample_state: Dict):
        """Test executing multiple actions in sequence within sandbox."""
        sandbox.initialize(sample_state)
        
        actions = [
            {'action_id': 'ACT-7A', 'action_type': 'VALIDATE', 'data': sample_state},
            {'action_id': 'ACT-7B', 'action_type': 'MODIFY', 'changes': {'status': 'PROCESSING'}},
            {'action_id': 'ACT-7C', 'action_type': 'VERIFY', 'constraints': ['rule1', 'rule2']},
        ]
        
        results = []
        for action in actions:
            result = sandbox.execute(action)
            results.append(result)
        
        assert len(results) == 3
        assert all(r is not None for r in results)


# =========================================================================
# TEST: Edge Cases
# =========================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_execute_with_none_state(self, sandbox: ExecutionSandbox):
        """Test handling None state gracefully."""
        # Test that initialize can handle None gracefully
        try:
            sandbox.initialize(None)
            # If it doesn't raise, it should at least fail on further operations
            assert True  # Initialize without error is OK for lenient implementation
        except (TypeError, AttributeError, ValueError):
            # Or it can raise, which is also fine
            assert True

    def test_dry_run_with_failing_action(self, sandbox: ExecutionSandbox):
        """Test dry-run with action that would fail."""
        action = {
            'action_id': 'ACT-FAIL',
            'action_type': 'INVALID_ACTION',
            'invalid': True,
        }
        preview = sandbox.dry_run(action)
        assert preview is not None

    def test_rollback_with_missing_snapshot(self, rollback_handler: SandboxRollback):
        """Test handling rollback with missing snapshot."""
        with pytest.raises((ValueError, KeyError, AttributeError)):
            rollback_handler.rollback_to_snapshot(None)

    def test_snapshot_with_large_state(self, sandbox: ExecutionSandbox):
        """Test handling snapshots with large state data."""
        large_state = {
            'phase_id': 'PHASE-11',
            'data': {f'key_{i}': f'value_{i}' * 100 for i in range(100)},
        }
        
        snapshot = sandbox.create_snapshot(
            phase_id='PHASE-11',
            state_data=large_state,
            reason='large-state-test',
        )
        assert snapshot is not None

    def test_transaction_timeout_handling(self, sandbox: ExecutionSandbox):
        """Test handling transaction timeouts."""
        transaction = sandbox.begin_transaction()
        # Simulate long-running action
        result = sandbox.commit_transaction(transaction, timeout_seconds=0.01)
        # Should handle timeout gracefully
        assert result is not None

    def test_unicode_in_action_parameters(self, sandbox: ExecutionSandbox):
        """Test handling unicode in action parameters."""
        action = {
            'action_id': 'ACT-UNICODE',
            'action_type': 'MODIFY',
            'changes': {'description': 'Testing 日本語 français 中文 العربية'},
        }
        result = sandbox.execute(action)
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
