"""
Integration Test: Planning Orchestrator TDD Injection

RED PHASE: This test MUST fail before implementation.

Purpose: Verify that all planning orchestrators automatically inject
mandatory TDD Mastery reminders into DoR/DoD so Copilot cannot miss them.

Test Coverage:
- DoR must include TDD workflow requirements
- DoD must include SKULL rule compliance
- Plans reference brain-protection-rules.yaml
- Test-first enforcement is mandatory

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import yaml
import tempfile
import shutil
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestPlanningTDDInjection:
    """Test suite for TDD requirement injection in planning workflows."""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX root with required structure."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_test_")
        cortex_root = Path(temp_dir)
        
        # Create required directories
        (cortex_root / "cortex-brain" / "config").mkdir(parents=True)
        (cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        (cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "completed").mkdir(parents=True)
        
        # Create minimal plan schema
        schema_path = cortex_root / "cortex-brain" / "config" / "plan-schema.yaml"
        schema_path.write_text("""
schema:
  version: "1.0.0"
  required_fields:
    - metadata
    - phases
    - definition_of_ready
    - definition_of_done
""")
        
        # Create response templates (minimal)
        template_path = cortex_root / "cortex-brain" / "response-templates.yaml"
        template_path.write_text("""
templates:
  work_planner_success:
    planning_mode_active: false
    session_restoration_enabled: true
""")
        
        yield cortex_root
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def orchestrator(self, temp_cortex_root):
        """Create PlanningOrchestrator instance."""
        return PlanningOrchestrator(str(temp_cortex_root))
    
    def test_dor_contains_tdd_workflow_requirement(self, orchestrator, temp_cortex_root):
        """
        RED PHASE TEST: DoR must include TDD workflow enforcement.
        
        Expected to FAIL until implementation adds TDD injection.
        """
        # Generate a plan
        plan_data = {
            "metadata": {
                "plan_id": "TEST-001",
                "title": "Test Feature",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Implementation",
                    "estimated_hours": "5",
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "task_name": "Implement feature",
                            "estimated_hours": 5
                        }
                    ]
                }
            ],
            "definition_of_ready": [],  # Empty - should be populated by orchestrator
            "definition_of_done": []    # Empty - should be populated by orchestrator
        }
        
        # Call TDD injection method (to be implemented)
        enriched_plan = orchestrator.inject_tdd_requirements(plan_data)
        
        # ASSERTION 1: DoR must contain TDD workflow requirement
        dor = enriched_plan.get("definition_of_ready", [])
        
        tdd_workflow_found = any(
            "TDD" in item and "RED→GREEN→REFACTOR" in item
            for item in dor
        )
        
        assert tdd_workflow_found, (
            "DoR must include 'TDD Mastery workflow MUST be followed (RED→GREEN→REFACTOR)' "
            "but found: " + str(dor)
        )
    
    def test_dor_contains_test_first_validation(self, orchestrator):
        """
        RED PHASE TEST: DoR must include test-first enforcement.
        
        Expected to FAIL until implementation adds RED phase validation.
        """
        plan_data = {
            "metadata": {
                "plan_id": "TEST-002",
                "title": "Test Feature 2",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [{"phase_number": 1, "phase_name": "Test", "estimated_hours": "5", "tasks": []}],
            "definition_of_ready": [],
            "definition_of_done": []
        }
        
        enriched_plan = orchestrator.inject_tdd_requirements(plan_data)
        dor = enriched_plan.get("definition_of_ready", [])
        
        # ASSERTION 2: DoR must include RED phase validation
        red_phase_found = any(
            "Tests MUST fail before implementation" in item or
            "RED phase validation" in item
            for item in dor
        )
        
        assert red_phase_found, (
            "DoR must include 'Tests MUST fail before implementation (RED phase validation)' "
            "but found: " + str(dor)
        )
    
    def test_dor_contains_brain_protection_reference(self, orchestrator):
        """
        RED PHASE TEST: DoR must reference SKULL rules.
        
        Expected to FAIL until implementation adds brain protection reference.
        """
        plan_data = {
            "metadata": {
                "plan_id": "TEST-003",
                "title": "Test Feature 3",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [{"phase_number": 1, "phase_name": "Test", "estimated_hours": "5", "tasks": []}],
            "definition_of_ready": [],
            "definition_of_done": []
        }
        
        enriched_plan = orchestrator.inject_tdd_requirements(plan_data)
        dor = enriched_plan.get("definition_of_ready", [])
        
        # ASSERTION 3: DoR must reference brain protection rules
        skull_found = any(
            "CORTEX brain protection rules" in item or
            "brain-protection-rules.yaml" in item or
            "SKULL" in item
            for item in dor
        )
        
        assert skull_found, (
            "DoR must include 'All CORTEX brain protection rules apply (SKULL enforcement)' "
            "but found: " + str(dor)
        )
    
    def test_dod_contains_tdd_workflow_compliance(self, orchestrator):
        """
        RED PHASE TEST: DoD must verify TDD workflow was followed.
        
        Expected to FAIL until implementation adds TDD compliance check.
        """
        plan_data = {
            "metadata": {
                "plan_id": "TEST-004",
                "title": "Test Feature 4",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [{"phase_number": 1, "phase_name": "Test", "estimated_hours": "5", "tasks": []}],
            "definition_of_ready": [],
            "definition_of_done": []
        }
        
        enriched_plan = orchestrator.inject_tdd_requirements(plan_data)
        dod = enriched_plan.get("definition_of_done", [])
        
        # ASSERTION 4: DoD must verify TDD workflow followed
        tdd_compliance_found = any(
            "TDD workflow" in item and "git checkpoints" in item
            for item in dod
        )
        
        assert tdd_compliance_found, (
            "DoD must include 'All code follows TDD workflow with git checkpoints' "
            "but found: " + str(dod)
        )
    
    def test_dod_contains_skull_rule_validation(self, orchestrator):
        """
        RED PHASE TEST: DoD must verify no SKULL violations.
        
        Expected to FAIL until implementation adds SKULL validation.
        """
        plan_data = {
            "metadata": {
                "plan_id": "TEST-005",
                "title": "Test Feature 5",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [{"phase_number": 1, "phase_name": "Test", "estimated_hours": "5", "tasks": []}],
            "definition_of_ready": [],
            "definition_of_done": []
        }
        
        enriched_plan = orchestrator.inject_tdd_requirements(plan_data)
        dod = enriched_plan.get("definition_of_done", [])
        
        # ASSERTION 5: DoD must verify no SKULL violations
        skull_validation_found = any(
            "SKULL rule violations" in item or
            "brain protection rules" in item
            for item in dod
        )
        
        assert skull_validation_found, (
            "DoD must include 'No SKULL rule violations detected' "
            "but found: " + str(dod)
        )
    
    def test_dod_contains_test_coverage_requirement(self, orchestrator):
        """
        RED PHASE TEST: DoD must verify test coverage standards.
        
        Expected to FAIL until implementation adds coverage requirement.
        """
        plan_data = {
            "metadata": {
                "plan_id": "TEST-006",
                "title": "Test Feature 6",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [{"phase_number": 1, "phase_name": "Test", "estimated_hours": "5", "tasks": []}],
            "definition_of_ready": [],
            "definition_of_done": []
        }
        
        enriched_plan = orchestrator.inject_tdd_requirements(plan_data)
        dod = enriched_plan.get("definition_of_done", [])
        
        # ASSERTION 6: DoD must verify test coverage
        coverage_found = any(
            "test coverage" in item.lower() or
            "coverage meets" in item.lower()
            for item in dod
        )
        
        assert coverage_found, (
            "DoD must include 'Test coverage meets CORTEX standards' "
            "but found: " + str(dod)
        )
    
    def test_injection_preserves_existing_items(self, orchestrator):
        """
        RED PHASE TEST: TDD injection must preserve existing DoR/DoD items.
        
        Expected to FAIL until implementation properly merges items.
        """
        plan_data = {
            "metadata": {
                "plan_id": "TEST-007",
                "title": "Test Feature 7",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [{"phase_number": 1, "phase_name": "Test", "estimated_hours": "5", "tasks": []}],
            "definition_of_ready": ["Existing DoR item"],
            "definition_of_done": ["Existing DoD item"]
        }
        
        enriched_plan = orchestrator.inject_tdd_requirements(plan_data)
        
        # ASSERTION 7: Must preserve existing items
        dor = enriched_plan.get("definition_of_ready", [])
        dod = enriched_plan.get("definition_of_done", [])
        
        assert "Existing DoR item" in dor, "Must preserve existing DoR items"
        assert "Existing DoD item" in dod, "Must preserve existing DoD items"
        
        # AND add TDD items
        assert len(dor) > 1, "Must add TDD items to DoR"
        assert len(dod) > 1, "Must add TDD items to DoD"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
