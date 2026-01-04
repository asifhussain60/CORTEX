"""
Unit tests for Phase-Level Acceptance Criteria Validation.

Tests DoR/DoD validation, blocking behavior, and integration with
Planning Orchestrator v5.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.

CORTEX-5.0 Sub-Plan 10 (C50-10): Gap 1 Remediation Tests
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import logging
import subprocess

from src.orchestrators.planning.acceptance_validator import (
    AcceptanceCriteriaValidator,
    PhaseNotReadyError,
    PhaseIncompleteError
)


@pytest.fixture
def temp_plan_dir(tmp_path):
    """Create temporary plan directory structure."""
    plan_dir = tmp_path / "C50-10"
    plan_dir.mkdir()
    (plan_dir / "context").mkdir()
    return plan_dir


@pytest.fixture
def sample_criteria():
    """Sample acceptance criteria YAML content."""
    return {
        "phases": [
            {
                "phase_number": 0,
                "dor": [
                    {
                        "criterion": "Test coverage ≥50%",
                        "validation_type": "automated",
                        "validation_command": "echo 'coverage: 89%'"
                    },
                    {
                        "criterion": "Dependencies met",
                        "validation_type": "manual",
                        "validation_notes": "C50-00B complete"
                    }
                ],
                "dod": [
                    {
                        "criterion": "Functions implemented",
                        "validation_type": "automated",
                        "validation_command": "/usr/bin/python3 -c 'import sys; sys.exit(0)'"
                    },
                    {
                        "criterion": "Code reviewed",
                        "validation_type": "manual",
                        "validation_notes": "PR approved"
                    }
                ]
            },
            {
                "phase_number": 1,
                "dor": [
                    {
                        "criterion": "Phase 0 complete",
                        "validation_type": "automated",
                        "validation_command": "test -f /tmp/phase_0_done"
                    }
                ],
                "dod": [
                    {
                        "criterion": "Integration tests pass",
                        "validation_type": "automated",
                        "validation_command": "pytest tests/ --tb=short"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def validator_with_criteria(temp_plan_dir, sample_criteria):
    """Create validator with sample criteria."""
    criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
    with open(criteria_file, 'w') as f:
        yaml.dump(sample_criteria, f)
    
    return AcceptanceCriteriaValidator(
        plan_root=temp_plan_dir,
        logger=logging.getLogger("test")
    )


class TestAcceptanceCriteriaValidator:
    """Test suite for AcceptanceCriteriaValidator."""
    
    def test_init_with_existing_criteria(self, temp_plan_dir, sample_criteria):
        """Test validator initialization with existing criteria file."""
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(sample_criteria, f)
        
        validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=logging.getLogger("test")
        )
        
        assert validator.criteria == sample_criteria
        assert validator.plan_root == temp_plan_dir
        assert validator.criteria_file == criteria_file
    
    def test_init_without_criteria_file(self, temp_plan_dir):
        """Test validator initialization when criteria file doesn't exist."""
        validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=logging.getLogger("test")
        )
        
        assert validator.criteria == {"phases": []}
        assert not validator.criteria_file.exists()
    
    def test_get_phase_criteria_existing_phase(self, validator_with_criteria):
        """Test retrieval of criteria for existing phase."""
        dor_criteria = validator_with_criteria._get_phase_criteria(0, "dor")
        
        assert len(dor_criteria) == 2
        assert dor_criteria[0]["criterion"] == "Test coverage ≥50%"
        assert dor_criteria[1]["criterion"] == "Dependencies met"
    
    def test_get_phase_criteria_missing_phase(self, validator_with_criteria):
        """Test retrieval of criteria for non-existent phase."""
        dor_criteria = validator_with_criteria._get_phase_criteria(999, "dor")
        
        assert dor_criteria == []
    
    def test_validate_automated_criterion_success(self, validator_with_criteria):
        """Test automated criterion validation - success case."""
        criterion = {
            "criterion": "Echo test",
            "validation_type": "automated",
            "validation_command": "echo 'success'"
        }
        
        success, error = validator_with_criteria._validate_criterion(criterion)
        
        assert success is True
        assert error is None
    
    def test_validate_automated_criterion_failure(self, validator_with_criteria):
        """Test automated criterion validation - failure case."""
        criterion = {
            "criterion": "Exit with error",
            "validation_type": "automated",
            "validation_command": "exit 1"
        }
        
        success, error = validator_with_criteria._validate_criterion(criterion)
        
        assert success is False
        assert "Command failed" in error or "exit 1" in error.lower()
    
    def test_validate_automated_criterion_timeout(self, validator_with_criteria):
        """Test automated criterion validation - timeout case."""
        criterion = {
            "criterion": "Long-running command",
            "validation_type": "automated",
            "validation_command": "/bin/sleep 60"
        }
        
        success, error = validator_with_criteria._validate_criterion(criterion)
        
        assert success is False
        assert "timeout" in error.lower() or "timed out" in error.lower()
    
    def test_validate_manual_criterion(self, validator_with_criteria):
        """Test manual criterion validation - always passes."""
        criterion = {
            "criterion": "Manual review",
            "validation_type": "manual",
            "validation_notes": "Code reviewed and approved"
        }
        
        success, error = validator_with_criteria._validate_criterion(criterion)
        
        assert success is True
        assert error is None
    
    def test_validate_unknown_criterion_type(self, validator_with_criteria):
        """Test validation with unknown criterion type - non-blocking."""
        criterion = {
            "criterion": "Unknown type",
            "validation_type": "future_type",
            "validation_command": "echo 'test'"
        }
        
        success, error = validator_with_criteria._validate_criterion(criterion)
        
        assert success is True  # Unknown types don't block
        assert error is None
    
    def test_validate_phase_dor_all_pass(self, validator_with_criteria):
        """Test Phase 0 DoR validation - all criteria pass."""
        # Phase 0 has automated command "echo 'coverage: 89%'" which exits 0
        result = validator_with_criteria.validate_phase_dor(0)
        
        assert result is True
    
    def test_validate_phase_dor_no_criteria(self, validator_with_criteria):
        """Test DoR validation for phase with no criteria."""
        result = validator_with_criteria.validate_phase_dor(999)
        
        assert result is True  # No criteria = no blocking
    
    def test_validate_phase_dor_blocking_failure(self, temp_plan_dir):
        """Test DoR validation blocks when automated criterion fails."""
        blocking_criteria = {
            "phases": [
                {
                    "phase_number": 0,
                    "dor": [
                        {
                            "criterion": "Required file exists",
                            "validation_type": "automated",
                            "validation_command": "test -f /nonexistent/file"
                        }
                    ]
                }
            ]
        }
        
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(blocking_criteria, f)
        
        validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=logging.getLogger("test")
        )
        
        with pytest.raises(PhaseNotReadyError) as exc_info:
            validator.validate_phase_dor(0)
        
        assert "DoR validation failed" in str(exc_info.value)
        assert "Required file exists" in str(exc_info.value)
    
    def test_validate_phase_dod_all_pass(self, validator_with_criteria):
        """Test Phase 0 DoD validation - all criteria pass."""
        # Phase 0 has automated command "python -c 'import sys; sys.exit(0)'" which exits 0
        result = validator_with_criteria.validate_phase_dod(0)
        
        assert result is True
    
    def test_validate_phase_dod_no_criteria(self, validator_with_criteria):
        """Test DoD validation for phase with no criteria."""
        result = validator_with_criteria.validate_phase_dod(999)
        
        assert result is True  # No criteria = no blocking
    
    def test_validate_phase_dod_blocking_failure(self, temp_plan_dir):
        """Test DoD validation blocks when automated criterion fails."""
        blocking_criteria = {
            "phases": [
                {
                    "phase_number": 0,
                    "dod": [
                        {
                            "criterion": "All tests pass",
                            "validation_type": "automated",
                            "validation_command": "/usr/bin/python3 -c 'import sys; sys.exit(1)'"
                        }
                    ]
                }
            ]
        }
        
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(blocking_criteria, f)
        
        validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=logging.getLogger("test")
        )
        
        with pytest.raises(PhaseIncompleteError) as exc_info:
            validator.validate_phase_dod(0)
        
        assert "DoD validation failed" in str(exc_info.value)
        assert "All tests pass" in str(exc_info.value)
    
    def test_get_validation_report_all_pass(self, validator_with_criteria):
        """Test validation report generation - all criteria pass."""
        report = validator_with_criteria.get_validation_report(0)
        
        assert report["phase_number"] == 0
        assert report["dor_status"] == "passed"
        assert report["dod_status"] == "passed"
        assert report["dor_criteria_count"] == 2
        assert report["dod_criteria_count"] == 2
        assert "timestamp" in report
    
    def test_get_validation_report_dor_fails(self, temp_plan_dir):
        """Test validation report when DoR fails."""
        failing_criteria = {
            "phases": [
                {
                    "phase_number": 0,
                    "dor": [
                        {
                            "criterion": "Failing check",
                            "validation_type": "automated",
                            "validation_command": "exit 1"
                        }
                    ],
                    "dod": []
                }
            ]
        }
        
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(failing_criteria, f)
        
        validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=logging.getLogger("test")
        )
        
        report = validator.get_validation_report(0)
        
        assert report["dor_status"] == "failed"
        assert "dor_errors" in report
        assert "DoR validation failed" in report["dor_errors"]
    
    def test_missing_validation_command(self, temp_plan_dir):
        """Test automated criterion without validation command."""
        incomplete_criteria = {
            "phases": [
                {
                    "phase_number": 0,
                    "dor": [
                        {
                            "criterion": "No command",
                            "validation_type": "automated"
                            # Missing validation_command
                        }
                    ]
                }
            ]
        }
        
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(incomplete_criteria, f)
        
        validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=logging.getLogger("test")
        )
        
        with pytest.raises(PhaseNotReadyError) as exc_info:
            validator.validate_phase_dor(0)
        
        assert "No validation command" in str(exc_info.value)


@pytest.mark.skip(reason="Integration test - requires full orchestrator setup and YAML fixes")
class TestPlanningOrchestratorIntegration:
    """Test integration of acceptance validator with Planning Orchestrator v5."""
    
    @patch('src.orchestrators.base.base_orchestrator_v4_1.BaseOrchestratorV4_1.load_config')
    @patch('src.orchestrators.planning.planning_orchestrator_v5.PlanningStateDB')
    def test_validator_initialization_in_execute(self, mock_db, mock_load_config, temp_plan_dir):
        """Test validator is initialized during orchestrator execute()."""
        from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
        
        # Mock config loading
        mock_load_config.return_value = {
            "orchestrator_id": "planning_v5",
            "version": "5.0",
            "phases": []
        }
        
        # Create plan directory for initialization
        temp_plan_dir.mkdir(parents=True, exist_ok=True)
        
        orchestrator = PlanningOrchestratorV5(
            config_path="cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
            state_db=mock_db.return_value
        )
        
        # Initially None
        assert orchestrator.acceptance_validator is None
    
    @patch('src.orchestrators.base.base_orchestrator_v4_1.BaseOrchestratorV4_1.load_config')
    @patch('src.orchestrators.planning.planning_orchestrator_v5.BaseOrchestratorV4_1.execute_phase')
    def test_dor_validation_before_phase_start(self, mock_base_execute, mock_load_config, temp_plan_dir, sample_criteria):
        """Test DoR validation runs before phase starts."""
        from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
        from src.orchestrators.base.base_orchestrator_v4_1 import PhaseResult, PhaseStatus
        
        # Mock config loading
        mock_load_config.return_value = {
            "orchestrator_id": "planning_v5",
            "version": "5.0",
            "phases": []
        }
        
        # Setup
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(sample_criteria, f)
        
        mock_db = Mock()
        orchestrator = PlanningOrchestratorV5(
            config_path="cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
            state_db=mock_db
        )
        
        orchestrator.acceptance_validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=orchestrator.logger
        )
        
        mock_base_execute.return_value = PhaseResult(
            phase_id="test_phase",
            phase_number=0,
            name="Test Phase",
            status=PhaseStatus.COMPLETED
        )
        
        # Execute - should validate DoR before calling base
        result = orchestrator.execute_phase(0, {'name': 'Test Phase'})
        
        assert result.status == PhaseStatus.COMPLETED
        mock_base_execute.assert_called_once()
    
    @patch('src.orchestrators.base.base_orchestrator_v4_1.BaseOrchestratorV4_1.load_config')
    @patch('src.orchestrators.planning.planning_orchestrator_v5.BaseOrchestratorV4_1.execute_phase')
    def test_dod_validation_after_phase_complete(self, mock_base_execute, mock_load_config, temp_plan_dir, sample_criteria):
        """Test DoD validation runs after phase completes."""
        from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
        from src.orchestrators.base.base_orchestrator_v4_1 import PhaseResult, PhaseStatus
        
        # Mock config loading
        mock_load_config.return_value = {
            "orchestrator_id": "planning_v5",
            "version": "5.0",
            "phases": []
        }
        
        # Setup
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(sample_criteria, f)
        
        mock_db = Mock()
        orchestrator = PlanningOrchestratorV5(
            config_path="cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
            state_db=mock_db
        )
        
        orchestrator.acceptance_validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=orchestrator.logger
        )
        
        mock_base_execute.return_value = PhaseResult(
            phase_id="test_phase",
            phase_number=0,
            name="Test Phase",
            status=PhaseStatus.COMPLETED
        )
        
        # Execute - should validate DoD after base execution
        result = orchestrator.execute_phase(0, {'name': 'Test Phase'})
        
        assert result.status == PhaseStatus.COMPLETED
    
    @patch('src.orchestrators.base.base_orchestrator_v4_1.BaseOrchestratorV4_1.load_config')
    @patch('src.orchestrators.planning.planning_orchestrator_v5.BaseOrchestratorV4_1.execute_phase')
    def test_dor_failure_blocks_execution(self, mock_base_execute, mock_load_config, temp_plan_dir):
        """Test DoR validation failure prevents phase execution."""
        from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
        
        # Mock config loading
        mock_load_config.return_value = {
            "orchestrator_id": "planning_v5",
            "version": "5.0",
            "phases": []
        }
        
        # Setup with failing DoR
        blocking_criteria = {
            "phases": [
                {
                    "phase_number": 0,
                    "dor": [
                        {
                            "criterion": "Blocking check",
                            "validation_type": "automated",
                            "validation_command": "exit 1"
                        }
                    ]
                }
            ]
        }
        
        criteria_file = temp_plan_dir / "acceptance-criteria.yaml"
        with open(criteria_file, 'w') as f:
            yaml.dump(blocking_criteria, f)
        
        mock_db = Mock()
        orchestrator = PlanningOrchestratorV5(
            config_path="cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml",
            state_db=mock_db
        )
        
        orchestrator.acceptance_validator = AcceptanceCriteriaValidator(
            plan_root=temp_plan_dir,
            logger=orchestrator.logger
        )
        
        # Execute - should raise before calling base
        with pytest.raises(PhaseNotReadyError):
            orchestrator.execute_phase(0, {'name': 'Test Phase'})
        
        # Base execute should NOT be called
        mock_base_execute.assert_not_called()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
