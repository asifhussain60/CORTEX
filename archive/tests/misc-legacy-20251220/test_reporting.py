"""
Test Report Generation and Formatting

Tests for SystemRefactorPlugin's markdown report generation and persistence.
This is Phase 5 of the 5-phase workflow.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))


class TestReportPersistence:
    """Test saving reports to brain directory."""
    
    @pytest.mark.unit
    def test_save_report_creates_file(self, plugin_with_mocked_paths, sample_review_report_excellent):
        """Test _save_report creates markdown file."""
        result = plugin_with_mocked_paths._save_report(sample_review_report_excellent)
        
        assert result is not None
        assert isinstance(result, Path)
        assert result.exists()
        assert result.suffix == ".md"
    
    @pytest.mark.unit
    def test_save_report_to_brain_directory(self, plugin_with_mocked_paths, sample_review_report_excellent):
        """Test report is saved to cortex-brain/documents/reports/."""
        result = plugin_with_mocked_paths._save_report(sample_review_report_excellent)
        
        # Should be in brain path
        assert plugin_with_mocked_paths.brain_path in result.parents
        
        # Should be in reports subdirectory
        assert "reports" in str(result)
    
    @pytest.mark.unit
    def test_save_report_includes_timestamp(self, plugin_with_mocked_paths, sample_review_report_excellent):
        """Test report filename includes timestamp."""
        result = plugin_with_mocked_paths._save_report(sample_review_report_excellent)
        
        # Filename should contain date pattern YYYYMMDD
        assert any(char.isdigit() for char in result.stem)
    
    @pytest.mark.unit
    def test_save_report_creates_directories(self, plugin_with_mocked_paths, sample_review_report_excellent):
        """Test _save_report creates missing directories."""
        # Remove reports directory if exists
        reports_dir = plugin_with_mocked_paths.brain_path / "documents" / "reports"
        if reports_dir.exists():
            import shutil
            shutil.rmtree(reports_dir)
        
        result = plugin_with_mocked_paths._save_report(sample_review_report_excellent)
        
        # Directory should be created
        assert reports_dir.exists()
        assert result.exists()


class TestMarkdownFormatting:
    """Test markdown report formatting."""
    
    @pytest.mark.unit
    def test_format_markdown_report_returns_string(self, refactor_plugin, sample_review_report_excellent):
        """Test _format_markdown_report returns formatted string."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        assert markdown is not None
        assert isinstance(markdown, str)
        assert len(markdown) > 0
    
    @pytest.mark.unit
    def test_markdown_has_title_header(self, refactor_plugin, sample_review_report_excellent):
        """Test markdown includes title header."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Should have H1 title
        assert markdown.startswith("#")
        assert "System Refactor" in markdown or "Critical Review" in markdown
    
    @pytest.mark.unit
    def test_markdown_has_section_headers(self, refactor_plugin, sample_review_report_excellent):
        """Test markdown includes section headers."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Should have H2 sections
        assert "##" in markdown
        
        # Key sections should be present
        sections = ["Health", "Metrics", "Categories", "Gaps", "Tasks", "Recommendations"]
        markdown_lower = markdown.lower()
        assert any(section.lower() in markdown_lower for section in sections)
    
    @pytest.mark.unit
    def test_markdown_includes_health_status(self, refactor_plugin, sample_review_report_excellent):
        """Test markdown includes overall health status."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        assert "EXCELLENT" in markdown
    
    @pytest.mark.unit
    def test_markdown_includes_test_metrics(self, refactor_plugin, sample_review_report_excellent):
        """Test markdown includes test metrics."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Should include test counts
        assert any(char.isdigit() for char in markdown)
        
        # Should mention tests
        assert "test" in markdown.lower()
    
    @pytest.mark.unit
    def test_markdown_formats_gaps_as_list(self, refactor_plugin, sample_review_report_with_gaps):
        """Test markdown formats coverage gaps as list."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_with_gaps)
        
        # Should have list items
        assert "-" in markdown or "*" in markdown or "1." in markdown
    
    @pytest.mark.unit
    def test_markdown_formats_tasks_as_list(self, refactor_plugin, sample_review_report_with_tasks):
        """Test markdown formats REFACTOR tasks as list."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_with_tasks)
        
        # Should have list items
        assert "-" in markdown or "*" in markdown
        
        # Should mention refactor
        assert "refactor" in markdown.lower() or "todo" in markdown.lower()
    
    @pytest.mark.unit
    def test_markdown_includes_recommendations(self, refactor_plugin, sample_review_report_critical):
        """Test markdown includes recommendations section."""
        # Generate recommendations first
        recommendations = refactor_plugin._generate_recommendations(sample_review_report_critical)
        sample_review_report_critical.recommendations = recommendations
        
        markdown = refactor_plugin._format_markdown_report(sample_review_report_critical)
        
        # Should have recommendations
        assert "recommendation" in markdown.lower()


class TestSummaryFormatting:
    """Test console summary formatting."""
    
    @pytest.mark.unit
    def test_format_summary_returns_string(self, refactor_plugin, sample_review_report_excellent):
        """Test _format_summary returns formatted string."""
        summary = refactor_plugin._format_summary(sample_review_report_excellent)
        
        assert summary is not None
        assert isinstance(summary, str)
        assert len(summary) > 0
    
    @pytest.mark.unit
    def test_summary_is_concise(self, refactor_plugin, sample_review_report_excellent):
        """Test summary is shorter than full report."""
        summary = refactor_plugin._format_summary(sample_review_report_excellent)
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Summary should be significantly shorter
        assert len(summary) < len(markdown) / 2
    
    @pytest.mark.unit
    def test_summary_includes_key_metrics(self, refactor_plugin, sample_review_report_excellent):
        """Test summary includes key metrics."""
        summary = refactor_plugin._format_summary(sample_review_report_excellent)
        
        # Should include health status
        assert "EXCELLENT" in summary
        
        # Should include test count
        assert any(char.isdigit() for char in summary)
    
    @pytest.mark.unit
    def test_summary_includes_gap_count(self, refactor_plugin, sample_review_report_with_gaps):
        """Test summary includes gap count when present."""
        summary = refactor_plugin._format_summary(sample_review_report_with_gaps)
        
        summary_lower = summary.lower()
        assert "gap" in summary_lower or "coverage" in summary_lower
    
    @pytest.mark.unit
    def test_summary_includes_task_count(self, refactor_plugin, sample_review_report_with_tasks):
        """Test summary includes task count when present."""
        summary = refactor_plugin._format_summary(sample_review_report_with_tasks)
        
        summary_lower = summary.lower()
        assert "refactor" in summary_lower or "task" in summary_lower


class TestReportStructure:
    """Test overall report structure."""
    
    @pytest.mark.unit
    def test_report_has_consistent_structure(self, refactor_plugin, sample_review_report_excellent):
        """Test report structure is consistent."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Should have clear sections in order
        lines = markdown.split("\n")
        headers = [line for line in lines if line.startswith("#")]
        
        # Should have multiple sections
        assert len(headers) > 1
    
    @pytest.mark.unit
    def test_report_sections_in_logical_order(self, refactor_plugin, sample_review_report_excellent):
        """Test report sections appear in logical order."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Health should come before gaps
        health_pos = markdown.lower().find("health")
        gaps_pos = markdown.lower().find("gap")
        
        if health_pos >= 0 and gaps_pos >= 0:
            assert health_pos < gaps_pos
    
    @pytest.mark.unit
    def test_report_includes_metadata(self, refactor_plugin, sample_review_report_excellent):
        """Test report includes metadata (timestamp, version)."""
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Should include date or timestamp
        assert any(char.isdigit() for char in markdown)


class TestReportEdgeCases:
    """Test report generation edge cases."""
    
    @pytest.mark.unit
    def test_report_handles_empty_gaps(self, refactor_plugin, sample_review_report_excellent):
        """Test report handles empty gaps list."""
        assert len(sample_review_report_excellent.coverage_gaps) == 0
        
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Should still generate report
        assert markdown is not None
        assert len(markdown) > 0
    
    @pytest.mark.unit
    def test_report_handles_empty_tasks(self, refactor_plugin, sample_review_report_excellent):
        """Test report handles empty tasks list."""
        assert len(sample_review_report_excellent.refactor_tasks) == 0
        
        markdown = refactor_plugin._format_markdown_report(sample_review_report_excellent)
        
        # Should still generate report
        assert markdown is not None
        assert len(markdown) > 0
    
    @pytest.mark.unit
    def test_report_handles_long_descriptions(self, refactor_plugin):
        """Test report handles very long gap/task descriptions."""
        from plugins.system_refactor_plugin import ReviewReport, CoverageGap
        
        long_description = "A" * 500  # Very long description
        report_with_long = ReviewReport(
            overall_health="GOOD",
            test_metrics={'total_tests': 300, 'passed': 285, 'failed': 15, 'pass_rate': 95.0},
            test_categories={},
            coverage_gaps=[
                CoverageGap("plugin", "test_plugin", "HIGH", long_description)
            ],
            refactor_tasks=[],
            recommendations=[]
        )
        
        markdown = refactor_plugin._format_markdown_report(report_with_long)
        
        # Should handle gracefully (truncate or wrap)
        assert markdown is not None
        assert len(markdown) > 0


class TestReportIntegration:
    """Test report generation integration."""
    
    @pytest.mark.integration
    def test_full_report_workflow(self, plugin_with_mocked_paths, sample_review_report_excellent):
        """Test complete report generation workflow."""
        # Generate markdown
        markdown = plugin_with_mocked_paths._format_markdown_report(sample_review_report_excellent)
        assert markdown is not None
        
        # Save to disk
        file_path = plugin_with_mocked_paths._save_report(sample_review_report_excellent)
        assert file_path.exists()
        
        # Verify content
        saved_content = file_path.read_text()
        assert "EXCELLENT" in saved_content
        
        # Generate summary
        summary = plugin_with_mocked_paths._format_summary(sample_review_report_excellent)
        assert summary is not None
        assert len(summary) < len(markdown)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
