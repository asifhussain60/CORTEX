"""
OrchestratorProtocolMixin — Wiring contract compliance for all orchestrators.

Provides default implementations of the 7 IOrchestrator interface methods
so that orchestrators which extend plain ``object`` can satisfy the wiring
contract's ``validation.required_methods`` without requiring ABC inheritance.

Also provides cross-cutting intelligence helpers (Phase 58):
- _extract_lens_context()      — LENS slice from forwarded orchestrator_context
- _consume_unified_context()   — accept KnowledgeSynthesisEngine output
- _governance_gate()           — EnforcementOrchestrator pre-execution check
- _query_domain_brain()        — BusinessKnowledgeRepository lookup

Phase 59-e adds:
- cross_cutting_enforced()     — decorator that guarantees hooks fire even when
                                 subclasses override execute_operation without
                                 calling super() (GAP-59-08b)

Usage::

    class MyOrchestrator(OrchestratorProtocolMixin):
        _orch_name = "MyOrchestrator"
        _orch_version = "1.0.0"

    # OR guard a specific override:
    @cross_cutting_enforced
    def execute_operation(self, operation_name, parameters):
        ...

Authority: Phase 13 Sub-Phase D — Base Class Convergence
         Phase 58 — 100% cross-cutting utilization
         Phase 59-e — @cross_cutting_enforced decorator (GAP-59-08b)
CORE-011 (type hints), CORE-012 (docstrings)
"""

import functools
import logging
from typing import Any, Callable, Dict, List, Optional, TypeVar

_logger = logging.getLogger(__name__)

F = TypeVar("F", bound=Callable[..., Any])


def cross_cutting_enforced(method: F) -> F:
    """Decorator that guarantees cross-cutting hooks fire on execute_operation overrides.

    Apply to any ``execute_operation`` override to ensure that
    ``_activate_cross_cutting_hooks()`` is called even when the subclass
    does not call ``super().execute_operation(...)``.

    Phase 59-e: Closes GAP-59-08b — hooks bypassed by domain orchestrator overrides.

    Args:
        method: The ``execute_operation`` method to wrap.

    Returns:
        Wrapped method that pre-activates cross-cutting hooks then delegates
        to the original implementation.

    Example::

        class MyOrchestrator(OrchestratorProtocolMixin):
            @cross_cutting_enforced
            def execute_operation(self, operation_name, parameters):
                return self._do_my_work(parameters)
    """
    @functools.wraps(method)
    def _wrapper(self: Any, operation_name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        # Only activate if not already activated (avoid double-fire on super() calls)
        if not getattr(self, "_cross_cutting_activated", False):
            self._cross_cutting_activated = True
            try:
                self._activate_cross_cutting_hooks(
                    operation=operation_name,
                    orchestrator_context=parameters.get("orchestrator_context"),
                    unified_context=parameters.get("unified_context"),
                )
            finally:
                self._cross_cutting_activated = False
        return method(self, operation_name, parameters)
    return _wrapper  # type: ignore[return-value]


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
        Activates cross-cutting hooks (LENS, KnSynth, GovGate) automatically.
        """
        # Phase 58 — cross-cutting hooks on every operation
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )
        if hasattr(self, "run"):
            return self.run(parameters)  # type: ignore[arg-type]
        if hasattr(self, "execute"):
            return self.execute(operation_name, parameters)  # type: ignore[arg-type]
        return {"status": "not_implemented", "operation": operation_name}

    # ------------------------------------------------------------------
    # Cross-cutting activation hook (Phase 58 — all dimensions)
    # ------------------------------------------------------------------

    def _activate_cross_cutting_hooks(
        self,
        operation: str = "",
        orchestrator_context: Optional[Dict[str, Any]] = None,
        unified_context: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Activate LENS, KnSynth, and GovGate cross-cutting dimensions.

        Intended to be called at the top of every orchestrator's primary
        entry point (``execute_operation``, ``execute``, ``run``, etc.) to
        ensure cross-cutting intelligence is consistently activated.  The
        default ``execute_operation`` implementation calls this automatically;
        orchestrators that override ``execute_operation`` should call it
        explicitly.

        Args:
            operation: The operation name being executed.
            orchestrator_context: LENS context forwarded by IntentRouter.
            unified_context: Pre-synthesised UnifiedIntelligenceContext.

        Returns:
            Dict containing ``lens_context``, ``knowledge``, and
            ``governance_allowed`` keys.

        Authority: AC-PHASE58-B-001 (Phase 58 cross-cutting activation)
        """
        lens_ctx = self._extract_lens_context(orchestrator_context)
        knowledge = self._consume_unified_context(unified_context)
        governance_allowed = self._governance_gate(
            operation or self.get_name(), params={"lens_context": lens_ctx}
        )
        return {
            "lens_context": lens_ctx,
            "knowledge": knowledge,
            "governance_allowed": governance_allowed,
        }

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

    # ------------------------------------------------------------------
    # LENS context extraction (GAP-57-05 — Phase 57-c)
    # ------------------------------------------------------------------

    def _extract_lens_context(
        self,
        orchestrator_context: Optional[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """Extract LENS intelligence context from orchestrator_context dict.

        Domain orchestrators receive LENS context forwarded by IntentRouter
        inside ``orchestrator_context["lens_context"]``. This helper centralises
        the extraction so every domain orchestrator gets the same behaviour.

        Args:
            orchestrator_context: The full context dict passed by IntentRouter.
                                  May be None (graceful degradation).

        Returns:
            The ``lens_context`` sub-dict when present, otherwise ``None``.

        Authority: AC-PHASE57-C-001 (Phase 57-c LENS wiring)
        """
        if orchestrator_context is None:
            return None
        return orchestrator_context.get("lens_context")

    # ------------------------------------------------------------------
    # Knowledge Synthesis consumption (Phase 58 — KnSynth dimension)
    # ------------------------------------------------------------------

    def _consume_unified_context(
        self,
        unified_context: Optional[Any],
    ) -> Dict[str, Any]:
        """Accept and unwrap a pre-synthesised UnifiedIntelligenceContext.

        MasterOrchestrator Stage 3 synthesises a ``UnifiedIntelligenceContext``
        and forwards it to every downstream orchestrator.  This helper lets any
        orchestrator extract the guidance and cited-rule data without importing
        the synthesis engine directly.

        Args:
            unified_context: A ``UnifiedIntelligenceContext`` instance produced
                by ``KnowledgeSynthesisEngine.synthesize_unified_context()``, or
                ``None`` when running outside a full pipeline (graceful degradation).

        Returns:
            Dict with ``guidance`` and ``cited_rules`` lists when context is
            available; empty dict otherwise.

        Authority: AC-PHASE58-A-001 (Phase 58 KnSynth wiring)
        """
        if unified_context is None:
            return {}
        try:
            return {
                "guidance": unified_context.get_guidance(),
                "cited_rules": unified_context.get_cited_rules(),
            }
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "OrchestratorProtocolMixin._consume_unified_context: "
                "failed to unwrap UnifiedIntelligenceContext — %s", exc
            )
            return {}

    # ------------------------------------------------------------------
    # Governance gate (Phase 58 — GovGate dimension)
    # ------------------------------------------------------------------

    def _governance_gate(
        self,
        operation: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Validate an operation against CORE governance rules.

        Delegates to ``EnforcementOrchestrator.validate_operation()`` when
        available.  Non-blocking: returns ``True`` (allow) on import failure
        so that optional wiring does not break orchestrators running outside
        a full CORTEX environment.

        Args:
            operation: Human-readable operation name (e.g. ``"refactor"``).
            params: Optional extra context forwarded to the enforcement engine.

        Returns:
            ``True`` if the operation is permitted (or enforcement is
            unavailable), ``False`` if explicitly blocked by a CORE rule.

        Authority: AC-PHASE58-A-002 (Phase 58 GovGate wiring)
        """
        try:
            from cortex.orchestrators.core.enforcement_orchestrator import (  # noqa: PLC0415
                EnforcementOrchestrator,
            )
            # Guard: skip if caller is EnforcementOrchestrator (would recurse)
            if isinstance(self, EnforcementOrchestrator):
                return True
            result = EnforcementOrchestrator().validate_operation(
                {"operation": operation, **(params or {})}
            )
            # validate_operation may return bool or a Result-like object
            if isinstance(result, bool):
                return result
            if hasattr(result, "is_ok"):
                return result.is_ok()
            return bool(result)
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "OrchestratorProtocolMixin._governance_gate: "
                "EnforcementOrchestrator unavailable — %s", exc
            )
            return True  # non-blocking degraded mode

    # ------------------------------------------------------------------
    # Domain Brain query (Phase 58 — DomainBrain dimension)
    # ------------------------------------------------------------------

    def _query_domain_brain(
        self,
        query: str,
        domain: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Query the Domain Brain knowledge graph.

        Provides decision-making orchestrators access to the
        ``BusinessKnowledgeRepository`` and domain-intent classification
        without requiring a direct import chain.

        Args:
            query: Free-text query or intent string.
            domain: Optional domain name to scope the query
                    (e.g. ``"refactoring"``, ``"planning"``).

        Returns:
            Dict with ``entries`` list and optional ``domain_context`` when
            the Domain Brain is available; empty dict otherwise.

        Authority: AC-PHASE58-A-003 (Phase 58 DomainBrain wiring)
        """
        try:
            from cortex.intelligence.domain_brain import DomainBrainAPI  # noqa: PLC0415
            brain = DomainBrainAPI()
            # DomainBrainAPI.query() returns matching knowledge entries
            if hasattr(brain, "query"):
                entries = brain.query(query, domain=domain)
            else:
                entries = []
            return {"entries": entries, "domain": domain, "query": query}
        except Exception as exc:  # noqa: BLE001
            _logger.warning(
                "OrchestratorProtocolMixin._query_domain_brain: "
                "DomainBrainAPI unavailable — %s", exc
            )
            return {}
