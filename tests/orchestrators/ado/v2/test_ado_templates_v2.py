"""
Test Suite: ADO Orchestrator v2 Template Rendering

Tests for Jinja2 template rendering in ADO v2, including work item preview,
completion messages, approval gates, and error formatting.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound
from unittest.mock import Mock, patch

from src.orchestrators.ado.v2.ado_orchestrator_v2 import ADOOrchestratorV2
from src.database.planning_state_db import PlanningStateDB


class TestADOTemplateRendering:
    """Test suite for ADO v2 Jinja2 template rendering."""
    
    @pytest.fixture
    def template_dir(self):
        """Return path to ADO templates directory."""
        return Path(__file__).parents[4] / "templates" / "ado"
    
    @pytest.fixture
    def work_item_data(self):
        """Sample work item data for template rendering."""
        return {
            "story": {
                "title": "User Authentication System",
                "description": "Implement secure user authentication with JWT tokens",
                "acceptance_criteria": [
                    "Users can register with email/password",
                    "JWT tokens expire after 24 hours",
                    "Failed login attempts are logged"
                ],
                "story_points": 13,
                "dor": {
                    "assumptions": [
                        "Development environment configured",
                        "Database schema supports user table"
                    ],
                    "constraints": [
                        "Must use bcrypt for password hashing",
                        "Token refresh endpoint required"
                    ]
                }
            },
            "tasks": [
                {
                    "title": "Create user registration endpoint",
                    "description": "POST /api/register with email validation",
                    "estimated_hours": 4,
                    "area": "Backend"
                },
                {
                    "title": "Implement JWT token generation",
                    "description": "Generate secure JWT tokens on successful login",
                    "estimated_hours": 3,
                    "area": "Backend"
                },
                {
                    "title": "Add login UI components",
                    "description": "Create React login form with validation",
                    "estimated_hours": 5,
                    "area": "Frontend"
                }
            ],
            "test_requirements": {
                "unit_tests": [
                    "test_user_registration_success",
                    "test_user_registration_duplicate_email",
                    "test_jwt_token_generation"
                ],
                "integration_tests": [
                    "test_full_registration_flow",
                    "test_login_flow_with_token"
                ]
            },
            "complexity": "HIGH",
            "total_effort_hours": 12
        }
    
    @pytest.fixture
    def completion_data(self):
        """Sample completion data for template rendering."""
        return {
            "feature_name": "User Authentication System",
            "test_mode": False,
            "items_created": 4,
            "work_item_links": [
                {"id": 12345, "type": "Story", "title": "User Authentication System", "url": "https://dev.azure.com/org/project/_workitems/edit/12345"},
                {"id": 12346, "type": "Task", "title": "Create registration endpoint", "url": "https://dev.azure.com/org/project/_workitems/edit/12346"},
                {"id": 12347, "type": "Task", "title": "Implement JWT generation", "url": "https://dev.azure.com/org/project/_workitems/edit/12347"},
                {"id": 12348, "type": "Task", "title": "Add login UI", "url": "https://dev.azure.com/org/project/_workitems/edit/12348"}
            ],
            "execution_time_seconds": 2.4
        }
    
    @pytest.fixture
    def error_data(self):
        """Sample error data for template rendering."""
        return {
            "error_type": "ADO_API_ERROR",
            "error_message": "Failed to create work item: Unauthorized (401)",
            "phase": "EXECUTION",
            "feature_name": "User Authentication System",
            "logs": [
                "[2026-01-02 10:30:15] Starting work item creation",
                "[2026-01-02 10:30:16] ADO API request failed: 401",
                "[2026-01-02 10:30:16] Aborting execution phase"
            ],
            "suggestions": [
                "Verify ADO Personal Access Token is valid",
                "Check ADO API permissions for work item creation",
                "Ensure organization URL is correct"
            ]
        }
    
    @pytest.fixture
    def mock_state_db(self):
        """Create mock PlanningStateDB."""
        db = Mock(spec=PlanningStateDB)
        db.create_plan.return_value = "test-plan-id"
        return db
    
    @pytest.fixture
    def mock_config(self):
        """Return path to ADO v2 config."""
        return "cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml"
    
    # ==================== Template File Existence Tests ====================
    
    def test_work_item_preview_template_exists(self, template_dir):
        """Test: work-item-preview.jinja2 template file exists."""
        template_path = template_dir / "work-item-preview.jinja2"
        assert template_path.exists(), f"Template not found: {template_path}"
        assert template_path.is_file()
    
    def test_completion_message_template_exists(self, template_dir):
        """Test: completion-message.jinja2 template file exists."""
        template_path = template_dir / "completion-message.jinja2"
        assert template_path.exists(), f"Template not found: {template_path}"
        assert template_path.is_file()
    
    def test_approval_gate_template_exists(self, template_dir):
        """Test: approval-gate.jinja2 template file exists."""
        template_path = template_dir / "approval-gate.jinja2"
        assert template_path.exists(), f"Template not found: {template_path}"
        assert template_path.is_file()
    
    def test_error_message_template_exists(self, template_dir):
        """Test: error-message.jinja2 template file exists."""
        template_path = template_dir / "error-message.jinja2"
        assert template_path.exists(), f"Template not found: {template_path}"
        assert template_path.is_file()
    
    # ==================== Work Item Preview Template Tests ====================
    
    def test_work_item_preview_renders_story_title(self, template_dir, work_item_data):
        """Test: Work item preview renders story title."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        output = template.render(**work_item_data)
        
        assert "User Authentication System" in output
        assert "story" in output.lower() or "Story" in output
    
    def test_work_item_preview_renders_tasks(self, template_dir, work_item_data):
        """Test: Work item preview renders all tasks."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        output = template.render(**work_item_data)
        
        assert "Create user registration endpoint" in output
        assert "Implement JWT token generation" in output
        assert "Add login UI components" in output
    
    def test_work_item_preview_renders_test_requirements(self, template_dir, work_item_data):
        """Test: Work item preview renders test requirements."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        output = template.render(**work_item_data)
        
        assert "test_user_registration_success" in output
        assert "test_full_registration_flow" in output
    
    def test_work_item_preview_renders_complexity(self, template_dir, work_item_data):
        """Test: Work item preview renders complexity rating."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        output = template.render(**work_item_data)
        
        assert "HIGH" in output
    
    def test_work_item_preview_renders_effort_estimate(self, template_dir, work_item_data):
        """Test: Work item preview renders total effort hours."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        output = template.render(**work_item_data)
        
        assert "12" in output  # total_effort_hours
    
    def test_work_item_preview_handles_missing_data(self, template_dir):
        """Test: Work item preview handles missing optional data gracefully."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        minimal_data = {
            "story": {
                "title": "Minimal Story",
                "description": "Basic description"
            },
            "tasks": [],
            "complexity": "LOW"
        }
        
        # Should not raise exception
        output = template.render(**minimal_data)
        assert "Minimal Story" in output
    
    # ==================== Completion Message Template Tests ====================
    
    def test_completion_message_renders_feature_name(self, template_dir, completion_data):
        """Test: Completion message renders feature name."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("completion-message.jinja2")
        
        output = template.render(**completion_data)
        
        assert "User Authentication System" in output
    
    def test_completion_message_renders_work_item_links(self, template_dir, completion_data):
        """Test: Completion message renders all work item links."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("completion-message.jinja2")
        
        output = template.render(**completion_data)
        
        assert "12345" in output
        assert "12346" in output
        assert "12347" in output
        assert "12348" in output
        assert "https://dev.azure.com" in output
    
    def test_completion_message_shows_test_mode_banner(self, template_dir, completion_data):
        """Test: Completion message shows test mode banner when enabled."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("completion-message.jinja2")
        
        test_mode_data = completion_data.copy()
        test_mode_data["test_mode"] = True
        
        output = template.render(**test_mode_data)
        
        assert "test" in output.lower() or "TEST" in output
    
    def test_completion_message_shows_execution_time(self, template_dir, completion_data):
        """Test: Completion message displays execution time."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("completion-message.jinja2")
        
        output = template.render(**completion_data)
        
        assert "2.4" in output or "2.40" in output  # execution_time_seconds
    
    def test_completion_message_shows_items_count(self, template_dir, completion_data):
        """Test: Completion message shows count of created items."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("completion-message.jinja2")
        
        output = template.render(**completion_data)
        
        assert "4" in output  # items_created
    
    # ==================== Approval Gate Template Tests ====================
    
    def test_approval_gate_renders_preview(self, template_dir, work_item_data):
        """Test: Approval gate renders work item preview."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        preview_template = env.get_template("work-item-preview.jinja2")
        approval_template = env.get_template("approval-gate.jinja2")
        
        preview = preview_template.render(**work_item_data)
        approval_data = {
            "preview": preview,
            "feature_name": "User Authentication System",
            "items_count": 4,
            "total_effort_hours": 12
        }
        
        output = approval_template.render(**approval_data)
        
        assert "User Authentication System" in output
        assert preview in output
    
    def test_approval_gate_shows_approval_options(self, template_dir):
        """Test: Approval gate shows approval/rejection options."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("approval-gate.jinja2")
        
        approval_data = {
            "preview": "Work item preview content",
            "feature_name": "Test Feature",
            "items_count": 3,
            "total_effort_hours": 8
        }
        
        output = template.render(**approval_data)
        
        # Should contain approval instructions
        assert "approve" in output.lower() or "yes" in output.lower()
    
    # ==================== Error Message Template Tests ====================
    
    def test_error_message_renders_error_type(self, template_dir, error_data):
        """Test: Error message renders error type."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("error-message.jinja2")
        
        output = template.render(**error_data)
        
        assert "ADO_API_ERROR" in output
    
    def test_error_message_renders_error_details(self, template_dir, error_data):
        """Test: Error message renders error details."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("error-message.jinja2")
        
        output = template.render(**error_data)
        
        assert "Failed to create work item" in output
        assert "Unauthorized (401)" in output
    
    def test_error_message_renders_phase(self, template_dir, error_data):
        """Test: Error message renders phase where error occurred."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("error-message.jinja2")
        
        output = template.render(**error_data)
        
        assert "EXECUTION" in output
    
    def test_error_message_renders_logs(self, template_dir, error_data):
        """Test: Error message renders relevant log entries."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("error-message.jinja2")
        
        output = template.render(**error_data)
        
        assert "Starting work item creation" in output
        assert "ADO API request failed: 401" in output
    
    def test_error_message_renders_suggestions(self, template_dir, error_data):
        """Test: Error message renders troubleshooting suggestions."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("error-message.jinja2")
        
        output = template.render(**error_data)
        
        assert "Verify ADO Personal Access Token" in output
        assert "Check ADO API permissions" in output
    
    # ==================== Orchestrator Template Integration Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_renders_approval_template(self, mock_wizard, mock_state_db, mock_config, work_item_data):
        """Test: Orchestrator uses approval template in _phase_approval()."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock _phase_generation to return work items
        orchestrator._phase_generation = Mock(return_value=work_item_data)
        
        # Call _phase_approval (should use template)
        with patch.object(orchestrator, '_prompt_user', return_value='approve'):
            result = orchestrator._phase_approval(work_item_data)
        
        # Verify template was used (would contain formatted output)
        assert result is not None
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_renders_completion_template(self, mock_wizard, mock_state_db, mock_config, completion_data):
        """Test: Orchestrator uses completion template in _phase_completion()."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock _phase_execution to return work item links
        orchestrator._phase_execution = Mock(return_value=completion_data["work_item_links"])
        
        # Call _phase_completion (should use template)
        result = orchestrator._phase_completion(completion_data["work_item_links"])
        
        # Verify template was used
        assert result is not None
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_orchestrator_handles_template_not_found(self, mock_wizard, mock_state_db, mock_config):
        """Test: Orchestrator handles missing template gracefully."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock template loading to raise TemplateNotFound
        with patch('jinja2.Environment.get_template', side_effect=TemplateNotFound("test.jinja2")):
            # Should not crash, should return error result
            result = orchestrator.execute(feature="Test Feature", test_mode=True)
            
            # Should fail gracefully
            assert result.success is False or result.status == "error"
    
    # ==================== Template Edge Cases ====================
    
    def test_template_handles_empty_tasks_list(self, template_dir):
        """Test: Template handles empty tasks list."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        data = {
            "story": {"title": "Story with no tasks", "description": "Minimal story"},
            "tasks": [],
            "complexity": "LOW"
        }
        
        output = template.render(**data)
        assert "Story with no tasks" in output
    
    def test_template_handles_long_descriptions(self, template_dir):
        """Test: Template handles very long descriptions."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        long_desc = "A" * 5000  # 5000 character description
        data = {
            "story": {"title": "Long story", "description": long_desc},
            "tasks": [],
            "complexity": "HIGH"
        }
        
        output = template.render(**data)
        assert "Long story" in output
    
    def test_template_handles_special_characters(self, template_dir):
        """Test: Template handles special characters in content."""
        env = Environment(loader=FileSystemLoader(str(template_dir)))
        template = env.get_template("work-item-preview.jinja2")
        
        data = {
            "story": {
                "title": "Story with <html> & special chars \"quotes\"",
                "description": "Test description"
            },
            "tasks": [
                {"title": "Task with 'quotes' and \"doubles\"", "estimated_hours": 2}
            ],
            "complexity": "MEDIUM"
        }
        
        output = template.render(**data)
        assert "Story with" in output
        assert "Task with" in output


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
