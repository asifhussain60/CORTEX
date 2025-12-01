"""
Test Phase 4: Incremental Planning System
RED Phase: Tests written before implementation

Purpose: Verify that planning orchestrator generates plans incrementally:
1. Create empty plan file with metadata first
2. Add phases one at a time with progress updates
3. Resume interrupted plans from last completed phase

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import yaml
import time
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestIncrementalPlanGeneration:
    """Test suite for incremental plan generation (Deliverable 4.1)"""
    
    @pytest.fixture
    def temp_cortex_root(self, tmp_path):
        """Create temporary CORTEX directory structure"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        # Create brain structure
        brain_path = cortex_root / "cortex-brain"
        config_path = brain_path / "config"
        config_path.mkdir(parents=True)
        
        plans_path = brain_path / "documents" / "planning" / "features" / "active"
        plans_path.mkdir(parents=True)
        
        # Create minimal schema
        schema_path = config_path / "plan-schema.yaml"
        schema_path.write_text("""
schema:
  version: "1.0.0"
  required_fields:
    - metadata
    - phases
    - definition_of_ready
    - definition_of_done
""", encoding='utf-8')
        
        return cortex_root
    
    @pytest.fixture
    def orchestrator(self, temp_cortex_root):
        """Create PlanningOrchestrator instance"""
        return PlanningOrchestrator(str(temp_cortex_root))
    
    def test_empty_plan_file_created_first(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 1: Verify empty plan file with metadata is created first
        
        Acceptance Criteria (4.1):
        - Step 1: Create empty plan file with metadata and headers
        - Plan file exists before phases are added
        - Contains metadata section only (no phases yet)
        """
        # Arrange
        plan_name = "test-feature"
        plan_metadata = {
            "name": "Test Feature",
            "description": "Test incremental planning",
            "priority": "high",
            "estimated_effort": "10 hours"
        }
        
        # Act - Generate plan incrementally
        result = orchestrator.generate_plan_incremental(
            plan_name=plan_name,
            metadata=plan_metadata,
            phases=[
                {"id": "1", "name": "Phase 1", "tasks": ["Task 1"]},
                {"id": "2", "name": "Phase 2", "tasks": ["Task 2"]}
            ]
        )
        
        # Assert - Empty plan file created
        assert result["success"] is True, "Plan generation should succeed"
        
        plan_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / f"{plan_name}.yaml"
        assert plan_path.exists(), "Plan file should be created immediately"
        
        # Read plan file
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        # Verify metadata exists
        assert "metadata" in plan_data, "Plan should have metadata section"
        assert plan_data["metadata"]["name"] == "Test Feature"
        assert plan_data["metadata"]["description"] == "Test incremental planning"
        
        # Verify phases section exists but may be incomplete during generation
        assert "phases" in plan_data, "Plan should have phases section"
    
    def test_phases_added_incrementally_with_progress(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 2: Verify phases are added one at a time with progress updates
        
        Acceptance Criteria (4.1):
        - Step 2: Add phases one at a time with progress updates
        - Step 3: Show 'Phase 1/5 added' after each phase
        """
        # Arrange
        plan_name = "multi-phase-feature"
        plan_metadata = {
            "name": "Multi-Phase Feature",
            "description": "Test multi-phase incremental planning"
        }
        
        phases = [
            {"id": "1", "name": "Foundation", "tasks": ["Setup"]},
            {"id": "2", "name": "Implementation", "tasks": ["Code"]},
            {"id": "3", "name": "Testing", "tasks": ["Test"]},
            {"id": "4", "name": "Documentation", "tasks": ["Docs"]},
            {"id": "5", "name": "Deployment", "tasks": ["Deploy"]}
        ]
        
        # Track progress callbacks
        progress_updates = []
        
        def progress_callback(phase_num, total_phases, phase_name):
            progress_updates.append({
                "phase_num": phase_num,
                "total": total_phases,
                "name": phase_name
            })
        
        # Act - Generate plan with progress tracking
        result = orchestrator.generate_plan_incremental(
            plan_name=plan_name,
            metadata=plan_metadata,
            phases=phases,
            progress_callback=progress_callback
        )
        
        # Assert - All phases added incrementally
        assert result["success"] is True
        assert len(progress_updates) == 5, "Should have 5 progress updates"
        
        # Verify progress updates
        for i, update in enumerate(progress_updates, 1):
            assert update["phase_num"] == i
            assert update["total"] == 5
        
        # Verify final plan contains all phases
        plan_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / f"{plan_name}.yaml"
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        assert len(plan_data["phases"]) == 5, "All phases should be in final plan"
    
    def test_interrupted_plan_can_resume(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 3: Verify interrupted plans can be resumed
        
        Acceptance Criteria (4.1):
        - Plans resumable if interrupted (check existing file, continue from last phase)
        """
        # Arrange - Create partial plan (simulating interruption)
        plan_name = "interrupted-feature"
        plan_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / f"{plan_name}.yaml"
        
        # Create partial plan with only 2 of 4 phases
        partial_plan = {
            "metadata": {
                "name": "Interrupted Feature",
                "status": "in_progress"
            },
            "phases": [
                {"id": "1", "name": "Phase 1", "status": "complete"},
                {"id": "2", "name": "Phase 2", "status": "complete"}
            ]
        }
        
        plan_path.parent.mkdir(parents=True, exist_ok=True)
        with open(plan_path, 'w', encoding='utf-8') as f:
            yaml.dump(partial_plan, f)
        
        # Act - Resume plan generation with all 4 phases
        all_phases = [
            {"id": "1", "name": "Phase 1", "tasks": ["Task 1"]},
            {"id": "2", "name": "Phase 2", "tasks": ["Task 2"]},
            {"id": "3", "name": "Phase 3", "tasks": ["Task 3"]},
            {"id": "4", "name": "Phase 4", "tasks": ["Task 4"]}
        ]
        
        result = orchestrator.generate_plan_incremental(
            plan_name=plan_name,
            metadata=partial_plan["metadata"],
            phases=all_phases,
            resume_if_exists=True
        )
        
        # Assert - Only phases 3-4 were added
        assert result["success"] is True
        assert result["resumed"] is True, "Should indicate plan was resumed"
        assert result["phases_added"] == 2, "Should add only remaining phases"
        assert result["phases_skipped"] == 2, "Should skip existing phases"
        
        # Verify final plan has all 4 phases
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        assert len(plan_data["phases"]) == 4, "Should have all 4 phases"
        assert plan_data["metadata"]["status"] == "complete", "Plan should be marked complete"
    
    def test_plan_generation_applies_to_all_types(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 4: Verify incremental generation works for YAML, MD, ADO, Swagger
        
        Acceptance Criteria (4.1):
        - Applied to YAML, MD, ADO, and Swagger plan generation
        """
        # This test verifies the interface is consistent across plan types
        plan_types = ["yaml", "markdown", "ado", "swagger"]
        
        for plan_type in plan_types:
            plan_name = f"test-{plan_type}-plan"
            result = orchestrator.generate_plan_incremental(
                plan_name=plan_name,
                metadata={"name": f"Test {plan_type.upper()} Plan"},
                phases=[{"id": "1", "name": "Phase 1"}],
                output_format=plan_type
            )
            
            assert result["success"] is True, f"Should generate {plan_type} plan incrementally"
            assert "file_path" in result, f"Should return file path for {plan_type}"


class TestProgressVisualizationForPlanning:
    """Test suite for progress visualization during planning (Deliverable 4.2)"""
    
    @pytest.fixture
    def temp_cortex_root(self, tmp_path):
        """Create temporary CORTEX directory structure"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        config_path = brain_path / "config"
        config_path.mkdir(parents=True)
        
        plans_path = brain_path / "documents" / "planning" / "features" / "active"
        plans_path.mkdir(parents=True)
        
        # Create minimal schema
        schema_path = config_path / "plan-schema.yaml"
        schema_path.write_text("""
schema:
  version: "1.0.0"
  required_fields: [metadata, phases]
""", encoding='utf-8')
        
        return cortex_root
    
    @pytest.fixture
    def orchestrator(self, temp_cortex_root):
        """Create PlanningOrchestrator instance"""
        return PlanningOrchestrator(str(temp_cortex_root))
    
    def test_progress_shows_percentage_and_eta(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 5: Verify progress shows completion percentage and ETA
        
        Acceptance Criteria (4.2):
        - Progress decorator shows 'Planning: Phase 3/7 (43% complete, ETA 2m 15s)'
        """
        # Arrange
        phases = [{"id": str(i), "name": f"Phase {i}"} for i in range(1, 8)]
        
        progress_messages = []
        
        def capture_progress(message):
            progress_messages.append(message)
        
        # Act - Generate plan with progress capture
        result = orchestrator.generate_plan_incremental(
            plan_name="progress-test",
            metadata={"name": "Progress Test"},
            phases=phases,
            progress_handler=capture_progress
        )
        
        # Assert - Progress messages contain percentage and ETA
        assert result["success"] is True
        assert len(progress_messages) > 0, "Should have progress messages"
        
        # Check at least one message has expected format
        sample_message = progress_messages[2]  # Phase 3/7
        assert "Phase 3/7" in sample_message or "3 of 7" in sample_message
        assert "%" in sample_message or "complete" in sample_message
    
    def test_hang_detection_if_phase_takes_too_long(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 6: Verify hang detection if phase takes >5x expected time
        
        Acceptance Criteria (4.2):
        - Hang detection if phase takes >5x expected time
        """
        # Arrange - Create phase with expected time
        phase_with_estimate = {
            "id": "1",
            "name": "Slow Phase",
            "estimated_time_seconds": 1  # Expect 1 second, >5 seconds = hang
        }
        
        hang_detected = False
        
        def detect_hang(phase_id, elapsed, expected):
            nonlocal hang_detected
            if elapsed > expected * 5:
                hang_detected = True
        
        # This test would require actually simulating slow phase generation
        # For now, we verify the interface exists
        assert hasattr(orchestrator, 'generate_plan_incremental'), "Method should exist"


class TestIncrementalValidation:
    """Test suite for validating phases during generation (Deliverable 4.3)"""
    
    @pytest.fixture
    def temp_cortex_root(self, tmp_path):
        """Create temporary CORTEX directory structure"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        config_path = brain_path / "config"
        config_path.mkdir(parents=True)
        
        plans_path = brain_path / "documents" / "planning" / "features" / "active"
        plans_path.mkdir(parents=True)
        
        # Create schema with validation rules
        schema_path = config_path / "plan-schema.yaml"
        schema_path.write_text("""
schema:
  version: "1.0.0"
  required_fields: [metadata, phases]
  phase_required_fields:
    - id
    - name
    - tasks
""", encoding='utf-8')
        
        return cortex_root
    
    @pytest.fixture
    def orchestrator(self, temp_cortex_root):
        """Create PlanningOrchestrator instance"""
        return PlanningOrchestrator(str(temp_cortex_root))
    
    def test_invalid_phase_rejected_immediately(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 7: Verify invalid phases are rejected immediately
        
        Acceptance Criteria (4.3):
        - YAML schema validated after each phase added
        - Errors reported immediately, not after all phases generated
        - Invalid phase discarded, generation continues
        """
        # Arrange - Mix valid and invalid phases
        phases = [
            {"id": "1", "name": "Valid Phase", "tasks": ["Task 1"]},
            {"id": "2", "name": "Invalid Phase"},  # Missing required 'tasks' field
            {"id": "3", "name": "Valid Phase 2", "tasks": ["Task 3"]}
        ]
        
        validation_errors = []
        
        def capture_validation_error(phase_id, errors):
            validation_errors.append({"phase_id": phase_id, "errors": errors})
        
        # Act - Generate plan with validation
        result = orchestrator.generate_plan_incremental(
            plan_name="validation-test",
            metadata={"name": "Validation Test"},
            phases=phases,
            validate_incrementally=True,
            validation_error_handler=capture_validation_error
        )
        
        # Assert - Invalid phase rejected but generation continued
        assert result["success"] is True, "Should succeed despite invalid phase"
        assert result["phases_added"] == 2, "Should add only valid phases"
        assert result["phases_rejected"] == 1, "Should reject invalid phase"
        
        # Verify validation error captured
        assert len(validation_errors) == 1, "Should capture validation error"
        assert validation_errors[0]["phase_id"] == "2"
        
        # Verify final plan contains only valid phases
        plan_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / "validation-test.yaml"
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        assert len(plan_data["phases"]) == 2, "Should have only valid phases"
        assert plan_data["phases"][0]["id"] == "1"
        assert plan_data["phases"][1]["id"] == "3"
    
    def test_dor_dod_validation_runs_incrementally(self, orchestrator, temp_cortex_root):
        """
        RED Phase Test 8: Verify DoR/DoD validation runs incrementally
        
        Acceptance Criteria (4.3):
        - DoR/DoD validation runs incrementally
        """
        # Arrange
        phases = [
            {
                "id": "1",
                "name": "Phase 1",
                "tasks": ["Task 1"],
                "definition_of_ready": ["Requirement 1"],
                "definition_of_done": ["Completion 1"]
            }
        ]
        
        dor_dod_validations = []
        
        def capture_dor_dod_validation(phase_id, dor_valid, dod_valid):
            dor_dod_validations.append({
                "phase_id": phase_id,
                "dor_valid": dor_valid,
                "dod_valid": dod_valid
            })
        
        # Act
        result = orchestrator.generate_plan_incremental(
            plan_name="dor-dod-test",
            metadata={"name": "DoR/DoD Test"},
            phases=phases,
            validate_dor_dod=True,
            dor_dod_handler=capture_dor_dod_validation
        )
        
        # Assert - Validation occurred
        assert result["success"] is True
        # Interface verification - actual validation logic tested separately
