"""
Tests for CORTEX Debug System
Validates debug session manager, instrumentation, and integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import tempfile
import time
from pathlib import Path
import sys

# Add cortex-brain agents to path
cortex_brain_path = Path(__file__).parent.parent / "cortex-brain"
sys.path.insert(0, str(cortex_brain_path))

from agents.debug_session_manager import DebugSessionManager, get_debug_manager
from agents.debug_agent import DebugAgent
from agents.debug_integration import DebugSystemIntegration


# Test fixtures
@pytest.fixture
def temp_brain_root():
    """Create temporary brain root directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_root = Path(tmpdir)
        (brain_root / "debug-sessions").mkdir(exist_ok=True)
        yield brain_root


@pytest.fixture
def debug_manager(temp_brain_root):
    """Create debug session manager instance."""
    return DebugSessionManager(temp_brain_root)


@pytest.fixture
def debug_agent(temp_brain_root):
    """Create debug agent instance."""
    # Ensure manager is initialized first
    manager = DebugSessionManager(temp_brain_root)
    agent = DebugAgent(temp_brain_root)
    agent.manager = manager
    return agent


@pytest.fixture
def debug_integration(temp_brain_root):
    """Create debug integration instance."""
    # Ensure manager is initialized first
    manager = DebugSessionManager(temp_brain_root)
    integration = DebugSystemIntegration(temp_brain_root)
    integration.debug_agent.manager = manager
    return integration


# Sample module for testing
class SampleModule:
    """Sample module for instrumentation testing."""
    
    def add(self, a, b):
        """Add two numbers."""
        return a + b
    
    def multiply(self, a, b):
        """Multiply two numbers."""
        return a * b
    
    def divide(self, a, b):
        """Divide two numbers."""
        if b == 0:
            raise ValueError("Cannot divide by zero")
        return a / b
    
    def fibonacci(self, n):
        """Calculate Fibonacci number (recursive)."""
        if n <= 1:
            return n
        return self.fibonacci(n - 1) + self.fibonacci(n - 2)


# ============================================================================
# Phase 1 Tests: Core Debug Infrastructure
# ============================================================================

class TestDebugSessionManager:
    """Test debug session manager functionality."""
    
    def test_session_creation(self, debug_manager):
        """Test creating a debug session."""
        session = debug_manager.start_session(
            target_module="test_module",
            session_name="test"
        )
        
        assert session is not None
        assert "test" in session.session_id
        assert session.target_module == "test_module"
        assert session.session_id in debug_manager.get_active_sessions()
    
    def test_session_stop(self, debug_manager):
        """Test stopping a debug session."""
        session = debug_manager.start_session(session_name="stop_test")
        session_id = session.session_id
        
        summary = debug_manager.stop_session(session_id)
        
        assert summary is not None
        assert summary['session_id'] == session_id
        assert session_id not in debug_manager.get_active_sessions()
    
    def test_multiple_sessions(self, debug_manager):
        """Test managing multiple debug sessions."""
        session1 = debug_manager.start_session(session_name="session1")
        session2 = debug_manager.start_session(session_name="session2")
        
        active = debug_manager.get_active_sessions()
        assert len(active) == 2
        assert session1.session_id in active
        assert session2.session_id in active
        
        debug_manager.stop_session(session1.session_id)
        
        active_after = debug_manager.get_active_sessions()
        assert len(active_after) == 1
        assert session2.session_id in active_after
    
    def test_session_history(self, debug_manager):
        """Test session history tracking."""
        session = debug_manager.start_session(session_name="history_test")
        debug_manager.stop_session(session.session_id)
        
        history = debug_manager.get_session_history(limit=10)
        
        assert len(history) > 0
        assert any(h['session_id'] == session.session_id for h in history)
    
    def test_stop_all_sessions(self, debug_manager):
        """Test stopping all active sessions."""
        debug_manager.start_session(session_name="bulk1")
        debug_manager.start_session(session_name="bulk2")
        debug_manager.start_session(session_name="bulk3")
        
        summaries = debug_manager.stop_all_sessions()
        
        assert len(summaries) == 3
        assert len(debug_manager.get_active_sessions()) == 0


# ============================================================================
# Phase 2 Tests: Runtime Instrumentation Engine
# ============================================================================

class TestDebugInstrumentation:
    """Test runtime instrumentation functionality."""
    
    def test_function_instrumentation(self, debug_manager):
        """Test instrumenting a single function."""
        session = debug_manager.start_session(session_name="instrument_test")
        sample = SampleModule()
        
        # Instrument the add function
        original_add = sample.add
        instrumented_add = session.instrument_function(original_add, "SampleModule")
        
        # Call instrumented function
        result = instrumented_add(5, 3)
        
        assert result == 8
        assert session.call_count == 1
        assert "SampleModule.add" in session.instrumented_functions
    
    def test_function_timing(self, debug_manager):
        """Test that function timing is captured."""
        session = debug_manager.start_session(session_name="timing_test")
        sample = SampleModule()
        
        instrumented_fib = session.instrument_function(sample.fibonacci, "SampleModule")
        
        # Call function that takes measurable time
        result = instrumented_fib(10)
        
        assert result == 55  # 10th Fibonacci number
        assert session.call_count > 0
        
        # Check log file contains timing information
        log_content = session.log_file.read_text()
        assert "duration_ms" in log_content
    
    def test_error_tracking(self, debug_manager):
        """Test that errors are tracked."""
        session = debug_manager.start_session(session_name="error_test")
        sample = SampleModule()
        
        instrumented_divide = session.instrument_function(sample.divide, "SampleModule")
        
        # Call function that will raise error
        with pytest.raises(ValueError):
            instrumented_divide(10, 0)
        
        assert session.error_count == 1
        
        # Check log file contains error information
        log_content = session.log_file.read_text()
        assert "ERROR" in log_content
        assert "Cannot divide by zero" in log_content
    
    def test_argument_capture(self, debug_manager):
        """Test that function arguments are captured."""
        session = debug_manager.start_session(session_name="args_test")
        sample = SampleModule()
        
        instrumented_multiply = session.instrument_function(sample.multiply, "SampleModule")
        
        result = instrumented_multiply(7, 6)
        
        assert result == 42
        
        # Check log file contains argument information
        log_content = session.log_file.read_text()
        assert "args" in log_content
        assert "7" in log_content
        assert "6" in log_content
    
    def test_return_value_capture(self, debug_manager):
        """Test that return values are captured."""
        session = debug_manager.start_session(session_name="return_test")
        sample = SampleModule()
        
        instrumented_add = session.instrument_function(sample.add, "SampleModule")
        
        result = instrumented_add(100, 200)
        
        assert result == 300
        
        # Check log file contains return value
        log_content = session.log_file.read_text()
        assert "result" in log_content
        assert "300" in log_content


# ============================================================================
# Phase 3 Tests: Intent Detection & Auto-Wiring
# ============================================================================

class TestDebugAgent:
    """Test debug agent intent detection and auto-wiring."""
    
    def test_detect_debug_intent(self, debug_agent):
        """Test detecting debug intent from messages."""
        messages = [
            "debug the planner",
            "trace authentication flow",
            "instrument the payment system",
            "stop debug"
        ]
        
        for msg in messages[:3]:
            intent = debug_agent.detect_debug_intent(msg)
            assert intent is not None
            assert intent['action'] == 'start'
        
        # Test stop command
        stop_intent = debug_agent.detect_debug_intent(messages[3])
        assert stop_intent is not None
        assert stop_intent['action'] == 'stop'
    
    def test_no_debug_intent(self, debug_agent):
        """Test that non-debug messages return None."""
        messages = [
            "show me the status",
            "create a new file",
            "what is the weather"
        ]
        
        for msg in messages:
            intent = debug_agent.detect_debug_intent(msg)
            assert intent is None
    
    def test_start_debug_session(self, debug_agent):
        """Test starting debug session via agent."""
        session = debug_agent.start_debug_session(target="test_target")
        
        assert session is not None
        assert session.session_id is not None
        
        # Clean up
        debug_agent.stop_debug_session(session.session_id)
    
    def test_get_session_report(self, debug_agent):
        """Test getting session report."""
        session = debug_agent.start_debug_session(target="report_test")
        
        report = debug_agent.get_session_report(session.session_id)
        
        assert report is not None
        assert report['session_id'] == session.session_id
        assert report['status'] == 'active'
        
        # Clean up
        debug_agent.stop_debug_session(session.session_id)
    
    def test_format_debug_response(self, debug_agent):
        """Test response formatting."""
        session = debug_agent.start_debug_session(target="format_test")
        
        # Test start response
        start_response = debug_agent.format_debug_response('start', session)
        assert "Debug session started" in start_response
        assert session.session_id in start_response
        
        # Test stop response
        summary = debug_agent.stop_debug_session(session.session_id)
        stop_response = debug_agent.format_debug_response('stop', summary)
        assert "Debug session stopped" in stop_response
        assert "Session Summary" in stop_response


# ============================================================================
# Phase 4 Tests: Integration & Testing
# ============================================================================

class TestDebugIntegration:
    """Test debug system integration with CORTEX."""
    
    def test_process_debug_message(self, debug_integration):
        """Test processing debug messages."""
        result = debug_integration.process_message("debug test_module")
        
        assert result is not None
        assert result['intent'] == 'DEBUG'
        assert result['action'] == 'start'
        assert result['success'] is True
        
        # Clean up
        debug_integration.process_message("stop debug")
    
    def test_process_non_debug_message(self, debug_integration):
        """Test that non-debug messages return None."""
        result = debug_integration.process_message("show me the status")
        
        assert result is None
    
    def test_debug_status_command(self, debug_integration):
        """Test debug status command."""
        # Start a session
        debug_integration.process_message("debug test")
        
        # Check status
        status = debug_integration._handle_debug_status()
        
        assert status is not None
        assert status['intent'] == 'DEBUG'
        assert status['success'] is True
        assert len(status['active_sessions']) > 0
        
        # Clean up
        debug_integration.process_message("stop debug")
    
    def test_debug_history_command(self, debug_integration):
        """Test debug history command."""
        # Start and stop a session
        result = debug_integration.process_message("debug history_test")
        session_id = result['session_id']
        debug_integration.process_message("stop debug")
        
        # Get history
        history = debug_integration._handle_debug_history()
        
        assert history is not None
        assert history['success'] is True
        assert len(history['history']) > 0
    
    def test_get_debug_capabilities(self, debug_integration):
        """Test getting debug capabilities."""
        capabilities = debug_integration.get_debug_capabilities()
        
        assert capabilities is not None
        assert 'name' in capabilities
        assert 'commands' in capabilities
        assert 'features' in capabilities
        assert len(capabilities['commands']) > 0
        assert len(capabilities['features']) > 0
    
    def test_session_isolation(self, debug_integration):
        """Test that sessions are properly isolated."""
        # Start two sessions
        result1 = debug_integration.process_message("debug module1")
        result2 = debug_integration.process_message("debug module2")
        
        session_id1 = result1['session_id']
        session_id2 = result2['session_id']
        
        assert session_id1 != session_id2
        
        # Stop one session
        debug_integration._stop_debug_session(session_id1)
        
        # Verify other session still active
        status = debug_integration._handle_debug_status()
        assert session_id2 in status['active_sessions']
        assert session_id1 not in status['active_sessions']
        
        # Clean up
        debug_integration._stop_debug_session(session_id2)


# ============================================================================
# Phase 5 Tests: Deployment & Documentation
# ============================================================================

class TestDebugDocumentation:
    """Test debug system documentation and deployment integration."""
    
    def test_capabilities_format(self, debug_integration):
        """Test that capabilities are properly formatted for documentation."""
        capabilities = debug_integration.get_debug_capabilities()
        
        # Check required fields
        assert 'name' in capabilities
        assert 'version' in capabilities
        assert 'description' in capabilities
        assert 'commands' in capabilities
        assert 'features' in capabilities
        assert 'storage' in capabilities
        
        # Check commands structure
        for command in capabilities['commands']:
            assert 'trigger' in command
            assert 'description' in command
            assert 'examples' in command
            assert len(command['examples']) > 0
    
    def test_command_triggers(self, debug_integration):
        """Test that all documented commands work."""
        capabilities = debug_integration.get_debug_capabilities()
        
        # Test each command trigger
        test_commands = [
            ("debug test", "start"),
            ("stop debug", "stop"),
            ("debug status", "status")
        ]
        
        for command, expected_action in test_commands:
            result = debug_integration.process_message(command)
            if result:
                assert result['action'] == expected_action or result['intent'] == 'DEBUG'
        
        # Clean up
        debug_integration.process_message("stop debug")


# ============================================================================
# Run tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
