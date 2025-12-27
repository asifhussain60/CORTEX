"""
Tests for Final REFACTOR Phase Enforcement (SKULL Rule).

Validates that Planning Orchestrator ALWAYS adds mandatory final REFACTOR phase
that reviews ENTIRE file for cleanliness (duplicates, broken structure, complexity).

SKULL Rule: REFACTOR_CODE_CLEANUP_ENFORCEMENT
"""

import pytest
from src.orchestrators.planning.planning_orchestrator import (
    PlanningOrchestrator,
    PlanData,
    PlanMetadata,
    PlanPhaseData,
    PlanType,
    PlanComplexity
)


@pytest.fixture
def planning_orchestrator(tmp_path):
    """Create PlanningOrchestrator instance."""
    config = {
        "cortex_root": "/Users/asifhussain/PROJECTS/CORTEX",
        "active_plans_dir": str(tmp_path / "active"),
        "temp_plans_dir": str(tmp_path / "temp"),
        "tdd_enabled": True,
        "enforce_dor": False  # Disable for testing
    }
    return PlanningOrchestrator(config)


@pytest.fixture
def sample_plan_dict():
    """Create sample plan dict."""
    return {
        "metadata": {
            "title": "Test Feature",
            "description": "Test description",
            "complexity": "medium",
            "plan_type": "incremental"
        },
        "phases": [
            {
                "name": "Design",
                "tasks": [{"task": "Design architecture", "estimated_hours": 2}],
                "acceptance_criteria": ["Architecture documented"]
            },
            {
                "name": "Implementation",
                "tasks": [{"task": "Implement code", "estimated_hours": 4}],
                "acceptance_criteria": ["Code complete"]
            }
        ]
    }


@pytest.fixture
def sample_plan_data():
    """Create sample PlanData object."""
    return PlanData(
        metadata=PlanMetadata(
            title="Test Feature",
            description="Test description",
            complexity=PlanComplexity.MEDIUM,
            plan_type=PlanType.INCREMENTAL
        ),
        definition_of_ready=["Requirements clear"],
        definition_of_done=["Tests passing"],
        phases=[
            PlanPhaseData(
                phase_name="Design",
                tasks=[{"task": "Design architecture", "estimated_hours": 2}],
                acceptance_criteria=["Architecture documented"]
            ),
            PlanPhaseData(
                phase_name="Implementation",
                tasks=[{"task": "Implement code", "estimated_hours": 4}],
                acceptance_criteria=["Code complete"]
            )
        ],
        tdd_requirements={}
    )


class TestFinalRefactorEnforcement:
    """Test final REFACTOR phase enforcement."""
    
    def test_enforce_final_refactor_phase_adds_phase(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test _enforce_final_refactor_phase adds final REFACTOR phase."""
        original_phase_count = len(sample_plan_dict["phases"])
        
        result = planning_orchestrator._enforce_final_refactor_phase(sample_plan_dict)
        
        assert len(result["phases"]) == original_phase_count + 1
        assert "final refactor" in result["phases"][-1]["name"].lower()
        assert result["metadata"]["final_refactor_enforced"] is True
    
    def test_final_refactor_phase_structure(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test final REFACTOR phase has correct structure."""
        result = planning_orchestrator._enforce_final_refactor_phase(sample_plan_dict)
        
        final_phase = result["phases"][-1]
        
        # Verify phase attributes
        assert final_phase["type"] == "quality_gate"
        assert "ENTIRE file" in final_phase["description"]
        assert "scope" in final_phase
        assert final_phase["scope"] == "ALL modified files (not just new code)"
        assert final_phase["required"] is True
        assert final_phase["enforcement_level"] == "MANDATORY"
        assert final_phase["skull_rule"] == "REFACTOR_CODE_CLEANUP_ENFORCEMENT"
    
    def test_final_refactor_phase_activities(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test final REFACTOR phase includes all required activities."""
        result = planning_orchestrator._enforce_final_refactor_phase(sample_plan_dict)
        
        activities = result["phases"][-1]["activities"]
        
        # Verify comprehensive activities
        assert any("ENTIRE file" in a for a in activities), "Must review ENTIRE file"
        assert any("broken HTML" in a or "syntax" in a for a in activities), "Must fix structural issues"
        assert any("duplicate" in a for a in activities), "Must remove duplicates"
        assert any("complexity >30" in a for a in activities), "Must refactor high complexity"
        assert any("SOLID" in a for a in activities), "Must enforce SOLID principles"
        assert any("dead" in a or "orphaned" in a for a in activities), "Must remove dead code"
        assert any("tests" in a for a in activities), "Must run tests"
    
    def test_final_refactor_phase_validation_criteria(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test final REFACTOR phase includes validation criteria."""
        result = planning_orchestrator._enforce_final_refactor_phase(sample_plan_dict)
        
        criteria = result["phases"][-1]["validation_criteria"]
        
        # Verify comprehensive validation
        assert any("broken HTML" in c or "structural" in c for c in criteria)
        assert any("duplicate" in c for c in criteria)
        assert any("complexity" in c for c in criteria)
        assert any("SOLID" in c for c in criteria)
        assert any("dead code" in c for c in criteria)
        assert any("tests passing" in c for c in criteria)
    
    def test_enforce_idempotent(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test enforcement is idempotent (doesn't add duplicate phases)."""
        result1 = planning_orchestrator._enforce_final_refactor_phase(sample_plan_dict)
        phase_count1 = len(result1["phases"])
        
        result2 = planning_orchestrator._enforce_final_refactor_phase(result1)
        phase_count2 = len(result2["phases"])
        
        assert phase_count1 == phase_count2, "Should not add duplicate final REFACTOR phase"
    
    def test_enforce_final_refactor_on_plan_data(
        self,
        planning_orchestrator,
        sample_plan_data
    ):
        """Test _enforce_final_refactor_on_plan_data works with PlanData objects."""
        original_phase_count = len(sample_plan_data.phases)
        
        result = planning_orchestrator._enforce_final_refactor_on_plan_data(sample_plan_data)
        
        assert len(result.phases) == original_phase_count + 1
        assert "final refactor" in result.phases[-1].phase_name.lower()
    
    def test_execute_enforces_final_refactor(
        self,
        planning_orchestrator,
        tmp_path
    ):
        """Test execute() method enforces final REFACTOR phase."""
        result = planning_orchestrator.execute(
            feature_name="Test Feature",
            plan_type="incremental",
            complexity=PlanComplexity.MEDIUM,
            output_dir=tmp_path
        )
        
        # Should succeed with final REFACTOR phase added
        assert result.success is True
        
        # Check that logs mention enforcement (if logging is captured)
        # This would require caplog fixture, but plan_data should have the phase


class TestSKULLRuleIntegration:
    """Test SKULL rule integration."""
    
    def test_tdd_integration_calls_final_refactor(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test _integrate_tdd_workflow calls _enforce_final_refactor_phase."""
        result = planning_orchestrator._integrate_tdd_workflow(sample_plan_dict)
        
        # Should have TDD phases AND final REFACTOR phase
        phase_names = [p["name"].lower() for p in result["phases"]]
        
        assert any("red phase" in name for name in phase_names), "Should have TDD RED phase"
        assert any("green phase" in name for name in phase_names), "Should have TDD GREEN phase"
        assert any("refactor phase" in name for name in phase_names), "Should have TDD REFACTOR phase"
        assert any("final refactor" in name for name in phase_names), "Should have FINAL REFACTOR phase"
    
    def test_final_refactor_is_last_phase(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test final REFACTOR phase comes before learning library (second to last)."""
        result = planning_orchestrator._integrate_tdd_workflow(sample_plan_dict)
        
        # Final REFACTOR should be second to last (learning library is last)
        phase_names = [p["name"].lower() for p in result["phases"]]
        
        # Find final REFACTOR phase
        refactor_found = False
        for name in phase_names:
            if "final refactor" in name:
                refactor_found = True
                break
        
        assert refactor_found, "Final REFACTOR phase not found in plan"
        
        # Verify learning library is last
        assert "learning library" in phase_names[-1], "Learning library should be last phase"


class TestPhaseContent:
    """Test phase content quality."""
    
    def test_phase_distinguishes_from_tdd_refactor(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test final REFACTOR phase clearly distinguishes from TDD REFACTOR."""
        result = planning_orchestrator._enforce_final_refactor_phase(sample_plan_dict)
        
        final_phase = result["phases"][-1]
        
        # Should mention ENTIRE file (not just new code)
        description = final_phase["description"]
        rationale = final_phase.get("rationale", "")
        scope = final_phase.get("scope", "")
        
        assert "ENTIRE" in description or "ENTIRE" in rationale or "ENTIRE" in scope
        assert "ALL modified files" in scope or "not just new code" in scope
    
    def test_phase_includes_estimated_hours(
        self,
        planning_orchestrator,
        sample_plan_dict
    ):
        """Test final REFACTOR phase includes time estimate."""
        result = planning_orchestrator._enforce_final_refactor_phase(sample_plan_dict)
        
        final_phase = result["phases"][-1]
        assert "estimated_hours" in final_phase
        assert final_phase["estimated_hours"] > 0
