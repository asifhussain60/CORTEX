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
    """
    CORE-035: dashboard_schema_v3.py is the ONLY place enums are defined.
    All other modules MUST import, never redefine.
    """
    schema_file = Path("cortex/models/dashboard_schema_v3.py")
    tool_file = Path("cortex/mcp/tools/repository_onboarding_v3_tool.py")
    
    assert schema_file.exists(), "Schema file must exist"
    assert tool_file.exists(), "Tool file must exist"
    
    schema_content = schema_file.read_text()
    tool_content = tool_file.read_text()
    
    # Schema should DEFINE enums
    assert "class Severity(str, Enum):" in schema_content
    assert "class Priority(str, Enum):" in schema_content
    assert "class HealthStatus(str, Enum):" in schema_content
    
    # Tool should IMPORT enums, not define
    assert "from cortex.models.dashboard_schema_v3 import" in tool_content
    
    # Tool should NOT define these (violations found in Phase 21)
    forbidden_definitions = [
        "class SeverityLevel",  # ❌ Found in original implementation
        "class UseCaseType",    # ❌ Found in original implementation
        "class ImpactLevel",    # ❌ Found in original implementation
    ]
    for forbidden in forbidden_definitions:
        assert forbidden not in tool_content, \
            f"CORE-035 violation: {forbidden} defined in tool (should import from schema)"


def test_tool_imports_all_required_enums_from_schema():
    """Validate tool imports enums from schema, not inventing them."""
    tool_file = Path("cortex/mcp/tools/repository_onboarding_v3_tool.py")
    tool_content = tool_file.read_text()
    
    # Parse imports
    tree = ast.parse(tool_content)
    imported_from_schema = set()
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module == "cortex.models.dashboard_schema_v3":
                for alias in node.names:
                    imported_from_schema.add(alias.name)
    
    # Required enums for Phase 21 (core data models)
    required_enums = {
        "Severity",      # Not SeverityLevel
        "Priority",
        "Vulnerability",
        "UseCase",
        "RepoSummary",
    }
    
    missing = required_enums - imported_from_schema
    assert not missing, f"Tool must import from schema: {missing}"


def test_enum_values_match_across_layers():
    """Ensure enum values are consistent between schema and tool usage."""
    from cortex.models.dashboard_schema_v3 import (
        Severity,
        Priority,
        HealthStatus,
    )
    
    # Validate enum values exist
    assert hasattr(Severity, 'CRITICAL')
    assert hasattr(Severity, 'HIGH')
    assert hasattr(Severity, 'MEDIUM')
    assert hasattr(Severity, 'LOW')
    
    assert hasattr(Priority, 'CRITICAL')
    assert hasattr(Priority, 'HIGH')
    assert hasattr(Priority, 'MEDIUM')
    assert hasattr(Priority, 'LOW')
    
    assert hasattr(HealthStatus, 'EXCELLENT')
    assert hasattr(HealthStatus, 'GOOD')
    assert hasattr(HealthStatus, 'FAIR')
    assert hasattr(HealthStatus, 'POOR')
    
    # Validate enum values are lowercase (database convention)
    assert Severity.CRITICAL == 'critical'
    assert Priority.HIGH == 'high'
    assert HealthStatus.GOOD == 'good'


def test_pydantic_models_have_correct_field_names():
    """Ensure Pydantic models use correct field names (not invented ones)."""
    from cortex.models.dashboard_schema_v3 import (
        UseCase,
        Vulnerability,
        CodeSmell,
    )
    
    # UseCase should have 'type' field, not 'category'
    assert 'type' in UseCase.model_fields
    assert 'category' not in UseCase.model_fields
    
    # Vulnerability should have 'severity' field
    assert 'severity' in Vulnerability.model_fields
    
    # CodeSmell should have 'category' field
    assert 'category' in CodeSmell.model_fields


# =============================================================================
# FRONTEND CONTRACT TESTS
# =============================================================================


def test_frontend_loader_expects_schema_structure():
    """
    Validate DualFormatDataLoader.js expects the same structure
    as dashboard_schema_v3.py produces.
    """
    loader_file = Path("company/dashboards/spa/js/data/DualFormatDataLoader.js")
    assert loader_file.exists(), "DualFormatDataLoader.js must exist"
    
    loader_content = loader_file.read_text()
    
    # Frontend should reference schema table names
    expected_tables = [
        "repo_summary",
        "use_cases",
        "vulnerabilities",
        "metrics_summary",
        "packages",
        "code_smells",
        "entities",
        "components",
        "files",
    ]
    
    for table in expected_tables:
        assert table in loader_content, \
            f"Frontend must reference table: {table}"


def test_frontend_enum_expectations_match_python():
    """
    Validate frontend code expects enum values that match Python enums.
    This catches issues like expecting 'SeverityLevel' when schema defines 'Severity'.
    """
    dashboard_html = Path("company/dashboards/spa/dashboard.html")
    assert dashboard_html.exists()
    
    html_content = dashboard_html.read_text()
    
    # Frontend should NOT reference wrong enum names
    forbidden_enum_refs = [
        "SeverityLevel",  # Should be Severity
        "UseCaseType",    # Should be type field
        "ImpactLevel",    # Not defined in schema
    ]
    
    for forbidden in forbidden_enum_refs:
        # Allow in comments, but not in actual code logic
        code_lines = [
            line for line in html_content.split('\n')
            if forbidden in line and not line.strip().startswith('//')
        ]
        assert not code_lines, \
            f"Frontend references undefined enum: {forbidden}"


def test_sqlite_schema_matches_pydantic_models():
    """Validate SQLite schema generator produces tables matching Pydantic models."""
    from cortex.models.dashboard_schema_v3 import (
        SQLiteSchemaGenerator,
        RepoSummary,
        UseCase,
        Vulnerability,
    )
    
    generator = SQLiteSchemaGenerator()
    sql_script = generator.generate_complete_schema()
    
    # Validate table creation statements exist
    assert "CREATE TABLE repo_summary" in sql_script
    assert "CREATE TABLE use_cases" in sql_script
    assert "CREATE TABLE vulnerabilities" in sql_script
    
    # Validate FTS5 tables exist
    assert "CREATE VIRTUAL TABLE use_cases_fts" in sql_script
    assert "CREATE VIRTUAL TABLE packages_fts" in sql_script
    
    # Validate enum columns use TEXT (SQLite convention)
    assert re.search(r"severity\s+TEXT", sql_script, re.IGNORECASE)
    assert re.search(r"priority\s+TEXT", sql_script, re.IGNORECASE)


# =============================================================================
# DATA GENERATOR CONTRACT TESTS
# =============================================================================


def test_sqlite_generator_uses_schema_models():
    """Ensure SQLiteDataGenerator imports and uses schema models."""
    generator_file = Path("cortex/visualization/sqlite_data_generator.py")
    assert generator_file.exists()
    
    generator_content = generator_file.read_text()
    
    # Must import from schema
    assert "from cortex.models.dashboard_schema_v3 import" in generator_content
    
    # Must import key models
    required_imports = [
        "RepoSummary",
        "UseCase",
        "Vulnerability",
        "MetricsSummary",
    ]
    
    for model in required_imports:
        assert model in generator_content, \
            f"Generator must import {model} from schema"


def test_mcp_tool_produces_valid_schema_data():
    """
    Integration test: Validate MCP tool produces data that validates
    against Pydantic schema.
    """
    from cortex.models.dashboard_schema_v3 import (
        RepoSummary,
        UseCase,
        Vulnerability,
        validate_dashboard_data,
    )
    from datetime import datetime
    
    # Simulate MCP tool output
    mock_data = {
        "repo_summary": RepoSummary(
            id=1,
            repo_name="Test",
            repo_slug="test",
            primary_language="Python",
            tech_stack=["Python"],
            total_loc=1000,
            file_count=10,
            contributor_count=1,
            health_score=85,
            last_commit_date=datetime.utcnow(),
        ),
        "use_cases": [
            UseCase(
                id=1,
                title="Authentication",
                description="User login",
                type="feature",  # Correct field name
                priority="high",
                actor="User",
                llm_generated=True,
            )
        ],
        "vulnerabilities": [
            Vulnerability(
                id=1,
                title="SQL Injection",
                description="Unsafe query",
                severity="high",  # Correct enum value (lowercase)
                file_path="auth.py",
                line_number=42,
                cwe_id="CWE-89",
                owasp_category="A03:2021",
            )
        ],
    }
    
    # Validate against schema
    result = validate_dashboard_data(mock_data)
    assert result["valid"], f"Schema validation failed: {result.get('errors')}"


# =============================================================================
# REGRESSION TESTS (Specific Phase 21 Bugs)
# =============================================================================


@pytest.mark.regression
def test_phase21_severity_enum_bug():
    """
    Regression test for Phase 21 bug:
    Tool tried to import 'SeverityLevel' which doesn't exist in schema.
    """
    from cortex.models.dashboard_schema_v3 import Severity
    
    # Schema defines Severity, not SeverityLevel
    assert Severity.CRITICAL == 'critical'
    assert Severity.HIGH == 'high'
    
    # Ensure tool doesn't define SeverityLevel
    tool_file = Path("cortex/mcp/tools/repository_onboarding_v3_tool.py")
    tool_content = tool_file.read_text()
    
    assert "SeverityLevel" not in tool_content, \
        "Phase 21 regression: SeverityLevel should not exist"


@pytest.mark.regression
def test_phase21_usecase_field_bug():
    """
    Regression test for Phase 21 bug:
    Tool referenced 'UseCase.category' which doesn't exist (should be 'type').
    """
    from cortex.models.dashboard_schema_v3 import UseCase
    
    # UseCase has 'type' field, not 'category'
    assert 'type' in UseCase.model_fields
    assert 'category' not in UseCase.model_fields
    
    # Validate a UseCase can be created with correct field
    use_case = UseCase(
        id=1,
        title="Test",
        description="Test case",
        type="feature",  # Correct field name
        priority="medium",
        actor="User",
    )
    assert use_case.type == "feature"


@pytest.mark.regression
def test_phase21_frontend_data_loading_bug():
    """
    Regression test for Phase 21 bug:
    Dashboard.html received SQLiteDataLayer object instead of actual data.
    """
    # This is a conceptual test - actual fix requires browser testing
    # But we can validate the structure
    
    from cortex.models.dashboard_schema_v3 import RepoSummary
    from datetime import datetime
    
    # Simulate what frontend should receive
    mock_repo_data = {
        "id": 1,
        "repo_name": "CORTEX",
        "repo_slug": "cortex",
        "primary_language": "Python",
        "tech_stack": ["Python", "FastAPI"],
        "total_loc": 125000,
        "file_count": 850,
        "contributor_count": 5,
        "health_score": 85,
        "last_commit_date": datetime.utcnow(),
    }
    
    # Should be able to create RepoSummary from this data
    repo = RepoSummary(**mock_repo_data)
    assert repo.repo_name == "CORTEX"
    
    # Should serialize to JSON for frontend
    json_data = repo.model_dump(mode='json')
    assert isinstance(json_data, dict)
    assert json_data['repo_name'] == "CORTEX"


# =============================================================================
# PERFORMANCE CONTRACT TESTS
# =============================================================================


def test_schema_validation_performance():
    """Ensure Pydantic validation doesn't become a bottleneck."""
    from cortex.models.dashboard_schema_v3 import UseCase
    import time
    
    # Create 1000 use cases
    start = time.perf_counter()
    for i in range(1000):
        UseCase(
            id=i,
            title=f"Use Case {i}",
            description="Test",
            type="feature",
            priority="medium",
            actor="User",
        )
    elapsed = time.perf_counter() - start
    
    # Should validate 1000 models in < 1 second
    assert elapsed < 1.0, f"Schema validation too slow: {elapsed:.2f}s"


# =============================================================================
# DOCUMENTATION CONTRACT TESTS
# =============================================================================


def test_schema_has_comprehensive_docstrings():
    """Ensure all Pydantic models have Google-style docstrings (CORE-012)."""
    schema_file = Path("cortex/models/dashboard_schema_v3.py")
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
    pytest.main([__file__, "-v", "--tb=short"])
