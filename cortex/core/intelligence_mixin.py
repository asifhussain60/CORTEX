"""
IntelligenceMixin — Cross-cutting intelligence injection for all CORTEX orchestrators.

Provides lazy-loaded LENS access, unified context forwarding, knowledge synthesis
queries, and AC-marker-backed SQLite audit trail. Designed to mirror the
OrchestratorProtocolMixin pattern (Phase 13) so any orchestrator gains intelligence
capabilities with a single base-class addition — zero logic changes required.

Usage::

    class MyOrchestrator(OrchestratorProtocolMixin, IntelligenceMixin):
        _orch_name = "MyOrchestrator"

Design principles:
- Defaults gracefully degrade when LENS / KnowledgeSynthesisEngine unavailable.
- Every public method emits AC_START / AC_COMPLETE to an in-memory ``_ac_log``
  (queryable by golden tests and ExternalAuditDB when wired).
- No circular imports — all heavy imports are deferred inside methods.
- CORE-035: single canonical implementation.
- CORE-011: type hints on all functions.
- CORE-012: docstrings on all public APIs.

Authority: Phase 57 — Intelligence Propagation Plan
Governance: CORE-008 (TDD) · CORE-011 · CORE-012 · CORE-035 · CORE-049 · CORE-064
Agent: cortex-executor.md · architecture-integrity-agent.md
"""

from __future__ import annotations

import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional


class IntelligenceMixin:
    """Mixin that injects LENS, knowledge synthesis, and unified context into any orchestrator.

    All methods degrade gracefully when intelligence subsystems are unavailable.
    AC markers are emitted to ``_ac_log`` (in-memory list of dicts) so golden tests
    and ExternalAuditDB consumers can assert audit completeness.

    Subclasses may override any method for full custom behaviour.
    """

    # -------------------------------------------------------------------------
    # Internal state — initialised lazily to avoid __init__ conflicts
    # -------------------------------------------------------------------------
    _unified_context: Dict[str, Any]
    _lens_context: Optional[Dict[str, Any]]
    _ac_log: List[Dict[str, Any]]

    # -------------------------------------------------------------------------
    # AC Marker support
    # -------------------------------------------------------------------------

    def _emit_ac_marker(
        self,
        marker: str,
        operation: str,
        *,
        entry_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Emit an AC audit marker to ``_ac_log``.

        Args:
            marker: One of ``AC_START``, ``AC_COMPLETE``, ``AC_FAILURE``.
            operation: Short operation name (e.g., ``LENS_CONTEXT``).
            entry_id: Optional correlation ID; generated if absent.
            metadata: Extra metadata to store with the entry.

        Returns:
            The entry_id used (for pairing AC_START → AC_COMPLETE).
        """
        if not hasattr(self, "_ac_log"):
            object.__setattr__(self, "_ac_log", [])

        eid = entry_id or str(uuid.uuid4())[:8]
        entry: Dict[str, Any] = {
            "id": eid,
            "marker": marker,
            "operation": operation,
            "orchestrator": getattr(self, "_orch_name", self.__class__.__name__),
            "timestamp_ms": int(time.time() * 1000),
        }
        if metadata:
            entry["metadata"] = metadata
        self._ac_log.append(entry)

        # --- SQLite persistence (Check #28 fix) ---
        # Non-fatal: in-memory _ac_log is the source of truth.
        try:
            from cortex.infrastructure.orchestrator_trace_logger import (
                OrchestratorTraceLogger,
            )

            OrchestratorTraceLogger().write_ac_marker(
                marker=marker,
                operation=operation,
                orchestrator_class=entry["orchestrator"],
                entry_id=eid,
                duration_ms=float(metadata.get("duration_ms", 0)) if metadata else None,
                metadata=metadata,
            )
        except Exception:  # pragma: no cover — non-fatal persistence guard
            pass

        return eid

    # -------------------------------------------------------------------------
    # Public intelligence API
    # -------------------------------------------------------------------------

    def get_lens_context(
        self,
        target_files: List[Path],
        *,
        depth: str = "standard",
    ) -> Dict[str, Any]:
        """Lazy-load LENS analysis for *target_files*.

        Args:
            target_files: Files or directories to analyse.
            depth: Analysis depth — ``shallow | standard | deep``.

        Returns:
            LENS analysis result dict. On failure returns ``{"degraded": True, ...}``.
        """
        eid = self._emit_ac_marker("AC_START", "LENS_CONTEXT")
        try:
            from cortex.lens.lens_orchestrator import LENSOrchestrator  # type: ignore[import]

            orchestrator = LENSOrchestrator()
            result: Dict[str, Any] = orchestrator.analyze_files(
                [str(f) for f in target_files],
                depth=depth,
            )
            if not hasattr(self, "_lens_context"):
                object.__setattr__(self, "_lens_context", None)
            self._lens_context = result
            self._emit_ac_marker("AC_COMPLETE", "LENS_CONTEXT", entry_id=eid,
                                 metadata={"files": len(target_files), "depth": depth})
            return result
        except Exception as exc:
            degraded: Dict[str, Any] = {
                "degraded": True,
                "reason": str(exc),
                "files_requested": len(target_files),
            }
            self._emit_ac_marker("AC_COMPLETE", "LENS_CONTEXT", entry_id=eid,
                                 metadata={"degraded": True, "reason": str(exc)})
            return degraded

    def inject_unified_context(self, context: Dict[str, Any]) -> None:
        """Receive and store a forwarded ``UnifiedIntelligenceContext`` from MasterOrchestrator.

        MasterOrchestrator Stage 4 calls this immediately before routing to a domain
        orchestrator so the orchestrator operates with full pipeline awareness.

        Args:
            context: Synthesised context dict containing intent, LENS findings,
                     knowledge artifacts, and synthesis_id.
        """
        eid = self._emit_ac_marker("AC_START", "INJECT_CONTEXT")
        object.__setattr__(self, "_unified_context", context)
        self._emit_ac_marker("AC_COMPLETE", "INJECT_CONTEXT", entry_id=eid,
                             metadata={"synthesis_id": context.get("synthesis_id", "unknown")})

    def query_knowledge(
        self,
        domain: str,
        query: str,
        *,
        max_results: int = 5,
    ) -> Dict[str, Any]:
        """Query KnowledgeSynthesisEngine for domain-specific best-practice knowledge.

        Args:
            domain: Knowledge domain (e.g., ``architecture``, ``testing``, ``security``).
            query: Natural-language query string.
            max_results: Maximum number of knowledge artifacts to return.

        Returns:
            Knowledge result dict. On failure returns ``{"degraded": True, ...}``.
        """
        eid = self._emit_ac_marker("AC_START", "KNOWLEDGE_QUERY")
        try:
            from cortex.intelligence.knowledge.knowledge_synthesis_engine import (  # type: ignore[import]
                KnowledgeSynthesisEngine,
            )

            engine = KnowledgeSynthesisEngine()
            result: Dict[str, Any] = engine.query(
                domain=domain,
                query=query,
                max_results=max_results,
            )
            self._emit_ac_marker("AC_COMPLETE", "KNOWLEDGE_QUERY", entry_id=eid,
                                 metadata={"domain": domain, "max_results": max_results})
            return result
        except Exception as exc:
            degraded = {
                "degraded": True,
                "reason": str(exc),
                "domain": domain,
                "query": query,
            }
            self._emit_ac_marker("AC_COMPLETE", "KNOWLEDGE_QUERY", entry_id=eid,
                                 metadata={"degraded": True, "reason": str(exc)})
            return degraded

    def get_unified_context(self) -> Dict[str, Any]:
        """Return the currently injected unified context (empty dict if not yet injected).

        Returns:
            Previously injected context dict, or empty dict.
        """
        return getattr(self, "_unified_context", {})

    def get_ac_log(self) -> List[Dict[str, Any]]:
        """Return the internal AC audit marker log (copy).

        Primarily used by golden tests and audit verification.

        Returns:
            Shallow copy of ``_ac_log`` entries.
        """
        return list(getattr(self, "_ac_log", []))
