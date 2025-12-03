"""
Unit tests for Test Migrator

Tests all migration capabilities: import rewriting, class name updates,
instantiation fixes, dry-run mode, backup creation, and batch processing.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import pytest
from pathlib import Path
from src.operations.modules.realignment.test_migrator import (
    TestMigrator,
    MigrationChange,
    MigrationResult,
    BatchMigrationResult
)


@pytest.fixture
def temp_project(tmp_path):
    """Create temporary CORTEX project structure."""
    (tmp_path / "cortex-operations.yaml").write_text("operations: []")
    
    # Create directories
    (tmp_path / "cortex-brain" / "backups" / "migrations").mkdir(parents=True)
    (tmp_path / "tests").mkdir()
    
    return tmp_path


@pytest.fixture
def migrator(temp_project):
    """Create migrator instance."""
    return TestMigrator(project_root=temp_project, create_backups=True)


@pytest.fixture
def migrator_no_backup(temp_project):
    """Create migrator without backups."""
    return TestMigrator(project_root=temp_project, create_backups=False)


# ============================================================================
# TestMigrator Tests
# ============================================================================

def test_migrator_init_with_root(temp_project):
    """Test migrator initialization with explicit root."""
    migrator = TestMigrator(project_root=temp_project)
    assert migrator.project_root == temp_project
    assert migrator.create_backups is True


def test_migrator_auto_detect_root(temp_project, monkeypatch):
    """Test auto-detection of project root."""
    monkeypatch.chdir(temp_project)
    migrator = TestMigrator()
    assert migrator.project_root == temp_project


def test_migrator_no_backup_mode(temp_project):
    """Test migrator with backups disabled."""
    migrator = TestMigrator(project_root=temp_project, create_backups=False)
    assert migrator.create_backups is False


def test_migrate_imports_from_orchestrators(migrator):
    """Test migrating 'from orchestrators' imports."""
    content = "from src.orchestrators.planning_orchestrator import PlanningOrchestrator"
    
    migrated, changes = migrator.migrate_imports(content)
    
    assert "from src.operations.modules.planning.planning_utility import PlanningOrchestrator" in migrated
    assert len(changes) == 1
    assert changes[0].change_type == 'import'


def test_migrate_imports_short_form(migrator):
    """Test migrating short form imports."""
    content = "from orchestrators.commit_orchestrator import CommitOrchestrator"
    
    migrated, changes = migrator.migrate_imports(content)
    
    assert "from src.operations.modules.commit.commit_utility import CommitOrchestrator" in migrated
    assert len(changes) == 1


def test_migrate_imports_import_statement(migrator):
    """Test migrating 'import' statements."""
    content = "import src.orchestrators.planning_orchestrator"
    
    migrated, changes = migrator.migrate_imports(content)
    
    assert "import src.operations.modules.planning.planning_utility" in migrated
    assert len(changes) == 1


def test_migrate_imports_multiple(migrator):
    """Test migrating multiple imports."""
    content = """
from src.orchestrators.planning_orchestrator import PlanningOrchestrator
from orchestrators.commit_orchestrator import CommitOrchestrator
import src.orchestrators.upgrade_orchestrator
"""
    
    migrated, changes = migrator.migrate_imports(content)
    
    assert len(changes) == 3
    assert "operations.modules.planning" in migrated
    assert "operations.modules.commit" in migrated
    assert "operations.modules.upgrade" in migrated


def test_migrate_imports_no_changes(migrator):
    """Test migration when no changes needed."""
    content = "from src.operations.modules.planning.planning_utility import PlanningUtility"
    
    migrated, changes = migrator.migrate_imports(content)
    
    assert migrated == content
    assert len(changes) == 0


def test_migrate_class_names_orchestrator_to_utility(migrator):
    """Test migrating class names from Orchestrator to Utility."""
    content = "orchestrator = PlanningOrchestrator()"
    
    migrated, changes = migrator.migrate_class_names(content)
    
    assert "PlanningUtility" in migrated
    assert len(changes) == 1
    assert changes[0].change_type == 'class_name'


def test_migrate_class_names_multiple(migrator):
    """Test migrating multiple class names."""
    content = """
planning = PlanningOrchestrator()
commit = CommitOrchestrator()
upgrade = UpgradeOrchestrator()
"""
    
    migrated, changes = migrator.migrate_class_names(content)
    
    assert "PlanningUtility" in migrated
    assert "CommitUtility" in migrated
    assert "UpgradeUtility" in migrated
    assert len(changes) == 3


def test_migrate_class_names_already_utility(migrator):
    """Test that Utility classes are not changed."""
    content = "utility = PlanningUtility()"
    
    migrated, changes = migrator.migrate_class_names(content)
    
    assert migrated == content
    assert len(changes) == 0


def test_migrate_instantiation_basic(migrator):
    """Test migrating basic instantiation."""
    content = "orchestrator = PlanningOrchestrator()"
    
    migrated, changes = migrator.migrate_instantiation(content)
    
    assert "orchestrator = PlanningUtility(" in migrated
    assert len(changes) == 1
    assert changes[0].change_type == 'instantiation'


def test_migrate_instantiation_with_args(migrator):
    """Test migrating instantiation with arguments."""
    content = "orchestrator = PlanningOrchestrator(config, logger)"
    
    migrated, changes = migrator.migrate_instantiation(content)
    
    assert "orchestrator = PlanningUtility(config, logger)" in migrated
    assert len(changes) == 1


def test_migrate_instantiation_multiple(migrator):
    """Test migrating multiple instantiations."""
    content = """
planning = PlanningOrchestrator()
commit = CommitOrchestrator()
"""
    
    migrated, changes = migrator.migrate_instantiation(content)
    
    assert "planning = PlanningUtility(" in migrated
    assert "commit = CommitUtility(" in migrated
    assert len(changes) == 2


def test_migrate_instantiation_already_utility(migrator):
    """Test that Utility instantiations are not changed."""
    content = "utility = PlanningUtility()"
    
    migrated, changes = migrator.migrate_instantiation(content)
    
    assert migrated == content
    assert len(changes) == 0


def test_generate_diff_with_changes(migrator):
    """Test diff generation with changes."""
    original = "from orchestrators.planning import Planning"
    migrated = "from src.operations.modules.planning import Planning"
    
    diff = migrator.generate_diff(original, migrated, "test.py")
    
    assert "a/test.py" in diff
    assert "b/test.py" in diff
    assert "-from orchestrators" in diff
    assert "+from src.operations" in diff


def test_generate_diff_no_changes(migrator):
    """Test diff generation with no changes."""
    content = "from src.operations import something"
    
    diff = migrator.generate_diff(content, content, "test.py")
    
    assert diff == ""


def test_create_backup(temp_project, migrator):
    """Test backup creation."""
    # Create test file
    test_file = temp_project / "test.py"
    test_file.write_text("original content")
    
    backup_path = migrator._create_backup(test_file)
    
    assert backup_path.exists()
    assert backup_path.read_text() == "original content"
    assert backup_path.parent == migrator.backup_dir


def test_create_backup_disabled(temp_project, migrator_no_backup):
    """Test that backup is not created when disabled."""
    test_file = temp_project / "test.py"
    test_file.write_text("content")
    
    backup_path = migrator_no_backup._create_backup(test_file)
    
    assert backup_path is None


def test_migrate_file_with_changes(temp_project, migrator):
    """Test migrating file with changes."""
    # Create test file
    test_file = temp_project / "test.py"
    test_file.write_text("""
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

orchestrator = PlanningOrchestrator()
""")
    
    result = migrator.migrate_file(test_file, dry_run=False)
    
    assert result.success
    assert result.has_changes
    assert result.changes_made > 0
    assert result.backup_path is not None
    
    # Verify file was updated
    updated_content = test_file.read_text()
    assert "operations.modules.planning" in updated_content
    assert "PlanningUtility" in updated_content


def test_migrate_file_dry_run(temp_project, migrator):
    """Test dry run mode doesn't modify file."""
    test_file = temp_project / "test.py"
    original_content = "from src.orchestrators.planning_orchestrator import PlanningOrchestrator"
    test_file.write_text(original_content)
    
    result = migrator.migrate_file(test_file, dry_run=True)
    
    assert result.success
    assert result.has_changes
    assert result.backup_path is None
    
    # Verify file was NOT updated
    assert test_file.read_text() == original_content


def test_migrate_file_no_changes(temp_project, migrator):
    """Test migrating file with no changes needed."""
    test_file = temp_project / "test.py"
    test_file.write_text("from src.operations.modules.planning import PlanningUtility")
    
    result = migrator.migrate_file(test_file, dry_run=False)
    
    assert result.success
    assert not result.has_changes
    assert result.changes_made == 0


def test_migrate_file_error_handling(migrator):
    """Test error handling for non-existent file."""
    result = migrator.migrate_file(Path("/nonexistent/file.py"))
    
    assert not result.success
    assert result.error is not None


def test_migrate_batch_success(temp_project, migrator):
    """Test batch migration of multiple files."""
    # Create test files
    files = []
    for i in range(3):
        file = temp_project / f"test{i}.py"
        file.write_text(f"from orchestrators.test_orchestrator import TestOrchestrator")
        files.append(file)
    
    result = migrator.migrate_batch(files, dry_run=False)
    
    assert result.total_files == 3
    assert result.successful == 3
    assert result.failed == 0
    assert result.total_changes > 0
    assert result.success_rate == 100.0


def test_migrate_batch_dry_run(temp_project, migrator):
    """Test batch migration in dry run mode."""
    files = []
    for i in range(2):
        file = temp_project / f"test{i}.py"
        original = "from orchestrators.test import Test"
        file.write_text(original)
        files.append(file)
    
    result = migrator.migrate_batch(files, dry_run=True)
    
    assert result.successful == 2
    # Verify files unchanged
    for file in files:
        assert "orchestrators" in file.read_text()


def test_migrate_batch_mixed_results(temp_project, migrator):
    """Test batch migration with some failures."""
    # Create valid file
    valid_file = temp_project / "valid.py"
    valid_file.write_text("from orchestrators.test import Test")
    
    files = [valid_file, Path("/nonexistent.py")]
    
    result = migrator.migrate_batch(files, dry_run=False)
    
    assert result.total_files == 2
    assert result.successful == 1
    assert result.failed == 1
    assert result.success_rate == 50.0


def test_generate_report_successful_migration(temp_project, migrator):
    """Test report generation for successful migration."""
    test_file = temp_project / "test.py"
    
    result = BatchMigrationResult(
        total_files=1,
        successful=1,
        failed=0,
        total_changes=3,
        results=[
            MigrationResult(
                file=test_file,
                success=True,
                changes_made=3,
                changes=[
                    MigrationChange(1, "old", "new", "import"),
                    MigrationChange(2, "old", "new", "class_name"),
                    MigrationChange(3, "old", "new", "instantiation")
                ]
            )
        ]
    )
    
    report = migrator.generate_report(result, dry_run=False)
    
    assert "**Total Files:** 1" in report
    assert "**Successful:** 1" in report
    assert "**Total Changes:** 3" in report
    assert "100.0%" in report
    assert "test.py" in report


def test_generate_report_dry_run(temp_project, migrator):
    """Test report includes dry run notice."""
    result = BatchMigrationResult(
        total_files=0,
        successful=0,
        failed=0,
        total_changes=0
    )
    
    report = migrator.generate_report(result, dry_run=True)
    
    assert "DRY RUN" in report
    assert "This was a dry run" in report


def test_generate_report_with_failures(temp_project, migrator):
    """Test report includes failure information."""
    test_file = temp_project / "test.py"
    
    result = BatchMigrationResult(
        total_files=1,
        successful=0,
        failed=1,
        total_changes=0,
        results=[
            MigrationResult(
                file=test_file,
                success=False,
                error="File not found"
            )
        ]
    )
    
    report = migrator.generate_report(result, dry_run=False)
    
    assert "**Failed:** 1" in report
    assert "Failed Migrations" in report
    assert "File not found" in report


def test_generate_report_no_changes(temp_project, migrator):
    """Test report for files with no changes."""
    test_file = temp_project / "test.py"
    
    result = BatchMigrationResult(
        total_files=1,
        successful=1,
        failed=0,
        total_changes=0,
        results=[
            MigrationResult(
                file=test_file,
                success=True,
                changes_made=0
            )
        ]
    )
    
    report = migrator.generate_report(result, dry_run=False)
    
    assert "No Changes Required" in report
    assert "already up-to-date" in report


# ============================================================================
# MigrationChange Tests
# ============================================================================

def test_migration_change_init():
    """Test MigrationChange initialization."""
    change = MigrationChange(
        line_number=10,
        original="old code",
        replacement="new code",
        change_type="import"
    )
    
    assert change.line_number == 10
    assert change.original == "old code"
    assert change.replacement == "new code"
    assert change.change_type == "import"


# ============================================================================
# MigrationResult Tests
# ============================================================================

def test_migration_result_has_changes_true():
    """Test MigrationResult.has_changes with changes."""
    result = MigrationResult(
        file=Path("test.py"),
        success=True,
        changes_made=5
    )
    
    assert result.has_changes is True


def test_migration_result_has_changes_false():
    """Test MigrationResult.has_changes without changes."""
    result = MigrationResult(
        file=Path("test.py"),
        success=True,
        changes_made=0
    )
    
    assert result.has_changes is False


# ============================================================================
# BatchMigrationResult Tests
# ============================================================================

def test_batch_result_success_rate():
    """Test BatchMigrationResult.success_rate calculation."""
    result = BatchMigrationResult(
        total_files=10,
        successful=8,
        failed=2,
        total_changes=50
    )
    
    assert result.success_rate == 80.0


def test_batch_result_success_rate_zero_files():
    """Test success rate with zero files."""
    result = BatchMigrationResult(
        total_files=0,
        successful=0,
        failed=0,
        total_changes=0
    )
    
    assert result.success_rate == 0.0


# ============================================================================
# CLI Tests
# ============================================================================

def test_main_with_specific_files(temp_project, monkeypatch, capsys):
    """Test main() with specific files argument."""
    monkeypatch.chdir(temp_project)
    
    # Create test file with deprecated imports that will be detected
    test_file = temp_project / "test.py"
    test_file.write_text("from src.orchestrators.test_orchestrator import TestOrchestrator")
    
    import sys
    monkeypatch.setattr(
        sys,
        'argv',
        ['test_migrator.py', str(test_file), '--dry-run']
    )
    
    from src.operations.modules.realignment.test_migrator import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "DRY RUN" in captured.out
    # File should be processed (may or may not have changes depending on content)


def test_main_no_files(temp_project, monkeypatch, capsys):
    """Test main() when no files need migration."""
    monkeypatch.chdir(temp_project)
    
    import sys
    monkeypatch.setattr(sys, 'argv', ['test_migrator.py', '--dry-run'])
    
    from src.operations.modules.realignment.test_migrator import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 0
    captured = capsys.readouterr()
    assert "No files to migrate" in captured.out


def test_main_exception_handling(tmp_path, monkeypatch, capsys):
    """Test main() handles exceptions gracefully."""
    monkeypatch.chdir(tmp_path)
    
    import sys
    monkeypatch.setattr(sys, 'argv', ['test_migrator.py'])
    
    from src.operations.modules.realignment.test_migrator import main
    
    with pytest.raises(SystemExit) as exc_info:
        main()
    
    assert exc_info.value.code == 2
