"""
CORTEX MCP Tools Shared Utilities (CORE-035: Single Canonical Implementation)

This module is the SSOT for all shared MCP tool utilities.
All MCP tool files MUST import from here — never copy-paste.

Authority: CORE-035 | CORE-011 | CORE-012
"""
from typing import Any, Dict, Optional


def validate_orchestrator_context(context: Optional[Dict[str, Any]]) -> None:
    """
    Validate that a request originates from MasterOrchestrator.

    All MCP tools are restricted to requests routed through the
    MasterOrchestrator pipeline. This function enforces that invariant
    at every tool boundary.

    Args:
        context: Orchestrator context dict expected to contain a
                 ``source`` key with value ``"MasterOrchestrator"``.

    Raises:
        ValueError: If *context* is missing or ``source`` is not
                    ``"MasterOrchestrator"``.

    Example::

        validate_orchestrator_context({"source": "MasterOrchestrator"})  # OK
        validate_orchestrator_context(None)  # raises ValueError
    """
    if not context:
        raise ValueError(
            "BLOCKED: Missing orchestrator_context. All requests MUST route "
            "through MasterOrchestrator via cortex_process_request or "
            "cortex_request_lifecycle entry point."
        )

    source = context.get("source")
    if source != "MasterOrchestrator":
        raise ValueError(
            f"BLOCKED: Request from '{source}'. Only MasterOrchestrator can "
            "invoke MCP tools directly. Use cortex_request_lifecycle entry point."
        )
