"""
Migration Strategist Component
Generates incremental migration plans using Strangler Fig pattern.

Features:
- Strangler Fig pattern implementation
- Phased migration planning
- Risk assessment per phase
- Rollback checkpoint generation
- Parallel run validation strategies
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class RiskLevel(Enum):
    """Risk levels for migration phases."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


@dataclass
class MigrationPhase:
    """Single phase in migration strategy."""
    phase_number: int
    name: str
    description: str
    duration_weeks: int
    effort_hours: int
    risk: str
    components: List[str]
    deliverables: List[str]
    rollback_strategy: str
    validation_strategy: Optional[str] = None


@dataclass
class MigrationStrategy:
    """Complete migration strategy document."""
    title: str
    total_duration_weeks: int
    total_effort_hours: int
    phases: List[MigrationPhase]
    risk_summary: Dict[str, int]
    assumptions: List[str]


class MigrationStrategist:
    """
    Generates incremental migration plans using Strangler Fig pattern.
    
    The Strangler Fig pattern incrementally replaces legacy components
    without requiring a big-bang rewrite. New functionality is built
    alongside old code, gradually replacing legacy behavior.
    
    Features:
    - Phased migration (2-4 week sprints)
    - Risk-based ordering (low-risk infrastructure first)
    - Parallel run validation (compare old vs new)
    - Rollback checkpoints (Git tags + feature flags)
    
    Example:
        strategist = MigrationStrategist()
        strategy = strategist.plan(architecture_assessment, constraints={"timeline": 6, "team_size": 3})
        print(f"Migration will take {strategy.total_duration_weeks} weeks")
    """
    
    # Effort estimation factors (hours per component type)
    EFFORT_FACTORS = {
        'infrastructure': 10,  # Config, DI, base classes
        'entity': 2,           # Domain entity
        'repository': 4,       # Data access layer
        'use_case': 6,         # Business logic
        'controller': 3,       # API endpoint
        'test': 1.5,           # Per component test
    }
    
    def __init__(self):
        """Initialize migration strategist."""
        self.phases: List[MigrationPhase] = []
    
    def plan(self, architecture_assessment: Dict[str, Any], constraints: Optional[Dict[str, Any]] = None) -> MigrationStrategy:
        """
        Generate migration strategy.
        
        Args:
            architecture_assessment: Architecture assessment from ArchitectureIntelligence
            constraints: User constraints (timeline, team_size, risk_tolerance)
        
        Returns:
            MigrationStrategy with phased plan
        """
        constraints = constraints or {}
        timeline_weeks = constraints.get('timeline', 8)
        team_size = constraints.get('team_size', 2)
        risk_tolerance = constraints.get('risk_tolerance', 'medium')
        
        # Extract assessment details
        current_pattern = architecture_assessment.get('current_pattern', 'unknown')
        recommended_pattern = architecture_assessment.get('recommended_pattern', 'clean_architecture')
        service_candidates = architecture_assessment.get('service_candidates', [])
        tech_stack = architecture_assessment.get('tech_stack', {})
        
        # Build phases
        self.phases = []
        
        # Phase 1: Infrastructure (always first, low risk)
        self._add_infrastructure_phase(recommended_pattern, tech_stack)
        
        # Phase 2-N: Service/component migration
        if service_candidates:
            self._add_service_migration_phases(service_candidates, risk_tolerance)
        else:
            self._add_component_migration_phases(recommended_pattern)
        
        # Final Phase: Cutover (always last, high risk)
        self._add_cutover_phase(current_pattern, recommended_pattern)
        
        # Calculate totals
        total_duration = sum(p.duration_weeks for p in self.phases)
        total_effort = sum(p.effort_hours for p in self.phases)
        
        # Adjust for team size and timeline constraints
        if total_duration > timeline_weeks:
            self._compress_timeline(timeline_weeks, team_size)
        
        # Build risk summary
        risk_summary = {
            RiskLevel.LOW.value: sum(1 for p in self.phases if p.risk == RiskLevel.LOW.value),
            RiskLevel.MEDIUM.value: sum(1 for p in self.phases if p.risk == RiskLevel.MEDIUM.value),
            RiskLevel.HIGH.value: sum(1 for p in self.phases if p.risk == RiskLevel.HIGH.value),
        }
        
        # Build strategy
        strategy = MigrationStrategy(
            title=f"Migration: {current_pattern} → {recommended_pattern}",
            total_duration_weeks=sum(p.duration_weeks for p in self.phases),
            total_effort_hours=sum(p.effort_hours for p in self.phases),
            phases=self.phases,
            risk_summary=risk_summary,
            assumptions=[
                f"Team size: {team_size} developers",
                f"Timeline constraint: {timeline_weeks} weeks",
                "Parallel run validation for all critical components",
                "30-day grace period before decommissioning legacy code"
            ]
        )
        
        logger.info(f"Migration strategy generated: {len(self.phases)} phases, {strategy.total_duration_weeks} weeks, {strategy.total_effort_hours} hours")
        return strategy
    
    def _add_infrastructure_phase(self, recommended_pattern: str, tech_stack: Dict[str, str]):
        """Add infrastructure setup phase (always first)."""
        phase = MigrationPhase(
            phase_number=1,
            name="Infrastructure Setup",
            description="Set up project structure, dependency injection, configuration",
            duration_weeks=2,
            effort_hours=self._estimate_effort(['infrastructure'] * 4),  # 4 infrastructure components
            risk=RiskLevel.LOW.value,
            components=['Project structure', 'DI container', 'Configuration', 'Base classes'],
            deliverables=[
                f"{recommended_pattern} folder structure",
                "Dependency injection configured",
                "Configuration management (env vars, secrets)",
                "Base entity, repository, use case classes"
            ],
            rollback_strategy="Git tag `v1.0-legacy` (no production impact)",
            validation_strategy="Compile/build succeeds, DI container resolves dependencies"
        )
        self.phases.append(phase)
    
    def _add_service_migration_phases(self, service_candidates: List[Dict[str, Any]], risk_tolerance: str):
        """Add phases for each service candidate (Strangler Fig pattern)."""
        for idx, service in enumerate(service_candidates, start=2):
            service_name = service.get('name', f'Service{idx}')
            files = service.get('files', [])
            confidence = service.get('confidence', 0.5)
            
            # Risk assessment based on confidence and file count
            if confidence > 0.8 and len(files) < 5:
                risk = RiskLevel.MEDIUM.value
            elif confidence < 0.6 or len(files) > 10:
                risk = RiskLevel.HIGH.value
            else:
                risk = RiskLevel.MEDIUM.value
            
            phase = MigrationPhase(
                phase_number=idx,
                name=f"Migrate {service_name}",
                description=f"Migrate {service_name} to Clean Architecture, run in parallel with legacy",
                duration_weeks=3,
                effort_hours=self._estimate_effort(['entity', 'repository', 'use_case', 'controller', 'test'] * len(files)),
                risk=risk,
                components=files,
                deliverables=[
                    f"{service_name} domain entities",
                    f"{service_name} repositories",
                    f"{service_name} use cases",
                    f"{service_name} API endpoints",
                    f"Unit + integration tests"
                ],
                rollback_strategy=f"Feature flag `use_new_{service_name.lower()}=false`",
                validation_strategy=f"Parallel run: Compare {service_name} outputs (100 transactions, assert equivalence)"
            )
            self.phases.append(phase)
    
    def _add_component_migration_phases(self, recommended_pattern: str):
        """Add generic component migration phases (when no service candidates identified)."""
        phase = MigrationPhase(
            phase_number=2,
            name="Core Component Migration",
            description=f"Migrate core business logic to {recommended_pattern}",
            duration_weeks=4,
            effort_hours=self._estimate_effort(['entity', 'repository', 'use_case', 'controller', 'test'] * 10),
            risk=RiskLevel.MEDIUM.value,
            components=['Business logic', 'Data access', 'API layer'],
            deliverables=[
                "Domain entities migrated",
                "Repositories implemented",
                "Use cases implemented",
                "API endpoints migrated",
                "Test coverage >80%"
            ],
            rollback_strategy="Feature flag `use_new_architecture=false`",
            validation_strategy="Parallel run: Compare API responses for all endpoints"
        )
        self.phases.append(phase)
    
    def _add_cutover_phase(self, current_pattern: str, recommended_pattern: str):
        """Add final cutover phase (always last, high risk)."""
        phase = MigrationPhase(
            phase_number=len(self.phases) + 1,
            name="Cutover & Decommission",
            description=f"Complete migration, monitor, decommission legacy {current_pattern} code",
            duration_weeks=1,
            effort_hours=self._estimate_effort(['infrastructure'] * 2),
            risk=RiskLevel.HIGH.value,
            components=['Legacy code removal', 'Monitoring', 'Documentation'],
            deliverables=[
                "Error rate <0.1%",
                "Performance metrics within SLA",
                "30-day monitoring period complete",
                "Legacy code archived"
            ],
            rollback_strategy="Feature flag toggle (emergency only)",
            validation_strategy="Monitor production metrics: error rate, latency, throughput"
        )
        self.phases.append(phase)
    
    def _estimate_effort(self, component_types: List[str]) -> int:
        """Estimate effort hours for components."""
        return sum(self.EFFORT_FACTORS.get(ct, 5) for ct in component_types)
    
    def _compress_timeline(self, target_weeks: int, team_size: int):
        """Compress timeline by parallelizing phases or increasing team size."""
        current_duration = sum(p.duration_weeks for p in self.phases)
        
        if current_duration <= target_weeks:
            return  # Already within timeline
        
        # Simple compression: reduce each phase proportionally
        compression_factor = target_weeks / current_duration
        
        for phase in self.phases:
            phase.duration_weeks = max(1, int(phase.duration_weeks * compression_factor))
        
        logger.warning(f"Timeline compressed from {current_duration} to {target_weeks} weeks. Consider increasing team size from {team_size}.")
    
    def to_dict(self, strategy: MigrationStrategy) -> Dict[str, Any]:
        """Convert strategy to dictionary for JSON serialization."""
        return {
            **asdict(strategy),
            'phases': [asdict(p) for p in strategy.phases]
        }
    
    def to_markdown(self, strategy: MigrationStrategy) -> str:
        """Generate Markdown migration strategy document."""
        md = f"# {strategy.title}\n\n"
        md += f"**Total Duration:** {strategy.total_duration_weeks} weeks  \n"
        md += f"**Total Effort:** {strategy.total_effort_hours} hours  \n"
        md += f"**Phases:** {len(strategy.phases)}  \n\n"
        
        md += "## Risk Summary\n\n"
        for risk, count in strategy.risk_summary.items():
            md += f"- **{risk}:** {count} phases  \n"
        md += "\n"
        
        md += "## Assumptions\n\n"
        for assumption in strategy.assumptions:
            md += f"- {assumption}  \n"
        md += "\n"
        
        md += "## Migration Phases\n\n"
        for phase in strategy.phases:
            md += f"### Phase {phase.phase_number}: {phase.name}\n\n"
            md += f"{phase.description}  \n\n"
            md += f"- **Duration:** {phase.duration_weeks} weeks  \n"
            md += f"- **Effort:** {phase.effort_hours} hours  \n"
            md += f"- **Risk:** {phase.risk}  \n\n"
            
            md += "**Deliverables:**  \n"
            for deliverable in phase.deliverables:
                md += f"- {deliverable}  \n"
            md += "\n"
            
            md += f"**Rollback Strategy:** {phase.rollback_strategy}  \n"
            if phase.validation_strategy:
                md += f"**Validation Strategy:** {phase.validation_strategy}  \n"
            md += "\n"
        
        return md
