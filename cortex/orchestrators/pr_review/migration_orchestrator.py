"""
Phase 52 S3.1: Migration Orchestrator Framework

Large-scale PR review framework for migration PRs:
- Migration validation rules
- Backward compatibility checks
- Data transformation analysis
- Rollback readiness verification
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class MigrationType(Enum):
    """Types of migrations"""
    DATABASE_SCHEMA = "database_schema"
    API_VERSION = "api_version"
    FRAMEWORK_UPGRADE = "framework_upgrade"
    DATA_FORMAT = "data_format"
    SERVICE_MIGRATION = "service_migration"
    INFRASTRUCTURE = "infrastructure"


class MigrationRiskLevel(Enum):
    """Risk assessment levels"""
    CRITICAL = 100  # Requires manual approval
    HIGH = 75       # Needs thorough review
    MEDIUM = 50     # Standard review required
    LOW = 25        # Minimal risk, can be fast-tracked
    MINIMAL = 10    # No special handling needed


class MigrationStatus(Enum):
    """Migration status tracking"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    TESTING = "testing"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    DEPLOYED = "deployed"
    ROLLED_BACK = "rolled_back"


@dataclass
class MigrationComponent:
    """Single component in a migration"""
    component_id: str
    name: str
    type: MigrationType
    description: str
    version_from: str
    version_to: str
    backward_compatible: bool = True
    rollback_supported: bool = True
    estimated_duration_minutes: int = 30
    affected_services: List[str] = field(default_factory=list)
    required_manual_steps: List[str] = field(default_factory=list)


@dataclass
class CompatibilityCheck:
    """Result of compatibility check"""
    component_id: str
    is_compatible: bool
    compatibility_score: float  # 0.0 - 1.0
    breaking_changes: List[str] = field(default_factory=list)
    deprecation_warnings: List[str] = field(default_factory=list)
    migration_path_warning: Optional[str] = None


@dataclass
class MigrationRollbackPlan:
    """Rollback plan for a migration"""
    migration_id: str
    is_reversible: bool
    rollback_steps: List[str] = field(default_factory=list)
    estimated_rollback_time_minutes: int = 0
    data_preservation_strategy: str = "full_backup"
    post_rollback_validation: List[str] = field(default_factory=list)


@dataclass
class DataTransformationCheck:
    """Analysis of data transformations"""
    component_id: str
    has_data_loss: bool = False
    data_loss_impact: Optional[str] = None
    transformation_reversible: bool = True
    affected_record_count: int = 0
    manual_intervention_needed: bool = False
    validation_queries: List[str] = field(default_factory=list)


class MigrationValidator:
    """Validates migration PRs for safety and completeness"""

    def __init__(self):
        self.checked_components: Dict[str, CompatibilityCheck] = {}
        self.rollback_plans: Dict[str, MigrationRollbackPlan] = {}
        self.data_transformations: Dict[str, DataTransformationCheck] = {}

    def validate_component_compatibility(self, component: MigrationComponent) -> CompatibilityCheck:
        """Check if component migration is compatible"""
        breaking_changes = []
        deprecations = []
        score = 1.0

        # Check backward compatibility
        if not component.backward_compatible:
            breaking_changes.append(f"Not backward compatible: {component.name}")
            score -= 0.3

        # Check affected services
        if len(component.affected_services) > 5:
            deprecations.append(f"High blast radius: {len(component.affected_services)} services affected")
            score -= 0.1

        # Check manual steps required
        if component.required_manual_steps:
            deprecations.append(f"Manual steps required: {len(component.required_manual_steps)} steps")
            score -= 0.05

        # Check version compatibility
        is_compatible = len(breaking_changes) == 0 and score > 0.5

        check = CompatibilityCheck(
            component_id=component.component_id,
            is_compatible=is_compatible,
            compatibility_score=max(0.0, min(1.0, score)),
            breaking_changes=breaking_changes,
            deprecation_warnings=deprecations
        )

        self.checked_components[component.component_id] = check
        return check

    def create_rollback_plan(self, component: MigrationComponent) -> MigrationRollbackPlan:
        """Create rollback plan for component"""
        is_reversible = component.rollback_supported and component.backward_compatible

        rollback_steps = []
        if is_reversible:
            rollback_steps = [
                f"Revert {component.name} to version {component.version_from}",
                "Restore database snapshot",
                "Verify service health",
                f"Validate {len(component.affected_services)} affected services"
            ]

        plan = MigrationRollbackPlan(
            migration_id=component.component_id,
            is_reversible=is_reversible,
            rollback_steps=rollback_steps,
            estimated_rollback_time_minutes=component.estimated_duration_minutes + 10,
            post_rollback_validation=[
                "Run smoke tests",
                "Check data integrity",
                "Verify service connectivity"
            ]
        )

        self.rollback_plans[component.component_id] = plan
        return plan

    def analyze_data_transformation(self, component: MigrationComponent,
                                  data_mapping: Dict[str, str]) -> DataTransformationCheck:
        """Analyze data transformation risks"""
        has_data_loss = False
        manual_intervention = False
        affected_count = 0

        # Check for data loss patterns
        for old_field, new_field in data_mapping.items():
            if new_field == "DROP":
                has_data_loss = True
            elif "||" not in new_field and old_field != new_field:
                manual_intervention = True

        check = DataTransformationCheck(
            component_id=component.component_id,
            has_data_loss=has_data_loss,
            transformation_reversible=component.backward_compatible,
            manual_intervention_needed=manual_intervention,
            validation_queries=[
                f"SELECT COUNT(*) FROM {component.name}",
                f"SELECT * FROM {component.name} WHERE id IS NULL",
                f"SELECT DISTINCT status FROM {component.name}"
            ]
        )

        self.data_transformations[component.component_id] = check
        return check

    def assess_migration_risk(self, components: List[MigrationComponent]) -> MigrationRiskLevel:
        """Assess overall migration risk"""
        if not components:
            return MigrationRiskLevel.MINIMAL

        total_risk = 0
        critical_found = False

        for component in components:
            # Check compatibility
            check = self.validate_component_compatibility(component)
            if check.compatibility_score < 0.5:
                critical_found = True
                total_risk += MigrationRiskLevel.CRITICAL.value

            # Check rollback capability
            plan = self.create_rollback_plan(component)
            if not plan.is_reversible:
                critical_found = True
                total_risk += MigrationRiskLevel.HIGH.value

            # Check data transformation
            data_check = self.analyze_data_transformation(component, {})
            if data_check.has_data_loss or data_check.manual_intervention_needed:
                total_risk += MigrationRiskLevel.MEDIUM.value

            # Affected services count
            if len(component.affected_services) > 10:
                total_risk += MigrationRiskLevel.HIGH.value

        avg_risk = total_risk / max(len(components), 1)

        if avg_risk >= MigrationRiskLevel.CRITICAL.value:
            return MigrationRiskLevel.CRITICAL
        elif avg_risk >= MigrationRiskLevel.HIGH.value:
            return MigrationRiskLevel.HIGH
        elif avg_risk >= MigrationRiskLevel.MEDIUM.value:
            return MigrationRiskLevel.MEDIUM
        elif avg_risk >= MigrationRiskLevel.LOW.value:
            return MigrationRiskLevel.LOW
        else:
            return MigrationRiskLevel.MINIMAL

    def get_validation_report(self) -> Dict[str, Any]:
        """Generate validation report"""
        return {
            "total_components_checked": len(self.checked_components),
            "compatible_components": len([c for c in self.checked_components.values() if c.is_compatible]),
            "breaking_changes_found": sum(len(c.breaking_changes) for c in self.checked_components.values()),
            "reversible_migrations": len([p for p in self.rollback_plans.values() if p.is_reversible]),
            "data_loss_risks": len([d for d in self.data_transformations.values() if d.has_data_loss]),
            "manual_steps_required": sum(
                len(p.rollback_steps) for p in self.rollback_plans.values()
            )
        }


class MigrationOrchestrator:
    """Main orchestrator for migration reviews"""

    def __init__(self):
        self.validator = MigrationValidator()
        self.migration_history: List[Dict[str, Any]] = []

    def review_migration_pr(self, pr_id: str, components: List[MigrationComponent]) -> Dict[str, Any]:
        """Review a migration PR"""
        risk_level = self.validator.assess_migration_risk(components)
        report = self.validator.get_validation_report()

        recommendation = self._get_recommendation(risk_level, report)

        migration_record = {
            "pr_id": pr_id,
            "components_count": len(components),
            "risk_level": risk_level.name,
            "recommendation": recommendation,
            "report": report
        }

        self.migration_history.append(migration_record)

        return migration_record

    def _get_recommendation(self, risk_level: MigrationRiskLevel, report: Dict[str, Any]) -> str:
        """Get recommendation based on risk"""
        if risk_level == MigrationRiskLevel.CRITICAL:
            return "BLOCK: Critical risk - requires security team review"
        elif risk_level == MigrationRiskLevel.HIGH:
            return "REQUEST_CHANGES: High risk - needs data loss analysis"
        elif risk_level == MigrationRiskLevel.MEDIUM:
            return "COMMENT: Medium risk - verify rollback plan"
        else:
            return "APPROVE: Low risk migration"

    def get_deployment_checklist(self, components: List[MigrationComponent]) -> List[str]:
        """Generate deployment checklist"""
        checklist = [
            "✓ Backup production database",
            "✓ Notify on-call team",
            "✓ Prepare rollback plan"
        ]

        for component in components:
            checklist.append(f"✓ Deploy {component.name} v{component.version_to}")
            for step in component.required_manual_steps:
                checklist.append(f"  → {step}")

        checklist.extend([
            "✓ Run post-deployment tests",
            "✓ Monitor metrics",
            "✓ Verify all services healthy"
        ])

        return checklist
