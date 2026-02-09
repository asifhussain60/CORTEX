"""
Phase 38 Stage 11: FileGovernanceValidator Tests
Authority: TDDOrchestrator | CORE-008
"""

import pytest
from pathlib import Path
from cortex.orchestrators.support.file_governance_validator import (
    FileGovernanceValidator,
    FolderStructureStatus,
)


class TestFileGovernanceValidator:
    """FileGovernanceValidator - validates folder structure"""

    @pytest.fixture
    def workspace(self, tmp_path):
        """Create test workspace structure"""
        # Create CORTEX structure
        (tmp_path / "cortex").mkdir()
        (tmp_path / "cortex" / "orchestrators").mkdir(parents=True)
        (tmp_path / "cortex" / "agents").mkdir(parents=True)
        (tmp_path / "cortex" / "governance").mkdir(parents=True)
        (tmp_path / "tests" / "unit").mkdir(parents=True)
        (tmp_path / "docs").mkdir(parents=True)
        
        # Add some files
        (tmp_path / "cortex" / "orchestrators" / "test_orch.py").write_text("pass")
        (tmp_path / "tests" / "unit" / "test_example.py").write_text("pass")
        
        return tmp_path

    @pytest.fixture
    def validator(self, workspace):
        """Initialize validator"""
        return FileGovernanceValidator(workspace)

    def test_initialization(self, validator, workspace):
        """Test: Validator initializes"""
        assert validator.workspace_root == workspace
        assert validator.required_dirs is not None
        assert validator.expected_structure is not None

    def test_validate_structure_returns_result(self, validator):
        """Test: validate_structure returns ValidationResult"""
        result = validator.validate_structure()
        
        assert result is not None
        assert hasattr(result, 'status')
        assert hasattr(result, 'issues')
        assert hasattr(result, 'structure_score')

    def test_validate_structure_status(self, validator):
        """Test: Status is valid FolderStructureStatus"""
        result = validator.validate_structure()
        
        assert isinstance(result.status, FolderStructureStatus)
        assert result.status in [
            FolderStructureStatus.OPTIMAL,
            FolderStructureStatus.ACCEPTABLE,
            FolderStructureStatus.NEEDS_IMPROVEMENT,
            FolderStructureStatus.CRITICAL,
        ]

    def test_validate_structure_score_range(self, validator):
        """Test: Structure score is 0.0-1.0"""
        result = validator.validate_structure()
        
        assert 0.0 <= result.structure_score <= 1.0

    def test_validate_naming_conventions(self, validator, workspace):
        """Test: Validates naming conventions"""
        # Create test files with various naming
        (workspace / "cortex" / "good_name.py").write_text("pass")
        (workspace / "cortex" / "SCREAMING_CASE.py").write_text("pass")
        
        valid, issues = validator.validate_naming_conventions()
        
        assert isinstance(valid, bool)
        assert isinstance(issues, list)

    def test_get_expected_location_for_orchestrator(self, validator, workspace):
        """Test: Gets expected location for orchestrator"""
        orch_file = workspace / "my_orchestrator.py"
        orch_file.write_text("pass")
        
        location = validator._get_expected_location(orch_file)
        
        assert location is not None
        assert "orchestrators" in location.lower()

    def test_get_expected_location_for_test(self, validator, workspace):
        """Test: Gets expected location for test"""
        test_file = workspace / "test_something.py"
        test_file.write_text("pass")
        
        location = validator._get_expected_location(test_file)
        
        assert location is not None

    def test_generate_improvement_plan(self, validator):
        """Test: Generates improvement plan"""
        result = validator.validate_structure()
        plan = validator.generate_improvement_plan(result)
        
        assert isinstance(plan, dict)
        assert "current_status" in plan
        assert "structure_score" in plan
        assert "immediate_actions" in plan

    def test_matches_pattern_wildcard_start(self, validator):
        """Test: Pattern matching with wildcard at start"""
        assert validator._matches_pattern("test_file.py", "*.py") is True
        assert validator._matches_pattern("test_file.py", "*_file.py") is True

    def test_matches_pattern_wildcard_end(self, validator):
        """Test: Pattern matching with wildcard at end"""
        assert validator._matches_pattern("file.py", "file.*") is True
        assert validator._matches_pattern("test_orch.py", "test_*") is True

    def test_is_screaming_case(self, validator):
        """Test: Detects SCREAMING_CASE"""
        assert validator._is_screaming_case("SCREAMING_CASE") is True
        assert validator._is_screaming_case("my_module") is False

    def test_is_camel_case(self, validator):
        """Test: Detects CamelCase"""
        assert validator._is_camel_case("CamelCase") is True
        assert validator._is_camel_case("camelCase") is True
        assert validator._is_camel_case("kebab_case") is False

    def test_calculate_score(self, validator):
        """Test: Calculates structure score correctly"""
        score = validator._calculate_score(num_issues=0, num_missing=0, num_misplaced=0)
        assert score == 1.0
        
        score = validator._calculate_score(num_issues=5, num_missing=5, num_misplaced=5)
        assert 0.0 <= score < 1.0

    def test_integration_complete_validation(self, validator):
        """Integration: Complete validation workflow"""
        # Validate structure
        result = validator.validate_structure()
        assert result is not None
        
        # Validate naming
        naming_valid, naming_issues = validator.validate_naming_conventions()
        assert isinstance(naming_valid, bool)
        
        # Generate plan
        plan = validator.generate_improvement_plan(result)
        assert isinstance(plan, dict)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
