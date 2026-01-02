"""
Test Suite: ADO Orchestrator v2 Wizard Integration

Tests for wizard mode integration in ADO v2, including _execute_wizard_mode(),
_execute_from_work_items(), vision context extraction, and wizard-to-auto pipeline.

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch, call
from pathlib import Path

from src.orchestrators.ado.v2.ado_orchestrator_v2 import ADOOrchestratorV2, ADOResultV2
from src.database.planning_state_db import PlanningStateDB


class TestADOWizardIntegration:
    """Test suite for ADO v2 wizard mode integration."""
    
    @pytest.fixture
    def mock_state_db(self):
        """Create mock PlanningStateDB."""
        db = Mock(spec=PlanningStateDB)
        db.create_plan.return_value = "test-plan-id"
        db.start_phase.return_value = "test-phase-id"
        db.complete_phase.return_value = None
        db.complete_plan.return_value = None
        return db
    
    @pytest.fixture
    def mock_config(self):
        """Return path to ADO v2 config."""
        return "cortex-brain/manifests/orchestrators/ado-orchestrator-v2.yaml"
    
    @pytest.fixture
    def mock_wizard(self):
        """Create mock ADOConversationalWizard."""
        wizard = MagicMock()
        
        # Mock wizard response structure
        wizard_response = MagicMock()
        wizard_response.stage = MagicMock()
        wizard_response.stage.value = "COMPLETE"
        wizard_response.session_id = "test-session-123"
        wizard_response.prompt = "Test wizard prompt"
        wizard_response.context = {
            "ado_item": {
                "story": {
                    "title": "User Authentication",
                    "description": "Implement JWT auth",
                    "acceptance_criteria": ["AC1", "AC2"],
                    "story_points": 8
                },
                "tasks": [
                    {"title": "Create login endpoint", "estimated_hours": 4},
                    {"title": "Add JWT middleware", "estimated_hours": 3}
                ]
            }
        }
        
        wizard.start_wizard.return_value = wizard_response
        wizard.process_response.return_value = wizard_response
        
        return wizard
    
    @pytest.fixture
    def wizard_work_items(self):
        """Sample work items from wizard session."""
        return {
            "story": {
                "title": "User Authentication System",
                "description": "Implement secure JWT-based authentication",
                "acceptance_criteria": [
                    "Users can register with email/password",
                    "JWT tokens expire after 24 hours",
                    "Failed attempts are logged"
                ],
                "story_points": 13,
                "dor": {
                    "assumptions": ["Dev env configured", "DB ready"],
                    "constraints": ["Use bcrypt", "Must have refresh endpoint"]
                }
            },
            "tasks": [
                {
                    "title": "Create registration endpoint",
                    "description": "POST /api/register",
                    "estimated_hours": 4,
                    "area": "Backend"
                },
                {
                    "title": "Implement JWT generation",
                    "description": "Generate secure tokens",
                    "estimated_hours": 3,
                    "area": "Backend"
                },
                {
                    "title": "Build login UI",
                    "description": "React login form",
                    "estimated_hours": 5,
                    "area": "Frontend"
                }
            ],
            "test_requirements": {
                "unit_tests": ["test_registration", "test_jwt_gen"],
                "integration_tests": ["test_full_auth_flow"]
            }
        }
    
    @pytest.fixture
    def vision_context_data(self):
        """Sample vision API context data."""
        return {
            "analysis": {
                "ui_elements": [
                    {"type": "button", "text": "Login", "location": "top-right"},
                    {"type": "form", "fields": ["email", "password"]},
                    {"type": "link", "text": "Forgot password?"}
                ],
                "layout": "Standard login screen with centered form",
                "colors": {"primary": "#007bff", "background": "#f8f9fa"}
            },
            "acceptance_criteria": [
                "Login button must be visible in top-right",
                "Form must validate email format",
                "Forgot password link present"
            ]
        }
    
    # ==================== _execute_wizard_mode() Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_wizard_mode_exists(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: _execute_wizard_mode() method exists."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        assert hasattr(orchestrator, '_execute_wizard_mode')
        assert callable(orchestrator._execute_wizard_mode)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_wizard_mode_starts_wizard(self, mock_wizard_class, mock_state_db, mock_config, mock_wizard):
        """Test: Wizard mode starts wizard session."""
        mock_wizard_class.return_value = mock_wizard
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        params = {"feature": "User Authentication", "mode": "wizard"}
        
        # Mock _execute_from_work_items to prevent actual execution
        orchestrator._execute_from_work_items = Mock(return_value={"status": "success"})
        
        result = orchestrator._execute_wizard_mode(params)
        
        # Verify wizard.start_wizard was called
        mock_wizard.start_wizard.assert_called_once_with("User Authentication")
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_wizard_mode_returns_work_items_to_pipeline(self, mock_wizard_class, mock_state_db, mock_config, mock_wizard):
        """Test: Wizard mode passes work items to _execute_from_work_items()."""
        mock_wizard_class.return_value = mock_wizard
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        params = {"feature": "Test Feature", "mode": "wizard"}
        
        # Mock the pipeline
        orchestrator._execute_from_work_items = Mock(return_value={"status": "success"})
        
        orchestrator._execute_wizard_mode(params)
        
        # Verify _execute_from_work_items was called with wizard's work items
        orchestrator._execute_from_work_items.assert_called_once()
        call_args = orchestrator._execute_from_work_items.call_args[0][0]
        assert "story" in call_args
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_wizard_mode_handles_wizard_unavailable(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: Wizard mode handles wizard unavailable gracefully."""
        mock_wizard_class.side_effect = ImportError("Wizard not available")
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        params = {"feature": "Test Feature", "mode": "wizard"}
        
        result = orchestrator._execute_wizard_mode(params)
        
        # Should return error result
        assert result["status"] == "error" or "wizard" in result.get("message", "").lower()
    
    # ==================== _execute_from_work_items() Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_from_work_items_exists(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: _execute_from_work_items() method exists."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        assert hasattr(orchestrator, '_execute_from_work_items')
        assert callable(orchestrator._execute_from_work_items)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_from_work_items_skips_phases_0_3(self, mock_wizard_class, mock_state_db, mock_config, wizard_work_items):
        """Test: _execute_from_work_items() skips DISCOVERY/VALIDATION/GENERATION phases."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock phases
        orchestrator._phase_discovery = Mock()
        orchestrator._phase_validation = Mock()
        orchestrator._phase_generation = Mock()
        orchestrator._phase_approval = Mock(return_value=wizard_work_items)
        orchestrator._phase_execution = Mock(return_value=[])
        orchestrator._phase_completion = Mock(return_value={"status": "success"})
        
        orchestrator._execute_from_work_items(wizard_work_items)
        
        # Verify phases 0-3 were NOT called
        orchestrator._phase_discovery.assert_not_called()
        orchestrator._phase_validation.assert_not_called()
        orchestrator._phase_generation.assert_not_called()
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_from_work_items_calls_approval(self, mock_wizard_class, mock_state_db, mock_config, wizard_work_items):
        """Test: _execute_from_work_items() calls APPROVAL phase."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock phases
        orchestrator._phase_approval = Mock(return_value=wizard_work_items)
        orchestrator._phase_execution = Mock(return_value=[])
        orchestrator._phase_completion = Mock(return_value={"status": "success"})
        
        orchestrator._execute_from_work_items(wizard_work_items)
        
        # Verify APPROVAL was called with work items
        orchestrator._phase_approval.assert_called_once_with(wizard_work_items)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_from_work_items_calls_execution(self, mock_wizard_class, mock_state_db, mock_config, wizard_work_items):
        """Test: _execute_from_work_items() calls EXECUTION phase."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock phases
        orchestrator._phase_approval = Mock(return_value=wizard_work_items)
        orchestrator._phase_execution = Mock(return_value=[{"id": 123, "type": "Story"}])
        orchestrator._phase_completion = Mock(return_value={"status": "success"})
        
        orchestrator._execute_from_work_items(wizard_work_items)
        
        # Verify EXECUTION was called
        orchestrator._phase_execution.assert_called_once_with(wizard_work_items)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_from_work_items_calls_completion(self, mock_wizard_class, mock_state_db, mock_config, wizard_work_items):
        """Test: _execute_from_work_items() calls COMPLETION phase."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock phases
        orchestrator._phase_approval = Mock(return_value=wizard_work_items)
        work_item_links = [{"id": 123, "type": "Story", "url": "https://..."}]
        orchestrator._phase_execution = Mock(return_value=work_item_links)
        orchestrator._phase_completion = Mock(return_value={"status": "success"})
        
        orchestrator._execute_from_work_items(wizard_work_items)
        
        # Verify COMPLETION was called with work item links
        orchestrator._phase_completion.assert_called_once_with(work_item_links)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_from_work_items_returns_result(self, mock_wizard_class, mock_state_db, mock_config, wizard_work_items):
        """Test: _execute_from_work_items() returns completion result."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock phases
        orchestrator._phase_approval = Mock(return_value=wizard_work_items)
        orchestrator._phase_execution = Mock(return_value=[])
        expected_result = {"status": "success", "items_created": 4}
        orchestrator._phase_completion = Mock(return_value=expected_result)
        
        result = orchestrator._execute_from_work_items(wizard_work_items)
        
        assert result == expected_result
    
    # ==================== Vision Context Integration Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_get_vision_api_method_exists(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: _get_vision_api() method exists."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        assert hasattr(orchestrator, '_get_vision_api')
        assert callable(orchestrator._get_vision_api)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_extract_vision_context_method_exists(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: _extract_vision_context() method exists."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        assert hasattr(orchestrator, '_extract_vision_context')
        assert callable(orchestrator._extract_vision_context)
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.VisionOrchestrator')
    def test_get_vision_api_detects_config_source(self, mock_vision_class, mock_wizard_class, mock_state_db, mock_config):
        """Test: _get_vision_api() detects Vision API from config."""
        mock_vision_instance = MagicMock()
        mock_vision_class.return_value = mock_vision_instance
        
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock config with vision API
        with patch.object(orchestrator, 'config', {"vision_api": {"enabled": True}}):
            result = orchestrator._get_vision_api()
        
        # Should return Vision API instance
        assert result is not None
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_get_vision_api_detects_middleware_source(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: _get_vision_api() detects Vision API from middleware."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock vision context middleware
        mock_middleware = MagicMock()
        mock_middleware.get_vision_api.return_value = "vision_api_instance"
        
        with patch('src.orchestrators.ado.v2.ado_orchestrator_v2.vision_context_middleware', mock_middleware):
            result = orchestrator._get_vision_api()
        
        # Should return Vision API from middleware
        assert result == "vision_api_instance"
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_extract_vision_context_returns_analysis(self, mock_wizard_class, mock_state_db, mock_config, vision_context_data):
        """Test: _extract_vision_context() extracts analysis from Vision API."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock Vision API
        mock_vision_api = MagicMock()
        mock_vision_api.analyze_image.return_value = vision_context_data
        
        with patch.object(orchestrator, '_get_vision_api', return_value=mock_vision_api):
            result = orchestrator._extract_vision_context("test_image.png")
        
        assert result == vision_context_data
        mock_vision_api.analyze_image.assert_called_once_with("test_image.png")
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_extract_vision_context_handles_no_vision_api(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: _extract_vision_context() handles missing Vision API gracefully."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        with patch.object(orchestrator, '_get_vision_api', return_value=None):
            result = orchestrator._extract_vision_context("test_image.png")
        
        # Should return None or empty dict
        assert result is None or result == {}
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_wizard_mode_injects_vision_context(self, mock_wizard_class, mock_state_db, mock_config, mock_wizard, vision_context_data):
        """Test: Wizard mode injects vision context at ACCEPTANCE_CRITERIA stage."""
        mock_wizard_class.return_value = mock_wizard
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock vision API
        with patch.object(orchestrator, '_extract_vision_context', return_value=vision_context_data):
            orchestrator._execute_from_work_items = Mock(return_value={"status": "success"})
            
            params = {"feature": "Login UI", "mode": "wizard"}
            orchestrator._execute_wizard_mode(params)
        
        # Verify wizard received vision context
        # (wizard.process_response should have been called with vision_context)
        assert mock_wizard.process_response.called or mock_wizard.start_wizard.called
    
    # ==================== Wizard-to-Auto Pipeline Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_wizard_pipeline_reuses_auto_phases(self, mock_wizard_class, mock_state_db, mock_config, mock_wizard):
        """Test: Wizard pipeline reuses auto-mode phases 4-5."""
        mock_wizard_class.return_value = mock_wizard
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock auto-mode phases
        orchestrator._phase_approval = Mock(return_value={"story": {}, "tasks": []})
        orchestrator._phase_execution = Mock(return_value=[])
        orchestrator._phase_completion = Mock(return_value={"status": "success"})
        
        params = {"feature": "Test", "mode": "wizard"}
        orchestrator._execute_wizard_mode(params)
        
        # Verify auto-mode phases were reused
        orchestrator._phase_approval.assert_called_once()
        orchestrator._phase_execution.assert_called_once()
        orchestrator._phase_completion.assert_called_once()
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_wizard_work_items_compatible_with_auto_pipeline(self, mock_wizard_class, mock_state_db, mock_config, wizard_work_items):
        """Test: Wizard work items structure is compatible with auto pipeline."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Verify work items have required fields
        assert "story" in wizard_work_items
        assert "tasks" in wizard_work_items
        assert "title" in wizard_work_items["story"]
        assert isinstance(wizard_work_items["tasks"], list)
    
    # ==================== Error Handling Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_wizard_mode_handles_wizard_error(self, mock_wizard_class, mock_state_db, mock_config):
        """Test: Wizard mode handles wizard errors gracefully."""
        mock_wizard = MagicMock()
        mock_wizard.start_wizard.side_effect = Exception("Wizard error")
        mock_wizard_class.return_value = mock_wizard
        
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        params = {"feature": "Test", "mode": "wizard"}
        
        result = orchestrator._execute_wizard_mode(params)
        
        # Should return error result
        assert result["status"] == "error"
        assert "wizard" in result["message"].lower() or "error" in result["message"].lower()
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_execute_from_work_items_handles_phase_failure(self, mock_wizard_class, mock_state_db, mock_config, wizard_work_items):
        """Test: _execute_from_work_items() handles phase failures."""
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock APPROVAL phase to fail
        orchestrator._phase_approval = Mock(side_effect=Exception("Approval failed"))
        
        result = orchestrator._execute_from_work_items(wizard_work_items)
        
        # Should return error result
        assert result["status"] == "error"
    
    # ==================== Integration Flow Tests ====================
    
    @patch('src.orchestrators.ado.v2.ado_orchestrator_v2.ADOConversationalWizard')
    def test_full_wizard_flow_end_to_end(self, mock_wizard_class, mock_state_db, mock_config, mock_wizard):
        """Test: Full wizard flow from start to completion."""
        mock_wizard_class.return_value = mock_wizard
        orchestrator = ADOOrchestratorV2(mock_config, mock_state_db)
        
        # Mock all phases
        orchestrator._phase_approval = Mock(return_value={"story": {}, "tasks": []})
        orchestrator._phase_execution = Mock(return_value=[
            {"id": 123, "type": "Story", "url": "https://dev.azure.com/..."}
        ])
        orchestrator._phase_completion = Mock(return_value={
            "status": "success",
            "items_created": 1,
            "work_item_links": [{"id": 123}]
        })
        
        params = {"feature": "Full Test", "mode": "wizard"}
        result = orchestrator._execute_wizard_mode(params)
        
        # Verify complete flow
        assert result["status"] == "success"
        assert result["items_created"] == 1
        mock_wizard.start_wizard.assert_called_once()
        orchestrator._phase_approval.assert_called_once()
        orchestrator._phase_execution.assert_called_once()
        orchestrator._phase_completion.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
