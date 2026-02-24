"""
Holistic Integration Harness — Production Testing Infrastructure.

Authority: Phase 64 sub-phase 64-A — GAP-64-08
Closes: AC-64-08-A, AC-64-08-B, AC-64-08-C

Adds to CORTEX testing infrastructure:
  - assert_trace_chain()           — queries REAL SQLite orchestrator traces (AC-64-08-A)
  - assert_no_orphan_ac_starts()   — detects unmatched AC_START markers (AC-64-08-C)

Design contract:
  - Zero production orchestrator dependencies (test infrastructure only)
  - Uses `ac_markers` SQLite table (tmp_path fixture or real .cortex-runtime/traces/)
  - All assertions raise AssertionError with actionable messages
  - CORE-011: all public methods fully type-hinted
  - CORE-012: all public methods have docstrings

Schema expected (tmp_path or real db):
  TABLE ac_markers (
      id            INTEGER PRIMARY KEY AUTOINCREMENT,
      marker_type   TEXT NOT NULL,   -- 'AC_START' | 'AC_COMPLETE'
      ac_id         TEXT NOT NULL,   -- e.g. 'AC-S01-QUERY-001'
      orchestrator  TEXT,
      session_id    TEXT,
      timestamp     TEXT DEFAULT CURRENT_TIMESTAMP
  )

Author: Asif Hussain
"""
import sqlite3
from pathlib import Path
from typing import List, Optional

# AC_START: AC-64-A-IMPL-001

class HolisticIntegrationHarness:
    """
    Production test harness for CORTEX holistic integration validation.

    Provides real SQLite trace assertions for golden tests — replacing
    mocked audit event assertions with queries against actual SQLite dbs.

    Usage (in golden tests)::

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        harness.assert_trace_chain(db_path=tmp_db, expected_events=["AC-S01-001"])
        harness.assert_no_orphan_ac_starts(db_path=tmp_db, session_id="s01")

    For full holistic integration scenarios (S01–S25), combine with
    the fixture harness in tests/golden/holistic_integration/fixtures/.
    """
    # ------------------------------------------------------------------
    # AC-64-08-A: assert_trace_chain — real SQLite query
    # ------------------------------------------------------------------

    def assert_trace_chain(
        self,
        db_path: Path,
        expected_events: List[str],
        validate_order: bool = False,
    ) -> None:
        """
        Assert that every expected AC marker is present in the SQLite db.

        Queries the `ac_markers` table for each ac_id in expected_events.
        For each ac_id, verifies:
          - At least one AC_START row is present
          - At least one AC_COMPLETE row is present
          - If validate_order=True: AC_START.id < AC_COMPLETE.id (insertion order)

        Args:
            db_path: Path to the SQLite database containing `ac_markers` table.
            expected_events: List of ac_id strings that must be present.
            validate_order: If True, assert AC_START precedes AC_COMPLETE by row id.

        Raises:
            AssertionError: If any expected ac_id is missing or ordering is wrong.
        """
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            for ac_id in expected_events:
                rows = conn.execute(
                    "SELECT id, marker_type FROM ac_markers WHERE ac_id = ? ORDER BY id ASC",
                    (ac_id,),
                ).fetchall()

                marker_types = {r["marker_type"] for r in rows}

                assert "AC_START" in marker_types, (
                    f"assert_trace_chain: AC_START for '{ac_id}' not found in {db_path}. "
                    f"Found marker_types: {marker_types or '(none)'}. "
                    "Ensure the orchestrator emits AC_START before executing."
                )
                assert "AC_COMPLETE" in marker_types, (
                    f"assert_trace_chain: AC_COMPLETE for '{ac_id}' not found in {db_path}. "
                    f"AC_START was found but no matching AC_COMPLETE. "
                    "Orphaned AC_START — orchestrator did not reach completion."
                )

                if validate_order:
                    # Find lowest id for AC_START and AC_COMPLETE
                    starts = [r["id"] for r in rows if r["marker_type"] == "AC_START"]
                    completes = [r["id"] for r in rows if r["marker_type"] == "AC_COMPLETE"]
                    first_start = min(starts)
                    first_complete = min(completes)
                    assert first_start < first_complete, (
                        f"assert_trace_chain: ordering violation for '{ac_id}' — "
                        f"AC_START must be inserted before AC_COMPLETE. "
                        f"AC_START.id={first_start}, AC_COMPLETE.id={first_complete}. "
                        "Check that the orchestrator opens the AC session before closing it."
                    )
        finally:
            conn.close()

    # ------------------------------------------------------------------
    # AC-64-08-C: assert_no_orphan_ac_starts — unmatched START detection
    # ------------------------------------------------------------------

    def assert_no_orphan_ac_starts(
        self,
        db_path: Path,
        session_id: Optional[str] = None,
    ) -> None:
        """
        Assert that every AC_START in the db has a matching AC_COMPLETE.

        Queries `ac_markers` for all AC_START rows in scope (optionally
        filtered by session_id) and verifies each ac_id also has an
        AC_COMPLETE row. Orphaned AC_START markers indicate a governance
        violation (P0: CORE AC marker contract broken).

        Args:
            db_path: Path to the SQLite database containing `ac_markers` table.
            session_id: If provided, scope the check to this session only.
                        If None, checks all rows in the table.

        Raises:
            AssertionError: If any AC_START has no matching AC_COMPLETE.
                            Error message includes the orphaned ac_id(s).
        """
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        try:
            if session_id is not None:
                starts = conn.execute(
                    "SELECT DISTINCT ac_id FROM ac_markers "
                    "WHERE marker_type = 'AC_START' AND session_id = ?",
                    (session_id,),
                ).fetchall()
                completes = conn.execute(
                    "SELECT DISTINCT ac_id FROM ac_markers "
                    "WHERE marker_type = 'AC_COMPLETE' AND session_id = ?",
                    (session_id,),
                ).fetchall()
            else:
                starts = conn.execute(
                    "SELECT DISTINCT ac_id FROM ac_markers WHERE marker_type = 'AC_START'"
                ).fetchall()
                completes = conn.execute(
                    "SELECT DISTINCT ac_id FROM ac_markers WHERE marker_type = 'AC_COMPLETE'"
                ).fetchall()

            start_ids = {r["ac_id"] for r in starts}
            complete_ids = {r["ac_id"] for r in completes}
            orphans = start_ids - complete_ids

            scope_desc = f"session_id='{session_id}'" if session_id else "all sessions"
            assert not orphans, (
                f"assert_no_orphan_ac_starts: Found {len(orphans)} orphaned AC_START marker(s) "
                f"in {db_path} ({scope_desc}) with no matching AC_COMPLETE:\n"
                + "\n".join(f"  - {ac_id}" for ac_id in sorted(orphans))
                + "\nEnsure every orchestrator emits AC_COMPLETE on success AND failure paths."
            )
        finally:
            conn.close()

# AC_COMPLETE: AC-64-A-IMPL-001 ✅ HolisticIntegrationHarness implemented (Phase 64-A GREEN)
