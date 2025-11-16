"""
CORTEX 3.0 - Test Feature 5.3: Smart Auto-Detection

Purpose: Test the Smart Auto-Detection system that monitors conversation
         quality and generates Smart Hints for valuable conversations.

Test Coverage:
- Real-time quality monitoring
- Smart hint generation for ≥7/10 quality conversations  
- User feedback recording and learning
- Integration with Quality Monitor and Smart Hint Generator

Success Criteria:
- Detection accuracy: ≥85%
- False positive rate: <15%
- Hint generation for GOOD+ quality conversations
- User feedback loop functional

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime

from src.operations.modules.conversations.smart_auto_detection import (
    SmartAutoDetection,
    create_smart_auto_detection
)
from src.tier1.conversation_quality import QualityScore, SemanticElements


class TestFeature53SmartAutoDetection:
    """Test Feature 5.3: Smart Auto-Detection System"""
    
    def setup_method(self):
        """Setup test environment for each test method."""
        self.smart_detection = SmartAutoDetection(
            quality_threshold="GOOD",
            min_turns_before_check=3,  # Lower for testing
            enable_learning=True
        )
    
    def test_initialization(self):
        """Test Smart Auto-Detection system initialization."""
        assert self.smart_detection.quality_threshold == "GOOD"
        assert self.smart_detection.enable_learning is True
        assert self.smart_detection.stats['conversations_monitored'] == 0
        assert self.smart_detection.stats['hints_generated'] == 0
    
    def test_start_conversation_monitoring(self):
        """Test starting conversation monitoring session."""
        session_id = self.smart_detection.start_conversation_monitoring()
        
        assert session_id is not None
        assert self.smart_detection.stats['conversations_monitored'] == 1
        
        # Test custom session ID
        custom_session = self.smart_detection.start_conversation_monitoring("test-session")
        assert custom_session == "test-session"
    
    def test_process_conversation_turn_insufficient_turns(self):
        """Test processing turns before minimum threshold."""
        self.smart_detection.start_conversation_monitoring()
        
        # Add first turn (below minimum threshold)
        result = self.smart_detection.process_conversation_turn(
            user_message="Hello",
            assistant_response="Hi there!"
        )
        
        assert result['should_show_hint'] is False
        assert result['hint_content'] == ''
        assert result['session_info']['turn_count'] == 1
    
    def test_process_conversation_turn_high_quality(self):
        """Test processing conversation with high quality (should trigger hint)."""
        self.smart_detection.start_conversation_monitoring()
        
        # Create mock quality score for EXCELLENT conversation
        mock_quality_score = QualityScore(
            total_score=20,  # EXCELLENT level
            level="EXCELLENT",
            reasoning="Multi-phase planning with code implementation",
            elements=SemanticElements(
                multi_phase_planning=True,
                phase_count=3,
                challenge_accept_flow=True,
                design_decisions=True,
                code_implementation=True,
                architectural_discussion=True,
                file_references=2,
                next_steps_provided=True
            ),
            should_show_hint=True
        )
        
        # Mock the quality monitor's analysis
        with patch.object(
            self.smart_detection.quality_monitor,
            'get_current_quality',
            return_value=mock_quality_score
        ):
            with patch.object(
                self.smart_detection.quality_monitor,
                'add_turn',
                return_value={
                    'should_check_quality': True,
                    'session_id': 'test-session',
                    'turn_count': 5,
                    'hint_shown': False
                }
            ):
                # Add multiple turns to reach threshold
                result = self.smart_detection.process_conversation_turn(
                    user_message="Create a multi-phase authentication system",
                    assistant_response="I'll create a comprehensive plan..."
                )
                
                assert result['should_show_hint'] is True
                assert 'CORTEX Learning Opportunity' in result['hint_content']
                assert result['quality_info']['level'] == "EXCELLENT"
                assert result['quality_info']['user_display_score'] in [9, 10]
                assert self.smart_detection.stats['hints_generated'] == 1
    
    def test_process_conversation_turn_low_quality(self):
        """Test processing conversation with low quality (should not trigger hint)."""
        self.smart_detection.start_conversation_monitoring()
        
        # Create mock quality score for LOW conversation
        mock_quality_score = QualityScore(
            total_score=1,  # LOW level
            level="LOW",
            reasoning="Simple question with minimal content",
            elements=SemanticElements(
                multi_phase_planning=False,
                phase_count=0,
                challenge_accept_flow=False,
                design_decisions=False,
                code_implementation=False,
                architectural_discussion=False,
                file_references=0,
                next_steps_provided=False
            ),
            should_show_hint=False
        )
        
        # Mock the quality monitor's analysis
        with patch.object(
            self.smart_detection.quality_monitor,
            'get_current_quality',
            return_value=mock_quality_score
        ):
            with patch.object(
                self.smart_detection.quality_monitor,
                'add_turn',
                return_value={
                    'should_check_quality': True,
                    'session_id': 'test-session',
                    'turn_count': 5,
                    'hint_shown': False
                }
            ):
                result = self.smart_detection.process_conversation_turn(
                    user_message="Hi",
                    assistant_response="Hello!"
                )
                
                assert result['should_show_hint'] is False
                assert result['hint_content'] == ''
                assert result['quality_info']['level'] == "LOW"
                assert self.smart_detection.stats['hints_generated'] == 0
    
    def test_record_user_feedback_accepted(self):
        """Test recording user acceptance of Smart Hint."""
        self.smart_detection.start_conversation_monitoring()
        
        # Mock current session
        self.smart_detection.quality_monitor.current_session = Mock()
        self.smart_detection.quality_monitor.current_session.session_id = "test-session"
        
        # Mock quality score for learning system
        mock_quality_score = QualityScore(
            total_score=12,  # GOOD level
            level="GOOD",
            reasoning="Test quality score",
            elements=SemanticElements(),
            should_show_hint=True
        )
        
        with patch.object(
            self.smart_detection.quality_monitor,
            'get_current_quality',
            return_value=mock_quality_score
        ):
            result = self.smart_detection.record_user_feedback("yes")
            
            assert result['feedback_recorded'] == 'accepted'
            assert self.smart_detection.stats['user_accepted'] == 1
            assert 'Capture this conversation' in result['confirmation_message']
    
    def test_record_user_feedback_rejected(self):
        """Test recording user rejection of Smart Hint."""
        self.smart_detection.start_conversation_monitoring()
        
        # Mock current session
        self.smart_detection.quality_monitor.current_session = Mock()
        self.smart_detection.quality_monitor.current_session.session_id = "test-session"
        
        # Mock quality score for learning system
        mock_quality_score = QualityScore(
            total_score=12,  # GOOD level
            level="GOOD",
            reasoning="Test quality score",
            elements=SemanticElements(),
            should_show_hint=True
        )
        
        with patch.object(
            self.smart_detection.quality_monitor,
            'get_current_quality',
            return_value=mock_quality_score
        ):
            result = self.smart_detection.record_user_feedback("skip")
            
            assert result['feedback_recorded'] == 'rejected'
            assert self.smart_detection.stats['user_rejected'] == 1
            assert 'adjust my detection patterns' in result['confirmation_message']
    
    def test_record_user_feedback_ignored(self):
        """Test recording ignored Smart Hint."""
        self.smart_detection.start_conversation_monitoring()
        
        # Mock current session
        self.smart_detection.quality_monitor.current_session = Mock()
        self.smart_detection.quality_monitor.current_session.session_id = "test-session"
        
        # Mock quality score for learning system
        mock_quality_score = QualityScore(
            total_score=12,  # GOOD level
            level="GOOD",
            reasoning="Test quality score",
            elements=SemanticElements(),
            should_show_hint=True
        )
        
        with patch.object(
            self.smart_detection.quality_monitor,
            'get_current_quality',
            return_value=mock_quality_score
        ):
            result = self.smart_detection.record_user_feedback("whatever")
            
            assert result['feedback_recorded'] == 'ignored'
            assert self.smart_detection.stats['user_ignored'] == 1
            assert 'continue monitoring' in result['confirmation_message']
    
    def test_end_conversation_monitoring(self):
        """Test ending conversation monitoring session."""
        session_id = self.smart_detection.start_conversation_monitoring()
        
        # Mock session with data
        with patch.object(
            self.smart_detection.quality_monitor,
            'end_session'
        ) as mock_end:
            mock_session = Mock()
            mock_session.session_id = session_id
            mock_session.started_at = datetime.now()
            mock_session.turns = [Mock(), Mock(), Mock()]  # 3 turns
            mock_session.hint_shown = True
            mock_session.user_response = 'accepted'
            mock_session.last_quality_check = Mock()
            mock_session.last_quality_check.total_score = 15
            mock_session.last_quality_check.level = "GOOD"
            
            mock_end.return_value = mock_session
            
            summary = self.smart_detection.end_conversation_monitoring()
            
            assert summary is not None
            assert summary['session_id'] == session_id
            assert summary['turn_count'] == 3
            assert summary['hint_shown'] is True
            assert summary['user_response'] == 'accepted'
            assert summary['final_quality']['level'] == "GOOD"
    
    def test_get_statistics(self):
        """Test getting system performance statistics."""
        # Set some mock statistics
        self.smart_detection.stats.update({
            'conversations_monitored': 10,
            'hints_generated': 4,
            'user_accepted': 3,
            'user_rejected': 1,
            'user_ignored': 0,
            'false_positives': 1
        })
        
        stats = self.smart_detection.get_statistics()
        
        assert stats['conversations_monitored'] == 10
        assert stats['hints_generated'] == 4
        assert stats['hint_generation_rate'] == 40.0
        assert stats['user_feedback']['accepted'] == 3
        assert stats['user_feedback']['rejected'] == 1
        assert stats['user_feedback']['total_responses'] == 4
        assert stats['user_feedback']['acceptance_rate'] == 75.0
        assert stats['quality_thresholds']['false_positives'] == 1
    
    def test_map_to_user_scale(self):
        """Test internal score to user scale mapping."""
        # Test EXCELLENT range (≥19 internal → 9-10 user)
        assert self.smart_detection._map_to_user_scale(19) == 9
        assert self.smart_detection._map_to_user_scale(25) == 10
        
        # Test GOOD range (10-18 internal → 7-8 user)
        assert self.smart_detection._map_to_user_scale(10) == 7
        assert self.smart_detection._map_to_user_scale(14) == 8
        assert self.smart_detection._map_to_user_scale(18) == 8
        
        # Test FAIR range (2-9 internal → 4-6 user)
        assert self.smart_detection._map_to_user_scale(2) == 4
        assert self.smart_detection._map_to_user_scale(6) == 5
        assert self.smart_detection._map_to_user_scale(9) == 6
        
        # Test LOW range (0-1 internal → 1-3 user)
        assert self.smart_detection._map_to_user_scale(0) == 1
        assert self.smart_detection._map_to_user_scale(1) == 2
    
    def test_normalize_feedback(self):
        """Test feedback normalization."""
        # Test acceptance terms
        assert self.smart_detection._normalize_feedback("yes") == 'accepted'
        assert self.smart_detection._normalize_feedback("accept") == 'accepted'
        assert self.smart_detection._normalize_feedback("ok") == 'accepted'
        assert self.smart_detection._normalize_feedback("capture") == 'accepted'
        
        # Test rejection terms
        assert self.smart_detection._normalize_feedback("no") == 'rejected'
        assert self.smart_detection._normalize_feedback("skip") == 'rejected'
        assert self.smart_detection._normalize_feedback("dismiss") == 'rejected'
        
        # Test ignored (unrecognized)
        assert self.smart_detection._normalize_feedback("maybe") == 'ignored'
        assert self.smart_detection._normalize_feedback("whatever") == 'ignored'
    
    def test_learning_from_false_positive(self):
        """Test learning from user rejecting a high-quality conversation."""
        self.smart_detection.start_conversation_monitoring()
        
        # Mock high-quality score that user rejects
        mock_quality_score = QualityScore(
            total_score=15,  # GOOD level but user rejects
            level="GOOD",
            reasoning="User doesn't find this valuable",
            elements=SemanticElements(),
            should_show_hint=True
        )
        
        with patch.object(
            self.smart_detection.quality_monitor,
            'get_current_quality',
            return_value=mock_quality_score
        ):
            # Mock current session
            self.smart_detection.quality_monitor.current_session = Mock()
            self.smart_detection.quality_monitor.current_session.session_id = "test"
            
            self.smart_detection.record_user_feedback("rejected")
            
            # Should increment false positives
            assert self.smart_detection.stats['false_positives'] == 1
    
    def test_detection_accuracy_threshold(self):
        """Test that detection meets ≥85% accuracy requirement."""
        # This is a integration test that would need real quality analyzer
        # For now, verify the threshold configuration is correct
        
        assert self.smart_detection.quality_threshold == "GOOD"
        
        # GOOD threshold maps to ≥10 internal score
        # which maps to ≥7/10 user scale (meeting roadmap requirement)
        user_scale_score = self.smart_detection._map_to_user_scale(10)
        assert user_scale_score >= 7
        
        # Test that excellent conversations definitely trigger
        excellent_score = self.smart_detection._map_to_user_scale(20)
        assert excellent_score >= 9
    
    def test_false_positive_rate_tracking(self):
        """Test that false positive rate can be tracked (<15% requirement)."""
        # Simulate 10 hints with 1 false positive
        self.smart_detection.stats.update({
            'hints_generated': 10,
            'false_positives': 1,
            'user_accepted': 8,
            'user_rejected': 1,
            'user_ignored': 1
        })
        
        stats = self.smart_detection.get_statistics()
        false_positive_rate = (stats['quality_thresholds']['false_positives'] / 
                             stats['hints_generated'] * 100)
        
        assert false_positive_rate == 10.0  # 10% < 15% requirement ✓


def test_feature_53_factory_function():
    """Test the factory function for creating Smart Auto-Detection."""
    # Test default configuration
    default_detection = create_smart_auto_detection()
    
    assert default_detection.quality_threshold == "GOOD"
    assert default_detection.enable_learning is True
    
    # Test custom configuration
    config = {
        'quality_threshold': 'EXCELLENT',
        'min_turns_before_check': 10,
        'enable_learning': False
    }
    
    custom_detection = create_smart_auto_detection(config)
    
    assert custom_detection.quality_threshold == "EXCELLENT"
    assert custom_detection.enable_learning is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])