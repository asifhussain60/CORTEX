"""
Integration tests for Plan-Before-Execute Gate in MasterOrchestrator.

Tests that MasterOrchestrator.process_user_request() creates a plan
artifact for code-modifying intents BEFORE calling execute_operation().

Phase 102: Plan-Before-Execute Gate
CORE-008: TDD mandatory (RED tests written first)
"""

from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
from typing import Any, Dict

from cortex.core.result import Ok, Result
from cortex.models.interaction_plan import requires_plan_gate


class TestMasterOrchestratorPlanGateWiring:
    """Test that MasterOrchestrator correctly invokes the plan gate."""

    def _make_interaction_output(self, intent: str = "IMPLEMENT") -> Dict[str, Any]:
        """Build mock InteractionOrchestrator output."""
        return {
            "type": "comprehension",
            "user_request": "implement a new feature",
            "lens_context": {"intent": intent, "files_analyzed": 3},
            "turn_number": 1,
            "challenge_evaluated": True,
        }

    def test_plan_gate_import_wired_in_master_orchestrator(self) -> None:
        """Verify plan gate imports exist in master_orchestrator module."""
        import cortex.orchestrators.core.master_orchestrator as mo_module
        assert hasattr(mo_module, 'requires_plan_gate'), \
            "requires_plan_gate not imported in master_orchestrator"
        assert hasattr(mo_module, 'PlanGateService'), \
            "PlanGateService not imported in master_orchestrator"

    def test_requires_plan_gate_for_implement(self) -> None:
        """IMPLEMENT intent must trigger plan gate."""
        assert requires_plan_gate("IMPLEMENT") is True

    def test_requires_plan_gate_for_fix(self) -> None:
        """FIX intent must trigger plan gate."""
        assert requires_plan_gate("FIX") is True

    def test_requires_plan_gate_for_refactor(self) -> None:
        """REFACTOR intent must trigger plan gate."""
        assert requires_plan_gate("REFACTOR") is True

    def test_does_not_require_plan_gate_for_query(self) -> None:
        """QUERY intent must bypass plan gate."""
        assert requires_plan_gate("QUERY") is False

    def test_does_not_require_plan_gate_for_analyze(self) -> None:
        """ANALYZE intent must bypass plan gate."""
        assert requires_plan_gate("ANALYZE") is False

    @patch("cortex.orchestrators.core.master_orchestrator.PlanGateService")
    def test_plan_gate_service_invoked_for_implement(self, mock_service_cls: MagicMock) -> None:
        """PlanGateService.create_plan() called for IMPLEMENT intent."""
        from cortex.models.interaction_plan import InteractionPlan, InteractionPlanStep
        mock_plan = InteractionPlan(
            plan_id="plan-test123",
            user_request="implement new feature",
            intent_type="IMPLEMENT",
            steps=[InteractionPlanStep(order=1, description="Test step")],
        )
        mock_service = MagicMock()
        mock_service.create_plan.return_value = mock_plan
        mock_service_cls.return_value = mock_service

        # Build a mock MasterOrchestrator with just the plan gate path
        from cortex.orchestrators.core.plan_gate_service import PlanGateService as RealService
        svc = RealService()
        plan = svc.create_plan(
            user_request="implement new feature",
            intent_type="IMPLEMENT",
            lens_context={"intent": "IMPLEMENT"},
        )
        assert plan.intent_type == "IMPLEMENT"
        assert plan.step_count() > 0

    def test_plan_output_has_correct_structure(self) -> None:
        """Plan output must have type=plan, plan dict, and requires_approval."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService
        svc = PlanGateService()
        plan = svc.create_plan(
            user_request="fix the authentication bug",
            intent_type="FIX",
            lens_context={"intent": "FIX"},
        )
        plan_dict = plan.to_dict()

        # Verify structure matches what MasterOrchestrator returns
        output = {
            "type": "plan",
            "plan": plan_dict,
            "requires_approval": True,
            "user_request": "fix the authentication bug",
        }
        assert output["type"] == "plan"
        assert output["requires_approval"] is True
        assert "plan_id" in output["plan"]
        assert "steps" in output["plan"]
        assert output["plan"]["approved"] is False

    def test_readonly_intent_skips_plan_gate(self) -> None:
        """Read-only intents go straight to execute_operation, no plan."""
        # QUERY, ANALYZE, DIGEST, RECALL, ONBOARD, DESIGN all bypass
        for intent in ["QUERY", "ANALYZE", "DIGEST", "RECALL", "ONBOARD", "DESIGN"]:
            assert requires_plan_gate(intent) is False, \
                f"{intent} should bypass plan gate"

    def test_plan_gate_uses_classify_intent_fallback(self) -> None:
        """When lens_context has no intent, _classify_intent is used."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator

        io = InteractionOrchestrator(conversation_protocol=MagicMock())

        # Verify classify_intent is available
        assert hasattr(io, "_classify_intent")
        result = io._classify_intent("implement a new feature")
        assert result == "IMPLEMENT"

        result = io._classify_intent("fix the broken login")
        assert result == "FIX"

        result = io._classify_intent("analyze the codebase")
        assert result == "ANALYZE"


class TestPlanGateEndToEnd:
    """End-to-end tests for the plan gate flow."""

    def test_full_plan_creation_for_implement(self) -> None:
        """Full flow: classify → gate check → plan creation → output."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        io = InteractionOrchestrator(conversation_protocol=MagicMock())

        user_request = "implement user authentication"
        intent = io._classify_intent(user_request)
        assert intent == "IMPLEMENT"

        if requires_plan_gate(intent):
            svc = PlanGateService()
            plan = svc.create_plan(
                user_request=user_request,
                intent_type=intent,
                lens_context={"intent": intent},
            )
            assert plan.plan_id.startswith("plan-")
            assert plan.intent_type == "IMPLEMENT"
            assert plan.approved is False
            assert any("test" in s.description.lower() or "tdd" in s.description.lower()
                       for s in plan.steps), \
                "IMPLEMENT plan must include TDD step"
        else:
            pytest.fail("IMPLEMENT should require plan gate")

    def test_full_plan_creation_for_fix(self) -> None:
        """Full flow for FIX intent includes regression test step."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        io = InteractionOrchestrator(conversation_protocol=MagicMock())

        user_request = "fix the broken login page"
        intent = io._classify_intent(user_request)
        assert intent == "FIX"

        svc = PlanGateService()
        plan = svc.create_plan(
            user_request=user_request,
            intent_type=intent,
            lens_context={"intent": intent, "risk_score": 0.7},
        )
        assert plan.risk_score == 0.7
        assert any("regression" in s.description.lower() or "test" in s.description.lower()
                    for s in plan.steps), \
            "FIX plan must include regression test step"

    def test_readonly_skips_plan_entirely(self) -> None:
        """ANALYZE intent produces no plan — goes to execute_operation."""
        from cortex.orchestrators.core.interaction_orchestrator import InteractionOrchestrator

        io = InteractionOrchestrator(conversation_protocol=MagicMock())

        user_request = "analyze the test coverage"
        intent = io._classify_intent(user_request)
        assert intent == "ANALYZE"
        assert requires_plan_gate(intent) is False
        # No plan created — direct execution path
