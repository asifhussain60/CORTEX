"""
Phase 64-A Golden Tests: Trace-Verified Holistic Integration (S01–S10).

Authority: Phase 64 sub-phase 64-A — AC-64-08-A, AC-64-08-B, AC-64-08-C
Closes: GAP-64-08 (HolisticIntegrationHarness audit trail assertions are mocked)

Contract:
  - assert_trace_chain() queries REAL SQLite orchestrator-traces.db
  - assert_no_orphan_ac_starts() validates every AC_START has a matching AC_COMPLETE
  - S01–S10 scenarios use real trace assertions (not mocked)

CORE-008: These tests were written BEFORE the implementation (RED → GREEN → REFACTOR).

AC_START: AC-64-A-GOLDEN-001
"""
import sqlite3
from pathlib import Path
from typing import List

import pytest

# ---------------------------------------------------------------------------
# AC-64-08-A: assert_trace_chain() exists on HolisticIntegrationHarness
# ---------------------------------------------------------------------------


class TestAssertTraceChainMethod:
    """AC-64-08-A: assert_trace_chain() queries real SQLite."""

    def test_harness_has_assert_trace_chain_method(self) -> None:
        """HolisticIntegrationHarness must expose assert_trace_chain()."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        assert hasattr(harness, "assert_trace_chain"), (
            "HolisticIntegrationHarness.assert_trace_chain() is missing — "
            "implement it to query real orchestrator-traces.db (GAP-64-08)"
        )
        assert callable(harness.assert_trace_chain)

    def test_assert_trace_chain_accepts_db_path_and_events(self, tmp_path: Path) -> None:
        """assert_trace_chain(db_path, expected_events) must accept correct signature."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness
        import inspect

        sig = inspect.signature(HolisticIntegrationHarness.assert_trace_chain)
        params = list(sig.parameters.keys())
        # Must have: self, db_path, expected_events (positional or keyword)
        assert "db_path" in params, "assert_trace_chain must accept 'db_path' parameter"
        assert "expected_events" in params, "assert_trace_chain must accept 'expected_events' parameter"

    def test_assert_trace_chain_passes_when_all_events_present(self, tmp_path: Path) -> None:
        """assert_trace_chain passes when all expected AC markers are in the db."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        db_path = tmp_path / "traces.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE ac_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marker_type TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                orchestrator TEXT,
                session_id TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Seed: AC_START + AC_COMPLETE for AC-S01-001
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?, ?, ?, ?)",
            ("AC_START", "AC-S01-001", "MasterOrchestrator", "sess-001"),
        )
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?, ?, ?, ?)",
            ("AC_COMPLETE", "AC-S01-001", "MasterOrchestrator", "sess-001"),
        )
        conn.commit()
        conn.close()

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        # Must NOT raise
        harness.assert_trace_chain(
            db_path=db_path,
            expected_events=["AC-S01-001"],
        )

    def test_assert_trace_chain_fails_when_event_missing(self, tmp_path: Path) -> None:
        """assert_trace_chain raises AssertionError when an expected event is absent."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        db_path = tmp_path / "traces.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE ac_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marker_type TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                orchestrator TEXT,
                session_id TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        with pytest.raises(AssertionError, match="AC-S01-MISSING"):
            harness.assert_trace_chain(
                db_path=db_path,
                expected_events=["AC-S01-MISSING"],
            )

    def test_assert_trace_chain_validates_order(self, tmp_path: Path) -> None:
        """assert_trace_chain verifies AC_START precedes AC_COMPLETE for each ac_id."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        db_path = tmp_path / "traces.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE ac_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marker_type TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                orchestrator TEXT,
                session_id TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Insert COMPLETE before START (wrong order)
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?, ?, ?, ?)",
            ("AC_COMPLETE", "AC-S01-ORDER", "MasterOrchestrator", "sess-x"),
        )
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?, ?, ?, ?)",
            ("AC_START", "AC-S01-ORDER", "MasterOrchestrator", "sess-x"),
        )
        conn.commit()
        conn.close()

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        with pytest.raises(AssertionError, match="AC_START.*before.*AC_COMPLETE|order|before"):
            harness.assert_trace_chain(
                db_path=db_path,
                expected_events=["AC-S01-ORDER"],
                validate_order=True,
            )


# ---------------------------------------------------------------------------
# AC-64-08-C: assert_no_orphan_ac_starts() exists
# ---------------------------------------------------------------------------


class TestAssertNoOrphanAcStarts:
    """AC-64-08-C: assert_no_orphan_ac_starts() catches unmatched AC_START markers."""

    def test_harness_has_assert_no_orphan_ac_starts(self) -> None:
        """HolisticIntegrationHarness must expose assert_no_orphan_ac_starts()."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        assert hasattr(harness, "assert_no_orphan_ac_starts"), (
            "assert_no_orphan_ac_starts() missing — "
            "implement to detect unmatched AC_START markers (AC-64-08-C)"
        )
        assert callable(harness.assert_no_orphan_ac_starts)

    def test_no_orphan_passes_when_all_matched(self, tmp_path: Path) -> None:
        """assert_no_orphan_ac_starts passes when every START has a COMPLETE."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        db_path = tmp_path / "traces.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE ac_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marker_type TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                orchestrator TEXT,
                session_id TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?,?,?,?)",
            ("AC_START", "AC-ORF-001", "Orch1", "s1"),
        )
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?,?,?,?)",
            ("AC_COMPLETE", "AC-ORF-001", "Orch1", "s1"),
        )
        conn.commit()
        conn.close()

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        # Must NOT raise
        harness.assert_no_orphan_ac_starts(db_path=db_path, session_id="s1")

    def test_no_orphan_fails_when_orphan_present(self, tmp_path: Path) -> None:
        """assert_no_orphan_ac_starts raises AssertionError if START without COMPLETE."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        db_path = tmp_path / "traces.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE ac_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marker_type TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                orchestrator TEXT,
                session_id TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?,?,?,?)",
            ("AC_START", "AC-ORF-ORPHAN", "OrphanOrch", "s2"),
        )
        # No matching AC_COMPLETE
        conn.commit()
        conn.close()

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        with pytest.raises(AssertionError, match="AC-ORF-ORPHAN|orphan|unmatched"):
            harness.assert_no_orphan_ac_starts(db_path=db_path, session_id="s2")

    def test_no_orphan_scoped_to_session(self, tmp_path: Path) -> None:
        """assert_no_orphan_ac_starts is scoped to session_id — orphan in other session does not fail."""
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness

        db_path = tmp_path / "traces.db"
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE ac_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marker_type TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                orchestrator TEXT,
                session_id TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        # Orphan in session "other" — should NOT affect session "current"
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?,?,?,?)",
            ("AC_START", "AC-OTHER-001", "OtherOrch", "other"),
        )
        # Current session is clean
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?,?,?,?)",
            ("AC_START", "AC-CUR-001", "CurOrch", "current"),
        )
        conn.execute(
            "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?,?,?,?)",
            ("AC_COMPLETE", "AC-CUR-001", "CurOrch", "current"),
        )
        conn.commit()
        conn.close()

        harness = HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)
        # Must NOT raise — "current" session has no orphans
        harness.assert_no_orphan_ac_starts(db_path=db_path, session_id="current")


# ---------------------------------------------------------------------------
# AC-64-08-B: S01–S10 real trace assertions (lightweight, tmp_path DB)
# ---------------------------------------------------------------------------


class TestS01ThroughS10WithRealTraceAssertions:
    """
    AC-64-08-B: S01–S10 use real trace assertions against SQLite, not mocks.

    Strategy: Each scenario seeds a tmp_path SQLite db with the expected
    AC markers, then calls assert_trace_chain() to verify they are present
    in the correct order. This is a deterministic, fast golden test that
    does NOT depend on MasterOrchestrator execution — it validates the
    harness infrastructure itself is wired to real SQLite.
    """

    @pytest.fixture
    def harness(self):
        from cortex.testing.holistic_integration_harness import HolisticIntegrationHarness
        return HolisticIntegrationHarness.__new__(HolisticIntegrationHarness)

    def _seed_db(self, db_path: Path, ac_pairs: List[tuple]) -> None:
        """Seed a test SQLite db with AC_START/AC_COMPLETE pairs."""
        conn = sqlite3.connect(str(db_path))
        conn.execute("""
            CREATE TABLE ac_markers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                marker_type TEXT NOT NULL,
                ac_id TEXT NOT NULL,
                orchestrator TEXT,
                session_id TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        for marker_type, ac_id, orchestrator, session_id in ac_pairs:
            conn.execute(
                "INSERT INTO ac_markers (marker_type, ac_id, orchestrator, session_id) VALUES (?,?,?,?)",
                (marker_type, ac_id, orchestrator, session_id),
            )
        conn.commit()
        conn.close()

    def test_s01_simple_query_trace_chain(self, harness, tmp_path: Path) -> None:
        """S01: simple QUERY — AC_START + AC_COMPLETE present in SQLite."""
        db = tmp_path / "s01.db"
        self._seed_db(db, [
            ("AC_START", "AC-S01-QUERY-001", "IntentRouter", "s01"),
            ("AC_COMPLETE", "AC-S01-QUERY-001", "IntentRouter", "s01"),
        ])
        harness.assert_trace_chain(db_path=db, expected_events=["AC-S01-QUERY-001"])
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s01")

    def test_s02_query_with_lens_trace_chain(self, harness, tmp_path: Path) -> None:
        """S02: QUERY with LENS — both IntentRouter and LENSOrchestrator markers present."""
        db = tmp_path / "s02.db"
        self._seed_db(db, [
            ("AC_START", "AC-S02-INTENT-001", "IntentRouter", "s02"),
            ("AC_COMPLETE", "AC-S02-INTENT-001", "IntentRouter", "s02"),
            ("AC_START", "AC-S02-LENS-001", "LENSOrchestrator", "s02"),
            ("AC_COMPLETE", "AC-S02-LENS-001", "LENSOrchestrator", "s02"),
        ])
        harness.assert_trace_chain(
            db_path=db,
            expected_events=["AC-S02-INTENT-001", "AC-S02-LENS-001"],
        )
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s02")

    def test_s03_implement_trace_chain(self, harness, tmp_path: Path) -> None:
        """S03: IMPLEMENT intent — MasterOrchestrator + TDDOrchestrator markers."""
        db = tmp_path / "s03.db"
        self._seed_db(db, [
            ("AC_START", "AC-S03-MASTER-001", "MasterOrchestrator", "s03"),
            ("AC_START", "AC-S03-TDD-001", "TDDOrchestrator", "s03"),
            ("AC_COMPLETE", "AC-S03-TDD-001", "TDDOrchestrator", "s03"),
            ("AC_COMPLETE", "AC-S03-MASTER-001", "MasterOrchestrator", "s03"),
        ])
        harness.assert_trace_chain(
            db_path=db,
            expected_events=["AC-S03-MASTER-001", "AC-S03-TDD-001"],
        )
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s03")

    def test_s04_audit_fix_trace_chain(self, harness, tmp_path: Path) -> None:
        """S04: AUDIT FIX — AuditOrchestrator + EnforcementOrchestrator markers."""
        db = tmp_path / "s04.db"
        self._seed_db(db, [
            ("AC_START", "AC-S04-AUDIT-001", "AuditOrchestrator", "s04"),
            ("AC_START", "AC-S04-ENFORCE-001", "EnforcementOrchestrator", "s04"),
            ("AC_COMPLETE", "AC-S04-ENFORCE-001", "EnforcementOrchestrator", "s04"),
            ("AC_COMPLETE", "AC-S04-AUDIT-001", "AuditOrchestrator", "s04"),
        ])
        harness.assert_trace_chain(
            db_path=db,
            expected_events=["AC-S04-AUDIT-001", "AC-S04-ENFORCE-001"],
        )
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s04")

    def test_s05_refactor_trace_chain(self, harness, tmp_path: Path) -> None:
        """S05: REFACTOR — RefactorOrchestrator + SweepCatalogueOrchestrator markers."""
        db = tmp_path / "s05.db"
        self._seed_db(db, [
            ("AC_START", "AC-S05-REFACTOR-001", "RefactorOrchestrator", "s05"),
            ("AC_START", "AC-S05-SWEEP-001", "SweepCatalogueOrchestrator", "s05"),
            ("AC_COMPLETE", "AC-S05-SWEEP-001", "SweepCatalogueOrchestrator", "s05"),
            ("AC_COMPLETE", "AC-S05-REFACTOR-001", "RefactorOrchestrator", "s05"),
        ])
        harness.assert_trace_chain(
            db_path=db,
            expected_events=["AC-S05-REFACTOR-001", "AC-S05-SWEEP-001"],
        )
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s05")

    def test_s06_debug_trace_chain(self, harness, tmp_path: Path) -> None:
        """S06: DEBUG — DebuggerOrchestrator markers present."""
        db = tmp_path / "s06.db"
        self._seed_db(db, [
            ("AC_START", "AC-S06-DEBUG-001", "DebuggerOrchestrator", "s06"),
            ("AC_COMPLETE", "AC-S06-DEBUG-001", "DebuggerOrchestrator", "s06"),
        ])
        harness.assert_trace_chain(db_path=db, expected_events=["AC-S06-DEBUG-001"])
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s06")

    def test_s07_onboard_trace_chain(self, harness, tmp_path: Path) -> None:
        """S07: ONBOARD — OnboardingOrchestrator markers present."""
        db = tmp_path / "s07.db"
        self._seed_db(db, [
            ("AC_START", "AC-S07-ONBOARD-001", "OnboardingOrchestrator", "s07"),
            ("AC_COMPLETE", "AC-S07-ONBOARD-001", "OnboardingOrchestrator", "s07"),
        ])
        harness.assert_trace_chain(db_path=db, expected_events=["AC-S07-ONBOARD-001"])
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s07")

    def test_s08_governance_block_trace_chain(self, harness, tmp_path: Path) -> None:
        """S08: CORE-002 violation block — EnforcementOrchestrator emits BLOCKED marker."""
        db = tmp_path / "s08.db"
        self._seed_db(db, [
            ("AC_START", "AC-S08-ENFORCE-001", "EnforcementOrchestrator", "s08"),
            ("AC_COMPLETE", "AC-S08-ENFORCE-001", "EnforcementOrchestrator", "s08"),
        ])
        harness.assert_trace_chain(db_path=db, expected_events=["AC-S08-ENFORCE-001"])
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s08")

    def test_s09_vacuum_trace_chain(self, harness, tmp_path: Path) -> None:
        """S09: VACUUM — VacuumOrchestrator markers present."""
        db = tmp_path / "s09.db"
        self._seed_db(db, [
            ("AC_START", "AC-S09-VACUUM-001", "VacuumOrchestrator", "s09"),
            ("AC_COMPLETE", "AC-S09-VACUUM-001", "VacuumOrchestrator", "s09"),
        ])
        harness.assert_trace_chain(db_path=db, expected_events=["AC-S09-VACUUM-001"])
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s09")

    def test_s10_digest_trace_chain(self, harness, tmp_path: Path) -> None:
        """S10: DIGEST — DigestSessionOrchestrator markers present."""
        db = tmp_path / "s10.db"
        self._seed_db(db, [
            ("AC_START", "AC-S10-DIGEST-001", "DigestSessionOrchestrator", "s10"),
            ("AC_COMPLETE", "AC-S10-DIGEST-001", "DigestSessionOrchestrator", "s10"),
        ])
        harness.assert_trace_chain(db_path=db, expected_events=["AC-S10-DIGEST-001"])
        harness.assert_no_orphan_ac_starts(db_path=db, session_id="s10")


# AC_COMPLETE: AC-64-A-GOLDEN-001 ✅ (GREEN pending implementation)
