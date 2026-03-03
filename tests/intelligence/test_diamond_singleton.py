"""Unit tests for Phase 117-b: singleton facade, WorkflowGateway injection, dead code, stubs.

TDD RED phase — GAPs: 117-04, 117-05, 117-06, 117-07, 117-03c, 117-03d

Authority: Phase 117 Sub-Phase B (cortex-registry/planning/phases/planned/phase-117-intelligence-diamond-completion.yaml)
CORE-008: tests written before implementation.
"""
from __future__ import annotations

import threading
from typing import Any
from unittest.mock import MagicMock, patch

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# GAP-117-05: IntelligenceFacade singleton
# ─────────────────────────────────────────────────────────────────────────────


class TestIntelligenceFacadeSingleton:
    """GAP-117-05: IntelligenceFacade() must return the same instance every time."""

    def test_facade_is_singleton_same_instance(self) -> None:
        """Two calls to IntelligenceFacade() must return the identical object."""
        from cortex.intelligence.facade import IntelligenceFacade

        f1 = IntelligenceFacade()
        f2 = IntelligenceFacade()
        assert f1 is f2, (
            "IntelligenceFacade is not a singleton — got two different instances. "
            "Fix: implement __new__ singleton or module-level instance in facade.py."
        )

    def test_get_intelligence_facade_helper_returns_singleton(self) -> None:
        """get_intelligence_facade() module helper must return the singleton."""
        from cortex.intelligence.facade import get_intelligence_facade

        f1 = get_intelligence_facade()
        f2 = get_intelligence_facade()
        assert f1 is f2

    def test_singleton_has_expected_api(self) -> None:
        """Singleton instance must expose analyze, synthesize, query."""
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        assert hasattr(facade, "analyze"), "Missing analyze()"
        assert hasattr(facade, "synthesize"), "Missing synthesize()"
        assert hasattr(facade, "query"), "Missing query()"

    def test_singleton_survives_concurrent_access(self) -> None:
        """Five threads all receiving the same singleton instance (thread-safe)."""
        from cortex.intelligence.facade import IntelligenceFacade

        instances: list[Any] = []
        errors: list[Exception] = []

        def _get() -> None:
            try:
                instances.append(IntelligenceFacade())
            except Exception as exc:  # noqa: BLE001
                errors.append(exc)

        threads = [threading.Thread(target=_get) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert not errors, f"Thread errors: {errors}"
        assert len(instances) == 5
        first = instances[0]
        for inst in instances[1:]:
            assert inst is first, "Singleton broken under concurrent access"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-117-05: orchestrators must NOT create local IntelligenceFacade()
# ─────────────────────────────────────────────────────────────────────────────


class TestOrchestratorsReuseSharedFacade:
    """GAP-117-05: No orchestrator method may instantiate a local IntelligenceFacade()."""

    def test_smart_citations_mixin_uses_get_facade_helper(self) -> None:
        """smart_citations_mixin must not call IntelligenceFacade() directly."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/core/intent_router/smart_citations_mixin.py"
        ).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                # Detect bare IntelligenceFacade() calls (not get_intelligence_facade())
                if isinstance(func, ast.Name) and func.id == "IntelligenceFacade":
                    pytest.fail(
                        "smart_citations_mixin.py still calls IntelligenceFacade() directly — "
                        "replace with get_intelligence_facade()."
                    )

    def test_enforcement_orchestrator_uses_get_facade_helper(self) -> None:
        """enforcement_orchestrator must not call IntelligenceFacade() directly."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/core/enforcement_orchestrator/orchestrator.py"
        ).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "IntelligenceFacade":
                    pytest.fail(
                        "enforcement_orchestrator/orchestrator.py still calls IntelligenceFacade() directly."
                    )

    def test_tdd_coordinator_uses_get_facade_helper(self) -> None:
        """TDD coordinator must not call IntelligenceFacade() directly."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/core/tdd_orchestrator/_coordinator.py"
        ).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "IntelligenceFacade":
                    pytest.fail(
                        "tdd_orchestrator/_coordinator.py still calls IntelligenceFacade() directly."
                    )

    def test_vacuum_orchestrator_uses_get_facade_helper(self) -> None:
        """VacuumOrchestrator must not call IntelligenceFacade() directly."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/health/vacuum_orchestrator.py"
        ).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "IntelligenceFacade":
                    pytest.fail(
                        "vacuum_orchestrator.py still calls IntelligenceFacade() directly."
                    )

    def test_health_orchestrator_uses_get_facade_helper(self) -> None:
        """HealthOrchestrator must not call IntelligenceFacade() directly."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/health/health_orchestrator.py"
        ).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "IntelligenceFacade":
                    pytest.fail(
                        "health_orchestrator.py still calls IntelligenceFacade() directly."
                    )

    def test_refactoring_orchestrator_uses_get_facade_helper(self) -> None:
        """RefactoringOrchestrator must not call IntelligenceFacade() directly."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/domain/refactoring_orchestrator.py"
        ).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "IntelligenceFacade":
                    pytest.fail(
                        "refactoring_orchestrator.py still calls IntelligenceFacade() directly."
                    )

    def test_security_orchestrator_uses_get_facade_helper(self) -> None:
        """SecurityVulnerabilityOrchestrator must not call IntelligenceFacade() directly."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/validation/security_vulnerability_orchestrator.py"
        ).read_text()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Name) and func.id == "IntelligenceFacade":
                    pytest.fail(
                        "security_vulnerability_orchestrator.py still calls IntelligenceFacade() directly."
                    )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-117-04: _get_intelligence_context dead code deleted
# ─────────────────────────────────────────────────────────────────────────────


class TestDeadCodeRemoved:
    """GAP-117-04: _get_intelligence_context dead code removed."""

    def test_get_intelligence_context_not_defined_in_request_mixin(self) -> None:
        """_get_intelligence_context must not be defined as a method in the request mixin."""
        import ast
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/core/master_orchestrator_request_mixin.py"
        ).read_text()
        tree = ast.parse(src)

        # Look for function *definitions* named _get_intelligence_context
        # (comments and tombstone notes are acceptable — the definition is not)
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if node.name == "_get_intelligence_context":
                    pytest.fail(
                        "_get_intelligence_context() is still *defined* as a method in "
                        "master_orchestrator_request_mixin.py — delete the dead function (GAP-117-04)."
                    )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-117-06: WorkflowGateway execution context has intelligence_facade
# ─────────────────────────────────────────────────────────────────────────────


class TestWorkflowGatewayContextHasFacade:
    """GAP-117-06: WorkflowGateway.execute_gated() must inject intelligence_facade."""

    def test_workflow_gateway_execute_gated_injects_facade(self) -> None:
        """execute_gated context must contain 'intelligence_facade' key."""
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()

        captured_context: dict = {}

        # Patch composer to capture context without running real workflow
        mock_composer = MagicMock()
        mock_composer.execute_from_template.side_effect = (
            lambda tid, ctx, **kw: captured_context.update(ctx) or {
                "status": "complete",
                "steps_completed": 1,
                "success": True,
            }
        )
        gateway._composer = mock_composer

        gateway.execute_gated(
            orchestrator_name="TestOrchestrator",
            mode="IMPLEMENT",
            context={"request_summary": "test"},
        )

        assert "intelligence_facade" in captured_context, (
            "WorkflowGateway.execute_gated() context dict does not include "
            "'intelligence_facade' key (GAP-117-06)."
        )

    def test_workflow_gateway_facade_in_context_is_singleton(self) -> None:
        """intelligence_facade in execute_gated context must be the singleton."""
        from cortex.intelligence.facade import IntelligenceFacade
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

        gateway = WorkflowGateway()
        captured_context: dict = {}

        mock_composer = MagicMock()
        mock_composer.execute_from_template.side_effect = (
            lambda tid, ctx, **kw: captured_context.update(ctx) or {
                "status": "complete",
                "steps_completed": 1,
                "success": True,
            }
        )
        gateway._composer = mock_composer

        gateway.execute_gated(
            orchestrator_name="TestOrchestrator",
            mode="IMPLEMENT",
            context={"request_summary": "test"},
        )

        facade_in_ctx = captured_context.get("intelligence_facade")
        assert facade_in_ctx is IntelligenceFacade(), (
            "intelligence_facade in context is not the singleton instance."
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-117-03c: OrchestratorContextInjector stub eliminated
# ─────────────────────────────────────────────────────────────────────────────


class TestOrchestratorContextInjector:
    """GAP-117-03c: OrchestratorContextInjector returns real metadata or is removed."""

    def test_extract_orchestrator_metadata_returns_nonempty_dict(self) -> None:
        """extract_orchestrator_metadata_from_wiring() must return non-empty metadata."""
        from cortex.orchestrators.core.orchestrator_context_injector import (
            extract_orchestrator_metadata_from_wiring,
        )

        result = extract_orchestrator_metadata_from_wiring("MasterOrchestrator")
        assert isinstance(result, dict), "Must return a dict"
        assert len(result) > 0, (
            "extract_orchestrator_metadata_from_wiring() still returns empty dict — "
            "stub not eliminated (GAP-117-03c)."
        )
        assert "name" in result, "Metadata must include 'name' key"

    def test_extract_metadata_degrades_when_wiring_yaml_missing(self) -> None:
        """Returns {} (not crash) when wiring YAML is inaccessible."""
        from cortex.orchestrators.core.orchestrator_context_injector import (
            extract_orchestrator_metadata_from_wiring,
        )

        with patch(
            "cortex.orchestrators.core.orchestrator_context_injector._load_wiring_yaml",
            side_effect=FileNotFoundError("wiring YAML missing"),
        ):
            result = extract_orchestrator_metadata_from_wiring("NonExistentOrchestrator")
        assert isinstance(result, dict), "Must not crash — must return empty dict"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-117-03d: MasterOrchestratorGateway placeholder resolved
# ─────────────────────────────────────────────────────────────────────────────


class TestMasterOrchestratorGatewayPlaceholders:
    """GAP-117-03d: MasterOrchestratorGateway placeholder paths resolved."""

    def test_gateway_classify_intent_uses_intent_router(self) -> None:
        """classify_intent() must delegate to IntentRouter, not keyword matching alone."""
        import pathlib

        src = pathlib.Path("cortex/core/master_orchestrator_gateway.py").read_text()
        # Check: the gateway references IntentRouter (production delegation path)
        assert "IntentRouter" in src or "intent_router" in src, (
            "MasterOrchestratorGateway.classify_intent() still uses inline keyword "
            "matching instead of delegating to IntentRouter (GAP-117-03d)."
        )

    def test_gateway_dependencies_met_not_hardcoded_placeholder(self) -> None:
        """dependencies_met must not be the exact hardcoded '# Placeholder' line."""
        import pathlib

        src = pathlib.Path("cortex/core/master_orchestrator_gateway.py").read_text()
        assert "dependencies_met = True  # Placeholder" not in src, (
            "MasterOrchestratorGateway still has 'dependencies_met = True  # Placeholder' "
            "(GAP-117-03d). Fix or document as intentional."
        )

    def test_gateway_execute_placeholder_comment_removed(self) -> None:
        """'# Placeholder execution' comment must be replaced with real docstring."""
        import pathlib

        src = pathlib.Path("cortex/core/master_orchestrator_gateway.py").read_text()
        assert "# Placeholder execution" not in src, (
            "MasterOrchestratorGateway still has '# Placeholder execution' comment "
            "(GAP-117-03d). Replace or annotate as development-only."
        )


# ─────────────────────────────────────────────────────────────────────────────
# GAP-117-07: TDDKnowledgeLoader documented as intentional domain-specific loader
# ─────────────────────────────────────────────────────────────────────────────


class TestTDDKnowledgeLoaderDocumented:
    """GAP-117-07: TDDKnowledgeLoader clearly documented as intentional, not a bypass."""

    def test_tdd_knowledge_loader_has_design_rationale_comment(self) -> None:
        """TDDKnowledgeLoader class/usage must have a comment explaining it is intentional."""
        import pathlib

        src = pathlib.Path(
            "cortex/orchestrators/core/tdd_orchestrator/_coordinator.py"
        ).read_text()
        # Look for a design-rationale comment near TDDKnowledgeLoader
        assert (
            "intentional" in src.lower()
            or "domain-specific" in src.lower()
            or "design choice" in src.lower()
            or "not a bypass" in src.lower()
        ), (
            "TDDKnowledgeLoader usage in _coordinator.py lacks design-rationale comment "
            "explaining it is an intentional domain-specific loader (GAP-117-07)."
        )
