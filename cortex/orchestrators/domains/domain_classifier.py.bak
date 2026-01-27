"""
Domain Classifier - Orchestrator Domain Classification System

AC-AR-016-01: Define 5 core domains and classify orchestrators

Classifies orchestrators into 5 core domains:
1. Planning: Manage plans, phases, roadmaps
2. Analysis: Discover, analyze, inspect
3. Integration: Connect systems, APIs, external tools
4. Validation: Validate, verify, test, review
5. Execution: Run, execute, deploy, cleanup

Each classification includes:
- Domain assignment
- Trait assignments
- Rationale for classification
- Orchestrator metadata

Author: Asif Hussain
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class DomainMetadata:
    """Metadata for a domain"""
    name: str
    description: str
    primary_responsibility: str
    example_activities: List[str]


@dataclass
class OrchestratorClassification:
    """Classification of an orchestrator into domain(s)"""
    name: str
    domain: str
    traits: List[str]
    rationale: str
    confidence: float = 1.0
    secondary_traits: Optional[List[str]] = None


class DomainClassifier:
    """
    Singleton classifier for orchestrator domain classification.
    
    Provides:
    - Domain definitions with clear boundaries
    - Classification of 20+ discovered orchestrators
    - Trait assignment for each orchestrator
    - Export/import of classifications
    """
    
    _instance: Optional['DomainClassifier'] = None
    
    # Domain definitions
    DOMAINS = {
        "planning": DomainMetadata(
            name="Planning",
            description="Manage implementation plans, phases, roadmaps, and project structure",
            primary_responsibility="Plan management",
            example_activities=[
                "Phase scheduling",
                "Roadmap management",
                "Project structure",
                "Checkpoint management",
                "Maintenance scheduling",
            ],
        ),
        "analysis": DomainMetadata(
            name="Analysis",
            description="Discover, analyze, inspect code and systems for insights",
            primary_responsibility="System analysis",
            example_activities=[
                "Codebase discovery",
                "Dependency analysis",
                "Architectural review",
                "Intelligence gathering",
                "AST parsing",
            ],
        ),
        "integration": DomainMetadata(
            name="Integration",
            description="Connect external systems, APIs, and tools",
            primary_responsibility="System integration",
            example_activities=[
                "ADO integration",
                "CI/CD pipeline management",
                "API integration",
                "System connectivity",
                "Data synchronization",
            ],
        ),
        "validation": DomainMetadata(
            name="Validation",
            description="Validate state, verify conditions, test, and review",
            primary_responsibility="Quality assurance",
            example_activities=[
                "System integrity checking",
                "Pre-flight validation",
                "TDD workflow",
                "Test coverage tracking",
                "Health validation",
            ],
        ),
        "execution": DomainMetadata(
            name="Execution",
            description="Run workflows, execute tasks, deploy, and cleanup",
            primary_responsibility="Task execution",
            example_activities=[
                "Workflow execution",
                "Autonomous execution",
                "Code sanitization",
                "Deep cleanup",
                "Rollback management",
            ],
        ),
    }
    
    # Orchestrator to domain mapping
    ORCHESTRATOR_CLASSIFICATIONS = {
        "Planning Orchestrator": ("planning", ["ComposableOrchestrator"], "Manages implementation plans and phases"),
        "Maintenance Orchestrator": ("planning", ["ComposableOrchestrator"], "System health and routine maintenance activities"),
        "Checkpoint Orchestrator": ("planning", ["ComposableOrchestrator"], "Git checkpoint and recovery point management"),
        "Documentation Orchestrator": ("planning", ["ComposableOrchestrator"], "Auto-generates and maintains comprehensive documentation"),
        
        "Discovery Orchestrator": ("analysis", ["AnalyticalOrchestrator"], "Codebase discovery and dependency analysis"),
        "Intelligence Orchestrator": ("analysis", ["AnalyticalOrchestrator"], "AI-driven insights and intelligence gathering"),
        "Architectural Review Orchestrator": ("analysis", ["AnalyticalOrchestrator"], "Architecture validation and review analysis"),
        
        "ADO Operations Orchestrator": ("integration", ["IntegrativeOrchestrator"], "Azure DevOps system integration and coordination"),
        "CI/CD Orchestrator": ("integration", ["IntegrativeOrchestrator"], "Pipeline and deployment automation integration"),
        "Upgrade Orchestrator": ("integration", ["IntegrativeOrchestrator"], "Version migration and system upgrades"),
        
        "System Integrity Orchestrator": ("validation", ["ValidatingOrchestrator"], "Health validation and integrity verification"),
        "Pre-Flight Orchestrator": ("validation", ["ValidatingOrchestrator"], "Pre-execution validation and safety checks"),
        "TDD Orchestrator": ("validation", ["ValidatingOrchestrator"], "Test-driven development workflow validation"),
        "Refinement Orchestrator": ("validation", ["ValidatingOrchestrator"], "Code improvement and refinement cycle management"),
        
        "Execution Orchestrator": ("execution", ["ExecutiveOrchestrator"], "Run autonomous workflows and task execution"),
        "Vacuum Orchestrator": ("execution", ["ExecutiveOrchestrator"], "Deep cleanup and consolidation activities"),
        "Sanitization Orchestrator": ("execution", ["ExecutiveOrchestrator"], "Code cleanup and security scanning execution"),
        "Housekeeping Orchestrator": ("execution", ["ExecutiveOrchestrator"], "Routine maintenance task execution and cleanup"),
        "Rollback Orchestrator": ("execution", ["ExecutiveOrchestrator"], "Safe state recovery and rollback execution"),
    }
    
    def __new__(cls) -> 'DomainClassifier':
        """Singleton pattern"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize classifier"""
        if self._initialized:
            return
        
        self._classifications_cache: Optional[List[OrchestratorClassification]] = None
        self._initialized = True
    
    def get_all_domains(self) -> List[str]:
        """
        Get all 5 core domains.
        
        Returns:
            List of domain names
        """
        return list(self.DOMAINS.keys())
    
    def get_domain_description(self, domain: str) -> str:
        """
        Get description for a domain.
        
        Args:
            domain: Domain name
        
        Returns:
            Domain description
        """
        metadata = self.DOMAINS.get(domain)
        if not metadata:
            raise ValueError(f"Unknown domain: {domain}")
        return metadata.description
    
    def get_orchestrators_by_domain(self, domain: str) -> List[str]:
        """
        Get orchestrators for a specific domain.
        
        Args:
            domain: Domain name
        
        Returns:
            List of orchestrator names
        """
        if domain not in self.DOMAINS:
            raise ValueError(f"Unknown domain: {domain}")
        
        return [
            name for name, (d, _, _) in self.ORCHESTRATOR_CLASSIFICATIONS.items()
            if d == domain
        ]
    
    def classify_all_orchestrators(self) -> List[OrchestratorClassification]:
        """
        Get all orchestrator classifications.
        
        Returns:
            List of OrchestratorClassification objects
        """
        if self._classifications_cache is not None:
            return self._classifications_cache
        
        classifications: List[OrchestratorClassification] = []
        
        for name, (domain, traits, rationale) in self.ORCHESTRATOR_CLASSIFICATIONS.items():
            classification = OrchestratorClassification(
                name=name,
                domain=domain,
                traits=traits,
                rationale=rationale,
            )
            classifications.append(classification)
        
        self._classifications_cache = classifications
        return classifications
    
    def get_classification(self, orchestrator_name: str) -> Optional[OrchestratorClassification]:
        """
        Get classification for a specific orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
        
        Returns:
            OrchestratorClassification or None if not found
        """
        for classification in self.classify_all_orchestrators():
            if classification.name == orchestrator_name:
                return classification
        return None
    
    def export_classifications(self) -> Dict[str, Any]:
        """
        Export classifications in structured format.
        
        Returns:
            Dict with metadata and classifications
        """
        classifications = self.classify_all_orchestrators()
        
        return {
            "metadata": {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "total_orchestrators": len(classifications),
                "total_domains": len(self.DOMAINS),
                "domains": self.get_all_domains(),
            },
            "classifications": [
                {
                    "name": c.name,
                    "domain": c.domain,
                    "traits": c.traits,
                    "rationale": c.rationale,
                    "confidence": c.confidence,
                }
                for c in classifications
            ],
            "domain_metadata": {
                domain: {
                    "name": meta.name,
                    "description": meta.description,
                    "primary_responsibility": meta.primary_responsibility,
                    "example_activities": meta.example_activities,
                    "orchestrators": self.get_orchestrators_by_domain(domain),
                }
                for domain, meta in self.DOMAINS.items()
            },
        }
    
    def get_domain_summary(self) -> Dict[str, Dict[str, Any]]:
        """
        Get summary statistics for each domain.
        
        Returns:
            Dict mapping domain names to summary stats
        """
        classifications = self.classify_all_orchestrators()
        summary: Dict[str, Dict[str, Any]] = {}
        
        for domain in self.get_all_domains():
            domain_orchs = [c for c in classifications if c.domain == domain]
            all_traits: List[str] = []
            for c in domain_orchs:
                all_traits.extend(c.traits)
            
            summary[domain] = {
                "count": len(domain_orchs),
                "orchestrators": [c.name for c in domain_orchs],
                "traits": list(set(all_traits)),
                "description": self.DOMAINS[domain].description,
            }
        
        return summary
