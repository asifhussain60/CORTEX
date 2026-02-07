"""
Tests for Phase 38 Readiness Validator - Phase 38.0 Stage 5
Tests MUST come before implementation (CORE-008 TDD)

AC-PHASE38.0-005: Phase 38 Readiness Validation
- Validates Phase 34 completion (24/24 tests)
- Validates test collection (0 errors)
- Validates orchestrator inventory (report exists)
- Validates baseline metrics (report exists)
- Validates test suite baseline (8,846+ tests)
- Validates Phase 38 index readiness
"""

import pytest
from pathlib import Path
from typing import Dict, Any
import json


class TestPhase38ReadinessValidator:
    """Test suite for Phase 38 readiness validation."""
    
    def test_validator_initializes(self):
        """Test validator initialization."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        assert validator.workspace_root == workspace
        assert validator.reports_dir.exists()
    
    def test_validator_checks_phase_34_completion(self):
        """Test validation of Phase 34 completion."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        result = validator.check_phase_34_completion()
        
        assert "status" in result
        assert "tests_passing" in result
        assert isinstance(result["status"], bool)
    
    def test_validator_checks_test_collection(self):
        """Test validation of test collection status."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        result = validator.check_test_collection()
        
        assert "status" in result
        assert "import_errors" in result
        assert isinstance(result["status"], bool)
    
    def test_validator_checks_orchestrator_inventory(self):
        """Test validation of orchestrator inventory report."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        result = validator.check_orchestrator_inventory()
        
        assert "status" in result
        assert "report_found" in result
        assert isinstance(result["status"], bool)
    
    def test_validator_checks_baseline_metrics(self):
        """Test validation of baseline metrics report."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        result = validator.check_baseline_metrics()
        
        assert "status" in result
        assert "report_found" in result
        assert isinstance(result["status"], bool)
    
    def test_validator_checks_test_suite_baseline(self):
        """Test validation of test suite baseline."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        result = validator.check_test_suite_baseline()
        
        assert "status" in result
        assert "tests_collected" in result
        assert isinstance(result["status"], bool)
    
    def test_validator_checks_phase_38_index(self):
        """Test validation of Phase 38 index status."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        result = validator.check_phase_38_index()
        
        assert "status" in result
        assert "index_file_exists" in result
        assert isinstance(result["status"], bool)
    
    def test_validator_runs_all_checks(self):
        """Test running all validation checks."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        results = validator.run_all_checks()
        
        assert "checks" in results
        assert "summary" in results
        assert "overall_status" in results
        assert len(results["checks"]) == 6
    
    def test_validator_calculates_readiness_score(self):
        """Test calculation of readiness score."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        results = validator.run_all_checks()
        score = validator.calculate_readiness_score(results)
        
        assert isinstance(score, float)
        assert 0.0 <= score <= 100.0
    
    def test_validator_generates_readiness_report(self):
        """Test generation of readiness validation report."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        report_path = validator.generate_readiness_report()
        
        assert report_path.exists()
        assert report_path.suffix == ".json"
        assert "phase-38-readiness" in report_path.name
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert "timestamp" in report
        assert "readiness_score" in report
        assert "checks" in report
        assert "verdict" in report
    
    def test_validator_report_includes_recommendations(self):
        """Test that report includes recommendations for failed checks."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        report_path = validator.generate_readiness_report()
        
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        if report["readiness_score"] < 100.0:
            assert "recommendations" in report
            assert isinstance(report["recommendations"], list)
    
    def test_validator_exit_code_reflects_readiness(self):
        """Test that validator returns proper exit code."""
        from cortex.phase_38.readiness_validator import Phase38ReadinessValidator
        
        workspace = Path("/Users/asifhussain/PROJECTS/CORTEX")
        validator = Phase38ReadinessValidator(workspace_root=workspace)
        
        exit_code = validator.validate_and_exit()
        
        # Exit code 0 = ready, 1 = not ready
        assert exit_code in [0, 1]
