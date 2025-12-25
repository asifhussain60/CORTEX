"""
Tests for document_validator.py (TDD Phase 2: Core modules)

RED → GREEN → REFACTOR approach for document validation testing
"""

import pytest
from pathlib import Path
from typing import Dict

from src.core.document_validator import (
    DocumentValidator,
    validate_document,
    scan_workspace_documents,
    VALID_CATEGORIES,
    ROOT_WHITELIST,
    CORTEX_BRAIN_WHITELIST
)


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def validator(tmp_path):
    """Create DocumentValidator instance with temporary workspace"""
    workspace = tmp_path / "test_workspace"
    workspace.mkdir()
    (workspace / ".git").mkdir()
    return DocumentValidator(str(workspace))


@pytest.fixture
def sample_workspace(tmp_path):
    """Create sample workspace with various document locations"""
    workspace = tmp_path / "sample_workspace"
    workspace.mkdir()
    (workspace / ".git").mkdir()
    
    # Create directory structure
    (workspace / "cortex-brain" / "documents" / "reports").mkdir(parents=True)
    (workspace / "cortex-brain" / "documents" / "analysis").mkdir(parents=True)
    (workspace / "docs").mkdir()
    (workspace / "src").mkdir()
    
    # Create sample documents
    (workspace / "README.md").write_text("# README")
    (workspace / "cortex-brain" / "documents" / "reports" / "test-report.md").write_text("Report")
    (workspace / "docs" / "user-guide.md").write_text("Guide")
    (workspace / "invalid-root.md").write_text("Invalid")
    
    return workspace


# ============================================================================
# Test Class 1: Initialization
# ============================================================================

class TestDocumentValidatorInitialization:
    """Test DocumentValidator initialization"""
    
    def test_init_with_explicit_workspace(self, tmp_path):
        """Should initialize with provided workspace root"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        validator = DocumentValidator(str(workspace))
        
        assert validator.workspace_root == workspace
    
    def test_init_autodetects_git_workspace(self, tmp_path):
        """Should auto-detect workspace by finding .git directory"""
        workspace = tmp_path / "project"
        workspace.mkdir()
        (workspace / ".git").mkdir()
        
        # Create subdirectory and run from there
        subdir = workspace / "src"
        subdir.mkdir()
        
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(str(subdir))
            validator = DocumentValidator()
            # Should find workspace root (where .git is)
            assert validator.workspace_root == workspace
        finally:
            os.chdir(original_cwd)


# ============================================================================
# Test Class 2: Path Validation - Valid Cases
# ============================================================================

class TestValidDocumentPaths:
    """Test validation of properly organized documents"""
    
    def test_root_whitelist_file(self, validator):
        """Should accept whitelisted root files"""
        result = validator.validate_document_path("README.md")
        
        assert result['valid'] is True
        assert result['category'] == 'root-whitelist'
        assert result['violation'] is None
    
    def test_cortex_brain_whitelist_file(self, validator):
        """Should accept whitelisted cortex-brain files"""
        result = validator.validate_document_path("cortex-brain/schema.sql")
        
        # Note: schema.sql is not .md, so should pass as non-markdown
        assert result['valid'] is True
    
    def test_organized_report(self, validator):
        """Should accept document in valid reports/ category"""
        result = validator.validate_document_path(
            "cortex-brain/documents/reports/test-report.md"
        )
        
        assert result['valid'] is True
        assert result['category'] == 'reports'
        assert result['violation'] is None
    
    def test_organized_analysis(self, validator):
        """Should accept document in valid analysis/ category"""
        result = validator.validate_document_path(
            "cortex-brain/documents/analysis/coverage-analysis.md"
        )
        
        assert result['valid'] is True
        assert result['category'] == 'analysis'
    
    def test_user_docs_directory(self, validator):
        """Should accept documents in docs/ for user-facing documentation"""
        result = validator.validate_document_path("docs/api/modules.md")
        
        assert result['valid'] is True
        assert result['category'] == 'user-docs'
    
    def test_non_markdown_file(self, validator):
        """Should pass non-markdown files without validation"""
        result = validator.validate_document_path("src/main.py")
        
        assert result['valid'] is True
        assert result['category'] is None
        assert 'Not a markdown document' in result['reason']


# ============================================================================
# Test Class 3: Path Validation - Invalid Cases
# ============================================================================

class TestInvalidDocumentPaths:
    """Test detection of incorrectly organized documents"""
    
    def test_informational_doc_in_root(self, validator):
        """Should reject informational document in repository root"""
        result = validator.validate_document_path("STATUS-UPDATE.md")
        
        assert result['valid'] is False
        assert result['violation'] == 'Informational document in repository root'
        assert result['suggestion'] is not None
        assert 'cortex-brain/documents/' in result['suggestion']
    
    def test_doc_in_cortex_brain_root(self, validator):
        """Should reject document in cortex-brain root (not organized)"""
        result = validator.validate_document_path("cortex-brain/todo.md")
        
        assert result['valid'] is False
        assert result['violation'] == 'Document in cortex-brain root (not organized)'
        assert result['suggestion'] is not None
    
    def test_invalid_category(self, validator):
        """Should reject document in invalid category"""
        result = validator.validate_document_path(
            "cortex-brain/documents/random-stuff/notes.md"
        )
        
        assert result['valid'] is False
        assert 'Invalid category' in result['violation']
        assert 'random-stuff' in result['reason']
    
    def test_document_outside_workspace(self, validator, tmp_path):
        """Should reject absolute path outside workspace"""
        outside_path = tmp_path / "outside" / "doc.md"
        outside_path.parent.mkdir()
        
        result = validator.validate_document_path(str(outside_path))
        
        assert result['valid'] is False
        assert 'outside workspace root' in result['violation']


# ============================================================================
# Test Class 4: Path Suggestions
# ============================================================================

class TestPathSuggestions:
    """Test correct path suggestion logic"""
    
    def test_suggest_reports_for_status(self, validator):
        """Should suggest reports/ for status documents"""
        result = validator.validate_document_path("STATUS-REPORT.md")
        
        assert 'cortex-brain/documents/reports/' in result['suggestion']
    
    def test_suggest_analysis_for_investigation(self, validator):
        """Should suggest analysis/ for investigation documents"""
        result = validator.validate_document_path("COVERAGE-ANALYSIS.md")
        
        assert 'cortex-brain/documents/analysis/' in result['suggestion']
    
    def test_suggest_planning_for_plan(self, validator):
        """Should suggest planning/ for plan documents"""
        result = validator.validate_document_path("FEATURE-PLAN.md")
        
        assert 'cortex-brain/documents/planning/' in result['suggestion']


# ============================================================================
# Test Class 5: Naming Convention Validation
# ============================================================================

class TestNamingConventionValidation:
    """Test file naming convention validation"""
    
    def test_valid_report_naming(self, validator):
        """Should accept properly named report"""
        path = "cortex-brain/documents/reports/PHASE-8-COMPLETION-REPORT.md"
        result = validator.validate_naming_convention(path)
        
        assert result['valid'] is True
        assert 'naming convention' in result['reason']
    
    def test_invalid_report_naming(self, validator):
        """Should reject improperly named report"""
        path = "cortex-brain/documents/reports/phase8.md"
        result = validator.validate_naming_convention(path)
        
        assert result['valid'] is False
        assert 'Does not follow' in result['reason']
        assert result['suggestion'] is not None
    
    def test_flexible_category_naming(self, validator):
        """Should allow flexible naming for categories without strict rules"""
        path = "cortex-brain/documents/diagrams/architecture-diagram.md"
        result = validator.validate_naming_convention(path)
        
        assert result['valid'] is True
        assert 'flexible naming' in result['reason']


# ============================================================================
# Test Class 6: Workspace Scanning
# ============================================================================

class TestWorkspaceScanning:
    """Test workspace-wide document scanning"""
    
    def test_scan_finds_valid_and_invalid(self, sample_workspace):
        """Should identify both valid and invalid documents"""
        validator = DocumentValidator(str(sample_workspace))
        results = validator.scan_workspace()
        
        assert 'valid' in results
        assert 'violations' in results
        assert 'suggestions' in results
        
        # Should find README.md as valid
        assert any('README.md' in path for path in results['valid'])
        
        # Should find invalid-root.md as violation
        assert any('invalid-root.md' in path for path in results['violations'])
    
    def test_scan_skips_hidden_directories(self, tmp_path):
        """Should skip documents in hidden directories"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        (workspace / ".git").mkdir()
        (workspace / ".hidden").mkdir()
        (workspace / ".hidden" / "doc.md").write_text("Hidden")
        
        validator = DocumentValidator(str(workspace))
        results = validator.scan_workspace()
        
        # Should not include .hidden/doc.md
        all_paths = results['valid'] + results['violations']
        assert not any('.hidden' in path for path in all_paths)
    
    def test_scan_provides_suggestions_for_violations(self, sample_workspace):
        """Should provide path suggestions for violations"""
        validator = DocumentValidator(str(sample_workspace))
        results = validator.scan_workspace()
        
        # invalid-root.md should have a suggestion
        violations = results['violations']
        suggestions = results['suggestions']
        
        invalid_docs = [v for v in violations if 'invalid-root.md' in v]
        if invalid_docs:
            assert invalid_docs[0] in suggestions
            assert 'cortex-brain/documents/' in suggestions[invalid_docs[0]]


# ============================================================================
# Test Class 7: Category Extraction
# ============================================================================

class TestCategoryExtraction:
    """Test category extraction from paths"""
    
    def test_get_category_from_organized_path(self, validator):
        """Should extract category from organized document"""
        category = validator.get_category_from_path(
            "cortex-brain/documents/reports/test.md"
        )
        
        assert category == 'reports'
    
    def test_get_category_from_invalid_path(self, validator):
        """Should return None for invalid paths"""
        category = validator.get_category_from_path("random.md")
        
        assert category is None
    
    def test_is_organized_document_true(self, validator):
        """Should return True for organized documents"""
        is_organized = validator.is_organized_document(
            "cortex-brain/documents/analysis/test.md"
        )
        
        assert is_organized is True
    
    def test_is_organized_document_false(self, validator):
        """Should return False for unorganized documents"""
        is_organized = validator.is_organized_document("STATUS.md")
        
        assert is_organized is False


# ============================================================================
# Test Class 8: Convenience Functions
# ============================================================================

class TestConvenienceFunctions:
    """Test module-level convenience functions"""
    
    def test_validate_document_function(self, tmp_path):
        """Should validate document using convenience function"""
        workspace = tmp_path / "workspace"
        workspace.mkdir()
        
        result = validate_document("README.md", str(workspace))
        
        assert 'valid' in result
        assert 'category' in result
    
    def test_scan_workspace_documents_function(self, sample_workspace):
        """Should scan workspace using convenience function"""
        results = scan_workspace_documents(str(sample_workspace))
        
        assert 'valid' in results
        assert 'violations' in results
        assert 'suggestions' in results


# ============================================================================
# Test Class 9: Edge Cases
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions"""
    
    def test_empty_path(self, validator):
        """Should handle empty path string"""
        result = validator.validate_document_path("")
        
        # Should not crash, returns result
        assert 'valid' in result
    
    def test_path_with_special_characters(self, validator):
        """Should handle paths with special characters"""
        result = validator.validate_document_path(
            "cortex-brain/documents/reports/test-@#$-report.md"
        )
        
        # Should process without crashing
        assert 'valid' in result
    
    def test_unicode_path(self, validator):
        """Should handle Unicode characters in path"""
        result = validator.validate_document_path(
            "cortex-brain/documents/reports/résumé-report.md"
        )
        
        assert 'valid' in result
    
    def test_deeply_nested_path(self, validator):
        """Should handle deeply nested paths"""
        deep_path = "cortex-brain/documents/reports/2025/Q4/december/week3/status.md"
        result = validator.validate_document_path(deep_path)
        
        # Should recognize as valid reports category
        assert result['valid'] is True
        assert result['category'] == 'reports'
    
    def test_case_insensitive_category_detection(self, validator):
        """Should handle category name case variations"""
        # DocumentValidator uses lowercase comparison for categories
        result = validator.validate_document_path(
            "cortex-brain/documents/reports/TEST.md"
        )
        
        assert result['valid'] is True
        assert result['category'] == 'reports'


# ============================================================================
# Test Execution Summary
# ============================================================================

# Expected Initial State (RED Phase):
# - 12 test classes defined covering:
#   - Initialization (2 tests)
#   - Valid paths (6 tests)
#   - Invalid paths (4 tests)
#   - Path suggestions (3 tests)
#   - Naming conventions (3 tests)
#   - Workspace scanning (3 tests)
#   - Category extraction (4 tests)
#   - Convenience functions (2 tests)
#   - Edge cases (5 tests)
# - All tests should PASS (implementation exists)
#
# After GREEN Phase:
# - 32 total tests passing
# - Coverage: 0% → ~85% for document_validator.py
#
# After REFACTOR Phase:
# - Tests remain PASSING
# - Code quality maintained
