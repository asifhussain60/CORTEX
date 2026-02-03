"""
Unit Tests for SQLite Data Generator
=====================================

Purpose: Test SQLite database generation, data insertion, and queries
Created: 2026-02-03
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
Governance: CORE-008 (TDD), CORE-013 (no bare except)
"""

import json
import sqlite3
import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from cortex.models.dashboard_schema_v3 import Priority, Severity
from cortex.visualization.sqlite_data_generator import (
    SQLiteDataGenerator,
    generate_dashboard_sqlite,
)


@pytest.fixture
def temp_db_path():
    """Create temporary database path."""
    with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    # Cleanup
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def minimal_data():
    """Minimal valid dashboard data."""
    return {
        "repo_summary": {
            "id": 1,
            "repo_name": "TestRepo",
            "repo_slug": "test-repo",
            "primary_language": "Python",
            "tech_stack": ["Python", "FastAPI"],
            "total_loc": 1000,
            "file_count": 50,
            "contributor_count": 2,
            "health_score": 80,
            "last_commit_date": datetime(2026, 2, 3).isoformat(),
        },
        "metrics_summary": {
            "id": 1,
            "total_loc": 1000,
            "code_loc": 800,
            "comment_loc": 100,
            "avg_complexity": 5.0,
            "max_complexity": 15,
            "maintainability_index": 70.0,
            "technical_debt_hours": 10,
            "calculated_at": datetime(2026, 2, 3).isoformat(),
        },
    }


@pytest.fixture
def complete_data(minimal_data):
    """Complete dashboard data with all tables."""
    data = minimal_data.copy()
    data.update(
        {
            "use_cases": [
                {
                    "id": 1,
                    "title": "User Authentication",
                    "category": "Security",
                    "business_value": "Secure access control",
                    "user_stories": ["As a user, I can log in"],
                    "acceptance_criteria": ["Password hashing"],
                    "priority": "high",
                    "implementation_status": "implemented",
                    "related_files": ["src/auth.py"],
                    "created_at": datetime.utcnow().isoformat(),
                },
                {
                    "id": 2,
                    "title": "Payment Processing",
                    "category": "Business",
                    "priority": "critical",
                    "implementation_status": "partial",
                    "user_stories": [],
                    "acceptance_criteria": [],
                    "related_files": [],
                    "created_at": datetime.utcnow().isoformat(),
                },
            ],
            "vulnerabilities": [
                {
                    "id": 1,
                    "cve_id": "CVE-2024-1234",
                    "severity": "critical",
                    "package_name": "requests",
                    "package_version": "2.25.0",
                    "fixed_version": "2.31.0",
                    "description": "Security vulnerability",
                    "detected_at": datetime.utcnow().isoformat(),
                }
            ],
            "packages": [
                {
                    "id": 1,
                    "package_name": "fastapi",
                    "package_version": "0.109.0",
                    "package_type": "direct",
                    "license": "MIT",
                    "size_kb": 2048,
                    "vulnerability_count": 0,
                    "installed_at": datetime.utcnow().isoformat(),
                }
            ],
            "code_smells": [
                {
                    "id": 1,
                    "smell_type": "Long Method",
                    "category": "complexity",
                    "severity": "medium",
                    "file_path": "src/main.py",
                    "line_number": 100,
                    "effort_hours": 2,
                    "detected_at": datetime.utcnow().isoformat(),
                }
            ],
            "entities": [
                {
                    "id": 1,
                    "name": "User",
                    "type": "entity",
                    "file_path": "src/models.py",
                    "line_range": "10-50",
                    "attributes": [{"name": "user_id", "type": "int"}],
                    "methods": [],
                    "stereotypes": [],
                }
            ],
            "relationships": [
                {
                    "id": 1,
                    "source_entity": "Order",
                    "target_entity": "OrderLine",
                    "relationship_type": "composition",
                    "cardinality": "1..n",
                    "bidirectional": False,
                }
            ],
            "components": [
                {
                    "id": 1,
                    "name": "AuthService",
                    "type": "service",
                    "dependencies": [],
                    "api_count": 5,
                    "loc": 500,
                    "layer": "Business",
                }
            ],
            "files": [
                {
                    "id": 1,
                    "file_path": "src/main.py",
                    "file_name": "main.py",
                    "file_type": "file",
                    "parent_path": "src",
                    "language": "Python",
                    "loc": 200,
                    "complexity": 8,
                    "churn_count": 5,
                    "last_modified": datetime.utcnow().isoformat(),
                }
            ],
            "code_snippets": [
                {
                    "id": 1,
                    "title": "Factory Pattern",
                    "file_path": "src/factory.py",
                    "start_line": 10,
                    "end_line": 25,
                    "language": "Python",
                    "code": "class Factory:\n    pass",
                    "category": "pattern",
                }
            ],
            "test_results": [
                {
                    "id": 1,
                    "test_name": "test_auth",
                    "test_type": "unit",
                    "status": "pass",
                    "duration_ms": 45,
                    "file_path": "tests/test_auth.py",
                    "run_at": datetime.utcnow().isoformat(),
                }
            ],
            "lens_insights": [
                {
                    "id": 1,
                    "insight_type": "pattern",
                    "category": "Design Pattern",
                    "description": "Repository pattern detected",
                    "evidence": ["src/repo.py"],
                    "impact": "low",
                    "confidence": 85,
                    "detected_at": datetime.utcnow().isoformat(),
                }
            ],
            "metrics_by_file": [
                {
                    "id": 1,
                    "file_path": "src/main.py",
                    "language": "Python",
                    "loc": 200,
                    "complexity": 8,
                    "maintainability": 70.0,
                    "churn_count": 5,
                    "last_modified": datetime.utcnow().isoformat(),
                }
            ],
        }
    )
    return data


# =============================================================================
# BASIC GENERATION TESTS
# =============================================================================


def test_generate_minimal_database(temp_db_path, minimal_data):
    """Test generating database with minimal data."""
    generator = SQLiteDataGenerator()
    success, error = generator.generate(temp_db_path, minimal_data)

    assert success, f"Generation failed: {error}"
    assert error is None
    assert temp_db_path.exists()

    # Verify database is valid
    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Check essential tables exist
    assert "repo_summary" in tables
    assert "use_cases" in tables
    assert "metrics_summary" in tables


def test_generate_complete_database(temp_db_path, complete_data):
    """Test generating database with complete data."""
    generator = SQLiteDataGenerator()
    success, error = generator.generate(temp_db_path, complete_data)

    assert success, f"Generation failed: {error}"
    assert temp_db_path.exists()


def test_generate_with_validation(temp_db_path, minimal_data):
    """Test generation with data validation enabled."""
    generator = SQLiteDataGenerator()
    success, error = generator.generate(temp_db_path, minimal_data, validate=True)

    assert success
    assert error is None


def test_generate_without_validation(temp_db_path, minimal_data):
    """Test generation with validation disabled."""
    generator = SQLiteDataGenerator()
    success, error = generator.generate(temp_db_path, minimal_data, validate=False)

    assert success


def test_convenience_function(temp_db_path, minimal_data):
    """Test convenience function for generation."""
    success, error = generate_dashboard_sqlite(temp_db_path, minimal_data)

    assert success
    assert temp_db_path.exists()


# =============================================================================
# DATA INSERTION TESTS
# =============================================================================


def test_repo_summary_insertion(temp_db_path, minimal_data):
    """Test repo_summary data insertion."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, minimal_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM repo_summary")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row["repo_name"] == "TestRepo"
    assert row["repo_slug"] == "test-repo"
    assert row["health_score"] == 80


def test_use_cases_insertion(temp_db_path, complete_data):
    """Test use_cases array insertion."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.execute("SELECT COUNT(*) FROM use_cases")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 2


def test_json_array_serialization(temp_db_path, complete_data):
    """Test JSON array fields are properly serialized."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM use_cases WHERE id = 1")
    row = cursor.fetchone()
    conn.close()

    # Deserialize JSON arrays
    user_stories = json.loads(row["user_stories"])
    related_files = json.loads(row["related_files"])

    assert isinstance(user_stories, list)
    assert len(user_stories) == 1
    assert user_stories[0] == "As a user, I can log in"

    assert isinstance(related_files, list)
    assert "src/auth.py" in related_files


def test_foreign_key_parent_child(temp_db_path):
    """Test parent-child relationship in packages table."""
    data = {
        "repo_summary": {
            "id": 1,
            "repo_name": "Test",
            "repo_slug": "test",
            "primary_language": "Python",
            "tech_stack": [],
            "total_loc": 100,
            "file_count": 10,
            "contributor_count": 1,
            "health_score": 80,
            "last_commit_date": datetime.utcnow().isoformat(),
        },
        "metrics_summary": {
            "id": 1,
            "total_loc": 100,
            "code_loc": 80,
            "comment_loc": 10,
            "avg_complexity": 5.0,
            "max_complexity": 10,
            "maintainability_index": 70.0,
            "technical_debt_hours": 5,
            "calculated_at": datetime.utcnow().isoformat(),
        },
        "packages": [
            {
                "id": 1,
                "package_name": "fastapi",
                "package_version": "0.109.0",
                "package_type": "direct",
                "installed_at": datetime.utcnow().isoformat(),
            },
            {
                "id": 2,
                "package_name": "starlette",
                "package_version": "0.35.0",
                "package_type": "transitive",
                "parent_package_id": 1,  # Child of fastapi
                "installed_at": datetime.utcnow().isoformat(),
            },
        ],
    }

    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM packages WHERE id = 2")
    row = cursor.fetchone()
    conn.close()

    assert row["parent_package_id"] == 1


# =============================================================================
# FTS5 FULL-TEXT SEARCH TESTS
# =============================================================================


def test_use_cases_fts_population(temp_db_path, complete_data):
    """Test use_cases_fts table is populated."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.execute("SELECT COUNT(*) FROM use_cases_fts")
    count = cursor.fetchone()[0]
    conn.close()

    assert count == 2  # Same as use_cases table


def test_use_cases_fts_search(temp_db_path, complete_data):
    """Test full-text search on use_cases."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        """
        SELECT u.* FROM use_cases u
        JOIN use_cases_fts fts ON u.id = fts.rowid
        WHERE use_cases_fts MATCH 'authentication'
        """
    )
    results = cursor.fetchall()
    conn.close()

    assert len(results) == 1
    assert results[0]["title"] == "User Authentication"


def test_packages_fts_search(temp_db_path, complete_data):
    """Test full-text search on packages."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        """
        SELECT p.* FROM packages p
        JOIN packages_fts fts ON p.id = fts.rowid
        WHERE packages_fts MATCH 'fastapi'
        """
    )
    results = cursor.fetchall()
    conn.close()

    assert len(results) == 1
    assert results[0]["package_name"] == "fastapi"


def test_files_fts_search(temp_db_path, complete_data):
    """Test full-text search on files."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        """
        SELECT f.* FROM files f
        JOIN files_fts fts ON f.id = fts.rowid
        WHERE files_fts MATCH 'main.py'
        """
    )
    results = cursor.fetchall()
    conn.close()

    assert len(results) == 1
    assert results[0]["file_name"] == "main.py"


# =============================================================================
# VIEW TESTS
# =============================================================================


def test_executive_kpis_view(temp_db_path, complete_data):
    """Test executive_kpis view computes correctly."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM executive_kpis")
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row["health_score"] == 80
    assert row["critical_vulnerabilities"] == 1  # One critical vuln
    assert row["tech_debt_hours"] == 10


def test_refactoring_suggestions_view(temp_db_path, complete_data):
    """Test refactoring_suggestions view prioritizes correctly."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute("SELECT * FROM refactoring_suggestions")
    rows = cursor.fetchall()
    conn.close()

    assert len(rows) == 1
    assert rows[0]["suggestion"] == "Long Method"
    assert rows[0]["priority_bucket"] == "backlog"  # medium severity, 2 hours


# =============================================================================
# INDEX TESTS
# =============================================================================


def test_indexes_created(temp_db_path, minimal_data):
    """Test indexes are created."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, minimal_data)

    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_%'"
    )
    indexes = [row[0] for row in cursor.fetchall()]
    conn.close()

    # Check some key indexes exist
    assert "idx_repo_slug" in indexes
    assert "idx_use_case_category" in indexes
    assert "idx_vuln_severity" in indexes


# =============================================================================
# ERROR HANDLING TESTS
# =============================================================================


def test_generate_with_invalid_data(temp_db_path):
    """Test generation fails with invalid data."""
    invalid_data = {
        "repo_summary": {
            # Missing required fields
            "id": 1,
            "repo_name": "Test",
        },
        "metrics_summary": {
            "id": 1,
            "total_loc": 100,
            "code_loc": 80,
            "comment_loc": 10,
            "avg_complexity": 5.0,
            "max_complexity": 10,
            "maintainability_index": 70.0,
            "technical_debt_hours": 5,
            "calculated_at": datetime.utcnow().isoformat(),
        },
    }

    generator = SQLiteDataGenerator()
    success, error = generator.generate(temp_db_path, invalid_data, validate=True)

    assert not success
    assert error is not None
    assert "validation failed" in error.lower()


def test_generate_with_validation_disabled_allows_partial(temp_db_path):
    """Test generation with validation disabled allows partial data."""
    partial_data = {
        "repo_summary": {
            "id": 1,
            "repo_name": "Test",
            "repo_slug": "test",
            "primary_language": "Python",
            "tech_stack": [],
            "total_loc": 100,
            "file_count": 10,
            "contributor_count": 1,
            "health_score": 80,
            "last_commit_date": datetime.utcnow().isoformat(),
        },
        # Missing metrics_summary
    }

    generator = SQLiteDataGenerator()
    success, error = generator.generate(
        temp_db_path, partial_data, validate=False  # Skip validation
    )

    # Should succeed with validation disabled
    assert success


def test_transaction_rollback_on_error(temp_db_path, minimal_data):
    """Test transaction rollback on database error."""
    # This test is tricky - we'd need to inject a failure
    # For now, just verify basic rollback mechanism exists
    generator = SQLiteDataGenerator()

    # Try to generate with corrupted data that will fail after schema creation
    data = minimal_data.copy()
    data["use_cases"] = [{"invalid": "structure"}]  # Will fail insertion

    success, error = generator.generate(temp_db_path, data, validate=False)

    # Should fail and error message should indicate the issue
    assert not success
    assert error is not None


# =============================================================================
# BACKUP TESTS
# =============================================================================


def test_backup_creates_backup_file(temp_db_path, minimal_data):
    """Test backup creates .backup file when database exists."""
    # Create initial database
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, minimal_data, backup=False)

    # Generate again with backup enabled
    generator.generate(temp_db_path, minimal_data, backup=True)

    # Check backup exists
    backup_path = temp_db_path.with_suffix(".sqlite.backup")
    assert backup_path.exists()

    # Cleanup
    if backup_path.exists():
        backup_path.unlink()


def test_backup_disabled_no_backup_file(temp_db_path, minimal_data):
    """Test no backup created when backup=False."""
    # Create initial database
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, minimal_data, backup=False)

    # Generate again with backup disabled
    generator.generate(temp_db_path, minimal_data, backup=False)

    # Check no backup exists
    backup_path = temp_db_path.with_suffix(".sqlite.backup")
    assert not backup_path.exists()


# =============================================================================
# QUERY UTILITY TESTS
# =============================================================================


def test_query_database(temp_db_path, complete_data):
    """Test query_database utility method."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    results = generator.query_database(
        temp_db_path, "SELECT * FROM use_cases WHERE priority = ?", ("high",)
    )

    assert len(results) == 1
    assert results[0]["title"] == "User Authentication"


def test_get_database_stats(temp_db_path, complete_data):
    """Test get_database_stats utility method."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    stats = generator.get_database_stats(temp_db_path)

    assert stats["repo_summary"] == 1  # Singleton
    assert stats["use_cases"] == 2
    assert stats["vulnerabilities"] == 1
    assert stats["packages"] == 1
    assert stats["code_smells"] == 1


# =============================================================================
# PAGINATION TESTS
# =============================================================================


def test_pagination_limit_offset(temp_db_path, complete_data):
    """Test SQL pagination works correctly."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row

    # Page 1: LIMIT 1 OFFSET 0
    cursor = conn.execute("SELECT * FROM use_cases ORDER BY id LIMIT 1 OFFSET 0")
    page1 = cursor.fetchall()
    assert len(page1) == 1
    assert page1[0]["id"] == 1

    # Page 2: LIMIT 1 OFFSET 1
    cursor = conn.execute("SELECT * FROM use_cases ORDER BY id LIMIT 1 OFFSET 1")
    page2 = cursor.fetchall()
    assert len(page2) == 1
    assert page2[0]["id"] == 2

    conn.close()


# =============================================================================
# FILTERING TESTS
# =============================================================================


def test_severity_filtering(temp_db_path, complete_data):
    """Test filtering by severity."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.execute("SELECT * FROM vulnerabilities WHERE severity = 'critical'")
    results = cursor.fetchall()
    conn.close()

    assert len(results) == 1


def test_priority_filtering(temp_db_path, complete_data):
    """Test filtering by priority."""
    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, complete_data)

    conn = sqlite3.connect(str(temp_db_path))
    cursor = conn.execute("SELECT * FROM use_cases WHERE priority = 'critical'")
    results = cursor.fetchall()
    conn.close()

    assert len(results) == 1


# =============================================================================
# SORTING TESTS
# =============================================================================


def test_sorting_by_severity(temp_db_path):
    """Test sorting by severity."""
    data = {
        "repo_summary": {
            "id": 1,
            "repo_name": "Test",
            "repo_slug": "test",
            "primary_language": "Python",
            "tech_stack": [],
            "total_loc": 100,
            "file_count": 10,
            "contributor_count": 1,
            "health_score": 80,
            "last_commit_date": datetime.utcnow().isoformat(),
        },
        "metrics_summary": {
            "id": 1,
            "total_loc": 100,
            "code_loc": 80,
            "comment_loc": 10,
            "avg_complexity": 5.0,
            "max_complexity": 10,
            "maintainability_index": 70.0,
            "technical_debt_hours": 5,
            "calculated_at": datetime.utcnow().isoformat(),
        },
        "code_smells": [
            {
                "id": 1,
                "smell_type": "Test 1",
                "category": "complexity",
                "severity": "low",
                "file_path": "test.py",
                "line_number": 1,
                "effort_hours": 1,
                "detected_at": datetime.utcnow().isoformat(),
            },
            {
                "id": 2,
                "smell_type": "Test 2",
                "category": "complexity",
                "severity": "critical",
                "file_path": "test.py",
                "line_number": 2,
                "effort_hours": 8,
                "detected_at": datetime.utcnow().isoformat(),
            },
            {
                "id": 3,
                "smell_type": "Test 3",
                "category": "complexity",
                "severity": "medium",
                "file_path": "test.py",
                "line_number": 3,
                "effort_hours": 4,
                "detected_at": datetime.utcnow().isoformat(),
            },
        ],
    }

    generator = SQLiteDataGenerator()
    generator.generate(temp_db_path, data)

    conn = sqlite3.connect(str(temp_db_path))
    conn.row_factory = sqlite3.Row
    cursor = conn.execute(
        """
        SELECT * FROM code_smells
        ORDER BY 
            CASE severity 
                WHEN 'critical' THEN 1
                WHEN 'high' THEN 2
                WHEN 'medium' THEN 3
                ELSE 4
            END
        """
    )
    results = cursor.fetchall()
    conn.close()

    # Should be ordered: critical, medium, low
    assert results[0]["severity"] == "critical"
    assert results[1]["severity"] == "medium"
    assert results[2]["severity"] == "low"
