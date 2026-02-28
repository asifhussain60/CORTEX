"""
Phase 90b — Enforcement Extension: Fail-Fast Disk Check + Remaining Orchestrator Opt-ins.

RED tests for:
  Cluster 1: WorkflowGateway.resolve_template() fails fast on stale map entries (P0)
  Cluster 2: TDDOrchestrator carries WorkflowEnforcementMixin + opt-in enabled (P1)
  Cluster 3: DebuggerOrchestrator carries WorkflowEnforcementMixin + opt-in enabled (P1)
  Cluster 4: RefactoringOrchestrator carries WorkflowEnforcementMixin + opt-in enabled (P1)
  Cluster 5: WorkflowGateway.resolve_template() strict=True raises on missing YAML

CORE-008: TDD mandatory — RED before GREEN
AC-ID: AC-P90B-001
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Type
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: resolve_template strict mode — fail-fast on stale map entries
# ════════════════════════════════════════════════════════════════════════════

class TestGatewayStrictResolve:
    """WorkflowGateway.resolve_template(strict=True) must raise if template YAML missing."""

    @pytest.fixture
    def gateway(self, tmp_path: Path) -> Any:
        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        return WorkflowGateway(db_path=tmp_path / "traces.db")

    def test_resolve_strict_passes_for_valid_template(self, gateway: Any) -> None:
        """Strict resolve passes when the canonical template YAML exists on disk."""
        result = gateway.resolve_template("IMPLEMENT", {}, strict=True)
        assert result == "sdlc/implement-workflow"

    def test_resolve_strict_raises_for_nonexistent_template(
        self, gateway: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Strict resolve raises WorkflowGatewayError when template YAML is missing."""
        from cortex.orchestrators.workflow.workflow_gateway import (
            WorkflowGatewayError,
            _MODE_TEMPLATE_MAP,
        )
        # Inject a stale entry into a copy-like view for this test
        monkeypatch.setitem(
            _MODE_TEMPLATE_MAP, "STALE_MODE", "sdlc/phantom-workflow-that-does-not-exist"
        )
        with pytest.raises(WorkflowGatewayError, match="phantom-workflow"):
            gateway.resolve_template("STALE_MODE", {}, strict=True)

    def test_resolve_non_strict_still_returns_stale_id(
        self, gateway: Any, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Non-strict resolve (default) returns the ID without checking disk — backward compat."""
        from cortex.orchestrators.workflow.workflow_gateway import _MODE_TEMPLATE_MAP
        monkeypatch.setitem(
            _MODE_TEMPLATE_MAP, "STALE_MODE_NS", "sdlc/phantom-workflow-that-does-not-exist"
        )
        result = gateway.resolve_template("STALE_MODE_NS", {})
        # Non-strict: no exception, just returns the ID as-is
        assert result == "sdlc/phantom-workflow-that-does-not-exist"

    def test_resolve_strict_exempt_mode_returns_none(self, gateway: Any) -> None:
        """Strict resolve of an exempt mode (QUERY) returns None without disk check."""
        result = gateway.resolve_template("QUERY", {}, strict=True)
        assert result is None

    @pytest.mark.parametrize("mode", ["IMPLEMENT", "FIX", "REFACTOR", "AUDIT", "HEALTH", "VACUUM", "TDD", "DEBUG"])
    def test_resolve_strict_all_core_modes_have_valid_yaml(self, gateway: Any, mode: str) -> None:
        """All core code-touching modes resolve to a YAML that exists on disk (strict=True)."""
        template_id = gateway.resolve_template(mode, {}, strict=True)
        assert template_id is not None
        yaml_path = TEMPLATES_ROOT / f"{template_id}.yaml"
        assert yaml_path.exists(), (
            f"Mode {mode!r}: template {template_id!r} → {yaml_path} not found on disk"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: TDDOrchestrator — WorkflowEnforcementMixin + gateway enabled
# ════════════════════════════════════════════════════════════════════════════

class TestTDDOrchestratorPhase90BWiring:
    """TDDOrchestrator must carry WorkflowEnforcementMixin with PHASE90_GATEWAY_ENABLED=True."""

    @pytest.fixture
    def tdd_class(self) -> Type:
        from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator
        return TDDOrchestrator

    def test_tdd_inherits_enforcement_mixin(self, tdd_class: Type) -> None:
        """TDDOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(tdd_class, WorkflowEnforcementMixin), (
            "TDDOrchestrator must inherit WorkflowEnforcementMixin (Phase 90b)"
        )

    def test_tdd_gateway_enabled_is_true(self, tdd_class: Type) -> None:
        """TDDOrchestrator.PHASE90_GATEWAY_ENABLED must be True."""
        assert tdd_class.PHASE90_GATEWAY_ENABLED is True, (
            "TDDOrchestrator.PHASE90_GATEWAY_ENABLED must be True — Phase 90b opt-in"
        )

    def test_tdd_in_template_orchestrator_map(self) -> None:
        """TDDOrchestrator must be in TEMPLATE_ORCHESTRATOR_MAP."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert "TDDOrchestrator" in WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: DebuggerOrchestrator — WorkflowEnforcementMixin + gateway enabled
# ════════════════════════════════════════════════════════════════════════════

class TestDebuggerOrchestratorPhase90BWiring:
    """DebuggerOrchestrator must carry WorkflowEnforcementMixin with PHASE90_GATEWAY_ENABLED=True."""

    @pytest.fixture
    def debugger_class(self) -> Type:
        from cortex.orchestrators.support.debugger_orchestrator import DebuggerOrchestrator
        return DebuggerOrchestrator

    def test_debugger_inherits_enforcement_mixin(self, debugger_class: Type) -> None:
        """DebuggerOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(debugger_class, WorkflowEnforcementMixin), (
            "DebuggerOrchestrator must inherit WorkflowEnforcementMixin (Phase 90b)"
        )

    def test_debugger_gateway_enabled_is_true(self, debugger_class: Type) -> None:
        """DebuggerOrchestrator.PHASE90_GATEWAY_ENABLED must be True."""
        assert debugger_class.PHASE90_GATEWAY_ENABLED is True, (
            "DebuggerOrchestrator.PHASE90_GATEWAY_ENABLED must be True — Phase 90b opt-in"
        )

    def test_debugger_in_template_orchestrator_map(self) -> None:
        """DebuggerOrchestrator must be in TEMPLATE_ORCHESTRATOR_MAP."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert "DebuggerOrchestrator" in WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: RefactoringOrchestrator — WorkflowEnforcementMixin + gateway enabled
# ════════════════════════════════════════════════════════════════════════════

class TestRefactoringOrchestratorPhase90BWiring:
    """RefactoringOrchestrator must carry WorkflowEnforcementMixin with PHASE90_GATEWAY_ENABLED=True."""

    @pytest.fixture
    def refactoring_class(self) -> Type:
        from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator
        return RefactoringOrchestrator

    def test_refactoring_inherits_enforcement_mixin(self, refactoring_class: Type) -> None:
        """RefactoringOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(refactoring_class, WorkflowEnforcementMixin), (
            "RefactoringOrchestrator must inherit WorkflowEnforcementMixin (Phase 90b)"
        )

    def test_refactoring_gateway_enabled_is_true(self, refactoring_class: Type) -> None:
        """RefactoringOrchestrator.PHASE90_GATEWAY_ENABLED must be True."""
        assert refactoring_class.PHASE90_GATEWAY_ENABLED is True, (
            "RefactoringOrchestrator.PHASE90_GATEWAY_ENABLED must be True — Phase 90b opt-in"
        )

    def test_refactoring_in_template_orchestrator_map(self) -> None:
        """RefactoringOrchestrator must be in TEMPLATE_ORCHESTRATOR_MAP with correct template."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        tmap = WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP
        assert "RefactoringOrchestrator" in tmap
        assert tmap["RefactoringOrchestrator"] == "quality/refactor-workflow"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 5: Gateway strict resolve round-trip through all mode→YAML pairs
# ════════════════════════════════════════════════════════════════════════════

class TestGatewayStrictRoundTrip:
    """Every entry in _MODE_TEMPLATE_MAP that is not None must exist on disk (golden contract)."""

    def test_all_registered_templates_exist_on_disk(self, tmp_path: Path) -> None:
        """_MODE_TEMPLATE_MAP must have zero stale entries — every mapped template exists."""
        from cortex.orchestrators.workflow.workflow_gateway import _MODE_TEMPLATE_MAP

        missing = {}
        for mode, template_id in _MODE_TEMPLATE_MAP.items():
            if template_id is None:
                continue
            yaml_path = TEMPLATES_ROOT / f"{template_id}.yaml"
            if not yaml_path.exists():
                missing[mode] = str(yaml_path.relative_to(ROOT))

        assert missing == {}, (
            "Stale _MODE_TEMPLATE_MAP entries (template YAML missing):\n"
            + "\n".join(f"  {mode}: {path}" for mode, path in sorted(missing.items()))
        )
