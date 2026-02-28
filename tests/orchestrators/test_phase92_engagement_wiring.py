"""
Phase 92: Engagement Block Wiring — RED tests first (CORE-008)

Validates:
1. EngagementRenderer.render_breadcrumb() emits SSOT-compliant format
   (backtick code spans, **Route:** prefix — not **Routing:**)
2. InteractionOrchestrator.execute_turn_with_challenge() includes
   'breadcrumb' key in its output dict
3. EngagementRenderer is callable from MasterOrchestrator context
4. WorkflowComplexityRouter default fallback is InteractionOrchestrator

AC-ID: AC-92-ENGAGEMENT-WIRING
CORE-008: TDD — RED before GREEN
CORE-011: Type hints on all functions
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock


class TestEngagementRendererSSOTCompliance:
    """
    Cluster 1: EngagementRenderer must match SSOT format from
    cortex-response-templates.md §BLOCK-ENGAGEMENT-BREADCRUMB.

    SSOT spec (line 1015):
        **Route:** `IntentRouter → {Orchestrator} → {Sub-orchestrator}`

    Current bug: render_breadcrumb() outputs **Routing:** (wrong prefix)
    and no backtick code spans.
    """

    def test_render_breadcrumb_uses_route_prefix(self) -> None:
        """render_breadcrumb() must start with '**Route:**' not '**Routing:**'."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert result.startswith("**Route:**"), (
            f"Expected '**Route:**' prefix (SSOT §BLOCK-ENGAGEMENT-BREADCRUMB), "
            f"got: {result!r}"
        )

    def test_render_breadcrumb_uses_backtick_code_spans(self) -> None:
        """render_breadcrumb() must wrap the routing chain in backtick code spans."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.render_breadcrumb(["IntentRouter", "TDDOrchestrator"])
        assert "`" in result, (
            f"Expected backtick code spans around routing chain (SSOT line 1020), "
            f"got: {result!r}"
        )

    def test_render_breadcrumb_full_ssot_format(self) -> None:
        """render_breadcrumb() must produce the exact SSOT format."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.render_breadcrumb(["IntentRouter", "RefactoringOrchestrator"])
        # SSOT: **Route:** `IntentRouter → {Orchestrator}`
        expected = "**Route:** `IntentRouter → RefactoringOrchestrator`"
        assert result == expected, (
            f"Expected SSOT-compliant breadcrumb, got: {result!r}"
        )

    def test_render_breadcrumb_three_hops(self) -> None:
        """Three-hop chain renders correctly with backtick span."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.render_breadcrumb(
            ["IntentRouter", "MasterOrchestrator", "TDDOrchestrator"]
        )
        expected = "**Route:** `IntentRouter → MasterOrchestrator → TDDOrchestrator`"
        assert result == expected

    def test_render_breadcrumb_empty_returns_empty_string(self) -> None:
        """Empty chain returns empty string (single-hop omit rule)."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.render_breadcrumb([])
        assert result == ""

    def test_breadcrumb_for_command_uses_route_prefix(self) -> None:
        """breadcrumb_for_command() must also use **Route:** prefix."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.breadcrumb_for_command("audit")
        assert result.startswith("**Route:**"), (
            f"Expected '**Route:**' prefix, got: {result!r}"
        )

    def test_breadcrumb_for_command_audit_chain_has_backticks(self) -> None:
        """audit breadcrumb includes backtick code spans."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.breadcrumb_for_command("audit")
        assert "`" in result

    def test_breadcrumb_for_implement_shows_tdd_orchestrator(self) -> None:
        """implement command chain routes through TDDOrchestrator."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.breadcrumb_for_command("implement")
        assert "TDDOrchestrator" in result

    def test_breadcrumb_for_health_shows_health_orchestrator(self) -> None:
        """health command chain routes through HealthOrchestrator."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.breadcrumb_for_command("health")
        assert "HealthOrchestrator" in result

    def test_breadcrumb_for_debug_shows_debugger_orchestrator(self) -> None:
        """debug command chain routes through DebuggerOrchestrator."""
        from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
        renderer = EngagementRenderer()
        result = renderer.breadcrumb_for_command("debug")
        assert "DebuggerOrchestrator" in result


class TestInteractionOrchestratorBreadcrumbOutput:
    """
    Cluster 2: InteractionOrchestrator.execute_turn_with_challenge()
    must include a 'breadcrumb' key in its Ok output dict so
    MasterOrchestrator can surface it directly in Copilot Chat.

    The breadcrumb must be the SSOT-compliant string from EngagementRenderer.
    """

    def test_execute_turn_returns_breadcrumb_key(self) -> None:
        """execute_turn_with_challenge() output dict must have 'breadcrumb' key."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(
            conversation_protocol=mock_protocol,
            enable_challenges=False,
        )

        mock_round_ctx = MagicMock()
        result = orchestrator.execute_turn_with_challenge(
            user_request="implement a login endpoint",
            round_context=mock_round_ctx,
        )

        assert result.is_ok(), f"Expected Ok result, got: {result}"
        output = result.unwrap()
        assert "breadcrumb" in output, (
            f"Output dict missing 'breadcrumb' key. Keys present: {list(output.keys())}"
        )

    def test_execute_turn_breadcrumb_is_ssot_compliant(self) -> None:
        """breadcrumb value in output must match SSOT **Route:** format."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(
            conversation_protocol=mock_protocol,
            enable_challenges=False,
        )

        mock_round_ctx = MagicMock()
        result = orchestrator.execute_turn_with_challenge(
            user_request="fix the authentication bug",
            round_context=mock_round_ctx,
        )

        output = result.unwrap()
        breadcrumb = output.get("breadcrumb", "")
        assert breadcrumb.startswith("**Route:**"), (
            f"Breadcrumb must start with '**Route:**' (SSOT), got: {breadcrumb!r}"
        )
        assert "`" in breadcrumb, (
            f"Breadcrumb must use backtick code spans (SSOT), got: {breadcrumb!r}"
        )
        assert "InteractionOrchestrator" in breadcrumb, (
            f"Breadcrumb must name InteractionOrchestrator, got: {breadcrumb!r}"
        )

    def test_execute_returns_breadcrumb_key(self) -> None:
        """execute() also returns 'breadcrumb' key for single-step operations."""
        from cortex.orchestrators.core.interaction_orchestrator import (
            InteractionOrchestrator,
        )

        mock_protocol = MagicMock()
        orchestrator = InteractionOrchestrator(
            conversation_protocol=mock_protocol,
            enable_challenges=False,
        )

        result = orchestrator.execute({"user_intent": "audit the repo"})
        assert result.is_ok()
        output = result.unwrap()
        assert "breadcrumb" in output, (
            f"execute() output missing 'breadcrumb'. Keys: {list(output.keys())}"
        )


class TestWorkflowGateInteractionDefault:
    """
    Cluster 3: WorkflowComplexityRouter must route unknown operations
    to InteractionOrchestrator (confirmed Phase 89 change).
    """

    def test_unknown_operation_defaults_to_interaction_orchestrator(self) -> None:
        """Unknown operations fall back to InteractionOrchestrator for LENS."""
        from cortex.orchestrators.core.intent_router.workflow_gate import (
            WorkflowComplexityRouter,
        )
        from cortex.orchestrators.core.intent_router import Intent
        from cortex.models.canonical_enums import IntentType

        router = WorkflowComplexityRouter()
        intent = Intent(
            intent_type=IntentType.UNKNOWN,
            confidence=0.0,
            operation_type="completely_unknown_xyz",
            metadata={},
        )
        result = router.evaluate(intent)
        assert result.orchestrator == "InteractionOrchestrator", (
            f"Default fallback must be InteractionOrchestrator, got: {result.orchestrator}"
        )

    def test_interact_operation_routes_to_interaction_orchestrator(self) -> None:
        """'interact' operation explicitly routes to InteractionOrchestrator."""
        from cortex.orchestrators.core.intent_router.workflow_gate import (
            WorkflowComplexityRouter,
        )
        from cortex.orchestrators.core.intent_router import Intent
        from cortex.models.canonical_enums import IntentType

        router = WorkflowComplexityRouter()
        intent = Intent(
            intent_type=IntentType.QUERY,
            confidence=0.8,
            operation_type="interact",
            metadata={},
        )
        result = router.evaluate(intent)
        assert result.orchestrator == "InteractionOrchestrator"

    def test_query_operation_routes_to_interaction_orchestrator(self) -> None:
        """'query' operation routes to InteractionOrchestrator for LENS comprehension."""
        from cortex.orchestrators.core.intent_router.workflow_gate import (
            WorkflowComplexityRouter,
        )
        from cortex.orchestrators.core.intent_router import Intent
        from cortex.models.canonical_enums import IntentType

        router = WorkflowComplexityRouter()
        intent = Intent(
            intent_type=IntentType.QUERY,
            confidence=0.75,
            operation_type="query",
            metadata={},
        )
        result = router.evaluate(intent)
        assert result.orchestrator == "InteractionOrchestrator"
