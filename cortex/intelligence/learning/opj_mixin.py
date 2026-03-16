"""
OPJMixin — zero-disruption drop-in for all operational orchestrators.

Provides three methods that orchestrators call:
  _opj_init(registry_root)       — optional explicit init (lazy-safe if skipped)
  _opj_consult(operation)        — call BEFORE execution; returns prior patterns
  _opj_record_success(...)       — call AFTER successful execution
  _opj_record_failure(...)       — call AFTER failed execution

Usage::

    class MyOrchestrator(OPJMixin, OrchestratorBase):
        def __init__(self):
            super().__init__()
            self._opj_init()   # optional — auto-inits on first use if skipped

        def execute(self, request):
            prior = self._opj_consult("execute")  # consult before
            result = self._do_work(request)
            if result.success:
                self._opj_record_success("execute", context={...}, resolution="...")
            else:
                self._opj_record_failure("execute", error="...", attempted_fix="...")
            return result

AC-ID: AC-OPJ-PHASE52-MIXIN
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.intelligence.learning.opj_promoter import promote_high_confidence_patterns  # noqa: E402
from cortex.intelligence.learning.reinforcement_signal import (
    ReinforcementEngine,
    SignalType,
)

logger = logging.getLogger(__name__)

_WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
_DEFAULT_REGISTRY = _WORKSPACE_ROOT / "cortex-registry"


def _snake(name: str) -> str:
    """Convert CamelCase or arbitrary string to snake_case (handles consecutive caps e.g. TDDOrchestrator)."""
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", name)
    s = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s)
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


class OPJMixin:
    """
    Mixin that adds Operational Pattern Journal (OPJ) capabilities to any orchestrator.

    Thread-safe. Minimal overhead (<10ms per call). No base class changes required.
    Lazy-safe: all methods work even if _opj_init() is never called.
    """

    _opj_writer: Optional[Any] = None
    _opj_reader: Optional[Any] = None
    _opj_registry_root: Optional[Path] = None
    _urs_engine: Optional[ReinforcementEngine] = None

    # ── Initialisation ──────────────────────────────────────────────────────

    def _opj_init(self, registry_root: Optional[Path] = None) -> None:
        """
        Explicitly initialise OPJ components.

        Args:
            registry_root: Path to patterns/ directory. Defaults to canonical location.
                           Pass tmp_path in tests for isolation.
        """
        root = Path(registry_root) if registry_root else _DEFAULT_REGISTRY
        self._opj_registry_root = root
        from cortex.intelligence.learning.opj_writer import OPJWriter
        from cortex.intelligence.learning.opj_reader import OPJReader

        self._opj_writer = OPJWriter(registry_root=root)
        self._opj_reader = OPJReader(registry_root=root)
        # _opj_store: in-session cache of consulted patterns (list of dicts)
        self._opj_store: List[Dict[str, Any]] = []

    def _opj_ensure_init(self) -> None:
        """Lazy-initialise OPJ components on first use."""
        if self._opj_writer is None:
            self._opj_init()

    def _opj_orchestrator_name(self) -> str:
        """Return the orchestrator name: `name` attr → class.__name__ fallback."""
        return getattr(self, "name", None) or self.__class__.__name__

    def _urs_ensure_engine(self) -> ReinforcementEngine:
        """Lazy-initialise the URS engine on first use.

        Returns:
            The ReinforcementEngine instance.
        """
        if self._urs_engine is None:
            self._urs_engine = ReinforcementEngine()
        return self._urs_engine

    def _urs_emit_signal(
        self,
        signal_type: SignalType,
        pattern_id: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Emit a reinforcement signal (resilient — never raises).

        Args:
            signal_type: Type of reinforcement signal.
            pattern_id: Operation or pattern identifier.
            context: Optional additional context.
        """
        try:
            engine = self._urs_ensure_engine()
            engine.emit_signal(
                signal_type=signal_type,
                pattern_id=pattern_id,
                source_orchestrator=self._opj_orchestrator_name(),
                context=context or {},
            )
        except Exception as exc:
            logger.debug("OPJMixin._urs_emit_signal: non-fatal — %s", exc)

    # ── Public OPJ API ──────────────────────────────────────────────────────

    def _opj_consult(self, operation: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Consult the OPJ for prior patterns before executing an operation.

        Call this BEFORE execution. Returns failure patterns first (ranked by
        confidence desc) so the orchestrator can avoid known mistakes.

        Args:
            operation: The operation about to be executed.
            limit: Maximum number of patterns to return.

        Returns:
            List of OPJ entry dicts, or [] if journal is empty or unavailable.
        """
        try:
            self._opj_ensure_init()
            orchestrator = self._opj_orchestrator_name()
            return self._opj_reader.query_patterns(  # type: ignore[union-attr]
                orchestrator=orchestrator,
                operation=operation,
                limit=limit,
            )
        except Exception as exc:
            logger.debug("OPJMixin._opj_consult: non-fatal error — %s", exc)
            return []

    def _opj_record_success(
        self,
        operation: str = "",
        context: Optional[Dict[str, Any]] = None,
        resolution: str = "",
        confidence: float = 0.8,
    ) -> None:
        """
        Record a successful operation to the OPJ and trigger T1 promotion check.

        Call this AFTER a successful execution.  Patterns with confidence >=
        0.80 are auto-promoted to the T1 knowledge tier (Phase 71-F ES-005).

        Args:
            operation: The operation that succeeded.
            context: Key input values that contributed to success.
            resolution: Human-readable description of what made it work.
            confidence: Confidence score 0.0–1.0 (default 0.8).
        """
        if context is None:
            context = {}
        try:
            self._opj_ensure_init()
            self._opj_writer.record_success(  # type: ignore[union-attr]
                orchestrator=self._opj_orchestrator_name(),
                operation=operation,
                context=context,
                resolution=resolution,
                confidence=confidence,
            )
        except Exception as exc:
            logger.warning("OPJMixin._opj_record_success: non-fatal error — %s", exc)

        # Phase 83-d: Emit URS reinforcement signal for success
        self._urs_emit_signal(
            signal_type=SignalType.MILD_REWARD,
            pattern_id=operation,
            context=context,
        )

        # Phase 71-F ES-005: auto-promote high-confidence patterns
        try:
            promote_high_confidence_patterns()
        except Exception as exc:  # noqa: BLE001
            logger.debug("OPJMixin: promotion check non-fatal — %s", exc)

    def _opj_record_failure(
        self,
        operation: str,
        error: str,
        attempted_fix: str = "",
        confidence: float = 0.7,
        root_cause: Optional[str] = None,
        avoid_in_future: Optional[str] = None,
    ) -> None:
        """
        Record a failed operation to the OPJ.

        Call this AFTER a failed execution.

        Args:
            operation: The operation that failed.
            error: What went wrong.
            attempted_fix: What was tried.
            confidence: Confidence in the failure pattern 0.0–1.0 (default 0.7).
            root_cause: Why it failed (optional).
            avoid_in_future: Actionable avoidance rule (optional).
        """
        try:
            self._opj_ensure_init()
            self._opj_writer.record_failure(  # type: ignore[union-attr]
                orchestrator=self._opj_orchestrator_name(),
                operation=operation,
                error=error,
                attempted_fix=attempted_fix,
                confidence=confidence,
                root_cause=root_cause,
                avoid_in_future=avoid_in_future,
            )
        except Exception as exc:
            logger.warning("OPJMixin._opj_record_failure: non-fatal error — %s", exc)

        # Phase 83-d: Emit URS reinforcement signal for failure
        self._urs_emit_signal(
            signal_type=SignalType.MILD_PUNISHMENT,
            pattern_id=operation,
            context={"error": error},
        )

    # ------------------------------------------------------------------
    # Phase 87 — RCA extensions
    # ------------------------------------------------------------------

    def _opj_analyze_rca(
        self,
        failure_id: str,
        failure_description: str,
        methodology: Optional[str] = None,
        category: Optional[str] = None,
    ) -> Any:
        """Run a root cause analysis for a failure event and persist the result.

        Delegates to RCAEngine (selects methodology automatically when not
        supplied) and persists the resulting RCAAnalysis via RCAStore.
        Non-fatal: returns a minimal RCAAnalysis shell on any internal error.

        Args:
            failure_id: Unique identifier of the originating failure event.
            failure_description: Human-readable description of the failure symptom.
            methodology: Optional RCATemplate value string (e.g. 'five_whys').
            category: Optional RCACategory value string (e.g. 'technology').

        Returns:
            A populated RCAAnalysis dataclass.
        """
        try:
            from cortex.intelligence.learning.rca_engine import RCAEngine
            from cortex.intelligence.learning.rca_models import (
                RCAAnalysis, RCACategory, RCATemplate,
            )
            from cortex.intelligence.learning.rca_store import RCAStore

            engine = RCAEngine()
            cat = RCACategory(category) if category else RCACategory.TECHNOLOGY
            meth = RCATemplate(methodology) if methodology else None
            rca = engine.analyze(
                failure_id=failure_id,
                symptom=failure_description or f"Failure: {failure_id}",
                category=cat,
                methodology=meth,
            )
            try:
                store = RCAStore()
                store.initialize()
                store.save_analysis(rca)
                if rca.prevention_rule:
                    store.save_rule(rca.prevention_rule)
            except Exception as store_exc:
                logger.debug("OPJMixin._opj_analyze_rca: store error (non-fatal) — %s", store_exc)
            return rca
        except Exception as exc:
            logger.warning("OPJMixin._opj_analyze_rca: non-fatal error — %s", exc)
            # Return a minimal shell so callers always get an RCAAnalysis-like object
            from cortex.intelligence.learning.rca_models import (
                RCAAnalysis, RCACategory, RCATemplate,
            )
            import uuid
            return RCAAnalysis(
                id=f"RCA-{uuid.uuid4().hex[:8].upper()}",
                failure_id=failure_id,
                methodology=RCATemplate.FIVE_WHYS,
                category=RCACategory.TECHNOLOGY,
                root_cause="RCA analysis unavailable (internal error)",
                confidence=0.0,
            )

    def _opj_check_prevention_gate(self, operation_context: str) -> Any:
        """Check an operation context against active prevention rules.

        Queries the RCAStore for prevention rules generated from past RCA runs
        and evaluates the supplied context through the PreventionGate.
        Non-fatal: returns a PASS result on any internal error.

        Args:
            operation_context: Natural-language description of the operation
                               about to be performed.

        Returns:
            A PreventionGateResult (gate_level PASS / ADVISORY / WARNING / BLOCKING).
        """
        try:
            from cortex.intelligence.learning.prevention_gate import PreventionGate
            from cortex.intelligence.learning.rca_store import RCAStore

            store = RCAStore()
            store.initialize()
            gate = PreventionGate(store=store)
            return gate.check(operation_context=operation_context)
        except Exception as exc:
            logger.warning("OPJMixin._opj_check_prevention_gate: non-fatal error — %s", exc)
            from cortex.intelligence.learning.rca_models import GateLevel, PreventionGateResult
            return PreventionGateResult(
                gate_level=GateLevel.PASS,
                matched_rule=None,
                similarity_score=0.0,
                rca_summary=None,
                message="Prevention gate unavailable (internal error) — defaulting to PASS.",
            )
