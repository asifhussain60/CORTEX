"""
End-to-End Integration Test: Planning TDD Auto-Injection

Purpose: Verify that TDD requirements are automatically injected when
creating plans through normal workflows (save_plan).

This test validates the complete wiring of TDD injection into planning
orchestrator, ensuring Copilot cannot create plans without TDD reminders.

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import yaml
import tempfile
import shutil
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestPlanningTDDEndToEnd:
    """End-to-end integration tests for automatic TDD injection."""
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX root with required structure."""
        temp_dir = tempfile.mkdtemp(prefix="cortex_e2e_")
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
    
    def test_save_plan_automatically_injects_tdd(self, orchestrator, temp_cortex_root):
        """
        E2E TEST: save_plan() must automatically inject TDD requirements.
        
        User creates plan without TDD items → save_plan() injects them.
        """
        # Create plan WITHOUT any TDD requirements
        plan_data = {
            "metadata": {
                "plan_id": "E2E-001",
                "title": "Test Feature",
                "description": "End-to-end test feature",
                "author": "Test Suite",
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
                    "name": "Implementation Phase",
                    "estimated_hours": "5",
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "task_name": "Implement feature",
                            "description": "Implement the test feature",
                            "estimated_hours": 5
                        }
                    ]
                }
            ],
            "definition_of_ready": ["Custom requirement 1"],
            "definition_of_done": ["Custom requirement 2"]
        }
        
        # Save plan (should auto-inject TDD)
        success, message = orchestrator.save_plan(plan_data)
        
        assert success, f"save_plan() failed: {message}"
        
        # Load saved plan and verify TDD injection
        saved_plan_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / "E2E-001.yaml"
        assert saved_plan_path.exists(), "Plan file was not created"
        
        with open(saved_plan_path, 'r', encoding='utf-8') as f:
            saved_plan = yaml.safe_load(f)
        
        # Verify TDD requirements injected
        dor = saved_plan.get("definition_of_ready", [])
        dod = saved_plan.get("definition_of_done", [])
        
        # Check DoR has TDD items
        assert any("TDD" in item and "RED→GREEN→REFACTOR" in item for item in dor), \
            f"TDD workflow not in DoR: {dor}"
        
        assert any("Tests MUST fail" in item for item in dor), \
            f"RED phase validation not in DoR: {dor}"
        
        assert any("brain protection" in item.lower() or "skull" in item.lower() for item in dor), \
            f"SKULL reference not in DoR: {dor}"
        
        # Check DoD has TDD items
        assert any("TDD workflow" in item for item in dod), \
            f"TDD workflow compliance not in DoD: {dod}"
        
        assert any("SKULL" in item for item in dod), \
            f"SKULL validation not in DoD: {dod}"
        
        assert any("coverage" in item.lower() for item in dod), \
            f"Test coverage not in DoD: {dod}"
        
        # Verify custom requirements preserved
        assert "Custom requirement 1" in dor, "Original DoR item lost"
        assert "Custom requirement 2" in dod, "Original DoD item lost"
    
    def test_tdd_injection_is_idempotent(self, orchestrator, temp_cortex_root):
        """
        E2E TEST: Multiple saves don't duplicate TDD requirements.
        
        Calling save_plan() twice must not create duplicate TDD items.
        """
        plan_data = {
            "metadata": {
                "plan_id": "E2E-002",
                "title": "Idempotent Test",
                "description": "Test idempotent injection",
                "author": "Test Suite",
                "created_date": "2024-01-01T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 5
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Test",
                    "name": "Test Phase",
                    "estimated_hours": "5",
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "task_name": "Test",
                            "description": "Test task description",
                            "estimated_hours": 5
                        }
                    ]
                }
            ],
            "definition_of_ready": [],
            "definition_of_done": []
        }
        
        # Save twice
        success1, msg1 = orchestrator.save_plan(plan_data.copy())
        assert success1, f"First save failed: {msg1}"
        
        # Load and save again
        saved_plan_path = temp_cortex_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / "E2E-002.yaml"
        with open(saved_plan_path, 'r', encoding='utf-8') as f:
            reloaded_plan = yaml.safe_load(f)
        
        success2, msg2 = orchestrator.save_plan(reloaded_plan)
        assert success2, f"Second save failed: {msg2}"
        
        # Load final version
        with open(saved_plan_path, 'r', encoding='utf-8') as f:
            final_plan = yaml.safe_load(f)
        
        # Count TDD requirements - should be exactly 4 in each
        dor = final_plan.get("definition_of_ready", [])
        dod = final_plan.get("definition_of_done", [])
        
        # Count TDD-specific items (each item from _tdd_dor_requirements and _tdd_dod_requirements)
        # Use the first 30 chars to match (same logic as inject_tdd_requirements)
        expected_dor_keys = [
            "tdd mastery workflow must",
            "tests must fail before",
            "all cortex brain protection",
            "reference: cortex-brain/"
        ]
        expected_dod_keys = [
            "all code follows tdd",
            "no skull rule violations",
            "test coverage meets",
            "git history shows test"
        ]
        
        dor_lower = [item.lower()[:30] for item in dor]
        dod_lower = [item.lower()[:30] for item in dod]
        
        tdd_dor_count = sum(1 for key in expected_dor_keys if key in ' '.join(dor_lower))
        tdd_dod_count = sum(1 for key in expected_dod_keys if key in ' '.join(dod_lower))
        
        assert tdd_dor_count == 4, f"Expected 4 TDD DoR items, found {tdd_dor_count}. DoR: {dor}"
        assert tdd_dod_count == 4, f"Expected 4 TDD DoD items, found {tdd_dod_count}. DoD: {dod}"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
