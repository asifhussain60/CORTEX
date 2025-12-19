"""
Test plan folder structure creation.

Verifies that copilot-chats and user-preferences folders are created.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager


class TestPlanFolderStructure:
    """Test plan folder structure creation."""
    
    def test_planning_orchestrator_creates_standard_folders(self):
        """Test PlanningOrchestrator creates all standard folders."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            with patch('src.operations.modules.orchestration.planning_orchestrator.get_version_manager') as mock_vm:
                mock_vm.return_value.get_version.return_value = "3.1.0"
                
                orchestrator = PlanningOrchestrator(project_root=workspace)
                
                # Create a test plan folder
                plan_folder = workspace / "test-plan"
                content = "# Test Plan\n"
                
                orchestrator._write_master_plan_file(plan_folder, content)
                
                # Verify standard folders created
                assert (plan_folder / "context").exists(), "context/ folder missing"
                assert (plan_folder / "reports").exists(), "reports/ folder missing"
                assert (plan_folder / "artifacts").exists(), "artifacts/ folder missing"
                assert (plan_folder / "artifacts" / "copilot-chats").exists(), "artifacts/copilot-chats/ folder missing"
                assert (plan_folder / "artifacts" / "user-preferences").exists(), "artifacts/user-preferences/ folder missing"
                assert (plan_folder / "tracking").exists(), "tracking/ folder missing"
                assert (plan_folder / "sub-plans").exists(), "sub-plans/ folder missing"
                assert (plan_folder / "00-master-plan.md").exists(), "00-master-plan.md missing"
    
    def test_temp_plan_manager_creates_standard_folders(self):
        """Test TempPlanManager creates all standard folders on approval."""
        with tempfile.TemporaryDirectory() as tmpdir:
            workspace = Path(tmpdir)
            
            # Create required directories
            (workspace / "cortex-brain" / "documents" / "planning" / "features" / "active").mkdir(parents=True)
            (workspace / "cortex-brain" / "documents" / "planning" / "features" / "approved").mkdir(parents=True)
            (workspace / "cortex-brain" / "metrics").mkdir(parents=True)
            
            manager = TemporaryPlanManager(project_root=workspace)
            
            # Create temporary plan
            temp_plan = manager.create_temporary_plan(
                user_request="Test feature",
                complexity_tier=2,
                approach="Test approach",
                phases=[{"name": "Test Phase", "description": "Test", "tasks": ["Task 1"]}],
                estimated_time="2h"
            )
            
            plan_id = temp_plan.plan_id
            
            # Approve plan and convert to full plan (triggers folder creation)
            manager.approve_temporary_plan(plan_id)
            manager.convert_to_full_plan(plan_id)
            
            # Get active folder path (plan moved from approved to active after conversion)
            active_folder = workspace / "cortex-brain" / "documents" / "planning" / "features" / "active" / plan_id
            
            # Get active folder path (plan moved from approved to active after conversion)
            active_folder = workspace / "cortex-brain" / "documents" / "planning" / "features" / "active" / plan_id
            
            # Verify standard folders created
            assert (active_folder / "context").exists(), "context/ folder missing"
            assert (active_folder / "reports").exists(), "reports/ folder missing"
            assert (active_folder / "artifacts").exists(), "artifacts/ folder missing"
            assert (active_folder / "artifacts" / "copilot-chats").exists(), "artifacts/copilot-chats/ folder missing"
            assert (active_folder / "artifacts" / "user-preferences").exists(), "artifacts/user-preferences/ folder missing"
            assert (active_folder / "tracking").exists(), "tracking/ folder missing"
            assert (active_folder / "sub-plans").exists(), "sub-plans/ folder missing"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
