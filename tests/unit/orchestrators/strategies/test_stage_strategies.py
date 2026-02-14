"""
P1 FIX: Stage Execution Strategy Pattern — RED Phase Tests

Tests for the 4-stage execution strategy pattern used by
MasterOrchestrator's ENH-087 pipeline.

Authority: ENH-087, CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-P1-STAGE-STRATEGIES-001
"""

import pytest
from typing import Dict, Any, Optional
from unittest.mock import MagicMock


class TestStageExecutionStrategyBase:
    """Tests for StageExecutionStrategy base class and StageContext."""

    def test_stage_context_importable(self) -> None:
        """StageContext must be importable."""
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        assert StageContext is not None

    def test_stage_context_creation(self) -> None:
        """StageContext must accept operation_name, parameters, metadata."""
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        ctx = StageContext(
            operation_name="process_request",
            parameters={"request": "implement feature"},
            metadata={},
        )

        assert ctx.operation_name == "process_request"
        assert ctx.parameters["request"] == "implement feature"
        assert isinstance(ctx.metadata, dict)

    def test_stage_context_has_result_field(self) -> None:
        """StageContext must have a result field for stage output chaining."""
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        ctx = StageContext(
            operation_name="test",
            parameters={},
            metadata={},
        )

        assert ctx.result is None  # Initially None

    def test_stage_execution_strategy_importable(self) -> None:
        """StageExecutionStrategy ABC must be importable."""
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageExecutionStrategy,
        )

        assert StageExecutionStrategy is not None

    def test_stage_execution_strategy_is_abstract(self) -> None:
        """StageExecutionStrategy must be an abstract base class."""
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageExecutionStrategy,
        )
        import abc

        assert abc.ABC in StageExecutionStrategy.__mro__ or hasattr(
            StageExecutionStrategy, "__abstractmethods__"
        )

    def test_stage_execution_strategy_requires_execute(self) -> None:
        """Subclasses must implement execute() method."""
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageExecutionStrategy,
            StageContext,
        )

        with pytest.raises(TypeError):
            # Can't instantiate abstract class
            StageExecutionStrategy()  # type: ignore


class TestStage1ComprehensionStrategy:
    """Tests for Stage 1: LENS Comprehension strategy."""

    def test_importable(self) -> None:
        """Stage1ComprehensionStrategy must be importable."""
        from cortex.orchestrators.strategies.stage1_comprehension_strategy import (
            Stage1ComprehensionStrategy,
        )

        assert Stage1ComprehensionStrategy is not None

    def test_is_stage_execution_strategy(self) -> None:
        """Must inherit from StageExecutionStrategy."""
        from cortex.orchestrators.strategies.stage1_comprehension_strategy import (
            Stage1ComprehensionStrategy,
        )
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageExecutionStrategy,
        )

        assert issubclass(Stage1ComprehensionStrategy, StageExecutionStrategy)

    def test_execute_returns_result(self) -> None:
        """execute() must return a Result[StageContext]."""
        from cortex.orchestrators.strategies.stage1_comprehension_strategy import (
            Stage1ComprehensionStrategy,
        )
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        strategy = Stage1ComprehensionStrategy()
        ctx = StageContext(
            operation_name="process_request",
            parameters={"request": "implement feature"},
            metadata={},
        )

        result = strategy.execute(ctx)
        assert result.is_ok()

    def test_execute_adds_lens_context_to_metadata(self) -> None:
        """Stage 1 must add lens_context to metadata."""
        from cortex.orchestrators.strategies.stage1_comprehension_strategy import (
            Stage1ComprehensionStrategy,
        )
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        strategy = Stage1ComprehensionStrategy()
        ctx = StageContext(
            operation_name="process_request",
            parameters={"request": "implement feature"},
            metadata={},
        )

        result = strategy.execute(ctx)
        updated_ctx = result.unwrap()
        assert "lens_context" in updated_ctx.metadata


class TestStage234Strategies:
    """Tests for Stage 2, 3, 4 strategies."""

    def test_stage2_importable(self) -> None:
        """Stage2IntentClassificationStrategy must be importable."""
        from cortex.orchestrators.strategies.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )

        assert Stage2IntentClassificationStrategy is not None

    def test_stage3_importable(self) -> None:
        """Stage3ComplianceValidationStrategy must be importable."""
        from cortex.orchestrators.strategies.stage234_strategies import (
            Stage3ComplianceValidationStrategy,
        )

        assert Stage3ComplianceValidationStrategy is not None

    def test_stage4_importable(self) -> None:
        """Stage4DomainExecutionStrategy must be importable."""
        from cortex.orchestrators.strategies.stage234_strategies import (
            Stage4DomainExecutionStrategy,
        )

        assert Stage4DomainExecutionStrategy is not None

    def test_stage2_execute_classifies_intent(self) -> None:
        """Stage 2 must add intent_classification to metadata."""
        from cortex.orchestrators.strategies.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        strategy = Stage2IntentClassificationStrategy()
        ctx = StageContext(
            operation_name="process_request",
            parameters={"request": "implement feature"},
            metadata={},
        )

        result = strategy.execute(ctx)
        assert result.is_ok()
        updated = result.unwrap()
        assert "intent_classification" in updated.metadata

    def test_stage3_execute_validates_compliance(self) -> None:
        """Stage 3 must add compliance_validation to metadata."""
        from cortex.orchestrators.strategies.stage234_strategies import (
            Stage3ComplianceValidationStrategy,
        )
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        strategy = Stage3ComplianceValidationStrategy()
        ctx = StageContext(
            operation_name="process_request",
            parameters={"request": "implement feature"},
            metadata={"intent_classification": {"classified_intent": "IMPLEMENT", "confidence": 0.9}},
        )

        result = strategy.execute(ctx)
        assert result.is_ok()
        updated = result.unwrap()
        assert "compliance_validation" in updated.metadata

    def test_stage4_execute_delegates(self) -> None:
        """Stage 4 must add execution results to metadata."""
        from cortex.orchestrators.strategies.stage234_strategies import (
            Stage4DomainExecutionStrategy,
        )
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageContext,
        )

        strategy = Stage4DomainExecutionStrategy()
        ctx = StageContext(
            operation_name="process_request",
            parameters={"request": "implement feature"},
            metadata={
                "intent_classification": {"classified_intent": "IMPLEMENT", "confidence": 0.9},
                "compliance_validation": {"status": "PASS", "warnings": []},
            },
        )

        result = strategy.execute(ctx)
        assert result.is_ok()
        updated = result.unwrap()
        assert "execution" in updated.metadata

    def test_all_stages_are_strategies(self) -> None:
        """All stage strategies must inherit from StageExecutionStrategy."""
        from cortex.orchestrators.strategies.stage234_strategies import (
            Stage2IntentClassificationStrategy,
            Stage3ComplianceValidationStrategy,
            Stage4DomainExecutionStrategy,
        )
        from cortex.orchestrators.strategies.stage_execution_strategy import (
            StageExecutionStrategy,
        )

        assert issubclass(Stage2IntentClassificationStrategy, StageExecutionStrategy)
        assert issubclass(Stage3ComplianceValidationStrategy, StageExecutionStrategy)
        assert issubclass(Stage4DomainExecutionStrategy, StageExecutionStrategy)


# AC_COMPLETE: AC-P1-STAGE-STRATEGIES-001
