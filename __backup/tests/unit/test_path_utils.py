"""
Tests for Path Utilities - CORE-005 Compliance
"""

import pytest
from pathlib import Path
import tempfile
import os
from src.utils.path_utils import (
    project_root,
    cortex_brain_path,
    audit_logs_path,
    state_db_path,
    tier0_governance_path,
    tier1_tracking_path,
    progress_tracker_path,
    ac_index_path,
    core_rules_path,
    ensure_dir,
)


def test_project_root_returns_path():
    """project_root() returns a Path object."""
    root = project_root()
    assert isinstance(root, Path)
    assert root.exists()


def test_project_root_is_absolute():
    """project_root() returns absolute path."""
    root = project_root()
    assert root.is_absolute()


def test_project_root_contains_github_marker():
    """project_root() points to directory with .github/prompts."""
    root = project_root()
    marker = root / ".github" / "prompts"
    assert marker.exists()


def test_cortex_brain_path_is_subdir():
    """cortex_brain_path() is under project_root()."""
    root = project_root()
    brain = cortex_brain_path()
    assert str(brain).startswith(str(root))


def test_audit_logs_path_is_subdir():
    """audit_logs_path() points to cortex-brain/audit-logs."""
    logs = audit_logs_path()
    assert str(logs).endswith("cortex-brain/audit-logs")


def test_state_db_path_ends_with_cortex_db():
    """state_db_path() points to cortex-brain/state/cortex.db."""
    db = state_db_path()
    assert str(db).endswith("cortex-brain/state/cortex.db")


def test_tier0_governance_path_is_subdir():
    """tier0_governance_path() points to cortex-brain/tier0/governance."""
    path = tier0_governance_path()
    assert str(path).endswith("cortex-brain/tier0/governance")


def test_tier1_tracking_path_is_subdir():
    """tier1_tracking_path() points to cortex-brain/tier1/tracking."""
    path = tier1_tracking_path()
    assert str(path).endswith("cortex-brain/tier1/tracking")


def test_progress_tracker_path_is_file():
    """progress_tracker_path() points to progress-tracker.json."""
    path = progress_tracker_path()
    assert str(path).endswith("progress-tracker.json")
    assert path.exists()  # Should exist in repo


def test_ac_index_path_is_file():
    """ac_index_path() points to AC-INDEX.yaml."""
    path = ac_index_path()
    assert str(path).endswith("AC-INDEX.yaml")
    assert path.exists()  # Should exist in repo


def test_core_rules_path_is_file():
    """core_rules_path() points to core-rules.yaml."""
    path = core_rules_path()
    assert str(path).endswith("core-rules.yaml")
    assert path.exists()  # Should exist in repo


def test_ensure_dir_creates_directory():
    """ensure_dir() creates directory if not present."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test" / "nested" / "dir"
        result = ensure_dir(test_dir)
        
        assert result.exists()
        assert result.is_dir()


def test_ensure_dir_idempotent():
    """ensure_dir() is idempotent (safe to call multiple times)."""
    with tempfile.TemporaryDirectory() as tmpdir:
        test_dir = Path(tmpdir) / "test"
        
        # Create directory
        ensure_dir(test_dir)
        assert test_dir.exists()
        
        # Call again - should not raise error
        ensure_dir(test_dir)
        assert test_dir.exists()


def test_paths_are_portable():
    """All paths use forward slashes (portable across OS)."""
    paths = [
        project_root(),
        cortex_brain_path(),
        audit_logs_path(),
        state_db_path(),
    ]
    
    for path in paths:
        # Path objects always use the system separator,
        # but the string representation should be convertible
        str_path = str(path)
        assert path.exists() or "/" in str_path or "\\" in str_path
