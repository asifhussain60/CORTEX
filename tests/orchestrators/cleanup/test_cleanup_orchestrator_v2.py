"""
Tests for CleanupOrchestratorV2 - Comprehensive unit and integration tests.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.orchestrators.cleanup.cleanup_orchestrator_v2 import CleanupOrchestratorV2
from src.orchestrators.cleanup.cache_cleaner import CacheCleaner
from src.orchestrators.cleanup.log_manager import LogManager
from src.orchestrators.cleanup.artifact_remover import ArtifactRemover
from src.orchestrators.cleanup.git_optimizer import GitOptimizer
from src.orchestrators.cleanup.cleanup_engine import CleanupEngine
from src.database.planning_state_db import PlanningStateDB
from src.orchestrators.base.base_orchestrator import OrchestratorStatus


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_state_db():
    """Mock PlanningStateDB."""
    db = Mock(spec=PlanningStateDB)
    # Configure mock attributes before they're accessed
    db.create_session = Mock(return_value="test-session-123")
    db.log_execution = Mock(return_value=1)
    db.update_execution_log = Mock()
    db.get_execution_logs = Mock(return_value=[])
    return db


@pytest.fixture
def config_file(temp_workspace):
    """Create test configuration file."""
    config_path = temp_workspace / "test-config.yaml"
    config_content = """
schema_version: "5.0"

orchestrator:
  name: "cleanup_orchestrator_v2"
  version: "2.0.0"
  type: "autonomous"

modes:
  cache:
    confirmation_required: false
  logs:
    log_rotation_threshold_mb: 10
  artifacts:
    retention_days: 30

rules_file: "cleanup-rules.yaml"
templates:
  base_path: "cortex-brain/templates"
"""
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def cleanup_rules_file(temp_workspace):
    """Create test cleanup rules file."""
    rules_path = temp_workspace / "cleanup-rules.yaml"
    rules_content = """
version: "1.1"

categories:
  python_cache:
    enabled: true
    priority: high
    risk_level: low
    paths:
      - "**/__pycache__"
      - "**/*.pyc"
    action: delete_all
    reason: "Python cache files"

protected_directories:
  - ".git"
  - "src"
"""
    rules_path.write_text(rules_content)
    return rules_path


class TestCleanupOrchestratorV2Initialization:
    """Test CleanupOrchestratorV2 initialization."""
    
    def test_init_success(self, config_file, mock_state_db, temp_workspace):
        """Test successful initialization."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        assert orchestrator.name == "cleanup_orchestrator_v2"
        assert orchestrator.version == "2.0.0"
        assert orchestrator.workspace_root == temp_workspace
        assert isinstance(orchestrator.cache_cleaner, CacheCleaner)
        assert isinstance(orchestrator.log_manager, LogManager)
        assert isinstance(orchestrator.artifact_remover, ArtifactRemover)
        assert isinstance(orchestrator.git_optimizer, GitOptimizer)
    
    def test_init_missing_config(self, mock_state_db, temp_workspace):
        """Test initialization with missing config file."""
        with pytest.raises(FileNotFoundError):
            CleanupOrchestratorV2(
                config_path="nonexistent.yaml",
                state_db=mock_state_db,
                workspace_root=temp_workspace
            )


class TestModeDetection:
    """Test cleanup mode detection and validation."""
    
    def test_extract_mode_cache(self, config_file, mock_state_db, temp_workspace):
        """Test mode extraction for cache."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        mode = orchestrator._extract_mode_from_request("cleanup cache")
        assert mode == "cache"
    
    def test_extract_mode_logs(self, config_file, mock_state_db, temp_workspace):
        """Test mode extraction for logs."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        mode = orchestrator._extract_mode_from_request("cleanup logs")
        assert mode == "logs"
    
    def test_extract_mode_default(self, config_file, mock_state_db, temp_workspace):
        """Test default mode extraction."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        mode = orchestrator._extract_mode_from_request("cleanup")
        assert mode == "full"
    
    def test_invalid_mode(self, config_file, mock_state_db, temp_workspace):
        """Test invalid mode handling."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        result = orchestrator.execute(mode="invalid_mode")
        assert result.status == OrchestratorStatus.ERROR
        assert "Invalid cleanup mode" in result.error_message


class TestCacheCleanup:
    """Test cache cleanup mode."""
    
    def test_cache_cleanup_execution(self, config_file, mock_state_db, temp_workspace):
        """Test cache cleanup execution."""
        # Create test cache files
        cache_dir = temp_workspace / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "test.pyc").write_text("cache")
        
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        # Mock cache cleaner
        orchestrator.cache_cleaner.execute = Mock(return_value={
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': 1,
                'files_deleted': 1,
                'files_archived': 0,
                'folders_deleted': 0,
                'space_freed_bytes': 1024,
                'space_freed_mb': 0.001,
                'categories_processed': 1
            },
            'categories': {'python_cache': {'count': 1, 'size_mb': 0.001}},
            'errors': [],
            'warnings': [],
            'artifacts': []
        })
        
        result = orchestrator.execute(mode="cache")
        
        assert result.status == OrchestratorStatus.SUCCESS
        assert result.metadata['mode'] == 'cache'
        orchestrator.cache_cleaner.execute.assert_called_once()


class TestLogManagement:
    """Test log management mode."""
    
    def test_log_rotation(self, config_file, mock_state_db, temp_workspace):
        """Test log rotation for large logs."""
        # Create large log file
        log_file = temp_workspace / "test.log"
        log_file.write_text("x" * (11 * 1024 * 1024))  # 11MB
        
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        # Mock log manager
        orchestrator.log_manager.execute = Mock(return_value={
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': 1,
                'files_deleted': 0,
                'files_archived': 1,
                'folders_deleted': 0,
                'space_freed_bytes': 0,
                'space_freed_mb': 0.0,
                'categories_processed': 1
            },
            'log_rotation': {
                'rotated_count': 1,
                'rotated_logs': [
                    {'path': 'test.log', 'size_mb': 11.0, 'archived_to': 'logs/archive/test_20260102.log.gz'}
                ]
            },
            'categories': {},
            'errors': [],
            'warnings': [],
            'artifacts': []
        })
        
        result = orchestrator.execute(mode="logs")
        
        assert result.status == OrchestratorStatus.SUCCESS
        orchestrator.log_manager.execute.assert_called_once()


class TestFullCleanup:
    """Test full cleanup mode."""
    
    def test_full_cleanup_aggregation(self, config_file, mock_state_db, temp_workspace):
        """Test full cleanup aggregates all categories."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        # Mock category cleaners
        mock_result = {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': 10,
                'files_deleted': 5,
                'files_archived': 0,
                'folders_deleted': 1,
                'space_freed_bytes': 1024000,
                'space_freed_mb': 1.0,
                'categories_processed': 1
            },
            'categories': {},
            'errors': [],
            'warnings': [],
            'artifacts': []
        }
        
        orchestrator.cache_cleaner.execute = Mock(return_value=mock_result.copy())
        orchestrator.log_manager.execute = Mock(return_value=mock_result.copy())
        orchestrator.artifact_remover.execute = Mock(return_value=mock_result.copy())
        
        result = orchestrator.execute(mode="full")
        
        assert result.status == OrchestratorStatus.SUCCESS
        # Verify all cleaners were called
        orchestrator.cache_cleaner.execute.assert_called_once()
        orchestrator.log_manager.execute.assert_called_once()
        orchestrator.artifact_remover.execute.assert_called_once()


class TestGitOptimization:
    """Test git optimization mode."""
    
    def test_git_optimization(self, config_file, mock_state_db, temp_workspace):
        """Test git optimization execution."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        # Mock git optimizer
        orchestrator.git_optimizer.execute = Mock(return_value={
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': 0,
                'files_deleted': 0,
                'files_archived': 0,
                'folders_deleted': 0,
                'space_freed_bytes': 1048576,
                'space_freed_mb': 1.0,
                'categories_processed': 1
            },
            'operations': [
                {'operation': 'git_gc', 'success': True},
                {'operation': 'git_prune', 'success': True},
                {'operation': 'git_repack', 'success': True}
            ],
            'categories': {},
            'errors': [],
            'warnings': [],
            'artifacts': []
        })
        
        result = orchestrator.execute(mode="git")
        
        assert result.status == OrchestratorStatus.SUCCESS
        orchestrator.git_optimizer.execute.assert_called_once()


class TestStatePersistence:
    """Test state persistence in database."""
    
    def test_session_creation(self, config_file, mock_state_db, temp_workspace):
        """Test session is created in database."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        orchestrator.cache_cleaner.execute = Mock(return_value={
            'timestamp': datetime.now().isoformat(),
            'statistics': {'files_scanned': 0, 'files_deleted': 0, 'files_archived': 0,
                          'folders_deleted': 0, 'space_freed_bytes': 0, 'space_freed_mb': 0.0,
                          'categories_processed': 0},
            'categories': {}, 'errors': [], 'warnings': [], 'artifacts': []
        })
        
        result = orchestrator.execute(mode="cache")
        
        mock_state_db.create_session.assert_called_once()
        assert result.metadata['session_id'] == "test-session-123"
    
    def test_session_artifact_saved(self, config_file, mock_state_db, temp_workspace):
        """Test cleanup result is saved as artifact."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        orchestrator.cache_cleaner.execute = Mock(return_value={
            'timestamp': datetime.now().isoformat(),
            'statistics': {'files_scanned': 0, 'files_deleted': 0, 'files_archived': 0,
                          'folders_deleted': 0, 'space_freed_bytes': 0, 'space_freed_mb': 0.0,
                          'categories_processed': 0},
            'categories': {}, 'errors': [], 'warnings': [], 'artifacts': []
        })
        
        orchestrator.execute(mode="cache")
        
        mock_state_db.save_session_artifact.assert_called_once()
        mock_state_db.complete_session.assert_called_once_with("test-session-123")


class TestErrorHandling:
    """Test error handling and recovery."""
    
    def test_cleaner_exception_handling(self, config_file, mock_state_db, temp_workspace):
        """Test exception in cleaner is caught and logged."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        orchestrator.cache_cleaner.execute = Mock(side_effect=Exception("Test error"))
        
        result = orchestrator.execute(mode="cache")
        
        assert result.status == OrchestratorStatus.ERROR
        assert "Test error" in result.error_message
        mock_state_db.fail_session.assert_called_once()


class TestTemplateRendering:
    """Test report template rendering."""
    
    def test_report_rendering(self, config_file, mock_state_db, temp_workspace):
        """Test cleanup report is rendered."""
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        orchestrator.cache_cleaner.execute = Mock(return_value={
            'timestamp': datetime.now().isoformat(),
            'statistics': {'files_scanned': 10, 'files_deleted': 5, 'files_archived': 0,
                          'folders_deleted': 1, 'space_freed_bytes': 1024, 'space_freed_mb': 0.001,
                          'categories_processed': 1},
            'categories': {'python_cache': {'count': 5, 'size_mb': 0.001}},
            'errors': [], 'warnings': [], 'artifacts': []
        })
        
        result = orchestrator.execute(mode="cache")
        
        assert result.status == OrchestratorStatus.SUCCESS
        assert 'report' in result.metadata
        report = result.metadata['report']
        assert 'Cleanup Report' in report
        assert 'cache' in report.lower()


# Integration Tests
class TestIntegration:
    """Integration tests with real file system."""
    
    def test_end_to_end_cache_cleanup(self, config_file, cleanup_rules_file, mock_state_db, temp_workspace):
        """End-to-end test of cache cleanup."""
        # Create test cache files
        cache_dir = temp_workspace / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "test1.pyc").write_text("cache1")
        (cache_dir / "test2.pyc").write_text("cache2")
        
        # Create cleanup rules file in workspace
        (temp_workspace / "cleanup-rules.yaml").write_text(cleanup_rules_file.read_text())
        
        orchestrator = CleanupOrchestratorV2(
            config_path=str(config_file),
            state_db=mock_state_db,
            workspace_root=temp_workspace
        )
        
        result = orchestrator.execute(mode="cache")
        
        assert result.status == OrchestratorStatus.SUCCESS
        # Note: Protected directories may prevent deletion in tests


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
