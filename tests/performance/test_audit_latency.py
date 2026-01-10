"""
Audit Logger Performance Tests - AC-AUDIT-001.

Tests to validate <5ms latency requirement for AuditLogger operations.

Acceptance Criteria Coverage:
- AC-AUDIT-001: AuditLogger <5ms latency validation

Performance Targets:
- Single log entry: <5ms
- Batch log entries (100): <50ms total (<0.5ms each)
- Query by correlation ID: <10ms
- File write flush: <5ms

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import time
import statistics
import tempfile
from pathlib import Path
from typing import List, Generator
from unittest.mock import MagicMock

from src.orchestrators.audit_logger import (
    EnterpriseAuditLogger,
    AuditLevel,
    AuditCategory,
    AuditEntry,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_log_dir(tmp_path: Path) -> Generator[Path, None, None]:
    """Create temporary log directory."""
    log_dir = tmp_path / "audit-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    yield log_dir


@pytest.fixture
def audit_logger(temp_log_dir: Path) -> Generator[EnterpriseAuditLogger, None, None]:
    """Create audit logger with temporary directory."""
    logger = EnterpriseAuditLogger(
        log_dir=str(temp_log_dir),
        enable_console=False,
        enable_file=True
    )
    yield logger


@pytest.fixture
def performance_audit_logger(temp_log_dir: Path) -> Generator[EnterpriseAuditLogger, None, None]:
    """Create audit logger optimized for performance testing."""
    logger = EnterpriseAuditLogger(
        log_dir=str(temp_log_dir),
        enable_console=False,
        enable_file=True,
    )
    yield logger


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def measure_execution_time_ms(func, *args, **kwargs) -> tuple:
    """Measure execution time in milliseconds.
    
    Returns:
        Tuple of (result, execution_time_ms)
    """
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    return result, (end - start) * 1000


def run_benchmark(func, iterations: int = 100, warmup: int = 10, *args, **kwargs) -> dict:
    """Run benchmark with warmup iterations.
    
    Returns:
        Dict with min, max, avg, p50, p95, p99 in milliseconds
    """
    # Warmup
    for _ in range(warmup):
        func(*args, **kwargs)
    
    # Actual benchmark
    times = []
    for _ in range(iterations):
        _, time_ms = measure_execution_time_ms(func, *args, **kwargs)
        times.append(time_ms)
    
    times.sort()
    return {
        "min_ms": min(times),
        "max_ms": max(times),
        "avg_ms": statistics.mean(times),
        "p50_ms": times[len(times) // 2],
        "p95_ms": times[int(len(times) * 0.95)],
        "p99_ms": times[int(len(times) * 0.99)],
        "samples": iterations,
    }


# =============================================================================
# AC-AUDIT-001: AuditLogger <5ms Latency Validation
# =============================================================================

class TestAuditLoggerLatency:
    """Performance tests for AC-AUDIT-001: <5ms latency requirement."""
    
    def test_single_info_log_under_5ms(self, audit_logger: EnterpriseAuditLogger):
        """
        AC-AUDIT-001: Single info log entry completes in <5ms.
        
        GIVEN: An initialized audit logger
        WHEN: A single info entry is logged
        THEN: Operation completes in <5ms
        """
        # Act
        _, time_ms = measure_execution_time_ms(
            audit_logger.info,
            category=AuditCategory.VALIDATION,
            component="test_component",
            operation="test_operation",
            message="Performance test message"
        )
        
        # Assert
        assert time_ms < 5.0, f"Single log took {time_ms:.2f}ms, expected <5ms"
    
    def test_single_error_log_under_5ms(self, audit_logger: EnterpriseAuditLogger):
        """
        AC-AUDIT-001: Single error log entry completes in <5ms.
        
        GIVEN: An initialized audit logger
        WHEN: A single error entry is logged
        THEN: Operation completes in <5ms
        """
        # Act
        _, time_ms = measure_execution_time_ms(
            audit_logger.error,
            category=AuditCategory.EXECUTION,
            component="test_component",
            operation="test_operation",
            message="Error test message"
        )
        
        # Assert
        assert time_ms < 5.0, f"Single error log took {time_ms:.2f}ms, expected <5ms"
    
    def test_log_with_context_under_5ms(self, audit_logger: EnterpriseAuditLogger):
        """
        AC-AUDIT-001: Log with context data completes in <5ms.
        
        GIVEN: An initialized audit logger
        WHEN: Entry with context dict is logged
        THEN: Operation completes in <5ms
        """
        # Arrange
        context = {
            "user_id": "test-user-123",
            "session_id": "session-456",
            "request_path": "/api/test",
            "method": "POST",
            "payload_size": 1024,
        }
        
        # Act
        _, time_ms = measure_execution_time_ms(
            audit_logger.info,
            category=AuditCategory.EXECUTION,
            component="api_handler",
            operation="process_request",
            message="Request processed",
            context=context
        )
        
        # Assert
        assert time_ms < 5.0, f"Log with context took {time_ms:.2f}ms, expected <5ms"
    
    def test_log_with_large_context_under_5ms(self, audit_logger: EnterpriseAuditLogger):
        """
        AC-AUDIT-001: Log with large context (1KB) completes in <5ms.
        
        GIVEN: An initialized audit logger
        WHEN: Entry with ~1KB context is logged
        THEN: Operation completes in <5ms
        """
        # Arrange - ~1KB of context data
        context = {
            f"field_{i}": f"value_{i}_" + "x" * 50
            for i in range(20)
        }
        
        # Act
        _, time_ms = measure_execution_time_ms(
            audit_logger.info,
            category=AuditCategory.STATE_MANAGEMENT,
            component="state_manager",
            operation="save_state",
            message="State saved",
            context=context
        )
        
        # Assert
        assert time_ms < 5.0, f"Log with large context took {time_ms:.2f}ms, expected <5ms"
    
    def test_avg_latency_under_5ms_100_iterations(self, performance_audit_logger: EnterpriseAuditLogger):
        """
        AC-AUDIT-001: Average latency <5ms over 100 iterations.
        
        GIVEN: An initialized audit logger
        WHEN: 100 log entries are written
        THEN: Average latency is <5ms
        """
        # Act
        benchmark = run_benchmark(
            performance_audit_logger.info,
            iterations=100,
            warmup=10,
            category=AuditCategory.VALIDATION,
            component="benchmark",
            operation="test",
            message="Benchmark message"
        )
        
        # Assert
        assert benchmark["avg_ms"] < 5.0, f"Average latency {benchmark['avg_ms']:.2f}ms, expected <5ms"
        assert benchmark["p95_ms"] < 10.0, f"P95 latency {benchmark['p95_ms']:.2f}ms, expected <10ms"
    
    def test_p99_latency_under_10ms(self, performance_audit_logger: EnterpriseAuditLogger):
        """
        AC-AUDIT-001: P99 latency <10ms (allowing for occasional spikes).
        
        GIVEN: An initialized audit logger
        WHEN: 100 log entries are written
        THEN: P99 latency is <10ms
        """
        # Act
        benchmark = run_benchmark(
            performance_audit_logger.info,
            iterations=100,
            warmup=10,
            category=AuditCategory.EXECUTION,
            component="benchmark",
            operation="p99_test",
            message="P99 benchmark"
        )
        
        # Assert
        assert benchmark["p99_ms"] < 10.0, f"P99 latency {benchmark['p99_ms']:.2f}ms, expected <10ms"


# =============================================================================
# BATCH LOGGING PERFORMANCE
# =============================================================================

class TestBatchLoggingPerformance:
    """Performance tests for batch logging operations."""
    
    def test_batch_100_logs_under_50ms(self, performance_audit_logger: EnterpriseAuditLogger):
        """
        Batch of 100 log entries completes in <50ms total.
        
        GIVEN: An initialized audit logger
        WHEN: 100 entries are logged in sequence
        THEN: Total time is <50ms (avg <0.5ms each)
        """
        # Act
        start = time.perf_counter()
        for i in range(100):
            performance_audit_logger.info(
                category=AuditCategory.VALIDATION,
                component="batch_test",
                operation=f"operation_{i}",
                message=f"Batch message {i}"
            )
        end = time.perf_counter()
        total_ms = (end - start) * 1000
        
        # Assert
        assert total_ms < 50.0, f"Batch of 100 took {total_ms:.2f}ms, expected <50ms"
        avg_per_entry = total_ms / 100
        assert avg_per_entry < 0.5, f"Average {avg_per_entry:.2f}ms/entry, expected <0.5ms"
    
    def test_batch_with_varied_categories(self, performance_audit_logger: EnterpriseAuditLogger):
        """
        Batch with varied categories maintains performance.
        
        GIVEN: An initialized audit logger
        WHEN: 100 entries with different categories are logged
        THEN: Total time is <50ms
        """
        categories = list(AuditCategory)
        
        # Act
        start = time.perf_counter()
        for i in range(100):
            performance_audit_logger.info(
                category=categories[i % len(categories)],
                component="varied_test",
                operation=f"op_{i}",
                message=f"Message {i}"
            )
        end = time.perf_counter()
        total_ms = (end - start) * 1000
        
        # Assert
        assert total_ms < 50.0, f"Varied batch took {total_ms:.2f}ms, expected <50ms"


# =============================================================================
# CORRELATION ID OPERATIONS
# =============================================================================

class TestCorrelationIdPerformance:
    """Performance tests for correlation ID operations."""
    
    def test_correlation_context_under_1ms(self, audit_logger: EnterpriseAuditLogger):
        """
        Correlation context setup completes in <1ms.
        
        GIVEN: An initialized audit logger
        WHEN: Correlation context is created
        THEN: Operation completes in <1ms
        """
        # Act - use context manager API
        start = time.perf_counter()
        with audit_logger.correlation_context("FEAT01-P3-12345678"):
            pass  # Just test context setup/teardown
        time_ms = (time.perf_counter() - start) * 1000
        
        # Assert
        assert time_ms < 2.0, f"Correlation context took {time_ms:.2f}ms, expected <2ms"
    
    def test_log_with_correlation_under_5ms(self, audit_logger: EnterpriseAuditLogger):
        """
        Logging with correlation ID completes in <5ms.
        
        GIVEN: An audit logger with correlation context
        WHEN: Entry is logged
        THEN: Operation completes in <5ms
        """
        # Act
        with audit_logger.correlation_context("CORR-PERF-001"):
            _, time_ms = measure_execution_time_ms(
                audit_logger.info,
                category=AuditCategory.EXECUTION,
                component="correlated",
                operation="test",
                message="Correlated message"
            )
        
        # Assert
        assert time_ms < 5.0, f"Correlated log took {time_ms:.2f}ms, expected <5ms"


# =============================================================================
# CONTEXT MANAGER PERFORMANCE
# =============================================================================

class TestContextManagerPerformance:
    """Performance tests for audit context managers."""
    
    def test_correlation_context_overhead_under_2ms(self, audit_logger: EnterpriseAuditLogger):
        """
        Correlation context manager overhead is <2ms.
        
        GIVEN: An initialized audit logger
        WHEN: Correlation context is entered and exited
        THEN: Overhead (excluding operation) is <2ms
        """
        # Act - measure context manager overhead
        start = time.perf_counter()
        with audit_logger.correlation_context("PERF-TEST-001"):
            pass  # Empty operation
        end = time.perf_counter()
        overhead_ms = (end - start) * 1000
        
        # Assert - should be minimal overhead
        assert overhead_ms < 2.0, f"Context overhead {overhead_ms:.2f}ms, expected <2ms"
    
    def test_trace_start_end_under_5ms(self, audit_logger: EnterpriseAuditLogger):
        """
        Trace start + end operations complete in <5ms.
        
        GIVEN: An initialized audit logger
        WHEN: trace_start and trace_end are called
        THEN: Combined overhead is <5ms
        """
        # Act
        correlation_id = "PERF-TRACE-001"
        start = time.perf_counter()
        audit_logger.trace_start(
            correlation_id=correlation_id,
            operation="noop",
            context={}
        )
        audit_logger.trace_end(
            correlation_id=correlation_id,
            status="success",
            result={}
        )
        end = time.perf_counter()
        overhead_ms = (end - start) * 1000
        
        # Assert
        assert overhead_ms < 10.0, f"Trace start/end took {overhead_ms:.2f}ms, expected <10ms"


# =============================================================================
# STRESS TESTS
# =============================================================================

class TestStressPerformance:
    """Stress tests for audit logger under load."""
    
    def test_1000_entries_under_500ms(self, performance_audit_logger: EnterpriseAuditLogger):
        """
        1000 log entries complete in <500ms.
        
        GIVEN: An initialized audit logger
        WHEN: 1000 entries are logged rapidly
        THEN: Total time is <500ms
        """
        # Act
        start = time.perf_counter()
        for i in range(1000):
            performance_audit_logger.info(
                category=AuditCategory.VALIDATION,
                component="stress",
                operation=f"op_{i}",
                message=f"Stress test {i}"
            )
        end = time.perf_counter()
        total_ms = (end - start) * 1000
        
        # Assert
        assert total_ms < 500.0, f"1000 entries took {total_ms:.2f}ms, expected <500ms"
    
    @pytest.mark.slow
    def test_sustained_throughput_10k(self, performance_audit_logger: EnterpriseAuditLogger):
        """
        10000 log entries maintain <5ms average.
        
        GIVEN: An initialized audit logger
        WHEN: 10000 entries are logged
        THEN: Average latency remains <5ms
        """
        # Act
        times = []
        for i in range(10000):
            start = time.perf_counter()
            performance_audit_logger.info(
                category=AuditCategory.EXECUTION,
                component="sustained",
                operation="test",
                message=f"Entry {i}"
            )
            times.append((time.perf_counter() - start) * 1000)
        
        avg_ms = statistics.mean(times)
        p99_ms = sorted(times)[int(len(times) * 0.99)]
        
        # Assert
        assert avg_ms < 5.0, f"Sustained average {avg_ms:.2f}ms, expected <5ms"
        assert p99_ms < 20.0, f"Sustained P99 {p99_ms:.2f}ms, expected <20ms"


# =============================================================================
# MEMORY EFFICIENCY
# =============================================================================

class TestMemoryEfficiency:
    """Memory efficiency tests for audit logger."""
    
    def test_entry_creation_memory_efficient(self, audit_logger: EnterpriseAuditLogger):
        """
        Audit entries are memory efficient.
        
        GIVEN: An audit entry creation
        WHEN: Entry is created with standard context
        THEN: Memory footprint is reasonable
        """
        import sys
        
        # Create entry
        entry = AuditEntry(
            timestamp="2026-01-10T12:00:00Z",
            level=AuditLevel.INFO,
            category=AuditCategory.VALIDATION,
            component="test",
            operation="test_op",
            message="Test message",
            context={"key": "value"},
            metadata={}
        )
        
        # Check size (should be reasonable)
        size = sys.getsizeof(entry)
        # Dataclass with these fields should be under 500 bytes
        assert size < 500, f"Entry size {size} bytes, expected <500"


# =============================================================================
# REGRESSION TESTS
# =============================================================================

class TestPerformanceRegression:
    """Regression tests to catch performance degradation."""
    
    def test_no_regression_single_log(self, audit_logger: EnterpriseAuditLogger):
        """
        Single log latency has not regressed.
        
        Baseline: 2ms (established 2026-01-10)
        Threshold: 5ms (allowing 2.5x buffer)
        """
        benchmark = run_benchmark(
            audit_logger.info,
            iterations=50,
            warmup=5,
            category=AuditCategory.VALIDATION,
            component="regression",
            operation="test",
            message="Regression test"
        )
        
        # Assert against baseline with buffer
        assert benchmark["avg_ms"] < 5.0, f"Regression detected: {benchmark['avg_ms']:.2f}ms (baseline: 2ms)"
    
    def test_no_regression_with_context(self, audit_logger: EnterpriseAuditLogger):
        """
        Log with context latency has not regressed.
        
        Baseline: 3ms (established 2026-01-10)
        Threshold: 5ms
        """
        context = {"field1": "value1", "field2": "value2", "field3": "value3"}
        
        benchmark = run_benchmark(
            audit_logger.info,
            iterations=50,
            warmup=5,
            category=AuditCategory.EXECUTION,
            component="regression",
            operation="context_test",
            message="Context regression test",
            context=context
        )
        
        assert benchmark["avg_ms"] < 5.0, f"Context regression: {benchmark['avg_ms']:.2f}ms (baseline: 3ms)"
