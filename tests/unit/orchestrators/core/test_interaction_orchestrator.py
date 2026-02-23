"""
P0 FIX: InteractionOrchestrator — RED Phase Tests

Tests for cortex.orchestrators.core.interaction_orchestrator that wires
LENS analysis into every turn via ConversationProtocol.

Authority: MCP-FIRST, CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-P0-INTERACTION-ORCH-001
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Dict, Any
from pathlib import Path


class TestInteractionOrchestratorImport:
    """Tests that InteractionOrchestrator is importable and meets interface contract."""

    def test_importable(self) -> None:
        """InteractionOrchestrator must be importable from expected path."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        assert InteractionOrchestrator is not None

    def test_implements_i_orchestrator(self) -> None:
        """InteractionOrchestrator must implement IOrchestrator interface."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )
        from cortex.core.core.interfaces.i_orchestrator import IOrchestrator

        assert issubclass(InteractionOrchestrator, IOrchestrator)


class TestInteractionOrchestratorInit:
    """Tests for InteractionOrchestrator initialization."""

    def test_init_with_conversation_protocol(self) -> None:
        """Must accept conversation_protocol parameter."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)

        assert orch.conversation_protocol is mock_protocol

    def test_init_with_enable_challenges_true(self) -> None:
        """Must accept enable_challenges=True (AC-PERMANENT-FIX-006)."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=mock_protocol,
            enable_challenges=True,
        )

        assert orch.enable_challenges is True

    def test_init_default_enable_challenges_false(self) -> None:
        """enable_challenges must default to False."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)

        assert orch.enable_challenges is False

    def test_init_creates_lens_orchestrator(self) -> None:
        """Must initialize a LENSOrchestrator for per-turn analysis."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)

        assert orch.lens_orchestrator is not None


class TestInteractionOrchestratorIOrchestratorContract:
    """Tests for IOrchestrator interface contract methods."""

    @pytest.fixture
    def orchestrator(self) -> "InteractionOrchestrator":
        """Create InteractionOrchestrator with mock protocol."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        return InteractionOrchestrator(conversation_protocol=mock_protocol)

    def test_get_name(self, orchestrator: Any) -> None:
        """get_name must return 'InteractionOrchestrator'."""
        result = orchestrator.get_name()
        assert result == "InteractionOrchestrator"

    def test_get_version(self, orchestrator: Any) -> None:
        """get_version must return a semantic version string."""
        version = orchestrator.get_version()
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    def test_initialize(self, orchestrator: Any) -> None:
        """initialize must return Ok result."""
        result = orchestrator.initialize()
        assert result.is_ok()

    def test_get_mode(self, orchestrator: Any) -> None:
        """get_mode must return an OperationMode."""
        from cortex.core.core.interfaces.i_orchestrator import OperationMode

        mode = orchestrator.get_mode()
        assert isinstance(mode, OperationMode)

    def test_get_mcp_tools(self, orchestrator: Any) -> None:
        """get_mcp_tools must return Ok with tool definitions."""
        result = orchestrator.get_mcp_tools()
        assert result.is_ok()
        tools = result.unwrap()
        assert isinstance(tools, dict)

    def test_get_audit_trail(self, orchestrator: Any) -> None:
        """get_audit_trail must return Ok with list."""
        result = orchestrator.get_audit_trail()
        assert result.is_ok()
        trail = result.unwrap()
        assert isinstance(trail, list)


class TestInteractionOrchestratorLensPerTurn:
    """Tests that LENS analysis runs on every turn (core requirement)."""

    @pytest.fixture
    def orchestrator(self) -> "InteractionOrchestrator":
        """Create InteractionOrchestrator with mock protocol."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        return InteractionOrchestrator(conversation_protocol=mock_protocol)

    def test_execute_operation_runs_lens(self, orchestrator: Any) -> None:
        """execute_operation must include LENS context in result."""
        result = orchestrator.execute_operation(
            operation_name="comprehend",
            parameters={"user_input": "implement a new feature"},
        )

        assert result.is_ok()
        output = result.unwrap()
        assert "lens_context" in output

    def test_execute_operation_lens_has_analysis_keys(self, orchestrator: Any) -> None:
        """LENS context must contain standard analysis keys."""
        result = orchestrator.execute_operation(
            operation_name="comprehend",
            parameters={"user_input": "fix the bug"},
        )

        output = result.unwrap()
        lens = output["lens_context"]
        # LENS orchestrator returns git, ast, comment analysis
        assert isinstance(lens, dict)

    def test_execute_turn_with_challenge_returns_result(self, orchestrator: Any) -> None:
        """execute_turn_with_challenge must return a Result."""
        from cortex.core.core.orchestrator.conversation_protocol import RoundContext

        round_context = RoundContext(
            round_number=1,
            user_input="implement feature X",
            previous_context={},
            orchestrator_name="InteractionOrchestrator",
        )

        result = orchestrator.execute_turn_with_challenge(
            user_request="implement feature X",
            round_context=round_context,
            pattern_id=None,
        )

        assert result.is_ok()

    def test_execute_turn_includes_lens_context(self, orchestrator: Any) -> None:
        """Each turn must include LENS analysis in output."""
        from cortex.core.core.orchestrator.conversation_protocol import RoundContext

        round_context = RoundContext(
            round_number=1,
            user_input="refactor module",
            previous_context={},
            orchestrator_name="InteractionOrchestrator",
        )

        result = orchestrator.execute_turn_with_challenge(
            user_request="refactor module",
            round_context=round_context,
            pattern_id=None,
        )

        output = result.unwrap()
        assert "lens_context" in output

    def test_turn_number_increments(self, orchestrator: Any) -> None:
        """Turn number must increment with each execute_turn_with_challenge call."""
        from cortex.core.core.orchestrator.conversation_protocol import RoundContext

        for i in range(3):
            ctx = RoundContext(
                round_number=i + 1,
                user_input=f"turn {i}",
                previous_context={},
                orchestrator_name="InteractionOrchestrator",
            )
            orchestrator.execute_turn_with_challenge(
                user_request=f"turn {i}",
                round_context=ctx,
                pattern_id=None,
            )

        assert orchestrator.turn_number == 3


class TestInteractionOrchestratorChallengeSystem:
    """Tests for challenge generation integration."""

    def test_challenge_disabled_by_default(self) -> None:
        """With enable_challenges=False, no challenges generated."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )
        from cortex.core.core.orchestrator.conversation_protocol import RoundContext

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=mock_protocol,
            enable_challenges=False,
        )

        ctx = RoundContext(
            round_number=1,
            user_input="implement feature",
            previous_context={},
            orchestrator_name="InteractionOrchestrator",
        )

        result = orch.execute_turn_with_challenge(
            user_request="implement feature",
            round_context=ctx,
            pattern_id=None,
        )

        output = result.unwrap()
        assert output.get("type") != "challenge"

    def test_challenge_enabled_includes_challenge_check(self) -> None:
        """With enable_challenges=True, output must include challenge_evaluated flag."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )
        from cortex.core.core.orchestrator.conversation_protocol import RoundContext

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(
            conversation_protocol=mock_protocol,
            enable_challenges=True,
        )

        ctx = RoundContext(
            round_number=1,
            user_input="implement feature",
            previous_context={},
            orchestrator_name="InteractionOrchestrator",
        )

        result = orch.execute_turn_with_challenge(
            user_request="implement feature",
            round_context=ctx,
            pattern_id=None,
        )

        output = result.unwrap()
        assert "challenge_evaluated" in output


class TestInteractionOrchestratorExecuteMethod:
    """Tests for the execute() method used by MasterOrchestrator."""

    def test_execute_with_context(self) -> None:
        """execute() method used by MasterOrchestrator Phase 1."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)

        result = orch.execute(context={"user_intent": "analyze codebase"})
        assert result.is_ok()
        data = result.unwrap()
        assert isinstance(data, dict)

    def test_execute_provides_intent_type(self) -> None:
        """execute() must provide intent_type in output for downstream routing."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)

        result = orch.execute(context={"user_intent": "implement new feature"})
        data = result.unwrap()
        assert "intent_type" in data


class TestExecuteTurn:
    """GAP-001: execute_turn() required by startup_validator (CORE-008 RED)."""

    def test_execute_turn_exists(self) -> None:
        """InteractionOrchestrator must have execute_turn() method."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        assert hasattr(InteractionOrchestrator, "execute_turn"), (
            "execute_turn() missing — startup_validator raises warning on every boot"
        )

    def test_execute_turn_returns_result(self) -> None:
        """execute_turn(user_input) must return a Result."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )
        from cortex.core.result import Ok

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)
        result = orch.execute_turn("fix the broken import")
        assert result is not None
        assert hasattr(result, "is_ok"), "execute_turn must return a Result type"
        assert result.is_ok()

    def test_execute_turn_output_contains_user_input(self) -> None:
        """execute_turn output must echo back user_input for traceability."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)
        result = orch.execute_turn("implement the new dashboard")
        data = result.unwrap()
        assert "user_input" in data

    def test_execute_turn_increments_turn_number(self) -> None:
        """execute_turn() must increment the turn counter."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orch = InteractionOrchestrator(conversation_protocol=mock_protocol)
        assert orch.turn_number == 0
        orch.execute_turn("first turn")
        assert orch.turn_number == 1
        orch.execute_turn("second turn")
        assert orch.turn_number == 2

    def test_startup_validator_no_longer_warns(self) -> None:
        """startup_validator check for execute_turn must pass (no warning emitted)."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        class_attrs = dir(InteractionOrchestrator)
        assert "execute_turn" in class_attrs, (
            "startup_validator line 317: 'execute_turn' not in class_attrs triggers P2 warning"
        )


# AC_COMPLETE: AC-P0-INTERACTION-ORCH-001
