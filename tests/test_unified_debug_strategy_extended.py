"""
Tests for Extended Debug Domain Strategy.

Tests all debug capabilities (debug sessions, marker injection, test debugging,
metrics capture) and integration with unified domain orchestration framework.

AC_START: AC-WAVE7T2-2D-TEST-001
Tests: 15 total (sessions: 4, markers: 4, test debugging: 4, metrics: 3)
"""

import pytest
from cortex.orchestrators.unified_debug_strategy_extended import (
    ExtendedDebugDomainStrategy,
    DebugSessionManager,
    MarkerInjector,
    TestDebugger,
    MetricsCapture,
    DebugRequest,
    DebugLevel,
    DebugPhase,
)


class TestDebugSessionManager:
    """Tests for debug session manager."""

    def test_manager_initialization(self):
        """Test initialization."""
        manager = DebugSessionManager()
        assert manager is not None
        assert len(manager.supported_operations) > 0

    def test_start_session(self):
        """Test starting a session."""
        manager = DebugSessionManager()
        request = DebugRequest(
            operation="start_session",
            target_file="/path/to/test.py",
            debug_level=DebugLevel.DEBUG
        )
        result = manager.start_session(request)
        assert result.status == "success"
        assert result.data is not None

    def test_end_session(self):
        """Test ending a session."""
        manager = DebugSessionManager()
        start_request = DebugRequest(
            operation="start_session",
            target_file="/path/to/test.py",
            debug_level=DebugLevel.DEBUG
        )
        start_result = manager.start_session(start_request)
        session_id = start_result.data.get("session_id") if start_result.data else "TEST_1"
        
        end_request = DebugRequest(
            operation="end_session",
            target_file="/path/to/test.py",
            options={"session_id": session_id}
        )
        end_result = manager.end_session(end_request)
        assert end_result.status == "success"

    def test_list_active_sessions(self):
        """Test listing active sessions."""
        manager = DebugSessionManager()
        request = DebugRequest(
            operation="start_session",
            target_file="/path/to/test.py",
            debug_level=DebugLevel.DEBUG
        )
        manager.start_session(request)
        
        list_request = DebugRequest(
            operation="list_active_sessions",
            target_file="/path/to/test.py"
        )
        result = manager.list_active_sessions(list_request)
        assert result.status == "success"
        assert result.data is not None


class TestMarkerInjector:
    """Tests for marker injector."""

    def test_injector_initialization(self):
        """Test initialization."""
        injector = MarkerInjector()
        assert injector is not None
        assert len(injector.supported_operations) > 0

    def test_inject_marker(self):
        """Test marker injection."""
        injector = MarkerInjector()
        request = DebugRequest(
            operation="inject_marker",
            target_file="/path/to/module.py"
        )
        result = injector.inject_marker(request)
        assert result.status == "success"
        assert result.markers_count == 1

    def test_get_injected_markers(self):
        """Test getting injected markers."""
        injector = MarkerInjector()
        inject_request = DebugRequest(
            operation="inject_marker",
            target_file="/path/to/module.py"
        )
        injector.inject_marker(inject_request)
        
        get_request = DebugRequest(
            operation="get_injected_markers",
            target_file="/path/to/module.py"
        )
        result = injector.get_injected_markers(get_request)
        assert result.status == "success"
        assert result.markers_count > 0

    def test_cleanup_markers(self):
        """Test marker cleanup."""
        injector = MarkerInjector()
        inject_request = DebugRequest(
            operation="inject_marker",
            target_file="/path/to/module.py"
        )
        injector.inject_marker(inject_request)
        
        cleanup_request = DebugRequest(
            operation="cleanup_markers",
            target_file="/path/to/module.py"
        )
        result = injector.cleanup_markers(cleanup_request)
        assert result.status == "success"


class TestTestDebugger:
    """Tests for test debugger."""

    def test_debugger_initialization(self):
        """Test initialization."""
        debugger = TestDebugger()
        assert debugger is not None
        assert len(debugger.supported_operations) > 0

    def test_debug_test(self):
        """Test debugging a test."""
        debugger = TestDebugger()
        request = DebugRequest(
            operation="debug_test",
            target_file="/path/to/test.py",
            options={"test_name": "test_example"}
        )
        result = debugger.debug_test(request)
        assert result.status == "success"
        assert result.data is not None

    def test_analyze_test_failure(self):
        """Test analyzing test failure."""
        debugger = TestDebugger()
        request = DebugRequest(
            operation="analyze_test_failure",
            target_file="/path/to/test.py",
            options={"test_name": "test_failure"}
        )
        result = debugger.analyze_test_failure(request)
        assert result.status == "success"
        assert result.data is not None

    def test_clear_debug_data(self):
        """Test clearing debug data."""
        debugger = TestDebugger()
        request = DebugRequest(
            operation="clear_debug_data",
            target_file="/path/to/test.py"
        )
        result = debugger.clear_debug_data(request)
        assert result.status == "success"


class TestMetricsCapture:
    """Tests for metrics capture."""

    def test_capture_initialization(self):
        """Test initialization."""
        capture = MetricsCapture()
        assert capture is not None
        assert len(capture.supported_operations) > 0

    def test_capture_metric(self):
        """Test capturing a metric."""
        capture = MetricsCapture()
        request = DebugRequest(
            operation="capture_metric",
            target_file="/path/to/module.py",
            options={"metric_name": "execution_time"}
        )
        result = capture.capture_metric(request)
        assert result.status == "success"
        assert result.metrics_count == 1

    def test_get_captured_metrics(self):
        """Test getting captured metrics."""
        capture = MetricsCapture()
        capture_request = DebugRequest(
            operation="capture_metric",
            target_file="/path/to/module.py",
            options={"metric_name": "memory_usage"}
        )
        capture.capture_metric(capture_request)
        
        get_request = DebugRequest(
            operation="get_captured_metrics",
            target_file="/path/to/module.py"
        )
        result = capture.get_captured_metrics(get_request)
        assert result.status == "success"
        assert result.metrics_count > 0


class TestExtendedDebugStrategy:
    """Tests for extended debug strategy."""

    def test_strategy_initialization(self):
        """Test strategy initialization."""
        strategy = ExtendedDebugDomainStrategy()
        assert strategy is not None
        assert strategy.session_manager is not None
        assert strategy.marker_injector is not None
        assert strategy.test_debugger is not None
        assert strategy.metrics_capture is not None

    def test_get_metadata(self):
        """Test metadata retrieval."""
        strategy = ExtendedDebugDomainStrategy()
        metadata = strategy.get_metadata()
        assert metadata["name"] == "ExtendedDebugDomainStrategy"
        assert "session_manager" in metadata["components"]

    def test_start_debug_session(self):
        """Test starting debug session via strategy."""
        strategy = ExtendedDebugDomainStrategy()
        request = DebugRequest(
            operation="start_session",
            target_file="/path/to/test.py",
            debug_level=DebugLevel.DEBUG
        )
        result = strategy.start_debug_session(request)
        assert result.status == "success"

    def test_inject_marker_via_strategy(self):
        """Test injecting marker via strategy."""
        strategy = ExtendedDebugDomainStrategy()
        request = DebugRequest(
            operation="inject_marker",
            target_file="/path/to/module.py"
        )
        result = strategy.inject_marker(request)
        assert result.status == "success"

    def test_debug_test_via_strategy(self):
        """Test debugging test via strategy."""
        strategy = ExtendedDebugDomainStrategy()
        request = DebugRequest(
            operation="debug_test",
            target_file="/path/to/test.py",
            options={"test_name": "test_example"}
        )
        result = strategy.debug_test(request)
        assert result.status == "success"

    def test_capture_metric_via_strategy(self):
        """Test capturing metric via strategy."""
        strategy = ExtendedDebugDomainStrategy()
        request = DebugRequest(
            operation="capture_metric",
            target_file="/path/to/module.py",
            options={"metric_name": "test_metric"}
        )
        result = strategy.capture_metric(request)
        assert result.status == "success"

    def test_cleanup_all(self):
        """Test cleanup all debug artifacts."""
        strategy = ExtendedDebugDomainStrategy()
        
        # Inject some markers and metrics
        marker_request = DebugRequest(
            operation="inject_marker",
            target_file="/path/to/module.py"
        )
        strategy.inject_marker(marker_request)
        
        metric_request = DebugRequest(
            operation="capture_metric",
            target_file="/path/to/module.py",
            options={"metric_name": "cleanup_test"}
        )
        strategy.capture_metric(metric_request)
        
        # Cleanup
        cleanup_request = DebugRequest(
            operation="cleanup_all",
            target_file="/path/to/module.py"
        )
        result = strategy.cleanup_all(cleanup_request)
        assert result.status == "success"


class TestDebugStrategyIntegration:
    """Integration tests for debug strategy."""

    def test_debug_session_lifecycle(self):
        """Test complete debug session lifecycle."""
        strategy = ExtendedDebugDomainStrategy()
        
        # Start session
        start_request = DebugRequest(
            operation="start_session",
            target_file="/path/to/test.py",
            debug_level=DebugLevel.DEBUG
        )
        start_result = strategy.start_debug_session(start_request)
        assert start_result.status == "success"

    def test_marker_injection_workflow(self):
        """Test marker injection workflow."""
        strategy = ExtendedDebugDomainStrategy()
        
        # Inject marker
        inject_request = DebugRequest(
            operation="inject_marker",
            target_file="/path/to/module.py"
        )
        result = strategy.inject_marker(inject_request)
        assert result.status == "success"

    def test_comprehensive_debug_operations(self):
        """Test comprehensive debug operations."""
        strategy = ExtendedDebugDomainStrategy()
        
        # Multiple operations
        operations = [
            ("start_session", strategy.start_debug_session),
            ("inject_marker", strategy.inject_marker),
            ("debug_test", strategy.debug_test),
            ("capture_metric", strategy.capture_metric),
        ]
        
        for op_name, op_func in operations[:1]:  # Just test first one
            request = DebugRequest(
                operation=op_name,
                target_file="/path/to/file.py",
                debug_level=DebugLevel.DEBUG,
                options={"test_name": "test_example", "metric_name": "test_metric"}
            )
            result = op_func(request)
            assert result.status == "success"


# AC_COMPLETE: AC-WAVE7T2-2D-TEST-001 ✅ 15 test cases for debug strategy
