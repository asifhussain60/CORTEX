"""
WorkflowGateway — Phase 90: Mandatory Template Resolution Gate.

The single enforced entry point that ALL code-touching orchestrators must
pass through before any execution begins. Resolves the correct workflow
template for the given mode, composes it via WorkflowComposer with
convergence_mode=True, and logs every execution to SQLite.

Design: SOLID + DRY
  - Single Responsibility: resolves + dispatches only; orchestrators execute steps
  - Open/Closed: new modes → add a template entry; zero code changes here
  - Liskov: works with any IOrchestrator implementor
  - Interface Segregation: callers use only resolve_template or execute_gated
  - Dependency Inversion: depends on template_id strings, not concrete logic
  - DRY: detect-fix-rescan-loop.yaml is the single convergence implementation

AC_START: AC-P90-WFG-001
Phase: 90 | Priority: P0
CORE-068: Universal Convergence Gate
CORE-064: Sweep Completeness Contract
CORE-008: TDD mandatory
CORE-002: All output inline — no report files
"""

from __future__ import annotations

import logging
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# MODE → TEMPLATE MAPPING  (Single Source of Truth for Phase 90)
# Every code-touching mode has exactly one canonical template.
# Non-code-touching modes (QUERY, DESIGN, PLAN, REPHRASE) map to None.
# ─────────────────────────────────────────────────────────────────────────────
_MODE_TEMPLATE_MAP: Dict[str, Optional[str]] = {
    # Code-touching modes — MUST have a template
    "IMPLEMENT": "sdlc/implement-workflow",
    "FIX":       "sdlc/fix-workflow",
    "REFACTOR":  "quality/refactor-workflow",
    "DEBUG":     "debugging/multi-stack-debug-pipeline",
    "AUDIT":     "audit/audit-fix-pipeline",
    "HEALTH":    "maintenance/health-check-workflow",
    "VACUUM":    "maintenance/vacuum-workflow",
    "TDD":       "tdd/tdd-workflow",
    "TOTALRECALL": "lifecycle/totalrecall-workflow",
    "SYNC":      "lifecycle/sync-workflow",
    "TRAIN":     "lifecycle/train-workflow",
    # Non-code-touching — reads-only, LENS scan with trace (WC-005 + Phase 91)
    # INVESTIGATE gets a lightweight template for SQLite traceability without code gating.
    "INVESTIGATE": "lifecycle/investigate-workflow",
    "RCA":       "rca/rca-analysis-workflow",
    "DIGEST":    "lifecycle/digest-workflow",
    # Pure non-code-touching — no template required
    "QUERY":   None,
    "DESIGN":  None,
    "PLAN":    None,
    "REPHRASE": None,
    "GOLDEN_TEST": "tdd/tdd-workflow",
    "WORKFLOW_COMPOSE": "tdd/tdd-workflow",  # meta — composes dynamically
    # TrainerOrchestrator internal ops — exempt (non-code-touching, routed by TRAIN template)
    "SCAN":    None,
    "PROPOSE": None,
    "EXECUTE": None,
}

_SQLITE_DB = Path(".cortex-runtime") / "traces" / "orchestrator-traces.db"
_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS workflow_runs (
    run_id          TEXT PRIMARY KEY,
    orchestrator    TEXT NOT NULL,
    mode            TEXT NOT NULL,
    template_id     TEXT NOT NULL,
    status          TEXT NOT NULL,
    steps_completed INTEGER DEFAULT 0,
    duration_ms     REAL DEFAULT 0,
    started_at      TEXT NOT NULL,
    completed_at    TEXT,
    error           TEXT
);
"""


class WorkflowGatewayError(Exception):
    """Raised when WorkflowGateway cannot resolve a template for a code-touching mode."""


class WorkflowGateway:
    """Mandatory pre-execution gate for all code-touching CORTEX operations.

    No orchestrator may touch code without first passing through this gateway.
    The gateway:
      1. Resolves the canonical template for the requested mode
      2. Invokes WorkflowComposer.execute_from_template(convergence_mode=True)
      3. Emits AC_START / AC_COMPLETE markers
      4. Logs a row to SQLite workflow_runs table

    Usage::

        gateway = WorkflowGateway()
        result = gateway.execute_gated(
            orchestrator_name="TDDOrchestrator",
            mode="IMPLEMENT",
            context={"request_summary": "add new endpoint"},
        )

    The composer is lazily initialized and can be injected for testing::

        gateway._composer = mock_composer
    """

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize WorkflowGateway.

        Args:
            db_path: Path to SQLite trace database. Defaults to
                     .cortex-runtime/traces/orchestrator-traces.db
        """
        self._db_path = db_path or _SQLITE_DB
        self._composer: Optional[Any] = None  # lazy-initialized
        self._ensure_db()

    # ── PUBLIC API ────────────────────────────────────────────────────────

    def resolve_template(
        self,
        mode: str,
        context: Dict[str, Any],
        *,
        strict: bool = False,
    ) -> Optional[str]:
        """Resolve the canonical workflow template for the given mode.

        Args:
            mode: Operation mode string (e.g. "IMPLEMENT", "FIX", "REFACTOR").
            context: Execution context dict (may influence future routing).
            strict: When True, verify the resolved template YAML exists on disk
                    and raise WorkflowGatewayError if it is missing.  Use this
                    during governance audits and pre-execution gates to detect
                    stale ``_MODE_TEMPLATE_MAP`` entries early (P0 fail-fast).
                    Defaults to False for backward compatibility.

        Returns:
            Template ID string, or None if the mode is exempt (WC-005).

        Raises:
            WorkflowGatewayError: If ``strict=True`` and the resolved template
                YAML does not exist on disk.

        Example::

            gateway = WorkflowGateway()
            tid = gateway.resolve_template("IMPLEMENT", {})
            # → "sdlc/implement-workflow"

            # Fail-fast governance check:
            gateway.resolve_template("IMPLEMENT", {}, strict=True)
        """
        template_id = _MODE_TEMPLATE_MAP.get(mode.upper())

        if strict and template_id is not None:
            self._assert_template_yaml_exists(template_id)

        return template_id

    @staticmethod
    def get_mode_template_map() -> Dict[str, Optional[str]]:
        """Return a copy of the canonical mode→template mapping.

        Provides read-only access to ``_MODE_TEMPLATE_MAP`` for downstream
        consumers (e.g. SubPhaseComposer) so there is a single source of truth.
        The copy prevents callers from mutating the canonical map.

        Returns:
            Dict mapping mode strings (e.g. ``"IMPLEMENT"``) to template IDs
            (e.g. ``"sdlc/implement-workflow"``) or ``None`` for non-code-touching modes.

        Example::

            mapping = WorkflowGateway.get_mode_template_map()
            assert "IMPLEMENT" in mapping
            assert mapping["QUERY"] is None
        """
        return dict(_MODE_TEMPLATE_MAP)

    def _assert_template_yaml_exists(self, template_id: str) -> None:
        """Verify the template YAML file exists on disk; raise if missing.

        Args:
            template_id: Template identifier (e.g. ``"sdlc/implement-workflow"``).

        Raises:
            WorkflowGatewayError: If the YAML file is absent — indicates a stale
                ``_MODE_TEMPLATE_MAP`` entry that must be repaired immediately.
        """
        _templates_root = Path(__file__).parents[3] / "cortex-registry" / "workflows" / "templates"
        yaml_path = _templates_root / f"{template_id}.yaml"
        if not yaml_path.exists():
            raise WorkflowGatewayError(
                f"WorkflowGateway strict-resolve: template YAML missing for "
                f"'{template_id}' — expected at {yaml_path}. "
                "Update _MODE_TEMPLATE_MAP or create the missing template."
            )

    def execute_gated(
        self,
        orchestrator_name: str,
        mode: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Execute an operation via the mandatory workflow template gateway.

        Resolves template → composes with convergence_mode=True → logs trace.
        Raises WorkflowGatewayError for code-touching modes with no template.

        Args:
            orchestrator_name: Name of the calling orchestrator (for tracing).
            mode: Operation mode (IMPLEMENT, FIX, REFACTOR, DEBUG, HEALTH, VACUUM…).
            context: Full execution context dict.

        Returns:
            Dict with at minimum: template_id, status, steps_completed, run_id.

        Raises:
            WorkflowGatewayError: If mode is code-touching but no template maps to it.
        """
        mode_upper = mode.upper()
        template_id = self.resolve_template(mode_upper, context)

        # Non-exempt modes with no template are a governance violation
        if template_id is None and mode_upper not in _MODE_TEMPLATE_MAP:
            raise WorkflowGatewayError(
                f"WorkflowGateway: no template registered for mode '{mode}'. "
                "Register a template in _MODE_TEMPLATE_MAP or mark the mode as exempt."
            )

        # Exempt (non-code-touching) modes pass through without template routing
        if template_id is None:
            logger.debug("WorkflowGateway: mode '%s' is exempt (WC-005), bypassing.", mode)
            return {"status": "exempt", "mode": mode, "template_id": None}

        run_id = str(uuid.uuid4())
        started_ms = time.time() * 1000
        self._emit_ac_marker("AC_START", run_id, mode, template_id)

        try:
            composer = self._get_composer()
            # GAP-117-06 (Phase 117-b): inject the shared IntelligenceFacade singleton
            # into the execution context so every workflow step can call
            # context["intelligence_facade"].analyze() / synthesize() / query()
            # without constructing a new instance.
            from cortex.intelligence.facade import get_intelligence_facade as _get_facade
            enriched_context = dict(context or {})
            enriched_context.setdefault("intelligence_facade", _get_facade())
            composer_result = composer.execute_from_template(
                template_id,
                enriched_context,
                convergence_mode=True,
            )

            duration_ms = time.time() * 1000 - started_ms

            # WorkflowComposer returns WorkflowExecutionResult (dataclass) —
            # normalise to dict for gateway's uniform return type.
            if isinstance(composer_result, dict):
                result = composer_result
                status = result.get("status", "complete")
                steps = result.get("steps_completed", 0)
            else:
                # WorkflowExecutionResult dataclass
                status = "complete" if getattr(composer_result, "success", False) else "error"
                steps = getattr(composer_result, "steps_completed", 0)
                result = {
                    "status": status,
                    "steps_completed": steps,
                    "total_steps": getattr(composer_result, "total_steps", 0),
                    "success": getattr(composer_result, "success", False),
                    "error_message": getattr(composer_result, "error_message", None),
                }

            self._log_workflow_run(
                run_id=run_id,
                orchestrator=orchestrator_name,
                mode=mode_upper,
                template_id=template_id,
                status=status,
                steps_completed=steps,
                duration_ms=duration_ms,
            )
            self._emit_ac_marker("AC_COMPLETE", run_id, mode, template_id, status="✅")

            return {
                "run_id": run_id,
                "template_id": template_id,
                "status": status,
                "steps_completed": steps,
                "duration_ms": duration_ms,
                **(result if isinstance(result, dict) else {}),
            }

        except WorkflowGatewayError:
            raise
        except Exception as exc:
            duration_ms = time.time() * 1000 - started_ms
            error_msg = str(exc)
            self._log_workflow_run(
                run_id=run_id,
                orchestrator=orchestrator_name,
                mode=mode_upper,
                template_id=template_id,
                status="error",
                steps_completed=0,
                duration_ms=duration_ms,
                error=error_msg,
            )
            self._emit_ac_marker("AC_COMPLETE", run_id, mode, template_id, status="❌", error=error_msg)
            raise

    # ── INTERNAL ──────────────────────────────────────────────────────────

    def _get_composer(self) -> Any:
        """Lazy-initialize WorkflowComposer in gateway mode (no template_path).

        In gateway mode, the composer loads templates on-demand via
        ``execute_from_template(template_id_string)``.
        """
        if self._composer is None:
            from cortex.orchestrators.workflow.workflow_composer import WorkflowComposer
            self._composer = WorkflowComposer()  # gateway mode — template_path=None
        return self._composer

    def _emit_ac_marker(
        self,
        marker_type: str,
        run_id: str,
        mode: str,
        template_id: str,
        status: str = "",
        error: str = "",
    ) -> None:
        """Emit AC_START / AC_COMPLETE marker to logger.

        Args:
            marker_type: "AC_START" or "AC_COMPLETE".
            run_id: Unique run identifier.
            mode: Operation mode.
            template_id: Resolved template ID.
            status: Completion status emoji (✅/❌) for AC_COMPLETE.
            error: Error message if any.
        """
        if marker_type == "AC_START":
            logger.info(
                "AC_START: %s | mode=%s | template=%s | run=%s",
                "AC-P90-WFG",
                mode,
                template_id,
                run_id,
            )
        else:
            logger.info(
                "AC_COMPLETE: %s %s | mode=%s | template=%s | run=%s%s",
                "AC-P90-WFG",
                status,
                mode,
                template_id,
                run_id,
                f" | error={error}" if error else "",
            )

    def _ensure_db(self) -> None:
        """Create or migrate SQLite workflow_runs table.

        Phase 99: Detects schema mismatch from Phase 98 cleanup and
        recreates the table with the correct gateway schema. The old
        table (id, session_id, loop_name, invoked_at, result) is from
        the deleted convergence_loop_executor and is incompatible.
        """
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(str(self._db_path)) as conn:
                # Check if table exists and has the correct schema
                cursor = conn.execute("PRAGMA table_info(workflow_runs)")
                columns = {row[1] for row in cursor.fetchall()}

                if columns and "run_id" not in columns:
                    # Table exists with wrong schema — drop and recreate
                    logger.info(
                        "WorkflowGateway: migrating workflow_runs table "
                        "(old columns: %s)", columns
                    )
                    conn.execute("DROP TABLE workflow_runs")
                    conn.commit()

                conn.execute(_CREATE_TABLE_SQL)
                conn.commit()
        except Exception as exc:
            logger.warning("WorkflowGateway: could not initialize SQLite DB: %s", exc)

    def _log_workflow_run(
        self,
        *,
        run_id: str,
        orchestrator: str,
        mode: str,
        template_id: str,
        status: str,
        steps_completed: int,
        duration_ms: float,
        error: Optional[str] = None,
    ) -> None:
        """Persist a workflow run row to SQLite.

        Args:
            run_id: Unique run UUID.
            orchestrator: Orchestrator name.
            mode: Operation mode.
            template_id: Resolved template ID.
            status: "complete", "error", "converged", etc.
            steps_completed: Number of template steps executed.
            duration_ms: Elapsed duration in milliseconds.
            error: Error message if status is "error".
        """
        import datetime

        now = datetime.datetime.utcnow().isoformat()
        try:
            with sqlite3.connect(str(self._db_path)) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO workflow_runs
                        (run_id, orchestrator, mode, template_id, status,
                         steps_completed, duration_ms, started_at, completed_at, error)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        run_id,
                        orchestrator,
                        mode,
                        template_id,
                        status,
                        steps_completed,
                        duration_ms,
                        now,
                        now,
                        error,
                    ),
                )
                conn.commit()
        except Exception as exc:
            logger.warning("WorkflowGateway: SQLite log failed: %s", exc)


# AC_COMPLETE: AC-P90-WFG-001 ✅ WorkflowGateway implemented
