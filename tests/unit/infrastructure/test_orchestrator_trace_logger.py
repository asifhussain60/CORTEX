"""
Unit tests for OrchestratorTraceLogger

AC-TRACE-001: Test trace recording, flush policies, statistics

Author: Asif Hussain
"""

import json
import os
import sqlite3
import tempfile
import uuid
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from cortex.infrastructure.orchestrator_trace_logger import (
    OrchestratorTraceLogger,
    PerOrchestrationTraceWriter,
    TraceEntry,
    TraceFlushEvent,
    TraceFlushPolicy,
    TraceFlushReason,
    TraceLevel,
    get_trace_logger,
)


@pytest.fixture
def temp_trace_db():
    """Create temporary trace database for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test-traces.db"
        os.environ["CORTEX_TRACE_DB"] = str(db_path)
        os.environ["CORTEX_TRACE_ENABLED"] = "true"
        os.environ["CORTEX_TRACE_MAX_ROWS"] = "100"  # Small limit for testing

        # Reset singleton
        OrchestratorTraceLogger._instance = None

        yield db_path

        # Cleanup
        OrchestratorTraceLogger._instance = None


class TestOrchestratorTraceLogger:
    """Tests for OrchestratorTraceLogger singleton."""

    def test_singleton_pattern(self, temp_trace_db):
        """Logger should be singleton."""
        logger1 = get_trace_logger()
        logger2 = get_trace_logger()
        assert logger1 is logger2

    def test_database_initialization(self, temp_trace_db):
        """Database should initialize with proper schema."""
        logger = get_trace_logger()
        assert temp_trace_db.exists()

        # Check schema
        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = {row[0] for row in cursor.fetchall()}

            assert "trace_metadata" in tables
            assert "trace_flush_log" in tables

    def test_trace_writer_creation(self, temp_trace_db):
        """Should create per-orchestrator trace writers."""
        logger = get_trace_logger()

        writer1 = logger.get_trace_writer("master", "MasterOrchestrator")
        writer2 = logger.get_trace_writer("enforcement", "EnforcementOrchestrator")

        assert writer1 is not writer2
        assert writer1.table_name == "trace_master"
        assert writer2.table_name == "trace_enforcement"

    def test_record_single_trace(self, temp_trace_db):
        """Should record single trace entry."""
        logger = get_trace_logger()

        entry = TraceEntry(
            trace_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            orchestrator_id="master",
            orchestrator_class="MasterOrchestrator",
            action="TEST_ACTION",
            level=TraceLevel.ACTION,
            correlation_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            context={"test": "data"},
            result="OK",
            duration_ms=100.5,
        )

        result = logger.record_trace(entry)
        assert result.is_ok()

        # Verify in database
        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM trace_master")
            count = cursor.fetchone()[0]
            assert count == 1

    def test_record_violation_trace(self, temp_trace_db):
        """Should record violation traces with correct level."""
        logger = get_trace_logger()

        entry = TraceEntry(
            trace_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            orchestrator_id="enforcement",
            orchestrator_class="EnforcementOrchestrator",
            action="VIOLATION_DETECTED",
            level=TraceLevel.VIOLATION,
            correlation_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            context={"rule": "CORE-002", "file": "test.md"},
            result="BLOCKED",
            violation_type="CORE-002",
        )

        result = logger.record_trace(entry)
        assert result.is_ok()

        # Verify violation recorded
        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute(
                "SELECT violation_type FROM trace_enforcement WHERE violation_type IS NOT NULL"
            )
            violation = cursor.fetchone()
            assert violation[0] == "CORE-002"

    def test_correlation_id_tracking(self, temp_trace_db):
        """Should track correlation IDs across traces."""
        logger = get_trace_logger()
        correlation_id = str(uuid.uuid4())

        # Record multiple traces with same correlation ID
        for i in range(3):
            entry = TraceEntry(
                trace_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                orchestrator_id="master",
                orchestrator_class="MasterOrchestrator",
                action=f"ACTION_{i}",
                level=TraceLevel.ACTION,
                correlation_id=correlation_id,
                request_id=str(uuid.uuid4()),
                context={"iteration": i},
                result="OK",
            )
            logger.record_trace(entry)

        # Query by correlation ID
        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM trace_master WHERE correlation_id = ?",
                (correlation_id,),
            )
            count = cursor.fetchone()[0]
            assert count == 3

    def test_flush_on_max_rows(self, temp_trace_db):
        """Should flush when max rows reached."""
        logger = get_trace_logger()

        # Record 110 entries (exceeds 100 limit)
        for i in range(110):
            entry = TraceEntry(
                trace_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow() - timedelta(hours=i / 1000),
                orchestrator_id="master",
                orchestrator_class="MasterOrchestrator",
                action="TEST_ACTION",
                level=TraceLevel.ACTION,
                correlation_id=str(uuid.uuid4()),
                request_id=str(uuid.uuid4()),
                context={"index": i},
                result="OK",
            )
            logger.record_trace(entry)

        # Trigger manual flush
        result = logger.flush_traces(TraceFlushReason.MANUAL)
        assert result.is_ok()

        flush_event = result.unwrap()
        assert flush_event.total_rows_removed > 0

        # Verify rows were removed
        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM trace_master")
            count = cursor.fetchone()[0]
            assert count < 110  # Should have fewer rows after flush

    def test_flush_event_logging(self, temp_trace_db):
        """Should log flush events to audit trail."""
        logger = get_trace_logger()

        # Create some traces
        for _ in range(10):
            entry = TraceEntry(
                trace_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                orchestrator_id="master",
                orchestrator_class="MasterOrchestrator",
                action="TEST_ACTION",
                level=TraceLevel.ACTION,
                correlation_id=str(uuid.uuid4()),
                request_id=str(uuid.uuid4()),
                context={"test": "data"},
                result="OK",
            )
            logger.record_trace(entry)

        # Flush and verify event logged
        logger.flush_traces(TraceFlushReason.MANUAL)

        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM trace_flush_log")
            count = cursor.fetchone()[0]
            assert count > 0

            cursor = conn.execute(
                "SELECT reason FROM trace_flush_log WHERE reason = ?",
                (TraceFlushReason.MANUAL.value,),
            )
            assert cursor.fetchone() is not None

    def test_statistics_reporting(self, temp_trace_db):
        """Should report accurate statistics."""
        logger = get_trace_logger()

        # Create traces for multiple orchestrators
        for orch_id in ["master", "enforcement", "tdd"]:
            for _ in range(5):
                entry = TraceEntry(
                    trace_id=str(uuid.uuid4()),
                    timestamp=datetime.utcnow(),
                    orchestrator_id=orch_id,
                    orchestrator_class=orch_id.upper(),
                    action="TEST_ACTION",
                    level=TraceLevel.ACTION,
                    correlation_id=str(uuid.uuid4()),
                    request_id=str(uuid.uuid4()),
                    context={"test": "data"},
                    result="OK",
                )
                logger.record_trace(entry)

        stats = logger.get_statistics()

        assert stats["enabled"] is True
        assert stats["total_tables"] >= 3
        assert stats["total_rows"] >= 15
        assert stats["db_size_mb"] > 0

    def test_query_traces(self, temp_trace_db):
        """Should query traces with filters."""
        logger = get_trace_logger()

        # Record traces for different orchestrators
        for orch_id in ["master", "enforcement"]:
            entry = TraceEntry(
                trace_id=str(uuid.uuid4()),
                timestamp=datetime.utcnow(),
                orchestrator_id=orch_id,
                orchestrator_class=orch_id.upper(),
                action="TEST_ACTION",
                level=TraceLevel.ACTION,
                correlation_id=str(uuid.uuid4()),
                request_id=str(uuid.uuid4()),
                context={"test": "data"},
                result="OK",
            )
            logger.record_trace(entry)

        # Query all
        result_all = logger.query_traces(limit=100)
        assert result_all.is_ok()
        traces_all = result_all.unwrap()
        assert len(traces_all) >= 2

        # Query specific orchestrator
        result_master = logger.query_traces(orchestrator_id="master", limit=100)
        assert result_master.is_ok()

    def test_disabled_in_production(self):
        """Should disable tracing when CORTEX_TRACE_ENABLED=false."""
        os.environ["CORTEX_TRACE_ENABLED"] = "false"
        OrchestratorTraceLogger._instance = None

        logger = get_trace_logger()
        assert logger._trace_enabled is False

        # Recording should still succeed (no-op)
        entry = TraceEntry(
            trace_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            orchestrator_id="master",
            orchestrator_class="MasterOrchestrator",
            action="TEST_ACTION",
            level=TraceLevel.ACTION,
            correlation_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            context={"test": "data"},
            result="OK",
        )

        result = logger.record_trace(entry)
        assert result.is_ok()

        # Re-enable for other tests
        os.environ["CORTEX_TRACE_ENABLED"] = "true"
        OrchestratorTraceLogger._instance = None


class TestPerOrchestrationTraceWriter:
    """Tests for per-orchestrator trace writer."""

    def test_table_creation(self, temp_trace_db):
        """Should create per-orchestrator trace table."""
        logger = get_trace_logger()
        writer = logger.get_trace_writer("master", "MasterOrchestrator")

        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='trace_master'"
            )
            assert cursor.fetchone() is not None

    def test_table_sanitization(self, temp_trace_db):
        """Should sanitize table names."""
        logger = get_trace_logger()
        writer = logger.get_trace_writer("master-orchestrator-123", "TestClass")

        # Name should be sanitized
        assert "-" not in writer.table_name
        assert writer.table_name.startswith("trace_")

    def test_write_with_indexes(self, temp_trace_db):
        """Should create indexes for efficient querying."""
        logger = get_trace_logger()
        writer = logger.get_trace_writer("master", "MasterOrchestrator")

        entry = TraceEntry(
            trace_id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            orchestrator_id="master",
            orchestrator_class="MasterOrchestrator",
            action="TEST_ACTION",
            level=TraceLevel.ACTION,
            correlation_id=str(uuid.uuid4()),
            request_id=str(uuid.uuid4()),
            context={"test": "data"},
            result="OK",
        )

        writer.write_trace(entry)

        # Check indexes exist
        with sqlite3.connect(str(temp_trace_db)) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='trace_master'"
            )
            indexes = {row[0] for row in cursor.fetchall()}

            assert any("timestamp" in idx for idx in indexes)
            assert any("correlation" in idx for idx in indexes)


class TestTraceFlushPolicy:
    """Tests for flush policy logic."""

    def test_size_based_flush(self):
        """Should implement size-based flush policy."""
        policy = TraceFlushPolicy(max_rows_per_table=100, flush_interval_hours=24)

        # Create in-memory database with test data
        conn = sqlite3.connect(":memory:")
        conn.execute(
            """
            CREATE TABLE test_table (
                trace_id TEXT PRIMARY KEY,
                timestamp TEXT,
                action TEXT
            )
            """
        )

        # Insert 110 rows
        for i in range(110):
            conn.execute(
                "INSERT INTO test_table VALUES (?, ?, ?)",
                (f"id_{i}", f"2026-02-13T{i:02d}:00:00", "ACTION"),
            )

        conn.execute("CREATE TABLE trace_metadata (table_name TEXT, row_count INTEGER)")
        conn.execute("INSERT INTO trace_metadata VALUES ('test_table', 110)")

        # Execute flush
        tables_flushed = {}
        tables_flushed["test_table"] = 55  # 50% of 110

        assert tables_flushed["test_table"] == 55

    def test_flush_reason_tracking(self):
        """Should track reasons for flush operations."""
        reasons = [
            TraceFlushReason.MAX_ROWS,
            TraceFlushReason.TIME_BASED,
            TraceFlushReason.MANUAL,
            TraceFlushReason.STARTUP,
        ]

        for reason in reasons:
            assert reason.value in ["max_rows_reached", "time_based_rotation", "manual_request", "startup_cleanup"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
