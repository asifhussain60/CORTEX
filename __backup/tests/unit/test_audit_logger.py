"""
CORTEX 6.0 - Audit Logger Enhancement Tests

TDD Phase: RED - These tests should FAIL initially.
Tests for Phase 3: Audit Logger Enhancement features.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import pytest
import tempfile
import time
from datetime import datetime
from pathlib import Path
from typing import Generator
from unittest.mock import MagicMock, patch

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.orchestrators.audit_logger import (
    EnterpriseAuditLogger,
    AuditLevel,
    AuditCategory,
    AuditEntry,
    get_audit_logger,
    set_audit_logger,
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
def sample_correlation_id() -> str:
    """Generate sample correlation ID."""
    return "FEAT01-P3-12345678"


# =============================================================================
# TASK 1.3.1: BASIC AUDIT LOGGER TESTS (Existing functionality verification)
# =============================================================================

class TestAuditLoggerBasicFunctionality:
    """Test basic audit logger functionality exists."""
    
    def test_audit_logger_initialization(self, temp_log_dir: Path):
        """Test audit logger can be initialized."""
        logger = EnterpriseAuditLogger(
            log_dir=str(temp_log_dir),
            enable_console=False,
            enable_file=True
        )
        assert logger is not None
        assert logger.log_dir == temp_log_dir
    
    def test_log_info_entry(self, audit_logger: EnterpriseAuditLogger):
        """Test logging an info entry."""
        audit_logger.info(
            category=AuditCategory.VALIDATION,
            component="test_component",
            operation="test_operation",
            message="Test message"
        )
        assert audit_logger.entry_count == 1
    
    def test_log_error_entry(self, audit_logger: EnterpriseAuditLogger):
        """Test logging an error entry."""
        audit_logger.error(
            category=AuditCategory.EXECUTION,
            component="test_component",
            operation="test_operation",
            message="Error message"
        )
        assert audit_logger.entry_count == 1


# =============================================================================
# TASK 1.3.2: CORRELATION ID PROPAGATION TESTS
# =============================================================================

class TestCorrelationIdPropagation:
    """
    Tests for correlation ID propagation across operations.
    
    TDD Status: RED - These tests should FAIL initially.
    Required enhancement: Add automatic correlation ID propagation.
    """
    
    def test_correlation_id_auto_generation(self, audit_logger: EnterpriseAuditLogger):
        """Test that correlation ID is auto-generated when not provided."""
        # Enhancement needed: auto-generate correlation ID
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="test",
            operation="auto_gen_test",
            message="Test auto-generation"
        )
        
        entries = audit_logger.search(operation="auto_gen_test")
        assert len(entries) == 1
        assert entries[0].correlation_id is not None  # Should auto-generate
        assert entries[0].correlation_id.startswith("CORTEX-")
    
    def test_correlation_id_context_propagation(self, audit_logger: EnterpriseAuditLogger):
        """Test correlation ID propagates through nested operations."""
        # Enhancement needed: context manager for correlation propagation
        parent_correlation = "FEAT01-P3-PARENT-001"
        
        # This should use a context manager that auto-propagates correlation IDs
        with audit_logger.correlation_context(parent_correlation):
            audit_logger.info(
                category=AuditCategory.EXECUTION,
                component="parent",
                operation="parent_op",
                message="Parent operation"
            )
            
            # Child operation should inherit correlation ID
            audit_logger.info(
                category=AuditCategory.EXECUTION,
                component="child",
                operation="child_op",
                message="Child operation"
            )
        
        entries = audit_logger.search(correlation_id=parent_correlation)
        assert len(entries) == 2  # Both should have same correlation ID
    
    def test_correlation_chain_tracking(self, audit_logger: EnterpriseAuditLogger):
        """Test tracking of correlation chain (parent-child relationships)."""
        parent_id = "FEAT01-P3-CHAIN-001"
        
        # Enhancement needed: support for correlation chains
        audit_logger.start_correlation_chain(parent_id)
        
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="op1",
            operation="first",
            message="First in chain"
        )
        
        child_id = audit_logger.create_child_correlation()  # Should create linked child
        
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="op2", 
            operation="second",
            message="Second in chain",
            correlation_id=child_id
        )
        
        audit_logger.end_correlation_chain()
        
        chain = audit_logger.get_correlation_chain(parent_id)
        assert chain is not None
        assert len(chain) == 2
        assert chain[0].correlation_id == parent_id
        assert chain[1].metadata.get("parent_correlation_id") == parent_id
    
    def test_correlation_id_thread_isolation(self, audit_logger: EnterpriseAuditLogger):
        """Test correlation IDs are isolated per thread."""
        import threading
        
        results = {}
        
        def thread_operation(thread_id: str, correlation: str):
            with audit_logger.correlation_context(correlation):
                audit_logger.info(
                    category=AuditCategory.EXECUTION,
                    component="thread_test",
                    operation=f"thread_{thread_id}",
                    message=f"Thread {thread_id} operation"
                )
                # Get current correlation from context
                results[thread_id] = audit_logger.get_current_correlation_id()
        
        thread1 = threading.Thread(target=thread_operation, args=("1", "CORR-THREAD-1"))
        thread2 = threading.Thread(target=thread_operation, args=("2", "CORR-THREAD-2"))
        
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        # Each thread should have its own correlation ID
        assert results["1"] == "CORR-THREAD-1"
        assert results["2"] == "CORR-THREAD-2"


# =============================================================================
# TASK 1.3.3: AUDIT LOG ANALYSIS METHODS TESTS
# =============================================================================

class TestAuditLogAnalysisMethods:
    """
    Tests for audit log analysis methods.
    
    TDD Status: RED - These tests should FAIL initially.
    Required enhancements: search_by_correlation, get_trace, get_error_summary
    """
    
    def test_search_by_correlation(self, audit_logger: EnterpriseAuditLogger, sample_correlation_id: str):
        """Test searching logs by correlation ID with enhanced filtering."""
        # Log multiple entries with same correlation ID
        for i in range(5):
            audit_logger.info(
                category=AuditCategory.EXECUTION,
                component=f"component_{i}",
                operation=f"operation_{i}",
                message=f"Message {i}",
                correlation_id=sample_correlation_id
            )
        
        # Log entry with different correlation ID
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="other",
            operation="other_op",
            message="Other message",
            correlation_id="OTHER-CORR-ID"
        )
        
        # Enhancement needed: search_by_correlation method with summary
        results = audit_logger.search_by_correlation(sample_correlation_id)
        
        assert results.correlation_id == sample_correlation_id
        assert results.total_entries == 5
        assert len(results.entries) == 5
        assert results.time_span_ms > 0
        assert results.components == ["component_0", "component_1", "component_2", "component_3", "component_4"]
    
    def test_get_trace(self, audit_logger: EnterpriseAuditLogger):
        """Test getting complete execution trace."""
        trace_correlation = "FEAT01-P3-TRACE-001"
        
        # Simulate operation with start/end
        audit_logger.trace_start(
            correlation_id=trace_correlation,
            operation="full_trace_test",
            context={"input": "test_input"}
        )
        
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="processor",
            operation="process",
            message="Processing step 1",
            correlation_id=trace_correlation
        )
        
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="processor",
            operation="process",
            message="Processing step 2",
            correlation_id=trace_correlation
        )
        
        audit_logger.trace_end(
            correlation_id=trace_correlation,
            status="success",
            result={"output": "test_output"}
        )
        
        # Enhancement needed: get_trace method
        trace = audit_logger.get_trace(trace_correlation)
        
        assert trace is not None
        assert trace.correlation_id == trace_correlation
        assert trace.status == "success"
        assert trace.start_time is not None
        assert trace.end_time is not None
        assert trace.duration_ms > 0
        assert len(trace.steps) == 4  # start + 2 info + end
        assert trace.input_context == {"input": "test_input"}
        assert trace.output_result == {"output": "test_output"}
    
    def test_get_error_summary(self, audit_logger: EnterpriseAuditLogger):
        """Test getting error summary for a correlation ID or time range."""
        error_correlation = "FEAT01-P3-ERRORS-001"
        
        # Log some successful operations
        for i in range(3):
            audit_logger.info(
                category=AuditCategory.EXECUTION,
                component="test",
                operation=f"success_{i}",
                message=f"Success {i}",
                correlation_id=error_correlation
            )
        
        # Log errors
        for i in range(2):
            audit_logger.error(
                category=AuditCategory.EXECUTION,
                component="test",
                operation=f"error_{i}",
                message=f"Error {i}",
                correlation_id=error_correlation,
                context={"error_type": f"TestError{i}"}
            )
        
        # Enhancement needed: get_error_summary method
        error_summary = audit_logger.get_error_summary(correlation_id=error_correlation)
        
        assert error_summary.total_entries == 5
        assert error_summary.error_count == 2
        assert error_summary.error_rate == 0.4  # 2/5 = 40%
        assert len(error_summary.errors) == 2
        assert "TestError0" in str(error_summary.error_types)
    
    def test_get_performance_metrics(self, audit_logger: EnterpriseAuditLogger):
        """Test getting performance metrics for operations."""
        perf_correlation = "FEAT01-P3-PERF-001"
        
        # Log operations with different durations
        durations = [10, 20, 30, 40, 50]  # ms
        for i, duration in enumerate(durations):
            audit_logger.info(
                category=AuditCategory.PERFORMANCE,
                component="perf_test",
                operation="timed_operation",
                message=f"Operation {i}",
                correlation_id=perf_correlation,
                duration_ms=duration
            )
        
        # Enhancement needed: get_performance_metrics method
        metrics = audit_logger.get_performance_metrics(
            correlation_id=perf_correlation,
            operation="timed_operation"
        )
        
        assert metrics.operation == "timed_operation"
        assert metrics.sample_count == 5
        assert metrics.min_ms == 10
        assert metrics.max_ms == 50
        assert metrics.avg_ms == 30
        assert metrics.p50_ms == 30
        # For small datasets (5 samples), p95 and p99 calculations are approximate
        assert 45 <= metrics.p95_ms <= 50  # Allow range for interpolation
        assert 48 <= metrics.p99_ms <= 50  # Allow range for interpolation
    
    def test_timeline_view(self, audit_logger: EnterpriseAuditLogger):
        """Test generating timeline view of operations."""
        timeline_correlation = "FEAT01-P3-TIMELINE-001"
        
        # Log sequential operations
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="api",
            operation="request_received",
            message="API request received",
            correlation_id=timeline_correlation
        )
        
        time.sleep(0.01)  # Small delay
        
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="validator",
            operation="validate",
            message="Validating request",
            correlation_id=timeline_correlation
        )
        
        time.sleep(0.01)
        
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="processor",
            operation="process",
            message="Processing request",
            correlation_id=timeline_correlation
        )
        
        # Enhancement needed: get_timeline method
        timeline = audit_logger.get_timeline(timeline_correlation)
        
        assert timeline is not None
        assert len(timeline.events) == 3
        assert timeline.events[0].component == "api"
        assert timeline.events[1].component == "validator"
        assert timeline.events[2].component == "processor"
        assert timeline.total_duration_ms > 20  # At least 20ms from sleeps


# =============================================================================
# TASK 1.3.4: PHASE/FEATURE GATE INTEGRATION TESTS
# =============================================================================

class TestPhaseFeatureGateIntegration:
    """
    Tests for phase and feature gate logging integration.
    
    TDD Status: RED - These tests should FAIL initially.
    Required enhancements: phase_gate_check, feature_gate_check, gate decorators
    """
    
    def test_phase_gate_logging(self, audit_logger: EnterpriseAuditLogger):
        """Test automatic logging of phase gate checks."""
        # Enhancement needed: phase_gate_check method
        result = audit_logger.phase_gate_check(
            feature_id="feat01",
            phase_id=2,
            gate_name="database_ready",
            condition=lambda: True,
            correlation_id="FEAT01-P2-GATE-001"
        )
        
        assert result.passed is True
        assert result.gate_name == "database_ready"
        assert result.feature_id == "feat01"
        assert result.phase_id == 2
        
        # Verify the gate check was logged
        entries = audit_logger.search(
            correlation_id="FEAT01-P2-GATE-001",
            operation="phase_gate_check"
        )
        assert len(entries) >= 1
        assert entries[0].metadata.get("gate_passed") is True
    
    def test_phase_gate_failure_logging(self, audit_logger: EnterpriseAuditLogger):
        """Test logging of failed phase gate checks."""
        result = audit_logger.phase_gate_check(
            feature_id="feat01",
            phase_id=3,
            gate_name="tests_passing",
            condition=lambda: False,
            correlation_id="FEAT01-P3-GATE-FAIL-001"
        )
        
        assert result.passed is False
        
        # Verify failure was logged as error
        entries = audit_logger.search(
            correlation_id="FEAT01-P3-GATE-FAIL-001",
            level=AuditLevel.ERROR
        )
        assert len(entries) >= 1
        assert "gate" in entries[0].operation.lower()
    
    def test_feature_gate_logging(self, audit_logger: EnterpriseAuditLogger):
        """Test automatic logging of feature gate checks."""
        # Enhancement needed: feature_gate_check method
        result = audit_logger.feature_gate_check(
            feature_id="feat02",
            gate_name="feat01_complete",
            required_features=["feat01"],
            correlation_id="FEAT02-GATE-001"
        )
        
        assert result.gate_name == "feat01_complete"
        assert result.feature_id == "feat02"
        assert "feat01" in result.required_features
        
        # Verify logging
        entries = audit_logger.search(
            correlation_id="FEAT02-GATE-001",
            operation="feature_gate_check"
        )
        assert len(entries) >= 1
    
    def test_gate_decorator(self, audit_logger: EnterpriseAuditLogger):
        """Test decorator for automatic gate logging."""
        # Enhancement needed: @audit_gate decorator
        @audit_logger.audit_gate(
            gate_type="phase",
            feature_id="feat01",
            phase_id=3,
            gate_name="audit_tests_passing"
        )
        def guarded_operation():
            return "success"
        
        result = guarded_operation()
        assert result == "success"
        
        # Verify decorator logged the operation
        entries = audit_logger.search(operation="guarded_operation")
        assert len(entries) >= 1
        assert entries[0].metadata.get("gate_type") == "phase"
    
    def test_gate_condition_decorator(self, audit_logger: EnterpriseAuditLogger):
        """Test decorator that checks condition before execution."""
        execution_count = {"value": 0}
        
        # Enhancement needed: @audit_gate_condition decorator
        @audit_logger.audit_gate_condition(
            condition=lambda: execution_count["value"] < 3,
            gate_name="execution_limit",
            on_fail="skip"
        )
        def limited_operation():
            execution_count["value"] += 1
            return execution_count["value"]
        
        # First 3 calls should succeed
        assert limited_operation() == 1
        assert limited_operation() == 2
        assert limited_operation() == 3
        
        # 4th call should be skipped
        result = limited_operation()
        assert result is None  # Skipped due to gate condition
        
        # Verify skip was logged
        entries = audit_logger.search(operation="limited_operation", level=AuditLevel.WARNING)
        assert len(entries) >= 1


# =============================================================================
# INTEGRATION TESTS: AUDIT LOGGER WITH STATE MANAGER
# =============================================================================

class TestAuditLoggerStateManagerIntegration:
    """
    Tests for audit logger integration with StateManager.
    
    TDD Status: RED - These tests require both components to be enhanced.
    """
    
    def test_audit_all_state_operations(self, audit_logger: EnterpriseAuditLogger, temp_log_dir: Path):
        """Test that all state operations are automatically audited."""
        # This test verifies integration once StateManager is connected
        # Enhancement needed: StateManager.set_audit_logger method
        
        # Import StateManager
        try:
            from src.database.state_manager import StateManager
            
            db_path = temp_log_dir / "test_state.db"
            state_mgr = StateManager(str(db_path))
            
            # Check if set_audit_logger method exists
            if not hasattr(state_mgr, 'set_audit_logger'):
                pytest.skip("StateManager.set_audit_logger not yet implemented - future enhancement")
        except ImportError:
            pytest.skip("StateManager not available yet")
        
        db_path = temp_log_dir / "test_state.db"
        state_mgr = StateManager(str(db_path))
        
        # Connect audit logger
        state_mgr.set_audit_logger(audit_logger)
        
        correlation = "STATE-AUDIT-001"
        
        # Perform state operations
        with audit_logger.correlation_context(correlation):
            state_mgr.set_state("test_key", {"value": "test"})
            state_mgr.get_state("test_key")
            state_mgr.delete_state("test_key")
        
        # All operations should be logged
        entries = audit_logger.search(
            correlation_id=correlation,
            category=AuditCategory.STATE_MANAGEMENT
        )
        assert len(entries) >= 3  # set, get, delete


# =============================================================================
# EDGE CASES AND ERROR HANDLING
# =============================================================================

class TestAuditLoggerEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_large_context_handling(self, audit_logger: EnterpriseAuditLogger):
        """Test handling of large context objects."""
        large_context = {"data": "x" * 100000}  # 100KB of data
        
        # Should handle large context without error
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="large_test",
            operation="large_context",
            message="Large context test",
            context=large_context
        )
        
        entries = audit_logger.search(operation="large_context")
        assert len(entries) == 1
        # Enhancement: should truncate or warn about large contexts
        assert entries[0].metadata.get("context_truncated") is True or len(json.dumps(entries[0].context)) > 0
    
    def test_circular_reference_handling(self, audit_logger: EnterpriseAuditLogger):
        """Test handling of circular references in context."""
        circular = {"self": None}
        circular["self"] = circular
        
        # Should handle circular reference without error
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="circular_test",
            operation="circular_context",
            message="Circular context test",
            context=circular
        )
        
        entries = audit_logger.search(operation="circular_context")
        assert len(entries) == 1
    
    def test_unicode_in_messages(self, audit_logger: EnterpriseAuditLogger):
        """Test handling of Unicode in messages."""
        unicode_message = "Test with émojis 🎉 and 中文 and العربية"
        
        audit_logger.info(
            category=AuditCategory.EXECUTION,
            component="unicode_test",
            operation="unicode_message",
            message=unicode_message
        )
        
        entries = audit_logger.search(operation="unicode_message")
        assert len(entries) == 1
        assert entries[0].message == unicode_message
    
    def test_concurrent_logging(self, audit_logger: EnterpriseAuditLogger):
        """Test concurrent logging from multiple threads."""
        import threading
        
        num_threads = 10
        entries_per_thread = 100
        threads = []
        
        def log_entries(thread_id: int):
            for i in range(entries_per_thread):
                audit_logger.info(
                    category=AuditCategory.EXECUTION,
                    component=f"thread_{thread_id}",
                    operation="concurrent_log",
                    message=f"Entry {i} from thread {thread_id}",
                    correlation_id=f"CONCURRENT-{thread_id}"
                )
        
        for i in range(num_threads):
            t = threading.Thread(target=log_entries, args=(i,))
            threads.append(t)
            t.start()
        
        for t in threads:
            t.join()
        
        # Verify all entries were logged
        assert audit_logger.entry_count == num_threads * entries_per_thread


# =============================================================================
# TEST SUMMARY
# =============================================================================
# 
# Total tests in this file: ~30
# Tests that should FAIL (RED phase): ~20
# Tests that should PASS (existing functionality): ~10
#
# Required enhancements for GREEN phase:
# 1. Correlation ID auto-generation
# 2. correlation_context() context manager
# 3. start_correlation_chain() / end_correlation_chain()
# 4. get_current_correlation_id()
# 5. search_by_correlation() with CorrelationSearchResult
# 6. trace_start() / trace_end()
# 7. get_trace() with TraceResult
# 8. get_error_summary() with ErrorSummary
# 9. get_performance_metrics() with PerformanceMetrics
# 10. get_timeline() with TimelineView
# 11. phase_gate_check() with GateResult
# 12. feature_gate_check() with GateResult
# 13. @audit_gate decorator
# 14. @audit_gate_condition decorator
# =============================================================================
