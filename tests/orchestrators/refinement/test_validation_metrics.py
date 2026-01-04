"""
Tests for Phase 7: Validation & Metrics.

Author: Asif Hussain
Created: January 3, 2026
"""

import pytest
from src.orchestrators.refinement.phases.validation_metrics import ValidationMetricsPhase


class MockOrchestrator:
    """Mock orchestrator for testing."""
    def __init__(self):
        self.state = {
            "results": {
                "QualityAssessment": {
                    "quality_score": 65,
                    "issues": ["issue1", "issue2", "issue3"]
                },
                "DuplicateDetection": {
                    "duplicates_found": 5
                },
                "PerformanceAnalysis": {
                    "performance_score": 70
                },
                "SecurityAudit": {
                    "security_score": 60,
                    "high_severity": 3
                },
                "ApplyRefactorings": {
                    "applied_count": 0
                },
                "RefactoringPlan": {
                    "refactoring_tasks": [
                        {"type": "quality", "priority": "high"},
                        {"type": "security", "priority": "high"},
                        {"type": "security", "priority": "high"}
                    ]
                }
            }
        }


class TestValidationMetricsPhase:
    """Test validation metrics phase."""
    
    @pytest.fixture
    def phase(self):
        """Create validation metrics phase."""
        orchestrator = MockOrchestrator()
        return ValidationMetricsPhase(orchestrator)
    
    def test_execute(self, phase):
        """Test phase execution."""
        results = phase.execute()
        
        assert "before" in results
        assert "after" in results
        assert "improvements" in results
        assert "validation_status" in results
    
    def test_before_metrics(self, phase):
        """Test before metrics capture."""
        results = phase.execute()
        before = results["before"]
        
        assert "quality_score" in before
        assert "issues_count" in before
        assert "duplicates_found" in before
        assert "performance_score" in before
        assert "security_score" in before
        
        # Check values match orchestrator state
        assert before["quality_score"] == 65
        assert before["issues_count"] == 3
        assert before["duplicates_found"] == 5
    
    def test_after_metrics_projected(self, phase):
        """Test projected after metrics."""
        results = phase.execute()
        after = results["after"]
        
        # Should have projected improvements
        assert after["quality_score"] >= results["before"]["quality_score"]
        assert results["validation_status"] == "projected"
    
    def test_improvements_calculation(self, phase):
        """Test improvements calculation."""
        results = phase.execute()
        improvements = results["improvements"]
        
        assert "quality_score_delta" in improvements
        assert "issues_fixed" in improvements
        assert "duplicates_removed" in improvements
        assert "performance_improvement" in improvements
        assert "security_improvement" in improvements
        assert "overall_improvement_percentage" in improvements
    
    def test_overall_improvement_percentage(self, phase):
        """Test overall improvement calculation."""
        results = phase.execute()
        improvements = results["improvements"]
        
        overall = improvements["overall_improvement_percentage"]
        assert isinstance(overall, (int, float))
        # Should show improvement
        assert overall >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
