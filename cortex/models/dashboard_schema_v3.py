"""
Dashboard Schema v3.0 - SQLite-First Architecture
==================================================

Purpose: Pydantic models for Enterprise Repository Intelligence Platform
Version: 3.0
Created: 2026-02-03
Authority: PHASE-21-ENTERPRISE-REPOSITORY-INTELLIGENCE.yaml

Architecture:
- SQLite-first design with native pagination, search, filtering
- Separate database per repository (SOLID compliance)
- 13 tabs with role-specific content
- Full-text search via FTS5
- Views for computed data (executive KPIs, refactoring suggestions)

Database Separation:
- cortex.db: CORTEX internal operations (audit logs, wiring registry)
- registry.sqlite: Repository registry for landing page
- dashboard.sqlite: Per-repo intelligence data (this schema)

Governance: CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single canonical)
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field, validator


# =============================================================================
# ENUMS - Type-Safe Status Values
# =============================================================================


class HealthStatus(str, Enum):
    """Repository health status."""

    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"


class Severity(str, Enum):
    """Issue severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Priority(str, Enum):
    """Task priority levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ImplementationStatus(str, Enum):
    """Feature implementation status."""

    IMPLEMENTED = "implemented"
    PARTIAL = "partial"
    PLANNED = "planned"


class PackageType(str, Enum):
    """Dependency package types."""

    DIRECT = "direct"
    DEV = "dev"
    TRANSITIVE = "transitive"


class EntityType(str, Enum):
    """Domain model entity types."""

    AGGREGATE_ROOT = "aggregate_root"
    ENTITY = "entity"
    VALUE_OBJECT = "value_object"
    SERVICE = "service"


class RelationshipType(str, Enum):
    """UML relationship types."""

    ASSOCIATION = "association"
    AGGREGATION = "aggregation"
    COMPOSITION = "composition"
    INHERITANCE = "inheritance"


class ComponentType(str, Enum):
    """Architecture component types."""

    SERVICE = "service"
    MODULE = "module"
    LIBRARY = "library"
    DATABASE = "database"
    EXTERNAL = "external"


class FileType(str, Enum):
    """File system item types."""

    FILE = "file"
    FOLDER = "folder"


class TestType(str, Enum):
    """Test classification types."""

    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"


class TestStatus(str, Enum):
    """Test execution status."""

    PASS = "pass"
    FAIL = "fail"
    SKIP = "skip"


class InsightType(str, Enum):
    """LENS insight classification."""

    PATTERN = "pattern"
    ANTI_PATTERN = "anti-pattern"
    RECOMMENDATION = "recommendation"


class SmellCategory(str, Enum):
    """Code smell categories."""

    COMPLEXITY = "complexity"
    DUPLICATION = "duplication"
    SMELL = "smell"
    MAINTAINABILITY = "maintainability"


# =============================================================================
# TABLE MODELS - SQLite Table Definitions
# =============================================================================


class RepoSummary(BaseModel):
    """
    Overview tab — high-level repository metadata.

    SQLite Table: repo_summary
    Purpose: Single-row summary of repository health and stats
    """

    id: int = Field(1, description="Primary key (always 1 for singleton)")
    repo_name: str = Field(..., description="Repository display name")
    repo_slug: str = Field(..., description="URL-safe identifier")
    description: Optional[str] = Field(None, description="Repository description")
    primary_language: str = Field(..., description="Primary programming language")
    tech_stack: List[str] = Field(default_factory=list, description="Technology stack")
    total_loc: int = Field(0, description="Total lines of code")
    file_count: int = Field(0, description="Number of files")
    contributor_count: int = Field(0, description="Number of contributors")
    health_score: int = Field(0, ge=0, le=100, description="Overall health (0-100)")
    last_commit_date: datetime = Field(..., description="Most recent commit")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    llm_overview: Optional[str] = Field(
        None, description="LLM-generated business summary"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "id": 1,
                "repo_name": "CORTEX",
                "repo_slug": "cortex",
                "description": "Cognitive Real-Time Execution System",
                "primary_language": "Python",
                "tech_stack": ["Python", "FastAPI", "SQLite", "Docker"],
                "total_loc": 45000,
                "file_count": 350,
                "contributor_count": 5,
                "health_score": 85,
                "last_commit_date": "2026-02-03T10:30:00Z",
                "llm_overview": "Enterprise AI orchestration platform...",
            }
        }


class UseCase(BaseModel):
    """
    Use Cases tab — business capabilities.

    SQLite Table: use_cases
    Purpose: PAGINATED list of business use cases with full-text search
    """

    id: int = Field(..., description="Auto-increment primary key")
    title: str = Field(..., description="Use case title")
    category: str = Field(..., description="Category (e.g., Authentication)")
    business_value: Optional[str] = Field(None, description="LLM-generated value prop")
    user_stories: List[str] = Field(default_factory=list)
    acceptance_criteria: List[str] = Field(default_factory=list)
    priority: Priority = Field(Priority.MEDIUM)
    implementation_status: ImplementationStatus = Field(ImplementationStatus.PLANNED)
    related_files: List[str] = Field(default_factory=list, description="File paths")
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class MetricsSummary(BaseModel):
    """
    Metrics tab — aggregate code metrics.

    SQLite Table: metrics_summary
    Purpose: Single-row aggregate metrics
    """

    id: int = Field(1, description="Primary key (singleton)")
    total_loc: int = Field(0)
    code_loc: int = Field(0, description="Excluding comments/blanks")
    comment_loc: int = Field(0)
    avg_complexity: float = Field(0.0)
    max_complexity: int = Field(0)
    maintainability_index: float = Field(0.0, ge=0, le=100)
    technical_debt_hours: int = Field(0)
    calculated_at: datetime = Field(default_factory=datetime.utcnow)


class MetricsByFile(BaseModel):
    """
    Metrics drill-down — per-file metrics.

    SQLite Table: metrics_by_file
    Purpose: Detailed file-level metrics for drill-down
    """

    id: int = Field(..., description="Auto-increment PK")
    file_path: str = Field(...)
    language: str = Field(...)
    loc: int = Field(0)
    complexity: int = Field(0)
    maintainability: float = Field(0.0)
    churn_count: int = Field(0, description="Commits in last 30 days")
    last_modified: datetime = Field(default_factory=datetime.utcnow)


class Vulnerability(BaseModel):
    """
    Security tab — CVEs and security issues.

    SQLite Table: vulnerabilities
    Purpose: PAGINATED security findings with severity filtering
    """

    id: int = Field(..., description="Auto-increment PK")
    cve_id: Optional[str] = Field(None)
    severity: Severity = Field(...)
    package_name: str = Field(...)
    package_version: str = Field(...)
    fixed_version: Optional[str] = Field(None)
    description: str = Field(...)
    file_path: Optional[str] = Field(None)
    line_number: Optional[int] = Field(None)
    remediation: Optional[str] = Field(None)
    detected_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class Package(BaseModel):
    """
    Dependencies tab — package tree.

    SQLite Table: packages
    Purpose: PAGINATED dependency list with tree structure
    """

    id: int = Field(..., description="Auto-increment PK")
    package_name: str = Field(...)
    package_version: str = Field(...)
    package_type: PackageType = Field(PackageType.DIRECT)
    license: Optional[str] = Field(None)
    size_kb: int = Field(0)
    vulnerability_count: int = Field(0)
    parent_package_id: Optional[int] = Field(
        None, description="For tree structure (transitive deps)"
    )
    installed_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class CodeSmell(BaseModel):
    """
    Code Quality tab — quality issues.

    SQLite Table: code_smells
    Purpose: PAGINATED quality issues with LLM explanations
    """

    id: int = Field(..., description="Auto-increment PK")
    smell_type: str = Field(..., description="e.g., 'Long Method', 'God Class'")
    category: SmellCategory = Field(...)
    severity: Severity = Field(...)
    file_path: str = Field(...)
    line_number: int = Field(...)
    code_snippet: Optional[str] = Field(None)
    explanation: Optional[str] = Field(None, description="LLM-generated")
    remediation: Optional[str] = Field(None, description="LLM-generated")
    effort_hours: int = Field(1, ge=1)
    detected_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class Entity(BaseModel):
    """
    Domain Model tab — domain entities.

    SQLite Table: entities
    Purpose: Domain-driven design entity catalog
    """

    id: int = Field(..., description="Auto-increment PK")
    name: str = Field(...)
    type: EntityType = Field(...)
    description: Optional[str] = Field(None, description="LLM-generated")
    file_path: str = Field(...)
    line_range: str = Field(..., description="e.g., '45-120'")
    attributes: List[Dict[str, Any]] = Field(default_factory=list)
    methods: List[Dict[str, Any]] = Field(default_factory=list)
    stereotypes: List[str] = Field(default_factory=list)

    class Config:
        use_enum_values = True


class Relationship(BaseModel):
    """
    Domain Model tab — entity relationships.

    SQLite Table: relationships
    Purpose: UML relationship data for diagram generation
    """

    id: int = Field(..., description="Auto-increment PK")
    source_entity: str = Field(...)
    target_entity: str = Field(...)
    relationship_type: RelationshipType = Field(...)
    cardinality: str = Field(..., description="e.g., '1..n', '0..1'")
    label: Optional[str] = Field(None)
    bidirectional: bool = Field(False)

    class Config:
        use_enum_values = True


class Component(BaseModel):
    """
    Architecture tab — system components.

    SQLite Table: components
    Purpose: Architectural component catalog
    """

    id: int = Field(..., description="Auto-increment PK")
    name: str = Field(...)
    type: ComponentType = Field(...)
    description: Optional[str] = Field(None, description="LLM-generated")
    dependencies: List[str] = Field(
        default_factory=list, description="Component names"
    )
    api_count: int = Field(0)
    loc: int = Field(0)
    layer: str = Field(..., description="e.g., 'Presentation', 'Business', 'Data'")

    class Config:
        use_enum_values = True


class FileEntry(BaseModel):
    """
    Code Explorer tab — file tree.

    SQLite Table: files
    Purpose: PAGINATED file browser with full-text search
    """

    id: int = Field(..., description="Auto-increment PK")
    file_path: str = Field(...)
    file_name: str = Field(...)
    file_type: FileType = Field(...)
    parent_path: Optional[str] = Field(None)
    language: Optional[str] = Field(None)
    loc: int = Field(0)
    complexity: int = Field(0)
    last_modified: datetime = Field(default_factory=datetime.utcnow)
    churn_count: int = Field(0)

    class Config:
        use_enum_values = True


class CodeSnippet(BaseModel):
    """
    Code Explorer tab — highlighted code examples.

    SQLite Table: code_snippets
    Purpose: Curated code examples with LLM explanations
    """

    id: int = Field(..., description="Auto-increment PK")
    title: str = Field(...)
    file_path: str = Field(...)
    start_line: int = Field(...)
    end_line: int = Field(...)
    language: str = Field(...)
    code: str = Field(...)
    explanation: Optional[str] = Field(None, description="LLM-generated")
    category: str = Field(
        ..., description="pattern|anti-pattern|example|entry-point"
    )


class TestResult(BaseModel):
    """
    Testing tab — test execution results.

    SQLite Table: test_results
    Purpose: Test run history with pyramid visualization data
    """

    id: int = Field(..., description="Auto-increment PK")
    test_name: str = Field(...)
    test_type: TestType = Field(...)
    status: TestStatus = Field(...)
    duration_ms: int = Field(0)
    file_path: str = Field(...)
    failure_message: Optional[str] = Field(None)
    run_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


class LENSInsight(BaseModel):
    """
    LENS Analysis tab — CORTEX findings.

    SQLite Table: lens_insights
    Purpose: CORTEX-discovered patterns, anti-patterns, recommendations
    """

    id: int = Field(..., description="Auto-increment PK")
    insight_type: InsightType = Field(...)
    category: str = Field(...)
    description: str = Field(..., description="LLM-generated")
    evidence: List[str] = Field(default_factory=list, description="File paths")
    impact: Severity = Field(...)
    confidence: int = Field(0, ge=0, le=100)
    detected_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        use_enum_values = True


# =============================================================================
# VIEW MODELS - Computed Data (No Duplication)
# =============================================================================


class ExecutiveKPI(BaseModel):
    """
    Executive Summary tab — computed KPIs.

    SQLite View: executive_kpis
    Purpose: Real-time computed executive metrics (no data duplication)
    """

    health_score: int = Field(..., ge=0, le=100)
    critical_vulnerabilities: int = Field(0)
    tech_debt_hours: int = Field(0)
    test_pass_rate: float = Field(0.0, ge=0, le=100)
    maintainability: float = Field(0.0, ge=0, le=100)


class RefactoringSuggestion(BaseModel):
    """
    Refactoring tab — prioritized improvements.

    SQLite View: refactoring_suggestions
    Purpose: Computed from code_smells with priority buckets
    """

    id: int
    suggestion: str
    file_path: str
    severity: Severity
    effort_hours: int
    priority_bucket: str = Field(
        ..., description="quick_win|high_priority|backlog"
    )

    class Config:
        use_enum_values = True


# =============================================================================
# REGISTRY MODELS - Landing Page Data
# =============================================================================


class RepositoryRegistry(BaseModel):
    """
    Landing page repository registry.

    SQLite Database: registry.sqlite
    Table: repositories
    Purpose: Quick repo catalog for index.html tiles
    """

    id: int = Field(..., description="Auto-increment PK")
    slug: str = Field(..., description="URL-safe identifier")
    name: str = Field(...)
    description: Optional[str] = Field(None)
    health_score: int = Field(0, ge=0, le=100)
    primary_language: str = Field(...)
    total_loc: int = Field(0)
    last_updated: datetime = Field(default_factory=datetime.utcnow)
    dashboard_path: str = Field(
        ..., description="Relative path to dashboard.html?repo={slug}"
    )


# =============================================================================
# SQL SCHEMA GENERATOR
# =============================================================================


class SQLiteSchemaGenerator:
    """
    Generate CREATE TABLE/VIEW statements for dashboard.sqlite.

    Usage:
        generator = SQLiteSchemaGenerator()
        schema_sql = generator.generate_full_schema()
    """

    @staticmethod
    def generate_full_schema() -> str:
        """Generate complete SQLite schema with tables, indexes, views, FTS5."""
        return """
-- ============================================================================
-- DASHBOARD.SQLITE SCHEMA v3.0
-- Generated: 2026-02-03
-- Purpose: Per-repository enterprise intelligence data
-- ============================================================================

-- TAB 1: EXECUTIVE SUMMARY / TAB 2: OVERVIEW
CREATE TABLE IF NOT EXISTS repo_summary (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    repo_name TEXT NOT NULL,
    repo_slug TEXT NOT NULL UNIQUE,
    description TEXT,
    primary_language TEXT NOT NULL,
    tech_stack TEXT NOT NULL, -- JSON array
    total_loc INTEGER DEFAULT 0,
    file_count INTEGER DEFAULT 0,
    contributor_count INTEGER DEFAULT 0,
    health_score INTEGER DEFAULT 0 CHECK (health_score BETWEEN 0 AND 100),
    last_commit_date TEXT NOT NULL, -- ISO8601
    created_at TEXT NOT NULL, -- ISO8601
    llm_overview TEXT
);
CREATE INDEX IF NOT EXISTS idx_repo_slug ON repo_summary(repo_slug);

-- TAB 3: USE CASES (PAGINATED)
CREATE TABLE IF NOT EXISTS use_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    category TEXT NOT NULL,
    business_value TEXT,
    user_stories TEXT NOT NULL, -- JSON array
    acceptance_criteria TEXT NOT NULL, -- JSON array
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'critical')),
    implementation_status TEXT NOT NULL CHECK (implementation_status IN ('implemented', 'partial', 'planned')),
    related_files TEXT NOT NULL, -- JSON array
    created_at TEXT NOT NULL -- ISO8601
);
CREATE INDEX IF NOT EXISTS idx_use_case_category ON use_cases(category);
CREATE INDEX IF NOT EXISTS idx_use_case_priority ON use_cases(priority);

-- Full-text search for use cases
CREATE VIRTUAL TABLE IF NOT EXISTS use_cases_fts USING fts5(
    title, business_value, content=use_cases, content_rowid=id
);

-- TAB 8: METRICS
CREATE TABLE IF NOT EXISTS metrics_summary (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    total_loc INTEGER DEFAULT 0,
    code_loc INTEGER DEFAULT 0,
    comment_loc INTEGER DEFAULT 0,
    avg_complexity REAL DEFAULT 0.0,
    max_complexity INTEGER DEFAULT 0,
    maintainability_index REAL DEFAULT 0.0 CHECK (maintainability_index BETWEEN 0 AND 100),
    technical_debt_hours INTEGER DEFAULT 0,
    calculated_at TEXT NOT NULL -- ISO8601
);

CREATE TABLE IF NOT EXISTS metrics_by_file (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL,
    language TEXT NOT NULL,
    loc INTEGER DEFAULT 0,
    complexity INTEGER DEFAULT 0,
    maintainability REAL DEFAULT 0.0,
    churn_count INTEGER DEFAULT 0,
    last_modified TEXT NOT NULL -- ISO8601
);
CREATE INDEX IF NOT EXISTS idx_metrics_file_path ON metrics_by_file(file_path);
CREATE INDEX IF NOT EXISTS idx_metrics_complexity ON metrics_by_file(complexity DESC);

-- TAB 9: SECURITY (PAGINATED)
CREATE TABLE IF NOT EXISTS vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cve_id TEXT,
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    package_name TEXT NOT NULL,
    package_version TEXT NOT NULL,
    fixed_version TEXT,
    description TEXT NOT NULL,
    file_path TEXT,
    line_number INTEGER,
    remediation TEXT,
    detected_at TEXT NOT NULL -- ISO8601
);
CREATE INDEX IF NOT EXISTS idx_vuln_severity ON vulnerabilities(severity);
CREATE INDEX IF NOT EXISTS idx_vuln_package ON vulnerabilities(package_name);

-- TAB 6: DEPENDENCIES (PAGINATED)
CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    package_name TEXT NOT NULL,
    package_version TEXT NOT NULL,
    package_type TEXT NOT NULL CHECK (package_type IN ('direct', 'dev', 'transitive')),
    license TEXT,
    size_kb INTEGER DEFAULT 0,
    vulnerability_count INTEGER DEFAULT 0,
    parent_package_id INTEGER,
    installed_at TEXT NOT NULL, -- ISO8601
    FOREIGN KEY (parent_package_id) REFERENCES packages(id)
);
CREATE INDEX IF NOT EXISTS idx_package_name ON packages(package_name);
CREATE INDEX IF NOT EXISTS idx_package_parent ON packages(parent_package_id);

-- Full-text search for packages
CREATE VIRTUAL TABLE IF NOT EXISTS packages_fts USING fts5(
    package_name, content=packages, content_rowid=id
);

-- TAB 7: CODE QUALITY (PAGINATED)
CREATE TABLE IF NOT EXISTS code_smells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    smell_type TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('complexity', 'duplication', 'smell', 'maintainability')),
    severity TEXT NOT NULL CHECK (severity IN ('low', 'medium', 'high', 'critical')),
    file_path TEXT NOT NULL,
    line_number INTEGER NOT NULL,
    code_snippet TEXT,
    explanation TEXT,
    remediation TEXT,
    effort_hours INTEGER DEFAULT 1 CHECK (effort_hours >= 1),
    detected_at TEXT NOT NULL -- ISO8601
);
CREATE INDEX IF NOT EXISTS idx_smell_type ON code_smells(smell_type);
CREATE INDEX IF NOT EXISTS idx_smell_file_path ON code_smells(file_path);

-- TAB 4: DOMAIN MODEL
CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    type TEXT NOT NULL CHECK (type IN ('aggregate_root', 'entity', 'value_object', 'service')),
    description TEXT,
    file_path TEXT NOT NULL,
    line_range TEXT NOT NULL,
    attributes TEXT NOT NULL, -- JSON array
    methods TEXT NOT NULL, -- JSON array
    stereotypes TEXT NOT NULL -- JSON array
);
CREATE INDEX IF NOT EXISTS idx_entity_name ON entities(name);
CREATE INDEX IF NOT EXISTS idx_entity_type ON entities(type);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relationship_type TEXT NOT NULL CHECK (relationship_type IN ('association', 'aggregation', 'composition', 'inheritance')),
    cardinality TEXT NOT NULL,
    label TEXT,
    bidirectional INTEGER DEFAULT 0 CHECK (bidirectional IN (0, 1))
);
CREATE INDEX IF NOT EXISTS idx_rel_source ON relationships(source_entity);
CREATE INDEX IF NOT EXISTS idx_rel_target ON relationships(target_entity);

-- TAB 5: ARCHITECTURE
CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('service', 'module', 'library', 'database', 'external')),
    description TEXT,
    dependencies TEXT NOT NULL, -- JSON array
    api_count INTEGER DEFAULT 0,
    loc INTEGER DEFAULT 0,
    layer TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_component_name ON components(name);
CREATE INDEX IF NOT EXISTS idx_component_layer ON components(layer);

-- TAB 11: CODE EXPLORER (PAGINATED, SEARCHABLE)
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path TEXT NOT NULL UNIQUE,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL CHECK (file_type IN ('file', 'folder')),
    parent_path TEXT,
    language TEXT,
    loc INTEGER DEFAULT 0,
    complexity INTEGER DEFAULT 0,
    last_modified TEXT NOT NULL, -- ISO8601
    churn_count INTEGER DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_file_path ON files(file_path);
CREATE INDEX IF NOT EXISTS idx_file_parent ON files(parent_path);

-- Full-text search for files
CREATE VIRTUAL TABLE IF NOT EXISTS files_fts USING fts5(
    file_path, file_name, content=files, content_rowid=id
);

CREATE TABLE IF NOT EXISTS code_snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    file_path TEXT NOT NULL,
    start_line INTEGER NOT NULL,
    end_line INTEGER NOT NULL,
    language TEXT NOT NULL,
    code TEXT NOT NULL,
    explanation TEXT,
    category TEXT NOT NULL CHECK (category IN ('pattern', 'anti-pattern', 'example', 'entry-point'))
);
CREATE INDEX IF NOT EXISTS idx_snippet_file ON code_snippets(file_path);

-- TAB 10: TESTING
CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    test_name TEXT NOT NULL,
    test_type TEXT NOT NULL CHECK (test_type IN ('unit', 'integration', 'e2e')),
    status TEXT NOT NULL CHECK (status IN ('pass', 'fail', 'skip')),
    duration_ms INTEGER DEFAULT 0,
    file_path TEXT NOT NULL,
    failure_message TEXT,
    run_at TEXT NOT NULL -- ISO8601
);
CREATE INDEX IF NOT EXISTS idx_test_type ON test_results(test_type);
CREATE INDEX IF NOT EXISTS idx_test_status ON test_results(status);

-- TAB 13: LENS ANALYSIS
CREATE TABLE IF NOT EXISTS lens_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    insight_type TEXT NOT NULL CHECK (insight_type IN ('pattern', 'anti-pattern', 'recommendation')),
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    evidence TEXT NOT NULL, -- JSON array
    impact TEXT NOT NULL CHECK (impact IN ('low', 'medium', 'high', 'critical')),
    confidence INTEGER DEFAULT 0 CHECK (confidence BETWEEN 0 AND 100),
    detected_at TEXT NOT NULL -- ISO8601
);
CREATE INDEX IF NOT EXISTS idx_insight_type ON lens_insights(insight_type);

-- ============================================================================
-- VIEWS - Computed Data (No Duplication)
-- ============================================================================

-- TAB 1: EXECUTIVE SUMMARY
CREATE VIEW IF NOT EXISTS executive_kpis AS
SELECT
    (SELECT health_score FROM repo_summary) AS health_score,
    (SELECT COUNT(*) FROM vulnerabilities WHERE severity IN ('critical', 'high')) AS critical_vulnerabilities,
    (SELECT technical_debt_hours FROM metrics_summary) AS tech_debt_hours,
    (SELECT CAST(COUNT(*) FILTER (WHERE status = 'pass') AS REAL) * 100.0 / 
        NULLIF(COUNT(*), 0) FROM test_results) AS test_pass_rate,
    (SELECT maintainability_index FROM metrics_summary) AS maintainability;

-- TAB 12: REFACTORING
CREATE VIEW IF NOT EXISTS refactoring_suggestions AS
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
    effort_hours ASC;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
"""


# =============================================================================
# VALIDATION UTILITIES
# =============================================================================


def validate_dashboard_data(data: Dict[str, Any]) -> tuple[bool, List[str]]:
    """
    Validate complete dashboard data against schema v3.0.

    Args:
        data: Dictionary with table names as keys

    Returns:
        Tuple of (valid: bool, errors: List[str])

    Example:
        valid, errors = validate_dashboard_data({
            "repo_summary": {...},
            "use_cases": [...],
            ...
        })
    """
    errors = []

    # Required tables
    required_tables = [
        "repo_summary",
        "metrics_summary",
    ]

    for table in required_tables:
        if table not in data:
            errors.append(f"Missing required table: {table}")

    # Validate repo_summary (singleton)
    if "repo_summary" in data:
        try:
            RepoSummary(**data["repo_summary"])
        except Exception as e:
            errors.append(f"repo_summary validation failed: {e}")

    # Validate metrics_summary (singleton)
    if "metrics_summary" in data:
        try:
            MetricsSummary(**data["metrics_summary"])
        except Exception as e:
            errors.append(f"metrics_summary validation failed: {e}")

    # Validate array tables (optional but if present must be valid)
    array_tables = {
        "use_cases": UseCase,
        "vulnerabilities": Vulnerability,
        "packages": Package,
        "code_smells": CodeSmell,
        "entities": Entity,
        "relationships": Relationship,
        "components": Component,
        "files": FileEntry,
        "code_snippets": CodeSnippet,
        "test_results": TestResult,
        "lens_insights": LENSInsight,
    }

    for table_name, model_class in array_tables.items():
        if table_name in data:
            if not isinstance(data[table_name], list):
                errors.append(f"{table_name} must be a list")
                continue

            for i, item in enumerate(data[table_name]):
                try:
                    model_class(**item)
                except Exception as e:
                    errors.append(f"{table_name}[{i}] validation failed: {e}")

    return len(errors) == 0, errors
