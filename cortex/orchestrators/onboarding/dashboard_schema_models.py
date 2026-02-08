"""
CORTEX Repository Dashboard Schema Validation Models
Pydantic-based models for all 9 dashboard tabs with comprehensive validation
"""

from pydantic import BaseModel, Field, validator, root_validator
from typing import List, Dict, Optional, Any
from datetime import datetime
from enum import Enum


# ============================================================================
# ENUMERATIONS
# ============================================================================

class ProgrammingLanguage(str, Enum):
    """Supported programming languages"""
    C_SHARP = "C#"
    PYTHON = "Python"
    JAVASCRIPT = "JavaScript"
    TYPESCRIPT = "TypeScript"
    JAVA = "Java"
    GO = "Go"
    RUST = "Rust"
    PHP = "PHP"
    RUBY = "Ruby"
    OTHER = "Other"


class Priority(str, Enum):
    """Priority levels"""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Severity(str, Enum):
    """Severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class Persona(str, Enum):
    """Dashboard audience personas"""
    EXECUTIVE = "Executive"
    PRODUCT_OWNER = "Product Owner"
    DEV_MANAGER = "Dev Manager"
    ENGINEER = "Engineer"
    LEADER = "Leader"


class Complexity(str, Enum):
    """Complexity levels"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Maturity(str, Enum):
    """Capability maturity levels"""
    EMERGING = "emerging"
    STABLE = "stable"
    MATURE = "mature"


class ComplianceStatus(str, Enum):
    """Compliance status"""
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"


class SecurityStatus(str, Enum):
    """Security status"""
    SAFE = "safe"
    VULNERABLE = "vulnerable"
    CRITICAL = "critical"


class IntegrationType(str, Enum):
    """Integration types"""
    API = "API"
    DATABASE = "Database"
    FILE = "File"
    MESSAGE = "Message"


# ============================================================================
# CORE MODELS
# ============================================================================

class RepositoryMetadata(BaseModel):
    """Repository metadata and basic information"""
    
    name: str = Field(..., min_length=1, max_length=255, description="Repository name")
    path: str = Field(..., min_length=1, description="Repository path")
    description: Optional[str] = None
    primary_language: ProgrammingLanguage
    total_files: int = Field(..., ge=0, description="Total number of files")
    total_lines: int = Field(..., ge=0, description="Total lines of code")
    contributors: int = Field(..., ge=1, description="Number of contributors")
    last_updated: datetime = Field(..., description="Last update timestamp")
    repo_age_days: int = Field(..., ge=0, description="Repository age in days")
    
    @validator('last_updated', pre=True)
    def parse_datetime(cls, v):
        if isinstance(v, str):
            return datetime.fromisoformat(v.replace('Z', '+00:00'))
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "KSESSIONS",
                "path": "D:\\PROJECTS\\KSESSIONS",
                "primary_language": "C#",
                "total_files": 26434,
                "total_lines": 3658465,
                "contributors": 30,
                "last_updated": "2026-02-08T15:30:00Z",
                "repo_age_days": 635
            }
        }


class AudienceCard(BaseModel):
    """Audience persona card"""
    
    persona: Persona
    icon: str = Field(..., description="Emoji or icon")
    description: str = Field(..., description="Audience description")


class OverviewTab(BaseModel):
    """Overview tab (📊) - Executive dashboard"""
    
    health_score: float = Field(..., ge=0, le=100, description="Overall health (0-100)")
    code_quality: float = Field(..., ge=0, le=10, description="Code quality score")
    test_coverage: float = Field(..., ge=0, le=100, description="Test coverage %")
    maintainability_index: float = Field(..., ge=0, le=100, description="Maintainability index")
    technical_debt_hours: int = Field(..., ge=0, description="Technical debt hours")
    languages: Dict[str, int] = Field(..., description="Lines of code by language")
    audiences: Optional[List[AudienceCard]] = None


class Layer(BaseModel):
    """Architectural layer"""
    
    name: str
    description: str
    modules: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)


class Module(BaseModel):
    """Code module"""
    
    lines_of_code: int = Field(..., ge=0)
    files: int = Field(..., ge=0)
    complexity: float = Field(..., ge=0)
    sub_modules: List[str] = Field(default_factory=list)
    dependencies: List[str] = Field(default_factory=list)


class DesignPattern(BaseModel):
    """Detected design pattern"""
    
    name: str
    description: str
    location: str
    usage_count: int = Field(..., ge=1)


class ArchitectureTab(BaseModel):
    """Architecture tab (🏗️) - System design"""
    
    layers: List[Layer] = Field(default_factory=list)
    modules: Dict[str, Module] = Field(default_factory=dict)
    design_patterns: List[DesignPattern] = Field(default_factory=list)


class TrendPoint(BaseModel):
    """Time-series data point"""
    
    date: str = Field(..., description="Date (YYYY-MM-DD)")
    value: float = Field(...)
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, '%Y-%m-%d')
        except ValueError:
            raise ValueError('Invalid date format (use YYYY-MM-DD)')
        return v


class ComplexityTrendPoint(TrendPoint):
    """Complexity trend data point"""
    
    avg_complexity: float = Field(...)


class Hotspot(BaseModel):
    """Code complexity hotspot"""
    
    file: str
    complexity: float = Field(..., ge=0)
    issues: int = Field(..., ge=0)
    priority: Priority


class QualityTab(BaseModel):
    """Quality tab (✅) - Code health metrics"""
    
    code_quality_score: float = Field(..., ge=0, le=10)
    maintainability_index: float = Field(..., ge=0, le=100)
    code_smells: int = Field(..., ge=0)
    duplication_percentage: float = Field(..., ge=0, le=100)
    technical_debt_hours: int = Field(..., ge=0)
    test_coverage: float = Field(..., ge=0, le=100)
    coverage_trend: List[TrendPoint] = Field(default_factory=list)
    complexity_trend: List[ComplexityTrendPoint] = Field(default_factory=list)
    complexity_by_module: Dict[str, float] = Field(default_factory=dict)
    hotspots: List[Hotspot] = Field(default_factory=list)


class OWASPFinding(BaseModel):
    """OWASP Top 10 finding"""
    
    category: str
    severity: Severity
    count: int = Field(..., ge=0)
    items: List[Dict[str, str]] = Field(default_factory=list)


class SecretsScan(BaseModel):
    """Secrets scan result"""
    
    status: str = Field(..., description="clean or violations_found")
    secrets_found: int = Field(..., ge=0)
    last_scan: Optional[datetime] = None


class CVE(BaseModel):
    """CVE (Common Vulnerabilities and Exposures)"""
    
    id: str
    severity: str
    affected_package: str
    fix_available: bool


class VulnerabilitiesTab(BaseModel):
    """Vulnerabilities tab (🛡️) - Security findings"""
    
    critical: int = Field(..., ge=0)
    high: int = Field(..., ge=0)
    medium: int = Field(..., ge=0)
    low: int = Field(..., ge=0)
    owasp_findings: List[OWASPFinding] = Field(default_factory=list)
    secrets_scan: Optional[SecretsScan] = None
    cves: List[CVE] = Field(default_factory=list)


class ComplianceFramework(BaseModel):
    """Compliance framework status"""
    
    name: str
    status: ComplianceStatus
    score: float = Field(..., ge=0, le=100)
    issues: int = Field(..., ge=0)


class Authentication(BaseModel):
    """Authentication configuration"""
    
    implemented: str
    standards: List[str] = Field(default_factory=list)
    multi_factor: bool = False


class Encryption(BaseModel):
    """Encryption status"""
    
    at_rest: bool
    in_transit: bool
    key_management: Optional[str] = None


class DataProtection(BaseModel):
    """Data protection measures"""
    
    pii_detection: int = Field(..., ge=0)
    masking: bool
    retention_policy: Optional[str] = None


class SecurityTab(BaseModel):
    """Security tab (🔒) - Compliance posture"""
    
    security_score: float = Field(..., ge=0, le=10)
    security_posture: str
    frameworks: List[ComplianceFramework] = Field(default_factory=list)
    authentication: Optional[Authentication] = None
    encryption: Optional[Encryption] = None
    data_protection: Optional[DataProtection] = None


class Dependency(BaseModel):
    """Package dependency"""
    
    name: str
    version: str
    latest: str
    type: str = Field(..., description="direct or transitive")
    license: Optional[str] = None
    security_status: SecurityStatus = SecurityStatus.SAFE
    update_recommended: bool = False


class License(BaseModel):
    """License information"""
    
    name: str
    count: int = Field(..., ge=0)
    packages: List[str] = Field(default_factory=list)


class DependenciesTab(BaseModel):
    """Dependencies tab (📦) - Package management"""
    
    direct_count: int = Field(..., ge=0)
    transitive_count: int = Field(..., ge=0)
    outdated_count: int = Field(..., ge=0)
    vulnerable_count: int = Field(..., ge=0)
    packages: List[Dependency] = Field(default_factory=list)
    dependency_graph: Dict[str, List[str]] = Field(default_factory=dict)
    licenses: List[License] = Field(default_factory=list)


class TestCounts(BaseModel):
    """Test execution counts"""
    
    total: int = Field(..., ge=0)
    passing: int = Field(..., ge=0)
    failing: int = Field(..., ge=0)
    skipped: int = Field(..., ge=0)


class TestTypes(BaseModel):
    """Test type breakdown"""
    
    unit: int = Field(..., ge=0)
    integration: int = Field(..., ge=0)
    e2e: int = Field(..., ge=0)


class FailingTest(BaseModel):
    """Failing test information"""
    
    name: str
    file: str
    error: str
    priority: Priority


class TestingTab(BaseModel):
    """Testing tab (🧪) - Quality assurance"""
    
    coverage_percentage: float = Field(..., ge=0, le=100)
    coverage_trend: List[TrendPoint] = Field(default_factory=list)
    test_counts: TestCounts
    test_types: TestTypes
    failing_tests: List[FailingTest] = Field(default_factory=list)
    coverage_by_module: Dict[str, float] = Field(default_factory=dict)


class AntiPattern(BaseModel):
    """Detected anti-pattern or code smell"""
    
    name: str
    severity: Severity
    count: int = Field(..., ge=0)
    locations: List[str] = Field(default_factory=list)
    remediation: str


class RefactoringOpportunity(BaseModel):
    """Refactoring opportunity"""
    
    type: str
    file: str
    priority: Priority
    effort_hours: float = Field(..., ge=0)
    description: str


class SOLIDPrinciples(BaseModel):
    """SOLID principles compliance scores"""
    
    single_responsibility: float = Field(..., ge=0, le=100)
    open_closed: float = Field(..., ge=0, le=100)
    liskov_substitution: float = Field(..., ge=0, le=100)
    interface_segregation: float = Field(..., ge=0, le=100)
    dependency_inversion: float = Field(..., ge=0, le=100)


class PatternsTab(BaseModel):
    """Patterns tab (🎨) - Design patterns & code smells"""
    
    design_patterns: List[DesignPattern] = Field(default_factory=list)
    anti_patterns: List[AntiPattern] = Field(default_factory=list)
    refactoring_opportunities: List[RefactoringOpportunity] = Field(default_factory=list)
    solid_principles: Optional[SOLIDPrinciples] = None


class BusinessCapability(BaseModel):
    """Business capability (LLM-generated)"""
    
    id: str
    business_capability: str
    technical_name: str
    description: str
    business_value: str
    actors: List[str] = Field(default_factory=list)
    systems: List[str] = Field(default_factory=list)
    complexity: Complexity
    maturity: Maturity
    modernization_score: float = Field(..., ge=0, le=100)


class BusinessFlow(BaseModel):
    """Business flow/workflow"""
    
    name: str
    description: str
    steps: List[str] = Field(default_factory=list)
    primary_actor: str
    preconditions: List[str] = Field(default_factory=list)
    success_criteria: List[str] = Field(default_factory=list)


class Integration(BaseModel):
    """External system integration"""
    
    system: str
    type: IntegrationType
    description: str


class UseCasesTab(BaseModel):
    """Use Cases tab (📋) - Business capabilities"""
    
    detected_capabilities: List[BusinessCapability] = Field(default_factory=list)
    business_flows: List[BusinessFlow] = Field(default_factory=list)
    integrations: List[Integration] = Field(default_factory=list)
    stakeholder_mapping: Dict[str, List[str]] = Field(default_factory=dict)


# ============================================================================
# MAIN DASHBOARD SCHEMA
# ============================================================================

class RepositoryDashboardSchema(BaseModel):
    """Complete CORTEX Repository Dashboard Schema - All 9 Tabs"""
    
    metadata: RepositoryMetadata
    overview: OverviewTab
    architecture: ArchitectureTab
    quality: QualityTab
    vulnerabilities: VulnerabilitiesTab
    security: SecurityTab
    dependencies: DependenciesTab
    testing: TestingTab
    patterns: PatternsTab
    use_cases: UseCasesTab
    
    @root_validator(skip_on_failure=True)
    def validate_schema_completeness(cls, values):
        """Validate schema is complete"""
        required_fields = [
            'metadata', 'overview', 'architecture', 'quality',
            'vulnerabilities', 'security', 'dependencies', 'testing',
            'patterns', 'use_cases'
        ]
        for field in required_fields:
            if field not in values or values[field] is None:
                raise ValueError(f"Required field missing: {field}")
        return values
    
    class Config:
        json_schema_extra = {
            "title": "Repository Dashboard Schema",
            "description": "Complete JSON schema for CORTEX Repository Dashboard"
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def validate_dashboard_data(data: Dict[str, Any]) -> RepositoryDashboardSchema:
    """
    Validate dashboard data against schema
    
    Args:
        data: Dictionary containing dashboard data
        
    Returns:
        RepositoryDashboardSchema instance if valid
        
    Raises:
        ValidationError: If data is invalid
    """
    return RepositoryDashboardSchema(**data)


def load_and_validate_json_file(filepath: str) -> RepositoryDashboardSchema:
    """
    Load and validate dashboard JSON file
    
    Args:
        filepath: Path to JSON file
        
    Returns:
        RepositoryDashboardSchema instance
    """
    import json
    
    with open(filepath, 'r') as f:
        data = json.load(f)
    
    return validate_dashboard_data(data)
