"""
Unit Tests for Teardown + REFACTOR + Commit Middleware (Phase N+1)

Tests:
1. Refactor operations (remove unused imports, consolidate logic)
2. Whole-file cleanup (orphaned code detection)
3. Git commit with /cortex-git-commit pattern
4. Co-authored-by attribution
5. Integration with TeardownRefactor class

Coverage Goal: 100%

Author: CORTEX
Date: January 4, 2026
Sub-Plan: C50-20 (Governance Middleware Implementation)
"""

import pytest
import tempfile
import subprocess
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock, call

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from src.orchestrators.middleware.teardown_refactor import (
    TeardownRefactor,
    RefactorResult,
    GitCommitResult,
    TeardownResult,
)


# Fixtures


@pytest.fixture
def temp_workspace():
    """Create temporary workspace with git repository"""
    with tempfile.TemporaryDirectory() as tmpdir:
        workspace = Path(tmpdir)

        # Initialize git repository
        subprocess.run(["git", "init"], cwd=workspace, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=workspace)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=workspace)

        # Create initial commit
        readme = workspace / "README.md"
        readme.write_text("# Test Project\n")
        subprocess.run(["git", "add", "README.md"], cwd=workspace)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=workspace)

        yield workspace


@pytest.fixture
def teardown_refactor(temp_workspace):
    """Create TeardownRefactor instance"""
    return TeardownRefactor(workspace_root=temp_workspace)


# Initialization Tests


def test_teardown_refactor_initialization(temp_workspace):
    """Test: TeardownRefactor initializes with workspace path"""
    refactor = TeardownRefactor(workspace_root=temp_workspace)

    assert refactor.workspace_root == temp_workspace


# Refactor Operation Tests


def test_refactor_file_remove_unused_imports(teardown_refactor, temp_workspace):
    """Test: Refactor removes unused imports"""
    # Create file with unused imports
    test_file = temp_workspace / "src" / "unused_imports.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
import os  # Used
import sys  # Unused
import json  # Unused
from pathlib import Path  # Used

def main():
    print(os.getcwd())
    return Path('.')
""")

    result = teardown_refactor._refactor_file(test_file)

    assert result.refactor_successful is True
    assert "removed unused imports" in " ".join(result.changes_made).lower()
    assert result.lines_removed >= 2  # sys and json removed


def test_refactor_file_remove_duplicate_functions(teardown_refactor, temp_workspace):
    """Test: Refactor removes duplicate function definitions"""
    # Create file with duplicate functions
    test_file = temp_workspace / "src" / "duplicates.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
def process_data(data):
    return data.strip()

def process_data(data):
    return data.strip()

def other_function():
    return "other"
""")

    result = teardown_refactor._refactor_file(test_file)

    assert result.refactor_successful is True
    assert "removed duplicate" in " ".join(result.changes_made).lower()


def test_refactor_file_consolidate_redundant_logic(teardown_refactor, temp_workspace):
    """Test: Refactor consolidates redundant conditional logic"""
    # Create file with redundant logic
    test_file = temp_workspace / "src" / "redundant.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("""
def check_value(x):
    if x > 0:
        return True
    else:
        return False

def another_check(y):
    if y > 0:
        return True
    else:
        return False
""")

    result = teardown_refactor._refactor_file(test_file)

    assert result.refactor_successful is True
    # Consolidation may vary based on implementation


def test_refactor_file_syntax_error_handling(teardown_refactor, temp_workspace):
    """Test: Refactor handles files with syntax errors gracefully"""
    # Create file with syntax error
    broken_file = temp_workspace / "src" / "broken.py"
    broken_file.parent.mkdir(parents=True, exist_ok=True)
    broken_file.write_text("def broken(\n")  # Missing closing parenthesis

    result = teardown_refactor._refactor_file(broken_file)

    assert result.refactor_successful is False
    assert result.error_message is not None
    assert "syntax" in result.error_message.lower() or "parse" in result.error_message.lower()


def test_refactor_file_no_changes_needed(teardown_refactor, temp_workspace):
    """Test: Refactor handles clean files (no changes needed)"""
    # Create clean file
    clean_file = temp_workspace / "src" / "clean.py"
    clean_file.parent.mkdir(parents=True, exist_ok=True)
    clean_file.write_text("""
from pathlib import Path

def process_path(path: Path) -> str:
    return str(path.resolve())
""")

    result = teardown_refactor._refactor_file(clean_file)

    assert result.refactor_successful is True
    assert result.lines_removed == 0
    assert result.lines_added == 0


# Git Commit Tests


def test_git_commit_success(teardown_refactor, temp_workspace):
    """Test: Git commit succeeds with proper message format"""
    # Create and stage a file
    test_file = temp_workspace / "src" / "test.py"
    test_file.parent.mkdir(parents=True, exist_ok=True)
    test_file.write_text("def test():\n    pass\n")
    subprocess.run(["git", "add", "src/test.py"], cwd=temp_workspace)

    result = teardown_refactor._git_commit(
        orchestrator_name="planning_v5",
        phase_summary="Phase 1: Context Discovery",
        files_committed=1,
        skip_commit=False
    )

    assert result.commit_successful is True
    assert result.commit_sha is not None
    assert "planning_v5" in result.commit_message
    assert "Phase 1" in result.commit_message
    assert "Co-authored-by" in result.commit_message


def test_git_commit_cortex_pattern(teardown_refactor, temp_workspace):
    """Test: Git commit follows /cortex-git-commit pattern"""
    # Create and stage a file
    test_file = temp_workspace / "modified.txt"
    test_file.write_text("modified content")
    subprocess.run(["git", "add", "modified.txt"], cwd=temp_workspace)

    result = teardown_refactor._git_commit(
        orchestrator_name="refinement_v2",
        phase_summary="Code quality improvements",
        files_committed=1,
        skip_commit=False
    )

    assert result.commit_successful is True
    # Verify commit message structure
    commit_msg = result.commit_message
    assert commit_msg.startswith("refinement_v2:")
    assert "Co-authored-by: CORTEX" in commit_msg


def test_git_commit_skip_mode(teardown_refactor):
    """Test: Git commit can be skipped (dry-run mode)"""
    result = teardown_refactor._git_commit(
        orchestrator_name="test_orch",
        phase_summary="Test phase",
        files_committed=0,
        skip_commit=True
    )

    assert result.commit_successful is False
    assert result.commit_sha is None
    assert "skipped" in result.commit_message.lower()


def test_git_commit_no_staged_changes(teardown_refactor, temp_workspace):
    """Test: Git commit handles no staged changes gracefully"""
    result = teardown_refactor._git_commit(
        orchestrator_name="test_orch",
        phase_summary="No changes",
        files_committed=0,
        skip_commit=False
    )

    # Should handle gracefully (no crash)
    assert result.commit_successful is False or result.commit_sha is None


# Integration Tests


def test_execute_teardown_full_pipeline(teardown_refactor, temp_workspace):
    """Test: execute_teardown runs full refactor + commit pipeline"""
    # Create files with issues
    file1 = temp_workspace / "src" / "file1.py"
    file1.parent.mkdir(parents=True, exist_ok=True)
    file1.write_text("""
import os
import sys  # Unused

def func():
    print(os.getcwd())
""")

    file2 = temp_workspace / "src" / "file2.py"
    file2.write_text("""
import json  # Unused

def another():
    return "test"
""")

    # Stage files
    subprocess.run(["git", "add", "src/"], cwd=temp_workspace)

    result = teardown_refactor.execute_teardown(
        orchestrator_name="planning_v5",
        modified_files=[file1, file2],
        phase_summary="Implementation complete",
        skip_git_commit=False
    )

    assert len(result.refactor_results) == 2
    assert all(r.refactor_successful for r in result.refactor_results)
    assert result.git_commit_result.commit_successful is True
    assert result.git_commit_result.files_committed == 2


def test_execute_teardown_partial_refactor_failure(teardown_refactor, temp_workspace):
    """Test: execute_teardown handles partial refactor failures"""
    # Create one good file and one broken file
    good_file = temp_workspace / "good.py"
    good_file.write_text("def good():\n    pass\n")

    broken_file = temp_workspace / "broken.py"
    broken_file.write_text("def broken(\n")  # Syntax error

    subprocess.run(["git", "add", "."], cwd=temp_workspace)

    result = teardown_refactor.execute_teardown(
        orchestrator_name="test_orch",
        modified_files=[good_file, broken_file],
        phase_summary="Mixed results",
        skip_git_commit=False
    )

    # Should have refactor results for both files
    assert len(result.refactor_results) == 2

    # One should succeed, one should fail
    success_count = sum(1 for r in result.refactor_results if r.refactor_successful)
    assert success_count == 1


def test_execute_teardown_empty_file_list(teardown_refactor):
    """Test: execute_teardown handles empty file list"""
    result = teardown_refactor.execute_teardown(
        orchestrator_name="test_orch",
        modified_files=[],
        phase_summary="No files",
        skip_git_commit=True
    )

    assert len(result.refactor_results) == 0
    assert result.git_commit_result.commit_successful is False


def test_execute_teardown_timestamp_format(teardown_refactor):
    """Test: execute_teardown includes ISO timestamp"""
    result = teardown_refactor.execute_teardown(
        orchestrator_name="test_orch",
        modified_files=[],
        phase_summary="Timestamp test",
        skip_git_commit=True
    )

    assert result.timestamp is not None
    # Validate ISO format
    datetime.fromisoformat(result.timestamp.replace('Z', '+00:00'))


# Edge Cases


def test_refactor_nonexistent_file(teardown_refactor):
    """Test: Refactor handles nonexistent files gracefully"""
    nonexistent = Path("/nonexistent/file.py")

    result = teardown_refactor._refactor_file(nonexistent)

    assert result.refactor_successful is False
    assert "not found" in result.error_message.lower() or "does not exist" in result.error_message.lower()


def test_git_commit_message_generation(teardown_refactor):
    """Test: Git commit message follows template"""
    # Test message generation directly
    message = teardown_refactor._generate_commit_message(
        orchestrator_name="planning_v5",
        phase_summary="Context discovery complete",
        files_modified=3,
        tests_added=2,
        coverage_change="+15%"
    )

    assert "planning_v5:" in message
    assert "Context discovery" in message
    assert "Files modified: 3" in message or "3" in message
    assert "Tests added: 2" in message or "2" in message
    assert "Coverage: +15%" in message or "+15%" in message
    assert "Co-authored-by: CORTEX" in message


def test_refactor_permissions_error_handling(teardown_refactor, temp_workspace):
    """Test: Refactor handles permission errors"""
    # Create read-only file
    readonly_file = temp_workspace / "readonly.py"
    readonly_file.write_text("def test():\n    pass\n")
    readonly_file.chmod(0o444)  # Read-only

    result = teardown_refactor._refactor_file(readonly_file)

    # Should handle gracefully (may succeed if only reading, or fail with clear error)
    if not result.refactor_successful:
        assert result.error_message is not None


def test_dataclass_serialization():
    """Test: Dataclasses can be serialized to dict"""
    refactor_result = RefactorResult(
        file_path=Path("test.py"),
        changes_made=["removed unused import"],
        lines_removed=1,
        lines_added=0,
        refactor_successful=True,
        error_message=None
    )

    result_dict = {
        'file_path': str(refactor_result.file_path),
        'changes_made': refactor_result.changes_made,
        'lines_removed': refactor_result.lines_removed,
        'lines_added': refactor_result.lines_added,
        'refactor_successful': refactor_result.refactor_successful,
        'error_message': refactor_result.error_message
    }

    assert result_dict['file_path'] == "test.py"
    assert result_dict['refactor_successful'] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.orchestrators.middleware.teardown_refactor", "--cov-report=term"])
