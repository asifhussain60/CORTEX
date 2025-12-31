"""
Tests for Audit Logger (Phase 6).

TDD Phase: RED - All tests should fail initially.

Tests cover:
- Audit event logging
- Tamper-evident log format
- Event types and filtering
- Log rotation and retention
- Sensitive data masking
"""

import json
import pytest
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for test files."""
    return tmp_path


@pytest.fixture
def audit_logger(temp_dir):
    """Create AuditLogger instance."""
    from core.audit_logger import AuditLogger
    
    log_path = temp_dir / "audit.jsonl"
    return AuditLogger(log_path=log_path)


@pytest.fixture
def sample_execution_event():
    """Sample execution event for testing."""
    from core.audit_logger import ExecutionEvent
    
    return ExecutionEvent(
        tool="align",
        args=["--check-only", "--verbose"],
        status="success",
        exit_code=0,
        duration_ms=150,
        checkpoint_id="cp-123"
    )


# =============================================================================
# Test AuditLogger Initialization
# =============================================================================

class TestAuditLoggerInit:
    """Tests for AuditLogger initialization."""
    
    def test_init_creates_log_directory(self, temp_dir):
        """Should create log directory if it doesn't exist."""
        from core.audit_logger import AuditLogger
        
        log_path = temp_dir / "logs" / "audit.jsonl"
        logger = AuditLogger(log_path=log_path)
        
        assert log_path.parent.exists()
    
    def test_init_with_default_path(self, temp_dir):
        """Should use default path if not specified."""
        from core.audit_logger import AuditLogger
        
        logger = AuditLogger(toolkit_root=temp_dir)
        
        assert logger.log_path is not None
        assert "audit" in str(logger.log_path)
    
    def test_init_preserves_existing_log(self, temp_dir):
        """Should not overwrite existing log file."""
        from core.audit_logger import AuditLogger
        
        log_path = temp_dir / "audit.jsonl"
        log_path.write_text('{"existing": "entry"}\n')
        
        logger = AuditLogger(log_path=log_path)
        
        content = log_path.read_text()
        assert '{"existing": "entry"}' in content


# =============================================================================
# Test Event Logging
# =============================================================================

class TestEventLogging:
    """Tests for logging execution events."""
    
    def test_log_execution_event(self, audit_logger, sample_execution_event):
        """Should log execution event to file."""
        audit_logger.log_execution(sample_execution_event)
        
        content = audit_logger.log_path.read_text()
        assert "align" in content
        assert "success" in content
    
    def test_log_includes_timestamp(self, audit_logger, sample_execution_event):
        """Should include ISO timestamp in log."""
        audit_logger.log_execution(sample_execution_event)
        
        content = audit_logger.log_path.read_text()
        record = json.loads(content.strip())
        
        assert "timestamp" in record
        # Should be ISO format
        datetime.fromisoformat(record["timestamp"])
    
    def test_log_includes_user(self, audit_logger, sample_execution_event):
        """Should include current user in log."""
        audit_logger.log_execution(sample_execution_event)
        
        content = audit_logger.log_path.read_text()
        record = json.loads(content.strip())
        
        assert "user" in record
        assert len(record["user"]) > 0
    
    def test_log_includes_hostname(self, audit_logger, sample_execution_event):
        """Should include hostname in log."""
        audit_logger.log_execution(sample_execution_event)
        
        content = audit_logger.log_path.read_text()
        record = json.loads(content.strip())
        
        assert "hostname" in record
    
    def test_log_hashes_arguments(self, audit_logger, sample_execution_event):
        """Should hash arguments instead of logging raw values."""
        audit_logger.log_execution(sample_execution_event)
        
        content = audit_logger.log_path.read_text()
        record = json.loads(content.strip())
        
        # Should have args_hash, not raw args
        assert "args_hash" in record
        # Raw args should not appear
        assert "--check-only" not in content or "args" not in record
    
    def test_log_multiple_events(self, audit_logger, sample_execution_event):
        """Should append multiple events correctly."""
        from core.audit_logger import ExecutionEvent
        
        event1 = sample_execution_event
        event2 = ExecutionEvent(
            tool="cleanup",
            args=["--dry-run"],
            status="failed",
            exit_code=1,
            duration_ms=500
        )
        
        audit_logger.log_execution(event1)
        audit_logger.log_execution(event2)
        
        lines = audit_logger.log_path.read_text().strip().split('\n')
        assert len(lines) == 2
        
        # Both should be valid JSON
        record1 = json.loads(lines[0])
        record2 = json.loads(lines[1])
        
        assert record1["tool"] == "align"
        assert record2["tool"] == "cleanup"


# =============================================================================
# Test Security Events
# =============================================================================

class TestSecurityEvents:
    """Tests for logging security-related events."""
    
    def test_log_security_violation(self, audit_logger):
        """Should log security violations."""
        from core.audit_logger import SecurityEvent
        
        event = SecurityEvent(
            event_type="security_violation",
            tool="cleanup",
            violation_type="shell_injection",
            severity="critical",
            blocked=True
        )
        
        audit_logger.log_security(event)
        
        content = audit_logger.log_path.read_text()
        record = json.loads(content.strip())
        
        assert record["event_type"] == "security_violation"
        assert record["severity"] == "critical"
        assert record["blocked"] is True
    
    def test_log_privilege_escalation_attempt(self, audit_logger):
        """Should log privilege escalation attempts."""
        from core.audit_logger import SecurityEvent
        
        event = SecurityEvent(
            event_type="privilege_escalation",
            tool="deploy",
            required_level="admin",
            current_level="user",
            blocked=True
        )
        
        audit_logger.log_security(event)
        
        content = audit_logger.log_path.read_text()
        assert "privilege_escalation" in content


# =============================================================================
# Test Tamper Evidence
# =============================================================================

class TestTamperEvidence:
    """Tests for tamper-evident log features."""
    
    def test_append_only_mode(self, temp_dir):
        """Log should be append-only."""
        from core.audit_logger import AuditLogger, ExecutionEvent
        
        log_path = temp_dir / "audit.jsonl"
        logger = AuditLogger(log_path=log_path)
        
        # Log first event
        event1 = ExecutionEvent(tool="align", args=[], status="success", 
                               exit_code=0, duration_ms=100)
        logger.log_execution(event1)
        
        # Log second event
        event2 = ExecutionEvent(tool="cleanup", args=[], status="success",
                               exit_code=0, duration_ms=200)
        logger.log_execution(event2)
        
        # Both events should be present
        lines = log_path.read_text().strip().split('\n')
        assert len(lines) == 2
    
    def test_includes_sequence_number(self, audit_logger, sample_execution_event):
        """Each log entry should have a sequence number."""
        from core.audit_logger import ExecutionEvent
        
        event1 = sample_execution_event
        event2 = ExecutionEvent(tool="cleanup", args=[], status="success",
                               exit_code=0, duration_ms=200)
        
        audit_logger.log_execution(event1)
        audit_logger.log_execution(event2)
        
        lines = audit_logger.log_path.read_text().strip().split('\n')
        record1 = json.loads(lines[0])
        record2 = json.loads(lines[1])
        
        assert record1.get("sequence", 0) < record2.get("sequence", 0)
    
    def test_includes_previous_hash(self, audit_logger, sample_execution_event):
        """Each entry should reference previous entry's hash (optional)."""
        from core.audit_logger import ExecutionEvent
        
        event1 = sample_execution_event
        event2 = ExecutionEvent(tool="cleanup", args=[], status="success",
                               exit_code=0, duration_ms=200)
        
        audit_logger.log_execution(event1)
        audit_logger.log_execution(event2)
        
        lines = audit_logger.log_path.read_text().strip().split('\n')
        record1 = json.loads(lines[0])
        record2 = json.loads(lines[1])
        
        # Second entry may reference first entry's hash
        if "prev_hash" in record2:
            assert record2["prev_hash"] is not None


# =============================================================================
# Test Log Queries
# =============================================================================

class TestLogQueries:
    """Tests for querying audit logs."""
    
    def test_get_recent_events(self, audit_logger, sample_execution_event):
        """Should retrieve recent events."""
        from core.audit_logger import ExecutionEvent
        
        # Log several events
        for i in range(5):
            event = ExecutionEvent(
                tool=f"tool-{i}",
                args=[],
                status="success",
                exit_code=0,
                duration_ms=100
            )
            audit_logger.log_execution(event)
        
        events = audit_logger.get_recent(limit=3)
        
        assert len(events) == 3
    
    def test_filter_by_tool(self, audit_logger):
        """Should filter events by tool name."""
        from core.audit_logger import ExecutionEvent
        
        # Log events for different tools
        for tool in ["align", "cleanup", "align", "deploy"]:
            event = ExecutionEvent(
                tool=tool, args=[], status="success",
                exit_code=0, duration_ms=100
            )
            audit_logger.log_execution(event)
        
        events = audit_logger.get_by_tool("align")
        
        assert len(events) == 2
        assert all(e["tool"] == "align" for e in events)
    
    def test_filter_by_status(self, audit_logger):
        """Should filter events by status."""
        from core.audit_logger import ExecutionEvent
        
        statuses = ["success", "failed", "success", "blocked"]
        for i, status in enumerate(statuses):
            event = ExecutionEvent(
                tool=f"tool-{i}", args=[], status=status,
                exit_code=0 if status == "success" else 1,
                duration_ms=100
            )
            audit_logger.log_execution(event)
        
        events = audit_logger.get_by_status("failed")
        
        assert len(events) == 1
        assert events[0]["status"] == "failed"
    
    def test_filter_by_date_range(self, audit_logger):
        """Should filter events by date range."""
        events = audit_logger.get_by_date_range(
            start=datetime.now() - timedelta(hours=1),
            end=datetime.now() + timedelta(hours=1)
        )
        
        # Should return events from the time range
        assert isinstance(events, list)


# =============================================================================
# Test Sensitive Data Masking
# =============================================================================

class TestSensitiveDataMasking:
    """Tests for masking sensitive data in logs."""
    
    def test_masks_password_arguments(self, audit_logger):
        """Should mask password-like arguments."""
        from core.audit_logger import ExecutionEvent
        
        event = ExecutionEvent(
            tool="deploy",
            args=["--password", "secret123", "--user", "admin"],
            status="success",
            exit_code=0,
            duration_ms=100
        )
        
        audit_logger.log_execution(event)
        
        content = audit_logger.log_path.read_text()
        
        # Password should not appear in raw form
        assert "secret123" not in content
    
    def test_masks_api_keys(self, audit_logger):
        """Should mask API key arguments."""
        from core.audit_logger import ExecutionEvent
        
        event = ExecutionEvent(
            tool="deploy",
            args=["--api-key", "sk-abc123xyz789"],
            status="success",
            exit_code=0,
            duration_ms=100
        )
        
        audit_logger.log_execution(event)
        
        content = audit_logger.log_path.read_text()
        assert "sk-abc123xyz789" not in content


# =============================================================================
# Test ExecutionEvent
# =============================================================================

class TestExecutionEvent:
    """Tests for ExecutionEvent dataclass."""
    
    def test_create_execution_event(self):
        """Should create execution event with all fields."""
        from core.audit_logger import ExecutionEvent
        
        event = ExecutionEvent(
            tool="align",
            args=["--check"],
            status="success",
            exit_code=0,
            duration_ms=150,
            checkpoint_id="cp-123"
        )
        
        assert event.tool == "align"
        assert event.status == "success"
        assert event.duration_ms == 150
    
    def test_event_defaults(self):
        """Should have sensible defaults."""
        from core.audit_logger import ExecutionEvent
        
        event = ExecutionEvent(
            tool="test",
            args=[],
            status="success",
            exit_code=0,
            duration_ms=0
        )
        
        assert event.checkpoint_id is None


# =============================================================================
# Test Edge Cases
# =============================================================================

class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_log_with_empty_args(self, audit_logger):
        """Should handle empty arguments list."""
        from core.audit_logger import ExecutionEvent
        
        event = ExecutionEvent(
            tool="align",
            args=[],
            status="success",
            exit_code=0,
            duration_ms=100
        )
        
        audit_logger.log_execution(event)
        
        content = audit_logger.log_path.read_text()
        assert len(content) > 0
    
    def test_handles_unicode_in_args(self, audit_logger):
        """Should handle unicode in arguments."""
        from core.audit_logger import ExecutionEvent
        
        event = ExecutionEvent(
            tool="align",
            args=["--name", "日本語", "--emoji", "🚀"],
            status="success",
            exit_code=0,
            duration_ms=100
        )
        
        audit_logger.log_execution(event)
        
        # Should not crash
        content = audit_logger.log_path.read_text()
        assert len(content) > 0
    
    def test_concurrent_logging(self, temp_dir):
        """Should handle concurrent log writes safely."""
        from core.audit_logger import AuditLogger, ExecutionEvent
        import threading
        
        log_path = temp_dir / "audit.jsonl"
        logger = AuditLogger(log_path=log_path)
        
        def log_event(tool_name):
            event = ExecutionEvent(
                tool=tool_name,
                args=[],
                status="success",
                exit_code=0,
                duration_ms=100
            )
            logger.log_execution(event)
        
        threads = [
            threading.Thread(target=log_event, args=(f"tool-{i}",))
            for i in range(10)
        ]
        
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All events should be logged
        lines = log_path.read_text().strip().split('\n')
        assert len(lines) == 10


# =============================================================================
# Test Integration with ToolkitManager
# =============================================================================

class TestIntegrationWithManager:
    """Tests for integration with ToolkitManager."""
    
    @pytest.fixture
    def manager_temp_dir(self, tmp_path):
        """Create temp directory with manifest for ToolkitManager."""
        manifest_content = """
version: 1.0.0
categories:
  test:
    description: Test tools
    tools:
      - name: align
        command: cortex-align
        script: core/align.py
        description: Alignment tool
        platforms: [linux, macos]
        requires_admin: false
        execution_method: cli
"""
        manifest_path = tmp_path / "toolkit-manifest.yaml"
        manifest_path.write_text(manifest_content)
        (tmp_path / ".checkpoints").mkdir(exist_ok=True)
        (tmp_path / "logs").mkdir(exist_ok=True)
        return tmp_path
    
    def test_manager_has_audit_logger(self, manager_temp_dir):
        """ToolkitManager should have AuditLogger."""
        from core.toolkit_manager import ToolkitManager
        from core.audit_logger import AuditLogger
        
        manager = ToolkitManager(toolkit_root=manager_temp_dir)
        
        assert hasattr(manager, 'audit_logger')
        assert isinstance(manager.audit_logger, AuditLogger)
