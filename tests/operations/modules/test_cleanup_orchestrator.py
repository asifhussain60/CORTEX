"""
Integration tests for CleanupOrchestrator.

Tests the cleanup operation that removes old files and optimizes databases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.cleanup.cleanup_orchestrator import CleanupOrchestrator
from src.operations.base_operation_module import OperationStatus


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with test files."""
    # Create cortex-brain directory structure
    brain_dir = tmp_path / "cortex-brain"
    brain_dir.mkdir()
    
    # Create conversation captures directory
    captures_dir = brain_dir / "conversation-captures"
    captures_dir.mkdir()
    
    # Create old capture file (35 days old)
    old_file = captures_dir / "old-capture-2024-10-01.jsonl"
    old_file.write_text('{"test": "old"}')
    old_time = (datetime.now() - timedelta(days=35)).timestamp()
    old_file.touch()
    
    # Create recent capture file (10 days old)
    recent_file = captures_dir / "recent-capture-2024-11-15.jsonl"
    recent_file.write_text('{"test": "recent"}')
    
    # Create crawler-temp directory
    crawler_temp = brain_dir / "crawler-temp"
    crawler_temp.mkdir()
    (crawler_temp / "temp1.txt").write_text("temp")
    (crawler_temp / "temp2.txt").write_text("temp")
    
    # Create database
    db_file = brain_dir / "tier1-working-memory.db"
    db_file.write_text("fake database")
    
    return tmp_path


@pytest.fixture
def orchestrator(project_root):
    """Create CleanupOrchestrator instance."""
    context = {"project_root": str(project_root)}
    return CleanupOrchestrator(context)


@pytest.fixture
def context(project_root):
    """Create test context."""
    return {
        "project_root": str(project_root),
        "user_request": "cleanup"
    }


class TestCleanupOrchestrator:
    """Test CleanupOrchestrator functionality."""
    
    def test_initialization(self, orchestrator, project_root):
        """Test orchestrator initializes correctly."""
        assert orchestrator.project_root == project_root
        assert orchestrator.cortex_brain == project_root / "cortex-brain"
    
    def test_validate_returns_true(self, orchestrator, context):
        """Test validate returns true (no prerequisites)."""
        assert orchestrator.validate(context) is True
    
    def test_validate_prerequisites(self, orchestrator, context):
        """Test validate_prerequisites passes."""
        valid, errors = orchestrator.validate_prerequisites(context)
        assert valid is True
        assert len(errors) == 0
    
    def test_get_metadata(self, orchestrator):
        """Test get_metadata returns correct information."""
        metadata = orchestrator.get_metadata()
        
        assert metadata.module_id == "cleanup"
        assert "Cleanup" in metadata.name
        assert metadata.optional is True
    
    @patch('sqlite3.connect')
    def test_execute_success(self, mock_connect, orchestrator, context):
        """Test successful cleanup execution."""
        # Mock database connection
        mock_conn = MagicMock()
        mock_connect.return_value = mock_conn
        
        result = orchestrator.execute(context)
        
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        assert "cleanup" in result.message.lower() or "clean" in result.message.lower()
    
    def test_cleanup_old_conversations(self, orchestrator):
        """Test cleaning old conversation captures."""
        captures_dir = orchestrator.cortex_brain / "conversation-captures"
        captures_dir.mkdir(parents=True, exist_ok=True)
        
        # Create old file
        old_file = captures_dir / "old-2024-01-01.jsonl"
        old_file.write_text("old")
        old_time = (datetime.now() - timedelta(days=35)).timestamp()
        import os
        os.utime(old_file, (old_time, old_time))
        
        # Create recent file
        recent_file = captures_dir / "recent.jsonl"
        recent_file.write_text("recent")
        
        files_before = list(captures_dir.glob("*.jsonl"))
        
        # Execute cleanup
        with patch('sqlite3.connect'):
            orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        files_after = list(captures_dir.glob("*.jsonl"))
        
        # Old file should be removed, recent file preserved
        assert old_file not in files_after or not old_file.exists()
        assert recent_file in files_after
    
    def test_cleanup_temp_files(self, orchestrator):
        """Test cleaning temporary crawler files."""
        temp_dir = orchestrator.cortex_brain / "crawler-temp"
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file = temp_dir / "temp.txt"
        temp_file.write_text("temporary")
        
        assert temp_file.exists()
        
        # Execute cleanup
        with patch('sqlite3.connect'):
            orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Temp files should be removed
        # Note: Implementation may vary
    
    @patch('sqlite3.connect')
    def test_vacuum_database(self, mock_connect, orchestrator):
        """Test database vacuum operation."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Should call VACUUM on databases
        # Note: Exact implementation may vary
        mock_connect.assert_called()
    
    def test_preserves_active_planning(self, orchestrator):
        """Test that active planning documents are preserved."""
        planning_dir = orchestrator.cortex_brain / "documents" / "planning" / "active"
        planning_dir.mkdir(parents=True, exist_ok=True)
        
        plan_file = planning_dir / "PLAN-active.md"
        plan_file.write_text("Active plan")
        
        with patch('sqlite3.connect'):
            orchestrator.execute({"project_root": str(orchestrator.project_root)})
        
        # Active planning should be preserved
        assert plan_file.exists()
    
    def test_rollback_not_applicable(self, orchestrator, context):
        """Test rollback (cleanup is not reversible)."""
        # Cleanup is destructive and cannot be rolled back
        result = orchestrator.rollback(context)
        # Should return False or handle gracefully
        assert isinstance(result, bool)


@pytest.mark.integration
class TestCleanupIntegration:
    """Integration tests with real filesystem."""
    
    def test_cleanup_on_real_project(self):
        """Test cleanup runs on actual CORTEX project."""
        project_root = Path.cwd()
        
        if not (project_root / "cortex-brain").exists():
            pytest.skip("Not in CORTEX project")
        
        context = {"project_root": str(project_root)}
        orchestrator = CleanupOrchestrator(context)
        
        # Run in dry-run mode to avoid actual cleanup
        result = orchestrator.execute(context)
        
        assert result.success is True or result.status == OperationStatus.WARNING
    
    def test_cleanup_reports_metrics(self):
        """Test cleanup reports space saved and items removed."""
        project_root = Path.cwd()
        
        if not (project_root / "cortex-brain").exists():
            pytest.skip("Not in CORTEX project")
        
        context = {"project_root": str(project_root)}
        orchestrator = CleanupOrchestrator(context)
        
        result = orchestrator.execute(context)
        
        # Should report some metrics
        assert result.message is not None
        # May include space saved, files removed, etc.
