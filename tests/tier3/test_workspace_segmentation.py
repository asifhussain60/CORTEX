"""
Tests for Brain Tier 3 Workspace Segmentation

Tests workspace-aware context storage and retrieval.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import pytest
import json
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from src.tier3.brain_tier3 import (
    BrainTier3,
    Tier3MigrationManager,
    get_brain_tier3
)


@pytest.fixture
def temp_cortex_root(tmp_path):
    """Create temporary CORTEX root structure."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    brain_dir = cortex_root / "cortex-brain"
    brain_dir.mkdir()
    
    tier3_dir = brain_dir / "tier3"
    tier3_dir.mkdir()
    
    return cortex_root


@pytest.fixture
def mock_workspace_detection(monkeypatch):
    """Mock workspace detection to return consistent workspace_id."""
    def mock_detect():
        return "test-workspace-uuid"
    
    with patch('src.tier3.brain_tier3.BrainTier3._detect_workspace_id', return_value="test-workspace-uuid"):
        yield


class TestBrainTier3Initialization:
    """Test BrainTier3 initialization and workspace detection."""
    
    def test_initialization_with_explicit_workspace(self, temp_cortex_root):
        """Test initialization with explicit workspace ID."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="explicit-uuid"
        )
        
        assert tier3.workspace_id == "explicit-uuid"
        assert tier3.workspace_dir == temp_cortex_root / "cortex-brain" / "tier3" / "workspace-explicit-uuid"
    
    def test_workspace_directory_created(self, temp_cortex_root):
        """Test workspace directory is created on initialization."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="new-workspace"
        )
        
        assert tier3.workspace_dir.exists()
        assert tier3.workspace_dir.is_dir()
    
    def test_database_paths_set(self, temp_cortex_root):
        """Test database paths are correctly set."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-uuid"
        )
        
        expected_dir = temp_cortex_root / "cortex-brain" / "tier3" / "workspace-test-uuid"
        assert tier3.context_db == expected_dir / "context.db"
        assert tier3.metrics_db == expected_dir / "metrics.db"


class TestContextStorage:
    """Test context data storage."""
    
    def test_store_context_creates_table(self, temp_cortex_root):
        """Test storing context creates database and table."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        
        data = {"key": "value", "count": 42}
        success = tier3.store_context("test_metric", data)
        
        assert success is True
        assert tier3.context_db.exists()
    
    def test_store_context_inserts_data(self, temp_cortex_root):
        """Test stored context can be retrieved from database."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        
        data = {"metric": "build_success", "duration": 45}
        tier3.store_context("build_metric", data)
        
        # Verify in database
        conn = sqlite3.connect(tier3.context_db)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM context WHERE context_type = ?", ("build_metric",))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        stored_data = json.loads(row[2])  # data column
        assert stored_data == data
    
    def test_store_multiple_contexts(self, temp_cortex_root):
        """Test storing multiple context entries."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        
        for i in range(5):
            data = {"index": i, "value": f"test_{i}"}
            tier3.store_context("test_metric", data)
        
        # Verify count
        conn = sqlite3.connect(tier3.context_db)
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM context")
        count = cursor.fetchone()[0]
        conn.close()
        
        assert count == 5


class TestContextRetrieval:
    """Test context data retrieval."""
    
    def test_query_context_basic(self, temp_cortex_root):
        """Test basic context query."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        
        # Store context
        data = {"metric": "test", "value": 100}
        tier3.store_context("test_metric", data)
        
        # Query
        results = tier3.query_context("test_metric")
        
        assert len(results) == 1
        assert results[0]['metric'] == "test"
        assert results[0]['value'] == 100
    
    def test_query_context_with_limit(self, temp_cortex_root):
        """Test context query with limit."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        
        # Store 10 contexts
        for i in range(10):
            tier3.store_context("test_metric", {"index": i})
        
        # Query with limit
        results = tier3.query_context("test_metric", limit=5)
        
        assert len(results) == 5
    
    def test_query_context_returns_newest_first(self, temp_cortex_root):
        """Test query returns newest contexts first."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        
        # Store contexts with microsecond-precision timestamps
        for i in range(3):
            tier3.store_context("test_metric", {"index": i})
        
        results = tier3.query_context("test_metric")
        
        # Verify we have all 3 results
        assert len(results) == 3
        
        # Newest (index 2) should be first due to ISO timestamp ordering
        assert results[0]['index'] == 2
        assert results[1]['index'] == 1
        assert results[2]['index'] == 0
    
    def test_query_context_empty_database(self, temp_cortex_root):
        """Test querying non-existent database returns empty list."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="empty-workspace"
        )
        
        results = tier3.query_context("nonexistent")
        
        assert results == []


class TestWorkspaceIsolation:
    """Test workspace context isolation."""
    
    def test_different_workspaces_isolated(self, temp_cortex_root):
        """Test contexts stored in different workspaces don't mix."""
        # Workspace 1
        tier3_1 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="workspace-1"
        )
        tier3_1.store_context("test", {"workspace": 1})
        
        # Workspace 2
        tier3_2 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="workspace-2"
        )
        tier3_2.store_context("test", {"workspace": 2})
        
        # Verify isolation
        results_1 = tier3_1.query_context("test")
        results_2 = tier3_2.query_context("test")
        
        assert len(results_1) == 1
        assert len(results_2) == 1
        assert results_1[0]['workspace'] == 1
        assert results_2[0]['workspace'] == 2
    
    def test_workspace_directories_separate(self, temp_cortex_root):
        """Test different workspaces create separate directories."""
        tier3_1 = BrainTier3(cortex_root=temp_cortex_root, workspace_id="ws1")
        tier3_2 = BrainTier3(cortex_root=temp_cortex_root, workspace_id="ws2")
        
        assert tier3_1.workspace_dir != tier3_2.workspace_dir
        assert tier3_1.workspace_dir.exists()
        assert tier3_2.workspace_dir.exists()


class TestWorkspaceSummary:
    """Test workspace summary functionality."""
    
    def test_get_workspace_summary_empty(self, temp_cortex_root):
        """Test summary for empty workspace."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="empty-workspace"
        )
        
        summary = tier3.get_workspace_summary()
        
        assert summary['workspace_id'] == "empty-workspace"
        assert summary['total_records'] == 0
    
    def test_get_workspace_summary_with_data(self, temp_cortex_root):
        """Test summary with stored context."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        
        # Store some context
        for i in range(3):
            tier3.store_context("test", {"index": i})
        
        summary = tier3.get_workspace_summary()
        
        assert summary['workspace_id'] == "test-workspace"
        assert summary['databases']['context'] == 3
        assert summary['total_records'] == 3


class TestWorkspaceClearing:
    """Test workspace context clearing."""
    
    def test_clear_workspace_context_requires_confirm(self, temp_cortex_root):
        """Test clearing requires explicit confirmation."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        tier3.store_context("test", {"data": "value"})
        
        # Without confirm
        result = tier3.clear_workspace_context(confirm=False)
        assert result is False
        assert tier3.workspace_dir.exists()
    
    def test_clear_workspace_context_removes_directory(self, temp_cortex_root):
        """Test clearing removes workspace directory."""
        tier3 = BrainTier3(
            cortex_root=temp_cortex_root,
            workspace_id="test-workspace"
        )
        tier3.store_context("test", {"data": "value"})
        
        # With confirm
        result = tier3.clear_workspace_context(confirm=True)
        assert result is True
        assert not tier3.workspace_dir.exists()


class TestTier3Migration:
    """Test migration from legacy structure."""
    
    def test_needs_migration_detects_legacy(self, temp_cortex_root):
        """Test detection of legacy database."""
        # Create legacy database
        legacy_db = temp_cortex_root / "cortex-brain" / "tier3" / "context.db"
        legacy_db.touch()
        
        manager = Tier3MigrationManager(cortex_root=temp_cortex_root)
        
        assert manager.needs_migration() is True
    
    def test_needs_migration_false_when_migrated(self, temp_cortex_root):
        """Test no migration needed when already migrated."""
        # Create workspace-cortex structure (already migrated)
        workspace_dir = temp_cortex_root / "cortex-brain" / "tier3" / "workspace-cortex"
        workspace_dir.mkdir(parents=True)
        
        manager = Tier3MigrationManager(cortex_root=temp_cortex_root)
        
        assert manager.needs_migration() is False
    
    def test_migrate_dry_run(self, temp_cortex_root):
        """Test dry run migration doesn't move files."""
        # Create legacy database
        legacy_db = temp_cortex_root / "cortex-brain" / "tier3" / "context.db"
        legacy_db.touch()
        
        manager = Tier3MigrationManager(cortex_root=temp_cortex_root)
        report = manager.migrate(dry_run=True)
        
        assert report['dry_run'] is True
        assert report['success'] is True
        assert len(report['files_migrated']) > 0
        assert legacy_db.exists()  # Still there in dry run
    
    def test_migrate_moves_files(self, temp_cortex_root):
        """Test actual migration moves files."""
        # Create legacy files
        tier3_dir = temp_cortex_root / "cortex-brain" / "tier3"
        legacy_context = tier3_dir / "context.db"
        legacy_context.write_text("legacy data")
        
        legacy_yaml = tier3_dir / "token-efficiency-metrics.yaml"
        legacy_yaml.write_text("metrics: []")
        
        manager = Tier3MigrationManager(cortex_root=temp_cortex_root)
        report = manager.migrate(dry_run=False)
        
        assert report['success'] is True
        assert len(report['files_migrated']) == 2
        
        # Verify files moved
        assert not legacy_context.exists()
        assert not legacy_yaml.exists()
        
        workspace_cortex = tier3_dir / "workspace-cortex"
        assert (workspace_cortex / "context.db").exists()
        assert (workspace_cortex / "token-efficiency-metrics.yaml").exists()


class TestGlobalInstance:
    """Test global Brain Tier 3 instance."""
    
    def test_get_brain_tier3_returns_instance(self):
        """Test get_brain_tier3 returns BrainTier3 instance."""
        tier3 = get_brain_tier3(workspace_id="test-workspace")
        
        assert isinstance(tier3, BrainTier3)
        assert tier3.workspace_id == "test-workspace"
    
    def test_get_brain_tier3_with_explicit_workspace(self):
        """Test get_brain_tier3 with explicit workspace always creates new."""
        tier3_1 = get_brain_tier3(workspace_id="ws1")
        tier3_2 = get_brain_tier3(workspace_id="ws2")
        
        assert tier3_1.workspace_id == "ws1"
        assert tier3_2.workspace_id == "ws2"
        assert tier3_1 is not tier3_2
