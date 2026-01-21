"""
Pytest Configuration - Minimal for Migrated Structure

Shared fixtures and configuration for all tests.
Handles both old (src/, cortex_brain/) and new (cortex/) structures gracefully.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import sys
import tempfile
import sqlite3
from pathlib import Path
from typing import Generator

import pytest

# Add all possible paths to Python path to support both structures
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "cortex"))  # New structure
sys.path.insert(0, str(project_root / "src"))     # Old structure (if exists)
sys.path.insert(0, str(project_root / "cortex_brain"))  # Tier structure (if exists)
sys.path.insert(0, str(project_root))  # Project root

# Register CORTEX test audit plugin for performance monitoring
def pytest_configure(config):
    """Configure pytest."""
    try:
        from cortex.testing.pytest_plugin_audit import cortex_test_audit_plugin
        config.pluginmanager.register(cortex_test_audit_plugin, name="cortex_test_audit")
    except Exception as e:
        # Plugin not available or import failed, continue without it
        import sys
        print(f"Note: Test audit plugin not loaded ({type(e).__name__})", file=sys.stderr)


@pytest.fixture
def temp_dir():
    """Provide a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_yaml_file(temp_dir):
    """Create a sample YAML file for testing."""
    yaml_content = """
name: test
version: "1.0"
settings:
  debug: true
  level: info
items:
  - one
  - two
  - three
"""
    yaml_path = temp_dir / "test.yaml"
    yaml_path.write_text(yaml_content)
    return yaml_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create a sample JSON file for testing."""
    import json
    
    data = {
        "name": "test",
        "version": "1.0",
        "items": ["one", "two", "three"]
    }
    
    json_path = temp_dir / "test.json"
    json_path.write_text(json.dumps(data, indent=2))
    return json_path


@pytest.fixture
def temp_project_dir(temp_dir):
    """Create a minimal project structure for testing."""
    cortex_dir = temp_dir / "cortex"
    cortex_dir.mkdir()
    
    # Create minimal structure
    for module in ['core', 'brain', 'api']:
        module_dir = cortex_dir / module
        module_dir.mkdir()
        (module_dir / "__init__.py").touch()
    
    return cortex_dir


@pytest.fixture(autouse=True)
def cleanup_db_connections():
    """Cleanup database connections between tests.
    
    Ensures proper cleanup of database connections to prevent
    pool exhaustion and connection leaks during integration testing.
    """
    yield
    
    # Cleanup after test
    try:
        from cortex_brain.tier0.state import get_db_pool
        pool = get_db_pool()
        pool.dispose()  # Clear exhausted connections
    except Exception:
        # Silently ignore if pool doesn't exist or cleanup fails
        pass


@pytest.fixture(autouse=True)
def reset_db_env():
    """Reset database environment variables between tests."""
    yield
    
    # Reset pool size to defaults
    for var in ['DB_POOL_SIZE', 'DB_MAX_OVERFLOW', 'DB_POOL_TIMEOUT']:
        if var in os.environ:
            del os.environ[var]


@pytest.fixture
def test_db_path(temp_dir):
    """Provide a temporary SQLite database path for testing.
    
    Creates a temporary SQLite database file that can be used
    by tests that require database connectivity.
    """
    db_path = temp_dir / "test.db"
    
    # Create empty database
    conn = sqlite3.connect(str(db_path))
    conn.close()
    
    return db_path