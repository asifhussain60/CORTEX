"""Tests for brain_metrics_collector.py

Test Coverage:
- Collector initialization with brain path validation
- Tier 1/2/3 metrics collection
- Brain health metrics calculation
- Memory usage metrics
- Error handling for missing databases
"""

import pytest
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.collectors.brain_metrics_collector import BrainMetricsCollector
from src.collectors.base_collector import CollectorMetric, CollectorPriority, CollectorStatus


@pytest.fixture
def mock_brain_structure(tmp_path):
    """Create mock CORTEX brain directory structure"""
    brain_path = tmp_path / "cortex-brain"
    brain_path.mkdir()
    
    # Create tier directories
    tier1 = brain_path / "tier1"
    tier2 = brain_path / "tier2"
    tier3 = brain_path / "tier3"
    
    tier1.mkdir()
    tier2.mkdir()
    tier3.mkdir()
    
    # Create mock databases
    _create_tier1_db(tier1 / "tier1-working-memory.db")
    _create_tier2_db(tier2 / "tier2-knowledge-graph.db")
    _create_tier3_db(tier3 / "tier3-development-context.db")
    
    return str(brain_path)


def _create_tier1_db(db_path):
    """Create mock Tier 1 database with test data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE conversations (
            id INTEGER PRIMARY KEY,
            active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO conversations (active) VALUES (1)")
    cursor.execute("INSERT INTO conversations (active) VALUES (1)")
    cursor.execute("INSERT INTO conversations (active) VALUES (0)")
    
    conn.commit()
    conn.close()


def _create_tier2_db(db_path):
    """Create mock Tier 2 database with test data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE patterns (
            id INTEGER PRIMARY KEY,
            confidence REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE workflows (
            id INTEGER PRIMARY KEY,
            name TEXT
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO patterns (confidence) VALUES (0.8)")
    cursor.execute("INSERT INTO patterns (confidence) VALUES (0.9)")
    cursor.execute("INSERT INTO patterns (confidence) VALUES (0.5)")
    
    cursor.execute("INSERT INTO workflows (name) VALUES ('workflow1')")
    cursor.execute("INSERT INTO workflows (name) VALUES ('workflow2')")
    
    conn.commit()
    conn.close()


def _create_tier3_db(db_path):
    """Create mock Tier 3 database with test data"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE git_commits (
            id INTEGER PRIMARY KEY,
            commit_hash TEXT
        )
    """)
    
    cursor.execute("""
        CREATE TABLE file_metrics (
            id INTEGER PRIMARY KEY,
            file_path TEXT
        )
    """)
    
    # Insert test data
    cursor.execute("INSERT INTO git_commits (commit_hash) VALUES ('abc123')")
    cursor.execute("INSERT INTO git_commits (commit_hash) VALUES ('def456')")
    
    cursor.execute("INSERT INTO file_metrics (file_path) VALUES ('/path/file1.py')")
    cursor.execute("INSERT INTO file_metrics (file_path) VALUES ('/path/file2.py')")
    cursor.execute("INSERT INTO file_metrics (file_path) VALUES ('/path/file3.py')")
    
    conn.commit()
    conn.close()


class TestBrainMetricsCollectorInitialization:
    """Tests for BrainMetricsCollector initialization"""
    
    def test_init_creates_collector(self, mock_brain_structure):
        """Test that BrainMetricsCollector initializes successfully"""
        collector = BrainMetricsCollector(mock_brain_structure)
        
        assert collector is not None
        assert collector.collector_id == "brain_metrics"
        assert collector.name == "CORTEX Brain Performance Metrics"
        assert collector.priority == CollectorPriority.CRITICAL
    
    def test_init_sets_collection_interval(self, mock_brain_structure):
        """Test that initialization sets 30 second collection interval"""
        collector = BrainMetricsCollector(mock_brain_structure)
        assert collector.collection_interval == 30.0
    
    def test_init_stores_brain_path(self, mock_brain_structure):
        """Test that brain path is stored correctly"""
        collector = BrainMetricsCollector(mock_brain_structure)
        assert collector.brain_path == Path(mock_brain_structure)
    
    def test_initialize_with_valid_brain_path(self, mock_brain_structure):
        """Test _initialize with valid brain path"""
        collector = BrainMetricsCollector(mock_brain_structure)
        result = collector._initialize()
        assert result is True
    
    def test_initialize_with_missing_brain_path(self, tmp_path):
        """Test _initialize fails with missing brain path"""
        nonexistent = str(tmp_path / "nonexistent")
        collector = BrainMetricsCollector(nonexistent)
        result = collector._initialize()
        assert result is False


class TestTier1MetricsCollection:
    """Tests for Tier 1 metrics collection"""
    
    def test_collect_tier1_active_conversations(self, mock_brain_structure):
        """Test collecting active conversation count"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier1_metrics(timestamp)
        
        # Should have metrics for active conversations
        active_conv_metrics = [m for m in metrics if m.name == "tier1_active_conversations"]
        assert len(active_conv_metrics) == 1
        assert active_conv_metrics[0].value == 2  # 2 active conversations in test data
    
    def test_collect_tier1_database_size(self, mock_brain_structure):
        """Test collecting Tier 1 database size"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier1_metrics(timestamp)
        
        # Should have database size metric
        size_metrics = [m for m in metrics if m.name == "tier1_database_size_mb"]
        assert len(size_metrics) == 1
        assert size_metrics[0].value > 0
        assert size_metrics[0].tags["unit"] == "mb"
    
    def test_collect_tier1_with_missing_database(self, tmp_path):
        """Test Tier 1 collection with missing database returns empty list"""
        brain_path = tmp_path / "brain"
        brain_path.mkdir()
        (brain_path / "tier1").mkdir()
        
        collector = BrainMetricsCollector(str(brain_path))
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier1_metrics(timestamp)
        
        assert metrics == []


class TestTier2MetricsCollection:
    """Tests for Tier 2 metrics collection"""
    
    def test_collect_tier2_high_confidence_patterns(self, mock_brain_structure):
        """Test collecting high confidence pattern count"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier2_metrics(timestamp)
        
        # Should have high confidence patterns metric
        pattern_metrics = [m for m in metrics if m.name == "tier2_high_confidence_patterns"]
        assert len(pattern_metrics) == 1
        assert pattern_metrics[0].value == 2  # 2 patterns with confidence > 0.7
        assert pattern_metrics[0].tags["confidence"] == "high"
    
    def test_collect_tier2_workflow_templates(self, mock_brain_structure):
        """Test collecting workflow template count"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier2_metrics(timestamp)
        
        # Should have workflow count metric
        workflow_metrics = [m for m in metrics if m.name == "tier2_workflow_templates"]
        assert len(workflow_metrics) == 1
        assert workflow_metrics[0].value == 2  # 2 workflows in test data
    
    def test_collect_tier2_database_size(self, mock_brain_structure):
        """Test collecting Tier 2 database size"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier2_metrics(timestamp)
        
        size_metrics = [m for m in metrics if m.name == "tier2_database_size_mb"]
        assert len(size_metrics) == 1
        assert size_metrics[0].value > 0


class TestTier3MetricsCollection:
    """Tests for Tier 3 metrics collection"""
    
    def test_collect_tier3_git_commits(self, mock_brain_structure):
        """Test collecting git commits analyzed count"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier3_metrics(timestamp)
        
        git_metrics = [m for m in metrics if m.name == "tier3_git_commits_analyzed"]
        assert len(git_metrics) == 1
        assert git_metrics[0].value == 2  # 2 commits in test data
        assert git_metrics[0].tags["type"] == "git"
    
    def test_collect_tier3_file_metrics(self, mock_brain_structure):
        """Test collecting file metrics tracked count"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier3_metrics(timestamp)
        
        file_metrics = [m for m in metrics if m.name == "tier3_file_metrics_tracked"]
        assert len(file_metrics) == 1
        assert file_metrics[0].value == 3  # 3 files in test data
    
    def test_collect_tier3_database_size(self, mock_brain_structure):
        """Test collecting Tier 3 database size"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier3_metrics(timestamp)
        
        size_metrics = [m for m in metrics if m.name == "tier3_database_size_mb"]
        assert len(size_metrics) == 1
        assert size_metrics[0].value > 0


class TestBrainHealthMetrics:
    """Tests for brain health metrics collection"""
    
    def test_collect_brain_health_score(self, mock_brain_structure):
        """Test collecting overall brain health score"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_brain_health_metrics(timestamp)
        
        health_metrics = [m for m in metrics if m.name == "brain_overall_health_score"]
        assert len(health_metrics) == 1
        assert isinstance(health_metrics[0].value, (int, float))
    
    def test_collect_agent_coordination_status(self, mock_brain_structure):
        """Test collecting agent coordination status"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_brain_health_metrics(timestamp)
        
        agent_metrics = [m for m in metrics if m.name == "brain_agent_coordination_status"]
        assert len(agent_metrics) == 1
        assert agent_metrics[0].value == "operational"
    
    def test_collect_protection_layers_active(self, mock_brain_structure):
        """Test collecting protection layers active count"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_brain_health_metrics(timestamp)
        
        protection_metrics = [m for m in metrics if m.name == "brain_protection_layers_active"]
        assert len(protection_metrics) == 1
        assert protection_metrics[0].value == 6


class TestMemoryUsageMetrics:
    """Tests for memory usage metrics collection"""
    
    @patch('psutil.Process')
    def test_collect_process_memory(self, mock_process, mock_brain_structure):
        """Test collecting process memory usage"""
        mock_memory = MagicMock()
        mock_memory.rss = 100 * 1024 * 1024  # 100 MB
        mock_process.return_value.memory_info.return_value = mock_memory
        
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_memory_usage_metrics(timestamp)
        
        memory_metrics = [m for m in metrics if m.name == "brain_process_memory_mb"]
        assert len(memory_metrics) == 1
        assert memory_metrics[0].value == 100.0
    
    def test_collect_total_storage(self, mock_brain_structure):
        """Test collecting total brain storage size"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_memory_usage_metrics(timestamp)
        
        storage_metrics = [m for m in metrics if m.name == "brain_total_storage_mb"]
        assert len(storage_metrics) == 1
        assert storage_metrics[0].value > 0


class TestFullMetricsCollection:
    """Tests for complete metrics collection workflow"""
    
    @patch('psutil.Process')
    def test_collect_returns_all_metric_types(self, mock_process, mock_brain_structure):
        """Test that collect returns metrics from all tiers"""
        mock_memory = MagicMock()
        mock_memory.rss = 100 * 1024 * 1024
        mock_process.return_value.memory_info.return_value = mock_memory
        
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        metrics = collector.collect()
        
        # Should have metrics from all sources
        assert len(metrics) > 0
        
        # Check we have tier metrics
        tier1_metrics = [m for m in metrics if "tier1" in m.name]
        tier2_metrics = [m for m in metrics if "tier2" in m.name]
        tier3_metrics = [m for m in metrics if "tier3" in m.name]
        
        assert len(tier1_metrics) > 0
        assert len(tier2_metrics) > 0
        assert len(tier3_metrics) > 0
    
    def test_collect_updates_collector_state(self, mock_brain_structure):
        """Test that collect updates collector state"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        assert collector.last_collection is None
        assert collector.metrics_collected == 0
        
        collector.collect()
        
        assert collector.last_collection is not None
        assert collector.metrics_collected > 0
    
    def test_collect_stores_recent_metrics(self, mock_brain_structure):
        """Test that collected metrics are stored in cache"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        collector.collect()
        recent = collector.get_recent_metrics()
        
        assert len(recent) > 0


class TestErrorHandling:
    """Tests for error handling in metrics collection"""
    
    def test_collect_tier1_handles_database_error(self, mock_brain_structure):
        """Test that Tier 1 collection handles database errors gracefully"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        # Corrupt the database
        tier1_db = Path(mock_brain_structure) / "tier1/tier1-working-memory.db"
        with open(tier1_db, 'w') as f:
            f.write("corrupted")
        
        timestamp = datetime.now(timezone.utc)
        metrics = collector._collect_tier1_metrics(timestamp)
        
        # Should return empty list on error, not raise exception
        assert metrics == []
    
    def test_collect_continues_after_tier_failure(self, mock_brain_structure):
        """Test that collection continues if one tier fails"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        # Remove Tier 1 database
        tier1_db = Path(mock_brain_structure) / "tier1/tier1-working-memory.db"
        tier1_db.unlink()
        
        metrics = collector.collect()
        
        # Should still collect from Tier 2 and Tier 3
        tier2_metrics = [m for m in metrics if "tier2" in m.name]
        tier3_metrics = [m for m in metrics if "tier3" in m.name]
        
        assert len(tier2_metrics) > 0
        assert len(tier3_metrics) > 0


class TestMetricTags:
    """Tests for metric tags and metadata"""
    
    def test_metrics_have_appropriate_tags(self, mock_brain_structure):
        """Test that metrics have appropriate tags"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        metrics = collector.collect()
        
        # All metrics should have tags
        for metric in metrics:
            assert isinstance(metric.tags, dict)
            assert len(metric.tags) > 0
    
    def test_tier_metrics_have_tier_tag(self, mock_brain_structure):
        """Test that tier metrics have tier tag"""
        collector = BrainMetricsCollector(mock_brain_structure)
        collector.start()
        
        timestamp = datetime.now(timezone.utc)
        tier1_metrics = collector._collect_tier1_metrics(timestamp)
        
        for metric in tier1_metrics:
            assert "tier" in metric.tags
            assert metric.tags["tier"] == "1"
