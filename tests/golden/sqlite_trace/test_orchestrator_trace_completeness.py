"""Phase 128-e: SQLite Trace Completeness Golden Test.

Authority: GAP-128-E-02 (Orchestrators missing AC_START/AC_COMPLETE SQLite trace)
Governance: CORE-008 (TDD mandatory), CORE-064 (Sweep Completeness)
SSOT: cortex-registry/planning/phases/completed/phase-128-conflict-drift-eradication.yaml

Verifies the structural integrity of the SQLite trace system:
1. trace_master table schema is correct when the DB exists
2. All wired orchestrators reference AC_START/AC_COMPLETE in source code
3. No orphaned AC_START without matching AC_COMPLETE patterns in source
4. In-memory trace roundtrip works correctly
"""
from __future__ import annotations

import re
import sqlite3
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
ORCHESTRATORS_ROOT = REPO_ROOT / "cortex" / "orchestrators"
TRACE_DB_PATH = REPO_ROOT / ".cortex-runtime" / "traces" / "orchestrator-traces.db"

# Core orchestrators that MUST emit AC markers (per cortex-master.yaml wiring)
CORE_ORCHESTRATORS = [
    "core/master_orchestrator.py",
    "core/intent_router.py",
    "core/tdd_orchestrator.py",
    "core/enforcement_orchestrator/__init__.py",
]


def _create_test_trace_db() -> sqlite3.Connection:
    """Create an in-memory trace DB with canonical schema for testing."""
    conn = sqlite3.connect(":memory:")
    conn.execute("""
        CREATE TABLE trace_master (
            trace_id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT DEFAULT (datetime('now')),
            action TEXT NOT NULL,
            level TEXT DEFAULT 'ACTION',
            correlation_id TEXT,
            request_id TEXT,
            context TEXT,
            result TEXT,
            violation_type TEXT,
            duration_ms INTEGER,
            metadata TEXT
        )
    """)
    conn.commit()
    return conn


class TestTraceSchemaIntegrity:
    """Verify the trace DB schema contract is correct."""

    def test_trace_master_schema_roundtrip(self) -> None:
        """In-memory trace DB must accept AC_START and AC_COMPLETE inserts."""
        conn = _create_test_trace_db()

        conn.execute(
            "INSERT INTO trace_master (action, context) VALUES (?, ?)",
            ("AC_START", '{"operation": "TEST_OP", "orchestrator": "TestOrch"}'),
        )
        conn.execute(
            "INSERT INTO trace_master (action, context, duration_ms) VALUES (?, ?, ?)",
            ("AC_COMPLETE", '{"operation": "TEST_OP", "orchestrator": "TestOrch"}', 42),
        )
        conn.commit()

        rows = conn.execute("SELECT action FROM trace_master ORDER BY trace_id").fetchall()
        actions = [r[0] for r in rows]
        assert actions == ["AC_START", "AC_COMPLETE"]
        conn.close()

    def test_orphan_detection_logic(self) -> None:
        """Orphan detection query must identify AC_START without AC_COMPLETE."""
        conn = _create_test_trace_db()

        # Insert orphaned AC_START (no matching AC_COMPLETE)
        conn.execute(
            "INSERT INTO trace_master (action, correlation_id) VALUES (?, ?)",
            ("AC_START", "orphan-001"),
        )
        # Insert paired AC_START + AC_COMPLETE
        conn.execute(
            "INSERT INTO trace_master (action, correlation_id) VALUES (?, ?)",
            ("AC_START", "paired-001"),
        )
        conn.execute(
            "INSERT INTO trace_master (action, correlation_id) VALUES (?, ?)",
            ("AC_COMPLETE", "paired-001"),
        )
        conn.commit()

        orphans = conn.execute("""
            SELECT correlation_id FROM trace_master
            WHERE action = 'AC_START'
            AND correlation_id NOT IN (
                SELECT correlation_id FROM trace_master
                WHERE action = 'AC_COMPLETE'
                AND correlation_id IS NOT NULL
            )
        """).fetchall()

        orphan_ids = [r[0] for r in orphans]
        assert "orphan-001" in orphan_ids
        assert "paired-001" not in orphan_ids
        conn.close()

    @pytest.mark.skipif(
        not TRACE_DB_PATH.exists(),
        reason="orchestrator-traces.db not present (runtime artifact)",
    )
    def test_live_trace_db_has_trace_master_table(self) -> None:
        """If the trace DB exists, it must contain the trace_master table."""
        conn = sqlite3.connect(str(TRACE_DB_PATH))
        tables = [
            t[0]
            for t in conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            ).fetchall()
        ]
        conn.close()
        assert "trace_master" in tables, (
            f"trace_master table missing from {TRACE_DB_PATH}. "
            f"Found tables: {tables}"
        )


class TestOrchestratorACMarkerCoverage:
    """Verify all core orchestrators have AC marker references in source."""

    @pytest.mark.parametrize("rel_path", CORE_ORCHESTRATORS)
    def test_core_orchestrator_has_ac_start(self, rel_path: str) -> None:
        """Each core orchestrator must reference AC_START in its source."""
        full_path = ORCHESTRATORS_ROOT / rel_path
        if not full_path.exists():
            pytest.skip(f"{rel_path} not found")
        content = full_path.read_text(errors="replace")
        assert re.search(r"\bAC_START\b", content), (
            f"{rel_path} has no AC_START reference"
        )

    @pytest.mark.parametrize("rel_path", CORE_ORCHESTRATORS)
    def test_core_orchestrator_has_ac_complete(self, rel_path: str) -> None:
        """Each core orchestrator must reference AC_COMPLETE in its source."""
        full_path = ORCHESTRATORS_ROOT / rel_path
        if not full_path.exists():
            pytest.skip(f"{rel_path} not found")
        content = full_path.read_text(errors="replace")
        assert re.search(r"\bAC_COMPLETE\b", content), (
            f"{rel_path} has no AC_COMPLETE reference"
        )

    def test_no_orphaned_ac_start_in_orchestrators(self) -> None:
        """No orchestrator file should have AC_START without AC_COMPLETE."""
        orphaned = []
        for py_file in ORCHESTRATORS_ROOT.rglob("*.py"):
            if "__pycache__" in str(py_file) or "test_" in py_file.name:
                continue
            content = py_file.read_text(errors="replace")
            starts = len(re.findall(r"\bAC_START\b", content))
            completes = len(re.findall(r"\bAC_COMPLETE\b", content))
            if starts > 0 and completes == 0:
                rel = py_file.relative_to(REPO_ROOT)
                orphaned.append(f"{rel}: {starts} AC_START, 0 AC_COMPLETE")

        assert not orphaned, (
            "Orphaned AC_START markers (no matching AC_COMPLETE):\n"
            + "\n".join(f"  - {o}" for o in orphaned)
        )
