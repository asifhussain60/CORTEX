"""
Tests for RefactoringOrchestrator.check_dual_structure — ENH-STS-08 / CORE-035.

Root cause: PB-STS-001 Run 1 committed two incompatible backend layouts into
Refactored/backend/ (flat files + src/ multi-project), violating CORE-035.
This gate detects that pattern and blocks commit before it reaches the repo.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: ENH-STS-08-TESTS
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from cortex.orchestrators.domain.refactoring_orchestrator import RefactoringOrchestrator


# ── Fixtures ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def orchestrator() -> RefactoringOrchestrator:
    """Return a RefactoringOrchestrator instance."""
    return RefactoringOrchestrator()


@pytest.fixture()
def clean_src_layout(tmp_path: Path) -> Path:
    """Canonical multi-project layout: .sln references src/ only — no flat files."""
    sln_content = textwrap.dedent("""\
        Microsoft Visual Studio Solution File, Format Version 12.00
        Project("{FAE04EC0}") = "API", "src\\API\\API.csproj", "{GUID-1}"
        EndProject
        Project("{FAE04EC0}") = "Domain", "src\\Domain\\Domain.csproj", "{GUID-2}"
        EndProject
    """)
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "MyApp.sln").write_text(sln_content)
    # Create src/ hierarchy
    src_api = backend / "src" / "API"
    src_api.mkdir(parents=True)
    (src_api / "API.csproj").write_text("<Project />")
    src_domain = backend / "src" / "Domain"
    src_domain.mkdir(parents=True)
    (src_domain / "Domain.csproj").write_text("<Project />")
    # tests/ is acceptable at the same level as .sln
    tests = backend / "tests"
    tests.mkdir()
    (tests / "Tests.csproj").write_text("<Project />")
    return backend


@pytest.fixture()
def dual_layout(tmp_path: Path) -> Path:
    """Dual-structure layout: .sln references src/ BUT flat domain dirs also exist."""
    sln_content = textwrap.dedent("""\
        Microsoft Visual Studio Solution File, Format Version 12.00
        Project("{FAE04EC0}") = "API", "src\\API\\API.csproj", "{GUID-1}"
        EndProject
        Project("{FAE04EC0}") = "Domain", "src\\Domain\\Domain.csproj", "{GUID-2}"
        EndProject
    """)
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "MyApp.sln").write_text(sln_content)
    (backend / "MyApp.csproj").write_text("<Project />")  # flat project file — orphan
    # Flat C# sources alongside the .sln
    (backend / "Program.cs").write_text("// flat Program.cs")
    (backend / "appsettings.json").write_text("{}")
    # Flat domain directories duplicating src/ (the trigger)
    for d in ("Api", "Application", "Domain", "Infrastructure"):
        flat_d = backend / d
        flat_d.mkdir()
        (flat_d / f"{d}Service.cs").write_text(f"// flat {d}")
    # Also create the .sln-referenced src/ hierarchy
    for d in ("API", "Domain"):
        p = backend / "src" / d
        p.mkdir(parents=True)
        (p / f"{d}.csproj").write_text("<Project />")
    return backend


@pytest.fixture()
def flat_only_layout(tmp_path: Path) -> Path:
    """Single flat layout: .sln references top-level project with no src/ hierarchy."""
    sln_content = textwrap.dedent("""\
        Microsoft Visual Studio Solution File, Format Version 12.00
        Project("{FAE04EC0}") = "MyApp", "MyApp.csproj", "{GUID-1}"
        EndProject
    """)
    backend = tmp_path / "backend"
    backend.mkdir()
    (backend / "MyApp.sln").write_text(sln_content)
    (backend / "MyApp.csproj").write_text("<Project />")
    (backend / "Program.cs").write_text("// single flat project")
    return backend


# ── Tests: target_root validation ─────────────────────────────────────────────

class TestDualStructureGateInputValidation:
    """Gate rejects invalid target paths immediately."""

    def test_returns_err_when_path_does_not_exist(self, orchestrator: RefactoringOrchestrator) -> None:
        result = orchestrator.check_dual_structure(Path("/nonexistent/path/xyz"))
        assert result.is_err(), "Expected Err for non-existent path"

    def test_returns_err_when_path_is_file(
        self, orchestrator: RefactoringOrchestrator, tmp_path: Path
    ) -> None:
        f = tmp_path / "file.txt"
        f.write_text("hello")
        result = orchestrator.check_dual_structure(f)
        assert result.is_err(), "Expected Err when target_root is a file"

    def test_returns_ok_for_empty_directory(
        self, orchestrator: RefactoringOrchestrator, tmp_path: Path
    ) -> None:
        result = orchestrator.check_dual_structure(tmp_path)
        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is True
        assert report["violation_count"] == 0


# ── Tests: clean layouts ───────────────────────────────────────────────────────

class TestDualStructureGateCleanLayouts:
    """Canonical single-structure layouts must pass with zero violations."""

    def test_clean_src_layout_passes(
        self, orchestrator: RefactoringOrchestrator, clean_src_layout: Path
    ) -> None:
        result = orchestrator.check_dual_structure(clean_src_layout)
        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is True, f"Expected clean; got violations: {report.get('violations')}"
        assert report["violation_count"] == 0

    def test_flat_only_layout_passes(
        self, orchestrator: RefactoringOrchestrator, flat_only_layout: Path
    ) -> None:
        """A single-project flat layout with no src/ sub-tree must not flag."""
        result = orchestrator.check_dual_structure(flat_only_layout)
        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is True

    def test_no_sln_directory_passes(
        self, orchestrator: RefactoringOrchestrator, tmp_path: Path
    ) -> None:
        """Directories with no .sln files are out of scope — gate passes."""
        (tmp_path / "main.py").write_text("print('hello')")
        result = orchestrator.check_dual_structure(tmp_path)
        assert result.is_ok()
        assert result.unwrap()["clean"] is True


# ── Tests: dual-structure violations ──────────────────────────────────────────

class TestDualStructureGateViolations:
    """Dual-layout configurations must be caught as P0 CORE-035 violations."""

    def test_dual_layout_is_flagged(
        self, orchestrator: RefactoringOrchestrator, dual_layout: Path
    ) -> None:
        result = orchestrator.check_dual_structure(dual_layout)
        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is False, "Expected dual layout to be flagged"
        assert report["violation_count"] >= 1

    def test_violation_has_p0_severity(
        self, orchestrator: RefactoringOrchestrator, dual_layout: Path
    ) -> None:
        report = orchestrator.check_dual_structure(dual_layout).unwrap()
        severities = [v["severity"] for v in report["violations"]]
        assert "P0" in severities

    def test_violation_identifies_orphan_dirs(
        self, orchestrator: RefactoringOrchestrator, dual_layout: Path
    ) -> None:
        report = orchestrator.check_dual_structure(dual_layout).unwrap()
        orphans = report["violations"][0].get("orphan_files_or_dirs", [])
        # At least one known flat domain dir should appear
        orphan_names = [Path(o).name for o in orphans]
        domain_dirs_found = {"Api", "Application", "Domain", "Infrastructure"} & set(orphan_names)
        assert domain_dirs_found, f"Expected flat domain dirs in orphans, got: {orphan_names}"

    def test_violation_contains_recommendation(
        self, orchestrator: RefactoringOrchestrator, dual_layout: Path
    ) -> None:
        report = orchestrator.check_dual_structure(dual_layout).unwrap()
        recommendation = report["violations"][0].get("recommendation", "")
        assert recommendation, "Violation should include a recommendation for cleanup"

    def test_flat_cs_files_beside_sln_with_src_trigger_violation(
        self, orchestrator: RefactoringOrchestrator, tmp_path: Path
    ) -> None:
        """Flat .cs files alongside .sln that references src/ must be caught."""
        sln = textwrap.dedent("""\
            Microsoft Visual Studio Solution File, Format Version 12.00
            Project("{FAE04EC0}") = "App", "src\\App\\App.csproj", "{GUID}"
            EndProject
        """)
        backend = tmp_path / "backend"
        backend.mkdir()
        (backend / "App.sln").write_text(sln)
        (backend / "Program.cs").write_text("// orphan flat source")
        src_app = backend / "src" / "App"
        src_app.mkdir(parents=True)
        (src_app / "App.csproj").write_text("<Project />")

        result = orchestrator.check_dual_structure(backend)
        assert result.is_ok()
        report = result.unwrap()
        assert report["clean"] is False
        assert report["violation_count"] >= 1

    def test_report_includes_target_root(
        self, orchestrator: RefactoringOrchestrator, dual_layout: Path
    ) -> None:
        report = orchestrator.check_dual_structure(dual_layout).unwrap()
        assert "target_root" in report
        assert str(dual_layout) == report["target_root"]


# ── Tests: result contract ────────────────────────────────────────────────────

class TestDualStructureGateContract:
    """Result dictionary must always include required keys."""

    def test_ok_result_has_required_keys(
        self, orchestrator: RefactoringOrchestrator, clean_src_layout: Path
    ) -> None:
        report = orchestrator.check_dual_structure(clean_src_layout).unwrap()
        required_keys = {"clean", "violations", "violation_count", "target_root"}
        assert required_keys.issubset(report.keys())

    def test_violations_list_is_empty_on_clean(
        self, orchestrator: RefactoringOrchestrator, clean_src_layout: Path
    ) -> None:
        report = orchestrator.check_dual_structure(clean_src_layout).unwrap()
        assert report["violations"] == []

    def test_violation_dict_has_required_keys(
        self, orchestrator: RefactoringOrchestrator, dual_layout: Path
    ) -> None:
        report = orchestrator.check_dual_structure(dual_layout).unwrap()
        for v in report["violations"]:
            assert "rule" in v
            assert "severity" in v
            assert "description" in v
            assert "recommendation" in v


# AC_COMPLETE: ENH-STS-08-TESTS ✅
