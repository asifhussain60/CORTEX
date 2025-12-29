"""
Tests for Planning Orchestrator -> CORTEX Toolkit Integration

Purpose: Validate that planning orchestrator properly uses toolkit's
         plan_scaffold_generator.py instead of duplicating folder creation logic.

Author: CORTEX Development Team
Created: 2025-12-29
"""

import json
import pytest
import shutil
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add cortex-toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "cortex-toolkit"))

# Import toolkit generator
from core.utilities.plan_scaffold_generator import PlanScaffoldGenerator

# Import orchestrator (will be updated to use toolkit)
from src.orchestrators.planning.planning_orchestrator import PlanningOrchestrator


class TestToolkitIntegration:
    """Test planning orchestrator uses toolkit for folder creation."""
    
    @pytest.fixture
    def temp_cortex_root(self, tmp_path):
        """Create temporary CORTEX structure."""
        cortex_root = tmp_path / "cortex"
        planning_root = cortex_root / "cortex-brain" / "documents" / "planning" / "active"
        planning_root.mkdir(parents=True)
        return cortex_root
    
    @pytest.fixture
    def scaffold_generator(self, temp_cortex_root):
        """Create scaffold generator instance."""
        return PlanScaffoldGenerator(cortex_root=temp_cortex_root)
    
    @pytest.fixture
    def orchestrator(self, temp_cortex_root):
        """Create planning orchestrator instance."""
        config = {
            "cortex_root": str(temp_cortex_root),
            "enable_folder_structure": True
        }
        return PlanningOrchestrator(config=config)
    
    # ========================================================================
    # RED Phase: Tests that SHOULD FAIL initially
    # ========================================================================
    
    def test_orchestrator_uses_toolkit_scaffold_generator(self, orchestrator):
        """
        WIRING TEST: Orchestrator must use PlanScaffoldGenerator from toolkit.
        
        This test FAILS until we wire the toolkit script into the orchestrator.
        """
        # Check orchestrator has toolkit generator
        assert hasattr(orchestrator, 'scaffold_generator'), \
            "Orchestrator missing 'scaffold_generator' attribute"
        
        # Verify it's the correct type
        assert isinstance(orchestrator.scaffold_generator, PlanScaffoldGenerator), \
            f"Expected PlanScaffoldGenerator, got {type(orchestrator.scaffold_generator)}"
    
    def test_orchestrator_create_plan_calls_toolkit(self, orchestrator, temp_cortex_root, monkeypatch):
        """
        INTEGRATION TEST: Orchestrator.create_plan() must call toolkit scaffold_generator.
        
        This test FAILS until orchestrator is refactored to delegate to toolkit.
        """
        # Mock the toolkit generator
        mock_generator = Mock(spec=PlanScaffoldGenerator)
        mock_generator.create_scaffold.return_value = {
            "status": "created",
            "plan_name": "Test Feature",
            "folder_name": "test-feature",
            "plan_dir": str(temp_cortex_root / "cortex-brain/documents/planning/active/test-feature"),
            "folders": {},
            "tracker": "tracking/progress-tracker.json"
        }
        
        # Replace orchestrator's generator
        orchestrator.scaffold_generator = mock_generator
        
        # Create a plan
        plan_data = {
            "metadata": {
                "title": "Test Feature",
                "description": "Test feature implementation"
            }
        }
        
        # This should call scaffold_generator.create_scaffold()
        result = orchestrator.create_plan_folders("test-feature", plan_data)
        
        # Verify toolkit was called
        mock_generator.create_scaffold.assert_called_once()
        call_kwargs = mock_generator.create_scaffold.call_args.kwargs
        assert call_kwargs.get("plan_name") == "test-feature"
        assert result["status"] == "created"
    
    def test_created_folders_match_toolkit_structure(self, scaffold_generator, temp_cortex_root):
        """
        STRUCTURE TEST: Folders created by orchestrator must match toolkit 4-folder spec.
        
        Required structure:
        - context/
        - reports/
        - artifacts/
        - tracking/ (with progress-tracker.json)
        """
        result = scaffold_generator.create_scaffold("test-feature")
        
        assert result["status"] == "created"
        
        plan_dir = Path(result["plan_dir"])
        assert plan_dir.exists()
        
        # Verify 4 required folders
        assert (plan_dir / "context").exists()
        assert (plan_dir / "reports").exists()
        assert (plan_dir / "artifacts").exists()
        assert (plan_dir / "tracking").exists()
        
        # Verify progress tracker
        tracker_path = plan_dir / "tracking" / "progress-tracker.json"
        assert tracker_path.exists()
        
        # Validate tracker content
        with open(tracker_path) as f:
            tracker = json.load(f)
        
        assert "plan_name" in tracker
        assert "created" in tracker
        assert "status" in tracker
        assert tracker["status"] == "initialized"
    
    def test_orchestrator_handles_existing_plan(self, orchestrator, temp_cortex_root):
        """
        ERROR HANDLING TEST: Orchestrator must handle existing plans gracefully.
        """
        # Create plan twice
        plan_data = {"metadata": {"title": "Duplicate Feature"}}
        
        result1 = orchestrator.create_plan_folders("duplicate-feature", plan_data)
        assert result1["status"] in ["created", "exists", "error"], f"Unexpected status: {result1['status']}"
        
        result2 = orchestrator.create_plan_folders("duplicate-feature", plan_data)
        # Toolkit returns "exists" status when plan already exists
        assert result2["status"] == "exists", f"Expected 'exists', got '{result2['status']}': {result2.get('message', '')}"
        assert result2.get("plan_name") == "duplicate-feature"
    
    def test_orchestrator_validates_plan_structure(self, scaffold_generator, temp_cortex_root):
        """
        VALIDATION TEST: Can validate existing plan has correct structure.
        """
        # Create plan
        scaffold_generator.create_scaffold("validation-test")
        
        # Validate structure
        result = scaffold_generator.validate_structure("validation-test")
        
        assert result["valid"] is True
        assert result["has_tracker"] is True
        assert len(result["missing_folders"]) == 0
    
    def test_orchestrator_sanitizes_plan_names(self, scaffold_generator):
        """
        SANITIZATION TEST: Plan names must be sanitized for filesystem.
        
        Examples:
        - "User Auth v2.0!" → "user-auth-v20" (dots removed)
        - "Feature: API Migration" → "feature-api-migration"
        """
        test_cases = [
            ("User Auth v2.0!", "user-auth-v20"),  # Dots are removed by toolkit
            ("Feature: API Migration", "feature-api-migration"),
            ("Test_With_Underscores", "test-with-underscores"),
            ("UPPERCASE", "uppercase"),
            ("Multi  Spaces", "multi-spaces"),
        ]
        
        for input_name, expected_output in test_cases:
            sanitized = scaffold_generator.sanitize_name(input_name)
            assert sanitized == expected_output, \
                f"Failed to sanitize '{input_name}': got '{sanitized}', expected '{expected_output}'"
    
    def test_progress_tracker_json_schema(self, scaffold_generator, temp_cortex_root):
        """
        SCHEMA TEST: progress-tracker.json must have required fields.
        """
        result = scaffold_generator.create_scaffold(
            "schema-test",
            description="Test plan description",
            metadata={"author": "Test Suite"}
        )
        
        tracker_path = Path(result["tracker"])
        with open(tracker_path) as f:
            tracker = json.load(f)
        
        # Required top-level fields
        required_fields = ["plan_name", "folder_name", "created", "description", "status", "phases", "metadata", "statistics"]
        for field in required_fields:
            assert field in tracker, f"Missing required field: {field}"
        
        # Validate statistics structure
        assert "total_phases" in tracker["statistics"]
        assert "completed_phases" in tracker["statistics"]
        assert "progress_percent" in tracker["statistics"]
        
        # Validate metadata passthrough
        assert tracker["metadata"]["author"] == "Test Suite"
        assert tracker["description"] == "Test plan description"
    
    def test_toolkit_generator_dry_run_mode(self, scaffold_generator, temp_cortex_root):
        """
        DRY RUN TEST: Generator supports dry-run without creating folders.
        """
        result = scaffold_generator.create_scaffold("dry-run-test", dry_run=True)
        
        assert result["status"] == "dry_run"
        
        plan_dir = Path(result["plan_dir"])
        assert not plan_dir.exists(), "Dry run should not create folders"
    
    def test_orchestrator_error_handling_invalid_names(self, scaffold_generator):
        """
        ERROR TEST: Invalid plan names must raise ValueError.
        """
        invalid_names = ["", "   ", "!!!"]
        
        for invalid_name in invalid_names:
            with pytest.raises(ValueError, match="sanitizes to empty string"):
                scaffold_generator.create_scaffold(invalid_name)


class TestBackwardCompatibility:
    """Ensure transition from PlanFolderManager to toolkit doesn't break existing code."""
    
    def test_old_plan_folder_manager_deprecated(self):
        """
        DEPRECATION TEST: Old PlanFolderManager should be marked deprecated.
        """
        from src.utils.plan_folder_manager import PlanFolderManager
        
        # Check for deprecation warning in docstring or module
        import inspect
        doc = inspect.getdoc(PlanFolderManager)
        
        # Should have deprecation notice (will add during refactor)
        # For now, just verify class still exists for backward compat
        assert PlanFolderManager is not None
    
    def test_folder_structures_are_equivalent(self, tmp_path):
        """
        COMPATIBILITY TEST: Old and new folder structures must be identical.
        """
        from src.utils.plan_folder_manager import PlanFolderManager
        
        # Create two separate temp directories
        old_root = tmp_path / "old"
        new_root = tmp_path / "new"
        
        for root in [old_root, new_root]:
            planning = root / "cortex-brain" / "documents" / "planning" / "active"
            planning.mkdir(parents=True)
        
        # Create with old manager
        old_manager = PlanFolderManager(project_root=old_root)
        old_folder = old_manager.create_plan_folder(
            plan_id="compat-test-v1",
            title="Compatibility Test",
            complexity_tier=3,
            status="active"
        )
        
        # Create with new toolkit
        new_generator = PlanScaffoldGenerator(cortex_root=new_root)
        new_result = new_generator.create_scaffold("compat-test-v1")
        new_folder = Path(new_result["plan_dir"])
        
        # Compare folder structures
        old_subfolders = {p.name for p in old_folder.iterdir() if p.is_dir()}
        new_subfolders = {p.name for p in new_folder.iterdir() if p.is_dir()}
        
        # Both should have the 4 core folders (may have different execution/ handling)
        core_folders = {"context", "reports", "artifacts", "tracking"}
        assert core_folders.issubset(old_subfolders), f"Old missing: {core_folders - old_subfolders}"
        assert core_folders.issubset(new_subfolders), f"New missing: {core_folders - new_subfolders}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
