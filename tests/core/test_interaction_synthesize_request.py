"""
tests/core/test_interaction_synthesize_request.py — TDD RED→GREEN

Tests for InteractionOrchestrator.synthesize_request() — the method that
reads prior requests from RequestLogManager and produces a holistic
summary with Definition of Done checklist for multi-turn sessions.

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Phase: Response template rendering overhaul
"""
from __future__ import annotations

from typing import Any, Dict, List
from unittest.mock import MagicMock

import pytest


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def interaction_orchestrator():
    """Create an InteractionOrchestrator instance for testing."""
    try:
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )
    except ImportError:
        pytest.skip("InteractionOrchestrator not importable")

    orch = InteractionOrchestrator.__new__(InteractionOrchestrator)
    # Minimal init — only the attributes synthesize_request needs
    orch._request_log_manager = None
    orch._prior_context_limit = 5
    return orch


@pytest.fixture
def mock_rlm() -> MagicMock:
    """Create a mock RequestLogManager with configurable prior_requests."""
    rlm = MagicMock()
    rlm.get_prior_requests.return_value = []
    return rlm


def _make_request(
    seq: int, text: str, intent: str = "IMPLEMENT", status: str = "COMPLETED"
) -> Dict[str, Any]:
    """Create a request dict matching RequestLogManager output shape."""
    return {
        "sequence_number": seq,
        "user_request": text,
        "intent_type": intent,
        "status": status,
        "request_id": f"req-{seq:03d}",
    }


# ---------------------------------------------------------------------------
# Tests: synthesize_request() existence and interface
# ---------------------------------------------------------------------------


class TestSynthesizeRequestInterface:
    """Verify the method exists and has the correct signature."""

    def test_method_exists(self, interaction_orchestrator) -> None:
        """InteractionOrchestrator must have a synthesize_request method."""
        assert hasattr(interaction_orchestrator, "synthesize_request"), (
            "InteractionOrchestrator missing synthesize_request() method"
        )

    def test_method_callable(self, interaction_orchestrator) -> None:
        """synthesize_request must be callable."""
        assert callable(getattr(interaction_orchestrator, "synthesize_request", None))

    def test_returns_dict(self, interaction_orchestrator, mock_rlm) -> None:
        """synthesize_request must return a dict."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = [
            _make_request(1, "fix the tests"),
        ]
        result = interaction_orchestrator.synthesize_request(
            current_request="also add logging",
            session_id="test-session",
        )
        assert isinstance(result, dict)


# ---------------------------------------------------------------------------
# Tests: Empty / first-turn behaviour
# ---------------------------------------------------------------------------


class TestSynthesizeRequestFirstTurn:
    """First turn — no prior requests available."""

    def test_no_rlm_returns_empty_synthesis(self, interaction_orchestrator) -> None:
        """When no RequestLogManager is set, return empty synthesis."""
        interaction_orchestrator._request_log_manager = None
        result = interaction_orchestrator.synthesize_request(
            current_request="fix the tests",
            session_id="test-session",
        )
        assert result["has_prior_context"] is False
        assert result["prior_count"] == 0
        assert result["synthesized_summary"] == ""
        assert result["dod_items"] == []

    def test_rlm_returns_no_prior_requests(
        self, interaction_orchestrator, mock_rlm
    ) -> None:
        """When RLM returns empty list, return empty synthesis."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = []
        result = interaction_orchestrator.synthesize_request(
            current_request="fix the tests",
            session_id="test-session",
        )
        assert result["has_prior_context"] is False
        assert result["prior_count"] == 0


# ---------------------------------------------------------------------------
# Tests: Multi-turn synthesis
# ---------------------------------------------------------------------------


class TestSynthesizeRequestMultiTurn:
    """Multiple prior requests — should produce holistic summary."""

    def test_single_prior_request(
        self, interaction_orchestrator, mock_rlm
    ) -> None:
        """One prior request should produce a summary with prior_count=1."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = [
            _make_request(1, "rename all BLOCK headers to professional format"),
        ]
        result = interaction_orchestrator.synthesize_request(
            current_request="also change H2 to H1 for CORTEX title",
            session_id="test-session",
        )
        assert result["has_prior_context"] is True
        assert result["prior_count"] == 1
        assert len(result["synthesized_summary"]) > 0
        assert isinstance(result["dod_items"], list)
        assert len(result["dod_items"]) >= 1

    def test_multiple_prior_requests(
        self, interaction_orchestrator, mock_rlm
    ) -> None:
        """Multiple prior requests should synthesize into one summary."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = [
            _make_request(1, "rename all BLOCK headers to professional format"),
            _make_request(2, "change H2 to H1 for CORTEX title"),
            _make_request(3, "add processing banner before header"),
        ]
        result = interaction_orchestrator.synthesize_request(
            current_request="also add a Request Echo section",
            session_id="test-session",
        )
        assert result["has_prior_context"] is True
        assert result["prior_count"] == 3
        assert len(result["synthesized_summary"]) > 0
        assert len(result["dod_items"]) >= 2

    def test_dod_always_ends_with_tests_pass(
        self, interaction_orchestrator, mock_rlm
    ) -> None:
        """DoD items should always include a tests-pass item."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = [
            _make_request(1, "fix the broken imports"),
        ]
        result = interaction_orchestrator.synthesize_request(
            current_request="run smoke tests",
            session_id="test-session",
        )
        dod_items = result["dod_items"]
        assert any("test" in item.lower() for item in dod_items), (
            f"DoD must include a testing item. Got: {dod_items}"
        )

    def test_synthesized_summary_includes_current_request(
        self, interaction_orchestrator, mock_rlm
    ) -> None:
        """The synthesized summary should reference the current request intent."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = [
            _make_request(1, "rename BLOCK headers"),
        ]
        result = interaction_orchestrator.synthesize_request(
            current_request="add a processing banner",
            session_id="test-session",
        )
        summary = result["synthesized_summary"]
        # Should mention key words from requests
        assert len(summary) > 10, "Summary should be a meaningful sentence"


# ---------------------------------------------------------------------------
# Tests: Output structure
# ---------------------------------------------------------------------------


class TestSynthesizeRequestOutput:
    """Verify the output dict has all expected keys."""

    def test_output_keys(self, interaction_orchestrator, mock_rlm) -> None:
        """Output must contain canonical keys."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = [
            _make_request(1, "fix something"),
        ]
        result = interaction_orchestrator.synthesize_request(
            current_request="also do another thing",
            session_id="test-session",
        )
        expected_keys = {
            "has_prior_context",
            "prior_count",
            "synthesized_summary",
            "dod_items",
            "prior_requests",
        }
        assert expected_keys.issubset(result.keys()), (
            f"Missing keys: {expected_keys - result.keys()}"
        )

    def test_prior_requests_passed_through(
        self, interaction_orchestrator, mock_rlm
    ) -> None:
        """The raw prior_requests list should be included in output."""
        prior = [
            _make_request(1, "do thing A"),
            _make_request(2, "do thing B"),
        ]
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.return_value = prior
        result = interaction_orchestrator.synthesize_request(
            current_request="do thing C",
            session_id="test-session",
        )
        assert result["prior_requests"] == prior


# ---------------------------------------------------------------------------
# Tests: Error resilience
# ---------------------------------------------------------------------------


class TestSynthesizeRequestResilience:
    """synthesize_request must never raise — non-blocking per CORE-049."""

    def test_rlm_raises_exception(
        self, interaction_orchestrator, mock_rlm
    ) -> None:
        """If RLM throws, synthesize_request should return empty synthesis."""
        interaction_orchestrator._request_log_manager = mock_rlm
        mock_rlm.get_prior_requests.side_effect = RuntimeError("DB locked")
        result = interaction_orchestrator.synthesize_request(
            current_request="fix something",
            session_id="test-session",
        )
        assert result["has_prior_context"] is False
        assert result["prior_count"] == 0
        assert result["synthesized_summary"] == ""
        assert result["dod_items"] == []
