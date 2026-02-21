"""
Execution Planner - Phase 12 S3 (Brain Action Layer)

AC-PHASE71-011: Execution planning in action layer

Brain action layer that:
- Generates execution plans from strategies
- Provides step-by-step guidance
- Adapts plans based on context
- Tracks execution progress

Used by learning loop to convert strategies into actionable steps.

Author: GitHub Copilot
Date: 2026-02-14
Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Status of execution step."""

    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    SKIPPED = auto()


@dataclass
class ExecutionStep:
    """Single step in execution plan."""

    order: int
    description: str
    status: StepStatus
    estimated_duration: str = "5m"
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "order": self.order,
            "description": self.description,
            "status": self.status.name,
            "estimated_duration": self.estimated_duration,
            "error_message": self.error_message,
        }


@dataclass
class ExecutionPlan:
    """Complete execution plan for strategy."""

    strategy_id: str
    steps: List[ExecutionStep]
    estimated_duration: str
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "strategy_id": self.strategy_id,
            "steps": [step.to_dict() for step in self.steps],
            "estimated_duration": self.estimated_duration,
            "context": self.context,
        }


class ExecutionPlanner:
    """
    Brain action layer execution planner.

    Generates actionable execution plans from strategies with
    step-by-step guidance adapted to context.

    AC-PHASE71-011: Execution planning
    """

    def __init__(self) -> None:
        """Initialize execution planner."""
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._initialize_default_templates()

    def generate_plan(
        self,
        strategy_context: Dict[str, Any]
    ) -> ExecutionPlan:
        """
        Generate execution plan from strategy context.

        Args:
            strategy_context: Context including strategy_id and parameters

        Returns:
            ExecutionPlan with ordered steps
        """
        strategy_id = strategy_context.get("strategy_id", "unknown")

        # Check for registered template
        if strategy_id in self._templates:
            steps = self._generate_from_template(strategy_id, strategy_context)
        else:
            steps = self._generate_generic_steps(strategy_context)

        # Adapt steps based on context
        steps = self._adapt_steps(steps, strategy_context)

        # Calculate estimated duration
        total_duration = sum(
            self._parse_duration(step.estimated_duration)
            for step in steps
        )
        estimated_duration = f"{total_duration}m"

        plan = ExecutionPlan(
            strategy_id=strategy_id,
            steps=steps,
            estimated_duration=estimated_duration,
            context=strategy_context
        )

        logger.info(f"Generated execution plan for {strategy_id}: {len(steps)} steps")
        return plan

    def validate_plan(self, plan: ExecutionPlan) -> bool:
        """
        Validate execution plan completeness.

        Args:
            plan: ExecutionPlan to validate

        Returns:
            True if plan is valid
        """
        if not plan.steps:
            logger.warning("Plan has no steps")
            return False

        # Check step ordering
        expected_order = 1
        for step in plan.steps:
            if step.order != expected_order:
                logger.warning(f"Step order mismatch: expected {expected_order}, got {step.order}")
                # Don't fail, just warn (might be intentional)
            expected_order += 1

        return True

    def mark_step_complete(self, step: ExecutionStep) -> ExecutionStep:
        """Mark step as completed."""
        step.status = StepStatus.COMPLETED
        return step

    def mark_step_failed(self, step: ExecutionStep, error: str) -> ExecutionStep:
        """Mark step as failed with error message."""
        step.status = StepStatus.FAILED
        step.error_message = error
        return step

    def calculate_progress(self, plan: ExecutionPlan) -> float:
        """
        Calculate plan execution progress.

        Args:
            plan: ExecutionPlan to analyze

        Returns:
            Progress percentage (0.0-1.0)
        """
        if not plan.steps:
            return 0.0

        completed = sum(
            1 for step in plan.steps
            if step.status == StepStatus.COMPLETED
        )

        return completed / len(plan.steps)

    def register_template(self, strategy_id: str, template: Dict[str, Any]) -> None:
        """
        Register execution plan template.

        Args:
            strategy_id: Strategy identifier
            template: Template definition
        """
        self._templates[strategy_id] = template
        logger.debug(f"Registered template for {strategy_id}")

    def get_available_templates(self) -> List[Dict[str, Any]]:
        """Get list of available templates."""
        return [
            {"id": strategy_id, "template": template}
            for strategy_id, template in self._templates.items()
        ]

    def _initialize_default_templates(self) -> None:
        """Initialize default execution templates."""
        # Refactoring template
        self._templates["extract_method"] = {
            "steps": [
                {"order": 1, "description": "Identify code to extract", "duration": "10m"},
                {"order": 2, "description": "Write tests for current behavior", "duration": "15m"},
                {"order": 3, "description": "Extract method", "duration": "10m"},
                {"order": 4, "description": "Run tests to verify", "duration": "5m"},
                {"order": 5, "description": "Refactor and optimize", "duration": "10m"}
            ]
        }

        # Migration template
        self._templates["extract_microservices"] = {
            "steps": [
                {"order": 1, "description": "Identify bounded context boundaries", "duration": "30m"},
                {"order": 2, "description": "Design service interfaces", "duration": "45m"},
                {"order": 3, "description": "Set up service infrastructure", "duration": "60m"},
                {"order": 4, "description": "Extract domain logic", "duration": "120m"},
                {"order": 5, "description": "Implement communication layer", "duration": "90m"},
                {"order": 6, "description": "Migrate data", "duration": "60m"},
                {"order": 7, "description": "Test end-to-end", "duration": "30m"}
            ]
        }

    def _generate_from_template(
        self,
        strategy_id: str,
        context: Dict[str, Any]
    ) -> List[ExecutionStep]:
        """Generate steps from registered template."""
        template = self._templates[strategy_id]
        steps = []

        for step_def in template.get("steps", []):
            step = ExecutionStep(
                order=step_def["order"],
                description=step_def["description"],
                status=StepStatus.PENDING,
                estimated_duration=step_def.get("duration", "5m")
            )
            steps.append(step)

        return steps

    def _generate_generic_steps(
        self,
        context: Dict[str, Any]
    ) -> List[ExecutionStep]:
        """Generate generic execution steps."""
        return [
            ExecutionStep(
                order=1,
                description="Validate prerequisites",
                status=StepStatus.PENDING,
                estimated_duration="5m"
            ),
            ExecutionStep(
                order=2,
                description="Analyze current state",
                status=StepStatus.PENDING,
                estimated_duration="15m"
            ),
            ExecutionStep(
                order=3,
                description="Execute strategy",
                status=StepStatus.PENDING,
                estimated_duration="30m"
            ),
            ExecutionStep(
                order=4,
                description="Verify results",
                status=StepStatus.PENDING,
                estimated_duration="10m"
            )
        ]

    def _adapt_steps(
        self,
        steps: List[ExecutionStep],
        context: Dict[str, Any]
    ) -> List[ExecutionStep]:
        """Adapt steps based on context."""
        complexity = context.get("complexity", "medium")

        # Adjust durations based on complexity
        if complexity == "high":
            for step in steps:
                current = self._parse_duration(step.estimated_duration)
                step.estimated_duration = f"{int(current * 1.5)}m"
        elif complexity == "low":
            for step in steps:
                current = self._parse_duration(step.estimated_duration)
                step.estimated_duration = f"{int(current * 0.7)}m"

        return steps

    def _parse_duration(self, duration_str: str) -> int:
        """Parse duration string to minutes."""
        if duration_str.endswith("m"):
            return int(duration_str[:-1])
        elif duration_str.endswith("h"):
            return int(duration_str[:-1]) * 60
        return 5  # Default


# Singleton accessor
_planner_instance: Optional[ExecutionPlanner] = None


def get_execution_planner() -> ExecutionPlanner:
    """
    Get singleton ExecutionPlanner instance.

    Returns:
        Singleton ExecutionPlanner instance
    """
    global _planner_instance

    if _planner_instance is None:
        _planner_instance = ExecutionPlanner()

    return _planner_instance
