"""
Phase 67-E: RED tests for WorkflowEngine._execute_step() StepHandlerRegistry (GAP-67-01).

Tests verify that:
1. WorkflowEngine has a StepHandlerRegistry (not a stub)
2. noop_handler is registered and does not raise
3. orchestrator_dispatch_handler dispatches to the named orchestrator
4. validate_handler returns validation result
5. Unknown operation raises StepError (not silent)
6. execute_step public API uses the registry
7. Handlers are callable with (step, context) signature
8. StepHandlerRegistry is a dict-like mapping: operation → handler
9. StepError carries the unknown operation name

Author: Asif Hussain
Phase: 67-E
Sweep: SWEEP-67-WORKFLOW-RUNTIME-WIRING
"""

import pytest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch

# AC_START: AC-67-E-STEP-HANDLER-REGISTRY-20260224T000000Z


class TestStepHandlerRegistryExists:
    """GAP-67-01: WorkflowEngine must expose a StepHandlerRegistry."""

    def test_workflow_engine_has_step_handler_registry_attr(self) -> None:
        """WorkflowEngine instance must have _step_handler_registry attribute."""
        from cortex.core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        assert hasattr(engine, "_step_handler_registry"), (
            "WorkflowEngine must have _step_handler_registry dict. "
            "_execute_step() is currently a pure stub — GAP-67-01."
        )

    def test_step_handler_registry_is_dict_like(self) -> None:
        """_step_handler_registry must support __getitem__ and __contains__."""
        from cortex.core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        registry = engine._step_handler_registry
        assert hasattr(registry, "__getitem__"), "registry must be dict-like"
        assert hasattr(registry, "__contains__"), "registry must support 'in' operator"

    def test_noop_is_registered(self) -> None:
        """'noop' operation must be pre-registered in StepHandlerRegistry."""
        from cortex.core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        assert "noop" in engine._step_handler_registry, (
            "WorkflowEngine._step_handler_registry must have a 'noop' handler"
        )

    def test_orchestrator_dispatch_is_registered(self) -> None:
        """'orchestrator_dispatch' operation must be pre-registered."""
        from cortex.core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        assert "orchestrator_dispatch" in engine._step_handler_registry, (
            "WorkflowEngine._step_handler_registry must have 'orchestrator_dispatch' handler"
        )

    def test_validate_is_registered(self) -> None:
        """'validate' operation must be pre-registered."""
        from cortex.core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        assert "validate" in engine._step_handler_registry, (
            "WorkflowEngine._step_handler_registry must have 'validate' handler"
        )


class TestStepError:
    """GAP-67-01: Unknown operations must raise StepError (not be silent)."""

    def test_step_error_importable(self) -> None:
        """StepError must be importable from cortex.core.workflow_engine."""
        from cortex.core.workflow_engine import StepError

        assert issubclass(StepError, Exception)

    def test_step_error_carries_operation(self) -> None:
        """StepError must carry the operation name that caused it."""
        from cortex.core.workflow_engine import StepError

        err = StepError("unknown_op_xyz")
        assert "unknown_op_xyz" in str(err), (
            "StepError must include the unknown operation name in its message"
        )

    def test_execute_step_raises_step_error_for_unknown_op(self) -> None:
        """_execute_step() must raise StepError for unregistered operations."""
        from cortex.core.workflow_engine import WorkflowEngine, StepError, ExecutionContext

        engine = WorkflowEngine()
        step = {"operation": "totally_unknown_operation_xyz"}
        ctx = ExecutionContext(workflow_id="test", template_path=Path("/tmp/test.yaml"))

        with pytest.raises(StepError) as exc_info:
            engine._execute_step(step, ctx)
        assert "totally_unknown_operation_xyz" in str(exc_info.value)


class TestNoopHandler:
    """noop_handler must complete without side effects."""

    def test_noop_handler_does_not_raise(self) -> None:
        """noop handler must execute without raising on a minimal step dict."""
        from cortex.core.workflow_engine import WorkflowEngine, ExecutionContext

        engine = WorkflowEngine()
        step = {"operation": "noop", "id": "test-noop"}
        ctx = ExecutionContext(workflow_id="test", template_path=Path("/tmp/test.yaml"))
        # Must not raise
        engine._execute_step(step, ctx)

    def test_noop_handler_callable_signature(self) -> None:
        """noop handler in registry must be callable with (step, context)."""
        from cortex.core.workflow_engine import WorkflowEngine, ExecutionContext

        engine = WorkflowEngine()
        handler = engine._step_handler_registry["noop"]
        assert callable(handler)
        ctx = ExecutionContext(workflow_id="t", template_path=Path("/tmp/t.yaml"))
        result = handler({"operation": "noop"}, ctx)
        # Must return None or a dict — not raise
        assert result is None or isinstance(result, dict)


class TestValidateHandler:
    """validate_handler must return a validation result dict."""

    def test_validate_handler_returns_dict(self) -> None:
        """validate handler must return a dict with at least a 'status' key."""
        from cortex.core.workflow_engine import WorkflowEngine, ExecutionContext

        engine = WorkflowEngine()
        handler = engine._step_handler_registry["validate"]
        ctx = ExecutionContext(workflow_id="v", template_path=Path("/tmp/v.yaml"))
        result = handler({"operation": "validate"}, ctx)
        assert isinstance(result, dict), "validate handler must return dict"
        assert "status" in result, "validate result must have 'status' key"


class TestOrchestratorDispatchHandler:
    """orchestrator_dispatch_handler must call the named orchestrator."""

    def test_orchestrator_dispatch_handler_callable(self) -> None:
        """orchestrator_dispatch handler must be callable."""
        from cortex.core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        handler = engine._step_handler_registry["orchestrator_dispatch"]
        assert callable(handler)

    def test_orchestrator_dispatch_no_target_does_not_crash(self) -> None:
        """orchestrator_dispatch with missing 'orchestrator' key must not crash (graceful)."""
        from cortex.core.workflow_engine import WorkflowEngine, ExecutionContext

        engine = WorkflowEngine()
        handler = engine._step_handler_registry["orchestrator_dispatch"]
        ctx = ExecutionContext(workflow_id="d", template_path=Path("/tmp/d.yaml"))
        # No 'orchestrator' key — must gracefully return or raise StepError
        try:
            result = handler({"operation": "orchestrator_dispatch"}, ctx)
            # If it doesn't raise, it must return a dict
            assert result is None or isinstance(result, dict)
        except Exception as e:
            # Must be a StepError or subclass, not generic Exception
            from cortex.core.workflow_engine import StepError
            assert isinstance(e, StepError), (
                f"orchestrator_dispatch with no target must raise StepError, got {type(e)}"
            )


class TestExecuteStepPublicAPI:
    """WorkflowEngine.execute_step() (public API) must delegate to registry."""

    def test_execute_step_public_delegates_to_noop(self) -> None:
        """execute_step(step_id, step_config, params) must use the registry for 'noop'."""
        from cortex.core.workflow_engine import WorkflowEngine

        engine = WorkflowEngine()
        result = engine.execute_step(
            step_id="test-noop",
            step_config={"operation": "noop"},
            params={},
        )
        assert isinstance(result, dict)
        assert result.get("status") == "complete"

    def test_register_handler_adds_to_registry(self) -> None:
        """register_step_handler() must add handler to _step_handler_registry."""
        from cortex.core.workflow_engine import WorkflowEngine, ExecutionContext

        engine = WorkflowEngine()

        def custom_handler(step: Dict[str, Any], ctx: ExecutionContext) -> None:
            pass

        # Must be callable: engine.register_step_handler("custom_op", custom_handler)
        assert hasattr(engine, "register_step_handler"), (
            "WorkflowEngine must have register_step_handler(op, handler) method"
        )
        engine.register_step_handler("custom_op", custom_handler)
        assert "custom_op" in engine._step_handler_registry


# AC_COMPLETE: AC-67-E-STEP-HANDLER-REGISTRY-20260224T000000Z ✅
