"""
Integration tests for SystemAlignmentOrchestrator.

Tests the convention-based discovery and validation system that auto-discovers
all CORTEX features and validates their integration depth.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.admin.system_alignment_orchestrator import (
    SystemAlignmentOrchestrator,
    IntegrationScore,
    AlignmentReport,
    RemediationSuggestion
)
from src.operations.base_operation_module import OperationStatus


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with necessary structure."""
    # Create admin directory to simulate admin environment
    admin_dir = tmp_path / "cortex-brain" / "admin"
    admin_dir.mkdir(parents=True)
    
    # Create source directories
    (tmp_path / "src" / "operations" / "modules").mkdir(parents=True)
    (tmp_path / "src" / "agents").mkdir(parents=True)
    (tmp_path / "src" / "workflows").mkdir(parents=True)
    
    # Create templates file
    templates_file = tmp_path / "cortex-brain" / "response-templates.yaml"
    templates_file.write_text("templates: {}\nrouting: {}")
    
    return tmp_path


@pytest.fixture
def orchestrator(project_root):
    """Create SystemAlignmentOrchestrator instance."""
    context = {"project_root": str(project_root)}
    return SystemAlignmentOrchestrator(context)


@pytest.fixture
def context(project_root):
    """Create test context."""
    return {
        "project_root": str(project_root),
        "user_request": "align"
    }


class TestSystemAlignmentOrchestrator:
    """Test SystemAlignmentOrchestrator functionality."""
    
    def test_initialization(self, orchestrator, project_root):
        """Test orchestrator initializes correctly."""
        assert orchestrator.project_root == project_root
        assert orchestrator.cortex_brain == project_root / "cortex-brain"
        assert orchestrator._orchestrator_scanner is None  # Lazy loaded
    
    def test_is_admin_environment_true(self, orchestrator):
        """Test admin environment detection returns true."""
        assert orchestrator._is_admin_environment() is True
    
    def test_is_admin_environment_false(self, tmp_path):
        """Test admin environment detection returns false without admin directory."""
        context = {"project_root": str(tmp_path)}
        orch = SystemAlignmentOrchestrator(context)
        assert orch._is_admin_environment() is False
    
    def test_validate_returns_true_in_admin_env(self, orchestrator, context):
        """Test validate returns true in admin environment."""
        assert orchestrator.validate(context) is True
    
    def test_validate_returns_false_in_user_env(self, tmp_path):
        """Test validate returns false in user environment."""
        context = {"project_root": str(tmp_path)}
        orch = SystemAlignmentOrchestrator(context)
        assert orch.validate(context) is False
    
    def test_validate_prerequisites_admin_env(self, orchestrator, context):
        """Test validate_prerequisites in admin environment."""
        valid, errors = orchestrator.validate_prerequisites(context)
        assert valid is True
        assert len(errors) == 0
    
    def test_validate_prerequisites_user_env(self, tmp_path):
        """Test validate_prerequisites in user environment."""
        context = {"project_root": str(tmp_path)}
        orch = SystemAlignmentOrchestrator(context)
        valid, errors = orch.validate_prerequisites(context)
        assert valid is False
        assert "Admin environment required" in errors
    
    @patch('src.operations.modules.admin.system_alignment_orchestrator.SystemAlignmentOrchestrator._discover_orchestrators')
    @patch('src.operations.modules.admin.system_alignment_orchestrator.SystemAlignmentOrchestrator._discover_agents')
    def test_execute_success(self, mock_agents, mock_orchestrators, orchestrator, context):
        """Test successful alignment execution."""
        # Mock discovery returns
        mock_orchestrators.return_value = {
            "TestOrchestrator": {
                "file_path": "src/test_orch.py",
                "class_name": "TestOrchestrator",
                "has_docstring": True
            }
        }
        mock_agents.return_value = {}
        
        # Mock other dependencies
        with patch.object(orchestrator, '_validate_entry_points', return_value=([], [])):
            with patch.object(orchestrator, '_calculate_integration_score') as mock_score:
                mock_score.return_value = IntegrationScore(
                    feature_name="TestOrchestrator",
                    feature_type="orchestrator",
                    discovered=True,
                    imported=True,
                    instantiated=True,
                    documented=True,
                    tested=True,
                    wired=True,
                    optimized=False
                )
                
                with patch.object(orchestrator, '_validate_documentation', return_value=[]):
                    with patch.object(orchestrator, '_validate_deployment_readiness'):
                        with patch.object(orchestrator, '_generate_remediation_suggestions'):
                            result = orchestrator.execute(context)
        
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        assert "report" in result.data
        assert isinstance(result.data["report"], AlignmentReport)
    
    def test_execute_failure_in_user_env(self, tmp_path):
        """Test execute fails gracefully in user environment."""
        context = {"project_root": str(tmp_path)}
        orch = SystemAlignmentOrchestrator(context)
        
        result = orch.execute(context)
        
        # Should still execute but return warning status (discovers 0 features)
        assert result.success is False
        assert result.status in [OperationStatus.FAILED, OperationStatus.WARNING]
    
    def test_run_full_validation_structure(self, orchestrator):
        """Test run_full_validation returns proper report structure."""
        with patch.object(orchestrator, '_discover_orchestrators', return_value={}):
            with patch.object(orchestrator, '_discover_agents', return_value={}):
                with patch.object(orchestrator, '_validate_entry_points', return_value=([], [])):
                    with patch.object(orchestrator, '_validate_documentation', return_value=[]):
                        with patch.object(orchestrator, '_validate_deployment_readiness'):
                            with patch.object(orchestrator, '_generate_remediation_suggestions'):
                                report = orchestrator.run_full_validation()
        
        assert isinstance(report, AlignmentReport)
        assert report.overall_health >= 0
        assert report.overall_health <= 100
        assert isinstance(report.feature_scores, dict)
        assert isinstance(report.remediation_suggestions, list)
    
    def test_get_metadata(self, orchestrator):
        """Test get_metadata returns correct information."""
        metadata = orchestrator.get_metadata()
        
        assert metadata.module_id == "system_alignment"
        assert metadata.name == "System Alignment Validator"
        assert "alignment" in metadata.tags
        assert "admin" in metadata.tags
    
    def test_rollback_always_succeeds(self, orchestrator, context):
        """Test rollback always returns true (read-only operation)."""
        assert orchestrator.rollback(context) is True


class TestIntegrationScore:
    """Test IntegrationScore data class."""
    
    def test_score_calculation_all_true(self):
        """Test score calculation with all checks passing."""
        score = IntegrationScore(
            feature_name="TestFeature",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=True,
            documented=True,
            tested=True,
            wired=True,
            optimized=True
        )
        
        assert score.score == 100
        assert score.status == "✅ Healthy"
        assert len(score.issues) == 0
    
    def test_score_calculation_partial(self):
        """Test score calculation with some checks failing."""
        score = IntegrationScore(
            feature_name="TestFeature",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=True,
            documented=False,
            tested=False,
            wired=False,
            optimized=False
        )
        
        assert score.score == 60
        assert score.status == "❌ Critical"
        assert "Missing documentation" in score.issues
        assert "No test coverage" in score.issues
        assert "Not wired to entry point" in score.issues
    
    def test_score_status_healthy(self):
        """Test status returns healthy for >90% score."""
        score = IntegrationScore(
            feature_name="Test",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=True,
            documented=True,
            tested=True,
            wired=True,
            optimized=False
        )
        
        assert score.score == 90
        assert "✅ Healthy" in score.status
    
    def test_score_status_warning(self):
        """Test status returns warning for 70-89% score."""
        score = IntegrationScore(
            feature_name="Test",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=True,
            documented=True,
            tested=False,
            wired=False,
            optimized=False
        )
        
        assert score.score == 70
        assert "⚠️ Warning" in score.status
    
    def test_score_status_critical(self):
        """Test status returns critical for <70% score."""
        score = IntegrationScore(
            feature_name="Test",
            feature_type="orchestrator",
            discovered=True,
            imported=True,
            instantiated=False,
            documented=False,
            tested=False,
            wired=False,
            optimized=False
        )
        
        assert score.score == 40
        assert "❌ Critical" in score.status


class TestAlignmentReport:
    """Test AlignmentReport data class."""
    
    def test_is_healthy_true(self):
        """Test is_healthy returns true for good health."""
        report = AlignmentReport(
            timestamp=None,
            overall_health=85,
            critical_issues=0
        )
        
        assert report.is_healthy is True
    
    def test_is_healthy_false_low_health(self):
        """Test is_healthy returns false for low health."""
        report = AlignmentReport(
            timestamp=None,
            overall_health=75,
            critical_issues=0
        )
        
        assert report.is_healthy is False
    
    def test_is_healthy_false_critical_issues(self):
        """Test is_healthy returns false with critical issues."""
        report = AlignmentReport(
            timestamp=None,
            overall_health=85,
            critical_issues=1
        )
        
        assert report.is_healthy is False
    
    def test_has_warnings_true(self):
        """Test has_warnings returns true with warnings."""
        report = AlignmentReport(
            timestamp=None,
            overall_health=80,
            critical_issues=0,
            warnings=3
        )
        
        assert report.has_warnings is True
        assert report.has_errors is False
    
    def test_has_errors_true(self):
        """Test has_errors returns true with critical issues."""
        report = AlignmentReport(
            timestamp=None,
            overall_health=60,
            critical_issues=2,
            warnings=1
        )
        
        assert report.has_errors is True
    
    def test_issues_found(self):
        """Test issues_found counts correctly."""
        report = AlignmentReport(
            timestamp=None,
            overall_health=70,
            critical_issues=2,
            warnings=5
        )
        
        assert report.issues_found == 7


class TestRemediationSuggestion:
    """Test RemediationSuggestion data class."""
    
    def test_remediation_suggestion_creation(self):
        """Test RemediationSuggestion can be created."""
        suggestion = RemediationSuggestion(
            feature_name="TestFeature",
            suggestion_type="wiring",
            content="Add template to response-templates.yaml",
            file_path="cortex-brain/templates/response-templates.yaml"
        )
        
        assert suggestion.feature_name == "TestFeature"
        assert suggestion.suggestion_type == "wiring"
        assert "template" in suggestion.content
        assert suggestion.file_path is not None


@pytest.mark.integration
class TestSystemAlignmentIntegration:
    """Integration tests with real filesystem."""
    
    def test_alignment_on_real_project(self):
        """Test alignment runs on actual CORTEX project."""
        project_root = Path.cwd()
        
        # Skip if not in CORTEX project
        if not (project_root / "cortex-brain" / "admin").exists():
            pytest.skip("Not in CORTEX admin environment")
        
        context = {"project_root": str(project_root)}
        orchestrator = SystemAlignmentOrchestrator(context)
        
        result = orchestrator.execute(context)
        
        assert result.success is True
        assert "report" in result.data
        
        report = result.data["report"]
        assert report.overall_health > 0
        assert isinstance(report.feature_scores, dict)
        assert len(report.feature_scores) > 0
    
    def test_discovers_system_alignment_orchestrator(self):
        """Test that alignment discovers itself."""
        project_root = Path.cwd()
        
        if not (project_root / "cortex-brain" / "admin").exists():
            pytest.skip("Not in CORTEX admin environment")
        
        context = {"project_root": str(project_root)}
        orchestrator = SystemAlignmentOrchestrator(context)
        
        result = orchestrator.execute(context)
        report = result.data["report"]
        
        # Should discover itself
        assert "SystemAlignmentOrchestrator" in report.feature_scores
        score = report.feature_scores["SystemAlignmentOrchestrator"]
        assert score.discovered is True
        assert score.imported is True
