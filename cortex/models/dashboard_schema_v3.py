"""
Dashboard Schema v3.0 - JSON-First Architecture.

Pydantic models for the Enterprise Repository Intelligence Dashboard.
Supports 13 tabs with full null-safety for graceful UI degradation.

Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml
Governance: CORE-011 (Type hints), CORE-012 (Docstrings), CORE-035 (Single implementation)
Created: 2026-02-04
"""

from __future__ import annotations

import json
from datetime import datetime
from enum import Enum
from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# =============================================================================
# ENUMS (Canonical Definitions)
# =============================================================================


class HealthStatus(str, Enum):
    """Health status for executive summary."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


class Severity(str, Enum):
    """Severity levels for vulnerabilities and issues."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Priority(str, Enum):
    """Priority levels for use cases and recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PackageType(str, Enum):
    """Type of package dependency."""

    DIRECT = "direct"
    DEV = "dev"
    TRANSITIVE = "transitive"


class SmellCategory(str, Enum):
    """Code smell categories."""

    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    SMELL = "smell"
    MAINTAINABILITY = "maintainability"


class EntityType(str, Enum):
    """Domain entity types (DDD)."""

    AGGREGATE_ROOT = "aggregate_root"
    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    DOMAIN_EVENT = "domain_event"
    REPOSITORY = "repository"
    SERVICE = "service"


class RelationshipType(str, Enum):
    """Entity relationship types for UML."""

    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    INHERITANCE = "inheritance"
    IMPLEMENTATION = "implementation"
    DEPENDENCY = "dependency"


class ComponentType(str, Enum):
    """Architecture component types."""

    SERVICE = "service"
    MODULE = "module"
    LIBRARY = "library"
    DATABASE = "database"
    EXTERNAL = "external"


class FileType(str, Enum):
    """File explorer entry types."""

    FILE = "file"
    FOLDER = "folder"


class TestType(str, Enum):
    """Test types for testing pyramid."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"


class TestStatus(str, Enum):
    """Test execution status."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


class InsightType(str, Enum):
    """LENS insight types."""

    PATTERN = "pattern"
    ANTI_PATTERN = "anti-pattern"
    RECOMMENDATION = "recommendation"


class ImplementationStatus(str, Enum):
    """Use case implementation status."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    PLANNED = "planned"


# =============================================================================
# BASE MODELS
# =============================================================================


class DashboardBaseModel(BaseModel):
    """Base model with common configuration."""

    model_config = ConfigDict(
        extra="ignore",  # Ignore unknown fields for forward compatibility
        validate_assignment=True,
        str_strip_whitespace=True,
    )


# =============================================================================
# REPOSITORY SUMMARY (SQLite: repo_summary table)
# =============================================================================


class RepoSummary(DashboardBaseModel):
    """
    Repository summary for Overview tab.
    
    Maps to: repo_summary table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    repo_name: str = Field(..., description="Repository display name")
    repo_slug: str = Field(..., description="URL-safe repository identifier")
    description: Optional[str] = Field(default=None, description="Repository description")
    primary_language: str = Field(..., description="Main programming language")
    tech_stack: list[str] = Field(default_factory=list, description="Technology stack")
    total_loc: int = Field(ge=0, description="Total lines of code")
    file_count: int = Field(ge=0, description="Total file count")
    contributor_count: int = Field(ge=0, description="Number of contributors")
    health_score: int = Field(ge=0, le=100, description="Health score 0-100")
    last_commit_date: datetime = Field(..., description="Last commit timestamp")
    created_at: Optional[datetime] = Field(default=None, description="Repository creation date")
    llm_overview: Optional[str] = Field(default=None, description="LLM-generated business overview")

    @field_validator("health_score")
    @classmethod
    def validate_health_score(cls, v: int) -> int:
        """Ensure health score is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError(f"health_score must be 0-100, got {v}")
        return v


# =============================================================================
# USE CASES (SQLite: use_cases table)
# =============================================================================


class UseCase(DashboardBaseModel):
    """
    Business use case extracted from code.
    
    Maps to: use_cases table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    title: str = Field(..., description="Use case title")
    category: str = Field(..., description="Category (e.g., Authentication)")
    business_value: Optional[str] = Field(default=None, description="LLM-generated business value")
    user_stories: list[str] = Field(default_factory=list, description="User stories")
    acceptance_criteria: list[str] = Field(default_factory=list, description="Acceptance criteria")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")
    implementation_status: ImplementationStatus = Field(
        default=ImplementationStatus.PLANNED, description="Implementation status"
    )
    related_files: list[str] = Field(default_factory=list, description="Related file paths")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")


# =============================================================================
# METRICS (SQLite: metrics_summary, metrics_by_file tables)
# =============================================================================


class MetricsSummary(DashboardBaseModel):
    """
    Aggregate code metrics.
    
    Maps to: metrics_summary table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    total_loc: int = Field(ge=0, description="Total lines of code")
    code_loc: int = Field(ge=0, description="Lines of code (excluding comments/blanks)")
    comment_loc: int = Field(ge=0, description="Comment lines")
    avg_complexity: float = Field(ge=0, description="Average cyclomatic complexity")
    max_complexity: int = Field(ge=0, description="Maximum cyclomatic complexity")
    maintainability_index: float = Field(ge=0, le=100, description="Maintainability index 0-100")
    technical_debt_hours: int = Field(ge=0, description="Technical debt in hours")
    calculated_at: datetime = Field(..., description="Calculation timestamp")


class MetricsByFile(DashboardBaseModel):
    """
    Per-file metrics for drill-down.
    
    Maps to: metrics_by_file table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    file_path: str = Field(..., description="Relative file path")
    language: Optional[str] = Field(default=None, description="Programming language")
    loc: int = Field(ge=0, description="Lines of code")
    complexity: int = Field(ge=0, description="Cyclomatic complexity")
    maintainability: float = Field(ge=0, le=100, description="Maintainability score")
    churn_count: int = Field(ge=0, description="Changes in last 30 days")
    last_modified: Optional[datetime] = Field(default=None, description="Last modification timestamp")


# =============================================================================
# SECURITY (SQLite: vulnerabilities table)
# =============================================================================


class Vulnerability(DashboardBaseModel):
    """
    Security vulnerability.
    
    Maps to: vulnerabilities table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    cve_id: Optional[str] = Field(default=None, description="CVE identifier")
    severity: Severity = Field(..., description="Vulnerability severity")
    package_name: str = Field(..., description="Affected package")
    package_version: str = Field(..., description="Affected version")
    fixed_version: Optional[str] = Field(default=None, description="Version with fix")
    description: str = Field(..., description="Vulnerability description")
    file_path: Optional[str] = Field(default=None, description="Location in code")
    line_number: Optional[int] = Field(default=None, ge=1, description="Line number")
    remediation: Optional[str] = Field(default=None, description="Remediation guidance")
    detected_at: Optional[datetime] = Field(default=None, description="Detection timestamp")


# =============================================================================
# DEPENDENCIES (SQLite: packages table)
# =============================================================================


class Package(DashboardBaseModel):
    """
    Package dependency.
    
    Maps to: packages table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    package_name: str = Field(..., description="Package name")
    package_version: Optional[str] = Field(default=None, description="Installed version")
    package_type: PackageType = Field(..., description="Dependency type")
    license: Optional[str] = Field(default=None, description="License type")
    size_kb: Optional[int] = Field(default=None, ge=0, description="Package size in KB")
    vulnerability_count: int = Field(default=0, ge=0, description="Known vulnerabilities")
    parent_package_id: Optional[int] = Field(default=None, description="Parent package for transitive deps")
    installed_at: Optional[datetime] = Field(default=None, description="Installation timestamp")


# =============================================================================
# CODE QUALITY (SQLite: code_smells table)
# =============================================================================


class CodeSmell(DashboardBaseModel):
    """
    Code quality issue.
    
    Maps to: code_smells table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    smell_type: str = Field(..., description="Smell type (e.g., Long Method)")
    category: SmellCategory = Field(..., description="Smell category")
    severity: Severity = Field(..., description="Severity level")
    file_path: str = Field(..., description="File location")
    line_number: int = Field(ge=1, description="Line number")
    code_snippet: Optional[str] = Field(default=None, description="Code snippet")
    explanation: Optional[str] = Field(default=None, description="LLM-generated explanation")
    remediation: Optional[str] = Field(default=None, description="LLM-generated remediation")
    effort_hours: int = Field(default=1, ge=1, description="Estimated fix effort")
    detected_at: Optional[datetime] = Field(default=None, description="Detection timestamp")


# =============================================================================
# DOMAIN MODEL (SQLite: entities, relationships tables)
# =============================================================================


class Entity(DashboardBaseModel):
    """
    Domain entity from DDD analysis.
    
    Maps to: entities table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    name: str = Field(..., description="Entity name")
    type: EntityType = Field(..., description="Entity type (aggregate, value object, etc.)")
    description: Optional[str] = Field(default=None, description="LLM-generated description")
    file_path: Optional[str] = Field(default=None, description="Source file")
    line_range: Optional[str] = Field(default=None, description="Line range (e.g., '45-120')")
    attributes: list[dict[str, Any]] = Field(default_factory=list, description="Entity attributes")
    methods: list[dict[str, Any]] = Field(default_factory=list, description="Entity methods")
    stereotypes: list[str] = Field(default_factory=list, description="UML stereotypes")


class Relationship(DashboardBaseModel):
    """
    Entity relationship for UML.
    
    Maps to: relationships table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    source_entity: str = Field(..., description="Source entity name")
    target_entity: str = Field(..., description="Target entity name")
    relationship_type: RelationshipType = Field(..., description="Relationship type")
    cardinality: Optional[str] = Field(default=None, description="Cardinality (e.g., '1..n')")
    label: Optional[str] = Field(default=None, description="Relationship label")
    bidirectional: bool = Field(default=False, description="Is bidirectional")


# =============================================================================
# ARCHITECTURE (SQLite: components table)
# =============================================================================


class Component(DashboardBaseModel):
    """
    Architecture component.
    
    Maps to: components table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    name: str = Field(..., description="Component name")
    type: ComponentType = Field(..., description="Component type")
    description: Optional[str] = Field(default=None, description="LLM-generated description")
    dependencies: list[str] = Field(default_factory=list, description="Component dependencies")
    api_count: int = Field(default=0, ge=0, description="Number of API endpoints")
    loc: int = Field(default=0, ge=0, description="Lines of code")
    layer: Optional[str] = Field(default=None, description="Architecture layer")


# =============================================================================
# FILE EXPLORER (SQLite: files table)
# =============================================================================


class FileEntry(DashboardBaseModel):
    """
    File system entry for Code Explorer.
    
    Maps to: files table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    file_path: str = Field(..., description="Full relative path")
    file_name: str = Field(..., description="File or folder name")
    file_type: FileType = Field(..., description="File or folder")
    parent_path: Optional[str] = Field(default=None, description="Parent directory path")
    language: Optional[str] = Field(default=None, description="Programming language")
    loc: Optional[int] = Field(default=None, ge=0, description="Lines of code")
    complexity: Optional[int] = Field(default=None, ge=0, description="Complexity score")
    last_modified: Optional[datetime] = Field(default=None, description="Last modification")
    churn_count: Optional[int] = Field(default=None, ge=0, description="Change frequency")


# =============================================================================
# CODE SNIPPETS (SQLite: code_snippets table)
# =============================================================================


class CodeSnippet(DashboardBaseModel):
    """
    Highlighted code example.
    
    Maps to: code_snippets table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    title: str = Field(..., description="Snippet title")
    file_path: str = Field(..., description="Source file")
    start_line: int = Field(ge=1, description="Start line")
    end_line: int = Field(ge=1, description="End line")
    language: str = Field(..., description="Programming language")
    code: str = Field(..., description="Code content")
    explanation: Optional[str] = Field(default=None, description="LLM-generated explanation")
    category: str = Field(default="example", description="pattern|anti-pattern|example|entry-point")


# =============================================================================
# TESTING (SQLite: test_results table)
# =============================================================================


class TestResult(DashboardBaseModel):
    """
    Test execution result.
    
    Maps to: test_results table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    test_name: str = Field(..., description="Test function name")
    test_type: TestType = Field(..., description="Test type")
    status: TestStatus = Field(..., description="Execution status")
    duration_ms: int = Field(ge=0, description="Execution time in ms")
    file_path: Optional[str] = Field(default=None, description="Test file path")
    failure_message: Optional[str] = Field(default=None, description="Failure message if failed")
    run_at: Optional[datetime] = Field(default=None, description="Execution timestamp")


# =============================================================================
# LENS INSIGHTS (SQLite: lens_insights table)
# =============================================================================


class LENSInsight(DashboardBaseModel):
    """
    LENS analysis insight.
    
    Maps to: lens_insights table in dashboard.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    insight_type: InsightType = Field(..., description="Insight type")
    category: str = Field(..., description="Category")
    description: str = Field(..., description="LLM-generated description")
    evidence: list[str] = Field(default_factory=list, description="File path evidence")
    impact: Severity = Field(default=Severity.MEDIUM, description="Impact level")
    confidence: int = Field(ge=0, le=100, description="Confidence 0-100")
    detected_at: Optional[datetime] = Field(default=None, description="Detection timestamp")


# =============================================================================
# REFACTORING (SQLite: refactoring_suggestions view)
# =============================================================================


class RefactoringSuggestion(DashboardBaseModel):
    """
    Refactoring recommendation.
    
    This is typically a computed view from code_smells.
    """

    id: int = Field(default=1, description="Primary key")
    suggestion: str = Field(..., description="Suggestion title")
    file_path: str = Field(..., description="Target file")
    severity: Severity = Field(..., description="Severity level")
    effort_hours: int = Field(ge=1, description="Estimated effort")
    priority_bucket: str = Field(..., description="quick_win|high_priority|backlog")


# =============================================================================
# EXECUTIVE KPI (SQLite: executive_kpis view)
# =============================================================================


class ExecutiveKPI(DashboardBaseModel):
    """
    Executive summary KPI.
    
    This is typically a computed view.
    """

    health_score: int = Field(ge=0, le=100, description="Overall health")
    critical_vulnerabilities: int = Field(ge=0, description="Critical + high vulns")
    tech_debt_hours: int = Field(ge=0, description="Technical debt hours")
    test_pass_rate: float = Field(ge=0, le=100, description="Test pass percentage")
    maintainability: float = Field(ge=0, le=100, description="Maintainability index")


# =============================================================================
# REPOSITORY REGISTRY (SQLite: registry.sqlite)
# =============================================================================


class RepositoryRegistry(DashboardBaseModel):
    """
    Repository entry in the landing page registry.
    
    Maps to: repositories table in registry.sqlite
    """

    id: int = Field(default=1, description="Primary key")
    slug: str = Field(..., description="URL-safe identifier")
    name: str = Field(..., description="Display name")
    description: Optional[str] = Field(default=None, description="Description")
    icon: str = Field(default="📁", description="Emoji icon")
    primary_language: Optional[str] = Field(default=None, description="Main language")
    health_score: int = Field(default=0, ge=0, le=100, description="Health score")
    total_loc: int = Field(default=0, ge=0, description="Lines of code")
    file_count: int = Field(default=0, ge=0, description="File count")
    last_analyzed_at: Optional[datetime] = Field(default=None, description="Last analysis")
    tags: list[str] = Field(default_factory=list, description="Tags")
    dashboard_path: Optional[str] = Field(default=None, description="Path to dashboard")


# =============================================================================
# SQLITE SCHEMA GENERATOR
# =============================================================================


class SQLiteSchemaGenerator:
    """
    Generate SQLite DDL from Pydantic models.
    
    Usage:
        schema_sql = SQLiteSchemaGenerator.generate_full_schema()
    """

    # Pydantic type to SQLite type mapping
    TYPE_MAP: dict[type, str] = {
        int: "INTEGER",
        float: "REAL",
        str: "TEXT",
        bool: "INTEGER",
        datetime: "TEXT",
        list: "TEXT",  # JSON encoded
        dict: "TEXT",  # JSON encoded
    }
    
    # Tables to generate from models
    TABLES: list[tuple[str, type[BaseModel]]] = [
        ("repo_summary", RepoSummary),
        ("use_cases", UseCase),
        ("metrics_summary", MetricsSummary),
        ("metrics_by_file", MetricsByFile),
        ("vulnerabilities", Vulnerability),
        ("packages", Package),
        ("code_smells", CodeSmell),
        ("entities", Entity),
        ("relationships", Relationship),
        ("components", Component),
        ("files", FileEntry),
        ("code_snippets", CodeSnippet),
        ("test_results", TestResult),
        ("lens_insights", LENSInsight),
    ]

    def __init__(self) -> None:
        """Initialize schema generator."""
        self.tables = self.TABLES

    @classmethod
    def _get_sqlite_type(cls, python_type: type) -> str:
        """Map Python type to SQLite type."""
        # Handle Optional types
        origin = getattr(python_type, "__origin__", None)
        if origin is type(None):
            return "TEXT"
        
        # Handle Union types (Optional is Union[T, None])
        args = getattr(python_type, "__args__", ())
        if args:
            # Get the non-None type
            for arg in args:
                if arg is not type(None):
                    python_type = arg
                    break

        # Handle list and dict
        if origin in (list, dict):
            return "TEXT"  # JSON encoded

        # Handle enums
        if isinstance(python_type, type) and issubclass(python_type, Enum):
            return "TEXT"

        return cls.TYPE_MAP.get(python_type, "TEXT")

    @classmethod
    def generate_table(cls, table_name: str, model: type[BaseModel]) -> str:
        """Generate CREATE TABLE statement for a model."""
        lines = [f"CREATE TABLE IF NOT EXISTS {table_name} ("]
        columns: list[str] = []
        
        for field_name, field_info in model.model_fields.items():
            sqlite_type = cls._get_sqlite_type(field_info.annotation)
            
            # Check if required (not Optional and no default)
            is_required = field_info.is_required()
            not_null = " NOT NULL" if is_required and field_name != "id" else ""
            
            # Handle primary key
            if field_name == "id":
                columns.append(f"    {field_name} INTEGER PRIMARY KEY AUTOINCREMENT")
            else:
                columns.append(f"    {field_name} {sqlite_type}{not_null}")
        
        lines.append(",\n".join(columns))
        lines.append(");")
        
        return "\n".join(lines)

    @classmethod
    def generate_full_schema(cls) -> str:
        """Generate all table schemas (class method for convenience)."""
        return cls().generate_all()

    def generate_all(self) -> str:
        """Generate all table schemas."""
        statements: list[str] = []
        
        # Header
        statements.append("-- Dashboard Schema v3.0")
        statements.append("-- Generated from Pydantic models")
        statements.append("-- Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml")
        statements.append("")
        
        # Generate each table
        for table_name, model in self.tables:
            statements.append(self.generate_table(table_name, model))
            statements.append("")
        
        # Add indexes
        statements.append("-- Indexes")
        statements.append("CREATE INDEX IF NOT EXISTS idx_repo_slug ON repo_summary(repo_slug);")
        statements.append("CREATE INDEX IF NOT EXISTS idx_use_cases_category ON use_cases(category);")
        statements.append("CREATE INDEX IF NOT EXISTS idx_use_cases_priority ON use_cases(priority);")
        statements.append("CREATE INDEX IF NOT EXISTS idx_vuln_severity ON vulnerabilities(severity);")
        statements.append("CREATE INDEX IF NOT EXISTS idx_vulnerabilities_severity ON vulnerabilities(severity);")
        statements.append("CREATE INDEX IF NOT EXISTS idx_packages_name ON packages(package_name);")
        statements.append("CREATE INDEX IF NOT EXISTS idx_code_smells_file ON code_smells(file_path);")
        statements.append("CREATE INDEX IF NOT EXISTS idx_files_path ON files(file_path);")
        statements.append("")
        
        # Add FTS5 tables
        statements.append("-- Full-Text Search Tables")
        statements.append("CREATE VIRTUAL TABLE IF NOT EXISTS use_cases_fts USING fts5(title, business_value, content=use_cases);")
        statements.append("CREATE VIRTUAL TABLE IF NOT EXISTS packages_fts USING fts5(package_name, content=packages);")
        statements.append("CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(file_path, file_name, content=files);")
        statements.append("")
        
        # Add views
        statements.append("-- Computed Views")
        statements.append("""CREATE VIEW IF NOT EXISTS executive_kpis AS
SELECT
    (SELECT health_score FROM repo_summary LIMIT 1) AS health_score,
    (SELECT COUNT(*) FROM vulnerabilities WHERE severity IN ('critical', 'high')) AS critical_vulnerabilities,
    (SELECT technical_debt_hours FROM metrics_summary LIMIT 1) AS tech_debt_hours,
    COALESCE(
        (SELECT COUNT(*) FROM test_results WHERE status = 'pass') * 100.0 / 
        NULLIF((SELECT COUNT(*) FROM test_results), 0),
        0
    ) AS test_pass_rate,
    (SELECT maintainability_index FROM metrics_summary LIMIT 1) AS maintainability;""")
        statements.append("")
        
        statements.append("""CREATE VIEW IF NOT EXISTS refactoring_suggestions AS
SELECT
    id,
    smell_type AS suggestion,
    file_path,
    severity,
    effort_hours,
    CASE
        WHEN severity = 'critical' AND effort_hours < 4 THEN 'quick_win'
        WHEN severity IN ('high', 'critical') THEN 'high_priority'
        ELSE 'backlog'
    END AS priority_bucket
FROM code_smells
ORDER BY 
    CASE severity 
        WHEN 'critical' THEN 1
        WHEN 'high' THEN 2
        WHEN 'medium' THEN 3
        ELSE 4
    END,
    effort_hours ASC;""")
        
        return "\n".join(statements)


# =============================================================================
# VALIDATION FUNCTION
# =============================================================================


def validate_dashboard_data(data: dict[str, Any]) -> tuple[bool, list[str]]:
    """
    Validate dashboard JSON data against the schema.
    
    Args:
        data: Dictionary of dashboard data
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors: list[str] = []
    
    # repo_summary is REQUIRED
    repo_data = data.get("repo_summary", data.get("repo"))
    if not repo_data:
        errors.append("repo_summary: Required field is missing")
    else:
        try:
            RepoSummary(**repo_data)
        except Exception as e:
            errors.append(f"repo_summary: {e}")
    
    # Validate use cases
    if "use_cases" in data:
        for i, uc in enumerate(data.get("use_cases", [])):
            try:
                UseCase(**uc)
            except Exception as e:
                errors.append(f"use_cases[{i}]: {e}")
    
    # Validate metrics
    if "metrics_summary" in data:
        try:
            MetricsSummary(**data["metrics_summary"])
        except Exception as e:
            errors.append(f"metrics_summary: {e}")
    
    # Validate vulnerabilities
    if "vulnerabilities" in data:
        for i, vuln in enumerate(data.get("vulnerabilities", [])):
            try:
                Vulnerability(**vuln)
            except Exception as e:
                errors.append(f"vulnerabilities[{i}]: {e}")
    
    # Validate packages
    if "packages" in data:
        for i, pkg in enumerate(data.get("packages", [])):
            try:
                Package(**pkg)
            except Exception as e:
                errors.append(f"packages[{i}]: {e}")
    
    # Validate code smells
    if "code_smells" in data:
        for i, smell in enumerate(data.get("code_smells", [])):
            try:
                CodeSmell(**smell)
            except Exception as e:
                errors.append(f"code_smells[{i}]: {e}")
    
    # Validate entities
    if "entities" in data:
        for i, entity in enumerate(data.get("entities", [])):
            try:
                Entity(**entity)
            except Exception as e:
                errors.append(f"entities[{i}]: {e}")
    
    # Validate relationships
    if "relationships" in data:
        for i, rel in enumerate(data.get("relationships", [])):
            try:
                Relationship(**rel)
            except Exception as e:
                errors.append(f"relationships[{i}]: {e}")
    
    # Validate components
    if "components" in data:
        for i, comp in enumerate(data.get("components", [])):
            try:
                Component(**comp)
            except Exception as e:
                errors.append(f"components[{i}]: {e}")
    
    return len(errors) == 0, errors
