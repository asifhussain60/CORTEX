"""
Tests for OptimizeCortexOrchestrator Phase 4 Enhancements

Tests admin detection and silent alignment integration:
- Admin environment detection
- Silent alignment validation
- Integration with optimize workflow
- User environment graceful decline

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

from src.operations.modules.optimization.optimize_cortex_orchestrator import (
    OptimizeCortexOrchestrator,
    OptimizationMetrics
)
from src.operations.base_operation_module import OperationStatus


@pytest.fixture
def temp_project():
    """Create temporary project structure."""
    with tempfile.TemporaryDirectory() as tmpdir:
        project_root = Path(tmpdir)
        
        # Create basic structure
        (project_root / "src").mkdir()
        (project_root / "tests").mkdir()
        (project_root / "cortex-brain").mkdir()
        (project_root / ".git").mkdir()
        (project_root / "cortex-brain" / "knowledge-graph.yaml").write_text("patterns: []")
        
        yield project_root


@pytest.fixture
def admin_project(temp_project):
    """Create project with admin directories."""
    admin_dir = temp_project / "src" / "operations" / "modules" / "admin"
    admin_dir.mkdir(parents=True)
    (admin_dir / "system_alignment_orchestrator.py").write_text("# Admin code")
    
    yield temp_project


@pytest.fixture
def user_project(temp_project):
    """Create project without admin directories (user environment)."""
    yield temp_project


class TestAdminEnvironmentDetection:
    """Test admin environment detection."""
    
    def test_admin_environment_with_admin_ops_dir(self, admin_project):
        """Test admin detection with admin operations directory."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = admin_project
        
        assert orchestrator._is_admin_environment(admin_project)
    
    def test_admin_environment_with_admin_brain_dir(self, temp_project):
        """Test admin detection with admin brain directory."""
        admin_brain = temp_project / "cortex-brain" / "admin"
        admin_brain.mkdir(parents=True)
        
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = temp_project
        
        assert orchestrator._is_admin_environment(temp_project)
    
    def test_user_environment_no_admin_dirs(self, user_project):
        """Test user environment detection (no admin directories)."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = user_project
        
        assert not orchestrator._is_admin_environment(user_project)
    
    def test_admin_environment_both_admin_dirs(self, admin_project):
        """Test admin detection with both admin directories present."""
        admin_brain = admin_project / "cortex-brain" / "admin"
        admin_brain.mkdir(parents=True)
        
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = admin_project
        
        assert orchestrator._is_admin_environment(admin_project)


class TestSilentAlignmentCheck:
    """Test silent alignment validation."""
    
    def test_alignment_check_in_admin_environment(self, admin_project):
        """Test alignment check runs in admin environment."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = admin_project
        metrics = OptimizationMetrics(
            optimization_id="test_001",
            timestamp=MagicMock()
        )
        
        # Mock SystemAlignmentOrchestrator
        mock_alignment = MagicMock()
        mock_alignment.execute.return_value = MagicMock(
            success=True,
            data={'report': MagicMock(is_healthy=True, critical_issues=0, warnings=0)}
        )
        
        with patch('src.operations.modules.admin.system_alignment_orchestrator.SystemAlignmentOrchestrator', return_value=mock_alignment):
            result = orchestrator._run_alignment_check(admin_project, metrics)
        
        assert result is not None
        assert result['is_healthy']
    
    def test_alignment_check_detects_issues(self, admin_project):
        """Test alignment check reports issues when detected."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = admin_project
        metrics = OptimizationMetrics(
            optimization_id="test_002",
            timestamp=MagicMock()
        )
        
        # Mock unhealthy system
        mock_report = MagicMock()
        mock_report.is_healthy = False
        mock_report.critical_issues = 3
        mock_report.warnings = 5
        
        mock_alignment = MagicMock()
        mock_alignment.execute.return_value = MagicMock(
            success=True,
            data={'report': mock_report}
        )
        
        with patch('src.operations.modules.admin.system_alignment_orchestrator.SystemAlignmentOrchestrator', return_value=mock_alignment):
            result = orchestrator._run_alignment_check(admin_project, metrics)
        
        assert result is not None
        assert not result['is_healthy']
        assert "3 critical issues, 5 warnings" in result['message']
    
    def test_alignment_check_handles_import_error(self, user_project):
        """Test alignment check gracefully handles missing SystemAlignmentOrchestrator."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = user_project
        metrics = OptimizationMetrics(
            optimization_id="test_003",
            timestamp=MagicMock()
        )
        
        # Simulate ImportError during import inside method
        def mock_import(name, *args, **kwargs):
            if 'system_alignment_orchestrator' in name:
                raise ImportError("Module not found")
            return __import__(name, *args, **kwargs)
        
        with patch('builtins.__import__', side_effect=mock_import):
            result = orchestrator._run_alignment_check(user_project, metrics)
        
        assert result is None  # Should return None in user environment
    
    def test_alignment_check_handles_execution_failure(self, admin_project):
        """Test alignment check handles execution failures gracefully."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = admin_project
        metrics = OptimizationMetrics(
            optimization_id="test_004",
            timestamp=MagicMock()
        )
        
        # Mock failed execution
        mock_alignment = MagicMock()
        mock_alignment.execute.return_value = MagicMock(
            success=False,
            message="Validation failed",
            data=None
        )
        
        with patch('src.operations.modules.admin.system_alignment_orchestrator.SystemAlignmentOrchestrator', return_value=mock_alignment):
            result = orchestrator._run_alignment_check(admin_project, metrics)
        
        assert result is not None
        assert not result['is_healthy']
        assert "Validation failed" in result['message']


class TestOptimizeWorkflowIntegration:
    """Test alignment integration into optimize workflow."""
    
    def test_execute_skips_alignment_in_user_environment(self, user_project):
        """Test optimize workflow skips alignment in user environment."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = user_project
        
        # Mock all phases to avoid actual execution
        with patch.object(orchestrator, '_validate_planning_rules', return_value={'success': True}):
            with patch.object(orchestrator, '_run_skull_tests', return_value={'success': True}):
                with patch.object(orchestrator, '_analyze_architecture', return_value={}):
                    with patch.object(orchestrator, '_generate_optimization_plan', return_value={}):
                        with patch.object(orchestrator, '_execute_optimizations', return_value={}):
                            with patch.object(orchestrator, '_generate_optimization_report', return_value="Report"):
                                with patch.object(orchestrator, '_is_admin_environment', return_value=False) as mock_admin_check:
                                    with patch.object(orchestrator, '_run_alignment_check') as mock_alignment:
                                        result = orchestrator.execute({'project_root': user_project})
                                        
                                        # Admin check should be called
                                        mock_admin_check.assert_called_once()
                                        # But alignment check should NOT be called
                                        mock_alignment.assert_not_called()
        
        assert result.success
    
    def test_execute_runs_alignment_in_admin_environment(self, admin_project):
        """Test optimize workflow runs alignment in admin environment."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = admin_project
        
        # Mock all phases
        with patch.object(orchestrator, '_validate_planning_rules', return_value={'success': True}):
            with patch.object(orchestrator, '_run_skull_tests', return_value={'success': True}):
                with patch.object(orchestrator, '_is_admin_environment', return_value=True):
                    with patch.object(orchestrator, '_run_alignment_check', return_value={'is_healthy': True}) as mock_alignment:
                        with patch.object(orchestrator, '_analyze_architecture', return_value={}):
                            with patch.object(orchestrator, '_generate_optimization_plan', return_value={}):
                                with patch.object(orchestrator, '_execute_optimizations', return_value={}):
                                    with patch.object(orchestrator, '_generate_optimization_report', return_value="Report"):
                                        result = orchestrator.execute({'project_root': admin_project})
                                        
                                        # Alignment check should be called
                                        mock_alignment.assert_called_once()
        
        assert result.success
    
    def test_execute_warns_on_alignment_issues(self, admin_project, caplog):
        """Test optimize workflow warns when alignment issues detected."""
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = admin_project
        
        # Mock unhealthy alignment
        mock_alignment_result = {
            'is_healthy': False,
            'message': '3 critical issues detected'
        }
        
        with patch.object(orchestrator, '_validate_planning_rules', return_value={'success': True}):
            with patch.object(orchestrator, '_run_skull_tests', return_value={'success': True}):
                with patch.object(orchestrator, '_is_admin_environment', return_value=True):
                    with patch.object(orchestrator, '_run_alignment_check', return_value=mock_alignment_result):
                        with patch.object(orchestrator, '_analyze_architecture', return_value={}):
                            with patch.object(orchestrator, '_generate_optimization_plan', return_value={}):
                                with patch.object(orchestrator, '_execute_optimizations', return_value={}):
                                    with patch.object(orchestrator, '_generate_optimization_report', return_value="Report"):
                                        result = orchestrator.execute({'project_root': admin_project})
                                        
                                        # Should still succeed (alignment doesn't fail optimization)
                                        assert result.success
                                        
                                        # But should log warning
                                        assert any("alignment issues detected" in record.message.lower() for record in caplog.records)
