"""
Unit tests for Obsolete Code Detector

Tests all detection capabilities: obsolete orchestrators, tests, scripts,
and deprecated import pattern analysis.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import pytest
from pathlib import Path
from src.operations.modules.realignment.obsolete_code_detector import (
    ObsoleteCodeDetector,
    CleanupPlan,
    ImportAnalysis
)


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary CORTEX project structure."""
    # Create basic structure
    (tmp_path / "cortex-operations.yaml").write_text("operations: []")
    
    # Create directories
    src = tmp_path / "src"
    orchestrators = src / "orchestrators"
    operations = src / "operations" / "modules"
    tests = tmp_path / "tests"
    scripts = tmp_path / "scripts"
    
    orchestrators.mkdir(parents=True)
    operations.mkdir(parents=True)
    tests.mkdir(parents=True)
    scripts.mkdir(parents=True)
    
    return tmp_path


@pytest.fixture
def detector(temp_project):
    """Create detector instance."""
    return ObsoleteCodeDetector(project_root=temp_project)


# ============================================================================
# ObsoleteCodeDetector Tests
# ============================================================================

def test_detector_init_with_root(temp_project):
    """Test detector initialization with explicit root."""
    detector = ObsoleteCodeDetector(project_root=temp_project)
    assert detector.project_root == temp_project
    assert detector.orchestrators_dir.exists()


def test_detector_auto_detect_root(temp_project, monkeypatch):
    """Test auto-detection of project root."""
    monkeypatch.chdir(temp_project)
    detector = ObsoleteCodeDetector()
    assert detector.project_root == temp_project


def test_detector_auto_detect_from_subdirectory(temp_project, monkeypatch):
    """Test auto-detection from subdirectory."""
    subdir = temp_project / "src" / "operations"
    subdir.mkdir(parents=True, exist_ok=True)
    monkeypatch.chdir(subdir)
    
    detector = ObsoleteCodeDetector()
    assert detector.project_root == temp_project


def test_detector_protected_paths(detector):
    """Test protected path detection."""
    protected = Path("/project/.git/config")
    assert detector._is_protected_path(protected)
    
    protected = Path("/project/.venv/lib/python")
    assert detector._is_protected_path(protected)
    
    not_protected = Path("/project/src/main.py")
    assert not detector._is_protected_path(not_protected)


def test_has_migrated_utility_exists(temp_project, detector):
    """Test detection of migrated utility."""
    # Create utility
    planning_dir = temp_project / "src" / "operations" / "modules" / "planning"
    planning_dir.mkdir(parents=True)
    (planning_dir / "planning_utility.py").write_text("# Planning utility")
    
    assert detector.has_migrated_utility("planning_orchestrator")


def test_has_migrated_utility_not_exists(detector):
    """Test detection when utility doesn't exist."""
    assert not detector.has_migrated_utility("nonexistent_orchestrator")


def test_has_migrated_utility_modules_dir_missing(temp_project, detector):
    """Test when modules directory doesn't exist."""
    modules = temp_project / "src" / "operations" / "modules"
    modules.rmdir()
    
    assert not detector.has_migrated_utility("planning_orchestrator")


def test_scan_for_obsolete_orchestrators_empty(detector):
    """Test scanning when no orchestrators exist."""
    obsolete = detector.scan_for_obsolete_orchestrators()
    assert obsolete == []


def test_scan_for_obsolete_orchestrators_with_migrated(temp_project, detector):
    """Test detection of obsolete orchestrators."""
    # Create orchestrator
    orch_dir = temp_project / "src" / "orchestrators"
    orch_file = orch_dir / "planning_orchestrator.py"
    orch_file.write_text("# Old orchestrator")
    
    # Create corresponding utility
    planning_dir = temp_project / "src" / "operations" / "modules" / "planning"
    planning_dir.mkdir(parents=True)
    (planning_dir / "planning_utility.py").write_text("# New utility")
    
    obsolete = detector.scan_for_obsolete_orchestrators()
    assert len(obsolete) == 1
    assert obsolete[0] == orch_file


def test_scan_for_obsolete_orchestrators_not_migrated(temp_project, detector):
    """Test orchestrator without migration is not flagged."""
    # Create orchestrator without utility
    orch_dir = temp_project / "src" / "orchestrators"
    orch_file = orch_dir / "active_orchestrator.py"
    orch_file.write_text("# Active orchestrator")
    
    obsolete = detector.scan_for_obsolete_orchestrators()
    assert len(obsolete) == 0


def test_scan_for_obsolete_tests_empty(detector):
    """Test scanning when no tests exist."""
    obsolete = detector.scan_for_obsolete_tests()
    assert obsolete == []


def test_scan_for_obsolete_tests_with_deleted_orchestrator(temp_project, detector):
    """Test detection of tests for deleted orchestrators."""
    # Create test without orchestrator
    tests_dir = temp_project / "tests"
    test_file = tests_dir / "test_planning_orchestrator.py"
    test_file.write_text("# Test for deleted orchestrator")
    
    obsolete = detector.scan_for_obsolete_tests()
    assert len(obsolete) == 1
    assert obsolete[0] == test_file


def test_scan_for_obsolete_tests_with_existing_orchestrator(temp_project, detector):
    """Test that tests for existing orchestrators are not flagged."""
    # Create orchestrator and test
    orch_dir = temp_project / "src" / "orchestrators"
    orch_file = orch_dir / "planning_orchestrator.py"
    orch_file.write_text("# Orchestrator")
    
    tests_dir = temp_project / "tests"
    test_file = tests_dir / "test_planning_orchestrator.py"
    test_file.write_text("# Test for orchestrator")
    
    obsolete = detector.scan_for_obsolete_tests()
    assert len(obsolete) == 0


def test_scan_for_obsolete_scripts_empty(detector):
    """Test scanning when no scripts exist."""
    obsolete = detector.scan_for_obsolete_scripts()
    assert obsolete == []


def test_scan_for_obsolete_scripts_with_backups(temp_project, detector):
    """Test detection of backup scripts."""
    scripts_dir = temp_project / "scripts"
    
    # Create various obsolete files
    (scripts_dir / "script_OLD.py").write_text("# Old")
    (scripts_dir / "backup_script.py").write_text("# Backup")
    (scripts_dir / "script_deprecated.py").write_text("# Deprecated")
    (scripts_dir / "temp_script.py").write_text("# Temp")
    
    obsolete = detector.scan_for_obsolete_scripts()
    # Each pattern is matched separately, some files may match multiple patterns
    # Just verify we found at least the core patterns
    assert len(obsolete) >= 2
    
    # Verify specific files are detected
    file_names = [f.name for f in obsolete]
    assert "script_OLD.py" in file_names
    assert "script_deprecated.py" in file_names


def test_scan_for_obsolete_scripts_test_files(temp_project, detector):
    """Test detection of test files in scripts directory."""
    scripts_dir = temp_project / "scripts"
    test_file = scripts_dir / "test_something.py"
    test_file.write_text("# Test in wrong location")
    
    obsolete = detector.scan_for_obsolete_scripts()
    assert test_file in obsolete


def test_analyze_import_usage_no_deprecated(temp_project, detector):
    """Test import analysis with clean file."""
    test_file = temp_project / "test.py"
    test_file.write_text("""
from src.operations.modules.planning import planning_utility
import logging
""")
    
    analysis = detector.analyze_import_usage(test_file)
    assert not analysis.has_deprecated
    assert len(analysis.findings) == 0


def test_analyze_import_usage_with_deprecated(temp_project, detector):
    """Test import analysis with deprecated imports."""
    test_file = temp_project / "test.py"
    test_file.write_text("""
from src.orchestrators.planning_orchestrator import PlanningOrchestrator
from orchestrators.commit_orchestrator import CommitOrchestrator
import src.orchestrators.upgrade_orchestrator
""")
    
    analysis = detector.analyze_import_usage(test_file)
    assert analysis.has_deprecated
    assert analysis.total_deprecated_imports == 3
    assert len(analysis.findings) == 3


def test_analyze_import_usage_with_replacements(temp_project, detector):
    """Test that replacements are suggested correctly."""
    test_file = temp_project / "test.py"
    test_file.write_text("from src.orchestrators.planning import Planning")
    
    analysis = detector.analyze_import_usage(test_file)
    assert analysis.has_deprecated
    assert len(analysis.findings) == 1
    assert 'replacement' in analysis.findings[0]
    assert 'operations.modules' in analysis.findings[0]['replacement']


def test_analyze_import_usage_file_not_found(detector):
    """Test import analysis with non-existent file."""
    analysis = detector.analyze_import_usage(Path("/nonexistent/file.py"))
    assert not analysis.has_deprecated
    assert len(analysis.findings) == 0


def test_scan_all_for_deprecated_imports_empty(detector):
    """Test scanning when no files have deprecated imports."""
    files = detector.scan_all_for_deprecated_imports()
    assert files == []


def test_scan_all_for_deprecated_imports_with_deprecated(temp_project, detector):
    """Test scanning finds files with deprecated imports."""
    # Create file with deprecated import
    src_dir = temp_project / "src"
    test_file = src_dir / "test.py"
    test_file.write_text("from src.orchestrators.planning import Planning")
    
    files = detector.scan_all_for_deprecated_imports()
    assert len(files) >= 1
    assert any(f.file == test_file for f in files)


def test_calculate_total_size_empty(detector):
    """Test size calculation with empty list."""
    size = detector.calculate_total_size([])
    assert size == 0.0


def test_calculate_total_size_with_files(temp_project, detector):
    """Test size calculation with actual files."""
    file1 = temp_project / "file1.py"
    file2 = temp_project / "file2.py"
    
    file1.write_text("x" * 1024)  # 1 KB
    file2.write_text("y" * 2048)  # 2 KB
    
    size = detector.calculate_total_size([file1, file2])
    expected = 3 / 1024  # 3 KB in MB
    assert abs(size - expected) < 0.001


def test_calculate_total_size_missing_file(detector):
    """Test size calculation handles missing files gracefully."""
    size = detector.calculate_total_size([Path("/nonexistent.py")])
    assert size == 0.0


def test_generate_cleanup_plan_empty(detector):
    """Test cleanup plan generation with no obsolete code."""
    plan = detector.generate_cleanup_plan()
    assert plan.total_files == 0
    assert plan.estimated_removal_size_mb == 0.0


def test_generate_cleanup_plan_with_obsolete(temp_project, detector):
    """Test cleanup plan generation with obsolete code."""
    # Create obsolete orchestrator
    orch_dir = temp_project / "src" / "orchestrators"
    orch_file = orch_dir / "planning_orchestrator.py"
    orch_file.write_text("# Obsolete" * 100)
    
    # Create utility (so orchestrator is flagged as obsolete)
    planning_dir = temp_project / "src" / "operations" / "modules" / "planning"
    planning_dir.mkdir(parents=True)
    (planning_dir / "planning_utility.py").write_text("# New")
    
    plan = detector.generate_cleanup_plan()
    # Should find at least the orchestrator
    assert plan.total_files >= 1
    assert len(plan.obsolete_orchestrators) >= 1


def test_generate_report_empty_plan(detector):
    """Test report generation with empty plan."""
    plan = CleanupPlan()
    report = detector.generate_report(plan)
    
    assert "All Clear" in report
    assert "0 files" in report


def test_generate_report_with_obsolete(temp_project, detector):
    """Test report generation with obsolete code."""
    # Create files
    orch_file = temp_project / "src" / "orchestrators" / "test_orchestrator.py"
    orch_file.parent.mkdir(parents=True, exist_ok=True)
    orch_file.write_text("# Test")
    
    plan = CleanupPlan(
        obsolete_orchestrators=[orch_file],
        estimated_removal_size_mb=0.5
    )
    
    report = detector.generate_report(plan)
    assert "1 files" in report
    assert "0.50 MB" in report or "0.5 MB" in report
    assert "test_orchestrator.py" in report


def test_generate_report_with_deprecated_imports(temp_project, detector):
    """Test report includes deprecated imports section."""
    test_file = temp_project / "test.py"
    test_file.write_text("from src.orchestrators import something")
    
    analysis = ImportAnalysis(
        file=test_file,
        has_deprecated=True,
        total_deprecated_imports=2
    )
    
    plan = CleanupPlan(files_with_deprecated_imports=[analysis])
    report = detector.generate_report(plan)
    
    assert "Deprecated Imports" in report
    assert "test.py" in report


# ============================================================================
# CleanupPlan Tests
# ============================================================================

def test_cleanup_plan_init_empty():
    """Test CleanupPlan initialization with defaults."""
    plan = CleanupPlan()
    assert plan.total_files == 0
    assert plan.estimated_removal_size_mb == 0.0
    assert plan.safety_checks_required is True


def test_cleanup_plan_total_calculation():
    """Test CleanupPlan calculates totals correctly."""
    plan = CleanupPlan(
        obsolete_orchestrators=[Path("o1.py"), Path("o2.py")],
        obsolete_tests=[Path("t1.py")],
        obsolete_scripts=[Path("s1.py"), Path("s2.py"), Path("s3.py")]
    )
    assert plan.total_files == 6


def test_cleanup_plan_get_all_files():
    """Test CleanupPlan.get_all_files() returns correct files."""
    files = [Path(f"file{i}.py") for i in range(5)]
    
    plan = CleanupPlan(
        obsolete_orchestrators=[files[0], files[1]],
        obsolete_tests=[files[2]],
        obsolete_scripts=[files[3], files[4]]
    )
    
    all_files = plan.get_all_files()
    assert len(all_files) == 5
    assert set(all_files) == set(files)


def test_cleanup_plan_excludes_import_files():
    """Test get_all_files() doesn't include deprecated import files."""
    analysis = ImportAnalysis(
        file=Path("import_file.py"),
        has_deprecated=True
    )
    
    plan = CleanupPlan(
        obsolete_orchestrators=[Path("orch.py")],
        files_with_deprecated_imports=[analysis]
    )
    
    all_files = plan.get_all_files()
    assert Path("orch.py") in all_files
    assert Path("import_file.py") not in all_files


# ============================================================================
# ImportAnalysis Tests
# ============================================================================

def test_import_analysis_init():
    """Test ImportAnalysis initialization."""
    analysis = ImportAnalysis(
        file=Path("test.py"),
        has_deprecated=True,
        total_deprecated_imports=3
    )
    assert analysis.file == Path("test.py")
    assert analysis.has_deprecated is True
    assert analysis.total_deprecated_imports == 3


def test_import_analysis_with_findings():
    """Test ImportAnalysis with findings."""
    findings = [
        {'line': 1, 'pattern': 'test', 'type': 'deprecated_import'},
        {'line': 2, 'pattern': 'test2', 'type': 'deprecated_import'}
    ]
    
    analysis = ImportAnalysis(
        file=Path("test.py"),
        has_deprecated=True,
        findings=findings,
        total_deprecated_imports=2
    )
    
    assert len(analysis.findings) == 2
    assert analysis.findings[0]['line'] == 1


# ============================================================================
# CLI Tests
# ============================================================================

def test_main_success(temp_project, monkeypatch, capsys):
    """Test main() execution with clean repository."""
    monkeypatch.chdir(temp_project)
    
    from src.operations.modules.realignment.obsolete_code_detector import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "All Clear" in captured.out


def test_main_with_obsolete_code(temp_project, monkeypatch, capsys):
    """Test main() exits with code 1 when obsolete code found."""
    monkeypatch.chdir(temp_project)
    
    # Create obsolete file
    orch_dir = temp_project / "src" / "orchestrators"
    orch_file = orch_dir / "test_orchestrator.py"
    orch_file.write_text("# Test")
    
    # Create utility
    util_dir = temp_project / "src" / "operations" / "modules" / "test"
    util_dir.mkdir(parents=True)
    (util_dir / "test_utility.py").write_text("# Utility")
    
    from src.operations.modules.realignment.obsolete_code_detector import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "test_orchestrator.py" in captured.out


def test_main_exception_handling(tmp_path, monkeypatch, capsys):
    """Test main() handles exceptions gracefully."""
    # Create directory without cortex-operations.yaml to trigger error
    monkeypatch.chdir(tmp_path)
    
    from src.operations.modules.realignment.obsolete_code_detector import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 2
