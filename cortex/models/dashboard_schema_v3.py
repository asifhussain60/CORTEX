"""
PHASE-21 Phase-0: JSON Schema v3.0 Pydantic Models
Authority: phase-21-json-first-rewrite.yaml
Status: GREEN phase (implementation)

Dashboard schema v3.0 with Pydantic models for type-safe JSON serialization.
Single source of truth for all dashboard JSON files.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


# ============================================================================
# METRICS MODELS
# ============================================================================

class CodeMetrics(BaseModel):
    """Code quality and complexity metrics"""
    lines_of_code: Optional[int] = Field(None, ge=0)
    cyclomatic_complexity: Optional[float] = Field(None, ge=0)
    maintainability_index: Optional[float] = Field(None, ge=0, le=100)
    test_coverage_percent: Optional[float] = Field(None, ge=0, le=100)
    duplication_percent: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        title = "Code Metrics"
        description = "Code quality, complexity, and coverage metrics"


class DependencyMetrics(BaseModel):
    """Dependency health and version status"""
    total_dependencies: Optional[int] = Field(None, ge=0)
    up_to_date: Optional[int] = Field(None, ge=0)
    outdated: Optional[int] = Field(None, ge=0)
    vulnerable: Optional[int] = Field(None, ge=0)
    
    class Config:
        title = "Dependency Metrics"
        description = "Dependency version and vulnerability tracking"


class SecurityMetrics(BaseModel):
    """Security vulnerability and scanning metrics"""
    critical_vulnerabilities: Optional[int] = Field(None, ge=0)
    high_vulnerabilities: Optional[int] = Field(None, ge=0)
    medium_vulnerabilities: Optional[int] = Field(None, ge=0)
    low_vulnerabilities: Optional[int] = Field(None, ge=0)
    security_score: Optional[float] = Field(None, ge=0, le=100)
    
    class Config:
        title = "Security Metrics"
        description = "Vulnerability counts and security scoring"


class PerformanceMetrics(BaseModel):
    """Performance and benchmarking metrics"""
    build_time_seconds: Optional[float] = Field(None, ge=0)
    test_execution_time_seconds: Optional[float] = Field(None, ge=0)
    deployment_frequency_days: Optional[float] = Field(None, ge=0)
    mean_time_to_recovery_hours: Optional[float] = Field(None, ge=0)
    
    class Config:
        title = "Performance Metrics"
        description = "Build, test, and deployment performance indicators"


# ============================================================================
# REPOSITORY MODEL
# ============================================================================

class Repository(BaseModel):
    """Repository metadata and identity"""
    slug: str = Field(..., description="URL-safe repo identifier (kebab-case)")
    display_name: str = Field(..., description="Human-readable repository name")
    description: Optional[str] = Field(None, description="One-line repo description")
    primary_language: Optional[str] = Field(None, description="Main programming language")
    tech_stack: Optional[List[str]] = Field(None, description="Technologies used")
    total_loc: Optional[int] = Field(None, ge=0, description="Total lines of code")
    file_count: Optional[int] = Field(None, ge=0, description="Total file count")
    health_score: Optional[float] = Field(None, ge=0, le=100, description="0-100 health score")
    last_analyzed_at: Optional[datetime] = Field(None, description="Last analysis timestamp")
    
    @validator('slug')
    def slug_must_be_kebab_case(cls, v):
        """Enforce kebab-case for slug"""
        if not all(c.isalnum() or c == '-' for c in v):
            raise ValueError("slug must be alphanumeric with hyphens only")
        if v.startswith('-') or v.endswith('-'):
            raise ValueError("slug cannot start or end with hyphen")
        return v.lower()
    
    class Config:
        title = "Repository"
        description = "Repository metadata and core information"


# ============================================================================
# OVERVIEW & SUMMARY MODELS
# ============================================================================

class Overview(BaseModel):
    """High-level repository overview"""
    summary: str = Field(..., description="Technical summary of the repository")
    business_summary: Optional[str] = Field(None, description="Business-friendly summary")
    key_features: Optional[List[str]] = Field(None, description="Top 3-5 features")
    critical_issues: Optional[List[str]] = Field(None, description="Active critical issues")
    upcoming_maintenance: Optional[List[str]] = Field(None, description="Scheduled maintenance")
    
    class Config:
        title = "Overview"
        description = "Repository summary and key information"


# ============================================================================
# LENS & ANALYSIS MODELS
# ============================================================================

class LensAnalysis(BaseModel):
    """LENS-powered code intelligence insights"""
    duplication_score: Optional[float] = Field(None, ge=0, le=100)
    pattern_violations: Optional[List[str]] = Field(None)
    anti_patterns_detected: Optional[List[Dict[str, Any]]] = Field(None)
    recommendations: Optional[List[str]] = Field(None)
    
    class Config:
        title = "LENS Analysis"
        description = "Code intelligence and pattern analysis"


# ============================================================================
# MAIN DASHBOARD MODEL
# ============================================================================

class Dashboard(BaseModel):
    """
    Complete dashboard JSON schema v3.0
    Single source of truth for all dashboard.json files
    """
    schema_version: str = Field("3.0", description="Schema version (3.0)")
    repo: Repository = Field(..., description="Repository metadata")
    overview: Overview = Field(..., description="Repository overview")
    
    # Metrics sections
    metrics: Optional[Dict[str, Any]] = Field(None, description="Code metrics")
    dependencies: Optional[Dict[str, Any]] = Field(None, description="Dependency info")
    security: Optional[Dict[str, Any]] = Field(None, description="Security metrics")
    performance: Optional[Dict[str, Any]] = Field(None, description="Performance metrics")
    
    # Analysis sections
    lens: Optional[LensAnalysis] = Field(None, description="LENS analysis")
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = Field(None, description="Generation metadata")
    
    @validator('schema_version')
    def schema_version_must_be_v3(cls, v):
        """Enforce schema version 3.0"""
        if v != "3.0":
            raise ValueError("schema_version must be '3.0'")
        return v
    
    class Config:
        title = "Dashboard"
        description = "Complete repository intelligence dashboard (schema v3.0)"
        example = {
            "schema_version": "3.0",
            "repo": {
                "slug": "cortex",
                "display_name": "CORTEX",
                "description": "Enterprise Code Intelligence Platform",
                "primary_language": "Python",
                "health_score": 85
            },
            "overview": {
                "summary": "High-performance code intelligence system",
                "business_summary": "AI-powered repository analysis for enterprises",
                "key_features": ["Code Analysis", "Metrics", "Security Scanning"]
            }
        }


# ============================================================================
# REGISTRY MODEL (for registry.json)
# ============================================================================

class RepositoryTile(BaseModel):
    """Individual repository entry in registry"""
    slug: str
    display_name: str
    description: Optional[str] = None
    health_score: Optional[float] = None
    icon_emoji: Optional[str] = None
    dashboard_path: str = Field(..., description="Relative path to dashboard.json")


class Registry(BaseModel):
    """Repository registry (index of all dashboards)"""
    schema_version: str = Field("3.0")
    repositories: List[RepositoryTile] = Field(default_factory=list)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    class Config:
        title = "Repository Registry"
        description = "Index of all repository dashboards"


# ============================================================================
# METADATA MODEL
# ============================================================================

class GenerationMetadata(BaseModel):
    """Dashboard generation metadata"""
    generated_at: datetime = Field(default_factory=datetime.now)
    generator_version: str = Field(..., description="CORTEX version")
    generator_name: str = Field(default="cortex-v3.0")
    analysis_duration_seconds: Optional[float] = Field(None, ge=0)
    adapter_type: str = Field(default="json", description="Data adapter used")
    
    class Config:
        title = "Generation Metadata"
        description = "Dashboard generation tracking and metadata"


# ============================================================================
# EXPORT CONVENIENCE FUNCTIONS
# ============================================================================

def create_empty_dashboard(slug: str, display_name: str) -> Dashboard:
    """
    Create minimal dashboard with required fields only
    
    Args:
        slug: Repository slug (kebab-case)
        display_name: Human-readable repo name
    
    Returns:
        Dashboard with required fields populated
    """
    return Dashboard(
        schema_version="3.0",
        repo=Repository(slug=slug, display_name=display_name),
        overview=Overview(summary=f"Dashboard for {display_name}")
    )


def create_full_dashboard(
    slug: str,
    display_name: str,
    description: str = "",
    health_score: float = 50.0,
    primary_language: str = "",
    tech_stack: List[str] = None,
    total_loc: int = 0,
    file_count: int = 0
) -> Dashboard:
    """
    Create fully-populated dashboard with common fields
    
    Args:
        slug: Repository slug
        display_name: Human-readable name
        description: Repository description
        health_score: Health score (0-100)
        primary_language: Main language
        tech_stack: Technology list
        total_loc: Total lines of code
        file_count: Total file count
    
    Returns:
        Fully populated Dashboard
    """
    return Dashboard(
        schema_version="3.0",
        repo=Repository(
            slug=slug,
            display_name=display_name,
            description=description,
            primary_language=primary_language,
            tech_stack=tech_stack or [],
            total_loc=total_loc,
            file_count=file_count,
            health_score=health_score
        ),
        overview=Overview(summary=description or f"Dashboard for {display_name}"),
        metadata={
            "generated_at": datetime.now().isoformat(),
            "generator_version": "3.0",
            "generator_name": "cortex-v3.0"
        }
    )
