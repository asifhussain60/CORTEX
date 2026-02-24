"""
HolisticFileReviewGate — CORE-065 enforcement.

Implements the BEFORE/AFTER holistic file inventory gate defined in:
  cortex-registry/workflows/templates/governance/holistic-file-review-gate.yaml

Evaluates 5 blocking gates after a FIX/REFACTOR/IMPLEMENT/AUDIT operation:
  GATE-1: No files skipped (files_skipped_count == 0)
  GATE-2: All high-risk files touched (risk_score > 0.4 → must appear in post)
  GATE-3: No new lint errors (post_lint_errors <= pre_lint_errors)
  GATE-4: No test regression (test_count_after >= test_count_before, CORE-008)
  GATE-5: Sweep catalogue exhausted (sweep_open_items == 0, CORE-064)

Multi-session continuity via SQLite: persist_session_state() / load_session_state()
allow a sweep started in one VS Code Copilot Chat Session to resume in the next.

Authority: CORE-065 (Holistic File Review Contract)
           CORE-064 (Sweep Completeness Contract)
           CORE-008 (TDD-First — no test regression gate)
           CORE-002 (All output inline — no report files)

AC_START: AC-64-G-IMPL-001
Phase: 64 | Stage: G | Priority: P0
"""

import sqlite3
import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Risk threshold: files with risk_score >= this are "high-risk" and MUST be touched
_HIGH_RISK_THRESHOLD: float = 0.4


class HolisticFileReviewGate:
    """Evaluates CORE-065 holistic file review gates after a multi-file operation.

    Args:
        db_connection: Optional SQLite connection for multi-session continuity.
                       When provided, persist_session_state() and
                       load_session_state() write/read from this connection.
                       When None, session state methods are no-ops.

    Example:
        >>> gate = HolisticFileReviewGate()
        >>> result = gate.evaluate_gates(pre_snapshot, post_snapshot)
        >>> result["all_gates_passed"]
        True
    """

    def __init__(self, db_connection: Optional[sqlite3.Connection] = None) -> None:
        """Initialize HolisticFileReviewGate.

        Args:
            db_connection: Optional SQLite connection for sweep session persistence.
        """
        self._db = db_connection

    # ──────────────────────────────────────────────────────────────────────────
    # PUBLIC: Gate evaluation
    # ──────────────────────────────────────────────────────────────────────────

    def evaluate_gates(
        self,
        pre_snapshot: Dict[str, Any],
        post_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Evaluate all 5 CORE-065 gates comparing pre and post work snapshots.

        Args:
            pre_snapshot: Holistic file inventory captured BEFORE the operation.
                Keys expected:
                  - files: List[dict] each with 'path', 'risk_score', 'open_issues',
                            'test_coverage_pct'
                  - pre_lint_errors: int
                  - pre_test_count: int
                  - high_risk_files: List[str] (paths with risk_score >= threshold)
            post_snapshot: State captured AFTER the operation.
                Keys expected:
                  - files_reviewed: List[str] (paths that were actually touched)
                  - post_lint_errors: int
                  - post_test_count: int
                  - high_risk_files_touched: List[str]
                  - sweep_open_items: int

        Returns:
            Dict with:
              - all_gates_passed: bool
              - gates: Dict[str, Dict] — per-gate result with 'passed', 'message', etc.
              - files_skipped_count: int
              - files_skipped: List[str]
        """
        pre_files: List[str] = [
            f["path"] for f in pre_snapshot.get("files", [])
        ]
        reviewed: List[str] = post_snapshot.get("files_reviewed", [])

        gate1 = self._gate1_no_files_skipped(pre_files, reviewed)
        gate2 = self._gate2_high_risk_touched(pre_snapshot, post_snapshot)
        gate3 = self._gate3_no_new_lint_errors(pre_snapshot, post_snapshot)
        gate4 = self._gate4_no_test_regression(pre_snapshot, post_snapshot)
        gate5 = self._gate5_sweep_exhausted(post_snapshot)

        gates = {
            "GATE-1": gate1,
            "GATE-2": gate2,
            "GATE-3": gate3,
            "GATE-4": gate4,
            "GATE-5": gate5,
        }
        all_passed = all(g["passed"] for g in gates.values())
        skipped = gate1.get("files_skipped", [])

        logger.info(
            "HolisticFileReviewGate: all_gates_passed=%s skipped=%d",
            all_passed,
            len(skipped),
        )

        return {
            "all_gates_passed": all_passed,
            "gates": gates,
            "files_skipped_count": len(skipped),
            "files_skipped": skipped,
        }

    # ──────────────────────────────────────────────────────────────────────────
    # PUBLIC: Multi-session continuity
    # ──────────────────────────────────────────────────────────────────────────

    def persist_session_state(
        self,
        sweep_id: str,
        operation_type: str,
        step_last_completed: str,
        pre_snapshot_json: str = "",
        post_snapshot_json: str = "",
        gate_results_json: str = "",
    ) -> None:
        """Persist sweep session state to SQLite for multi-session resume.

        Args:
            sweep_id: Unique sweep identifier (UUID).
            operation_type: FIX | REFACTOR | IMPLEMENT | AUDIT
            step_last_completed: Last step that completed successfully.
            pre_snapshot_json: JSON-serialised pre-work snapshot (optional).
            post_snapshot_json: JSON-serialised post-work snapshot (optional).
            gate_results_json: JSON-serialised gate results (optional).
        """
        if self._db is None:
            logger.debug(
                "persist_session_state: no db_connection — skipping persistence"
            )
            return

        self._db.execute(
            """
            INSERT INTO holistic_review_sessions (
                sweep_id, operation_type, step_last_completed,
                pre_snapshot_json, post_snapshot_json, gate_results_json
            ) VALUES (?, ?, ?, ?, ?, ?)
            ON CONFLICT(sweep_id) DO UPDATE SET
                step_last_completed = excluded.step_last_completed,
                pre_snapshot_json = excluded.pre_snapshot_json,
                post_snapshot_json = excluded.post_snapshot_json,
                gate_results_json = excluded.gate_results_json,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                sweep_id,
                operation_type,
                step_last_completed,
                pre_snapshot_json,
                post_snapshot_json,
                gate_results_json,
            ),
        )
        self._db.commit()
        logger.info(
            "Persisted session state: sweep_id=%s step=%s",
            sweep_id,
            step_last_completed,
        )

    def load_session_state(self, sweep_id: str) -> Optional[Dict[str, Any]]:
        """Load sweep session state from SQLite for resume.

        Args:
            sweep_id: Unique sweep identifier to look up.

        Returns:
            Dict with sweep state keys if found, None if not found.
        """
        if self._db is None:
            logger.debug(
                "load_session_state: no db_connection — returning None"
            )
            return None

        cursor = self._db.execute(
            """
            SELECT sweep_id, operation_type, step_last_completed,
                   pre_snapshot_json, post_snapshot_json, gate_results_json
            FROM holistic_review_sessions
            WHERE sweep_id = ?
            """,
            (sweep_id,),
        )
        row = cursor.fetchone()
        if row is None:
            return None

        return {
            "sweep_id": row[0],
            "operation_type": row[1],
            "step_last_completed": row[2],
            "pre_snapshot_json": row[3],
            "post_snapshot_json": row[4],
            "gate_results_json": row[5],
        }

    # ──────────────────────────────────────────────────────────────────────────
    # PRIVATE: Individual gate implementations
    # ──────────────────────────────────────────────────────────────────────────

    @staticmethod
    def _gate1_no_files_skipped(
        pre_files: List[str],
        reviewed: List[str],
    ) -> Dict[str, Any]:
        """GATE-1: Every file in pre-work scope must appear in post-work reviewed list."""
        reviewed_set = set(reviewed)
        skipped = [f for f in pre_files if f not in reviewed_set]
        passed = len(skipped) == 0
        return {
            "passed": passed,
            "gate_id": "GATE-1",
            "name": "No Files Skipped",
            "files_skipped": skipped,
            "message": (
                "All files reviewed ✅"
                if passed
                else f"{len(skipped)} file(s) skipped: {skipped}"
            ),
        }

    @staticmethod
    def _gate2_high_risk_touched(
        pre_snapshot: Dict[str, Any],
        post_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """GATE-2: All high-risk files (risk_score > threshold) must have been touched."""
        pre_high_risk: List[str] = [
            f["path"]
            for f in pre_snapshot.get("files", [])
            if f.get("risk_score", 0.0) > _HIGH_RISK_THRESHOLD
        ]
        post_touched: List[str] = post_snapshot.get("high_risk_files_touched", [])
        touched_set = set(post_touched)
        # Also count anything in files_reviewed as touched
        reviewed_set = set(post_snapshot.get("files_reviewed", []))
        untouched = [f for f in pre_high_risk if f not in touched_set and f not in reviewed_set]
        passed = len(untouched) == 0
        return {
            "passed": passed,
            "gate_id": "GATE-2",
            "name": "High-Risk Files Touched",
            "high_risk_total": len(pre_high_risk),
            "high_risk_untouched": untouched,
            "message": (
                "All high-risk files addressed ✅"
                if passed
                else f"{len(untouched)} high-risk file(s) untouched: {untouched}"
            ),
        }

    @staticmethod
    def _gate3_no_new_lint_errors(
        pre_snapshot: Dict[str, Any],
        post_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """GATE-3: post_lint_errors must not exceed pre_lint_errors."""
        pre_lint: int = pre_snapshot.get("pre_lint_errors", 0)
        post_lint: int = post_snapshot.get("post_lint_errors", 0)
        passed = post_lint <= pre_lint
        return {
            "passed": passed,
            "gate_id": "GATE-3",
            "name": "No New Lint Errors",
            "pre_lint_errors": pre_lint,
            "post_lint_errors": post_lint,
            "message": (
                f"Lint stable: {pre_lint}→{post_lint} ✅"
                if passed
                else f"New lint errors introduced: {pre_lint}→{post_lint} 🔴"
            ),
        }

    @staticmethod
    def _gate4_no_test_regression(
        pre_snapshot: Dict[str, Any],
        post_snapshot: Dict[str, Any],
    ) -> Dict[str, Any]:
        """GATE-4: post_test_count must be >= pre_test_count (CORE-008)."""
        pre_count: int = pre_snapshot.get("pre_test_count", 0)
        post_count: int = post_snapshot.get("post_test_count", 0)
        passed = post_count >= pre_count
        return {
            "passed": passed,
            "gate_id": "GATE-4",
            "name": "No Test Regression",
            "pre_test_count": pre_count,
            "post_test_count": post_count,
            "message": (
                f"Test count stable: {pre_count}→{post_count} ✅"
                if passed
                else (
                    f"CORE-008 violation: test count dropped "
                    f"{pre_count}→{post_count} 🔴"
                )
            ),
        }

    @staticmethod
    def _gate5_sweep_exhausted(post_snapshot: Dict[str, Any]) -> Dict[str, Any]:
        """GATE-5: Sweep catalogue must have zero open items (CORE-064)."""
        open_items: int = post_snapshot.get("sweep_open_items", 0)
        passed = open_items == 0
        return {
            "passed": passed,
            "gate_id": "GATE-5",
            "name": "Sweep Catalogue Exhausted",
            "open_items_count": open_items,
            "message": (
                "Sweep catalogue clean ✅"
                if passed
                else f"CORE-064: {open_items} open sweep item(s) remain 🔴"
            ),
        }


# AC_COMPLETE: AC-64-G-IMPL-001 ✅ HolisticFileReviewGate implemented (GREEN phase)
