"""
Test capability-driven documentation coverage validation

Validates that the new coverage validation correctly:
1. Loads capabilities from capabilities.yaml
2. Generates expected documentation list
3. Scans existing docs
4. Calculates coverage percentage
5. Identifies gaps
6. Passes/fails based on threshold
"""

import pytest
from pathlib import Path
from src.epm.modules.validation_engine import ValidationEngine


class TestCapabilityCoverageValidation:
    """Test suite for capability-driven documentation coverage"""
    
    @pytest.fixture
    def workspace_root(self, tmp_path):
        """Create temporary workspace structure"""
        root = tmp_path / "cortex"
        root.mkdir()
        
        # Create brain structure
        brain_path = root / "cortex-brain"
        brain_path.mkdir()
        
        # Create docs structure
        docs_path = root / "docs"
        docs_path.mkdir()
        (docs_path / "guides").mkdir()
        (docs_path / "api").mkdir()
        
        return root
    
    @pytest.fixture
    def sample_capabilities(self, workspace_root):
        """Create sample capabilities.yaml"""
        capabilities_content = """
version: "2.0"

capabilities:
  - id: "code_writing"
    name: "Code Writing"
    status: "implemented"
    can_do: true
    agent: "code_executor"
    
  - id: "code_review"
    name: "Code Review"
    status: "partial"
    can_do: true
    
  - id: "backend_testing"
    name: "Backend Testing"
    status: "implemented"
    can_do: true
    agent: "test_generator"
    
  - id: "mobile_testing"
    name: "Mobile Testing"
    status: "not_implemented"
    can_do: "partial"
    
  - id: "code_documentation"
    name: "Code Documentation"
    status: "implemented"
    can_do: true
"""
        capabilities_file = workspace_root / "cortex-brain" / "capabilities.yaml"
        capabilities_file.write_text(capabilities_content)
        return capabilities_file
    
    def test_validation_with_full_coverage(self, workspace_root, sample_capabilities):
        """Test validation passes when all implemented capabilities are documented"""
        # Create documentation for all implemented capabilities
        docs_path = workspace_root / "docs"
        (docs_path / "guides" / "code-writing.md").write_text("# Code Writing Guide")
        (docs_path / "guides" / "code-review.md").write_text("# Code Review Guide")
        (docs_path / "guides" / "backend-testing.md").write_text("# Backend Testing Guide")
        (docs_path / "guides" / "code-documentation.md").write_text("# Code Documentation Guide")
        
        # Run validation
        validator = ValidationEngine(workspace_root)
        is_valid, report = validator.validate_documentation_coverage(coverage_threshold=0.80)
        
        # Should pass with 100% coverage (4/4 implemented capabilities documented)
        assert is_valid is True
        assert report['coverage_rate'] == 1.0
        assert report['documented_capabilities'] == 4
        assert report['undocumented_capabilities'] == 0
        assert report['status'] == "PASS"
    
    def test_validation_with_partial_coverage(self, workspace_root, sample_capabilities):
        """Test validation fails when coverage below threshold"""
        # Create documentation for only 2 out of 4 implemented capabilities
        docs_path = workspace_root / "docs"
        (docs_path / "guides" / "code-writing.md").write_text("# Code Writing Guide")
        (docs_path / "guides" / "backend-testing.md").write_text("# Backend Testing Guide")
        
        # Run validation
        validator = ValidationEngine(workspace_root)
        is_valid, report = validator.validate_documentation_coverage(coverage_threshold=0.80)
        
        # Should fail with only 50% coverage (2/4 implemented capabilities documented)
        assert is_valid is False
        assert report['coverage_rate'] == 0.5
        assert report['documented_capabilities'] == 2
        assert report['undocumented_capabilities'] == 2
        assert report['status'] == "FAIL"
        
        # Check undocumented list
        undoc_ids = [cap['id'] for cap in report['undocumented_list']]
        assert 'code_review' in undoc_ids
        assert 'code_documentation' in undoc_ids
    
    def test_validation_ignores_not_implemented(self, workspace_root, sample_capabilities):
        """Test validation only counts implemented/partial capabilities"""
        # Create documentation for implemented capabilities only
        docs_path = workspace_root / "docs"
        (docs_path / "guides" / "code-writing.md").write_text("# Code Writing Guide")
        (docs_path / "guides" / "code-review.md").write_text("# Code Review Guide")
        (docs_path / "guides" / "backend-testing.md").write_text("# Backend Testing Guide")
        (docs_path / "guides" / "code-documentation.md").write_text("# Code Documentation Guide")
        # Note: mobile_testing is not_implemented, so no doc needed
        
        # Run validation
        validator = ValidationEngine(workspace_root)
        is_valid, report = validator.validate_documentation_coverage(coverage_threshold=0.80)
        
        # Should only count 4 implemented capabilities, not mobile_testing
        assert report['total_capabilities'] == 4
        assert is_valid is True
    
    def test_validation_flexible_naming(self, workspace_root, sample_capabilities):
        """Test validation handles flexible file naming (hyphens vs underscores)"""
        # Create documentation with various naming conventions
        docs_path = workspace_root / "docs"
        (docs_path / "guides" / "code_writing.md").write_text("# Code Writing")  # underscore
        (docs_path / "guides" / "code-review-guide.md").write_text("# Code Review")  # with suffix
        (docs_path / "guides" / "backend-testing.md").write_text("# Backend Testing")  # hyphen
        (docs_path / "guides" / "code-documentation.md").write_text("# Docs")
        
        # Run validation
        validator = ValidationEngine(workspace_root)
        is_valid, report = validator.validate_documentation_coverage(coverage_threshold=0.80)
        
        # Should match all despite naming variations
        assert is_valid is True
        assert report['documented_capabilities'] == 4
    
    def test_validation_reports_gaps(self, workspace_root, sample_capabilities):
        """Test validation provides detailed gap report"""
        # Create documentation for only 1 capability
        docs_path = workspace_root / "docs"
        (docs_path / "guides" / "code-writing.md").write_text("# Code Writing Guide")
        
        # Run validation
        validator = ValidationEngine(workspace_root)
        is_valid, report = validator.validate_documentation_coverage(coverage_threshold=0.80)
        
        # Should fail with detailed gap report
        assert is_valid is False
        assert len(report['undocumented_list']) == 3
        
        # Check gap details include expected patterns
        for cap in report['undocumented_list']:
            assert 'id' in cap
            assert 'name' in cap
            assert 'expected_docs' in cap
            assert len(cap['expected_docs']) > 0
    
    def test_validation_handles_missing_capabilities_file(self, workspace_root):
        """Test validation gracefully handles missing capabilities.yaml"""
        # Don't create capabilities.yaml
        
        # Run validation
        validator = ValidationEngine(workspace_root)
        is_valid, report = validator.validate_documentation_coverage()
        
        # Should fail with error message
        assert is_valid is False
        assert 'error' in report
        assert 'capabilities.yaml not found' in report['error']
    
    def test_validation_adjustable_threshold(self, workspace_root, sample_capabilities):
        """Test validation threshold is configurable"""
        # Create documentation for 75% of capabilities
        docs_path = workspace_root / "docs"
        (docs_path / "guides" / "code-writing.md").write_text("# Code Writing")
        (docs_path / "guides" / "backend-testing.md").write_text("# Backend Testing")
        (docs_path / "guides" / "code-documentation.md").write_text("# Code Documentation")
        
        # Run validation with 70% threshold - should pass
        validator = ValidationEngine(workspace_root)
        is_valid_70, report_70 = validator.validate_documentation_coverage(coverage_threshold=0.70)
        assert is_valid_70 is True
        assert report_70['coverage_rate'] == 0.75
        
        # Run validation with 80% threshold - should fail
        is_valid_80, report_80 = validator.validate_documentation_coverage(coverage_threshold=0.80)
        assert is_valid_80 is False
        assert report_80['coverage_rate'] == 0.75
    
    def test_validation_includes_metadata(self, workspace_root, sample_capabilities):
        """Test validation report includes useful metadata"""
        docs_path = workspace_root / "docs"
        (docs_path / "guides" / "code-writing.md").write_text("# Code Writing")
        
        # Run validation
        validator = ValidationEngine(workspace_root)
        is_valid, report = validator.validate_documentation_coverage()
        
        # Check metadata fields
        assert 'validation_approach' in report
        assert report['validation_approach'] == 'capability_driven'
        assert 'threshold' in report
        assert 'total_capabilities' in report
        assert 'documented_capabilities' in report
        assert 'undocumented_capabilities' in report
        assert 'coverage_rate' in report
        assert 'is_valid' in report
        assert 'status' in report
        assert report['status'] in ['PASS', 'FAIL']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
