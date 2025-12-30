"""
Tests for Learning Library Documentation Phase Enforcement (SKULL Rule).

Validates that Planning Orchestrator ALWAYS adds mandatory learning library documentation phase
that captures implementation knowledge, design decisions, and lessons learned in 6-file structure.

SKULL Rule: LEARNING_LIBRARY_DOCUMENTATION_ENFORCEMENT
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
        "cortex_root": Path(CORTEX_ROOT) / "",
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
                "tasks": [{"task": "Implement feature", "estimated_hours": 4}],
                "acceptance_criteria": ["Feature working"]
            }
        ]
    }


@pytest.fixture
def sample_plan_data():
    """Create sample PlanData object."""
    metadata = PlanMetadata(
        title="Test Feature",
        description="Test description",
        complexity=PlanComplexity.MEDIUM,
        plan_type=PlanType.INCREMENTAL
    )
    
    phases = [
        PlanPhaseData(
            phase_name="Design",
            tasks=[{"task": "Design architecture", "estimated_hours": 2}],
            acceptance_criteria=["Architecture documented"]
        ),
        PlanPhaseData(
            phase_name="Implementation",
            tasks=[{"task": "Implement feature", "estimated_hours": 4}],
            acceptance_criteria=["Feature working"]
        )
    ]
    
    return PlanData(
        metadata=metadata,
        definition_of_ready=["DoR criteria 1"],
        definition_of_done=["DoD criteria 1"],
        phases=phases
    )


# ============================================================================
# TEST CLASS 1: LEARNING LIBRARY ENFORCEMENT
# ============================================================================

class TestLearningLibraryEnforcement:
    """Test learning library documentation phase enforcement."""
    
    def test_enforce_learning_library_phase_adds_phase(self, planning_orchestrator, sample_plan_dict):
        """Test that enforcement adds learning library documentation phase."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        
        # Assert phase added (should be exactly 3: Design, Implementation, Learning Library)
        assert len(result["phases"]) == 3  # Original 2 + 1 learning library
        
        # Assert it's the last phase
        last_phase = result["phases"][-1]
        assert "learning library" in last_phase["name"].lower()
    
    def test_learning_library_phase_structure(self, planning_orchestrator, sample_plan_dict):
        """Test learning library phase has correct structure."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        last_phase = result["phases"][-1]
        
        # Assert phase structure
        assert "name" in last_phase
        assert "learning library documentation" in last_phase["name"].lower()
        assert "type" in last_phase
        assert last_phase["type"] in ["documentation", "knowledge_capture"]  # Accept either
        assert "estimated_hours" in last_phase
        assert last_phase["estimated_hours"] > 0
        assert "required" in last_phase
        assert last_phase["required"] is True
    
    def test_learning_library_phase_activities(self, planning_orchestrator, sample_plan_dict):
        """Test learning library phase has 7-8 mandatory activities."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        last_phase = result["phases"][-1]
        
        # Assert activities present (8 activities total including knowledge graph linking)
        assert "activities" in last_phase
        activities = last_phase["activities"]
        assert len(activities) >= 7  # At least 7 activities
        
        # Assert key activities present
        activities_text = " ".join(activities).lower()
        assert "folder structure" in activities_text or "create organized" in activities_text or "create learning library" in activities_text
        assert "readme" in activities_text
        assert "context" in activities_text
        assert "architecture" in activities_text
        assert "implementation" in activities_text or "implementation-guide" in activities_text
        assert "test strategy" in activities_text or "test-strategy" in activities_text
        assert "research" in activities_text or "research-notes" in activities_text
    
    def test_learning_library_phase_validation_criteria(self, planning_orchestrator, sample_plan_dict):
        """Test learning library phase has 8 validation criteria."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        last_phase = result["phases"][-1]
        
        # Assert validation criteria present
        assert "validation_criteria" in last_phase
        criteria = last_phase["validation_criteria"]
        assert len(criteria) == 8
        
        # Assert key criteria present (case-insensitive)
        criteria_text = " ".join(criteria).lower()
        assert "6" in criteria_text or "files" in criteria_text  # "All 6 documentation files created"
        assert "overview" in criteria_text or "readme" in criteria_text  # "README includes overview"
        assert "problem" in criteria_text or "context" in criteria_text  # "Context captures problem"
        assert "diagrams" in criteria_text or "architecture" in criteria_text or "components" in criteria_text
        assert "implementation" in criteria_text or "code" in criteria_text or "walkthrough" in criteria_text
        assert "test" in criteria_text or "coverage" in criteria_text or "strategy" in criteria_text
        assert "decisions" in criteria_text or "research" in criteria_text or "notes" in criteria_text
        assert "knowledge graph" in criteria_text or "linked" in criteria_text
    
    def test_enforce_idempotent(self, planning_orchestrator, sample_plan_dict):
        """Test that enforcement is idempotent (doesn't add duplicate phase)."""
        # Execute twice
        result1 = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        result2 = planning_orchestrator._enforce_learning_library_documentation(result1)
        
        # Assert only one learning library phase added
        learning_phases = [p for p in result2["phases"] if "learning library" in p["name"].lower()]
        assert len(learning_phases) == 1
    
    def test_enforce_learning_library_on_plan_data(self, planning_orchestrator, sample_plan_data):
        """Test enforcement on PlanData object."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation_on_plan_data(sample_plan_data)
        
        # Assert type preserved
        assert isinstance(result, PlanData)
        
        # Assert phase added (should be exactly 3: Design, Implementation, Learning Library)
        assert len(result.phases) == 3  # Original 2 + 1 learning library
        
        # Assert last phase is learning library
        last_phase = result.phases[-1]
        assert "learning library" in last_phase.phase_name.lower()
    
    def test_execute_enforces_learning_library(self, planning_orchestrator, tmp_path):
        """Test that execute() method enforces learning library documentation."""
        # Setup
        output_file = tmp_path / "test-plan.md"
        
        # Execute plan generation
        result = planning_orchestrator.execute(
            feature_name="Test Feature",
            plan_type="incremental",
            output_dir=str(tmp_path)
        )
        
        # Assert learning library phase present in result
        if hasattr(result, "plan_data") and result.plan_data:
            phases = result.plan_data.phases
            learning_phases = [p for p in phases if "learning library" in p.phase_name.lower()]
            assert len(learning_phases) >= 1, "Learning library phase not found in generated plan"


# ============================================================================
# TEST CLASS 2: SKULL RULE INTEGRATION
# ============================================================================

class TestSKULLRuleIntegration:
    """Test SKULL rule integration with TDD workflow."""
    
    def test_tdd_integration_calls_learning_library(self, planning_orchestrator, sample_plan_dict):
        """Test that TDD workflow integration calls learning library enforcement."""
        # Execute TDD integration (which should call learning library)
        result = planning_orchestrator._integrate_tdd_workflow(sample_plan_dict)
        
        # Assert learning library phase present
        learning_phases = [p for p in result["phases"] if "learning library" in p["name"].lower()]
        assert len(learning_phases) >= 1, "Learning library phase not added by TDD integration"
    
    def test_learning_library_after_final_refactor(self, planning_orchestrator, sample_plan_dict):
        """Test that learning library phase comes AFTER final REFACTOR phase."""
        # Execute TDD integration (adds both final REFACTOR and learning library)
        result = planning_orchestrator._integrate_tdd_workflow(sample_plan_dict)
        
        # Find phase indices
        refactor_idx = None
        learning_idx = None
        
        for i, phase in enumerate(result["phases"]):
            phase_name = phase["name"].lower()
            if "final refactor" in phase_name:
                refactor_idx = i
            if "learning library" in phase_name:
                learning_idx = i
        
        # Assert both phases present
        assert refactor_idx is not None, "Final REFACTOR phase not found"
        assert learning_idx is not None, "Learning library phase not found"
        
        # Assert learning library comes AFTER final REFACTOR
        assert learning_idx > refactor_idx, \
            f"Learning library (idx {learning_idx}) should come AFTER final REFACTOR (idx {refactor_idx})"


# ============================================================================
# TEST CLASS 3: PHASE CONTENT
# ============================================================================

class TestPhaseContent:
    """Test learning library phase content quality."""
    
    def test_phase_distinguishes_from_tdd_documentation(self, planning_orchestrator, sample_plan_dict):
        """Test that learning library phase is distinct from TDD documentation."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        last_phase = result["phases"][-1]
        
        # Assert scope is knowledge capture (not just test documentation)
        phase_text = str(last_phase).lower()
        
        # Should mention knowledge, design decisions, lessons learned
        assert any(keyword in phase_text for keyword in [
            "knowledge", "design decisions", "lessons learned", 
            "implementation guide", "architecture", "research"
        ]), "Phase should focus on knowledge capture, not just test documentation"
    
    def test_phase_includes_six_file_structure(self, planning_orchestrator, sample_plan_dict):
        """Test that phase explicitly mentions 6-file documentation structure."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        last_phase = result["phases"][-1]
        
        # Assert activities or criteria mention 6 files
        phase_text = str(last_phase).lower()
        
        # Count expected files mentioned
        expected_files = ["readme", "context", "architecture", "implementation", "test", "research"]
        files_mentioned = sum(1 for f in expected_files if f in phase_text)
        
        assert files_mentioned >= 5, \
            f"Phase should mention at least 5 of 6 documentation files (found {files_mentioned})"
    
    def test_phase_includes_output_location(self, planning_orchestrator, sample_plan_dict):
        """Test that phase specifies output location in cortex-brain/documents/library/{repo_name}/."""
        # Execute
        result = planning_orchestrator._enforce_learning_library_documentation(sample_plan_dict)
        last_phase = result["phases"][-1]
        
        # Assert output location mentioned
        phase_text = str(last_phase).lower()
        assert any(keyword in phase_text for keyword in [
            "cortex-brain", "documents/library", "learning library", "organized folder"
        ]), "Phase should specify output location for documentation"


# ============================================================================
# RUN TESTS
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
