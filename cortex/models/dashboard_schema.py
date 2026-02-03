"""
Dashboard Data Schema Models v2.0.

Standardized data contract for repository dashboard generation.
All onboarding orchestrators must generate schema-compliant JSON.
All dashboard templates must consume this schema.

AC-ID: AC-DASHBOARD-SCHEMA-002
Authority: CORE-011 (Type hints), CORE-012 (Docstrings), CORE-035 (Single implementation)
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Any, Optional, Tuple
import json
from datetime import datetime

from cortex.common.debug_logger import (
    log_dashboard_debug,
    log_dashboard_schema_validation,
    dashboard_debug
)


@dataclass
class RepoMetadata:
    """
    Repository metadata section.
    
    Attributes:
        slug: URL-safe repository identifier (lowercase, no spaces)
        display_name: Human-readable repository name
        description: Brief repository description
        owner: Repository owner/team
        primary_language: Primary programming language
        version: Repository version
        last_analyzed_at: ISO 8601 timestamp of last analysis
    """
    slug: str
    display_name: str
    description: str
    owner: str
    primary_language: str
    version: str
    last_analyzed_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RepoMetadata":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class OverviewSection:
    """
    Overview section with business context.
    
    Attributes:
        summary: Technical summary
        business_summary: Business-oriented summary
        key_findings: List of important findings
    """
    summary: str
    business_summary: str
    key_findings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OverviewSection":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class MetricsSection:
    """
    Code metrics section.
    
    Attributes:
        health_score: Overall health (0-100)
        risk_score: Risk level (0-100)
        loc: Total lines of code
        code_lines: Lines containing code
        comment_lines: Lines containing comments
        blank_lines: Blank lines
        files: Total file count
        coverage_pct: Test coverage percentage
        languages: Language breakdown {language: lines}
    """
    health_score: int
    risk_score: int
    loc: int
    code_lines: int
    comment_lines: int
    blank_lines: int
    files: int
    coverage_pct: float
    languages: Dict[str, int] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate score ranges."""
        if not (0 <= self.health_score <= 100):
            raise ValueError(f"health_score must be 0-100, got {self.health_score}")
        if not (0 <= self.risk_score <= 100):
            raise ValueError(f"risk_score must be 0-100, got {self.risk_score}")
        if not (0 <= self.coverage_pct <= 100):
            raise ValueError(f"coverage_pct must be 0-100, got {self.coverage_pct}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetricsSection":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class SecurityVulnerability:
    """
    Individual security vulnerability.
    
    Attributes:
        id: Unique vulnerability ID
        title: Vulnerability title
        severity: Severity level (critical|high|medium|low)
        cwe_id: CWE identifier
        location: File location (file.py:line)
        status: Status (open|in_progress|resolved)
        description: Detailed description
    """
    id: str
    title: str
    severity: str
    cwe_id: str
    location: str
    status: str
    description: str
    
    def __post_init__(self):
        """Validate severity."""
        valid_severities = {"critical", "high", "medium", "low"}
        if self.severity not in valid_severities:
            raise ValueError(f"severity must be one of {valid_severities}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecurityVulnerability":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class SecuritySection:
    """
    Security analysis section.
    
    Attributes:
        total_count: Total vulnerability count
        critical_count: Critical vulnerabilities
        high_count: High severity vulnerabilities
        medium_count: Medium severity vulnerabilities
        low_count: Low severity vulnerabilities
        vulnerabilities: List of vulnerabilities
    """
    total_count: int
    critical_count: int
    high_count: int
    medium_count: int
    low_count: int
    vulnerabilities: List[SecurityVulnerability] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["vulnerabilities"] = [v.to_dict() for v in self.vulnerabilities]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SecuritySection":
        """Deserialize from dictionary."""
        vulns = [
            SecurityVulnerability.from_dict(v)
            for v in data.get("vulnerabilities", [])
        ]
        data_copy = data.copy()
        data_copy["vulnerabilities"] = vulns
        return cls(**data_copy)


@dataclass
class PackageDependency:
    """
    Package dependency information.
    
    Attributes:
        name: Package name
        version: Package version
        license: License identifier
        is_direct: Whether this is a direct dependency
    """
    name: str
    version: str
    license: str
    is_direct: bool
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PackageDependency":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class DependenciesSection:
    """
    Dependencies analysis section.
    
    Attributes:
        total_count: Total dependency count
        direct_count: Direct dependencies
        transitive_count: Transitive dependencies
        packages: List of packages
        licenses: License distribution {license: count}
    """
    total_count: int
    direct_count: int
    transitive_count: int
    packages: List[PackageDependency] = field(default_factory=list)
    licenses: Dict[str, int] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["packages"] = [p.to_dict() for p in self.packages]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DependenciesSection":
        """Deserialize from dictionary."""
        packages = [
            PackageDependency.from_dict(p)
            for p in data.get("packages", [])
        ]
        data_copy = data.copy()
        data_copy["packages"] = packages
        return cls(**data_copy)


@dataclass
class CodeSmell:
    """
    Code quality issue.
    
    Attributes:
        id: Unique issue ID
        title: Issue title
        severity: Severity level
        category: Category (complexity|duplication|maintainability)
        location: File location
        description: Detailed description
    """
    id: str
    title: str
    severity: str
    category: str
    location: str
    description: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CodeSmell":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class QualitySection:
    """
    Code quality section.
    
    Attributes:
        maintainability: Maintainability score (0-100)
        readability: Readability score (0-100)
        documentation: Documentation score (0-100)
        complexity: Complexity score (0-100, lower is better)
        code_smells: List of code smells
        hotspots: List of hotspot files
    """
    maintainability: int
    readability: int
    documentation: int
    complexity: int
    code_smells: List[CodeSmell] = field(default_factory=list)
    hotspots: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        data = asdict(self)
        data["code_smells"] = [cs.to_dict() for cs in self.code_smells]
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "QualitySection":
        """Deserialize from dictionary."""
        smells = [
            CodeSmell.from_dict(s)
            for s in data.get("code_smells", [])
        ]
        data_copy = data.copy()
        data_copy["code_smells"] = smells
        return cls(**data_copy)


@dataclass
class UseCase:
    """
    Dashboard use case.
    
    Attributes:
        id: Unique use case ID
        title: Use case title
        persona: Target persona (Engineer|Manager|Leadership|Security|QA)
        category: Category (Delivery|Risk|Compliance|Reliability|Cost|Maintainability|Observability)
        summary: Brief summary
        signals: List of relevant metrics/signals
        recommended_actions: List of recommended actions
        tags: List of tags for filtering
        severity: Severity level (info|low|medium|high|critical)
    """
    id: str
    title: str
    persona: str
    category: str
    summary: str
    signals: List[str]
    recommended_actions: List[str]
    tags: List[str]
    severity: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UseCase":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class LensSection:
    """
    LENS analysis section.
    
    Attributes:
        analysis_summary: Summary of LENS analysis
    """
    analysis_summary: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LensSection":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class RefactoringSection:
    """
    Refactoring recommendations section.
    
    Attributes:
        recommendations: List of refactoring recommendations
    """
    recommendations: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "RefactoringSection":
        """Deserialize from dictionary."""
        return cls(**data)


@dataclass
class RepoDashboardModel:
    """
    Complete repository dashboard data model v2.0.
    
    This is the canonical schema for all dashboard data.
    Onboarding orchestrators MUST generate this schema.
    Dashboard templates MUST consume this schema.
    
    Attributes:
        repo: Repository metadata
        overview: Overview section
        metrics: Code metrics
        security: Security analysis
        dependencies: Dependencies analysis
        quality: Code quality analysis
        use_cases: List of use cases
        lens: LENS analysis
        refactoring: Refactoring recommendations
    
    Example:
        >>> model = RepoDashboardModel(
        ...     repo=RepoMetadata(...),
        ...     overview=OverviewSection(...),
        ...     metrics=MetricsSection(...),
        ...     security=SecuritySection(...),
        ...     dependencies=DependenciesSection(...),
        ...     quality=QualitySection(...),
        ...     use_cases=[],
        ...     lens=LensSection(...),
        ...     refactoring=RefactoringSection(...)
        ... )
        >>> json_str = model.to_json()
    """
    repo: RepoMetadata
    overview: OverviewSection
    metrics: MetricsSection
    security: SecuritySection
    dependencies: DependenciesSection
    quality: QualitySection
    use_cases: List[UseCase]
    lens: LensSection
    refactoring: RefactoringSection
    
    @dashboard_debug
    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize to dictionary.
        
        Returns:
            Dictionary representation
        """
        log_dashboard_debug("Serializing RepoDashboardModel", repo=self.repo.slug)
        
        data = {
            "repo": self.repo.to_dict(),
            "overview": self.overview.to_dict(),
            "metrics": self.metrics.to_dict(),
            "security": self.security.to_dict(),
            "dependencies": self.dependencies.to_dict(),
            "quality": self.quality.to_dict(),
            "use_cases": [uc.to_dict() for uc in self.use_cases],
            "lens": self.lens.to_dict(),
            "refactoring": self.refactoring.to_dict(),
        }
        
        log_dashboard_debug("Serialization complete", sections=len(data))
        return data
    
    @dashboard_debug
    def to_json(self, indent: int = 2) -> str:
        """
        Serialize to JSON string.
        
        Args:
            indent: JSON indentation level
            
        Returns:
            JSON string representation
        """
        log_dashboard_debug("Converting to JSON", repo=self.repo.slug, indent=indent)
        return json.dumps(self.to_dict(), indent=indent)
    
    @classmethod
    @dashboard_debug
    def from_dict(cls, data: Dict[str, Any]) -> "RepoDashboardModel":
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary data
            
        Returns:
            RepoDashboardModel instance
        """
        log_dashboard_debug("Deserializing RepoDashboardModel", keys=list(data.keys()))
        
        return cls(
            repo=RepoMetadata.from_dict(data["repo"]),
            overview=OverviewSection.from_dict(data["overview"]),
            metrics=MetricsSection.from_dict(data["metrics"]),
            security=SecuritySection.from_dict(data["security"]),
            dependencies=DependenciesSection.from_dict(data["dependencies"]),
            quality=QualitySection.from_dict(data["quality"]),
            use_cases=[UseCase.from_dict(uc) for uc in data.get("use_cases", [])],
            lens=LensSection.from_dict(data["lens"]),
            refactoring=RefactoringSection.from_dict(data["refactoring"]),
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> "RepoDashboardModel":
        """
        Deserialize from JSON string.
        
        Args:
            json_str: JSON string
            
        Returns:
            RepoDashboardModel instance
        """
        data = json.loads(json_str)
        return cls.from_dict(data)


@dashboard_debug
def validate_dashboard_model(data: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate dashboard model data structure.
    
    Args:
        data: Data to validate
        
    Returns:
        Tuple of (is_valid, error_list)
        
    Example:
        >>> is_valid, errors = validate_dashboard_model(data)
        >>> if not is_valid:
        ...     print(f"Validation failed: {errors}")
    """
    errors = []
    
    log_dashboard_debug("Starting schema validation", data_keys=list(data.keys()))
    
    # Required top-level sections
    required_sections = [
        "repo", "overview", "metrics", "security",
        "dependencies", "quality", "use_cases", "lens", "refactoring"
    ]
    
    for section in required_sections:
        if section not in data:
            errors.append(f"Missing required section: {section}")
    
    # Validate repo section
    if "repo" in data:
        repo_required = [
            "slug", "display_name", "description", "owner",
            "primary_language", "version", "last_analyzed_at"
        ]
        for field in repo_required:
            if field not in data["repo"]:
                errors.append(f"repo.{field} is required")
    
    # Validate metrics section
    if "metrics" in data:
        metrics_required = [
            "health_score", "risk_score", "loc", "code_lines",
            "comment_lines", "blank_lines", "files", "coverage_pct"
        ]
        for field in metrics_required:
            if field not in data["metrics"]:
                errors.append(f"metrics.{field} is required")
    
    # Validate security section
    if "security" in data:
        security_required = [
            "total_count", "critical_count", "high_count",
            "medium_count", "low_count", "vulnerabilities"
        ]
        for field in security_required:
            if field not in data["security"]:
                errors.append(f"security.{field} is required")
    
    is_valid = len(errors) == 0
    
    log_dashboard_schema_validation(
        "RepoDashboardModel",
        data,
        is_valid,
        errors
    )
    
    return is_valid, errors


# Export public API
__all__ = [
    "RepoMetadata",
    "OverviewSection",
    "MetricsSection",
    "SecurityVulnerability",
    "SecuritySection",
    "PackageDependency",
    "DependenciesSection",
    "CodeSmell",
    "QualitySection",
    "UseCase",
    "LensSection",
    "RefactoringSection",
    "RepoDashboardModel",
    "validate_dashboard_model",
]
