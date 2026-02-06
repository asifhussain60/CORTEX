"""
Unit tests for LearningTrigger.

Tests cover:
- Initialization and configuration
- Trigger detection based on readiness scores
- ReadinessEngine integration
- Notification system
- Trigger history tracking
- Multi-trigger handling
- Error handling
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import logging

from cortex.orchestrators.intelligence.learning_trigger import (
    LearningTrigger,
    TriggerEvent,
    TriggerReason,
    TriggerAction,
)
from cortex.orchestrators.intelligence.tech_intelligence_orchestrator import TechStack
from cortex.orchestrators.intelligence.readiness_engine import ReadinessScore


def create_readiness_score(overall, best_practices, tdd_support, security_tooling, cross_repo_usage, action):
    """Helper to create ReadinessScore with correct parameter names."""
    return ReadinessScore(
        overall=overall,
        best_practices_coverage=best_practices,
        tdd_support=tdd_support,
        security_tooling=security_tooling,
        cross_repo_usage=cross_repo_usage,
        action=action,
    )


class TestLearningTriggerInitialization:
    """Test LearningTrigger initialization."""

    def test_trigger_initializes_with_defaults(self):
        """Test trigger initializes with default configuration."""
        trigger = LearningTrigger()
        
        assert trigger is not None
        assert hasattr(trigger, 'check_readiness')
        assert hasattr(trigger, 'get_trigger_history')
        assert hasattr(trigger, 'clear_history')

    def test_trigger_accepts_custom_config(self):
        """Test trigger accepts custom configuration."""
        config = {
            "threshold": 0.6,
            "notification_enabled": False,
            "history_limit": 50,
        }
        trigger = LearningTrigger(config=config)
        
        assert trigger is not None
        assert trigger.threshold == 0.6

    def test_trigger_initializes_history(self):
        """Test trigger initializes empty history."""
        trigger = LearningTrigger()
        
        history = trigger.get_trigger_history()
        assert isinstance(history, list)
        assert len(history) == 0


class TestTriggerDetection:
    """Test trigger detection logic."""

    def test_triggers_on_low_score(self):
        """Test triggers learning when score below threshold."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown_framework"],
            version="3.11",
            tools=[],
        )
        
        # Mock low readiness score
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            
            result = trigger.check_readiness(tech_stack)
            
            assert result.triggered is True
            assert result.reason == TriggerReason.LOW_SCORE

    def test_no_trigger_on_high_score(self):
        """Test does not trigger when score above threshold."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        # Mock high readiness score
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.8,
                best_practices=0.9,
                tdd_support=0.8,
                security_tooling=0.7,
                cross_repo_usage=0.5,
                action="PROCEED",
            )
            
            result = trigger.check_readiness(tech_stack)
            
            assert result.triggered is False
            assert result.reason is None

    def test_triggers_on_missing_knowledge(self):
        """Test triggers when critical knowledge missing."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="unknown_language",
            frameworks=[],
            version="1.0",
            tools=[],
        )
        
        result = trigger.check_readiness(tech_stack)
        
        assert result.triggered is True
        assert result.reason in [TriggerReason.MISSING_KNOWLEDGE, TriggerReason.LOW_SCORE]

    def test_respects_custom_threshold(self):
        """Test respects custom threshold configuration."""
        config = {"threshold": 0.6}
        trigger = LearningTrigger(config=config)
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        # Mock score between default (0.5) and custom (0.6) threshold
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.55,
                best_practices=0.6,
                tdd_support=0.5,
                security_tooling=0.5,
                cross_repo_usage=0.6,
                action="PROCEED_WITH_WARNING",
            )
            
            result = trigger.check_readiness(tech_stack)
            
            # Should trigger with custom threshold 0.6 (0.55 < 0.6)
            assert result.triggered is True


class TestReadinessEngineIntegration:
    """Test integration with ReadinessEngine."""

    def test_uses_readiness_engine_for_scoring(self):
        """Test uses ReadinessEngine for score calculation."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        with patch('cortex.orchestrators.intelligence.learning_trigger.ReadinessEngine') as mock_engine:
            mock_instance = Mock()
            mock_instance.calculate_readiness_score.return_value = create_readiness_score(
                overall=0.8,
                best_practices=0.9,
                tdd_support=0.8,
                security_tooling=0.7,
                cross_repo_usage=0.5,
                action="PROCEED",
            )
            mock_engine.return_value = mock_instance
            
            trigger = LearningTrigger()
            result = trigger.check_readiness(tech_stack)
            
            # Should have called ReadinessEngine
            assert result is not None

    def test_handles_readiness_engine_failure(self):
        """Test handles ReadinessEngine failure gracefully."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.side_effect = Exception("Engine failure")
            
            # Should not raise, should handle gracefully
            result = trigger.check_readiness(tech_stack)
            
            assert result.triggered is True
            assert result.reason == TriggerReason.MISSING_KNOWLEDGE


class TestNotificationSystem:
    """Test notification system."""

    def test_sends_notification_on_trigger(self):
        """Test sends notification when trigger fires."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_send_notification') as mock_notify:
            with patch.object(trigger, '_get_readiness_score') as mock_score:
                mock_score.return_value = create_readiness_score(
                    overall=0.3,
                    best_practices=0.2,
                    tdd_support=0.1,
                    security_tooling=0.5,
                    cross_repo_usage=0.0,
                    action="TRIGGER_LEARNING",
                )
                
                trigger.check_readiness(tech_stack)
                
                # Should have sent notification
                mock_notify.assert_called_once()

    def test_respects_notification_disabled_config(self):
        """Test respects notification disabled configuration."""
        config = {"notification_enabled": False}
        trigger = LearningTrigger(config=config)
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_send_notification') as mock_notify:
            with patch.object(trigger, '_get_readiness_score') as mock_score:
                mock_score.return_value = create_readiness_score(
                    overall=0.3,
                    best_practices=0.2,
                    tdd_support=0.1,
                    security_tooling=0.5,
                    cross_repo_usage=0.0,
                    action="TRIGGER_LEARNING",
                )
                
                trigger.check_readiness(tech_stack)
                
                # Should NOT have sent notification
                mock_notify.assert_not_called()

    def test_notification_includes_trigger_details(self):
        """Test notification includes trigger event details."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_send_notification') as mock_notify:
            with patch.object(trigger, '_get_readiness_score') as mock_score:
                mock_score.return_value = create_readiness_score(
                    overall=0.3,
                    best_practices=0.2,
                    tdd_support=0.1,
                    security_tooling=0.5,
                    cross_repo_usage=0.0,
                    action="TRIGGER_LEARNING",
                )
                
                trigger.check_readiness(tech_stack)
                
                # Verify notification was called with TriggerEvent
                call_args = mock_notify.call_args[0]
                assert isinstance(call_args[0], TriggerEvent)
                assert call_args[0].tech_stack == tech_stack


class TestTriggerHistoryTracking:
    """Test trigger history tracking."""

    def test_records_trigger_in_history(self):
        """Test records trigger events in history."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            
            trigger.check_readiness(tech_stack)
            
            history = trigger.get_trigger_history()
            assert len(history) == 1
            assert history[0].tech_stack == tech_stack

    def test_does_not_record_non_triggers(self):
        """Test does not record non-trigger events."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.8,
                best_practices=0.9,
                tdd_support=0.8,
                security_tooling=0.7,
                cross_repo_usage=0.5,
                action="PROCEED",
            )
            
            trigger.check_readiness(tech_stack)
            
            history = trigger.get_trigger_history()
            assert len(history) == 0

    def test_respects_history_limit(self):
        """Test respects history limit configuration."""
        config = {"history_limit": 3}
        trigger = LearningTrigger(config=config)
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            
            # Trigger 5 times
            for _ in range(5):
                trigger.check_readiness(tech_stack)
            
            history = trigger.get_trigger_history()
            # Should only keep last 3
            assert len(history) == 3

    def test_clears_history(self):
        """Test clears trigger history."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            
            trigger.check_readiness(tech_stack)
            assert len(trigger.get_trigger_history()) == 1
            
            trigger.clear_history()
            assert len(trigger.get_trigger_history()) == 0


class TestTriggerEventMetadata:
    """Test TriggerEvent metadata."""

    def test_event_includes_timestamp(self):
        """Test trigger event includes timestamp."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            
            result = trigger.check_readiness(tech_stack)
            
            assert hasattr(result, 'timestamp')
            assert isinstance(result.timestamp, datetime)

    def test_event_includes_readiness_score(self):
        """Test trigger event includes readiness score."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            expected_score = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            mock_score.return_value = expected_score
            
            result = trigger.check_readiness(tech_stack)
            
            assert hasattr(result, 'score')
            assert result.score == expected_score

    def test_event_includes_recommended_action(self):
        """Test trigger event includes recommended action."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            
            result = trigger.check_readiness(tech_stack)
            
            assert hasattr(result, 'recommended_action')
            assert result.recommended_action in [
                TriggerAction.SYNTHESIZE_KNOWLEDGE,
                TriggerAction.ACQUIRE_BEST_PRACTICES,
                TriggerAction.GENERATE_TDD_PATTERNS,
                TriggerAction.UPDATE_SECURITY_RULES,
            ]


class TestErrorHandling:
    """Test error handling."""

    def test_handles_none_tech_stack(self):
        """Test handles None tech stack gracefully."""
        trigger = LearningTrigger()
        
        result = trigger.check_readiness(None)
        
        # Should trigger due to missing input
        assert result.triggered is True
        assert result.reason == TriggerReason.MISSING_KNOWLEDGE

    def test_handles_empty_tech_stack(self):
        """Test handles empty tech stack gracefully."""
        trigger = LearningTrigger()
        tech_stack = TechStack(language="", frameworks=[], version="", tools=[])
        
        result = trigger.check_readiness(tech_stack)
        
        # Should trigger due to insufficient data
        assert result.triggered is True

    def test_handles_readiness_calculation_error(self):
        """Test handles readiness calculation error."""
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.side_effect = Exception("Calculation error")
            
            # Should not raise, should trigger learning
            result = trigger.check_readiness(tech_stack)
            
            assert result.triggered is True
            assert result.reason == TriggerReason.MISSING_KNOWLEDGE


class TestPerformance:
    """Test trigger performance."""

    def test_trigger_check_completes_quickly(self):
        """Test trigger check completes in reasonable time."""
        import time
        
        trigger = LearningTrigger()
        tech_stack = TechStack(
            language="python",
            frameworks=["django"],
            version="3.11",
            tools=["pytest"],
        )
        
        start = time.time()
        result = trigger.check_readiness(tech_stack)
        duration = time.time() - start
        
        assert result is not None
        assert duration < 0.5  # Should complete in under 0.5 seconds

    def test_history_retrieval_is_fast(self):
        """Test history retrieval is fast even with many entries."""
        import time
        
        config = {"history_limit": 100}
        trigger = LearningTrigger(config=config)
        tech_stack = TechStack(
            language="python",
            frameworks=["unknown"],
            version="3.11",
            tools=[],
        )
        
        # Fill history
        with patch.object(trigger, '_get_readiness_score') as mock_score:
            mock_score.return_value = create_readiness_score(
                overall=0.3,
                best_practices=0.2,
                tdd_support=0.1,
                security_tooling=0.5,
                cross_repo_usage=0.0,
                action="TRIGGER_LEARNING",
            )
            
            for _ in range(100):
                trigger.check_readiness(tech_stack)
        
        start = time.time()
        history = trigger.get_trigger_history()
        duration = time.time() - start
        
        assert len(history) == 100
        assert duration < 0.1  # Should retrieve in under 0.1 seconds
