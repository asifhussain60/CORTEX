"""
Test Suite for OrchestrationCheckpointManager (Feature 11)

Phase: 11.1 (RED)
Purpose: Validate checkpoint save/restore/rollback functionality for orchestrator workflows

Test Coverage:
- BasicCheckpointOperations: save_checkpoint, restore_checkpoint
- StateSerializationDeserialization: complex state handling (nested dicts, lists)
- RollbackCapability: restore to previous checkpoint on failure
- CheckpointCleanup: 30-day retention policy with auto-cleanup
- ConcurrentCheckpoints: thread-safe operations for parallel orchestrators
- CheckpointMetadata: timestamp, orchestrator_name, phase, task_state tracking
- Performance: <50ms save/restore operations

Author: Asif Hussain
Created: December 13, 2024
"""

import pytest
import json
import os
import time
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import tempfile
import shutil
import threading

from src.operations.utilities.orchestration_checkpoint_manager import (
    OrchestrationCheckpointManager,
    CheckpointNotFoundError,
    CheckpointCorruptedError
)


class TestBasicCheckpointOperations:
    """Test basic save and restore checkpoint functionality."""
    
    def test_save_checkpoint_creates_file(self, tmp_path):
        """Test that save_checkpoint creates a checkpoint file with correct structure."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        state = {
            'phase': 2,
            'current_task': 'task_2.1',
            'completed_tasks': ['task_1.1', 'task_1.2'],
            'variables': {'feature_name': 'Feature 11', 'progress': 0.5}
        }
        
        checkpoint_id = manager.save_checkpoint(
            orchestrator_name='planning_orchestrator',
            state=state,
            phase='Phase 2: Implementation'
        )
        
        # Verify checkpoint file exists
        checkpoint_path = tmp_path / 'planning_orchestrator' / f'{checkpoint_id}.json'
        assert checkpoint_path.exists(), "Checkpoint file not created"
        
        # Verify checkpoint structure
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
        
        assert 'checkpoint_id' in checkpoint_data
        assert 'orchestrator_name' in checkpoint_data
        assert 'timestamp' in checkpoint_data
        assert 'phase' in checkpoint_data
        assert 'state' in checkpoint_data
        assert checkpoint_data['orchestrator_name'] == 'planning_orchestrator'
        assert checkpoint_data['phase'] == 'Phase 2: Implementation'
        assert checkpoint_data['state'] == state
    
    def test_restore_checkpoint_returns_correct_state(self, tmp_path):
        """Test that restore_checkpoint returns the exact saved state."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        original_state = {
            'phase': 3,
            'tasks': ['task_1', 'task_2', 'task_3'],
            'metadata': {'author': 'CORTEX', 'version': '3.8.1'}
        }
        
        checkpoint_id = manager.save_checkpoint(
            orchestrator_name='tdd_orchestrator',
            state=original_state,
            phase='Phase 3: Refactor'
        )
        
        restored_state = manager.restore_checkpoint(
            orchestrator_name='tdd_orchestrator',
            checkpoint_id=checkpoint_id
        )
        
        assert restored_state == original_state, "Restored state does not match original"
    
    def test_save_checkpoint_returns_unique_ids(self, tmp_path):
        """Test that multiple save_checkpoint calls return unique checkpoint IDs."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        state1 = {'phase': 1, 'task': 'task_1'}
        state2 = {'phase': 2, 'task': 'task_2'}
        
        checkpoint_id1 = manager.save_checkpoint('orchestrator_1', state1)
        time.sleep(0.01)  # Ensure timestamp difference
        checkpoint_id2 = manager.save_checkpoint('orchestrator_1', state2)
        
        assert checkpoint_id1 != checkpoint_id2, "Checkpoint IDs are not unique"


class TestStateSerializationDeserialization:
    """Test serialization/deserialization of complex state objects."""
    
    def test_nested_dict_serialization(self, tmp_path):
        """Test saving and restoring deeply nested dictionaries."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        complex_state = {
            'level1': {
                'level2': {
                    'level3': {
                        'data': [1, 2, 3],
                        'metadata': {'key': 'value'}
                    }
                }
            },
            'tasks': [
                {'task_id': 'T1', 'status': 'completed'},
                {'task_id': 'T2', 'status': 'in-progress'}
            ]
        }
        
        checkpoint_id = manager.save_checkpoint('orchestrator', complex_state)
        restored_state = manager.restore_checkpoint('orchestrator', checkpoint_id)
        
        assert restored_state == complex_state
        assert restored_state['level1']['level2']['level3']['data'] == [1, 2, 3]
    
    def test_list_of_dicts_serialization(self, tmp_path):
        """Test saving and restoring lists containing dictionaries."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        state = {
            'execution_log': [
                {'phase': 1, 'task': 'task_1.1', 'status': 'completed'},
                {'phase': 1, 'task': 'task_1.2', 'status': 'completed'},
                {'phase': 2, 'task': 'task_2.1', 'status': 'in-progress'}
            ]
        }
        
        checkpoint_id = manager.save_checkpoint('orchestrator', state)
        restored_state = manager.restore_checkpoint('orchestrator', checkpoint_id)
        
        assert len(restored_state['execution_log']) == 3
        assert restored_state['execution_log'][2]['status'] == 'in-progress'
    
    def test_none_and_empty_values(self, tmp_path):
        """Test handling of None and empty values in state."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        state = {
            'nullable_field': None,
            'empty_list': [],
            'empty_dict': {},
            'zero_value': 0,
            'false_value': False
        }
        
        checkpoint_id = manager.save_checkpoint('orchestrator', state)
        restored_state = manager.restore_checkpoint('orchestrator', checkpoint_id)
        
        assert restored_state['nullable_field'] is None
        assert restored_state['empty_list'] == []
        assert restored_state['empty_dict'] == {}
        assert restored_state['zero_value'] == 0
        assert restored_state['false_value'] is False


class TestRollbackCapability:
    """Test rollback to previous checkpoint on failure."""
    
    def test_rollback_to_previous_checkpoint(self, tmp_path):
        """Test rolling back to the previous checkpoint after a failure."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        # Save checkpoint 1 (successful phase)
        state1 = {'phase': 1, 'status': 'completed'}
        checkpoint_id1 = manager.save_checkpoint('orchestrator', state1, phase='Phase 1')
        
        # Save checkpoint 2 (phase that will fail)
        state2 = {'phase': 2, 'status': 'in-progress'}
        checkpoint_id2 = manager.save_checkpoint('orchestrator', state2, phase='Phase 2')
        
        # Rollback to checkpoint 1
        rolled_back_state = manager.rollback(
            orchestrator_name='orchestrator',
            checkpoint_id=checkpoint_id1
        )
        
        assert rolled_back_state == state1
        assert rolled_back_state['phase'] == 1
        assert rolled_back_state['status'] == 'completed'
    
    def test_rollback_removes_later_checkpoints(self, tmp_path):
        """Test that rollback removes checkpoints created after the target checkpoint."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        checkpoint_id1 = manager.save_checkpoint('orch', {'phase': 1})
        time.sleep(0.01)
        checkpoint_id2 = manager.save_checkpoint('orch', {'phase': 2})
        time.sleep(0.01)
        checkpoint_id3 = manager.save_checkpoint('orch', {'phase': 3})
        
        # Rollback to checkpoint 1 (should remove checkpoint 2 and 3)
        manager.rollback('orch', checkpoint_id1)
        
        # Verify checkpoint 1 still exists
        state1 = manager.restore_checkpoint('orch', checkpoint_id1)
        assert state1['phase'] == 1
        
        # Verify checkpoint 2 and 3 are removed
        with pytest.raises(CheckpointNotFoundError):
            manager.restore_checkpoint('orch', checkpoint_id2)
        
        with pytest.raises(CheckpointNotFoundError):
            manager.restore_checkpoint('orch', checkpoint_id3)
    
    def test_list_checkpoints_returns_chronological_order(self, tmp_path):
        """Test that list_checkpoints returns checkpoints in chronological order."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        checkpoint_id1 = manager.save_checkpoint('orch', {'phase': 1})
        time.sleep(0.01)
        checkpoint_id2 = manager.save_checkpoint('orch', {'phase': 2})
        time.sleep(0.01)
        checkpoint_id3 = manager.save_checkpoint('orch', {'phase': 3})
        
        checkpoints = manager.list_checkpoints('orch')
        
        assert len(checkpoints) == 3
        assert checkpoints[0]['checkpoint_id'] == checkpoint_id1
        assert checkpoints[1]['checkpoint_id'] == checkpoint_id2
        assert checkpoints[2]['checkpoint_id'] == checkpoint_id3


class TestCheckpointCleanup:
    """Test 30-day retention policy and auto-cleanup."""
    
    def test_cleanup_removes_old_checkpoints(self, tmp_path):
        """Test that cleanup_old_checkpoints removes checkpoints older than 30 days."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        # Create checkpoint with fake old timestamp
        old_checkpoint_id = manager.save_checkpoint('orch', {'phase': 1})
        checkpoint_path = tmp_path / 'orch' / f'{old_checkpoint_id}.json'
        
        # Modify timestamp to 31 days ago
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
        
        old_timestamp = (datetime.now() - timedelta(days=31)).isoformat()
        checkpoint_data['timestamp'] = old_timestamp
        
        with open(checkpoint_path, 'w') as f:
            json.dump(checkpoint_data, f, indent=2)
        
        # Create recent checkpoint
        recent_checkpoint_id = manager.save_checkpoint('orch', {'phase': 2})
        
        # Run cleanup
        removed_count = manager.cleanup_old_checkpoints(retention_days=30)
        
        assert removed_count == 1, "Should remove 1 old checkpoint"
        
        # Verify old checkpoint is gone
        with pytest.raises(CheckpointNotFoundError):
            manager.restore_checkpoint('orch', old_checkpoint_id)
        
        # Verify recent checkpoint still exists
        state = manager.restore_checkpoint('orch', recent_checkpoint_id)
        assert state['phase'] == 2
    
    def test_cleanup_preserves_recent_checkpoints(self, tmp_path):
        """Test that cleanup preserves checkpoints within retention period."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        checkpoint_id1 = manager.save_checkpoint('orch', {'phase': 1})
        checkpoint_id2 = manager.save_checkpoint('orch', {'phase': 2})
        
        removed_count = manager.cleanup_old_checkpoints(retention_days=30)
        
        assert removed_count == 0, "Should not remove recent checkpoints"
        
        # Verify both checkpoints still exist
        assert manager.restore_checkpoint('orch', checkpoint_id1)['phase'] == 1
        assert manager.restore_checkpoint('orch', checkpoint_id2)['phase'] == 2
    
    def test_cleanup_handles_multiple_orchestrators(self, tmp_path):
        """Test that cleanup works across multiple orchestrators."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        # Create old checkpoints for different orchestrators
        old_id1 = manager.save_checkpoint('orch1', {'phase': 1})
        old_id2 = manager.save_checkpoint('orch2', {'phase': 1})
        
        # Modify timestamps to 31 days ago
        for orchestrator, checkpoint_id in [('orch1', old_id1), ('orch2', old_id2)]:
            checkpoint_path = tmp_path / orchestrator / f'{checkpoint_id}.json'
            with open(checkpoint_path, 'r') as f:
                data = json.load(f)
            data['timestamp'] = (datetime.now() - timedelta(days=31)).isoformat()
            with open(checkpoint_path, 'w') as f:
                json.dump(data, f)
        
        removed_count = manager.cleanup_old_checkpoints(retention_days=30)
        
        assert removed_count == 2, "Should remove old checkpoints from both orchestrators"


class TestConcurrentCheckpoints:
    """Test thread-safe operations for parallel orchestrators."""
    
    def test_concurrent_checkpoint_saving(self, tmp_path):
        """Test that multiple threads can save checkpoints concurrently."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        checkpoint_ids = []
        
        def save_checkpoint_thread(thread_id):
            state = {'thread_id': thread_id, 'data': f'data_{thread_id}'}
            checkpoint_id = manager.save_checkpoint(f'orch_{thread_id}', state)
            checkpoint_ids.append(checkpoint_id)
        
        threads = []
        for i in range(10):
            thread = threading.Thread(target=save_checkpoint_thread, args=(i,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all checkpoints have unique IDs
        assert len(checkpoint_ids) == 10
        assert len(set(checkpoint_ids)) == 10, "Checkpoint IDs are not unique"
    
    def test_concurrent_checkpoint_restoration(self, tmp_path):
        """Test that multiple threads can restore checkpoints concurrently."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        # Create checkpoints
        checkpoint_ids = []
        for i in range(5):
            state = {'phase': i, 'data': f'data_{i}'}
            checkpoint_id = manager.save_checkpoint('orch', state)
            checkpoint_ids.append((checkpoint_id, state))
        
        restored_states = []
        
        def restore_checkpoint_thread(checkpoint_id, expected_state):
            state = manager.restore_checkpoint('orch', checkpoint_id)
            restored_states.append((checkpoint_id, state, expected_state))
        
        threads = []
        for checkpoint_id, expected_state in checkpoint_ids:
            thread = threading.Thread(
                target=restore_checkpoint_thread,
                args=(checkpoint_id, expected_state)
            )
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Verify all restorations were successful
        assert len(restored_states) == 5
        for checkpoint_id, restored_state, expected_state in restored_states:
            assert restored_state == expected_state


class TestCheckpointMetadata:
    """Test checkpoint metadata tracking."""
    
    def test_checkpoint_includes_timestamp(self, tmp_path):
        """Test that checkpoints include ISO format timestamps."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        before_save = datetime.now()
        checkpoint_id = manager.save_checkpoint('orch', {'phase': 1})
        after_save = datetime.now()
        
        checkpoint_path = tmp_path / 'orch' / f'{checkpoint_id}.json'
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
        
        timestamp = datetime.fromisoformat(checkpoint_data['timestamp'])
        assert before_save <= timestamp <= after_save
    
    def test_checkpoint_includes_orchestrator_name(self, tmp_path):
        """Test that checkpoints store orchestrator name in metadata."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        checkpoint_id = manager.save_checkpoint(
            orchestrator_name='planning_orchestrator',
            state={'phase': 1}
        )
        
        checkpoint_path = tmp_path / 'planning_orchestrator' / f'{checkpoint_id}.json'
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
        
        assert checkpoint_data['orchestrator_name'] == 'planning_orchestrator'
    
    def test_checkpoint_includes_phase_information(self, tmp_path):
        """Test that checkpoints store phase information."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        checkpoint_id = manager.save_checkpoint(
            orchestrator_name='orch',
            state={'data': 'test'},
            phase='Phase 2: Implementation'
        )
        
        checkpoint_path = tmp_path / 'orch' / f'{checkpoint_id}.json'
        with open(checkpoint_path, 'r') as f:
            checkpoint_data = json.load(f)
        
        assert checkpoint_data['phase'] == 'Phase 2: Implementation'


class TestCheckpointPerformance:
    """Test performance characteristics of checkpoint operations."""
    
    def test_save_checkpoint_performance(self, tmp_path):
        """Test that save_checkpoint completes in <50ms for typical state."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        state = {
            'phase': 2,
            'completed_tasks': [f'task_{i}' for i in range(50)],
            'metadata': {'key': 'value'},
            'execution_log': [
                {'task': f'task_{i}', 'status': 'completed'}
                for i in range(50)
            ]
        }
        
        start_time = time.time()
        checkpoint_id = manager.save_checkpoint('orch', state)
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert elapsed_ms < 50, f"save_checkpoint took {elapsed_ms:.2f}ms (expected <50ms)"
    
    def test_restore_checkpoint_performance(self, tmp_path):
        """Test that restore_checkpoint completes in <50ms for typical state."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        state = {
            'phase': 2,
            'completed_tasks': [f'task_{i}' for i in range(50)],
            'execution_log': [
                {'task': f'task_{i}', 'status': 'completed'}
                for i in range(50)
            ]
        }
        
        checkpoint_id = manager.save_checkpoint('orch', state)
        
        start_time = time.time()
        restored_state = manager.restore_checkpoint('orch', checkpoint_id)
        elapsed_ms = (time.time() - start_time) * 1000
        
        assert elapsed_ms < 50, f"restore_checkpoint took {elapsed_ms:.2f}ms (expected <50ms)"


class TestErrorHandling:
    """Test error handling for edge cases."""
    
    def test_restore_nonexistent_checkpoint_raises_error(self, tmp_path):
        """Test that restoring a non-existent checkpoint raises CheckpointNotFoundError."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        with pytest.raises(CheckpointNotFoundError):
            manager.restore_checkpoint('orch', 'nonexistent-checkpoint-id')
    
    def test_restore_corrupted_checkpoint_raises_error(self, tmp_path):
        """Test that restoring a corrupted checkpoint raises CheckpointCorruptedError."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        # Create checkpoint
        checkpoint_id = manager.save_checkpoint('orch', {'phase': 1})
        
        # Corrupt checkpoint file
        checkpoint_path = tmp_path / 'orch' / f'{checkpoint_id}.json'
        with open(checkpoint_path, 'w') as f:
            f.write("{ invalid json content")
        
        with pytest.raises(CheckpointCorruptedError):
            manager.restore_checkpoint('orch', checkpoint_id)
    
    def test_rollback_to_nonexistent_checkpoint_raises_error(self, tmp_path):
        """Test that rolling back to a non-existent checkpoint raises CheckpointNotFoundError."""
        manager = OrchestrationCheckpointManager(checkpoint_root=str(tmp_path))
        
        with pytest.raises(CheckpointNotFoundError):
            manager.rollback('orch', 'nonexistent-checkpoint-id')


# Pytest fixtures
@pytest.fixture
def tmp_path():
    """Create a temporary directory for test checkpoints."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)
