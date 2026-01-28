"""
Unit Tests for DoRTracker - Definition of Ready Confidence Tracking.

Tests for DoRTracker from Phase 8.0 Challenge Orchestrator foundation.

Authority: CORE-008 (TDD - tests first)
Coverage Target: 90%+
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

from cortex.brain.core.dor_tracker import (
    DoRTracker,
    DoRTurn,
    UserResponse,
    Challenge,
)


class TestDoRTracker:
    """Test DoRTracker for per-turn DoR tracking."""
    
    @pytest.fixture
    def tracker(self) -> DoRTracker:
        """Create DoRTracker instance."""
        return DoRTracker()
    
    def test_tracker_initializes_with_session_id(self, tracker: DoRTracker):
        """Test that tracker initializes with session ID."""
        assert tracker.session_id is not None
        assert len(tracker.session_id) > 0
        assert isinstance(tracker.turns, list)
        assert len(tracker.turns) == 0
    
    def test_start_turn_creates_dor_turn(self, tracker: DoRTracker):
        """Test starting a turn creates DoRTurn object."""
        turn = tracker.start_turn(
            orchestrator="TestOrchestrator",
            user_request="Test request",
            initial_dor=0.75,
            dor_factors={"factor1": 0.5, "factor2": 0.25}
        )
        
        assert isinstance(turn, DoRTurn)
        assert turn.orchestrator == "TestOrchestrator"
        assert turn.user_request == "Test request"
        assert turn.initial_dor == 0.75
        assert len(tracker.turns) == 1
    
    def test_turn_has_unique_id(self, tracker: DoRTracker):
        """Test that each turn has unique ID."""
        turn1 = tracker.start_turn("Orch1", "Request1", 0.7, {})
        turn2 = tracker.start_turn("Orch2", "Request2", 0.8, {})
        
        assert turn1.turn_id != turn2.turn_id
    
    def test_add_challenge_to_turn(self, tracker: DoRTracker):
        """Test adding challenge to turn."""
        turn = tracker.start_turn("TestOrch", "Request", 0.6, {})
        
        tracker.add_challenge(
            turn=turn,
            challenge_type="srp",
            confidence_threshold=0.7,
            gate_type="soft",
            description="SRP violation detected",
            alternatives=["Option 1", "Option 2"]
        )
        
        assert len(turn.challenges_offered) == 1
        challenge = turn.challenges_offered[0]
        assert challenge.challenge_type == "srp"
        assert challenge.gate_type == "soft"
        assert len(challenge.alternatives) == 2
    
    def test_multiple_challenges_per_turn(self, tracker: DoRTracker):
        """Test adding multiple challenges to same turn."""
        turn = tracker.start_turn("TestOrch", "Request", 0.6, {})
        
        tracker.add_challenge(turn, "srp", 0.7, "soft", "SRP violation")
        tracker.add_challenge(turn, "security", 0.5, "hard", "Security issue")
        tracker.add_challenge(turn, "architecture", 0.65, "soft", "Architecture violation")
        
        assert len(turn.challenges_offered) == 3
    
    def test_record_user_response(self, tracker: DoRTracker):
        """Test recording user response to challenges."""
        turn = tracker.start_turn("TestOrch", "Request", 0.6, {})
        tracker.add_challenge(turn, "srp", 0.7, "soft", "SRP violation")
        
        tracker.record_response(turn, UserResponse.ACCEPTED)
        
        assert turn.user_response == UserResponse.ACCEPTED
        assert turn.response_timestamp is not None
    
    def test_complete_turn_with_results(self, tracker: DoRTracker):
        """Test completing turn with execution results."""
        turn = tracker.start_turn("TestOrch", "Request", 0.6, {"factor1": 0.6})
        tracker.add_challenge(turn, "srp", 0.7, "soft", "SRP violation")
        tracker.record_response(turn, UserResponse.ACCEPTED)
        
        tracker.complete_turn(
            turn=turn,
            final_dor=0.95,
            dor_factors={"factor1": 0.95},
            execution_success=True,
            execution_result="Execution completed successfully",
            execution_time_ms=245.5,
            rca_data={"fixed_issues": 1}
        )
        
        assert turn.final_dor == 0.95
        assert turn.execution_success is True
        assert turn.dor_improvement == 0.35  # 0.95 - 0.60
    
    def test_dor_improvement_calculation(self, tracker: DoRTracker):
        """Test DoR improvement calculation."""
        turn = tracker.start_turn("TestOrch", "Request", 0.5, {})
        
        tracker.complete_turn(
            turn=turn,
            final_dor=0.9,
            dor_factors={},
            execution_success=True,
            execution_result="Success",
            execution_time_ms=100.0
        )
        
        assert turn.dor_improvement == 0.4  # 0.9 - 0.5
    
    def test_statistics_empty_tracker(self, tracker: DoRTracker):
        """Test statistics on empty tracker."""
        stats = tracker.get_statistics()
        assert stats == {}
    
    def test_statistics_with_turns(self, tracker: DoRTracker):
        """Test statistics calculation with turns."""
        # Complete first turn
        turn1 = tracker.start_turn("Orch1", "Request1", 0.6, {})
        tracker.complete_turn(turn1, 0.9, {}, True, "Success", 100.0)
        
        # Complete second turn
        turn2 = tracker.start_turn("Orch2", "Request2", 0.7, {})
        tracker.complete_turn(turn2, 0.95, {}, True, "Success", 150.0)
        
        stats = tracker.get_statistics()
        
        assert stats["total_turns"] == 2
        assert stats["completed_turns"] == 2
        assert stats["successful_turns"] == 2
        assert stats["success_rate"] == 1.0
        assert abs(stats["avg_initial_dor"] - 0.65) < 0.001  # (0.6 + 0.7) / 2
        assert abs(stats["avg_final_dor"] - 0.925) < 0.001  # (0.9 + 0.95) / 2
        assert abs(stats["avg_dor_improvement"] - 0.275) < 0.01
    
    def test_statistics_with_failed_turn(self, tracker: DoRTracker):
        """Test statistics with failed execution."""
        turn1 = tracker.start_turn("Orch1", "Request1", 0.6, {})
        tracker.complete_turn(turn1, 0.9, {}, True, "Success", 100.0)
        
        turn2 = tracker.start_turn("Orch2", "Request2", 0.5, {})
        tracker.complete_turn(turn2, 0.6, {}, False, "Failed", 150.0)
        
        stats = tracker.get_statistics()
        
        assert stats["total_turns"] == 2
        assert stats["successful_turns"] == 1
        assert stats["success_rate"] == 0.5
    
    def test_challenge_bypass_tracking(self, tracker: DoRTracker):
        """Test tracking of bypassed challenges."""
        turn = tracker.start_turn("Orch", "Request", 0.5, {})
        tracker.add_challenge(turn, "srp", 0.7, "soft", "SRP violation")
        tracker.record_response(turn, UserResponse.BYPASSED)
        tracker.complete_turn(turn, 0.8, {}, True, "Success", 100.0)
        
        stats = tracker.get_statistics()
        
        assert stats["bypassed_challenges"] == 1
        assert stats["bypass_rate"] == 1.0
    
    def test_get_turn_history(self, tracker: DoRTracker):
        """Test retrieving turn history."""
        turn1 = tracker.start_turn("Orch1", "Request1", 0.6, {})
        tracker.complete_turn(turn1, 0.9, {}, True, "Success", 100.0)
        
        turn2 = tracker.start_turn("Orch2", "Request2", 0.7, {})
        tracker.complete_turn(turn2, 0.95, {}, True, "Success", 150.0)
        
        history = tracker.get_turn_history()
        
        assert len(history) == 2
        assert all(isinstance(t, dict) for t in history)
        assert all("turn_id" in t for t in history)
        assert all("orchestrator" in t for t in history)
    
    def test_turn_to_dict_conversion(self, tracker: DoRTracker):
        """Test DoRTurn to_dict conversion."""
        turn = tracker.start_turn("TestOrch", "Test request with details", 0.75, {})
        tracker.add_challenge(turn, "srp", 0.7, "soft", "SRP violation")
        tracker.record_response(turn, UserResponse.ACCEPTED)
        tracker.complete_turn(turn, 0.9, {}, True, "Success", 250.5)
        
        turn_dict = turn.to_dict()
        
        assert turn_dict["orchestrator"] == "TestOrch"
        assert "initial_dor" in turn_dict
        assert "final_dor" in turn_dict
        assert turn_dict["challenges_offered"] == 1
        assert turn_dict["user_response"] == "accepted"
        assert turn_dict["execution_success"] is True
    
    def test_multiple_sessions(self):
        """Test creating multiple independent trackers."""
        tracker1 = DoRTracker()
        tracker2 = DoRTracker()
        
        assert tracker1.session_id != tracker2.session_id
        
        turn1 = tracker1.start_turn("Orch1", "Request1", 0.6, {})
        turn2 = tracker2.start_turn("Orch2", "Request2", 0.7, {})
        
        assert len(tracker1.turns) == 1
        assert len(tracker2.turns) == 1
        assert turn1.turn_id != turn2.turn_id
    
    def test_dor_factors_preservation(self, tracker: DoRTracker):
        """Test that DoR factors are preserved correctly."""
        initial_factors = {"factor1": 0.5, "factor2": 0.25, "factor3": 0.1}
        turn = tracker.start_turn("Orch", "Request", 0.85, initial_factors)
        
        assert turn.initial_dor_factors == initial_factors
        
        final_factors = {"factor1": 0.8, "factor2": 0.9, "factor3": 0.5}
        tracker.complete_turn(turn, 0.95, final_factors, True, "Success", 100.0)
        
        assert turn.final_dor_factors == final_factors
    
    def test_challenge_with_empty_alternatives(self, tracker: DoRTracker):
        """Test adding challenge without alternatives."""
        turn = tracker.start_turn("Orch", "Request", 0.6, {})
        
        tracker.add_challenge(
            turn=turn,
            challenge_type="security",
            confidence_threshold=0.5,
            gate_type="hard",
            description="Security issue"
        )
        
        challenge = turn.challenges_offered[0]
        assert challenge.alternatives == []
    
    def test_challenge_id_uniqueness(self, tracker: DoRTracker):
        """Test that each challenge gets unique ID."""
        turn = tracker.start_turn("Orch", "Request", 0.6, {})
        
        tracker.add_challenge(turn, "srp", 0.7, "soft", "Issue1")
        tracker.add_challenge(turn, "security", 0.5, "hard", "Issue2")
        
        ids = [c.challenge_id for c in turn.challenges_offered]
        assert len(ids) == len(set(ids))  # All unique
    
    def test_statistics_min_max_dor(self, tracker: DoRTracker):
        """Test min/max DoR calculation in statistics."""
        tracker.start_turn("Orch1", "Request1", 0.5, {})
        tracker.turns[0].initial_dor = 0.3
        tracker.complete_turn(tracker.turns[0], 0.6, {}, True, "Success", 100.0)
        
        tracker.start_turn("Orch2", "Request2", 0.9, {})
        tracker.complete_turn(tracker.turns[1], 0.95, {}, True, "Success", 100.0)
        
        stats = tracker.get_statistics()
        
        assert stats["min_dor"] == 0.3
        assert stats["max_dor"] == 0.95
