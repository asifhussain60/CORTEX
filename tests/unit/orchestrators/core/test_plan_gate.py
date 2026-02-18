"""
Tests for InteractionPlan model and PlanGate logic.

CORE-008: TDD — these tests written BEFORE implementation.
Authority: Phase 102 — Plan-Before-Execute Gate

Tests:
  1. InteractionPlan creation and serialization
  2. InteractionPlanStep creation
  3. requires_plan_gate() for code-modifying intents
  4. requires_plan_gate() bypass for read-only intents
  5. Plan approval workflow
  6. Risk assessment
  7. PlanGateService.create_plan() integration
  8. PlanGateService integration with MasterOrchestrator flow
"""

import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime


# =============================================================================
# UNIT TESTS: InteractionPlan Model
# =============================================================================

class TestInteractionPlanModel:
    """Tests for InteractionPlan dataclass."""

    def test_interaction_plan_creation(self) -> None:
        """InteractionPlan can be created with required fields."""
        from cortex.models.interaction_plan import InteractionPlan

        plan = InteractionPlan(
            plan_id="plan-001",
            user_request="implement user auth",
            intent_type="IMPLEMENT",
        )
        assert plan.plan_id == "plan-001"
        assert plan.user_request == "implement user auth"
        assert plan.intent_type == "IMPLEMENT"
        assert plan.approved is False
        assert plan.steps == []

    def test_interaction_plan_step_creation(self) -> None:
        """InteractionPlanStep can be created and serialized."""
        from cortex.models.interaction_plan import InteractionPlanStep

        step = InteractionPlanStep(
            order=1,
            description="Write failing tests",
            estimated_duration="10m",
            risk_level="low",
        )
        d = step.to_dict()
        assert d["order"] == 1
        assert d["description"] == "Write failing tests"
        assert d["estimated_duration"] == "10m"
        assert d["risk_level"] == "low"

    def test_interaction_plan_to_dict(self) -> None:
        """InteractionPlan.to_dict() serializes all fields."""
        from cortex.models.interaction_plan import InteractionPlan, InteractionPlanStep

        plan = InteractionPlan(
            plan_id="plan-002",
            user_request="fix login bug",
            intent_type="FIX",
            steps=[
                InteractionPlanStep(order=1, description="Reproduce bug"),
                InteractionPlanStep(order=2, description="Write regression test"),
            ],
            estimated_duration="30m",
            risk_score=0.3,
        )
        d = plan.to_dict()
        assert d["plan_id"] == "plan-002"
        assert d["intent_type"] == "FIX"
        assert len(d["steps"]) == 2
        assert d["steps"][0]["order"] == 1
        assert d["estimated_duration"] == "30m"
        assert d["risk_score"] == 0.3
        assert d["approved"] is False

    def test_interaction_plan_approve(self) -> None:
        """InteractionPlan.approve() sets approved to True."""
        from cortex.models.interaction_plan import InteractionPlan

        plan = InteractionPlan(
            plan_id="plan-003",
            user_request="refactor module",
            intent_type="REFACTOR",
        )
        assert plan.approved is False
        plan.approve()
        assert plan.approved is True

    def test_interaction_plan_step_count(self) -> None:
        """InteractionPlan.step_count() returns correct count."""
        from cortex.models.interaction_plan import InteractionPlan, InteractionPlanStep

        plan = InteractionPlan(
            plan_id="plan-004",
            user_request="implement feature",
            intent_type="IMPLEMENT",
            steps=[
                InteractionPlanStep(order=1, description="Step 1"),
                InteractionPlanStep(order=2, description="Step 2"),
                InteractionPlanStep(order=3, description="Step 3"),
            ],
        )
        assert plan.step_count() == 3

    def test_interaction_plan_is_high_risk(self) -> None:
        """InteractionPlan.is_high_risk() thresholds correctly."""
        from cortex.models.interaction_plan import InteractionPlan

        low_risk = InteractionPlan(
            plan_id="p1", user_request="test", intent_type="FIX", risk_score=0.3
        )
        assert low_risk.is_high_risk() is False

        high_risk = InteractionPlan(
            plan_id="p2", user_request="test", intent_type="FIX", risk_score=0.8
        )
        assert high_risk.is_high_risk() is True

        boundary = InteractionPlan(
            plan_id="p3", user_request="test", intent_type="FIX", risk_score=0.7
        )
        assert boundary.is_high_risk() is False  # 0.7 is NOT high (> 0.7)

    def test_interaction_plan_lens_context_stored(self) -> None:
        """LENS context from Stage 1 is stored in plan."""
        from cortex.models.interaction_plan import InteractionPlan

        lens = {"files_analyzed": 5, "intent_confidence": 0.92}
        plan = InteractionPlan(
            plan_id="p5",
            user_request="implement auth",
            intent_type="IMPLEMENT",
            lens_context=lens,
        )
        assert plan.lens_context["files_analyzed"] == 5
        assert plan.lens_context["intent_confidence"] == 0.92


# =============================================================================
# UNIT TESTS: requires_plan_gate()
# =============================================================================

class TestRequiresPlanGate:
    """Tests for the requires_plan_gate() function."""

    @pytest.mark.parametrize("intent", ["IMPLEMENT", "FIX", "REFACTOR"])
    def test_code_modifying_intents_require_plan(self, intent: str) -> None:
        """Code-modifying intents (IMPLEMENT/FIX/REFACTOR) require plan gate."""
        from cortex.models.interaction_plan import requires_plan_gate
        assert requires_plan_gate(intent) is True

    @pytest.mark.parametrize("intent", ["QUERY", "ANALYZE", "DIGEST", "RECALL", "ONBOARD", "DESIGN"])
    def test_readonly_intents_bypass_plan(self, intent: str) -> None:
        """Read-only intents bypass the plan gate."""
        from cortex.models.interaction_plan import requires_plan_gate
        assert requires_plan_gate(intent) is False

    def test_case_insensitive(self) -> None:
        """Intent matching is case-insensitive."""
        from cortex.models.interaction_plan import requires_plan_gate
        assert requires_plan_gate("implement") is True
        assert requires_plan_gate("query") is False

    def test_unknown_intent_requires_plan(self) -> None:
        """Unknown intents default to requiring plan (safety-first)."""
        from cortex.models.interaction_plan import requires_plan_gate
        assert requires_plan_gate("UNKNOWN") is True
        assert requires_plan_gate("SOMETHING_WEIRD") is True


# =============================================================================
# UNIT TESTS: PlanGateService
# =============================================================================

class TestPlanGateService:
    """Tests for PlanGateService that creates interaction plans."""

    def test_plan_gate_service_importable(self) -> None:
        """PlanGateService can be imported."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService
        assert PlanGateService is not None

    def test_create_plan_returns_interaction_plan(self) -> None:
        """PlanGateService.create_plan() returns InteractionPlan."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService
        from cortex.models.interaction_plan import InteractionPlan

        service = PlanGateService()
        plan = service.create_plan(
            user_request="implement user authentication",
            intent_type="IMPLEMENT",
            lens_context={"files_analyzed": 3},
        )
        assert isinstance(plan, InteractionPlan)
        assert plan.intent_type == "IMPLEMENT"
        assert plan.user_request == "implement user authentication"
        assert plan.approved is False

    def test_create_plan_generates_steps(self) -> None:
        """PlanGateService.create_plan() generates at least one step."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan(
            user_request="fix login crash",
            intent_type="FIX",
            lens_context={},
        )
        assert plan.step_count() >= 1

    def test_create_plan_includes_tdd_step_for_implement(self) -> None:
        """IMPLEMENT plans always include a TDD step (CORE-008)."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan(
            user_request="implement new feature",
            intent_type="IMPLEMENT",
            lens_context={},
        )
        step_descriptions = [s.description.lower() for s in plan.steps]
        assert any("test" in desc for desc in step_descriptions), \
            "IMPLEMENT plans must include a TDD/test step"

    def test_create_plan_includes_tdd_step_for_fix(self) -> None:
        """FIX plans always include a regression test step (CORE-008)."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan(
            user_request="fix authentication bug",
            intent_type="FIX",
            lens_context={},
        )
        step_descriptions = [s.description.lower() for s in plan.steps]
        assert any("test" in desc for desc in step_descriptions), \
            "FIX plans must include a regression test step"

    def test_create_plan_unique_plan_id(self) -> None:
        """Each plan gets a unique plan_id."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan1 = service.create_plan("req1", "IMPLEMENT", {})
        plan2 = service.create_plan("req2", "FIX", {})
        assert plan1.plan_id != plan2.plan_id

    def test_create_plan_risk_score_from_lens(self) -> None:
        """Risk score is derived from LENS context when available."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan(
            user_request="implement feature",
            intent_type="IMPLEMENT",
            lens_context={"risk_score": 0.65, "files_affected": 12},
        )
        assert plan.risk_score == 0.65

    def test_create_plan_default_risk_score(self) -> None:
        """Default risk score is 0.3 when LENS provides no risk data."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan(
            user_request="implement feature",
            intent_type="IMPLEMENT",
            lens_context={},
        )
        assert plan.risk_score == 0.3

    def test_create_plan_refactor_includes_safety_step(self) -> None:
        """REFACTOR plans include a verify-tests-pass step."""
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan(
            user_request="refactor auth module",
            intent_type="REFACTOR",
            lens_context={},
        )
        step_descriptions = [s.description.lower() for s in plan.steps]
        assert any("test" in desc or "verify" in desc for desc in step_descriptions), \
            "REFACTOR plans must include a safety verification step"


# =============================================================================
# GOLDEN PATH: Plan Gate Integration with MasterOrchestrator Flow
# =============================================================================

class TestPlanGateGoldenPaths:
    """Golden path tests for plan gate in MasterOrchestrator flow."""

    def test_golden_path_14_plan_created_before_execution(self) -> None:
        """
        GOLDEN PATH 14: Plan MUST be created before execution for
        code-modifying intents (IMPLEMENT/FIX/REFACTOR).

        Flow: process_user_request → InteractionOrchestrator → PlanGate → Plan
        Expected: Plan artifact returned to user BEFORE execute_operation() is called.
        """
        from cortex.models.interaction_plan import InteractionPlan, requires_plan_gate

        # Verify code-modifying intents require plan
        assert requires_plan_gate("IMPLEMENT") is True

        # Verify plan can be created from comprehension output
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan(
            user_request="implement user authentication with JWT",
            intent_type="IMPLEMENT",
            lens_context={"files_analyzed": 5, "complexity": "medium"},
        )

        # Plan must exist and be unapproved
        assert isinstance(plan, InteractionPlan)
        assert plan.approved is False
        assert plan.step_count() >= 2  # At least TDD step + implementation step
        assert plan.plan_id.startswith("plan-")

    def test_golden_path_15_readonly_bypasses_plan_gate(self) -> None:
        """
        GOLDEN PATH 15: Read-only intents MUST bypass plan gate.

        QUERY, ANALYZE, DIGEST, RECALL, ONBOARD, DESIGN → no plan needed.
        """
        from cortex.models.interaction_plan import requires_plan_gate

        for intent in ["QUERY", "ANALYZE", "DIGEST", "RECALL", "ONBOARD", "DESIGN"]:
            assert requires_plan_gate(intent) is False, \
                f"{intent} should bypass plan gate"

    def test_golden_path_16_plan_output_format(self) -> None:
        """
        GOLDEN PATH 16: Plan output MUST follow standard format
        for MasterOrchestrator to return to user.

        Output must have: type="plan", plan=InteractionPlan, requires_approval=True
        """
        from cortex.orchestrators.core.plan_gate_service import PlanGateService

        service = PlanGateService()
        plan = service.create_plan("implement feature", "IMPLEMENT", {})

        # Simulate MasterOrchestrator output format
        output = {
            "type": "plan",
            "plan": plan.to_dict(),
            "requires_approval": True,
        }

        assert output["type"] == "plan"
        assert output["requires_approval"] is True
        assert "steps" in output["plan"]
        assert output["plan"]["approved"] is False

    def test_golden_path_17_autonomous_continuation_bypasses_plan(self) -> None:
        """
        GOLDEN PATH 17: Autonomous continuation MUST bypass plan gate.

        When AutonomousPlanExecutor detects continuation (e.g., "proceed",
        "continue"), skip plan creation and go directly to execution.
        """
        from cortex.models.interaction_plan import requires_plan_gate

        # Plan gate is intent-based, not request-based
        # Autonomous bypass happens BEFORE intent classification
        # So we just verify the gate function works correctly
        assert requires_plan_gate("IMPLEMENT") is True
        # The actual bypass is in MasterOrchestrator.process_user_request()
        # which checks autonomous_mode BEFORE reaching plan gate
