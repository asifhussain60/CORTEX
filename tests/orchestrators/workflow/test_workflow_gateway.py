"""
Phase 90 — WorkflowGateway: Mandatory Template Resolution Gate (RED tests).

Verifies that no code-touching operation can proceed without resolving a
dedicated workflow template and engaging the convergence loop.

CORE-008: TDD mandatory — RED before GREEN
CORE-068: Universal Convergence Gate
AC-ID: AC-P90-WFG-001
"""
from __future__ import annotations

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch, call
from typing import Any, Dict


ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: WorkflowGateway exists and is importable
# ════════════════════════════════════════════════════════════════════════════

class TestWorkflowGatewayImport:
    """WorkflowGateway must be importable from canonical location."""

    def test_workflow_gateway_importable(self) -> None:
        """WorkflowGateway is importable from cortex.orchestrators.workflow.workflow_gateway."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        assert WorkflowGateway is not None

    def test_workflow_gateway_has_resolve_template(self) -> None:
        """WorkflowGateway must expose resolve_template(mode, context) -> str."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        assert hasattr(WorkflowGateway, "resolve_template"), (
            "WorkflowGateway must have resolve_template(mode, context) method"
        )

    def test_workflow_gateway_has_execute_gated(self) -> None:
        """WorkflowGateway must expose execute_gated(orchestrator, mode, context)."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        assert hasattr(WorkflowGateway, "execute_gated"), (
            "WorkflowGateway must have execute_gated(orchestrator, mode, context) method"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: resolve_template returns correct IDs per mode
# ════════════════════════════════════════════════════════════════════════════

class TestWorkflowGatewayResolution:
    """resolve_template must map every code-touching mode to a template ID."""

    @pytest.fixture
    def gateway(self) -> Any:
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        return WorkflowGateway()

    def test_implement_mode_resolves_implement_workflow(self, gateway: Any) -> None:
        template_id = gateway.resolve_template("IMPLEMENT", {})
        assert template_id == "sdlc/implement-workflow", (
            f"IMPLEMENT must resolve to sdlc/implement-workflow, got {template_id}"
        )

    def test_fix_mode_resolves_fix_workflow(self, gateway: Any) -> None:
        template_id = gateway.resolve_template("FIX", {})
        assert template_id == "sdlc/fix-workflow", (
            f"FIX must resolve to sdlc/fix-workflow, got {template_id}"
        )

    def test_refactor_mode_resolves_refactor_workflow(self, gateway: Any) -> None:
        template_id = gateway.resolve_template("REFACTOR", {})
        assert template_id == "quality/refactor-workflow", (
            f"REFACTOR must resolve to quality/refactor-workflow, got {template_id}"
        )

    def test_debug_mode_resolves_debug_pipeline(self, gateway: Any) -> None:
        template_id = gateway.resolve_template("DEBUG", {})
        assert template_id == "debugging/multi-stack-debug-pipeline", (
            f"DEBUG must resolve to debugging/multi-stack-debug-pipeline, got {template_id}"
        )

    def test_health_mode_resolves_health_check_workflow(self, gateway: Any) -> None:
        template_id = gateway.resolve_template("HEALTH", {})
        assert template_id == "maintenance/health-check-workflow", (
            f"HEALTH must resolve to maintenance/health-check-workflow, got {template_id}"
        )

    def test_vacuum_mode_resolves_vacuum_workflow(self, gateway: Any) -> None:
        template_id = gateway.resolve_template("VACUUM", {})
        assert template_id == "maintenance/vacuum-workflow", (
            f"VACUUM must resolve to maintenance/vacuum-workflow, got {template_id}"
        )

    def test_audit_mode_resolves_audit_fix_pipeline(self, gateway: Any) -> None:
        template_id = gateway.resolve_template("AUDIT", {})
        assert template_id == "audit/audit-fix-pipeline", (
            f"AUDIT must resolve to audit/audit-fix-pipeline, got {template_id}"
        )

    def test_tdd_mode_resolves_tdd_workflow(self, gateway: Any) -> None:
        """TDD mode (generic) resolves to tdd/tdd-workflow dispatcher."""
        template_id = gateway.resolve_template("TDD", {})
        assert template_id == "tdd/tdd-workflow", (
            f"TDD must resolve to tdd/tdd-workflow, got {template_id}"
        )

    def test_unknown_exempt_mode_returns_none(self, gateway: Any) -> None:
        """Non-code-touching modes (QUERY, DESIGN, PLAN) return None — exempt per WC-005."""
        assert gateway.resolve_template("QUERY", {}) is None
        assert gateway.resolve_template("DESIGN", {}) is None
        assert gateway.resolve_template("PLAN", {}) is None


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: execute_gated calls WorkflowComposer with convergence_mode=True
# ════════════════════════════════════════════════════════════════════════════

class TestWorkflowGatewayExecution:
    """execute_gated must always route through WorkflowComposer.execute_from_template."""

    def test_execute_gated_calls_composer_with_convergence(self) -> None:
        """execute_gated must call execute_from_template(convergence_mode=True)."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        mock_composer = MagicMock()
        mock_composer.execute_from_template.return_value = {
            "status": "complete",
            "steps_completed": 5,
        }
        gateway._composer = mock_composer

        result = gateway.execute_gated(
            orchestrator_name="TDDOrchestrator",
            mode="IMPLEMENT",
            context={"request_summary": "add new feature"},
        )

        mock_composer.execute_from_template.assert_called_once()
        call_kwargs = mock_composer.execute_from_template.call_args
        # convergence_mode must be True
        assert call_kwargs.kwargs.get("convergence_mode", False) is True or (
            len(call_kwargs.args) > 1 and call_kwargs.args[1] is True
        ), "execute_from_template must be called with convergence_mode=True"

    def test_execute_gated_blocks_when_no_template_for_code_mode(self) -> None:
        """execute_gated must raise WorkflowGatewayError if no template resolves for code-touching mode."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway, WorkflowGatewayError

        gateway = WorkflowGateway()
        # Simulate unregistered code-touching mode
        with pytest.raises(WorkflowGatewayError):
            gateway.execute_gated(
                orchestrator_name="SomeNewOrchestrator",
                mode="UNKNOWN_CODE_MODE",
                context={},
            )

    def test_execute_gated_emits_ac_start_and_complete(self) -> None:
        """execute_gated must emit AC_START before execution and AC_COMPLETE after."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        mock_composer = MagicMock()
        mock_composer.execute_from_template.return_value = {"status": "complete"}
        gateway._composer = mock_composer

        with patch.object(gateway, "_emit_ac_marker") as mock_ac:
            gateway.execute_gated(
                orchestrator_name="TDDOrchestrator",
                mode="IMPLEMENT",
                context={},
            )
            calls = [c.args[0] for c in mock_ac.call_args_list]
            assert any("AC_START" in str(c) for c in calls), "AC_START must be emitted"
            assert any("AC_COMPLETE" in str(c) for c in calls), "AC_COMPLETE must be emitted"

    def test_execute_gated_returns_result_with_template_id(self) -> None:
        """execute_gated result must include the resolved template_id for traceability."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        mock_composer = MagicMock()
        mock_composer.execute_from_template.return_value = {"status": "complete", "steps_completed": 3}
        gateway._composer = mock_composer

        result = gateway.execute_gated(
            orchestrator_name="TDDOrchestrator",
            mode="FIX",
            context={},
        )

        assert "template_id" in result, "Result must include template_id for traceability"
        assert result["template_id"] == "sdlc/fix-workflow"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: SQLite trace row written per execution
# ════════════════════════════════════════════════════════════════════════════

class TestWorkflowGatewayTracing:
    """execute_gated must log a SQLite trace row for every execution."""

    def test_execute_gated_logs_workflow_run_row(self) -> None:
        """execute_gated must call _log_workflow_run() to persist trace to SQLite."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        mock_composer = MagicMock()
        mock_composer.execute_from_template.return_value = {"status": "complete"}
        gateway._composer = mock_composer

        with patch.object(gateway, "_log_workflow_run") as mock_log:
            gateway.execute_gated(
                orchestrator_name="RefactoringOrchestrator",
                mode="REFACTOR",
                context={"target_module": "cortex/core/"},
            )
            mock_log.assert_called_once()
            log_args = mock_log.call_args.kwargs or {}
            if not log_args:
                log_args = {}
            # Must log at minimum: template_id, mode, orchestrator_name, status
            call_repr = str(mock_log.call_args)
            assert "REFACTOR" in call_repr or "refactor" in call_repr.lower(), (
                "Trace row must record the operation mode"
            )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 5: Phase 142 — get_mode_template_map() public accessor
# ════════════════════════════════════════════════════════════════════════════


class TestGetModeTemplateMap:
    """Phase 142-a: WorkflowGateway.get_mode_template_map() SSOT accessor."""

    def test_get_mode_template_map_returns_dict(self) -> None:
        """get_mode_template_map() must return a dict."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        result = WorkflowGateway.get_mode_template_map()
        assert isinstance(result, dict), "get_mode_template_map() must return dict"

    def test_get_mode_template_map_contains_implement(self) -> None:
        """Canonical IMPLEMENT mode must be in the returned map."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        result = WorkflowGateway.get_mode_template_map()
        assert "IMPLEMENT" in result, "IMPLEMENT must be in mode→template map"
        assert result["IMPLEMENT"] == "sdlc/implement-workflow"

    def test_get_mode_template_map_returns_copy_not_reference(self) -> None:
        """Mutating the returned dict must not affect the canonical map."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        a = WorkflowGateway.get_mode_template_map()
        a["FAKE_MODE"] = "fake/template"
        b = WorkflowGateway.get_mode_template_map()
        assert "FAKE_MODE" not in b, (
            "get_mode_template_map() must return a copy, not the internal reference"
        )

    def test_get_mode_template_map_none_for_query(self) -> None:
        """QUERY is a non-code-touching mode — must map to None."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        result = WorkflowGateway.get_mode_template_map()
        assert "QUERY" in result
        assert result["QUERY"] is None, "QUERY must map to None (non-code-touching)"

    def test_get_mode_template_map_callable_as_static(self) -> None:
        """get_mode_template_map() must be callable without instantiating the class."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        # Must not raise — no instance needed
        result = WorkflowGateway.get_mode_template_map()
        assert isinstance(result, dict)


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 6: Phase 142-b — SubPhaseComposer uses WorkflowGateway SSOT
# ════════════════════════════════════════════════════════════════════════════


class TestSubPhaseComposerDRY:
    """Phase 142-b: SubPhaseComposer derives intent→template map from WorkflowGateway."""

    def test_subphasecomposer_importable(self) -> None:
        """SubPhaseComposer must be importable from canonical location."""
        from cortex.orchestrators.workflow.sub_phase_composer import SubPhaseComposer
        assert SubPhaseComposer is not None

    def test_intent_template_map_matches_workflow_gateway(self) -> None:
        """SubPhaseComposer.INTENT_TEMPLATE_MAP must agree with WorkflowGateway for all shared keys."""
        from cortex.orchestrators.workflow.sub_phase_composer import SubPhaseComposer
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway_map = WorkflowGateway.get_mode_template_map()
        composer_map = SubPhaseComposer.INTENT_TEMPLATE_MAP

        # Every key in composer_map that exists in gateway_map must have the same value
        for mode, template in composer_map.items():
            if mode in gateway_map and gateway_map[mode] is not None:
                assert template == gateway_map[mode], (
                    f"INTENT_TEMPLATE_MAP[{mode!r}]={template!r} disagrees with "
                    f"WorkflowGateway[{mode!r}]={gateway_map[mode]!r}"
                )

    def test_subphasecomposer_no_hardcoded_duplicates(self) -> None:
        """SubPhaseComposer must not re-declare entries already in WorkflowGateway."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/workflow/sub_phase_composer.py"
        ).read_text()
        # The file must NOT contain a large hardcoded dict literal reproducing _MODE_TEMPLATE_MAP
        # Heuristic: count "sdlc/implement-workflow" literal — if present inline, it's a duplicate
        assert "sdlc/implement-workflow" not in src or "get_mode_template_map" in src, (
            "SubPhaseComposer must not hardcode template IDs already in WorkflowGateway. "
            "Use get_mode_template_map() instead."
        )

    def test_subphasecomposer_exposes_intent_template_map(self) -> None:
        """SubPhaseComposer.INTENT_TEMPLATE_MAP must be a non-empty dict."""
        from cortex.orchestrators.workflow.sub_phase_composer import SubPhaseComposer

        assert hasattr(SubPhaseComposer, "INTENT_TEMPLATE_MAP")
        assert isinstance(SubPhaseComposer.INTENT_TEMPLATE_MAP, dict)
        assert len(SubPhaseComposer.INTENT_TEMPLATE_MAP) >= 10, (
            "INTENT_TEMPLATE_MAP should have at least 10 entries (from WorkflowGateway)"
        )

    def test_subphasecomposer_get_template_for_mode(self) -> None:
        """SubPhaseComposer.get_template_for_mode() must resolve via the canonical map."""
        from cortex.orchestrators.workflow.sub_phase_composer import SubPhaseComposer

        composer = SubPhaseComposer()
        result = composer.get_template_for_mode("IMPLEMENT")
        assert result == "sdlc/implement-workflow", (
            f"Expected 'sdlc/implement-workflow', got {result!r}"
        )

    def test_subphasecomposer_returns_none_for_unknown_mode(self) -> None:
        """SubPhaseComposer.get_template_for_mode() returns None for unrecognised modes."""
        from cortex.orchestrators.workflow.sub_phase_composer import SubPhaseComposer

        composer = SubPhaseComposer()
        result = composer.get_template_for_mode("TOTALLY_UNKNOWN_MODE")
        assert result is None

