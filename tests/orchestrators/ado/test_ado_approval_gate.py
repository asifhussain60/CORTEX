"""
Test Suite: ADO Approval Gate Phase

RED Phase Tests - Task 5: Approval Gate
These tests define expected behavior for approval workflow, DoD validation, preview display.

Task 5 Scope:
- DoD (Definition of Done) validation
- Work item preview formatting
- User approval gate (interactive)
- Modification loop support

Expected: All tests FAIL initially (RED phase)
Then: Implement code to make tests pass (GREEN phase)
Finally: Refactor while keeping tests green (REFACTOR phase)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).resolve().parents[5]))

from src.orchestrators.ado.ado_orchestrator import ADOOrchestrator, ADOPhase


class TestDoDValidation:
    """
    RED Phase Tests for DoD (Definition of Done) Validation
    
    Requirements:
    - DoD completeness scoring (0-100)
    - Test coverage requirement (≥80%)
    - Documentation requirement check
    - Code review requirement flag
    """
    
    def test_validate_dod_completeness_all_criteria(self):
        """
        Test: DoD validation with all criteria met
        
        Expected DoD Criteria:
        - Test coverage ≥80%
        - Documentation updated
        - Code review completed
        - Acceptance criteria verified
        
        Expected (RED): Method not implemented
        Expected (GREEN): 100% completeness score
        """
        orchestrator = ADOOrchestrator()
        
        # Complete DoD data
        dod_data = {
            "test_coverage": 85,
            "documentation_updated": True,
            "code_review_completed": True,
            "acceptance_criteria_verified": True
        }
        
        # Validate DoD
        validation_result = orchestrator._validate_dod_completeness(dod_data)
        
        # Verify completeness
        assert validation_result["is_complete"] is True
        assert validation_result["percentage"] == 100
        assert validation_result["missing_criteria"] == []
    
    def test_validate_dod_completeness_partial(self):
        """
        Test: DoD validation with partial criteria met
        
        Expected (RED): Method not implemented
        Expected (GREEN): Partial score with missing criteria list
        """
        orchestrator = ADOOrchestrator()
        
        # Partial DoD data
        dod_data = {
            "test_coverage": 85,
            "documentation_updated": False,
            "code_review_completed": True,
            "acceptance_criteria_verified": True
        }
        
        # Validate DoD
        validation_result = orchestrator._validate_dod_completeness(dod_data)
        
        # Verify partial completeness
        assert validation_result["is_complete"] is False
        assert 70 <= validation_result["percentage"] < 100
        assert "documentation_updated" in validation_result["missing_criteria"]
    
    def test_validate_dod_test_coverage_threshold(self):
        """
        Test: DoD validation enforces ≥80% test coverage
        
        Expected (RED): Method not implemented
        Expected (GREEN): Fails validation if coverage <80%
        """
        orchestrator = ADOOrchestrator()
        
        # Low test coverage
        dod_data = {
            "test_coverage": 65,
            "documentation_updated": True,
            "code_review_completed": True,
            "acceptance_criteria_verified": True
        }
        
        # Validate DoD
        validation_result = orchestrator._validate_dod_completeness(dod_data)
        
        # Verify test coverage enforced
        assert validation_result["is_complete"] is False
        assert "test_coverage" in validation_result["missing_criteria"]
        assert validation_result["test_coverage_percentage"] == 65


class TestWorkItemPreview:
    """
    RED Phase Tests for Work Item Preview Formatting
    
    Requirements:
    - Hierarchical display (indented)
    - Summary statistics (count, story points)
    - Color-coded work item types
    - TDD requirements display
    """
    
    def test_format_work_item_preview_hierarchy(self):
        """
        Test: Format work item preview with hierarchy visualization
        
        Expected Output:
        Epic: User Authentication (21 points)
          Feature: Login System (13 points)
            Story: User Login (5 points)
              Task: Login Form (2 points)
        
        Expected (RED): Method not implemented
        Expected (GREEN): Formatted preview string with indentation
        """
        orchestrator = ADOOrchestrator()
        
        # Sample hierarchy
        hierarchy = {
            "epic": {
                "title": "Epic: User Authentication",
                "story_points": 21,
                "work_item_type": "Epic"
            },
            "features": [
                {
                    "title": "Feature: Login System",
                    "story_points": 13,
                    "work_item_type": "Feature",
                    "stories": [
                        {
                            "title": "Story: User Login",
                            "story_points": 5,
                            "work_item_type": "User Story",
                            "tasks": [
                                {
                                    "title": "Task: Login Form",
                                    "story_points": 2,
                                    "work_item_type": "Task"
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Format preview
        preview = orchestrator._format_work_item_preview(hierarchy)
        
        # Verify hierarchical display
        assert "Epic: User Authentication" in preview
        assert "21 points" in preview
        assert "  Feature: Login System" in preview  # Indented
        assert "    Story: User Login" in preview    # More indented
        assert "      Task: Login Form" in preview   # Most indented
    
    def test_format_work_item_preview_summary(self):
        """
        Test: Preview includes summary statistics
        
        Expected Summary:
        - Total work items: 10
        - Total story points: 42
        - Epics: 1, Features: 2, Stories: 4, Tasks: 3
        
        Expected (RED): Method not implemented
        Expected (GREEN): Summary section in preview
        """
        orchestrator = ADOOrchestrator()
        
        # Sample hierarchy with multiple items
        hierarchy = {
            "features": [
                {
                    "title": "Feature 1",
                    "story_points": 13,
                    "stories": [
                        {
                            "title": "Story 1",
                            "story_points": 5,
                            "tasks": [
                                {"title": "Task 1", "story_points": 2},
                                {"title": "Task 2", "story_points": 3}
                            ]
                        }
                    ]
                }
            ]
        }
        
        # Format preview
        preview = orchestrator._format_work_item_preview(hierarchy)
        
        # Verify summary statistics
        assert "Total work items:" in preview
        assert "Total story points:" in preview
        assert "Features:" in preview
        assert "Stories:" in preview
        assert "Tasks:" in preview


class TestApprovalGate:
    """
    RED Phase Tests for Approval Gate Workflow
    
    Requirements:
    - User approval prompt
    - Approval/rejection handling
    - Modification loop support
    - Skip approval if auto_approve=True
    """
    
    def test_approval_gate_user_approves(self):
        """
        Test: Approval gate with user approval
        
        Expected Flow:
        1. Show work item preview
        2. Prompt user for approval
        3. User types "yes" or "approve"
        4. Return approved=True
        
        Expected (RED): Method not implemented
        Expected (GREEN): Returns approved result
        """
        orchestrator = ADOOrchestrator()
        
        # Mock user input
        with patch('builtins.input', return_value='yes'):
            hierarchy = {"features": [{"title": "Test Feature"}]}
            
            # Request approval
            approval_result = orchestrator._request_approval(hierarchy)
            
            # Verify approval
            assert approval_result["approved"] is True
            assert approval_result["action"] == "proceed"
    
    def test_approval_gate_user_rejects(self):
        """
        Test: Approval gate with user rejection
        
        Expected Flow:
        1. Show work item preview
        2. Prompt user for approval
        3. User types "no" or "reject"
        4. Return approved=False with modification_requested=True
        
        Expected (RED): Method not implemented
        Expected (GREEN): Returns rejection with modification flag
        """
        orchestrator = ADOOrchestrator()
        
        # Mock user input
        with patch('builtins.input', return_value='no'):
            hierarchy = {"features": [{"title": "Test Feature"}]}
            
            # Request approval
            approval_result = orchestrator._request_approval(hierarchy)
            
            # Verify rejection
            assert approval_result["approved"] is False
            assert approval_result["action"] == "modify"
    
    def test_approval_gate_auto_approve(self):
        """
        Test: Approval gate skips prompt if auto_approve=True
        
        Expected (RED): Method not implemented
        Expected (GREEN): Returns approved=True without prompting
        """
        orchestrator = ADOOrchestrator()
        
        hierarchy = {"features": [{"title": "Test Feature"}]}
        
        # Request approval with auto_approve
        approval_result = orchestrator._request_approval(hierarchy, auto_approve=True)
        
        # Verify auto-approval
        assert approval_result["approved"] is True
        assert approval_result["action"] == "proceed"
        assert approval_result["auto_approved"] is True


class TestModificationLoop:
    """
    RED Phase Tests for Modification Loop
    
    Requirements:
    - Collect modification feedback
    - Re-run generation with feedback
    - Re-validate DoD
    - Limit iteration count (max 3)
    """
    
    def test_modification_loop_collect_feedback(self):
        """
        Test: Collect user feedback for modifications
        
        Expected Feedback Types:
        - Add more stories
        - Remove specific tasks
        - Adjust story points
        - Add acceptance criteria
        
        Expected (RED): Method not implemented
        Expected (GREEN): Returns structured feedback
        """
        orchestrator = ADOOrchestrator()
        
        # Mock user feedback
        with patch('builtins.input', return_value='Add more acceptance criteria'):
            feedback = orchestrator._collect_modification_feedback()
            
            # Verify feedback structure
            assert "feedback_text" in feedback
            assert "modification_type" in feedback
            assert feedback["feedback_text"] == "Add more acceptance criteria"
    
    def test_modification_loop_max_iterations(self):
        """
        Test: Modification loop limits iterations to 3
        
        Expected (RED): Method not implemented
        Expected (GREEN): Raises error after 3 rejections
        """
        orchestrator = ADOOrchestrator()
        
        # Mock repeated rejections
        with patch('builtins.input', return_value='no'):
            hierarchy = {"features": [{"title": "Test"}]}
            
            # Attempt approval loop (should fail after 3 iterations)
            with pytest.raises(Exception) as exc_info:
                orchestrator._approval_loop(hierarchy, max_iterations=3)
            
            assert "Maximum modification iterations" in str(exc_info.value)


# ===== TEST EXECUTION SUMMARY =====
# Expected Initial State (RED Phase):
# - 10 tests defined
# - All tests should FAIL (methods not implemented)
#
# After GREEN Phase Implementation:
# - All tests should PASS
#
# After REFACTOR Phase:
# - Tests remain PASSING
# - Code quality improved
