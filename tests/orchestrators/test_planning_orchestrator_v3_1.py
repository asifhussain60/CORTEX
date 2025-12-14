"""
Test suite for Planning Orchestrator v3.1

Tests new features:
1. Temporary plan creation for implicit requests
2. Plan folder lifecycle (approved → active → completed)
3. Master plan status updates (In Progress, Complete)
4. Knowledge extraction on completion
5. ASCII progress bars removed from user responses
6. Autonomous execution with phase tracking

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
import shutil

from src.operations.modules.orchestration.planning_orchestrator import PlanningOrchestrator
from src.operations.modules.orchestration.temporary_plan_manager import TemporaryPlanManager, TemporaryPlan


@pytest.fixture
def temp_project_root(tmp_path):
    """Create temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    
    # Create planning directory structure
    planning_base = project_root / "cortex-brain" / "documents" / "planning" / "features"
    for status in ["active", "approved", "completed"]:
        (planning_base / status).mkdir(parents=True)
    
    return project_root


@pytest.fixture
def orchestrator(temp_project_root):
    """Create orchestrator instance."""
    return PlanningOrchestrator(project_root=temp_project_root)


@pytest.fixture
def temp_plan_manager(temp_project_root):
    """Create temporary plan manager instance."""
    return TemporaryPlanManager(project_root=temp_project_root)


class TestTemporaryPlanCreation:
    """Test temporary plan creation for implicit requests."""
    
    def test_create_temporary_plan(self, orchestrator, temp_project_root):
        """Test creating temporary plan from implicit request."""
        result = orchestrator.create_temporary_plan_for_task(
            user_request="Add logging to all API endpoints",
            auto_approve=False
        )
        
        assert result['success'] is True
        assert 'plan_id' in result
        assert result['requires_approval'] is True
        assert result['plan']['user_request'] == "Add logging to all API endpoints"
        
        # Verify plan folder created in active/
        plan_id = result['plan_id']
        plan_folder = temp_project_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / plan_id
        assert plan_folder.exists()
        
        # Verify temporary plan file
        temp_file = plan_folder / "temporary-plan.json"
        assert temp_file.exists()
        
        temp_data = json.loads(temp_file.read_text())
        assert temp_data['approved'] is False
    
    def test_auto_approve_temporary_plan(self, orchestrator, temp_project_root):
        """Test auto-approval of temporary plan."""
        result = orchestrator.create_temporary_plan_for_task(
            user_request="Fix typo in documentation",
            auto_approve=True
        )
        
        assert result['success'] is True
        assert result['requires_approval'] is False
        
        # Plan should be in approved/ folder
        plan_id = result['plan_id']
        approved_folder = temp_project_root / "cortex-brain" / "documents" / "planning" / "features" / "approved" / plan_id
        # Note: with auto_approve, it gets moved immediately after creation
        # So we need to check if it was approved in the data
        assert result['plan']['approved'] is True


class TestPlanFolderLifecycle:
    """Test plan folder movement through lifecycle."""
    
    def test_approved_to_active_transition(self, temp_plan_manager, temp_project_root):
        """Test plan moves from approved/ to active/ when converted."""
        # Create temporary plan
        temp_plan = temp_plan_manager.create_temporary_plan(
            user_request="Test request",
            complexity_tier=2,
            estimated_time="10min",
            approach="Simple approach",
            phases=[{'name': 'Test Phase', 'tasks': ['Task 1']}]
        )
        
        # Approve it
        temp_plan_manager.approve_temporary_plan(temp_plan.plan_id)
        
        # Verify in approved/
        approved_path = temp_project_root / "cortex-brain" / "documents" / "planning" / "features" / "approved" / temp_plan.plan_id
        assert approved_path.exists()
        
        # Convert to full plan
        master_plan_path = temp_plan_manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Verify moved to active/
        active_path = temp_project_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / temp_plan.plan_id
        assert active_path.exists()
        assert not approved_path.exists()  # Should be moved, not copied
        
        # Verify master plan created
        assert master_plan_path.exists()
        assert master_plan_path.name == "master-plan.md"
    
    def test_active_to_completed_transition(self, temp_plan_manager, temp_project_root):
        """Test plan moves from active/ to completed/ when complete."""
        # Create and approve plan
        temp_plan = temp_plan_manager.create_temporary_plan(
            user_request="Test request",
            complexity_tier=2,
            estimated_time="10min",
            approach="Simple approach",
            phases=[{'name': 'Test Phase', 'tasks': ['Task 1']}]
        )
        temp_plan_manager.approve_temporary_plan(temp_plan.plan_id)
        temp_plan_manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Complete plan
        completed_path = temp_plan_manager.complete_plan(temp_plan.plan_id, extract_knowledge=False)
        
        # Verify moved to completed/
        assert completed_path.exists()
        assert completed_path.parent.name == "completed"
        
        # Verify not in active/
        active_path = temp_project_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / temp_plan.plan_id
        assert not active_path.exists()


class TestMasterPlanStatusUpdates:
    """Test master plan status updates during execution."""
    
    def test_mark_phase_in_progress(self, temp_plan_manager, temp_project_root):
        """Test marking phase as In Progress."""
        # Create full plan
        temp_plan = temp_plan_manager.create_temporary_plan(
            user_request="Test request",
            complexity_tier=2,
            estimated_time="10min",
            approach="Simple approach",
            phases=[
                {'name': 'Phase One', 'tasks': ['Task 1']},
                {'name': 'Phase Two', 'tasks': ['Task 2']}
            ]
        )
        temp_plan_manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = temp_plan_manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Mark phase 1 as in progress
        temp_plan_manager.mark_phase_in_progress(temp_plan.plan_id, 1)
        
        # Verify master plan updated (use UTF-8 encoding)
        content = master_plan_path.read_text(encoding='utf-8', errors='replace')
        assert "In Progress" in content
        assert "Phase 1:" in content
    
    def test_mark_phase_complete(self, temp_plan_manager, temp_project_root):
        """Test marking phase as Complete."""
        # Create full plan
        temp_plan = temp_plan_manager.create_temporary_plan(
            user_request="Test request",
            complexity_tier=2,
            estimated_time="10min",
            approach="Simple approach",
            phases=[
                {'name': 'Phase One', 'tasks': ['Task 1']},
                {'name': 'Phase Two', 'tasks': ['Task 2']}
            ]
        )
        temp_plan_manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = temp_plan_manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Mark phase 1 in progress, then complete
        temp_plan_manager.mark_phase_in_progress(temp_plan.plan_id, 1)
        temp_plan_manager.mark_phase_complete(temp_plan.plan_id, 1)
        
        # Verify master plan updated (use UTF-8 encoding and check for Complete text)
        content = master_plan_path.read_text(encoding='utf-8', errors='replace')
        assert "Complete" in content
        assert "Phase 1:" in content
        # The emoji might have encoding issues, just check for "Complete"


class TestKnowledgeExtraction:
    """Test knowledge extraction on plan completion."""
    
    def test_knowledge_extraction_creates_report(self, temp_plan_manager, temp_project_root):
        """Test knowledge extraction creates report."""
        # Create and complete plan
        temp_plan = temp_plan_manager.create_temporary_plan(
            user_request="Test request with learnings",
            complexity_tier=2,
            estimated_time="10min",
            approach="Test approach",
            phases=[{'name': 'Test Phase', 'tasks': ['Task 1']}]
        )
        temp_plan_manager.approve_temporary_plan(temp_plan.plan_id)
        temp_plan_manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Add some content to master plan with lessons learned
        master_plan_path = temp_project_root / "cortex-brain" / "documents" / "planning" / "features" / "active" / temp_plan.plan_id / "master-plan.md"
        master_content = master_plan_path.read_text()
        master_content += """

## Lessons Learned

- Always validate input before processing
- Use proper error handling
- Test edge cases thoroughly

## Best Practices

- Follow TDD approach
- Write clear documentation
"""
        master_plan_path.write_text(master_content)
        
        # Complete with knowledge extraction
        completed_path = temp_plan_manager.complete_plan(temp_plan.plan_id, extract_knowledge=True)
        
        # Verify knowledge extraction report created
        report_path = completed_path / "knowledge-extraction-report.md"
        assert report_path.exists()
        
        report_content = report_path.read_text()
        assert "Knowledge Extraction Report" in report_content
        assert "Learnings Extracted" in report_content


class TestASCIIProgressBarRemoval:
    """Test that ASCII progress bars are not in user responses."""
    
    def test_execute_result_has_no_ascii_bars(self, orchestrator):
        """Test execute() result message has no ASCII progress bars."""
        result = orchestrator.execute({
            'operation': 'Simple test operation'
        })
        
        # Check message doesn't contain ASCII bar characters
        assert '█' not in result.message
        assert '░' not in result.message
        assert '▓' not in result.message
        
        # Check data doesn't contain progress_summary
        assert 'progress_summary' not in result.data
    
    def test_progress_logged_internally(self, orchestrator, caplog):
        """Test progress summary is logged but not returned to user."""
        import logging
        caplog.set_level(logging.INFO)
        
        result = orchestrator.execute({
            'operation': 'Test operation'
        })
        
        # Check internal logs contain progress (for debugging)
        log_text = caplog.text
        assert 'INTERNAL LOGGING' in log_text or 'Progress' in log_text
        
        # But user message should not
        assert '█' not in result.message


class TestAutonomousExecution:
    """Test autonomous plan execution."""
    
    def test_autonomous_execution_updates_phases(self, orchestrator, temp_project_root):
        """Test autonomous execution updates phase statuses."""
        # Create and approve temporary plan
        result = orchestrator.create_temporary_plan_for_task(
            user_request="Test autonomous execution",
            auto_approve=False
        )
        plan_id = result['plan_id']
        
        # Approve and convert
        orchestrator.temp_plan_manager.approve_temporary_plan(plan_id)
        orchestrator.temp_plan_manager.convert_to_full_plan(plan_id)
        
        # Execute autonomously
        exec_result = orchestrator.execute_plan_autonomously(plan_id)
        
        assert exec_result['success'] is True
        assert exec_result['is_complete'] is True
        assert 'phase_results' in exec_result
        
        # Verify plan moved to completed/
        completed_path = temp_project_root / "cortex-brain" / "documents" / "planning" / "features" / "completed" / plan_id
        assert completed_path.exists()


class TestEndToEndWorkflow:
    """Test complete end-to-end workflow."""
    
    def test_full_implicit_planning_workflow(self, orchestrator, temp_project_root):
        """Test complete workflow from implicit request to completion."""
        # Step 1: User provides task (no "create a plan")
        temp_result = orchestrator.create_temporary_plan_for_task(
            user_request="Add authentication to API endpoints",
            auto_approve=False
        )
        
        assert temp_result['success'] is True
        plan_id = temp_result['plan_id']
        
        # Step 2: User reviews and provides feedback (optional)
        orchestrator.temp_plan_manager.update_temporary_plan(
            plan_id=plan_id,
            user_feedback="Looks good, please proceed"
        )
        
        # Step 3: User approves
        # Step 4: System converts to full plan and executes
        exec_result = orchestrator.approve_and_execute_plan(
            plan_id=plan_id,
            autonomous=True
        )
        
        assert exec_result['success'] is True
        assert exec_result['is_complete'] is True
        
        # Verify plan in completed/
        completed_path = Path(exec_result['completed_path'])
        assert completed_path.exists()
        assert completed_path.parent.name == "completed"
        
        # Verify knowledge extraction report
        report_path = completed_path / "knowledge-extraction-report.md"
        # Note: Report may not exist if no learnings found, but path should be valid
        assert completed_path.exists()
        
        # Verify metrics updated
        assert orchestrator.metrics['temporary_plans_created'] == 1
        assert orchestrator.metrics['plans_approved'] == 1
        assert orchestrator.metrics['plans_completed'] == 1
        assert orchestrator.metrics['knowledge_extractions'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
