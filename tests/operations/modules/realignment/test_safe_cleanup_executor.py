"""
Unit tests for Safe Cleanup Executor

Tests all safety mechanisms: git checks, test execution, backup/restore,
category-level cleanup, rollback on failure, and dry-run mode.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.operations.modules.realignment.safe_cleanup_executor import (
    SafeCleanupExecutor,
    CleanupCategory,
    CleanupResult,
    ExecutionReport
)
from src.operations.modules.realignment.obsolete_code_detector import CleanupPlan


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary CORTEX project structure."""
    (tmp_path / "cortex-operations.yaml").write_text("operations: []")
    (tmp_path / "cortex-brain" / "backups" / "cleanup").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    
    return tmp_path


@pytest.fixture
def executor(temp_project):
    """Create executor instance."""
    return SafeCleanupExecutor(project_root=temp_project, create_backups=True)


@pytest.fixture
def executor_no_backup(temp_project):
    """Create executor without backups."""
    return SafeCleanupExecutor(project_root=temp_project, create_backups=False)


# ============================================================================
# SafeCleanupExecutor Tests
# ============================================================================

def test_executor_init_with_root(temp_project):
    """Test executor initialization with explicit root."""
    executor = SafeCleanupExecutor(project_root=temp_project)
    assert executor.project_root == temp_project
    assert executor.create_backups is True


def test_executor_auto_detect_root(temp_project, monkeypatch):
    """Test auto-detection of project root."""
    monkeypatch.chdir(temp_project)
    executor = SafeCleanupExecutor()
    assert executor.project_root == temp_project


def test_executor_no_backup_mode(temp_project):
    """Test executor with backups disabled."""
    executor = SafeCleanupExecutor(project_root=temp_project, create_backups=False)
    assert executor.create_backups is False


@patch('subprocess.run')
def test_check_git_status_clean(mock_run, executor):
    """Test git status check with clean working directory."""
    mock_run.return_value = Mock(returncode=0, stdout="")
    
    assert executor.check_git_status() is True
    mock_run.assert_called_once()


@patch('subprocess.run')
def test_check_git_status_dirty(mock_run, executor):
    """Test git status check with uncommitted changes."""
    mock_run.return_value = Mock(returncode=0, stdout="M file.py\n")
    
    assert executor.check_git_status() is False


@patch('subprocess.run')
def test_check_git_status_error(mock_run, executor):
    """Test git status check handles errors."""
    from subprocess import CalledProcessError
    mock_run.side_effect = CalledProcessError(1, 'git')
    
    # Should return False on error
    assert executor.check_git_status() is False


@patch('subprocess.run')
def test_check_git_status_no_git(mock_run, executor):
    """Test git status when git not available."""
    mock_run.side_effect = FileNotFoundError()
    
    # Should allow cleanup when git not available
    assert executor.check_git_status() is True


@patch('subprocess.run')
def test_run_tests_success(mock_run, executor):
    """Test running tests successfully."""
    mock_run.return_value = Mock(returncode=0, stdout="All passed")
    
    assert executor.run_tests() is True


@patch('subprocess.run')
def test_run_tests_failure(mock_run, executor):
    """Test running tests with failures."""
    mock_run.return_value = Mock(returncode=1, stdout="1 failed", stderr="")
    
    assert executor.run_tests() is False


@patch('subprocess.run')
def test_run_tests_timeout(mock_run, executor):
    """Test test timeout handling."""
    from subprocess import TimeoutExpired
    mock_run.side_effect = TimeoutExpired(cmd=['pytest'], timeout=300)
    
    assert executor.run_tests() is False


@patch('subprocess.run')
def test_run_tests_exception(mock_run, executor):
    """Test test execution exception handling."""
    mock_run.side_effect = Exception("Test error")
    
    assert executor.run_tests() is False


def test_create_backup(temp_project, executor):
    """Test backup creation."""
    # Create test files
    files = []
    for i in range(3):
        file = temp_project / f"test{i}.py"
        file.write_text(f"content {i}")
        files.append(file)
    
    backup_path = executor.create_backup(files)
    
    assert backup_path.exists()
    assert backup_path.parent == executor.backup_dir
    
    # Verify files backed up
    for file in files:
        relative = file.relative_to(temp_project)
        backup_file = backup_path / relative
        assert backup_file.exists()
        assert backup_file.read_text() == file.read_text()


def test_create_backup_disabled(executor_no_backup):
    """Test backup creation when disabled."""
    files = [Path("/tmp/test.py")]
    backup_path = executor_no_backup.create_backup(files)
    
    assert backup_path is None


def test_create_backup_nonexistent_files(temp_project, executor):
    """Test backup handles non-existent files."""
    files = [temp_project / "nonexistent.py"]
    
    # Should not raise exception
    backup_path = executor.create_backup(files)
    assert backup_path.exists()


def test_remove_files_success(temp_project, executor):
    """Test successful file removal."""
    # Create files
    files = []
    for i in range(3):
        file = temp_project / f"test{i}.py"
        file.write_text("content")
        files.append(file)
    
    removed, failed = executor.remove_files(files)
    
    assert len(removed) == 3
    assert len(failed) == 0
    
    # Verify files deleted
    for file in files:
        assert not file.exists()


def test_remove_files_nonexistent(temp_project, executor):
    """Test removal of non-existent files."""
    files = [temp_project / "nonexistent.py"]
    
    removed, failed = executor.remove_files(files)
    
    assert len(removed) == 0
    assert len(failed) == 1


def test_remove_files_mixed_results(temp_project, executor):
    """Test removal with some failures."""
    # Create one file
    existing = temp_project / "existing.py"
    existing.write_text("content")
    
    files = [existing, temp_project / "nonexistent.py"]
    
    removed, failed = executor.remove_files(files)
    
    assert len(removed) == 1
    assert len(failed) == 1


def test_restore_backup(temp_project, executor):
    """Test backup restoration."""
    # Create and backup files
    files = []
    for i in range(2):
        file = temp_project / f"test{i}.py"
        file.write_text(f"original {i}")
        files.append(file)
    
    backup_path = executor.create_backup(files)
    
    # Modify/delete files
    files[0].write_text("modified")
    files[1].unlink()
    
    # Restore
    success = executor.restore_backup(backup_path, files)
    
    assert success
    assert files[0].read_text() == "original 0"
    assert files[1].exists()
    assert files[1].read_text() == "original 1"


def test_restore_backup_error(temp_project, executor):
    """Test backup restoration error handling."""
    files = [temp_project / "test.py"]
    fake_backup = temp_project / "fake_backup"
    
    success = executor.restore_backup(fake_backup, files)
    
    assert success is True  # No files to restore, but doesn't fail


@patch.object(SafeCleanupExecutor, 'run_tests')
@patch.object(SafeCleanupExecutor, 'create_backup')
@patch.object(SafeCleanupExecutor, 'remove_files')
def test_cleanup_category_success(mock_remove, mock_backup, mock_tests, temp_project, executor):
    """Test successful category cleanup."""
    # Setup mocks
    mock_tests.return_value = True
    mock_backup.return_value = temp_project / "backup"
    
    test_files = [temp_project / f"test{i}.py" for i in range(2)]
    mock_remove.return_value = (test_files, [])
    
    result = executor.cleanup_category(
        category=CleanupCategory.OBSOLETE_TESTS,
        files=test_files,
        run_tests_after=True
    )
    
    assert result.success
    assert result.tests_passed_before
    assert result.tests_passed_after
    assert len(result.files_removed) == 2
    assert not result.rolled_back


@patch.object(SafeCleanupExecutor, 'run_tests')
def test_cleanup_category_tests_fail_before(mock_tests, temp_project, executor):
    """Test cleanup aborts if tests fail before."""
    mock_tests.return_value = False
    
    files = [temp_project / "test.py"]
    
    result = executor.cleanup_category(
        category=CleanupCategory.OBSOLETE_TESTS,
        files=files,
        run_tests_after=True
    )
    
    assert not result.success
    assert not result.tests_passed_before
    assert result.error is not None


@patch.object(SafeCleanupExecutor, 'run_tests')
@patch.object(SafeCleanupExecutor, 'create_backup')
@patch.object(SafeCleanupExecutor, 'remove_files')
@patch.object(SafeCleanupExecutor, 'restore_backup')
def test_cleanup_category_rollback_on_test_failure(
    mock_restore, mock_remove, mock_backup, mock_tests, temp_project, executor
):
    """Test rollback when tests fail after cleanup."""
    # Tests pass before, fail after
    mock_tests.side_effect = [True, False]
    
    backup_path = temp_project / "backup"
    mock_backup.return_value = backup_path
    
    test_files = [temp_project / "test.py"]
    mock_remove.return_value = (test_files, [])
    mock_restore.return_value = True
    
    result = executor.cleanup_category(
        category=CleanupCategory.OBSOLETE_TESTS,
        files=test_files,
        run_tests_after=True
    )
    
    assert not result.success
    assert result.tests_passed_before
    assert not result.tests_passed_after
    assert result.rolled_back
    mock_restore.assert_called_once_with(backup_path, test_files)


@patch.object(SafeCleanupExecutor, 'run_tests')
@patch.object(SafeCleanupExecutor, 'create_backup')
@patch.object(SafeCleanupExecutor, 'remove_files')
def test_cleanup_category_skip_tests(mock_remove, mock_backup, mock_tests, temp_project, executor):
    """Test cleanup without running tests."""
    mock_backup.return_value = temp_project / "backup"
    test_files = [temp_project / "test.py"]
    mock_remove.return_value = (test_files, [])
    
    result = executor.cleanup_category(
        category=CleanupCategory.OBSOLETE_TESTS,
        files=test_files,
        run_tests_after=False
    )
    
    assert result.success
    assert result.tests_passed_after
    mock_tests.assert_not_called()


def test_cleanup_category_empty_files(executor):
    """Test cleanup with no files."""
    result = executor.cleanup_category(
        category=CleanupCategory.OBSOLETE_TESTS,
        files=[],
        run_tests_after=True
    )
    
    assert result.success
    assert result.tests_passed_before
    assert result.tests_passed_after


@patch.object(SafeCleanupExecutor, 'check_git_status')
@patch.object(SafeCleanupExecutor, 'cleanup_category')
def test_execute_cleanup_dry_run(mock_cleanup, mock_git, executor):
    """Test dry run mode doesn't execute cleanup."""
    mock_git.return_value = True
    
    plan = CleanupPlan(
        obsolete_tests=[Path("test.py")],
        estimated_removal_size_mb=0.1
    )
    
    report = executor.execute_cleanup(plan, dry_run=True)
    
    mock_cleanup.assert_not_called()
    assert report.total_files_removed == 0


@patch.object(SafeCleanupExecutor, 'check_git_status')
def test_execute_cleanup_git_dirty(mock_git, executor):
    """Test cleanup aborts if git is dirty."""
    mock_git.return_value = False
    
    plan = CleanupPlan(obsolete_tests=[Path("test.py")])
    
    report = executor.execute_cleanup(plan, dry_run=False)
    
    assert report.total_files_removed == 0
    assert len(report.categories_completed) == 0


@patch.object(SafeCleanupExecutor, 'check_git_status')
@patch.object(SafeCleanupExecutor, 'cleanup_category')
def test_execute_cleanup_success(mock_cleanup, mock_git, temp_project, executor):
    """Test successful complete cleanup."""
    mock_git.return_value = True
    
    # Mock successful cleanup
    mock_cleanup.return_value = CleanupResult(
        category=CleanupCategory.OBSOLETE_TESTS,
        files_removed=[temp_project / "test.py"],
        tests_passed_before=True,
        tests_passed_after=True
    )
    
    plan = CleanupPlan(obsolete_tests=[temp_project / "test.py"])
    
    report = executor.execute_cleanup(plan, dry_run=False)
    
    assert report.success
    assert report.total_files_removed == 1
    assert len(report.categories_completed) == 1


@patch.object(SafeCleanupExecutor, 'check_git_status')
@patch.object(SafeCleanupExecutor, 'cleanup_category')
def test_execute_cleanup_stops_on_failure(mock_cleanup, mock_git, temp_project, executor):
    """Test cleanup stops after first category failure."""
    mock_git.return_value = True
    
    # First category fails
    mock_cleanup.return_value = CleanupResult(
        category=CleanupCategory.OBSOLETE_SCRIPTS,
        files_failed=[temp_project / "script.py"],
        error="Removal failed"
    )
    
    plan = CleanupPlan(
        obsolete_scripts=[temp_project / "script.py"],
        obsolete_tests=[temp_project / "test.py"]
    )
    
    report = executor.execute_cleanup(plan, dry_run=False)
    
    assert not report.success
    assert len(report.categories_failed) == 1
    # Should only call once (first category), not proceed to tests
    assert mock_cleanup.call_count == 1


def test_generate_report_dry_run(temp_project, executor):
    """Test report generation for dry run."""
    report = ExecutionReport()
    
    output = executor.generate_report(report, dry_run=True)
    
    assert "DRY RUN" in output
    assert "This was a dry run" in output


def test_generate_report_success(temp_project, executor):
    """Test report generation for successful cleanup."""
    result = CleanupResult(
        category=CleanupCategory.OBSOLETE_TESTS,
        files_removed=[temp_project / "test1.py", temp_project / "test2.py"],
        tests_passed_before=True,
        tests_passed_after=True,
        backup_path=temp_project / "backup"
    )
    
    report = ExecutionReport(
        total_files_removed=2,
        categories_completed=[CleanupCategory.OBSOLETE_TESTS],
        results=[result]
    )
    
    output = executor.generate_report(report, dry_run=False)
    
    assert "✅ Success" in output
    assert "Total Files Removed: 2" in output or "**Total Files Removed:** 2" in output
    assert "obsolete_tests" in output


def test_generate_report_failure(temp_project, executor):
    """Test report generation for failed cleanup."""
    result = CleanupResult(
        category=CleanupCategory.OBSOLETE_TESTS,
        files_failed=[temp_project / "test.py"],
        error="Tests failed after cleanup",
        rolled_back=True
    )
    
    report = ExecutionReport(
        total_files_failed=1,
        categories_failed=[CleanupCategory.OBSOLETE_TESTS],
        results=[result]
    )
    
    output = executor.generate_report(report, dry_run=False)
    
    assert "❌ Failed" in output
    assert "Failed Categories" in output
    assert "rolled back" in output


# ============================================================================
# CleanupResult Tests
# ============================================================================

def test_cleanup_result_success_property():
    """Test CleanupResult.success property."""
    result = CleanupResult(
        category=CleanupCategory.OBSOLETE_TESTS,
        files_removed=[Path("test.py")]
    )
    
    assert result.success is True


def test_cleanup_result_not_success_with_error():
    """Test CleanupResult.success with error."""
    result = CleanupResult(
        category=CleanupCategory.OBSOLETE_TESTS,
        error="Something failed"
    )
    
    assert result.success is False


def test_cleanup_result_not_success_with_rollback():
    """Test CleanupResult.success with rollback."""
    result = CleanupResult(
        category=CleanupCategory.OBSOLETE_TESTS,
        rolled_back=True
    )
    
    assert result.success is False


# ============================================================================
# ExecutionReport Tests
# ============================================================================

def test_execution_report_success_property():
    """Test ExecutionReport.success property."""
    report = ExecutionReport(
        total_files_removed=5,
        categories_completed=[CleanupCategory.OBSOLETE_TESTS]
    )
    
    assert report.success is True


def test_execution_report_not_success_with_failures():
    """Test ExecutionReport.success with failures."""
    report = ExecutionReport(
        total_files_failed=1,
        categories_failed=[CleanupCategory.OBSOLETE_TESTS]
    )
    
    assert report.success is False


# ============================================================================
# CLI Tests
# ============================================================================

@patch('src.operations.modules.realignment.safe_cleanup_executor.ObsoleteCodeDetector')
@patch.object(SafeCleanupExecutor, 'execute_cleanup')
def test_main_dry_run(mock_execute, mock_detector, temp_project, monkeypatch, capsys):
    """Test main() in dry run mode."""
    monkeypatch.chdir(temp_project)
    
    # Mock detector
    detector_instance = Mock()
    detector_instance.generate_cleanup_plan.return_value = CleanupPlan(
        obsolete_tests=[Path("test.py")]
    )
    mock_detector.return_value = detector_instance
    
    # Mock executor
    mock_execute.return_value = ExecutionReport()
    
    import sys
    monkeypatch.setattr(sys, 'argv', ['cleanup.py', '--dry-run'])
    
    from src.operations.modules.realignment.safe_cleanup_executor import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 0
    mock_execute.assert_called_once()


@patch('src.operations.modules.realignment.safe_cleanup_executor.ObsoleteCodeDetector')
def test_main_no_files(mock_detector, temp_project, monkeypatch, capsys):
    """Test main() when no files to clean."""
    monkeypatch.chdir(temp_project)
    
    # Mock detector with empty plan
    detector_instance = Mock()
    detector_instance.generate_cleanup_plan.return_value = CleanupPlan()
    mock_detector.return_value = detector_instance
    
    import sys
    monkeypatch.setattr(sys, 'argv', ['cleanup.py'])
    
    from src.operations.modules.realignment.safe_cleanup_executor import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "No obsolete files" in captured.out


def test_main_exception_handling(tmp_path, monkeypatch):
    """Test main() handles exceptions gracefully."""
    monkeypatch.chdir(tmp_path)
    
    import sys
    monkeypatch.setattr(sys, 'argv', ['cleanup.py'])
    
    from src.operations.modules.realignment.safe_cleanup_executor import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 2
