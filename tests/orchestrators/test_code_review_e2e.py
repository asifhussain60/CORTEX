"""End-to-End Tests for Code Review Feature."""

import pytest
from src.orchestrators.code_review_orchestrator import (
    CodeReviewOrchestrator, PRInfo, ReviewConfig, ReviewDepth, FocusArea
)


@pytest.fixture
def orchestrator(tmp_path):
    """Create orchestrator for testing."""
    return CodeReviewOrchestrator(str(tmp_path))


class TestEndToEndReview:
    """End-to-end tests for complete code review workflow."""
    
    def test_full_workflow(self, orchestrator):
        """Test complete workflow with real CORTEX files."""
        pr_info = PRInfo(
            pr_id="TEST001",
            changed_files=[
                "src/orchestrators/code_review_orchestrator.py",
                "src/orchestrators/analysis_engine.py"
            ]
        )
        config = ReviewConfig(depth=ReviewDepth.STANDARD, focus_areas=[FocusArea.ALL])
        
        result = orchestrator.execute_review(pr_info, config)
        
        assert result is not None
        assert result.pr_info.pr_id == "TEST001"
        assert len(result.context_files) >= 2
        assert 0 <= result.risk_score <= 100
        assert len(result.executive_summary) > 0
    
    def test_report_generation_complete(self, orchestrator):
        """Test Phase 4 enhancements in report."""
        pr_info = PRInfo(pr_id="TEST002", changed_files=["src/orchestrators/code_review_orchestrator.py"])
        config = ReviewConfig(depth=ReviewDepth.STANDARD, focus_areas=[FocusArea.SECURITY])
        
        result = orchestrator.execute_review(pr_info, config)
        report_md = orchestrator._format_report_markdown(result)
        
        assert "## 📋 Priority Matrix" in report_md
        assert "## 🎯 Risk Assessment" in report_md
        assert "## ⚠️ Developer Disclaimer" in report_md
        assert "False positives" in report_md
    
    def test_all_focus_areas_work(self, orchestrator):
        """Test all focus areas execute successfully."""
        pr_info = PRInfo(pr_id="TEST003", changed_files=["src/orchestrators/code_review_orchestrator.py"])
        
        for focus_area in [FocusArea.SECURITY, FocusArea.PERFORMANCE, FocusArea.ALL]:
            config = ReviewConfig(depth=ReviewDepth.QUICK, focus_areas=[focus_area])
            result = orchestrator.execute_review(pr_info, config)
            assert result is not None
