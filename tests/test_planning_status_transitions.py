"""
Test Planning Status Transitions - Phase 2.3 Implementation
RED Phase: Tests written before implementation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
from datetime import datetime
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestPlanningStatusTransitions:
    """Test suite for plan status transitions"""
    
    @pytest.fixture
    def temp_cortex_with_plans(self, tmp_path):
        """Create CORTEX environment with sample plans"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        planning_path = brain_path / "documents" / "planning"
        
        # Create status directories
        (planning_path / "active").mkdir(parents=True)
        (planning_path / "approved").mkdir(parents=True)
        (planning_path / "completed").mkdir(parents=True)
        
        # Create sample active plan
        active_plan = planning_path / "active" / "PLAN-2025-11-28-test-feature.md"
        active_plan.write_text("""# Test Feature Plan

**Status:** in-progress  
**Created:** 2025-11-28

## Overview

Test feature implementation.
""", encoding='utf-8')
        
        # Create sample approved plan
        approved_plan = planning_path / "approved" / "PLAN-2025-11-27-approved-feature.md"
        approved_plan.write_text("""# Approved Feature Plan

**Status:** approved  
**Created:** 2025-11-27

## Overview

Approved feature ready for implementation.
""", encoding='utf-8')
        
        return cortex_root
    
    def test_approve_plan_moves_to_approved_directory(self, temp_cortex_with_plans):
        """Test that approve_plan() moves plan from active to approved"""
        orchestrator = PlanningOrchestrator(str(temp_cortex_with_plans))
        
        # Approve the active plan
        result = orchestrator.approve_plan("PLAN-2025-11-28-test-feature.md")
        
        # Verify result
        assert result['success'] is True
        assert result['old_status'] == 'active'
        assert result['new_status'] == 'approved'
        
        # Verify file moved
        planning_path = temp_cortex_with_plans / "cortex-brain" / "documents" / "planning"
        active_dir = planning_path / "active"
        approved_dir = planning_path / "approved"
        
        assert not (active_dir / "PLAN-2025-11-28-test-feature.md").exists()
        assert (approved_dir / "PLAN-2025-11-28-test-feature.md").exists()
        
        # Verify status updated in content
        content = (approved_dir / "PLAN-2025-11-28-test-feature.md").read_text(encoding='utf-8')
        assert "**Status:** approved" in content
    
    def test_complete_plan_moves_to_completed_directory(self, temp_cortex_with_plans):
        """Test that complete_plan() moves plan from approved to completed"""
        orchestrator = PlanningOrchestrator(str(temp_cortex_with_plans))
        
        # Complete the approved plan
        result = orchestrator.complete_plan("PLAN-2025-11-27-approved-feature.md")
        
        # Verify result
        assert result['success'] is True
        assert result['old_status'] == 'approved'
        assert result['new_status'] == 'completed'
        
        # Verify file moved
        planning_path = temp_cortex_with_plans / "cortex-brain" / "documents" / "planning"
        approved_dir = planning_path / "approved"
        completed_dir = planning_path / "completed"
        
        assert not (approved_dir / "PLAN-2025-11-27-approved-feature.md").exists()
        assert (completed_dir / "PLAN-2025-11-27-approved-feature.md").exists()
        
        # Verify status updated
        content = (completed_dir / "PLAN-2025-11-27-approved-feature.md").read_text(encoding='utf-8')
        assert "**Status:** completed" in content
    
    def test_completed_plans_include_timestamp(self, temp_cortex_with_plans):
        """Test that completed plans include completion timestamp"""
        orchestrator = PlanningOrchestrator(str(temp_cortex_with_plans))
        
        # Complete plan
        result = orchestrator.complete_plan("PLAN-2025-11-27-approved-feature.md")
        
        # Verify timestamp added
        planning_path = temp_cortex_with_plans / "cortex-brain" / "documents" / "planning"
        completed_dir = planning_path / "completed"
        content = (completed_dir / "PLAN-2025-11-27-approved-feature.md").read_text(encoding='utf-8')
        
        assert "**Completed:**" in content
        # Should have today's date
        today = datetime.now().strftime("%Y-%m-%d")
        assert today in content
    
    def test_approve_plan_fails_if_not_in_active(self, temp_cortex_with_plans):
        """Test that approve_plan() fails if plan not in active directory"""
        orchestrator = PlanningOrchestrator(str(temp_cortex_with_plans))
        
        # Try to approve a plan that's already approved
        result = orchestrator.approve_plan("PLAN-2025-11-27-approved-feature.md")
        
        assert result['success'] is False
        assert 'not found in active' in result['message'].lower()
    
    def test_complete_plan_fails_if_not_in_approved(self, temp_cortex_with_plans):
        """Test that complete_plan() fails if plan not in approved directory"""
        orchestrator = PlanningOrchestrator(str(temp_cortex_with_plans))
        
        # Try to complete a plan that's still in active
        result = orchestrator.complete_plan("PLAN-2025-11-28-test-feature.md")
        
        assert result['success'] is False
        assert 'not found in approved' in result['message'].lower()
    
    def test_status_transition_preserves_content(self, temp_cortex_with_plans):
        """Test that status transitions preserve all content except status"""
        orchestrator = PlanningOrchestrator(str(temp_cortex_with_plans))
        
        # Get original content
        planning_path = temp_cortex_with_plans / "cortex-brain" / "documents" / "planning"
        original_content = (planning_path / "active" / "PLAN-2025-11-28-test-feature.md").read_text(encoding='utf-8')
        
        # Approve plan
        orchestrator.approve_plan("PLAN-2025-11-28-test-feature.md")
        
        # Get new content
        new_content = (planning_path / "approved" / "PLAN-2025-11-28-test-feature.md").read_text(encoding='utf-8')
        
        # Remove status lines for comparison
        original_body = original_content.replace("**Status:** in-progress", "").strip()
        new_body = new_content.replace("**Status:** approved", "").strip()
        
        # Content should be identical except status
        assert "Test feature implementation" in new_body
        assert "## Overview" in new_body
    
    def test_status_transition_updates_existing_status_field(self, temp_cortex_with_plans):
        """Test that status transition updates existing status field rather than adding new one"""
        orchestrator = PlanningOrchestrator(str(temp_cortex_with_plans))
        
        # Approve plan
        orchestrator.approve_plan("PLAN-2025-11-28-test-feature.md")
        
        planning_path = temp_cortex_with_plans / "cortex-brain" / "documents" / "planning"
        content = (planning_path / "approved" / "PLAN-2025-11-28-test-feature.md").read_text(encoding='utf-8')
        
        # Should have exactly one Status field
        status_count = content.count("**Status:**")
        assert status_count == 1, f"Expected 1 Status field, found {status_count}"


class TestGitCheckpointIntegration:
    """Test suite for git checkpoint integration with status transitions"""
    
    def test_approve_plan_creates_git_checkpoint(self, temp_cortex_with_plans):
        """Test that approving plan creates git checkpoint"""
        # This will be implemented when Phase Checkpoint Manager is available
        pass
    
    def test_complete_plan_creates_git_checkpoint(self, temp_cortex_with_plans):
        """Test that completing plan creates git checkpoint"""
        # This will be implemented when Phase Checkpoint Manager is available
        pass
