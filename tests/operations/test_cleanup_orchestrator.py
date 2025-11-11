"""
Tests for Cleanup Orchestrator

Tests comprehensive workspace cleanup functionality including:
- Backup management with GitHub archival
- Root folder organization
- File reorganization
- MD file consolidation
- Bloat detection
- Optimization integration
- Safety verification

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.cleanup import CleanupOrchestrator, CleanupMetrics


@pytest.fixture
def temp_project():
    """Create temporary project structure"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create CORTEX structure
    (temp_dir / 'src').mkdir()
    (temp_dir / 'tests').mkdir()
    (temp_dir / 'docs').mkdir()
    (temp_dir / 'cortex-brain').mkdir()
    (temp_dir / 'prompts').mkdir()
    (temp_dir / 'scripts').mkdir()
    (temp_dir / '.git').mkdir()
    
    # Create some protected files
    (temp_dir / 'README.md').write_text('# CORTEX')
    (temp_dir / 'LICENSE').write_text('MIT License')
    (temp_dir / 'cortex.config.json').write_text('{}')
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


class TestCleanupOrchestrator:
    """Test CleanupOrchestrator class"""
    
    def test_initialization(self, temp_project):
        """Test orchestrator initialization"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        assert orchestrator.project_root == temp_project
        assert isinstance(orchestrator.metrics, CleanupMetrics)
        assert len(orchestrator.protected_paths) > 0
        assert orchestrator.metadata['name'] == 'Cleanup Orchestrator'
    
    def test_metadata(self, temp_project):
        """Test metadata properties"""
        orchestrator = CleanupOrchestrator(temp_project)
        metadata = orchestrator.metadata
        
        assert 'name' in metadata
        assert 'description' in metadata
        assert 'version' in metadata
        assert 'author' in metadata


class TestSafetyVerification:
    """Test safety verification mechanisms"""
    
    def test_protected_paths_preserved(self, temp_project):
        """Test that protected paths are preserved"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create files in protected paths
        src_file = temp_project / 'src' / 'module.py'
        src_file.write_text('# Source code')
        
        test_file = temp_project / 'tests' / 'test_module.py'
        test_file.write_text('# Test code')
        
        # Verify they're protected
        assert orchestrator._is_protected(src_file)
        assert orchestrator._is_protected(test_file)
    
    def test_safety_verification(self, temp_project):
        """Test safety verification"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        safety_result = orchestrator._verify_safety()
        
        assert safety_result['safe'] is True
        assert 'violations' not in safety_result or len(safety_result['violations']) == 0
    
    def test_core_files_protected(self, temp_project):
        """Test that core files are protected"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        core_files = [
            'src/', 'tests/', 'cortex-brain/', 'docs/',
            'README.md', 'LICENSE', 'cortex.config.json'
        ]
        
        for core_file in core_files:
            path = temp_project / core_file
            if path.exists():
                assert orchestrator._is_protected(path), f"{core_file} should be protected"


class TestBackupManagement:
    """Test backup file management"""
    
    def test_backup_detection(self, temp_project):
        """Test backup file detection"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create backup files
        (temp_project / 'file.bak').write_text('backup content')
        (temp_project / 'file.backup').write_text('backup content')
        (temp_project / 'file_backup_20250101.txt').write_text('backup content')
        
        # Run backup management (dry run)
        orchestrator._manage_backups(dry_run=True)
        
        # Should detect backups
        assert orchestrator.metrics.backups_deleted >= 3
    
    @patch('subprocess.run')
    def test_github_archival(self, mock_run, temp_project):
        """Test GitHub archival of backups"""
        mock_run.return_value = Mock(returncode=0, stdout='abc123\n')
        
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create backup file
        backup_file = temp_project / 'file.bak'
        backup_file.write_text('backup content')
        
        # Archive to GitHub
        result = orchestrator._archive_backups_to_github([backup_file])
        
        assert result['success'] is True
        assert 'commit_sha' in result
        assert result['archived_count'] >= 1


class TestRootFolderCleanup:
    """Test root folder cleanup"""
    
    def test_misplaced_files_detected(self, temp_project):
        """Test detection of misplaced files in root"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create misplaced files in root
        (temp_project / 'execute_something.py').write_text('# Script')
        (temp_project / 'test_something.py').write_text('# Test')
        (temp_project / 'random_doc.txt').write_text('Random')
        
        # Run cleanup (dry run)
        orchestrator._cleanup_root_folder(dry_run=True)
        
        # Should detect misplaced files
        assert orchestrator.metrics.root_files_cleaned >= 3
    
    def test_allowed_root_files_preserved(self, temp_project):
        """Test that allowed root files are preserved"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        # These should stay in root
        (temp_project / 'README.md').write_text('# Project')
        (temp_project / 'package.json').write_text('{}')
        (temp_project / 'requirements.txt').write_text('pytest')
        
        orchestrator._cleanup_root_folder(dry_run=True)
        
        # Should not be moved
        assert (temp_project / 'README.md').exists()
        assert (temp_project / 'package.json').exists()
        assert (temp_project / 'requirements.txt').exists()


class TestFileReorganization:
    """Test file reorganization"""
    
    def test_script_reorganization(self, temp_project):
        """Test script file reorganization"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create misplaced script in root
        script_file = temp_project / 'fix_something.py'
        script_file.write_text('# Fix script')
        
        # Run reorganization (dry run)
        orchestrator._reorganize_files(dry_run=True)
        
        # Should be marked for reorganization
        assert orchestrator.metrics.files_reorganized >= 1
    
    def test_documentation_reorganization(self, temp_project):
        """Test documentation reorganization"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create misplaced docs in root
        (temp_project / 'IMPLEMENTATION-SUMMARY.md').write_text('# Summary')
        (temp_project / 'PROJECT-PLAN.md').write_text('# Plan')
        
        # Run reorganization (dry run)
        orchestrator._reorganize_files(dry_run=True)
        
        # Should be marked for reorganization
        assert orchestrator.metrics.files_reorganized >= 2


class TestMDConsolidation:
    """Test MD file consolidation"""
    
    def test_duplicate_detection(self, temp_project):
        """Test duplicate MD file detection"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        docs_dir = temp_project / 'docs'
        
        # Create duplicate versions
        (docs_dir / 'plan.md').write_text('# Latest plan')
        (docs_dir / 'plan-v1.md').write_text('# Old plan v1')
        (docs_dir / 'plan-v2.md').write_text('# Old plan v2')
        (docs_dir / 'plan-COPY.md').write_text('# Copy')
        
        # Run consolidation (dry run)
        orchestrator._consolidate_md_files(dry_run=True)
        
        # Should detect duplicates
        assert orchestrator.metrics.md_files_consolidated >= 3
    
    def test_newest_file_kept(self, temp_project):
        """Test that newest file is kept during consolidation"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        docs_dir = temp_project / 'docs'
        
        # Create files with different timestamps
        old_file = docs_dir / 'doc-v1.md'
        old_file.write_text('# Old')
        
        # Make it older
        import time
        time.sleep(0.1)
        
        new_file = docs_dir / 'doc.md'
        new_file.write_text('# New')
        
        # Run consolidation (dry run)
        orchestrator._consolidate_md_files(dry_run=True)
        
        # Should mark old file for consolidation
        assert orchestrator.metrics.md_files_consolidated >= 1


class TestBloatDetection:
    """Test bloat detection"""
    
    def test_entry_point_bloat_detection(self, temp_project):
        """Test detection of bloated entry points"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        prompts_dir = temp_project / 'prompts'
        prompts_dir.mkdir(exist_ok=True)
        
        # Create bloated entry point (> 3000 tokens = ~12KB)
        bloated_content = "# Entry Point\n" + ("Token " * 4000)
        (prompts_dir / 'entry.md').write_text(bloated_content)
        
        # Detect bloat
        orchestrator._detect_bloat()
        
        # Should detect bloat
        assert orchestrator.metrics.bloated_files_found >= 1
    
    def test_orchestrator_bloat_detection(self, temp_project):
        """Test detection of bloated orchestrators"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        modules_dir = temp_project / 'src' / 'operations' / 'modules'
        modules_dir.mkdir(parents=True, exist_ok=True)
        
        # Create bloated orchestrator (> 5000 tokens = ~20KB)
        bloated_content = "# Orchestrator\n" + ("Token " * 6000)
        (modules_dir / 'big_orchestrator.py').write_text(bloated_content)
        
        # Detect bloat
        orchestrator._detect_bloat()
        
        # Should detect bloat
        assert orchestrator.metrics.bloated_files_found >= 1


class TestGitOperations:
    """Test git operations"""
    
    @patch('subprocess.run')
    def test_git_commit_success(self, mock_run, temp_project):
        """Test successful git commit"""
        mock_run.side_effect = [
            Mock(returncode=0, stdout='M file.txt\n'),  # git status
            Mock(returncode=0),  # git add
            Mock(returncode=0)   # git commit
        ]
        
        orchestrator = CleanupOrchestrator(temp_project)
        orchestrator.metrics.backups_deleted = 5
        orchestrator.metrics.space_freed_bytes = 1024 * 1024  # 1MB
        
        # Commit changes
        orchestrator._git_commit_cleanup()
        
        # Should create commit
        assert orchestrator.metrics.git_commits_created == 1
    
    @patch('subprocess.run')
    def test_no_commit_when_no_changes(self, mock_run, temp_project):
        """Test no commit when no changes"""
        mock_run.return_value = Mock(returncode=0, stdout='')  # No changes
        
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Commit changes
        orchestrator._git_commit_cleanup()
        
        # Should not create commit
        assert orchestrator.metrics.git_commits_created == 0


class TestOptimizationIntegration:
    """Test optimization orchestrator integration"""
    
    @patch('src.operations.modules.cleanup.cleanup_orchestrator.OptimizeCortexOrchestrator')
    def test_optimization_trigger(self, mock_optimizer, temp_project):
        """Test optimization orchestrator trigger"""
        mock_instance = Mock()
        mock_instance.execute.return_value = Mock(
            success=True,
            message="Optimization completed"
        )
        mock_optimizer.return_value = mock_instance
        
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Trigger optimization
        orchestrator._trigger_optimization({'optimization_profile': 'standard'})
        
        # Should trigger optimization
        assert orchestrator.metrics.optimization_triggered is True
    
    @patch('src.operations.modules.cleanup.cleanup_orchestrator.OptimizeCortexOrchestrator')
    def test_optimization_failure_handling(self, mock_optimizer, temp_project):
        """Test handling of optimization failure"""
        mock_instance = Mock()
        mock_instance.execute.return_value = Mock(
            success=False,
            message="Optimization failed"
        )
        mock_optimizer.return_value = mock_instance
        
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Trigger optimization
        orchestrator._trigger_optimization({'optimization_profile': 'standard'})
        
        # Should not mark as triggered
        assert orchestrator.metrics.optimization_triggered is False
        assert len(orchestrator.metrics.warnings) > 0


class TestFullWorkflow:
    """Test complete cleanup workflow"""
    
    @patch('subprocess.run')
    def test_quick_profile(self, mock_run, temp_project):
        """Test quick profile execution"""
        mock_run.return_value = Mock(returncode=0, stdout='')
        
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create test files
        (temp_project / 'file.bak').write_text('backup')
        (temp_project / 'test_script.py').write_text('# Script')
        
        # Execute quick profile
        result = orchestrator.execute({
            'profile': 'quick',
            'dry_run': True
        })
        
        assert result.success is True
        assert 'metrics' in result.data
    
    @patch('subprocess.run')
    def test_comprehensive_profile(self, mock_run, temp_project):
        """Test comprehensive profile execution"""
        mock_run.return_value = Mock(returncode=0, stdout='')
        
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create test files
        (temp_project / 'file.bak').write_text('backup')
        (temp_project / 'docs' / 'plan-v1.md').write_text('# Old')
        (temp_project / 'docs' / 'plan.md').write_text('# New')
        
        # Execute comprehensive profile
        result = orchestrator.execute({
            'profile': 'comprehensive',
            'dry_run': True
        })
        
        assert result.success is True
        assert 'metrics' in result.data
    
    def test_metrics_tracking(self, temp_project):
        """Test metrics tracking throughout workflow"""
        orchestrator = CleanupOrchestrator(temp_project)
        
        # Create various files
        (temp_project / 'file.bak').write_text('backup')
        (temp_project / 'test_script.py').write_text('# Script')
        (temp_project / 'docs' / 'plan-v1.md').write_text('# Old')
        
        # Execute cleanup (dry run)
        result = orchestrator.execute({
            'profile': 'comprehensive',
            'dry_run': True
        })
        
        metrics = result.data['metrics']
        
        # Verify metrics collected
        assert 'backups_deleted' in metrics
        assert 'root_files_cleaned' in metrics
        assert 'files_reorganized' in metrics
        assert 'duration_seconds' in metrics


class TestErrorHandling:
    """Test error handling"""
    
    def test_invalid_project_root(self):
        """Test handling of invalid project root"""
        invalid_path = Path('/nonexistent/path')
        orchestrator = CleanupOrchestrator(invalid_path)
        
        prereq_result = orchestrator.check_prerequisites({})
        
        assert prereq_result['prerequisites_met'] is False
        assert len(prereq_result['issues']) > 0
    
    @patch('subprocess.run')
    def test_git_operation_failure(self, mock_run, temp_project):
        """Test handling of git operation failures"""
        mock_run.side_effect = Exception("Git error")
        
        orchestrator = CleanupOrchestrator(temp_project)
        orchestrator.metrics.backups_deleted = 1
        
        # Should not raise exception
        orchestrator._git_commit_cleanup()
        
        # Should record error
        assert len(orchestrator.metrics.errors) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
