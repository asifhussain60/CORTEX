"""
Tests for Effectiveness Analyzer - Phase 12 S2

AC-PHASE71-007: Pattern effectiveness scoring and tracking

Tests effectiveness analysis of learned patterns:
- Success rate tracking
- Time savings calculation
- Quality improvement metrics
- Historical effectiveness analysis

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any, Dict, List

import pytest

from cortex.learning.effectiveness_analyzer import (
    EffectivenessAnalyzer,
    EffectivenessMetrics,
    PatternApplication,
)


@pytest.fixture
def analyzer() -> EffectivenessAnalyzer:
    """Create EffectivenessAnalyzer instance."""
    return EffectivenessAnalyzer()


@pytest.fixture
def sample_application() -> PatternApplication:
    """Create sample pattern application."""
    return PatternApplication(
        pattern_id="extract_method_refactoring",
        orchestrator="RefactoringOrchestrator",
        timestamp=datetime.now(),
        success=True,
        time_taken_seconds=45.0,
        quality_before=0.6,
        quality_after=0.85,
        context={"complexity_reduced": 7}
    )


class TestEffectivenessAnalyzerInitialization:
    """Test EffectivenessAnalyzer initialization."""

    def test_initialization(self) -> None:
        """Test analyzer initialization with defaults."""
        analyzer = EffectivenessAnalyzer()

        assert analyzer is not None
        assert len(analyzer._applications) == 0

    def test_initial_metrics_empty(self, analyzer: EffectivenessAnalyzer) -> None:
        """Test getting metrics from fresh analyzer."""
        metrics = analyzer.get_metrics_for_pattern("nonexistent")

        assert metrics.success_rate == 0.0
        assert metrics.total_applications == 0


class TestPatternApplicationTracking:
    """Test tracking pattern applications."""

    def test_record_single_application(
        self,
        analyzer: EffectivenessAnalyzer,
        sample_application: PatternApplication
    ) -> None:
        """Test recording a single pattern application."""
        analyzer.record_application(sample_application)

        metrics = analyzer.get_metrics_for_pattern("extract_method_refactoring")
        assert metrics.total_applications == 1
        assert metrics.success_rate == 1.0

    def test_record_multiple_applications(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test recording multiple applications of same pattern."""
        pattern_id = "test_pattern"
        
        for i in range(5):
            app = PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=True,
                time_taken_seconds=10.0,
                quality_before=0.5,
                quality_after=0.7
            )
            analyzer.record_application(app)

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert metrics.total_applications == 5
        assert metrics.success_rate == 1.0

    def test_record_mixed_success_failure(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test recording applications with mixed success/failure."""
        pattern_id = "mixed_pattern"
        
        # 3 successes
        for _ in range(3):
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=True,
                time_taken_seconds=10.0,
                quality_before=0.5,
                quality_after=0.7
            ))
        
        # 2 failures
        for _ in range(2):
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=False,
                time_taken_seconds=10.0,
                quality_before=0.5,
                quality_after=0.5
            ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert metrics.total_applications == 5
        assert metrics.success_rate == 0.6  # 3/5


class TestSuccessRateCalculation:
    """Test success rate calculation."""

    def test_perfect_success_rate(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test pattern with 100% success rate."""
        pattern_id = "perfect_pattern"
        
        for _ in range(10):
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=True,
                time_taken_seconds=5.0,
                quality_before=0.5,
                quality_after=0.8
            ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert metrics.success_rate == 1.0

    def test_zero_success_rate(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test pattern with 0% success rate."""
        pattern_id = "failing_pattern"
        
        for _ in range(5):
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=False,
                time_taken_seconds=5.0,
                quality_before=0.5,
                quality_after=0.5
            ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert metrics.success_rate == 0.0

    def test_success_rate_as_float_between_0_and_1(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test success rate is always float between 0.0 and 1.0."""
        pattern_id = "test_pattern"
        
        # Record 7 successes out of 10
        for i in range(10):
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=(i < 7),
                time_taken_seconds=5.0,
                quality_before=0.5,
                quality_after=0.7 if i < 7 else 0.5
            ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert 0.0 <= metrics.success_rate <= 1.0
        assert metrics.success_rate == 0.7


class TestTimeSavingsCalculation:
    """Test time savings calculation."""

    def test_average_time_calculation(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test calculating average time for pattern."""
        pattern_id = "timed_pattern"
        times = [10.0, 20.0, 30.0, 40.0, 50.0]
        
        for time in times:
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=True,
                time_taken_seconds=time,
                quality_before=0.5,
                quality_after=0.7
            ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert metrics.average_time_seconds == 30.0  # (10+20+30+40+50)/5

    def test_time_savings_vs_baseline(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test calculating time savings vs baseline."""
        pattern_id = "efficient_pattern"
        baseline_time = 100.0
        
        # Record applications that take less time
        for _ in range(5):
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=True,
                time_taken_seconds=60.0,  # 40% faster than baseline
                quality_before=0.5,
                quality_after=0.7
            ))

        savings = analyzer.calculate_time_savings(pattern_id, baseline_time)
        assert savings == 40.0  # 40 seconds saved per application


class TestQualityImprovementMetrics:
    """Test quality improvement calculation."""

    def test_average_quality_improvement(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test calculating average quality improvement."""
        pattern_id = "quality_pattern"
        
        improvements = [0.1, 0.2, 0.15, 0.25, 0.3]
        for improvement in improvements:
            before = 0.5
            after = before + improvement
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=datetime.now(),
                success=True,
                time_taken_seconds=10.0,
                quality_before=before,
                quality_after=after
            ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        # Average improvement: (0.1+0.2+0.15+0.25+0.3)/5 = 0.2
        assert abs(metrics.average_quality_improvement - 0.2) < 0.01

    def test_quality_improvement_handles_no_change(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test quality improvement when quality unchanged."""
        pattern_id = "neutral_pattern"
        
        analyzer.record_application(PatternApplication(
            pattern_id=pattern_id,
            orchestrator="TestOrch",
            timestamp=datetime.now(),
            success=True,
            time_taken_seconds=10.0,
            quality_before=0.7,
            quality_after=0.7  # No change
        ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert metrics.average_quality_improvement == 0.0

    def test_quality_improvement_handles_regression(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test quality improvement when quality decreases."""
        pattern_id = "regression_pattern"
        
        analyzer.record_application(PatternApplication(
            pattern_id=pattern_id,
            orchestrator="TestOrch",
            timestamp=datetime.now(),
            success=False,
            time_taken_seconds=10.0,
            quality_before=0.8,
            quality_after=0.6  # Regression
        ))

        metrics = analyzer.get_metrics_for_pattern(pattern_id)
        assert metrics.average_quality_improvement < 0.0


class TestHistoricalEffectivenessAnalysis:
    """Test historical effectiveness tracking."""

    def test_get_effectiveness_over_time(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test getting effectiveness metrics over time period."""
        pattern_id = "historical_pattern"
        now = datetime.now()
        
        # Record applications over 30 days
        for days_ago in range(30, 0, -1):
            timestamp = now - timedelta(days=days_ago)
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=timestamp,
                success=True,
                time_taken_seconds=10.0,
                quality_before=0.5,
                quality_after=0.7
            ))

        # Get metrics for last 7 days
        recent_metrics = analyzer.get_metrics_for_pattern(
            pattern_id,
            since=now - timedelta(days=7)
        )
        
        assert recent_metrics.total_applications == 7

    def test_effectiveness_trend_analysis(
        self,
        analyzer: EffectivenessAnalyzer
    ) -> None:
        """Test analyzing effectiveness trends over time."""
        pattern_id = "trending_pattern"
        now = datetime.now()
        
        # Record improving effectiveness over time
        for i in range(10):
            timestamp = now - timedelta(days=9-i)
            success = i >= 3  # First 3 fail, then succeed
            
            analyzer.record_application(PatternApplication(
                pattern_id=pattern_id,
                orchestrator="TestOrch",
                timestamp=timestamp,
                success=success,
                time_taken_seconds=10.0,
                quality_before=0.5,
                quality_after=0.7 if success else 0.5
            ))

        trend = analyzer.analyze_trend(pattern_id)
        assert trend == "improving"  # Success rate improved over time


class TestEffectivenessMetricsDataClass:
    """Test EffectivenessMetrics data class."""

    def test_metrics_creation(self) -> None:
        """Test creating EffectivenessMetrics instance."""
        metrics = EffectivenessMetrics(
            pattern_id="test_pattern",
            total_applications=10,
            successful_applications=8,
            success_rate=0.8,
            average_time_seconds=25.5,
            average_quality_improvement=0.15,
            last_application=datetime.now()
        )

        assert metrics.pattern_id == "test_pattern"
        assert metrics.success_rate == 0.8
        assert metrics.total_applications == 10

    def test_metrics_to_dict(self) -> None:
        """Test converting metrics to dictionary."""
        now = datetime.now()
        metrics = EffectivenessMetrics(
            pattern_id="test_pattern",
            total_applications=5,
            successful_applications=4,
            success_rate=0.8,
            average_time_seconds=20.0,
            average_quality_improvement=0.2,
            last_application=now
        )

        data = metrics.to_dict()
        
        assert data["pattern_id"] == "test_pattern"
        assert data["success_rate"] == 0.8
        assert "last_application" in data


class TestPatternApplicationDataClass:
    """Test PatternApplication data class."""

    def test_application_creation(self) -> None:
        """Test creating PatternApplication instance."""
        now = datetime.now()
        app = PatternApplication(
            pattern_id="test_pattern",
            orchestrator="TestOrch",
            timestamp=now,
            success=True,
            time_taken_seconds=15.5,
            quality_before=0.6,
            quality_after=0.8,
            context={"test": "data"}
        )

        assert app.pattern_id == "test_pattern"
        assert app.success is True
        assert app.time_taken_seconds == 15.5
        assert app.context["test"] == "data"

    def test_application_quality_improvement(self) -> None:
        """Test calculating quality improvement from application."""
        app = PatternApplication(
            pattern_id="test",
            orchestrator="TestOrch",
            timestamp=datetime.now(),
            success=True,
            time_taken_seconds=10.0,
            quality_before=0.5,
            quality_after=0.75
        )

        improvement = app.quality_after - app.quality_before
        assert improvement == 0.25
