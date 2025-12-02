"""
Phase 7.3 Tests: Brain Initialization System

Tests for:
- Brain initialization orchestrator (first-run setup)
- Brain health monitoring (health dashboard)
- Schema version tracking (migration support)

TDD Phase: RED (tests written first, expected to fail)

Author: Asif Hussain
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
import json


class TestBrainInitOrchestrator:
    """Test brain initialization and first-run setup"""
    
    @pytest.fixture
    def temp_brain_path(self):
        """Create temporary brain directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_orchestrator_exists(self):
        """Test that BrainInitOrchestrator exists"""
        from src.orchestrators import brain_init_orchestrator
        assert brain_init_orchestrator is not None
    
    def test_detect_first_run(self, temp_brain_path):
        """Test detecting first-run vs existing installation"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        
        # Should detect first run (no databases exist)
        assert orchestrator.is_first_run() is True
        
        # Create tier1 database
        tier1_db = temp_brain_path / "tier1" / "working_memory.db"
        tier1_db.parent.mkdir(parents=True, exist_ok=True)
        tier1_db.touch()
        
        # Should no longer be first run
        assert orchestrator.is_first_run() is False
    
    def test_initialize_brain_structure(self, temp_brain_path):
        """Test initializing complete brain directory structure"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        
        result = orchestrator.initialize_brain()
        
        assert result['success'] is True
        
        # Verify tier directories created
        assert (temp_brain_path / "tier1").exists()
        assert (temp_brain_path / "tier2").exists()
        assert (temp_brain_path / "tier3").exists()
        
        # Verify databases created
        assert (temp_brain_path / "tier1" / "working_memory.db").exists()
        assert (temp_brain_path / "tier2" / "knowledge_graph.db").exists()
        assert (temp_brain_path / "tier3" / "development_context.db").exists()
    
    def test_setup_tier1_database(self, temp_brain_path):
        """Test setting up Tier 1 (working memory) database"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        
        result = orchestrator.setup_tier1()
        
        assert result['success'] is True
        assert result['tables_created'] > 0
        
        # Verify schema applied
        db_path = temp_brain_path / "tier1" / "working_memory.db"
        assert db_path.exists()
        
        # Check for expected tables
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'conversations' in tables
        assert 'entities' in tables
        assert 'metadata' in tables
    
    def test_setup_tier2_database(self, temp_brain_path):
        """Test setting up Tier 2 (knowledge graph) database"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        
        result = orchestrator.setup_tier2()
        
        assert result['success'] is True
        assert result['tables_created'] > 0
        
        # Verify schema applied
        db_path = temp_brain_path / "tier2" / "knowledge_graph.db"
        assert db_path.exists()
        
        # Check for expected tables
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'patterns' in tables
        assert 'relationships' in tables
        assert 'pattern_fts' in tables  # FTS5 virtual table
    
    def test_setup_tier3_database(self, temp_brain_path):
        """Test setting up Tier 3 (development context) database"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        
        result = orchestrator.setup_tier3()
        
        assert result['success'] is True
        assert result['tables_created'] > 0
        
        # Verify schema applied
        db_path = temp_brain_path / "tier3" / "development_context.db"
        assert db_path.exists()
        
        # Check for expected tables
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        assert 'code_metrics' in tables
        assert 'git_activity' in tables
        assert 'project_insights' in tables
    
    def test_verify_schema_versions(self, temp_brain_path):
        """Test verifying all tier schemas are at correct version"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        orchestrator.initialize_brain()
        
        versions = orchestrator.get_schema_versions()
        
        assert 'tier1' in versions
        assert 'tier2' in versions
        assert 'tier3' in versions
        
        # All should have valid version numbers
        assert versions['tier1'] > 0
        assert versions['tier2'] > 0
        assert versions['tier3'] > 0
    
    def test_repair_missing_tables(self, temp_brain_path):
        """Test auto-repair of missing database tables"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        orchestrator.initialize_brain()
        
        # Delete a table to simulate corruption
        db_path = temp_brain_path / "tier1" / "working_memory.db"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("DROP TABLE IF EXISTS entities")
        conn.commit()
        conn.close()
        
        # Run repair
        result = orchestrator.repair_brain()
        
        assert result['success'] is True
        assert result['repairs_made'] > 0
        
        # Verify table restored
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
        tables = cursor.fetchall()
        conn.close()
        
        assert len(tables) == 1
    
    def test_initialization_idempotency(self, temp_brain_path):
        """Test that running initialization twice doesn't break anything"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        orchestrator = BrainInitOrchestrator(brain_path=str(temp_brain_path))
        
        # Initialize twice
        result1 = orchestrator.initialize_brain()
        result2 = orchestrator.initialize_brain()
        
        assert result1['success'] is True
        assert result2['success'] is True
        
        # Second run should detect existing setup
        assert result2.get('already_initialized', False) is True


class TestBrainHealthMonitor:
    """Test brain health monitoring and diagnostics"""
    
    @pytest.fixture
    def initialized_brain(self, tmp_path):
        """Create initialized brain for testing"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        brain_path = tmp_path / "cortex-brain"
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        orchestrator.initialize_brain()
        
        return brain_path
    
    def test_health_monitor_exists(self):
        """Test that BrainHealthMonitor exists"""
        from src.tier0 import brain_health_monitor
        assert brain_health_monitor is not None
    
    def test_check_overall_brain_health(self, initialized_brain):
        """Test overall brain health check"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        health = monitor.check_health()
        
        assert 'status' in health
        assert health['status'] in ['healthy', 'degraded', 'critical']
        assert 'tier1' in health
        assert 'tier2' in health
        assert 'tier3' in health
    
    def test_check_tier1_health(self, initialized_brain):
        """Test Tier 1 specific health checks"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        tier1_health = monitor.check_tier1()
        
        assert 'database_exists' in tier1_health
        assert tier1_health['database_exists'] is True
        assert 'schema_version' in tier1_health
        assert 'conversation_count' in tier1_health
        assert 'size_mb' in tier1_health
    
    def test_check_tier2_health(self, initialized_brain):
        """Test Tier 2 specific health checks"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        tier2_health = monitor.check_tier2()
        
        assert 'database_exists' in tier2_health
        assert tier2_health['database_exists'] is True
        assert 'pattern_count' in tier2_health
        assert 'relationship_count' in tier2_health
        assert 'fts5_enabled' in tier2_health
    
    def test_check_tier3_health(self, initialized_brain):
        """Test Tier 3 specific health checks"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        tier3_health = monitor.check_tier3()
        
        assert 'database_exists' in tier3_health
        assert tier3_health['database_exists'] is True
        assert 'metrics_count' in tier3_health
        assert 'git_activity_tracked' in tier3_health
    
    def test_detect_corruption(self, initialized_brain):
        """Test detecting database corruption"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        # Corrupt a database file
        db_path = initialized_brain / "tier1" / "working_memory.db"
        with open(db_path, 'wb') as f:
            f.write(b'CORRUPTED DATA')
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        health = monitor.check_health()
        
        assert health['status'] == 'critical'
        assert health['tier1']['corrupted'] is True
    
    def test_generate_health_report(self, initialized_brain):
        """Test generating human-readable health report"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        report = monitor.generate_report()
        
        assert isinstance(report, str)
        assert len(report) > 0
        assert 'Brain Health Report' in report
        assert 'Tier 1' in report
        assert 'Tier 2' in report
        assert 'Tier 3' in report
    
    def test_health_dashboard_cli(self, initialized_brain, capsys):
        """Test CLI health dashboard output"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        monitor.display_dashboard()
        
        captured = capsys.readouterr()
        
        assert 'Brain Health Dashboard' in captured.out
        assert '✓' in captured.out or '✅' in captured.out  # Success indicators
    
    def test_performance_metrics(self, initialized_brain):
        """Test collecting performance metrics"""
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        monitor = BrainHealthMonitor(brain_path=str(initialized_brain))
        
        metrics = monitor.get_performance_metrics()
        
        assert 'query_performance' in metrics
        assert 'tier1_avg_query_ms' in metrics
        assert 'tier2_avg_query_ms' in metrics
        assert 'tier3_avg_query_ms' in metrics
        
        # All should be under 100ms threshold
        assert metrics['tier1_avg_query_ms'] < 100
        assert metrics['tier2_avg_query_ms'] < 100
        assert metrics['tier3_avg_query_ms'] < 100


class TestSchemaVersionTracker:
    """Test schema version tracking and migrations"""
    
    @pytest.fixture
    def initialized_brain(self, tmp_path):
        """Create initialized brain for testing"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        
        brain_path = tmp_path / "cortex-brain"
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        orchestrator.initialize_brain()
        
        return brain_path
    
    def test_version_tracker_exists(self):
        """Test that SchemaVersionTracker exists"""
        from src.tier0 import schema_version_tracker
        assert schema_version_tracker is not None
    
    def test_get_current_version(self, initialized_brain):
        """Test getting current schema version for each tier"""
        from src.tier0.schema_version_tracker import SchemaVersionTracker
        
        tracker = SchemaVersionTracker(brain_path=str(initialized_brain))
        
        tier1_version = tracker.get_version('tier1')
        tier2_version = tracker.get_version('tier2')
        tier3_version = tracker.get_version('tier3')
        
        assert tier1_version > 0
        assert tier2_version > 0
        assert tier3_version > 0
    
    def test_version_storage(self, initialized_brain):
        """Test that versions are stored in Tier 1 metadata"""
        from src.tier0.schema_version_tracker import SchemaVersionTracker
        
        tracker = SchemaVersionTracker(brain_path=str(initialized_brain))
        
        # Set a version
        tracker.set_version('tier1', 5)
        
        # Retrieve it
        version = tracker.get_version('tier1')
        assert version == 5
    
    def test_needs_migration(self, initialized_brain):
        """Test detecting when migration is needed"""
        from src.tier0.schema_version_tracker import SchemaVersionTracker
        
        tracker = SchemaVersionTracker(brain_path=str(initialized_brain))
        
        # Set current version to 1
        tracker.set_version('tier2', 1)
        
        # Check if migration needed to version 2
        needs_migration = tracker.needs_migration('tier2', target_version=2)
        
        assert needs_migration is True
        
        # Update to version 2
        tracker.set_version('tier2', 2)
        
        # Should no longer need migration
        needs_migration = tracker.needs_migration('tier2', target_version=2)
        assert needs_migration is False
    
    def test_version_history(self, initialized_brain):
        """Test tracking version history"""
        from src.tier0.schema_version_tracker import SchemaVersionTracker
        
        tracker = SchemaVersionTracker(brain_path=str(initialized_brain))
        
        # Record some version changes
        tracker.set_version('tier1', 1)
        tracker.set_version('tier1', 2)
        tracker.set_version('tier1', 3)
        
        history = tracker.get_version_history('tier1')
        
        assert len(history) >= 3
        
        # History should have timestamps
        for entry in history:
            assert 'version' in entry
            assert 'timestamp' in entry
    
    def test_migration_tracking(self, initialized_brain):
        """Test tracking applied migrations"""
        from src.tier0.schema_version_tracker import SchemaVersionTracker
        
        tracker = SchemaVersionTracker(brain_path=str(initialized_brain))
        
        # Record a migration
        tracker.record_migration(
            tier='tier2',
            from_version=1,
            to_version=2,
            description='Add pattern_fts table'
        )
        
        migrations = tracker.get_applied_migrations('tier2')
        
        assert len(migrations) > 0
        assert migrations[-1]['from_version'] == 1
        assert migrations[-1]['to_version'] == 2
    
    def test_get_latest_versions(self, initialized_brain):
        """Test getting latest available schema versions"""
        from src.tier0.schema_version_tracker import SchemaVersionTracker
        
        tracker = SchemaVersionTracker(brain_path=str(initialized_brain))
        
        latest = tracker.get_latest_versions()
        
        assert 'tier1' in latest
        assert 'tier2' in latest
        assert 'tier3' in latest
        
        # Latest versions should match defined schema versions
        assert latest['tier1'] > 0
        assert latest['tier2'] > 0
        assert latest['tier3'] > 0


class TestIntegration:
    """Integration tests for complete brain initialization flow"""
    
    def test_complete_initialization_flow(self, tmp_path):
        """Test complete brain initialization from scratch"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        from src.tier0.schema_version_tracker import SchemaVersionTracker
        
        brain_path = tmp_path / "cortex-brain"
        
        # Initialize brain
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        assert orchestrator.is_first_run() is True
        
        result = orchestrator.initialize_brain()
        assert result['success'] is True
        
        # Verify health
        monitor = BrainHealthMonitor(brain_path=str(brain_path))
        health = monitor.check_health()
        assert health['status'] == 'healthy'
        
        # Verify versions
        tracker = SchemaVersionTracker(brain_path=str(brain_path))
        versions = tracker.get_latest_versions()
        assert all(v > 0 for v in versions.values())
    
    def test_repair_and_recovery_flow(self, tmp_path):
        """Test repair flow when corruption detected"""
        from src.orchestrators.brain_init_orchestrator import BrainInitOrchestrator
        from src.tier0.brain_health_monitor import BrainHealthMonitor
        
        brain_path = tmp_path / "cortex-brain"
        
        # Initialize brain
        orchestrator = BrainInitOrchestrator(brain_path=str(brain_path))
        orchestrator.initialize_brain()
        
        # Simulate corruption
        db_path = brain_path / "tier2" / "knowledge_graph.db"
        import sqlite3
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        cursor.execute("DROP TABLE patterns")
        conn.commit()
        conn.close()
        
        # Detect corruption
        monitor = BrainHealthMonitor(brain_path=str(brain_path))
        health = monitor.check_health()
        assert health['status'] != 'healthy'
        
        # Repair
        result = orchestrator.repair_brain()
        assert result['success'] is True
        
        # Verify recovery
        health = monitor.check_health()
        assert health['status'] == 'healthy'
