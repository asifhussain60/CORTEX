"""
Pytest Configuration - Minimal for Migrated Structure

Shared fixtures and configuration for all tests.
Handles both old (src/, cortex-brain/) and new (cortex/) structures gracefully.

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

# Add cortex to Python path
sys.path.insert(0, str(Path(__file__).parent.parent / "cortex"))
sys.path.insert(0, str(Path(__file__).parent.parent))

# Disable audit logger for migration - too many import issues
# Will re-enable after all imports are updated
def pytest_configure(config):
    """Configure pytest."""
    pass  # Minimal configuration


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
