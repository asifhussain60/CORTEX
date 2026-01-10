"""
CORTEX 6.0 Stage 1 Phase 1.1 - Enhanced Audit Logger Tests

Tests for AC-AUDIT-001 through AC-AUDIT-006:
- AC-AUDIT-001: Queryable logs by AC-ID, orchestrator, date range
- AC-AUDIT-002: Memory buffer with configurable flush thresholds
- AC-AUDIT-003: Per-repo SQLite audit database isolation
- AC-AUDIT-004: MCP tools (audit_query, audit_list, audit_export)
- AC-AUDIT-005: Automatic vacuum removes old logs
- AC-AUDIT-006: Log level-based retention policy

RED PHASE: All tests will fail initially (implementation pending)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
import sqlite3
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock

# Import the enhanced AuditLogger (will fail until implementation)
from src.infrastructure.enhanced_audit_logger import (
    EnhancedAuditLogger,
    AuditStorage,
    AuditMemoryBuffer,
    AuditLevel,
    AuditCategory,
)


# ==============================================================================
# AC-AUDIT-001: Queryable Logs Tests
# ==============================================================================

@pytest.mark.ac_id
class TestAuditQueries:
    """Test queryable audit logs by various filters."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.storage = AuditStorage(self.db_path)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_query_by_ac_id(self):
        """Test: Query by ac_id returns matching entries only."""
        # Setup: Insert test entries
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="test",
            operation="test_op",
            message="Test AC-GOV-001",
            ac_id="AC-GOV-001"
        )
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="test",
            operation="test_op",
            message="Test AC-GOV-002",
            ac_id="AC-GOV-002"
        )
        
        # Execute: Query by AC-ID
        results = self.storage.query(ac_id="AC-GOV-001")
        
        # Assert: Only matching entries returned
        assert len(results) == 1
        assert results[0]["ac_id"] == "AC-GOV-001"
        assert results[0]["message"] == "Test AC-GOV-001"
    
    def test_query_by_orchestrator(self):
        """Test: Query by orchestrator returns filtered entries."""
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="planning",
            operation="execute",
            message="Planning execution"
        )
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="tdd",
            operation="execute",
            message="TDD execution"
        )
        
        results = self.storage.query(component="planning")
        
        assert len(results) == 1
        assert results[0]["component"] == "planning"
    
    def test_query_by_date_range(self):
        """Test: Query by date range filters correctly."""
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        
        # Insert entry from yesterday (simulate)
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Old entry",
            timestamp=yesterday.isoformat()
        )
        
        # Insert entry from today
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="New entry"
        )
        
        # Query for today only
        results = self.storage.query(
            start_date=now.replace(hour=0, minute=0, second=0).isoformat()
        )
        
        assert len(results) == 1
        assert "New entry" in results[0]["message"]
    
    def test_query_by_level(self):
        """Test: Query by log level returns correct entries."""
        self.storage.log(
            level=AuditLevel.ERROR,
            category=AuditCategory.VALIDATION,
            component="test",
            operation="test",
            message="Error entry"
        )
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.VALIDATION,
            component="test",
            operation="test",
            message="Info entry"
        )
        
        results = self.storage.query(level=AuditLevel.ERROR)
        
        assert len(results) == 1
        assert results[0]["level"] == AuditLevel.ERROR.value
    
    def test_combined_query(self):
        """Test: Combined queries return intersection of filters."""
        self.storage.log(
            level=AuditLevel.ERROR,
            category=AuditCategory.GOVERNANCE,
            component="planning",
            operation="validate",
            message="Planning error",
            ac_id="AC-GOV-001"
        )
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="planning",
            operation="validate",
            message="Planning info",
            ac_id="AC-GOV-001"
        )
        
        # Query: ERROR level + AC-GOV-001
        results = self.storage.query(
            level=AuditLevel.ERROR,
            ac_id="AC-GOV-001"
        )
        
        assert len(results) == 1
        assert results[0]["level"] == AuditLevel.ERROR.value
        assert results[0]["ac_id"] == "AC-GOV-001"
    
    def test_query_pagination(self):
        """Test: Results paginated (default 100, configurable)."""
        # Insert 150 entries
        for i in range(150):
            self.storage.log(
                level=AuditLevel.INFO,
                category=AuditCategory.ORCHESTRATOR,
                component="test",
                operation="test",
                message=f"Entry {i}"
            )
        
        # Query with default pagination
        results_page1 = self.storage.query(page=1, page_size=100)
        results_page2 = self.storage.query(page=2, page_size=100)
        
        assert len(results_page1) == 100
        assert len(results_page2) == 50
    
    def test_query_ordering(self):
        """Test: Results ordered by timestamp DESC by default."""
        time.sleep(0.01)  # Ensure different timestamps
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="First"
        )
        time.sleep(0.01)
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Second"
        )
        
        results = self.storage.query()
        
        assert results[0]["message"] == "Second"  # Most recent first
        assert results[1]["message"] == "First"


# ==============================================================================
# AC-AUDIT-002: Memory Buffer Tests
# ==============================================================================

@pytest.mark.ac_id
class TestMemoryBuffer:
    """Test memory buffer with configurable flush thresholds."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.buffer = AuditMemoryBuffer(
            storage_path=self.db_path,
            max_entries=10,  # Small for testing
            max_memory_mb=1,
            flush_interval_seconds=60
        )
    
    def teardown_method(self):
        """Cleanup test environment."""
        self.buffer.flush()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_buffer_size_flush(self):
        """Test: Log 11 entries triggers flush at 10."""
        flush_called = False
        original_flush = self.buffer._flush_to_storage
        
        def mock_flush():
            nonlocal flush_called
            flush_called = True
            original_flush()
        
        self.buffer._flush_to_storage = mock_flush
        
        # Log 9 entries (no flush)
        for i in range(9):
            self.buffer.log(
                level=AuditLevel.INFO,
                category=AuditCategory.ORCHESTRATOR,
                component="test",
                operation="test",
                message=f"Entry {i}"
            )
        
        assert not flush_called
        
        # Log 10th entry (triggers flush)
        self.buffer.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Entry 9"
        )
        
        assert flush_called
    
    def test_error_immediate_flush(self):
        """Test: ERROR level triggers immediate flush."""
        self.buffer.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Info 1"
        )
        
        # ERROR should flush immediately
        self.buffer.log(
            level=AuditLevel.ERROR,
            category=AuditCategory.VALIDATION,
            component="test",
            operation="test",
            message="Error occurred"
        )
        
        # Check storage has ERROR entry (flushed)
        storage = AuditStorage(self.db_path)
        results = storage.query(level=AuditLevel.ERROR)
        assert len(results) == 1
        assert results[0]["message"] == "Error occurred"
    
    def test_time_threshold_flush(self):
        """Test: Auto-flush after flush_interval_seconds."""
        buffer = AuditMemoryBuffer(
            storage_path=self.db_path,
            max_entries=1000,
            flush_interval_seconds=1  # 1 second for testing
        )
        
        buffer.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Test entry"
        )
        
        # Wait for auto-flush
        time.sleep(1.5)
        
        # Check storage has entry
        storage = AuditStorage(self.db_path)
        results = storage.query()
        assert len(results) >= 1
    
    def test_shutdown_flush(self):
        """Test: Graceful flush on shutdown."""
        self.buffer.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Pre-shutdown entry"
        )
        
        # Trigger shutdown
        self.buffer.shutdown()
        
        # Check storage has entry
        storage = AuditStorage(self.db_path)
        results = storage.query()
        assert len(results) == 1
        assert results[0]["message"] == "Pre-shutdown entry"
    
    def test_buffer_performance(self):
        """Test: <1ms per log entry (buffered)."""
        start = time.perf_counter()
        
        for i in range(100):
            self.buffer.log(
                level=AuditLevel.INFO,
                category=AuditCategory.ORCHESTRATOR,
                component="test",
                operation="test",
                message=f"Entry {i}"
            )
        
        elapsed = time.perf_counter() - start
        avg_per_entry = (elapsed / 100) * 1000  # Convert to ms
        
        assert avg_per_entry < 1.0, f"Avg {avg_per_entry:.3f}ms exceeds 1ms target"


# ==============================================================================
# AC-AUDIT-003: Per-Repo Isolation Tests
# ==============================================================================

@pytest.mark.ac_id
class TestRepoIsolation:
    """Test per-repo SQLite audit database isolation."""
    
    def setup_method(self):
        """Setup test environment with multiple repos."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_a = Path(self.temp_dir) / "repo_a"
        self.repo_b = Path(self.temp_dir) / "repo_b"
        self.repo_a.mkdir(parents=True)
        self.repo_b.mkdir(parents=True)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_repo_isolation(self):
        """Test: Repo A logs never appear in repo B database."""
        logger_a = EnhancedAuditLogger(repo_path=self.repo_a)
        logger_b = EnhancedAuditLogger(repo_path=self.repo_b)
        
        # Log to repo A
        logger_a.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Repo A entry",
            ac_id="AC-TEST-001"
        )
        logger_a.flush()  # FLUSH BUFFER
        
        # Log to repo B
        logger_b.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Repo B entry",
            ac_id="AC-TEST-002"
        )
        logger_b.flush()  # FLUSH BUFFER
        
        # Query repo A storage
        storage_a = AuditStorage(self.repo_a / "cortex-brain" / "state" / "audit.db")
        results_a = storage_a.query()
        
        # Query repo B storage
        storage_b = AuditStorage(self.repo_b / "cortex-brain" / "state" / "audit.db")
        results_b = storage_b.query()
        
        # Assert: No cross-contamination
        assert len(results_a) == 1
        assert results_a[0]["message"] == "Repo A entry"
        assert len(results_b) == 1
        assert results_b[0]["message"] == "Repo B entry"
    
    def test_context_switch(self):
        """Test: Switch repo context changes database target."""
        logger = EnhancedAuditLogger(repo_path=self.repo_a)
        
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Repo A log"
        )
        logger.flush()  # FLUSH BEFORE SWITCH
        
        # Switch context to repo B
        logger.set_repo_context(self.repo_b)
        
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Repo B log"
        )
        logger.flush()  # FLUSH AFTER SWITCH
        
        # Verify isolation
        storage_a = AuditStorage(self.repo_a / "cortex-brain" / "state" / "audit.db")
        storage_b = AuditStorage(self.repo_b / "cortex-brain" / "state" / "audit.db")
        
        results_a = storage_a.query()
        results_b = storage_b.query()
        
        assert len(results_a) == 1
        assert "Repo A log" in results_a[0]["message"]
        assert len(results_b) == 1
        assert "Repo B log" in results_b[0]["message"]
    
    def test_path_convention(self):
        """Test: Database at {repo_path}/cortex-brain/state/audit.db."""
        logger = EnhancedAuditLogger(repo_path=self.repo_a)
        
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Test"
        )
        
        expected_path = self.repo_a / "cortex-brain" / "state" / "audit.db"
        assert expected_path.exists()


# ==============================================================================
# AC-AUDIT-004: MCP Tools Tests
# ==============================================================================

@pytest.mark.ac_id
class TestMCPTools:
    """Test MCP audit tools (audit_query, audit_list, audit_export)."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.storage = AuditStorage(self.db_path)
        
        # Insert test data
        for i in range(5):
            self.storage.log(
                level=AuditLevel.INFO,
                category=AuditCategory.ORCHESTRATOR,
                component="test",
                operation="test",
                message=f"Test entry {i}",
                ac_id=f"AC-TEST-{i:03d}"
            )
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_audit_query_tool(self):
        """Test: MCP call to audit_query returns filtered results."""
        from src.mcp.audit_tools import audit_query
        
        result = audit_query(
            db_path=str(self.db_path),
            filters={"ac_id": "AC-TEST-001"}
        )
        
        assert result["success"] is True
        assert len(result["entries"]) == 1
        assert result["entries"][0]["ac_id"] == "AC-TEST-001"
    
    def test_audit_list_tool(self):
        """Test: audit_list provides paginated view."""
        from src.mcp.audit_tools import audit_list
        
        result = audit_list(
            db_path=str(self.db_path),
            page=1,
            page_size=3
        )
        
        assert result["success"] is True
        assert len(result["entries"]) == 3
        assert result["total_count"] == 5
        assert result["page"] == 1
        assert result["page_size"] == 3
    
    def test_audit_export_csv(self):
        """Test: audit_export to csv generates valid CSV file."""
        from src.mcp.audit_tools import audit_export
        
        output_path = Path(self.temp_dir) / "export.csv"
        result = audit_export(
            db_path=str(self.db_path),
            output_path=str(output_path),
            format="csv"
        )
        
        assert result["success"] is True
        assert output_path.exists()
        
        # Verify CSV content
        import csv
        with open(output_path, 'r') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
            assert len(rows) == 5
    
    def test_audit_export_jsonl(self):
        """Test: audit_export to jsonl generates valid JSONL file."""
        from src.mcp.audit_tools import audit_export
        
        output_path = Path(self.temp_dir) / "export.jsonl"
        result = audit_export(
            db_path=str(self.db_path),
            output_path=str(output_path),
            format="jsonl"
        )
        
        assert result["success"] is True
        assert output_path.exists()
        
        # Verify JSONL content
        with open(output_path, 'r') as f:
            lines = f.readlines()
            assert len(lines) == 5
            first_entry = json.loads(lines[0])
            assert "ac_id" in first_entry


# ==============================================================================
# AC-AUDIT-005: Automatic Vacuum Tests
# ==============================================================================

@pytest.mark.ac_id
class TestAutomaticVacuum:
    """Test automatic vacuum removes old logs."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_audit.db"
        self.storage = AuditStorage(self.db_path)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_vacuum_deletes_expired(self):
        """Test: 31-day-old INFO log deleted by vacuum."""
        now = datetime.now()
        old_date = now - timedelta(days=31)
        
        # Insert old INFO entry
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Old INFO entry",
            timestamp=old_date.isoformat()
        )
        
        # Insert recent entry
        self.storage.log(
            level=AuditLevel.INFO,
            category=AuditCategory.ORCHESTRATOR,
            component="test",
            operation="test",
            message="Recent INFO entry"
        )
        
        # Run vacuum with INFO retention=30 days
        from src.infrastructure.audit_vacuum import AuditVacuum
        vacuum = AuditVacuum(self.storage)
        result = vacuum.run(retention_policy={"INFO": 30})
        
        # Verify old entry deleted, recent preserved
        results = self.storage.query()
        assert len(results) == 1
        assert "Recent INFO entry" in results[0]["message"]
        assert result["deleted_count"] == 1
    
    def test_vacuum_preserves_errors(self):
        """Test: 89-day-old ERROR log preserved by vacuum."""
        now = datetime.now()
        old_date = now - timedelta(days=89)
        
        # Insert 89-day-old ERROR entry
        self.storage.log(
            level=AuditLevel.ERROR,
            category=AuditCategory.VALIDATION,
            component="test",
            operation="test",
            message="Old ERROR entry",
            timestamp=old_date.isoformat()
        )
        
        # Run vacuum with ERROR retention=90 days
        from src.infrastructure.audit_vacuum import AuditVacuum
        vacuum = AuditVacuum(self.storage)
        result = vacuum.run(retention_policy={"ERROR": 90})
        
        # Verify ERROR preserved
        results = self.storage.query(level=AuditLevel.ERROR)
        assert len(results) == 1
        assert result["deleted_count"] == 0
    
    def test_vacuum_space_reporting(self):
        """Test: Vacuum reports space reclaimed."""
        # Insert and delete entries to create fragmentation
        for i in range(100):
            self.storage.log(
                level=AuditLevel.INFO,
                category=AuditCategory.ORCHESTRATOR,
                component="test",
                operation="test",
                message=f"Entry {i}",
                timestamp=(datetime.now() - timedelta(days=60)).isoformat()
            )
        
        # Get size before vacuum
        size_before = self.db_path.stat().st_size
        
        # Run vacuum
        from src.infrastructure.audit_vacuum import AuditVacuum
        vacuum = AuditVacuum(self.storage)
        result = vacuum.run(retention_policy={"INFO": 30})
        
        # Verify space reporting
        assert "space_reclaimed_bytes" in result
        assert result["space_reclaimed_bytes"] > 0


# ==============================================================================
# AC-AUDIT-006: Retention Policy Tests
# ==============================================================================

@pytest.mark.ac_id
class TestRetentionPolicy:
    """Test log level-based retention policy."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_path = Path(self.temp_dir) / "audit-config.yaml"
        
        # Create config with retention policy
        import yaml
        config = {
            "retention_policy": {
                "ERROR": 90,
                "WARNING": 60,
                "INFO": 30,
                "DEBUG": 7
            }
        }
        with open(self.config_path, 'w') as f:
            yaml.dump(config, f)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_retention_levels(self):
        """Test: Each level has correct retention period."""
        from src.infrastructure.audit_config import load_retention_policy
        
        policy = load_retention_policy(self.config_path)
        
        assert policy["ERROR"] == 90
        assert policy["WARNING"] == 60
        assert policy["INFO"] == 30
        assert policy["DEBUG"] == 7
    
    def test_per_repo_override(self):
        """Test: Per-repo overrides supported."""
        # Create repo-specific config
        repo_config_path = Path(self.temp_dir) / "repo-audit-config.yaml"
        import yaml
        repo_config = {
            "retention_policy": {
                "ERROR": 180,  # Override: 180 instead of 90
                "INFO": 60     # Override: 60 instead of 30
            }
        }
        with open(repo_config_path, 'w') as f:
            yaml.dump(repo_config, f)
        
        from src.infrastructure.audit_config import load_retention_policy
        
        # Load with override
        policy = load_retention_policy(
            self.config_path,
            override_path=repo_config_path
        )
        
        assert policy["ERROR"] == 180  # Overridden
        assert policy["INFO"] == 60    # Overridden
        assert policy["WARNING"] == 60 # Default (not overridden)
        assert policy["DEBUG"] == 7    # Default (not overridden)


# ==============================================================================
# Integration Tests
# ==============================================================================

@pytest.mark.ac_id
class TestAuditLoggerIntegration:
    """Integration tests for enhanced audit logger."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.repo_path = Path(self.temp_dir) / "test_repo"
        self.repo_path.mkdir(parents=True)
    
    def teardown_method(self):
        """Cleanup test environment."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_end_to_end_workflow(self):
        """Test: Complete workflow from log to query."""
        logger = EnhancedAuditLogger(repo_path=self.repo_path)
        
        # Log entries
        logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.GOVERNANCE,
            component="planning",
            operation="validate",
            message="Planning validation passed",
            ac_id="AC-GOV-001"
        )
        
        logger.log(
            level=AuditLevel.ERROR,
            category=AuditCategory.VALIDATION,
            component="tdd",
            operation="execute",
            message="Test failed",
            ac_id="AC-TDD-001"
        )
        
        # Flush buffer
        logger.flush()
        
        # Query logs
        storage = AuditStorage(
            self.repo_path / "cortex-brain" / "state" / "audit.db"
        )
        
        all_entries = storage.query()
        assert len(all_entries) == 2
        
        gov_entries = storage.query(ac_id="AC-GOV-001")
        assert len(gov_entries) == 1
        
        error_entries = storage.query(level=AuditLevel.ERROR)
        assert len(error_entries) == 1
    
    def test_latency_target(self):
        """Test: <5ms latency target (AC-AUDIT-002 performance)."""
        logger = EnhancedAuditLogger(repo_path=self.repo_path)
        
        latencies = []
        for i in range(100):
            start = time.perf_counter()
            logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.ORCHESTRATOR,
                component="test",
                operation="perf_test",
                message=f"Perf test {i}",
                ac_id=f"AC-PERF-{i:03d}"
            )
            elapsed = (time.perf_counter() - start) * 1000  # Convert to ms
            latencies.append(elapsed)
        
        avg_latency = sum(latencies) / len(latencies)
        p95_latency = sorted(latencies)[95]
        
        assert avg_latency < 5.0, f"Avg latency {avg_latency:.2f}ms exceeds 5ms"
        assert p95_latency < 10.0, f"P95 latency {p95_latency:.2f}ms exceeds 10ms"
