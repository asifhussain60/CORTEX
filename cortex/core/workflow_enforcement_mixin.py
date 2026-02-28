"""
WorkflowEnforcementMixin — Phase 90: Mandatory Gateway Opt-in for Orchestrators.

Drop-in mixin that adds execute_via_gateway() to any orchestrator. When
PHASE90_GATEWAY_ENABLED = True the mixin routes all execution through
WorkflowGateway instead of calling execute_operation() directly.

Also provides:
  enforce_gateway — decorator (Phase 90c) that closes the bypass gap.
    Apply to any execute_operation() override: when PHASE90_GATEWAY_ENABLED=True
    the decorator intercepts the call and routes it through WorkflowGateway
    before the original method body executes. No-op when disabled.

Migration path (zero big-bang risk):
  1. Orchestrator inherits WorkflowEnforcementMixin alongside existing bases
  2. Set PHASE90_GATEWAY_ENABLED = False (default) — zero behaviour change
  3. When ready: PHASE90_GATEWAY_ENABLED = True — gateway takes over
  4. Optionally decorate execute_operation() with @enforce_gateway to close bypass gap

Design: Liskov-safe — WorkflowEnforcementMixin is compatible with any class
that implements execute_operation(operation_name, parameters).

AC_START: AC-P90-WEM-001
Phase: 90 | Priority: P0 | Phase 90c: enforce_gateway decorator
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

from __future__ import annotations

import functools
import logging
from typing import Any, Callable, Dict, Optional, TypeVar

logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def enforce_gateway(method: F) -> F:
    """Decorator that closes the bypass gap on ``execute_operation`` overrides.

    When applied to an ``execute_operation`` method on a class that inherits
    ``WorkflowEnforcementMixin``, this decorator intercepts the call and
    routes it through ``WorkflowGateway`` when ``PHASE90_GATEWAY_ENABLED=True``.

    When ``PHASE90_GATEWAY_ENABLED=False`` (default), the decorator is a
    transparent no-op — the original method executes as usual.

    This closes the architectural bypass gap (Phase 90c, Tension 1): an
    orchestrator could previously skip the gateway by calling
    ``execute_operation()`` directly without going through
    ``execute_via_gateway()``. With this decorator on the override,
    the gateway fires regardless of the call site.

    Design mirrors ``cross_cutting_enforced`` from ``OrchestratorProtocolMixin``
    (Phase 59-e).

    Args:
        method: The ``execute_operation`` method to decorate.

    Returns:
        Wrapped method that routes through WorkflowGateway when enabled.

    Example::

        class TDDOrchestrator(WorkflowEnforcementMixin, OrchestratorProtocolMixin, ...):
            PHASE90_GATEWAY_ENABLED = True

            @enforce_gateway
            def execute_operation(self, mode: str, params: dict) -> Any:
                # This body is BYPASSED when gateway is enabled.
                # Gateway calls WorkflowComposer instead.
                ...

    Note:
        ``mode`` is taken from the first positional argument of
        ``execute_operation(self, mode_or_operation_name, parameters)``.
        This matches the ``OrchestratorProtocolMixin.execute_operation``
        signature.
    """
    @functools.wraps(method)
    def _wrapper(self: Any, *args: Any, **kwargs: Any) -> Any:
        # Resolve mode/operation_name from positional or keyword args.
        # Supports both: execute_operation("IMPLEMENT", {...})
        #            and execute_operation(operation_name="IMPLEMENT", parameters={...})
        if args:
            mode_or_operation: str = args[0]
            parameters: Dict[str, Any] = args[1] if len(args) > 1 else kwargs.pop("parameters", {})
        else:
            mode_or_operation = kwargs.pop(
                "operation_name",
                kwargs.pop("mode_or_operation", kwargs.pop("operation", "")),
            )
            parameters = kwargs.pop("parameters", kwargs.pop("context", {}))
        if getattr(self, "PHASE90_GATEWAY_ENABLED", False):
            gateway = self._get_gateway()
            orchestrator_name = getattr(self, "_orch_name", None) or type(self).__name__
            return gateway.execute_gated(
                orchestrator_name=orchestrator_name,
                mode=mode_or_operation,
                context=parameters,
            )
        # Gateway disabled — fall through to original method (zero behaviour change)
        # Pass remaining kwargs through for methods with extended signatures.
        if kwargs:
            return method(self, mode_or_operation, parameters, **kwargs)
        return method(self, mode_or_operation, parameters)

    return _wrapper  # type: ignore[return-value]


class WorkflowEnforcementMixin:
    """Mixin that gates execute_operation() calls through WorkflowGateway.

    Provides a safe, opt-in migration path for all operational orchestrators
    to adopt mandatory Workflow Composer routing (Phase 90).

    Class Attributes:
        PHASE90_GATEWAY_ENABLED: Set to True to activate gateway routing.
            Defaults to False for zero-risk rollout.

    Usage (opt-in)::

        class TDDOrchestrator(WorkflowEnforcementMixin, OrchestratorProtocolMixin, ...):
            PHASE90_GATEWAY_ENABLED = True

            def execute_operation(self, name, params):
                # Called by execute_via_gateway when gateway routes back to impl
                ...

        # At call site:
        result = orch.execute_via_gateway(mode="IMPLEMENT", parameters={...})

    Usage (disabled — no behaviour change)::

        class LegacyOrchestrator(WorkflowEnforcementMixin, ...):
            PHASE90_GATEWAY_ENABLED = False  # default

        result = orch.execute_via_gateway(mode="IMPLEMENT", parameters={...})
        # Falls through to execute_operation() directly — identical to current behaviour
    """

    # ── Class-level opt-in flag ───────────────────────────────────────────
    PHASE90_GATEWAY_ENABLED: bool = False

    # Injected for testing; lazily initialized otherwise
    _gateway: Optional[Any] = None

    def execute_via_gateway(
        self,
        mode: str,
        parameters: Dict[str, Any],
    ) -> Any:
        """Execute an operation through the mandatory WorkflowGateway.

        When PHASE90_GATEWAY_ENABLED is True:
          1. Instantiates (or reuses) WorkflowGateway
          2. Calls gateway.execute_gated(orchestrator_name, mode, context)
          3. Returns gated result (includes template_id, run_id, trace)

        When PHASE90_GATEWAY_ENABLED is False:
          - Falls through to execute_operation(mode, parameters) directly.
          - Zero behaviour change — safe migration path.

        Args:
            mode: Operation mode string (e.g. "IMPLEMENT", "FIX", "REFACTOR").
            parameters: Operation parameters forwarded to gateway or execute_operation.

        Returns:
            Result from gateway or execute_operation.
        """
        if not self.PHASE90_GATEWAY_ENABLED:
            # Graceful degradation — call execute_operation directly
            logger.debug(
                "WorkflowEnforcementMixin: gateway disabled for %s — "
                "calling execute_operation directly.",
                type(self).__name__,
            )
            return self.execute_operation(mode, parameters)  # type: ignore[attr-defined]

        gateway = self._get_gateway()
        orchestrator_name = getattr(self, "_orch_name", type(self).__name__)

        return gateway.execute_gated(
            orchestrator_name=orchestrator_name,
            mode=mode,
            context=parameters,
        )

    def get_gateway(self) -> Any:
        """Return the WorkflowGateway instance used by this mixin.

        Returns:
            WorkflowGateway instance (lazily initialized).
        """
        return self._get_gateway()

    # ── INTERNAL ──────────────────────────────────────────────────────────

    def _get_gateway(self) -> Any:
        """Lazy-initialize WorkflowGateway (or return injected mock).

        Returns:
            WorkflowGateway instance.
        """
        if self._gateway is not None:
            return self._gateway

        from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
        self._gateway = WorkflowGateway()
        return self._gateway


# AC_COMPLETE: AC-P90-WEM-001 ✅ WorkflowEnforcementMixin implemented
