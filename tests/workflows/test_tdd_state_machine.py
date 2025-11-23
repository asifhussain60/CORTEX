"""
Tests for TDD State Machine (Milestone 2.1)

Validates state transitions, cycle tracking, metrics collection,
and session persistence.

Author: Asif Hussain
Created: 2025-11-23
Phase: TDD Mastery Phase 2 - Milestone 2.1
"""

import pytest
import tempfile
import os
from datetime import datetime
from src.workflows.tdd_state_machine import (
    TDDStateMachine,
    TDDState,
    TDDCycleMetrics,
    TDDSession
)


class TestTDDStateTransitions:
    """Test valid and invalid state transitions."""
    
    def test_initial_state_is_idle(self):
        """Should start in IDLE state."""
        machine = TDDStateMachine("test_feature", "session_123")
        assert machine.get_current_state() == TDDState.IDLE
    
    def test_idle_to_red_transition(self):
        """Should transition from IDLE to RED."""
        machine = TDDStateMachine("test_feature", "session_123")
        assert machine.start_red_phase()
        assert machine.get_current_state() == TDDState.RED
    
    def test_red_to_green_transition(self):
        """Should transition from RED to GREEN."""
        machine = TDDStateMachine("test_feature", "session_123")
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=3)
        
        assert machine.start_green_phase()
        assert machine.get_current_state() == TDDState.GREEN
    
    def test_green_to_refactor_transition(self):
        """Should transition from GREEN to REFACTOR."""
        machine = TDDStateMachine("test_feature", "session_123")
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=3)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=3, code_lines_added=20)
        
        assert machine.start_refactor_phase()
        assert machine.get_current_state() == TDDState.REFACTOR
    
    def test_refactor_to_green_transition(self):
        """Should transition from REFACTOR back to GREEN."""
        machine = TDDStateMachine("test_feature", "session_123")
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=3)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=3, code_lines_added=20)
        machine.start_refactor_phase()
        machine.complete_refactor_phase(code_lines_refactored=15, iterations=1)
        
        # After refactoring, should re-run tests (GREEN)
        assert machine.complete_cycle()
        assert machine.get_current_state() == TDDState.GREEN
    
    def test_invalid_transition_rejected(self):
        """Should reject invalid state transitions."""
        machine = TDDStateMachine("test_feature", "session_123")
        
        # Cannot go directly from IDLE to GREEN
        assert not machine.start_green_phase()
        assert machine.get_current_state() == TDDState.IDLE


class TestTDDCycleTracking:
    """Test TDD cycle metrics and tracking."""
    
    def test_cycle_metrics_recorded(self):
        """Should record metrics for each cycle."""
        machine = TDDStateMachine("test_feature", "session_123")
        
        # Complete one cycle
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=3)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=3, code_lines_added=20)
        machine.start_refactor_phase()
        machine.complete_refactor_phase(code_lines_refactored=15, iterations=2)
        machine.complete_cycle()
        
        # Check metrics
        cycles = machine.get_cycle_metrics()
        assert len(cycles) == 1
        
        cycle = cycles[0]
        assert cycle.cycle_number == 1
        assert cycle.tests_written == 3
        assert cycle.tests_passing == 3
        assert cycle.code_lines_added == 20
        assert cycle.code_lines_refactored == 15
        assert cycle.refactoring_iterations == 2
        assert cycle.total_duration > 0
    
    def test_multiple_cycles_tracked(self):
        """Should track multiple TDD cycles."""
        machine = TDDStateMachine("test_feature", "session_123")
        
        # Complete two cycles
        for i in range(2):
            machine.start_red_phase()
            machine.complete_red_phase(tests_written=2 + i)
            machine.start_green_phase()
            machine.complete_green_phase(tests_passing=2 + i, code_lines_added=10 + i)
            machine.start_refactor_phase()
            machine.complete_refactor_phase(code_lines_refactored=5 + i, iterations=1)
            machine.complete_cycle()
        
        cycles = machine.get_cycle_metrics()
        assert len(cycles) == 2
        assert cycles[0].cycle_number == 1
        assert cycles[1].cycle_number == 2
    
    def test_phase_durations_tracked(self):
        """Should track duration of each phase."""
        machine = TDDStateMachine("test_feature", "session_123")
        
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=1)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=1, code_lines_added=5)
        machine.start_refactor_phase()
        machine.complete_refactor_phase(code_lines_refactored=3, iterations=1)
        machine.complete_cycle()
        
        cycle = machine.get_cycle_metrics()[0]
        assert cycle.red_duration >= 0
        assert cycle.green_duration >= 0
        assert cycle.refactor_duration >= 0
        assert cycle.total_duration == (
            cycle.red_duration + cycle.green_duration + cycle.refactor_duration
        )


class TestSessionSummary:
    """Test session summary generation."""
    
    def test_session_summary_empty(self):
        """Should handle empty session summary."""
        machine = TDDStateMachine("test_feature", "session_123")
        summary = machine.get_session_summary()
        
        assert summary["feature_name"] == "test_feature"
        assert summary["total_cycles"] == 0
        assert summary["current_state"] == "idle"
    
    def test_session_summary_with_cycles(self):
        """Should generate summary with aggregate metrics."""
        machine = TDDStateMachine("test_feature", "session_123")
        
        # Complete one cycle
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=5)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=5, code_lines_added=30)
        machine.start_refactor_phase()
        machine.complete_refactor_phase(code_lines_refactored=20, iterations=2)
        machine.complete_cycle()
        
        summary = machine.get_session_summary()
        
        assert summary["feature_name"] == "test_feature"
        assert summary["total_cycles"] == 1
        assert summary["total_tests_written"] == 5
        assert summary["total_tests_passing"] == 5
        assert summary["test_pass_rate"] == 100.0
        assert summary["total_code_lines_added"] == 30
        assert summary["total_code_lines_refactored"] == 20
        assert summary["total_duration_seconds"] > 0
    
    def test_session_summary_multiple_cycles(self):
        """Should aggregate metrics across multiple cycles."""
        machine = TDDStateMachine("test_feature", "session_123")
        
        # Complete two cycles
        for i in range(2):
            machine.start_red_phase()
            machine.complete_red_phase(tests_written=3)
            machine.start_green_phase()
            machine.complete_green_phase(tests_passing=3, code_lines_added=15)
            machine.start_refactor_phase()
            machine.complete_refactor_phase(code_lines_refactored=10, iterations=1)
            machine.complete_cycle()
        
        summary = machine.get_session_summary()
        
        assert summary["total_cycles"] == 2
        assert summary["total_tests_written"] == 6
        assert summary["total_tests_passing"] == 6
        assert summary["total_code_lines_added"] == 30
        assert summary["total_code_lines_refactored"] == 20


class TestSessionPersistence:
    """Test session save/load functionality."""
    
    def test_save_session(self):
        """Should save session to file."""
        machine = TDDStateMachine("test_feature", "session_123")
        
        # Complete a cycle
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=2)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=2, code_lines_added=10)
        machine.complete_cycle()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            assert machine.save_session(filepath)
            assert os.path.exists(filepath)
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_load_session(self):
        """Should load session from file."""
        # Create and save session
        machine = TDDStateMachine("test_feature", "session_123")
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=3)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=3, code_lines_added=15)
        machine.complete_cycle()
        
        # Save to temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            machine.save_session(filepath)
            
            # Load session
            loaded = TDDStateMachine.load_session(filepath)
            
            assert loaded is not None
            assert loaded.session.feature_name == "test_feature"
            assert loaded.session.session_id == "session_123"
            assert len(loaded.get_cycle_metrics()) == 1
            assert loaded.get_current_state() == TDDState.GREEN
            
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)
    
    def test_load_preserves_metrics(self):
        """Should preserve all metrics when loading."""
        machine = TDDStateMachine("test_feature", "session_123")
        machine.start_red_phase()
        machine.complete_red_phase(tests_written=5)
        machine.start_green_phase()
        machine.complete_green_phase(tests_passing=5, code_lines_added=25)
        machine.start_refactor_phase()
        machine.complete_refactor_phase(code_lines_refactored=18, iterations=3)
        machine.complete_cycle()
        
        # Save and load
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            filepath = f.name
        
        try:
            machine.save_session(filepath)
            loaded = TDDStateMachine.load_session(filepath)
            
            # Compare metrics
            original_cycle = machine.get_cycle_metrics()[0]
            loaded_cycle = loaded.get_cycle_metrics()[0]
            
            assert loaded_cycle.tests_written == original_cycle.tests_written
            assert loaded_cycle.tests_passing == original_cycle.tests_passing
            assert loaded_cycle.code_lines_added == original_cycle.code_lines_added
            assert loaded_cycle.code_lines_refactored == original_cycle.code_lines_refactored
            assert loaded_cycle.refactoring_iterations == original_cycle.refactoring_iterations
            
        finally:
            if os.path.exists(filepath):
                os.unlink(filepath)


class TestErrorHandling:
    """Test error state handling."""
    
    def test_error_state_transition(self):
        """Should transition to ERROR state on failure."""
        machine = TDDStateMachine("test_feature", "session_123")
        machine.start_red_phase()
        
        assert machine.handle_error("Test execution failed")
        assert machine.get_current_state() == TDDState.ERROR
    
    def test_recover_from_error(self):
        """Should recover from ERROR state to RED."""
        machine = TDDStateMachine("test_feature", "session_123")
        machine.start_red_phase()
        machine.handle_error("Test execution failed")
        
        # Should be able to retry from RED
        assert machine.start_red_phase()
        assert machine.get_current_state() == TDDState.RED


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
