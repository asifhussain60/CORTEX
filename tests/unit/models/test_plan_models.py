"""Tests for plan models and registry."""

import pytest
from datetime import datetime

from cortex.models.plan_models import (
    PlanSpec,
    PlanMetadata,
    PlanClassification,
    Overview,
    PlanStage,
    IntentType,
    RiskLevel,
    PlanStatus,
    StageType,
)
from cortex.registry.plan_registry import PlanRegistry, PlanSummary


class TestPlanModels:
    """Test plan model validation."""

    def test_plan_metadata_creation(self) -> None:
        """Test PlanMetadata model creation."""
        metadata = PlanMetadata(
            phase_id="phase-45",
            title="Test Plan",
            author="test",
            created_date=datetime.utcnow(),
            estimated_duration="5 days",
            estimated_hours=10,
            test_target=50,
            roi_score=0.8,
            risk_level=RiskLevel.MEDIUM,
        )
        assert metadata.phase_id == "phase-45"
        assert metadata.title == "Test Plan"

    def test_plan_classification_creation(self) -> None:
        """Test PlanClassification model creation."""
        classification = PlanClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.9,
            scope="system",
            impact="high",
        )
        assert classification.intent == IntentType.IMPLEMENT
        assert classification.confidence == 0.9

    def test_plan_spec_full_creation(self) -> None:
        """Test full PlanSpec creation."""
        metadata = PlanMetadata(
            phase_id="phase-45",
            title="Enhanced Planning System",
            author="test",
            created_date=datetime.utcnow(),
            estimated_duration="5 days",
            estimated_hours=18,
            test_target=100,
            roi_score=0.89,
            risk_level=RiskLevel.LOW_MEDIUM,
        )
        classification = PlanClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.92,
            scope="system",
            impact="high",
            handler="TDDOrchestrator",
        )
        overview = Overview(
            vision="A unified planning system",
            outcome="Production-grade plan lifecycle",
            success_criteria=["99% discovery rate"],
        )
        spec = PlanSpec(
            metadata=metadata,
            classification=classification,
            overview=overview,
        )
        assert spec.metadata.phase_id == "phase-45"
        assert spec.total_tests() == 0

    def test_plan_with_stages(self) -> None:
        """Test plan with stages."""
        metadata = PlanMetadata(
            phase_id="test",
            title="Test",
            author="test",
            created_date=datetime.utcnow(),
            estimated_duration="1 day",
            estimated_hours=5,
            test_target=10,
            roi_score=0.7,
            risk_level=RiskLevel.LOW,
        )
        classification = PlanClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.9,
            scope="module",
            impact="medium",
        )
        overview = Overview(
            vision="Test",
            outcome="Test outcome",
        )
        stage = PlanStage(
            stage_id="S1",
            stage_name="Foundation",
            stage_type=StageType.FOUNDATION,
            estimated_hours=5,
            test_count=10,
            description="Foundation stage",
        )
        spec = PlanSpec(
            metadata=metadata,
            classification=classification,
            overview=overview,
            stages=[stage],
        )
        assert len(spec.stages) == 1
        assert spec.total_tests() == 10
        assert spec.total_hours() == 5

    def test_plan_json_schema_generation(self) -> None:
        """Test JSON schema generation."""
        schema = PlanSpec.model_json_schema()
        assert "$defs" in schema or "definitions" in schema
        assert "properties" in schema

    def test_plan_status_enum(self) -> None:
        """Test PlanStatus enum values."""
        assert PlanStatus.PENDING.value == "pending"
        assert PlanStatus.APPROVED.value == "approved"
        assert PlanStatus.COMPLETED.value == "completed"

    def test_plan_summary_creation(self) -> None:
        """Test PlanSummary creation."""
        summary = PlanSummary(
            plan_id="phase-45",
            title="Test Plan",
            status="pending",
            priority="P0",
            roi_score=0.89,
        )
        assert summary.plan_id == "phase-45"
        dump = summary.model_dump()
        assert dump["plan_id"] == "phase-45"


class TestPlanRegistry:
    """Test plan registry operations."""

    @pytest.fixture
    def registry(self, tmp_path):
        """Create test registry."""
        return PlanRegistry(str(tmp_path / "planning"))

    @pytest.fixture
    def sample_plan(self) -> PlanSpec:
        """Create sample plan."""
        metadata = PlanMetadata(
            phase_id="test-plan-1",
            title="Test Plan",
            author="test",
            created_date=datetime.utcnow(),
            estimated_duration="1 day",
            estimated_hours=5,
            test_target=10,
            roi_score=0.75,
            risk_level=RiskLevel.LOW,
        )
        classification = PlanClassification(
            intent=IntentType.IMPLEMENT,
            confidence=0.9,
            scope="module",
            impact="medium",
        )
        overview = Overview(
            vision="Test vision",
            outcome="Test outcome",
        )
        return PlanSpec(
            metadata=metadata,
            classification=classification,
            overview=overview,
        )

    def test_registry_initialization(self, registry) -> None:
        """Test registry initialization."""
        assert registry.active_path.exists()
        assert registry.completed_path.exists()

    def test_create_plan(self, registry, sample_plan) -> None:
        """Test plan creation."""
        plan_id = registry.create_plan(sample_plan)
        assert plan_id == "test-plan-1"
        
        plan_file = registry.active_path / plan_id / "plan.yaml"
        assert plan_file.exists()

    def test_get_plan(self, registry, sample_plan) -> None:
        """Test retrieving plan."""
        registry.create_plan(sample_plan)
        retrieved = registry.get_plan("test-plan-1")
        assert retrieved.metadata.phase_id == "test-plan-1"
        assert retrieved.metadata.title == "Test Plan"

    def test_list_plans(self, registry, sample_plan) -> None:
        """Test listing plans."""
        registry.create_plan(sample_plan)
        plans = registry.list_plans()
        assert len(plans) == 1
        assert plans[0].plan_id == "test-plan-1"

    def test_list_plans_with_search(self, registry, sample_plan) -> None:
        """Test plan search."""
        registry.create_plan(sample_plan)
        results = registry.search_plans("Test")
        assert len(results) == 1
        
        no_results = registry.search_plans("NotFound")
        assert len(no_results) == 0

    def test_update_plan_status(self, registry, sample_plan) -> None:
        """Test updating plan status."""
        registry.create_plan(sample_plan)
        registry.update_plan_status("test-plan-1", "in_progress")
        
        plans = registry.list_plans()
        assert plans[0].status == "in_progress"

    def test_archive_plan(self, registry, sample_plan) -> None:
        """Test plan archival."""
        registry.create_plan(sample_plan)
        archive_path = registry.archive_plan("test-plan-1")
        
        assert "completed" in archive_path
        assert "test-plan-1" in archive_path
        
        active_plans = registry.list_plans()
        assert len(active_plans) == 0

    def test_generate_plans_json(self, registry, sample_plan, tmp_path) -> None:
        """Test JSON generation for viewer."""
        registry.create_plan(sample_plan)
        output_file = tmp_path / "plans.json"
        data = registry.generate_plans_json(str(output_file))
        
        assert data["total_plans"] == 1
        assert len(data["plans"]) == 1
        assert output_file.exists()

    def test_duplicate_plan_creation_fails(self, registry, sample_plan) -> None:
        """Test that duplicate plan creation fails."""
        registry.create_plan(sample_plan)
        with pytest.raises(ValueError):
            registry.create_plan(sample_plan)

    def test_get_nonexistent_plan_fails(self, registry) -> None:
        """Test retrieving non-existent plan fails."""
        with pytest.raises(FileNotFoundError):
            registry.get_plan("does-not-exist")
