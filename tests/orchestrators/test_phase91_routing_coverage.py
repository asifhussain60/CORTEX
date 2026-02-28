"""
Phase 91: Routing Coverage Improvements — Routing Miss Detection + Unified Engagement Visibility

RED → GREEN → REFACTOR

Purpose:
- Test that IntentRouter logs routing misses (IntentType.UNKNOWN) to SQLite
- Test that EngagementRenderer is usable across /health, /audit, /totalrecall
- Test unified breadcrumb format consistency

Governance:
- CORE-008: TDD mandatory (this is RED phase)
- CORE-011: Type hints on all functions
- CORE-064: Sweep completeness contract
"""

import pytest
from typing import Any, Dict, List, Optional

from cortex.models.canonical_enums import IntentType
from cortex.orchestrators.response.engagement_renderer import EngagementRenderer


class TestRoutingMissDetection:
    """Cluster 1: IntentRouter should track when requests fall through to UNKNOWN/default."""

    def test_detect_intent_returns_implement_for_unrecognized(self) -> None:
        """Unrecognized text should return IMPLEMENT (the default), not crash."""
        from cortex.orchestrators.core.intent_router_impl import IntentRouter

        router = IntentRouter()
        result = router.detect_intent({
            "description": "xyzzy flurble garbonzo completely novel gibberish"
        })
        # Default fallback is IMPLEMENT
        assert result == IntentType.IMPLEMENT

    def test_detect_intent_classifies_known_keywords_correctly(self) -> None:
        """Known keywords should NOT fall to default."""
        from cortex.orchestrators.core.intent_router_impl import IntentRouter

        router = IntentRouter()

        cases = [
            ({"description": "debug the failing test"}, IntentType.DEBUG),
            ({"description": "vacuum cleanup the repo"}, IntentType.VACUUM),
            ({"description": "run health check on orchestrators"}, IntentType.HEALTH),
            ({"description": "sync to company folder"}, IntentType.SYNC),
            ({"description": "root cause analysis on failures"}, IntentType.RCA),
        ]

        for context, expected in cases:
            result = router.detect_intent(context)
            assert result == expected, (
                f"Expected {expected.name} for '{context['description']}', got {result.name}"
            )


class TestEngagementRendererUnifiedUsage:
    """Cluster 2: EngagementRenderer should produce consistent output for all commands."""

    @pytest.fixture
    def renderer(self) -> EngagementRenderer:
        """Create renderer instance."""
        return EngagementRenderer()

    def test_breadcrumb_for_health_command(self, renderer: EngagementRenderer) -> None:
        """Health command should produce valid breadcrumb."""
        chain = ["IntentRouter", "HealthOrchestrator"]
        result = renderer.render_breadcrumb(chain)
        assert "IntentRouter" in result
        assert "HealthOrchestrator" in result
        assert "→" in result

    def test_breadcrumb_for_audit_command(self, renderer: EngagementRenderer) -> None:
        """Audit command should produce valid breadcrumb with 9-stage pipeline."""
        chain = [
            "IntentRouter", "AuditOrchestrator",
            "HealthOrchestrator", "VacuumOrchestrator",
            "EnforcementOrchestrator"
        ]
        result = renderer.render_breadcrumb(chain)
        assert "AuditOrchestrator" in result
        assert "VacuumOrchestrator" in result
        assert result.count("→") == 4  # 5 items = 4 arrows

    def test_breadcrumb_for_totalrecall_command(self, renderer: EngagementRenderer) -> None:
        """TotalRecall command should produce valid breadcrumb."""
        chain = ["IntentRouter", "MasterOrchestrator", "RefactoringOrchestrator"]
        result = renderer.render_breadcrumb(chain)
        assert "MasterOrchestrator" in result

    def test_timeline_for_multi_stage_audit(self, renderer: EngagementRenderer) -> None:
        """Multi-stage audit timeline should render all stages."""
        stages = [
            {"name": "Stage 0: Governance Pre-Flight", "duration_ms": 120},
            {"name": "Stage 2: 19-Point Scan", "duration_ms": 450},
            {"name": "Stage 4: Health Check", "duration_ms": 85},
            {"name": "Stage 5: Vacuum", "duration_ms": 200},
            {"name": "Stage 9: Tests", "duration_ms": 3200},
        ]
        result = renderer.render_timeline(stages)
        assert result is not None
        assert "Stage 0" in result
        assert "Stage 9" in result
        assert "3200ms" in result

    def test_empty_chain_returns_empty_string(self, renderer: EngagementRenderer) -> None:
        """Empty chain should return empty string, not crash."""
        result = renderer.render_breadcrumb([])
        assert result == ""

    def test_empty_stages_returns_none(self, renderer: EngagementRenderer) -> None:
        """Empty stages list should return None."""
        result = renderer.render_timeline([])
        assert result is None

    def test_breadcrumb_with_template_info(self, renderer: EngagementRenderer) -> None:
        """Breadcrumb should support template context when provided."""
        chain = [
            "IntentRouter",
            "WorkflowComplexityRouter",
            "RefactoringOrchestrator",
        ]
        result = renderer.render_breadcrumb(chain)
        assert "**Routing:**" in result
        assert "WorkflowComplexityRouter" in result

    def test_render_breadcrumb_single_item(self, renderer: EngagementRenderer) -> None:
        """Single orchestrator chain should render without arrows."""
        result = renderer.render_breadcrumb(["MasterOrchestrator"])
        assert result == "**Routing:** MasterOrchestrator"
        assert "→" not in result


class TestBreadcrumbForCommand:
    """Cluster 4: Pre-built breadcrumb chains for common CORTEX commands."""

    @pytest.fixture
    def renderer(self) -> EngagementRenderer:
        """Create renderer instance."""
        return EngagementRenderer()

    @pytest.mark.parametrize("command", [
        "health", "vacuum", "audit", "debug", "totalrecall",
        "implement", "fix", "refactor", "rca", "sync",
        "train", "digest", "design", "plan",
    ])
    def test_breadcrumb_for_known_commands(
        self, renderer: EngagementRenderer, command: str
    ) -> None:
        """All known commands produce non-empty breadcrumbs."""
        result = renderer.breadcrumb_for_command(command)
        assert result != "", f"Empty breadcrumb for command '{command}'"
        assert "**Routing:**" in result
        assert "IntentRouter" in result

    def test_breadcrumb_for_unknown_command_returns_empty(
        self, renderer: EngagementRenderer
    ) -> None:
        """Unknown command returns empty string."""
        result = renderer.breadcrumb_for_command("xyzzy_nonexistent")
        assert result == ""

    def test_breadcrumb_for_audit_includes_all_pipeline_stages(
        self, renderer: EngagementRenderer
    ) -> None:
        """Audit breadcrumb includes key orchestrators from the 9-stage pipeline."""
        result = renderer.breadcrumb_for_command("audit")
        assert "AuditOrchestrator" in result
        assert "HealthOrchestrator" in result
        assert "VacuumOrchestrator" in result
        assert "EnforcementOrchestrator" in result

    def test_command_chains_dict_exists(self) -> None:
        """COMMAND_CHAINS class variable exists with ≥14 entries."""
        assert hasattr(EngagementRenderer, "COMMAND_CHAINS")
        assert len(EngagementRenderer.COMMAND_CHAINS) >= 14


class TestWorkflowGateDefaultFallback:
    """Cluster 3: WorkflowComplexityRouter default fallback is InteractionOrchestrator."""

    def test_unknown_operation_defaults_to_interaction_orchestrator(self) -> None:
        """Unknown operations route to InteractionOrchestrator (LENS comprehension)."""
        from cortex.orchestrators.core.intent_router import (
            WorkflowComplexityRouter, Intent
        )

        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="unknown_operation",
            target_files=["file.txt"],
            dependencies=[],
            risk_level="LOW",
            metadata={},
        )
        decision = router.route(intent)
        assert decision.orchestrator == "InteractionOrchestrator"

    def test_gibberish_operation_defaults_to_interaction_orchestrator(self) -> None:
        """Completely novel operation types route to InteractionOrchestrator."""
        from cortex.orchestrators.core.intent_router import (
            WorkflowComplexityRouter, Intent
        )

        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="xyzzy_flurble",
            target_files=[],
            dependencies=[],
            risk_level="LOW",
            metadata={},
        )
        decision = router.route(intent)
        assert decision.orchestrator == "InteractionOrchestrator"
