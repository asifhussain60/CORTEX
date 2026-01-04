"""
CORTEX 5.0 Epic & Feature Planner - Comprehensive Test Suite

Purpose: Test dual-mode planning system components with TDD validation.

Version: 5.0.0
Author: Asif Hussain
Created: January 4, 2026

Test Coverage:
- Mode detection algorithm
- Epic planner functionality
- Feature planner functionality
- Dependency validation
- Progress calculation
- HTML viewer generation
- Integration layer
"""

import json
import pytest
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List

from src.orchestrators.planning.planner_mode_detector import (
    PlannerMode,
    detect_planner_mode,
    analyze_plan_structure,
    validate_epic_structure,
    validate_feature_structure
)
from src.orchestrators.planning.epic_planner import (
    EpicPlanner,
    ChildPlan,
    Milestone,
    Dependency,
    DependencyValidator,
    ProgressCalculator,
    PlanStatus,
    DependencyType
)
from src.orchestrators.planning.feature_planner import (
    FeaturePlanner,
    Phase,
    PhaseStatus
)
from src.orchestrators.planning.html_viewer_generator import (
    HTMLViewerGenerator,
    ViewerConfig,
    ViewerStyle
)
from src.orchestrators.planning.dual_mode_integration import (
    DualModePlanningOrchestrator,
    create_epic_plan,
    create_feature_plan
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def epic_structure(temp_dir):
    """Create epic plan directory structure."""
    epic_path = temp_dir / "test-epic"
    epic_path.mkdir()
    
    # Master plan
    (epic_path / "00-MASTER-EPIC-PLAN.md").write_text("# Master Epic Plan")
    
    # Tracking directory
    tracking = epic_path / "tracking"
    tracking.mkdir()
    
    # Child plans
    for i in range(2):
        child_folder = epic_path / f"0{i}-child-plan-{i}"
        child_folder.mkdir()
        (child_folder / f"00-child-plan-{i}.md").write_text(f"# Child Plan {i}")
        
        child_tracking = child_folder / "tracking"
        child_tracking.mkdir()
    
    return epic_path


@pytest.fixture
def feature_structure(temp_dir):
    """Create feature plan directory structure."""
    feature_path = temp_dir / "test-feature"
    feature_path.mkdir()
    
    # Master plan
    (feature_path / "00-test-feature.md").write_text("# Test Feature")
    
    # Standard folders
    (feature_path / "context").mkdir()
    (feature_path / "artifacts").mkdir()
    (feature_path / "reports").mkdir()
    
    tracking = feature_path / "tracking"
    tracking.mkdir()
    
    return feature_path


# ============================================================================
# MODE DETECTION TESTS
# ============================================================================

class TestModeDetection:
    """Test planner mode detection algorithm."""
    
    def test_detect_epic_mode(self, epic_structure):
        """Test detection of epic mode."""
        mode = detect_planner_mode(epic_structure)
        assert mode == PlannerMode.EPIC
    
    def test_detect_feature_mode(self, feature_structure):
        """Test detection of feature mode."""
        mode = detect_planner_mode(feature_structure)
        assert mode == PlannerMode.FEATURE
    
    def test_detect_unknown_mode(self, temp_dir):
        """Test detection of unknown/invalid structure."""
        invalid_path = temp_dir / "invalid"
        invalid_path.mkdir()
        mode = detect_planner_mode(invalid_path)
        assert mode == PlannerMode.UNKNOWN
    
    def test_analyze_plan_structure_epic(self, epic_structure):
        """Test detailed structure analysis for epic."""
        analysis = analyze_plan_structure(epic_structure)
        
        assert analysis["detected_mode"] == "epic"
        assert len(analysis["master_plans"]) == 1
        assert len(analysis["child_plans_with_master"]) >= 2
        assert analysis["tracking"]["has_tracking_dir"]
    
    def test_analyze_plan_structure_feature(self, feature_structure):
        """Test detailed structure analysis for feature."""
        analysis = analyze_plan_structure(feature_structure)
        
        assert analysis["detected_mode"] == "feature"
        assert len(analysis["master_plans"]) == 1
        assert analysis["standard_folders"]["context"]
        assert analysis["standard_folders"]["artifacts"]
    
    def test_validate_epic_structure(self, epic_structure):
        """Test epic structure validation."""
        # Add epic tracker for valid structure
        tracker_data = {
            "schema_version": "1.0",
            "plan_type": "epic",
            "plan_id": "test-epic",
            "plan_name": "Test Epic",
            "overall_progress": 0.0,
            "child_plans": []
        }
        tracker_file = epic_structure / "tracking" / "epic-progress-tracker.json"
        tracker_file.write_text(json.dumps(tracker_data))
        
        is_valid, errors = validate_epic_structure(epic_structure)
        assert is_valid
        assert len(errors) == 0
    
    def test_validate_feature_structure(self, feature_structure):
        """Test feature structure validation."""
        is_valid, errors = validate_feature_structure(feature_structure)
        assert is_valid
        assert len(errors) == 0


# ============================================================================
# EPIC PLANNER TESTS
# ============================================================================

class TestEpicPlanner:
    """Test epic planner functionality."""
    
    def test_initialize_epic_planner(self, epic_structure):
        """Test epic planner initialization."""
        planner = EpicPlanner(epic_structure)
        
        assert planner.epic_path == epic_structure
        assert planner.tracker is not None
        assert planner.tracker.plan_type == "epic"
    
    def test_add_child_plan(self, epic_structure):
        """Test adding child plans."""
        planner = EpicPlanner(epic_structure)
        
        child = ChildPlan(
            order="00",
            id="test-child",
            name="Test Child Plan",
            folder="00-test-child/",
            total_phases=5,
            duration="1w"
        )
        
        planner.add_child_plan(child)
        
        assert len(planner.tracker.child_plans) == 1
        assert planner.tracker.total_plans == 1
        assert planner.tracker.child_plans[0].id == "test-child"
    
    def test_add_duplicate_child_plan(self, epic_structure):
        """Test prevention of duplicate child plans."""
        planner = EpicPlanner(epic_structure)
        
        child1 = ChildPlan(order="00", id="test-child", name="Test 1", folder="00-test/")
        child2 = ChildPlan(order="00", id="different", name="Test 2", folder="01-test/")
        
        planner.add_child_plan(child1)
        
        with pytest.raises(ValueError, match="already exists"):
            planner.add_child_plan(child2)
    
    def test_update_child_plan_progress(self, epic_structure):
        """Test updating child plan progress."""
        planner = EpicPlanner(epic_structure)
        
        child = ChildPlan(order="00", id="test-child", name="Test", folder="00-test/")
        planner.add_child_plan(child)
        
        planner.update_child_plan_progress("test-child", 50.0, phases_complete=3)
        
        updated_child = planner._get_child_plan("test-child")
        assert updated_child.progress == 50.0
        assert updated_child.phases_complete == 3
        assert updated_child.status == PlanStatus.IN_PROGRESS
    
    def test_complete_child_plan(self, epic_structure):
        """Test completing a child plan."""
        planner = EpicPlanner(epic_structure)
        
        child = ChildPlan(order="00", id="test-child", name="Test", folder="00-test/")
        planner.add_child_plan(child)
        
        planner.mark_plan_complete("test-child")
        
        updated_child = planner._get_child_plan("test-child")
        assert updated_child.progress == 100.0
        assert updated_child.status == PlanStatus.COMPLETE
        assert updated_child.end_date is not None
    
    def test_aggregate_progress_calculation(self, epic_structure):
        """Test aggregate progress calculation."""
        planner = EpicPlanner(epic_structure)
        
        child1 = ChildPlan(order="00", id="child1", name="Child 1", folder="00-/")
        child2 = ChildPlan(order="01", id="child2", name="Child 2", folder="01-/")
        
        planner.add_child_plan(child1)
        planner.add_child_plan(child2)
        
        planner.update_child_plan_progress("child1", 50.0)
        planner.update_child_plan_progress("child2", 30.0)
        
        assert planner.tracker.overall_progress == 40.0  # (50 + 30) / 2


# ============================================================================
# DEPENDENCY VALIDATION TESTS
# ============================================================================

class TestDependencyValidation:
    """Test dependency validation system."""
    
    def test_validate_satisfied_dependencies(self):
        """Test validation of satisfied dependencies."""
        child1 = ChildPlan(order="00", id="child1", name="Child 1", folder="00-/",
                          status=PlanStatus.COMPLETE)
        child2 = ChildPlan(order="01", id="child2", name="Child 2", folder="01-/",
                          dependencies=["child1"])
        
        validator = DependencyValidator([child1, child2])
        is_satisfied, unsatisfied = validator.validate_dependencies("child2")
        
        assert is_satisfied
        assert len(unsatisfied) == 0
    
    def test_validate_unsatisfied_dependencies(self):
        """Test validation of unsatisfied dependencies."""
        child1 = ChildPlan(order="00", id="child1", name="Child 1", folder="00-/",
                          status=PlanStatus.IN_PROGRESS)
        child2 = ChildPlan(order="01", id="child2", name="Child 2", folder="01-/",
                          dependencies=["child1"])
        
        validator = DependencyValidator([child1, child2])
        is_satisfied, unsatisfied = validator.validate_dependencies("child2")
        
        assert not is_satisfied
        assert len(unsatisfied) > 0
    
    def test_detect_circular_dependencies(self):
        """Test detection of circular dependency chains."""
        child1 = ChildPlan(order="00", id="child1", name="Child 1", folder="00-/",
                          dependencies=["child2"])
        child2 = ChildPlan(order="01", id="child2", name="Child 2", folder="01-/",
                          dependencies=["child1"])
        
        validator = DependencyValidator([child1, child2])
        cycles = validator.detect_circular_dependencies()
        
        assert len(cycles) > 0
    
    def test_get_ready_plans(self):
        """Test getting list of plans ready to start."""
        child1 = ChildPlan(order="00", id="child1", name="Child 1", folder="00-/",
                          status=PlanStatus.COMPLETE)
        child2 = ChildPlan(order="01", id="child2", name="Child 2", folder="01-/",
                          dependencies=["child1"], status=PlanStatus.NOT_STARTED)
        child3 = ChildPlan(order="02", id="child3", name="Child 3", folder="02-/",
                          dependencies=["child2"], status=PlanStatus.NOT_STARTED)
        
        validator = DependencyValidator([child1, child2, child3])
        ready = validator.get_ready_plans()
        
        assert "child2" in ready
        assert "child3" not in ready  # Blocked by child2


# ============================================================================
# FEATURE PLANNER TESTS
# ============================================================================

class TestFeaturePlanner:
    """Test feature planner functionality."""
    
    def test_initialize_feature_planner(self, feature_structure):
        """Test feature planner initialization."""
        planner = FeaturePlanner(feature_structure)
        
        assert planner.feature_path == feature_structure
        assert planner.tracker is not None
        assert planner.tracker.plan_type == "feature"
    
    def test_add_phase(self, feature_structure):
        """Test adding phases."""
        planner = FeaturePlanner(feature_structure)
        
        phase = Phase(
            phase_number=0,
            phase_name="Phase 0: Planning",
            estimated_hours=8.0,
            total_tasks=5
        )
        
        planner.add_phase(phase)
        
        assert len(planner.tracker.phases) == 1
        assert planner.tracker.total_phases == 1
        assert planner.tracker.estimated_hours == 8.0
    
    def test_update_phase_progress(self, feature_structure):
        """Test updating phase progress."""
        planner = FeaturePlanner(feature_structure)
        
        phase = Phase(phase_number=0, phase_name="Test Phase", total_tasks=10)
        planner.add_phase(phase)
        
        planner.update_phase_progress(0, 60.0, tasks_complete=6, actual_hours=5.0)
        
        updated_phase = planner._get_phase(0)
        assert updated_phase.progress == 60.0
        assert updated_phase.tasks_complete == 6
        assert updated_phase.actual_hours == 5.0
        assert updated_phase.status == PhaseStatus.IN_PROGRESS
    
    def test_complete_phase(self, feature_structure):
        """Test completing a phase."""
        planner = FeaturePlanner(feature_structure)
        
        phase = Phase(phase_number=0, phase_name="Test Phase")
        planner.add_phase(phase)
        
        planner.complete_phase(0)
        
        updated_phase = planner._get_phase(0)
        assert updated_phase.progress == 100.0
        assert updated_phase.status == PhaseStatus.COMPLETE
        assert updated_phase.end_date is not None
    
    def test_get_next_phase(self, feature_structure):
        """Test getting next phase to execute."""
        planner = FeaturePlanner(feature_structure)
        
        phase0 = Phase(phase_number=0, phase_name="Phase 0", status=PhaseStatus.COMPLETE)
        phase1 = Phase(phase_number=1, phase_name="Phase 1", status=PhaseStatus.NOT_STARTED)
        phase2 = Phase(phase_number=2, phase_name="Phase 2", status=PhaseStatus.NOT_STARTED)
        
        planner.add_phase(phase0)
        planner.add_phase(phase1)
        planner.add_phase(phase2)
        
        next_phase = planner.get_next_phase()
        
        assert next_phase is not None
        assert next_phase.phase_number == 1


# ============================================================================
# HTML VIEWER GENERATION TESTS
# ============================================================================

class TestHTMLViewerGeneration:
    """Test HTML viewer generator."""
    
    def test_generate_epic_viewer(self, temp_dir):
        """Test generating epic HTML viewer."""
        tracker_data = {
            "plan_name": "Test Epic",
            "plan_id": "test-epic",
            "overall_progress": 45.0,
            "total_plans": 3,
            "completed_plans": 1,
            "total_phases": 15,
            "completed_phases": 7,
            "estimated_days": 30,
            "child_plans": [],
            "milestones": []
        }
        
        config = ViewerConfig(
            plan_name="Test Epic",
            plan_type="epic",
            tracker_path="tracking/epic-progress-tracker.json"
        )
        
        generator = HTMLViewerGenerator(config)
        output_path = temp_dir / "test-epic-viewer.html"
        
        generator.generate(tracker_data, output_path)
        
        assert output_path.exists()
        html_content = output_path.read_text()
        assert "Test Epic" in html_content
        assert "Auto-refreshing" in html_content
        assert "glassmorphism" in html_content.lower() or "glass" in html_content.lower()
    
    def test_generate_feature_viewer(self, temp_dir):
        """Test generating feature HTML viewer."""
        tracker_data = {
            "plan_name": "Test Feature",
            "plan_id": "test-feature",
            "overall_progress": 60.0,
            "current_phase": 2,
            "total_phases": 5,
            "completed_phases": 2,
            "actual_hours": 15.5,
            "phases": []
        }
        
        config = ViewerConfig(
            plan_name="Test Feature",
            plan_type="feature",
            tracker_path="tracking/progress-tracker.json"
        )
        
        generator = HTMLViewerGenerator(config)
        output_path = temp_dir / "test-feature-viewer.html"
        
        generator.generate(tracker_data, output_path)
        
        assert output_path.exists()
        html_content = output_path.read_text()
        assert "Test Feature" in html_content
        assert "Phase 2" in html_content or "current_phase" in html_content.lower()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestDualModeIntegration:
    """Test dual-mode integration layer."""
    
    def test_create_epic_plan(self, temp_dir):
        """Test epic plan creation via integration layer."""
        epic_path = temp_dir / "integration-epic"
        
        child_plans = [
            {
                "order": "00",
                "id": "child-plan-1",
                "name": "Child Plan 1",
                "folder": "00-child-plan-1/",
                "total_phases": 4,
                "duration": "1w"
            },
            {
                "order": "01",
                "id": "child-plan-2",
                "name": "Child Plan 2",
                "folder": "01-child-plan-2/",
                "total_phases": 3,
                "duration": "3d",
                "dependencies": ["child-plan-1"]
            }
        ]
        
        orchestrator = create_epic_plan(
            epic_path,
            "Integration Test Epic",
            "integration-epic",
            child_plans
        )
        
        assert orchestrator.get_mode() == PlannerMode.EPIC
        assert (epic_path / "integration-epic-plan-viewer.html").exists()
    
    def test_create_feature_plan(self, temp_dir):
        """Test feature plan creation via integration layer."""
        feature_path = temp_dir / "integration-feature"
        
        phases = [
            {"phase_number": 0, "phase_name": "Planning", "estimated_hours": 8.0, "total_tasks": 5},
            {"phase_number": 1, "phase_name": "Implementation", "estimated_hours": 16.0, "total_tasks": 10},
            {"phase_number": 2, "phase_name": "Testing", "estimated_hours": 8.0, "total_tasks": 8}
        ]
        
        orchestrator = create_feature_plan(
            feature_path,
            "Integration Test Feature",
            "integration-feature",
            phases
        )
        
        assert orchestrator.get_mode() == PlannerMode.FEATURE
        assert (feature_path / "integration-feature-plan-viewer.html").exists()
    
    def test_dual_mode_orchestrator_epic(self, epic_structure):
        """Test dual-mode orchestrator with epic plan."""
        # Setup epic tracker
        tracker_data = {
            "schema_version": "1.0",
            "plan_type": "epic",
            "plan_id": "test-epic",
            "plan_name": "Test Epic",
            "overall_progress": 0.0,
            "total_plans": 0,
            "completed_plans": 0,
            "total_phases": 0,
            "completed_phases": 0,
            "estimated_days": 0,
            "status": "not_started",
            "child_plans": [],
            "milestones": [],
            "dependencies": []
        }
        tracker_file = epic_structure / "tracking" / "epic-progress-tracker.json"
        tracker_file.write_text(json.dumps(tracker_data))
        
        orchestrator = DualModePlanningOrchestrator(epic_structure)
        
        assert orchestrator.get_mode() == PlannerMode.EPIC
        summary = orchestrator.get_progress_summary()
        assert summary["mode"] == "epic"
    
    def test_dual_mode_orchestrator_feature(self, feature_structure):
        """Test dual-mode orchestrator with feature plan."""
        orchestrator = DualModePlanningOrchestrator(feature_structure)
        
        assert orchestrator.get_mode() == PlannerMode.FEATURE
        summary = orchestrator.get_progress_summary()
        assert summary["mode"] == "feature"


# ============================================================================
# PROGRESS CALCULATOR TESTS
# ============================================================================

class TestProgressCalculator:
    """Test progress calculation utilities."""
    
    def test_calculate_overall_progress(self):
        """Test overall progress calculation."""
        plans = [
            ChildPlan(order="00", id="p1", name="P1", folder="00-/", progress=50.0),
            ChildPlan(order="01", id="p2", name="P2", folder="01-/", progress=75.0),
            ChildPlan(order="02", id="p3", name="P3", folder="02-/", progress=25.0)
        ]
        
        progress = ProgressCalculator.calculate_overall_progress(plans)
        assert progress == 50.0  # (50 + 75 + 25) / 3
    
    def test_calculate_phase_totals(self):
        """Test phase totals calculation."""
        plans = [
            ChildPlan(order="00", id="p1", name="P1", folder="00-/", 
                     total_phases=5, phases_complete=3),
            ChildPlan(order="01", id="p2", name="P2", folder="01-/",
                     total_phases=4, phases_complete=2)
        ]
        
        total, completed = ProgressCalculator.calculate_phase_totals(plans)
        assert total == 9
        assert completed == 5
    
    def test_determine_epic_status(self):
        """Test epic status determination."""
        # All complete
        complete_plans = [
            ChildPlan(order="00", id="p1", name="P1", folder="00-/", 
                     status=PlanStatus.COMPLETE),
            ChildPlan(order="01", id="p2", name="P2", folder="01-/",
                     status=PlanStatus.COMPLETE)
        ]
        assert ProgressCalculator.determine_epic_status(complete_plans) == PlanStatus.COMPLETE
        
        # In progress
        in_progress_plans = [
            ChildPlan(order="00", id="p1", name="P1", folder="00-/",
                     status=PlanStatus.COMPLETE),
            ChildPlan(order="01", id="p2", name="P2", folder="01-/",
                     status=PlanStatus.IN_PROGRESS)
        ]
        assert ProgressCalculator.determine_epic_status(in_progress_plans) == PlanStatus.IN_PROGRESS


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short", "--cov=src.orchestrators.planning", 
                 "--cov-report=term-missing"])
