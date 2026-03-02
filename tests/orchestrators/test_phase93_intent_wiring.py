"""
Phase 93 — IntentRouter Full-Wiring Tests.

Validates that IntentRouter is fully connected into MasterOrchestrator:
  Cluster 1: Stage2 uses IntentRouter.route() (not missing classify())
  Cluster 2: Stage2 routing map covers all 27 IntentType values
  Cluster 3: Breadcrumb propagates from InteractionOrchestrator → pipeline result
  Cluster 4: InteractionOrchestrator is always active (initialized, not None)

Authority: Phase 93 — CORE-008 (TDD), CORE-064 (Sweep Completeness)
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest


# ═══════════════════════════════════════════════════════════════════════════════
# Cluster 1: Stage2 IntentRouter wiring — must call route(), not classify()
# ═══════════════════════════════════════════════════════════════════════════════


class TestStage2IntentRouterWiring:
    """Stage2 must delegate intent classification to IntentRouter.route()."""

    def test_stage2_classify_calls_router_route_not_classify(self) -> None:
        """Stage2._classify() must call router.route() when router lacks classify()."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )
        from cortex.orchestrators.core.pipeline_stage_strategy import StageContext

        # Simulate real IntentRouter — has route() but not classify()
        mock_router = MagicMock(spec=[])  # empty spec — no classify()
        mock_router.route = MagicMock(return_value=MagicMock(
            intent_type=MagicMock(value="IMPLEMENT"),
            target_handler="TDDOrchestrator",
            confidence_score=0.92,
        ))

        strategy = Stage2IntentClassificationStrategy(
            dependencies={"intent_router": mock_router}
        )
        ctx = StageContext(
            operation_name="create_feature",
            parameters={"request": "implement a new login form"},
            metadata={},
            result=None,
            stage_results={},
        )
        result = strategy.execute(ctx)

        assert result.is_ok(), "Stage2 must not fail when router has no classify()"
        # route() must have been called
        mock_router.route.assert_called_once(), (
            "Stage2 must delegate to router.route() as primary path"
        )

    def test_stage2_passes_request_and_operation_to_route(self) -> None:
        """Stage2 must pass both request text and operation_name into router.route()."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )
        from cortex.orchestrators.core.pipeline_stage_strategy import StageContext

        captured_context: Dict[str, Any] = {}

        mock_router = MagicMock(spec=[])
        def fake_route(ctx: Dict[str, Any]) -> Any:
            captured_context.update(ctx)
            return MagicMock(
                intent_type=MagicMock(value="FIX"),
                target_handler="RefactoringOrchestrator",
                confidence_score=0.88,
            )
        mock_router.route = fake_route

        strategy = Stage2IntentClassificationStrategy(
            dependencies={"intent_router": mock_router}
        )
        ctx = StageContext(
            operation_name="fix_bug",
            parameters={"request": "fix the null pointer in login service"},
            metadata={},
            result=None,
            stage_results={},
        )
        strategy.execute(ctx)

        assert "request" in captured_context or "operation" in captured_context or "user_intent" in captured_context, (
            "Stage2 must pass request/operation context to router.route()"
        )

    def test_stage2_extracts_intent_type_from_routing_decision(self) -> None:
        """Stage2 must extract intent_type.value from RoutingDecision for metadata."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )
        from cortex.orchestrators.core.pipeline_stage_strategy import StageContext

        mock_decision = MagicMock()
        mock_decision.intent_type = MagicMock()
        mock_decision.intent_type.value = "REFACTOR"
        mock_decision.target_handler = "RefactoringOrchestrator"
        mock_decision.confidence_score = 0.91

        mock_router = MagicMock(spec=[])
        mock_router.route = MagicMock(return_value=mock_decision)

        strategy = Stage2IntentClassificationStrategy(
            dependencies={"intent_router": mock_router}
        )
        ctx = StageContext(
            operation_name="refactor_service",
            parameters={"request": "refactor the authentication service"},
            metadata={},
            result=None,
            stage_results={},
        )
        result = strategy.execute(ctx)

        assert result.is_ok()
        classification = result.unwrap().metadata.get("intent_classification", {})
        classified = classification.get("classified_intent", "")
        assert "REFACTOR" in classified.upper() or "refactor" in classified.lower(), (
            f"classified_intent must reflect REFACTOR from RoutingDecision, got: {classified}"
        )

    def test_stage2_routing_target_comes_from_intent_router(self) -> None:
        """Stage2 routing_target must come from IntentRouter, not only hardcoded map."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )
        from cortex.orchestrators.core.pipeline_stage_strategy import StageContext

        mock_decision = MagicMock()
        mock_decision.intent_type = MagicMock()
        mock_decision.intent_type.value = "VACUUM"
        mock_decision.target_handler = "VacuumOrchestrator"
        mock_decision.confidence_score = 0.85

        mock_router = MagicMock(spec=[])
        mock_router.route = MagicMock(return_value=mock_decision)

        strategy = Stage2IntentClassificationStrategy(
            dependencies={"intent_router": mock_router}
        )
        ctx = StageContext(
            operation_name="vacuum",
            parameters={"request": "/vacuum"},
            metadata={},
            result=None,
            stage_results={},
        )
        result = strategy.execute(ctx)

        assert result.is_ok()
        classification = result.unwrap().metadata.get("intent_classification", {})
        routing_target = classification.get("routing_target", "")
        assert routing_target == "VacuumOrchestrator", (
            f"routing_target must be VacuumOrchestrator from IntentRouter, got: {routing_target}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Cluster 2: Stage2 _get_routing_target covers all 27 IntentType values
# ═══════════════════════════════════════════════════════════════════════════════


class TestStage2RoutingCoverage:
    """_get_routing_target must NOT return 'MasterOrchestrator' as a catch-all."""

    @pytest.mark.parametrize("intent,expected_not", [
        ("VACUUM", "MasterOrchestrator"),
        ("DEBUG", "MasterOrchestrator"),
        ("HEALTH", "MasterOrchestrator"),
        ("SYNC", "MasterOrchestrator"),
        ("TRAIN", "MasterOrchestrator"),
        ("TOTALRECALL", "MasterOrchestrator"),
        ("RCA", "MasterOrchestrator"),
        ("IMPLEMENT", "MasterOrchestrator"),
        ("FIX", "MasterOrchestrator"),
        ("REFACTOR", "MasterOrchestrator"),
        ("ANALYZE", "MasterOrchestrator"),
        ("TEST", "MasterOrchestrator"),
        ("AUDIT", "MasterOrchestrator"),
        ("DESIGN", "MasterOrchestrator"),
        ("DOCUMENT", "MasterOrchestrator"),
        ("PLAN", "MasterOrchestrator"),
        ("DIGEST", "MasterOrchestrator"),
        ("INVESTIGATE", "MasterOrchestrator"),
        ("ONBOARD", "MasterOrchestrator"),
    ])
    def test_routing_target_not_master_orchestrator_fallback(
        self, intent: str, expected_not: str
    ) -> None:
        """Every known IntentType must route to a specific orchestrator, not MasterOrchestrator."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )

        strategy = Stage2IntentClassificationStrategy()
        routing_target = strategy._get_routing_target(intent)
        assert routing_target != expected_not, (
            f"Intent '{intent}' fell through to MasterOrchestrator catch-all. "
            f"Add it to _get_routing_target() routing map."
        )

    def test_routing_map_covers_interaction_orchestrator_for_unknown(self) -> None:
        """UNKNOWN/QUERY intents should route to InteractionOrchestrator (LENS default)."""
        from cortex.orchestrators.core.stage234_strategies import (
            Stage2IntentClassificationStrategy,
        )

        strategy = Stage2IntentClassificationStrategy()
        for intent in ("UNKNOWN", "QUERY", "INTERACT"):
            target = strategy._get_routing_target(intent)
            assert target == "InteractionOrchestrator", (
                f"'{intent}' must route to InteractionOrchestrator (LENS default), got: {target}"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Cluster 3: Breadcrumb propagates to pipeline output
# ═══════════════════════════════════════════════════════════════════════════════


class TestBreadcrumbPropagation:
    """Breadcrumb from InteractionOrchestrator must reach Stage1 context metadata."""

    def test_stage1_preserves_breadcrumb_from_interaction_orchestrator(self) -> None:
        """When InteractionOrchestrator returns a breadcrumb, Stage1 stores it in metadata."""
        from cortex.orchestrators.core.stage1_comprehension_strategy import (
            Stage1ComprehensionStrategy,
        )
        from cortex.orchestrators.core.pipeline_stage_strategy import StageContext

        mock_io = MagicMock()
        mock_io.execute = MagicMock(return_value=MagicMock(
            is_ok=lambda: True,
            unwrap=lambda: {
                "intent_type": "IMPLEMENT",
                "lens_context": {"status": "ok"},
                "confidence": 0.9,
                "analysis_complete": True,
                "breadcrumb": "**Route:** `IntentRouter → InteractionOrchestrator`",
            }
        ))

        strategy = Stage1ComprehensionStrategy(
            dependencies={"interaction_orchestrator": mock_io}
        )
        ctx = StageContext(
            operation_name="implement_feature",
            parameters={"request": "add login", "user_intent": "add login"},
            metadata={},
            result=None,
            stage_results={},
        )
        result = strategy.execute(ctx)

        assert result.is_ok()
        metadata = result.unwrap().metadata
        breadcrumb = metadata.get("breadcrumb", "")
        assert breadcrumb.startswith("**Route:**"), (
            f"Stage1 must preserve breadcrumb in metadata. Got: '{breadcrumb}'"
        )

    def test_stage1_uses_interaction_orchestrator_when_provided(self) -> None:
        """Stage1 must call interaction_orchestrator.execute() when available in dependencies."""
        from cortex.orchestrators.core.stage1_comprehension_strategy import (
            Stage1ComprehensionStrategy,
        )
        from cortex.orchestrators.core.pipeline_stage_strategy import StageContext

        mock_io = MagicMock()
        mock_io.execute = MagicMock(return_value=MagicMock(
            is_ok=lambda: True,
            unwrap=lambda: {
                "intent_type": "QUERY",
                "lens_context": {},
                "confidence": 0.8,
                "analysis_complete": True,
                "breadcrumb": "**Route:** `IntentRouter → InteractionOrchestrator`",
            }
        ))

        strategy = Stage1ComprehensionStrategy(
            dependencies={"interaction_orchestrator": mock_io}
        )
        ctx = StageContext(
            operation_name="query",
            parameters={"request": "what does cortex do", "user_intent": "what does cortex do"},
            metadata={},
            result=None,
            stage_results={},
        )
        strategy.execute(ctx)

        mock_io.execute.assert_called_once(), (
            "Stage1 must call interaction_orchestrator.execute() when provided"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Cluster 4: InteractionOrchestrator always active in MasterOrchestrator
# ═══════════════════════════════════════════════════════════════════════════════


class TestInteractionOrchestratorAlwaysActive:
    """InteractionOrchestrator must always be initialized in MasterOrchestrator."""

    def test_master_orchestrator_has_interaction_orchestrator(self) -> None:
        """MasterOrchestrator.interaction_orchestrator must not be None after init."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        assert mo.interaction_orchestrator is not None, (
            "interaction_orchestrator must not be None after MasterOrchestrator.__init__"
        )

    def test_master_orchestrator_has_intent_router(self) -> None:
        """MasterOrchestrator.intent_router must not be None after init."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        assert mo.intent_router is not None, (
            "intent_router must not be None after MasterOrchestrator.__init__"
        )

    def test_interaction_orchestrator_has_execute_turn_with_challenge(self) -> None:
        """InteractionOrchestrator instance must expose execute_turn_with_challenge()."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        assert hasattr(mo.interaction_orchestrator, "execute_turn_with_challenge"), (
            "interaction_orchestrator must expose execute_turn_with_challenge() for Stage 1 LENS"
        )

    def test_interaction_orchestrator_execute_turn_returns_breadcrumb(self) -> None:
        """execute_turn_with_challenge() must emit breadcrumb key in output."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        if not hasattr(mo.interaction_orchestrator, "execute_turn_with_challenge"):
            pytest.skip("interaction_orchestrator lacks execute_turn_with_challenge")

        round_ctx = MagicMock()
        round_ctx.session_id = "test-session"
        result = mo.interaction_orchestrator.execute_turn_with_challenge(
            user_request="confirm wiring",
            round_context=round_ctx,
        )
        assert result.is_ok(), f"execute_turn_with_challenge failed: {result}"
        output = result.unwrap()
        assert "breadcrumb" in output, (
            f"execute_turn_with_challenge output missing 'breadcrumb'. Keys: {list(output.keys())}"
        )
        # SSOT: cortex-response-templates.md §BLOCK-ENGAGEMENT-BREADCRUMB (line 1521)
        # ❌ Never use **Route:** prefix — canonical format is italic *🧭 ... * (compass icon)
        bc = output["breadcrumb"]
        assert bc.startswith("*🧭") or bc == "", (
            f"Breadcrumb must use SSOT italic format '*🧭 ...', got: {bc!r}"
        )
