"""
Unit tests for StrategicFeatureValidator.

Tests verify that validators correctly return healthy/warning/critical based on
workspace artifacts (files, templates, routing configuration).
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from src.operations.modules.healthcheck.strategic_feature_validator import StrategicFeatureValidator


@pytest.fixture
def validator():
    """Create validator instance for testing."""
    return StrategicFeatureValidator()


@pytest.fixture
def mock_root():
    """Mock workspace root path."""
    return Path("/Users/asifhussain/PROJECTS/CORTEX")


class TestArchitectureIntelligence:
    """Test Architecture Intelligence validator."""
    
    def test_all_checks_pass_returns_healthy(self, validator, mock_root):
        """When all checks pass (docs, analysis dir, routing), return healthy."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists') as mock_exists, \
             patch.object(validator, '_load_response_templates') as mock_templates, \
             patch.object(validator, '_template_has_triggers', return_value=True):
            
            # All files exist
            mock_exists.return_value = True
            mock_templates.return_value = {"templates": {"architecture_intelligence": {}}}
            
            result = validator.validate_architecture_intelligence()
            
            assert result["status"] == "healthy"
            assert result["details"]["docs"] is True
            assert result["details"]["routing"] is True
            assert result["details"]["reports_dir"] is True
    
    def test_missing_guide_with_others_ok_returns_critical(self, validator, mock_root):
        """When guide missing (even if other checks pass), return critical.
        
        Note: The validator logic requires guide_ok AND (analysis_dir_ok OR routing_ok)
        for warning status. If guide is missing, it goes straight to critical.
        """
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists') as mock_exists, \
             patch.object(validator, '_load_response_templates') as mock_templates, \
             patch.object(validator, '_template_has_triggers', return_value=True):
            
            # Guide missing, others exist
            mock_exists.side_effect = lambda p: "architecture-intelligence-guide.md" not in str(p)
            mock_templates.return_value = {"templates": {"architecture_intelligence": {}}}
            
            result = validator.validate_architecture_intelligence()
            
            assert result["status"] == "critical"
            assert "Missing architecture-intelligence-guide.md" in result["issues"]
            assert result["details"]["docs"] is False
            assert result["details"]["routing"] is True
    
    def test_missing_multiple_returns_critical(self, validator, mock_root):
        """When multiple checks fail, return critical."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists', return_value=False), \
             patch.object(validator, '_load_response_templates', return_value=None):
            
            result = validator.validate_architecture_intelligence()
            
            assert result["status"] == "critical"
            assert len(result["issues"]) >= 2
            assert result["details"]["docs"] is False
            assert result["details"]["routing"] is False


class TestRollbackSystem:
    """Test Rollback System validator."""
    
    def test_all_components_present_returns_healthy(self, validator, mock_root):
        """When guide, rules, and tests exist, return healthy."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists', return_value=True):
            
            result = validator.validate_rollback_system()
            
            assert result["status"] == "healthy"
            assert result["details"]["docs"] is True
            assert result["details"]["rules"] is True
            assert result["details"]["tests"] is True
    
    def test_missing_tests_returns_warning(self, validator, mock_root):
        """When tests missing but docs/rules OK, return warning."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists') as mock_exists:
            
            # Tests missing, others exist
            mock_exists.side_effect = lambda p: "test_git_checkpoint" not in str(p)
            
            result = validator.validate_rollback_system()
            
            assert result["status"] == "warning"
            assert "Missing checkpoint system tests" in result["issues"]
            assert result["details"]["tests"] is False
    
    def test_missing_all_components_returns_critical(self, validator, mock_root):
        """When all components missing, return critical."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists', return_value=False):
            
            result = validator.validate_rollback_system()
            
            assert result["status"] == "critical"
            assert len(result["issues"]) == 3
            assert result["details"]["docs"] is False
            assert result["details"]["rules"] is False
            assert result["details"]["tests"] is False


class TestSwaggerDoR:
    """Test Planning DoR/DoD system validator."""
    
    def test_complete_planning_system_returns_healthy(self, validator, mock_root):
        """When guide exists and both routing triggers work, return healthy."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists', return_value=True), \
             patch.object(validator, '_load_response_templates') as mock_templates, \
             patch.object(validator, '_template_has_triggers', return_value=True):
            
            mock_templates.return_value = {"templates": {}}
            
            result = validator.validate_swagger_dor()
            
            assert result["status"] == "healthy"
            assert result["details"]["docs"] is True
            assert result["details"]["ado_routing"] is True
            assert result["details"]["planning_routing"] is True
    
    def test_missing_ado_routing_returns_warning(self, validator, mock_root):
        """When ADO routing missing but guide and planning OK, return warning."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists', return_value=True), \
             patch.object(validator, '_load_response_templates') as mock_templates, \
             patch.object(validator, '_template_has_triggers') as mock_triggers:
            
            mock_templates.return_value = {"templates": {}}
            # ADO routing fails, planning routing succeeds
            mock_triggers.side_effect = [False, True]
            
            result = validator.validate_swagger_dor()
            
            assert result["status"] == "warning"
            assert result["details"]["ado_routing"] is False
            assert result["details"]["planning_routing"] is True


class TestADOAgent:
    """Test ADO Agent validator."""
    
    def test_complete_ado_system_returns_healthy(self, validator, mock_root):
        """When routing, agent, and DB all exist, return healthy."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists', return_value=True), \
             patch.object(validator, '_load_response_templates') as mock_templates, \
             patch.object(validator, '_template_has_triggers', return_value=True):
            
            mock_templates.return_value = {"templates": {}}
            
            result = validator.validate_ado_agent()
            
            assert result["status"] == "healthy"
            assert result["details"]["routing"] is True
            assert result["details"]["agent"] is True
            assert result["details"]["db"] is True
    
    def test_missing_database_returns_warning(self, validator, mock_root):
        """When DB missing but routing and agent OK, return warning."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists') as mock_exists, \
             patch.object(validator, '_load_response_templates') as mock_templates, \
             patch.object(validator, '_template_has_triggers', return_value=True):
            
            # DB missing, others exist
            mock_exists.side_effect = lambda p: "ado-work-items.db" not in str(p)
            mock_templates.return_value = {"templates": {}}
            
            result = validator.validate_ado_agent()
            
            assert result["status"] == "warning"
            assert "Missing ado-work-items.db" in result["issues"]
            assert result["details"]["db"] is False
    
    def test_missing_all_components_returns_critical(self, validator, mock_root):
        """When routing, agent, and DB all missing, return critical."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(validator, '_exists', return_value=False), \
             patch.object(validator, '_load_response_templates', return_value=None):
            
            result = validator.validate_ado_agent()
            
            assert result["status"] == "critical"
            assert len(result["issues"]) >= 2
            assert result["details"]["routing"] is False
            assert result["details"]["agent"] is False
            assert result["details"]["db"] is False


class TestHelperMethods:
    """Test helper methods for status construction."""
    
    def test_ok_status(self, validator):
        """Test _ok helper constructs healthy status."""
        result = validator._ok({"test": True})
        
        assert result["status"] == "healthy"
        assert result["details"]["test"] is True
        assert result["issues"] == []
    
    def test_warn_status(self, validator):
        """Test _warn helper constructs warning status."""
        result = validator._warn(["Issue 1", "Issue 2"], {"test": False})
        
        assert result["status"] == "warning"
        assert result["details"]["test"] is False
        assert len(result["issues"]) == 2
    
    def test_crit_status(self, validator):
        """Test _crit helper constructs critical status."""
        result = validator._crit(["Critical issue"], {"test": False})
        
        assert result["status"] == "critical"
        assert result["details"]["test"] is False
        assert "Critical issue" in result["issues"]
    
    def test_error_status(self, validator):
        """Test _error helper constructs error status.
        
        Note: Error messages are stored in the 'issues' list, not a separate 'message' field.
        """
        error = ValueError("Test error")
        result = validator._error(error)
        
        assert result["status"] == "error"
        assert result["details"] == {}
        assert len(result["issues"]) == 1
        assert "Test error" in result["issues"][0]


class TestTemplateLoading:
    """Test YAML template loading helpers."""
    
    def test_load_response_templates_success(self, validator, mock_root):
        """Test successful template loading."""
        yaml_content = """
templates:
  test_template:
    triggers:
      - test trigger
"""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch('builtins.open', create=True) as mock_open, \
             patch('yaml.safe_load') as mock_yaml:
            
            mock_yaml.return_value = {"templates": {"test_template": {"triggers": ["test trigger"]}}}
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = validator._load_response_templates()
            
            assert result is not None
            assert "templates" in result
    
    def test_load_response_templates_file_not_found(self, validator, mock_root):
        """Test template loading when file doesn't exist."""
        with patch.object(validator, '_root', return_value=mock_root), \
             patch.object(Path, 'exists', return_value=False):
            
            result = validator._load_response_templates()
            
            assert result is None
    
    def test_template_has_triggers_all_present(self, validator):
        """Test trigger checking when all expected triggers present."""
        templates = {
            "templates": {
                "test_template": {
                    "triggers": ["trigger1", "trigger2", "trigger3"]
                }
            }
        }
        
        result = validator._template_has_triggers(templates, "test_template", ["trigger1", "trigger2"])
        
        assert result is True
    
    def test_template_has_triggers_some_missing(self, validator):
        """Test trigger checking when some triggers missing."""
        templates = {
            "templates": {
                "test_template": {
                    "triggers": ["trigger1"]
                }
            }
        }
        
        result = validator._template_has_triggers(templates, "test_template", ["trigger1", "trigger2"])
        
        assert result is False
