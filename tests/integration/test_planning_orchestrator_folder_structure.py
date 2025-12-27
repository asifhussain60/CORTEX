"""
Integration Test: Planning Orchestrator Folder Structure

Validates that PlanningOrchestrator creates proper hierarchical folder structure
following the Planning System 4.0 manifest specification.

Test Objectives:
1. Create sample plan via PlanningOrchestrator
2. Verify folder structure (context/, reports/, artifacts/, tracking/, execution/)
3. Verify naming conventions (00-master-plan.md)
4. Verify progress-tracker.json initialization
5. Verify README.md generation
6. Verify YAML moved to execution/ subfolder
7. Verify OVERALL REFACTOR phase exists in plan
8. Verify learning library documentation phase exists
9. Clean up test plan folder

Author: CORTEX Development Team
Created: December 27, 2025
Test Type: Integration
"""

import json
import pytest
import shutil
import yaml
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator, PlanComplexity, PlanType
from src.utils.plan_folder_manager import PlanFolderManager


@pytest.fixture
def cortex_root(tmp_path):
    """Create temporary CORTEX root structure."""
    cortex_root = tmp_path / "cortex"
    
    # Create required directories
    brain_dir = cortex_root / "cortex-brain"
    (brain_dir / "config").mkdir(parents=True)
    (brain_dir / "documents" / "planning" / "features" / "active").mkdir(parents=True)
    (brain_dir / "documents" / "planning" / "features" / "completed").mkdir(parents=True)
    (brain_dir / "manifests" / "orchestrators").mkdir(parents=True)
    
    # Create minimal schema file
    schema_path = brain_dir / "config" / "plan-schema.yaml"
    schema_content = {
        "type": "object",
        "properties": {
            "metadata": {"type": "object"},
            "phases": {"type": "array"}
        }
    }
    schema_path.write_text(yaml.dump(schema_content))
    
    return cortex_root


@pytest.fixture
def planning_orchestrator(cortex_root):
    """Create PlanningOrchestrator instance with folder structure enabled."""
    config = {
        "cortex_root": str(cortex_root),
        "workspace_root": str(cortex_root),
        "enable_git_checkpoints": False,  # Disable git for testing
        "enable_session_restoration": False,
        "enable_autonomous_execution": False,
        "enable_test_intelligence": False,
        "enable_tdd_intelligence": False,
        "enable_validation_framework": False,
        "enable_manifest_validation": False,
        "enable_folder_structure": True,  # CRITICAL: Enable folder structure
        "enforce_dor": False,  # Disable DoR for simple test
        "enforce_dod": False,  # Disable DoD for simple test
    }
    
    orchestrator = PlanningOrchestrator(config)
    return orchestrator


class TestPlanningOrchestratorFolderStructure:
    """Integration tests for folder structure creation."""
    
    def test_create_plan_with_folder_structure(self, planning_orchestrator, cortex_root):
        """
        Test complete workflow: create plan → verify structure → cleanup.
        
        Validates:
        - Hierarchical folder structure created
        - Required subfolders exist
        - Naming conventions followed
        - Progress tracker initialized
        - README generated
        - YAML in execution/ folder
        - OVERALL REFACTOR phase exists
        - Learning library documentation phase exists
        """
        # Step 1: Create a simple test plan
        feature_name = "test-feature-integration"
        
        # Mock plan data with REFACTOR and learning library phases
        from src.orchestrators.planning.planning_orchestrator import PlanData, PlanMetadata, PlanPhaseData
        
        plan_data = PlanData(
            metadata=PlanMetadata(
                title="Test Feature Integration",
                description="Integration test for folder structure",
                complexity=PlanComplexity.HIGH,
                plan_type=PlanType.INCREMENTAL,
                author="CORTEX Test Suite",
                created=datetime.now(),
                version="1.0.0"
            ),
            definition_of_ready={
                "context_gathered": True,
                "requirements_clear": True,
                "stakeholders_aligned": True
            },
            definition_of_done={
                "implementation_complete": True,
                "tests_passing": True,
                "documentation_updated": True
            },
            phases=[
                PlanPhaseData(
                    phase_name="Phase 1: Setup",
                    tasks=["Task 1.1: Initialize", "Task 1.2: Configure"],
                    acceptance_criteria=["Setup complete", "Configuration valid"],
                    dependencies=[]
                ),
                PlanPhaseData(
                    phase_name="Phase 2: Implementation",
                    tasks=["Task 2.1: Implement feature", "Task 2.2: Add tests"],
                    acceptance_criteria=["Feature working", "Tests passing"],
                    dependencies=["Phase 1"]
                ),
                PlanPhaseData(
                    phase_name="OVERALL REFACTOR (MANDATORY - Post-Implementation)",
                    tasks=[
                        "Task REFACTOR.1: Scan entire codebase for orphaned/unused code",
                        "Task REFACTOR.2: Remove duplicate implementations",
                        "Task REFACTOR.3: Consolidate similar functions",
                        "Task REFACTOR.4: Clean up temporary/debug code"
                    ],
                    acceptance_criteria=[
                        "Zero orphaned files detected",
                        "No duplicate implementations",
                        "Code complexity reduced",
                        "All tests still passing"
                    ],
                    dependencies=["Phase 2"]
                ),
                PlanPhaseData(
                    phase_name="Learning Library Documentation (Post-Refactor)",
                    tasks=[
                        "Task LEARN.1: Document patterns discovered",
                        "Task LEARN.2: Update best practices",
                        "Task LEARN.3: Record lessons learned"
                    ],
                    acceptance_criteria=[
                        "Patterns documented in learning library",
                        "Best practices updated",
                        "Lessons learned recorded"
                    ],
                    dependencies=["OVERALL REFACTOR"]
                )
            ],
            tdd_requirements={
                "coverage_threshold": 80,
                "test_first": True
            }
        )
        
        # Step 2: Render the plan (triggers folder creation)
        rendering_result = planning_orchestrator._render_markdown(
            plan_data=plan_data,
            output_dir=planning_orchestrator.active_plans_dir
        )
        
        assert rendering_result.success, f"Plan rendering failed: {rendering_result.errors}"
        assert rendering_result.markdown_path is not None
        assert rendering_result.plan_path is not None
        
        # Step 3: Verify folder structure
        # Find the actual plan folder created by PlanFolderManager
        # It should be in cortex-brain/documents/planning/active/test-feature-integration-v1/
        planning_root = cortex_root / "cortex-brain" / "documents" / "planning" / "active"
        plan_folders = [f for f in planning_root.glob("test-feature-integration-v*") if f.is_dir()]
        
        assert len(plan_folders) == 1, f"Expected 1 plan folder, found {len(plan_folders)} in {planning_root}"
        plan_folder = plan_folders[0]
        
        # Verify folder exists
        assert plan_folder.exists(), f"Plan folder not created: {plan_folder}"
        assert plan_folder.name.startswith("test-feature-integration-v")
        
        # Step 4: Verify required subfolders
        required_subfolders = ["context", "reports", "artifacts", "tracking", "execution"]
        for subfolder in required_subfolders:
            subfolder_path = plan_folder / subfolder
            assert subfolder_path.exists(), f"Missing required subfolder: {subfolder}/"
            assert subfolder_path.is_dir(), f"Subfolder is not a directory: {subfolder}/"
        
        # Step 5: Verify naming conventions
        master_plan = plan_folder / "00-master-plan.md"
        assert master_plan.exists(), "Missing 00-master-plan.md"
        assert master_plan == rendering_result.markdown_path
        
        # Step 6: Verify progress tracker
        tracker_path = plan_folder / "tracking" / "progress-tracker.json"
        assert tracker_path.exists(), "Missing progress-tracker.json"
        
        tracker_data = json.loads(tracker_path.read_text())
        assert "plan_id" in tracker_data
        assert "title" in tracker_data
        assert tracker_data["title"] == "Test Feature Integration"
        assert tracker_data["complexity_tier"] == 3  # DOCUMENTED
        assert tracker_data["status"] == "planning"
        
        # Step 7: Verify README.md
        readme_path = plan_folder / "README.md"
        assert readme_path.exists(), "Missing README.md"
        
        readme_content = readme_path.read_text()
        assert "Test Feature Integration" in readme_content
        assert "00-master-plan.md" in readme_content
        assert "progress-tracker.json" in readme_content
        
        # Step 8: Verify YAML in execution/ folder
        execution_folder = plan_folder / "execution"
        yaml_files = list(execution_folder.glob("*.yaml"))
        assert len(yaml_files) == 1, f"Expected 1 YAML file in execution/, found {len(yaml_files)}"
        assert yaml_files[0] == rendering_result.plan_path
        
        # Step 9: Verify OVERALL REFACTOR phase exists in master plan
        master_plan_content = master_plan.read_text()
        assert "OVERALL REFACTOR" in master_plan_content, "Missing OVERALL REFACTOR phase"
        assert "MANDATORY" in master_plan_content, "OVERALL REFACTOR not marked as MANDATORY"
        assert "orphaned/unused code" in master_plan_content, "Missing orphaned code cleanup task"
        
        # Step 10: Verify learning library documentation phase exists
        assert "Learning Library Documentation" in master_plan_content, "Missing learning library phase"
        assert "Post-Refactor" in master_plan_content, "Learning library phase not marked as post-refactor"
        assert "patterns discovered" in master_plan_content.lower(), "Missing pattern documentation task"
        
        # Step 11: Verify phase ordering (learning library comes after REFACTOR)
        refactor_idx = master_plan_content.find("OVERALL REFACTOR")
        learning_idx = master_plan_content.find("Learning Library Documentation")
        assert refactor_idx < learning_idx, "Learning library phase should come after OVERALL REFACTOR"
        
        # Step 12: Verify YAML structure includes both phases
        yaml_content = yaml.safe_load(rendering_result.plan_path.read_text())
        phase_names = [phase.get("phase_name", "") for phase in yaml_content.get("phases", [])]
        
        refactor_phase_exists = any("OVERALL REFACTOR" in name for name in phase_names)
        learning_phase_exists = any("Learning Library" in name for name in phase_names)
        
        assert refactor_phase_exists, "OVERALL REFACTOR phase missing from YAML"
        assert learning_phase_exists, "Learning library phase missing from YAML"
        
        # Step 13: Cleanup - Delete test plan folder
        shutil.rmtree(plan_folder)
        assert not plan_folder.exists(), "Test plan folder not cleaned up"
        
        print(f"✅ Integration test passed: {plan_folder.name}")
        print(f"   - Folder structure: ✅")
        print(f"   - Naming conventions: ✅")
        print(f"   - Progress tracker: ✅")
        print(f"   - README generation: ✅")
        print(f"   - YAML in execution/: ✅")
        print(f"   - OVERALL REFACTOR phase: ✅")
        print(f"   - Learning library phase: ✅")
        print(f"   - Cleanup: ✅")
    
    def test_folder_structure_disabled(self, planning_orchestrator, cortex_root):
        """
        Test that folder structure is NOT created when disabled.
        
        Validates backward compatibility with flat file structure.
        """
        # Disable folder structure
        planning_orchestrator.folder_structure_enabled = False
        
        from src.orchestrators.planning.planning_orchestrator import PlanData, PlanMetadata, PlanPhaseData
        
        plan_data = PlanData(
            metadata=PlanMetadata(
                title="Test Flat Structure",
                description="Test backward compatibility",
                complexity=PlanComplexity.MEDIUM,
                plan_type=PlanType.INCREMENTAL,
                author="CORTEX Test Suite",
                created=datetime.now(),
                version="1.0.0"
            ),
            definition_of_ready={},
            definition_of_done={},
            phases=[
                PlanPhaseData(
                    phase_name="Phase 1: Test",
                    tasks=["Task 1"],
                    acceptance_criteria=["Done"],
                    dependencies=[]
                )
            ]
        )
        
        rendering_result = planning_orchestrator._render_markdown(
            plan_data=plan_data,
            output_dir=planning_orchestrator.active_plans_dir
        )
        
        assert rendering_result.success
        
        # Verify flat structure (no subfolders)
        plan_file = rendering_result.markdown_path
        assert plan_file.exists()
        
        # Verify NO subfolders created in parent directory
        parent_dir = plan_file.parent
        subfolders = [d for d in parent_dir.iterdir() if d.is_dir()]
        
        # Should not have context/, reports/, artifacts/, tracking/, execution/ as children
        subfolder_names = [d.name for d in subfolders]
        assert "context" not in subfolder_names
        assert "reports" not in subfolder_names
        assert "artifacts" not in subfolder_names
        assert "tracking" not in subfolder_names
        
        # Cleanup
        plan_file.unlink()
        
        print("✅ Backward compatibility test passed (flat structure)")
    
    def test_folder_validation_after_creation(self, planning_orchestrator, cortex_root):
        """
        Test that created folder passes validation.
        """
        from src.orchestrators.planning.planning_orchestrator import PlanData, PlanMetadata, PlanPhaseData
        
        plan_data = PlanData(
            metadata=PlanMetadata(
                title="Test Validation",
                description="Test folder validation",
                complexity=PlanComplexity.HIGH,
                plan_type=PlanType.INCREMENTAL,
                author="CORTEX Test Suite",
                created=datetime.now(),
                version="1.0.0"
            ),
            definition_of_ready={},
            definition_of_done={},
            phases=[
                PlanPhaseData(
                    phase_name="Phase 1: Test",
                    tasks=["Task 1"],
                    acceptance_criteria=["Done"],
                    dependencies=[]
                )
            ]
        )
        
        rendering_result = planning_orchestrator._render_markdown(
            plan_data=plan_data,
            output_dir=planning_orchestrator.active_plans_dir
        )
        
        plan_folder = rendering_result.markdown_path.parent
        
        # Validate folder structure
        is_valid, issues = planning_orchestrator.folder_manager.validate_folder_structure(plan_folder)
        
        assert is_valid, f"Folder validation failed: {issues}"
        assert len(issues) == 0
        
        # Cleanup
        shutil.rmtree(plan_folder)
        
        print("✅ Folder validation test passed")


class TestVersionDetectionIntegration:
    """Integration tests for version detection."""
    
    def test_multiple_plan_versions(self, planning_orchestrator, cortex_root):
        """
        Test that version detection works across multiple plan creations.
        """
        from src.orchestrators.planning.planning_orchestrator import PlanData, PlanMetadata, PlanPhaseData
        
        base_plan_data = PlanData(
            metadata=PlanMetadata(
                title="Versioned Feature",
                description="Test version detection",
                complexity=PlanComplexity.HIGH,
                plan_type=PlanType.INCREMENTAL,
                author="CORTEX Test Suite",
                created=datetime.now(),
                version="1.0.0"
            ),
            definition_of_ready={},
            definition_of_done={},
            phases=[
                PlanPhaseData(
                    phase_name="Phase 1: Test",
                    tasks=["Task 1"],
                    acceptance_criteria=["Done"],
                    dependencies=[]
                )
            ]
        )
        
        created_folders = []
        
        # Create v1
        result_v1 = planning_orchestrator._render_markdown(
            plan_data=base_plan_data,
            output_dir=planning_orchestrator.active_plans_dir
        )
        folder_v1 = result_v1.markdown_path.parent
        created_folders.append(folder_v1)
        assert "versioned-feature-v1" in folder_v1.name
        
        # Create v2 (should auto-increment)
        result_v2 = planning_orchestrator._render_markdown(
            plan_data=base_plan_data,
            output_dir=planning_orchestrator.active_plans_dir
        )
        folder_v2 = result_v2.markdown_path.parent
        created_folders.append(folder_v2)
        assert "versioned-feature-v2" in folder_v2.name
        
        # Create v3
        result_v3 = planning_orchestrator._render_markdown(
            plan_data=base_plan_data,
            output_dir=planning_orchestrator.active_plans_dir
        )
        folder_v3 = result_v3.markdown_path.parent
        created_folders.append(folder_v3)
        assert "versioned-feature-v3" in folder_v3.name
        
        # Verify all versions exist
        assert folder_v1.exists()
        assert folder_v2.exists()
        assert folder_v3.exists()
        
        # Cleanup all versions
        for folder in created_folders:
            shutil.rmtree(folder)
        
        print("✅ Version detection integration test passed (v1, v2, v3)")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
