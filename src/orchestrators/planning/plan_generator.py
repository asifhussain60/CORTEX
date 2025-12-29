"""
CORTEX 4.0 Plan Generator - Plan Creation Logic

Purpose: Generate feature plans with complexity analysis and DoR/DoD requirements
Version: 4.0.0
Author: CORTEX Development Team
Migrated: 2025-12-19 (from legacy planning_orchestrator.py)

Key Features (Week 8 MVP):
- Plan generation from feature requirements
- Complexity analysis (LOW/MEDIUM/HIGH/CRITICAL)
- Plan type selection (skeleton/conditional/incremental)
- DoR/DoD generation
- TDD requirements integration
- Phase structure generation

Deferred to Week 9:
- Test intelligence integration (automatic test requirement detection)
- TDD intelligence integration (smart TDD enforcement)

Deferred to Week 11+:
- Threat modeling integration (security analysis)
- Architecture review integration (contextual review)
- Incremental generation with checkpoints
- Folder-based plan generation

Architecture:
- Standalone generator module
- Callable from PlanningOrchestrator
- Returns PlanData with generated plan
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import uuid

logger = logging.getLogger(__name__)


# Import domain models from planning_orchestrator
# Note: In real implementation, these would be in a shared models module
# For Week 8 MVP, we'll duplicate the minimal models needed


@dataclass
class PlanMetadata:
    """Plan metadata structure."""
    title: str
    description: str
    complexity: int  # 1-4
    plan_type: str
    plan_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8].upper())
    author: str = "CORTEX Planning System 4.0"
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    created_by: str = "CORTEX"
    status: str = "proposed"
    priority: str = "medium"
    estimated_hours: float = 8.0
    version: str = "4.0.0"
    tags: List[str] = field(default_factory=list)


@dataclass
class PlanTask:
    """Plan task structure."""
    task_id: str
    task_name: str
    estimated_hours: float
    description: Optional[str] = None
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class PlanPhase:
    """Plan phase structure."""
    phase_number: int
    phase_name: str
    estimated_hours: float
    tasks: List[PlanTask]
    acceptance_criteria: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    is_conditional: bool = False
    condition: Optional[str] = None


@dataclass
class PlanData:
    """Complete plan data structure."""
    metadata: PlanMetadata
    definition_of_ready: List[str]
    definition_of_done: List[str]
    phases: List[PlanPhase]
    tdd_requirements: Optional[Dict[str, List[str]]] = None
    risks: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class GenerationResult:
    """Result of plan generation."""
    success: bool
    plan_data: Optional[PlanData]
    complexity_analysis: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Complexity Analyzer
# ============================================================================

class ComplexityAnalyzer:
    """
    Analyze feature complexity for adaptive plan generation.
    
    Complexity Factors:
    - Security keywords (auth, encryption, compliance) → +2
    - Integration keywords (API, third-party, migration) → +1
    - Architecture keywords (microservice, distributed, scalable) → +1
    - Data keywords (database, schema, migration) → +1
    - UI keywords (dashboard, visualization, responsive) → +0.5
    
    Levels:
    - LOW (1): Simple features, < 8 hours
    - MEDIUM (2): Moderate features, 8-24 hours
    - HIGH (3): Complex features, 24-80 hours
    - CRITICAL (4): Critical features with security/compliance, > 80 hours
    """
    
    # Security-related keywords
    SECURITY_KEYWORDS = [
        "auth", "authentication", "authorization", "encrypt", "decrypt",
        "security", "compliance", "gdpr", "hipaa", "pci", "token", "jwt",
        "oauth", "saml", "sso", "password", "credential", "certificate"
    ]
    
    # Integration keywords
    INTEGRATION_KEYWORDS = [
        "api", "integration", "third-party", "external", "webhook",
        "migration", "import", "export", "sync", "etl"
    ]
    
    # Architecture keywords
    ARCHITECTURE_KEYWORDS = [
        "microservice", "distributed", "scalable", "architecture",
        "refactor", "redesign", "performance", "optimization"
    ]
    
    # Data keywords
    DATA_KEYWORDS = [
        "database", "schema", "migration", "model", "entity",
        "query", "index", "transaction", "backup", "restore"
    ]
    
    # UI keywords
    UI_KEYWORDS = [
        "dashboard", "visualization", "chart", "graph", "report",
        "ui", "ux", "responsive", "mobile", "frontend"
    ]
    
    @classmethod
    def analyze(cls, feature_requirements: str) -> Dict[str, Any]:
        """
        Analyze feature complexity.
        
        Args:
            feature_requirements: Feature description
        
        Returns:
            Dictionary with complexity analysis
        """
        text_lower = feature_requirements.lower()
        
        # Count keyword matches
        security_score = sum(1 for kw in cls.SECURITY_KEYWORDS if kw in text_lower)
        integration_score = sum(1 for kw in cls.INTEGRATION_KEYWORDS if kw in text_lower)
        architecture_score = sum(1 for kw in cls.ARCHITECTURE_KEYWORDS if kw in text_lower)
        data_score = sum(1 for kw in cls.DATA_KEYWORDS if kw in text_lower)
        ui_score = sum(1 for kw in cls.UI_KEYWORDS if kw in text_lower)
        
        # Calculate complexity score
        complexity_score = 0.0
        complexity_score += security_score * 2.0  # Security is high priority
        complexity_score += integration_score * 1.0
        complexity_score += architecture_score * 1.0
        complexity_score += data_score * 1.0
        complexity_score += ui_score * 0.5
        
        # Determine complexity level
        if complexity_score >= 6 or security_score >= 2:
            level = 4  # CRITICAL
            hours = 80
        elif complexity_score >= 3:
            level = 3  # HIGH
            hours = 40
        elif complexity_score >= 1:
            level = 2  # MEDIUM
            hours = 16
        else:
            level = 1  # LOW
            hours = 8
        
        return {
            "complexity_level": level,
            "complexity_score": complexity_score,
            "estimated_hours": hours,
            "factors": {
                "security": security_score,
                "integration": integration_score,
                "architecture": architecture_score,
                "data": data_score,
                "ui": ui_score
            },
            "recommended_plan_type": cls._get_recommended_plan_type(level)
        }
    
    @classmethod
    def _get_recommended_plan_type(cls, complexity_level: int) -> str:
        """Get recommended plan type for complexity level."""
        if complexity_level == 1:
            return "skeleton"
        elif complexity_level == 2:
            return "conditional"
        else:
            return "incremental"


# ============================================================================
# Plan Generator
# ============================================================================

class PlanGenerator:
    """
    CORTEX 4.0 Plan Generator.
    
    Generates feature plans with adaptive complexity analysis.
    
    Plan Types:
    - Skeleton: DoR/DoD only (LOW complexity)
    - Conditional: Some detailed phases (MEDIUM complexity)
    - Incremental: All phases detailed (HIGH/CRITICAL complexity)
    
    Week 8 MVP: Basic generation with complexity analysis
    Week 9: Add test intelligence, TDD intelligence
    Week 11+: Add threat modeling, architecture review, incremental checkpoints
    """
    
    def __init__(self, cortex_root: Path):
        """
        Initialize plan generator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = cortex_root
        self.complexity_analyzer = ComplexityAnalyzer()
        
        # TDD requirements (SKULL enforcement)
        self._tdd_dor_requirements = [
            "TDD Mastery workflow MUST be followed (RED→GREEN→REFACTOR)",
            "Tests MUST fail before implementation (RED phase validation)",
            "All CORTEX brain protection rules apply (SKULL enforcement)",
            "Reference: cortex-brain/brain-protection-rules.yaml for complete ruleset"
        ]
        
        self._tdd_dod_requirements = [
            "All code follows TDD workflow with git checkpoints at phase boundaries",
            "No SKULL rule violations detected (brain protection compliance verified)",
            "Test coverage meets CORTEX standards (RED→GREEN→REFACTOR documented)",
            "Git history shows test-first commits (RED phase before GREEN phase)"
        ]
        
        logger.info("✅ Plan Generator initialized")
    
    def generate(
        self,
        feature_requirements: str,
        plan_type: Optional[str] = None,
        complexity_override: Optional[int] = None
    ) -> GenerationResult:
        """
        Generate feature plan.
        
        Args:
            feature_requirements: Feature description
            plan_type: Optional plan type override (skeleton/conditional/incremental)
            complexity_override: Optional complexity override (1-4)
        
        Returns:
            GenerationResult with generated plan
        """
        try:
            # Step 1: Analyze complexity
            complexity_analysis = self.complexity_analyzer.analyze(feature_requirements)
            complexity_level = complexity_override or complexity_analysis["complexity_level"]
            estimated_hours = complexity_analysis["estimated_hours"]
            
            logger.info(f"📊 Complexity analysis: level={complexity_level}, hours={estimated_hours}")
            
            # Step 2: Determine plan type
            if not plan_type:
                plan_type = complexity_analysis["recommended_plan_type"]
            
            logger.info(f"📋 Generating {plan_type} plan")
            
            # Step 3: Generate plan based on type
            if plan_type == "skeleton":
                plan_data = self._generate_skeleton_plan(feature_requirements, complexity_level, estimated_hours)
            elif plan_type == "conditional":
                plan_data = self._generate_conditional_plan(feature_requirements, complexity_level, estimated_hours)
            else:  # incremental
                plan_data = self._generate_incremental_plan(feature_requirements, complexity_level, estimated_hours)
            
            return GenerationResult(
                success=True,
                plan_data=plan_data,
                complexity_analysis=complexity_analysis
            )
        
        except Exception as e:
            logger.error(f"Plan generation failed: {e}", exc_info=True)
            return GenerationResult(
                success=False,
                plan_data=None,
                errors=[str(e)]
            )
    
    def _generate_skeleton_plan(
        self,
        feature_requirements: str,
        complexity_level: int,
        estimated_hours: float
    ) -> PlanData:
        """Generate skeleton plan (DoR/DoD only)."""
        feature_name = self._extract_feature_name(feature_requirements)
        
        metadata = PlanMetadata(
            title=feature_name,
            description=feature_requirements[:200],
            complexity=complexity_level,
            plan_type="skeleton",
            estimated_hours=estimated_hours,
            tags=["skeleton", "low-complexity"]
        )
        
        # Basic DoR
        dor = [
            "Requirements clearly defined and approved",
            "Architecture design reviewed",
            "Test strategy defined",
            "Dependencies identified"
        ]
        
        # Basic DoD
        dod = [
            "All acceptance criteria met",
            "All tests passing (100% pass rate)",
            "Code reviewed and merged",
            "Documentation updated"
        ]
        
        # Single implementation phase
        phases = [
            PlanPhase(
                phase_number=1,
                phase_name="Implementation",
                estimated_hours=estimated_hours,
                tasks=[
                    PlanTask(
                        task_id="1.1",
                        task_name=f"Implement {feature_name}",
                        estimated_hours=estimated_hours * 0.7,
                        description="Core implementation"
                    ),
                    PlanTask(
                        task_id="1.2",
                        task_name="Write tests",
                        estimated_hours=estimated_hours * 0.3,
                        description="Unit and integration tests"
                    )
                ],
                acceptance_criteria=[
                    "Feature working as specified",
                    "Tests passing"
                ]
            )
        ]
        
        return PlanData(
            metadata=metadata,
            definition_of_ready=dor,
            definition_of_done=dod,
            phases=phases,
            tdd_requirements={
                "dor": self._tdd_dor_requirements,
                "dod": self._tdd_dod_requirements
            }
        )
    
    def _generate_conditional_plan(
        self,
        feature_requirements: str,
        complexity_level: int,
        estimated_hours: float
    ) -> PlanData:
        """Generate conditional plan (some detailed phases)."""
        feature_name = self._extract_feature_name(feature_requirements)
        
        metadata = PlanMetadata(
            title=feature_name,
            description=feature_requirements[:200],
            complexity=complexity_level,
            plan_type="conditional",
            estimated_hours=estimated_hours,
            tags=["conditional", "medium-complexity"]
        )
        
        # Enhanced DoR
        dor = [
            "Requirements clearly defined and approved",
            "Architecture design reviewed and documented",
            "Test strategy defined with coverage targets",
            "Dependencies identified and documented",
            "Data model designed (if applicable)",
            "API contracts defined (if applicable)"
        ]
        
        # Enhanced DoD
        dod = [
            "All acceptance criteria met",
            "All tests passing (100% pass rate, 85%+ coverage)",
            "Code reviewed and approved",
            "Documentation updated (README, API docs)",
            "Performance benchmarks met",
            "Security review completed (if applicable)"
        ]
        
        # Multi-phase implementation
        phases = [
            PlanPhase(
                phase_number=1,
                phase_name="Foundation",
                estimated_hours=estimated_hours * 0.3,
                tasks=[
                    PlanTask(
                        task_id="1.1",
                        task_name="Design architecture",
                        estimated_hours=estimated_hours * 0.1,
                        description="Define components and interactions"
                    ),
                    PlanTask(
                        task_id="1.2",
                        task_name="Setup data models",
                        estimated_hours=estimated_hours * 0.1,
                        description="Define entities and relationships"
                    ),
                    PlanTask(
                        task_id="1.3",
                        task_name="Create test framework",
                        estimated_hours=estimated_hours * 0.1,
                        description="Setup test infrastructure"
                    )
                ],
                acceptance_criteria=[
                    "Architecture documented",
                    "Data models defined",
                    "Test framework ready"
                ]
            ),
            PlanPhase(
                phase_number=2,
                phase_name="Implementation",
                estimated_hours=estimated_hours * 0.5,
                tasks=[
                    PlanTask(
                        task_id="2.1",
                        task_name=f"Implement {feature_name} core",
                        estimated_hours=estimated_hours * 0.3,
                        description="Core functionality"
                    ),
                    PlanTask(
                        task_id="2.2",
                        task_name="Write unit tests",
                        estimated_hours=estimated_hours * 0.2,
                        description="Test core functionality"
                    )
                ],
                acceptance_criteria=[
                    "Core functionality working",
                    "Unit tests passing"
                ]
            ),
            PlanPhase(
                phase_number=3,
                phase_name="Integration & Polish",
                estimated_hours=estimated_hours * 0.2,
                tasks=[
                    PlanTask(
                        task_id="3.1",
                        task_name="Integration testing",
                        estimated_hours=estimated_hours * 0.1,
                        description="Test end-to-end flows"
                    ),
                    PlanTask(
                        task_id="3.2",
                        task_name="Documentation",
                        estimated_hours=estimated_hours * 0.1,
                        description="Update docs"
                    )
                ],
                acceptance_criteria=[
                    "Integration tests passing",
                    "Documentation complete"
                ]
            )
        ]
        
        return PlanData(
            metadata=metadata,
            definition_of_ready=dor,
            definition_of_done=dod,
            phases=phases,
            tdd_requirements={
                "dor": self._tdd_dor_requirements,
                "dod": self._tdd_dod_requirements
            }
        )
    
    def _generate_incremental_plan(
        self,
        feature_requirements: str,
        complexity_level: int,
        estimated_hours: float
    ) -> PlanData:
        """Generate incremental plan (all phases detailed)."""
        # Week 8 MVP: Simplified incremental plan
        # Week 11: Will add threat modeling, architecture review, checkpoints
        
        feature_name = self._extract_feature_name(feature_requirements)
        
        metadata = PlanMetadata(
            title=feature_name,
            description=feature_requirements[:200],
            complexity=complexity_level,
            plan_type="incremental",
            estimated_hours=estimated_hours,
            priority="high" if complexity_level >= 3 else "medium",
            tags=["incremental", "high-complexity"]
        )
        
        # Comprehensive DoR
        dor = [
            "Requirements clearly defined, documented, and approved by stakeholders",
            "Architecture design reviewed, documented, and approved",
            "Test strategy defined with coverage targets (85%+ unit, 70%+ integration)",
            "Dependencies identified, documented, and version-locked",
            "Data model designed and reviewed (if applicable)",
            "API contracts defined and reviewed (if applicable)",
            "Security requirements defined and threat model completed",
            "Performance requirements defined with benchmarks",
            "Deployment strategy defined"
        ]
        
        # Comprehensive DoD
        dod = [
            "All acceptance criteria met and verified",
            "All tests passing (100% pass rate, 85%+ coverage)",
            "Code reviewed and approved by at least 2 reviewers",
            "Documentation updated (README, API docs, architecture docs)",
            "Performance benchmarks met and verified",
            "Security review completed and approved",
            "Deployment runbook created and reviewed",
            "Rollback plan defined and tested",
            "Monitoring and alerting configured"
        ]
        
        # Detailed multi-phase implementation
        phases = [
            PlanPhase(
                phase_number=1,
                phase_name="Discovery & Design",
                estimated_hours=estimated_hours * 0.2,
                tasks=[
                    PlanTask(
                        task_id="1.1",
                        task_name="Requirements analysis",
                        estimated_hours=estimated_hours * 0.05,
                        description="Analyze and document requirements"
                    ),
                    PlanTask(
                        task_id="1.2",
                        task_name="Architecture design",
                        estimated_hours=estimated_hours * 0.08,
                        description="Design system architecture"
                    ),
                    PlanTask(
                        task_id="1.3",
                        task_name="Data model design",
                        estimated_hours=estimated_hours * 0.04,
                        description="Design data structures"
                    ),
                    PlanTask(
                        task_id="1.4",
                        task_name="API contract definition",
                        estimated_hours=estimated_hours * 0.03,
                        description="Define API interfaces"
                    )
                ],
                acceptance_criteria=[
                    "Requirements documented",
                    "Architecture approved",
                    "Data model reviewed",
                    "API contracts defined"
                ]
            ),
            PlanPhase(
                phase_number=2,
                phase_name="Foundation",
                estimated_hours=estimated_hours * 0.25,
                tasks=[
                    PlanTask(
                        task_id="2.1",
                        task_name="Setup project structure",
                        estimated_hours=estimated_hours * 0.05,
                        description="Create folders, config files"
                    ),
                    PlanTask(
                        task_id="2.2",
                        task_name="Implement data models",
                        estimated_hours=estimated_hours * 0.08,
                        description="Create entities and relationships"
                    ),
                    PlanTask(
                        task_id="2.3",
                        task_name="Setup test framework",
                        estimated_hours=estimated_hours * 0.05,
                        description="Configure testing infrastructure"
                    ),
                    PlanTask(
                        task_id="2.4",
                        task_name="Write model tests",
                        estimated_hours=estimated_hours * 0.07,
                        description="Test data models"
                    )
                ],
                acceptance_criteria=[
                    "Project structure ready",
                    "Data models implemented",
                    "Test framework configured",
                    "Model tests passing"
                ]
            ),
            PlanPhase(
                phase_number=3,
                phase_name="Core Implementation",
                estimated_hours=estimated_hours * 0.35,
                tasks=[
                    PlanTask(
                        task_id="3.1",
                        task_name=f"Implement {feature_name} core logic",
                        estimated_hours=estimated_hours * 0.20,
                        description="Core business logic"
                    ),
                    PlanTask(
                        task_id="3.2",
                        task_name="Write unit tests",
                        estimated_hours=estimated_hours * 0.15,
                        description="Test core functionality"
                    )
                ],
                acceptance_criteria=[
                    "Core logic implemented",
                    "Unit tests passing (85%+ coverage)"
                ]
            ),
            PlanPhase(
                phase_number=4,
                phase_name="Integration & Testing",
                estimated_hours=estimated_hours * 0.15,
                tasks=[
                    PlanTask(
                        task_id="4.1",
                        task_name="Integration testing",
                        estimated_hours=estimated_hours * 0.08,
                        description="Test end-to-end flows"
                    ),
                    PlanTask(
                        task_id="4.2",
                        task_name="Performance testing",
                        estimated_hours=estimated_hours * 0.07,
                        description="Verify performance benchmarks"
                    )
                ],
                acceptance_criteria=[
                    "Integration tests passing",
                    "Performance benchmarks met"
                ]
            ),
            PlanPhase(
                phase_number=5,
                phase_name="Documentation & Deployment",
                estimated_hours=estimated_hours * 0.05,
                tasks=[
                    PlanTask(
                        task_id="5.1",
                        task_name="Update documentation",
                        estimated_hours=estimated_hours * 0.03,
                        description="Update README, API docs"
                    ),
                    PlanTask(
                        task_id="5.2",
                        task_name="Create deployment runbook",
                        estimated_hours=estimated_hours * 0.02,
                        description="Document deployment process"
                    )
                ],
                acceptance_criteria=[
                    "Documentation complete",
                    "Deployment runbook reviewed"
                ]
            )
        ]
        
        return PlanData(
            metadata=metadata,
            definition_of_ready=dor,
            definition_of_done=dod,
            phases=phases,
            tdd_requirements={
                "dor": self._tdd_dor_requirements,
                "dod": self._tdd_dod_requirements
            }
        )
    
    def _extract_feature_name(self, feature_requirements: str) -> str:
        """Extract concise feature name from requirements."""
        # Take first sentence or first 50 chars
        first_sentence = feature_requirements.split('.')[0].strip()
        if len(first_sentence) <= 50:
            return first_sentence
        return feature_requirements[:50].strip() + "..."


# ============================================================================
# Convenience Functions
# ============================================================================

def generate_plan(
    feature_requirements: str,
    cortex_root: Path,
    plan_type: Optional[str] = None,
    complexity_override: Optional[int] = None
) -> GenerationResult:
    """
    Convenience function to generate a plan.
    
    Args:
        feature_requirements: Feature description
        cortex_root: Path to CORTEX root
        plan_type: Optional plan type override
        complexity_override: Optional complexity override
    
    Returns:
        GenerationResult with generated plan
    """
    generator = PlanGenerator(cortex_root)
    return generator.generate(feature_requirements, plan_type, complexity_override)
