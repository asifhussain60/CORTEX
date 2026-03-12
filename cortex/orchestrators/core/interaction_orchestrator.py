"""
InteractionOrchestrator — Stage 1 Comprehension with LENS per-turn.

Wires LENS analysis into every interaction turn, providing:
1. Per-turn LENS context (git, AST, comment, relationship analysis)
2. Optional challenge generation (AC-PERMANENT-FIX-006)
3. IOrchestrator contract compliance
4. ConversationProtocol integration

This is the missing implementation that MasterOrchestrator, wiring.yaml,
and startup_validator all reference. It bridges:
- ConversationProtocol (per-turn LENS comprehension)
- LENSOrchestrator (code intelligence)
- ChallengeEngine (optional disagreement detection)

Authority: MCP-FIRST, CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: AC-P0-INTERACTION-ORCH-GREEN-001
"""

from datetime import datetime
import os
from pathlib import Path
import sqlite3
from typing import Any, Dict, List, Optional

from cortex.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Err, Ok, Result
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.infrastructure.trace_integration import trace_orchestrator_action

# Phase 23: Import WorkflowTemplateMixin for template consumption capability
from cortex.core.workflow_template_mixin import WorkflowTemplateMixin
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin  # Phase 62-B
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin, enforce_gateway  # Phase 94d / 95


class InteractionOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin, IOrchestrator, WorkflowTemplateMixin):
    """
    Stage 1 orchestrator: LENS-powered comprehension on every turn.

    Coordinates:
    - LENSOrchestrator for per-turn code intelligence
    - ConversationProtocol for turn lifecycle
    - Optional ChallengeEngine for disagreement detection

    Used by MasterOrchestrator as primary Stage 1 orchestrator.
    Registered in wiring.yaml as core orchestrator with lens_protocol capability.

    Attributes:
        conversation_protocol: ConversationProtocol instance for turn management.
        enable_challenges: Whether challenge generation is active.
        lens_orchestrator: LENSOrchestrator for code intelligence.
        turn_number: Current turn counter.
        logger: EnhancedAuditLogger for audit trail.
    """

    # Phase 95 — advisory: Stage 1 execute_operation receives domain-specific operation
    # names ("comprehend"), not top-level gateway mode strings ("IMPLEMENT").
    # @enforce_gateway applied for decorator coverage but flag stays False.
    PHASE90_GATEWAY_EXEMPT: bool = True

    def __init__(
        self,
        conversation_protocol: Any,
        enable_challenges: bool = True,
        trace_db_path: Optional[str] = None,
    ) -> None:
        """
        Initialize InteractionOrchestrator.

        Args:
            conversation_protocol: ConversationProtocol instance for turn management.
            enable_challenges: Enable challenge generation (AC-PERMANENT-FIX-006).
                MUST remain True (hardcoded default) — skull rule AC-PERMANENT-FIX-006
                mandates that challenge-driven interaction is permanently wired.
                Setting False is only permitted in test isolation contexts.
            trace_db_path: Override path to SQLite trace DB (for testing; defaults to
                CORTEX_TRACE_DB env var or .cortex-runtime/traces/orchestrator-traces.db).
        """
        self.orchestrator_id = "interaction"  # For trace logging
        self.conversation_protocol = conversation_protocol
        self.enable_challenges: bool = enable_challenges
        self.turn_number: int = 0
        self._audit_trail: List[Dict[str, Any]] = []
        self.logger = EnhancedAuditLogger.instance()
        self._plan_store: Any = None  # Phase 00 D10 — injectable InteractionPlanStore
        self._user_role: str = "developer"  # G7: role-aware LENS context (default: developer)

        # P2-D: Resolve trace DB path (injectable for testing)
        _default_db = os.getenv("CORTEX_TRACE_DB", ".cortex-runtime/traces/orchestrator-traces.db")
        self._trace_db_path: str = trace_db_path if trace_db_path is not None else _default_db

        # G1: Wire ChallengeGenerator for mandatory code-touch governance gate (CORE-048)
        try:
            from cortex.orchestrators.core.intent_router.challenge_generator import ChallengeGenerator
            self._challenge_gen = ChallengeGenerator()
        except Exception:
            self._challenge_gen = None  # graceful degradation

        # P2-D: Ensure challenge_decisions table exists in trace DB
        self._ensure_challenge_decisions_table()

        # Initialize LENSOrchestrator for per-turn analysis
        self.lens_orchestrator = self._init_lens_orchestrator()

        # Phase 113-C: Prior-request context chain — injected by MasterOrchestrator
        self._request_log_manager: Any = None
        self._prior_context_limit: int = 5  # default: last 5 requests

        # Phase 150-c: Personality layer for voiced orchestrator output
        try:
            from cortex.orchestrators.core.personality_layer import PersonalityLayer
            self._personality: Any = PersonalityLayer(persona="default")
        except Exception:
            self._personality = None  # graceful degradation

    def set_request_log_manager(self, manager: Any) -> None:
        """
        Inject a RequestLogManager for prior-request context chain (Phase 113-C).

        Called by MasterOrchestrator after init so InteractionOrchestrator can
        query prior requests and build cumulative LENS context for each turn.

        Args:
            manager: A ``RequestLogManager`` instance (or compatible duck-type).
        """
        self._request_log_manager = manager

    def build_context_summary(self, prior_requests: List[Dict[str, Any]]) -> str:
        """
        Build a compact context string from a list of prior requests.

        Used to inject prior-turn context into the LENS analysis for the current
        turn, enabling cumulative understanding across a session.

        Args:
            prior_requests: List of request dicts as returned by
                ``RequestLogManager.get_prior_requests()``.  Each dict must
                contain ``sequence_number``, ``user_request``, and ``intent_type``.

        Returns:
            A compact multi-line string summarising prior requests, or ``""``
            for an empty list (first-turn case).
        """
        if not prior_requests:
            return ""

        lines = ["[Prior context from this session]"]
        for req in reversed(prior_requests):  # chronological order (oldest → newest)
            seq = req.get("sequence_number", "?")
            text = req.get("user_request", "")
            intent = req.get("intent_type") or "UNKNOWN"
            lines.append(f"  [{seq}] ({intent}) {text}")
        return "\n".join(lines)

    def synthesize_request(
        self,
        current_request: str,
        session_id: str,
    ) -> Dict[str, Any]:
        """Synthesize prior requests into a holistic summary with Definition of Done.

        Reads up to ``_prior_context_limit`` prior requests from the
        ``RequestLogManager`` for the given session, combines them with the
        current request, and produces:

        - A concise synthesized summary (1–3 sentences)
        - A Definition of Done (DoD) checklist with concrete, verifiable items
        - Metadata (prior_count, has_prior_context, raw prior_requests)

        This output is consumed by the ``📋 Request Echo & Definition of Done``
        response template section.

        Non-blocking: if the RequestLogManager is unavailable or raises, returns
        an empty synthesis (CORE-049 — silent degradation).

        Args:
            current_request: The user's current (latest) request text.
            session_id: Session identifier for querying prior requests.

        Returns:
            A dict with keys:
            - ``has_prior_context`` (bool): True if prior requests exist.
            - ``prior_count`` (int): Number of prior requests found.
            - ``synthesized_summary`` (str): Holistic 1–3 sentence summary.
            - ``dod_items`` (list[str]): Definition of Done checklist items.
            - ``prior_requests`` (list[dict]): Raw prior request dicts.
        """
        empty_result: Dict[str, Any] = {
            "has_prior_context": False,
            "prior_count": 0,
            "synthesized_summary": "",
            "dod_items": [],
            "prior_requests": [],
        }

        rlm = getattr(self, "_request_log_manager", None)
        if rlm is None:
            return empty_result

        try:
            prior_requests: List[Dict[str, Any]] = rlm.get_prior_requests(
                session_id=session_id,
                limit=getattr(self, "_prior_context_limit", 5),
            )
        except Exception:
            return empty_result

        if not prior_requests:
            return empty_result

        # Build synthesized summary from all requests (prior + current)
        all_request_texts: List[str] = []
        for req in sorted(prior_requests, key=lambda r: r.get("sequence_number", 0)):
            text = req.get("user_request", "").strip()
            if text:
                all_request_texts.append(text)
        all_request_texts.append(current_request.strip())

        synthesized_summary = self._build_synthesized_summary(all_request_texts)

        # Build DoD items from combined requests
        dod_items = self._build_dod_items(all_request_texts)

        return {
            "has_prior_context": True,
            "prior_count": len(prior_requests),
            "synthesized_summary": synthesized_summary,
            "dod_items": dod_items,
            "prior_requests": prior_requests,
        }

    def _build_synthesized_summary(self, request_texts: List[str]) -> str:
        """Build a concise multi-request summary.

        Combines all request texts into a coherent 1–3 sentence summary
        describing the holistic user intent across the session.

        Args:
            request_texts: Chronologically ordered request texts.

        Returns:
            A concise summary string.
        """
        if not request_texts:
            return ""

        if len(request_texts) == 1:
            return request_texts[0]

        # Build a numbered summary for multi-request sessions
        parts = []
        for i, text in enumerate(request_texts, 1):
            # Truncate very long requests for the summary
            truncated = text[:200] + "..." if len(text) > 200 else text
            parts.append(f"({i}) {truncated}")

        return f"Session with {len(request_texts)} requests: " + "; ".join(parts)

    def _build_dod_items(self, request_texts: List[str]) -> List[str]:
        """Build Definition of Done checklist from request texts.

        Creates concrete, verifiable DoD items — one per distinct request action,
        plus a mandatory testing item at the end.

        Args:
            request_texts: Chronologically ordered request texts.

        Returns:
            List of DoD checklist strings.
        """
        if not request_texts:
            return []

        items: List[str] = []
        for text in request_texts:
            # Extract a concise action from each request
            truncated = text[:150].strip()
            if truncated:
                items.append(truncated)

        # Always end with a testing DoD item
        items.append("All tests pass (make test-preflight)")

        return items

    def set_plan_store(self, plan_store: Any) -> None:
        """Inject an InteractionPlanStore for plan-first execution (Phase 00 D10).

        Args:
            plan_store: InteractionPlanStore instance to use for plan lifecycle.
        """
        self._plan_store = plan_store

    # -------------------------------------------------------------------------
    # P2-D: SQLite challenge_decisions persistence
    # -------------------------------------------------------------------------

    def _ensure_challenge_decisions_table(self) -> None:
        """Create challenge_decisions table in trace DB if it does not exist.

        Called once during __init__() so the table is always ready before any
        turn executes.  Uses CREATE TABLE IF NOT EXISTS — idempotent and safe
        across singleton / test re-instantiations.
        """
        try:
            db_dir = Path(self._trace_db_path).parent
            db_dir.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self._trace_db_path, timeout=10.0) as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS challenge_decisions (
                        decision_id        TEXT PRIMARY KEY,
                        timestamp          TEXT NOT NULL,
                        turn_number        INTEGER NOT NULL,
                        user_request_hint  TEXT NOT NULL,
                        challenge_category TEXT,
                        challenge_severity TEXT,
                        decision           TEXT NOT NULL,
                        challenge_description TEXT,
                        mitigation         TEXT,
                        session_id         TEXT
                    )
                    """
                )
                conn.execute(
                    "CREATE INDEX IF NOT EXISTS idx_cd_timestamp "
                    "ON challenge_decisions(timestamp DESC)"
                )
                # Phase 113-final (GAP-05): add request_id FK column — backward compatible
                try:
                    conn.execute(
                        "ALTER TABLE challenge_decisions ADD COLUMN request_id TEXT"
                    )
                except sqlite3.OperationalError:
                    # Column already exists — safe to ignore on repeated schema init
                    pass
                conn.commit()
        except Exception as e:
            # Non-fatal — in-memory audit trail is the fallback
            try:
                self.logger.log_operation_complete(
                    ac_id="AC-P2D-TABLE-INIT",
                    operation="challenge_decisions_table_init",
                    success=False,
                    details={"error": str(e)},
                )
            except Exception:
                pass

    def _log_challenge_decision(
        self,
        challenge: Dict[str, Any],
        session_id: str,
        request_id: Optional[str] = None,
    ) -> None:
        """Persist a challenge decision to the challenge_decisions SQLite table.

        Args:
            challenge: The challenge dict returned by _evaluate_challenge()
                       (keys: category, severity, description, mitigation, …).
            session_id: Session identifier from the round context.
            request_id: Phase 113 FK — links to request_log.request_id for
                        full audit trail. None for calls made before Phase 113
                        wiring was active (backward compatible).
        """
        try:
            import uuid as _uuid

            decision_id = str(_uuid.uuid4())
            user_hint = str(challenge.get("user_request", ""))[:100]
            if not user_hint:
                user_hint = str(challenge.get("description", ""))[:100]

            with sqlite3.connect(self._trace_db_path, timeout=10.0) as conn:
                conn.execute(
                    """
                    INSERT INTO challenge_decisions
                        (decision_id, timestamp, turn_number, user_request_hint,
                         challenge_category, challenge_severity, decision,
                         challenge_description, mitigation, session_id,
                         request_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        decision_id,
                        datetime.now().isoformat(),
                        self.turn_number,
                        user_hint,
                        str(challenge.get("category", "")),
                        str(challenge.get("severity", "")),
                        "surfaced",   # default decision — user has not yet chosen proceed/mitigate/cancel
                        str(challenge.get("description", ""))[:500],
                        str(challenge.get("mitigation", ""))[:500],
                        session_id,
                        request_id,
                    ),
                )
                conn.commit()
        except Exception as e:
            # Non-fatal — never block a turn on logging failure
            try:
                self.logger.log_operation_complete(
                    ac_id="AC-P2D-LOG-DECISION",
                    operation="log_challenge_decision",
                    success=False,
                    details={"error": str(e)},
                )
            except Exception:
                pass

    def _init_lens_orchestrator(self) -> Any:
        """
        Initialize LENSOrchestrator with graceful fallback.

        Returns:
            LENSOrchestrator instance or None if unavailable.
        """
        try:
            from cortex.lens.lens_orchestrator import LENSOrchestrator

            repo_path = Path.cwd()
            return LENSOrchestrator(repo_path=repo_path)
        except Exception:
            # Graceful degradation — LENS not available
            return None

    # =========================================================================
    # IOrchestrator Contract
    # =========================================================================

    def get_name(self) -> str:
        """Get orchestrator name.

        Returns:
            'InteractionOrchestrator' identifier string.
        """
        return "InteractionOrchestrator"

    def get_recommended_template(self) -> Optional[str]:
        """Return the recommended workflow template for InteractionOrchestrator.

        Returns:
            Template ID for request execution plan gate.
        """
        return "request-execution/plan-gate"

    def get_version(self) -> str:
        """Get orchestrator version.

        Returns:
            Semantic version string.
        """
        return "1.0.0"

    def initialize(self) -> Result[str]:
        """Initialize orchestrator.

        Returns:
            Ok with success message or Err with failure reason.
        """
        try:
            if self.lens_orchestrator is None:
                self.lens_orchestrator = self._init_lens_orchestrator()
            return Ok("InteractionOrchestrator initialized")
        except Exception as e:
            return Err(f"Initialization failed: {str(e)}")

    def get_mode(self) -> OperationMode:
        """Get current operation mode.

        Returns:
            OperationMode.EXECUTION for interaction turns.
        """
        return OperationMode.EXECUTION

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get exposed MCP tools.

        Returns:
            Ok with dict of tool definitions.
        """
        return Ok({
            "execute_turn_with_challenge": {
                "name": "execute_turn_with_challenge",
                "description": "Execute one interaction turn with LENS and optional challenge",
            },
            "execute": {
                "name": "execute",
                "description": "Execute comprehension with LENS context",
            },
        })

    @enforce_gateway
    @trace_orchestrator_action("EXECUTE_OPERATION")
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """
        Execute operation with LENS analysis.

        Every operation runs LENS analysis to provide code intelligence
        context for downstream orchestrators.

        Args:
            operation_name: Operation identifier (e.g., 'comprehend').
            parameters: Operation parameters including 'user_input'.

        Returns:
            Result with operation output including lens_context.
        """
        user_input = parameters.get("user_input", parameters.get("request", ""))

        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(
            operation=operation_name,
            orchestrator_context=parameters.get("orchestrator_context"),
            unified_context=parameters.get("unified_context"),
        )

        try:
            # Run LENS analysis (per-turn requirement)
            lens_context = self._run_lens_analysis(user_input)

            # Build output
            output: Dict[str, Any] = {
                "operation": operation_name,
                "user_input": user_input,
                "lens_context": lens_context,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
            }

            # Log audit entry
            self._audit_trail.append({
                "ac_id": "AC-P0-INTERACTION-ORCH-GREEN-001",
                "operation": operation_name,
                "success": True,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
            })

            return Ok(output)

        except Exception as e:
            return Err(f"Operation {operation_name} failed: {str(e)}")

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail from trace database + in-memory fallback.

        Args:
            limit: Maximum entries to return.

        Returns:
            Ok with list of audit entries from trace DB.

        Note — P2-C (SQLite flush guarantee):
            The @trace_orchestrator_action decorator on execute_turn_with_challenge()
            calls PerOrchestrationTraceWriter.write_trace() which issues conn.commit()
            after every insert — so every Stage 1 turn is flushed to SQLite immediately.
            No deferred flush is required here.
        """
        try:
            audit_entries = []

            # Try reading from trace database first
            trace_db_path = Path(os.getenv("CORTEX_TRACE_DB", ".cortex-runtime/traces/orchestrator-traces.db"))
            if trace_db_path.exists():
                import sqlite3
                with sqlite3.connect(str(trace_db_path)) as conn:
                    # Query trace_interaction table (per-orchestrator table)
                    cursor = conn.execute(
                        "SELECT timestamp, action, context, result, metadata FROM trace_interaction ORDER BY timestamp DESC LIMIT ?",
                        (limit,)
                    )
                    for row in cursor.fetchall():
                        audit_entries.append({
                            "timestamp": row[0],
                            "action": row[1],
                            "context": row[2],
                            "result": row[3],
                            "metadata": row[4]
                        })

            # Fallback to in-memory if DB empty
            if not audit_entries:
                audit_entries = self._audit_trail[-limit:]

            return Ok(audit_entries)
        except Exception:
            # Fallback to in-memory on any error
            return Ok(self._audit_trail[-limit:])

    # =========================================================================
    # Core Turn Execution (used by MasterOrchestrator)
    # =========================================================================

    def execute_turn(self, user_input: str) -> Result[Dict[str, Any]]:
        """
        Execute a single interaction turn (simplified interface).

        Delegates core logic without challenge evaluation.
        Required by startup_validator (line 317) and ConversationProtocol contract.

        Args:
            user_input: User's natural language request.

        Returns:
            Result with turn output including user_input, lens_context, turn_number.
        """
        self.turn_number += 1

        try:
            lens_context = self._run_lens_analysis(user_input)

            output: Dict[str, Any] = {
                "user_input": user_input,
                "lens_context": lens_context,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
                "challenge_evaluated": False,
            }

            self._audit_trail.append({
                "operation": "execute_turn",
                "turn_number": self.turn_number,
                "success": True,
                "timestamp": datetime.now().isoformat(),
            })

            return Ok(output)

        except Exception as e:
            return Err(f"execute_turn {self.turn_number} failed: {str(e)}")

    @trace_orchestrator_action("EXECUTE_TURN_WITH_CHALLENGE")
    def execute_turn_with_challenge(
        self,
        user_request: str,
        round_context: Any,
        pattern_id: Optional[str] = None,
    ) -> Result[Dict[str, Any]]:
        """
        Execute one interaction turn with LENS analysis and optional challenge.

        This is the primary method called by MasterOrchestrator for Stage 1
        comprehension. Every turn:
        1. Increments turn counter
        2. Runs LENS analysis on workspace context
        3. Optionally evaluates challenge patterns
        4. Returns enriched context for Stage 2+

        Args:
            user_request: User's natural language request.
            round_context: RoundContext with turn metadata.
            pattern_id: Optional specific pattern to check for challenge.

        Returns:
            Result with turn output including lens_context and
            optional challenge data.
        """
        self.turn_number += 1

        try:
            # Phase 113-C: Query prior requests for cumulative context
            _prior_context_summary: str = ""
            _rlm = getattr(self, "_request_log_manager", None)
            if _rlm is not None:
                try:
                    _session = str(getattr(round_context, "session_id", "default"))
                    _prior = _rlm.get_prior_requests(
                        session_id=_session,
                        limit=getattr(self, "_prior_context_limit", 5),
                    )
                    _prior_context_summary = self.build_context_summary(_prior)
                except Exception:
                    pass  # Non-blocking — context failure must never break comprehension

            # Step 1: Run LENS analysis (MANDATORY per-turn)
            lens_context = self._run_lens_analysis(user_request)

            # Step 2: Build base output
            output: Dict[str, Any] = {
                "type": "comprehension",
                "user_request": user_request,
                "lens_context": lens_context,
                "turn_number": self.turn_number,
                "timestamp": datetime.now().isoformat(),
                "challenge_evaluated": False,
                "user_role": getattr(self, "_user_role", "developer"),  # G7: role-aware context
                "prior_context_summary": _prior_context_summary,  # Phase 113-C
            }

            # Step 3: Optional challenge evaluation
            if self.enable_challenges:
                challenge_result = self._evaluate_challenge(
                    user_request, lens_context, pattern_id
                )
                output["challenge_evaluated"] = True
                if challenge_result is not None:
                    output["type"] = "challenge"
                    output["challenge"] = challenge_result
                    # P2-D: Persist challenge decision to SQLite (CORE-064 completeness)
                    _session = getattr(round_context, "session_id", "unknown")
                    _loggable = dict(challenge_result)
                    _loggable["user_request"] = user_request
                    # Phase 113-final (GAP-05): pass request_id FK from round_context metadata
                    _rc_meta = getattr(round_context, "metadata", {}) or {}
                    _challenge_rid = _rc_meta.get("request_id") if isinstance(_rc_meta, dict) else None
                    self._log_challenge_decision(
                        _loggable, session_id=str(_session), request_id=_challenge_rid
                    )

            # Step 3b: Render engagement (Phase 92 — three-tier routing gate)
            try:
                from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
                _chain = ["IntentRouter", "InteractionOrchestrator"]
                _engagement = EngagementRenderer().render_engagement(chain=_chain)
                output["breadcrumb"] = _engagement["breadcrumb"]
                output["engagement"] = _engagement
            except Exception:
                output["breadcrumb"] = ""
                output["engagement"] = {"breadcrumb": "", "stage_pulse": None, "timeline": None}

            # Step 3c: G3 — WorkflowGateway delegation for code-touching intents (Phase 90)
            # Every IMPLEMENT/FIX/REFACTOR turn must pass through the mandatory template gate.
            _code_intents = {"IMPLEMENT", "FIX", "REFACTOR", "DEBUG", "AUDIT", "TDD"}
            _detected_intent = self._classify_intent(user_request).upper()
            if _detected_intent in _code_intents and output.get("type") != "challenge":
                try:
                    from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway
                    _wf_gateway = WorkflowGateway()
                    _wf_result = _wf_gateway.execute_gated(
                        orchestrator_name="InteractionOrchestrator",
                        mode=_detected_intent,
                        context={
                            "user_request": user_request,
                            "lens_context": lens_context,
                            "user_role": getattr(self, "_user_role", "developer"),
                        },
                    )
                    output["workflow_template"] = _wf_result
                except Exception as _wf_err:
                    # Graceful degradation — never block Stage 1 on gateway failure
                    output["workflow_template"] = {
                        "status": "degraded",
                        "error": str(_wf_err),
                    }

            # Step 4: Apply token optimization (ENH-046 Phase 4 Integration)
            try:
                from cortex.orchestrators.core.context_synthesis_gateway import get_gateway

                gateway = get_gateway()
                session_id = getattr(round_context, 'session_id', 'default_session')

                synthesized = gateway.synthesize(
                    context=output,
                    session_id=session_id,
                    orchestrator_name="InteractionOrchestrator"
                )

                # Log budget violations but don't block
                if not synthesized.budget_compliant:
                    self.logger.log_operation_complete(
                        ac_id="AC-TOKEN-OPT-001",
                        operation="token_budget_violation",
                        success=False,
                        details={
                            "turn_number": self.turn_number,
                            "tokens": synthesized.token_count,
                            "budget": gateway.token_budget,
                            "overflow": synthesized.token_count - gateway.token_budget
                        }
                    )

                # Merge synthesis metadata — preserve canonical keys
                # (challenge_evaluated, lens_context, type required downstream)
                synthesis_meta = synthesized.context or {}
                output["synthesized_content"] = synthesis_meta.get("synthesized_content")
                output["compression_strategy"] = synthesis_meta.get("compression_strategy")

            except Exception as gateway_err:
                # Graceful degradation - log but continue with original output
                self.logger.log_operation_complete(
                    ac_id="AC-TOKEN-OPT-001",
                    operation="token_optimization_failed",
                    success=False,
                    details={"error": str(gateway_err)}
                )

            # Step 5: Audit trail
            self._audit_trail.append({
                "ac_id": "AC-PERMANENT-FIX-006",
                "operation": "execute_turn_with_challenge",
                "turn_number": self.turn_number,
                "success": True,
                "lens_context_keys": list(lens_context.keys()) if isinstance(lens_context, dict) else [],
                "challenge_evaluated": output.get("challenge_evaluated", False),
                "timestamp": datetime.now().isoformat(),
            })

            return Ok(output)

        except Exception as e:
            self._audit_trail.append({
                "ac_id": "AC-PERMANENT-FIX-006",
                "operation": "execute_turn_with_challenge",
                "turn_number": self.turn_number,
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            })
            return Err(f"Turn {self.turn_number} failed: {str(e)}")

    @trace_orchestrator_action("EXECUTE_COMPREHENSION")
    def execute(self, context: Dict[str, Any]) -> Result[Dict[str, Any]]:
        """
        Execute comprehension for MasterOrchestrator Phase 1.

        Simplified interface used by MasterOrchestrator._execute_phase_1()
        to get LENS context for a user intent.

        Args:
            context: Dict with 'user_intent' key.

        Returns:
            Result with comprehension data including intent_type and lens_context.
        """
        user_intent = context.get("user_intent", "")

        try:
            lens_context = self._run_lens_analysis(user_intent)

            # Classify intent from user input
            intent_type = self._classify_intent(user_intent)

            output: Dict[str, Any] = {
                "intent_type": intent_type,
                "lens_context": lens_context,
                "confidence": 0.8,
                "analysis_complete": True,
                "timestamp": datetime.now().isoformat(),
            }

            # Phase 92: Render engagement — three-tier routing gate
            try:
                from cortex.orchestrators.response.engagement_renderer import EngagementRenderer
                _chain = ["IntentRouter", "InteractionOrchestrator"]
                _engagement = EngagementRenderer().render_engagement(chain=_chain)
                output["breadcrumb"] = _engagement["breadcrumb"]
                output["engagement"] = _engagement
            except Exception:
                output["breadcrumb"] = ""
                output["engagement"] = {"breadcrumb": "", "stage_pulse": None, "timeline": None}

            # Apply token optimization (ENH-046 Phase 4 Integration)
            try:
                from cortex.orchestrators.core.context_synthesis_gateway import get_gateway

                gateway = get_gateway()
                session_id = context.get('session_id', 'default_session')

                synthesized = gateway.synthesize(
                    context=output,
                    session_id=session_id,
                    orchestrator_name="InteractionOrchestrator"
                )

                # Merge synthesis metadata into output — preserve canonical keys
                # (intent_type, lens_context, confidence) required by MasterOrchestrator
                synthesis_meta = synthesized.context or {}
                output["synthesized_content"] = synthesis_meta.get("synthesized_content")
                output["compression_strategy"] = synthesis_meta.get("compression_strategy")

            except Exception:
                # Graceful degradation - return original output
                pass

            return Ok(output)

        except Exception as e:
            return Err(f"Comprehension failed: {str(e)}")

    # =========================================================================
    # Internal Methods
    # =========================================================================

    def _run_lens_analysis(self, user_input: str) -> Dict[str, Any]:
        """
        Run LENS analysis for current turn.

        Provides code intelligence context by analyzing workspace files
        relevant to the user's request.

        Args:
            user_input: User's request text for context extraction.

        Returns:
            Dict with LENS analysis results (git, AST, comments, etc.)
            or empty dict on graceful degradation.
        """
        if self.lens_orchestrator is None:
            return {"status": "lens_unavailable", "degraded": True}

        try:
            # Analyze current working directory as default target
            repo_path = Path.cwd()
            # Try to find a relevant file from user input context
            target_file = self._extract_target_file(user_input, repo_path)

            if target_file and target_file.exists():
                return self.lens_orchestrator.analyze_file(target_file)
            else:
                # Fallback: return workspace-level metadata
                return {
                    "status": "no_target_file",
                    "repo_path": str(repo_path),
                    "user_input_hint": user_input[:100],
                }

        except Exception as e:
            # Graceful degradation — never block on LENS failure
            return {
                "status": "lens_error",
                "error": str(e),
                "degraded": True,
            }

    def _extract_target_file(
        self, user_input: str, repo_path: Path
    ) -> Optional[Path]:
        """
        Extract target file path from user input.

        Looks for file references in the user's request to provide
        targeted LENS analysis.

        Args:
            user_input: User's natural language request.
            repo_path: Repository root path.

        Returns:
            Path to target file if found, None otherwise.
        """
        # Simple heuristic: look for .py file references
        words = user_input.split()
        for word in words:
            cleaned = word.strip("'\"`,;:")
            if cleaned.endswith(".py") or cleaned.endswith(".ts") or cleaned.endswith(".js"):
                candidate = repo_path / cleaned
                if candidate.exists():
                    return candidate
                # Try common source directories
                for src_dir in ["cortex", "cortex/intelligence", "src", "tests"]:
                    candidate = repo_path / src_dir / cleaned
                    if candidate.exists():
                        return candidate
        return None

    def _classify_intent(self, user_input: str) -> str:
        """
        Classify user intent from natural language input.

        Simple keyword-based classification for Stage 1 comprehension.
        More sophisticated classification happens in Stage 2 (IntentRouter).

        Args:
            user_input: User's natural language request.

        Returns:
            Intent type string (IMPLEMENT, FIX, REFACTOR, ANALYZE, UNKNOWN).
        """
        lower = user_input.lower()
        if any(kw in lower for kw in ["implement", "create", "add", "build", "new"]):
            return "IMPLEMENT"
        elif any(kw in lower for kw in ["fix", "bug", "error", "broken", "issue"]):
            return "FIX"
        elif any(kw in lower for kw in ["refactor", "clean", "improve", "optimize"]):
            return "REFACTOR"
        elif any(kw in lower for kw in ["analyze", "audit", "check", "review", "scan"]):
            return "ANALYZE"
        return "UNKNOWN"

    def _evaluate_challenge(
        self,
        user_request: str,
        lens_context: Dict[str, Any],
        pattern_id: Optional[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Evaluate whether to generate a governance challenge for the user's request.

        G1+G2: Mandatory governance gate for every code-touching request (CORE-048).
        Uses ChallengeGenerator to scan code snippets from LENS context for:
        - CORE-013 violations (bare except)
        - Dangerous patterns (eval, exec)
        - Missing docstrings on public APIs
        - Breaking change risks

        Only code-touching requests are challenged. Non-code requests (explain,
        what is, show me) are exempt to avoid governance noise.

        Args:
            user_request: User's natural language request.
            lens_context: LENS analysis context (may contain code_snippet).
            pattern_id: Specific pattern to check, or None for auto-detect.

        Returns:
            Challenge dict (with category/severity/description/mitigation) if a
            governance concern is found, or None if the request is clean/exempt.
        """
        # G2: Only challenge code-touching requests — governance performance rule
        _CODE_TOUCH_KEYWORDS = {
            "implement", "fix", "refactor", "create", "build",
            "add", "modify", "delete", "edit", "update", "change",
            "rewrite", "migrate", "rename", "remove", "replace",
        }
        request_lower = user_request.lower()
        touches_code = any(kw in request_lower for kw in _CODE_TOUCH_KEYWORDS)
        if not touches_code:
            return None  # Non-code request — exempt from challenge gate

        # G1: Use wired ChallengeGenerator (graceful degradation if unavailable)
        if self._challenge_gen is None:
            return None

        # Extract code snippet from LENS context for analysis
        code_snippet = lens_context.get("code_snippet", "")
        if not code_snippet:
            # No code to analyse — challenge based on request text only
            code_snippet = f"# Request: {user_request}\n"

        try:
            # Run governance analysis (mandatory for all code-touching turns)
            governance_challenges = self._challenge_gen.analyze_governance(code_snippet)

            # Run coverage analysis if test context available
            existing_tests = lens_context.get("test_files", [])
            coverage_challenges = self._challenge_gen.analyze_coverage(
                code_snippet,
                context={"existing_tests": existing_tests},
            )

            all_challenges = governance_challenges + coverage_challenges

            if not all_challenges:
                return None

            # Return the highest-severity challenge (P0 first)
            _severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
            top_challenge = max(
                all_challenges,
                key=lambda c: _severity_order.get(str(c.severity), 0),
            )
            return top_challenge.to_dict()

        except Exception:
            # Graceful degradation — never block Stage 1 on challenge failure
            return None

    # =========================================================================
    # ENH-090: Semantic Block Assembly Integration
    # =========================================================================

    def _init_block_assembler(self) -> Any:
        """
        Initialize SemanticBlockAssembler with graceful fallback.

        Returns:
            SemanticBlockAssembler instance or None if unavailable.
        """
        try:
            from cortex.core.registry.semantic_blocks import SemanticBlockAssembler, SemanticBlockLoader, SemanticBlockReasoner

            loader = SemanticBlockLoader()
            reasoner = SemanticBlockReasoner(loader)
            return SemanticBlockAssembler(loader, reasoner)
        except Exception:
            # Graceful degradation — blocks not available
            return None

    @property
    def block_assembler(self) -> Any:
        """
        Lazy-load semantic block assembler on first access.

        Returns:
            SemanticBlockAssembler instance.
        """
        if not hasattr(self, "_block_assembler"):
            self._block_assembler = self._init_block_assembler()
        return self._block_assembler

    def detect_intent(self, context: Dict[str, Any]) -> str:
        """
        Classify user intent from request text.

        Analyzes user request to determine intent (IMPLEMENT, FIX, ANALYZE, etc.).

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            Intent string (IMPLEMENT|FIX|REFACTOR|ANALYZE|AUDIT|PLAN).
        """
        user_request = context.get("user_request", "").lower()

        # Intent detection heuristics (order matters — check specific before general)
        if any(kw in user_request for kw in ["implement", "create", "build", "add", "new"]):
            return "IMPLEMENT"
        elif any(kw in user_request for kw in ["fix", "bug", "error", "broken", "issue", "debug"]):
            return "FIX"
        elif any(kw in user_request for kw in ["refactor", "clean", "improve", "optimize", "reorganize"]):
            return "REFACTOR"
        elif any(kw in user_request for kw in ["plan", "design", "organize", "roadmap"]):
            # Check PLAN before ANALYZE (architect can mean analyze OR plan)
            return "PLAN"
        elif any(kw in user_request for kw in ["analyze", "audit", "check", "review", "scan", "what", "show", "explain"]):
            return "ANALYZE"
        else:
            # Default to ANALYZE for queries
            return "ANALYZE"

    def select_blocks_for_intent(self, intent: str) -> List[str]:
        """
        Select appropriate semantic blocks for an intent.

        Maps intent to block composition rules.

        Args:
            intent: User intent (IMPLEMENT|FIX|REFACTOR|ANALYZE|AUDIT|PLAN).

        Returns:
            List of block names to assemble.
        """
        # Intent → block selection mapping
        intent_blocks = {
            "IMPLEMENT": ["capabilities", "tutorial", "next_steps"],
            "FIX": ["capabilities", "lens", "next_steps"],
            "REFACTOR": ["capabilities", "tutorial", "next_steps"],
            "ANALYZE": ["lens", "orchestrators", "next_steps"],
            "AUDIT": ["capabilities", "orchestrators", "next_steps"],
            "PLAN": ["capabilities", "orchestrators", "next_steps"],
        }

        return intent_blocks.get(intent, ["capabilities", "next_steps"])

    def select_blocks_for_context(self, context: Dict[str, Any]) -> List[str]:
        """
        Select blocks based on conversation context.

        First interaction includes INTRO block.
        Subsequent interactions omit INTRO.

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            List of block names to assemble.
        """
        history = context.get("conversation_history", [])
        is_first = len(history) == 0

        # Detect intent
        intent = self.detect_intent(context)
        blocks = self.select_blocks_for_intent(intent)

        # Add INTRO for first interaction
        if is_first:
            blocks = ["intro"] + blocks

        return blocks

    def assemble_response(self, context: Dict[str, Any]) -> str:
        """
        Assemble personality-consistent response using semantic blocks.

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            Assembled markdown response.
        """
        if self.block_assembler is None:
            # Fallback: return simple message if blocks unavailable
            return "**CORTEX Ready** — Unable to load semantic blocks. Proceeding with basic mode."

        # Select blocks for context
        blocks = self.select_blocks_for_context(context)

        # Assemble
        result = self.block_assembler.assemble(blocks)

        return result.assembled_content

    def assemble_response_with_metrics(
        self, context: Dict[str, Any]
    ) -> tuple:
        """
        Assemble response and return metrics.

        Args:
            context: Dictionary with 'user_request' and 'conversation_history'.

        Returns:
            Tuple of (assembled_content, metrics_dict).
        """
        if self.block_assembler is None:
            return ("CORTEX Ready — Blocks unavailable", {})

        # Select and assemble
        blocks = self.select_blocks_for_context(context)
        result = self.block_assembler.assemble(blocks)

        # Build metrics
        metrics = {
            "blocks_used": result.blocks_assembled,
            "total_words": result.total_words,
            "personality_consistent": result.personality_consistent,
            "duplication_check_passed": result.duplication_check_passed,
            "rendering_valid": result.rendering_valid,
        }

        return (result.assembled_content, metrics)


# AC_COMPLETE: AC-P0-INTERACTION-ORCH-GREEN-001
