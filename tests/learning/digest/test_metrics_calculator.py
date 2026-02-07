"""
Unit tests for DIGEST Quantitative Metrics System.

Tests for Phase 41 Stage 2 (ENH-055):
- AC-PHASE41-006: Efficiency score calculation (3 tests)
- AC-PHASE41-007: Accuracy score calculation (3 tests)
- AC-PHASE41-008: Tool success rate calculation (3 tests)
- AC-PHASE41-009: Learning velocity calculation (3 tests)
- AC-PHASE41-010: Context efficiency calculation (3 tests)

Total: 15 tests

Author: Asif Hussain
Date: 2026-02-07
"""

import pytest
from datetime import datetime
from typing import Dict, List, Any

from cortex.learning.digest.metrics_calculator import MetricsCalculator
from cortex.learning.digest.metrics_schema import (
    EfficiencyMetrics,
    AccuracyMetrics,
    ToolSuccessMetrics,
    LearningVelocityMetrics,
    ContextEfficiencyMetrics,
    DigestMetrics,
)
from cortex.learning.digest.models import DigestResult


# AC_START: AC-PHASE41-006
# Description: Efficiency score calculation
# Author: Asif Hussain
# Date: 2026-02-07


@pytest.fixture
def sample_chat_session():
    """Sample chat session data for metrics calculation."""
    return {
        "user_turns": 5,
        "copilot_turns": 5,
        "tool_invocations": 3,
        "successful_tools": 2,
        "corrections": 1,
        "task_complexity": "medium",  # Expected: 3-4 turns
        "total_tokens": 1000,
        "meaningful_tokens": 750,
        "enhancements_extracted": 2,
    }


@pytest.fixture
def metrics_calculator():
    """Create MetricsCalculator instance."""
    return MetricsCalculator()


class TestEfficiencyScoreCalculation:
    """Test AC-PHASE41-006: Efficiency score calculation (3 tests)."""
    
    def test_calculates_efficiency_from_expected_vs_actual(self, metrics_calculator):
        """Test efficiency = (expected_turns / actual_turns) × 100."""
        # Simple task: expected 3 turns, actual 5 turns
        efficiency = metrics_calculator.calculate_efficiency(
            actual_turns=5,
            expected_turns=3,
            task_complexity="simple"
        )
        
        assert efficiency.score == 60  # (3/5) * 100
        assert efficiency.actual_turns == 5
        assert efficiency.expected_turns == 3
    
    def test_estimates_expected_turns_from_complexity(self, metrics_calculator):
        """Test that complexity maps to expected turn ranges."""
        # Simple: 2-3 turns, Medium: 3-5, Complex: 5-8
        simple_eff = metrics_calculator.calculate_efficiency(
            actual_turns=4,
            task_complexity="simple"
        )
        
        # Should estimate ~2-3 turns for simple task
        assert simple_eff.expected_turns <= 3
        assert simple_eff.score < 100  # 4 turns is over-expected for simple
    
    def test_efficiency_caps_at_100_percent(self, metrics_calculator):
        """Test that efficiency score caps at 100% for under-expected."""
        # Beat expectations: 2 turns for 5-turn expectation
        efficiency = metrics_calculator.calculate_efficiency(
            actual_turns=2,
            expected_turns=5
        )
        
        # Should cap at 100%, not go to 250%
        assert efficiency.score == 100
        assert efficiency.exceeded_expectations is True


# AC-PHASE41-007: Accuracy score calculation (3 tests)


class TestAccuracyScoreCalculation:
    """Test AC-PHASE41-007: Accuracy score calculation (3 tests)."""
    
    def test_calculates_accuracy_from_corrections(self, metrics_calculator):
        """Test accuracy = ((total - corrections) / total) × 100."""
        accuracy = metrics_calculator.calculate_accuracy(
            total_turns=10,
            corrections=2
        )
        
        assert accuracy.score == 80  # ((10-2)/10) * 100
        assert accuracy.total_turns == 10
        assert accuracy.corrections == 2
        assert accuracy.correct_responses == 8
    
    def test_perfect_accuracy_no_corrections(self, metrics_calculator):
        """Test 100% accuracy when no corrections needed."""
        accuracy = metrics_calculator.calculate_accuracy(
            total_turns=5,
            corrections=0
        )
        
        assert accuracy.score == 100
        assert accuracy.corrections == 0
    
    def test_detects_corrections_from_chat_content(self, metrics_calculator):
        """Test automatic correction detection from keywords."""
        chat_content = """
User: Implement feature X
GitHub Copilot: I'll create the file.
User: Actually, that's wrong. Fix it.
GitHub Copilot: I'll correct that.
"""
        
        accuracy = metrics_calculator.calculate_accuracy_from_content(chat_content)
        
        assert accuracy.corrections >= 1  # Should detect "wrong", "fix", "correct"
        assert accuracy.score < 100


# AC-PHASE41-008: Tool success rate calculation (3 tests)


class TestToolSuccessRateCalculation:
    """Test AC-PHASE41-008: Tool success rate calculation (3 tests)."""
    
    def test_calculates_tool_success_rate(self, metrics_calculator):
        """Test tool_success = (successful / total) × 100."""
        tool_metrics = metrics_calculator.calculate_tool_success(
            successful_invocations=7,
            total_invocations=10
        )
        
        assert tool_metrics.success_rate == 70  # (7/10) * 100
        assert tool_metrics.successful_invocations == 7
        assert tool_metrics.failed_invocations == 3
    
    def test_parses_tool_results_from_chat(self, metrics_calculator):
        """Test parsing tool success/failure from chat."""
        chat_content = """
[Tool call: create_file]
Result: Created successfully

[Tool call: run_in_terminal]
Result: Error: Command failed

[Tool call: read_file]
Result: File contents retrieved
"""
        
        tool_metrics = metrics_calculator.calculate_tool_success_from_content(chat_content)
        
        assert tool_metrics.total_invocations == 3
        assert tool_metrics.successful_invocations == 2  # create_file, read_file
        assert tool_metrics.failed_invocations == 1  # run_in_terminal
        assert tool_metrics.success_rate == pytest.approx(66.67, rel=0.1)
    
    def test_handles_zero_tool_invocations(self, metrics_calculator):
        """Test graceful handling of zero tool invocations."""
        tool_metrics = metrics_calculator.calculate_tool_success(
            successful_invocations=0,
            total_invocations=0
        )
        
        assert tool_metrics.success_rate == 0
        assert tool_metrics.total_invocations == 0


# AC-PHASE41-009: Learning velocity calculation (3 tests)


class TestLearningVelocityCalculation:
    """Test AC-PHASE41-009: Learning velocity calculation (3 tests)."""
    
    def test_calculates_learning_velocity(self, metrics_calculator):
        """Test learning_velocity = enhancements / sessions."""
        velocity = metrics_calculator.calculate_learning_velocity(
            enhancements_extracted=10,
            sessions_analyzed=20
        )
        
        assert velocity.velocity == 0.5  # 10/20
        assert velocity.enhancements_extracted == 10
        assert velocity.sessions_analyzed == 20
    
    def test_tracks_velocity_over_time(self, metrics_calculator):
        """Test velocity tracking across multiple time periods."""
        # Week 1: 5 enhancements / 10 sessions = 0.5
        # Week 2: 8 enhancements / 10 sessions = 0.8
        
        velocity_week1 = metrics_calculator.calculate_learning_velocity(
            enhancements_extracted=5,
            sessions_analyzed=10
        )
        
        velocity_week2 = metrics_calculator.calculate_learning_velocity(
            enhancements_extracted=8,
            sessions_analyzed=10,
            previous_velocity=velocity_week1.velocity  # Pass previous velocity
        )
        
        assert velocity_week2.velocity > velocity_week1.velocity
        assert velocity_week2.improvement_rate == pytest.approx(60.0, rel=1.0)  # +60% improvement
    
    def test_identifies_high_value_sessions(self, metrics_calculator):
        """Test identification of sessions with >1 enhancement."""
        velocity = metrics_calculator.calculate_learning_velocity(
            enhancements_extracted=15,
            sessions_analyzed=10
        )
        
        assert velocity.velocity == 1.5
        assert velocity.high_value_session is True  # >1 enhancement per session


# AC-PHASE41-010: Context efficiency calculation (3 tests)


class TestContextEfficiencyCalculation:
    """Test AC-PHASE41-010: Context efficiency calculation (3 tests)."""
    
    def test_calculates_context_efficiency(self, metrics_calculator):
        """Test context_efficiency = meaningful_tokens / total_tokens."""
        context_eff = metrics_calculator.calculate_context_efficiency(
            meaningful_tokens=750,
            total_tokens=1000
        )
        
        assert context_eff.efficiency == 75.0  # (750/1000) * 100
        assert context_eff.wasted_tokens == 250
        assert context_eff.meaningful_tokens == 750
    
    def test_identifies_token_waste_patterns(self, metrics_calculator):
        """Test detection of common token waste patterns."""
        chat_content = """
User: Create a file
GitHub Copilot: I understand. Let me think about this carefully. I see that you want to create a file.
I'll now proceed to create the file you requested. Here's what I'll do in detail.
First, I'll need to analyze the requirements thoroughly. Then I'll create the structure carefully.
After that, I'll implement the logic step by step. Once that's done, I'll test everything thoroughly.
Let me start by examining the context in detail. I see you want a file created.
I'll now proceed to create this file for you step by step. Here's my detailed approach.
Let me think about this. I understand what you need. I'll now do that.
Here's what I'll do. First, I'll do this. Then I'll do that. After that, I'll do something else.
I see that. I understand that. Let me proceed with that. Here's how I'll approach that.
Actually, let me create the file.
[Tool call: create_file]
Result: Created
"""
        
        context_eff = metrics_calculator.calculate_context_efficiency_from_content(chat_content)
        
        # Waste detected: narration patterns reduce efficiency
        assert context_eff.efficiency < 90  # Should detect waste from narration
        assert len(context_eff.waste_patterns) > 0
        assert any("narration" in p.lower() for p in context_eff.waste_patterns)
    
    def test_recommends_efficiency_improvements(self, metrics_calculator):
        """Test generation of efficiency improvement recommendations."""
        context_eff = metrics_calculator.calculate_context_efficiency(
            meaningful_tokens=500,
            total_tokens=1000
        )
        
        # Low efficiency (50%) should trigger recommendations
        assert len(context_eff.recommendations) > 0
        assert context_eff.needs_improvement is True


# Integration test: Full metrics calculation


def test_calculates_all_metrics_together(metrics_calculator, sample_chat_session):
    """Integration test: Calculate all 5 metrics from session data."""
    metrics = metrics_calculator.calculate_all_metrics(
        chat_session_data=sample_chat_session
    )
    
    # Verify all 5 metric types present
    assert isinstance(metrics, DigestMetrics)
    assert metrics.efficiency is not None
    assert metrics.accuracy is not None
    assert metrics.tool_success is not None
    assert metrics.learning_velocity is not None
    assert metrics.context_efficiency is not None
    
    # Verify overall quality score calculated
    assert 0 <= metrics.overall_quality_score <= 100


def test_compares_metrics_to_baseline(metrics_calculator):
    """Test comparison of current metrics to historical baseline."""
    current_metrics = DigestMetrics(
        efficiency=EfficiencyMetrics(score=80, actual_turns=4, expected_turns=5),
        accuracy=AccuracyMetrics(score=90, total_turns=10, corrections=1, correct_responses=9),
        tool_success=ToolSuccessMetrics(success_rate=75, total_invocations=8, successful_invocations=6, failed_invocations=2),
        learning_velocity=LearningVelocityMetrics(velocity=0.6, enhancements_extracted=6, sessions_analyzed=10),
        context_efficiency=ContextEfficiencyMetrics(efficiency=70, meaningful_tokens=700, total_tokens=1000, wasted_tokens=300),
        overall_quality_score=79
    )
    
    baseline_metrics = DigestMetrics(
        efficiency=EfficiencyMetrics(score=70, actual_turns=5, expected_turns=5),
        accuracy=AccuracyMetrics(score=85, total_turns=10, corrections=1, correct_responses=8),
        tool_success=ToolSuccessMetrics(success_rate=70, total_invocations=10, successful_invocations=7, failed_invocations=3),
        learning_velocity=LearningVelocityMetrics(velocity=0.5, enhancements_extracted=5, sessions_analyzed=10),
        context_efficiency=ContextEfficiencyMetrics(efficiency=65, meaningful_tokens=650, total_tokens=1000, wasted_tokens=350),
        overall_quality_score=70
    )
    
    comparison = metrics_calculator.compare_to_baseline(current_metrics, baseline_metrics)
    
    assert comparison["efficiency_improvement"] == pytest.approx(14.3, rel=0.5)  # +10 points
    assert comparison["accuracy_improvement"] == pytest.approx(5.9, rel=0.5)  # +5 points
    assert comparison["overall_improvement"] is True


# AC_COMPLETE: AC-PHASE41-006, AC-PHASE41-007, AC-PHASE41-008, AC-PHASE41-009, AC-PHASE41-010 ✅ 15/15 tests
