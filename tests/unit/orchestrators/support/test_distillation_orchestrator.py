"""
Sub-phase 129-b RED tests — DistillationOrchestrator.

TDD contract (CORE-008): tests MUST fail before implementation.
Run RED gate:  python3 -m pytest tests/unit/orchestrators/support/test_distillation_orchestrator.py -v
Run GREEN gate: same after creating cortex/orchestrators/support/distillation_orchestrator.py
"""

from __future__ import annotations

import pytest


# ---------------------------------------------------------------------------
# Import guard — these all fail until the module is created
# ---------------------------------------------------------------------------

def _import_module():
    from cortex.orchestrators.support.distillation_orchestrator import (
        DistillationOrchestrator,
        DistillationResult,
        ConversationSegment,
        SegmentType,
        IntentGraph,
    )
    return DistillationOrchestrator, DistillationResult, ConversationSegment, SegmentType, IntentGraph


class TestDistillationOrchestratorImports:
    """Module must be importable with all public symbols."""

    def test_distillation_orchestrator_importable(self):
        """DistillationOrchestrator must be importable from the support package."""
        DistillationOrchestrator, *_ = _import_module()
        assert DistillationOrchestrator is not None

    def test_distillation_result_importable(self):
        """DistillationResult dataclass must be importable."""
        _, DistillationResult, *_ = _import_module()
        assert DistillationResult is not None

    def test_conversation_segment_importable(self):
        """ConversationSegment dataclass must be importable."""
        _, _, ConversationSegment, *_ = _import_module()
        assert ConversationSegment is not None

    def test_segment_type_importable(self):
        """SegmentType enum must be importable."""
        _, _, _, SegmentType, _ = _import_module()
        assert SegmentType is not None

    def test_intent_graph_importable(self):
        """IntentGraph dataclass must be importable."""
        *_, IntentGraph = _import_module()
        assert IntentGraph is not None


class TestDistillationOrchestratorProtocol:
    """DistillationOrchestrator must satisfy OrchestratorProtocolMixin."""

    def test_inherits_protocol_mixin(self):
        """Must inherit OrchestratorProtocolMixin."""
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        DistillationOrchestrator, *_ = _import_module()
        assert issubclass(DistillationOrchestrator, OrchestratorProtocolMixin)

    def test_inherits_workflow_enforcement_mixin(self):
        """Must inherit WorkflowEnforcementMixin."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        DistillationOrchestrator, *_ = _import_module()
        assert issubclass(DistillationOrchestrator, WorkflowEnforcementMixin)

    def test_has_distill_method(self):
        """Must expose a public `distill` method."""
        DistillationOrchestrator, *_ = _import_module()
        assert callable(getattr(DistillationOrchestrator, "distill", None))

    def test_has_health_check_method(self):
        """Must expose `health_check` for HealthOrchestrator registration."""
        DistillationOrchestrator, *_ = _import_module()
        assert callable(getattr(DistillationOrchestrator, "health_check", None))


class TestSegmentTypeEnum:
    """SegmentType must define the correct members."""

    def test_segment_type_has_goal(self):
        _, _, _, SegmentType, _ = _import_module()
        assert hasattr(SegmentType, "GOAL")

    def test_segment_type_has_decision(self):
        _, _, _, SegmentType, _ = _import_module()
        assert hasattr(SegmentType, "DECISION")

    def test_segment_type_has_constraint(self):
        _, _, _, SegmentType, _ = _import_module()
        assert hasattr(SegmentType, "CONSTRAINT")

    def test_segment_type_has_context(self):
        _, _, _, SegmentType, _ = _import_module()
        assert hasattr(SegmentType, "CONTEXT")

    def test_segment_type_has_noise(self):
        _, _, _, SegmentType, _ = _import_module()
        assert hasattr(SegmentType, "NOISE")


class TestDistillationResultDataclass:
    """DistillationResult must expose expected fields."""

    def test_result_has_success_field(self):
        _, DistillationResult, *_ = _import_module()
        r = DistillationResult()
        assert hasattr(r, "success")

    def test_result_has_distilled_prompt_field(self):
        _, DistillationResult, *_ = _import_module()
        r = DistillationResult()
        assert hasattr(r, "distilled_prompt")

    def test_result_has_segment_count_field(self):
        _, DistillationResult, *_ = _import_module()
        r = DistillationResult()
        assert hasattr(r, "segment_count")

    def test_result_has_noise_ratio_field(self):
        _, DistillationResult, *_ = _import_module()
        r = DistillationResult()
        assert hasattr(r, "noise_ratio")

    def test_result_has_error_message_field(self):
        _, DistillationResult, *_ = _import_module()
        r = DistillationResult()
        assert hasattr(r, "error_message")

    def test_result_defaults_success_false(self):
        _, DistillationResult, *_ = _import_module()
        r = DistillationResult()
        assert r.success is False

    def test_result_to_dict_method(self):
        _, DistillationResult, *_ = _import_module()
        r = DistillationResult()
        d = r.to_dict()
        assert isinstance(d, dict)
        assert "success" in d
        assert "distilled_prompt" in d


class TestDistillationOrchestratorDistillMethod:
    """distill() must return a DistillationResult with valid defaults on empty input."""

    def test_distill_returns_distillation_result(self):
        DistillationOrchestrator, DistillationResult, *_ = _import_module()
        orch = DistillationOrchestrator()
        result = orch.distill(conversation="")
        assert isinstance(result, DistillationResult)

    def test_distill_empty_input_fails_gracefully(self):
        DistillationOrchestrator, DistillationResult, *_ = _import_module()
        orch = DistillationOrchestrator()
        result = orch.distill(conversation="")
        # Empty conversation — success=False with an error message
        assert result.success is False
        assert result.error_message is not None

    def test_distill_with_valid_conversation(self):
        DistillationOrchestrator, DistillationResult, *_ = _import_module()
        orch = DistillationOrchestrator()
        conversation = (
            "User: I want to build a REST API for managing tasks.\n"
            "Agent: Sure, shall we use FastAPI?\n"
            "User: Yes. It must support JWT auth and have a Postgres backend.\n"
            "Agent: Understood. Any rate-limiting requirements?\n"
            "User: No. Keep it simple.\n"
        )
        result = orch.distill(conversation=conversation)
        assert isinstance(result, DistillationResult)
        assert result.success is True
        assert isinstance(result.distilled_prompt, str)
        assert len(result.distilled_prompt) > 0
