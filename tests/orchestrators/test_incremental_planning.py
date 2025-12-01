"""
Test suite for Phase 4: Incremental Planning System
Following TDD Mastery workflow (RED → GREEN → REFACTOR)

Tests for:
- Deliverable 4.1: Incremental plan generation
- Deliverable 4.2: Progress visualization 
- Deliverable 4.3: Incremental validation

Author: Asif Hussain
Created: 2025-12-01
"""

import pytest
from pathlib import Path
from datetime import datetime
import time
from src.orchestrators.planning_orchestrator import PlanningOrchestrator
from src.utils.incremental_writer import IncrementalWriter


# Module-level fixture accessible by all test classes
@pytest.fixture
def planning_orchestrator(tmp_path):
    """Create planning orchestrator with temp directory."""
    cortex_root = tmp_path / "CORTEX"
    cortex_root.mkdir()
    
    # Create required directories
    brain_path = cortex_root / "cortex-brain"
    brain_path.mkdir()
    
    plans_dir = brain_path / "documents" / "planning" / "features"
    plans_dir.mkdir(parents=True)
    
    (plans_dir / "active").mkdir()
    (plans_dir / "completed").mkdir()
    
    # Create minimal schema
    schema_dir = brain_path / "config"
    schema_dir.mkdir(parents=True)
    schema_path = schema_dir / "plan-schema.yaml"
    schema_path.write_text("schema:\n  version: '1.0.0'\n")
    
    return PlanningOrchestrator(str(cortex_root))


class TestIncrementalPlanGeneration:
    """Test Deliverable 4.1: Incremental Plan Generation"""
    
    def test_create_empty_plan_file_first(self, planning_orchestrator, tmp_path):
        """
        RED TEST: Step 1 - Create empty plan file with metadata only
        
        Acceptance Criteria:
        - Empty plan file created before phase generation
        - File contains metadata section (name, timestamp, status)
        - File contains phase headers but no phase content
        - File size < 1KB (minimal content)
        """
        # Arrange
        feature_name = "user_authentication"
        
        # Act
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        # Assert
        assert plan_path.exists(), "Empty plan file should be created"
        
        content = plan_path.read_text()
        assert "metadata:" in content, "Should contain metadata section"
        assert "name:" in content, "Should contain feature name"
        assert "created_at:" in content, "Should contain timestamp"
        assert "status: planning" in content, "Should have planning status"
        assert "phases:" in content, "Should have phases header"
        
        # Verify minimal size (empty file)
        assert len(content) < 1024, "Empty plan should be < 1KB"
        
        # Verify no phase content yet
        assert "Phase 1:" not in content, "Should not contain phase content yet"
    
    def test_add_phases_incrementally(self, planning_orchestrator, tmp_path):
        """
        RED TEST: Step 2 - Add phases one at a time
        
        Acceptance Criteria:
        - Each phase added separately with progress update
        - File updates after each phase addition
        - Phase count increases incrementally
        """
        # Arrange
        feature_name = "payment_processing"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        phases = [
            {"phase_id": 1, "name": "Requirements Analysis", "tasks": ["Task 1"]},
            {"phase_id": 2, "name": "Implementation", "tasks": ["Task 2"]},
            {"phase_id": 3, "name": "Testing", "tasks": ["Task 3"]}
        ]
        
        # Act & Assert
        for idx, phase in enumerate(phases, 1):
            result = planning_orchestrator.add_phase_to_plan(plan_path, phase)
            
            assert result["success"], f"Phase {idx} should be added successfully"
            assert result["phase_number"] == idx, f"Should be phase {idx}"
            assert result["total_phases"] == idx, f"Total should be {idx}"
            
            # Verify file updated
            content = plan_path.read_text()
            assert f"phase_id: {idx}" in content, f"Phase {idx} should be in file"
            
            # Verify previous phases still present
            for prev_idx in range(1, idx):
                assert f"phase_id: {prev_idx}" in content, f"Phase {prev_idx} should still be present"
    
    def test_show_progress_after_each_phase(self, planning_orchestrator, tmp_path):
        """
        RED TEST: Step 3 - Show progress message after each phase
        
        Acceptance Criteria:
        - Progress message format: "Phase X/Y added"
        - Percentage shown after each phase
        """
        # Arrange
        feature_name = "api_integration"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        phases = [
            {"phase_id": 1, "name": "Phase 1"},
            {"phase_id": 2, "name": "Phase 2"},
            {"phase_id": 3, "name": "Phase 3"}
        ]
        
        # Act & Assert
        for idx, phase in enumerate(phases, 1):
            result = planning_orchestrator.add_phase_to_plan(plan_path, phase)
            
            expected_message = f"Phase {idx}/{len(phases)} added"
            assert expected_message in result["message"], f"Should show progress message"
            
            expected_percentage = int((idx / len(phases)) * 100)
            assert result["percentage"] == expected_percentage, f"Should show {expected_percentage}%"
    
    def test_plan_resumable_after_interruption(self, planning_orchestrator, tmp_path):
        """
        RED TEST: Plans should be resumable if interrupted
        
        Acceptance Criteria:
        - Check existing file for last phase
        - Continue from next phase number
        - Don't duplicate phases
        """
        # Arrange
        feature_name = "notification_system"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        # Add first 2 phases
        planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 1, "name": "Phase 1"})
        planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 2, "name": "Phase 2"})
        
        # Simulate interruption - get last phase
        last_phase = planning_orchestrator.get_last_phase_number(plan_path)
        assert last_phase == 2, "Should detect 2 phases already added"
        
        # Act - Resume adding phases
        result = planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 3, "name": "Phase 3"})
        
        # Assert
        assert result["success"], "Should resume successfully"
        assert result["phase_number"] == 3, "Should add phase 3"
        
        content = plan_path.read_text()
        phase_count = content.count("phase_id:")
        assert phase_count == 3, "Should have exactly 3 phases (no duplicates)"


class TestProgressVisualization:
    """Test Deliverable 4.2: Progress Visualization for Planning"""
    
    def test_progress_decorator_shows_phase_progress(self, planning_orchestrator, tmp_path):
        """
        RED TEST: Progress decorator shows real-time progress
        
        Acceptance Criteria:
        - Progress format: "Planning: Phase 3/7 (43% complete, ETA 2m 15s)"
        - Updates after each phase
        """
        # Arrange
        feature_name = "data_migration"
        total_phases = 7
        
        # Act - Generate plan with progress tracking
        with planning_orchestrator.track_progress(feature_name, total_phases) as tracker:
            for phase_num in range(1, total_phases + 1):
                tracker.update_phase(phase_num)
                
                # Assert
                status = tracker.get_status()
                assert status["current_phase"] == phase_num
                assert status["total_phases"] == total_phases
                assert status["percentage"] == int((phase_num / total_phases) * 100)
                assert "ETA" in status["message"], "Should show ETA"
    
    def test_hang_detection_if_phase_takes_too_long(self, planning_orchestrator):
        """
        RED TEST: Hang detection if phase takes >5x expected time
        
        Acceptance Criteria:
        - Warn if phase exceeds 5x expected duration
        - Don't block operation, just warn
        """
        # Arrange
        expected_time = 1  # 1 second per phase
        
        # Act - Simulate slow phase (>5 seconds)
        with planning_orchestrator.track_progress("slow_feature", 1) as tracker:
            tracker.set_expected_phase_time(expected_time)
            
            # Simulate 6 second delay (>5x expected)
            tracker.start_phase(1)
            time.sleep(6)
            
            # Assert
            status = tracker.get_status()
            assert status["hang_detected"], "Should detect hang"
            assert "taking longer than expected" in status["warning"], "Should show warning"
    
    def test_cancel_without_losing_work(self, planning_orchestrator, tmp_path):
        """
        RED TEST: User can cancel without losing partial plan
        
        Acceptance Criteria:
        - Partial plan saved to disk
        - Can resume from cancellation point
        """
        # Arrange
        feature_name = "user_registration"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        # Act - Add 3 phases then cancel
        planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 1, "name": "Phase 1"})
        planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 2, "name": "Phase 2"})
        planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 3, "name": "Phase 3"})
        
        # Simulate cancellation
        planning_orchestrator.cancel_planning(plan_path)
        
        # Assert - Partial work saved
        assert plan_path.exists(), "Partial plan should be saved"
        content = plan_path.read_text()
        assert "phase_id: 1" in content, "Phase 1 should be saved"
        assert "phase_id: 2" in content, "Phase 2 should be saved"
        assert "phase_id: 3" in content, "Phase 3 should be saved"
        
        # Verify can resume
        last_phase = planning_orchestrator.get_last_phase_number(plan_path)
        assert last_phase == 3, "Should detect 3 phases saved"


class TestIncrementalValidation:
    """Test Deliverable 4.3: Plan Validation During Generation"""
    
    def test_yaml_schema_validated_after_each_phase(self, planning_orchestrator, tmp_path):
        """
        RED TEST: YAML schema validated incrementally
        
        Acceptance Criteria:
        - Schema check after each phase added
        - Invalid phase rejected immediately
        - Generation continues after rejection
        """
        # Arrange
        feature_name = "schema_validation"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        valid_phase = {"phase_id": 1, "name": "Valid Phase", "tasks": ["Task 1"]}
        invalid_phase = {"name": "Missing ID"}  # No phase_id
        
        # Act - Add valid phase
        result1 = planning_orchestrator.add_phase_to_plan(plan_path, valid_phase)
        assert result1["success"], "Valid phase should be accepted"
        
        # Act - Add invalid phase
        result2 = planning_orchestrator.add_phase_to_plan(plan_path, invalid_phase)
        
        # Assert
        assert not result2["success"], "Invalid phase should be rejected"
        assert "schema validation failed" in result2["error"].lower()
        
        # Verify only valid phase in file
        content = plan_path.read_text()
        assert "phase_id: 1" in content, "Valid phase should be present"
        assert content.count("phase_id:") == 1, "Invalid phase should not be added"
    
    def test_dor_dod_validation_runs_incrementally(self, planning_orchestrator, tmp_path):
        """
        RED TEST: DoR/DoD validation per phase
        
        Acceptance Criteria:
        - Check DoR criteria as phases added
        - Warn if criteria not met
        - Track completion percentage
        """
        # Arrange
        feature_name = "dor_validation"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        phase_with_dor = {
            "phase_id": 1,
            "name": "Requirements Phase",
            "dor_criteria": [
                {"criterion": "Requirements documented", "met": True},
                {"criterion": "Dependencies identified", "met": False}
            ]
        }
        
        # Act
        result = planning_orchestrator.add_phase_to_plan(plan_path, phase_with_dor)
        
        # Assert
        assert result["success"], "Phase should be added"
        assert result["dor_validation"], "Should include DoR validation"
        assert result["dor_validation"]["percentage"] == 50, "Should show 50% complete (1/2)"
        assert result["dor_validation"]["incomplete_criteria"] == ["Dependencies identified"]
    
    def test_errors_reported_immediately(self, planning_orchestrator, tmp_path):
        """
        RED TEST: Errors reported immediately, not after all phases
        
        Acceptance Criteria:
        - Error returned on add_phase_to_plan() call
        - Error includes line number and field name
        - Subsequent phases can still be added
        """
        # Arrange
        feature_name = "error_reporting"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        # Act - Add phase with error
        invalid_phase = {"phase_id": "invalid", "name": 123}  # Wrong types
        result = planning_orchestrator.add_phase_to_plan(plan_path, invalid_phase)
        
        # Assert
        assert not result["success"], "Should report failure"
        assert "validation_errors" in result
        assert any("phase_id" in err for err in result["validation_errors"])
        assert any("name" in err for err in result["validation_errors"])
        
        # Verify next phase can be added
        valid_phase = {"phase_id": 1, "name": "Valid Phase"}
        result2 = planning_orchestrator.add_phase_to_plan(plan_path, valid_phase)
        assert result2["success"], "Subsequent valid phases should work"
    
    def test_invalid_phase_discarded_generation_continues(self, planning_orchestrator, tmp_path):
        """
        RED TEST: Invalid phase discarded, generation continues
        
        Acceptance Criteria:
        - Invalid phase not written to file
        - Phase count doesn't increment for invalid phase
        - Next phase uses correct phase number
        """
        # Arrange
        feature_name = "discard_invalid"
        plan_path = planning_orchestrator.create_empty_plan(feature_name)
        
        # Add valid phase 1
        planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 1, "name": "Phase 1"})
        
        # Try invalid phase (should be discarded)
        invalid_result = planning_orchestrator.add_phase_to_plan(plan_path, {"invalid": "data"})
        assert not invalid_result["success"]
        
        # Add valid phase 2
        result = planning_orchestrator.add_phase_to_plan(plan_path, {"phase_id": 2, "name": "Phase 2"})
        
        # Assert
        assert result["success"]
        assert result["phase_number"] == 2, "Should be phase 2 (skipped invalid)"
        
        content = plan_path.read_text()
        assert content.count("phase_id:") == 2, "Should have exactly 2 phases"


class TestIncrementalWriter:
    """Test IncrementalWriter utility class"""
    
    def test_incremental_writer_create_empty_file(self, tmp_path):
        """
        RED TEST: IncrementalWriter.create_empty()
        
        Creates file with minimal content
        """
        # Arrange
        file_path = tmp_path / "test_plan.yaml"
        writer = IncrementalWriter(file_path)
        
        # Act
        writer.create_empty(
            metadata={"name": "test_feature", "status": "planning"}
        )
        
        # Assert
        assert file_path.exists()
        content = file_path.read_text()
        assert "metadata:" in content
        assert "name: test_feature" in content
        assert len(content) < 512, "Should be minimal content"
    
    def test_incremental_writer_append_section(self, tmp_path):
        """
        RED TEST: IncrementalWriter.append_section()
        
        Appends content without rewriting entire file
        """
        # Arrange
        file_path = tmp_path / "test_plan.yaml"
        writer = IncrementalWriter(file_path)
        writer.create_empty(metadata={"name": "test"})
        
        # Act
        writer.append_section(
            section_name="phases",
            content="  - phase_id: 1\n    name: Phase 1\n"
        )
        
        # Assert
        content = file_path.read_text()
        assert "phases:" in content
        assert "phase_id: 1" in content
        assert "name: Phase 1" in content
    
    def test_incremental_writer_get_last_section(self, tmp_path):
        """
        RED TEST: IncrementalWriter.get_last_section()
        
        Reads file to find last completed section
        """
        # Arrange
        file_path = tmp_path / "test_plan.yaml"
        writer = IncrementalWriter(file_path)
        writer.create_empty(metadata={"name": "test"})
        writer.append_section("phases", "  - phase_id: 1\n")
        writer.append_section("phases", "  - phase_id: 2\n")
        
        # Act
        last_phase = writer.get_last_section_count("phases")
        
        # Assert
        assert last_phase == 2, "Should detect 2 phases"
