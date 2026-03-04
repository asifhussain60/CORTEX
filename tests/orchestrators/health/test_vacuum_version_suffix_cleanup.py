"""
TDD tests for VacuumOrchestrator version suffix cleanup — Phase 121 Sub-phase E.

Authority: CORE-008 (TDD mandatory — RED before GREEN).
All tests written BEFORE implementation.
"""
import tempfile
from pathlib import Path

import pytest
import yaml

from cortex.orchestrators.health.vacuum_orchestrator import VacuumOrchestrator


# ─────────────────────────────────────────────────────────────────────────────
# Fixtures
# ─────────────────────────────────────────────────────────────────────────────


@pytest.fixture()
def repo_with_versioned_files(tmp_path: Path) -> Path:
    """Workspace containing _v2/_v3 versioned filenames."""
    (tmp_path / "module_v2.py").write_text("# old version\n")
    (tmp_path / "report_v3.yaml").write_text("version: 3\n")
    (tmp_path / "clean_module.py").write_text("# clean\n")
    return tmp_path


@pytest.fixture()
def repo_with_git_venv(tmp_path: Path) -> Path:
    """Workspace containing versioned files inside .git and .venv — must be excluded."""
    git_dir = tmp_path / ".git"
    git_dir.mkdir()
    (git_dir / "object_v2.py").write_text("# git internal\n")
    venv_dir = tmp_path / ".venv" / "lib"
    venv_dir.mkdir(parents=True)
    (venv_dir / "lib_v3.py").write_text("# venv lib\n")
    pycache = tmp_path / "__pycache__"
    pycache.mkdir()
    (pycache / "compiled_v2.pyc").write_text("")
    return tmp_path


@pytest.fixture()
def repo_with_semantic_version(tmp_path: Path) -> Path:
    """Workspace where schema_version='1.0.0' in content — NOT a violation."""
    f = tmp_path / "config.yaml"
    f.write_text("schema_version: '1.0.0'\nname: service\n")
    return tmp_path


@pytest.fixture()
def repo_with_s_numbered_tests(tmp_path: Path) -> Path:
    """Workspace with _s1.py _s2.py sub-step test markers — NOT violations."""
    (tmp_path / "test_workflow_s1.py").write_text("# sub-step 1\n")
    (tmp_path / "test_workflow_s2.py").write_text("# sub-step 2\n")
    return tmp_path


@pytest.fixture()
def repo_with_v3_content(tmp_path: Path) -> Path:
    """Workspace where file content references a versioned tool name."""
    (tmp_path / "workflow.yaml").write_text(
        "tool: cortex_onboard_repository_v3\nstep: analyze\n"
    )
    return tmp_path


@pytest.fixture()
def vacuum(tmp_path: Path) -> VacuumOrchestrator:
    return VacuumOrchestrator(workspace_root=tmp_path)


# ─────────────────────────────────────────────────────────────────────────────
# Tests
# ─────────────────────────────────────────────────────────────────────────────


class TestVacuumVersionSuffixDetection:
    """GAP-121-13: VacuumOrchestrator detects version suffix violations."""

    def test_vacuum_detects_versioned_filenames(self, tmp_path: Path) -> None:
        repo = tmp_path / "workspace"
        repo.mkdir()
        (repo / "module_v2.py").write_text("# v2\n")
        vacuum = VacuumOrchestrator(workspace_root=repo)
        results = vacuum.run_version_suffix_cleanup(dry_run=True)
        # Detection works — at least one result planned for rename
        assert len(results) >= 1

    def test_vacuum_excludes_git_venv(
        self, repo_with_git_venv: Path
    ) -> None:
        vacuum = VacuumOrchestrator(workspace_root=repo_with_git_venv)
        results = vacuum.run_version_suffix_cleanup(dry_run=True)
        # Nothing flagged (all versioned files are in .git/.venv/__pycache__)
        assert len(results) == 0

    def test_vacuum_excludes_semantic_versions(
        self, repo_with_semantic_version: Path
    ) -> None:
        vacuum = VacuumOrchestrator(workspace_root=repo_with_semantic_version)
        results = vacuum.run_version_suffix_cleanup(dry_run=True)
        # config.yaml has no _v[N] in filename — must not be flagged
        assert len(results) == 0

    def test_vacuum_excludes_s_numbered_tests(
        self, repo_with_s_numbered_tests: Path
    ) -> None:
        vacuum = VacuumOrchestrator(workspace_root=repo_with_s_numbered_tests)
        results = vacuum.run_version_suffix_cleanup(dry_run=True)
        # _s1.py/_s2.py are sub-step markers, not version suffixes
        assert len(results) == 0

    def test_vacuum_plans_rename_operations(
        self, repo_with_versioned_files: Path
    ) -> None:
        vacuum = VacuumOrchestrator(workspace_root=repo_with_versioned_files)
        results = vacuum.run_version_suffix_cleanup(dry_run=True)
        assert len(results) >= 2  # module_v2 and report_v3

    def test_vacuum_dry_run_no_rename(
        self, repo_with_versioned_files: Path
    ) -> None:
        vacuum = VacuumOrchestrator(workspace_root=repo_with_versioned_files)
        vacuum.run_version_suffix_cleanup(dry_run=True)
        # Original versioned files still exist — dry_run must not rename
        assert (repo_with_versioned_files / "module_v2.py").exists()
        assert (repo_with_versioned_files / "report_v3.yaml").exists()

    def test_vacuum_renames_file(
        self, repo_with_versioned_files: Path
    ) -> None:
        vacuum = VacuumOrchestrator(workspace_root=repo_with_versioned_files)
        vacuum.run_version_suffix_cleanup(dry_run=False)
        # Versioned file should be renamed
        assert not (repo_with_versioned_files / "module_v2.py").exists()
        assert (repo_with_versioned_files / "module.py").exists()


class TestCWideVersionSuffixAssertions:
    """GAP-121-10/11: Codebase-wide zero-violation assertions."""

    def test_no_versioned_filenames_in_codebase(self) -> None:
        """All _v[N] versioned filenames must be eliminated (excluding .git/.venv/__pycache__)."""
        workspace = Path(__file__).parent.parent.parent.parent
        violations = []
        import re
        pattern = re.compile(r"_v\d+\.", re.IGNORECASE)
        for f in workspace.rglob("*"):
            if not f.is_file():
                continue
            parts = f.parts
            if any(p in {".git", ".venv", "__pycache__", "node_modules"} for p in parts):
                continue
            # Exclude the phase-121 plan file itself (documents violations, not a violation)
            if "phase-121" in str(f):
                continue
            if pattern.search(f.name):
                violations.append(str(f.relative_to(workspace)))
        assert violations == [], (
            f"Found {len(violations)} file(s) with _v[N] version suffixes:\n"
            + "\n".join(violations)
        )

    def test_no_v3_tool_references(self) -> None:
        """cortex_onboard_repository_v3 must be replaced everywhere."""
        workspace = Path(__file__).parent.parent.parent.parent
        refs = []
        for f in workspace.rglob("*"):
            if not f.is_file():
                continue
            parts = f.parts
            if any(p in {".git", ".venv", "__pycache__"} for p in parts):
                continue
            if f.suffix not in {".py", ".yaml", ".yml", ".md", ".json"}:
                continue
            # Exclude the phase-121 plan file itself and historical completed plans
            if "phase-121" in str(f):
                continue
            # Exclude completed phase plans (historical references only)
            if "planning/phases/completed/" in str(f):
                continue
            # Exclude _cortex-master mirror directory
            if "_cortex-master" in str(f):
                continue
            # Exclude meta-auditor deprecation notice (documents removed tools, not active use)
            if "cortex-meta-auditor.md" in str(f):
                continue
            # Exclude this test file itself (contains fixture with v3 string for test purposes)
            if f.name == "test_vacuum_version_suffix_cleanup.py":
                continue
            # Exclude cortex-master.yaml historical notes (archive record, not active code)
            if f.name == "cortex-master.yaml":
                continue
            try:
                if "cortex_onboard_repository_v3" in f.read_text(encoding="utf-8", errors="ignore"):
                    refs.append(str(f.relative_to(workspace)))
            except OSError:
                continue
        assert refs == [], (
            f"Found {len(refs)} file(s) still referencing cortex_onboard_repository_v3:\n"
            + "\n".join(refs)
        )


class TestVacuumWorkflowYaml:
    """GAP-121-13: vacuum-workflow.yaml must have version_suffix_cleanup stage."""

    def test_vacuum_workflow_has_version_suffix_stage(self) -> None:
        wf_path = (
            Path(__file__).parent.parent.parent.parent
            / "cortex-registry"
            / "workflows"
            / "templates"
            / "maintenance"
            / "vacuum-workflow.yaml"
        )
        assert wf_path.exists(), "vacuum-workflow.yaml must exist"
        data = yaml.safe_load(wf_path.read_text())
        wf = data.get("workflow", data)
        steps = wf.get("steps", [])
        step_ids = [s.get("id", "") for s in steps]
        assert "version_suffix_cleanup" in step_ids, (
            "vacuum-workflow.yaml must have a 'version_suffix_cleanup' step. "
            "Add it per GAP-121-13."
        )
