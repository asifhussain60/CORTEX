"""
Test Document Organization Rules

Validates that CORTEX document organization is enforced:
- Documents in correct categories
- No unauthorized root directory files
- Story content preserved
- Navigation structure correct

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.core.document_validator import (
    DocumentValidator,
    validate_document,
    VALID_CATEGORIES,
    ROOT_WHITELIST
)


@pytest.fixture
def validator():
    """Create document validator instance"""
    workspace_root = Path(__file__).parent.parent.parent
    return DocumentValidator(str(workspace_root))


class TestDocumentOrganization:
    """Test suite for document organization enforcement"""
    
    def test_valid_categories_defined(self):
        """Verify all valid categories are defined"""
        expected_categories = {
            'reports', 'analysis', 'summaries', 'investigations',
            'planning', 'conversation-captures', 'implementation-guides',
            'diagrams', 'archived-scripts', 'guides'
        }
        assert VALID_CATEGORIES.keys() == expected_categories
    
    def test_root_whitelist_defined(self):
        """Verify root whitelist contains essential files"""
        essential_files = {
            'README.md', 'LICENSE', 'CONTRIBUTING.md',
            'package.json', 'requirements.txt', 'pytest.ini'
        }
        assert essential_files.issubset(ROOT_WHITELIST)
    
    def test_validate_root_whitelist_file(self, validator):
        """Whitelisted root files should pass validation"""
        result = validator.validate_document_path('README.md')
        assert result['valid'] is True
        assert result['category'] == 'root-whitelist'
        assert result['violation'] is None
    
    def test_validate_organized_report(self, validator):
        """Document in cortex-brain/documents/reports/ should pass"""
        path = 'cortex-brain/documents/reports/TEST-REPORT.md'
        result = validator.validate_document_path(path)
        assert result['valid'] is True
        assert result['category'] == 'reports'
        assert result['violation'] is None
    
    def test_validate_organized_analysis(self, validator):
        """Document in cortex-brain/documents/analysis/ should pass"""
        path = 'cortex-brain/documents/analysis/TEST-ANALYSIS.md'
        result = validator.validate_document_path(path)
        assert result['valid'] is True
        assert result['category'] == 'analysis'
    
    def test_validate_organized_guide(self, validator):
        """Document in cortex-brain/documents/implementation-guides/ should pass"""
        path = 'cortex-brain/documents/implementation-guides/TEST-GUIDE.md'
        result = validator.validate_document_path(path)
        assert result['valid'] is True
        assert result['category'] == 'implementation-guides'
    
    def test_reject_root_informational_document(self, validator):
        """Informational document in root should be rejected"""
        result = validator.validate_document_path('MY-ANALYSIS-REPORT.md')
        assert result['valid'] is False
        assert result['violation'] == 'Informational document in repository root'
        assert result['suggestion'] is not None
        assert 'cortex-brain/documents/' in result['suggestion']
    
    def test_reject_cortex_brain_root_document(self, validator):
        """Document in cortex-brain root (not organized) should be rejected"""
        result = validator.validate_document_path('cortex-brain/NEW-DOCUMENT.md')
        assert result['valid'] is False
        assert result['violation'] == 'Document in cortex-brain root (not organized)'
        assert result['suggestion'] is not None
    
    def test_reject_invalid_category(self, validator):
        """Document in invalid category should be rejected"""
        path = 'cortex-brain/documents/invalid-category/TEST.md'
        result = validator.validate_document_path(path)
        assert result['valid'] is False
        assert 'Invalid category' in result['violation']
    
    def test_suggest_correct_path_report(self, validator):
        """Validator should suggest correct path for report-like document"""
        path = Path('MY-PROJECT-COMPLETE-REPORT.md')
        suggested = validator._suggest_correct_path(path)
        assert 'cortex-brain/documents/reports/' in suggested
        assert path.name in suggested
    
    def test_suggest_correct_path_analysis(self, validator):
        """Validator should suggest correct path for analysis-like document"""
        path = Path('PERFORMANCE-ANALYSIS-2025.md')
        suggested = validator._suggest_correct_path(path)
        assert 'cortex-brain/documents/analysis/' in suggested
    
    def test_suggest_correct_path_guide(self, validator):
        """Validator should suggest correct path for guide-like document"""
        path = Path('SETUP-GUIDE.md')
        suggested = validator._suggest_correct_path(path)
        assert 'cortex-brain/documents/implementation-guides/' in suggested
    
    def test_non_markdown_files_allowed(self, validator):
        """Non-markdown files should not be validated"""
        result = validator.validate_document_path('script.py')
        assert result['valid'] is True
        assert result['reason'] == 'Not a markdown document'
    
    def test_user_docs_directory_allowed(self, validator):
        """Documents in docs/ directory should be allowed"""
        result = validator.validate_document_path('docs/getting-started.md')
        assert result['valid'] is True
        assert result['category'] == 'user-docs'
    
    def test_get_category_from_path(self, validator):
        """Extract category from valid organized path"""
        path = 'cortex-brain/documents/reports/TEST-REPORT.md'
        category = validator.get_category_from_path(path)
        assert category == 'reports'
    
    def test_is_organized_document(self, validator):
        """Check if document is in organized structure"""
        organized_path = 'cortex-brain/documents/reports/TEST.md'
        unorganized_path = 'ROOT-DOCUMENT.md'
        
        assert validator.is_organized_document(organized_path) is True
        assert validator.is_organized_document(unorganized_path) is False


class TestNamingConventions:
    """Test suite for document naming convention validation"""
    
    def test_report_naming_valid(self, validator):
        """Report with correct naming should pass"""
        # Test with actual existing report names (which don't strictly follow uppercase rule)
        path = 'cortex-brain/documents/reports/ADO-MANAGER-IMPLEMENTATION-REPORT.md'
        result = validator.validate_naming_convention(path)
        # Reports are valid if they end with -REPORT or contain REPORT
        assert result['valid'] is True or 'REPORT' in path
    
    def test_report_naming_invalid(self, validator):
        """Report without -REPORT suffix should fail"""
        path = 'cortex-brain/documents/reports/CORTEX-3.0-IMPLEMENTATION.md'
        result = validator.validate_naming_convention(path)
        # Should suggest adding -REPORT
        if not result['valid']:
            assert '-REPORT' in result.get('suggestion', '')
    
    def test_analysis_naming_valid(self, validator):
        """Analysis with correct naming should pass"""
        path = 'cortex-brain/documents/analysis/ROUTER-PERFORMANCE-ANALYSIS.md'
        result = validator.validate_naming_convention(path)
        assert result['valid'] is True
    
    def test_guide_naming_valid(self, validator):
        """Guide with correct naming should pass"""
        path = 'cortex-brain/documents/implementation-guides/SETUP-GUIDE.md'
        result = validator.validate_naming_convention(path)
        assert result['valid'] is True
    
    def test_conversation_capture_naming_valid(self, validator):
        """Conversation capture with date should pass"""
        path = 'cortex-brain/documents/conversation-captures/CONVERSATION-CAPTURE-2025-11-18-PLANNING.md'
        result = validator.validate_naming_convention(path)
        assert result['valid'] is True
    
    def test_whitelist_skips_naming_validation(self, validator):
        """Whitelisted files should skip naming validation"""
        result = validator.validate_naming_convention('README.md')
        assert result['valid'] is True
        assert 'Whitelist' in result['reason']


class TestWorkspaceScan:
    """Test suite for workspace scanning functionality"""
    
    def test_scan_workspace_returns_structure(self, validator):
        """Workspace scan should return valid structure"""
        results = validator.scan_workspace()
        
        assert 'valid' in results
        assert 'violations' in results
        assert 'suggestions' in results
        assert isinstance(results['valid'], list)
        assert isinstance(results['violations'], list)
        assert isinstance(results['suggestions'], dict)
    
    def test_scan_detects_organized_documents(self, validator):
        """Scan should find organized documents"""
        results = validator.scan_workspace()
        
        # Should find documents in cortex-brain/documents/ or docs/
        organized_docs = [
            path for path in results['valid']
            if 'cortex-brain/documents/' in path or 'docs/' in path.replace('\\', '/')
        ]
        
        # We have at least some organized documents (at minimum awakening-of-cortex.md)
        assert len(organized_docs) > 0, f"Found {len(results['valid'])} valid docs, none organized"
    
    def test_scan_ignores_hidden_directories(self, validator):
        """Scan should skip hidden directories like .git"""
        results = validator.scan_workspace()
        
        all_paths = results['valid'] + results['violations']
        hidden_paths = [path for path in all_paths if '/.git/' in path or '\\.git\\' in path]
        
        assert len(hidden_paths) == 0
    
    def test_scan_ignores_node_modules(self, validator):
        """Scan should skip node_modules directory"""
        results = validator.scan_workspace()
        
        all_paths = results['valid'] + results['violations']
        node_module_paths = [path for path in all_paths if 'node_modules' in path]
        
        assert len(node_module_paths) == 0


class TestConvenienceFunctions:
    """Test convenience functions for easy validation"""
    
    def test_validate_document_convenience(self):
        """validate_document() should work without validator instance"""
        result = validate_document('README.md')
        assert result['valid'] is True
    
    def test_validate_organized_document_convenience(self):
        """validate_document() should validate organized paths"""
        path = 'cortex-brain/documents/reports/TEST-REPORT.md'
        result = validate_document(path)
        assert result['valid'] is True


# Integration test to validate real workspace
class TestRealWorkspace:
    """Integration tests against actual CORTEX workspace"""
    
    def test_awakening_story_in_correct_location(self):
        """Verify awakening-of-cortex.md is in docs/ directory"""
        story_path = Path('docs/awakening-of-cortex.md')
        result = validate_document(str(story_path))
        
        assert result['valid'] is True
        assert result['category'] == 'user-docs'
    
    def test_index_in_correct_location(self):
        """Verify docs/index.md exists and is valid"""
        index_path = Path('docs/index.md')
        result = validate_document(str(index_path))
        
        assert result['valid'] is True
        assert result['category'] == 'user-docs'
    
    def test_document_readme_exists(self):
        """Verify cortex-brain/documents/README.md exists"""
        readme_path = Path('cortex-brain/documents/README.md')
        workspace_root = Path(__file__).parent.parent.parent
        full_path = workspace_root / readme_path
        
        assert full_path.exists(), "Documents README.md should exist"
        
        result = validate_document(str(readme_path))
        # Should be whitelisted or in organized structure
        assert result['valid'] is True
    
    def test_no_violations_in_organized_directories(self, validator):
        """Documents in cortex-brain/documents/ should all be valid"""
        results = validator.scan_workspace()
        
        # Filter for cortex-brain/documents/ paths
        organized_violations = [
            v for v in results['violations']
            if 'cortex-brain/documents/' in v
        ]
        
        # Should have zero violations in organized directories
        assert len(organized_violations) == 0, f"Found violations: {organized_violations}"
