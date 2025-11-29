"""
Test Recommendation Generation

Tests for SystemRefactorPlugin's recommendation generation based on health, gaps, and tasks.
This is Phase 4 of the 5-phase workflow.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestRecommendationGeneration:
    """Test generating recommendations from review data."""
    
    @pytest.mark.unit
    def test_generate_recommendations_returns_list(self, refactor_plugin, sample_review_report_excellent):
        """Test _generate_recommendations returns list."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_excellent)
        
        assert recommendations is not None
        assert isinstance(recommendations, list)
    
    @pytest.mark.unit
    def test_generate_recommendations_for_excellent_health(self, refactor_plugin, sample_review_report_excellent):
        """Test recommendations for EXCELLENT health status."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_excellent)
        
        # EXCELLENT health should have maintenance recommendations
        if recommendations:
            rec_text = " ".join(recommendations).lower()
            assert "maintain" in rec_text or "continue" in rec_text or "monitor" in rec_text
    
    @pytest.mark.unit
    def test_generate_recommendations_for_critical_health(self, refactor_plugin, sample_review_report_critical):
        """Test recommendations for CRITICAL health status."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_critical)
        
        # CRITICAL health should have urgent action recommendations
        assert len(recommendations) > 0
        rec_text = " ".join(recommendations).lower()
        assert any(keyword in rec_text for keyword in ["urgent", "immediate", "critical", "fix", "improve"])
    
    @pytest.mark.unit
    def test_recommendations_include_test_count(self, refactor_plugin, sample_review_report_critical):
        """Test recommendations mention test count when low."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_critical)
        
        if recommendations:
            rec_text = " ".join(recommendations)
            # Should mention test count or coverage
            assert "test" in rec_text.lower()


class TestRecommendationsForGaps:
    """Test recommendations based on coverage gaps."""
    
    @pytest.mark.unit
    def test_generate_recommendations_for_gaps(self, refactor_plugin, sample_review_report_with_gaps):
        """Test recommendations include gap remediation."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_gaps)
        
        # Should have recommendations for gaps
        assert len(recommendations) > 0
    
    @pytest.mark.unit
    def test_recommendations_prioritize_high_priority_gaps(self, refactor_plugin, sample_review_report_with_gaps):
        """Test HIGH priority gaps appear in recommendations."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_gaps)
        
        if recommendations:
            rec_text = " ".join(recommendations).lower()
            # Should mention plugins or entry points (HIGH priority gaps)
            assert "plugin" in rec_text or "entry point" in rec_text or "high priority" in rec_text
    
    @pytest.mark.unit
    def test_recommendations_mention_gap_categories(self, refactor_plugin, sample_review_report_with_gaps):
        """Test recommendations mention specific gap categories."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_gaps)
        
        rec_text = " ".join(recommendations).lower()
        # Should mention gap types
        gap_keywords = ["plugin", "entry point", "refactor", "module", "performance", "coverage"]
        assert any(keyword in rec_text for keyword in gap_keywords)


class TestRecommendationsForRefactorTasks:
    """Test recommendations based on REFACTOR tasks."""
    
    @pytest.mark.unit
    def test_generate_recommendations_for_tasks(self, refactor_plugin, sample_review_report_with_tasks):
        """Test recommendations include REFACTOR task guidance."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_tasks)
        
        # Should have recommendations for tasks
        assert len(recommendations) > 0
    
    @pytest.mark.unit
    def test_recommendations_mention_refactor_backlog(self, refactor_plugin, sample_review_report_with_tasks):
        """Test recommendations mention REFACTOR backlog."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_tasks)
        
        rec_text = " ".join(recommendations).lower()
        # Should mention refactoring or TODO comments
        assert "refactor" in rec_text or "todo" in rec_text or "backlog" in rec_text
    
    @pytest.mark.unit
    def test_recommendations_include_task_count(self, refactor_plugin, sample_review_report_with_tasks):
        """Test recommendations include task count."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_tasks)
        
        if recommendations:
            # Should mention number of tasks
            rec_text = " ".join(recommendations)
            assert any(char.isdigit() for char in rec_text) or "task" in rec_text.lower()


class TestRecommendationPrioritization:
    """Test recommendation prioritization logic."""
    
    @pytest.mark.unit
    def test_critical_health_recommendations_come_first(self, refactor_plugin):
        """Test CRITICAL health recommendations are prioritized."""
        # Create report with critical health
        from plugins.system_refactor_plugin import ReviewReport
        
        critical_report = ReviewReport(
            overall_health="CRITICAL",
            test_metrics={'total_tests': 50, 'passed': 30, 'failed': 20, 'pass_rate': 60.0},
            test_categories={},
            coverage_gaps=[],
            refactor_tasks=[],
            recommendations=[]
        )
        
        recommendations = refactor_plugin._generate_recommendations(critical_report)
        
        # First recommendation should address critical health
        if recommendations:
            first_rec = recommendations[0].lower()
            assert any(keyword in first_rec for keyword in ["urgent", "immediate", "critical", "priority"])
    
    @pytest.mark.unit
    def test_recommendations_grouped_by_category(self, refactor_plugin, sample_review_report_with_gaps):
        """Test recommendations are logically grouped."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_gaps)
        
        # Recommendations should be organized (health, gaps, tasks)
        assert len(recommendations) > 0
        
        # Each recommendation should be distinct
        assert len(set(recommendations)) == len(recommendations)


class TestRecommendationContent:
    """Test recommendation content quality."""
    
    @pytest.mark.unit
    def test_recommendations_are_actionable(self, refactor_plugin, sample_review_report_critical):
        """Test recommendations contain actionable guidance."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_critical)
        
        # Each recommendation should be specific
        for rec in recommendations:
            assert len(rec) > 20  # Not trivial
            # Should contain action verbs
            action_verbs = ["add", "fix", "improve", "create", "update", "address", "resolve", "implement"]
            assert any(verb in rec.lower() for verb in action_verbs)
    
    @pytest.mark.unit
    def test_recommendations_include_specifics(self, refactor_plugin, sample_review_report_with_gaps):
        """Test recommendations include specific details."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_gaps)
        
        # Should include numbers, names, or specifics
        rec_text = " ".join(recommendations)
        assert any(char.isdigit() for char in rec_text) or any(word[0].isupper() for word in rec_text.split())
    
    @pytest.mark.unit
    def test_recommendations_avoid_generic_advice(self, refactor_plugin, sample_review_report_critical):
        """Test recommendations are not generic platitudes."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_critical)
        
        # Should NOT be generic like "Write better tests"
        generic_phrases = ["be better", "work harder", "do more", "try again"]
        rec_text = " ".join(recommendations).lower()
        
        for phrase in generic_phrases:
            assert phrase not in rec_text


class TestRecommendationEdgeCases:
    """Test recommendation generation edge cases."""
    
    @pytest.mark.unit
    def test_recommendations_for_empty_report(self, refactor_plugin):
        """Test recommendations handle empty report gracefully."""
        from plugins.system_refactor_plugin import ReviewReport
        
        empty_report = ReviewReport(
            overall_health="EXCELLENT",
            test_metrics={'total_tests': 0, 'passed': 0, 'failed': 0, 'pass_rate': 0.0},
            test_categories={},
            coverage_gaps=[],
            refactor_tasks=[],
            recommendations=[]
        )
        
        recommendations = refactor_plugin._generate_recommendations(empty_report)
        
        # Should still provide guidance
        assert recommendations is not None
        assert isinstance(recommendations, list)
    
    @pytest.mark.unit
    def test_recommendations_limit_count(self, refactor_plugin, sample_review_report_with_gaps):
        """Test recommendations don't overwhelm with too many items."""
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_with_gaps)
        
        # Should be reasonable number (not 50+ recommendations)
        assert len(recommendations) <= 20
    
    @pytest.mark.unit
    def test_recommendations_for_mixed_signals(self, refactor_plugin):
        """Test recommendations handle mixed health/gaps/tasks."""
        from plugins.system_refactor_plugin import ReviewReport, CoverageGap
        
        mixed_report = ReviewReport(
            overall_health="GOOD",
            test_metrics={'total_tests': 300, 'passed': 285, 'failed': 15, 'pass_rate': 95.0},
            test_categories={},
            coverage_gaps=[
                CoverageGap("plugin", "test_plugin", "HIGH", "Missing tests")
            ],
            refactor_tasks=[],
            recommendations=[]
        )
        
        recommendations = refactor_plugin._generate_recommendations(mixed_report)
        
        # Should address both good health AND gaps
        rec_text = " ".join(recommendations).lower()
        assert "maintain" in rec_text or "continue" in rec_text
        assert "gap" in rec_text or "plugin" in rec_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
