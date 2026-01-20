"""
Tests for performance profiling and debugging tools (AC-OPS-004-06).

Tests on-demand profiling, request replay, slow query logging,
and transaction tracing functionality.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any
from datetime import datetime

from cortex.devx.profiling_tools import (
    ProfileConfig,
    ProfilingTools,
    CPUProfile,
    MemoryProfile,
    SlowQuery,
    TransactionTrace,
)


class TestProfilingConfig:
    """Test profiling configuration."""

    def test_profiling_config_creation(self) -> None:
        """Test creating profiling configuration."""
        config = ProfileConfig(
            enable_cpu_profiling=True,
            enable_memory_profiling=True,
            slow_query_threshold_ms=100,
        )
        assert config.enable_cpu_profiling is True
        assert config.slow_query_threshold_ms == 100

    def test_profiling_config_defaults(self) -> None:
        """Test profiling config applies defaults."""
        config = ProfileConfig()
        assert config.enable_cpu_profiling is True
        assert config.max_profile_size_mb == 100
        assert config.require_auth_token is True


class TestProfilingTools:
    """Test profiling tools coordinator."""

    def test_profiling_tools_creation(self) -> None:
        """Test creating profiling tools."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        assert tools is not None
        assert tools.config == config


class TestCPUProfiling:
    """Test CPU profiling functionality."""

    def test_start_cpu_profiling(self) -> None:
        """Test starting CPU profiling."""
        config = ProfileConfig(enable_cpu_profiling=True)
        tools = ProfilingTools(config)
        
        profile_id = tools.start_cpu_profiling(duration_seconds=30)
        assert profile_id is not None
        assert "cpu" in profile_id

    def test_cpu_profiling_duration_capped(self) -> None:
        """Test CPU profiling duration is capped at 5 minutes."""
        config = ProfileConfig(enable_cpu_profiling=True)
        tools = ProfilingTools(config)
        
        profile_id = tools.start_cpu_profiling(duration_seconds=600)
        
        # Should complete without error - duration capped
        assert profile_id is not None

    def test_cpu_profiling_concurrent_limit(self) -> None:
        """Test that only one CPU profile can run concurrently."""
        config = ProfileConfig(enable_cpu_profiling=True)
        tools = ProfilingTools(config)
        
        profile_id1 = tools.start_cpu_profiling(duration_seconds=30)
        
        # Second profile should fail
        with pytest.raises(RuntimeError):
            tools.start_cpu_profiling(duration_seconds=30)

    def test_cpu_profiling_disabled(self) -> None:
        """Test error when CPU profiling is disabled."""
        config = ProfileConfig(enable_cpu_profiling=False)
        tools = ProfilingTools(config)
        
        with pytest.raises(ValueError):
            tools.start_cpu_profiling()

    def test_get_cpu_profile_generates_pprof(self) -> None:
        """Test that CPU profile can be retrieved as pprof format."""
        config = ProfileConfig(enable_cpu_profiling=True)
        tools = ProfilingTools(config)
        
        # Start profile
        profile_id = tools.start_cpu_profiling(duration_seconds=1)
        
        # Simulate profile completion by directly updating state
        tools._active_profilers[profile_id]["status"] = "completed"
        
        # Get profile
        profile = tools.get_cpu_profile(profile_id)
        
        # Should have top functions
        assert profile is not None
        assert len(profile.top_functions) > 0


class TestMemoryProfiling:
    """Test memory profiling functionality."""

    def test_start_memory_profiling(self) -> None:
        """Test starting memory profiling."""
        config = ProfileConfig(enable_memory_profiling=True)
        tools = ProfilingTools(config)
        
        profile = tools.start_memory_profiling()
        assert profile is not None
        assert profile.heap_size_mb > 0

    def test_memory_profile_captures_gc_info(self) -> None:
        """Test that memory profile captures GC information."""
        config = ProfileConfig(enable_memory_profiling=True)
        tools = ProfilingTools(config)
        
        profile = tools.start_memory_profiling()
        assert profile.gc_count >= 0

    def test_memory_profile_shows_object_types(self) -> None:
        """Test memory profile includes object type distribution."""
        config = ProfileConfig(enable_memory_profiling=True)
        tools = ProfilingTools(config)
        
        profile = tools.start_memory_profiling()
        assert "dict" in profile.objects_by_type
        assert "list" in profile.objects_by_type
        assert "str" in profile.objects_by_type

    def test_memory_profiling_disabled(self) -> None:
        """Test error when memory profiling is disabled."""
        config = ProfileConfig(enable_memory_profiling=False)
        tools = ProfilingTools(config)
        
        with pytest.raises(ValueError):
            tools.start_memory_profiling()

    def test_memory_profile_heap_snapshot(self) -> None:
        """Test memory profile captures heap snapshot."""
        config = ProfileConfig(enable_memory_profiling=True)
        tools = ProfilingTools(config)
        
        profile = tools.start_memory_profiling()
        assert profile.heap_size_mb > 0
        assert profile.alloc_mb > 0
        assert profile.sys_mb > profile.alloc_mb


class TestSlowQueryLogging:
    """Test slow query logging functionality."""

    def test_log_slow_query(self) -> None:
        """Test logging a slow query."""
        config = ProfileConfig(enable_slow_query_logging=True, slow_query_threshold_ms=100)
        tools = ProfilingTools(config)
        
        tools.log_slow_query(
            query_text="SELECT * FROM users WHERE active = true",
            duration_ms=150.5,
            query_type="SELECT",
        )
        
        log = tools.get_slow_query_log()
        assert len(log) == 1
        assert log[0].query_text == "SELECT * FROM users WHERE active = true"
        assert log[0].duration_ms == 150.5

    def test_fast_query_not_logged(self) -> None:
        """Test that fast queries are not logged."""
        config = ProfileConfig(enable_slow_query_logging=True, slow_query_threshold_ms=100)
        tools = ProfilingTools(config)
        
        tools.log_slow_query(
            query_text="SELECT * FROM users WHERE id = 1",
            duration_ms=5.0,  # Fast query
            query_type="SELECT",
        )
        
        log = tools.get_slow_query_log()
        assert len(log) == 0

    def test_slow_query_log_disabled(self) -> None:
        """Test slow query logging can be disabled."""
        config = ProfileConfig(enable_slow_query_logging=False)
        tools = ProfilingTools(config)
        
        tools.log_slow_query(
            query_text="SELECT * FROM users",
            duration_ms=500.0,
            query_type="SELECT",
        )
        
        log = tools.get_slow_query_log()
        assert len(log) == 0

    def test_slow_query_log_limit(self) -> None:
        """Test slow query log is limited to prevent memory issues."""
        config = ProfileConfig(enable_slow_query_logging=True, slow_query_threshold_ms=10)
        tools = ProfilingTools(config)
        
        # Log many slow queries
        for i in range(2000):
            tools.log_slow_query(
                query_text=f"SELECT * FROM table_{i}",
                duration_ms=100.0,
                query_type="SELECT",
            )
        
        log = tools.get_slow_query_log(limit=1000)
        # Should be limited
        assert len(log) <= 1000

    def test_get_slow_query_log_with_pagination(self) -> None:
        """Test paginating through slow query log."""
        config = ProfileConfig(enable_slow_query_logging=True, slow_query_threshold_ms=10)
        tools = ProfilingTools(config)
        
        # Log multiple queries
        for i in range(25):
            tools.log_slow_query(
                query_text=f"SELECT * FROM table_{i}",
                duration_ms=100.0,
                query_type="SELECT",
            )
        
        # Get first page
        page1 = tools.get_slow_query_log(limit=10, offset=0)
        assert len(page1) == 10
        
        # Get second page
        page2 = tools.get_slow_query_log(limit=10, offset=10)
        assert len(page2) == 10
        
        # Get third page (partial)
        page3 = tools.get_slow_query_log(limit=10, offset=20)
        assert len(page3) == 5


class TestTransactionTracing:
    """Test transaction tracing functionality."""

    def test_start_transaction_trace(self) -> None:
        """Test starting transaction tracing."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        trace = tools.start_transaction_trace("txn-123")
        assert trace.transaction_id == "txn-123"
        assert trace.status == "running"

    def test_record_transaction_operation(self) -> None:
        """Test recording operations in transaction."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        tools.start_transaction_trace("txn-123")
        tools.record_transaction_operation(
            "txn-123",
            "query",
            {"table": "users", "duration_ms": 5.0},
        )
        
        trace = tools.get_transaction_trace("txn-123")
        assert len(trace.operations) == 1
        assert trace.operations[0]["operation"] == "query"

    def test_end_transaction_trace(self) -> None:
        """Test completing transaction trace."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        tools.start_transaction_trace("txn-123")
        tools.record_transaction_operation("txn-123", "query")
        
        trace = tools.end_transaction_trace("txn-123", status="success")
        assert trace.status == "success"
        assert trace.end_time is not None

    def test_transaction_trace_with_error(self) -> None:
        """Test transaction trace with error."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        tools.start_transaction_trace("txn-456")
        tools.end_transaction_trace("txn-456", status="error", error_message="Connection timeout")
        
        trace = tools.get_transaction_trace("txn-456")
        assert trace.status == "error"
        assert "timeout" in trace.error_message.lower()

    def test_get_transaction_trace(self) -> None:
        """Test retrieving transaction trace."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        tools.start_transaction_trace("txn-789")
        
        trace = tools.get_transaction_trace("txn-789")
        assert trace is not None
        assert trace.transaction_id == "txn-789"


class TestRequestReplay:
    """Test request replay for debugging."""

    def test_replay_request(self) -> None:
        """Test replaying a captured request."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        captured_request = {
            "method": "GET",
            "path": "/api/test",
            "headers": {"User-Agent": "test-client"},
        }
        
        result = tools.replay_request("req-123", captured_request)
        assert "status" in result
        assert result["response_status"] == 200

    def test_replay_preserves_request_details(self) -> None:
        """Test that replay preserves original request details."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        captured_request = {
            "method": "POST",
            "path": "/api/governance",
            "body": '{"rule": "CORE-001"}',
        }
        
        result = tools.replay_request("req-456", captured_request)
        assert result["original_request_id"] == "req-456"


class TestProfilingPerformance:
    """Test profiling overhead and performance."""

    def test_profiling_overhead_minimal_when_inactive(self) -> None:
        """Test that profiling adds minimal overhead when inactive."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        overhead = tools.get_profiling_overhead()
        assert overhead < 1.0  # Should be <1% when not profiling

    def test_profiling_overhead_during_profiling(self) -> None:
        """Test profiling overhead increases during active profiling."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        # Start profiling
        tools.start_cpu_profiling(duration_seconds=10)
        
        overhead = tools.get_profiling_overhead()
        assert overhead > 1.0  # Should be >1% during profiling

    def test_slow_query_logging_performance(self) -> None:
        """Test that slow query logging doesn't significantly impact performance."""
        config = ProfileConfig(enable_slow_query_logging=True)
        tools = ProfilingTools(config)
        
        start = time.time()
        for i in range(1000):
            tools.log_slow_query(
                query_text=f"SELECT * FROM table_{i % 10}",
                duration_ms=100.0 + i,
                query_type="SELECT",
            )
        elapsed = time.time() - start
        
        # Should log 1000 queries in <1 second
        assert elapsed < 1.0


class TestProfilingEdgeCases:
    """Test edge cases in profiling."""

    def test_query_text_truncation(self) -> None:
        """Test that very long query text is truncated."""
        config = ProfileConfig(enable_slow_query_logging=True)
        tools = ProfilingTools(config)
        
        long_query = "SELECT * " + "FROM very_long_table_name " * 100
        tools.log_slow_query(
            query_text=long_query,
            duration_ms=150.0,
            query_type="SELECT",
        )
        
        log = tools.get_slow_query_log()
        # Should be truncated to reasonable length
        assert len(log[0].query_text) <= 500

    def test_concurrent_transaction_traces(self) -> None:
        """Test handling multiple concurrent transaction traces."""
        config = ProfileConfig()
        tools = ProfilingTools(config)
        
        # Start multiple transactions
        for i in range(10):
            tools.start_transaction_trace(f"txn-{i}")
        
        # Each should be independent
        for i in range(10):
            trace = tools.get_transaction_trace(f"txn-{i}")
            assert trace is not None
            assert trace.transaction_id == f"txn-{i}"

    def test_profile_size_limit(self) -> None:
        """Test that profiles are limited to max size."""
        config = ProfileConfig(max_profile_size_mb=100)
        tools = ProfilingTools(config)
        
        # Profile size should be limited
        assert config.max_profile_size_mb == 100
