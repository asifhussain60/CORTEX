"""
OrchestratorProtocolMixin — Wiring contract compliance for all orchestrators.

Provides default implementations of the 7 IOrchestrator interface methods
so that orchestrators which extend plain ``object`` can satisfy the wiring
contract's ``validation.required_methods`` without requiring ABC inheritance.

Usage::

    class MyOrchestrator(OrchestratorProtocolMixin):
        _orch_name = "MyOrchestrator"
        _orch_version = "1.0.0"

Or override ``get_name`` / ``get_version`` directly.

Authority: Phase 13 Sub-Phase D — Base Class Convergence
CORE-011 (type hints), CORE-012 (docstrings)
"""

from typing import Any, Dict, List, Optional


class OrchestratorProtocolMixin:
    """Mixin providing default IOrchestrator protocol methods.

    Subclasses may override any method. The defaults use ``_orch_name``
    and ``_orch_version`` class attributes when available, falling back
    to ``self.__class__.__name__`` and ``"1.0.0"``.
    """

    _orch_name: str = ""
    _orch_version: str = "1.0.0"

    # ------------------------------------------------------------------
    # Required by wiring contract validation.required_methods
    # ------------------------------------------------------------------

    def get_name(self) -> str:
        """Return orchestrator name."""
        return self._orch_name or self.__class__.__name__

    def get_version(self) -> str:
        """Return orchestrator version."""
        return self._orch_version

    def initialize(self) -> Dict[str, Any]:
        """Initialize orchestrator (idempotent).

        Returns:
            Dict with ``status`` key.
        """
        return {"status": "initialized", "orchestrator": self.get_name()}

    # ------------------------------------------------------------------
    # Optional by wiring contract validation.optional_methods
    # ------------------------------------------------------------------

    def get_mode(self) -> str:
        """Return current operation mode as string."""
        return "EXECUTION"

    def get_mcp_tools(self) -> Dict[str, Any]:
        """Return MCP tools exposed by this orchestrator."""
        return {}

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute a named operation with parameters.

        Default delegates to ``self.run()`` or ``self.execute()`` if present.
        """
        if hasattr(self, "run"):
            return self.run(parameters)  # type: ignore[arg-type]
        if hasattr(self, "execute"):
            return self.execute(operation_name, parameters)  # type: ignore[arg-type]
        return {"status": "not_implemented", "operation": operation_name}

    def get_audit_trail(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Return audit trail entries (up to *limit*)."""
        return []

    def health_check(self) -> Dict[str, Any]:
        """Return orchestrator health status."""
        return {
            "status": "healthy",
            "orchestrator": self.get_name(),
            "version": self.get_version(),
        }
