"""
Phase 90c — Bypass-Gap Closure: enforce_gateway decorator + Top-Level Orchestrator Opt-ins.

RED tests for:
  Cluster 1: enforce_gateway decorator exists and is importable (P1)
  Cluster 2: enforce_gateway routes through WorkflowGateway when PHASE90_GATEWAY_ENABLED=True
  Cluster 3: enforce_gateway is a no-op when PHASE90_GATEWAY_ENABLED=False (safe)
  Cluster 4: MasterOrchestrator carries WorkflowEnforcementMixin (not yet opted in — advisory)
  Cluster 5: EnforcementOrchestrator carries WorkflowEnforcementMixin (not yet opted in — advisory)
  Cluster 6: AuditOrchestrator carries WorkflowEnforcementMixin (not yet opted in — advisory)

CORE-008: TDD mandatory — RED before GREEN
AC-ID: AC-P90C-001
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Type
from unittest.mock import MagicMock

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 1: enforce_gateway decorator — importable + correct location
# ════════════════════════════════════════════════════════════════════════════

class TestEnforceGatewayDecoratorExists:
    """enforce_gateway must be importable from WorkflowEnforcementMixin module."""

    def test_enforce_gateway_importable_from_enforcement_mixin(self) -> None:
        """enforce_gateway is importable from cortex.core.workflow_enforcement_mixin."""
        from cortex.core.workflow_enforcement_mixin import enforce_gateway
        assert callable(enforce_gateway), "enforce_gateway must be a callable decorator"

    def test_enforce_gateway_importable_from_workflow_package(self) -> None:
        """enforce_gateway is also re-exported from cortex.orchestrators.workflow."""
        from cortex.orchestrators.workflow import enforce_gateway
        assert callable(enforce_gateway)

    def test_enforce_gateway_is_a_decorator_factory_or_decorator(self) -> None:
        """enforce_gateway applied to a function returns a callable."""
        from cortex.core.workflow_enforcement_mixin import enforce_gateway

        def dummy_execute_operation(self, mode, params):
            return "result"

        wrapped = enforce_gateway(dummy_execute_operation)
        assert callable(wrapped), "enforce_gateway must return a callable when applied to a method"


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 2: enforce_gateway routes through WorkflowGateway when enabled
# ════════════════════════════════════════════════════════════════════════════

class TestEnforceGatewayRoutingEnabled:
    """When PHASE90_GATEWAY_ENABLED=True, decorated execute_operation routes to gateway."""

    def test_decorated_execute_operation_calls_gateway(self, tmp_path: Path) -> None:
        """enforce_gateway-decorated execute_operation delegates to WorkflowGateway."""
        from cortex.core.workflow_enforcement_mixin import (
            WorkflowEnforcementMixin,
            enforce_gateway,
        )

        gateway_calls: list = []

        class MockGateway:
            def execute_gated(self, orchestrator_name, mode, context):
                gateway_calls.append((orchestrator_name, mode))
                return {"status": "COMPLETED", "template_id": "sdlc/implement-workflow",
                        "steps_completed": 1, "run_id": "gw-001"}

        class EnabledOrch(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = True

            @enforce_gateway
            def execute_operation(self, mode: str, params: Dict) -> Any:
                raise AssertionError("Should not reach original method when gateway enabled")

        orch = EnabledOrch()
        orch._gateway = MockGateway()
        result = orch.execute_operation("IMPLEMENT", {"key": "val"})
        assert result["status"] == "COMPLETED"
        assert gateway_calls == [("EnabledOrch", "IMPLEMENT")]

    def test_decorated_method_passes_mode_from_first_arg(self, tmp_path: Path) -> None:
        """enforce_gateway extracts mode from the first positional argument."""
        from cortex.core.workflow_enforcement_mixin import (
            WorkflowEnforcementMixin,
            enforce_gateway,
        )

        captured: list = []

        class MockGateway:
            def execute_gated(self, orchestrator_name, mode, context):
                captured.append(mode)
                return {"status": "COMPLETED", "template_id": "sdlc/fix-workflow",
                        "steps_completed": 0, "run_id": "gw-002"}

        class Orch(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = True

            @enforce_gateway
            def execute_operation(self, mode, params):
                return "direct"

        orch = Orch()
        orch._gateway = MockGateway()
        orch.execute_operation("FIX", {})
        assert captured == ["FIX"]


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 3: enforce_gateway is a no-op when PHASE90_GATEWAY_ENABLED=False
# ════════════════════════════════════════════════════════════════════════════

class TestEnforceGatewayNoOpWhenDisabled:
    """When PHASE90_GATEWAY_ENABLED=False, decorated execute_operation runs normally."""

    def test_disabled_gateway_does_not_intercept(self) -> None:
        """enforce_gateway passes through to original method when gateway disabled."""
        from cortex.core.workflow_enforcement_mixin import (
            WorkflowEnforcementMixin,
            enforce_gateway,
        )

        original_called: list = []

        class DisabledOrch(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = False  # default

            @enforce_gateway
            def execute_operation(self, mode, params):
                original_called.append(mode)
                return {"status": "direct", "mode": mode}

        orch = DisabledOrch()
        result = orch.execute_operation("IMPLEMENT", {})
        assert result["status"] == "direct"
        assert original_called == ["IMPLEMENT"]

    def test_disabled_gateway_does_not_create_gateway_instance(self) -> None:
        """enforce_gateway must not instantiate WorkflowGateway when disabled."""
        from cortex.core.workflow_enforcement_mixin import (
            WorkflowEnforcementMixin,
            enforce_gateway,
        )

        class DisabledOrch(WorkflowEnforcementMixin):
            PHASE90_GATEWAY_ENABLED = False

            @enforce_gateway
            def execute_operation(self, mode, params):
                return "ok"

        orch = DisabledOrch()
        orch.execute_operation("IMPLEMENT", {})
        # _gateway must remain None — no lazy init when disabled
        assert orch._gateway is None, (
            "enforce_gateway must not create a WorkflowGateway instance when disabled"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 4: MasterOrchestrator — WorkflowEnforcementMixin wired
# ════════════════════════════════════════════════════════════════════════════

class TestMasterOrchestratorPhase90CWiring:
    """MasterOrchestrator must carry WorkflowEnforcementMixin (advisory opt-in)."""

    @pytest.fixture
    def master_class(self) -> Type:
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        return MasterOrchestrator

    def test_master_inherits_enforcement_mixin(self, master_class: Type) -> None:
        """MasterOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(master_class, WorkflowEnforcementMixin), (
            "MasterOrchestrator must inherit WorkflowEnforcementMixin (Phase 90c)"
        )

    def test_master_in_template_orchestrator_map(self) -> None:
        """MasterOrchestrator must be in TEMPLATE_ORCHESTRATOR_MAP."""
        from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
        assert "MasterOrchestrator" in WorkflowTemplateMixin.TEMPLATE_ORCHESTRATOR_MAP

    def test_master_gateway_enabled_is_false_initially(self, master_class: Type) -> None:
        """MasterOrchestrator.PHASE90_GATEWAY_ENABLED starts as False — advisory only."""
        # MasterOrchestrator is the top-level coordinator; gateway must be False
        # until all downstream orchestrators have been migrated and validated.
        assert master_class.PHASE90_GATEWAY_ENABLED is False, (
            "MasterOrchestrator.PHASE90_GATEWAY_ENABLED must remain False — "
            "it coordinates all other orchestrators; full opt-in requires "
            "all downstream orchestrators to be gateway-enabled first"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 5: EnforcementOrchestrator — WorkflowEnforcementMixin wired
# ════════════════════════════════════════════════════════════════════════════

class TestEnforcementOrchestratorPhase90CWiring:
    """EnforcementOrchestrator must carry WorkflowEnforcementMixin."""

    @pytest.fixture
    def enforcement_class(self) -> Type:
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator
        return EnforcementOrchestrator

    def test_enforcement_inherits_enforcement_mixin(self, enforcement_class: Type) -> None:
        """EnforcementOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(enforcement_class, WorkflowEnforcementMixin), (
            "EnforcementOrchestrator must inherit WorkflowEnforcementMixin (Phase 90c)"
        )

    def test_enforcement_gateway_enabled_is_false_initially(self, enforcement_class: Type) -> None:
        """EnforcementOrchestrator.PHASE90_GATEWAY_ENABLED is False — it IS the gate."""
        # EnforcementOrchestrator is the pre-execution governance gate.
        # Routing IT through a gateway would create a circular dependency.
        # It carries the mixin for future extensibility but must not self-gate.
        assert enforcement_class.PHASE90_GATEWAY_ENABLED is False, (
            "EnforcementOrchestrator.PHASE90_GATEWAY_ENABLED must be False — "
            "it IS the governance gate; self-gating creates circular dependency"
        )


# ════════════════════════════════════════════════════════════════════════════
# CLUSTER 6: AuditOrchestrator — WorkflowEnforcementMixin wired
# ════════════════════════════════════════════════════════════════════════════

class TestAuditOrchestratorPhase90CWiring:
    """AuditOrchestrator must carry WorkflowEnforcementMixin."""

    @pytest.fixture
    def audit_class(self) -> Type:
        from cortex.orchestrators.core.audit_orchestrator import AuditOrchestrator
        return AuditOrchestrator

    def test_audit_inherits_enforcement_mixin(self, audit_class: Type) -> None:
        """AuditOrchestrator is a WorkflowEnforcementMixin subclass."""
        from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin
        assert issubclass(audit_class, WorkflowEnforcementMixin), (
            "AuditOrchestrator must inherit WorkflowEnforcementMixin (Phase 90c)"
        )

    def test_audit_gateway_enabled_is_false_initially(self, audit_class: Type) -> None:
        """AuditOrchestrator.PHASE90_GATEWAY_ENABLED is False — audit-fix-pipeline routes it."""
        assert audit_class.PHASE90_GATEWAY_ENABLED is False, (
            "AuditOrchestrator.PHASE90_GATEWAY_ENABLED must be False — "
            "it is invoked by audit-fix-pipeline.yaml, not the other way around"
        )
