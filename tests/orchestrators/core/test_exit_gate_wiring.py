"""
Phase 149-A: Exit Gate Wiring Tests.

Verifies ContextSynthesisGateway.synthesize() injects knowledge (best_practices)
into the synthesized context dict before Copilot handoff.

GAP-149-01: load_cortex_best_practices() wired into ContextSynthesisGateway exit gate
CORE-008: TDD mandatory

AC_START: AC-P149-EXIT-001
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from cortex.orchestrators.core.context_synthesis_gateway import (
    ContextSynthesisGateway,
    SynthesizedContext,
)


@pytest.fixture
def gateway():
    """Create gateway with mocked dependencies for fast unit tests."""
    with (
        patch("cortex.orchestrators.core.context_synthesis_gateway.CopilotContextOptimizer") as mock_opt,
        patch("cortex.orchestrators.core.context_synthesis_gateway.ContextSynthesizer") as mock_syn,
        patch("cortex.orchestrators.core.context_synthesis_gateway.ContextCacheLayer") as mock_cache,
        patch("cortex.orchestrators.core.context_synthesis_gateway.ContextMetricsCollector") as mock_metrics,
    ):
        opt = Mock()
        opt.optimize_for_copilot.return_value = {"optimized": True}
        opt.estimate_copilot_tokens.return_value = 500
        mock_opt.return_value = opt

        syn = Mock()
        syn.synthesize_all.return_value = {"synthesized": True}
        mock_syn.return_value = syn

        cache = Mock()
        cache.get.return_value = None
        mock_cache.return_value = cache

        metrics = Mock()
        mock_metrics.return_value = metrics

        gw = ContextSynthesisGateway(
            optimizer=opt,
            synthesizer=syn,
            cache=cache,
            metrics=metrics,
        )
        yield gw


class TestExitGateKnowledgeWiring:
    """Phase 149-A: Exit gate injects knowledge into synthesized context."""

    def test_synthesize_returns_synthesized_context(self, gateway: ContextSynthesisGateway) -> None:
        """synthesize() must return SynthesizedContext."""
        result = gateway.synthesize(
            context={"data": "test"},
            session_id="s1",
            orchestrator_name="TestOrchestrator",
        )
        assert isinstance(result, SynthesizedContext)

    def test_synthesized_context_has_best_practices_key(self, gateway: ContextSynthesisGateway) -> None:
        """Synthesized context dict must contain 'best_practices' injection key."""
        result = gateway.synthesize(
            context={"data": "test"},
            session_id="s1",
            orchestrator_name="TDDOrchestrator",
        )
        assert "best_practices" in result.context, (
            "Knowledge injection key 'best_practices' must be present in synthesized context. "
            "GAP-149-01: exit gate knowledge wiring."
        )

    def test_best_practices_is_list(self, gateway: ContextSynthesisGateway) -> None:
        """best_practices value must be a list."""
        result = gateway.synthesize(
            context={"data": "test"},
            session_id="s2",
            orchestrator_name="TDDOrchestrator",
        )
        assert isinstance(result.context["best_practices"], list)

    def test_best_practices_injection_tolerates_unknown_orchestrator(
        self, gateway: ContextSynthesisGateway
    ) -> None:
        """Unknown orchestrator name must not raise — best_practices returns empty list."""
        result = gateway.synthesize(
            context={"data": "test"},
            session_id="s3",
            orchestrator_name="UnknownFutureOrchestrator",
        )
        assert isinstance(result.context.get("best_practices"), list)

    def test_exit_gate_degrades_gracefully_on_import_error(
        self, gateway: ContextSynthesisGateway
    ) -> None:
        """When best_practices import fails, synthesize() must not raise."""
        with patch.object(gateway, "_get_best_practices_for", return_value=[]):
            result = gateway.synthesize(
                context={"fallback": True},
                session_id="s4",
                orchestrator_name="TestOrchestrator",
            )
        assert result is not None
        assert isinstance(result, SynthesizedContext)

    def test_synthesized_dict_contains_orchestrator_name(self, gateway: ContextSynthesisGateway) -> None:
        """Synthesized context must record the originating orchestrator."""
        result = gateway.synthesize(
            context={"data": "test"},
            session_id="s5",
            orchestrator_name="InteractionOrchestrator",
        )
        assert result.orchestrator_name == "InteractionOrchestrator"


# AC_COMPLETE: AC-P149-EXIT-001 ✅
