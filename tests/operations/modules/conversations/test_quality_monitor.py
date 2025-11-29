"""
Tests for Real-Time Conversation Quality Monitor

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime
from src.operations.modules.conversations.quality_monitor import (
    QualityMonitor,
    MonitoringSession,
    ConversationTurn,
    create_monitor
)


class TestQualityMonitor:
    """Test suite for QualityMonitor."""
    
    def test_monitor_initialization(self):
        """Test monitor initializes with correct defaults."""
        monitor = QualityMonitor()
        
        assert monitor.min_turns_before_check == 5
        assert monitor.quality_threshold == "GOOD"
        assert monitor.current_session is None
        assert len(monitor.session_history) == 0
    
    def test_monitor_custom_config(self):
        """Test monitor with custom configuration."""
        monitor = QualityMonitor(
            min_turns_before_check=3,
            quality_threshold="EXCELLENT"
        )
        
        assert monitor.min_turns_before_check == 3
        assert monitor.quality_threshold == "EXCELLENT"
    
    def test_start_session(self):
        """Test starting a new monitoring session."""
        monitor = QualityMonitor()
        session_id = monitor.start_session()
        
        assert monitor.current_session is not None
        assert monitor.current_session.session_id == session_id
        assert len(monitor.current_session.turns) == 0
        assert monitor.current_session.hint_shown is False
    
    def test_start_session_custom_id(self):
        """Test starting session with custom ID."""
        monitor = QualityMonitor()
        custom_id = "test-session-123"
        session_id = monitor.start_session(custom_id)
        
        assert session_id == custom_id
        assert monitor.current_session.session_id == custom_id
    
    def test_add_turn_auto_starts_session(self):
        """Test adding turn automatically starts session if none active."""
        monitor = QualityMonitor()
        
        result = monitor.add_turn(
            user_message="Test question",
            assistant_response="Test answer"
        )
        
        assert monitor.current_session is not None
        assert len(monitor.current_session.turns) == 1
        assert result['turn_count'] == 1
        assert result['should_check_quality'] is False  # Below min_turns
    
    def test_add_multiple_turns(self):
        """Test adding multiple turns."""
        monitor = QualityMonitor()
        
        for i in range(3):
            result = monitor.add_turn(
                user_message=f"Question {i+1}",
                assistant_response=f"Answer {i+1}"
            )
        
        assert len(monitor.current_session.turns) == 3
        assert result['turn_count'] == 3
        assert result['should_check_quality'] is False  # Still below min (5)
    
    def test_quality_check_triggers_after_min_turns(self):
        """Test quality check triggers after minimum turns."""
        monitor = QualityMonitor(min_turns_before_check=3)
        
        # Add turns below threshold
        for i in range(2):
            result = monitor.add_turn(
                user_message=f"Question {i+1}",
                assistant_response=f"Answer {i+1}"
            )
            assert result['should_check_quality'] is False
        
        # Add turn that meets threshold
        result = monitor.add_turn(
            user_message="Question 3",
            assistant_response="Answer 3"
        )
        
        assert result['should_check_quality'] is True
        assert 'quality_score' in result
        assert 'quality_level' in result
    
    def test_quality_check_with_strategic_content(self):
        """Test quality check with strategic conversation."""
        monitor = QualityMonitor(min_turns_before_check=2)
        
        # Add strategic conversation
        monitor.add_turn(
            user_message="Let's plan the authentication feature",
            assistant_response="""
            🎯 Understanding: Implement user authentication
            
            ⚠️ **Challenge:** ✓ **Accept**
            
            💬 **Response:** I'll implement authentication with these phases:
            
            Phase 1: Backend API
            Phase 2: UI Integration
            Phase 3: Testing
            
            Files to modify: `auth_service.py`, `api/routes.py`
            
            🔍 Next Steps:
               1. Design authentication flow
               2. Implement JWT tokens
               3. Add security tests
            """
        )
        
        result = monitor.add_turn(
            user_message="Great, let's start",
            assistant_response="Starting Phase 1 implementation"
        )
        
        assert result['should_check_quality'] is True
        assert result['quality_level'] in ['GOOD', 'EXCELLENT']
        assert result['quality_score'] >= 10  # GOOD threshold
        assert result['elements']['multi_phase_planning'] is True
        assert result['elements']['challenge_accept_flow'] is True
    
    def test_hint_shown_only_once_per_session(self):
        """Test Smart Hint shown only once per session."""
        monitor = QualityMonitor(min_turns_before_check=2)
        
        # Add strategic content
        monitor.add_turn(
            user_message="Plan feature X",
            assistant_response="""
            Phase 1: Design
            Phase 2: Implementation
            Phase 3: Testing
            
            🔍 Next Steps:
               1. Task 1
               2. Task 2
            """
        )
        
        result1 = monitor.add_turn(
            user_message="Continue",
            assistant_response="Implementing..."
        )
        
        # First check should recommend hint
        assert result1['should_show_hint'] is True
        
        # Mark hint as shown
        monitor.record_user_response('ignored')
        
        # Add more turns
        result2 = monitor.add_turn(
            user_message="More work",
            assistant_response="More implementation..."
        )
        
        # Subsequent checks should not recommend hint
        assert result2['should_show_hint'] is False
    
    def test_record_user_response(self):
        """Test recording user response to Smart Hint."""
        monitor = QualityMonitor()
        monitor.start_session("test-123")
        
        monitor.record_user_response('accepted')
        
        assert monitor.current_session.user_response == 'accepted'
        assert monitor.current_session.hint_shown is True
    
    def test_end_session(self):
        """Test ending monitoring session."""
        monitor = QualityMonitor()
        monitor.start_session()
        
        monitor.add_turn("Question", "Answer")
        
        session = monitor.end_session()
        
        assert session is not None
        assert len(session.turns) == 1
        assert monitor.current_session is None
        assert len(monitor.session_history) == 1
    
    def test_get_current_quality(self):
        """Test getting current quality score."""
        monitor = QualityMonitor(min_turns_before_check=1)
        
        # Before any turns
        assert monitor.get_current_quality() is None
        
        # After quality check
        monitor.add_turn(
            user_message="Test",
            assistant_response="Response"
        )
        
        quality = monitor.get_current_quality()
        assert quality is not None
        assert hasattr(quality, 'total_score')
        assert hasattr(quality, 'level')
    
    def test_session_stats_no_sessions(self):
        """Test stats with no session history."""
        monitor = QualityMonitor()
        stats = monitor.get_session_stats()
        
        assert stats['total_sessions'] == 0
        assert stats['hints_shown'] == 0
        assert stats['acceptance_rate'] == 0.0
        assert stats['average_turns'] == 0.0
    
    def test_session_stats_with_history(self):
        """Test stats with session history."""
        monitor = QualityMonitor(min_turns_before_check=1)
        
        # Session 1: Hint shown, accepted
        monitor.start_session()
        monitor.add_turn("Q1", "A1")
        monitor.record_user_response('accepted')
        monitor.end_session()
        
        # Session 2: Hint shown, rejected
        monitor.start_session()
        monitor.add_turn("Q2", "A2")
        monitor.record_user_response('rejected')
        monitor.end_session()
        
        # Session 3: No hint
        monitor.start_session()
        monitor.add_turn("Q3", "A3")
        monitor.end_session()
        
        stats = monitor.get_session_stats()
        
        assert stats['total_sessions'] == 3
        assert stats['hints_shown'] == 2
        assert stats['accepted_count'] == 1
        assert stats['acceptance_rate'] == 50.0
        assert stats['total_turns'] == 3
        assert stats['average_turns'] == 1.0
    
    def test_factory_function_default(self):
        """Test factory function with defaults."""
        monitor = create_monitor()
        
        assert monitor.min_turns_before_check == 5
        assert monitor.quality_threshold == "GOOD"
    
    def test_factory_function_custom_config(self):
        """Test factory function with custom config."""
        config = {
            'min_turns_before_check': 3,
            'quality_threshold': 'EXCELLENT'
        }
        
        monitor = create_monitor(config)
        
        assert monitor.min_turns_before_check == 3
        assert monitor.quality_threshold == "EXCELLENT"
    
    def test_low_quality_conversation_no_hint(self):
        """Test low quality conversation doesn't trigger hint."""
        monitor = QualityMonitor(min_turns_before_check=2)
        
        # Add low-quality conversation
        monitor.add_turn(
            user_message="Hi",
            assistant_response="Hello"
        )
        
        result = monitor.add_turn(
            user_message="Thanks",
            assistant_response="You're welcome"
        )
        
        assert result['should_check_quality'] is True
        assert result['quality_level'] in ['LOW', 'FAIR']
        assert result['should_show_hint'] is False
    
    def test_multi_turn_bonus_points(self):
        """Test multi-turn conversations get bonus points."""
        monitor = QualityMonitor(min_turns_before_check=3)
        
        # Add 3+ turns with some content
        for i in range(5):
            result = monitor.add_turn(
                user_message=f"Question {i+1} about architecture",
                assistant_response=f"Answer {i+1} discussing module design"
            )
        
        # Should have bonus points for 5 turns (≥3 turns = +2 points)
        assert result['quality_score'] > 0  # Has some points from content
        # Multi-turn bonus should help push it higher
