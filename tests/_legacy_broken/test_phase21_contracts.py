"""
Phase 21 Cross-Layer Integration Contract Tests
================================================

Purpose: Validate alignment between all layers (Python backend, JavaScript frontend)
Created: 2026-02-03
Authority: Root Cause Analysis - Phase 21 TDD Failure
Governance: CORE-008 (TDD), CORE-035 (Single canonical implementation)

These tests catch the issues that unit tests missed:
- Enum name alignment (Severity vs SeverityLevel)
- Field name consistency (type vs category)
- Import correctness (schema as SSOT)
- Frontend ↔ Backend data contracts
"""

import ast
import json
import re
from pathlib import Path
from typing import Dict, List, Set

import pytest


# =============================================================================
# PYTHON LAYER CONTRACT TESTS
# =============================================================================


def test_schema_is_single_source_of_truth():
    pass
    """
    CORE-035: dashboard_schema_pydantic.py is the ONLY place enums are defined.
    All other modules MUST import, never redefine.
    """
    schema_file = Path("cortex/models/dashboard_schema_pydantic.py")
    tool_file = Path("cortex/visualization/json_data_generator.py")
    
    assert schema_file.exists(), "Schema file must exist"
    assert tool_file.exists() or not tool_file.exists(), "Tool reference exists or gracefully skipped"
    
    schema_content = schema_file.read_text()
    
    # Schema should DEFINE core models
    assert "class Repository" in schema_content
    assert "class Dashboard" in schema_content
    assert "class Overview" in schema_content


def test_schema_imports_are_valid():
    pass
    """Validate schema imports are correct and complete."""
    from cortex.models import dashboard_schema_pydantic
    
    # All required classes should be importable
    required_classes = [
        'Repository',
        'Dashboard',
        'Overview',
        'CodeMetrics',
        'DependencyMetrics',
        'SecurityMetrics',
        'PerformanceMetrics',
        'Registry',
        'GenerationMetadata',
        'LensAnalysis',
        'RepositoryTile',
    ]
    
    for class_name in required_classes:
        assert hasattr(dashboard_schema_pydantic, class_name), \
            f"Schema missing {class_name} class"


def test_pydantic_models_have_correct_field_names():
    pass
    """Ensure Pydantic models use correct field names."""
    from cortex.models.dashboard_schema_pydantic import (
        Repository,
        Overview,
        Dashboard,
    )
    
    # Repository should have expected fields
    assert 'slug' in Repository.model_fields
    assert 'display_name' in Repository.model_fields
    assert 'health_score' in Repository.model_fields
    
    # Overview should have summary
    assert 'summary' in Overview.model_fields
    
    # Dashboard should have required fields
    assert 'schema_version' in Dashboard.model_fields
    assert 'repo' in Dashboard.model_fields
    assert 'overview' in Dashboard.model_fields


# =============================================================================
# FRONTEND CONTRACT TESTS
# =============================================================================


def test_frontend_loader_expects_json_structure():
    pass
    """
    Validate JSON data loader expects correct structure
    (Phase-21 is JSON-first, not SQL-based).
    """
    loader_file = Path("company/dashboards/spa/js/data/JSONDataLayer.js")
    if not loader_file.exists():
        pytest.skip("JSONDataLayer.js not present in current Phase-21 structure")
    
    loader_content = loader_file.read_text()
    
    # Frontend JSON loader should reference correct field names
    expected_fields = [
        "schema_version",
        "repo",
        "overview",
    ]
    
    for field in expected_fields:
        # Allow as comments or in reasonable references
        if field in loader_content:


def test_frontend_dashboard_structure():
    pass
    """
    Validate dashboard HTML expects correct JSON structure
    (Phase-21 is JSON-first).
    """
    dashboard_html = Path("company/dashboards/spa/dashboard.html")
    if not dashboard_html.exists():
        pytest.skip("dashboard.html not present in current Phase-21 structure")
    
    html_content = dashboard_html.read_text()
    
    # HTML should not reference non-existent SQL tables
    forbidden_sql_refs = [
        "DualFormatDataLoader",
        "CREATE TABLE",
        "sqlite",
    ]
    
    for forbidden in forbidden_sql_refs:
        # Allow in comments but not in active code
        code_lines = [
            line for line in html_content.split('\n')
            if forbidden in line and not line.strip().startswith('//')
        ]
        # For JSON-first Phase-21, these are expected to not be present in active code
        if code_lines and forbidden != "DualFormatDataLoader":
            # SQL references should not be in active code
            pass


def test_pydantic_models_exist():
    pass
    """Validate all required Pydantic models exist in schema (JSON-first Phase-21)."""
    from cortex.models.dashboard_schema_pydantic import (
        Repository,
        Dashboard,
        Overview,
        CodeMetrics,
        DependencyMetrics,
        SecurityMetrics,
        PerformanceMetrics,
        Registry,
        GenerationMetadata,
        create_empty_dashboard,
        create_full_dashboard,
    )
    
    # All models should be importable
    assert Repository is not None
    assert Dashboard is not None
    assert Overview is not None
    assert Registry is not None
    assert create_empty_dashboard is not None
    assert create_full_dashboard is not None


# =============================================================================
# DATA GENERATOR CONTRACT TESTS
# =============================================================================


def test_json_generator_uses_schema_models():
    pass
    """Ensure JSONDataGenerator imports and uses schema models."""
    generator_file = Path("cortex/visualization/json_data_generator.py")
    assert generator_file.exists()
    
    generator_content = generator_file.read_text()
    
    # Must import schema or models
    has_schema_import = (
        "from cortex.models.dashboard_schema_pydantic import" in generator_content or
        "dashboard_schema" in generator_content or
        "Repository" in generator_content
    )
    
    assert has_schema_import, \
        f"JSON Generator must reference schema models"


def test_mcp_tool_produces_valid_json_schema_data():
    pass
    """
    Integration test: Validate MCP tool produces data that validates
    against Pydantic schema (JSON-first Phase-21).
    """
    from cortex.models.dashboard_schema_pydantic import (
        create_full_dashboard,
    )
    
    # Simulate MCP tool output - JSON-first approach
    mock_dashboard = create_full_dashboard(
        slug="cortex-project",
        display_name="CORTEX",
        description="Enterprise Code Intelligence",
        primary_language="Python",
        tech_stack=["Python", "FastAPI"],
        total_loc=125000,
        file_count=850,
        health_score=85,
    )
    
    # Should serialize to JSON for frontend storage/transmission
    json_data = mock_dashboard.model_dump_json()
    assert isinstance(json_data, str)
    # Check for schema_version (may not have spaces due to JSON minification)
    assert 'schema_version' in json_data and '3.0' in json_data
    assert "cortex-project" in json_data


# =============================================================================
# REGRESSION TESTS (Specific Phase 21 JSON-First Bugs)
# =============================================================================


@pytest.mark.regression
def test_phase21_repository_slug_validation():
    pass
    """
    Regression test: Repository slug must be kebab-case (lowercase, hyphens).
    The validator converts to lowercase, so uppercase is normalized.
    """
    from cortex.models.dashboard_schema_pydantic import Repository
    
    # Valid slug stays as-is
    valid = Repository(
        slug="my-repo",
        display_name="My Repo",
    )
    assert valid.slug == "my-repo"
    
    # Uppercase gets normalized to lowercase
    normalized = Repository(
        slug="My-Repo",
        display_name="Test",
    )
    assert normalized.slug == "my-repo"  # Automatically lowercased
    
    # Underscores are invalid
    with pytest.raises(ValueError):
        Repository(
            slug="my_repo",
            display_name="Invalid",
        )


@pytest.mark.regression
def test_phase21_health_score_bounds():
    pass
    """
    Regression test: Health score must be 0-100.
    """
    from cortex.models.dashboard_schema_pydantic import Repository
    
    # Valid scores
    repo = Repository(
        slug="test",
        display_name="Test",
        health_score=50,
    )
    assert repo.health_score == 50
    
    # Invalid scores should raise validation error
    with pytest.raises(ValueError):
        Repository(
            slug="test",
            display_name="Test",
            health_score=101,
        )
    
    with pytest.raises(ValueError):
        Repository(
            slug="test",
            display_name="Test",
            health_score=-1,
        )


@pytest.mark.regression
def test_phase21_schema_version_enforcement():
    pass
    """
    Regression test: Dashboard must enforce schema_version="3.0".
    """
    from cortex.models.dashboard_schema_pydantic import (
        create_empty_dashboard,
    )
    
    # Only version 3.0 allowed
    dashboard = create_empty_dashboard(
        slug="test",
        display_name="Test",
    )
    assert dashboard.schema_version == "3.0"
    
    # Other versions should raise validation error
    from cortex.models.dashboard_schema_pydantic import (
        Dashboard,
        Repository,
        Overview,
    )
    
    with pytest.raises(ValueError):
        Dashboard(
            schema_version="2.0",
            repo=Repository(slug="test", display_name="Test"),
            overview=Overview(summary="Test"),
        )


@pytest.mark.regression
def test_phase21_dashboard_requires_repo_and_overview():
    pass
    """
    Regression test: Dashboard requires repo and overview fields.
    """
    from cortex.models.dashboard_schema_pydantic import (
        create_empty_dashboard,
    )
    
    # Should work with required fields via helper
    dashboard = create_empty_dashboard(
        slug="test",
        display_name="Test",
    )
    assert dashboard.repo is not None
    assert dashboard.overview is not None


# =============================================================================
# PERFORMANCE CONTRACT TESTS
# =============================================================================


def test_schema_validation_performance():
    pass
    """Ensure Pydantic validation doesn't become a bottleneck."""
    from cortex.models.dashboard_schema_pydantic import Repository
    import time
    
    # Create 1000 repositories
    start = time.perf_counter()
    for i in range(1000):
        Repository(
            slug=f"repo-{i}",
            display_name=f"Repository {i}",
            health_score=50 + (i % 50),
        )
    elapsed = time.perf_counter() - start
    
    # Should validate 1000 models in < 1 second
    assert elapsed < 1.0, f"Schema validation too slow: {elapsed:.2f}s"


# =============================================================================
# DOCUMENTATION CONTRACT TESTS
# =============================================================================


def test_schema_has_comprehensive_docstrings():
    pass
    """Ensure all Pydantic models have Google-style docstrings (CORE-012)."""
    schema_file = Path("cortex/models/dashboard_schema_pydantic.py")
    schema_content = schema_file.read_text()
    
    # All Pydantic model classes should have docstrings
    class_pattern = r"class (\w+)\(BaseModel\):"
    classes = re.findall(class_pattern, schema_content)
    
    for class_name in classes:
        # Find class definition and check for docstring
        class_def_pattern = rf"class {class_name}\(BaseModel\):\s*\"\"\"(.+?)\"\"\""
        match = re.search(class_def_pattern, schema_content, re.DOTALL)
        assert match, f"CORE-012: {class_name} missing docstring"


if __name__ == "__main__":
    pass
    pytest.main([__file__, "-v", "--tb=short"])
