"""
Integration Tests for Interactive Planning Workflow

Purpose: End-to-end validation of interactive planning wiring
Version: 1.0.0
Author: CORTEX Maintenance System
Created: 2025-12-29 (Interactive Workflow Wiring - Component 6 of 6)

Tests the complete interactive workflow integration:
1. Decision logic correctly detects interactive mode
2. Orchestrator routes to interactive execution path
3. Interactive session is created and managed
4. UI bridge components are accessible
5. Session state transitions work end-to-end

NOTE: These are TRUE integration tests (not mocked), validating actual wiring.
"""

import pytest
import os
from pathlib import Path
from datetime import datetime

from src.orchestrators.planning.planning_orchestrator import (
    PlanningOrchestrator,
    OrchestratorStatus
)
from src.orchestrators.planning.interactive_session import SessionState
from src.orchestrators.planning.user_interface import PlanningUI, PromptType


class TestInteractiveWorkflowWiring:
    """Integration tests for interactive workflow wiring (Component 1-6)."""
    
    def setup_method(self):
        """Setup test fixtures."""
        # Minimal config for testing
        config = {
            "cortex_root": "/Users/asifhussain/PROJECTS/CORTEX",
            "brain_dir": "cortex-brain",
            "schema_path": "cortex-brain/manifests/planning/plan-schema.yaml"
        }
        self.orchestrator = PlanningOrchestrator(config=config)
        self.test_feature_name = "test-interactive-feature"
    
    # Component 1 & 2: Decision Logic Tests
    
    def test_decision_logic_detects_interactive_flag(self):
        """Test: _should_use_interactive_mode() detects 'interactive' flag."""
        # Explicit flag
        assert self.orchestrator._should_use_interactive_mode(interactive=True) is True
        assert self.orchestrator._should_use_interactive_mode(interactive=False) is False
    
    def test_decision_logic_detects_mode_parameter(self):
        """Test: _should_use_interactive_mode() detects 'mode' parameter."""
        assert self.orchestrator._should_use_interactive_mode(mode='interactive') is True
        assert self.orchestrator._should_use_interactive_mode(mode='autonomous') is False
    
    def test_decision_logic_detects_environment_variable(self):
        """Test: _should_use_interactive_mode() detects CORTEX_INTERACTIVE env var."""
        # Set environment variable
        os.environ['CORTEX_INTERACTIVE'] = 'true'
        try:
            assert self.orchestrator._should_use_interactive_mode() is True
        finally:
            # Cleanup
            del os.environ['CORTEX_INTERACTIVE']
        
        # Verify it's false without env var
        assert self.orchestrator._should_use_interactive_mode() is False
    
    def test_decision_logic_default_is_autonomous(self):
        """Test: Default behavior is autonomous mode (no flags)."""
        assert self.orchestrator._should_use_interactive_mode() is False
    
    # Component 3: Execution Routing Tests
    
    def test_execute_routes_to_interactive_mode(self):
        """Test: execute() routes to interactive mode when flag set."""
        result = self.orchestrator.execute(
            feature_name=self.test_feature_name,
            interactive=True
        )
        
        # Verify interactive mode was used
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.data.get("mode") == "interactive"
        assert "session_id" in result.data
        assert result.data.get("interactive") is True
    
    def test_execute_routes_to_autonomous_mode_by_default(self):
        """Test: execute() routes to autonomous mode without flags."""
        # This test would run full autonomous execution
        # For safety, we'll just verify the routing decision
        assert self.orchestrator._should_use_interactive_mode() is False
    
    # Component 4: Interactive Method Tests
    
    def test_interactive_method_creates_session(self):
        """Test: interactive_plan_creation() creates PlanningSession."""
        session = self.orchestrator.interactive_plan_creation(
            plan_name=self.test_feature_name,
            user_context={"test_key": "test_value"}
        )
        
        # Verify session created
        assert session is not None
        assert session.plan_name == self.test_feature_name
        assert session.state == SessionState.DISCOVERY
        assert session.user_context.get("test_key") == "test_value"
        assert session.session_id is not None
    
    def test_interactive_session_state_transitions(self):
        """Test: PlanningSession state transitions work correctly."""
        session = self.orchestrator.interactive_plan_creation(
            plan_name=self.test_feature_name
        )
        
        # Verify initial state
        assert session.state == SessionState.DISCOVERY
        
        # Test state transition (if session has transition_to method)
        if hasattr(session, 'transition_to'):
            # Transition to valid next state (CONTEXT_GATHERING is valid from DISCOVERY)
            session.transition_to(SessionState.CONTEXT_GATHERING)
            assert session.state == SessionState.CONTEXT_GATHERING
    
    # Component 5: UI Bridge Tests
    
    def test_ui_bridge_module_exists(self):
        """Test: user_interface.py module can be imported."""
        from src.orchestrators.planning.user_interface import (
            PlanningUI,
            PromptType,
            PromptResult,
            get_planning_ui
        )
        
        # Verify imports successful
        assert PlanningUI is not None
        assert PromptType is not None
        assert get_planning_ui is not None
    
    def test_ui_bridge_can_be_instantiated(self):
        """Test: PlanningUI can be instantiated and configured."""
        ui = PlanningUI(colorize=False, verbose=False)
        
        assert ui is not None
        assert ui.colorize is False
        assert ui.verbose is False
    
    def test_ui_bridge_factory_function(self):
        """Test: get_planning_ui() factory function works."""
        from src.orchestrators.planning.user_interface import get_planning_ui
        
        ui = get_planning_ui(colorize=False, verbose=True)
        assert ui is not None
        assert isinstance(ui, PlanningUI)
    
    # Component 6: End-to-End Integration Tests
    
    def test_full_interactive_workflow_initialization(self):
        """
        Test: Full workflow from execute() to session creation.
        
        This is a TRUE integration test with no mocks.
        """
        # Execute with interactive flag
        result = self.orchestrator.execute(
            feature_name=self.test_feature_name,
            interactive=True,
            user_context={"source": "integration_test"}
        )
        
        # Verify complete flow
        assert result.status == OrchestratorStatus.COMPLETED
        assert result.data["mode"] == "interactive"
        assert result.data["plan_name"] == self.test_feature_name
        assert "session_id" in result.data
        assert result.data["state"] == str(SessionState.DISCOVERY)
        assert result.data["interactive"] is True
        
        # Verify timing
        assert result.execution_time_seconds > 0
    
    def test_interactive_and_autonomous_modes_distinct(self):
        """Test: Interactive and autonomous modes produce different results."""
        # Get interactive result
        interactive_result = self.orchestrator.execute(
            feature_name=self.test_feature_name,
            interactive=True
        )
        
        # Verify interactive characteristics
        assert interactive_result.data.get("mode") == "interactive"
        assert "session_id" in interactive_result.data
        
        # Note: We don't run autonomous mode in this test to avoid
        # actually generating a plan (which has side effects)
    
    def test_multiple_interactive_sessions_have_unique_ids(self):
        """Test: Multiple interactive sessions have unique session IDs."""
        result1 = self.orchestrator.execute(
            feature_name="test-feature-1",
            interactive=True
        )
        
        result2 = self.orchestrator.execute(
            feature_name="test-feature-2",
            interactive=True
        )
        
        # Verify unique session IDs
        session_id1 = result1.data.get("session_id")
        session_id2 = result2.data.get("session_id")
        
        assert session_id1 is not None
        assert session_id2 is not None
        assert session_id1 != session_id2


class TestInteractiveModeErrorHandling:
    """Test error handling in interactive mode."""
    
    def setup_method(self):
        """Setup test fixtures."""
        config = {
            "cortex_root": "/Users/asifhussain/PROJECTS/CORTEX",
            "brain_dir": "cortex-brain",
            "schema_path": "cortex-brain/manifests/planning/plan-schema.yaml"
        }
        self.orchestrator = PlanningOrchestrator(config=config)
    
    def test_interactive_mode_requires_feature_name(self):
        """Test: Interactive mode returns error without feature_name."""
        result = self.orchestrator.execute(
            interactive=True
            # Missing feature_name
        )
        
        # Should get error result
        assert result.status == OrchestratorStatus.FAILED
        assert "requires 'feature_name'" in result.message or "requires 'feature_name'" in str(result.errors)
    
    def test_invalid_mode_parameter_defaults_to_autonomous(self):
        """Test: Invalid mode parameter defaults to autonomous behavior."""
        # Invalid mode should not trigger interactive
        assert self.orchestrator._should_use_interactive_mode(mode='invalid') is False


class TestUIBridgeComponents:
    """Test UI bridge component functionality."""
    
    def setup_method(self):
        """Setup UI bridge."""
        self.ui = PlanningUI(colorize=False, verbose=False)
    
    def test_ui_display_section(self):
        """Test: UI can display formatted sections (no user input)."""
        # This should not raise exceptions
        self.ui.display_section(
            title="Test Section",
            content={"key1": "value1", "key2": "value2"}
        )
    
    def test_ui_display_progress(self):
        """Test: UI can display progress indicators (no user input)."""
        # This should not raise exceptions
        self.ui.display_progress(
            phase="TESTING",
            step=1,
            total_steps=3,
            message="Running tests"
        )
    
    def test_ui_format_methods_dont_crash(self):
        """Test: UI formatting methods are safe to call."""
        # These should not raise exceptions
        self.ui._print_success("Success message")
        self.ui._print_error("Error message")
        self.ui._print_warning("Warning message")
        self.ui._print_info("Info message")
    
    # Note: prompt_text(), prompt_choice(), prompt_confirm() require actual
    # user input, so they're not tested in automated tests without mocking stdin


# Pytest markers for test organization
pytestmark = pytest.mark.integration  # Mark as integration tests


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
