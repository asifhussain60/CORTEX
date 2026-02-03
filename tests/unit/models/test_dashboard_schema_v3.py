"""
Unit Tests for Dashboard Schema v3.0
=====================================

Purpose: Test Pydantic models, validation, and SQL schema generation
Created: 2026-02-03
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
Governance: CORE-008 (TDD), CORE-013 (no bare except)
"""

import json
from datetime import datetime

import pytest
from pydantic import ValidationError

from cortex.models.dashboard_schema_v3 import (
    CodeSmell,
    CodeSnippet,
    Component,
    ComponentType,
    Entity,
    EntityType,
    ExecutiveKPI,
    FileEntry,
    FileType,
    HealthStatus,
    ImplementationStatus,
    InsightType,
    LENSInsight,
    MetricsByFile,
    MetricsSummary,
    Package,
    PackageType,
    Priority,
    RefactoringSuggestion,
    Relationship,
    RelationshipType,
    RepoSummary,
    RepositoryRegistry,
    Severity,
    SmellCategory,
    SQLiteSchemaGenerator,
    TestResult,
    TestStatus,
    TestType,
    UseCase,
    Vulnerability,
    validate_dashboard_data,
)


# =============================================================================
# REPO SUMMARY TESTS
# =============================================================================


def test_repo_summary_valid():
    """Test valid RepoSummary creation."""
    data = {
        "id": 1,
        "repo_name": "CORTEX",
        "repo_slug": "cortex",
        "description": "AI Orchestration System",
        "primary_language": "Python",
        "tech_stack": ["Python", "FastAPI", "SQLite"],
        "total_loc": 45000,
        "file_count": 350,
        "contributor_count": 5,
        "health_score": 85,
        "last_commit_date": datetime(2026, 2, 3, 10, 30, 0),
        "llm_overview": "Enterprise platform...",
    }
    summary = RepoSummary(**data)
    assert summary.repo_name == "CORTEX"
    assert summary.health_score == 85
    assert len(summary.tech_stack) == 3


def test_repo_summary_health_score_validation():
    """Test health_score must be 0-100."""
    data = {
        "id": 1,
        "repo_name": "Test",
        "repo_slug": "test",
        "primary_language": "Python",
        "tech_stack": [],
        "total_loc": 100,
        "file_count": 10,
        "contributor_count": 1,
        "health_score": 150,  # Invalid
        "last_commit_date": datetime.utcnow(),
    }
    with pytest.raises(ValidationError) as exc_info:
        RepoSummary(**data)
    assert "health_score" in str(exc_info.value)


def test_repo_summary_json_serialization():
    """Test JSON serialization for SQLite storage."""
    summary = RepoSummary(
        id=1,
        repo_name="Test",
        repo_slug="test",
        primary_language="Python",
        tech_stack=["Python", "Docker"],
        total_loc=1000,
        file_count=50,
        contributor_count=3,
        health_score=75,
        last_commit_date=datetime(2026, 2, 3),
    )
    json_str = summary.model_dump_json()
    data = json.loads(json_str)
    assert data["repo_name"] == "Test"
    assert data["tech_stack"] == ["Python", "Docker"]


# =============================================================================
# USE CASE TESTS
# =============================================================================


def test_use_case_valid():
    """Test valid UseCase creation."""
    use_case = UseCase(
        id=1,
        title="User Authentication",
        category="Security",
        business_value="Secure user access control",
        user_stories=["As a user, I can log in"],
        acceptance_criteria=["Password hashing", "Session management"],
        priority=Priority.HIGH,
        implementation_status=ImplementationStatus.IMPLEMENTED,
        related_files=["src/auth.py", "src/middleware.py"],
    )
    assert use_case.title == "User Authentication"
    assert use_case.priority == Priority.HIGH
    assert len(use_case.related_files) == 2


def test_use_case_enum_validation():
    """Test Priority enum validation."""
    with pytest.raises(ValidationError):
        UseCase(
            id=1,
            title="Test",
            category="Test",
            priority="invalid_priority",  # Invalid enum
            implementation_status=ImplementationStatus.PLANNED,
        )


def test_use_case_defaults():
    """Test default values."""
    use_case = UseCase(
        id=1,
        title="Test Feature",
        category="Feature",
    )
    assert use_case.priority == Priority.MEDIUM
    assert use_case.implementation_status == ImplementationStatus.PLANNED
    assert use_case.user_stories == []
    assert use_case.related_files == []


# =============================================================================
# METRICS TESTS
# =============================================================================


def test_metrics_summary_valid():
    """Test valid MetricsSummary creation."""
    metrics = MetricsSummary(
        id=1,
        total_loc=50000,
        code_loc=40000,
        comment_loc=5000,
        avg_complexity=5.2,
        max_complexity=25,
        maintainability_index=72.5,
        technical_debt_hours=120,
        calculated_at=datetime.utcnow(),
    )
    assert metrics.total_loc == 50000
    assert metrics.maintainability_index == 72.5


def test_metrics_by_file_valid():
    """Test valid MetricsByFile creation."""
    file_metrics = MetricsByFile(
        id=1,
        file_path="src/core/auth.py",
        language="Python",
        loc=250,
        complexity=8,
        maintainability=68.5,
        churn_count=12,
        last_modified=datetime.utcnow(),
    )
    assert file_metrics.file_path == "src/core/auth.py"
    assert file_metrics.complexity == 8


# =============================================================================
# VULNERABILITY TESTS
# =============================================================================


def test_vulnerability_valid():
    """Test valid Vulnerability creation."""
    vuln = Vulnerability(
        id=1,
        cve_id="CVE-2024-1234",
        severity=Severity.CRITICAL,
        package_name="django",
        package_version="3.0.0",
        fixed_version="3.2.5",
        description="SQL injection vulnerability",
        file_path="requirements.txt",
        line_number=5,
        remediation="Upgrade to 3.2.5 or later",
    )
    assert vuln.cve_id == "CVE-2024-1234"
    assert vuln.severity == Severity.CRITICAL


def test_vulnerability_severity_validation():
    """Test Severity enum validation."""
    with pytest.raises(ValidationError):
        Vulnerability(
            id=1,
            severity="super_critical",  # Invalid
            package_name="test",
            package_version="1.0.0",
            description="Test",
        )


# =============================================================================
# PACKAGE TESTS
# =============================================================================


def test_package_direct_dependency():
    """Test direct package dependency."""
    pkg = Package(
        id=1,
        package_name="fastapi",
        package_version="0.109.0",
        package_type=PackageType.DIRECT,
        license="MIT",
        size_kb=2048,
        vulnerability_count=0,
        parent_package_id=None,
    )
    assert pkg.package_type == PackageType.DIRECT
    assert pkg.parent_package_id is None


def test_package_transitive_dependency():
    """Test transitive dependency with parent."""
    pkg = Package(
        id=2,
        package_name="starlette",
        package_version="0.35.0",
        package_type=PackageType.TRANSITIVE,
        license="BSD",
        size_kb=512,
        vulnerability_count=0,
        parent_package_id=1,  # Child of fastapi
    )
    assert pkg.package_type == PackageType.TRANSITIVE
    assert pkg.parent_package_id == 1


# =============================================================================
# CODE SMELL TESTS
# =============================================================================


def test_code_smell_valid():
    """Test valid CodeSmell creation."""
    smell = CodeSmell(
        id=1,
        smell_type="God Class",
        category=SmellCategory.COMPLEXITY,
        severity=Severity.HIGH,
        file_path="src/monolith.py",
        line_number=1,
        code_snippet="class Monster:\n    ...",
        explanation="Class has 2000+ lines",
        remediation="Split into smaller classes",
        effort_hours=8,
    )
    assert smell.smell_type == "God Class"
    assert smell.effort_hours == 8


def test_code_smell_effort_validation():
    """Test effort_hours must be >= 1."""
    with pytest.raises(ValidationError):
        CodeSmell(
            id=1,
            smell_type="Test",
            category=SmellCategory.SMELL,
            severity=Severity.LOW,
            file_path="test.py",
            line_number=1,
            effort_hours=0,  # Invalid
        )


# =============================================================================
# DOMAIN MODEL TESTS
# =============================================================================


def test_entity_aggregate_root():
    """Test Entity as aggregate root."""
    entity = Entity(
        id=1,
        name="Order",
        type=EntityType.AGGREGATE_ROOT,
        description="Order aggregate in DDD",
        file_path="src/domain/order.py",
        line_range="10-150",
        attributes=[{"name": "order_id", "type": "str"}],
        methods=[{"name": "place_order", "parameters": []}],
        stereotypes=["AggregateRoot"],
    )
    assert entity.type == EntityType.AGGREGATE_ROOT
    assert len(entity.stereotypes) == 1


def test_relationship_composition():
    """Test Relationship for composition."""
    rel = Relationship(
        id=1,
        source_entity="Order",
        target_entity="OrderLine",
        relationship_type=RelationshipType.COMPOSITION,
        cardinality="1..n",
        label="contains",
        bidirectional=False,
    )
    assert rel.relationship_type == RelationshipType.COMPOSITION
    assert rel.cardinality == "1..n"


# =============================================================================
# ARCHITECTURE TESTS
# =============================================================================


def test_component_service():
    """Test Component as service."""
    component = Component(
        id=1,
        name="AuthService",
        type=ComponentType.SERVICE,
        description="Handles authentication",
        dependencies=["DatabaseService", "CacheService"],
        api_count=5,
        loc=1200,
        layer="Business",
    )
    assert component.type == ComponentType.SERVICE
    assert len(component.dependencies) == 2


# =============================================================================
# FILE EXPLORER TESTS
# =============================================================================


def test_file_entry_file():
    """Test FileEntry for file."""
    file = FileEntry(
        id=1,
        file_path="src/main.py",
        file_name="main.py",
        file_type=FileType.FILE,
        parent_path="src",
        language="Python",
        loc=150,
        complexity=5,
        last_modified=datetime.utcnow(),
        churn_count=8,
    )
    assert file.file_type == FileType.FILE
    assert file.language == "Python"


def test_file_entry_folder():
    """Test FileEntry for folder."""
    folder = FileEntry(
        id=2,
        file_path="src",
        file_name="src",
        file_type=FileType.FOLDER,
        parent_path="/",
        last_modified=datetime.utcnow(),
    )
    assert folder.file_type == FileType.FOLDER
    assert folder.language is None


def test_code_snippet_valid():
    """Test CodeSnippet for code example."""
    snippet = CodeSnippet(
        id=1,
        title="Factory Pattern Example",
        file_path="src/factory.py",
        start_line=10,
        end_line=25,
        language="Python",
        code="class Factory:\n    ...",
        explanation="Factory pattern implementation",
        category="pattern",
    )
    assert snippet.category == "pattern"
    assert snippet.start_line < snippet.end_line


# =============================================================================
# TESTING TESTS
# =============================================================================


def test_test_result_pass():
    """Test TestResult for passing test."""
    result = TestResult(
        id=1,
        test_name="test_authentication",
        test_type=TestType.UNIT,
        status=TestStatus.PASS,
        duration_ms=45,
        file_path="tests/test_auth.py",
    )
    assert result.status == TestStatus.PASS
    assert result.test_type == TestType.UNIT


def test_test_result_fail():
    """Test TestResult for failing test."""
    result = TestResult(
        id=2,
        test_name="test_integration",
        test_type=TestType.INTEGRATION,
        status=TestStatus.FAIL,
        duration_ms=1200,
        file_path="tests/test_integration.py",
        failure_message="AssertionError: Expected 200, got 500",
    )
    assert result.status == TestStatus.FAIL
    assert result.failure_message is not None


# =============================================================================
# LENS INSIGHT TESTS
# =============================================================================


def test_lens_insight_pattern():
    """Test LENSInsight for pattern detection."""
    insight = LENSInsight(
        id=1,
        insight_type=InsightType.PATTERN,
        category="Design Pattern",
        description="Repository pattern detected",
        evidence=["src/repositories/user_repo.py", "src/repositories/order_repo.py"],
        impact=Severity.LOW,
        confidence=85,
    )
    assert insight.insight_type == InsightType.PATTERN
    assert insight.confidence == 85


def test_lens_insight_anti_pattern():
    """Test LENSInsight for anti-pattern detection."""
    insight = LENSInsight(
        id=2,
        insight_type=InsightType.ANTI_PATTERN,
        category="Code Smell",
        description="God object anti-pattern detected",
        evidence=["src/god_object.py"],
        impact=Severity.HIGH,
        confidence=92,
    )
    assert insight.insight_type == InsightType.ANTI_PATTERN
    assert insight.impact == Severity.HIGH


# =============================================================================
# VIEW MODEL TESTS
# =============================================================================


def test_executive_kpi_valid():
    """Test ExecutiveKPI view model."""
    kpi = ExecutiveKPI(
        health_score=85,
        critical_vulnerabilities=3,
        tech_debt_hours=120,
        test_pass_rate=94.5,
        maintainability=72.3,
    )
    assert kpi.health_score == 85
    assert kpi.test_pass_rate == 94.5


def test_refactoring_suggestion_valid():
    """Test RefactoringSuggestion view model."""
    suggestion = RefactoringSuggestion(
        id=1,
        suggestion="Extract Method",
        file_path="src/complex.py",
        severity=Severity.HIGH,
        effort_hours=2,
        priority_bucket="quick_win",
    )
    assert suggestion.priority_bucket == "quick_win"


# =============================================================================
# REGISTRY MODEL TESTS
# =============================================================================


def test_repository_registry_valid():
    """Test RepositoryRegistry model."""
    registry = RepositoryRegistry(
        id=1,
        slug="cortex",
        name="CORTEX",
        description="AI Orchestration Platform",
        health_score=85,
        primary_language="Python",
        total_loc=45000,
        dashboard_path="/spa/dashboard.html?repo=cortex",
    )
    assert registry.slug == "cortex"
    assert registry.health_score == 85


# =============================================================================
# SQL SCHEMA GENERATION TESTS
# =============================================================================


def test_sqlite_schema_generation():
    """Test full SQLite schema generation."""
    schema_sql = SQLiteSchemaGenerator.generate_full_schema()

    # Check essential tables present
    assert "CREATE TABLE IF NOT EXISTS repo_summary" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS use_cases" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS vulnerabilities" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS packages" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS code_smells" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS entities" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS relationships" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS components" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS files" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS test_results" in schema_sql
    assert "CREATE TABLE IF NOT EXISTS lens_insights" in schema_sql

    # Check indexes present
    assert "CREATE INDEX" in schema_sql
    assert "idx_repo_slug" in schema_sql
    assert "idx_vuln_severity" in schema_sql

    # Check FTS5 tables present
    assert "CREATE VIRTUAL TABLE IF NOT EXISTS use_cases_fts USING fts5" in schema_sql
    assert "CREATE VIRTUAL TABLE IF NOT EXISTS packages_fts USING fts5" in schema_sql
    assert "CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5" in schema_sql

    # Check views present
    assert "CREATE VIEW IF NOT EXISTS executive_kpis" in schema_sql
    assert "CREATE VIEW IF NOT EXISTS refactoring_suggestions" in schema_sql


# =============================================================================
# VALIDATION UTILITY TESTS
# =============================================================================


def test_validate_dashboard_data_complete():
    """Test validation of complete dashboard data."""
    data = {
        "repo_summary": {
            "id": 1,
            "repo_name": "Test",
            "repo_slug": "test",
            "primary_language": "Python",
            "tech_stack": ["Python"],
            "total_loc": 1000,
            "file_count": 50,
            "contributor_count": 2,
            "health_score": 80,
            "last_commit_date": datetime.utcnow().isoformat(),
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
            "calculated_at": datetime.utcnow().isoformat(),
        },
        "use_cases": [
            {
                "id": 1,
                "title": "Test Use Case",
                "category": "Feature",
                "user_stories": [],
                "acceptance_criteria": [],
                "priority": "medium",
                "implementation_status": "planned",
                "related_files": [],
                "created_at": datetime.utcnow().isoformat(),
            }
        ],
    }

    valid, errors = validate_dashboard_data(data)
    assert valid, f"Validation failed: {errors}"
    assert len(errors) == 0


def test_validate_dashboard_data_missing_required():
    """Test validation fails for missing required tables."""
    data = {
        # Missing repo_summary
        "metrics_summary": {
            "id": 1,
            "total_loc": 1000,
            "code_loc": 800,
            "comment_loc": 100,
            "avg_complexity": 5.0,
            "max_complexity": 15,
            "maintainability_index": 70.0,
            "technical_debt_hours": 10,
            "calculated_at": datetime.utcnow().isoformat(),
        }
    }

    valid, errors = validate_dashboard_data(data)
    assert not valid
    assert any("repo_summary" in error for error in errors)


def test_validate_dashboard_data_invalid_model():
    """Test validation fails for invalid model data."""
    data = {
        "repo_summary": {
            "id": 1,
            "repo_name": "Test",
            "repo_slug": "test",
            "primary_language": "Python",
            "tech_stack": ["Python"],
            "total_loc": 1000,
            "file_count": 50,
            "contributor_count": 2,
            "health_score": 150,  # Invalid: > 100
            "last_commit_date": datetime.utcnow().isoformat(),
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
            "calculated_at": datetime.utcnow().isoformat(),
        },
    }

    valid, errors = validate_dashboard_data(data)
    assert not valid
    assert any("health_score" in error for error in errors)


# =============================================================================
# ENUM TESTS
# =============================================================================


def test_all_enums_have_values():
    """Test all enums have proper values."""
    assert HealthStatus.HEALTHY.value == "healthy"
    assert Severity.CRITICAL.value == "critical"
    assert Priority.HIGH.value == "high"
    assert PackageType.DIRECT.value == "direct"
    assert EntityType.AGGREGATE_ROOT.value == "aggregate_root"
    assert RelationshipType.COMPOSITION.value == "composition"
    assert ComponentType.SERVICE.value == "service"
    assert FileType.FILE.value == "file"
    assert TestType.UNIT.value == "unit"
    assert TestStatus.PASS.value == "pass"
    assert InsightType.PATTERN.value == "pattern"
    assert SmellCategory.COMPLEXITY.value == "complexity"


# =============================================================================
# INTEGRATION TEST: FULL DATA MODEL
# =============================================================================


def test_complete_dashboard_data_structure():
    """Test creating complete dashboard data structure."""
    # Build complete dashboard data
    dashboard = {
        "repo_summary": RepoSummary(
            id=1,
            repo_name="TestRepo",
            repo_slug="test-repo",
            primary_language="Python",
            tech_stack=["Python", "FastAPI"],
            total_loc=5000,
            file_count=100,
            contributor_count=3,
            health_score=82,
            last_commit_date=datetime.utcnow(),
        ),
        "use_cases": [
            UseCase(
                id=1,
                title="User Login",
                category="Authentication",
                priority=Priority.HIGH,
                implementation_status=ImplementationStatus.IMPLEMENTED,
            )
        ],
        "metrics_summary": MetricsSummary(
            id=1,
            total_loc=5000,
            code_loc=4000,
            comment_loc=500,
            avg_complexity=5.5,
            max_complexity=20,
            maintainability_index=75.0,
            technical_debt_hours=40,
            calculated_at=datetime.utcnow(),
        ),
        "vulnerabilities": [
            Vulnerability(
                id=1,
                severity=Severity.HIGH,
                package_name="requests",
                package_version="2.25.0",
                fixed_version="2.31.0",
                description="Security issue",
            )
        ],
        "packages": [
            Package(
                id=1,
                package_name="fastapi",
                package_version="0.109.0",
                package_type=PackageType.DIRECT,
                license="MIT",
                size_kb=2048,
                vulnerability_count=0,
            )
        ],
    }

    # Validate structure
    assert isinstance(dashboard["repo_summary"], RepoSummary)
    assert len(dashboard["use_cases"]) == 1
    assert len(dashboard["vulnerabilities"]) == 1
    assert dashboard["metrics_summary"].maintainability_index == 75.0

    # Test JSON serialization
    json_data = {}
    for key, value in dashboard.items():
        if isinstance(value, list):
            json_data[key] = [item.model_dump() for item in value]
        else:
            json_data[key] = value.model_dump()

    # Verify JSON is valid
    json_str = json.dumps(json_data, default=str)
    assert len(json_str) > 0
    parsed = json.loads(json_str)
    assert parsed["repo_summary"]["repo_name"] == "TestRepo"
