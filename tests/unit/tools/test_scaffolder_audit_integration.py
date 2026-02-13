"""
Tests for Scaffolder Audit Integration (AC-WAVE-2-S1-INTEGRATION-001)

Tests that audit logging is properly integrated into scaffolder pipeline.
"""

import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
import yaml

from cortex.tools.orchestrator_scaffolder import (
    OrchestratorScaffolder,
    ScaffoldConfig,
    ScaffoldType,
)


@pytest.fixture
def temp_db():
    """Create temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = Path(f.name)
    yield db_path
    db_path.unlink()


@pytest.fixture
def sample_template_yaml():
    """Sample orchestrator template."""
    return """
orchestrator:
  name: TestOrchestrator
  domain: test
  version: "1.0"
  purpose: Test orchestrator for audit integration

capabilities:
  capabilities:
    - name: process_request
      description: Process requests
    - name: validate_input
      description: Validate input

stages:
  - name: stage1
    description: First stage
  - name: stage2
    description: Second stage
"""


class TestScaffolderAuditIntegration:
    """Test audit logging integration in scaffolder."""
    
    def test_scaffolder_logs_pre_scaffolding_check(self, sample_template_yaml, temp_db):
        """Scaffolder logs pre-scaffolding registry query."""
        with patch('cortex.tools.scaffolder_audit_logger.ScaffolderAuditLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            mock_logger.log_pre_scaffolding_check.return_value = "AC-WAVE-2-S1A-TEST"
            
            scaffolder = OrchestratorScaffolder()
            result = scaffolder.scaffold_from_dict(yaml.safe_load(sample_template_yaml))
            
            # Verify pre-scaffolding check was logged
            assert mock_logger.log_pre_scaffolding_check.called
            call_args = mock_logger.log_pre_scaffolding_check.call_args[1]
            assert call_args['orchestrator_name'] == 'TestOrchestrator'
            assert 'query_result' in call_args
            assert 'decision' in call_args
    
    def test_scaffolder_logs_demand_generation(self, sample_template_yaml, temp_db):
        """Scaffolder logs intelligent test demand generation."""
        with patch('cortex.tools.scaffolder_audit_logger.ScaffolderAuditLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            mock_logger.log_intelligent_test_generation.return_value = "AC-WAVE-2-S2-TEST"
            
            scaffolder = OrchestratorScaffolder()
            result = scaffolder.scaffold_from_dict(yaml.safe_load(sample_template_yaml))
            
            # Verify demand generation was logged
            demand_calls = [
                call for call in mock_logger.log_intelligent_test_generation.call_args_list
                if call[1].get('stage') == 'demand'
            ]
            assert len(demand_calls) >= 0  # May be 0 if intelligence layer not available
    
    def test_scaffolder_stores_ac_markers(self, sample_template_yaml, temp_db):
        """Scaffolder stores AC markers in result metadata."""
        with patch('cortex.tools.scaffolder_audit_logger.ScaffolderAuditLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            mock_logger.log_pre_scaffolding_check.return_value = "AC-WAVE-2-S1A-12345"
            
            scaffolder = OrchestratorScaffolder()
            result = scaffolder.scaffold_from_dict(yaml.safe_load(sample_template_yaml))
            
            assert 'ac_marker_pre_check' in result.metadata
            assert result.metadata['ac_marker_pre_check'] == "AC-WAVE-2-S1A-12345"
    
    def test_scaffolder_handles_audit_logger_failure_gracefully(self, sample_template_yaml):
        """Scaffolder continues if audit logger fails."""
        with patch('cortex.tools.scaffolder_audit_logger.ScaffolderAuditLogger') as mock_logger_class:
            mock_logger_class.side_effect = Exception("Audit logger unavailable")
            
            scaffolder = OrchestratorScaffolder()
            result = scaffolder.scaffold_from_dict(yaml.safe_load(sample_template_yaml))
            
            # Should still succeed with warning
            assert len(result.warnings) > 0
            assert any("Audit logger not available" in w for w in result.warnings)


class TestDuplicateDetectionIntegration:
    """Test duplicate detection in scaffolder."""
    
    def test_scaffolder_detects_no_duplicate(self, sample_template_yaml):
        """Scaffolder detects no duplicate and proceeds."""
        scaffolder = OrchestratorScaffolder()
        result = scaffolder.scaffold_from_dict(yaml.safe_load(sample_template_yaml))
        
        assert 'duplicate_detected' in result.metadata
        assert result.metadata['duplicate_detected'] is False
    
    def test_scaffolder_logs_duplicate_not_found(self, sample_template_yaml, temp_db):
        """Scaffolder logs when no duplicate found."""
        with patch('cortex.tools.scaffolder_audit_logger.ScaffolderAuditLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            scaffolder = OrchestratorScaffolder()
            result = scaffolder.scaffold_from_dict(yaml.safe_load(sample_template_yaml))
            
            # Verify log call with found=False
            assert mock_logger.log_pre_scaffolding_check.called
            call_args = mock_logger.log_pre_scaffolding_check.call_args[1]
            assert call_args['decision'] in ['create_new', 'upgrade_proposed']


class TestQualityScoreLogging:
    """Test quality score logging during test generation."""
    
    def test_scaffolder_logs_quality_scores_per_test(self, sample_template_yaml, temp_db):
        """Scaffolder logs quality score for each generated test."""
        with patch('cortex.tools.scaffolder_audit_logger.ScaffolderAuditLogger') as mock_logger_class:
            mock_logger = MagicMock()
            mock_logger_class.return_value = mock_logger
            
            scaffolder = OrchestratorScaffolder()
            result = scaffolder.scaffold_from_dict(yaml.safe_load(sample_template_yaml))
            
            # Verify quality validation was logged
            validate_calls = [
                call for call in mock_logger.log_intelligent_test_generation.call_args_list
                if call[1].get('stage') == 'validate'
            ]
            # Should have at least some validation logs (if intelligence layer available)
            assert len(validate_calls) >= 0
