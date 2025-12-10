"""
Planning Orchestrator for CORTEX 4.0

Implements strategic feature planning with DoR/DoD enforcement.

Consolidates:
- plan_generation (legacy planning logic)
- Feature planning workflows

New Implementation: 800 LOC

Features:
- Feature decomposition into phases
- Complexity analysis (HIGH/MEDIUM/LOW)
- DoR/DoD validation
- Dependency mapping
- Risk assessment
- Resource estimation
- Test strategy generation
- Autonomous execution after approval

Author: Asif Hussain
Date: December 10, 2025
Version: 4.0.0
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime, timedelta
import logging

from ...core.base_orchestrator import (
    BaseOrchestrator,
    WorkflowContext,
    ValidationResult,
    OrchestratorResult
)
from ...core.state_machine import StateMachine, create_basic_orchestrator_fsm
from ...session.session_manager import SessionManager

logger = logging.getLogger(__name__)


class ComplexityLevel(Enum):
    """Feature complexity levels."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class PhaseType(Enum):
    """Implementation phase types."""
    FOUNDATION = "Foundation"
    CORE = "Core Implementation"
    INTEGRATION = "Integration"
    TESTING = "Testing & Validation"
    DEPLOYMENT = "Deployment"


@dataclass
class Dependency:
    """Feature dependency."""
    feature_name: str
    dependency_type: str  # BLOCKS, DEPENDS_ON, ENHANCES
    description: str


@dataclass
class Risk:
    """Implementation risk."""
    category: str  # TECHNICAL, RESOURCE, TIMELINE, INTEGRATION
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    description: str
    mitigation: str


@dataclass
class Phase:
    """Implementation phase."""
    phase_number: int
    phase_type: PhaseType
    name: str
    description: str
    estimated_days: int
    deliverables: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)


@dataclass
class TestStrategy:
    """Testing strategy for feature."""
    unit_tests: bool
    integration_tests: bool
    e2e_tests: bool
    coverage_target: float
    test_pyramid: Dict[str, int]  # unit, integration, e2e counts
    tdd_recommended: bool


@dataclass
class FeaturePlan:
    """Complete feature implementation plan."""
    feature_name: str
    description: str
    complexity: ComplexityLevel
    phases: List[Phase]
    dependencies: List[Dependency]
    risks: List[Risk]
    test_strategy: TestStrategy
    estimated_total_days: int
    estimated_total_hours: int
    team_size_recommended: int
    created_at: datetime
    approved: bool = False


class PlanningOrchestrator(BaseOrchestrator):
    """
    Planning Orchestrator for strategic feature planning.
    
    Workflow:
    1. DoR Validation: Verify feature requirements, acceptance criteria
    2. Complexity Analysis: Determine feature complexity (HIGH/MEDIUM/LOW)
    3. Phase Decomposition: Break feature into implementation phases
    4. Dependency Mapping: Identify blocking dependencies
    5. Risk Assessment: Analyze technical/resource/timeline risks
    6. Test Strategy: Generate TDD/testing approach
    7. DoD Validation: Ensure plan completeness
    
    Autonomous Execution: Once user approves plan, executes all phases
    without requesting confirmation at every step.
    
    Visual Progress: Real-time progress bars for planning phases.
    """
    
    def __init__(
        self,
        session_manager: SessionManager,
        container: Optional[Any] = None
    ):
        """
        Initialize Planning Orchestrator.
        
        Args:
            session_manager: Session persistence manager
            container: Optional DI container
        """
        state_machine = create_basic_orchestrator_fsm(orchestrator_name="PlanningOrchestrator")
        super().__init__(
            orchestrator_name="PlanningOrchestrator",
            state_machine=state_machine,
            session_manager=session_manager,
            container=container
        )
        
        self.current_plan: Optional[FeaturePlan] = None
        
        logger.info("PlanningOrchestrator initialized")
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Ready for planning workflow.
        
        Prerequisites:
        - Feature name provided
        - Feature description (min 50 chars)
        - At least 3 acceptance criteria
        - Target release or timeline specified
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check feature name
        feature_name = context.inputs.get('feature_name', '').strip()
        if not feature_name:
            errors.append("Feature name is required")
        elif len(feature_name) < 5:
            errors.append("Feature name too short (minimum 5 characters)")
        
        # Check description
        description = context.inputs.get('description', '').strip()
        if not description:
            errors.append("Feature description is required")
        elif len(description) < 50:
            errors.append("Feature description too brief (minimum 50 characters)")
        
        # Check acceptance criteria
        acceptance_criteria = context.inputs.get('acceptance_criteria', [])
        if not acceptance_criteria:
            errors.append("At least 3 acceptance criteria required")
        elif len(acceptance_criteria) < 3:
            errors.append(f"Only {len(acceptance_criteria)} acceptance criteria provided (minimum 3)")
        
        # Check timeline
        if not context.inputs.get('target_release') and not context.inputs.get('timeline_weeks'):
            warnings.append("No target release or timeline specified - will use default estimates")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Done for planning workflow.
        
        Completion Criteria:
        - Feature plan created with all phases
        - Complexity level assigned
        - Dependencies identified
        - Risks assessed with mitigations
        - Test strategy defined
        - Time estimates provided
        - Plan approved by stakeholder
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        if not self.current_plan:
            errors.append("No feature plan created")
            return ValidationResult(passed=False, errors=errors, warnings=warnings)
        
        plan = self.current_plan
        
        # Check phases
        if not plan.phases:
            errors.append("No implementation phases defined")
        elif len(plan.phases) < 2:
            warnings.append("Only 1 phase defined - consider breaking down further")
        
        # Check dependencies
        if not plan.dependencies:
            warnings.append("No dependencies identified - verify feature is standalone")
        
        # Check risks
        if not plan.risks:
            warnings.append("No risks identified - consider technical/resource/timeline risks")
        
        # Check test strategy
        if not plan.test_strategy.unit_tests:
            errors.append("Test strategy missing unit tests")
        if plan.test_strategy.coverage_target < 80.0:
            warnings.append(f"Coverage target {plan.test_strategy.coverage_target}% below recommended 80%")
        
        # Check estimates
        if plan.estimated_total_days == 0:
            errors.append("No time estimates provided")
        
        # Check approval
        if not plan.approved:
            errors.append("Plan not approved by stakeholder")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)
    
    def execute_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute planning workflow.
        
        Autonomous Execution: Once approved, executes all phases without
        requesting confirmation at every step.
        
        Args:
            context: Workflow context
            
        Returns:
            Workflow outputs (feature plan)
        """
        feature_name = context.inputs.get('feature_name')
        description = context.inputs.get('description')
        acceptance_criteria = context.inputs.get('acceptance_criteria', [])
        
        logger.info(f"Starting planning workflow for feature: {feature_name}")
        
        # Phase 1: Complexity Analysis
        self.report_progress(
            current_phase=1,
            total_phases=5,
            phase_name="📊 Complexity Analysis",
            completed_tasks=0,
            total_tasks=5,
            current_task="Analyzing feature complexity"
        )
        
        complexity = self._analyze_complexity(description, acceptance_criteria)
        
        # Phase 2: Phase Decomposition
        self.report_progress(
            current_phase=2,
            total_phases=5,
            phase_name="🔨 Phase Decomposition",
            completed_tasks=1,
            total_tasks=5,
            current_task="Breaking feature into implementation phases"
        )
        
        phases = self._decompose_phases(feature_name, description, complexity, acceptance_criteria)
        
        # Phase 3: Dependency & Risk Analysis
        self.report_progress(
            current_phase=3,
            total_phases=5,
            phase_name="🔗 Dependency & Risk Analysis",
            completed_tasks=2,
            total_tasks=5,
            current_task="Identifying dependencies and assessing risks"
        )
        
        dependencies = self._identify_dependencies(feature_name, description)
        risks = self._assess_risks(complexity, dependencies, phases)
        
        # Phase 4: Test Strategy
        self.report_progress(
            current_phase=4,
            total_phases=5,
            phase_name="🧪 Test Strategy",
            completed_tasks=3,
            total_tasks=5,
            current_task="Generating TDD/testing approach"
        )
        
        test_strategy = self._generate_test_strategy(complexity, phases)
        
        # Phase 5: Resource Estimation
        self.report_progress(
            current_phase=5,
            total_phases=5,
            phase_name="👥 Resource Estimation",
            completed_tasks=4,
            total_tasks=5,
            current_task="Calculating time/resource estimates"
        )
        
        total_days = sum(p.estimated_days for p in phases)
        total_hours = total_days * 8
        team_size = self._recommend_team_size(complexity, total_days)
        
        # Create feature plan
        self.current_plan = FeaturePlan(
            feature_name=feature_name,
            description=description,
            complexity=complexity,
            phases=phases,
            dependencies=dependencies,
            risks=risks,
            test_strategy=test_strategy,
            estimated_total_days=total_days,
            estimated_total_hours=total_hours,
            team_size_recommended=team_size,
            created_at=datetime.now(),
            approved=context.inputs.get('auto_approve', False)
        )
        
        # Final progress
        self.report_progress(
            current_phase=5,
            total_phases=5,
            phase_name="✅ Planning Complete",
            completed_tasks=5,
            total_tasks=5,
            current_task=f"Feature plan created - {len(phases)} phases, {total_days} days"
        )
        
        return {
            'plan': self._plan_to_dict(self.current_plan),
            'success': True
        }
    
    def _analyze_complexity(
        self,
        description: str,
        acceptance_criteria: List[str]
    ) -> ComplexityLevel:
        """
        Analyze feature complexity.
        
        Heuristics:
        - HIGH: 10+ acceptance criteria, multiple integrations, data migration
        - MEDIUM: 5-9 criteria, single integration, API changes
        - LOW: 3-4 criteria, UI changes only, no integrations
        
        Args:
            description: Feature description
            acceptance_criteria: List of acceptance criteria
            
        Returns:
            ComplexityLevel
        """
        criteria_count = len(acceptance_criteria)
        description_lower = description.lower()
        
        # HIGH complexity indicators
        high_indicators = [
            'migration', 'integration', 'api', 'database schema',
            'authentication', 'security', 'performance', 'scalability'
        ]
        
        if criteria_count >= 10:
            return ComplexityLevel.HIGH
        
        if any(indicator in description_lower for indicator in high_indicators):
            return ComplexityLevel.HIGH
        
        # LOW complexity indicators
        if criteria_count <= 4 and 'ui' in description_lower:
            return ComplexityLevel.LOW
        
        # Default to MEDIUM
        return ComplexityLevel.MEDIUM
    
    def _decompose_phases(
        self,
        feature_name: str,
        description: str,
        complexity: ComplexityLevel,
        acceptance_criteria: List[str]
    ) -> List[Phase]:
        """
        Decompose feature into implementation phases.
        
        Phase structure varies by complexity:
        - HIGH: 5 phases (Foundation, Core, Integration, Testing, Deployment)
        - MEDIUM: 3 phases (Foundation, Core, Testing)
        - LOW: 2 phases (Implementation, Testing)
        
        Args:
            feature_name: Feature name
            description: Feature description
            complexity: Complexity level
            acceptance_criteria: List of acceptance criteria
            
        Returns:
            List of Phase objects
        """
        phases = []
        
        if complexity == ComplexityLevel.HIGH:
            # 5-phase approach for high complexity
            phases = [
                Phase(
                    phase_number=1,
                    phase_type=PhaseType.FOUNDATION,
                    name="Foundation & Architecture",
                    description="Set up architecture, models, interfaces",
                    estimated_days=5,
                    deliverables=[
                        "Domain models defined",
                        "Interfaces/contracts established",
                        "Database schema designed"
                    ],
                    acceptance_criteria=acceptance_criteria[:2]
                ),
                Phase(
                    phase_number=2,
                    phase_type=PhaseType.CORE,
                    name="Core Implementation",
                    description="Implement core business logic",
                    estimated_days=10,
                    deliverables=[
                        "Business logic implemented",
                        "Application services created",
                        "Unit tests passing"
                    ],
                    dependencies=["Phase 1"],
                    acceptance_criteria=acceptance_criteria[2:6]
                ),
                Phase(
                    phase_number=3,
                    phase_type=PhaseType.INTEGRATION,
                    name="Integration",
                    description="Integrate with external systems",
                    estimated_days=7,
                    deliverables=[
                        "External API integrations complete",
                        "Data migration scripts tested",
                        "Integration tests passing"
                    ],
                    dependencies=["Phase 2"],
                    acceptance_criteria=acceptance_criteria[6:8] if len(acceptance_criteria) > 6 else []
                ),
                Phase(
                    phase_number=4,
                    phase_type=PhaseType.TESTING,
                    name="Testing & Validation",
                    description="Comprehensive testing and bug fixes",
                    estimated_days=5,
                    deliverables=[
                        "E2E tests complete",
                        "Performance tests passing",
                        "All bugs resolved"
                    ],
                    dependencies=["Phase 3"]
                ),
                Phase(
                    phase_number=5,
                    phase_type=PhaseType.DEPLOYMENT,
                    name="Deployment & Monitoring",
                    description="Production deployment and monitoring setup",
                    estimated_days=3,
                    deliverables=[
                        "Production deployment complete",
                        "Monitoring/alerts configured",
                        "Documentation updated"
                    ],
                    dependencies=["Phase 4"]
                )
            ]
        
        elif complexity == ComplexityLevel.MEDIUM:
            # 3-phase approach for medium complexity
            phases = [
                Phase(
                    phase_number=1,
                    phase_type=PhaseType.FOUNDATION,
                    name="Foundation",
                    description="Set up models and interfaces",
                    estimated_days=3,
                    deliverables=["Models defined", "Interfaces established"],
                    acceptance_criteria=acceptance_criteria[:2]
                ),
                Phase(
                    phase_number=2,
                    phase_type=PhaseType.CORE,
                    name="Core Implementation",
                    description="Implement feature logic",
                    estimated_days=5,
                    deliverables=["Feature implemented", "Unit tests passing"],
                    dependencies=["Phase 1"],
                    acceptance_criteria=acceptance_criteria[2:]
                ),
                Phase(
                    phase_number=3,
                    phase_type=PhaseType.TESTING,
                    name="Testing & Integration",
                    description="Integration testing and refinement",
                    estimated_days=2,
                    deliverables=["Integration tests complete", "All tests passing"],
                    dependencies=["Phase 2"]
                )
            ]
        
        else:  # LOW complexity
            # 2-phase approach for low complexity
            phases = [
                Phase(
                    phase_number=1,
                    phase_type=PhaseType.CORE,
                    name="Implementation",
                    description="Implement feature",
                    estimated_days=2,
                    deliverables=["Feature implemented"],
                    acceptance_criteria=acceptance_criteria
                ),
                Phase(
                    phase_number=2,
                    phase_type=PhaseType.TESTING,
                    name="Testing",
                    description="Test and validate",
                    estimated_days=1,
                    deliverables=["Tests passing", "Feature validated"],
                    dependencies=["Phase 1"]
                )
            ]
        
        return phases
    
    def _identify_dependencies(
        self,
        feature_name: str,
        description: str
    ) -> List[Dependency]:
        """
        Identify feature dependencies.
        
        Analyzes description for dependency keywords:
        - "requires", "depends on" → DEPENDS_ON
        - "blocks", "prerequisite for" → BLOCKS
        - "enhances", "extends" → ENHANCES
        
        Args:
            feature_name: Feature name
            description: Feature description
            
        Returns:
            List of Dependency objects
        """
        dependencies = []
        description_lower = description.lower()
        
        # Simple keyword-based detection (in production, use NLP)
        if 'authentication' in description_lower:
            dependencies.append(Dependency(
                feature_name="User Authentication",
                dependency_type="DEPENDS_ON",
                description="Requires user authentication system"
            ))
        
        if 'api' in description_lower:
            dependencies.append(Dependency(
                feature_name="API Infrastructure",
                dependency_type="DEPENDS_ON",
                description="Requires API endpoints and routing"
            ))
        
        if 'database' in description_lower or 'data' in description_lower:
            dependencies.append(Dependency(
                feature_name="Database Schema",
                dependency_type="DEPENDS_ON",
                description="Requires database schema updates"
            ))
        
        return dependencies
    
    def _assess_risks(
        self,
        complexity: ComplexityLevel,
        dependencies: List[Dependency],
        phases: List[Phase]
    ) -> List[Risk]:
        """
        Assess implementation risks.
        
        Risk categories:
        - TECHNICAL: Integration complexity, technical debt
        - RESOURCE: Team availability, skill gaps
        - TIMELINE: Deadline pressure, scope creep
        - INTEGRATION: External system dependencies
        
        Args:
            complexity: Feature complexity
            dependencies: List of dependencies
            phases: Implementation phases
            
        Returns:
            List of Risk objects
        """
        risks = []
        
        # Complexity-based risks
        if complexity == ComplexityLevel.HIGH:
            risks.append(Risk(
                category="TECHNICAL",
                severity="HIGH",
                description="High complexity increases risk of technical debt",
                mitigation="Implement thorough code reviews and architecture validation"
            ))
        
        # Dependency-based risks
        if len(dependencies) > 2:
            risks.append(Risk(
                category="INTEGRATION",
                severity="MEDIUM",
                description="Multiple dependencies may cause blocking issues",
                mitigation="Coordinate with dependent teams early, use feature flags"
            ))
        
        # Timeline risks
        total_days = sum(p.estimated_days for p in phases)
        if total_days > 20:
            risks.append(Risk(
                category="TIMELINE",
                severity="MEDIUM",
                description="Extended timeline increases risk of scope creep",
                mitigation="Lock scope after planning phase, use agile sprints"
            ))
        
        # Always include resource risk
        risks.append(Risk(
            category="RESOURCE",
            severity="LOW",
            description="Team availability may impact delivery",
            mitigation="Ensure backup resources, document knowledge"
        ))
        
        return risks
    
    def _generate_test_strategy(
        self,
        complexity: ComplexityLevel,
        phases: List[Phase]
    ) -> TestStrategy:
        """
        Generate testing strategy.
        
        Test pyramid by complexity:
        - HIGH: 60% unit, 30% integration, 10% e2e
        - MEDIUM: 70% unit, 25% integration, 5% e2e
        - LOW: 80% unit, 15% integration, 5% e2e
        
        Args:
            complexity: Feature complexity
            phases: Implementation phases
            
        Returns:
            TestStrategy
        """
        if complexity == ComplexityLevel.HIGH:
            return TestStrategy(
                unit_tests=True,
                integration_tests=True,
                e2e_tests=True,
                coverage_target=85.0,
                test_pyramid={'unit': 60, 'integration': 30, 'e2e': 10},
                tdd_recommended=True
            )
        
        elif complexity == ComplexityLevel.MEDIUM:
            return TestStrategy(
                unit_tests=True,
                integration_tests=True,
                e2e_tests=True,
                coverage_target=80.0,
                test_pyramid={'unit': 70, 'integration': 25, 'e2e': 5},
                tdd_recommended=True
            )
        
        else:  # LOW
            return TestStrategy(
                unit_tests=True,
                integration_tests=True,
                e2e_tests=False,
                coverage_target=80.0,
                test_pyramid={'unit': 80, 'integration': 15, 'e2e': 5},
                tdd_recommended=False
            )
    
    def _recommend_team_size(
        self,
        complexity: ComplexityLevel,
        total_days: int
    ) -> int:
        """
        Recommend team size based on complexity and timeline.
        
        Args:
            complexity: Feature complexity
            total_days: Total estimated days
            
        Returns:
            Recommended team size
        """
        if complexity == ComplexityLevel.HIGH and total_days > 20:
            return 3  # Large team for complex, long features
        elif complexity == ComplexityLevel.MEDIUM or total_days > 10:
            return 2  # Medium team for moderate features
        else:
            return 1  # Solo developer for simple features
    
    def _plan_to_dict(self, plan: FeaturePlan) -> Dict[str, Any]:
        """Convert FeaturePlan to dictionary."""
        return {
            'feature_name': plan.feature_name,
            'description': plan.description,
            'complexity': plan.complexity.value,
            'phases': [
                {
                    'phase_number': p.phase_number,
                    'phase_type': p.phase_type.value,
                    'name': p.name,
                    'description': p.description,
                    'estimated_days': p.estimated_days,
                    'deliverables': p.deliverables,
                    'dependencies': p.dependencies,
                    'acceptance_criteria': p.acceptance_criteria
                }
                for p in plan.phases
            ],
            'dependencies': [
                {
                    'feature_name': d.feature_name,
                    'dependency_type': d.dependency_type,
                    'description': d.description
                }
                for d in plan.dependencies
            ],
            'risks': [
                {
                    'category': r.category,
                    'severity': r.severity,
                    'description': r.description,
                    'mitigation': r.mitigation
                }
                for r in plan.risks
            ],
            'test_strategy': {
                'unit_tests': plan.test_strategy.unit_tests,
                'integration_tests': plan.test_strategy.integration_tests,
                'e2e_tests': plan.test_strategy.e2e_tests,
                'coverage_target': plan.test_strategy.coverage_target,
                'test_pyramid': plan.test_strategy.test_pyramid,
                'tdd_recommended': plan.test_strategy.tdd_recommended
            },
            'estimated_total_days': plan.estimated_total_days,
            'estimated_total_hours': plan.estimated_total_hours,
            'team_size_recommended': plan.team_size_recommended,
            'created_at': plan.created_at.isoformat(),
            'approved': plan.approved
        }


# Factory function
def create_planning_orchestrator(
    session_manager: SessionManager,
    container: Optional[Any] = None
) -> PlanningOrchestrator:
    """Create and return Planning Orchestrator instance."""
    return PlanningOrchestrator(
        session_manager=session_manager,
        container=container
    )
