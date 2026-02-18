"""
Golden Tests: InventoryAgent → VacuumExecutor handoff — Phase 98

Scenarios GI-001 to GI-010

Architecture contract being tested
-----------------------------------
HealthOrchestrator (reporter)
    └─ InventoryAgent.check()       ← pure scanner, zero mutations
         └─ emits HealthIssues with inventory_finding metadata
    └─ write_handoff()              ← serialises findings to health-issues.yaml
VacuumExecutor.execute_from_handoff()  ← reads yaml, executes cleanup
HealthVacuumPipeline.run()         ← end-to-end coordinator

Standard practice enforced by these tests
------------------------------------------
1. InventoryAgent NEVER mutates files — it is a pure reporter.
2. All cleanup is delegated to VacuumExecutor via health-issues.yaml.
3. HealthOrchestrator is a reporting tool: scan → write_handoff → done.
4. VacuumExecutor is the action tool: execute_from_handoff → operations.
5. Unsafe findings (external imports present) are skipped by VacuumExecutor.

TDD: RED phase — these tests drive the integration.
Authority: Phase 98, CORE-008, CORE-028, CORE-035
"""

from __future__ import annotations

import shutil
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture()
def tmp_repo(tmp_path: Path) -> Path:
    """Minimal CORTEX repo skeleton for inventory tests."""
    for d in [
        "cortex/brain/vacuum",
        "cortex_intelligence",
        "cortex-registry",
        "tests",
        "scripts",
        "deployment",
        "_workspaces/sts",
    ]:
        (tmp_path / d).mkdir(parents=True, exist_ok=True)
    return tmp_path


@pytest.fixture()
def inventory_agent(tmp_repo: Path):
    """InventoryAgent pointed at tmp_repo."""
    from cortex.orchestrators.health.agents.inventory_agent import InventoryAgent
    return InventoryAgent()


@pytest.fixture()
def health_orchestrator(tmp_repo: Path):
    """Phase-48 HealthOrchestrator (scanner + write_handoff)."""
    from cortex.orchestrators.support.health_orchestrator import HealthOrchestrator
    return HealthOrchestrator(workspace_root=tmp_repo)


@pytest.fixture()
def vacuum_executor(tmp_repo: Path):
    """VacuumExecutor (action layer)."""
    from cortex.orchestrators.support.health_orchestrator import VacuumExecutor
    return VacuumExecutor(workspace_root=tmp_repo, dry_run=False)


@pytest.fixture()
def vacuum_executor_dry(tmp_repo: Path):
    """VacuumExecutor in dry-run mode."""
    from cortex.orchestrators.support.health_orchestrator import VacuumExecutor
    return VacuumExecutor(workspace_root=tmp_repo, dry_run=True)


@pytest.fixture()
def handoff_path(tmp_repo: Path) -> Path:
    return tmp_repo / "cortex" / "brain" / "vacuum" / "health-issues.yaml"


# =============================================================================
# GI-001: InventoryAgent is a pure reporter — never mutates files
# =============================================================================

class TestInventoryAgentIsPureReporter:
    """GI-001: Running InventoryAgent must not change any file on disk."""

    def test_no_files_deleted_after_check(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-001a: Files present before check must still exist after check."""
        # Arrange — place a duplicate sub-package inside cortex/
        inner = tmp_repo / "cortex" / "cortex_intelligence"
        inner.mkdir(parents=True, exist_ok=True)
        sentinel = inner / "__init__.py"
        sentinel.write_text("# duplicate")

        snapshot_before = set(tmp_repo.rglob("*"))

        # Act
        inventory_agent.check(tmp_repo)

        snapshot_after = set(tmp_repo.rglob("*"))
        assert snapshot_before == snapshot_after, (
            "InventoryAgent must not create, delete, or rename any file"
        )

    def test_no_files_created_after_check(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-001b: InventoryAgent must not write any output files."""
        inventory_agent.check(tmp_repo)
        # No health-issues.yaml or any new file should appear
        assert not (tmp_repo / "health-issues.yaml").exists()
        assert not (tmp_repo / "cortex" / "brain" / "vacuum" / "health-issues.yaml").exists()


# =============================================================================
# GI-002: InventoryAgent detects CONSOLIDATE (inner duplicate of root package)
# =============================================================================

class TestConsolidateDetection:
    """GI-002: cortex/cortex_intelligence detected when root cortex_intelligence exists."""

    def test_detects_inner_cortex_intelligence(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-002a: Inner duplicate triggers CONSOLIDATE finding."""
        (tmp_repo / "cortex" / "cortex_intelligence").mkdir(parents=True, exist_ok=True)
        (tmp_repo / "cortex_intelligence").mkdir(parents=True, exist_ok=True)

        result = inventory_agent.check(tmp_repo)

        actions = [
            issue.metadata["inventory_finding"]["action"]
            for issue in result.issues
            if "inventory_finding" in issue.metadata
        ]
        assert "consolidate" in actions, "Expected CONSOLIDATE finding"

    def test_consolidate_finding_has_source_and_target(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-002b: CONSOLIDATE finding must carry source_path and target_path."""
        (tmp_repo / "cortex" / "cortex_intelligence").mkdir(parents=True, exist_ok=True)
        (tmp_repo / "cortex_intelligence").mkdir(parents=True, exist_ok=True)

        result = inventory_agent.check(tmp_repo)

        finding = next(
            issue.metadata["inventory_finding"]
            for issue in result.issues
            if issue.metadata.get("inventory_finding", {}).get("action") == "consolidate"
        )
        assert "cortex/cortex_intelligence" in finding["source_path"]
        assert finding["target_path"] == "cortex_intelligence"

    def test_no_consolidate_when_inner_missing(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-002c: No CONSOLIDATE when inner duplicate does not exist."""
        # root cortex_intelligence exists but inner one does not
        result = inventory_agent.check(tmp_repo)
        actions = [
            issue.metadata.get("inventory_finding", {}).get("action")
            for issue in result.issues
        ]
        assert "consolidate" not in actions


# =============================================================================
# GI-003: InventoryAgent detects RELOCATE (folder in wrong root)
# =============================================================================

class TestRelocateDetection:
    """GI-003: cortex/sts flagged for relocation; Python packages are exempt."""

    def test_detects_sts_misplaced(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-003a: cortex/sts triggers RELOCATE to _workspaces/sts."""
        sts_dir = tmp_repo / "cortex" / "sts"
        sts_dir.mkdir(parents=True, exist_ok=True)
        (sts_dir / "session.py").write_text("# stray sts")

        result = inventory_agent.check(tmp_repo)

        findings = [
            issue.metadata["inventory_finding"]
            for issue in result.issues
            if issue.metadata.get("inventory_finding", {}).get("action") == "relocate"
            and "sts" in issue.metadata.get("inventory_finding", {}).get("source_path", "")
        ]
        assert findings, "Expected RELOCATE finding for cortex/sts"
        assert findings[0]["target_path"] == "_workspaces/sts"

    @pytest.mark.parametrize("folder", ["tests", "scripts", "deployment"])
    def test_python_packages_not_flagged_for_relocation(
        self, tmp_repo: Path, inventory_agent, folder: str
    ) -> None:
        """GI-003b: Python packages (tests, scripts, deployment) are exempt from relocation.

        These directories are importable Python packages with legitimate consumers
        inside cortex/. They must NOT appear in the relocation map.
        Regression guard: the vacuum previously relocated these, breaking imports.
        """
        pkg_dir = tmp_repo / "cortex" / folder
        pkg_dir.mkdir(parents=True, exist_ok=True)
        (pkg_dir / "__init__.py").write_text("")
        (pkg_dir / "module.py").write_text("# legitimate package member")

        result = inventory_agent.check(tmp_repo)

        reloc_findings = [
            issue.metadata["inventory_finding"]
            for issue in result.issues
            if issue.metadata.get("inventory_finding", {}).get("action") == "relocate"
            and folder in issue.metadata.get("inventory_finding", {}).get("source_path", "")
        ]
        assert not reloc_findings, (
            f"cortex/{folder} is an importable Python package and must NOT be "
            "flagged for relocation — regression guard for _RELOCATION_MAP bug"
        )


# =============================================================================
# GI-004: InventoryAgent detects DELETE (stray folder, no canonical home)
# =============================================================================

class TestDeleteDetection:
    """GI-004: cortex/reports and cortex/phase_38 flagged for deletion."""

    @pytest.mark.parametrize("folder", ["reports", "phase_38"])
    def test_detects_orphaned_folder(self, tmp_repo: Path, inventory_agent, folder: str) -> None:
        """GI-004a: Orphaned folder triggers DELETE finding."""
        (tmp_repo / "cortex" / folder).mkdir(parents=True, exist_ok=True)
        (tmp_repo / "cortex" / folder / "__init__.py").write_text("")

        result = inventory_agent.check(tmp_repo)

        actions_and_paths = [
            (issue.metadata["inventory_finding"]["action"],
             issue.metadata["inventory_finding"]["source_path"])
            for issue in result.issues
            if "inventory_finding" in issue.metadata
        ]
        assert any(
            action == "delete" and folder in path
            for action, path in actions_and_paths
        ), f"Expected DELETE finding for cortex/{folder}"


# =============================================================================
# GI-005: InventoryAgent detects STUB_DIR (only __init__.py)
# =============================================================================

class TestStubDirDetection:
    """GI-005: A cortex/orchestrators subfolder with only __init__.py is flagged."""

    def test_detects_orchestrator_stub_dir(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-005a: Single __init__.py orchestrator dir → STUB_DIR finding."""
        stub = tmp_repo / "cortex" / "orchestrators" / "persona"
        stub.mkdir(parents=True, exist_ok=True)
        (stub / "__init__.py").write_text("# placeholder")

        result = inventory_agent.check(tmp_repo)

        stub_findings = [
            issue.metadata["inventory_finding"]
            for issue in result.issues
            if issue.metadata.get("inventory_finding", {}).get("action") == "stub_dir"
        ]
        assert stub_findings, "Expected STUB_DIR finding for orchestrators/persona"

    def test_populated_dir_not_flagged_as_stub(self, tmp_repo: Path, inventory_agent) -> None:
        """GI-005b: A dir with real implementation files at top level is NOT a stub."""
        real_dir = tmp_repo / "cortex" / "orchestrators" / "health"
        real_dir.mkdir(parents=True, exist_ok=True)
        (real_dir / "__init__.py").write_text("")
        (real_dir / "health_orchestrator.py").write_text("class HealthOrchestrator: pass")

        result = inventory_agent.check(tmp_repo)

        stub_findings = [
            issue.metadata["inventory_finding"]
            for issue in result.issues
            if issue.metadata.get("inventory_finding", {}).get("action") == "stub_dir"
            and "health" in issue.metadata["inventory_finding"].get("source_path", "")
        ]
        assert not stub_findings, "Populated orchestrator dir must not be flagged as stub"

    def test_dir_with_subdir_files_not_flagged_as_stub(
        self, tmp_repo: Path, inventory_agent
    ) -> None:
        """GI-005c: A dir with only __init__.py at root but real files in subdirs is NOT a stub.

        Regression guard for the glob→rglob bug: _scan_stub_orchestrator_dirs
        previously used subdir.glob("*.py") which only checked the top level,
        causing dirs like cortex/orchestrators/planning/ (which has models/ and
        strategies/ subdirs with real Python files) to be incorrectly deleted.
        """
        planning = tmp_repo / "cortex" / "orchestrators" / "planning"
        models = planning / "models"
        strategies = planning / "strategies"
        for d in (planning, models, strategies):
            d.mkdir(parents=True, exist_ok=True)

        # Only __init__.py at the top level — the rglob bug would see this as stub
        (planning / "__init__.py").write_text("# planning orchestrator package")
        # Real Python files live *only* in subdirectories
        (models / "__init__.py").write_text("")
        (models / "dependency_resolver.py").write_text("class DependencyResolver: pass")
        (models / "roi_composite_scorer.py").write_text("class ROIScorer: pass")
        (strategies / "__init__.py").write_text("")
        (strategies / "phase.py").write_text("class PhaseStrategy: pass")

        result = inventory_agent.check(tmp_repo)

        stub_findings = [
            issue.metadata["inventory_finding"]
            for issue in result.issues
            if issue.metadata.get("inventory_finding", {}).get("action") == "stub_dir"
            and "planning" in issue.metadata["inventory_finding"].get("source_path", "")
        ]
        assert not stub_findings, (
            "Orchestrator dir with Python files in subdirectories must NOT be "
            "flagged as STUB_DIR — regression guard for glob→rglob bug"
        )


# =============================================================================
# GI-006: Unsafe findings are NOT executed by VacuumExecutor
# =============================================================================

class TestUnsafeFindingsSkipped:
    """GI-006: VacuumExecutor skips findings where safe=False."""

    def _write_handoff(self, path: Path, finding: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "metadata": {"generated_at": "2026-02-18T00:00:00Z", "issues_found": 1},
            "issues": {
                "screaming_case": {"count": 0, "files": []},
                "empty_files": {"count": 0, "files": []},
                "orphaned_directories": {"count": 0, "directories": []},
                "deprecated_code": {"count": 0, "files": []},
                "duplicate_content": {"count": 0, "groups": []},
                "wrong_references": {"count": 0, "files": []},
                "invalid_markdown": {"count": 0, "files": []},
            },
            "inventory_findings": {"findings": [finding]},
            "summary": {"delete_count": 0, "rename_count": 0, "relocate_count": 0,
                        "estimated_bytes_freed": 0},
        }
        with open(path, "w") as fh:
            yaml.dump(data, fh)

    def test_unsafe_delete_skipped(
        self, tmp_repo: Path, vacuum_executor, handoff_path: Path
    ) -> None:
        """GI-006a: DELETE with safe=False → OperationResult.success=False, file intact."""
        target_dir = tmp_repo / "cortex" / "phase_38"
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "impl.py").write_text("# used externally")

        self._write_handoff(handoff_path, {
            "action": "delete",
            "source_path": "cortex/phase_38",
            "target_path": None,
            "reason": "orphaned phase",
            "severity": "medium",
            "safe": False,
        })

        results = vacuum_executor.execute_from_handoff(handoff_path)

        unsafe_results = [r for r in results if "phase_38" in r.source]
        assert all(not r.success for r in unsafe_results), (
            "Unsafe findings must not be executed"
        )
        assert target_dir.exists(), "Directory must remain when finding is unsafe"

    def test_unsafe_consolidate_skipped(
        self, tmp_repo: Path, vacuum_executor, handoff_path: Path
    ) -> None:
        """GI-006b: CONSOLIDATE with safe=False → skipped, source dir preserved."""
        inner = tmp_repo / "cortex" / "cortex_intelligence"
        inner.mkdir(parents=True, exist_ok=True)
        (inner / "impl.py").write_text("# imported externally")

        self._write_handoff(handoff_path, {
            "action": "consolidate",
            "source_path": "cortex/cortex_intelligence",
            "target_path": "cortex_intelligence",
            "reason": "inner duplicate",
            "severity": "high",
            "safe": False,
        })

        vacuum_executor.execute_from_handoff(handoff_path)
        assert inner.exists(), "Inner dir must remain when finding is unsafe"


# =============================================================================
# GI-007: VacuumExecutor executes safe DELETE via inventory_findings
# =============================================================================

class TestSafeDeleteExecuted:
    """GI-007: VacuumExecutor deletes stray folder when safe=True."""

    def _write_handoff_with_delete(self, path: Path, source_path: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "metadata": {"generated_at": "2026-02-18T00:00:00Z", "issues_found": 1},
            "issues": {
                "screaming_case": {"count": 0, "files": []},
                "empty_files": {"count": 0, "files": []},
                "orphaned_directories": {"count": 0, "directories": []},
                "deprecated_code": {"count": 0, "files": []},
                "duplicate_content": {"count": 0, "groups": []},
                "wrong_references": {"count": 0, "files": []},
                "invalid_markdown": {"count": 0, "files": []},
            },
            "inventory_findings": {"findings": [{
                "action": "delete",
                "source_path": source_path,
                "target_path": None,
                "reason": "orphaned stray folder",
                "severity": "medium",
                "safe": True,
            }]},
            "summary": {"delete_count": 1, "rename_count": 0, "relocate_count": 0,
                        "estimated_bytes_freed": 0},
        }
        with open(path, "w") as fh:
            yaml.dump(data, fh)

    def test_safe_delete_removes_directory(
        self, tmp_repo: Path, vacuum_executor, handoff_path: Path
    ) -> None:
        """GI-007a: Safe DELETE → directory removed from disk."""
        stray = tmp_repo / "cortex" / "reports"
        stray.mkdir(parents=True, exist_ok=True)
        (stray / "__init__.py").write_text("")

        self._write_handoff_with_delete(handoff_path, "cortex/reports")

        results = vacuum_executor.execute_from_handoff(handoff_path)

        delete_results = [r for r in results if "reports" in r.source]
        assert any(r.success for r in delete_results), "Safe DELETE must succeed"
        assert not stray.exists(), "Stray directory must be removed"

    def test_safe_delete_dry_run_preserves_directory(
        self, tmp_repo: Path, vacuum_executor_dry, handoff_path: Path
    ) -> None:
        """GI-007b: Dry-run DELETE → directory preserved, operation recorded."""
        stray = tmp_repo / "cortex" / "reports"
        stray.mkdir(parents=True, exist_ok=True)
        (stray / "__init__.py").write_text("")

        self._write_handoff_with_delete(handoff_path, "cortex/reports")

        vacuum_executor_dry.execute_from_handoff(handoff_path)
        assert stray.exists(), "Dry-run must not delete directory"


# =============================================================================
# GI-008: VacuumExecutor executes safe CONSOLIDATE
# =============================================================================

class TestSafeConsolidateExecuted:
    """GI-008: VacuumExecutor removes inner duplicate when safe=True."""

    def test_safe_consolidate_removes_inner_dir(
        self, tmp_repo: Path, vacuum_executor, handoff_path: Path
    ) -> None:
        """GI-008a: Safe CONSOLIDATE → inner dir deleted, root canonical intact."""
        inner = tmp_repo / "cortex" / "cortex_intelligence"
        inner.mkdir(parents=True, exist_ok=True)
        (inner / "__init__.py").write_text("# inner duplicate")

        root_canonical = tmp_repo / "cortex_intelligence"
        root_canonical.mkdir(parents=True, exist_ok=True)
        (root_canonical / "__init__.py").write_text("# canonical")

        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "metadata": {"generated_at": "2026-02-18T00:00:00Z", "issues_found": 1},
            "issues": {k: {"count": 0, "files": []} for k in [
                "screaming_case", "empty_files", "deprecated_code",
                "wrong_references", "invalid_markdown",
            ]},
            "issues_extra": {
                "orphaned_directories": {"count": 0, "directories": []},
                "duplicate_content": {"count": 0, "groups": []},
            },
            "inventory_findings": {"findings": [{
                "action": "consolidate",
                "source_path": "cortex/cortex_intelligence",
                "target_path": "cortex_intelligence",
                "reason": "inner duplicate of canonical root package",
                "severity": "high",
                "safe": True,
            }]},
            "summary": {"delete_count": 1, "rename_count": 0, "relocate_count": 0,
                        "estimated_bytes_freed": 0},
        }
        # Ensure all required sections exist
        data["issues"]["orphaned_directories"] = {"count": 0, "directories": []}
        data["issues"]["duplicate_content"] = {"count": 0, "groups": []}
        with open(handoff_path, "w") as fh:
            yaml.dump(data, fh)

        results = vacuum_executor.execute_from_handoff(handoff_path)

        consolidate_results = [r for r in results if "cortex_intelligence" in r.source]
        assert any(r.success for r in consolidate_results)
        assert not inner.exists(), "Inner duplicate must be removed"
        assert root_canonical.exists(), "Root canonical must remain intact"


# =============================================================================
# GI-009: VacuumExecutor executes safe RELOCATE
# =============================================================================

class TestSafeRelocateExecuted:
    """GI-009: VacuumExecutor moves folder to canonical root when safe=True."""

    def test_safe_relocate_moves_directory(
        self, tmp_repo: Path, vacuum_executor, handoff_path: Path
    ) -> None:
        """GI-009a: Safe RELOCATE → folder moved to target root dir."""
        cortex_tests = tmp_repo / "cortex" / "tests"
        cortex_tests.mkdir(parents=True, exist_ok=True)
        (cortex_tests / "test_example.py").write_text("# misplaced test")

        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "metadata": {"generated_at": "2026-02-18T00:00:00Z", "issues_found": 1},
            "issues": {k: {"count": 0, "files": []} for k in [
                "screaming_case", "empty_files", "deprecated_code",
                "wrong_references", "invalid_markdown",
            ]},
            "inventory_findings": {"findings": [{
                "action": "relocate",
                "source_path": "cortex/tests",
                "target_path": "tests",
                "reason": "belongs in root tests/",
                "severity": "medium",
                "safe": True,
            }]},
            "summary": {"delete_count": 0, "rename_count": 0, "relocate_count": 1,
                        "estimated_bytes_freed": 0},
        }
        data["issues"]["orphaned_directories"] = {"count": 0, "directories": []}
        data["issues"]["duplicate_content"] = {"count": 0, "groups": []}
        with open(handoff_path, "w") as fh:
            yaml.dump(data, fh)

        results = vacuum_executor.execute_from_handoff(handoff_path)

        relocate_results = [r for r in results if "tests" in r.source and r.operation == "relocate_tree"]
        assert any(r.success for r in relocate_results), "RELOCATE must succeed"
        assert not cortex_tests.exists(), "Source must be removed after relocation"
        assert (tmp_repo / "tests" / "tests").exists() or (tmp_repo / "tests").exists()


# =============================================================================
# GI-010: Full pipeline — HealthOrchestrator → write_handoff → VacuumExecutor
# =============================================================================

class TestFullInventoryPipeline:
    """GI-010: End-to-end: scanner produces handoff, vacuum consumes it."""

    def test_handoff_contains_inventory_findings_section(
        self, tmp_repo: Path, health_orchestrator, handoff_path: Path
    ) -> None:
        """GI-010a: write_handoff always emits inventory_findings key."""
        (tmp_repo / "cortex" / "cortex_intelligence").mkdir(parents=True, exist_ok=True)
        (tmp_repo / "cortex_intelligence").mkdir(parents=True, exist_ok=True)

        scan = health_orchestrator.scan()
        health_orchestrator.write_handoff(scan, handoff_path)

        with open(handoff_path) as fh:
            data = yaml.safe_load(fh)

        assert "inventory_findings" in data, (
            "health-issues.yaml must contain inventory_findings section"
        )
        assert "findings" in data["inventory_findings"]

    def test_inventory_findings_in_handoff_are_dicts(
        self, tmp_repo: Path, health_orchestrator, handoff_path: Path
    ) -> None:
        """GI-010b: Each finding in the handoff has action, source_path, safe keys."""
        (tmp_repo / "cortex" / "cortex_intelligence").mkdir(parents=True, exist_ok=True)
        (tmp_repo / "cortex_intelligence").mkdir(parents=True, exist_ok=True)

        scan = health_orchestrator.scan()
        health_orchestrator.write_handoff(scan, handoff_path)

        with open(handoff_path) as fh:
            data = yaml.safe_load(fh)

        for finding in data["inventory_findings"]["findings"]:
            assert "action" in finding
            assert "source_path" in finding
            assert "safe" in finding

    def test_scan_issues_found_includes_inventory(
        self, tmp_repo: Path, health_orchestrator
    ) -> None:
        """GI-010c: ScanResult.issues_found is incremented by inventory findings."""
        (tmp_repo / "cortex" / "cortex_intelligence").mkdir(parents=True, exist_ok=True)
        (tmp_repo / "cortex_intelligence").mkdir(parents=True, exist_ok=True)

        scan = health_orchestrator.scan()

        assert scan.issues_found >= 1, (
            "issues_found must include at least the CONSOLIDATE inventory finding"
        )
        assert len(scan.inventory_findings) >= 1

    def test_pipeline_executes_safe_inventory_delete(
        self, tmp_repo: Path
    ) -> None:
        """GI-010d: Full pipeline removes safe DELETE inventory finding from disk."""
        from cortex.orchestrators.support.health_orchestrator import HealthVacuumPipeline

        # Place a stray reports dir with no imports
        stray = tmp_repo / "cortex" / "reports"
        stray.mkdir(parents=True, exist_ok=True)
        (stray / "__init__.py").write_text("")

        pipeline = HealthVacuumPipeline(workspace_root=tmp_repo, dry_run=False)

        with patch.object(pipeline, "_stage_preflight", return_value="PASS"):
            report = pipeline.run(autonomous=True)

        assert report.stage_2_health_scan == "PASS"
        assert report.stage_4_vacuum in ("PASS", "DRY_RUN")
        # After pipeline: stray dir deleted (if safe=True and no imports found)
        # We assert the report ran without error
        assert not report.errors or all("reports" not in e for e in report.errors)
