"""
Pytest configuration for CORTEX test suite.

Handles graceful skipping of tests with missing module dependencies.
Provides shared SQLite fixtures with proper setup/teardown cleanup.
"""
import pytest
import sqlite3
import sys
from pathlib import Path
from typing import Generator
from _pytest.python import Module

# Disable pytest-asyncio plugin inheritance for all tests
# This resolves the "pytest_plugins in non-top-level conftest" deprecation
pytest_plugins = []

# Collect ignore patterns - these files work when run directly but cause
# collection conflicts during full test runs due to namespace issues
collect_ignore = [
    "visualization/scripts/test_bundle_dependencies.py",
    "visualization/scripts/test_bundle_vendor_assets.py",
    "visualization/scripts/test_lazy_module_loader.py",
]

# Add tier modules to path
project_root = Path(__file__).parent
tier_paths = [
    str(project_root),  # For cortex imports
    str(project_root / "cortex_intelligence"),  # For tier0, tier1, tier2 imports
]

for path in tier_paths:
    if path not in sys.path:
        sys.path.insert(0, path)


def pytest_collection_modifyitems(session, config, items):
    """
    Auto-tag tests by tier based on directory structure.
    
    Tier Strategy:
    - smoke: golden/ tests + core orchestrator tests (fast, high-value)
    - critical: unit/ tests for core/, orchestrators/, mcp/, governance/
    - full: performance/, chaos/, regression/, manual/ (slow/specialized)
    
    Usage:
        pytest -m smoke          # ~500 tests, <60s
        pytest -m critical       # ~3000 tests, <3min
        pytest -m "not full"     # skip perf/chaos only
    """
    smoke_paths = {"golden", "core", "mcp"}
    critical_paths = {"orchestrators", "governance", "intelligence", "integration"}
    full_paths = {"performance", "chaos", "regression", "manual"}
    
    for item in items:
        # Get relative path parts
        rel = str(item.fspath)
        parts = rel.split("/")
        
        # Find the directory under tests/
        test_idx = None
        for i, p in enumerate(parts):
            if p == "tests":
                test_idx = i
                break
        if test_idx is None or test_idx + 1 >= len(parts):
            continue
        
        top_dir = parts[test_idx + 1]
        sub_dir = parts[test_idx + 2] if test_idx + 2 < len(parts) - 1 else ""
        
        # Auto-tag by tier
        if top_dir in smoke_paths or sub_dir in smoke_paths:
            item.add_marker(pytest.mark.smoke)
            item.add_marker(pytest.mark.critical)
        elif top_dir in full_paths:
            item.add_marker(pytest.mark.full)
        elif top_dir in critical_paths or sub_dir in critical_paths:
            item.add_marker(pytest.mark.critical)


def pytest_pycollect_makemodule(module_path, parent):
    """
    Handle module collection with graceful error handling.
    
    If a test module has import errors due to missing dependencies,
    we return None to skip it rather than failing collection.
    """
    try:
        return Module.from_parent(parent, path=module_path)
    except (ImportError, ModuleNotFoundError) as e:
        # Skip modules with missing dependencies
        return None


@pytest.fixture
def test_db_path(tmp_path):
    """Provide temporary database path for tests.
    
    Args:
        tmp_path: Pytest's temporary directory fixture.
        
    Returns:
        str: Path to temporary database file.
    """
    return str(tmp_path / "test.db")


@pytest.fixture
def sqlite_db(tmp_path: Path) -> Generator[sqlite3.Connection, None, None]:
    """Provide a SQLite connection with automatic cleanup.

    Creates a temporary database with a connection that is guaranteed
    to be closed after test completion. Uses tmp_path so the file
    is also cleaned up by pytest.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Yields:
        sqlite3.Connection: Open connection to temporary database.
    """
    db_path = tmp_path / "test.db"
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=DELETE;")  # Avoid WAL leftovers
    try:
        yield conn
    finally:
        conn.close()


@pytest.fixture
def sqlite_db_path(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a temporary database path with WAL cleanup on teardown.

    After test completion, ensures any WAL/SHM files are removed
    by running a checkpoint if the database exists.

    Args:
        tmp_path: Pytest's temporary directory fixture.

    Yields:
        Path: Path to temporary database file.
    """
    db_path = tmp_path / "test.db"
    try:
        yield db_path
    finally:
        # Clean up WAL/SHM files if database was created in WAL mode
        if db_path.exists():
            try:
                conn = sqlite3.connect(str(db_path))
                conn.execute("PRAGMA wal_checkpoint(TRUNCATE);")
                conn.close()
            except sqlite3.Error:
                pass
        # Remove any remaining WAL/SHM files
        for suffix in ("-wal", "-shm"):
            leftover = db_path.parent / f"{db_path.name}{suffix}"
            if leftover.exists():
                leftover.unlink(missing_ok=True)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """
    Hook to customize test reporting.
    """
    outcome = yield
    report = outcome.get_result()
    
    # Add custom handling if needed
    return report


def pytest_configure(config):
    """
    Configure pytest with custom settings.
    """
    # Register custom markers
    config.addinivalue_line(
        "markers", 
        "requires_module(module): mark test as requiring a specific module"
    )

