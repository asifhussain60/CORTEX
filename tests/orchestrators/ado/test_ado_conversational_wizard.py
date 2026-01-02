"""
Tests for ADO Conversational Wizard

Comprehensive test suite for multi-turn interactive work item creation wizard.
Tests all 7 stages, validation logic, error handling, and edge cases.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, MagicMock
from typing import Dict, Any

from src.orchestrators.ado.ado_conversational_wizard import (
    ADOConversationalWizard,
    WizardStage,
    WizardResponse,
    WorkItemData
)


class TestADOConversationalWizard:
    """Test suite for ADO Conversational Wizard."""
    
    @pytest.fixture
    def wizard(self):
        """Create wizard instance for testing."""
        return ADOConversationalWizard()
    
    @pytest.fixture
    def wizard_with_mocks(self):
        """Create wizard with mock dependencies."""
        state_db = Mock()
        vision_api = Mock()
        return ADOConversationalWizard(state_db=state_db, vision_api=vision_api)
    
    # ===== Initialization Tests =====
    
    def test_wizard_initialization(self, wizard):
        """Test wizard initializes correctly."""
        assert wizard.sessions == {}
        assert wizard.state_db is None
        assert wizard.vision_api is None
    
    def test_wizard_initialization_with_dependencies(self, wizard_with_mocks):
        """Test wizard initializes with dependencies."""
        assert wizard_with_mocks.state_db is not None
        assert wizard_with_mocks.vision_api is not None
    
    # ===== Start Wizard Tests =====
    
    def test_start_wizard_basic(self, wizard):
        """Test starting wizard with basic input."""
        response = wizard.start_wizard("User authentication system")
        
        assert response.session_id is not None
        assert response.stage == WizardStage.BASIC_INFO
        assert "Basic Information" in response.prompt
        assert response.context["feature_name"] == "User authentication system"
        assert len(wizard.sessions) == 1
    
    def test_start_wizard_extracts_feature_name(self, wizard):
        """Test feature name extraction from various inputs."""
        test_cases = [
            ("Create user login", "User login"),
            ("Implement dashboard", "Dashboard"),
            ("Build API endpoint", "API endpoint"),
            ("Add notification system", "Notification system")
        ]
        
        for input_text, expected_name in test_cases:
            response = wizard.start_wizard(input_text)
            assert expected_name in response.context["feature_name"]
    
    def test_start_wizard_handles_empty_input(self, wizard):
        """Test wizard handles empty feature name."""
        response = wizard.start_wizard("")
        assert response.context["feature_name"] == "Untitled Feature"
    
    # ===== Basic Info Stage Tests =====
    
    def test_process_basic_info_full(self, wizard):
        """Test processing complete basic info."""
        response = wizard.start_wizard("Authentication feature")
        session_id = response.session_id
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="Feature, High priority, XL"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert data.work_item_type == "Feature"
        assert data.priority == "High"
        assert data.effort == "XL"
        assert response.stage == WizardStage.ACCEPTANCE_CRITERIA
    
    def test_process_basic_info_partial(self, wizard):
        """Test processing partial basic info (uses defaults)."""
        response = wizard.start_wizard("API endpoint")
        session_id = response.session_id
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="Story"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert data.work_item_type == "Story"
        assert data.priority == "Medium"  # default
        assert data.effort == "M"  # default
    
    def test_process_basic_info_continue(self, wizard):
        """Test 'continue' skips basic info (uses defaults)."""
        response = wizard.start_wizard("Feature X")
        session_id = response.session_id
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="continue"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert data.work_item_type == "Story"  # default
        assert data.priority == "Medium"
        assert data.effort == "M"
    
    def test_process_basic_info_various_formats(self, wizard):
        """Test different input formats for basic info."""
        test_cases = [
            ("Bug, Low, S", "Bug", "Low", "S"),
            ("Epic, HIGH, m", "Epic", "High", "M"),
            ("Task, medium priority, Large", "Task", "Medium", "L"),
        ]
        
        for user_input, expected_type, expected_priority, expected_effort in test_cases:
            response = wizard.start_wizard("Test feature")
            session_id = response.session_id
            
            wizard.process_response(session_id=session_id, user_input=user_input)
            data = wizard.sessions[session_id]["data"]
            
            assert data.work_item_type == expected_type
            assert data.priority == expected_priority
            assert data.effort == expected_effort
    
    # ===== Acceptance Criteria Stage Tests =====
    
    def test_process_acceptance_criteria_list(self, wizard):
        """Test processing acceptance criteria as list."""
        response = wizard.start_wizard("Login feature")
        session_id = response.session_id
        
        # Complete basic info
        wizard.process_response(session_id=session_id, user_input="continue")
        
        # Provide acceptance criteria
        response = wizard.process_response(
            session_id=session_id,
            user_input="1. User can login\n2. Session persists\n3. Logout works"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert len(data.acceptance_criteria) == 3
        assert "User can login" in data.acceptance_criteria[0]
        assert response.stage == WizardStage.DEFINITION_OF_READY
    
    def test_process_acceptance_criteria_single_line(self, wizard):
        """Test processing single acceptance criterion."""
        response = wizard.start_wizard("Feature X")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="User can perform action"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert len(data.acceptance_criteria) == 1
        assert data.acceptance_criteria[0] == "User can perform action"
    
    def test_process_acceptance_criteria_skip(self, wizard):
        """Test skipping acceptance criteria."""
        response = wizard.start_wizard("Feature Y")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="skip"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert data.acceptance_criteria == ["[Auto-generated during review]"]
    
    def test_process_acceptance_criteria_vision_context(self, wizard):
        """Test acceptance criteria with vision context."""
        response = wizard.start_wizard("UI Feature")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        
        vision_context = {
            "ui_elements": ["Login button", "Password field", "Remember me checkbox"]
        }
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="Using screenshot",
            vision_context=vision_context
        )
        
        data = wizard.sessions[session_id]["data"]
        assert len(data.acceptance_criteria) == 3
        assert data.vision_context is not None
    
    def test_process_acceptance_criteria_validation_error(self, wizard):
        """Test validation error for empty acceptance criteria."""
        response = wizard.start_wizard("Feature Z")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input=""
        )
        
        # Should stay on same stage with validation error
        assert response.stage == WizardStage.ACCEPTANCE_CRITERIA
        assert len(response.validation_errors) > 0
    
    # ===== Definition of Ready Tests =====
    
    def test_process_dor_full(self, wizard):
        """Test processing complete DoR with all categories."""
        response = wizard.start_wizard("Feature A")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="User can do X")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="Assumptions: Users have email. Constraints: Use OAuth. Dependencies: API ready"
        )
        
        data = wizard.sessions[session_id]["data"]
        dor = data.definition_of_ready
        assert len(dor["assumptions"]) > 0
        assert len(dor["constraints"]) > 0
        assert len(dor["dependencies"]) > 0
        assert response.stage == WizardStage.DEFINITION_OF_DONE
    
    def test_process_dor_skip(self, wizard):
        """Test skipping DoR."""
        response = wizard.start_wizard("Feature B")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="User can do X")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="skip"
        )
        
        data = wizard.sessions[session_id]["data"]
        dor = data.definition_of_ready
        assert "Standard assumptions apply" in dor["assumptions"]
        assert "No specific constraints" in dor["constraints"]
    
    def test_process_dor_no_dependencies(self, wizard):
        """Test DoR with no dependencies."""
        response = wizard.start_wizard("Feature C")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="Assumptions: Test. Dependencies: None"
        )
        
        data = wizard.sessions[session_id]["data"]
        # Dependencies should be empty or handled gracefully
        assert isinstance(data.definition_of_ready["dependencies"], list)
    
    # ===== Definition of Done Tests =====
    
    def test_process_dod_list(self, wizard):
        """Test processing DoD as list."""
        response = wizard.start_wizard("Feature D")
        session_id = response.session_id
        
        # Navigate to DoD stage
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="1. Code complete\n2. Tests pass\n3. Deployed"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert len(data.definition_of_done) == 3
        assert "Code complete" in data.definition_of_done[0]
    
    def test_process_dod_comma_separated(self, wizard):
        """Test processing DoD as comma-separated values."""
        response = wizard.start_wizard("Feature E")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="Code complete, Tests pass, Documentation updated"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert len(data.definition_of_done) == 3
    
    def test_process_dod_skip(self, wizard):
        """Test skipping DoD."""
        response = wizard.start_wizard("Feature F")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="standard"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert len(data.definition_of_done) >= 4  # Standard checklist
        assert "Code complete" in data.definition_of_done
    
    # ===== Estimation Tests =====
    
    def test_process_estimation_explicit(self, wizard):
        """Test processing explicit story points."""
        response = wizard.start_wizard("Feature G")
        session_id = response.session_id
        
        # Navigate to estimation
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="8 points"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert data.story_points == 8
    
    def test_process_estimation_auto(self, wizard):
        """Test auto-calculating story points from effort."""
        response = wizard.start_wizard("Feature H")
        session_id = response.session_id
        
        # Set effort to L
        wizard.process_response(session_id=session_id, user_input="Story, Medium, L")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="skip"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert data.story_points == 8  # L maps to 8
    
    def test_process_estimation_invalid_range(self, wizard):
        """Test validation error for story points out of range."""
        response = wizard.start_wizard("Feature I")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="100 points"
        )
        
        # Should stay on estimation with error
        assert response.stage == WizardStage.ESTIMATION
        assert len(response.validation_errors) > 0
    
    # ===== Dependencies Tests =====
    
    def test_process_dependencies_list(self, wizard):
        """Test processing dependencies list."""
        response = wizard.start_wizard("Feature J")
        session_id = response.session_id
        
        # Navigate to dependencies
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="1. Work item #123\n2. API deployment"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert len(data.dependencies) == 2
    
    def test_process_dependencies_none(self, wizard):
        """Test processing no dependencies."""
        response = wizard.start_wizard("Feature K")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="none"
        )
        
        data = wizard.sessions[session_id]["data"]
        assert data.dependencies == []
    
    # ===== Review Tests =====
    
    def test_process_review_approve(self, wizard):
        """Test approving work item in review."""
        response = wizard.start_wizard("Feature L")
        session_id = response.session_id
        
        # Navigate to review
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="none")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="approve"
        )
        
        assert response.stage == WizardStage.COMPLETE
        assert "ado_item" in response.context
    
    def test_process_review_cancel(self, wizard):
        """Test cancelling in review."""
        response = wizard.start_wizard("Feature M")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="skip")
        wizard.process_response(session_id=session_id, user_input="none")
        
        response = wizard.process_response(
            session_id=session_id,
            user_input="cancel"
        )
        
        session = wizard.sessions.get(session_id)
        assert session.get("cancelled") is True
    
    # ===== Edge Cases & Error Handling =====
    
    def test_invalid_session_id(self, wizard):
        """Test error handling for invalid session ID."""
        with pytest.raises(ValueError, match="Invalid session ID"):
            wizard.process_response(
                session_id="invalid-session-id",
                user_input="test"
            )
    
    def test_session_history_tracking(self, wizard):
        """Test wizard tracks interaction history."""
        response = wizard.start_wizard("Feature N")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        wizard.process_response(session_id=session_id, user_input="AC")
        
        session = wizard.sessions[session_id]
        assert len(session["history"]) == 2
        assert session["history"][0]["stage"] == "basic_info"
        assert session["history"][1]["stage"] == "acceptance_criteria"
    
    def test_get_session_summary(self, wizard):
        """Test getting session summary."""
        response = wizard.start_wizard("Feature O")
        session_id = response.session_id
        
        wizard.process_response(session_id=session_id, user_input="continue")
        
        summary = wizard.get_session_summary(session_id)
        
        assert summary is not None
        assert summary["session_id"] == session_id
        assert summary["feature_name"] == "Feature O"
        assert "progress" in summary
    
    def test_get_session_summary_invalid_id(self, wizard):
        """Test session summary returns None for invalid ID."""
        summary = wizard.get_session_summary("invalid-id")
        assert summary is None
    
    def test_cancel_wizard(self, wizard):
        """Test cancelling wizard session."""
        response = wizard.start_wizard("Feature P")
        session_id = response.session_id
        
        result = wizard.cancel_wizard(session_id)
        
        assert result is True
        assert session_id not in wizard.sessions
    
    def test_cancel_wizard_invalid_id(self, wizard):
        """Test cancelling non-existent wizard."""
        result = wizard.cancel_wizard("invalid-id")
        assert result is False
    
    # ===== Integration Tests =====
    
    def test_full_wizard_flow_minimal(self, wizard):
        """Test complete wizard flow with minimal inputs (all skips)."""
        response = wizard.start_wizard("Minimal Feature")
        session_id = response.session_id
        
        # Skip through all stages
        wizard.process_response(session_id=session_id, user_input="continue")  # basic info
        wizard.process_response(session_id=session_id, user_input="skip")  # AC
        wizard.process_response(session_id=session_id, user_input="skip")  # DoR
        wizard.process_response(session_id=session_id, user_input="skip")  # DoD
        wizard.process_response(session_id=session_id, user_input="skip")  # Estimation
        wizard.process_response(session_id=session_id, user_input="none")  # Dependencies
        response = wizard.process_response(session_id=session_id, user_input="approve")  # Review
        
        assert response.stage == WizardStage.COMPLETE
        assert "ado_item" in response.context
    
    def test_full_wizard_flow_complete(self, wizard):
        """Test complete wizard flow with all data provided."""
        response = wizard.start_wizard("Complete Feature")
        session_id = response.session_id
        
        # Provide all data
        wizard.process_response(session_id=session_id, user_input="Feature, High, XL")
        wizard.process_response(session_id=session_id, user_input="1. AC1\n2. AC2\n3. AC3")
        wizard.process_response(session_id=session_id, user_input="Assumptions: A. Constraints: C. Dependencies: None")
        wizard.process_response(session_id=session_id, user_input="Code complete, Tests pass, Deployed")
        wizard.process_response(session_id=session_id, user_input="13")
        wizard.process_response(session_id=session_id, user_input="Work item #456")
        response = wizard.process_response(session_id=session_id, user_input="approve")
        
        assert response.stage == WizardStage.COMPLETE
        
        ado_item = response.context["ado_item"]
        assert ado_item["type"] == "Feature"
        assert ado_item["priority"] == "High"
        assert ado_item["story_points"] == 13
        assert len(ado_item["acceptance_criteria"]) == 3
        assert len(ado_item["dependencies"]) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--cov=src.orchestrators.ado.ado_conversational_wizard", "--cov-report=term-missing"])
