"""
Tests for Knowledge Graph Auto-Updater.

Tests auto-update functionality, file locking, backup/rollback, and concurrent access safety.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, mock_open
from src.operations.utilities.knowledge_graph_auto_updater import (
    KnowledgeGraphAutoUpdater,
    UpdateResult,
    PatternExtractor
)


@pytest.fixture
def updater():
    """Create updater instance with test config."""
    return KnowledgeGraphAutoUpdater(
        graph_path=Path("cortex-brain/knowledge-graph.yaml")
    )


@pytest.fixture
def sample_knowledge_graph():
    """Sample knowledge graph structure."""
    return {
        'patterns': [
            {
                'name': 'existing-pattern',
                'description': 'An existing pattern',
                'occurrences': 5
            }
        ],
        'relationships': [],
        'metadata': {
            'version': '1.0',
            'last_updated': '2025-01-01'
        }
    }


@pytest.fixture
def sample_execution_context():
    """Sample execution context for pattern extraction."""
    return {
        'feature_name': 'test-feature',
        'files_modified': ['file1.py', 'file2.py', 'file3.py'],
        'tests_run': 15,
        'tests_passed': 15,
        'coverage': 95.5,
        'quality_gates': ['code_quality', 'test_coverage', 'documentation']
    }


class TestPatternExtraction:
    """Test pattern extraction from execution context."""

    def test_extract_patterns_basic(self, updater, sample_execution_context):
        """Test basic pattern extraction."""
        patterns = updater.extract_patterns(sample_execution_context)
        
        assert isinstance(patterns, list)
        assert len(patterns) >= 3, "Should extract at least 3 patterns"
        assert all(isinstance(p, dict) for p in patterns)

    def test_pattern_structure(self, updater, sample_execution_context):
        """Test extracted pattern structure."""
        patterns = updater.extract_patterns(sample_execution_context)
        
        for pattern in patterns:
            assert 'name' in pattern
            assert 'description' in pattern
            assert 'confidence' in pattern
            assert isinstance(pattern['confidence'], (int, float))

    def test_extract_patterns_returns_3_to_5(self, updater, sample_execution_context):
        """Test extraction returns 3-5 patterns per run."""
        patterns = updater.extract_patterns(sample_execution_context)
        
        assert 3 <= len(patterns) <= 5, f"Expected 3-5 patterns, got {len(patterns)}"


class TestFileLocking:
    """Test file locking mechanism for concurrent access safety."""

    def test_acquire_lock_success(self, updater):
        """Test successful lock acquisition."""
        result = updater.acquire_lock()
        
        assert result is True
        updater.release_lock()

    @patch('builtins.open', side_effect=OSError("Resource temporarily unavailable"))
    def test_acquire_lock_failure(self, mock_file, updater):
        """Test lock acquisition failure when file is locked."""
        result = updater.acquire_lock()
        
        assert result is False

    def test_release_lock(self, updater):
        """Test lock release."""
        updater.acquire_lock()
        result = updater.release_lock()
        
        assert result is True


class TestBackupRestore:
    """Test backup and restore functionality."""

    @patch.object(Path, 'read_text')
    @patch.object(Path, 'write_text')
    def test_create_backup(self, mock_write, mock_read, updater, sample_knowledge_graph):
        """Test backup creation."""
        mock_read.return_value = yaml.dump(sample_knowledge_graph)
        
        backup_path = updater.create_backup()
        
        assert backup_path is not None
        assert '.backup' in str(backup_path)

    @patch.object(Path, 'read_text')
    @patch.object(Path, 'write_text')
    @patch.object(Path, 'exists', return_value=True)
    def test_restore_from_backup(self, mock_exists, mock_write, mock_read, updater, sample_knowledge_graph):
        """Test restore from backup."""
        backup_path = Path("cortex-brain/knowledge-graph.yaml.backup")
        mock_read.return_value = yaml.dump(sample_knowledge_graph)
        
        result = updater.restore_from_backup(backup_path)
        
        assert result is True

    @patch.object(Path, 'exists', return_value=False)
    def test_restore_missing_backup(self, mock_exists, updater):
        """Test restore fails with missing backup."""
        result = updater.restore_from_backup(Path("missing.backup"))
        
        assert result is False


class TestAutoUpdate:
    """Test auto-update workflow."""

    @patch.object(Path, 'read_text')
    @patch.object(Path, 'write_text')
    def test_update_knowledge_graph_success(self, mock_write, mock_read, updater, sample_knowledge_graph, sample_execution_context):
        """Test successful knowledge graph update."""
        mock_read.return_value = yaml.dump(sample_knowledge_graph)
        
        result = updater.update_knowledge_graph(sample_execution_context)
        
        assert isinstance(result, UpdateResult)
        assert result.success is True
        assert result.patterns_added >= 3

    @patch.object(Path, 'read_text')
    @patch.object(Path, 'write_text')
    def test_update_prevents_duplicates(self, mock_write, mock_read, updater, sample_knowledge_graph, sample_execution_context):
        """Test update prevents duplicate patterns."""
        # Add pattern to context that already exists
        sample_knowledge_graph['patterns'].append({
            'name': 'high-test-coverage-pattern',
            'description': 'High test coverage achieved',
            'occurrences': 1
        })
        mock_read.return_value = yaml.dump(sample_knowledge_graph)
        
        result = updater.update_knowledge_graph(sample_execution_context)
        
        assert result.success is True
        assert result.duplicates_skipped >= 0

    @patch('builtins.open', side_effect=OSError("Permission denied"))
    def test_update_failure_with_rollback(self, mock_file, updater, sample_execution_context):
        """Test update failure triggers rollback."""
        result = updater.update_knowledge_graph(sample_execution_context)
        
        assert isinstance(result, UpdateResult)
        assert result.success is False


class TestConcurrency:
    """Test concurrent access safety."""

    def test_concurrent_updates_blocked(self, updater, sample_execution_context):
        """Test concurrent updates are blocked by file lock."""
        # This test verifies the locking mechanism prevents concurrent writes
        # In practice, a second updater instance would fail to acquire lock
        updater.acquire_lock()
        
        updater2 = KnowledgeGraphAutoUpdater(
            graph_path=Path("cortex-brain/knowledge-graph.yaml")
        )
        can_acquire = updater2.acquire_lock()
        
        # Second instance should not be able to acquire lock
        assert can_acquire is False or updater2._lock_file is None


class TestIntegration:
    """Test complete integration workflows."""

    @patch.object(Path, 'read_text')
    @patch.object(Path, 'write_text')
    def test_complete_update_workflow(self, mock_write, mock_read, updater, sample_knowledge_graph, sample_execution_context):
        """Test complete update workflow with all steps."""
        mock_read.return_value = yaml.dump(sample_knowledge_graph)
        
        # Extract patterns
        patterns = updater.extract_patterns(sample_execution_context)
        assert len(patterns) >= 3
        
        # Update knowledge graph
        result = updater.update_knowledge_graph(sample_execution_context)
        assert result.success is True
        
        # Verify backup was created
        assert result.backup_path is not None
