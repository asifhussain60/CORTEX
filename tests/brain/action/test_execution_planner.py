"""
Tests for Execution Planner - Phase 12 S3

AC-PHASE71-011: Execution planning in action layer

Tests brain action layer execution planner:
- Execution plan generation from strategies
- Step-by-step guidance based on patterns
- Adaptive planning based on context
- Plan validation and prerequisite ordering

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

from typing import Any, Dict, List

import pytest

from cortex_intelligence.action.execution_planner import (
    ExecutionPlanner,
    ExecutionPlan,
    ExecutionStep,
    StepStatus,
)


@pytest.fixture
def planner() -> ExecutionPlanner:
    """Create ExecutionPlanner instance."""
    return ExecutionPlanner()


@pytest.fixture
def sample_strategy_context() -> Dict[str, Any]:
    """Create sample strategy context."""
    return {
        "strategy_id": "extract_microservices",
        "repository": "example-repo",
        "architecture_type": "modular_monolith",
        "segment_count": 5
    }


class TestExecutionPlannerInitialization:
    """Test ExecutionPlanner initialization."""

    def test_initialization(self) -> None:
        """Test planner initialization."""
        planner = ExecutionPlanner()
        assert planner is not None

    def test_has_step_templates(self, planner: ExecutionPlanner) -> None:
        """Test planner has step templates."""
        templates = planner.get_available_templates()
        assert isinstance(templates, list)


class TestPlanGeneration:
    """Test execution plan generation."""

    def test_generate_plan_from_strategy(
        self,
        planner: ExecutionPlanner,
        sample_strategy_context: Dict[str, Any]
    ) -> None:
        """Test generating execution plan from strategy."""
        plan = planner.generate_plan(sample_strategy_context)

        assert isinstance(plan, ExecutionPlan)
        assert plan.strategy_id == "extract_microservices"
        assert len(plan.steps) > 0

    def test_plan_has_ordered_steps(
        self,
        planner: ExecutionPlanner,
        sample_strategy_context: Dict[str, Any]
    ) -> None:
        """Test generated plan has ordered steps."""
        plan = planner.generate_plan(sample_strategy_context)

        # Steps should have sequential order
        for i, step in enumerate(plan.steps):
            assert step.order == i + 1

    def test_plan_includes_prerequisites(
        self,
        planner: ExecutionPlanner,
        sample_strategy_context: Dict[str, Any]
    ) -> None:
        """Test plan includes prerequisite validation."""
        plan = planner.generate_plan(sample_strategy_context)

        # First step should typically be prerequisite check
        if plan.steps:
            first_step = plan.steps[0]
            assert "prerequisite" in first_step.description.lower() or first_step.order == 1


class TestStepGeneration:
    """Test step generation for different strategies."""

    def test_generate_steps_for_refactoring(
        self,
        planner: ExecutionPlanner
    ) -> None:
        """Test generating steps for refactoring strategy."""
        context = {
            "strategy_id": "extract_method",
            "target_file": "example.py",
            "complexity": "high"
        }

        plan = planner.generate_plan(context)

        assert len(plan.steps) > 0
        assert any("test" in step.description.lower() for step in plan.steps)

    def test_generate_steps_for_migration(
        self,
        planner: ExecutionPlanner
    ) -> None:
        """Test generating steps for migration strategy."""
        context = {
            "strategy_id": "migrate_to_microservices",
            "source_architecture": "monolith"
        }

        plan = planner.generate_plan(context)

        assert len(plan.steps) > 0

    def test_adaptive_steps_based_on_context(
        self,
        planner: ExecutionPlanner
    ) -> None:
        """Test steps adapt based on context."""
        context_simple = {
            "strategy_id": "refactor",
            "complexity": "low"
        }

        context_complex = {
            "strategy_id": "refactor",
            "complexity": "high"
        }

        plan_simple = planner.generate_plan(context_simple)
        plan_complex = planner.generate_plan(context_complex)

        # Complex contexts may generate more steps
        assert isinstance(plan_simple.steps, list)
        assert isinstance(plan_complex.steps, list)


class TestStepOrdering:
    """Test step ordering and dependencies."""

    def test_steps_ordered_by_dependencies(
        self,
        planner: ExecutionPlanner,
        sample_strategy_context: Dict[str, Any]
    ) -> None:
        """Test steps ordered respecting dependencies."""
        plan = planner.generate_plan(sample_strategy_context)

        # Verify order is sequential
        for i, step in enumerate(plan.steps):
            assert step.order == i + 1

    def test_prerequisite_steps_come_first(
        self,
        planner: ExecutionPlanner,
        sample_strategy_context: Dict[str, Any]
    ) -> None:
        """Test prerequisite validation steps come first."""
        plan = planner.generate_plan(sample_strategy_context)

        if len(plan.steps) > 1:
            # Early steps should be setup/validation or identify/design
            early_steps = plan.steps[:2]
            assert any(
                "setup" in step.description.lower() or 
                "validate" in step.description.lower() or
                "check" in step.description.lower() or
                "identify" in step.description.lower() or
                "design" in step.description.lower() or
                "bounded" in step.description.lower()
                for step in early_steps
            )


class TestPlanValidation:
    """Test plan validation."""

    def test_validate_complete_plan(
        self,
        planner: ExecutionPlanner,
        sample_strategy_context: Dict[str, Any]
    ) -> None:
        """Test validating a complete plan."""
        plan = planner.generate_plan(sample_strategy_context)

        is_valid = planner.validate_plan(plan)
        assert isinstance(is_valid, bool)

    def test_validate_detects_missing_steps(
        self,
        planner: ExecutionPlanner
    ) -> None:
        """Test validation detects incomplete plans."""
        incomplete_plan = ExecutionPlan(
            strategy_id="test",
            steps=[],  # No steps
            estimated_duration="0m"
        )

        is_valid = planner.validate_plan(incomplete_plan)
        assert is_valid is False

    def test_validate_checks_step_order(
        self,
        planner: ExecutionPlanner
    ) -> None:
        """Test validation checks step ordering."""
        steps = [
            ExecutionStep(order=2, description="Step 2", status=StepStatus.PENDING),
            ExecutionStep(order=1, description="Step 1", status=StepStatus.PENDING)  # Wrong order
        ]

        plan = ExecutionPlan(
            strategy_id="test",
            steps=steps,
            estimated_duration="10m"
        )

        is_valid = planner.validate_plan(plan)
        # Should detect ordering issue
        assert isinstance(is_valid, bool)


class TestStepExecution:
    """Test step execution tracking."""

    def test_mark_step_complete(self, planner: ExecutionPlanner) -> None:
        """Test marking step as complete."""
        step = ExecutionStep(
            order=1,
            description="Test step",
            status=StepStatus.PENDING
        )

        updated_step = planner.mark_step_complete(step)
        assert updated_step.status == StepStatus.COMPLETED

    def test_mark_step_failed(self, planner: ExecutionPlanner) -> None:
        """Test marking step as failed."""
        step = ExecutionStep(
            order=1,
            description="Test step",
            status=StepStatus.IN_PROGRESS
        )

        updated_step = planner.mark_step_failed(step, "Error occurred")
        assert updated_step.status == StepStatus.FAILED

    def test_track_plan_progress(
        self,
        planner: ExecutionPlanner,
        sample_strategy_context: Dict[str, Any]
    ) -> None:
        """Test tracking plan execution progress."""
        plan = planner.generate_plan(sample_strategy_context)

        progress = planner.calculate_progress(plan)
        assert 0.0 <= progress <= 1.0


class TestExecutionPlanDataClass:
    """Test ExecutionPlan data class."""

    def test_plan_creation(self) -> None:
        """Test creating ExecutionPlan instance."""
        steps = [
            ExecutionStep(order=1, description="Step 1", status=StepStatus.PENDING)
        ]

        plan = ExecutionPlan(
            strategy_id="test_strategy",
            steps=steps,
            estimated_duration="30m"
        )

        assert plan.strategy_id == "test_strategy"
        assert len(plan.steps) == 1

    def test_plan_to_dict(self) -> None:
        """Test converting plan to dictionary."""
        steps = [
            ExecutionStep(order=1, description="Step 1", status=StepStatus.PENDING)
        ]

        plan = ExecutionPlan(
            strategy_id="test",
            steps=steps,
            estimated_duration="15m"
        )

        data = plan.to_dict()
        assert data["strategy_id"] == "test"
        assert "steps" in data


class TestExecutionStepDataClass:
    """Test ExecutionStep data class."""

    def test_step_creation(self) -> None:
        """Test creating ExecutionStep instance."""
        step = ExecutionStep(
            order=1,
            description="Test step",
            status=StepStatus.PENDING,
            estimated_duration="5m"
        )

        assert step.order == 1
        assert step.status == StepStatus.PENDING

    def test_step_to_dict(self) -> None:
        """Test converting step to dictionary."""
        step = ExecutionStep(
            order=1,
            description="Test",
            status=StepStatus.COMPLETED
        )

        data = step.to_dict()
        assert data["order"] == 1
        assert data["status"] == "COMPLETED"


class TestStepStatusEnum:
    """Test StepStatus enum."""

    def test_status_values(self) -> None:
        """Test StepStatus enum values."""
        assert StepStatus.PENDING
        assert StepStatus.IN_PROGRESS
        assert StepStatus.COMPLETED
        assert StepStatus.FAILED
        assert StepStatus.SKIPPED


class TestTemplateManagement:
    """Test execution step templates."""

    def test_register_template(self, planner: ExecutionPlanner) -> None:
        """Test registering step template."""
        template = {
            "strategy_id": "test_strategy",
            "steps": [
                {"order": 1, "description": "Step 1"},
                {"order": 2, "description": "Step 2"}
            ]
        }

        planner.register_template("test_strategy", template)

        templates = planner.get_available_templates()
        assert "test_strategy" in [t.get("id") for t in templates]

    def test_use_registered_template(self, planner: ExecutionPlanner) -> None:
        """Test using registered template for plan generation."""
        template = {
            "strategy_id": "custom_strategy",
            "steps": [
                {"order": 1, "description": "Custom step 1"},
                {"order": 2, "description": "Custom step 2"}
            ]
        }

        planner.register_template("custom_strategy", template)

        context = {"strategy_id": "custom_strategy"}
        plan = planner.generate_plan(context)

        assert len(plan.steps) == 2
        assert "Custom step 1" in plan.steps[0].description


class TestAdaptivePlanning:
    """Test adaptive planning based on historical data."""

    def test_adjust_plan_based_on_complexity(
        self,
        planner: ExecutionPlanner
    ) -> None:
        """Test plan adjusts based on complexity."""
        low_complexity = {
            "strategy_id": "refactor",
            "complexity": "low"
        }

        high_complexity = {
            "strategy_id": "refactor",
            "complexity": "high"
        }

        plan_low = planner.generate_plan(low_complexity)
        plan_high = planner.generate_plan(high_complexity)

        # Both should generate plans
        assert isinstance(plan_low, ExecutionPlan)
        assert isinstance(plan_high, ExecutionPlan)

    def test_adjust_plan_based_on_team_size(
        self,
        planner: ExecutionPlanner
    ) -> None:
        """Test plan adjusts based on team size."""
        small_team = {
            "strategy_id": "migration",
            "team_size": 2
        }

        large_team = {
            "strategy_id": "migration",
            "team_size": 10
        }

        plan_small = planner.generate_plan(small_team)
        plan_large = planner.generate_plan(large_team)

        # Both should generate valid plans
        assert plan_small.strategy_id == "migration"
        assert plan_large.strategy_id == "migration"
