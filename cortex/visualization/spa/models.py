"""
SPA Dashboard Data Models.

Provides strongly-typed models for dashboard generation matching GPT spec.

Authority: CORE-011 (Type hints), CORE-012 (Docstrings)
AC-ID: SPA-SUITE-001
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any


class Severity(Enum):
    """Severity levels for findings and use cases."""
    
    INFO = "info"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UseCasePersona(Enum):
    """Target personas for use cases."""
    
    LEADERSHIP = "leadership"
    PRODUCTION_OWNER = "production_owner"
    ENGINEER = "engineer"
    SECURITY = "security"
    QA = "qa"


class UseCaseCategory(Enum):
    """Categories for use case classification."""
    
    DELIVERY = "delivery"
    RISK = "risk"
    COMPLIANCE = "compliance"
    RELIABILITY = "reliability"
    COST = "cost"
    MAINTAINABILITY = "maintainability"
    OBSERVABILITY = "observability"


@dataclass
class UseCase:
    """
    Use case definition for dashboard.
    
    Supports GPT-specified filtering by persona, category, severity.
    
    Attributes:
        id: Unique identifier
        title: Short title (displayed)
        summary: Description of the use case
        persona: Target persona
        category: Use case category
        severity: Severity level
        tags: Searchable tags
        signals: Data signals related to this use case
        actions: Recommended actions
        related_tabs: Tabs where related data can be found
    """
    
    id: str
    title: str
    summary: str
    persona: UseCasePersona
    category: UseCaseCategory
    severity: Severity
    tags: List[str] = field(default_factory=list)
    signals: List[str] = field(default_factory=list)
    actions: List[str] = field(default_factory=list)
    related_tabs: List[str] = field(default_factory=list)


@dataclass
class VulnerabilityFinding:
    """Security vulnerability finding."""
    
    id: str
    title: str
    description: str
    severity: Severity
    cwe_id: Optional[str] = None
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    recommendation: Optional[str] = None


@dataclass
class DependencyInfo:
    """Package dependency information."""
    
    name: str
    version: str
    latest_version: Optional[str] = None
    is_outdated: bool = False
    has_vulnerabilities: bool = False
    vulnerability_count: int = 0


@dataclass 
class QualityMetric:
    """Code quality metric."""
    
    name: str
    value: float
    threshold: Optional[float] = None
    status: str = "ok"  # ok, warning, critical


@dataclass
class ArchitectureLayer:
    """Architecture layer definition."""
    
    name: str
    module_count: int
    loc: int
    complexity: float
    dependencies: List[str] = field(default_factory=list)


@dataclass
class TestingMetrics:
    """Testing coverage and metrics."""
    
    coverage_pct: float
    unit_tests: int
    integration_tests: int
    e2e_tests: int
    risky_files: List[str] = field(default_factory=list)
    uncovered_files: List[str] = field(default_factory=list)


@dataclass
class Recommendation:
    """Actionable recommendation."""
    
    id: str
    title: str
    description: str
    priority: str  # p0, p1, p2
    category: str
    effort: str  # low, medium, high
    impact: str  # low, medium, high


@dataclass
class RepoDashboardData:
    """
    Complete dashboard data model for a repository.
    
    This model is embedded as JSON into each repo's dashboard HTML.
    Matches GPT specification section 3.
    
    Attributes:
        repo_slug: URL-safe identifier
        display_name: Human-readable name
        owner: Repository owner/team
        primary_language: Main programming language
        health_score: Overall health (0-100)
        risk_score: Risk level (0-100)
        loc: Lines of code
        files: Total files
        services_count: Number of services/modules
        coverage_pct: Test coverage percentage
        last_analyzed_at: Timestamp of analysis
        version: CORTEX version used
        tags: Repository tags
        overview_metrics: Overview tab metrics
        architecture: Architecture layer data
        dependencies: Dependency information
        quality: Quality metrics
        vulnerabilities: Security findings
        testing: Testing metrics
        use_cases: Use case definitions
        recommendations: Actionable recommendations
    """
    
    # Core identifiers
    repo_slug: str
    display_name: str
    owner: str
    primary_language: str
    
    # Summary metrics
    health_score: int
    risk_score: int
    loc: int
    files: int
    services_count: int
    coverage_pct: float
    
    # Metadata
    last_analyzed_at: str
    version: str = "8.0"
    tags: List[str] = field(default_factory=list)
    
    # Tab data
    overview_metrics: Dict[str, Any] = field(default_factory=dict)
    architecture: List[ArchitectureLayer] = field(default_factory=list)
    dependencies: List[DependencyInfo] = field(default_factory=list)
    quality: List[QualityMetric] = field(default_factory=list)
    vulnerabilities: List[VulnerabilityFinding] = field(default_factory=list)
    testing: Optional[TestingMetrics] = None
    use_cases: List[UseCase] = field(default_factory=list)
    recommendations: List[Recommendation] = field(default_factory=list)


@dataclass
class RepoManifestEntry:
    """
    Landing page manifest entry for a repository.
    
    Embedded into landing page for tile rendering.
    Matches GPT specification section 3.
    """
    
    slug: str
    display_name: str
    owner: str
    primary_language: str
    health_score: int
    risk_score: int
    loc: int
    files: int
    services_count: int
    coverage_pct: float
    last_analyzed_at: str
    version: str
    tags: List[str] = field(default_factory=list)
    icon: str = "📁"


@dataclass
class DashboardSuiteConfig:
    """
    Configuration for dashboard suite generation.
    
    Attributes:
        repos: List of repo manifest entries
        output_dir: Output directory path
        title: Suite title
        subtitle: Suite subtitle
        version: CORTEX version
        logo_path: Path to logo image
    """
    
    repos: List[RepoManifestEntry]
    output_dir: str
    title: str = "CORTEX Repository Intelligence"
    subtitle: str = "Offline enterprise dashboards • file:// compatible • MCP-generated"
    version: str = "8.0"
    logo_path: str = "images/cortex-logo.png"


def to_dict(obj: Any) -> Any:
    """
    Convert dataclass to dictionary recursively.
    
    Handles nested dataclasses, enums, and datetime objects.
    
    Args:
        obj: Object to convert
        
    Returns:
        Dictionary representation
    """
    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for field_name in obj.__dataclass_fields__:
            value = getattr(obj, field_name)
            result[field_name] = to_dict(value)
        return result
    elif isinstance(obj, Enum):
        return obj.value
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, list):
        return [to_dict(item) for item in obj]
    elif isinstance(obj, dict):
        return {key: to_dict(value) for key, value in obj.items()}
    else:
        return obj
