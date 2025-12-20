"""
Unit tests for State Machine Engine
Tests FSM transitions, guards, actions, history, checkpoints
"""

import pytest
from orchestration_3_0.core.state_machine import (
    StateMachine,
    StateTransition,
    TransitionResult,
    create_basic_orchestrator_fsm
)


class TestStateMachine:
    """Test StateMachine core functionality."""
    
    def test_initialization(self):
        """Test FSM initializes with correct initial state."""
        fsm = StateMachine(initial_state="INITIALIZED", orchestrator_name="TestOrch")
        assert fsm.current_state == "INITIALIZED"
        assert fsm.orchestrator_name == "TestOrch"
        # History is empty until first transition
        assert len(fsm.history) == 0
    
    def test_register_transition(self):
        """Test transition registration."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "EXECUTING")
        
        can_transition, _ = fsm.can_transition_to("EXECUTING")
        assert can_transition is True
    
    def test_successful_transition(self):
        """Test successful state transition."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "EXECUTING")
        
        result = fsm.transition_to("EXECUTING")
        
        assert result == TransitionResult.SUCCESS
        assert fsm.current_state == "EXECUTING"
        assert len(fsm.history) == 1  # One transition recorded
    
    def test_invalid_transition(self):
        """Test invalid state transition is rejected."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        # No transition registered from INITIALIZED to COMPLETED
        
        result = fsm.transition_to("COMPLETED")
        
        assert result == TransitionResult.INVALID_TRANSITION
        assert fsm.current_state == "INITIALIZED"  # State unchanged
    
    def test_guard_condition_blocks_transition(self):
        """Test guard condition prevents invalid transition."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        
        # Guard that always fails
        def failing_guard() -> bool:
            return False
        
        fsm.register_transition(
            "INITIALIZED", 
            "EXECUTING",
            guard_conditions=[failing_guard]
        )
        
        result = fsm.transition_to("EXECUTING")
        
        assert result == TransitionResult.GUARD_FAILED
        assert fsm.current_state == "INITIALIZED"
    
    def test_guard_condition_allows_transition(self):
        """Test guard condition allows valid transition."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        
        # Guard that always passes
        def passing_guard() -> bool:
            return True
        
        fsm.register_transition(
            "INITIALIZED",
            "EXECUTING",
            guard_conditions=[passing_guard]
        )
        
        result = fsm.transition_to("EXECUTING")
        
        assert result == TransitionResult.SUCCESS
        assert fsm.current_state == "EXECUTING"
    
    def test_action_executes_on_transition(self):
        """Test action hook executes during transition."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        action_executed = {"flag": False}
        
        def test_action():
            action_executed["flag"] = True
        
        fsm.register_transition(
            "INITIALIZED",
            "EXECUTING",
            actions=[test_action]
        )
        
        fsm.transition_to("EXECUTING")
        
        assert action_executed["flag"] is True
    
    def test_action_exception_fails_transition(self):
        """Test action exception causes transition failure."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        
        def failing_action():
            raise ValueError("Action failed")
        
        fsm.register_transition(
            "INITIALIZED",
            "EXECUTING",
            actions=[failing_action]
        )
        
        result = fsm.transition_to("EXECUTING")
        
        assert result == TransitionResult.ACTION_FAILED
        assert fsm.current_state == "INITIALIZED"
    
    def test_state_history_tracking(self):
        """Test state history records all transitions."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "VALIDATING_DOR")
        fsm.register_transition("VALIDATING_DOR", "EXECUTING")
        
        fsm.transition_to("VALIDATING_DOR")
        fsm.transition_to("EXECUTING")
        
        assert len(fsm.history) == 3
        assert fsm.history[0].state == "INITIALIZED"
        assert fsm.history[1].state == "VALIDATING_DOR"
        assert fsm.history[2].state == "EXECUTING"
    
    def test_checkpoint_creation(self):
        """Test checkpoint saves current state."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "EXECUTING")
        fsm.transition_to("EXECUTING")
        
        checkpoint = fsm.create_checkpoint()
        
        assert checkpoint["state"] == "EXECUTING"
        assert checkpoint["orchestrator_name"] == "TestOrch"
        assert "timestamp" in checkpoint
        assert "history_length" in checkpoint
    
    def test_rollback_to_checkpoint(self):
        """Test rollback restores previous state."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "EXECUTING")
        fsm.register_transition("EXECUTING", "COMPLETED")
        
        fsm.transition_to("EXECUTING")
        checkpoint = fsm.create_checkpoint()
        
        fsm.transition_to("COMPLETED")
        assert fsm.current_state == "COMPLETED"
        
        fsm.rollback_to_checkpoint(checkpoint)
        assert fsm.current_state == "EXECUTING"
    
    def test_can_transition_to(self):
        """Test can_transition_to predicate."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "EXECUTING")
        
        assert fsm.can_transition_to("EXECUTING") is True
        assert fsm.can_transition_to("COMPLETED") is False
    
    def test_get_valid_transitions(self):
        """Test get_valid_transitions returns all registered transitions."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "VALIDATING_DOR")
        fsm.register_transition("INITIALIZED", "FAILED")
        
        transitions = fsm.get_valid_transitions("INITIALIZED")
        
        assert "VALIDATING_DOR" in transitions
        assert "FAILED" in transitions
        assert len(transitions) == 2


class TestBasicOrchestratorFSM:
    """Test create_basic_orchestrator_fsm factory function."""
    
    def test_factory_creates_valid_fsm(self):
        """Test factory function creates FSM with standard states."""
        fsm = create_basic_orchestrator_fsm("TestOrch")
        
        assert fsm.current_state == "INITIALIZED"
        assert fsm.orchestrator_name == "TestOrch"
    
    def test_standard_transitions_registered(self):
        """Test standard orchestrator transitions are registered."""
        fsm = create_basic_orchestrator_fsm("TestOrch")
        
        # Test standard workflow path
        assert fsm.can_transition_to("VALIDATING_DOR")
        
        fsm.transition_to("VALIDATING_DOR")
        assert fsm.can_transition_to("EXECUTING")
        
        fsm.transition_to("EXECUTING")
        assert fsm.can_transition_to("VALIDATING_DOD")
        
        fsm.transition_to("VALIDATING_DOD")
        assert fsm.can_transition_to("COMPLETED")
    
    def test_failure_transitions_registered(self):
        """Test failure transitions from any state."""
        fsm = create_basic_orchestrator_fsm("TestOrch")
        
        # Should be able to transition to FAILED from INITIALIZED
        assert fsm.can_transition_to("FAILED")
        
        # Should be able to transition to FAILED from EXECUTING
        fsm.register_transition("INITIALIZED", "EXECUTING")
        fsm.transition_to("EXECUTING")
        assert fsm.can_transition_to("FAILED")
    
    def test_complete_workflow_execution(self):
        """Test complete workflow from INITIALIZED to COMPLETED."""
        fsm = create_basic_orchestrator_fsm("TestOrch")
        
        result1 = fsm.transition_to("VALIDATING_DOR")
        result2 = fsm.transition_to("EXECUTING")
        result3 = fsm.transition_to("VALIDATING_DOD")
        result4 = fsm.transition_to("COMPLETED")
        
        assert result1 == TransitionResult.SUCCESS
        assert result2 == TransitionResult.SUCCESS
        assert result3 == TransitionResult.SUCCESS
        assert result4 == TransitionResult.SUCCESS
        assert fsm.current_state == "COMPLETED"
        assert len(fsm.history) == 5  # INIT + 4 transitions


class TestTransitionEdgeCases:
    """Test edge cases and error handling."""
    
    def test_transition_to_same_state(self):
        """Test transitioning to current state."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        fsm.register_transition("INITIALIZED", "INITIALIZED")  # Self-loop
        
        result = fsm.transition_to("INITIALIZED")
        
        assert result == TransitionResult.SUCCESS
        assert fsm.current_state == "INITIALIZED"
    
    def test_multiple_guards_all_must_pass(self):
        """Test all guard conditions must pass."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        
        def guard1() -> bool:
            return True
        
        def guard2() -> bool:
            return False  # This one fails
        
        fsm.register_transition(
            "INITIALIZED",
            "EXECUTING",
            guard_conditions=[guard1, guard2]
        )
        
        result = fsm.transition_to("EXECUTING")
        
        assert result == TransitionResult.GUARD_FAILED
    
    def test_multiple_actions_execute_in_order(self):
        """Test multiple actions execute in registration order."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        execution_order = []
        
        def action1():
            execution_order.append(1)
        
        def action2():
            execution_order.append(2)
        
        def action3():
            execution_order.append(3)
        
        fsm.register_transition(
            "INITIALIZED",
            "EXECUTING",
            actions=[action1, action2, action3]
        )
        
        fsm.transition_to("EXECUTING")
        
        assert execution_order == [1, 2, 3]
    
    def test_invalid_checkpoint_rollback(self):
        """Test rollback with invalid checkpoint data."""
        fsm = StateMachine("INITIALIZED", "TestOrch")
        
        invalid_checkpoint = {"state": "INVALID_STATE"}
        
        with pytest.raises(ValueError):
            fsm.rollback_to_checkpoint(invalid_checkpoint)
