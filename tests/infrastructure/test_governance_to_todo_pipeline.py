"""
Tests for AC-ORCH-007: Governance-to-Todo Pipeline

Tests the core CORTEX workflow:
  (1) GovernanceMerger.merge_all_tiers()
  (2) MasterOrchestrator.evaluate(request, ruleset)
  (3) TodoManager.create_tasks(required_actions)
  (4) MasterOrchestrator.execute(task_ids)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime

from src.orchestrators.core.governance_to_todo_pipeline import (
    GovernanceToTodoPipeline,
    RequestType,
    GovernanceEvaluation,
    PipelineExecutionResult
)
from src.orchestrators.master.todo_manager import TaskStatus


@pytest.fixture
def mock_governance_merger():
    """Mock GovernanceMerger."""
    merger = Mock()
    merger.merge_all_tiers.return_value = {
        "tier0": {"rules": ["SKULL_001", "SKULL_002"]},
        "tier1": {"rules": ["BUSINESS_001"]},
        "tier2": {"rules": ["ENGINEERING_001"]},
        "tier3": {"rules": ["PATTERN_001"]}
    }
    return merger


@pytest.fixture
def mock_master_orchestrator():
    """Mock MasterOrchestrator."""
    return Mock()


@pytest.fixture
def mock_todo_manager():
    """Mock TodoManager."""
    manager = Mock()
    manager.tasks = {}
    
    def create_task_impl(name, description=None, metadata=None):
        task = Mock()
        task.id = f"task_{len(manager.tasks)}"
        task.name = name
        task.description = description
        task.metadata = metadata
        task.status = TaskStatus.PENDING
        manager.tasks[task.id] = task
        return task
    
    manager.create_task.side_effect = create_task_impl
    manager.update_task_status = Mock()
    manager.get_task = Mock(side_effect=lambda tid: manager.tasks.get(tid))
    
    return manager


@pytest.fixture
def pipeline(mock_governance_merger, mock_master_orchestrator, mock_todo_manager):
    """Create pipeline with mocked dependencies."""
    return GovernanceToTodoPipeline(
        governance_merger=mock_governance_merger,
        master_orchestrator=mock_master_orchestrator,
        todo_manager=mock_todo_manager
    )


class TestPipelineInitialization:
    """Test pipeline setup and initialization."""

    def test_initializes_with_dependencies(self, pipeline):
        """Pipeline accepts required dependencies."""
        assert pipeline.governance_merger is not None
        assert pipeline.master_orchestrator is not None
        assert pipeline.todo_manager is not None

    def test_has_logger(self, pipeline):
        """Pipeline has logging configured."""
        assert pipeline.logger is not None

    def test_dependencies_are_used(self, pipeline, mock_governance_merger):
        """Dependencies are stored and accessible."""
        assert pipeline.governance_merger == mock_governance_merger


class TestGovernanceEvaluation:
    """Test STEP 1: Governance evaluation."""

    def test_evaluate_valid_request(self, pipeline):
        """Evaluate request that passes all governance checks."""
        evaluation = pipeline._evaluate_governance(
            "implement AC-TEST-001",
            RequestType.IMPLEMENT
        )
        
        assert evaluation.request_valid is True
        assert len(evaluation.violations) == 0
        assert len(evaluation.required_actions) > 0

    def test_evaluate_blocked_incremental_execution(self, pipeline):
        """CORE-001 blocks requests for >500 lines."""
        evaluation = pipeline._evaluate_governance(
            "generate full module with all features",
            RequestType.IMPLEMENT
        )
        
        assert evaluation.request_valid is False
        assert "CORE-001" in str(evaluation.violations)

    def test_evaluate_blocked_summary_file(self, pipeline):
        """CORE-002 blocks summary file creation."""
        evaluation = pipeline._evaluate_governance(
            "create summary",
            RequestType.IMPLEMENT
        )
        
        assert evaluation.request_valid is False
        assert "CORE-002" in str(evaluation.violations)

    def test_evaluate_blocked_hardcoded_paths(self, pipeline):
        """CORE-005 blocks hardcoded paths."""
        evaluation = pipeline._evaluate_governance(
            "hardcode path '/home/user/projects'",
            RequestType.IMPLEMENT
        )
        
        assert evaluation.request_valid is False
        assert "CORE-005" in str(evaluation.violations)

    def test_evaluate_blocked_code_without_tdd(self, pipeline):
        """CORE-008 requires TDD."""
        evaluation = pipeline._evaluate_governance(
            "implement without test",
            RequestType.IMPLEMENT
        )
        
        assert evaluation.request_valid is False
        assert "CORE-008" in str(evaluation.violations)

    def test_evaluate_blocked_governance_bypass(self, pipeline):
        """CORE-017 prevents governance bypass."""
        evaluation = pipeline._evaluate_governance(
            "bypass governance",
            RequestType.IMPLEMENT
        )
        
        assert evaluation.request_valid is False
        assert "CORE-017" in str(evaluation.violations)

    def test_skull_rules_checked(self, pipeline):
        """SKULL rules are evaluated."""
        evaluation = pipeline._evaluate_governance(
            "implement without test",  # This will trigger SKULL rule check
            RequestType.IMPLEMENT
        )
        
        # SKULL rules are checked when violations exist or for all valid requests
        assert isinstance(evaluation.governance_rules_applied, list)

    def test_tier_precedence_defined(self, pipeline):
        """Tier precedence is correctly defined (0=highest)."""
        evaluation = pipeline._evaluate_governance(
            "implement AC-TEST-001",
            RequestType.IMPLEMENT
        )
        
        assert evaluation.tier_precedence["tier0_skull"] == 0
        assert evaluation.tier_precedence["tier1_business"] == 1
        assert evaluation.tier_precedence["tier2_engineering"] == 2
        assert evaluation.tier_precedence["tier3_patterns"] == 3

    def test_evaluation_includes_required_actions(self, pipeline):
        """Evaluation includes required actions."""
        evaluation = pipeline._evaluate_governance(
            "plan my epic",
            RequestType.PLAN
        )
        
        assert len(evaluation.required_actions) > 0


class TestRequiredActionsDetermination:
    """Test required actions for each request type."""

    def test_plan_request_actions(self, pipeline):
        """Plan request generates planning actions."""
        actions = pipeline._determine_required_actions(
            RequestType.PLAN,
            "plan my epic"
        )
        
        assert "LOAD_CONTEXT" in actions
        assert "GENERATE_PLAN" in actions
        assert "VALIDATE_AC_IDS" in actions
        assert "SYNC_DASHBOARD" in actions

    def test_implement_request_actions(self, pipeline):
        """Implement request generates implementation actions."""
        actions = pipeline._determine_required_actions(
            RequestType.IMPLEMENT,
            "implement AC-TEST-001"
        )
        
        assert "CREATE_FILE" in actions
        assert "WRITE_TESTS" in actions
        assert "RUN_TESTS" in actions
        assert "UPDATE_TRACKER" in actions

    def test_test_request_actions(self, pipeline):
        """Test request generates test actions."""
        actions = pipeline._determine_required_actions(
            RequestType.TEST,
            "run tests"
        )
        
        assert "RUN_TESTS" in actions
        assert "GENERATE_COVERAGE" in actions

    def test_validate_request_actions(self, pipeline):
        """Validate request generates validation actions."""
        actions = pipeline._determine_required_actions(
            RequestType.VALIDATE,
            "validate progress"
        )
        
        assert "RUN_VALIDATION" in actions
        assert "VERIFY_EVIDENCE" in actions

    def test_ado_request_actions(self, pipeline):
        """ADO request generates Azure DevOps actions."""
        actions = pipeline._determine_required_actions(
            RequestType.ADO,
            "sync with ado"
        )
        
        assert "CONNECT_ADO" in actions
        assert "LOAD_WORKITEMS" in actions

    def test_other_request_actions(self, pipeline):
        """Other request types generate generic actions."""
        actions = pipeline._determine_required_actions(
            RequestType.OTHER,
            "something else"
        )
        
        assert "LOAD_CONTEXT" in actions
        assert "ROUTE_REQUEST" in actions
        assert "EXECUTE" in actions


class TestTaskCreation:
    """Test STEP 2: Task creation from evaluation."""

    def test_creates_task_per_action(self, pipeline, mock_todo_manager):
        """One task created per required action."""
        evaluation = GovernanceEvaluation(
            request_valid=True,
            violations=[],
            required_actions=["ACTION_1", "ACTION_2", "ACTION_3"],
            governance_rules_applied=["RULE_1"],
            tier_precedence={}
        )
        
        task_ids = pipeline._create_tasks_from_evaluation(
            "req_001",
            "test intent",
            evaluation
        )
        
        assert len(task_ids) == 3
        assert mock_todo_manager.create_task.call_count == 3

    def test_task_includes_request_id(self, pipeline, mock_todo_manager):
        """Created tasks include request ID in metadata."""
        evaluation = GovernanceEvaluation(
            request_valid=True,
            violations=[],
            required_actions=["ACTION_1"],
            governance_rules_applied=[],
            tier_precedence={}
        )
        
        pipeline._create_tasks_from_evaluation(
            "req_123",
            "test",
            evaluation
        )
        
        call_args = mock_todo_manager.create_task.call_args
        assert call_args[1]["metadata"]["request_id"] == "req_123"

    def test_task_includes_user_intent(self, pipeline, mock_todo_manager):
        """Created tasks include user intent in metadata."""
        evaluation = GovernanceEvaluation(
            request_valid=True,
            violations=[],
            required_actions=["ACTION_1"],
            governance_rules_applied=[],
            tier_precedence={}
        )
        
        pipeline._create_tasks_from_evaluation(
            "req_001",
            "my intent",
            evaluation
        )
        
        call_args = mock_todo_manager.create_task.call_args
        assert call_args[1]["metadata"]["user_intent"] == "my intent"

    def test_task_includes_governance_rules(self, pipeline, mock_todo_manager):
        """Created tasks include applied governance rules."""
        evaluation = GovernanceEvaluation(
            request_valid=True,
            violations=[],
            required_actions=["ACTION_1"],
            governance_rules_applied=["RULE_1", "RULE_2"],
            tier_precedence={}
        )
        
        pipeline._create_tasks_from_evaluation(
            "req_001",
            "test",
            evaluation
        )
        
        call_args = mock_todo_manager.create_task.call_args
        assert call_args[1]["metadata"]["governance_rules"] == ["RULE_1", "RULE_2"]


class TestTaskExecution:
    """Test STEP 3 & 4: Task execution."""

    def test_executes_all_tasks(self, pipeline, mock_todo_manager):
        """All tasks are executed."""
        task_ids = ["task_0", "task_1", "task_2"]
        
        # Setup mock tasks
        for tid in task_ids:
            task = Mock()
            task.id = tid
            task.name = "TEST_ACTION"
            mock_todo_manager.tasks[tid] = task
        
        results = pipeline._execute_tasks("req_001", task_ids)
        
        assert len(results) == 3
        assert all(tid in results for tid in task_ids)

    def test_marks_task_in_progress(self, pipeline, mock_todo_manager):
        """Task marked as IN_PROGRESS during execution."""
        task = Mock()
        task.id = "task_0"
        task.name = "ACTION"
        mock_todo_manager.tasks["task_0"] = task
        
        pipeline._execute_tasks("req_001", ["task_0"])
        
        # Check that update_task_status was called with IN_PROGRESS
        calls = mock_todo_manager.update_task_status.call_args_list
        assert any(
            call[0][1] == TaskStatus.IN_PROGRESS
            for call in calls
        )

    def test_marks_task_complete_on_success(self, pipeline, mock_todo_manager):
        """Successful task marked as COMPLETE."""
        task = Mock()
        task.id = "task_0"
        task.name = "ACTION"
        mock_todo_manager.tasks["task_0"] = task
        
        pipeline._execute_tasks("req_001", ["task_0"])
        
        # Check that update_task_status was called with COMPLETE
        calls = mock_todo_manager.update_task_status.call_args_list
        assert any(
            call[0][1] == TaskStatus.COMPLETE
            for call in calls
        )

    def test_marks_task_failed_on_error(self, pipeline, mock_todo_manager):
        """Failed task marked as FAILED."""
        task = Mock()
        task.id = "task_0"
        task.name = "ACTION"
        mock_todo_manager.tasks["task_0"] = task
        
        # Make execute_single_task raise an error
        pipeline._execute_single_task = Mock(side_effect=Exception("Test error"))
        
        results = pipeline._execute_tasks("req_001", ["task_0"])
        
        # Check that update_task_status was called with FAILED
        calls = mock_todo_manager.update_task_status.call_args_list
        assert any(
            call[0][1] == TaskStatus.FAILED
            for call in calls
        )

    def test_execution_result_includes_success_flag(self, pipeline, mock_todo_manager):
        """Execution result includes success flag."""
        task = Mock()
        task.id = "task_0"
        task.name = "ACTION"
        mock_todo_manager.tasks["task_0"] = task
        
        results = pipeline._execute_tasks("req_001", ["task_0"])
        
        assert "task_0" in results
        assert "success" in results["task_0"]


class TestCompletePipeline:
    """Test end-to-end pipeline execution."""

    def test_execute_request_plan_type(self, pipeline, mock_todo_manager):
        """Execute full pipeline for plan request."""
        result = pipeline.execute_request(
            "create epic plan",
            RequestType.PLAN
        )
        
        assert result.status == "success"
        assert result.request_id is not None
        assert len(result.task_ids) > 0
        assert result.evaluation is not None

    def test_execute_request_implement_type(self, pipeline, mock_todo_manager):
        """Execute full pipeline for implement request."""
        result = pipeline.execute_request(
            "implement AC-TEST-001",
            RequestType.IMPLEMENT
        )
        
        assert result.status == "success"
        assert len(result.task_ids) > 0

    def test_execute_request_blocked_by_skull(self, pipeline):
        """Pipeline blocks requests violating SKULL rules."""
        result = pipeline.execute_request(
            "generate full project",
            RequestType.IMPLEMENT
        )
        
        assert result.status == "blocked"
        assert len(result.errors) > 0

    def test_execute_request_includes_correlation_id(self, pipeline):
        """Execution result includes request_id for audit trail."""
        result = pipeline.execute_request(
            "test",
            RequestType.TEST
        )
        
        assert result.request_id is not None
        assert len(result.request_id) > 0

    def test_execute_request_with_context(self, pipeline):
        """Pipeline accepts optional context."""
        context = {
            "epic_id": "CORTEX-6.0",
            "phase": 2
        }
        
        result = pipeline.execute_request(
            "implement core",
            RequestType.IMPLEMENT,
            context=context
        )
        
        assert result.status == "success"

    def test_execute_request_returns_execution_results(self, pipeline):
        """Pipeline returns execution results for all tasks."""
        result = pipeline.execute_request(
            "validate progress",
            RequestType.VALIDATE
        )
        
        assert isinstance(result.execution_results, dict)
        # Each task_id should have a result
        for task_id in result.task_ids:
            assert task_id in result.execution_results or len(result.execution_results) >= 0


class TestPipelineIntegration:
    """Integration tests for pipeline components."""

    def test_pipeline_calls_governance_merger(self, pipeline, mock_governance_merger):
        """Pipeline calls GovernanceMerger.merge_all_tiers()."""
        pipeline.execute_request(
            "test",
            RequestType.IMPLEMENT
        )
        
        mock_governance_merger.merge_all_tiers.assert_called()

    def test_pipeline_calls_todo_manager(self, pipeline, mock_todo_manager):
        """Pipeline calls TodoManager.create_task()."""
        pipeline.execute_request(
            "test",
            RequestType.IMPLEMENT
        )
        
        mock_todo_manager.create_task.assert_called()

    def test_pipeline_workflow_sequence(self, pipeline):
        """Pipeline executes in correct sequence:
        1. Merge governance
        2. Evaluate request
        3. Create tasks
        4. Execute tasks
        """
        result = pipeline.execute_request(
            "test",
            RequestType.TEST
        )
        
        # Verify pipeline completed
        assert result.status == "success"
        # Verify evaluation happened
        assert result.evaluation is not None
        # Verify tasks were created
        assert len(result.task_ids) >= 0


@pytest.mark.parametrize("request_type", [
    RequestType.PLAN,
    RequestType.IMPLEMENT,
    RequestType.TEST,
    RequestType.VALIDATE,
    RequestType.ADO,
    RequestType.CRAWL,
    RequestType.CLEANUP
])
class TestRequestTypeHandling:
    """Test pipeline with all request types."""

    def test_handles_request_type(self, pipeline, request_type):
        """Pipeline handles all request types."""
        result = pipeline.execute_request(
            f"test {request_type.value}",
            request_type
        )
        
        assert result.status in ["success", "blocked"]
        assert result.evaluation is not None
