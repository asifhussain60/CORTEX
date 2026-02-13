"""
Fixtures for integration tests.
"""

import pytest
import importlib.util
from pathlib import Path


@pytest.fixture
def setup_mcp():
    """Fixture to load and provide the setup-mcp.py module."""
    setup_mcp_path = Path(".cortex/setup-mcp.py")
    
    if not setup_mcp_path.exists():
        pytest.skip(f"setup-mcp.py not found at {setup_mcp_path}")
    
    spec = importlib.util.spec_from_file_location("setup_mcp", setup_mcp_path)
    if spec is None or spec.loader is None:
        pytest.skip("Could not load setup-mcp.py module spec")
    
    setup_mcp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(setup_mcp_module)
    
    return setup_mcp_module
