"""
Integration tests for Refinement Orchestrator.

Tests the complete 7-phase refinement workflow.

Author: Asif Hussain
Created: January 3, 2026
"""

import pytest
import tempfile
from pathlib import Path

from src.orchestrators.refinement import RefinementOrchestrator


class TestRefinementOrchestrator:
    """Test refinement orchestrator integration."""
    
    @pytest.fixture
    def sample_file(self, tmp_path):
        """Create a sample Python file with quality issues."""
        test_file = tmp_path / "sample.py"
        test_file.write_text("""
def bad_function(a,b,c,d,e,f):
    # Too many parameters
    result = ""
    for i in range(100):
        result = result + str(i)  # Inefficient string concat
    return result

def duplicate_logic():
    x = 1
    y = 2
    z = x + y
    return z

def duplicate_logic2():
    x = 1
    y = 2
    z = x + y
    return z
""")
        return test_file
    
    @pytest.fixture
    def orchestrator(self, sample_file, tmp_path):
        """Create orchestrator instance."""
        output_dir = tmp_path / "output"
        return RefinementOrchestrator(sample_file, output_dir)
    
    def test_orchestrator_initialization(self, orchestrator, sample_file):
        """Test orchestrator initializes correctly."""
        assert orchestrator.target_path == sample_file
        assert orchestrator.output_dir.exists()
        assert len(orchestrator.phases) == 7
        assert orchestrator.session_id is not None
    
    def test_execute_all_phases(self, orchestrator):
        """Test executing all 7 phases."""
        results = orchestrator.execute(auto_apply=False)
        
        assert results["status"] == "completed"
        assert len(results["phases_completed"]) == 7
        assert "report_path" in results
        
        # Verify phase results exist
        assert "QualityAssessment" in results["results"]
        assert "DuplicateDetection" in results["results"]
        assert "PerformanceAnalysis" in results["results"]
        assert "SecurityAudit" in results["results"]
        assert "RefactoringPlan" in results["results"]
        assert "ApplyRefactorings" in results["results"]
        assert "ValidationMetrics" in results["results"]
    
    def test_execute_specific_phases(self, orchestrator):
        """Test executing specific phases."""
        results = orchestrator.execute(phases=[1, 2, 3])
        
        assert results["status"] == "completed"
        assert len(results["phases_completed"]) == 3
        assert "QualityAssessment" in results["results"]
        assert "DuplicateDetection" in results["results"]
        assert "PerformanceAnalysis" in results["results"]
    
    def test_get_summary(self, orchestrator):
        """Test getting refinement summary."""
        orchestrator.execute(auto_apply=False)
        summary = orchestrator.get_summary()
        
        assert "session_id" in summary
        assert summary["phases_completed"] == 7
        assert summary["status"] == "completed"
        assert "improvements" in summary
    
    def test_phase_1_quality_assessment(self, orchestrator):
        """Test Phase 1: Quality Assessment."""
        orchestrator.execute(phases=[1])
        results = orchestrator.state["results"]["QualityAssessment"]
        
        assert "quality_score" in results
        assert "issues" in results
        assert "metrics" in results
        assert results["files_analyzed"] == 1
        
        # Should find quality issues
        assert len(results["issues"]) > 0
    
    def test_phase_2_duplicate_detection(self, orchestrator):
        """Test Phase 2: Duplicate Detection."""
        orchestrator.execute(phases=[2])
        results = orchestrator.state["results"]["DuplicateDetection"]
        
        assert "duplicates_found" in results
        assert "duplicate_groups" in results
        assert "consolidation_suggestions" in results
        
        # Should find duplicates in sample file
        assert results["duplicates_found"] > 0
    
    def test_phase_5_refactoring_plan(self, orchestrator):
        """Test Phase 5: Refactoring Plan."""
        # Run phases 1-4 first
        orchestrator.execute(phases=[1, 2, 3, 4])
        
        # Then run phase 5
        orchestrator.execute(phases=[5])
        results = orchestrator.state["results"]["RefactoringPlan"]
        
        assert "refactoring_tasks" in results
        assert "priority_high" in results
        assert "estimated_effort_hours" in results
        
        # Should generate tasks from previous phases
        assert len(results["refactoring_tasks"]) > 0
    
    def test_phase_7_validation_metrics(self, orchestrator):
        """Test Phase 7: Validation & Metrics."""
        # Run all phases
        orchestrator.execute(auto_apply=False)
        results = orchestrator.state["results"]["ValidationMetrics"]
        
        assert "before" in results
        assert "after" in results
        assert "improvements" in results
        assert "validation_status" in results
        
        # Validation should be complete
        assert results["validation_status"] in ["validated", "projected"]
    
    def test_error_handling(self, tmp_path):
        """Test error handling with invalid target."""
        invalid_path = tmp_path / "nonexistent.py"
        orchestrator = RefinementOrchestrator(invalid_path)
        
        # Orchestrator should complete gracefully even with no files
        results = orchestrator.execute()
        assert results["status"] == "completed"
        # Should analyze 0 files
        assert results["results"]["QualityAssessment"]["files_analyzed"] == 0
    
    def test_report_generation(self, orchestrator):
        """Test report generation."""
        orchestrator.execute(auto_apply=False)
        
        # Check reports exist
        assert orchestrator.state["report_path"] is not None
        report_path = Path(orchestrator.state["report_path"])
        assert report_path.exists()
        
        # Check for HTML and markdown reports
        session_id = orchestrator.session_id
        html_report = orchestrator.output_dir / f"refinement-report-{session_id}.html"
        md_report = orchestrator.output_dir / f"refinement-summary-{session_id}.md"
        
        assert html_report.exists()
        assert md_report.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
