"""
Dashboard Data Schema v3 - Comprehensive Data Models.

Standalone schema definitions for v3 API compatibility.
These models are used by the onboarding v3 tool.

AC-ID: AC-DASHBOARD-SCHEMA-V3
Authority: CORE-035 (Single implementation)
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional
from enum import Enum
from datetime import datetime


# =============================================================================
# Enums
# =============================================================================

class Severity(str, Enum):
    """Severity levels for issues."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class Priority(str, Enum):
    """Priority levels for tasks."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TestStatus(str, Enum):
    """Test execution status."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"
    PENDING = "pending"


class ImplementationStatus(str, Enum):
    """Implementation status for use cases."""
    DETECTED = "detected"
    PARTIAL = "partial"
    COMPLETE = "complete"
    DEPRECATED = "deprecated"


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class RepoSummary:
    """Repository summary information."""
    slug: str
    display_name: str
    description: str = ""
    owner: str = ""
    primary_language: str = ""
    version: str = "0.0.0"
    last_analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    health_score: int = 0
    total_files: int = 0
    total_loc: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class UseCase:
    """Use case detection result."""
    use_case_id: str
    title: str
    description: str = ""
    category: str = ""
    actors: List[str] = field(default_factory=list)
    business_value: str = ""
    confidence_score: float = 0.0
    implementation_status: str = "detected"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class MetricsSummary:
    """Code metrics summary."""
    total_loc: int = 0
    code_loc: int = 0
    comment_loc: int = 0
    avg_complexity: float = 0.0
    test_coverage: float = 0.0
    technical_debt_hours: int = 0
    health_score: int = 0
    calculated_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Vulnerability:
    """Security vulnerability."""
    vuln_id: str
    severity: str
    category: str = ""
    description: str = ""
    file_path: str = ""
    line_number: int = 0
    fix_suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Package:
    """Package dependency."""
    name: str
    version: str = ""
    package_type: str = "runtime"
    is_outdated: bool = False
    has_vulnerability: bool = False
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class CodeSmell:
    """Code smell detection."""
    smell_type: str
    severity: str
    file_path: str
    line_number: int = 0
    description: str = ""
    fix_suggestion: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Entity:
    """Domain entity."""
    name: str
    entity_type: str
    file_path: str = ""
    description: str = ""
    attributes: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Relationship:
    """Entity relationship."""
    source_entity: str
    target_entity: str
    relationship_type: str
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Component:
    """Architectural component."""
    name: str
    component_type: str
    file_path: str = ""
    dependencies: List[str] = field(default_factory=list)
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class FileEntry:
    """File information."""
    file_path: str
    language: str = ""
    loc: int = 0
    complexity: int = 0
    last_modified: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class TestResult:
    """Test execution result."""
    test_name: str
    status: str
    duration_seconds: float = 0.0
    file_path: str = ""
    error_message: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class LENSInsight:
    """LENS analysis insight."""
    insight_type: str
    severity: str = "info"
    description: str = ""
    file_path: str = ""
    line_number: int = 0
    recommendation: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class RefactoringSuggestion:
    """Refactoring suggestion."""
    suggestion_type: str
    priority: str
    file_path: str
    description: str
    estimated_effort: str = ""
    impact: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class SQLiteSchemaGenerator:
    """
    Generates SQLite schema for dashboard data persistence.
    
    This is a simplified generator that creates tables matching
    the dashboard data models.
    """
    
    @staticmethod
    def generate_full_schema() -> str:
        """
        Generate complete SQLite schema.
        
        Returns:
            SQL DDL string for all tables
        """
        return '''
-- Dashboard Data Schema v3 SQLite DDL
-- Generated for CORTEX Dashboard persistence

CREATE TABLE IF NOT EXISTS repo_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    description TEXT,
    owner TEXT,
    primary_language TEXT,
    version TEXT,
    last_analyzed_at TEXT NOT NULL,
    health_score INTEGER DEFAULT 0,
    total_files INTEGER DEFAULT 0,
    total_loc INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS use_cases (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    use_case_id TEXT NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    actors TEXT,  -- JSON array
    business_value TEXT,
    confidence_score REAL DEFAULT 0.0,
    implementation_status TEXT DEFAULT 'detected',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS metrics_summary (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL UNIQUE,
    total_loc INTEGER DEFAULT 0,
    code_loc INTEGER DEFAULT 0,
    comment_loc INTEGER DEFAULT 0,
    avg_complexity REAL DEFAULT 0.0,
    test_coverage REAL DEFAULT 0.0,
    technical_debt_hours INTEGER DEFAULT 0,
    health_score INTEGER DEFAULT 0,
    calculated_at TEXT NOT NULL,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS vulnerabilities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    vuln_id TEXT NOT NULL,
    severity TEXT NOT NULL,
    category TEXT,
    description TEXT,
    file_path TEXT,
    line_number INTEGER,
    fix_suggestion TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    name TEXT NOT NULL,
    version TEXT,
    package_type TEXT DEFAULT 'runtime',
    is_outdated INTEGER DEFAULT 0,
    has_vulnerability INTEGER DEFAULT 0,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS code_smells (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    smell_type TEXT NOT NULL,
    severity TEXT NOT NULL,
    file_path TEXT NOT NULL,
    line_number INTEGER,
    description TEXT,
    fix_suggestion TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS entities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    name TEXT NOT NULL,
    entity_type TEXT NOT NULL,
    file_path TEXT,
    description TEXT,
    attributes TEXT,  -- JSON array
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    source_entity TEXT NOT NULL,
    target_entity TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    description TEXT,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS components (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    name TEXT NOT NULL,
    component_type TEXT NOT NULL,
    file_path TEXT,
    dependencies TEXT,  -- JSON array
    description TEXT,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    file_path TEXT NOT NULL,
    language TEXT,
    loc INTEGER DEFAULT 0,
    complexity INTEGER DEFAULT 0,
    last_modified TEXT,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS test_results (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    test_name TEXT NOT NULL,
    status TEXT NOT NULL,
    duration_seconds REAL DEFAULT 0.0,
    file_path TEXT,
    error_message TEXT,
    run_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS lens_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    insight_type TEXT NOT NULL,
    severity TEXT,
    description TEXT NOT NULL,
    file_path TEXT,
    line_number INTEGER,
    recommendation TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

CREATE TABLE IF NOT EXISTS refactoring_suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    repo_slug TEXT NOT NULL,
    suggestion_type TEXT NOT NULL,
    priority TEXT NOT NULL,
    file_path TEXT NOT NULL,
    description TEXT NOT NULL,
    estimated_effort TEXT,
    impact TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (repo_slug) REFERENCES repo_summary(slug)
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_use_cases_repo ON use_cases(repo_slug);
CREATE INDEX IF NOT EXISTS idx_vulnerabilities_repo ON vulnerabilities(repo_slug);
CREATE INDEX IF NOT EXISTS idx_packages_repo ON packages(repo_slug);
CREATE INDEX IF NOT EXISTS idx_code_smells_repo ON code_smells(repo_slug);
CREATE INDEX IF NOT EXISTS idx_entities_repo ON entities(repo_slug);
CREATE INDEX IF NOT EXISTS idx_files_repo ON files(repo_slug);
CREATE INDEX IF NOT EXISTS idx_test_results_repo ON test_results(repo_slug);
CREATE INDEX IF NOT EXISTS idx_lens_insights_repo ON lens_insights(repo_slug);
'''