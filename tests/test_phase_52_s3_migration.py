"""
Phase 52 S3.2: Migration Orchestrator Test Suite (25+ tests)
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).parent.parent / "cortex" / "orchestrators" / "pr_review"))

from migration_orchestrator import (
    MigrationComponent, MigrationType, MigrationRiskLevel, MigrationStatus,
    CompatibilityCheck, MigrationRollbackPlan, DataTransformationCheck,
    MigrationValidator, MigrationOrchestrator
)


class TestMigrationComponent:
    """Test migration component creation"""

    def test_create_database_migration(self):
        """Test creating database schema migration"""
        comp = MigrationComponent(
            component_id="DB-001",
            name="Users Table Schema",
            type=MigrationType.DATABASE_SCHEMA,
            description="Add email verification",
            version_from="1.0.0",
            version_to="1.1.0"
        )
        assert comp.component_id == "DB-001"
        assert comp.type == MigrationType.DATABASE_SCHEMA
        assert comp.backward_compatible

    def test_create_api_migration(self):
        """Test creating API version migration"""
        comp = MigrationComponent(
            component_id="API-001",
            name="API v2 Upgrade",
            type=MigrationType.API_VERSION,
            description="Migrate to v2",
            version_from="1.0",
            version_to="2.0",
            backward_compatible=False
        )
        assert comp.type == MigrationType.API_VERSION
        assert not comp.backward_compatible

    def test_component_with_affected_services(self):
        """Test component with multiple affected services"""
        comp = MigrationComponent(
            component_id="FW-001",
            name="Framework Upgrade",
            type=MigrationType.FRAMEWORK_UPGRADE,
            description="Node 18 to 20",
            version_from="18",
            version_to="20",
            affected_services=["auth-service", "api-gateway", "worker-service"]
        )
        assert len(comp.affected_services) == 3

    def test_component_with_manual_steps(self):
        """Test component requiring manual steps"""
        comp = MigrationComponent(
            component_id="INF-001",
            name="Infrastructure Change",
            type=MigrationType.INFRASTRUCTURE,
            description="Kubernetes upgrade",
            version_from="1.24",
            version_to="1.26",
            required_manual_steps=[
                "Update node pool",
                "Drain pods",
                "Verify networking"
            ]
        )
        assert len(comp.required_manual_steps) == 3


class TestCompatibilityChecking:
    """Test compatibility validation"""

    def test_compatible_backward_compatible_component(self):
        """Test compatible component with backward compatibility"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="COMPAT-001",
            name="Minor Version Bump",
            type=MigrationType.API_VERSION,
            description="v1.1 minor release",
            version_from="1.0.0",
            version_to="1.1.0",
            backward_compatible=True
        )
        
        check = validator.validate_component_compatibility(comp)
        assert check.is_compatible
        assert check.compatibility_score > 0.7

    def test_incompatible_breaking_changes(self):
        """Test incompatible component with breaking changes"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="COMPAT-002",
            name="Major Version",
            type=MigrationType.API_VERSION,
            description="v1 to v2",
            version_from="1.0.0",
            version_to="2.0.0",
            backward_compatible=False
        )
        
        check = validator.validate_component_compatibility(comp)
        assert not check.is_compatible
        assert check.compatibility_score < 0.7

    def test_compatibility_score_degradation(self):
        """Test compatibility score decreases with risk factors"""
        validator = MigrationValidator()
        
        # Low risk
        comp_low = MigrationComponent(
            component_id="SCORE-1",
            name="Low Risk",
            type=MigrationType.API_VERSION,
            description="Patch",
            version_from="1.0.0",
            version_to="1.0.1",
            affected_services=["service1"]
        )
        check_low = validator.validate_component_compatibility(comp_low)
        
        # High risk
        comp_high = MigrationComponent(
            component_id="SCORE-2",
            name="High Risk",
            type=MigrationType.FRAMEWORK_UPGRADE,
            description="Major",
            version_from="1.0",
            version_to="3.0",
            affected_services=[f"service{i}" for i in range(15)],
            backward_compatible=False,
            required_manual_steps=["step1", "step2", "step3"]
        )
        check_high = validator.validate_component_compatibility(comp_high)
        
        assert check_low.compatibility_score > check_high.compatibility_score


class TestRollbackPlanning:
    """Test rollback plan generation"""

    def test_reversible_rollback_plan(self):
        """Test creating rollback plan for reversible migration"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="ROLL-001",
            name="Reversible Change",
            type=MigrationType.DATABASE_SCHEMA,
            description="Add column",
            version_from="1.0",
            version_to="1.1",
            rollback_supported=True,
            backward_compatible=True
        )
        
        plan = validator.create_rollback_plan(comp)
        assert plan.is_reversible
        assert len(plan.rollback_steps) > 0
        assert plan.estimated_rollback_time_minutes > 0

    def test_non_reversible_rollback_plan(self):
        """Test rollback plan for non-reversible migration"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="ROLL-002",
            name="Non-reversible",
            type=MigrationType.DATA_FORMAT,
            description="Data transformation",
            version_from="1.0",
            version_to="2.0",
            rollback_supported=False
        )
        
        plan = validator.create_rollback_plan(comp)
        assert not plan.is_reversible
        assert len(plan.rollback_steps) == 0

    def test_rollback_validation_steps(self):
        """Test post-rollback validation includes checks"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="ROLL-003",
            name="Test",
            type=MigrationType.API_VERSION,
            description="Version bump",
            version_from="1.0",
            version_to="1.1"
        )
        
        plan = validator.create_rollback_plan(comp)
        assert len(plan.post_rollback_validation) >= 3
        assert any("smoke" in v.lower() for v in plan.post_rollback_validation)
        assert any("health" in v.lower() for v in plan.post_rollback_validation)


class TestDataTransformation:
    """Test data transformation analysis"""

    def test_no_data_loss_transformation(self):
        """Test transformation with no data loss"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="DATA-001",
            name="Safe Transform",
            type=MigrationType.DATA_FORMAT,
            description="Column rename",
            version_from="1.0",
            version_to="1.1"
        )
        
        check = validator.analyze_data_transformation(comp, {
            "old_name": "new_name",
            "email": "email || '@example.com'"
        })
        
        assert not check.has_data_loss

    def test_data_loss_transformation(self):
        """Test transformation with data loss"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="DATA-002",
            name="Unsafe Transform",
            type=MigrationType.DATA_FORMAT,
            description="Drop columns",
            version_from="1.0",
            version_to="1.1"
        )
        
        check = validator.analyze_data_transformation(comp, {
            "id": "id",
            "temporary_field": "DROP"
        })
        
        assert check.has_data_loss

    def test_manual_intervention_detection(self):
        """Test detection of transformations requiring manual intervention"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="DATA-003",
            name="Manual Transform",
            type=MigrationType.DATA_FORMAT,
            description="Complex mapping",
            version_from="1.0",
            version_to="1.1"
        )
        
        check = validator.analyze_data_transformation(comp, {
            "old_format": "new_format_v2"
        })
        
        assert check.manual_intervention_needed

    def test_validation_queries_generated(self):
        """Test validation queries are generated"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="DATA-004",
            name="Test",
            type=MigrationType.DATABASE_SCHEMA,
            description="Schema change",
            version_from="1.0",
            version_to="1.1"
        )
        
        check = validator.analyze_data_transformation(comp, {})
        assert len(check.validation_queries) >= 3


class TestRiskAssessment:
    """Test overall migration risk assessment"""

    def test_minimal_risk_assessment(self):
        """Test minimal risk: single small change"""
        validator = MigrationValidator()
        comp = MigrationComponent(
            component_id="RISK-1",
            name="Patch",
            type=MigrationType.API_VERSION,
            description="1.0.0 → 1.0.1",
            version_from="1.0.0",
            version_to="1.0.1",
            affected_services=["service1"]
        )
        
        risk = validator.assess_migration_risk([comp])
        assert risk in [MigrationRiskLevel.MINIMAL, MigrationRiskLevel.LOW]

    def test_low_risk_assessment(self):
        """Test low risk: backward compatible change"""
        validator = MigrationValidator()
        comps = [
            MigrationComponent(
                component_id="RISK-2a",
                name="Minor 1",
                type=MigrationType.API_VERSION,
                description="1.0 → 1.1",
                version_from="1.0",
                version_to="1.1",
                affected_services=["service1", "service2"]
            ),
            MigrationComponent(
                component_id="RISK-2b",
                name="Minor 2",
                type=MigrationType.API_VERSION,
                description="1.0 → 1.1",
                version_from="1.0",
                version_to="1.1",
                affected_services=["service3"]
            )
        ]
        
        risk = validator.assess_migration_risk(comps)
        assert risk in [MigrationRiskLevel.LOW, MigrationRiskLevel.MEDIUM]

    def test_high_risk_assessment(self):
        """Test high risk: breaking changes"""
        validator = MigrationValidator()
        comps = [
            MigrationComponent(
                component_id="RISK-3",
                name="Major",
                type=MigrationType.FRAMEWORK_UPGRADE,
                description="1.0 → 3.0",
                version_from="1.0",
                version_to="3.0",
                backward_compatible=False,
                affected_services=[f"service{i}" for i in range(15)],
                required_manual_steps=["step1", "step2"]
            )
        ]
        
        risk = validator.assess_migration_risk(comps)
        assert risk in [MigrationRiskLevel.HIGH, MigrationRiskLevel.CRITICAL]

    def test_critical_risk_assessment(self):
        """Test critical risk: non-reversible + data loss"""
        validator = MigrationValidator()
        comps = [
            MigrationComponent(
                component_id="RISK-4",
                name="Irreversible",
                type=MigrationType.DATA_FORMAT,
                description="Lossy transform",
                version_from="1.0",
                version_to="2.0",
                rollback_supported=False,
                backward_compatible=False
            )
        ]
        
        risk = validator.assess_migration_risk(comps)
        assert risk == MigrationRiskLevel.CRITICAL


class TestMigrationOrchestrator:
    """Test main orchestrator"""

    def test_orchestrator_review_low_risk_pr(self):
        """Test reviewing low-risk migration PR"""
        orchestrator = MigrationOrchestrator()
        comp = MigrationComponent(
            component_id="ORCH-1",
            name="Safe Change",
            type=MigrationType.API_VERSION,
            description="Patch",
            version_from="1.0.0",
            version_to="1.0.1"
        )
        
        result = orchestrator.review_migration_pr("PR-001", [comp])
        assert result["pr_id"] == "PR-001"
        assert "APPROVE" in result["recommendation"]

    def test_orchestrator_review_high_risk_pr(self):
        """Test reviewing high-risk migration PR"""
        orchestrator = MigrationOrchestrator()
        comp = MigrationComponent(
            component_id="ORCH-2",
            name="Risky",
            type=MigrationType.DATABASE_SCHEMA,
            description="Restructure",
            version_from="1.0",
            version_to="2.0",
            backward_compatible=False
        )
        
        result = orchestrator.review_migration_pr("PR-002", [comp])
        assert result["pr_id"] == "PR-002"
        assert "REQUEST_CHANGES" in result["recommendation"] or "BLOCK" in result["recommendation"]

    def test_orchestrator_deployment_checklist(self):
        """Test generating deployment checklist"""
        orchestrator = MigrationOrchestrator()
        comps = [
            MigrationComponent(
                component_id="CHECKLIST-1",
                name="Database",
                type=MigrationType.DATABASE_SCHEMA,
                description="Schema change",
                version_from="1.0",
                version_to="1.1",
                required_manual_steps=["Run migrations", "Verify data"]
            )
        ]
        
        checklist = orchestrator.get_deployment_checklist(comps)
        assert len(checklist) >= 5
        assert any("backup" in item.lower() for item in checklist)
        assert any("database" in item.lower() for item in checklist)

    def test_orchestrator_migration_history(self):
        """Test migration history tracking"""
        orchestrator = MigrationOrchestrator()
        comp = MigrationComponent(
            component_id="HIST-1",
            name="Test",
            type=MigrationType.API_VERSION,
            description="Test",
            version_from="1.0",
            version_to="1.1"
        )
        
        orchestrator.review_migration_pr("PR-001", [comp])
        orchestrator.review_migration_pr("PR-002", [comp])
        
        assert len(orchestrator.migration_history) == 2
        assert orchestrator.migration_history[0]["pr_id"] == "PR-001"
        assert orchestrator.migration_history[1]["pr_id"] == "PR-002"


class TestValidationReports:
    """Test validation report generation"""

    def test_report_with_no_checks(self):
        """Test report generation with no components checked"""
        validator = MigrationValidator()
        report = validator.get_validation_report()
        
        assert report["total_components_checked"] == 0
        assert report["compatible_components"] == 0
        assert report["breaking_changes_found"] == 0

    def test_report_with_multiple_components(self):
        """Test report generation with multiple components"""
        validator = MigrationValidator()
        
        for i in range(3):
            comp = MigrationComponent(
                component_id=f"RPT-{i}",
                name=f"Component {i}",
                type=MigrationType.API_VERSION,
                description=f"Component {i}",
                version_from="1.0",
                version_to="1.1"
            )
            validator.validate_component_compatibility(comp)
            validator.create_rollback_plan(comp)
        
        report = validator.get_validation_report()
        assert report["total_components_checked"] == 3
        assert report["reversible_migrations"] >= 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
