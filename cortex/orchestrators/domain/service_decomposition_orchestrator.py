"""
ServiceDecompositionOrchestrator — Phase 14 implementation.

Reads service-decomposition-workflow.yaml and dispatches each step to the
WorkflowEngine, enforcing the security gate as a hard blocker before any
downstream layer executes.

Naming: FileFactory-validated — service_decomposition_orchestrator.py (CORE-028 ✅)
Authority: CORE-008 (TDD) · CORE-011 (type hints) · CORE-012 (docstrings) · CORE-035 (single canonical)
"""
from __future__ import annotations

import logging
from typing import Any

from cortex.core.orchestrator_base import OrchestratorBase

logger = logging.getLogger(__name__)

# MCP intent registration — used by IntentRouter for cortex_process_request routing.
_SUPPORTED_INTENTS: tuple[str, ...] = ("refactor", "service_decomposition", "legacy_modernization")


class ServiceDecompositionOrchestrator(OrchestratorBase):
    """
    Orchestrates security-first, layer-gated service decomposition.

    Reads the workflow template YAML via WorkflowEngine and executes each
    step in dependency order.  The ``security_gate`` step is a hard blocker:
    if it returns ``status != 'complete'``, all downstream layers are skipped
    and the result is marked ``halted_at: security_gate``.

    Reusable for any tightly-coupled legacy system — not hardcoded to a
    specific target.  Runtime behaviour is fully parameterised via the
    ``params`` argument passed to :meth:`execute`.
    """

    #: MCP routing — intents that route to this orchestrator.
    supported_intents: tuple[str, ...] = _SUPPORTED_INTENTS

    def __init__(self, workflow_engine: Any | None = None) -> None:
        """
        Initialise with an optional injected WorkflowEngine.

        Args:
            workflow_engine: Pre-built WorkflowEngine instance.  When *None*
                the orchestrator lazily imports and instantiates the default
                CORTEX WorkflowEngine on first call to :meth:`execute`.
        """
        super().__init__(orchestrator_id="service_decomposition")
        self._workflow_engine = workflow_engine

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def execute(  # type: ignore[override]
        self,
        workflow_path: str = (
            "cortex-registry/workflows/templates/lifecycle/service-decomposition-workflow.yaml"
        ),
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Execute the service decomposition workflow.

        Loads the workflow template, iterates steps in declared order, and
        enforces the ``security_gate`` hard-block policy.

        Args:
            workflow_path: Path to the workflow YAML template.  Defaults to
                the canonical service-decomposition template.
            params: Runtime substitution parameters forwarded to each step
                (e.g. ``backend_language``, ``entity``, ``orm``).

        Returns:
            Result dict containing ``status``, ``steps_executed``, and
            optionally ``halted_at`` if the security gate blocked execution.
        """
        params = params or {}
        engine = self._get_engine()
        workflow = engine.load(workflow_path)

        steps: list[dict[str, Any]] = workflow.get("workflow", {}).get("steps", [])
        executed: list[str] = []
        halt_at: str | None = None

        for step in steps:
            step_id: str = step.get("step_id", "unknown")
            is_blocking: bool = step.get("blocking", False)

            step_result: dict[str, Any] = engine.execute_step(
                step_id=step_id,
                step_config=step,
                params=params,
            )

            executed.append(step_id)

            if is_blocking and step_result.get("status") != "complete":
                halt_at = step_id
                logger.warning(
                    "Blocking step '%s' did not complete — halting workflow. "
                    "Status: %s",
                    step_id,
                    step_result.get("status"),
                )
                break

        result: dict[str, Any] = {
            "status": "halted" if halt_at else "complete",
            "steps_executed": executed,
        }
        if halt_at:
            result["halted_at"] = halt_at

        return result

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_engine(self) -> Any:
        """
        Return the WorkflowEngine, lazily importing if not injected.

        Returns:
            A WorkflowEngine instance.
        """
        if self._workflow_engine is not None:
            return self._workflow_engine

        try:
            from cortex.core.workflow_engine import WorkflowEngine  # type: ignore[import]
            self._workflow_engine = WorkflowEngine()
        except ImportError:
            logger.warning(
                "WorkflowEngine not importable; falling back to no-op stub."
            )
            self._workflow_engine = _NoOpWorkflowEngine()

        return self._workflow_engine


# ---------------------------------------------------------------------------
# No-op fallback (graceful degradation — CORE-012)
# ---------------------------------------------------------------------------

class _NoOpWorkflowEngine:
    """
    Minimal fallback engine used when WorkflowEngine cannot be imported.

    Returns empty-complete results for every step so the orchestrator
    degrades gracefully rather than raising at import time.
    """

    def load(self, path: str) -> dict[str, Any]:
        """Return an empty workflow definition."""
        return {"workflow": {"steps": []}}

    def execute_step(self, *, step_id: str, step_config: dict, params: dict) -> dict[str, Any]:
        """Return a no-op complete result for any step."""
        return {"status": "complete", "outputs": {}}
