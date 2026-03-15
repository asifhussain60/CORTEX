"""context_assembly_orchestrator.py — Context Assembly Orchestrator.

Assembles unified orchestrator context from multiple workspace sources
(Phase 84-d, GAP-84-12). Reads each source path and merges discovered
metadata into a single context dictionary for downstream orchestrators.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations
from typing import Any
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94f
from cortex.core.context_validator import ContextValidator


class ContextAssemblyOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Assembles unified context for orchestrator invocations."""

    orchestrator_name = "ContextAssemblyOrchestrator"
    domain = "support"

    # Phase 94f — advisory: context assembly utility, not a code-execution entry point.
    # Invoked by intelligence pipeline. Gateway routing deferred.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(self) -> None:
        """Initialise ContextAssemblyOrchestrator."""
        self._request_count = 0
        self._success_count = 0
        self._context_validator = ContextValidator()

    def assemble(self, sources: list[str]) -> dict[str, Any]:
        """Assemble context from multiple workspace sources.

        Reads each source path and merges discovered metadata into a unified
        context dictionary for downstream orchestrators.

        Args:
            sources: List of context source paths or keys.

        Returns:
            Assembled context dictionary with merged data per source.
        """
        self._activate_cross_cutting_hooks(operation="assemble")
        self._request_count += 1
        from pathlib import Path as _Path
        context: dict[str, Any] = {}
        for src in sources:
            p = _Path(src)
            if p.exists() and p.is_file():
                try:
                    context[src] = {"content": p.read_text(encoding="utf-8", errors="replace")[:512], "type": "file"}
                except Exception:
                    context[src] = {"type": "file", "error": "unreadable"}
            elif p.exists() and p.is_dir():
                entries = [e.name for e in p.iterdir() if not e.name.startswith(".")][:20]
                context[src] = {"type": "directory", "entries": entries}
            else:
                context[src] = {"type": "key", "value": src}

        validation_payload = self._build_validation_payload(sources)
        is_valid, errors = self._context_validator.validate(validation_payload)

        self._success_count += 1
        return {
            "sources": sources,
            "context": context,
            "assembled": True,
            "context_validation": {
                "is_valid": is_valid,
                "errors": errors,
                "missing_keys": self._context_validator.get_missing_keys(validation_payload),
            },
        }

    def _build_validation_payload(self, sources: list[str]) -> dict[str, Any]:
        """Build validation payload for assembled context.

        Args:
            sources: Source entries passed to assemble.

        Returns:
            Minimal context payload for ContextValidator.
        """
        candidate_files = [
            source
            for source in sources
            if source and source.strip() and source.endswith((".py", ".md", ".yaml", ".yml", ".json", ".toml", ".ini", ".txt"))
        ]
        return {
            "intent": "context_assembly",
            "files": candidate_files,
        }

    def health_check(self) -> dict[str, Any]:
        """Return health status."""
        return {"status": "healthy", "orchestrator": self.orchestrator_name,
                "uptime_requests": self._request_count, "success_count": self._success_count, "last_success": None}
