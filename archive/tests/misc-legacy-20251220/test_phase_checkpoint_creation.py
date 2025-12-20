"""
Test suite for Phase Checkpoint Creation (INCREMENT 9).

Tests the integration between PhaseCheckpointManager and GitCheckpointOrchestrator
for automated checkpoint creation during workflow phases.

INCREMENT 9: Phase Checkpoint Creation
- Pre-work checkpoint creation before operations
- Phase checkpoint creation after phase completion  
- Git checkpoint orchestrator integration
- Metadata storage after checkpoint creation

Test Coverage:
- create_pre_work_checkpoint() method
- create_phase_checkpoint() method
- GitCheckpointOrchestrator integration
- Metadata persistence after creation
- Error handling for checkpoint failures

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Status: RED PHASE (tests expected to fail)
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager


class TestPhaseCheckpointCreation:
    """Test suite for phase checkpoint creation functionality."""
    
    @pytest.fixture
    def manager(self, tmp_path):
        """Create PhaseCheckpointManager with temporary directory."""
        cortex_dir = tmp_path / "CORTEX"
        cortex_dir.mkdir()
        return PhaseCheckpointManager(cortex_root=cortex_dir)
    
    def test_manager_creates_pre_work_checkpoint(self, manager):
        """
        Test: Manager creates pre-work checkpoint before operation starts
        
        Given: PhaseCheckpointManager initialized
        When: create_pre_work_checkpoint() called with operation and session_id
        Then: 
          - Returns checkpoint_id (str)
          - Git checkpoint created via GitCheckpointOrchestrator
          - Metadata stored with phase="pre-work"
          - Checkpoint retrievable via get_checkpoint_metadata()
        """
        # Mock GitCheckpointOrchestrator
        with patch.object(manager, 'git_checkpoint') as mock_git:
            mock_git.create_checkpoint.return_value = {
                'success': True,
                'checkpoint_id': 'pre-work-20251128-100000',
                'commit_sha': 'abc123def456'
            }
            
            # Execute
            checkpoint_id = manager.create_pre_work_checkpoint(
                operation="Test feature implementation",
                session_id="test-session-001"
            )
            
            # Assert
            assert checkpoint_id is not None
            assert checkpoint_id == 'pre-work-20251128-100000'
            
            # Verify git checkpoint was created
            mock_git.create_checkpoint.assert_called_once()
            call_args = mock_git.create_checkpoint.call_args
            assert call_args[1]['session_id'] == 'test-session-001'
            assert call_args[1]['checkpoint_type'] == 'pre-work'
            assert 'Test feature implementation' in call_args[1]['message']
            
            # Verify metadata stored
            metadata = manager.get_checkpoint_metadata('test-session-001', 'pre-work')
            assert metadata is not None
            assert metadata['checkpoint_id'] == 'pre-work-20251128-100000'
            assert metadata['commit_sha'] == 'abc123def456'
    
    def test_manager_creates_phase_checkpoint(self, manager):
        """
        Test: Manager creates phase checkpoint after phase completion
        
        Given: PhaseCheckpointManager initialized
        When: create_phase_checkpoint() called with phase name, session_id, and metrics
        Then:
          - Returns checkpoint_id (str)
          - Git checkpoint created with correct phase type
          - Metadata stored with phase metrics
          - Checkpoint retrievable via get_checkpoint_metadata()
        """
        # Mock GitCheckpointOrchestrator
        with patch.object(manager, 'git_checkpoint') as mock_git:
            mock_git.create_checkpoint.return_value = {
                'success': True,
                'checkpoint_id': 'phase-1-20251128-110000',
                'commit_sha': 'def456abc789'
            }
            
            # Execute
            checkpoint_id = manager.create_phase_checkpoint(
                phase="phase-1-foundation",
                session_id="test-session-001",
                metrics={'duration': 300, 'tests_passing': 25}
            )
            
            # Assert
            assert checkpoint_id is not None
            assert checkpoint_id == 'phase-1-20251128-110000'
            
            # Verify git checkpoint was created
            mock_git.create_checkpoint.assert_called_once()
            call_args = mock_git.create_checkpoint.call_args
            assert call_args[1]['session_id'] == 'test-session-001'
            assert call_args[1]['checkpoint_type'] == 'phase-phase-1-foundation'
            assert 'phase-1-foundation' in call_args[1]['message']
            
            # Verify metadata stored with metrics
            metadata = manager.get_checkpoint_metadata('test-session-001', 'phase-1-foundation')
            assert metadata is not None
            assert metadata['checkpoint_id'] == 'phase-1-20251128-110000'
            assert metadata['commit_sha'] == 'def456abc789'
            assert metadata['metrics']['duration'] == 300
            assert metadata['metrics']['tests_passing'] == 25
    
    def test_manager_handles_git_checkpoint_failure(self, manager):
        """
        Test: Manager handles git checkpoint creation failure gracefully
        
        Given: PhaseCheckpointManager initialized
        When: GitCheckpointOrchestrator returns failure
        Then:
          - Returns None (no checkpoint_id)
          - No metadata stored
          - Warning logged (not tested here)
        """
        # Mock GitCheckpointOrchestrator failure
        with patch.object(manager, 'git_checkpoint') as mock_git:
            mock_git.create_checkpoint.return_value = {
                'success': False,
                'error': 'Git repository not found'
            }
            
            # Execute
            checkpoint_id = manager.create_pre_work_checkpoint(
                operation="Test operation",
                session_id="test-session-002"
            )
            
            # Assert
            assert checkpoint_id is None
            
            # Verify no metadata stored
            metadata = manager.get_checkpoint_metadata('test-session-002', 'pre-work')
            assert metadata is None
    
    def test_manager_integrates_with_git_checkpoint_orchestrator(self, manager):
        """
        Test: Manager correctly integrates with GitCheckpointOrchestrator
        
        Given: PhaseCheckpointManager initialized
        When: create_pre_work_checkpoint() called
        Then:
          - GitCheckpointOrchestrator.create_checkpoint() called
          - Correct parameters passed (session_id, checkpoint_type, message)
          - Commit SHA extracted from result
          - Checkpoint ID extracted from result
        """
        # Mock GitCheckpointOrchestrator
        with patch.object(manager, 'git_checkpoint') as mock_git:
            mock_git.create_checkpoint.return_value = {
                'success': True,
                'checkpoint_id': 'pre-work-test',
                'commit_sha': 'testsha123'
            }
            
            # Execute
            manager.create_pre_work_checkpoint(
                operation="Integration test",
                session_id="integration-session"
            )
            
            # Assert git checkpoint called correctly
            mock_git.create_checkpoint.assert_called_once()
            call_kwargs = mock_git.create_checkpoint.call_args[1]
            
            assert 'session_id' in call_kwargs
            assert 'checkpoint_type' in call_kwargs
            assert 'message' in call_kwargs
            assert call_kwargs['session_id'] == 'integration-session'
            assert call_kwargs['checkpoint_type'] == 'pre-work'
    
    def test_manager_stores_correct_metadata_after_checkpoint(self, manager):
        """
        Test: Manager stores complete metadata after checkpoint creation
        
        Given: PhaseCheckpointManager initialized
        When: create_phase_checkpoint() succeeds
        Then:
          - Metadata includes checkpoint_id
          - Metadata includes commit_sha
          - Metadata includes phase name
          - Metadata includes timestamp
          - Metadata includes provided metrics
        """
        # Mock GitCheckpointOrchestrator
        with patch.object(manager, 'git_checkpoint') as mock_git:
            mock_git.create_checkpoint.return_value = {
                'success': True,
                'checkpoint_id': 'phase-2-test',
                'commit_sha': 'commit-sha-456'
            }
            
            # Execute
            manager.create_phase_checkpoint(
                phase="phase-2-implementation",
                session_id="metadata-test",
                metrics={'lines_added': 150, 'tests_added': 10}
            )
            
            # Assert metadata completeness
            metadata = manager.get_checkpoint_metadata('metadata-test', 'phase-2-implementation')
            
            assert metadata is not None
            assert 'checkpoint_id' in metadata
            assert 'commit_sha' in metadata
            assert 'phase' in metadata
            assert 'created_at' in metadata
            assert 'metrics' in metadata
            
            assert metadata['checkpoint_id'] == 'phase-2-test'
            assert metadata['commit_sha'] == 'commit-sha-456'
            assert metadata['phase'] == 'phase-2-implementation'
            assert metadata['metrics']['lines_added'] == 150
            assert metadata['metrics']['tests_added'] == 10
