"""
Test Suite: Planning Orchestrator Checkpoint Management

Tests for Task 13.4:
- Part 1: Enhanced _create_checkpoint with history tracking (3 tests)
- Part 2: _list_checkpoints with phase filtering (3 tests)
- Part 3: Enhanced _rollback_to_checkpoint by ID (3 tests)
- Part 4: Enhanced _cleanup_old_checkpoints with retention (4 tests)

Total: 13 tests

Author: CORTEX Planning System
Version: 4.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import yaml
import tempfile
from datetime import datetime, timedelta
from typing import Dict, Any

from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def orchestrator(temp_dir):
    """Create PlanningOrchestrator instance for testing."""
    config = {
        "cortex_root": str(temp_dir),
        "schema_path": str(temp_dir / "schema.yaml"),
        "plans_dir": str(temp_dir / "plans"),
        "enable_git_checkpoints": False,  # Use memory checkpoints for testing
        "checkpoint_retention_limit": 10
    }
    
    # Create required directories
    (temp_dir / "plans" / "active").mkdir(parents=True, exist_ok=True)
    (temp_dir / "plans" / "completed").mkdir(parents=True, exist_ok=True)
    
    # Create minimal schema
    schema = {
        "name": "test-schema",
        "version": "1.0",
        "required": ["metadata", "phases"]
    }
    with open(temp_dir / "schema.yaml", "w") as f:
        yaml.safe_dump(schema, f)
    
    return PlanningOrchestrator(config)


@pytest.fixture
def orchestrator_with_checkpoints(orchestrator):
    """Create orchestrator with pre-existing checkpoints."""
    # Create checkpoints for multiple phases
    orchestrator._create_checkpoint("Requirements Analysis", {"progress": "100%"})
    orchestrator._create_checkpoint("Architecture Design", {"progress": "80%"})
    orchestrator._create_checkpoint("Implementation", {"progress": "50%"})
    orchestrator._create_checkpoint("Implementation", {"progress": "75%"})  # Second checkpoint for same phase
    orchestrator._create_checkpoint("Testing", {"progress": "30%"})
    
    return orchestrator


# ============================================================================
# Part 1: Enhanced _create_checkpoint Tests (3 tests)
# ============================================================================

class TestEnhancedCreateCheckpoint:
    """Test enhanced _create_checkpoint with history tracking."""
    
    def test_create_checkpoint_adds_to_history(self, orchestrator):
        """Test checkpoint is added to history."""
        checkpoint_id = orchestrator._create_checkpoint("Phase1", {"test": "data"})
        
        assert checkpoint_id != ""
        assert hasattr(orchestrator, "_checkpoint_history")
        assert len(orchestrator._checkpoint_history) == 1
        
        history_entry = orchestrator._checkpoint_history[0]
        assert history_entry["checkpoint_id"] == checkpoint_id
        assert history_entry["phase_name"] == "Phase1"
        assert history_entry["type"] == "memory"
        assert "timestamp" in history_entry
        assert history_entry["metadata"] == {"test": "data"}
    
    def test_create_multiple_checkpoints_tracks_all(self, orchestrator):
        """Test multiple checkpoints are all tracked in history."""
        cp1 = orchestrator._create_checkpoint("Phase1", {"step": 1})
        cp2 = orchestrator._create_checkpoint("Phase2", {"step": 2})
        cp3 = orchestrator._create_checkpoint("Phase3", {"step": 3})
        
        assert len(orchestrator._checkpoint_history) == 3
        assert orchestrator._checkpoint_history[0]["checkpoint_id"] == cp1
        assert orchestrator._checkpoint_history[1]["checkpoint_id"] == cp2
        assert orchestrator._checkpoint_history[2]["checkpoint_id"] == cp3
    
    def test_create_checkpoint_tracks_timestamp(self, orchestrator):
        """Test checkpoint timestamps are recorded."""
        before = datetime.now()
        checkpoint_id = orchestrator._create_checkpoint("PhaseTest", {})
        after = datetime.now()
        
        history_entry = orchestrator._checkpoint_history[0]
        checkpoint_time = datetime.fromisoformat(history_entry["timestamp"])
        
        assert before <= checkpoint_time <= after


# ============================================================================
# Part 2: _list_checkpoints Tests (3 tests)
# ============================================================================

class TestListCheckpoints:
    """Test _list_checkpoints with filtering."""
    
    def test_list_all_checkpoints(self, orchestrator_with_checkpoints):
        """Test listing all checkpoints without filter."""
        checkpoints = orchestrator_with_checkpoints._list_checkpoints()
        
        # Should have 5 checkpoints total
        assert len(checkpoints) == 5
        
        # Should be sorted by timestamp (newest first)
        timestamps = [cp["timestamp"] for cp in checkpoints]
        assert timestamps == sorted(timestamps, reverse=True)
    
    def test_list_checkpoints_with_phase_filter(self, orchestrator_with_checkpoints):
        """Test filtering checkpoints by phase."""
        impl_checkpoints = orchestrator_with_checkpoints._list_checkpoints(phase_filter="Implementation")
        
        # Should have 2 Implementation checkpoints
        assert len(impl_checkpoints) == 2
        assert all(cp["phase_name"] == "Implementation" for cp in impl_checkpoints)
        
        # Test other phase
        req_checkpoints = orchestrator_with_checkpoints._list_checkpoints(phase_filter="Requirements Analysis")
        assert len(req_checkpoints) == 1
        assert req_checkpoints[0]["phase_name"] == "Requirements Analysis"
    
    def test_list_checkpoints_empty_history(self, orchestrator):
        """Test listing checkpoints with no history."""
        checkpoints = orchestrator._list_checkpoints()
        
        assert checkpoints == []


# ============================================================================
# Part 3: Enhanced _rollback_to_checkpoint Tests (3 tests)
# ============================================================================

class TestEnhancedRollback:
    """Test enhanced _rollback_to_checkpoint by ID."""
    
    def test_rollback_to_valid_checkpoint(self, orchestrator_with_checkpoints):
        """Test rollback to valid checkpoint ID."""
        # Get first checkpoint ID
        checkpoints = orchestrator_with_checkpoints._list_checkpoints()
        checkpoint_id = checkpoints[0]["checkpoint_id"]
        
        # Rollback should succeed
        result = orchestrator_with_checkpoints._rollback_to_checkpoint(checkpoint_id)
        
        assert result is True
    
    def test_rollback_to_invalid_checkpoint(self, orchestrator_with_checkpoints):
        """Test rollback to non-existent checkpoint ID."""
        result = orchestrator_with_checkpoints._rollback_to_checkpoint("invalid-checkpoint-id")
        
        assert result is False
    
    def test_rollback_without_history(self, orchestrator):
        """Test rollback fails gracefully without checkpoint history."""
        result = orchestrator._rollback_to_checkpoint("some-id")
        
        assert result is False


# ============================================================================
# Part 4: Enhanced _cleanup_old_checkpoints Tests (4 tests)
# ============================================================================

class TestEnhancedCleanup:
    """Test enhanced _cleanup_old_checkpoints with retention."""
    
    def test_cleanup_removes_old_checkpoints(self, orchestrator):
        """Test cleanup removes checkpoints older than retention period."""
        # Create checkpoints with different timestamps
        now = datetime.now()
        
        # Create 2 checkpoints for same phase - one old, one newer (but still old)
        old_checkpoint_id = orchestrator._create_checkpoint("Phase1", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=15)).isoformat()
        
        # Newer checkpoint for same phase (10 days old - still beyond retention)
        older_recent_checkpoint_id = orchestrator._create_checkpoint("Phase1", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=10)).isoformat()
        
        # Recent checkpoint for different phase (2 days ago - within retention)
        recent_checkpoint_id = orchestrator._create_checkpoint("Phase2", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=2)).isoformat()
        
        # Cleanup with 7-day retention
        removed = orchestrator._cleanup_old_checkpoints(retention_days=7)
        
        # Should remove 1 old checkpoint (oldest Phase1, keeping newer Phase1 + Phase2)
        assert removed == 1
        
        # Should have 2 checkpoints remaining
        checkpoints = orchestrator._list_checkpoints()
        assert len(checkpoints) == 2
    
    def test_cleanup_preserves_most_recent_per_phase(self, orchestrator):
        """Test cleanup preserves most recent checkpoint for each phase."""
        now = datetime.now()
        
        # Create 2 old checkpoints for same phase
        cp1 = orchestrator._create_checkpoint("Phase1", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=10)).isoformat()
        
        cp2 = orchestrator._create_checkpoint("Phase1", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=9)).isoformat()
        
        # Cleanup with 7-day retention
        removed = orchestrator._cleanup_old_checkpoints(retention_days=7)
        
        # Should remove older checkpoint but keep newer one
        assert removed == 1
        
        checkpoints = orchestrator._list_checkpoints()
        assert len(checkpoints) == 1
        assert checkpoints[0]["checkpoint_id"] == cp2  # Newer checkpoint preserved
    
    def test_cleanup_with_no_old_checkpoints(self, orchestrator):
        """Test cleanup does nothing when all checkpoints are recent."""
        # Create recent checkpoint
        orchestrator._create_checkpoint("RecentPhase", {})
        
        # Cleanup with 7-day retention
        removed = orchestrator._cleanup_old_checkpoints(retention_days=7)
        
        # Should remove nothing
        assert removed == 0
        assert len(orchestrator._checkpoint_history) == 1
    
    def test_cleanup_with_empty_history(self, orchestrator):
        """Test cleanup handles empty checkpoint history."""
        removed = orchestrator._cleanup_old_checkpoints(retention_days=7)
        
        assert removed == 0


# ============================================================================
# Part 5: Integration Tests (3 bonus tests)
# ============================================================================

class TestCheckpointManagementIntegration:
    """Test integration of checkpoint management features."""
    
    def test_full_checkpoint_lifecycle(self, orchestrator):
        """Test create → list → rollback → cleanup lifecycle."""
        # Create checkpoints
        cp1 = orchestrator._create_checkpoint("Phase1", {"step": 1})
        cp2 = orchestrator._create_checkpoint("Phase2", {"step": 2})
        
        # List checkpoints
        checkpoints = orchestrator._list_checkpoints()
        assert len(checkpoints) == 2
        
        # Rollback to first checkpoint
        result = orchestrator._rollback_to_checkpoint(cp1)
        assert result is True
        
        # Cleanup (should keep both since recent)
        removed = orchestrator._cleanup_old_checkpoints(retention_days=7)
        assert removed == 0
    
    def test_checkpoint_filtering_and_cleanup(self, orchestrator):
        """Test phase filtering works with cleanup."""
        now = datetime.now()
        
        # Create old checkpoints for different phases (each phase has 1 checkpoint)
        cp1 = orchestrator._create_checkpoint("Phase1", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=10)).isoformat()
        
        cp2 = orchestrator._create_checkpoint("Phase2", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=10)).isoformat()
        
        # Create newer checkpoint for Phase1 to prevent it from being "most recent"
        cp3 = orchestrator._create_checkpoint("Phase1", {})
        orchestrator._checkpoint_history[-1]["timestamp"] = (now - timedelta(days=8)).isoformat()
        
        # Cleanup removes old checkpoints (keeps most recent per phase)
        # Should remove cp1 (older Phase1) but keep cp2 (most recent Phase2) and cp3 (most recent Phase1)
        # Since both cp2 and cp3 are beyond retention, they get removed too unless they're most recent
        removed = orchestrator._cleanup_old_checkpoints(retention_days=7)
        
        # Should remove cp1 (old Phase1), but preserve cp2 and cp3 as most recent per phase
        # Actually: cp2 is old AND most recent for Phase2, cp3 is old AND most recent for Phase1
        # Both should be preserved as "most recent per phase" even though old
        assert removed == 1  # Only cp1 removed
        
        # Check remaining checkpoints
        assert len(orchestrator._list_checkpoints()) == 2
    
    def test_checkpoint_history_tracks_types(self, orchestrator):
        """Test checkpoint history correctly tracks checkpoint types."""
        # Create memory checkpoint
        cp1 = orchestrator._create_checkpoint("MemoryPhase", {})
        
        # Check history
        checkpoints = orchestrator._list_checkpoints()
        assert len(checkpoints) == 1
        assert checkpoints[0]["type"] == "memory"
        assert checkpoints[0]["checkpoint_id"] == cp1
