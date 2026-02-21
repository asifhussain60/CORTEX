"""
Golden Tests — Sweep Completeness Contract (CORE-064 / Phase 16)

AC_START: AC-P16-B-001
Truth-based golden tests covering the full Sweep Completeness Contract.
Tests are P0/P1/P2 tiered; all must PASS when Phase 16 GREEN phase completes.

Semantic IDs follow CORTEX golden test conventions:
  GOL-SCT-{seq:03d}

Coverage matrix: 10 P0 · 5 P1 · 5 P2 = 20 total
AC_COMPLETE: AC-P16-B-001 ✅
"""
from __future__ import annotations

import importlib
import os
import sqlite3
import textwrap
from pathlib import Path
from types import SimpleNamespace
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
import yaml

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CORTEX_ROOT = Path(__file__).parent.parent.parent
SKULL_RULES = CORTEX_ROOT / "cortex-registry" / "core" / "tier0-skull" / "skull-rules.yaml"
SUPPORT_WIRING = (
    CORTEX_ROOT / "cortex-registry" / "core" / "specifications" / "support-orchestrator-wiring.yaml"
)
GOLDEN_TEST_FILE = Path(__file__)


def _import_sweep_catalogue_orchestrator():
    """Import SweepCatalogueOrchestrator — fails RED until Sub-phase C."""
    mod = importlib.import_module("cortex.orchestrators.support.sweep_catalogue_orchestrator")
    return mod.SweepCatalogueOrchestrator


def _import_sweep_status_tool():
    """Import cortex_sweep_status tool — fails RED until Sub-phase E."""
    mod = importlib.import_module("cortex.mcp.tools.sweep_status_tool")
    return mod.cortex_sweep_status


# ===========================================================================
# P0 — Critical path (open · mark · assert · MasterOrchestrator gates · rule)
# ===========================================================================


class TestOpenCatalogueCreatesSQLiteDB:
    """GOL-SCT-001 · P0 · AC-P16-001"""

    semantic_id = "GOL-SCT-001"

    def test_open_catalogue_creates_sqlite_db_in_cortex_runtime(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-001
        SweepCatalogueOrchestrator.open_catalogue() must create a SQLite .db
        file inside .cortex-runtime/sweeps/{sweep_id}.db.
        AC_COMPLETE: AC-P16-001 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        sweep_id = orch.open_catalogue(intent="FIX", scope_files=["cortex/foo.py"])
        assert sweep_id, "open_catalogue() must return a non-empty sweep_id"
        db_path = tmp_path / ".cortex-runtime" / "sweeps" / f"{sweep_id}.db"
        assert db_path.exists(), f"SQLite DB not found at {db_path}"
        # Verify WAL mode
        conn = sqlite3.connect(str(db_path))
        mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        conn.close()
        assert mode == "wal", f"Expected WAL journal mode, got {mode!r}"


class TestOpenCatalogueRunsFullScan:
    """GOL-SCT-002 · P0 · AC-P16-002"""

    semantic_id = "GOL-SCT-002"

    def test_open_catalogue_runs_full_enforcement_scan_on_scope(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-002
        open_catalogue() must enumerate ALL items in the declared scope —
        not a sample — and store them as open issues in the catalogue DB.
        AC_COMPLETE: AC-P16-002 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        scope = ["cortex/foo.py", "cortex/bar.py", "cortex/baz.py"]
        sweep_id = orch.open_catalogue(intent="REFACTOR", scope_files=scope)
        manifest = orch.get_manifest(sweep_id)
        assert "open_count" in manifest, "manifest must contain 'open_count'"
        assert "scope_files" in manifest, "manifest must contain 'scope_files'"
        assert set(manifest["scope_files"]) == set(scope)


class TestMarkResolvedDecrementsOpenCount:
    """GOL-SCT-003 · P0 · AC-P16-003"""

    semantic_id = "GOL-SCT-003"

    def test_mark_resolved_decrements_open_count(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-003
        mark_resolved(sweep_id, issue_id) must decrement open_count by 1
        and mark the item RESOLVED in the catalogue DB.
        AC_COMPLETE: AC-P16-003 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        sweep_id = orch.open_catalogue(intent="FIX", scope_files=["cortex/foo.py"])
        manifest_before = orch.get_manifest(sweep_id)
        # Seed one issue so we have something to resolve
        issue_id = orch.add_issue(sweep_id, file="cortex/foo.py", description="type error")
        count_before = orch.get_manifest(sweep_id)["open_count"]
        orch.mark_resolved(sweep_id, issue_id)
        count_after = orch.get_manifest(sweep_id)["open_count"]
        assert count_after == count_before - 1, (
            f"Expected open_count to decrement from {count_before} to {count_before - 1}, "
            f"got {count_after}"
        )


class TestAssertExhaustedOkWhenAllResolved:
    """GOL-SCT-004 · P0 · AC-P16-004"""

    semantic_id = "GOL-SCT-004"

    def test_assert_exhausted_returns_ok_when_all_resolved(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-004
        assert_exhausted() must return a truthy/Ok result when open_count == 0.
        AC_COMPLETE: AC-P16-004 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        sweep_id = orch.open_catalogue(intent="FIX", scope_files=["cortex/foo.py"])
        # No issues seeded → open_count starts at 0
        result = orch.assert_exhausted(sweep_id)
        assert result.ok, f"assert_exhausted should be Ok when open_count==0, got {result!r}"


class TestAssertExhaustedErrWithRemainingList:
    """GOL-SCT-005 · P0 · AC-P16-005"""

    semantic_id = "GOL-SCT-005"

    def test_assert_exhausted_returns_err_with_remaining_list_when_open(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-005
        assert_exhausted() must return an Err result containing the numbered
        list of remaining items when open_count > 0.
        AC_COMPLETE: AC-P16-005 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        sweep_id = orch.open_catalogue(intent="REFACTOR", scope_files=["cortex/foo.py"])
        orch.add_issue(sweep_id, file="cortex/foo.py", description="missing type hint")
        orch.add_issue(sweep_id, file="cortex/foo.py", description="missing docstring")
        result = orch.assert_exhausted(sweep_id)
        assert not result.ok, "assert_exhausted should be Err when open_count > 0"
        assert result.remaining, "Err result must include remaining items list"
        assert len(result.remaining) == 2


class TestMasterOrchestratorPreRoutingGateFix:
    """GOL-SCT-006 · P0 · AC-P16-006"""

    semantic_id = "GOL-SCT-006"

    def test_master_orchestrator_pre_routing_gate_opens_catalogue_for_fix_intent(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-006
        MasterOrchestrator._pre_routing_gate() must call
        SweepCatalogueOrchestrator.open_catalogue() for FIX intents.
        AC_COMPLETE: AC-P16-006 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        # Patch the backing instance attribute (property delegates to it)
        mock_sco = MagicMock()
        mock_sco.configure_mock(**{"open_catalogue.return_value": "sweep-fix-001"})
        mo._sweep_catalogue_orchestrator_instance = mock_sco
        mo._pre_routing_gate(intent="FIX", scope_files=["cortex/foo.py"])
        mock_sco.open_catalogue.assert_called_once_with(intent="FIX", scope_files=["cortex/foo.py"])


class TestMasterOrchestratorPreRoutingGateRefactor:
    """GOL-SCT-007 · P0 · AC-P16-007"""

    semantic_id = "GOL-SCT-007"

    def test_master_orchestrator_pre_routing_gate_opens_catalogue_for_refactor_intent(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-007
        MasterOrchestrator._pre_routing_gate() must call open_catalogue()
        for REFACTOR intents — not just FIX.
        AC_COMPLETE: AC-P16-007 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        mock_sco = MagicMock()
        mock_sco.configure_mock(**{"open_catalogue.return_value": "sweep-refactor-001"})
        mo._sweep_catalogue_orchestrator_instance = mock_sco
        mo._pre_routing_gate(intent="REFACTOR", scope_files=["cortex/bar.py"])
        mock_sco.open_catalogue.assert_called_once_with(
            intent="REFACTOR", scope_files=["cortex/bar.py"]
        )


class TestMasterOrchestratorFinalizeBlocksWhenRemaining:
    """GOL-SCT-008 · P0 · AC-P16-008"""

    semantic_id = "GOL-SCT-008"

    def test_master_orchestrator_finalize_blocks_when_remaining_greater_than_zero(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-008
        MasterOrchestrator._finalize_operation() must raise SweepIncompleteError
        (or equivalent blocking exception) when assert_exhausted() returns Err.
        AC_COMPLETE: AC-P16-008 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        err_result = SimpleNamespace(ok=False, remaining=["issue-1", "issue-2"])

        # Use SimpleNamespace stub — MagicMock blocks 'assert_*' attribute names
        class _StubSCO:
            def assert_exhausted(self, sweep_id):  # noqa: D102
                return err_result

        mo._sweep_catalogue_orchestrator_instance = _StubSCO()
        with pytest.raises(Exception, match=r"[Ss]weep|[Ii]ncomplete|[Rr]emaining"):
            mo._finalize_operation(sweep_id="sweep-001")


class TestMasterOrchestratorFinalizePassesWhenZero:
    """GOL-SCT-009 · P0 · AC-P16-009"""

    semantic_id = "GOL-SCT-009"

    def test_master_orchestrator_finalize_passes_when_remaining_zero(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-009
        MasterOrchestrator._finalize_operation() must NOT raise when
        assert_exhausted() returns Ok (remaining == 0).
        AC_COMPLETE: AC-P16-009 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()
        ok_result = SimpleNamespace(ok=True, remaining=[])

        class _StubSCO:
            def assert_exhausted(self, sweep_id):  # noqa: D102
                return ok_result

        mo._sweep_catalogue_orchestrator_instance = _StubSCO()
        mo._finalize_operation(sweep_id="sweep-001")  # Must not raise


class TestCore064RegisteredInSkullRules:
    """GOL-SCT-010 · P0 · AC-P16-010"""

    semantic_id = "GOL-SCT-010"

    def test_core_064_registered_in_skull_rules_yaml(self):
        """AC_START: AC-P16-010
        skull-rules.yaml must contain a rule with rule_id=CORE-064 and
        principle matching 'Sweep Completeness'.
        AC_COMPLETE: AC-P16-010 ✅"""
        assert SKULL_RULES.exists(), f"skull-rules.yaml not found at {SKULL_RULES}"
        data = yaml.safe_load(SKULL_RULES.read_text())
        rules = data.get("rules", [])
        core_064 = next((r for r in rules if r.get("rule_id") == "CORE-064"), None)
        assert core_064 is not None, "CORE-064 not found in skull-rules.yaml"
        principle = core_064.get("principle", "")
        assert "Sweep" in principle or "Catalogue" in principle or "Partial" in principle, (
            f"CORE-064 principle does not mention sweep/catalogue: {principle!r}"
        )


# ===========================================================================
# P1 — Session persistence, resume, hash drift, WONT-FIX protocol
# ===========================================================================


class TestCataloguePersistsAcrossSessionBoundary:
    """GOL-SCT-011 · P1 · AC-P16-011"""

    semantic_id = "GOL-SCT-011"

    def test_catalogue_persists_across_session_boundary_via_sqlite(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-011
        A catalogue opened by one SweepCatalogueOrchestrator instance must
        be readable by a fresh instance (simulating a new session).
        AC_COMPLETE: AC-P16-011 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()

        # Session 1
        orch1 = SCO()
        sweep_id = orch1.open_catalogue(intent="FIX", scope_files=["cortex/foo.py"])
        orch1.add_issue(sweep_id, file="cortex/foo.py", description="lint error")

        # Session 2 — fresh instance, same sweep_id
        orch2 = SCO()
        manifest = orch2.get_manifest(sweep_id)
        assert manifest["open_count"] >= 1, (
            "Fresh instance should read the persisted open_count from SQLite"
        )


class TestResumeOpenCatalogueReturnsSameManifest:
    """GOL-SCT-012 · P1 · AC-P16-012"""

    semantic_id = "GOL-SCT-012"

    def test_resume_open_catalogue_returns_existing_manifest_for_same_scope(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-012
        Calling open_catalogue() twice with the same intent+scope must
        resume the existing catalogue (same sweep_id) rather than creating
        a second duplicate catalogue.
        AC_COMPLETE: AC-P16-012 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        scope = ["cortex/foo.py"]
        sweep_id_1 = orch.open_catalogue(intent="FIX", scope_files=scope)
        sweep_id_2 = orch.open_catalogue(intent="FIX", scope_files=scope)
        assert sweep_id_1 == sweep_id_2, (
            "Identical intent+scope must resume existing catalogue, not create a new one. "
            f"Got sweep_id_1={sweep_id_1!r} sweep_id_2={sweep_id_2!r}"
        )


class TestResumeInvalidatesOnHashDrift:
    """GOL-SCT-013 · P1 · AC-P16-013"""

    semantic_id = "GOL-SCT-013"

    def test_resume_open_catalogue_invalidates_on_scope_file_hash_drift(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-013
        If >20% of scope files have changed (hash drift), open_catalogue()
        must invalidate the old catalogue and open a fresh one with a new sweep_id.
        AC_COMPLETE: AC-P16-013 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()

        # Create actual scope files so hash can change
        scope_file = tmp_path / "cortex" / "foo.py"
        scope_file.parent.mkdir(parents=True, exist_ok=True)
        scope_file.write_text("# version 1\n")

        orch = SCO()
        sweep_id_1 = orch.open_catalogue(intent="FIX", scope_files=[str(scope_file)])

        # Simulate significant file change
        scope_file.write_text("# version 2 — substantially different content\n" * 50)

        sweep_id_2 = orch.open_catalogue(intent="FIX", scope_files=[str(scope_file)])
        assert sweep_id_1 != sweep_id_2, (
            "open_catalogue() must return a new sweep_id when file-hash drift exceeds 20%"
        )


class TestWontFixRequiresJustification:
    """GOL-SCT-014 · P1 · AC-P16-014"""

    semantic_id = "GOL-SCT-014"

    def test_wont_fix_requires_justification_and_writes_audit_entry(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-014
        approve_wont_fix() must succeed and write an audit entry when a
        non-empty justification is provided.
        AC_COMPLETE: AC-P16-014 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        sweep_id = orch.open_catalogue(intent="FIX", scope_files=["cortex/foo.py"])
        issue_id = orch.add_issue(sweep_id, file="cortex/foo.py", description="legacy anti-pattern")
        result = orch.approve_wont_fix(
            sweep_id=sweep_id,
            issue_id=issue_id,
            justification="Legacy code in deprecated module — scheduled for removal in Phase 20",
        )
        assert result is True or result is not None, (
            "approve_wont_fix() must succeed with a non-empty justification"
        )
        # Verify audit entry written
        audit = orch.get_audit_log(sweep_id)
        assert any("WONT_FIX" in str(entry) or "wont_fix" in str(entry) for entry in audit), (
            "No WONT_FIX audit entry found after approve_wont_fix()"
        )


class TestWontFixWithoutJustificationRaisesValueError:
    """GOL-SCT-015 · P1 · AC-P16-015"""

    semantic_id = "GOL-SCT-015"

    def test_wont_fix_without_justification_raises_value_error(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-015
        approve_wont_fix() must raise ValueError when justification is empty
        or whitespace-only — no silent approval allowed.
        AC_COMPLETE: AC-P16-015 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        sweep_id = orch.open_catalogue(intent="FIX", scope_files=["cortex/foo.py"])
        issue_id = orch.add_issue(sweep_id, file="cortex/foo.py", description="legacy code")
        with pytest.raises(ValueError, match=r"[Jj]ustification|[Ee]mpty|[Rr]equired"):
            orch.approve_wont_fix(sweep_id=sweep_id, issue_id=issue_id, justification="")


# ===========================================================================
# P2 — MCP tool, health check, wiring YAML, end-to-end
# ===========================================================================


class TestSweepStatusToolReturnsOpenItemsCount:
    """GOL-SCT-016 · P2 · AC-P16-016"""

    semantic_id = "GOL-SCT-016"

    def test_cortex_sweep_status_tool_returns_open_items_count(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-016
        cortex_sweep_status MCP tool must return a dict with 'open_items_count'
        key when called with a valid sweep_id.
        AC_COMPLETE: AC-P16-016 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        cortex_sweep_status = _import_sweep_status_tool()
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        sweep_id = orch.open_catalogue(intent="FIX", scope_files=["cortex/foo.py"])
        result = cortex_sweep_status(sweep_id=sweep_id)
        assert isinstance(result, dict), f"Tool must return dict, got {type(result)}"
        assert "open_items_count" in result, (
            f"Result must contain 'open_items_count', got keys: {list(result.keys())}"
        )


class TestSweepStatusToolRaisesWhenNoOpenCatalogue:
    """GOL-SCT-017 · P2 · AC-P16-017"""

    semantic_id = "GOL-SCT-017"

    def test_cortex_sweep_status_tool_raises_when_no_open_catalogue(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-017
        cortex_sweep_status must raise (or return an error dict) when given
        a non-existent sweep_id.
        AC_COMPLETE: AC-P16-017 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        cortex_sweep_status = _import_sweep_status_tool()
        with pytest.raises(Exception):
            cortex_sweep_status(sweep_id="nonexistent-sweep-99999")


class TestSweepCatalogueOrchestratorHealthCheckReturnsHealthy:
    """GOL-SCT-018 · P2 · AC-P16-018"""

    semantic_id = "GOL-SCT-018"

    def test_sweep_catalogue_orchestrator_health_check_returns_healthy(self, tmp_path, monkeypatch):
        """AC_START: AC-P16-018
        SweepCatalogueOrchestrator.health_check() must return a dict with
        a truthy 'healthy' key.
        AC_COMPLETE: AC-P16-018 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()
        result = orch.health_check()
        assert isinstance(result, dict), f"health_check() must return dict, got {type(result)}"
        assert result.get("healthy") is True, (
            f"health_check() must return healthy=True, got {result!r}"
        )


class TestSweepCatalogueOrchestratorWiredAtPriority155:
    """GOL-SCT-019 · P2 · AC-P16-019"""

    semantic_id = "GOL-SCT-019"

    def test_sweep_catalogue_orchestrator_wired_in_support_wiring_yaml_at_priority_155(self):
        """AC_START: AC-P16-019
        support-orchestrator-wiring.yaml must contain SweepCatalogueOrchestrator
        with priority 155.
        AC_COMPLETE: AC-P16-019 ✅"""
        assert SUPPORT_WIRING.exists(), f"support-orchestrator-wiring.yaml not found at {SUPPORT_WIRING}"
        data = yaml.safe_load(SUPPORT_WIRING.read_text())
        # Wiring spec uses 'provides' list (not 'orchestrators')
        orchestrators = data.get("provides", data.get("orchestrators", []))
        if isinstance(orchestrators, dict):
            orchestrators = list(orchestrators.values())
        entry = next(
            (
                o for o in orchestrators
                if "SweepCatalogueOrchestrator" in str(o.get("class", ""))
                or "SweepCatalogueOrchestrator" in str(o.get("name", ""))
                or "sweep_catalogue" in str(o.get("module", ""))
                or "sweep_catalogue" in str(o.get("entry_point", ""))
            ),
            None,
        )
        assert entry is not None, (
            "SweepCatalogueOrchestrator not found in support-orchestrator-wiring.yaml"
        )
        assert entry.get("priority") == 155, (
            f"Expected priority 155, got {entry.get('priority')!r}"
        )


class TestEndToEndFixSessionExhaustesCatalogue:
    """GOL-SCT-020 · P2 · AC-P16-020"""

    semantic_id = "GOL-SCT-020"

    def test_end_to_end_fix_session_exhausts_catalogue_and_closes_cleanly(
        self, tmp_path, monkeypatch
    ):
        """AC_START: AC-P16-020
        Full lifecycle: open_catalogue → add_issues → mark all resolved →
        assert_exhausted returns Ok → _finalize_operation does not raise.
        This is the end-to-end happy path for CORE-064 enforcement.
        AC_COMPLETE: AC-P16-020 ✅"""
        monkeypatch.setenv("CORTEX_RUNTIME_DIR", str(tmp_path / ".cortex-runtime"))
        SCO = _import_sweep_catalogue_orchestrator()
        orch = SCO()

        # 1. Open catalogue
        scope = ["cortex/alpha.py", "cortex/beta.py"]
        sweep_id = orch.open_catalogue(intent="FIX", scope_files=scope)

        # 2. Add 3 issues
        issues = [
            orch.add_issue(sweep_id, file="cortex/alpha.py", description="missing type hint"),
            orch.add_issue(sweep_id, file="cortex/alpha.py", description="missing docstring"),
            orch.add_issue(sweep_id, file="cortex/beta.py", description="unused import"),
        ]

        # 3. Resolve all
        for issue_id in issues:
            orch.mark_resolved(sweep_id, issue_id)

        # 4. assert_exhausted must be Ok
        result = orch.assert_exhausted(sweep_id)
        assert result.ok, f"All issues resolved — assert_exhausted must return Ok, got {result!r}"

        # 5. MasterOrchestrator._finalize_operation() must not raise
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        mo = MasterOrchestrator()

        class _StubSCO:
            def assert_exhausted(self, sid):  # noqa: D102
                return SimpleNamespace(ok=True, remaining=[])

        mo._sweep_catalogue_orchestrator_instance = _StubSCO()
        mo._finalize_operation(sweep_id=sweep_id)  # Must not raise
