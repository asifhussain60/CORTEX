"""
Tests for Validation Components

Tests integration depth scoring and validation:
- IntegrationScorer
- WiringValidator
- TestCoverageValidator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.validation.integration_scorer import IntegrationScorer
from src.validation.wiring_validator import WiringValidator
from src.validation.test_coverage_validator import TestCoverageValidator


class TestIntegrationScorer:
    """Test integration scorer."""
    
    @pytest.fixture
    def project_with_module(self, tmp_path):
        """Create project with importable module."""
        # Create module structure
        src_dir = tmp_path / "src"
        src_dir.mkdir()
        (src_dir / "__init__.py").write_text("")
        
        # Create test module
        test_module = src_dir / "test_module.py"
        test_module.write_text('''"""Test module."""

class TestOrchestrator:
    """Test orchestrator."""
    def __init__(self):
        pass
    
    def execute(self):
        return "success"
''')
        
        return tmp_path
    
    def test_validate_import_success(self, project_with_module):
        """Test successful import validation."""
        scorer = IntegrationScorer(project_with_module)
        
        result = scorer.validate_import("src.test_module")
        
        assert result is True
    
    def test_validate_import_failure(self, tmp_path):
        """Test import validation failure."""
        scorer = IntegrationScorer(tmp_path)
        
        result = scorer.validate_import("nonexistent.module")
        
        assert result is False
    
    def test_validate_instantiation_success(self, project_with_module):
        """Test successful instantiation validation."""
        scorer = IntegrationScorer(project_with_module)
        
        result = scorer.validate_instantiation("src.test_module", "TestOrchestrator")
        
        assert result is True
    
    def test_validate_instantiation_class_not_found(self, project_with_module):
        """Test instantiation with missing class."""
        scorer = IntegrationScorer(project_with_module)
        
        result = scorer.validate_instantiation("src.test_module", "NonexistentClass")
        
        assert result is False
    
    def test_calculate_score_full_integration(self, project_with_module):
        """Test score calculation with full integration."""
        scorer = IntegrationScorer(project_with_module)
        
        metadata = {
            "module_path": "src.test_module",
            "class_name": "TestOrchestrator"
        }
        
        score = scorer.calculate_score(
            feature_name="TestOrchestrator",
            metadata=metadata,
            feature_type="orchestrator",
            documentation_validated=True,
            test_coverage_pct=80.0,
            is_wired=True,
            performance_validated=True
        )
        
        assert score == 100
    
    def test_calculate_score_partial_integration(self, project_with_module):
        """Test score calculation with partial integration."""
        scorer = IntegrationScorer(project_with_module)
        
        metadata = {
            "module_path": "src.test_module",
            "class_name": "TestOrchestrator"
        }
        
        score = scorer.calculate_score(
            feature_name="TestOrchestrator",
            metadata=metadata,
            feature_type="orchestrator",
            documentation_validated=False,
            test_coverage_pct=0.0,
            is_wired=False,
            performance_validated=False
        )
        
        # Should have: discovered (20) + imported (20) + instantiated (20) = 60
        assert score == 60
    
    def test_get_score_breakdown(self):
        """Test score breakdown calculation."""
        scorer = IntegrationScorer(Path.cwd())
        
        breakdown = scorer.get_score_breakdown(75)
        
        assert breakdown["discovered"] is True
        assert breakdown["imported"] is True
        assert breakdown["instantiated"] is True
        assert breakdown["documented"] is True
        assert breakdown["tested"] is False
        assert breakdown["wired"] is False
        assert breakdown["optimized"] is False


class TestWiringValidator:
    """Test wiring validator."""
    
    @pytest.fixture
    def sample_orchestrators(self):
        """Sample discovered orchestrators."""
        return {
            "TDDWorkflowOrchestrator": {
                "class_name": "TDDWorkflowOrchestrator",
                "module_path": "src.workflows.tdd_workflow_orchestrator"
            },
            "SetupOrchestrator": {
                "class_name": "SetupOrchestrator",
                "module_path": "src.setup.setup_orchestrator"
            }
        }
    
    @pytest.fixture
    def sample_entry_points(self):
        """Sample entry points."""
        return {
            "start tdd": {
                "template": "tdd_workflow",
                "expected_orchestrator": "TDDWorkflowOrchestrator"
            },
            "optimize": {
                "template": "optimize_system",
                "expected_orchestrator": "OptimizeOrchestrator"  # Missing
            },
            "setup": {
                "template": "setup_environment",
                "expected_orchestrator": "SetupOrchestrator"
            }
        }
    
    def test_validate_wiring_detects_orphaned_triggers(
        self,
        tmp_path,
        sample_orchestrators,
        sample_entry_points
    ):
        """Test detection of orphaned triggers."""
        validator = WiringValidator(tmp_path)
        
        results = validator.validate_wiring(sample_orchestrators, sample_entry_points)
        
        assert results["orphaned_count"] == 1
        assert len(results["orphaned_triggers"]) == 1
        assert results["orphaned_triggers"][0]["trigger"] == "optimize"
    
    def test_validate_wiring_detects_ghost_features(
        self,
        tmp_path,
        sample_entry_points
    ):
        """Test detection of ghost features."""
        validator = WiringValidator(tmp_path)
        
        orchestrators = {
            "TDDWorkflowOrchestrator": {},
            "UnwiredOrchestrator": {},  # Ghost
            "SetupOrchestrator": {}
        }
        
        results = validator.validate_wiring(orchestrators, sample_entry_points)
        
        assert results["ghost_count"] == 1
        assert results["ghost_features"][0]["orchestrator"] == "UnwiredOrchestrator"
    
    def test_validate_wiring_counts_wired_orchestrators(
        self,
        tmp_path,
        sample_orchestrators,
        sample_entry_points
    ):
        """Test counting of properly wired orchestrators."""
        validator = WiringValidator(tmp_path)
        
        results = validator.validate_wiring(sample_orchestrators, sample_entry_points)
        
        assert results["wired_count"] == 2  # TDD and Setup
        assert "TDDWorkflowOrchestrator" in results["wired_orchestrators"]
        assert "SetupOrchestrator" in results["wired_orchestrators"]
    
    def test_check_orchestrator_wired_true(self, tmp_path, sample_entry_points):
        """Test checking if orchestrator is wired."""
        validator = WiringValidator(tmp_path)
        
        result = validator.check_orchestrator_wired(
            "TDDWorkflowOrchestrator",
            sample_entry_points
        )
        
        assert result is True
    
    def test_check_orchestrator_wired_false(self, tmp_path, sample_entry_points):
        """Test checking unwired orchestrator."""
        validator = WiringValidator(tmp_path)
        
        result = validator.check_orchestrator_wired(
            "NonexistentOrchestrator",
            sample_entry_points
        )
        
        assert result is False
    
    def test_get_wiring_status_admin(self, tmp_path):
        """Test admin orchestrator status."""
        validator = WiringValidator(tmp_path)
        
        status = validator.get_wiring_status("SystemAlignmentOrchestrator", {})
        
        assert status == "admin"
    
    def test_get_wiring_status_wired(self, tmp_path, sample_entry_points):
        """Test wired orchestrator status."""
        validator = WiringValidator(tmp_path)
        
        status = validator.get_wiring_status("TDDWorkflowOrchestrator", sample_entry_points)
        
        assert status == "wired"
    
    def test_get_wiring_status_unwired(self, tmp_path, sample_entry_points):
        """Test unwired orchestrator status."""
        validator = WiringValidator(tmp_path)
        
        status = validator.get_wiring_status("UnwiredOrchestrator", sample_entry_points)
        
        assert status == "unwired"


class TestTestCoverageValidator:
    """Test test coverage validator."""
    
    @pytest.fixture
    def project_with_tests(self, tmp_path):
        """Create project with test files."""
        # Create test directory
        tests_dir = tmp_path / "tests" / "workflows"
        tests_dir.mkdir(parents=True)
        
        # Create test file
        test_file = tests_dir / "test_tdd_workflow_orchestrator.py"
        test_file.write_text('''"""Tests for TDD workflow."""
import pytest

class TestTDDWorkflowOrchestrator:
    """Test TDD workflow orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        return None
    
    @pytest.mark.parametrize("input,expected", [(1, 2), (2, 3)])
    def test_increment(self, input, expected):
        assert input + 1 == expected
    
    def test_execute(self):
        assert True
    
    def test_validate(self):
        assert True
''')
        
        return tmp_path
    
    def test_find_test_file_success(self, project_with_tests):
        """Test finding test file."""
        validator = TestCoverageValidator(project_with_tests)
        
        test_file = validator.find_test_file("TDDWorkflowOrchestrator", "orchestrator")
        
        assert test_file is not None
        assert test_file.name == "test_tdd_workflow_orchestrator.py"
    
    def test_find_test_file_not_found(self, tmp_path):
        """Test when test file doesn't exist."""
        validator = TestCoverageValidator(tmp_path)
        
        test_file = validator.find_test_file("NonexistentOrchestrator", "orchestrator")
        
        assert test_file is None
    
    def test_get_test_coverage_with_tests(self, project_with_tests):
        """Test getting coverage when tests exist."""
        validator = TestCoverageValidator(project_with_tests)
        
        coverage = validator.get_test_coverage("TDDWorkflowOrchestrator", "orchestrator")
        
        assert coverage["has_tests"] is True
        assert coverage["test_count"] == 3
        assert coverage["status"] in ["good", "needs_improvement"]
    
    def test_get_test_coverage_no_tests(self, tmp_path):
        """Test getting coverage when no tests exist."""
        validator = TestCoverageValidator(tmp_path)
        
        coverage = validator.get_test_coverage("NonexistentOrchestrator", "orchestrator")
        
        assert coverage["has_tests"] is False
        assert coverage["test_count"] == 0
        assert coverage["coverage_pct"] == 0.0
        assert coverage["status"] == "no_tests"
    
    def test_snake_case_conversion(self, tmp_path):
        """Test CamelCase to snake_case conversion."""
        validator = TestCoverageValidator(tmp_path)
        
        result = validator._snake_case("TDDWorkflowOrchestrator")
        
        assert result == "t_d_d_workflow_orchestrator"
    
    def test_validate_test_quality(self, project_with_tests):
        """Test test quality validation."""
        validator = TestCoverageValidator(project_with_tests)
        
        test_file = validator.find_test_file("TDDWorkflowOrchestrator", "orchestrator")
        quality = validator.validate_test_quality(test_file)
        
        assert quality["assertion_count"] >= 3
        assert quality["has_parametrize"] is True
        assert quality["has_fixtures"] is True
        assert quality["test_class_count"] >= 1
        assert quality["quality_score"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
