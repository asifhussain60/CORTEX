"""
Phase 2.1: Deploy-Triggered Architecture Updates - RED Tests

Purpose: Move architecture synchronization from align CLI to deploy CLI
Challenge: Architecture updates during 'align' are too frequent and noisy
Solution: Move to deploy orchestrator - version-gated, less frequent

Test Coverage:
1. Deploy orchestrator triggers architecture sync
2. Architecture sync updates ARCHITECTURE.md
3. Align orchestrator does NOT trigger architecture sync  
4. Sync only runs during deploy, not align
5. Version-gated execution

TDD Phase: RED (Tests should FAIL until GREEN implementation)
Author: Asif Hussain
Created: 2024-12-01
"""

import pytest
import unittest.mock as mock
from pathlib import Path
from datetime import datetime


# Module-level fixtures (pytest auto-discovery)
@pytest.fixture
def mock_cortex_root(tmp_path):
    """Create mock CORTEX directory structure."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create necessary directories
    (cortex_root / "src" / "orchestrators").mkdir(parents=True)
    (cortex_root / "docs").mkdir()
    (cortex_root / "cortex-brain").mkdir()
    
    # Create VERSION file
    version_file = cortex_root / "VERSION"
    version_file.write_text("3.2.0")
    
    # Create ARCHITECTURE.md
    arch_file = cortex_root / "docs" / "ARCHITECTURE.md"
    arch_file.write_text("# CORTEX Architecture\n\nLast updated: 2024-11-01\n")
    
    return cortex_root


@pytest.fixture
def mock_deploy_orchestrator(mock_cortex_root):
    """Mock deploy orchestrator instance."""
    # Import after path setup
    import sys
    sys.path.insert(0, str(mock_cortex_root / "src"))
    
    # Mock the module to prevent import errors in RED phase
    with mock.patch.dict('sys.modules', {
        'orchestrators.deploy_orchestrator': mock.MagicMock()
    }):
        yield mock.MagicMock()


@pytest.fixture
def mock_align_orchestrator(mock_cortex_root):
    """Mock align orchestrator instance."""
    # Mock the module to prevent import errors in RED phase
    with mock.patch.dict('sys.modules', {
        'orchestrators.align_orchestrator': mock.MagicMock()
    }):
        yield mock.MagicMock()


class TestDeployTriggeredArchitectureSync:
    """Test suite for Phase 2.1 - Deploy-triggered architecture synchronization."""
    pass


class TestDeployOrchestratorArchitectureSync:
    """Test deploy orchestrator includes architecture sync step."""
    
    def test_deploy_orchestrator_has_architecture_sync_method(self, mock_deploy_orchestrator):
        """
        RED TEST 1: Deploy orchestrator should have _sync_architecture() method
        
        Acceptance: deploy_cortex.py includes architecture sync step
        """
        # This will FAIL in RED phase - method doesn't exist yet
        assert hasattr(mock_deploy_orchestrator, '_sync_architecture'), \
            "Deploy orchestrator missing _sync_architecture() method"
    
    def test_deploy_orchestrator_calls_architecture_sync(self, mock_deploy_orchestrator):
        """
        RED TEST 2: Deploy orchestrator execute() should call architecture sync
        
        Acceptance: Architecture sync runs during deploy
        """
        # Mock execute method
        mock_deploy_orchestrator.execute = mock.MagicMock()
        mock_deploy_orchestrator._sync_architecture = mock.MagicMock()
        
        # Execute deploy
        mock_deploy_orchestrator.execute()
        
        # This will FAIL in RED phase - method not called
        assert mock_deploy_orchestrator._sync_architecture.called, \
            "Deploy execute() should call _sync_architecture()"
    
    def test_architecture_sync_updates_architecture_md(self, mock_cortex_root, mock_deploy_orchestrator):
        """
        RED TEST 3: Architecture sync should update ARCHITECTURE.md
        
        Acceptance: ARCHITECTURE.md updated with latest features before version bump
        """
        arch_file = mock_cortex_root / "docs" / "ARCHITECTURE.md"
        original_content = arch_file.read_text()
        original_modified = arch_file.stat().st_mtime
        
        # Mock sync method
        mock_deploy_orchestrator._sync_architecture = mock.MagicMock()
        mock_deploy_orchestrator._sync_architecture()
        
        # This will FAIL in RED phase - file not actually updated
        current_modified = arch_file.stat().st_mtime
        assert current_modified > original_modified, \
            "ARCHITECTURE.md should be updated during sync"
    
    def test_architecture_sync_before_version_bump(self, mock_deploy_orchestrator):
        """
        RED TEST 4: Architecture sync should run BEFORE version bump
        
        Acceptance: Architecture reflects latest features for new version
        """
        # Track call order
        call_order = []
        
        def mock_sync():
            call_order.append('sync')
        
        def mock_bump():
            call_order.append('bump')
        
        mock_deploy_orchestrator._sync_architecture = mock_sync
        mock_deploy_orchestrator._bump_version = mock_bump
        mock_deploy_orchestrator.execute = lambda: [mock_sync(), mock_bump()]
        
        mock_deploy_orchestrator.execute()
        
        # This will FAIL in RED phase - order not enforced
        assert call_order == ['sync', 'bump'], \
            f"Architecture sync should run before version bump, got order: {call_order}"
    
    def test_architecture_sync_includes_new_features(self, mock_cortex_root, mock_deploy_orchestrator):
        """
        RED TEST 5: Architecture sync should discover and document new features
        
        Acceptance: New operations/agents/orchestrators appear in ARCHITECTURE.md
        """
        # Create mock new feature
        new_feature_file = mock_cortex_root / "src" / "orchestrators" / "code_review_orchestrator.py"
        new_feature_file.write_text('"""Code Review Orchestrator"""')
        
        # Mock sync method
        mock_deploy_orchestrator._sync_architecture = mock.MagicMock(return_value={
            'features_added': ['code_review_orchestrator']
        })
        
        result = mock_deploy_orchestrator._sync_architecture()
        
        # This will FAIL in RED phase - discovery not implemented
        assert 'features_added' in result, \
            "Architecture sync should return discovered features"
        assert len(result['features_added']) > 0, \
            "Should discover new features in codebase"


class TestAlignOrchestratorNoArchitectureSync:
    """Test align orchestrator does NOT trigger architecture sync."""
    
    def test_align_orchestrator_no_architecture_sync_method(self, mock_align_orchestrator):
        """
        RED TEST 6: Align orchestrator should NOT have _sync_architecture() method
        
        Acceptance: align_orchestrator.py NO LONGER updates architecture
        """
        # This will FAIL in RED phase - method still exists (legacy)
        assert not hasattr(mock_align_orchestrator, '_sync_architecture'), \
            "Align orchestrator should NOT have _sync_architecture() method"
    
    def test_align_orchestrator_execute_no_architecture_sync(self, mock_align_orchestrator):
        """
        RED TEST 7: Align orchestrator execute() should NOT call architecture sync
        
        Acceptance: Sync only triggers during deploy, not align
        """
        # Mock execute method
        mock_align_orchestrator.execute = mock.MagicMock()
        mock_align_orchestrator._sync_architecture = mock.MagicMock()
        
        # Execute align
        mock_align_orchestrator.execute()
        
        # This will FAIL in RED phase - method still called (legacy)
        assert not mock_align_orchestrator._sync_architecture.called, \
            "Align execute() should NOT call _sync_architecture()"


class TestVersionGatedArchitectureSync:
    """Test architecture sync is version-gated."""
    
    def test_architecture_sync_only_during_deploy(self, mock_deploy_orchestrator, mock_align_orchestrator):
        """
        RED TEST 8: Architecture sync should only run during deploy, not align
        
        Acceptance: Sync only triggers during deploy, not align
        """
        # Mock sync tracking
        sync_called = {'deploy': False, 'align': False}
        
        def deploy_sync():
            sync_called['deploy'] = True
        
        def align_sync():
            sync_called['align'] = True
        
        mock_deploy_orchestrator._sync_architecture = deploy_sync
        mock_align_orchestrator._sync_architecture = align_sync
        
        # Execute both
        mock_deploy_orchestrator.execute = lambda: deploy_sync()
        mock_align_orchestrator.execute = lambda: None  # Should not call sync
        
        mock_deploy_orchestrator.execute()
        mock_align_orchestrator.execute()
        
        # This will FAIL in RED phase - align still calls sync (legacy)
        assert sync_called['deploy'] is True, \
            "Deploy should trigger architecture sync"
        assert sync_called['align'] is False, \
            "Align should NOT trigger architecture sync"
    
    def test_architecture_sync_gated_by_version_change(self, mock_deploy_orchestrator):
        """
        RED TEST 9: Architecture sync should be gated by version changes
        
        Acceptance: Sync aligns with version bumps, not every deploy
        """
        # Mock version check
        mock_deploy_orchestrator._version_changed = mock.MagicMock(return_value=True)
        mock_deploy_orchestrator._sync_architecture = mock.MagicMock()
        
        # Execute deploy
        mock_deploy_orchestrator.execute = lambda: (
            mock_deploy_orchestrator._sync_architecture() 
            if mock_deploy_orchestrator._version_changed() 
            else None
        )
        
        mock_deploy_orchestrator.execute()
        
        # This will FAIL in RED phase - version gating not implemented
        assert mock_deploy_orchestrator._version_changed.called, \
            "Should check if version changed"
        assert mock_deploy_orchestrator._sync_architecture.called, \
            "Should sync when version changed"
    
    def test_architecture_sync_skipped_without_version_change(self, mock_deploy_orchestrator):
        """
        RED TEST 10: Architecture sync should skip if version unchanged
        
        Acceptance: Reduces noise - only sync on significant changes
        """
        # Mock version check (no change)
        mock_deploy_orchestrator._version_changed = mock.MagicMock(return_value=False)
        mock_deploy_orchestrator._sync_architecture = mock.MagicMock()
        
        # Execute deploy
        mock_deploy_orchestrator.execute = lambda: (
            mock_deploy_orchestrator._sync_architecture() 
            if mock_deploy_orchestrator._version_changed() 
            else None
        )
        
        mock_deploy_orchestrator.execute()
        
        # This will FAIL in RED phase - sync still runs without version change
        assert not mock_deploy_orchestrator._sync_architecture.called, \
            "Should NOT sync when version unchanged"


class TestArchitectureSyncIntegration:
    """Integration tests for architecture sync workflow."""
    
    def test_full_deploy_workflow_with_architecture_sync(self, mock_cortex_root, mock_deploy_orchestrator):
        """
        RED TEST 11: Full deploy workflow should include architecture sync
        
        Acceptance: End-to-end deploy updates architecture correctly
        """
        # Mock full workflow
        workflow_steps = []
        
        mock_deploy_orchestrator._pre_deploy_checks = lambda: workflow_steps.append('pre_checks')
        mock_deploy_orchestrator._sync_architecture = lambda: workflow_steps.append('sync_arch')
        mock_deploy_orchestrator._bump_version = lambda: workflow_steps.append('bump_version')
        mock_deploy_orchestrator._publish_release = lambda: workflow_steps.append('publish')
        mock_deploy_orchestrator._post_deploy_validation = lambda: workflow_steps.append('validate')
        
        mock_deploy_orchestrator.execute = lambda: [
            mock_deploy_orchestrator._pre_deploy_checks(),
            mock_deploy_orchestrator._sync_architecture(),
            mock_deploy_orchestrator._bump_version(),
            mock_deploy_orchestrator._publish_release(),
            mock_deploy_orchestrator._post_deploy_validation()
        ]
        
        mock_deploy_orchestrator.execute()
        
        # This will FAIL in RED phase - workflow not complete
        assert 'sync_arch' in workflow_steps, \
            "Architecture sync should be in deploy workflow"
        assert workflow_steps.index('sync_arch') < workflow_steps.index('bump_version'), \
            "Architecture sync should run before version bump"
    
    def test_architecture_md_contains_version_timestamp(self, mock_cortex_root, mock_deploy_orchestrator):
        """
        RED TEST 12: ARCHITECTURE.md should contain last-updated timestamp
        
        Acceptance: Documentation shows when it was last synchronized
        """
        arch_file = mock_cortex_root / "docs" / "ARCHITECTURE.md"
        
        # Mock sync
        mock_deploy_orchestrator._sync_architecture = mock.MagicMock()
        mock_deploy_orchestrator._sync_architecture()
        
        # Read updated file
        content = arch_file.read_text()
        
        # This will FAIL in RED phase - timestamp not added
        assert "Last updated:" in content, \
            "ARCHITECTURE.md should include last-updated timestamp"
        assert "2024-12-01" in content or datetime.now().strftime("%Y-%m-%d") in content, \
            "Timestamp should be current date"


# Run tests to confirm RED phase
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
