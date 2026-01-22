"""
State Machine Tests - TDD for AC-FR-003

Tests for:
- AC-FR-003-01: Atomic State Transitions (validate → lock → commit)
- AC-FR-003-02: Invalid Transition Rejection with audit trail
- AC-FR-003-03: State History Tracking (previous → current → next)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest

from cortex.core.state_machine import (
    StateMachine,
    ACState,
    PhaseState,
    TransitionType,
    StateTransition,
)
from cortex.infrastructure.database import DatabaseManager, DatabaseConfig


@pytest.mark.ac("FR-003-01")
class TestAtomicTransitions:
    """Test AC-FR-003-01: Atomic transitions (validate → lock → commit)"""
    
    def test_initialize_ac_state(self):
        """AC should initialize in DRAFT state."""
        sm = StateMachine()
        
        result = sm.initialize_ac("AC-TEST-001")
        
        assert result.is_ok()
        
        # Verify state
        state_result = sm.get_ac_state("AC-TEST-001")
        assert state_result.is_ok()
        snapshot = state_result.unwrap()
        assert snapshot.current_state == "DRAFT"
        assert snapshot.is_locked is False
    
    def test_initialize_phase_state(self):
        """Phase should initialize in PLANNING state."""
        sm = StateMachine()
        
        result = sm.initialize_phase("PHASE-01")
        
        assert result.is_ok()
        
        # Verify state
        state_result = sm.get_phase_state("PHASE-01")
        assert state_result.is_ok()
        snapshot = state_result.unwrap()
        assert snapshot.current_state == "PLANNING"
    
    def test_valid_ac_transition_draft_to_active(self):
        """AC should transition from DRAFT to ACTIVE."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        result = sm.transition_ac("AC-TEST-001", ACState.ACTIVE, reason="Ready for implementation")
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "ACTIVE"
        assert snapshot.previous_state == "DRAFT"
        assert snapshot.is_locked is False
        assert "REVIEWING" in snapshot.next_allowed_states
    
    def test_valid_ac_transition_active_to_reviewing(self):
        """AC should transition from ACTIVE to REVIEWING."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        
        result = sm.transition_ac("AC-TEST-001", ACState.REVIEWING, reason="Ready for review")
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "REVIEWING"
        assert snapshot.previous_state == "ACTIVE"
    
    def test_valid_ac_transition_reviewing_to_locked(self):
        """AC should transition from REVIEWING to LOCKED."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        sm.transition_ac("AC-TEST-001", ACState.REVIEWING)
        
        result = sm.transition_ac("AC-TEST-001", ACState.LOCKED, reason="Implementation complete")
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "LOCKED"
        assert snapshot.is_locked is True
        assert len(snapshot.next_allowed_states) == 0  # Terminal state
    
    def test_transition_with_metadata(self):
        """Transitions should preserve metadata."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        metadata = {"implemented_by": "test_user", "timestamp": "2026-01-14T10:00:00Z"}
        result = sm.transition_ac(
            "AC-TEST-001",
            ACState.ACTIVE,
            reason="Ready",
            metadata=metadata
        )
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "ACTIVE"
        
        # Verify metadata in history
        history_result = sm.get_transition_history(ac_id="AC-TEST-001")
        assert history_result.is_ok()
        transitions = history_result.unwrap()
        last_transition = [t for t in transitions if t.to_state == "ACTIVE"][0]
        assert last_transition.metadata == metadata
    
    def test_valid_phase_transition_planning_to_implementing(self):
        """Phase should transition from PLANNING to IMPLEMENTING."""
        sm = StateMachine()
        sm.initialize_phase("PHASE-01")
        
        result = sm.transition_phase("PHASE-01", PhaseState.IMPLEMENTING)
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "IMPLEMENTING"
    
    def test_valid_phase_transition_implementing_to_validating(self):
        """Phase should transition from IMPLEMENTING to VALIDATING."""
        sm = StateMachine()
        sm.initialize_phase("PHASE-01")
        sm.transition_phase("PHASE-01", PhaseState.IMPLEMENTING)
        
        result = sm.transition_phase("PHASE-01", PhaseState.VALIDATING)
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "VALIDATING"
    
    def test_valid_phase_transition_validating_to_complete(self):
        """Phase should transition from VALIDATING to COMPLETE."""
        sm = StateMachine()
        sm.initialize_phase("PHASE-01")
        sm.transition_phase("PHASE-01", PhaseState.IMPLEMENTING)
        sm.transition_phase("PHASE-01", PhaseState.VALIDATING)
        
        result = sm.transition_phase("PHASE-01", PhaseState.COMPLETE)
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "COMPLETE"
        assert snapshot.is_locked is True


@pytest.mark.ac("FR-003-02")
class TestInvalidTransitions:
    """Test AC-FR-003-02: Invalid transition rejection with audit trail"""
    
    def test_reject_invalid_ac_transition_draft_to_reviewing(self):
        """AC cannot transition directly from DRAFT to REVIEWING."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        result = sm.transition_ac("AC-TEST-001", ACState.REVIEWING)
        
        assert result.is_err()
        assert "Invalid transition" in str(result)
        assert "DRAFT" in str(result)
        assert "REVIEWING" in str(result)
    
    def test_reject_invalid_ac_transition_from_locked(self):
        """AC cannot transition from LOCKED state."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        sm.transition_ac("AC-TEST-001", ACState.REVIEWING)
        sm.transition_ac("AC-TEST-001", ACState.LOCKED)
        
        result = sm.transition_ac("AC-TEST-001", ACState.DRAFT)
        
        assert result.is_err()
        assert "Invalid transition" in str(result)
    
    def test_reject_transition_nonexistent_ac(self):
        """Transition should fail for nonexistent AC."""
        sm = StateMachine()
        
        result = sm.transition_ac("AC-NONEXISTENT", ACState.ACTIVE)
        
        assert result.is_err()
        assert "not found" in str(result)
    
    def test_reject_invalid_phase_transition(self):
        """Phase cannot transition directly from PLANNING to VALIDATING."""
        sm = StateMachine()
        sm.initialize_phase("PHASE-01")
        
        result = sm.transition_phase("PHASE-01", PhaseState.VALIDATING)
        
        assert result.is_err()
        assert "Invalid transition" in str(result)
    
    def test_reject_transition_nonexistent_phase(self):
        """Transition should fail for nonexistent Phase."""
        sm = StateMachine()
        
        result = sm.transition_phase("PHASE-NONEXISTENT", PhaseState.IMPLEMENTING)
        
        assert result.is_err()
        assert "not found" in str(result)
    
    def test_transition_rejection_creates_no_state_change(self):
        """Invalid transition should not change state."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        # Attempt invalid transition
        sm.transition_ac("AC-TEST-001", ACState.REVIEWING)
        
        # Verify state unchanged
        state_result = sm.get_ac_state("AC-TEST-001")
        snapshot = state_result.unwrap()
        assert snapshot.current_state == "DRAFT"
    
    def test_backtrack_transition_allowed(self):
        """AC should be able to backtrack from ACTIVE to DRAFT."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        
        result = sm.transition_ac("AC-TEST-001", ACState.DRAFT, reason="Backtracking")
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "DRAFT"
    
    def test_backtrack_transition_phase_allowed(self):
        """Phase should be able to backtrack from VALIDATING to IMPLEMENTING."""
        sm = StateMachine()
        sm.initialize_phase("PHASE-01")
        sm.transition_phase("PHASE-01", PhaseState.IMPLEMENTING)
        sm.transition_phase("PHASE-01", PhaseState.VALIDATING)
        
        result = sm.transition_phase("PHASE-01", PhaseState.IMPLEMENTING, reason="Need more work")
        
        assert result.is_ok()
        snapshot = result.unwrap()
        assert snapshot.current_state == "IMPLEMENTING"


@pytest.mark.ac("FR-003-03")
class TestStateHistory:
    """Test AC-FR-003-03: State history tracking (previous → current → next)"""
    
    def test_transition_history_tracks_all_transitions(self):
        """All transitions should be recorded in history."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        sm.transition_ac("AC-TEST-001", ACState.REVIEWING)
        
        result = sm.get_transition_history(ac_id="AC-TEST-001")
        
        assert result.is_ok()
        transitions = result.unwrap()
        
        # Should have: initialization, DRAFT→ACTIVE, ACTIVE→REVIEWING
        assert len(transitions) == 3
        assert transitions[0].to_state == "DRAFT"
        assert transitions[1].to_state == "ACTIVE"
        assert transitions[2].to_state == "REVIEWING"
    
    def test_transition_history_contains_metadata(self):
        """History should include transition metadata."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        metadata = {"user": "test_user", "reason": "implementation"}
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE, metadata=metadata)
        
        result = sm.get_transition_history(ac_id="AC-TEST-001")
        transitions = result.unwrap()
        
        active_transition = [t for t in transitions if t.to_state == "ACTIVE"][0]
        assert active_transition.metadata == metadata
    
    def test_transition_history_contains_timestamps(self):
        """Each transition should have a timestamp."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        
        result = sm.get_transition_history(ac_id="AC-TEST-001")
        transitions = result.unwrap()
        
        for transition in transitions:
            assert transition.timestamp is not None
            assert len(transition.timestamp) > 0
            assert "T" in transition.timestamp  # ISO format
    
    def test_snapshot_shows_previous_state(self):
        """State snapshot should show previous state."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        
        result = sm.transition_ac("AC-TEST-001", ACState.REVIEWING)
        snapshot = result.unwrap()
        
        assert snapshot.previous_state == "ACTIVE"
        assert snapshot.current_state == "REVIEWING"
    
    def test_snapshot_shows_next_allowed_states(self):
        """State snapshot should list next allowed states."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        result = sm.get_ac_state("AC-TEST-001")
        snapshot = result.unwrap()
        
        # In DRAFT, only ACTIVE is allowed
        assert "ACTIVE" in snapshot.next_allowed_states
        assert len(snapshot.next_allowed_states) == 1
    
    def test_snapshot_counts_transitions(self):
        """State snapshot should count transitions."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        result1 = sm.get_ac_state("AC-TEST-001")
        assert result1.unwrap().transition_count == 1  # Just initialization
        
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        result2 = sm.get_ac_state("AC-TEST-001")
        assert result2.unwrap().transition_count == 2  # Initialization + transition
    
    def test_phase_history_tracked_separately(self):
        """Phase and AC histories should be separate."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.initialize_phase("PHASE-01")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        sm.transition_phase("PHASE-01", PhaseState.IMPLEMENTING)
        
        ac_history_result = sm.get_transition_history(ac_id="AC-TEST-001")
        phase_history_result = sm.get_transition_history(phase_id="PHASE-01")
        
        ac_transitions = ac_history_result.unwrap()
        phase_transitions = phase_history_result.unwrap()
        
        assert len(ac_transitions) == 2  # Init + transition
        assert len(phase_transitions) == 2  # Init + transition
        assert all(t.ac_id == "AC-TEST-001" for t in ac_transitions)
        assert all(t.phase_id == "PHASE-01" for t in phase_transitions)
    
    def test_full_lifecycle_history(self):
        """Complete AC lifecycle should be tracked."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE, reason="Start implementation")
        sm.transition_ac("AC-TEST-001", ACState.REVIEWING, reason="Ready for review")
        sm.transition_ac("AC-TEST-001", ACState.LOCKED, reason="Approved and locked")
        
        result = sm.get_transition_history(ac_id="AC-TEST-001")
        transitions = result.unwrap()
        
        states = [t.to_state for t in transitions]
        assert states == ["DRAFT", "ACTIVE", "REVIEWING", "LOCKED"]
    
    def test_transition_reason_preserved(self):
        """Transition reason should be preserved in history."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        reason = "Starting implementation phase"
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE, reason=reason)
        
        result = sm.get_transition_history(ac_id="AC-TEST-001")
        transitions = result.unwrap()
        
        active_transition = [t for t in transitions if t.to_state == "ACTIVE"][0]
        assert active_transition.reason == reason
    
    def test_transition_history_with_database(self, tmp_path):
        """Transitions should persist to database."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        sm = StateMachine(db)
        sm.initialize_ac("AC-TEST-001")
        
        result = sm.transition_ac("AC-TEST-001", ACState.ACTIVE, reason="Starting")
        
        assert result.is_ok()
        
        # Verify persistence to audit log
        query_result = db.query_audit_by_ac_id("AC-TEST-001")
        assert query_result.is_ok()
        entries = query_result.unwrap()
        assert len(entries) >= 1
        
        db.close()


class TestStateMachineIntegration:
    """Integration tests for state machine."""
    
    def test_multiple_ac_states_independent(self):
        """Multiple ACs should have independent state machines."""
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        sm.initialize_ac("AC-TEST-002")
        
        sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
        
        # AC-002 should still be in DRAFT
        result = sm.get_ac_state("AC-TEST-002")
        snapshot = result.unwrap()
        assert snapshot.current_state == "DRAFT"
    
    def test_concurrent_transitions_safe(self):
        """Concurrent transitions should be thread-safe."""
        import threading
        
        sm = StateMachine()
        sm.initialize_ac("AC-TEST-001")
        
        results = []
        
        def transition():
            result = sm.transition_ac("AC-TEST-001", ACState.ACTIVE)
            results.append(result)
        
        threads = [threading.Thread(target=transition) for _ in range(3)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Only one should succeed
        successful = [r for r in results if r.is_ok()]
        assert len(successful) == 1
    
    def test_singleton_instance_consistency(self):
        """Singleton instance should be consistent across calls."""
        sm1 = StateMachine.instance()
        sm2 = StateMachine.instance()
        
        assert sm1 is sm2
