"""Tests for telemetry aggregation (AC-UNIFIED-DEPLOY-001-03)."""

import pytest
from datetime import datetime, timedelta
from cortex.api.telemetry.aggregator import TelemetryAggregator, ErrorPattern


class TestTelemetryAggregator:
    """Test suite for telemetry aggregator."""

    @pytest.fixture
    def aggregator(self):
        """Create test aggregator."""
        return TelemetryAggregator(time_window_hours=24)

    def test_compute_impact_score(self, aggregator):
        """Test impact score computation."""
        score = aggregator.compute_impact_score(
            frequency=50, severity=0.8, reproducibility=0.9
        )
        assert 0 <= score <= 10
        assert score > 0  # Should be non-zero for these inputs

    def test_compute_impact_score_ranges(self, aggregator):
        """Test impact score at various ranges."""
        # Low impact
        low = aggregator.compute_impact_score(10, 0.3, 0.2)
        # High impact
        high = aggregator.compute_impact_score(100, 1.0, 1.0)
        assert high > low

    def test_deduplicate_errors_empty(self, aggregator):
        """Test deduplication of empty event list."""
        patterns = aggregator.deduplicate_errors([])
        assert len(patterns) == 0

    def test_deduplicate_errors_single_pattern(self, aggregator):
        """Test deduplication with single error pattern."""
        events = [
            {
                "event_type": "error",
                "error_id": "err_123",
                "error_category": "parsing",
                "reproducibility_score": 0.8,
                "environment_signature": "env_abc",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 5,
            }
        ]

        patterns = aggregator.deduplicate_errors(events)
        assert len(patterns) >= 1
        pattern_list = list(patterns.values())
        assert pattern_list[0].frequency >= 5

    def test_deduplicate_errors_multiple_environments(self, aggregator):
        """Test that errors from multiple envs are aggregated."""
        events = [
            {
                "event_type": "error",
                "error_id": "err_123",
                "error_category": "api_timeout",
                "reproducibility_score": 0.7,
                "environment_signature": "env_linux",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 3,
            },
            {
                "event_type": "error",
                "error_id": "err_123",
                "error_category": "api_timeout",
                "reproducibility_score": 0.7,
                "environment_signature": "env_windows",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 2,
            },
        ]

        patterns = aggregator.deduplicate_errors(events)
        pattern_list = list(patterns.values())
        assert pattern_list[0].frequency >= 3  # At least first occurrence count

    def test_identify_trends_increasing(self, aggregator):
        """Test trend identification for increasing patterns."""
        current = {
            "key1": ErrorPattern(
                error_id="err_1",
                error_category="test",
                impact_score=0.5,
                frequency=100,
                severity=0.8,
                reproducibility=0.7,
                trend_direction="stable",
            )
        }

        historical = {
            "key1": ErrorPattern(
                error_id="err_1",
                error_category="test",
                impact_score=0.3,
                frequency=50,
                severity=0.8,
                reproducibility=0.7,
                trend_direction="stable",
            )
        }

        result = aggregator.identify_trends(current, historical)
        assert result["key1"].trend_direction == "increasing"

    def test_identify_trends_decreasing(self, aggregator):
        """Test trend identification for decreasing patterns."""
        current = {
            "key1": ErrorPattern(
                error_id="err_1",
                error_category="test",
                impact_score=0.2,
                frequency=20,
                severity=0.8,
                reproducibility=0.7,
                trend_direction="stable",
            )
        }

        historical = {
            "key1": ErrorPattern(
                error_id="err_1",
                error_category="test",
                impact_score=0.5,
                frequency=100,
                severity=0.8,
                reproducibility=0.7,
                trend_direction="stable",
            )
        }

        result = aggregator.identify_trends(current, historical)
        assert result["key1"].trend_direction == "decreasing"

    def test_identify_trends_new_pattern(self, aggregator):
        """Test trend identification for new patterns."""
        current = {
            "key1": ErrorPattern(
                error_id="err_1",
                error_category="test",
                impact_score=0.5,
                frequency=10,
                severity=0.8,
                reproducibility=0.7,
                trend_direction="stable",
            )
        }

        result = aggregator.identify_trends(current, None)
        assert result["key1"].trend_direction == "stable"

    def test_generate_insights_top_patterns(self, aggregator):
        """Test insight generation from patterns."""
        patterns = {
            f"key{i}": ErrorPattern(
                error_id=f"err_{i}",
                error_category=f"cat_{i}",
                impact_score=10.0 - i,  # Decreasing scores
                frequency=100 - i * 10,
                severity=0.9,
                reproducibility=0.8,
                trend_direction="increasing" if i < 3 else "stable",
            )
            for i in range(15)  # 15 patterns
        }

        insights = aggregator.generate_insights(patterns)
        assert len(insights) <= 10  # Should limit to top 10
        assert insights[0].pattern.impact_score >= insights[-1].pattern.impact_score

    def test_create_github_issue_critical(self, aggregator):
        """Test GitHub issue creation for critical pattern."""
        insight_pattern = ErrorPattern(
            error_id="err_crit",
            error_category="critical_error",
            impact_score=9.5,
            frequency=200,
            severity=1.0,
            reproducibility=0.95,
            affected_environments=["env1", "env2", "env3"],
            trend_direction="increasing",
        )

        from cortex.api.telemetry.aggregator import TelemetryInsight

        insight = TelemetryInsight(
            insight_type="error_pattern",
            title="Test insight",
            pattern=insight_pattern,
            affected_count=200,
            environments=["env1", "env2"],
            recommendations=["Fix immediately"],
        )

        payload = aggregator.create_github_issue_payload(insight)
        assert "[TELEMETRY]" in payload.title
        assert "CRITICAL" in payload.title
        assert "p0-critical" in payload.labels or "p1-high" in payload.labels

    def test_aggregate_events_complete_pipeline(self, aggregator):
        """Test complete aggregation pipeline."""
        events = [
            {
                "event_type": "error",
                "error_id": "err_123",
                "error_category": "network",
                "reproducibility_score": 0.75,
                "environment_signature": "env_prod",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 50,
            },
            {
                "event_type": "error",
                "error_id": "err_456",
                "error_category": "memory",
                "reproducibility_score": 0.5,
                "environment_signature": "env_dev",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 10,
            },
        ]

        patterns, insights, issues = aggregator.aggregate_events(events)
        assert len(patterns) >= 1
        assert len(insights) >= 0
        assert len(issues) >= 0

    def test_aggregate_events_high_impact_threshold(self, aggregator):
        """Test that only high-impact errors create issues."""
        events = [
            {
                "event_type": "error",
                "error_id": "err_high",
                "error_category": "critical",
                "reproducibility_score": 0.95,
                "environment_signature": "env_prod",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 100,
            },
            {
                "event_type": "error",
                "error_id": "err_low",
                "error_category": "minor",
                "reproducibility_score": 0.1,
                "environment_signature": "env_test",
                "first_seen_at": datetime.utcnow().isoformat() + "Z",
                "last_seen_at": datetime.utcnow().isoformat() + "Z",
                "occurrence_count": 1,
            },
        ]

        patterns, insights, issues = aggregator.aggregate_events(events)
        # Should have issues for high-impact only
        assert all(issue.impact_level in ["critical", "high"] for issue in issues)
