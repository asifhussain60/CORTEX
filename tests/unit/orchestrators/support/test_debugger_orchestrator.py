"""
Unit tests for DebuggerOrchestrator

Tests EventBus-driven debug marker injection without manual intervention.

AC-ID: AC-WAVE-R-003
"""

import pytest
from datetime import datetime
from unittest.mock import Mock, MagicMock, call
from typing import Dict, Any

from cortex.orchestrators.support.debugger_orchestrator import (
    DebuggerOrchestrator,
    DebugSession
)
from cortex.core.event_bus import Event
from cortex.models.canonical_enums import IntentType


class TestDebuggerOrchestratorInitialization:
    """Test DebuggerOrchestrator initialization and setup."""
    
    def test_debugger_orchestrator_initializes_with_event_bus(self):
        """Test orchestrator initializes with EventBus."""
        # Arrange
        event_bus = Mock()
        
        # Act
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Assert
        assert orchestrator.event_bus is event_bus
        assert orchestrator.active_sessions == {}
    
    def test_debugger_subscribes_to_test_failure_event(self):
        """Test orchestrator subscribes to TEST_FAILURE event."""
        # Arrange
        event_bus = Mock()
        
        # Act
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Assert
        event_bus.subscribe.assert_any_call("TEST_FAILURE", orchestrator.handle_test_failure)
    
    def test_debugger_subscribes_to_refactor_regression_event(self):
        """Test orchestrator subscribes to REFACTOR_REGRESSION event."""
        # Arrange
        event_bus = Mock()
        
        # Act
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Assert
        event_bus.subscribe.assert_any_call("REFACTOR_REGRESSION", orchestrator.handle_refactor_regression)
    
    def test_debugger_subscribes_to_governance_violation_event(self):
        """Test orchestrator subscribes to GOVERNANCE_VIOLATION event."""
        # Arrange
        event_bus = Mock()
        
        # Act
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Assert
        event_bus.subscribe.assert_any_call("GOVERNANCE_VIOLATION", orchestrator.handle_governance_violation)
    
    def test_debugger_subscribes_to_tests_passed_event(self):
        """Test orchestrator subscribes to TESTS_PASSED event for auto-cleanup."""
        # Arrange
        event_bus = Mock()
        
        # Act
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Assert
        event_bus.subscribe.assert_any_call("TESTS_PASSED", orchestrator.handle_tests_passed)


class TestTestFailureHandler:
    """Test TEST_FAILURE event handling."""
    
    def test_test_failure_handler_receives_payload(self):
        """Test handler receives and parses TEST_FAILURE payload."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        event = Event(
            type="TEST_FAILURE",
            payload={
                "test_name": "test_master_orchestrator_stage_2",
                "file_path": "cortex/orchestrators/core/master_orchestrator.py",
                "line_number": 2380,
                "failure_reason": "AssertionError: Expected stage2_result, got None"
            }
        )
        
        # Act
        orchestrator.handle_test_failure(event)
        
        # Assert
        assert len(orchestrator.active_sessions) == 1
        session = list(orchestrator.active_sessions.values())[0]
        assert session.trigger_event == "TEST_FAILURE"
        assert session.file_paths == ["cortex/orchestrators/core/master_orchestrator.py"]
    
    def test_test_failure_handler_extracts_file_path(self):
        """Test handler extracts file_path from event payload."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        expected_file = "cortex/orchestrators/core/master_orchestrator.py"
        event = Event(
            type="TEST_FAILURE",
            payload={
                "test_name": "test_example",
                "file_path": expected_file,
                "line_number": 100,
                "failure_reason": "Test failed"
            }
        )
        
        # Act
        orchestrator.handle_test_failure(event)
        
        # Assert
        session = list(orchestrator.active_sessions.values())[0]
        assert expected_file in session.file_paths
    
    def test_test_failure_handler_extracts_line_number(self):
        """Test handler extracts line_number from event payload."""
        # Arrange
        event_bus = Mock()
        marker_engine = Mock()
        orchestrator = DebuggerOrchestrator(event_bus, marker_injection_engine=marker_engine)
        
        expected_line = 2380
        event = Event(
            type="TEST_FAILURE",
            payload={
                "test_name": "test_example",
                "file_path": "example.py",
                "line_number": expected_line,
                "failure_reason": "Test failed"
            }
        )
        
        # Act
        orchestrator.handle_test_failure(event)
        
        # Assert
        marker_engine.inject.assert_called_once()
        call_args = marker_engine.inject.call_args
        assert call_args[1]["line_number"] == expected_line
    
    def test_test_failure_handler_calls_marker_injection_engine(self):
        """Test handler calls MarkerInjectionEngine.inject()."""
        # Arrange
        event_bus = Mock()
        marker_engine = Mock()
        orchestrator = DebuggerOrchestrator(event_bus, marker_injection_engine=marker_engine)
        
        event = Event(
            type="TEST_FAILURE",
            payload={
                "test_name": "test_example",
                "file_path": "example.py",
                "line_number": 100,
                "failure_reason": "Test failed"
            }
        )
        
        # Act
        orchestrator.handle_test_failure(event)
        
        # Assert
        marker_engine.inject.assert_called_once()
        call_args = marker_engine.inject.call_args
        assert call_args[1]["strategy"] == "test_failure"
        assert call_args[1]["file_path"] == "example.py"


class TestDebugMarkersInjectedEvent:
    """Test DEBUG_MARKERS_INJECTED event emission."""
    
    def test_debugger_emits_debug_markers_injected_event(self):
        """Test orchestrator emits DEBUG_MARKERS_INJECTED after injection."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        event = Event(
            type="TEST_FAILURE",
            payload={
                "test_name": "test_example",
                "file_path": "example.py",
                "line_number": 100,
                "failure_reason": "Test failed"
            }
        )
        
        # Act
        orchestrator.handle_test_failure(event)
        
        # Assert
        event_bus.publish.assert_called_once()
        published_event = event_bus.publish.call_args[0][0]
        assert published_event.type == "DEBUG_MARKERS_INJECTED"
    
    def test_debug_markers_injected_includes_file_paths(self):
        """Test DEBUG_MARKERS_INJECTED event includes file_paths."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        expected_file = "example.py"
        event = Event(
            type="TEST_FAILURE",
            payload={
                "test_name": "test_example",
                "file_path": expected_file,
                "line_number": 100,
                "failure_reason": "Test failed"
            }
        )
        
        # Act
        orchestrator.handle_test_failure(event)
        
        # Assert
        published_event = event_bus.publish.call_args[0][0]
        assert expected_file in published_event.payload["file_paths"]
    
    def test_debug_markers_injected_includes_session_id(self):
        """Test DEBUG_MARKERS_INJECTED event includes session_id."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        event = Event(
            type="TEST_FAILURE",
            payload={
                "test_name": "test_example",
                "file_path": "example.py",
                "line_number": 100,
                "failure_reason": "Test failed"
            }
        )
        
        # Act
        orchestrator.handle_test_failure(event)
        
        # Assert
        published_event = event_bus.publish.call_args[0][0]
        assert "session_id" in published_event.payload
        assert published_event.payload["session_id"].startswith("session-test_failure-")


class TestRefactorRegressionHandler:
    """Test REFACTOR_REGRESSION event handling."""
    
    def test_refactor_regression_handler_receives_payload(self):
        """Test handler receives and parses REFACTOR_REGRESSION payload."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        event = Event(
            type="REFACTOR_REGRESSION",
            payload={
                "refactor_type": "consolidation",
                "affected_files": ["file1.py", "file2.py"],
                "regression_type": "performance_latency"
            }
        )
        
        # Act
        orchestrator.handle_refactor_regression(event)
        
        # Assert
        assert len(orchestrator.active_sessions) == 1
        session = list(orchestrator.active_sessions.values())[0]
        assert session.trigger_event == "REFACTOR_REGRESSION"
        assert len(session.file_paths) == 2
    
    def test_refactor_regression_handler_injects_markers_in_all_affected_files(self):
        """Test handler injects markers in all affected files."""
        # Arrange
        event_bus = Mock()
        marker_engine = Mock()
        orchestrator = DebuggerOrchestrator(event_bus, marker_injection_engine=marker_engine)
        
        affected_files = ["file1.py", "file2.py", "file3.py"]
        event = Event(
            type="REFACTOR_REGRESSION",
            payload={
                "refactor_type": "consolidation",
                "affected_files": affected_files,
                "regression_type": "performance_latency"
            }
        )
        
        # Act
        orchestrator.handle_refactor_regression(event)
        
        # Assert
        assert marker_engine.inject.call_count == 3
        injected_files = [call[1]["file_path"] for call in marker_engine.inject.call_args_list]
        assert set(injected_files) == set(affected_files)


class TestGovernanceViolationHandler:
    """Test GOVERNANCE_VIOLATION event handling."""
    
    def test_governance_violation_handler_receives_payload(self):
        """Test handler receives and parses GOVERNANCE_VIOLATION payload."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        event = Event(
            type="GOVERNANCE_VIOLATION",
            payload={
                "rule_id": "CORE-008",
                "file_path": "example.py",
                "violation_details": {"line": 50, "message": "Missing type hints"}
            }
        )
        
        # Act
        orchestrator.handle_governance_violation(event)
        
        # Assert
        assert len(orchestrator.active_sessions) == 1
        session = list(orchestrator.active_sessions.values())[0]
        assert session.trigger_event == "GOVERNANCE_VIOLATION"
        assert session.file_paths == ["example.py"]
    
    def test_governance_violation_handler_calls_marker_injection(self):
        """Test handler calls MarkerInjectionEngine with governance strategy."""
        # Arrange
        event_bus = Mock()
        marker_engine = Mock()
        orchestrator = DebuggerOrchestrator(event_bus, marker_injection_engine=marker_engine)
        
        event = Event(
            type="GOVERNANCE_VIOLATION",
            payload={
                "rule_id": "CORE-008",
                "file_path": "example.py",
                "violation_details": {}
            }
        )
        
        # Act
        orchestrator.handle_governance_violation(event)
        
        # Assert
        marker_engine.inject.assert_called_once()
        call_args = marker_engine.inject.call_args
        assert call_args[1]["strategy"] == "governance_violation"


class TestAutoCleanup:
    """Test auto-cleanup on TESTS_PASSED event."""
    
    def test_tests_passed_triggers_auto_cleanup(self):
        """Test TESTS_PASSED event triggers auto-cleanup."""
        # Arrange
        event_bus = Mock()
        cleanup_manager = Mock()
        cleanup_manager.cleanup_resolved_sessions.return_value = ["session-1"]
        
        orchestrator = DebuggerOrchestrator(event_bus, auto_cleanup_manager=cleanup_manager)
        
        # Create a test session
        orchestrator.active_sessions["session-1"] = DebugSession(
            session_id="session-1",
            trigger_event="TEST_FAILURE",
            file_paths=["example.py"],
            created_at=datetime.now(),
            status="active"
        )
        
        event = Event(
            type="TESTS_PASSED",
            payload={"test_suite": "unit", "passed_count": 10}
        )
        
        # Act
        orchestrator.handle_tests_passed(event)
        
        # Assert
        cleanup_manager.cleanup_resolved_sessions.assert_called_once()
        assert orchestrator.active_sessions["session-1"].status == "resolved"


class TestIOrchestrator:
    """Test IOrchestrator interface compliance."""
    
    def test_get_name_returns_debugger_orchestrator(self):
        """Test get_name() returns correct orchestrator name."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Act
        name = orchestrator.get_name()
        
        # Assert
        assert name == "DebuggerOrchestrator"
    
    def test_get_intent_types_returns_empty_list(self):
        """Test get_intent_types() returns empty list (EventBus-driven)."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Act
        intent_types = orchestrator.get_intent_types()
        
        # Assert
        assert intent_types == []
    
    def test_can_handle_returns_false(self):
        """Test can_handle() returns False (EventBus-driven, no direct intent handling)."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Act
        result = orchestrator.can_handle(IntentType.IMPLEMENT)
        
        # Assert
        assert result is False
    
    def test_execute_list_sessions_returns_active_sessions(self):
        """Test execute('list_sessions') returns active debug sessions."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Create test session
        orchestrator.active_sessions["session-1"] = DebugSession(
            session_id="session-1",
            trigger_event="TEST_FAILURE",
            file_paths=["example.py"],
            created_at=datetime.now(),
            status="active"
        )
        
        # Act
        result = orchestrator.execute("list_sessions", {})
        
        # Assert
        assert "active_sessions" in result
        assert len(result["active_sessions"]) == 1
        assert result["active_sessions"][0]["session_id"] == "session-1"
    
    def test_execute_cleanup_session_removes_session(self):
        """Test execute('cleanup_session') marks session as resolved."""
        # Arrange
        event_bus = Mock()
        cleanup_manager = Mock()
        orchestrator = DebuggerOrchestrator(event_bus, auto_cleanup_manager=cleanup_manager)
        
        # Create test session
        orchestrator.active_sessions["session-1"] = DebugSession(
            session_id="session-1",
            trigger_event="TEST_FAILURE",
            file_paths=["example.py"],
            created_at=datetime.now(),
            status="active"
        )
        
        # Act
        result = orchestrator.execute("cleanup_session", {"session_id": "session-1"})
        
        # Assert
        assert result["status"] == "success"
        assert orchestrator.active_sessions["session-1"].status == "resolved"
        cleanup_manager.cleanup_session.assert_called_once_with("session-1")


class TestUtilityMethods:
    """Test utility methods."""
    
    def test_generate_session_id_format(self):
        """Test session ID generation format."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Act
        session_id = orchestrator._generate_session_id("test_failure")
        
        # Assert
        assert session_id.startswith("session-test_failure-")
        assert len(session_id) > len("session-test_failure-")
    
    def test_get_active_sessions_filters_by_status(self):
        """Test get_active_sessions() returns only active sessions."""
        # Arrange
        event_bus = Mock()
        orchestrator = DebuggerOrchestrator(event_bus)
        
        # Create active and resolved sessions
        orchestrator.active_sessions["session-1"] = DebugSession(
            session_id="session-1",
            trigger_event="TEST_FAILURE",
            file_paths=["file1.py"],
            created_at=datetime.now(),
            status="active"
        )
        orchestrator.active_sessions["session-2"] = DebugSession(
            session_id="session-2",
            trigger_event="TEST_FAILURE",
            file_paths=["file2.py"],
            created_at=datetime.now(),
            status="resolved"
        )
        
        # Act
        active = orchestrator.get_active_sessions()
        
        # Assert
        assert len(active) == 1
        assert active[0].session_id == "session-1"
