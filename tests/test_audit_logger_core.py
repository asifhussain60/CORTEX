"""
Test suite for enterprise audit logger core functionality.

Tests cover:
- Async logging with buffering
- Structured JSONL format
- Daily rotation
- Sensitive data redaction
- Performance (<5ms overhead)
- Context propagation
- Error handling
"""

import asyncio
import json
import pytest
import tempfile
import time
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

from src.logging.audit_logger import AuditLogger, LogLevel
from src.logging.log_buffer import LogBuffer
from src.logging.log_writer import LogWriter


class TestAuditLoggerCore:
    """Test enterprise audit logger core functionality."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def audit_logger(self, temp_log_dir):
        """Create audit logger instance."""
        config = {
            "log_dir": str(temp_log_dir),
            "buffer_size": 100,
            "flush_interval": 1.0,
            "rotation_size_mb": 10,
            "backup_count": 5,
            "retention_days": 30,
            "async_enabled": True,
            "compression_enabled": True
        }
        return AuditLogger(config)
    
    def test_initialization(self, temp_log_dir):
        """Test audit logger initializes correctly."""
        config = {"log_dir": str(temp_log_dir)}
        logger = AuditLogger(config)
        
        assert logger.log_dir == temp_log_dir
        assert logger.buffer_size == 1000  # default
        assert logger.flush_interval == 5.0  # default
        assert (temp_log_dir / "audit").exists()
    
    @pytest.mark.asyncio
    async def test_async_logging(self, audit_logger, temp_log_dir):
        """Test async logging writes entries without blocking."""
        start = time.time()
        
        # Log 100 entries
        for i in range(100):
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator="planning",
                event="task_started",
                data={"task_id": i, "description": f"Task {i}"}
            )
        
        elapsed = time.time() - start
        
        # Should complete in <50ms (100 * 0.5ms target per operation)
        assert elapsed < 0.05, f"Async logging took {elapsed}s, expected <0.05s"
        
        # Flush buffer to disk
        await audit_logger.flush()
        
        # Verify logs written
        log_files = list(temp_log_dir.glob("audit/planning/*.jsonl"))
        assert len(log_files) > 0, "No log files created"
        
        # Verify JSONL format
        with open(log_files[0], 'r') as f:
            lines = f.readlines()
            assert len(lines) == 100, f"Expected 100 log entries, found {len(lines)}"
            
            # Parse first entry
            entry = json.loads(lines[0])
            assert "timestamp" in entry
            assert entry["level"] == "INFO"
            assert entry["orchestrator"] == "planning"
            assert entry["event"] == "task_started"
            assert "task_id" in entry["data"]
    
    def test_structured_jsonl_format(self, audit_logger, temp_log_dir):
        """Test logs are written in structured JSONL format."""
        # Log synchronously for immediate write
        audit_logger.log_sync(
            level=LogLevel.ERROR,
            orchestrator="tdd",
            event="test_failed",
            data={
                "test_name": "test_example",
                "error": "AssertionError: Expected 5, got 3",
                "file": "tests/test_example.py",
                "line": 42
            }
        )
        
        audit_logger.flush_sync()
        
        # Read log file
        log_files = list(temp_log_dir.glob("audit/tdd/*.jsonl"))
        assert len(log_files) == 1
        
        with open(log_files[0], 'r') as f:
            entry = json.loads(f.readline())
        
        # Verify structure
        assert entry["level"] == "ERROR"
        assert entry["orchestrator"] == "tdd"
        assert entry["event"] == "test_failed"
        assert entry["data"]["test_name"] == "test_example"
        assert "timestamp" in entry
        assert "session_id" in entry
        assert "correlation_id" in entry
    
    def test_daily_rotation(self, audit_logger, temp_log_dir):
        """Test logs rotate daily."""
        # Log entry for "today"
        audit_logger.log_sync(
            level=LogLevel.INFO,
            orchestrator="maintenance",
            event="health_check",
            data={"status": "healthy"}
        )
        audit_logger.flush_sync()
        
        # Mock tomorrow's date
        with patch('src.logging.audit_logger.datetime') as mock_datetime:
            mock_datetime.now.return_value = datetime(2026, 1, 6, 10, 0, 0)
            mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
            
            audit_logger.log_sync(
                level=LogLevel.INFO,
                orchestrator="maintenance",
                event="health_check",
                data={"status": "healthy"}
            )
            audit_logger.flush_sync()
        
        # Should have 2 log files (different dates)
        log_files = list(temp_log_dir.glob("audit/maintenance/*.jsonl"))
        assert len(log_files) == 2, f"Expected 2 log files, found {len(log_files)}"
        
        # Verify filenames contain dates
        filenames = [f.name for f in log_files]
        assert any("2026-01-05" in name for name in filenames)
        assert any("2026-01-06" in name for name in filenames)
    
    def test_sensitive_data_redaction(self, audit_logger, temp_log_dir):
        """Test sensitive data is redacted from logs."""
        audit_logger.log_sync(
            level=LogLevel.INFO,
            orchestrator="ado",
            event="api_call",
            data={
                "url": "https://dev.azure.com/org/project",
                "api_key": "sk-1234567890abcdef1234567890abcdef",
                "password": "super_secret_password",
                "token": "ghp_1234567890abcdefghijklmnopqrstuvwxyz",
                "payload": {
                    "secret": "my_secret_value",
                    "username": "user@example.com"
                }
            }
        )
        audit_logger.flush_sync()
        
        # Read log file
        log_files = list(temp_log_dir.glob("audit/ado/*.jsonl"))
        with open(log_files[0], 'r') as f:
            entry = json.loads(f.readline())
        
        # Verify redaction
        data = entry["data"]
        assert data["api_key"] == "***REDACTED***"
        assert data["password"] == "***REDACTED***"
        assert data["token"] == "***REDACTED***"
        assert data["payload"]["secret"] == "***REDACTED***"
        assert data["payload"]["username"] == "user@example.com"  # not sensitive
        assert data["url"] == "https://dev.azure.com/org/project"  # preserved
    
    @pytest.mark.asyncio
    async def test_performance_overhead(self, audit_logger):
        """Test logging overhead is <5ms per operation."""
        iterations = 1000
        
        start = time.perf_counter()
        for i in range(iterations):
            await audit_logger.log(
                level=LogLevel.INFO,
                orchestrator="debug",
                event="operation",
                data={"iteration": i}
            )
        end = time.perf_counter()
        
        elapsed_ms = (end - start) * 1000
        overhead_per_op = elapsed_ms / iterations
        
        assert overhead_per_op < 5.0, \
            f"Logging overhead {overhead_per_op:.2f}ms exceeds 5ms threshold"
        
        print(f"✅ Performance: {overhead_per_op:.3f}ms per operation (target: <5ms)")
    
    def test_context_propagation(self, audit_logger, temp_log_dir):
        """Test context (session_id, correlation_id) propagates correctly."""
        session_id = "session-12345"
        correlation_id = "corr-abcdef"
        
        # Set context
        audit_logger.set_context(
            session_id=session_id,
            correlation_id=correlation_id,
            metadata={"user": "test_user", "env": "test"}
        )
        
        # Log multiple entries
        audit_logger.log_sync(LogLevel.INFO, "planning", "task_1", {})
        audit_logger.log_sync(LogLevel.INFO, "planning", "task_2", {})
        audit_logger.flush_sync()
        
        # Read log file
        log_files = list(temp_log_dir.glob("audit/planning/*.jsonl"))
        with open(log_files[0], 'r') as f:
            entries = [json.loads(line) for line in f]
        
        # Verify context in all entries
        for entry in entries:
            assert entry["session_id"] == session_id
            assert entry["correlation_id"] == correlation_id
            assert entry["metadata"]["user"] == "test_user"
            assert entry["metadata"]["env"] == "test"
    
    @pytest.mark.asyncio
    async def test_error_handling(self, audit_logger, temp_log_dir):
        """Test graceful error handling (disk full, permission errors)."""
        # Make log directory read-only
        (temp_log_dir / "audit").chmod(0o444)
        
        try:
            # Should not raise exception
            await audit_logger.log(
                level=LogLevel.ERROR,
                orchestrator="vacuum",
                event="cleanup_failed",
                data={"error": "Permission denied"}
            )
            
            # Should log error internally
            assert audit_logger.error_count > 0
        finally:
            # Restore permissions
            (temp_log_dir / "audit").chmod(0o755)


class TestLogBuffer:
    """Test log buffer functionality."""
    
    @pytest.fixture
    def log_buffer(self):
        """Create log buffer instance."""
        return LogBuffer(max_size=100, flush_interval=1.0)
    
    def test_buffer_initialization(self, log_buffer):
        """Test buffer initializes correctly."""
        assert log_buffer.max_size == 100
        assert log_buffer.flush_interval == 1.0
        assert log_buffer.size == 0
        assert log_buffer.is_empty
    
    @pytest.mark.asyncio
    async def test_buffer_add_and_flush(self, log_buffer):
        """Test adding entries and flushing buffer."""
        entries = [
            {"timestamp": "2026-01-05T10:00:00", "event": f"event_{i}"}
            for i in range(10)
        ]
        
        for entry in entries:
            await log_buffer.add(entry)
        
        assert log_buffer.size == 10
        assert not log_buffer.is_empty
        
        # Flush buffer
        flushed = await log_buffer.flush()
        assert len(flushed) == 10
        assert log_buffer.is_empty
        assert log_buffer.size == 0
    
    @pytest.mark.asyncio
    async def test_auto_flush_on_size(self, log_buffer):
        """Test buffer auto-flushes when size threshold reached."""
        flush_callback = AsyncMock()
        log_buffer.set_flush_callback(flush_callback)
        
        # Add entries up to max_size
        for i in range(100):
            await log_buffer.add({"event": f"event_{i}"})
        
        # Should trigger flush
        assert flush_callback.called
        assert log_buffer.size == 0
    
    @pytest.mark.asyncio
    async def test_auto_flush_on_interval(self, log_buffer):
        """Test buffer auto-flushes after time interval."""
        flush_callback = AsyncMock()
        log_buffer.set_flush_callback(flush_callback)
        
        # Add few entries (below threshold)
        for i in range(10):
            await log_buffer.add({"event": f"event_{i}"})
        
        # Wait for flush interval
        await asyncio.sleep(1.1)
        
        # Should trigger flush
        assert flush_callback.called


class TestLogWriter:
    """Test log writer functionality."""
    
    @pytest.fixture
    def temp_log_dir(self):
        """Create temporary log directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def log_writer(self, temp_log_dir):
        """Create log writer instance."""
        config = {
            "log_dir": str(temp_log_dir),
            "rotation_size_mb": 1,
            "backup_count": 3,
            "compression_enabled": True
        }
        return LogWriter(config)
    
    @pytest.mark.asyncio
    async def test_write_entries(self, log_writer, temp_log_dir):
        """Test writing log entries to disk."""
        entries = [
            {
                "timestamp": "2026-01-05T10:00:00",
                "orchestrator": "planning",
                "event": f"task_{i}",
                "data": {"task_id": i}
            }
            for i in range(10)
        ]
        
        await log_writer.write_batch(entries)
        
        # Verify file created
        log_files = list(temp_log_dir.glob("planning/*.jsonl"))
        assert len(log_files) == 1
        
        # Verify content
        with open(log_files[0], 'r') as f:
            lines = f.readlines()
            assert len(lines) == 10
    
    @pytest.mark.asyncio
    async def test_rotation_on_size(self, log_writer, temp_log_dir):
        """Test file rotation when size threshold reached."""
        # Write large entries to exceed 1MB
        large_data = "x" * 100000  # 100KB
        entries = [
            {
                "timestamp": f"2026-01-05T10:00:{i:02d}",
                "orchestrator": "maintenance",
                "event": "large_event",
                "data": {"payload": large_data}
            }
            for i in range(15)  # 15 * 100KB = 1.5MB
        ]
        
        await log_writer.write_batch(entries)
        
        # Should have rotated (2 files: current + 1 backup)
        log_files = sorted(temp_log_dir.glob("maintenance/*.jsonl*"))
        assert len(log_files) >= 2, f"Expected rotation, found {len(log_files)} files"
    
    @pytest.mark.asyncio
    async def test_compression(self, log_writer, temp_log_dir):
        """Test log compression for rotated files."""
        entries = [{"event": f"event_{i}"} for i in range(100)]
        await log_writer.write_batch(entries)
        
        # Force rotation
        await log_writer.rotate()
        
        # Check for compressed file
        compressed_files = list(temp_log_dir.glob("**/*.jsonl.gz"))
        assert len(compressed_files) > 0, "No compressed files found"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
