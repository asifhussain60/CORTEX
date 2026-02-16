"""
Tests for AutonomousWorkflowExecutor bridge.

Phase 100 Stage 2: Bridges WorkflowComposer → AutonomousExecutor

Test Coverage:
- Workflow → Plan conversion
- Knowledge context injection
- AutonomousExecutor integration
- ProgressTracker real-time updates
- Convergence gate handling
- Epilogue auto-injection
- Error recovery + checkpointing
- End-to-end autonomous execution

Author: Asif Hussain
"""

import pytest
from typing import Dict, Any, List
from unittest.mock import Mock, patch, MagicMock, call
from dataclasses import dataclass

# AC_START: AC-PHASE100-003
# Description: AutonomousWorkflowExecutor bridge


@dataclass
class MockResolvedWorkflow:
    """Mock workflow for testing."""
    id: str
    name: str
    steps: List[Dict[str, Any]]
    knowledge_context: Dict[str, Any]


@dataclass
class MockCrystallizedContext:
    """Mock crystallized context."""
    knowledge: Dict[str, Any]
    metadata: Dict[str, Any]


class TestWorkflowToPlanConversion:
    """Test workflow → Plan conversion logic."""

    def test_workflow_to_plan_conversion_success(self):
        """Should convert workflow steps to Plan stages."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        workflow = MockResolvedWorkflow(
            id="test-workflow",
            name="Test Workflow",
            steps=[
                {"id": "step1", "action": "write_test", "convergence_gate": {}},
                {"id": "step2", "action": "implement_code", "convergence_gate": {}},
            ],
            knowledge_context={"test_framework": "pytest"},
        )
        knowledge_context = MockCrystallizedContext(
            knowledge={"test_framework": "pytest"},
            metadata={"mode": "ARCHITECT"},
        )

        plan = executor._convert_workflow_to_plan(workflow, knowledge_context)

        assert plan is not None
        assert len(plan.stages) == 2
        assert plan.stages[0]["step_id"] == "step1"
        assert plan.stages[1]["step_id"] == "step2"

    def test_workflow_to_plan_with_convergence_gates(self):
        """Should preserve convergence gate config in Plan stages."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        workflow = MockResolvedWorkflow(
            id="test-workflow",
            name="Test Workflow",
            steps=[
                {
                    "id": "step1",
                    "action": "test",
                    "convergence_gate": {
                        "max_cycles": 5,
                        "success_criteria": {"tests_pass": True},
                    },
                }
            ],
            knowledge_context={},
        )
        knowledge_context = MockCrystallizedContext(
            knowledge={}, metadata={}
        )

        plan = executor._convert_workflow_to_plan(workflow, knowledge_context)

        assert plan.stages[0]["convergence_gate"]["max_cycles"] == 5
        assert plan.stages[0]["convergence_gate"]["success_criteria"]["tests_pass"]


class TestKnowledgeContextInjection:
    """Test knowledge context injection into steps."""

    def test_knowledge_injection_per_step(self):
        """Should inject knowledge context into each step execution."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        step = {
            "id": "step1",
            "action": "write_test",
            "template": "Use {{test_framework}} for testing",
        }
        knowledge_context = MockCrystallizedContext(
            knowledge={"test_framework": "pytest"},
            metadata={},
        )

        injected = executor._inject_knowledge_into_step(step, knowledge_context)

        assert "{{test_framework}}" not in injected["template"]
        assert "pytest" in injected["template"]


class TestAutonomousExecutorIntegration:
    """Test AutonomousExecutor integration."""

    @patch("cortex.execution.autonomous_executor.AutonomousExecutor")
    def test_autonomous_executor_delegation(self, mock_executor_class):
        """Should delegate execution to AutonomousExecutor."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        mock_executor = MagicMock()
        mock_executor.execute_plan.return_value = {"status": "COMPLETED"}
        mock_executor_class.return_value = mock_executor

        executor = AutonomousWorkflowExecutor()
        workflow = MockResolvedWorkflow(
            id="test-workflow",
            name="Test Workflow",
            steps=[{"id": "step1", "action": "test", "convergence_gate": {}}],
            knowledge_context={},
        )
        knowledge_context = MockCrystallizedContext(knowledge={}, metadata={})

        result = executor.execute_workflow_autonomously(workflow, knowledge_context)

        assert result["status"] == "COMPLETED"
        mock_executor.execute_plan.assert_called_once()
        call_args = mock_executor.execute_plan.call_args
        assert call_args[1]["silent"] is True  # Silent execution


class TestProgressTrackerIntegration:
    """Test ProgressTracker real-time updates."""

    @patch("cortex.execution.progress_tracker.ProgressTracker")
    def test_progress_tracker_updates(self, mock_tracker_class):
        """Should update ProgressTracker in real-time."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        executor = AutonomousWorkflowExecutor()
        executor._progress_tracker = mock_tracker  # Set directly
        executor._update_progress("step1", "RUNNING", 1, 5)

        mock_tracker.update_step.assert_called_once_with(
            step_id="step1",
            state="RUNNING",
            cycle=1,
            max_cycles=5,
        )


class TestConvergenceGateHandling:
    """Test convergence gate retry loops."""

    def test_convergence_gate_retry_loop(self):
        """Should handle retry loops for non-converged steps."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        step = {
            "id": "step1",
            "action": "fix_issue",
            "convergence_gate": {
                "max_cycles": 3,
                "success_criteria": {"issue_resolved": True},
            },
        }

        # Simulate convergence on 2nd attempt
        convergence_results = [False, True]
        cycle_count = executor._execute_with_convergence_gate(
            step, lambda: convergence_results.pop(0)
        )

        assert cycle_count == 2  # Converged on 2nd cycle


class TestEpilogueAutoInjection:
    """Test auto-injection of workflow epilogues."""

    def test_post_phase_dedup_epilogue_injection(self):
        """Should auto-inject PostPhaseDeduplicationReview epilogue."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        workflow = MockResolvedWorkflow(
            id="test-workflow",
            name="Test Workflow",
            steps=[{"id": "step1", "action": "test", "convergence_gate": {}}],
            knowledge_context={},
        )
        knowledge_context = MockCrystallizedContext(knowledge={}, metadata={})

        plan = executor._convert_workflow_to_plan(workflow, knowledge_context)
        epilogues = executor._inject_epilogues(plan)

        assert any(e["step_id"] == "review/post-phase-dedup" for e in epilogues)

    def test_holistic_refactor_epilogue_injection(self):
        """Should auto-inject HolisticRefactoringSweep epilogue."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        executor = AutonomousWorkflowExecutor()
        workflow = MockResolvedWorkflow(
            id="test-workflow",
            name="Test Workflow",
            steps=[{"id": "step1", "action": "test", "convergence_gate": {}}],
            knowledge_context={},
        )
        knowledge_context = MockCrystallizedContext(knowledge={}, metadata={})

        plan = executor._convert_workflow_to_plan(workflow, knowledge_context)
        epilogues = executor._inject_epilogues(plan)

        assert any(e["step_id"] == "refactor/holistic-sweep" for e in epilogues)


class TestEndToEndAutonomousExecution:
    """Test complete autonomous execution (zero user prompts)."""

    @patch("cortex.execution.progress_tracker.ProgressTracker")
    @patch("cortex.execution.autonomous_executor.AutonomousExecutor")
    def test_end_to_end_execution_no_prompts(
        self, mock_executor_class, mock_tracker_class
    ):
        """Should execute workflow autonomously without user prompts."""
        from cortex.orchestrators.workflow.autonomous_workflow_executor import (
            AutonomousWorkflowExecutor,
        )

        mock_executor = MagicMock()
        mock_executor.execute_plan.return_value = {"status": "COMPLETED"}
        mock_executor_class.return_value = mock_executor

        mock_tracker = MagicMock()
        mock_tracker_class.return_value = mock_tracker

        executor = AutonomousWorkflowExecutor()
        workflow = MockResolvedWorkflow(
            id="test-workflow",
            name="Test Workflow",
            steps=[
                {"id": "step1", "action": "test", "convergence_gate": {}},
                {"id": "step2", "action": "implement", "convergence_gate": {}},
            ],
            knowledge_context={},
        )
        knowledge_context = MockCrystallizedContext(knowledge={}, metadata={})

        result = executor.execute_workflow_autonomously(
            workflow, knowledge_context, silent=True
        )

        assert result["status"] == "COMPLETED"
        # Verify silent=True passed to AutonomousExecutor
        call_args = mock_executor.execute_plan.call_args
        assert call_args[1]["silent"] is True


# AC_COMPLETE: AC-PHASE100-003 ✅ 8/8 tests written (RED phase)
