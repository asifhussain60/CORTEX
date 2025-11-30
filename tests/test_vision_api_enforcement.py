"""
Test Vision API Integration with TDD Mastery.

This test file validates that Vision API auto-triggers when images are attached
during TDD workflow, as required by Deployment Gate 13.

Version: 1.0
Author: Asif Hussain
Created: 2025-11-30
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.workflows.tdd_workflow_orchestrator import TDDWorkflowOrchestrator, TDDWorkflowConfig


class TestVisionAPIEnforcement:
    """Test suite for Vision API enforcement in TDD Mastery."""
    
    @pytest.fixture
    def tdd_config(self, tmp_path):
        """Create TDD config with Vision API enabled."""
        return TDDWorkflowConfig(
            project_root=str(tmp_path),
            enable_vision_api=True,
            enable_view_discovery=False,
            enable_feedback_collection=False
        )
    
    @pytest.fixture
    def tdd_orchestrator(self, tdd_config):
        """Create TDD orchestrator instance."""
        return TDDWorkflowOrchestrator(tdd_config)
    
    def test_vision_api_auto_triggers_with_images(self, tdd_orchestrator, tmp_path):
        """
        Test 1: Vision API auto-triggers when images present in context.
        
        Requirement: Deployment Gate 13, line 1681
        Expected: Screenshot analyzer called, UI elements extracted
        """
        # Create mock source file
        source_file = tmp_path / "test_module.py"
        source_file.write_text("""
def login_user(username, password):
    return True
""")
        
        # Mock screenshot analyzer
        with patch.object(tdd_orchestrator, 'screenshot_analyzer') as mock_analyzer:
            mock_analyzer.analyze.return_value = {
                "extracted_elements": {
                    "buttons": ["Submit", "Cancel"],
                    "inputs": ["username", "password"],
                    "labels": ["Username:", "Password:"]
                }
            }
            
            # Start session
            tdd_orchestrator.start_session("login_feature")
            
            # Generate tests with mock image data (simulating screenshot)
            scenarios = [b"mock_image_data_that_looks_like_screenshot" * 10]  # >100 bytes
            result = tdd_orchestrator.generate_tests(str(source_file), scenarios=scenarios)
            
            # Verify screenshot analyzer was called
            assert mock_analyzer.analyze.called, "Vision API should auto-trigger with images"
            
            # Verify extracted elements available
            assert "ui_elements" in str(result), "Extracted UI elements should be in test context"
    
    def test_extracted_elements_injected_into_tests(self, tdd_orchestrator, tmp_path):
        """
        Test 2: Extracted UI elements injected into test generation context.
        
        Requirement: Deployment Gate 13, line 1792
        Expected: UI elements passed to test generator
        """
        # Create mock source file
        source_file = tmp_path / "ui_module.py"
        source_file.write_text("""
def validate_form(form_data):
    return True
""")
        
        # Mock screenshot analyzer with realistic UI elements
        extracted_elements = {
            "buttons": ["#submitButton", "#cancelButton"],
            "inputs": ["#emailInput", "#passwordInput"],
            "labels": ["Email:", "Password:", "Remember me"]
        }
        
        with patch.object(tdd_orchestrator, 'screenshot_analyzer') as mock_analyzer:
            mock_analyzer.analyze.return_value = {"extracted_elements": extracted_elements}
            
            # Mock test generator to capture func_info
            original_generate = tdd_orchestrator.test_generator.generate
            captured_func_info = []
            
            def capture_generate(func_info):
                captured_func_info.append(func_info)
                return "def test_validate_form(): pass"
            
            tdd_orchestrator.test_generator.generate = capture_generate
            
            # Start session and generate tests
            tdd_orchestrator.start_session("ui_validation")
            scenarios = [b"X" * 200]  # Mock image data
            tdd_orchestrator.generate_tests(str(source_file), scenarios=scenarios)
            
            # Verify UI elements passed to test generator
            assert len(captured_func_info) > 0, "Test generator should be called"
            assert "ui_elements" in captured_func_info[0], "UI elements should be in func_info"
            assert captured_func_info[0]["ui_elements"] == extracted_elements
    
    def test_vision_api_disabled_when_no_images(self, tdd_orchestrator, tmp_path):
        """
        Test 3: Vision API does not trigger when no images present.
        
        Requirement: Deployment Gate 13 (implicit - avoid unnecessary processing)
        Expected: Screenshot analyzer not called without images
        """
        # Create mock source file
        source_file = tmp_path / "logic_module.py"
        source_file.write_text("""
def calculate_total(items):
    return sum(items)
""")
        
        # Mock screenshot analyzer
        with patch.object(tdd_orchestrator, 'screenshot_analyzer') as mock_analyzer:
            # Start session and generate tests WITHOUT images
            tdd_orchestrator.start_session("calculation_logic")
            result = tdd_orchestrator.generate_tests(str(source_file))
            
            # Verify screenshot analyzer was NOT called
            assert not mock_analyzer.analyze.called, "Vision API should not trigger without images"
    
    def test_vision_api_handles_analysis_errors_gracefully(self, tdd_orchestrator, tmp_path):
        """
        Test 4: Vision API handles errors gracefully without breaking TDD workflow.
        
        Requirement: Brain protection - robust error handling
        Expected: TDD workflow continues even if Vision API fails
        """
        # Create mock source file
        source_file = tmp_path / "robust_module.py"
        source_file.write_text("""
def process_data(data):
    return data
""")
        
        # Mock screenshot analyzer to raise error
        with patch.object(tdd_orchestrator, 'screenshot_analyzer') as mock_analyzer:
            mock_analyzer.analyze.side_effect = Exception("Vision API connection failed")
            
            # Start session and generate tests with images
            tdd_orchestrator.start_session("robust_processing")
            scenarios = [b"Y" * 200]  # Mock image data
            
            # Should not raise exception - error handled gracefully
            result = tdd_orchestrator.generate_tests(str(source_file), scenarios=scenarios)
            
            # Verify test generation completed despite Vision API error
            assert result is not None, "Test generation should complete despite Vision API error"
            assert "test_code" in str(result) or "test_" in str(result)
    
    def test_vision_api_config_flag_respected(self, tmp_path):
        """
        Test 5: Vision API respects enable_vision_api configuration flag.
        
        Requirement: User control over feature enablement
        Expected: Vision API disabled when config flag is False
        """
        # Create config with Vision API disabled
        config_disabled = TDDWorkflowConfig(
            project_root=str(tmp_path),
            enable_vision_api=False
        )
        orchestrator_disabled = TDDWorkflowOrchestrator(config_disabled)
        
        # Verify screenshot analyzer not initialized
        assert orchestrator_disabled.screenshot_analyzer is None, \
            "Screenshot analyzer should not initialize when enable_vision_api=False"
    
    def test_vision_api_initialization_failure_handled(self, tmp_path):
        """
        Test 6: Vision API initialization failure handled gracefully.
        
        Requirement: Robust initialization with fallback
        Expected: TDD workflow functional even if ScreenshotAnalyzer fails to initialize
        """
        with patch('src.workflows.tdd_workflow_orchestrator.ScreenshotAnalyzer') as MockAnalyzer:
            MockAnalyzer.side_effect = ImportError("ScreenshotAnalyzer not available")
            
            config = TDDWorkflowConfig(
                project_root=str(tmp_path),
                enable_vision_api=True
            )
            
            # Should not raise exception during initialization
            orchestrator = TDDWorkflowOrchestrator(config)
            
            # Verify screenshot analyzer is None after failed initialization
            assert orchestrator.screenshot_analyzer is None, \
                "Screenshot analyzer should be None after initialization failure"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
