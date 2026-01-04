"""
Tests for Phase 1: Quality Assessment.

Author: Asif Hussain
Created: January 3, 2026
"""

import pytest
from pathlib import Path
from src.orchestrators.refinement.phases.quality_assessment import QualityAssessmentPhase


class MockOrchestrator:
    """Mock orchestrator for testing."""
    def __init__(self, target_path):
        self.target_path = target_path


class TestQualityAssessmentPhase:
    """Test quality assessment phase."""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create sample file with quality issues."""
        test_file = tmp_path / "test.py"
        test_file.write_text("""
def long_function(a, b, c, d, e, f, g):
    # Function with too many parameters
    result = None
    if a:
        if b:
            if c:
                # Deeply nested
                result = a + b + c
    return result

class BadClass:
    pass
""")
        return test_file
    
    @pytest.fixture
    def phase(self, sample_file):
        """Create quality assessment phase."""
        orchestrator = MockOrchestrator(sample_file)
        return QualityAssessmentPhase(orchestrator)
    
    def test_execute(self, phase):
        """Test phase execution."""
        results = phase.execute()
        
        assert "quality_score" in results
        assert "issues" in results
        assert "metrics" in results
        assert "files_analyzed" in results
        assert results["files_analyzed"] == 1
    
    def test_detect_code_smells(self, phase):
        """Test code smell detection."""
        results = phase.execute()
        issues = results["issues"]
        
        # Should find issues with too many parameters
        param_issues = [i for i in issues if "parameters" in i.get("message", "").lower()]
        assert len(param_issues) > 0
    
    def test_complexity_calculation(self, phase):
        """Test complexity metrics."""
        results = phase.execute()
        metrics = results["metrics"]
        
        assert "cyclomatic_complexity" in metrics
        assert metrics["cyclomatic_complexity"] > 0
    
    def test_quality_score_calculation(self, phase):
        """Test quality score calculation."""
        results = phase.execute()
        
        assert 0 <= results["quality_score"] <= 100
        # File with issues should have score < 100
        assert results["quality_score"] < 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
