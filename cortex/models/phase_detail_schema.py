"""
Phase Detail Schema - Pydantic Models for Comprehensive Phase Detail Pages

Data models for phase detail pages with LLM-generated content, diagrams, and narrative.
Authority: PHASE-STORY-SYSTEM-COMPREHENSIVE.yaml (ENH-032)
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class PhaseStatus(str, Enum):
    """Phase lifecycle status"""
    ACTIVE = "ACTIVE"
    COMPLETED = "COMPLETED"
    PLANNED = "PLANNED"


class ImpactLevel(str, Enum):
    """Impact measurement levels"""
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class MermaidDiagram(BaseModel):
    """Mermaid diagram specification"""
    type: str = Field(..., description="Diagram type: architecture, workflow, data_flow, dependency")
    title: str = Field(..., description="Diagram title for display")
    mermaid_code: str = Field(..., description="Mermaid.js diagram code")
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "architecture",
                "title": "Event Bus Architecture",
                "mermaid_code": "graph TD\nA[Publisher] --> B[EventBus]\nB --> C[Subscriber]"
            }
        }


class Feature(BaseModel):
    """Phase feature specification"""
    name: str = Field(..., description="Feature name")
    description: str = Field(..., description="Feature description")
    status: str = Field(..., description="Implementation status")
    test_coverage: float = Field(..., ge=0.0, le=1.0, description="Test coverage ratio")


class CodeFile(BaseModel):
    """Code file metadata"""
    path: str = Field(..., description="File path relative to repo root")
    lines_of_code: int = Field(..., ge=0, description="Lines of code (LOC)")
    purpose: str = Field(..., description="File purpose/responsibility")
    language: str = Field(..., description="Programming language")
    test_file: Optional[str] = Field(None, description="Corresponding test file path")
    complexity_score: Optional[float] = Field(None, description="Cyclomatic complexity score")


class ArchitectureSection(BaseModel):
    """Architecture section with diagrams"""
    overview: str = Field(..., description="LLM-generated architecture overview")
    diagrams: List[MermaidDiagram] = Field(default_factory=list, description="Architecture diagrams")
    components: List[str] = Field(default_factory=list, description="Key components")
    design_patterns: Optional[List[str]] = Field(None, description="Design patterns applied")
    
    class Config:
        json_schema_extra = {
            "example": {
                "overview": "Event-driven architecture foundation",
                "diagrams": [],
                "components": ["OrchestratorEventBus", "OrchestratorEvent"]
            }
        }


class ImplementationSection(BaseModel):
    """Implementation details section"""
    files: List[CodeFile] = Field(..., description="Implementation files")
    total_loc: int = Field(..., ge=0, description="Total lines of code")
    tier: int = Field(..., ge=1, le=3, description="Architecture tier")
    priority: int = Field(..., ge=1, description="Implementation priority")
    dependencies: Optional[List[str]] = Field(None, description="External dependencies")


class TestingSection(BaseModel):
    """Testing section with metrics"""
    test_count: int = Field(..., ge=0, description="Number of tests")
    test_pass_rate: float = Field(..., ge=0.0, le=1.0, description="Test pass rate")
    coverage: float = Field(..., ge=0.0, le=1.0, description="Code coverage ratio")
    test_file: str = Field(..., description="Test file path")
    test_scenarios: Optional[List[str]] = Field(None, description="Test scenario descriptions")


class ComplianceRule(BaseModel):
    """Governance compliance rule"""
    rule: str = Field(..., description="CORE rule identifier (e.g., CORE-008)")
    description: str = Field(..., description="Rule description")
    status: str = Field(..., description="Compliance status: COMPLIANT, VIOLATION, N/A")


class ImpactMetrics(BaseModel):
    """Phase impact metrics"""
    extensibility: ImpactLevel = Field(..., description="Extensibility impact")
    scalability: ImpactLevel = Field(..., description="Scalability impact")
    maintainability: ImpactLevel = Field(..., description="Maintainability impact")
    description: Optional[str] = Field(None, description="Impact narrative")


class StoryContext(BaseModel):
    """Phase narrative and story linking"""
    previous_phase: Optional[str] = Field(None, description="Previous phase ID")
    next_phase: Optional[str] = Field(None, description="Next phase ID")
    narrative: str = Field(..., description="LLM-generated phase narrative")
    related_enhancements: Optional[List[str]] = Field(None, description="Related enhancement IDs")
    theme: Optional[str] = Field(None, description="Phase theme or arc")


class TechnicalDecision(BaseModel):
    """Technical decision documentation"""
    title: str = Field(..., description="Decision title")
    chosen: str = Field(..., description="Chosen approach")
    rejected: List[str] = Field(..., description="Rejected alternatives")
    rationale: str = Field(..., description="Decision rationale")
    tradeoffs: str = Field(..., description="Tradeoffs analysis")
    date: Optional[str] = Field(None, description="Decision date")


class Lesson(BaseModel):
    """Lesson learned documentation"""
    title: str = Field(..., description="Lesson title")
    description: str = Field(..., description="Lesson description")
    category: str = Field(..., description="Category: PERFORMANCE, ARCHITECTURE, TESTING, etc.")
    recommendation: str = Field(..., description="Recommendation for future phases")


class PhaseDetail(BaseModel):
    """Complete phase detail model for comprehensive detail pages"""
    
    # Core metadata
    phase_id: str = Field(..., description="Phase identifier (e.g., PHASE-01)")
    title: str = Field(..., description="Phase title")
    status: PhaseStatus = Field(..., description="Phase status")
    completion_date: Optional[str] = Field(None, description="Completion date (YYYY-MM-DD)")
    
    # LLM-generated content sections
    overview: Optional[str] = Field(None, description="LLM-generated phase overview")
    objectives: Optional[List[str]] = Field(None, description="Phase objectives")
    key_features: Optional[List[Feature]] = Field(None, description="Key features delivered")
    
    # Architecture section with diagrams
    architecture: Optional[ArchitectureSection] = Field(None, description="Architecture details")
    
    # Implementation details
    implementation_details: Optional[ImplementationSection] = Field(None, description="Implementation section")
    
    # Testing section
    testing: Optional[TestingSection] = Field(None, description="Testing metrics")
    
    # Governance compliance
    compliance: Optional[List[ComplianceRule]] = Field(None, description="CORE rule compliance")
    
    # Impact metrics
    impact: Optional[ImpactMetrics] = Field(None, description="Impact assessment")
    
    # Story and narrative
    story_context: Optional[StoryContext] = Field(None, description="Phase narrative and links")
    
    # Technical decisions
    technical_decisions: Optional[List[TechnicalDecision]] = Field(None, description="Key decisions made")
    
    # Lessons learned
    lessons_learned: Optional[List[Lesson]] = Field(None, description="Lessons from this phase")
    
    # Additional metadata
    git_tag: Optional[str] = Field(None, description="Git tag for phase completion")
    author: Optional[str] = Field(None, description="Phase author")
    created_date: Optional[str] = Field(None, description="Phase creation date")
    
    class Config:
        json_schema_extra = {
            "example": {
                "phase_id": "PHASE-01",
                "title": "Orchestrator Event Bus Infrastructure",
                "status": "COMPLETED",
                "completion_date": "2026-02-04",
                "overview": "Event-driven communication backbone enabling decoupled orchestrator communication",
                "objectives": [
                    "Enable event-driven orchestrator communication",
                    "Remove direct orchestrator dependencies"
                ]
            }
        }
    
    def to_html_context(self) -> Dict[str, Any]:
        """Convert to HTML template context"""
        return {
            "phase_id": self.phase_id,
            "title": self.title,
            "status": self.status.value,
            "completion_date": self.completion_date,
            "overview": self.overview,
            "objectives": self.objectives or [],
            "features": [f.model_dump() for f in self.key_features] if self.key_features else [],
            "architecture": self.architecture.model_dump() if self.architecture else None,
            "implementation": self.implementation_details.model_dump() if self.implementation_details else None,
            "testing": self.testing.model_dump() if self.testing else None,
            "compliance": [c.model_dump() for c in self.compliance] if self.compliance else [],
            "impact": self.impact.model_dump() if self.impact else None,
            "story": self.story_context.model_dump() if self.story_context else None,
            "decisions": [d.model_dump() for d in self.technical_decisions] if self.technical_decisions else [],
            "lessons": [l.model_dump() for l in self.lessons_learned] if self.lessons_learned else []
        }
    
    def get_diagram_count(self) -> int:
        """Get total number of diagrams"""
        if not self.architecture or not self.architecture.diagrams:
            return 0
        return len(self.architecture.diagrams)
    
    def get_test_coverage_percentage(self) -> int:
        """Get test coverage as percentage"""
        if not self.testing:
            return 0
        return int(self.testing.coverage * 100)
    
    def has_complete_documentation(self) -> bool:
        """Check if phase has complete documentation"""
        required_sections = [
            self.overview,
            self.objectives,
            self.architecture,
            self.implementation_details,
            self.testing
        ]
        return all(section is not None for section in required_sections)
    
    def get_completion_percentage(self) -> int:
        """Calculate documentation completion percentage"""
        sections = [
            self.overview,
            self.objectives,
            self.key_features,
            self.architecture,
            self.implementation_details,
            self.testing,
            self.compliance,
            self.impact,
            self.story_context,
            self.technical_decisions,
            self.lessons_learned
        ]
        completed = sum(1 for section in sections if section is not None)
        return int((completed / len(sections)) * 100)


# Export all models
__all__ = [
    "PhaseStatus",
    "ImpactLevel",
    "MermaidDiagram",
    "Feature",
    "CodeFile",
    "ArchitectureSection",
    "ImplementationSection",
    "TestingSection",
    "ComplianceRule",
    "ImpactMetrics",
    "StoryContext",
    "TechnicalDecision",
    "Lesson",
    "PhaseDetail"
]
