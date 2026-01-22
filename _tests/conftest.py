"""
Conftest for docs/_tests directory.

Provides pytest fixtures and configuration for documentation tests,
including automatic logo dimension validation on mkdocs builds.
"""

import pytest
import os
from pathlib import Path


@pytest.fixture(scope="session")
def docs_root():
    """Get the docs directory root."""
    current_dir = Path(__file__).parent
    docs_dir = current_dir.parent  # _tests -> docs
    assert docs_dir.name == "docs", f"Expected docs directory, got {docs_dir}"
    return docs_dir


@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory."""
    current_dir = Path(__file__).parent
    docs_dir = current_dir.parent
    project_dir = docs_dir.parent
    return project_dir


@pytest.fixture(scope="session")
def assets_dir(docs_root):
    """Get the documentation assets directory."""
    assets = docs_root / "assets" / "images"
    assets.mkdir(parents=True, exist_ok=True)
    return assets


def pytest_configure(config):
    """Configure pytest with documentation-specific settings."""
    
    # Register custom markers
    config.addinivalue_line(
        "markers",
        "logo: Logo asset validation tests (dimensions, format, integrity)"
    )
    config.addinivalue_line(
        "markers",
        "assets: Documentation asset tests"
    )
    config.addinivalue_line(
        "markers",
        "integration: Integration tests for mkdocs build artifacts"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test items after collection.
    
    Automatically mark certain tests based on naming patterns.
    """
    for item in items:
        if "logo" in item.nodeid:
            item.add_marker(pytest.mark.logo)
        if "asset" in item.nodeid:
            item.add_marker(pytest.mark.assets)


@pytest.fixture(autouse=True)
def check_logo_before_tests():
    """Automatically verify logo exists before running any tests.
    
    This fixture runs before each test module to ensure the primary
    logo asset is available. Prevents cascading failures.
    """
    docs_dir = Path(__file__).parent.parent
    logo_path = docs_dir / "assets" / "images" / "cortex-logo-200.png"
    
    if not logo_path.exists():
        pytest.skip(f"Logo asset not found: {logo_path}")
    
    yield


# Environment markers for CI/CD integration
def pytest_addoption(parser):
    """Add custom command-line options."""
    parser.addoption(
        "--mkdocs-build",
        action="store_true",
        default=False,
        help="Run logo tests as part of mkdocs build process"
    )


@pytest.fixture
def is_mkdocs_build(request):
    """Check if tests are running as part of mkdocs build."""
    return request.config.getoption("--mkdocs-build")
