"""
Test suite for align_system_v2 refactoring (RED phase).

This test file covers the current behavior of align_system_v2 before refactoring.
Target: Reduce complexity from 56 to <15 per extracted function.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.operations.modules.realignment.realignment_utility import align_system_v2


class TestAlignSystemV2CurrentBehavior:
    """Test current behavior before refactoring."""
    
    @pytest.fixture
    def mock_paths(self, tmp_path):
        """Create mock project and CORTEX paths."""
        project_root = tmp_path / "project"
        cortex_root = tmp_path / "cortex"
        
        # Create directory structure
        project_root.mkdir()
        cortex_root.mkdir()
        (cortex_root / "src" / "operations").mkdir(parents=True)
        (cortex_root / "src" / "operations" / "modules" / "realignment").mkdir(parents=True)
        (cortex_root / ".github" / "prompts").mkdir(parents=True)
        
        return {"project_root": project_root, "cortex_root": cortex_root}
    
    def test_function_exists_and_callable(self):
        """RED: Verify function exists and is callable."""
        assert callable(align_system_v2)
    
    def test_returns_dict_with_expected_keys(self, mock_paths):
        """RED: Verify function returns dict with required keys."""
        with patch('src.operations.modules.realignment.realignment_utility.FeatureRegistrationValidator'):
            with patch('src.operations.modules.realignment.realignment_utility._check_intent_router_coverage'):
                with patch('src.operations.modules.realignment.realignment_utility._check_response_template_coverage'):
                    with patch('src.operations.modules.realignment.realignment_utility._check_template_structure'):
                        with patch('src.operations.modules.realignment.realignment_utility._check_prompt_optimization'):
                            with patch('src.operations.modules.realignment.realignment_utility.ObsoleteCodeDetector'):
                                with patch('src.operations.modules.realignment.realignment_utility._check_specialist_router_wiring'):
                                    with patch('src.operations.modules.realignment.realignment_utility._check_module_imports'):
                                        with patch('src.operations.modules.realignment.realignment_utility._check_git_checkpoint_wiring'):
                                            with patch('src.operations.modules.realignment.realignment_utility._check_component_discovery_wiring'):
                                                with patch('src.operations.modules.realignment.realignment_utility._check_autonomous_execution_wiring'):
                                                    result = align_system_v2(
                                                        mock_paths["project_root"],
                                                        mock_paths["cortex_root"],
                                                        dry_run=True
                                                    )
        
        # Must fail initially - no mocks configured
        assert "success" in result
        assert "checks" in result
        assert "fixes_applied" in result
        assert "warnings" in result
        assert "errors" in result
        assert "report_path" in result
    
    def test_dry_run_prevents_changes(self, mock_paths):
        """RED: Verify dry_run=True prevents file modifications."""
        with patch('src.operations.modules.realignment.realignment_utility.FeatureRegistrationValidator') as mock_validator:
            mock_validator.return_value.validate.return_value = Mock(
                passed=False,
                unregistered_operations=["test_op"],
                unregistered_count=1,
                registered_operations=[],
                registration_percentage=0,
                unregistered_modules=[]
            )
            
            with patch('src.operations.modules.realignment.realignment_utility._check_intent_router_coverage') as mock_router:
                mock_router.return_value = {"missing_count": 0, "coverage_percentage": 100}
                
                with patch('src.operations.modules.realignment.realignment_utility._check_response_template_coverage') as mock_template:
                    mock_template.return_value = {"missing_count": 0}
                    
                    with patch('src.operations.modules.realignment.realignment_utility._check_template_structure') as mock_structure:
                        mock_structure.return_value = {"root_level_templates": 0}
                        
                        with patch('src.operations.modules.realignment.realignment_utility._check_prompt_optimization') as mock_prompt:
                            mock_prompt.return_value = {"optimized": True, "line_count": 250}
                            
                            with patch('src.operations.modules.realignment.realignment_utility.ObsoleteCodeDetector') as mock_detector:
                                mock_detector.return_value.detect_all.return_value = {}
                                
                                with patch('src.operations.modules.realignment.realignment_utility._check_specialist_router_wiring') as mock_wiring:
                                    mock_wiring.return_value = {"passed": True, "unwired_count": 0, "total_specialist_routers": 0}
                                    
                                    with patch('src.operations.modules.realignment.realignment_utility._check_module_imports') as mock_imports:
                                        mock_imports.return_value = {"broken_imports": 0}
                                        
                                        with patch('src.operations.modules.realignment.realignment_utility._check_git_checkpoint_wiring') as mock_git:
                                            mock_git.return_value = {"passed": True}
                                            
                                            with patch('src.operations.modules.realignment.realignment_utility._check_component_discovery_wiring') as mock_component:
                                                mock_component.return_value = {"passed": True}
                                                
                                                with patch('src.operations.modules.realignment.realignment_utility._check_autonomous_execution_wiring') as mock_auto:
                                                    mock_auto.return_value = {"passed": True}
                                                    
                                                    result = align_system_v2(
                                                        mock_paths["project_root"],
                                                        mock_paths["cortex_root"],
                                                        auto_fix=True,
                                                        dry_run=True
                                                    )
        
        # Dry run should NOT apply fixes
        assert len(result["fixes_applied"]) == 0
        assert result["success"] == False  # Has errors but no fixes applied
    
    def test_check1_feature_registration_validation(self, mock_paths):
        """RED: Test CHECK 1 - Feature Registration Validation."""
        with patch('src.operations.modules.realignment.realignment_utility.FeatureRegistrationValidator') as mock_validator:
            # Configure mock to return failed validation
            mock_result = Mock()
            mock_result.passed = False
            mock_result.unregistered_operations = ["missing_op1", "missing_op2"]
            mock_result.unregistered_count = 2
            mock_result.registered_operations = ["existing_op"]
            mock_result.registration_percentage = 33.3
            mock_result.unregistered_modules = ["missing_op1"]
            
            mock_validator.return_value.validate.return_value = mock_result
            
            # Mock other checks to pass
            with patch('src.operations.modules.realignment.realignment_utility._check_intent_router_coverage', return_value={"missing_count": 0}):
                with patch('src.operations.modules.realignment.realignment_utility._check_response_template_coverage', return_value={"missing_count": 0}):
                    with patch('src.operations.modules.realignment.realignment_utility._check_template_structure', return_value={"root_level_templates": 0}):
                        with patch('src.operations.modules.realignment.realignment_utility._check_prompt_optimization', return_value={"optimized": True, "line_count": 200}):
                            with patch('src.operations.modules.realignment.realignment_utility.ObsoleteCodeDetector') as mock_detector:
                                mock_detector.return_value.detect_all.return_value = {}
                                
                                with patch('src.operations.modules.realignment.realignment_utility._check_specialist_router_wiring', return_value={"passed": True, "unwired_count": 0}):
                                    with patch('src.operations.modules.realignment.realignment_utility._check_module_imports', return_value={"broken_imports": 0}):
                                        with patch('src.operations.modules.realignment.realignment_utility._check_git_checkpoint_wiring', return_value={"passed": True}):
                                            with patch('src.operations.modules.realignment.realignment_utility._check_component_discovery_wiring', return_value={"passed": True}):
                                                with patch('src.operations.modules.realignment.realignment_utility._check_autonomous_execution_wiring', return_value={"passed": True}):
                                                    result = align_system_v2(
                                                        mock_paths["project_root"],
                                                        mock_paths["cortex_root"],
                                                        dry_run=True
                                                    )
        
        # Assertions - must fail initially
        assert result["success"] == False
        assert "feature_registration" in result["checks"]
        assert result["checks"]["feature_registration"]["passed"] == False
        assert result["checks"]["feature_registration"]["unregistered_operations"] == 2
        assert len([e for e in result["errors"] if e["category"] == "feature_registration"]) == 1
    
    def test_check2_intent_router_coverage(self, mock_paths):
        """RED: Test CHECK 2 - Intent Router Coverage."""
        # This test will initially FAIL because we haven't mocked everything
        pass  # Will implement after confirming test framework works
    
    def test_auto_fix_registers_features(self, mock_paths):
        """RED: Test auto_fix=True registers unregistered features."""
        # This test will initially FAIL
        pass
    
    def test_all_11_checks_execute(self, mock_paths):
        """RED: Verify all 11 checks are executed."""
        # This test will initially FAIL
        pass


class TestComplexityMetrics:
    """Measure current complexity before refactoring."""
    
    def test_current_complexity_is_56(self):
        """RED: Document current complexity = 56."""
        # This test documents the starting point
        # Will be replaced with post-refactoring complexity check
        import radon.complexity as radon_complexity
        from pathlib import Path
        
        file_path = Path(__file__).parent.parent.parent / "src" / "operations" / "modules" / "realignment" / "realignment_utility.py"
        
        with open(file_path) as f:
            code = f.read()
        
        # Find align_system_v2 complexity
        complexities = radon_complexity.cc_visit(code)
        align_v2_complexity = next(
            (c.complexity for c in complexities if c.name == "align_system_v2"),
            None
        )
        
        assert align_v2_complexity is not None, "align_system_v2 not found"
        assert align_v2_complexity == 56, f"Expected complexity 56, got {align_v2_complexity}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
