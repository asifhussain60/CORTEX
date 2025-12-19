"""
Test suite for Live Documentation System (Phase 2.3)

Following TDD Mastery: RED → GREEN → REFACTOR

Test Categories:
1. Doc Sync Hook Detection - Detect when code changes require doc updates
2. Auto-Update Triggers - Trigger doc generation on specific file changes
3. Integration with Deploy - Doc sync runs during deploy, not development
4. Performance - Sync completes in <30 seconds for typical changes
5. Safety - No sync during active development (dirty git state)
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil


# Tests will fail until implementation exists (RED phase)
class TestDocSyncHooks:
    """Test doc sync hook detection and triggering."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary git repository for testing."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir)
        
        # Initialize git repo
        import subprocess
        subprocess.run(['git', 'init'], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@cortex.ai'], cwd=repo_path, check=True)
        subprocess.run(['git', 'config', 'user.name', 'CORTEX Test'], cwd=repo_path, check=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    def test_doc_sync_hook_detects_agent_changes(self, temp_repo):
        """RED: Test that doc sync detects when agents are added/modified."""
        # This will fail - DocSyncHook doesn't exist yet
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(temp_repo)
        
        # Simulate agent file change
        agent_file = temp_repo / "src" / "cortex_agents" / "new_agent.py"
        agent_file.parent.mkdir(parents=True, exist_ok=True)
        agent_file.write_text("class NewAgent: pass")
        
        changes = hook.detect_changes()
        
        assert changes['requires_doc_update'] is True
        assert 'agents' in changes['categories']
    
    def test_doc_sync_hook_ignores_non_doc_changes(self, temp_repo):
        """RED: Test that doc sync ignores changes that don't affect docs."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(temp_repo)
        
        # Simulate test file change (shouldn't trigger doc update)
        test_file = temp_repo / "tests" / "test_something.py"
        test_file.parent.mkdir(parents=True, exist_ok=True)
        test_file.write_text("def test_foo(): pass")
        
        changes = hook.detect_changes()
        
        assert changes['requires_doc_update'] is False
    
    def test_doc_sync_hook_detects_orchestrator_changes(self, temp_repo):
        """RED: Test that doc sync detects orchestrator changes."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(temp_repo)
        
        orchestrator_file = temp_repo / "src" / "orchestrators" / "new_orchestrator.py"
        orchestrator_file.parent.mkdir(parents=True, exist_ok=True)
        orchestrator_file.write_text("class NewOrchestrator: pass")
        
        changes = hook.detect_changes()
        
        assert changes['requires_doc_update'] is True
        assert 'orchestrators' in changes['categories']
    
    def test_doc_sync_hook_detects_template_changes(self, temp_repo):
        """RED: Test that doc sync detects response template changes."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(temp_repo)
        
        template_file = temp_repo / "cortex-brain" / "response-templates.yaml"
        template_file.parent.mkdir(parents=True, exist_ok=True)
        template_file.write_text("templates:\n  new_template:\n    name: New")
        
        changes = hook.detect_changes()
        
        assert changes['requires_doc_update'] is True
        assert 'templates' in changes['categories']


class TestAutoUpdateTriggers:
    """Test automatic doc update triggering."""
    
    def test_auto_update_runs_during_deploy(self):
        """RED: Test that doc updates run automatically during deploy."""
        from src.orchestrators.deploy_orchestrator import DeployOrchestrator
        from src.utils.doc_sync_hooks import DocSyncHook
        
        # Mock doc sync hook
        with patch('src.utils.doc_sync_hooks.DocSyncHook') as mock_hook:
            mock_hook.return_value.needs_update.return_value = True
            
            orchestrator = DeployOrchestrator(Path.cwd())
            
            # Deploy should trigger doc sync
            # This will fail - integration doesn't exist yet
            result = orchestrator._check_and_update_docs()
            
            assert result['docs_updated'] is True
            mock_hook.return_value.update_docs.assert_called_once()
    
    def test_auto_update_skips_if_no_changes(self):
        """RED: Test that doc updates skip if no relevant changes."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(Path.cwd())
        
        # No changes detected
        with patch.object(hook, 'detect_changes', return_value={'requires_doc_update': False}):
            result = hook.update_docs()
            
            assert result['skipped'] is True
            assert result['reason'] == 'no_changes'
    
    def test_auto_update_blocks_during_dirty_state(self):
        """RED: Test that doc updates block when git is dirty."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(Path.cwd())
        
        # Simulate dirty git state
        with patch('subprocess.run') as mock_run:
            mock_run.return_value.stdout = b'M src/file.py'
            
            result = hook.update_docs()
            
            assert result['blocked'] is True
            assert result['reason'] == 'dirty_git_state'


class TestDeployIntegration:
    """Test doc sync integration with deploy orchestrator."""
    
    def test_deploy_runs_doc_sync_before_version_bump(self):
        """RED: Test deploy order: doc sync → version bump → package."""
        from src.orchestrators.deploy_orchestrator import DeployOrchestrator
        
        orchestrator = DeployOrchestrator(Path.cwd())
        
        call_order = []
        
        def track_doc_sync(*args, **kwargs):
            call_order.append('doc_sync')
            return {'docs_updated': True}
        
        def track_version_bump(*args, **kwargs):
            call_order.append('version_bump')
            return True
        
        with patch.object(orchestrator, '_check_and_update_docs', side_effect=track_doc_sync):
            with patch.object(orchestrator, '_bump_version', side_effect=track_version_bump):
                orchestrator.execute()
        
        # Doc sync must come before version bump
        assert call_order.index('doc_sync') < call_order.index('version_bump')
    
    def test_deploy_skips_doc_sync_if_disabled(self):
        """RED: Test that doc sync can be disabled via config."""
        from src.orchestrators.deploy_orchestrator import DeployOrchestrator
        
        # Config with doc_sync disabled
        config = {'doc_sync': {'enabled': False}}
        
        orchestrator = DeployOrchestrator(Path.cwd(), config=config)
        
        with patch('src.utils.doc_sync_hooks.DocSyncHook') as mock_hook:
            orchestrator.execute()
            
            # Doc sync should not be called
            mock_hook.assert_not_called()


class TestPerformance:
    """Test doc sync performance requirements."""
    
    def test_doc_sync_completes_under_30_seconds(self):
        """RED: Test that doc sync completes in <30 seconds."""
        from src.utils.doc_sync_hooks import DocSyncHook
        import time
        
        hook = DocSyncHook(Path.cwd())
        
        start = time.time()
        hook.update_docs()
        duration = time.time() - start
        
        assert duration < 30.0, f"Doc sync took {duration}s (must be <30s)"
    
    def test_doc_sync_uses_incremental_updates(self):
        """RED: Test that doc sync only updates changed sections."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(Path.cwd())
        
        # Only agent changed
        changes = {'categories': ['agents']}
        
        result = hook.update_docs(changes)
        
        # Should only update agent docs, not all docs
        assert result['sections_updated'] == ['agents']
        assert 'orchestrators' not in result['sections_updated']


class TestSafety:
    """Test doc sync safety mechanisms."""
    
    def test_doc_sync_creates_backup_before_update(self):
        """RED: Test that doc sync backs up files before updating."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(Path.cwd())
        
        result = hook.update_docs()
        
        assert result['backup_created'] is True
        assert 'backup_path' in result
    
    def test_doc_sync_validates_generated_docs(self):
        """RED: Test that doc sync validates docs after generation."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(Path.cwd())
        
        result = hook.update_docs()
        
        assert result['validation_passed'] is True
        assert 'validation_errors' in result
        assert len(result['validation_errors']) == 0
    
    def test_doc_sync_rolls_back_on_validation_failure(self):
        """RED: Test that doc sync rolls back if validation fails."""
        from src.utils.doc_sync_hooks import DocSyncHook
        
        hook = DocSyncHook(Path.cwd())
        
        # Simulate validation failure
        with patch.object(hook, '_validate_docs', return_value=False):
            result = hook.update_docs()
            
            assert result['rolled_back'] is True
            assert result['reason'] == 'validation_failed'


# Test execution summary for TDD tracking
def test_suite_summary():
    """Summary of test suite for TDD Mastery tracking."""
    categories = {
        'Doc Sync Hook Detection': 4,
        'Auto-Update Triggers': 3,
        'Deploy Integration': 2,
        'Performance': 2,
        'Safety': 3
    }
    
    total_tests = sum(categories.values())
    
    print(f"\n{'='*60}")
    print(f"Phase 2.3 Test Suite: {total_tests} tests")
    print(f"{'='*60}")
    for category, count in categories.items():
        print(f"  {category}: {count} tests")
    print(f"{'='*60}\n")
    
    return total_tests


if __name__ == '__main__':
    print("Phase 2.3: Live Documentation System - Test Suite")
    print("Following TDD Mastery: RED → GREEN → REFACTOR")
    print("\nExpected Result: ALL TESTS FAIL (RED phase)")
    print("Next Step: Implement DocSyncHook to pass tests (GREEN phase)\n")
    
    test_suite_summary()
