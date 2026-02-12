"""
Unit tests for Phase State Machine (AC-STATE-002-06).

Tests atomic phase state transitions with validation,
finite state machine enforcement, and conflict resolution.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import pytest
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

from cortex.core.state.phase_state_machine import (
    PhaseStateMachine,
    PhaseState,
    InvalidTransitionError,
    PhaseNotFoundError,
)


@pytest.fixture
def state_machine() -> PhaseStateMachine:
    """Create phase state machine for testing."""
    return PhaseStateMachine()


class TestBasicTransitions:
    """Test basic state transitions."""
    
    def test_initial_state(self, state_machine: PhaseStateMachine) -> None:
        """Test phase starts in PLANNED state."""
        state_machine.create_phase("test-phase")
        state = state_machine.get_state("test-phase")
        assert state == PhaseState.PLANNED
    
    def test_valid_transition_planned_to_in_progress(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test valid transition from PLANNED to IN_PROGRESS."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        
        state = state_machine.get_state("test-phase")
        assert state == PhaseState.IN_PROGRESS
    
    def test_valid_transition_to_completed(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test valid transition to COMPLETED."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        state_machine.transition("test-phase", PhaseState.COMPLETED)
        
        state = state_machine.get_state("test-phase")
        assert state == PhaseState.COMPLETED
    
    def test_valid_transition_to_locked(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test valid transition to LOCKED."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        state_machine.transition("test-phase", PhaseState.COMPLETED)
        state_machine.transition("test-phase", PhaseState.LOCKED)
        
        state = state_machine.get_state("test-phase")
        assert state == PhaseState.LOCKED


class TestInvalidTransitions:
    """Test invalid transition rejection."""
    
    def test_cannot_go_from_planned_to_completed(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test invalid skip from PLANNED to COMPLETED."""
        state_machine.create_phase("test-phase")
        
        with pytest.raises(InvalidTransitionError):
            state_machine.transition("test-phase", PhaseState.COMPLETED)
    
    def test_cannot_go_from_locked_to_in_progress(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test cannot revert from LOCKED."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        state_machine.transition("test-phase", PhaseState.COMPLETED)
        state_machine.transition("test-phase", PhaseState.LOCKED)
        
        with pytest.raises(InvalidTransitionError):
            state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
    
    def test_all_invalid_transitions_rejected(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test comprehensive invalid transition matrix."""
        # PLANNED -> LOCKED (invalid)
        state_machine.create_phase("phase1")
        with pytest.raises(InvalidTransitionError):
            state_machine.transition("phase1", PhaseState.LOCKED)
        
        # COMPLETED -> IN_PROGRESS (invalid)
        state_machine.create_phase("phase2")
        state_machine.transition("phase2", PhaseState.IN_PROGRESS)
        state_machine.transition("phase2", PhaseState.COMPLETED)
        with pytest.raises(InvalidTransitionError):
            state_machine.transition("phase2", PhaseState.IN_PROGRESS)


class TestConcurrentTransitions:
    """Test concurrent state transitions."""
    
    def test_concurrent_completion_from_in_progress(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test concurrent transitions to COMPLETED succeed."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        
        results = []
        
        def try_complete():
            try:
                state_machine.transition("test-phase", PhaseState.COMPLETED)
                results.append("success")
            except Exception:
                results.append("failed")
        
        threads = [threading.Thread(target=try_complete) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # At least one should succeed
        assert "success" in results
        assert state_machine.get_state("test-phase") == PhaseState.COMPLETED
    
    def test_50_phases_concurrent_transitions(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test 50 different phases transition concurrently."""
        # Create phases
        for i in range(50):
            state_machine.create_phase(f"phase-{i}")
        
        def transition_phase(phase_id: str):
            state_machine.transition(phase_id, PhaseState.IN_PROGRESS)
            state_machine.transition(phase_id, PhaseState.COMPLETED)
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [
                executor.submit(transition_phase, f"phase-{i}")
                for i in range(50)
            ]
            [f.result() for f in as_completed(futures)]
        
        # All completed
        for i in range(50):
            assert state_machine.get_state(f"phase-{i}") == PhaseState.COMPLETED


class TestAtomicTransitions:
    """Test transition atomicity."""
    
    def test_transition_is_atomic(self, state_machine: PhaseStateMachine) -> None:
        """Test no intermediate states visible."""
        state_machine.create_phase("test-phase")
        
        observed_states = []
        
        def observer():
            for _ in range(100):
                state = state_machine.get_state("test-phase")
                observed_states.append(state)
        
        def transitioner():
            state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
            state_machine.transition("test-phase", PhaseState.COMPLETED)
        
        t1 = threading.Thread(target=observer)
        t2 = threading.Thread(target=transitioner)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
        
        # Should only see valid states
        valid_states = {PhaseState.PLANNED, PhaseState.IN_PROGRESS, PhaseState.COMPLETED}
        assert all(s in valid_states for s in observed_states)


class TestTransitionAudit:
    """Test transition audit logging."""
    
    def test_tracks_transition_history(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test transition history is recorded."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        state_machine.transition("test-phase", PhaseState.COMPLETED)
        
        history = state_machine.get_history("test-phase")
        assert len(history) == 3  # CREATE, IN_PROGRESS, COMPLETED
    
    def test_history_includes_timestamps(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test transition history includes timestamps."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        
        history = state_machine.get_history("test-phase")
        for entry in history:
            assert "timestamp" in entry
            assert "from_state" in entry or "to_state" in entry


class TestPhaseQueries:
    """Test phase query operations."""
    
    def test_list_phases_by_state(self, state_machine: PhaseStateMachine) -> None:
        """Test querying phases by state."""
        state_machine.create_phase("phase1")
        state_machine.create_phase("phase2")
        state_machine.transition("phase2", PhaseState.IN_PROGRESS)
        
        planned = state_machine.list_phases_by_state(PhaseState.PLANNED)
        in_progress = state_machine.list_phases_by_state(PhaseState.IN_PROGRESS)
        
        assert "phase1" in planned
        assert "phase2" in in_progress
    
    def test_phase_not_found_error(self, state_machine: PhaseStateMachine) -> None:
        """Test error on nonexistent phase."""
        with pytest.raises(PhaseNotFoundError):
            state_machine.get_state("nonexistent")


class TestIdempotency:
    """Test idempotent transitions."""
    
    def test_transition_to_same_state_idempotent(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test transitioning to same state is idempotent."""
        state_machine.create_phase("test-phase")
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        
        # Second transition to same state should succeed
        state_machine.transition("test-phase", PhaseState.IN_PROGRESS)
        
        assert state_machine.get_state("test-phase") == PhaseState.IN_PROGRESS


class TestMetrics:
    """Test state machine metrics."""
    
    def test_tracks_transition_count(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test transition counter."""
        for i in range(5):
            state_machine.create_phase(f"phase-{i}")
            state_machine.transition(f"phase-{i}", PhaseState.IN_PROGRESS)
        
        metrics = state_machine.get_metrics()
        assert metrics["total_transitions"] >= 5
    
    def test_invalid_transition_counter(
        self, state_machine: PhaseStateMachine
    ) -> None:
        """Test invalid transition counter."""
        state_machine.create_phase("test-phase")
        
        try:
            state_machine.transition("test-phase", PhaseState.LOCKED)
        except InvalidTransitionError:
            pass
        
        metrics = state_machine.get_metrics()
        assert metrics["invalid_transitions"] >= 1


def test_state_machine_performance() -> None:
    """Benchmark state machine performance."""
    import time
    sm = PhaseStateMachine()
    
    num_phases = 100
    for i in range(num_phases):
        sm.create_phase(f"phase-{i}")
    
    start = time.time()
    for i in range(num_phases):
        sm.transition(f"phase-{i}", PhaseState.IN_PROGRESS)
        sm.transition(f"phase-{i}", PhaseState.COMPLETED)
    duration = time.time() - start
    
    transitions_per_sec = (num_phases * 2) / duration
    assert transitions_per_sec > 1000  # >1000 transitions/sec
