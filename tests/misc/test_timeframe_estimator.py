"""
Tests for TIMEFRAME Entry Point Module

Test Coverage:
- Story point calculation (complexity → Fibonacci)
- Hours estimation (single developer)
- Team effort calculation (with communication overhead)
- Sprint allocation (with/without velocity)
- Effort breakdown generation
- Confidence determination
- Three-point estimation (PERT)
- Report formatting
- Edge cases and validation
"""

import pytest
from src.agents.estimation.timeframe_estimator import (
    TimeframeEstimator,
    TimeEstimate,
    quick_estimate
)


class TestStoryPointCalculation:
    """Test complexity → story point conversion"""
    
    def test_trivial_complexity_maps_to_1_point(self):
        """Complexity 0-10 → 1 story point"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(5) == 1
        assert estimator._complexity_to_story_points(10) == 1
    
    def test_simple_complexity_maps_to_2_points(self):
        """Complexity 11-20 → 2 story points"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(15) == 2
        assert estimator._complexity_to_story_points(20) == 2
    
    def test_small_complexity_maps_to_3_points(self):
        """Complexity 21-35 → 3 story points"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(25) == 3
        assert estimator._complexity_to_story_points(35) == 3
    
    def test_medium_complexity_maps_to_5_points(self):
        """Complexity 36-50 → 5 story points"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(42) == 5
        assert estimator._complexity_to_story_points(50) == 5
    
    def test_large_complexity_maps_to_8_points(self):
        """Complexity 51-65 → 8 story points"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(58) == 8
        assert estimator._complexity_to_story_points(65) == 8
    
    def test_very_large_complexity_maps_to_13_points(self):
        """Complexity 66-80 → 13 story points"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(70) == 13
        assert estimator._complexity_to_story_points(80) == 13
    
    def test_huge_complexity_maps_to_21_points(self):
        """Complexity 81-90 → 21 story points"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(85) == 21
        assert estimator._complexity_to_story_points(90) == 21
    
    def test_epic_complexity_maps_to_34_points(self):
        """Complexity 91-100 → 34 story points"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(95) == 34
        assert estimator._complexity_to_story_points(100) == 34
    
    def test_boundary_values(self):
        """Test exact boundary conditions"""
        estimator = TimeframeEstimator()
        assert estimator._complexity_to_story_points(0) == 1
        assert estimator._complexity_to_story_points(11) == 2
        assert estimator._complexity_to_story_points(21) == 3
        assert estimator._complexity_to_story_points(36) == 5
        assert estimator._complexity_to_story_points(51) == 8
        assert estimator._complexity_to_story_points(66) == 13
        assert estimator._complexity_to_story_points(81) == 21
        assert estimator._complexity_to_story_points(91) == 34


class TestHoursEstimation:
    """Test hours calculation"""
    
    def test_default_hours_per_point_is_4(self):
        """Default: 4 hours per story point"""
        estimator = TimeframeEstimator()
        assert estimator.hours_per_point == 4.0
    
    def test_single_developer_hours_calculation(self):
        """Hours = story_points * hours_per_point"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)  # 5 points
        assert estimate.story_points == 5
        assert estimate.hours_single == 20.0  # 5 * 4
    
    def test_custom_hours_per_point(self):
        """Support custom hours per point configuration"""
        estimator = TimeframeEstimator(hours_per_point=6.0)
        estimate = estimator.estimate_timeframe(complexity=42)  # 5 points
        assert estimate.hours_single == 30.0  # 5 * 6
    
    def test_days_calculation(self):
        """Days = hours / working_hours_per_day"""
        estimator = TimeframeEstimator(working_hours_day=6.0)
        estimate = estimator.estimate_timeframe(complexity=42)  # 5 points, 20h
        assert estimate.days_single == pytest.approx(3.3, 0.1)  # 20 / 6


class TestTeamEffortCalculation:
    """Test team capacity and communication overhead"""
    
    def test_single_developer_has_no_overhead(self):
        """Team size 1: no communication overhead"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=1)
        assert estimate.hours_single == estimate.hours_team
        assert estimate.days_single == estimate.days_team
    
    def test_two_developers_have_5_percent_overhead(self):
        """Team size 2: 5% communication overhead"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=2)
        
        # Single: 20h
        # Ideal parallel: 20h / 2 = 10h
        # Overhead: 10h * 1.05 = 10.5h per person
        assert estimate.hours_team == pytest.approx(10.5, 0.1)
    
    def test_three_developers_have_10_percent_overhead(self):
        """Team size 3: 10% communication overhead"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=3)
        
        # Single: 20h
        # Ideal parallel: 20h / 3 = 6.67h
        # Overhead: 6.67h * 1.10 = 7.33h per person
        assert estimate.hours_team == pytest.approx(7.3, 0.2)
    
    def test_large_team_has_significant_overhead(self):
        """Team size 5: 20% communication overhead (Brooks's Law)"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=5)
        
        # Single: 20h
        # Ideal parallel: 20h / 5 = 4h
        # Overhead: 4h * 1.20 = 4.8h per person
        assert estimate.hours_team == pytest.approx(4.8, 0.2)


class TestSprintCalculation:
    """Test sprint allocation"""
    
    def test_default_velocity_single_developer(self):
        """Single developer: 20 points per sprint"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=1)  # 5 points
        
        # 5 points / 20 points per sprint = 0.25 sprints
        # But minimum enforced is 0.5 sprints
        assert estimate.sprints == 0.5
    
    def test_default_velocity_scales_with_team_size(self):
        """Team size 3: 60 points per sprint (3 * 20)"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=3)  # 5 points
        
        # 5 points / 60 points per sprint = 0.08 sprints (minimum 0.5)
        assert estimate.sprints == 0.5  # Minimum enforced
    
    def test_custom_velocity_overrides_default(self):
        """Custom velocity: use provided value"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(
            complexity=42,  # 5 points
            team_size=2,
            velocity=10.0  # 10 points per sprint
        )
        
        # 5 points / 10 points per sprint = 0.5 sprints
        assert estimate.sprints == 0.5
    
    def test_large_feature_multiple_sprints(self):
        """Large feature requires multiple sprints"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(
            complexity=85,  # 21 points
            team_size=2,
            velocity=15.0  # 15 points per sprint
        )
        
        # 21 points / 15 points per sprint = 1.4 sprints
        assert estimate.sprints == pytest.approx(1.4, 0.1)


class TestEffortBreakdown:
    """Test effort distribution by entity type"""
    
    def test_breakdown_without_scope_uses_defaults(self):
        """No scope: use default distribution"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)  # 20h
        
        assert 'implementation' in estimate.breakdown
        assert 'testing' in estimate.breakdown
        assert 'deployment' in estimate.breakdown
        
        # Total should equal hours_single
        total = sum(estimate.breakdown.values())
        assert total == pytest.approx(estimate.hours_single, 0.5)
    
    def test_breakdown_with_scope_uses_entity_distribution(self):
        """With scope: distribute by entity counts"""
        estimator = TimeframeEstimator()
        scope = {
            'tables': ['Users', 'AuthTokens'],
            'files': ['UserService.cs', 'AuthController.cs'],
            'services': ['AuthService'],
            'dependencies': ['Azure AD']
        }
        estimate = estimator.estimate_timeframe(complexity=42, scope=scope)
        
        assert 'tables' in estimate.breakdown
        assert 'files' in estimate.breakdown
        assert 'services' in estimate.breakdown
        assert 'dependencies' in estimate.breakdown
        assert 'testing' in estimate.breakdown
        
        # Total should approximately equal hours_single
        total = sum(estimate.breakdown.values())
        assert total == pytest.approx(estimate.hours_single, 1.0)


class TestConfidenceDetermination:
    """Test estimate confidence scoring"""
    
    def test_high_swagger_confidence_gives_high_estimate_confidence(self):
        """SWAGGER confidence 0.85 → HIGH"""
        estimator = TimeframeEstimator()
        scope = {'confidence': 0.85}
        estimate = estimator.estimate_timeframe(complexity=42, scope=scope)
        assert estimate.confidence == "HIGH"
    
    def test_medium_swagger_confidence_gives_medium_estimate_confidence(self):
        """SWAGGER confidence 0.65 → MEDIUM"""
        estimator = TimeframeEstimator()
        scope = {'confidence': 0.65}
        estimate = estimator.estimate_timeframe(complexity=42, scope=scope)
        assert estimate.confidence == "MEDIUM"
    
    def test_low_swagger_confidence_gives_low_estimate_confidence(self):
        """SWAGGER confidence 0.40 → LOW"""
        estimator = TimeframeEstimator()
        scope = {'confidence': 0.40}
        estimate = estimator.estimate_timeframe(complexity=42, scope=scope)
        assert estimate.confidence == "LOW"
    
    def test_high_complexity_reduces_confidence(self):
        """Complexity >80 downgrades confidence"""
        estimator = TimeframeEstimator()
        scope = {'confidence': 0.85}  # Would be HIGH
        estimate = estimator.estimate_timeframe(complexity=90, scope=scope)
        assert estimate.confidence == "MEDIUM"  # Downgraded
    
    def test_no_scope_defaults_to_medium_confidence(self):
        """No SWAGGER data → MEDIUM confidence"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)
        assert estimate.confidence == "MEDIUM"


class TestThreePointEstimation:
    """Test PERT three-point estimation"""
    
    def test_three_point_generates_best_likely_worst(self):
        """Returns dict with 3 estimates"""
        estimator = TimeframeEstimator()
        estimates = estimator.estimate_three_point(complexity=42)
        
        assert 'best' in estimates
        assert 'likely' in estimates
        assert 'worst' in estimates
        
        assert isinstance(estimates['best'], TimeEstimate)
        assert isinstance(estimates['likely'], TimeEstimate)
        assert isinstance(estimates['worst'], TimeEstimate)
    
    def test_best_case_is_75_percent_of_likely(self):
        """Best = complexity * 0.75"""
        estimator = TimeframeEstimator()
        estimates = estimator.estimate_three_point(complexity=42)  # 5 points
        
        # Best: 42 * 0.75 = 31.5 → 3 points
        assert estimates['best'].story_points == 3
        assert estimates['likely'].story_points == 5
    
    def test_worst_case_is_150_percent_of_likely(self):
        """Worst = complexity * 1.50"""
        estimator = TimeframeEstimator()
        estimates = estimator.estimate_three_point(complexity=42)  # 5 points
        
        # Worst: 42 * 1.50 = 63 → 8 points
        assert estimates['worst'].story_points == 8
        assert estimates['likely'].story_points == 5
    
    def test_worst_case_capped_at_100(self):
        """Worst case never exceeds complexity 100"""
        estimator = TimeframeEstimator()
        estimates = estimator.estimate_three_point(complexity=90)  # 21 points
        
        # Worst: 90 * 1.50 = 135 → capped at 100 → 34 points
        assert estimates['worst'].story_points == 34


class TestReportFormatting:
    """Test human-readable report generation"""
    
    def test_format_includes_story_points(self):
        """Report shows story points"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)
        report = estimator.format_estimate_report(estimate)
        
        assert "Story Points" in report
        assert "5" in report  # 42 complexity = 5 points
    
    def test_format_includes_confidence(self):
        """Report shows confidence level"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)
        report = estimator.format_estimate_report(estimate)
        
        assert "Confidence" in report
        assert estimate.confidence in report
    
    def test_format_includes_single_developer_section(self):
        """Report always shows single developer estimate"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)
        report = estimator.format_estimate_report(estimate)
        
        assert "Single Developer" in report
        assert "Hours:" in report
        assert "Days:" in report
    
    def test_format_includes_team_section_when_team_size_greater_than_1(self):
        """Report shows team section for multi-developer teams"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=3)
        report = estimator.format_estimate_report(estimate)
        
        assert "Team" in report
        assert "3 developers" in report
        assert "Sprints:" in report
    
    def test_format_includes_breakdown_when_requested(self):
        """Report includes effort breakdown if requested"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)
        report = estimator.format_estimate_report(estimate, include_breakdown=True)
        
        assert "Effort Breakdown" in report
    
    def test_format_excludes_breakdown_when_not_requested(self):
        """Report excludes breakdown if not requested"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)
        report = estimator.format_estimate_report(estimate, include_breakdown=False)
        
        assert "Effort Breakdown" not in report
    
    def test_format_includes_assumptions(self):
        """Report always includes assumptions"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42)
        report = estimator.format_estimate_report(estimate)
        
        assert "Assumptions" in report
        assert "hours per story point" in report


class TestQuickEstimate:
    """Test convenience function for quick estimates"""
    
    def test_quick_estimate_returns_one_line_summary(self):
        """Quick estimate returns concise string"""
        result = quick_estimate(complexity=42, team_size=1)
        
        assert "5 story points" in result
        assert "20.0h" in result
        assert "3.3 days" in result
        assert "MEDIUM confidence" in result
    
    def test_quick_estimate_includes_team_info_for_multi_developer(self):
        """Quick estimate shows team metrics when team_size > 1"""
        result = quick_estimate(complexity=42, team_size=2)
        
        assert "5 story points" in result
        assert "Team:" in result
        assert "calendar days" in result
        assert "sprints" in result


class TestEdgeCases:
    """Test edge cases and validation"""
    
    def test_complexity_below_zero_clamped_to_zero(self):
        """Negative complexity → 0"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=-10)
        assert estimate.story_points == 1  # 0 complexity = 1 point
    
    def test_complexity_above_100_clamped_to_100(self):
        """Complexity >100 → 100"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=150)
        assert estimate.story_points == 34  # 100 complexity = 34 points
    
    def test_team_size_below_1_clamped_to_1(self):
        """Team size <1 → 1"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, team_size=0)
        assert estimate.team_size == 1
    
    def test_zero_complexity_produces_minimum_estimate(self):
        """Complexity 0 → 1 point, 4h, 0.7 days"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=0)
        
        assert estimate.story_points == 1
        assert estimate.hours_single == 4.0
        assert estimate.days_single == pytest.approx(0.7, 0.1)
    
    def test_maximum_complexity_produces_epic_estimate(self):
        """Complexity 100 → 34 points, 136h, 22.7 days"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=100)
        
        assert estimate.story_points == 34
        assert estimate.hours_single == 136.0
        assert estimate.days_single == pytest.approx(22.7, 0.5)
    
    def test_empty_scope_dict_uses_default_breakdown(self):
        """Empty scope → default distribution"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=42, scope={})
        
        assert 'implementation' in estimate.breakdown
        assert 'testing' in estimate.breakdown


class TestIntegrationWithSWAGGER:
    """Test integration with SWAGGER complexity scores"""
    
    def test_swagger_medium_complexity_42_estimate(self):
        """SWAGGER complexity 42 (MEDIUM) → Complete estimate"""
        estimator = TimeframeEstimator()
        scope = {
            'tables': ['Users', 'AuthTokens'],
            'files': ['UserService.cs', 'AuthController.cs'],
            'services': ['AuthService'],
            'dependencies': ['Azure AD'],
            'confidence': 0.88
        }
        estimate = estimator.estimate_timeframe(complexity=42, scope=scope)
        
        # Validate complete estimate
        assert estimate.story_points == 5
        assert estimate.hours_single == 20.0
        assert estimate.days_single == pytest.approx(3.3, 0.1)
        assert estimate.confidence == "HIGH"
        assert 'tables' in estimate.breakdown
        assert 'files' in estimate.breakdown
    
    def test_swagger_high_complexity_85_estimate(self):
        """SWAGGER complexity 85 (HIGH) → Large estimate"""
        estimator = TimeframeEstimator()
        estimate = estimator.estimate_timeframe(complexity=85)
        
        assert estimate.story_points == 21
        assert estimate.hours_single == 84.0
        assert estimate.days_single == pytest.approx(14.0, 0.5)
    
    def test_end_to_end_planning_workflow_simulation(self):
        """Simulate complete planning workflow with TIMEFRAME"""
        estimator = TimeframeEstimator()
        
        # Step 1: SWAGGER provides complexity and scope
        swagger_complexity = 42
        swagger_scope = {
            'tables': ['Users', 'Sessions'],
            'files': ['auth.py', 'middleware.py'],
            'services': ['AuthService'],
            'dependencies': ['JWT'],
            'confidence': 0.82
        }
        
        # Step 2: User asks "what's the timeframe?"
        estimate = estimator.estimate_timeframe(
            complexity=swagger_complexity,
            scope=swagger_scope,
            team_size=2
        )
        
        # Step 3: CORTEX provides estimate
        assert estimate.story_points == 5
        assert estimate.hours_team < estimate.hours_single  # Team faster
        assert estimate.confidence == "HIGH"
        assert estimate.sprints > 0
        
        # Step 4: Generate report for user
        report = estimator.format_estimate_report(estimate)
        assert len(report) > 100  # Substantial report
        assert "TIMEFRAME Estimate" in report


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
