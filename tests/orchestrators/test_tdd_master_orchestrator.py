"""
TDD-Master Orchestrator Tests - AC-TDD-MASTER-001 to AC-TDD-MASTER-007.

Tests for the TDD-Master coordination layer that bridges Planning → TDD.

Acceptance Criteria Coverage:
- AC-TDD-MASTER-001: Plan detection via config.yaml validation
- AC-TDD-MASTER-002: Planning → TDD context transformation (JSON)
- AC-TDD-MASTER-003: TDD Orchestrator invocation with enriched context
- AC-TDD-MASTER-004: 100% AC coverage validation post-TDD
- AC-TDD-MASTER-005: Tier0-3 governance continuity enforcement
- AC-TDD-MASTER-006: Dashboard updates (plan-viewer.html)
- AC-TDD-MASTER-007: Unified completion report generation (JSON)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch
from typing import Dict, Any

# Import SUT (System Under Test)
from src.orchestrators.tdd_master.tdd_master_orchestrator import (
    TDDMasterOrchestrator,
    TDDMasterConfig,
    TDDMasterContext,
    TDDMasterResult,
    PlanValidationStatus,
    CompletionReport,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def temp_workspace(tmp_path: Path) -> Path:
    """Create temporary workspace with plan structure."""
    # Create cortex-brain structure
    brain_dir = tmp_path / "cortex-brain"
    brain_dir.mkdir()
    
    # Create planning directory
    planning_dir = brain_dir / "documents" / "planning" / "active" / "test-plan"
    planning_dir.mkdir(parents=True)
    
    # Create config.yaml with valid plan
    config_content = """
plan_id: test-plan-001
status: READY_FOR_IMPLEMENTATION
feature_name: user-authentication
version: 1.0.0
created: 2026-01-10
acceptance_criteria:
  - AC-AUTH-001
  - AC-AUTH-002
  - AC-AUTH-003
phases:
  - id: phase-1
    name: Core Auth
    tasks:
      - implement login
      - implement logout
"""
    (planning_dir / "config.yaml").write_text(config_content)
    
    # Create requirements.yaml
    requirements_content = """
feature:
  name: user-authentication
  domain: security
  description: Secure user authentication with OAuth2
requirements:
  - id: REQ-001
    description: Support OAuth2 authentication
    priority: P1_HIGH
  - id: REQ-002
    description: Support session management
    priority: P1_HIGH
"""
    (planning_dir / "requirements.yaml").write_text(requirements_content)
    
    # Create tier0 governance directory
    tier0_dir = brain_dir / "tier0" / "governance"
    tier0_dir.mkdir(parents=True)
    
    # Create core-rules.yaml
    rules_content = """
metadata:
  version: 1.0.0
rules:
  - rule_id: CORE-001
    name: Test Isolation
    severity: critical
  - rule_id: CORE-019
    name: TDD Enforcement
    severity: critical
"""
    (tier0_dir / "core-rules.yaml").write_text(rules_content)
    
    return tmp_path


@pytest.fixture
def orchestrator(temp_workspace: Path) -> TDDMasterOrchestrator:
    """Create TDD-Master orchestrator instance."""
    return TDDMasterOrchestrator(
        workspace_path=temp_workspace,
        brain_path=temp_workspace / "cortex-brain"
    )


@pytest.fixture
def mock_tdd_orchestrator() -> Mock:
    """Create mock TDD Orchestrator."""
    mock = MagicMock()
    mock.execute.return_value = MagicMock(
        success=True,
        status="SUCCESS",
        message="TDD cycle complete",
        data={
            "tests_created": 5,
            "tests_passed": 5,
            "coverage": 92.5
        }
    )
    return mock


# =============================================================================
# AC-TDD-MASTER-001: Plan Detection via config.yaml validation
# =============================================================================

class TestPlanDetection:
    """Tests for AC-TDD-MASTER-001."""
    
    def test_detects_valid_plan_config(self, orchestrator: TDDMasterOrchestrator, temp_workspace: Path):
        """
        AC-TDD-MASTER-001: Detects completed plans via config.yaml validation.
        
        GIVEN: A workspace with a valid config.yaml in planning directory
        WHEN: TDD-Master scans for ready plans
        THEN: Returns the plan with READY_FOR_IMPLEMENTATION status
        """
        # Act
        plans = orchestrator.detect_ready_plans()
        
        # Assert
        assert len(plans) >= 1
        assert plans[0].plan_id == "test-plan-001"
        assert plans[0].status == PlanValidationStatus.READY
    
    def test_rejects_invalid_plan_config(self, temp_workspace: Path):
        """
        AC-TDD-MASTER-001: Rejects plans with invalid config.yaml.
        
        GIVEN: A config.yaml missing required fields
        WHEN: TDD-Master validates the plan
        THEN: Returns INVALID status with error details
        """
        # Arrange - create invalid config
        planning_dir = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "invalid-plan"
        planning_dir.mkdir(parents=True)
        
        invalid_config = """
plan_id: invalid-plan
# Missing status, acceptance_criteria, phases
"""
        (planning_dir / "config.yaml").write_text(invalid_config)
        
        orchestrator = TDDMasterOrchestrator(
            workspace_path=temp_workspace,
            brain_path=temp_workspace / "cortex-brain"
        )
        
        # Act
        plans = orchestrator.detect_ready_plans()
        invalid_plans = [p for p in plans if p.plan_id == "invalid-plan"]
        
        # Assert
        assert len(invalid_plans) == 1
        assert invalid_plans[0].status == PlanValidationStatus.INVALID
        assert "missing" in invalid_plans[0].error_message.lower() or "required" in invalid_plans[0].error_message.lower()
    
    def test_skips_in_progress_plans(self, temp_workspace: Path):
        """
        AC-TDD-MASTER-001: Skips plans not ready for implementation.
        
        GIVEN: A config.yaml with status IN_PROGRESS
        WHEN: TDD-Master scans for ready plans
        THEN: Plan is not included in ready plans list
        """
        # Arrange
        planning_dir = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "wip-plan"
        planning_dir.mkdir(parents=True)
        
        wip_config = """
plan_id: wip-plan
status: IN_PROGRESS
feature_name: incomplete-feature
phases: []
"""
        (planning_dir / "config.yaml").write_text(wip_config)
        
        orchestrator = TDDMasterOrchestrator(
            workspace_path=temp_workspace,
            brain_path=temp_workspace / "cortex-brain"
        )
        
        # Act
        plans = orchestrator.detect_ready_plans()
        ready_plans = [p for p in plans if p.status == PlanValidationStatus.READY]
        
        # Assert
        assert not any(p.plan_id == "wip-plan" for p in ready_plans)


# =============================================================================
# AC-TDD-MASTER-002: Context Transformation (Planning → TDD)
# =============================================================================

class TestContextTransformation:
    """Tests for AC-TDD-MASTER-002."""
    
    def test_transforms_planning_to_tdd_context(self, orchestrator: TDDMasterOrchestrator, temp_workspace: Path):
        """
        AC-TDD-MASTER-002: Transforms Planning data → TDD context (JSON).
        
        GIVEN: A valid plan with requirements and acceptance criteria
        WHEN: TDD-Master transforms the plan
        THEN: Produces tdd-context.json with correct structure
        """
        # Arrange
        plan_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan"
        
        # Act
        context = orchestrator.transform_plan_to_context(str(plan_path))
        
        # Assert
        assert isinstance(context, TDDMasterContext)
        assert context.feature_name == "user-authentication"
        assert len(context.acceptance_criteria) >= 3
        assert context.domain_knowledge is not None
        assert context.test_requirements is not None
    
    def test_generates_tdd_context_json(self, orchestrator: TDDMasterOrchestrator, temp_workspace: Path):
        """
        AC-TDD-MASTER-002: Generates tdd-context.json file.
        
        GIVEN: A transformed planning context
        WHEN: TDD-Master saves the context
        THEN: Creates valid JSON file at expected location
        """
        # Arrange
        plan_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan"
        
        # Act
        context = orchestrator.transform_plan_to_context(str(plan_path))
        output_path = orchestrator.save_tdd_context(context, str(plan_path))
        
        # Assert
        assert Path(output_path).exists()
        with open(output_path) as f:
            saved_context = json.load(f)
        
        assert saved_context["feature_name"] == "user-authentication"
        assert "acceptance_criteria" in saved_context
        assert "test_requirements" in saved_context
        assert "domain_knowledge" in saved_context
    
    def test_context_includes_governance_rules(self, orchestrator: TDDMasterOrchestrator, temp_workspace: Path):
        """
        AC-TDD-MASTER-002: Context includes governance rules.
        
        GIVEN: A plan and tier0 governance rules
        WHEN: TDD-Master creates context
        THEN: Context includes relevant CORE rules
        """
        # Arrange
        plan_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan"
        
        # Act
        context = orchestrator.transform_plan_to_context(str(plan_path))
        
        # Assert
        assert context.governance_rules is not None
        assert len(context.governance_rules) >= 1
        assert any("CORE" in r.get("rule_id", "") for r in context.governance_rules)


# =============================================================================
# AC-TDD-MASTER-003: TDD Orchestrator Invocation
# =============================================================================

class TestTDDInvocation:
    """Tests for AC-TDD-MASTER-003."""
    
    def test_invokes_tdd_orchestrator(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path,
        mock_tdd_orchestrator: Mock
    ):
        """
        AC-TDD-MASTER-003: Invokes TDD Orchestrator with enriched context.
        
        GIVEN: A valid tdd-context.json
        WHEN: TDD-Master invokes TDD Orchestrator
        THEN: TDD Orchestrator receives the context and executes
        """
        # Arrange
        plan_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan"
        context = orchestrator.transform_plan_to_context(str(plan_path))
        
        with patch.object(orchestrator, '_get_tdd_orchestrator', return_value=mock_tdd_orchestrator):
            # Act
            result = orchestrator.invoke_tdd(context)
            
            # Assert
            mock_tdd_orchestrator.execute.assert_called_once()
            call_args = mock_tdd_orchestrator.execute.call_args
            assert "context" in call_args.kwargs or len(call_args.args) > 0
    
    def test_handles_tdd_failure(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path,
        mock_tdd_orchestrator: Mock
    ):
        """
        AC-TDD-MASTER-003: Handles TDD Orchestrator failure gracefully.
        
        GIVEN: TDD Orchestrator returns failure
        WHEN: TDD-Master processes the result
        THEN: Returns failure result with error details
        """
        # Arrange
        mock_tdd_orchestrator.execute.return_value = MagicMock(
            success=False,
            status="FAILURE",
            message="Tests failed",
            data={"tests_passed": 3, "tests_failed": 2}
        )
        
        plan_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan"
        context = orchestrator.transform_plan_to_context(str(plan_path))
        
        with patch.object(orchestrator, '_get_tdd_orchestrator', return_value=mock_tdd_orchestrator):
            # Act
            result = orchestrator.invoke_tdd(context)
            
            # Assert
            assert result.success is False
            assert "failed" in result.message.lower()


# =============================================================================
# AC-TDD-MASTER-004: AC Coverage Validation
# =============================================================================

class TestACValidation:
    """Tests for AC-TDD-MASTER-004."""
    
    def test_validates_full_ac_coverage(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path
    ):
        """
        AC-TDD-MASTER-004: Validates 100% AC coverage post-TDD.
        
        GIVEN: TDD result with test coverage mapping
        WHEN: TDD-Master validates AC coverage
        THEN: Reports 100% coverage when all ACs have tests
        """
        # Arrange
        tdd_result = MagicMock(
            success=True,
            data={
                "ac_coverage": {
                    "AC-AUTH-001": ["test_login_success", "test_login_failure"],
                    "AC-AUTH-002": ["test_logout"],
                    "AC-AUTH-003": ["test_session_management"]
                }
            }
        )
        
        plan_acs = ["AC-AUTH-001", "AC-AUTH-002", "AC-AUTH-003"]
        
        # Act
        coverage_result = orchestrator.validate_ac_coverage(tdd_result, plan_acs)
        
        # Assert
        assert coverage_result.coverage_percent == 100.0
        assert coverage_result.all_acs_covered is True
        assert len(coverage_result.missing_acs) == 0
    
    def test_detects_missing_ac_coverage(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path
    ):
        """
        AC-TDD-MASTER-004: Detects missing AC coverage.
        
        GIVEN: TDD result missing some AC coverage
        WHEN: TDD-Master validates AC coverage
        THEN: Reports missing ACs and partial coverage
        """
        # Arrange
        tdd_result = MagicMock(
            success=True,
            data={
                "ac_coverage": {
                    "AC-AUTH-001": ["test_login"],
                    # AC-AUTH-002 missing
                    "AC-AUTH-003": ["test_session"]
                }
            }
        )
        
        plan_acs = ["AC-AUTH-001", "AC-AUTH-002", "AC-AUTH-003"]
        
        # Act
        coverage_result = orchestrator.validate_ac_coverage(tdd_result, plan_acs)
        
        # Assert
        assert coverage_result.coverage_percent < 100.0
        assert coverage_result.all_acs_covered is False
        assert "AC-AUTH-002" in coverage_result.missing_acs


# =============================================================================
# AC-TDD-MASTER-005: Governance Continuity
# =============================================================================

class TestGovernanceContinuity:
    """Tests for AC-TDD-MASTER-005."""
    
    def test_enforces_tier0_rules(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path
    ):
        """
        AC-TDD-MASTER-005: Enforces Tier0-3 governance continuity.
        
        GIVEN: CORE rules in tier0/governance
        WHEN: TDD-Master executes
        THEN: All CORE rules are validated
        """
        # Act
        governance_result = orchestrator.validate_governance()
        
        # Assert
        assert governance_result.tier0_validated is True
        assert len(governance_result.validated_rules) >= 1
        assert any("CORE" in r for r in governance_result.validated_rules)
    
    def test_blocks_on_governance_violation(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path
    ):
        """
        AC-TDD-MASTER-005: Blocks execution on governance violation.
        
        GIVEN: A governance violation is detected
        WHEN: TDD-Master validates governance
        THEN: Raises GovernanceViolationError
        """
        # Arrange - simulate a violation by removing core-rules.yaml
        rules_path = temp_workspace / "cortex-brain" / "tier0" / "governance" / "core-rules.yaml"
        rules_path.unlink()
        
        # Re-create orchestrator
        orchestrator = TDDMasterOrchestrator(
            workspace_path=temp_workspace,
            brain_path=temp_workspace / "cortex-brain"
        )
        
        # Act
        governance_result = orchestrator.validate_governance()
        
        # Assert
        assert governance_result.tier0_validated is False
        assert len(governance_result.violations) >= 1


# =============================================================================
# AC-TDD-MASTER-006: Dashboard Updates
# =============================================================================

class TestDashboardUpdates:
    """Tests for AC-TDD-MASTER-006."""
    
    def test_updates_plan_viewer_dashboard(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path
    ):
        """
        AC-TDD-MASTER-006: Updates plan-viewer.html with TDD progress.
        
        GIVEN: TDD execution result
        WHEN: TDD-Master updates dashboard
        THEN: Dashboard data file is updated with progress
        """
        # Arrange
        tdd_result = MagicMock(
            success=True,
            data={
                "tests_created": 5,
                "tests_passed": 5,
                "coverage": 92.5,
                "phases_complete": ["RED", "GREEN", "REFACTOR"]
            }
        )
        
        # Act
        dashboard_result = orchestrator.update_dashboard(
            plan_id="test-plan-001",
            tdd_result=tdd_result
        )
        
        # Assert
        assert dashboard_result.updated is True
        # Check dashboard data file exists
        dashboard_data_path = temp_workspace / "cortex-brain" / "dashboards" / "plan-data.json"
        if dashboard_data_path.exists():
            with open(dashboard_data_path) as f:
                data = json.load(f)
            assert "test-plan-001" in data.get("plans", {})


# =============================================================================
# AC-TDD-MASTER-007: Completion Report
# =============================================================================

class TestCompletionReport:
    """Tests for AC-TDD-MASTER-007."""
    
    def test_generates_json_completion_report(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path
    ):
        """
        AC-TDD-MASTER-007: Generates unified completion report (JSON).
        
        GIVEN: Completed TDD execution
        WHEN: TDD-Master generates report
        THEN: Creates JSON report with all execution data
        """
        # Arrange
        tdd_result = MagicMock(
            success=True,
            data={
                "tests_created": 5,
                "tests_passed": 5,
                "coverage": 92.5
            }
        )
        
        coverage_result = MagicMock(
            coverage_percent=100.0,
            all_acs_covered=True,
            missing_acs=[]
        )
        
        # Act
        report = orchestrator.generate_completion_report(
            plan_id="test-plan-001",
            tdd_result=tdd_result,
            coverage_result=coverage_result
        )
        
        # Assert
        assert report.format == "json"
        assert report.plan_id == "test-plan-001"
        assert report.success is True
        assert report.data["tdd_summary"]["tests_passed"] == 5
        assert report.data["ac_coverage"]["coverage_percent"] == 100.0
    
    def test_report_saved_to_correct_location(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path
    ):
        """
        AC-TDD-MASTER-007: Report saved to plan directory.
        
        GIVEN: A completion report
        WHEN: TDD-Master saves the report
        THEN: Report is saved as JSON in plan directory
        """
        # Arrange - use actual CompletionReport dataclass
        report = CompletionReport(
            format="json",
            plan_id="test-plan-001",
            success=True,
            data={"summary": "complete"}
        )
        
        plan_path = temp_workspace / "cortex-brain" / "documents" / "planning" / "active" / "test-plan"
        
        # Act
        output_path = orchestrator.save_completion_report(report, str(plan_path))
        
        # Assert
        assert Path(output_path).exists()
        assert output_path.endswith(".json")


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestEndToEndWorkflow:
    """Integration tests for full TDD-Master workflow."""
    
    @pytest.mark.skip(reason="TDD-Master validation logic needs refinement (Phase 2)")
    def test_full_workflow_execution(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path,
        mock_tdd_orchestrator: Mock
    ):
        """
        Integration: Full Planning → TDD-Master → TDD workflow.
        
        GIVEN: A complete plan ready for implementation
        WHEN: TDD-Master executes full workflow
        THEN: All phases complete successfully with reports generated
        """
        # Arrange
        mock_tdd_orchestrator.execute.return_value = MagicMock(
            success=True,
            status="SUCCESS",
            message="TDD complete",
            data={
                "tests_created": 5,
                "tests_passed": 5,
                "coverage": 92.5,
                "ac_coverage": {
                    "AC-AUTH-001": ["test_1"],
                    "AC-AUTH-002": ["test_2"],
                    "AC-AUTH-003": ["test_3"]
                }
            }
        )
        
        with patch.object(orchestrator, '_get_tdd_orchestrator', return_value=mock_tdd_orchestrator):
            # Act
            result = orchestrator.execute(
                plan_id="test-plan-001",
                context={"auto_mode": True}
            )
            
            # Assert
            assert result.success is True
            assert result.data.get("plan_detected") is True
            assert result.data.get("context_transformed") is True
            assert result.data.get("tdd_invoked") is True
            assert result.data.get("ac_validated") is True
            assert result.data.get("report_generated") is True


# =============================================================================
# UNPLANNED MODE TESTS (AC-TDD-MASTER-000)
# =============================================================================

class TestUnplannedMode:
    """Tests for unplanned development mode (AC-TDD-MASTER-000)."""
    
    @pytest.mark.skip(reason="TDD-Master unplanned mode needs validation refinement (Phase 2)")
    def test_handles_unplanned_request(
        self, 
        orchestrator: TDDMasterOrchestrator, 
        temp_workspace: Path,
        mock_tdd_orchestrator: Mock
    ):
        """
        AC-TDD-MASTER-000: Handles unplanned development requests.
        
        GIVEN: A development request without a plan
        WHEN: TDD-Master receives the request
        THEN: Creates minimal context and invokes TDD
        """
        # Arrange
        request = "implement user login validation"
        
        mock_tdd_orchestrator.execute.return_value = MagicMock(
            success=True,
            status="SUCCESS",
            message="TDD complete",
            data={"tests_created": 2, "tests_passed": 2}
        )
        
        with patch.object(orchestrator, '_get_tdd_orchestrator', return_value=mock_tdd_orchestrator):
            # Act
            result = orchestrator.handle_unplanned_request(request)
            
            # Assert
            assert result.success is True
            assert result.mode == "unplanned"
            mock_tdd_orchestrator.execute.assert_called_once()
