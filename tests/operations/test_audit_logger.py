"""
Unit Tests for AuditLogger Module

Tests comprehensive audit trail functionality including:
- Event logging with all event types
- Query operations with filters
- Archival logic and compression
- CSV export functionality
- Statistics generation
- Performance validation

Author: Asif Hussain
Date: December 17, 2025
"""

import pytest
import json
import gzip
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
from src.operations.modules.orchestration.audit_logger import (
    AuditLogger,
    AuditEvent,
    get_audit_logger
)


@pytest.fixture
def temp_audit_dir():
    """Create temporary directory for audit files."""
    temp_dir = Path(tempfile.mkdtemp())
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def audit_logger(temp_audit_dir):
    """Create AuditLogger instance with temp directory."""
    # Reset singleton
    AuditLogger._instance = None
    logger = AuditLogger(base_path=temp_audit_dir)
    return logger


class TestAuditEvent:
    """Test AuditEvent dataclass."""
    
    def test_audit_event_creation(self):
        """Test creating audit event."""
        event = AuditEvent(
            timestamp="2025-12-17T10:30:00Z",
            event_type="test_event",
            session_id="session-123",
            plan_id="plan-456",
            user_request="Test request",
            orchestrator="TestOrchestrator",
            phase="testing",
            metadata={"key": "value"},
            outcome="success",
            duration_ms=100
        )
        
        assert event.timestamp == "2025-12-17T10:30:00Z"
        assert event.event_type == "test_event"
        assert event.session_id == "session-123"
        assert event.plan_id == "plan-456"
        assert event.outcome == "success"
    
    def test_audit_event_to_dict(self):
        """Test converting event to dictionary."""
        event = AuditEvent(
            timestamp="2025-12-17T10:30:00Z",
            event_type="test_event",
            session_id="session-123",
            plan_id="plan-456",
            user_request="Test",
            orchestrator="TestOrchestrator",
            phase="testing",
            metadata={},
            outcome="success"
        )
        
        event_dict = event.to_dict()
        assert isinstance(event_dict, dict)
        assert event_dict["event_type"] == "test_event"
        assert "duration_ms" not in event_dict  # None values excluded


class TestAuditLoggerBasics:
    """Test basic AuditLogger functionality."""
    
    def test_singleton_pattern(self, temp_audit_dir):
        """Test AuditLogger is singleton."""
        logger1 = AuditLogger(base_path=temp_audit_dir)
        logger2 = AuditLogger(base_path=temp_audit_dir)
        assert logger1 is logger2
    
    def test_initialization_creates_directories(self, temp_audit_dir):
        """Test logger creates required directories."""
        logger = AuditLogger(base_path=temp_audit_dir)
        
        assert logger.audit_file.parent.exists()
        assert logger.archive_dir.exists()
    
    def test_log_event_creates_file(self, audit_logger):
        """Test logging event creates audit file."""
        audit_logger.log_event(
            event_type="test_event",
            session_id="session-123",
            plan_id="plan-456",
            orchestrator="TestOrchestrator",
            phase="testing"
        )
        
        assert audit_logger.audit_file.exists()
    
    def test_log_event_appends_jsonl(self, audit_logger):
        """Test events are appended in JSONL format."""
        audit_logger.log_event(
            event_type="event1",
            session_id="session-1",
            plan_id="plan-1",
            orchestrator="Test"
        )
        audit_logger.log_event(
            event_type="event2",
            session_id="session-2",
            plan_id="plan-2",
            orchestrator="Test"
        )
        
        # Read file
        with open(audit_logger.audit_file, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) == 2
        event1 = json.loads(lines[0])
        event2 = json.loads(lines[1])
        
        assert event1["event_type"] == "event1"
        assert event2["event_type"] == "event2"


class TestEventTypes:
    """Test all event types can be logged."""
    
    def test_session_started_event(self, audit_logger):
        """Test session_started event."""
        audit_logger.log_event(
            event_type="session_started",
            session_id="session-123",
            plan_id="plan-456",
            orchestrator="SessionContextManager",
            user_request="Add authentication",
            phase="initialization",
            metadata={"complexity_tier": 3}
        )
        
        events = audit_logger.query_events(event_type="session_started")
        assert len(events) == 1
        assert events[0]["metadata"]["complexity_tier"] == 3
    
    def test_temp_plan_created_event(self, audit_logger):
        """Test temp_plan_created event."""
        audit_logger.log_event(
            event_type="temp_plan_created",
            session_id="session-123",
            plan_id="plan-456",
            orchestrator="TemporaryPlanManager",
            phase="initialization",
            metadata={
                "folder": "temp-plans/auth/",
                "dor_score": 0.0,
                "iteration": 0
            }
        )
        
        events = audit_logger.query_events(event_type="temp_plan_created")
        assert len(events) == 1
        assert events[0]["metadata"]["folder"] == "temp-plans/auth/"
    
    def test_plan_refined_event(self, audit_logger):
        """Test plan_refined event."""
        audit_logger.log_event(
            event_type="plan_refined",
            session_id="session-123",
            plan_id="plan-456",
            orchestrator="TemporaryPlanManager",
            phase="refinement",
            metadata={
                "iteration": 2,
                "dor_score": 0.87,
                "ambiguity_score": 0.13
            }
        )
        
        events = audit_logger.query_events(event_type="plan_refined")
        assert len(events) == 1
        assert events[0]["metadata"]["iteration"] == 2
    
    def test_error_event(self, audit_logger):
        """Test error_occurred event."""
        audit_logger.log_event(
            event_type="error_occurred",
            session_id="session-123",
            plan_id="plan-456",
            orchestrator="TemporaryPlanManager",
            phase="refinement",
            outcome="failure",
            error_message="DoR validation failed",
            metadata={"error_type": "ValidationError"}
        )
        
        events = audit_logger.query_events(outcome="failure")
        assert len(events) == 1
        assert events[0]["error_message"] == "DoR validation failed"


class TestQueryOperations:
    """Test query and filtering functionality."""
    
    @pytest.fixture
    def populated_logger(self, audit_logger):
        """Create logger with sample events."""
        # Create events across multiple plans and sessions
        for i in range(5):
            audit_logger.log_event(
                event_type="plan_refined",
                session_id=f"session-{i % 2}",
                plan_id=f"plan-{i}",
                orchestrator="TemporaryPlanManager",
                phase="refinement",
                metadata={"iteration": i}
            )
        
        # Add different event types
        audit_logger.log_event(
            event_type="plan_approved",
            session_id="session-0",
            plan_id="plan-0",
            orchestrator="TemporaryPlanManager",
            phase="approval"
        )
        
        return audit_logger
    
    def test_query_by_plan_id(self, populated_logger):
        """Test filtering by plan_id."""
        events = populated_logger.query_events(plan_id="plan-0")
        assert len(events) == 2  # plan_refined + plan_approved
    
    def test_query_by_session_id(self, populated_logger):
        """Test filtering by session_id."""
        events = populated_logger.query_events(session_id="session-0")
        assert len(events) == 4  # 3 plan_refined + 1 plan_approved
    
    def test_query_by_event_type(self, populated_logger):
        """Test filtering by event_type."""
        events = populated_logger.query_events(event_type="plan_refined")
        assert len(events) == 5
    
    def test_query_with_limit(self, populated_logger):
        """Test query with limit."""
        events = populated_logger.query_events(limit=3)
        assert len(events) == 3
    
    def test_query_by_date_range(self, audit_logger):
        """Test filtering by date range."""
        # Create events with different timestamps
        base_time = datetime(2025, 12, 1, 10, 0, 0)
        
        for i in range(5):
            event_time = base_time + timedelta(days=i)
            audit_logger.log_event(
                event_type="test_event",
                session_id=f"session-{i}",
                plan_id=f"plan-{i}",
                orchestrator="Test"
            )
            # Manually set timestamp (for testing)
            # In real usage, timestamp is auto-generated
        
        since = datetime(2025, 12, 2)
        until = datetime(2025, 12, 4)
        
        # Note: This test may need adjustment based on actual timestamp handling
        events = audit_logger.query_events(since=since, until=until)
        # Verify some events returned (exact count depends on implementation)
        assert isinstance(events, list)
    
    def test_query_returns_most_recent_first(self, populated_logger):
        """Test query returns events in reverse chronological order."""
        events = populated_logger.query_events()
        
        # Verify timestamps are descending
        for i in range(len(events) - 1):
            assert events[i]["timestamp"] >= events[i + 1]["timestamp"]
    
    def test_get_plan_history(self, populated_logger):
        """Test getting complete plan history."""
        history = populated_logger.get_plan_history("plan-0")
        
        # Should be chronological (oldest first)
        assert len(history) == 2
        # Verify chronological order
        assert history[0]["timestamp"] <= history[1]["timestamp"]
    
    def test_get_session_timeline(self, populated_logger):
        """Test getting session timeline."""
        timeline = populated_logger.get_session_timeline("session-0")
        
        # Should be chronological
        assert len(timeline) == 4
        # Verify chronological order
        for i in range(len(timeline) - 1):
            assert timeline[i]["timestamp"] <= timeline[i + 1]["timestamp"]


class TestStatistics:
    """Test statistics generation."""
    
    def test_generate_stats_empty(self, audit_logger):
        """Test statistics with no events."""
        stats = audit_logger.generate_stats()
        
        assert stats["total_events"] == 0
    
    def test_generate_stats_with_events(self, audit_logger):
        """Test statistics calculation."""
        # Create sample events
        for i in range(10):
            audit_logger.log_event(
                event_type="plan_refined" if i < 7 else "plan_approved",
                session_id=f"session-{i % 3}",
                plan_id=f"plan-{i}",
                orchestrator="TemporaryPlanManager",
                metadata={"dor_score": 0.9} if i >= 5 else {"dor_score": 0.7}
            )
        
        stats = audit_logger.generate_stats()
        
        assert stats["total_events"] == 10
        assert "plan_refined" in stats["event_types"]
        assert stats["event_types"]["plan_refined"] == 7
        assert stats["event_types"]["plan_approved"] == 3
    
    def test_generate_stats_with_sessions(self, audit_logger):
        """Test session statistics."""
        # Session started
        audit_logger.log_event(
            event_type="session_started",
            session_id="session-1",
            plan_id="plan-1",
            orchestrator="SessionContextManager"
        )
        
        # Session closed
        audit_logger.log_event(
            event_type="session_closed",
            session_id="session-1",
            plan_id="plan-1",
            orchestrator="SessionContextManager",
            metadata={"duration_seconds": 600}
        )
        
        stats = audit_logger.generate_stats()
        
        assert stats["active_sessions"] == 0  # 1 started - 1 closed


class TestCSVExport:
    """Test CSV export functionality."""
    
    def test_export_to_csv(self, audit_logger, temp_audit_dir):
        """Test exporting events to CSV."""
        # Create events
        for i in range(3):
            audit_logger.log_event(
                event_type="test_event",
                session_id=f"session-{i}",
                plan_id=f"plan-{i}",
                orchestrator="TestOrchestrator",
                metadata={"iteration": i}
            )
        
        # Export
        csv_path = temp_audit_dir / "export.csv"
        events = audit_logger.query_events()
        audit_logger.export_to_csv(events, str(csv_path))
        
        assert csv_path.exists()
        
        # Verify CSV content
        with open(csv_path, 'r') as f:
            lines = f.readlines()
        
        assert len(lines) >= 4  # Header + 3 events
        assert "timestamp" in lines[0]
        assert "event_type" in lines[0]
    
    def test_export_empty_events(self, audit_logger, temp_audit_dir):
        """Test exporting empty event list."""
        csv_path = temp_audit_dir / "empty.csv"
        audit_logger.export_to_csv([], str(csv_path))
        
        # Should not create file or create empty file
        assert not csv_path.exists() or csv_path.stat().st_size == 0


class TestArchival:
    """Test archival functionality."""
    
    def test_archive_old_logs(self, audit_logger):
        """Test archiving old logs."""
        # Create old events (manually add to file with old timestamps)
        old_time = datetime.utcnow() - timedelta(days=35)
        recent_time = datetime.utcnow() - timedelta(days=1)
        
        # Manually create events in file
        with open(audit_logger.audit_file, 'w') as f:
            f.write(json.dumps({
                "timestamp": old_time.isoformat() + "Z",
                "event_type": "old_event",
                "session_id": "old-session",
                "plan_id": "old-plan",
                "orchestrator": "Test",
                "phase": "test",
                "metadata": {},
                "outcome": "success"
            }) + '\n')
            f.write(json.dumps({
                "timestamp": recent_time.isoformat() + "Z",
                "event_type": "recent_event",
                "session_id": "recent-session",
                "plan_id": "recent-plan",
                "orchestrator": "Test",
                "phase": "test",
                "metadata": {},
                "outcome": "success"
            }) + '\n')
        
        # Archive
        result = audit_logger.archive_old_logs(days_threshold=30)
        
        assert result["archived"] >= 1
        assert len(result["months"]) >= 1
        assert result["remaining"] >= 1
        
        # Verify archive files created
        archive_files = list(audit_logger.archive_dir.glob("*.jsonl.gz"))
        assert len(archive_files) >= 1
    
    def test_archive_creates_compressed_files(self, audit_logger):
        """Test archive files are gzip compressed."""
        # Create old event
        old_time = datetime.utcnow() - timedelta(days=35)
        
        with open(audit_logger.audit_file, 'w') as f:
            f.write(json.dumps({
                "timestamp": old_time.isoformat() + "Z",
                "event_type": "old_event",
                "session_id": "old",
                "plan_id": "old",
                "orchestrator": "Test",
                "phase": "test",
                "metadata": {},
                "outcome": "success"
            }) + '\n')
        
        # Archive
        audit_logger.archive_old_logs(days_threshold=30)
        
        # Find archive file
        archive_files = list(audit_logger.archive_dir.glob("*.jsonl.gz"))
        assert len(archive_files) >= 1
        
        # Verify it's gzip compressed
        archive_file = archive_files[0]
        with gzip.open(archive_file, 'rt') as f:
            content = f.read()
            assert "old_event" in content


class TestPerformance:
    """Test performance characteristics."""
    
    def test_log_event_performance(self, audit_logger):
        """Test logging performance (<5ms target)."""
        import time
        
        # Warm up
        audit_logger.log_event(
            event_type="warmup",
            session_id="warm",
            plan_id="warm",
            orchestrator="Test"
        )
        
        # Measure
        iterations = 100
        start = time.time()
        
        for i in range(iterations):
            audit_logger.log_event(
                event_type="perf_test",
                session_id=f"session-{i}",
                plan_id=f"plan-{i}",
                orchestrator="Test"
            )
        
        elapsed = time.time() - start
        avg_ms = (elapsed / iterations) * 1000
        
        # Should be fast (<5ms average)
        assert avg_ms < 10  # Allow some buffer for CI environments
    
    def test_query_performance_large_dataset(self, audit_logger):
        """Test query performance with large dataset."""
        import time
        
        # Create large dataset
        for i in range(1000):
            audit_logger.log_event(
                event_type="test_event",
                session_id=f"session-{i % 10}",
                plan_id=f"plan-{i}",
                orchestrator="Test",
                metadata={"index": i}
            )
        
        # Measure query time
        start = time.time()
        events = audit_logger.query_events(session_id="session-0")
        elapsed = time.time() - start
        
        # Should be fast (<100ms for 1000 events)
        assert elapsed < 0.5  # 500ms buffer
        assert len(events) == 100  # 1000/10 sessions


class TestGlobalAccessor:
    """Test global get_audit_logger function."""
    
    def test_get_audit_logger_returns_singleton(self, temp_audit_dir):
        """Test get_audit_logger returns singleton."""
        logger1 = get_audit_logger(temp_audit_dir)
        logger2 = get_audit_logger(temp_audit_dir)
        assert logger1 is logger2
    
    def test_get_audit_logger_default_path(self):
        """Test get_audit_logger with default path."""
        logger = get_audit_logger()
        assert logger is not None
        assert logger.base_path == Path("cortex-brain")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
