"""
Unit Tests for Debug MCP Tools

Purpose:
    Validate MCP tool exposure for DebuggerOrchestrator capabilities.
    Tests manual injection, session listing, and cleanup operations.

Authority:
    - ENH-089 (EventBus-Driven Debugger) Stage 5
    - WAVE-R Execution Plan

AC-ID: AC-WAVE-R-007
"""

import pytest
from unittest.mock import Mock, MagicMock
from datetime import datetime

from cortex.mcp.tools.debug_tools import DebugMCPTools, register_debug_tools
from cortex.core.event_bus import EventBus, Event
from cortex.orchestrators.support.debugger_orchestrator import DebugSession


class TestDebugMCPTools:
    """Unit tests for DebugMCPTools."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.event_bus = Mock(spec=EventBus)
        self.orchestrator = Mock()
        self.tools = DebugMCPTools(self.event_bus, self.orchestrator)
    
    def test_auto_inject_test_failure(self):
        """Test manual TEST_FAILURE marker injection."""
        # Setup
        self.orchestrator.get_active_sessions.return_value = [
            DebugSession(
                session_id="session-test_failure-123",
                trigger_event="TEST_FAILURE",
                file_paths=["/tmp/test.py"],
                created_at=datetime.now(),
                status="active"
            )
        ]
        
        # Execute
        result = self.tools.auto_inject(
            trigger_type="test_failure",
            file_path="/tmp/test.py",
            line_number=42,
            context={"test_name": "test_example", "failure_reason": "AssertionError"}
        )
        
        # Verify event published
        assert self.event_bus.publish.called
        published_event = self.event_bus.publish.call_args[0][0]
        assert published_event.type == "TEST_FAILURE"
        assert published_event.payload["file_path"] == "/tmp/test.py"
        assert published_event.payload["line_number"] == 42
        assert published_event.payload["test_name"] == "test_example"
        
        # Verify result
        assert result["status"] == "success"
        assert result["session_id"] == "session-test_failure-123"
    
    def test_auto_inject_invalid_trigger(self):
        """Test auto_inject with invalid trigger type."""
        result = self.tools.auto_inject(
            trigger_type="invalid_trigger",
            file_path="/tmp/test.py",
            line_number=42,
            context={}
        )
        
        assert result["status"] == "error"
        assert "Invalid trigger_type" in result["message"]
        assert not self.event_bus.publish.called
    
    def test_auto_inject_refactor_regression(self):
        """Test manual REFACTOR_REGRESSION marker injection."""
        # Setup
        self.orchestrator.get_active_sessions.return_value = [
            DebugSession(
                session_id="session-refactor_regression-456",
                trigger_event="REFACTOR_REGRESSION",
                file_paths=["/tmp/refactored.py"],
                created_at=datetime.now(),
                status="active"
            )
        ]
        
        # Execute
        result = self.tools.auto_inject(
            trigger_type="refactor_regression",
            file_path="/tmp/refactored.py",
            line_number=10,
            context={"regression_type": "performance"}
        )
        
        # Verify event published
        assert self.event_bus.publish.called
        published_event = self.event_bus.publish.call_args[0][0]
        assert published_event.type == "REFACTOR_REGRESSION"
        assert published_event.payload["regression_type"] == "performance"
        
        # Verify result
        assert result["status"] == "success"
    
    def test_list_sessions_all(self):
        """Test listing all debug sessions."""
        # Setup
        self.orchestrator.get_active_sessions.return_value = [
            DebugSession(
                session_id="session-1",
                trigger_event="TEST_FAILURE",
                file_paths=["/tmp/test1.py"],
                created_at=datetime(2026, 2, 13, 6, 30, 0),
                status="active"
            ),
            DebugSession(
                session_id="session-2",
                trigger_event="GOVERNANCE_VIOLATION",
                file_paths=["/tmp/test2.py"],
                created_at=datetime(2026, 2, 13, 6, 31, 0),
                status="resolved"
            )
        ]
        
        # Execute
        result = self.tools.list_sessions(status_filter="all")
        
        # Verify
        assert result["status"] == "success"
        assert result["count"] == 2
        assert len(result["sessions"]) == 2
        assert result["sessions"][0]["session_id"] == "session-1"
        assert result["sessions"][1]["session_id"] == "session-2"
    
    def test_list_sessions_active_filter(self):
        """Test listing sessions with active status filter."""
        # Setup
        self.orchestrator.get_active_sessions.return_value = [
            DebugSession(
                session_id="session-1",
                trigger_event="TEST_FAILURE",
                file_paths=["/tmp/test1.py"],
                created_at=datetime(2026, 2, 13, 6, 30, 0),
                status="active"
            ),
            DebugSession(
                session_id="session-2",
                trigger_event="GOVERNANCE_VIOLATION",
                file_paths=["/tmp/test2.py"],
                created_at=datetime(2026, 2, 13, 6, 31, 0),
                status="resolved"
            )
        ]
        
        # Execute
        result = self.tools.list_sessions(status_filter="active")
        
        # Verify
        assert result["status"] == "success"
        assert result["count"] == 1
        assert result["sessions"][0]["status"] == "active"
    
    def test_cleanup_specific_session(self):
        """Test cleanup of specific session."""
        # Setup
        self.orchestrator.auto_cleanup_manager = Mock()
        
        # Execute
        result = self.tools.cleanup(session_id="session-test_failure-123")
        
        # Verify
        assert result["status"] == "success"
        assert result["removed_markers"] == 1
        self.orchestrator.auto_cleanup_manager.cleanup_session.assert_called_once_with(
            "session-test_failure-123"
        )
    
    def test_cleanup_all_resolved(self):
        """Test cleanup of all resolved sessions."""
        # Setup
        self.orchestrator.get_active_sessions.return_value = [
            DebugSession(
                session_id="session-1",
                trigger_event="TEST_FAILURE",
                file_paths=["/tmp/test1.py"],
                created_at=datetime.now(),
                status="active"
            ),
            DebugSession(
                session_id="session-2",
                trigger_event="TEST_FAILURE",
                file_paths=["/tmp/test2.py"],
                created_at=datetime.now(),
                status="resolved"
            ),
            DebugSession(
                session_id="session-3",
                trigger_event="GOVERNANCE_VIOLATION",
                file_paths=["/tmp/test3.py"],
                created_at=datetime.now(),
                status="resolved"
            )
        ]
        self.orchestrator.auto_cleanup_manager = Mock()
        
        # Execute
        result = self.tools.cleanup(cleanup_all=True)
        
        # Verify
        assert result["status"] == "success"
        assert result["removed_markers"] == 2
        assert self.orchestrator.auto_cleanup_manager.cleanup_session.call_count == 2
    
    def test_cleanup_no_parameters(self):
        """Test cleanup with no parameters returns error."""
        result = self.tools.cleanup()
        
        assert result["status"] == "error"
        assert "Must provide session_id" in result["message"]


class TestMCPToolRegistration:
    """Unit tests for MCP tool registration."""
    
    def test_register_debug_tools(self):
        """Test registration returns correct tool structure."""
        # Setup
        event_bus = Mock(spec=EventBus)
        orchestrator = Mock()
        
        # Execute
        registry = register_debug_tools(event_bus, orchestrator)
        
        # Verify
        assert "cortex_debug_auto_inject" in registry
        assert "cortex_debug_list_sessions" in registry
        assert "cortex_debug_cleanup" in registry
        
        # Verify tool structure
        auto_inject = registry["cortex_debug_auto_inject"]
        assert "handler" in auto_inject
        assert "description" in auto_inject
        assert "parameters" in auto_inject
        assert "trigger_type" in auto_inject["parameters"]
        assert "file_path" in auto_inject["parameters"]
        assert "line_number" in auto_inject["parameters"]
    
    def test_registered_handlers_callable(self):
        """Test registered handlers are callable."""
        # Setup
        event_bus = Mock(spec=EventBus)
        orchestrator = Mock()
        orchestrator.get_active_sessions.return_value = []
        orchestrator.auto_cleanup_manager = Mock()
        
        # Execute
        registry = register_debug_tools(event_bus, orchestrator)
        
        # Verify handlers are callable
        assert callable(registry["cortex_debug_auto_inject"]["handler"])
        assert callable(registry["cortex_debug_list_sessions"]["handler"])
        assert callable(registry["cortex_debug_cleanup"]["handler"])
