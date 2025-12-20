"""
Tests for Document Path Validator - Feature 3
TDD Phase: RED (All tests should FAIL initially)

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

# Import the implemented module
from src.orchestrators.document_path_validator import (
    DocumentPathValidator,
    ValidationResult,
    DocumentCategory,
    PatternMatcher
)


class TestForbiddenPatterns:
    """Test detection of forbidden document locations"""
    
    def test_detects_root_level_markdown_files(self):
        """Should reject files like CORTEX/summary.md"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("CORTEX/summary.md")
        
        assert result.valid is False
        assert "root-level" in result.reason.lower()
        assert result.suggested_path is not None
    
    def test_detects_review_folders_in_user_repos(self):
        """Should reject .review/ folders in user repositories"""
        validator = DocumentPathValidator()
        
        paths = [
            "user-repo/.review/summary.md",
            "/home/user/projects/app/.review/report.md",
            "C:\\Projects\\MyApp\\.review\\analysis.md"
        ]
        
        for path in paths:
            result = validator.validate_path(path)
            assert result.valid is False
            assert ".review" in result.reason.lower()
    
    def test_detects_windows_absolute_paths_with_review(self):
        """Should reject Windows absolute paths with .review"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("C:\\PROJECTS\\CORTEX\\.review\\summary.md")
        
        assert result.valid is False
        assert "review" in result.reason.lower()
    
    def test_detects_generic_summary_files_at_root(self):
        """Should reject summary.md at repository root"""
        validator = DocumentPathValidator()
        
        paths = [
            "summary.md",
            "project-summary.md",
            "SUMMARY.md"
        ]
        
        for path in paths:
            result = validator.validate_path(path)
            assert result.valid is False


class TestRequiredPatterns:
    """Test enforcement of cortex-brain/documents structure"""
    
    def test_accepts_valid_cortex_brain_documents_path(self):
        """Should accept cortex-brain/documents/{category}/file.md"""
        validator = DocumentPathValidator()
        
        valid_paths = [
            "cortex-brain/documents/reports/test-results.md",
            "cortex-brain/documents/analysis/code-review.md",
            "cortex-brain/documents/summaries/project-summary.md",
            "cortex-brain/documents/investigations/bug-123.md",
            "cortex-brain/documents/planning/feature-plan.md",
            "cortex-brain/documents/implementation-guides/setup-guide.md"
        ]
        
        for path in valid_paths:
            result = validator.validate_path(path)
            assert result.valid is True, f"Path should be valid: {path}"
    
    def test_rejects_cortex_brain_documents_without_category(self):
        """Should reject files directly in cortex-brain/documents/"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("cortex-brain/documents/summary.md")
        
        assert result.valid is False
        assert "category" in result.reason.lower()
    
    def test_rejects_invalid_category_names(self):
        """Should reject invalid categories"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("cortex-brain/documents/random-category/file.md")
        
        assert result.valid is False
        assert "category" in result.reason.lower()
    
    def test_requires_lowercase_hyphenated_filenames(self):
        """Should enforce lowercase-hyphenated-filenames.md"""
        validator = DocumentPathValidator()
        
        invalid_paths = [
            "cortex-brain/documents/reports/MyReport.md",
            "cortex-brain/documents/reports/my_report.md",
            "cortex-brain/documents/reports/my report.md"
        ]
        
        for path in invalid_paths:
            result = validator.validate_path(path)
            assert result.valid is False


class TestPathSuggestion:
    """Test path suggestion algorithm"""
    
    def test_suggests_reports_category_for_test_results(self):
        """Should suggest reports/ for test-related files"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("test-results.md")
        
        assert result.valid is False
        assert result.suggested_path is not None
        assert "cortex-brain/documents/reports/" in result.suggested_path
    
    def test_suggests_analysis_category_for_analysis_files(self):
        """Should suggest analysis/ for analysis-related files"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("code-analysis.md")
        
        assert result.valid is False
        assert "cortex-brain/documents/analysis/" in result.suggested_path
    
    def test_suggests_summaries_category_for_summary_files(self):
        """Should suggest summaries/ for summary files"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("summary.md")
        
        assert result.valid is False
        assert "cortex-brain/documents/summaries/" in result.suggested_path
    
    def test_converts_invalid_filename_to_lowercase_hyphenated(self):
        """Should convert filenames to lowercase-hyphenated format"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("My Test Results.md")
        
        assert result.suggested_path is not None
        assert "my-test-results.md" in result.suggested_path


class TestCategoryDetection:
    """Test document category detection"""
    
    def test_detects_reports_category_from_keywords(self):
        """Should detect reports category from filename"""
        validator = DocumentPathValidator()
        
        category = validator.detect_category("test-results-summary.md")
        
        assert category == DocumentCategory.REPORTS
    
    def test_detects_analysis_category_from_keywords(self):
        """Should detect analysis category from filename"""
        validator = DocumentPathValidator()
        
        category = validator.detect_category("code-analysis-results.md")
        
        assert category == DocumentCategory.ANALYSIS
    
    def test_detects_planning_category_from_keywords(self):
        """Should detect planning category from filename"""
        validator = DocumentPathValidator()
        
        category = validator.detect_category("feature-enhancement-plan.md")
        
        assert category == DocumentCategory.PLANNING
    
    def test_defaults_to_summaries_for_ambiguous_files(self):
        """Should default to summaries for ambiguous filenames"""
        validator = DocumentPathValidator()
        
        category = validator.detect_category("unknown-document.md")
        
        assert category == DocumentCategory.SUMMARIES


class TestCrossPlatformPaths:
    """Test cross-platform path handling"""
    
    def test_handles_windows_paths_with_backslashes(self):
        """Should normalize Windows paths"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("C:\\Projects\\CORTEX\\summary.md")
        
        assert result.valid is False
        # Suggestion should use forward slashes
        assert "\\" not in result.suggested_path
    
    def test_handles_unix_absolute_paths(self):
        """Should handle Unix absolute paths"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("/Users/asifhussain/PROJECTS/CORTEX/summary.md")
        
        assert result.valid is False
        assert result.suggested_path is not None
    
    def test_normalizes_path_separators_in_suggestions(self):
        """Suggestions should always use forward slashes"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("test\\report.md")
        
        assert result.suggested_path is not None
        assert "/" in result.suggested_path
        assert "\\" not in result.suggested_path


class TestValidationPerformance:
    """Test validation performance requirements"""
    
    def test_validation_completes_under_10ms(self):
        """Should validate in <10ms per requirement"""
        import time
        
        validator = DocumentPathValidator()
        
        start = time.perf_counter()
        for _ in range(100):
            validator.validate_path("cortex-brain/documents/reports/test.md")
        duration = time.perf_counter() - start
        
        avg_time_ms = (duration / 100) * 1000
        assert avg_time_ms < 10, f"Average validation time: {avg_time_ms:.2f}ms (required: <10ms)"


class TestIntegrationHooks:
    """Test integration with orchestrators"""
    
    def test_provides_validation_hook_for_file_creation(self):
        """Should provide hook callable by orchestrators"""
        validator = DocumentPathValidator()
        
        # Simulate orchestrator calling validation before file creation
        path_to_create = "summary.md"
        result = validator.validate_before_creation(path_to_create)
        
        assert result.valid is False
        assert result.should_block_creation is True
    
    def test_returns_category_suggestions_for_orchestrators(self):
        """Should help orchestrators select category"""
        validator = DocumentPathValidator()
        
        suggestions = validator.get_category_suggestions("test results")
        
        assert DocumentCategory.REPORTS in suggestions
        assert len(suggestions) > 0


class TestUserFriendlyMessages:
    """Test error message quality"""
    
    def test_provides_clear_error_message_for_root_files(self):
        """Error messages should be actionable"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("summary.md")
        
        assert result.valid is False
        assert "cortex-brain/documents" in result.reason
        assert result.suggested_path is not None
        # Should include category in message
        assert any(cat in result.reason.lower() for cat in ["reports", "analysis", "summaries"])
    
    def test_includes_available_categories_in_error(self):
        """Should list valid categories in error"""
        validator = DocumentPathValidator()
        
        result = validator.validate_path("cortex-brain/documents/invalid/file.md")
        
        assert result.valid is False
        assert "reports" in result.reason.lower()
        assert "analysis" in result.reason.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
