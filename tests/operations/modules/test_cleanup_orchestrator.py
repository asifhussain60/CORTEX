"""
Tests for CleanupOrchestrator

Comprehensive tests for workspace cleanup functionality including:
- CleanupMetrics data class
- Backup file detection and management
- File organization rules
- MD file consolidation patterns
- Bloat detection thresholds
- Protected paths validation
- Execute workflow with dry-run mode

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import re

from src.operations.modules.cleanup.cleanup_orchestrator import (
    CleanupOrchestrator,
    CleanupMetrics
)
from src.operations.base_operation_module import OperationStatus, OperationPhase


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with test files."""
    # Create directory structure
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / "docs" / "summaries").mkdir(parents=True)
    (tmp_path / "scripts" / "temp").mkdir(parents=True)
    (tmp_path / ".git").mkdir()
    
    # Create backup files
    (tmp_path / "test.bak").write_text("backup content")
    (tmp_path / "old_file.old").write_text("old content")
    (tmp_path / "backup_data.backup").write_text("backup data")
    
    # Create MD files (duplicates)
    (tmp_path / "README.md").write_text("# Main README")
    (tmp_path / "README-v2.md").write_text("# README v2")
    (tmp_path / "SUMMARY.md").write_text("# Summary")
    (tmp_path / "SUMMARY-COPY.md").write_text("# Summary Copy")
    
    # Create misplaced files
    (tmp_path / "temp_fix_script.py").write_text("# Fix script")
    (tmp_path / "STATUS-REPORT.md").write_text("# Status Report")
    
    # Create protected files
    (tmp_path / "src" / "main.py").write_text("# Main code")
    (tmp_path / "tests" / "test_main.py").write_text("# Tests")
    (tmp_path / "LICENSE").write_text("License content")
    
    return tmp_path


@pytest.fixture
def orchestrator(project_root):
    """Create CleanupOrchestrator instance."""
    return CleanupOrchestrator(project_root=project_root)


class TestCleanupMetrics:
    """Test CleanupMetrics data class."""
    
    def test_metrics_initialization(self):
        """Test metrics initialize with defaults."""
        metrics = CleanupMetrics(timestamp=datetime.now())
        
        assert metrics.backups_deleted == 0
        assert metrics.backups_archived == 0
        assert metrics.files_reorganized == 0
        assert metrics.warnings == []
        assert metrics.errors == []
    
    def test_space_freed_conversions(self):
        """Test space freed MB/GB conversions."""
        metrics = CleanupMetrics(
            timestamp=datetime.now(),
            space_freed_bytes=1024 * 1024 * 500  # 500 MB
        )
        
        assert metrics.space_freed_mb == 500.0
        assert abs(metrics.space_freed_gb - 0.488) < 0.01  # ~0.488 GB
    
    def test_metrics_to_dict(self):
        """Test metrics serialization to dict."""
        timestamp = datetime.now()
        metrics = CleanupMetrics(
            timestamp=timestamp,
            backups_deleted=5,
            space_freed_bytes=1024 * 1024 * 100
        )
        
        data = metrics.to_dict()
        
        assert data['backups_deleted'] == 5
        assert data['space_freed_mb'] == 100.0
        assert 'timestamp' in data
        assert isinstance(data['timestamp'], str)


class TestCleanupOrchestratorInitialization:
    """Test CleanupOrchestrator initialization."""
    
    def test_initialization_with_defaults(self):
        """Test orchestrator initializes with default project root."""
        orchestrator = CleanupOrchestrator()
        
        assert orchestrator.project_root == Path.cwd()
        assert isinstance(orchestrator.metrics, CleanupMetrics)
        assert orchestrator.actions_log == []
    
    def test_initialization_with_custom_root(self, project_root):
        """Test orchestrator initializes with custom project root."""
        orchestrator = CleanupOrchestrator(project_root=project_root)
        
        assert orchestrator.project_root == project_root
        assert isinstance(orchestrator.project_root, Path)
    
    def test_protected_paths_defined(self, orchestrator):
        """Test protected paths are properly defined."""
        assert 'src/' in orchestrator.protected_paths
        assert 'tests/' in orchestrator.protected_paths
        assert '.git/' in orchestrator.protected_paths
        assert 'LICENSE' in orchestrator.protected_paths
        assert 'README.md' in orchestrator.protected_paths
    
    def test_backup_patterns_defined(self, orchestrator):
        """Test backup file patterns are defined."""
        assert '*.bak' in orchestrator.backup_patterns
        assert '*.backup' in orchestrator.backup_patterns
        assert '*.old' in orchestrator.backup_patterns
    
    def test_bloat_thresholds_configured(self, orchestrator):
        """Test bloat detection thresholds are configured."""
        assert orchestrator.bloat_thresholds['entry_points'] == 3000
        assert orchestrator.bloat_thresholds['orchestrators'] == 5000
        assert orchestrator.bloat_thresholds['modules'] == 2000
    
    def test_file_organization_rules_defined(self, orchestrator):
        """Test file organization rules are defined."""
        assert len(orchestrator.file_organization_rules) > 0
        
        # Check specific rules exist
        assert any('scripts' in target for target in orchestrator.file_organization_rules.values())
        assert any('docs' in target for target in orchestrator.file_organization_rules.values())


class TestCleanupOrchestratorMetadata:
    """Test CleanupOrchestrator metadata."""
    
    def test_get_metadata(self, orchestrator):
        """Test module metadata is properly configured."""
        metadata = orchestrator.get_metadata()
        
        assert metadata.module_id == "cleanup_orchestrator"
        assert metadata.name == "Cleanup Orchestrator"
        assert "cleanup" in metadata.description.lower()
        assert metadata.version == "1.0.0"
        assert metadata.author == "Asif Hussain"
        assert metadata.phase == OperationPhase.PROCESSING
        assert metadata.priority == 100
        assert 'cleanup' in metadata.tags
        assert 'maintenance' in metadata.tags


class TestCleanupOrchestratorPrerequisites:
    """Test prerequisite checking."""
    
    @patch('src.operations.modules.cleanup.cleanup_orchestrator.subprocess.run')
    def test_check_prerequisites_with_valid_project(self, mock_subprocess, orchestrator):
        """Test prerequisites pass with valid project."""
        # Mock git status to return clean
        mock_subprocess.return_value = Mock(returncode=0, stdout="", stderr="")
        
        result = orchestrator.check_prerequisites({})
        
        assert result['prerequisites_met'] is True
        assert len(result['issues']) == 0
    
    def test_check_prerequisites_without_git(self, tmp_path):
        """Test prerequisites fail without git repository."""
        orchestrator = CleanupOrchestrator(project_root=tmp_path)
        result = orchestrator.check_prerequisites({})
        
        assert result['prerequisites_met'] is False
        assert any('git repository' in issue.lower() for issue in result['issues'])


class TestBackupFileDetection:
    """Test backup file detection logic."""
    
    def test_detects_bak_files(self, orchestrator, project_root):
        """Test detects .bak files."""
        test_file = project_root / "test.bak"
        
        matches = any(
            test_file.match(pattern)
            for pattern in orchestrator.backup_patterns
        )
        
        assert matches is True
    
    def test_detects_backup_files(self, orchestrator, project_root):
        """Test detects .backup files."""
        test_file = project_root / "data.backup"
        
        matches = any(
            test_file.match(pattern)
            for pattern in orchestrator.backup_patterns
        )
        
        assert matches is True
    
    def test_detects_old_files(self, orchestrator, project_root):
        """Test detects .old files."""
        test_file = project_root / "config.old"
        
        matches = any(
            test_file.match(pattern)
            for pattern in orchestrator.backup_patterns
        )
        
        assert matches is True
    
    def test_ignores_regular_files(self, orchestrator, project_root):
        """Test doesn't match regular files."""
        test_file = project_root / "normal.py"
        
        matches = any(
            test_file.match(pattern)
            for pattern in orchestrator.backup_patterns
        )
        
        assert matches is False


class TestFileOrganizationRules:
    """Test file organization rules."""
    
    def test_identifies_script_files(self, orchestrator):
        """Test identifies script files for reorganization."""
        script_patterns = [
            "temp_fix_issue.py",  # Has underscore before fix
            "script_execute_migration.py",  # Has underscore before execute
            "run_demo_feature.py",  # Has underscore before demo
            "system_validate_check.py"  # Has underscore before validate
        ]
        
        for pattern_str in script_patterns:
            matches = any(
                re.match(rule_pattern, pattern_str)
                for rule_pattern in orchestrator.file_organization_rules.keys()
            )
            assert matches is True, f"Should match: {pattern_str}"
    
    def test_identifies_documentation_files(self, orchestrator):
        """Test identifies documentation files."""
        doc_patterns = [
            "PROJECT-SUMMARY.md",
            "ANALYSIS-REPORT.md",
            "SYSTEM-STATUS.md"
        ]
        
        for pattern_str in doc_patterns:
            matches = any(
                re.match(rule_pattern, pattern_str)
                for rule_pattern in orchestrator.file_organization_rules.keys()
            )
            assert matches is True, f"Should match: {pattern_str}"
    
    def test_identifies_implementation_docs(self, orchestrator):
        """Test identifies implementation documentation."""
        impl_patterns = [
            "FEATURE-IMPLEMENTATION.md",
            "API-IMPLEMENTATION.md"
        ]
        
        for pattern_str in impl_patterns:
            matches = any(
                re.match(rule_pattern, pattern_str)
                for rule_pattern in orchestrator.file_organization_rules.keys()
            )
            assert matches is True, f"Should match: {pattern_str}"


class TestMDConsolidationPatterns:
    """Test MD file consolidation patterns."""
    
    def test_version_suffix_pattern(self, orchestrator):
        """Test MD version suffix pattern."""
        pattern, replacement = orchestrator.md_consolidation_patterns[0]
        
        assert re.match(pattern, "README-v2.md")
        assert re.match(pattern, "GUIDE-v10.md")
        assert not re.match(pattern, "README.md")
    
    def test_date_suffix_pattern(self, orchestrator):
        """Test MD date suffix pattern."""
        pattern, replacement = orchestrator.md_consolidation_patterns[1]
        
        assert re.match(pattern, "REPORT-20250101.md")
        assert not re.match(pattern, "REPORT.md")
    
    def test_copy_suffix_pattern(self, orchestrator):
        """Test MD COPY suffix pattern."""
        pattern, replacement = orchestrator.md_consolidation_patterns[2]
        
        assert re.match(pattern, "README-COPY.md")
        assert not re.match(pattern, "README.md")


class TestBloatDetection:
    """Test bloat detection configuration."""
    
    def test_bloat_thresholds_reasonable(self, orchestrator):
        """Test bloat thresholds are reasonable values."""
        assert orchestrator.bloat_thresholds['entry_points'] > 0
        assert orchestrator.bloat_thresholds['orchestrators'] > 0
        assert orchestrator.bloat_thresholds['modules'] > 0
    
    def test_bloat_detection_categories(self, orchestrator):
        """Test all required categories exist."""
        required = ['entry_points', 'orchestrators', 'modules']
        
        for category in required:
            assert category in orchestrator.bloat_thresholds


class TestCleanupExecute:
    """Test cleanup execute method."""
    
    def test_execute_dry_run_mode(self, orchestrator):
        """Test execute in dry-run mode."""
        files_before = list(orchestrator.project_root.rglob("*"))
        files_before_count = len([f for f in files_before if f.is_file()])
        
        result = orchestrator.execute({'dry_run': True, 'profile': 'standard'})
        
        files_after = list(orchestrator.project_root.rglob("*"))
        files_after_count = len([f for f in files_after if f.is_file()])
        
        assert result.success is True or result.status == OperationStatus.WARNING
        assert files_before_count == files_after_count
    
    def test_execute_tracks_metrics(self, orchestrator):
        """Test execute tracks metrics."""
        result = orchestrator.execute({'dry_run': True, 'profile': 'standard'})
        
        assert isinstance(orchestrator.metrics, CleanupMetrics)
        assert orchestrator.metrics.duration_seconds >= 0
    
    def test_execute_protected_paths_never_touched(self, orchestrator):
        """Test protected paths are never touched."""
        protected_file = orchestrator.project_root / "src" / "important.py"
        protected_file.write_text("# Important code")
        
        orchestrator.execute({'dry_run': True, 'profile': 'standard'})
        
        assert protected_file.exists()
        assert protected_file.read_text() == "# Important code"
        # May include space saved, files removed, etc.
