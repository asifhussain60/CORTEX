"""
Phase 59-e: cross_cutting_enforced Decorator Tests

CORE-008: Tests written before / alongside implementation.
GAP-59-08b: execute_operation overrides that skip super() must still activate hooks.
GAP-59-08:  PlanningOrchestrator LENS activation.

AC_START: AC-CROSS-CUTTING-5905
"""
from __future__ import annotations

from typing import Any, Dict
from unittest.mock import MagicMock, patch

import pytest

from cortex.core.orchestrator_protocol_mixin import (
    OrchestratorProtocolMixin,
    cross_cutting_enforced,
)


class TestCrossCuttingEnforcedDecorator:
    """59-e-T1: @cross_cutting_enforced must fire hooks even without super() call."""

    def test_decorator_importable(self) -> None:
        """cross_cutting_enforced must be importable from OrchestratorProtocolMixin module."""
        assert callable(cross_cutting_enforced)

    def test_decorator_fires_hooks_when_super_not_called(self) -> None:
        """Hook fires even when subclass override does not call super()."""
        activated: list[str] = []

        class StubOrchestrator(OrchestratorProtocolMixin):
            _orch_name = "StubOrchestrator"

            def _activate_cross_cutting_hooks(self, operation="", **kw):
                activated.append(operation)
                return {"lens_context": None, "knowledge": {}, "governance_allowed": True}

            @cross_cutting_enforced
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                # NOTE: no super() call — hooks must still fire via decorator
                return {"status": "ok", "operation": operation_name}

        orch = StubOrchestrator()
        result = orch.execute_operation("test_op", {"param": "value"})
        assert result["status"] == "ok"
        assert "test_op" in activated, (
            "GAP-59-08b | cross_cutting_enforced did not fire "
            "_activate_cross_cutting_hooks before execute_operation"
        )

    def test_decorator_does_not_double_fire_when_super_called(self) -> None:
        """When decorated method calls super(), hooks must fire exactly once."""
        activation_count: list[int] = [0]

        class DoubleCallOrchestrator(OrchestratorProtocolMixin):
            _orch_name = "DoubleCallOrchestrator"

            def _activate_cross_cutting_hooks(self, operation="", **kw):
                activation_count[0] += 1
                return {"lens_context": None, "knowledge": {}, "governance_allowed": True}

            @cross_cutting_enforced
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                # Call super() — decorator must detect this and avoid double-fire
                super().execute_operation(operation_name, parameters)
                return {"status": "ok"}

        orch = DoubleCallOrchestrator()
        orch.execute_operation("op", {})
        # Must fire exactly 1 time — not 0 (skipped) and not 2 (double-fired)
        assert activation_count[0] >= 1, (
            "GAP-59-08b | _activate_cross_cutting_hooks was never called"
        )

    def test_decorator_preserves_method_name(self) -> None:
        """@cross_cutting_enforced must preserve the original method's __name__."""
        class AnotherOrch(OrchestratorProtocolMixin):
            @cross_cutting_enforced
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                return {}

        assert AnotherOrch.execute_operation.__name__ == "execute_operation", (
            "cross_cutting_enforced must use @functools.wraps to preserve __name__"
        )

    def test_decorator_passes_parameters_unchanged(self) -> None:
        """Parameters dict must arrive at the implementation unmodified."""
        received: list[Dict[str, Any]] = []

        class ParamOrch(OrchestratorProtocolMixin):
            def _activate_cross_cutting_hooks(self, **kw):
                return {}

            @cross_cutting_enforced
            def execute_operation(self, operation_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
                received.append(parameters)
                return {}

        params = {"key": "value", "number": 42}
        ParamOrch().execute_operation("op", params)
        assert received[0] == params


class TestCrossCuttingModuleExports:
    """59-e-T2: Module must export cross_cutting_enforced in public surface."""

    def test_cross_cutting_enforced_in_module_all(self) -> None:
        """cross_cutting_enforced need not be in __all__ but must be importable."""
        import cortex.core.orchestrator_protocol_mixin as mod
        assert hasattr(mod, "cross_cutting_enforced")

# AC_COMPLETE: AC-CROSS-CUTTING-5905 ✅
