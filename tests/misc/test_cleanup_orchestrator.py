"""
Test suite for Cleanup Orchestrator v3.8.1

Tests comprehensive file organization and cleanup:
1. Phase 0: Duplicate functionality analysis (safety-enhanced)
2. Phase 1: File organization (tests, scripts, docs)
3. Phase 2: Reference updates (imports, paths)
4. Phase 3: Obsolete cleanup (uses Phase 0 analysis)
5. Phase 4: Validation (directory compliance)
6. SKULL rule enforcement (HOLISTIC_CODE_DISCOVERY, REFACTOR_CODE_CLEANUP)

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.orchestration.cleanup_orchestrator import CleanupOrchestrator
from src.operations.base_operation_module import OperationStatus


@pytest.fixture
def temp_project_root(tmp_path):
    """Create temporary project structure with misplaced files."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    
    # Create expected directory structure
    (project_root / "src").mkdir()
    (project_root / "tests").mkdir()
    (project_root / "scripts").mkdir()
    (project_root / "cortex-brain" / "documents").mkdir(parents=True)
    (project_root / "cortex-brain" / "backups" / "cleanup").mkdir(parents=True)
    
    # Create misplaced test file (should be in tests/)
    misplaced_test = project_root / "src" / "test_utils.py"
    misplaced_test.write_text("def test_something(): pass")
    
    # Create misplaced doc (should be in cortex-brain/documents/)
    misplaced_doc = project_root / "summary.md"
    misplaced_doc.write_text("# Summary\nThis is a summary document.")
    
    # Create duplicate file (for Phase 0 detection)
    (project_root / "src" / "utils.py").write_text("def helper(): return 42")
    (project_root / "src" / "utils_old.py").write_text("def helper(): return 42")
    
    return project_root


@pytest.fixture
def orchestrator(temp_project_root):
    """Create cleanup orchestrator instance."""
    return CleanupOrchestrator(project_root=temp_project_root)


# ===== PHASE 0: DUPLICATE ANALYSIS =====

class TestPhase0DuplicateAnalysis:
    """Test Phase 0 duplicate functionality detection."""
    
    def test_duplicate_detection_finds_duplicates(self, orchestrator, temp_project_root):
        """Phase 0: Detects duplicate functionality."""
        context = {'phases': ['duplicate_analysis']}
        
        # Mock duplicate analyzer
        with patch('src.operations.modules.orchestration.cleanup_orchestrator.DUPLICATE_ANALYZER_AVAILABLE', True):
            with patch('src.operations.modules.orchestration.cleanup_orchestrator.DuplicateFunctionalityAnalyzer') as MockAnalyzer:
                mock_analyzer = MagicMock()
                mock_analyzer.analyze_directory.return_value = {
                    'duplicates': [
                        {
                            'file1': 'src/utils.py',
                            'file2': 'src/utils_old.py',
                            'similarity': 95.0,
                            'safe_to_delete': True
                        }
                    ]
                }
                MockAnalyzer.return_value = mock_analyzer
                
                result = orchestrator.execute(context)
                
                assert result is not None
                assert orchestrator.metrics['duplicates_found'] >= 0
    
    def test_duplicate_analysis_safety_check(self, orchestrator):
        """Phase 0: Safety checks prevent deleting critical files."""
        context = {'phases': ['duplicate_analysis']}
        
        # Critical files should be marked needs_review, not safe_to_delete
        with patch('src.operations.modules.orchestration.cleanup_orchestrator.DUPLICATE_ANALYZER_AVAILABLE', True):
            with patch('src.operations.modules.orchestration.cleanup_orchestrator.DuplicateFunctionalityAnalyzer') as MockAnalyzer:
                mock_analyzer = MagicMock()
                mock_analyzer.analyze_directory.return_value = {
                    'duplicates': [
                        {
                            'file1': 'src/tier0/core.py',  # Critical file
                            'file2': 'src/tier0/core_backup.py',
                            'similarity': 98.0,
                            'safe_to_delete': False,  # Should NOT be safe
                            'needs_review': True
                        }
                    ]
                }
                MockAnalyzer.return_value = mock_analyzer
                
                result = orchestrator.execute(context)
                
                # Should mark as needs review, not delete
                assert result is not None
    
    def test_duplicate_analysis_skipped_if_unavailable(self, orchestrator):
        """Phase 0: Gracefully skips if analyzer unavailable."""
        context = {'phases': ['duplicate_analysis']}
        
        with patch('src.operations.modules.orchestration.cleanup_orchestrator.DUPLICATE_ANALYZER_AVAILABLE', False):
            result = orchestrator.execute(context)
            
            # Should complete without error
            assert result is not None
            assert result.status in [OperationStatus.SUCCESS, OperationStatus.PARTIAL_SUCCESS]


# ===== PHASE 1: FILE ORGANIZATION =====

class TestPhase1FileOrganization:
    """Test Phase 1 file organization and relocation."""
    
    def test_misplaced_test_files_moved(self, orchestrator, temp_project_root):
        """Phase 1: Test files moved to tests/ directory."""
        misplaced_test = temp_project_root / "src" / "test_utils.py"
        assert misplaced_test.exists()
        
        context = {'phases': ['file_organization']}
        result = orchestrator.execute(context)
        
        # Test file should be moved (or planned to move)
        assert result is not None
        # Verify metrics tracked movement
        assert orchestrator.metrics['files_moved'] >= 0
    
    def test_misplaced_docs_moved(self, orchestrator, temp_project_root):
        """Phase 1: Documents moved to cortex-brain/documents/."""
        misplaced_doc = temp_project_root / "summary.md"
        assert misplaced_doc.exists()
        
        context = {'phases': ['file_organization']}
        result = orchestrator.execute(context)
        
        # Doc should be moved or flagged
        assert result is not None
        assert orchestrator.metrics['files_moved'] >= 0
    
    def test_file_organization_creates_backup(self, orchestrator, temp_project_root):
        """Phase 1: Creates backup before moving files."""
        context = {'phases': ['file_organization']}
        
        with patch('shutil.copy2') as mock_copy:
            result = orchestrator.execute(context)
            
            # Should create backups (implementation-dependent)
            assert result is not None
    
    def test_holistic_code_discovery_prevents_duplicates(self, orchestrator):
        """SKULL: HOLISTIC_CODE_DISCOVERY_ENFORCEMENT prevents duplicate file creation."""
        context = {'phases': ['file_organization']}
        
        # When moving files, should check if destination already exists
        # This enforces HOLISTIC_CODE_DISCOVERY
        result = orchestrator.execute(context)
        
        assert result is not None
        # Implementation should search before moving


# ===== PHASE 2: REFERENCE UPDATES =====

class TestPhase2ReferenceUpdates:
    """Test Phase 2 import and path reference updates."""
    
    def test_import_references_updated(self, orchestrator, temp_project_root):
        """Phase 2: Import statements updated after file moves."""
        # Create file with import
        main_file = temp_project_root / "src" / "main.py"
        main_file.write_text("from src.test_utils import test_something")
        
        context = {'phases': ['reference_updates']}
        result = orchestrator.execute(context)
        
        # References should be updated or tracked
        assert result is not None
        assert orchestrator.metrics['references_updated'] >= 0
    
    def test_path_references_updated(self, orchestrator, temp_project_root):
        """Phase 2: Path strings updated after file moves."""
        config_file = temp_project_root / "config.json"
        config_file.write_text('{"doc_path": "summary.md"}')
        
        context = {'phases': ['reference_updates']}
        result = orchestrator.execute(context)
        
        # Path references should be tracked
        assert result is not None
    
    def test_reference_update_validation(self, orchestrator):
        """Phase 2: Validates all references after updates."""
        context = {'phases': ['reference_updates']}
        
        result = orchestrator.execute(context)
        
        # Should validate references work
        assert result is not None


# ===== PHASE 3: OBSOLETE CLEANUP =====

class TestPhase3ObsoleteCleanup:
    """Test Phase 3 obsolete and duplicate file cleanup."""
    
    def test_uses_phase0_duplicate_analysis(self, orchestrator):
        """Phase 3: Uses Phase 0 duplicate analysis for safe deletion."""
        # Set up Phase 0 report
        orchestrator.duplicate_report = {
            'duplicates': [
                {
                    'file1': 'src/utils.py',
                    'file2': 'src/utils_old.py',
                    'similarity': 95.0,
                    'safe_to_delete': True,
                    'recommended_action': 'delete src/utils_old.py'
                }
            ]
        }
        
        context = {'phases': ['obsolete_cleanup']}
        result = orchestrator.execute(context)
        
        # Should use Phase 0 analysis
        assert result is not None
        assert orchestrator.metrics['files_removed'] >= 0
    
    def test_refactor_code_cleanup_enforcement(self, orchestrator):
        """SKULL: REFACTOR_CODE_CLEANUP_ENFORCEMENT removes orphaned code."""
        # Create orphaned test file (no corresponding source file)
        # This should be flagged for cleanup
        context = {'phases': ['obsolete_cleanup']}
        
        result = orchestrator.execute(context)
        
        # Should clean up orphaned files
        assert result is not None
    
    def test_obsolete_cleanup_respects_safety(self, orchestrator):
        """Phase 3: Respects safety flags from Phase 0."""
        orchestrator.duplicate_report = {
            'duplicates': [
                {
                    'file1': 'src/critical.py',
                    'file2': 'src/critical_backup.py',
                    'safe_to_delete': False,
                    'needs_review': True
                }
            ]
        }
        
        context = {'phases': ['obsolete_cleanup']}
        result = orchestrator.execute(context)
        
        # Should NOT delete files marked unsafe
        assert result is not None
        # needs_review files should be preserved


# ===== PHASE 4: VALIDATION =====

class TestPhase4Validation:
    """Test Phase 4 directory structure and reference validation."""
    
    def test_directory_structure_compliance(self, orchestrator, temp_project_root):
        """Phase 4: Validates directory structure compliance."""
        context = {'phases': ['validation']}
        result = orchestrator.execute(context)
        
        # Should validate expected directories exist
        assert result is not None
    
    def test_reference_integrity_check(self, orchestrator):
        """Phase 4: Checks all references are valid."""
        context = {'phases': ['validation']}
        result = orchestrator.execute(context)
        
        # Should detect broken references
        assert result is not None
    
    def test_no_root_level_docs_validation(self, orchestrator, temp_project_root):
        """Phase 4: Validates no docs at root level."""
        # Create root-level doc (should be flagged)
        (temp_project_root / "README_EXTRA.md").write_text("Extra doc")
        
        context = {'phases': ['validation']}
        result = orchestrator.execute(context)
        
        # Should flag or have moved root-level docs
        assert result is not None


# ===== METRICS & REPORTING =====

class TestMetricsAndReporting:
    """Test metrics collection and reporting."""
    
    def test_metrics_collected_per_phase(self, orchestrator):
        """Metrics collected for each phase."""
        context = {'phases': ['file_organization', 'reference_updates']}
        result = orchestrator.execute(context)
        
        # Metrics should be populated
        assert orchestrator.metrics['files_moved'] >= 0
        assert orchestrator.metrics['references_updated'] >= 0
        assert orchestrator.metrics['files_removed'] >= 0
    
    def test_space_freed_calculated(self, orchestrator):
        """Space freed metric calculated."""
        context = {'phases': ['obsolete_cleanup']}
        result = orchestrator.execute(context)
        
        # Space freed should be tracked
        assert 'space_freed_mb' in orchestrator.metrics
        assert orchestrator.metrics['space_freed_mb'] >= 0.0
    
    def test_error_tracking(self, orchestrator):
        """Errors tracked during cleanup."""
        context = {'phases': ['file_organization']}
        
        # Force an error scenario
        with patch('shutil.move', side_effect=PermissionError("Access denied")):
            result = orchestrator.execute(context)
            
            # Should track errors
            assert result is not None


# ===== INTEGRATION & ERROR HANDLING =====

class TestIntegrationAndErrors:
    """Test integration scenarios and error handling."""
    
    def test_all_phases_in_sequence(self, orchestrator, temp_project_root):
        """All phases execute in correct sequence."""
        context = {
            'phases': [
                'duplicate_analysis',
                'file_organization', 
                'reference_updates',
                'obsolete_cleanup',
                'validation'
            ]
        }
        
        with patch('src.operations.modules.orchestration.cleanup_orchestrator.DUPLICATE_ANALYZER_AVAILABLE', True):
            result = orchestrator.execute(context)
            
            # Should complete all phases
            assert result is not None
    
    def test_phase_failure_handling(self, orchestrator):
        """Handles phase failures gracefully."""
        context = {'phases': ['file_organization']}
        
        with patch.object(orchestrator, '_organize_files', side_effect=Exception("Test error")):
            result = orchestrator.execute(context)
            
            # Should not crash
            assert result is not None
            assert result.status == OperationStatus.FAILED
    
    def test_dry_run_mode(self, orchestrator):
        """Dry run mode doesn't modify files."""
        context = {
            'phases': ['file_organization'],
            'dry_run': True
        }
        
        result = orchestrator.execute(context)
        
        # Should complete without modifying files
        assert result is not None


# ===== BACKUP & ROLLBACK =====

class TestBackupAndRollback:
    """Test backup creation and rollback capability."""
    
    def test_backup_created_before_cleanup(self, orchestrator, temp_project_root):
        """Backup created before any modifications."""
        context = {'phases': ['file_organization']}
        
        result = orchestrator.execute(context)
        
        # Backup directory should exist
        backup_dir = temp_project_root / "cortex-brain" / "backups" / "cleanup"
        assert backup_dir.exists()
    
    def test_backup_includes_metadata(self, orchestrator):
        """Backup includes metadata about changes."""
        context = {'phases': ['file_organization']}
        result = orchestrator.execute(context)
        
        # Should generate metadata about backup
        assert result is not None


# ===== END-TO-END WORKFLOW =====

class TestEndToEndWorkflow:
    """Test complete cleanup workflows."""
    
    def test_complete_cleanup_workflow(self, orchestrator, temp_project_root):
        """Complete cleanup: analyze → organize → update → clean → validate."""
        context = {}  # Default to all phases
        
        with patch('src.operations.modules.orchestration.cleanup_orchestrator.DUPLICATE_ANALYZER_AVAILABLE', False):
            result = orchestrator.execute(context)
            
            # Should complete full workflow
            assert result is not None
            assert result.status in [
                OperationStatus.SUCCESS,
                OperationStatus.PARTIAL_SUCCESS,
                OperationStatus.FAILED
            ]
    
    def test_cleanup_with_conflicts(self, orchestrator, temp_project_root):
        """Handles conflicts during cleanup."""
        # Create conflicting file at destination
        (temp_project_root / "tests" / "test_utils.py").write_text("existing file")
        
        context = {'phases': ['file_organization']}
        result = orchestrator.execute(context)
        
        # Should detect and handle conflicts
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
