"""
Tests for AC-TODO-002: Task Creation from Governance Evaluation

Tests the creation of actionable tasks from governance evaluation results.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from datetime import datetime

from src.orchestrators.master.todo_manager import (
    TodoManager,
    TaskStatus,
    TaskPriority,
    GovernanceEvaluationResult,
    Task
)


@pytest.fixture
def todo_manager():
    """Create fresh TodoManager instance."""
    return TodoManager()


@pytest.fixture
def mock_governance_evaluation():
    """Create mock governance evaluation result."""
    return GovernanceEvaluationResult(
        request_valid=True,
        violations=[],
        required_actions=[
            "LOAD_CONTEXT",
            "CREATE_FILE",
            "RUN_TESTS",
            "UPDATE_TRACKER"
        ],
        governance_rules_applied=["SKULL_RULES", "ENGINEERING_STANDARDS"],
        tier_precedence={
            "tier0": 0,
            "tier1": 1,
            "tier2": 2,
            "tier3": 3
        }
    )


class TestTaskCreation:
    """Test basic task creation functionality."""

    def test_create_task_basic(self, todo_manager):
        """Create basic task with name."""
        task = todo_manager.create_task("Test Action")
        
        assert task.id is not None
        assert task.name == "Test Action"
        assert task.status == TaskStatus.PENDING
        assert task.priority == TaskPriority.MEDIUM

    def test_create_task_with_description(self, todo_manager):
        """Create task with description."""
        task = todo_manager.create_task(
            "Test Action",
            description="Test description"
        )
        
        assert task.description == "Test description"

    def test_create_task_with_priority(self, todo_manager):
        """Create task with specific priority."""
        task = todo_manager.create_task(
            "Test Action",
            priority=TaskPriority.CRITICAL
        )
        
        assert task.priority == TaskPriority.CRITICAL

    def test_create_task_with_metadata(self, todo_manager):
        """Create task with metadata."""
        metadata = {"key": "value", "count": 42}
        task = todo_manager.create_task(
            "Test Action",
            metadata=metadata
        )
        
        assert task.metadata == metadata

    def test_create_task_with_dependencies(self, todo_manager):
        """Create task with dependencies."""
        deps = ["task_1", "task_2"]
        task = todo_manager.create_task(
            "Test Action",
            dependencies=deps
        )
        
        assert task.dependencies == deps

    def test_create_task_with_ac_id(self, todo_manager):
        """Create task linked to AC-ID."""
        task = todo_manager.create_task(
            "Test Action",
            ac_id="AC-TODO-002"
        )
        
        assert task.ac_id == "AC-TODO-002"

    def test_task_has_timestamps(self, todo_manager):
        """Created task has creation and update timestamps."""
        task = todo_manager.create_task("Test Action")
        
        assert task.created_at is not None
        assert task.updated_at is not None
        assert isinstance(task.created_at, datetime)
        assert isinstance(task.updated_at, datetime)

    def test_task_id_is_unique(self, todo_manager):
        """Each task gets a unique ID."""
        task1 = todo_manager.create_task("Action 1")
        task2 = todo_manager.create_task("Action 2")
        
        assert task1.id != task2.id


class TestGovernanceTaskCreation:
    """Test AC-TODO-002: Task creation from governance evaluation."""

    def test_creates_task_per_required_action(
        self,
        todo_manager,
        mock_governance_evaluation
    ):
        """One task created per required action."""
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            mock_governance_evaluation,
            "req_123",
            "test intent"
        )
        
        assert len(tasks) == len(mock_governance_evaluation.required_actions)

    def test_action_names_become_task_names(
        self,
        todo_manager,
        mock_governance_evaluation
    ):
        """Action names are used as task names."""
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            mock_governance_evaluation,
            "req_123",
            "test intent"
        )
        
        task_names = [t.name for t in tasks]
        for action in mock_governance_evaluation.required_actions:
            assert action in task_names

    def test_governance_evaluation_with_violations(self, todo_manager):
        """Violations create violation-address tasks."""
        evaluation = GovernanceEvaluationResult(
            request_valid=False,
            violations=[
                "CORE-001: Cannot generate >500 lines",
                "CORE-002: Summary file creation blocked"
            ],
            required_actions=["LOAD_CONTEXT"],
            governance_rules_applied=["SKULL_RULES"],
            tier_precedence={}
        )
        
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            evaluation,
            "req_123",
            "test intent"
        )
        
        # Should have 1 action task + 2 violation tasks
        assert len(tasks) == 3
        # Check for violation tasks
        violation_tasks = [t for t in tasks if "ADDRESS_VIOLATION" in t.name]
        assert len(violation_tasks) == 2

    def test_violation_tasks_critical_priority(self, todo_manager):
        """Violation-address tasks get CRITICAL priority."""
        evaluation = GovernanceEvaluationResult(
            request_valid=False,
            violations=["VIOLATION_1"],
            required_actions=[],
            governance_rules_applied=[],
            tier_precedence={}
        )
        
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            evaluation,
            "req_123",
            "test intent"
        )
        
        violation_tasks = [t for t in tasks if "ADDRESS_VIOLATION" in t.name]
        assert all(t.priority == TaskPriority.CRITICAL for t in violation_tasks)

    def test_tasks_include_request_id(
        self,
        todo_manager,
        mock_governance_evaluation
    ):
        """Created tasks include request_id in metadata."""
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            mock_governance_evaluation,
            "req_abc123",
            "test intent"
        )
        
        for task in tasks:
            assert task.metadata["request_id"] == "req_abc123"

    def test_tasks_include_user_intent(
        self,
        todo_manager,
        mock_governance_evaluation
    ):
        """Created tasks include user intent in metadata."""
        user_intent = "implement AC-TEST-001"
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            mock_governance_evaluation,
            "req_123",
            user_intent
        )
        
        for task in tasks:
            assert task.metadata["user_intent"] == user_intent

    def test_tasks_include_governance_rules(
        self,
        todo_manager,
        mock_governance_evaluation
    ):
        """Created tasks include applied governance rules."""
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            mock_governance_evaluation,
            "req_123",
            "test"
        )
        
        for task in tasks:
            assert "governance_rules" in task.metadata
            assert task.metadata["governance_rules"] == mock_governance_evaluation.governance_rules_applied

    def test_tasks_include_tier_precedence(
        self,
        todo_manager,
        mock_governance_evaluation
    ):
        """Created tasks include tier precedence info."""
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            mock_governance_evaluation,
            "req_123",
            "test"
        )
        
        for task in tasks:
            assert "tier_precedence" in task.metadata

    def test_custom_priority_mapping(self, todo_manager):
        """Custom priority mapping applied to action tasks."""
        evaluation = GovernanceEvaluationResult(
            request_valid=True,
            violations=[],
            required_actions=["ACTION_1", "ACTION_2"],
            governance_rules_applied=[],
            tier_precedence={}
        )
        
        custom_mapping = {
            "ACTION_1": TaskPriority.CRITICAL,
            "ACTION_2": TaskPriority.LOW
        }
        
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            evaluation,
            "req_123",
            "test",
            priority_mapping=custom_mapping
        )
        
        action_tasks = [t for t in tasks if not "ADDRESS_VIOLATION" in t.name]
        for task in action_tasks:
            if task.name == "ACTION_1":
                assert task.priority == TaskPriority.CRITICAL
            elif task.name == "ACTION_2":
                assert task.priority == TaskPriority.LOW

    def test_default_priority_mapping_applied(self, todo_manager):
        """Default priority mapping applied when none provided."""
        evaluation = GovernanceEvaluationResult(
            request_valid=True,
            violations=[],
            required_actions=["LOAD_CONTEXT", "RUN_TESTS"],
            governance_rules_applied=[],
            tier_precedence={}
        )
        
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            evaluation,
            "req_123",
            "test"
        )
        
        for task in tasks:
            if task.name == "LOAD_CONTEXT":
                assert task.priority == TaskPriority.HIGH
            elif task.name == "RUN_TESTS":
                assert task.priority == TaskPriority.MEDIUM


class TestTaskLifecycle:
    """Test task status transitions."""

    def test_task_default_pending(self, todo_manager):
        """New tasks start as PENDING."""
        task = todo_manager.create_task("Test")
        assert task.status == TaskStatus.PENDING

    def test_update_task_to_in_progress(self, todo_manager):
        """Update task status to IN_PROGRESS."""
        task = todo_manager.create_task("Test")
        todo_manager.update_task_status(task.id, TaskStatus.IN_PROGRESS)
        
        updated_task = todo_manager.get_task(task.id)
        assert updated_task.status == TaskStatus.IN_PROGRESS

    def test_start_task(self, todo_manager):
        """start_task() marks task IN_PROGRESS."""
        task = todo_manager.create_task("Test")
        todo_manager.start_task(task.id)
        
        updated_task = todo_manager.get_task(task.id)
        assert updated_task.status == TaskStatus.IN_PROGRESS

    def test_complete_task(self, todo_manager):
        """complete_task() marks task COMPLETE."""
        task = todo_manager.create_task("Test")
        todo_manager.complete_task(task.id)
        
        updated_task = todo_manager.get_task(task.id)
        assert updated_task.status == TaskStatus.COMPLETE

    def test_fail_task(self, todo_manager):
        """fail_task() marks task FAILED."""
        task = todo_manager.create_task("Test")
        todo_manager.fail_task(task.id, reason="Test failure")
        
        updated_task = todo_manager.get_task(task.id)
        assert updated_task.status == TaskStatus.FAILED
        assert updated_task.metadata["failure_reason"] == "Test failure"

    def test_block_task(self, todo_manager):
        """block_task() marks task BLOCKED."""
        task = todo_manager.create_task("Test")
        todo_manager.block_task(task.id, reason="Waiting for dependency")
        
        updated_task = todo_manager.get_task(task.id)
        assert updated_task.status == TaskStatus.BLOCKED
        assert updated_task.metadata["block_reason"] == "Waiting for dependency"


class TestTaskQueries:
    """Test task query and filtering methods."""

    def test_get_tasks_by_status(self, todo_manager):
        """Get all tasks with specific status."""
        t1 = todo_manager.create_task("Task 1")
        t2 = todo_manager.create_task("Task 2")
        t3 = todo_manager.create_task("Task 3")
        
        todo_manager.complete_task(t1.id)
        todo_manager.complete_task(t2.id)
        
        completed = todo_manager.get_tasks_by_status(TaskStatus.COMPLETE)
        assert len(completed) == 2

    def test_get_pending_tasks(self, todo_manager):
        """Get all PENDING tasks."""
        t1 = todo_manager.create_task("Task 1")
        t2 = todo_manager.create_task("Task 2")
        t3 = todo_manager.create_task("Task 3")
        
        todo_manager.complete_task(t1.id)
        
        pending = todo_manager.get_pending_tasks()
        assert len(pending) == 2

    def test_get_blocked_tasks(self, todo_manager):
        """Get all BLOCKED tasks."""
        t1 = todo_manager.create_task("Task 1")
        t2 = todo_manager.create_task("Task 2")
        
        todo_manager.block_task(t1.id)
        
        blocked = todo_manager.get_blocked_tasks()
        assert len(blocked) == 1

    def test_get_task_statistics(self, todo_manager):
        """Get task statistics."""
        for i in range(5):
            todo_manager.create_task(f"Task {i}")
        
        stats = todo_manager.get_task_statistics()
        
        assert stats["total_tasks"] == 5
        assert stats["by_status"]["pending"] == 5
        assert stats["completion_rate"] == 0.0

    def test_task_statistics_with_progress(self, todo_manager):
        """Task statistics reflect current progress."""
        t1 = todo_manager.create_task("Task 1")
        t2 = todo_manager.create_task("Task 2")
        t3 = todo_manager.create_task("Task 3")
        
        todo_manager.complete_task(t1.id)
        
        stats = todo_manager.get_task_statistics()
        
        assert stats["total_tasks"] == 3
        assert stats["by_status"]["complete"] == 1
        assert stats["by_status"]["pending"] == 2
        assert stats["completion_rate"] == pytest.approx(33.33, abs=1)

    def test_get_blocked_task_reasons(self, todo_manager):
        """Get reasons for blocked tasks."""
        t1 = todo_manager.create_task("Task 1")
        t2 = todo_manager.create_task("Task 2")
        
        todo_manager.block_task(t1.id, reason="Waiting for build")
        todo_manager.block_task(t2.id, reason="Dependency failed")
        
        reasons = todo_manager.get_blocked_task_reasons()
        
        assert reasons[t1.id] == "Waiting for build"
        assert reasons[t2.id] == "Dependency failed"


class TestTaskExport:
    """Test task export and serialization."""

    def test_task_to_dict(self, todo_manager):
        """Task can be serialized to dictionary."""
        task = todo_manager.create_task(
            "Test Action",
            description="Test description",
            priority=TaskPriority.HIGH,
            ac_id="AC-TODO-002"
        )
        
        task_dict = task.to_dict()
        
        assert task_dict["name"] == "Test Action"
        assert task_dict["description"] == "Test description"
        assert task_dict["priority"] == 2  # HIGH
        assert task_dict["status"] == "pending"
        assert task_dict["ac_id"] == "AC-TODO-002"

    def test_export_tasks_as_json(self, todo_manager):
        """Export all tasks as JSON-serializable list."""
        t1 = todo_manager.create_task("Task 1")
        t2 = todo_manager.create_task("Task 2")
        
        exported = todo_manager.export_tasks_as_json()
        
        assert len(exported) == 2
        assert all(isinstance(t, dict) for t in exported)
        assert exported[0]["name"] == "Task 1"
        assert exported[1]["name"] == "Task 2"


class TestTodoManagerIntegration:
    """Integration tests for TodoManager."""

    def test_governance_to_todo_workflow(self, todo_manager):
        """Complete workflow: governance evaluation → task creation."""
        # Simulate governance evaluation
        evaluation = GovernanceEvaluationResult(
            request_valid=True,
            violations=[],
            required_actions=[
                "LOAD_CONTEXT",
                "CREATE_FILE",
                "RUN_TESTS"
            ],
            governance_rules_applied=["SKULL_RULES"],
            tier_precedence={"tier0": 0}
        )
        
        # Create tasks from evaluation
        tasks = todo_manager.create_tasks_from_governance_evaluation(
            evaluation,
            "req_001",
            "implement AC-TEST-001"
        )
        
        # Execute tasks
        assert len(tasks) == 3
        for task in tasks:
            assert task.status == TaskStatus.PENDING
        
        # Mark first task in progress
        todo_manager.start_task(tasks[0].id)
        assert todo_manager.get_task(tasks[0].id).status == TaskStatus.IN_PROGRESS
        
        # Complete first task
        todo_manager.complete_task(tasks[0].id)
        assert todo_manager.get_task(tasks[0].id).status == TaskStatus.COMPLETE
        
        # Check statistics
        stats = todo_manager.get_task_statistics()
        assert stats["total_tasks"] == 3
        assert stats["by_status"]["complete"] == 1
        assert stats["by_status"]["pending"] == 2
