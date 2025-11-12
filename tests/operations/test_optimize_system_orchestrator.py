"""
Tests for System Optimization Meta-Orchestrator.

These tests validate the meta-level orchestrator that coordinates
all CORTEX optimization operations.

SKULL-001 compliance: Tests must pass before claiming optimize_system is production-ready.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.system.optimize_system_orchestrator import (
    OptimizeSystemOrchestrator,
    OptimizationMetrics,
    SystemHealthReport,
    ExecutionMode
)
from src.operations.base_operation_module import OperationStatus


class TestOptimizeSystemOrchestrator:
    """Test suite for System Optimization Meta-Orchestrator."""
    
    @pytest.fixture
    def project_root(self, tmp_path):
        """Create temporary project structure."""
        # Create required directories
        (tmp_path / "src" / "operations" / "modules" / "design_sync").mkdir(parents=True)
        (tmp_path / "src" / "operations" / "modules" / "optimize").mkdir(parents=True)
        (tmp_path / "cortex-brain").mkdir(parents=True)
        (tmp_path / ".git").mkdir(parents=True)
        
        # Create placeholder orchestrator files
        (tmp_path / "src" / "operations" / "modules" / "design_sync" / "design_sync_orchestrator.py").touch()
        (tmp_path / "src" / "operations" / "modules" / "optimize" / "optimize_cortex_orchestrator.py").touch()
        
        return tmp_path
    
    @pytest.fixture
    def orchestrator(self, project_root):
        """Create orchestrator instance."""
        return OptimizeSystemOrchestrator(project_root=project_root, mode=ExecutionMode.DRY_RUN)
    
    def test_orchestrator_initialization(self, orchestrator, project_root):
        """Test orchestrator initializes correctly."""
        assert orchestrator.project_root == project_root
        assert orchestrator.mode == ExecutionMode.DRY_RUN
        assert isinstance(orchestrator.metrics, OptimizationMetrics)
        assert orchestrator.VERSION == "1.0.0"
    
    def test_metadata_properties(self, orchestrator):
        """Test orchestrator metadata is correct."""
        metadata = orchestrator.metadata
        
        assert metadata.module_id == "optimize_system_orchestrator"
        assert metadata.name == "System Optimization Meta-Orchestrator"
        assert metadata.version == "1.0.0"
        assert "comprehensive" in metadata.description.lower()
    
    def test_prerequisite_validation_success(self, orchestrator):
        """Test prerequisite validation passes with valid setup."""
        result = orchestrator.validate_prerequisites({})
        
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        assert "validated" in result.message.lower()
    
    def test_prerequisite_validation_failure_missing_directory(self, tmp_path):
        """Test prerequisite validation fails with missing directories."""
        # Create orchestrator with non-existent root
        bad_root = tmp_path / "nonexistent"
        orchestrator = OptimizeSystemOrchestrator(project_root=bad_root)
        
        result = orchestrator.validate_prerequisites({})
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert len(result.errors) > 0
        assert "Project root not found" in result.errors[0]
    
    def test_prerequisite_validation_failure_missing_orchestrators(self, project_root):
        """Test prerequisite validation fails with missing orchestrators."""
        # Remove orchestrator files
        (project_root / "src" / "operations" / "modules" / "design_sync" / "design_sync_orchestrator.py").unlink()
        
        orchestrator = OptimizeSystemOrchestrator(project_root=project_root)
        result = orchestrator.validate_prerequisites({})
        
        assert result.success is False
        assert len(result.errors) > 0
        assert "design_sync_orchestrator.py not found" in result.errors[0]
    
    def test_execute_dry_run_mode(self, orchestrator, project_root):
        """Test execution in dry-run mode."""
        context = {
            'profile': 'minimal',
            'mode': 'dry_run',
            'skip_phases': ['design_sync', 'code_health', 'brain_tuning', 'entry_point_alignment', 'test_suite']
        }
        
        result = orchestrator.execute(context)
        
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        assert orchestrator.mode == ExecutionMode.DRY_RUN
        assert "complete" in result.message.lower()
    
    def test_execute_live_mode(self, orchestrator, project_root):
        """Test execution in live mode."""
        orchestrator.mode = ExecutionMode.LIVE
        
        context = {
            'profile': 'minimal',
            'mode': 'live',
            'skip_phases': ['design_sync', 'code_health', 'brain_tuning', 'entry_point_alignment', 'test_suite']
        }
        
        result = orchestrator.execute(context)
        
        assert result.success is True
        assert orchestrator.mode == ExecutionMode.LIVE
    
    def test_calculate_total_improvements(self, orchestrator):
        """Test improvement calculation."""
        orchestrator.metrics.design_drift_resolved = 5
        orchestrator.metrics.obsolete_tests_identified = 3
        orchestrator.metrics.tier_violations_fixed = 2
        orchestrator.metrics.tests_fixed = 4
        
        total = orchestrator._calculate_total_improvements()
        
        assert total == 14  # 5 + 3 + 2 + 4
    
    def test_health_score_calculation(self, orchestrator):
        """Test health score calculation."""
        # Base score with no errors/warnings
        score = orchestrator._calculate_health_score()
        assert 0.0 <= score <= 100.0
        
        # Add errors - should decrease score
        orchestrator.metrics.errors_encountered.append("Error 1")
        score_with_error = orchestrator._calculate_health_score()
        assert score_with_error < score
        
        # Add warnings - should decrease score further
        orchestrator.metrics.warnings.append("Warning 1")
        score_with_warning = orchestrator._calculate_health_score()
        assert score_with_warning < score_with_error
    
    def test_generate_health_report(self, orchestrator):
        """Test health report generation."""
        orchestrator.metrics.design_drift_resolved = 5
        orchestrator.metrics.total_improvements = 10
        
        report = orchestrator._generate_health_report()
        
        assert isinstance(report, SystemHealthReport)
        assert report.overall_health in ['excellent', 'good', 'fair', 'poor', 'critical']
        assert 0.0 <= report.health_score <= 100.0
        assert isinstance(report.recommendations, list)
        assert isinstance(report.next_actions, list)
    
    def test_report_to_dict(self, orchestrator):
        """Test health report serialization."""
        report = orchestrator._generate_health_report()
        report_dict = report.to_dict()
        
        assert 'timestamp' in report_dict
        assert 'overall_health' in report_dict
        assert 'health_score' in report_dict
        assert 'metrics' in report_dict
        assert 'recommendations' in report_dict
        assert 'next_actions' in report_dict
        
        # Verify nested metrics structure
        assert 'design_sync' in report_dict['metrics']
        assert 'code_health' in report_dict['metrics']
        assert 'brain_tuning' in report_dict['metrics']
        assert 'entry_point_alignment' in report_dict['metrics']
        assert 'test_suite' in report_dict['metrics']
    
    def test_save_report(self, orchestrator, project_root):
        """Test report saving to file."""
        report = orchestrator._generate_health_report()
        report_path = project_root / "cortex-brain" / "system-optimization-report.md"
        
        orchestrator._save_report(report, report_path)
        
        assert report_path.exists()
        content = report_path.read_text(encoding='utf-8')
        
        assert "CORTEX System Optimization Report" in content
        assert "Overall Health:" in content
        assert "Health Score:" in content
        assert "Optimization Metrics" in content
        assert "Recommendations" in content
        assert "Next Actions" in content
    
    def test_phase_skipping(self, orchestrator):
        """Test skipping specific phases."""
        context = {
            'profile': 'focused',
            'mode': 'dry_run',
            'skip_phases': ['brain_tuning', 'entry_point_alignment']
        }
        
        result = orchestrator.execute(context)
        
        # Should complete successfully even with skipped phases
        assert result.success is True
    
    def test_execution_time_tracking(self, orchestrator):
        """Test execution time is tracked."""
        context = {
            'profile': 'minimal',
            'mode': 'dry_run',
            'skip_phases': ['design_sync', 'code_health', 'brain_tuning', 'entry_point_alignment', 'test_suite']
        }
        
        result = orchestrator.execute(context)
        
        assert orchestrator.metrics.execution_time_seconds > 0.0
    
    def test_formatted_header_in_result(self, orchestrator):
        """Test formatted header is included in result (SKULL-006 compliance)."""
        context = {
            'profile': 'minimal',
            'mode': 'dry_run',
            'skip_phases': ['design_sync', 'code_health', 'brain_tuning', 'entry_point_alignment', 'test_suite']
        }
        
        result = orchestrator.execute(context)
        
        assert result.formatted_header is not None
        assert "CORTEX System Optimization Orchestrator" in result.formatted_header
        assert "© 2024-2025 Asif Hussain" in result.formatted_header
    
    def test_formatted_footer_in_result(self, orchestrator):
        """Test formatted footer is included in result (SKULL-006 compliance)."""
        context = {
            'profile': 'minimal',
            'mode': 'dry_run',
            'skip_phases': ['design_sync', 'code_health', 'brain_tuning', 'entry_point_alignment', 'test_suite']
        }
        
        result = orchestrator.execute(context)
        
        assert result.formatted_footer is not None
        assert "System Optimization ✅ COMPLETED" in result.formatted_footer
        assert "Health Score:" in result.formatted_footer
    
    def test_error_handling(self, orchestrator, project_root):
        """Test error handling during execution."""
        # Remove required directory to trigger error
        import shutil
        shutil.rmtree(project_root / "cortex-brain")
        
        context = {'profile': 'comprehensive', 'mode': 'dry_run'}
        
        result = orchestrator.execute(context)
        
        # Should return failure result, not raise exception
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert len(result.errors) > 0


class TestOptimizationMetrics:
    """Test OptimizationMetrics dataclass."""
    
    def test_metrics_initialization(self):
        """Test metrics initialize with correct defaults."""
        metrics = OptimizationMetrics()
        
        assert metrics.design_drift_resolved == 0
        assert metrics.modules_synced == 0
        assert metrics.obsolete_tests_identified == 0
        assert metrics.tier_violations_fixed == 0
        assert metrics.final_pass_rate == 0.0
        assert metrics.skull_007_compliant is False
        assert metrics.total_improvements == 0
        assert isinstance(metrics.errors_encountered, list)
        assert isinstance(metrics.warnings, list)
    
    def test_metrics_modification(self):
        """Test metrics can be modified."""
        metrics = OptimizationMetrics()
        
        metrics.design_drift_resolved = 10
        metrics.tests_fixed = 5
        metrics.errors_encountered.append("Error 1")
        
        assert metrics.design_drift_resolved == 10
        assert metrics.tests_fixed == 5
        assert len(metrics.errors_encountered) == 1


class TestSystemHealthReport:
    """Test SystemHealthReport dataclass."""
    
    def test_report_initialization(self):
        """Test report initializes correctly."""
        metrics = OptimizationMetrics()
        report = SystemHealthReport(
            timestamp=datetime.now(),
            overall_health="good",
            health_score=85.0,
            metrics=metrics
        )
        
        assert report.overall_health == "good"
        assert report.health_score == 85.0
        assert isinstance(report.recommendations, list)
        assert isinstance(report.next_actions, list)
    
    def test_report_serialization(self):
        """Test report can be serialized to dict."""
        metrics = OptimizationMetrics()
        metrics.design_drift_resolved = 5
        
        report = SystemHealthReport(
            timestamp=datetime.now(),
            overall_health="excellent",
            health_score=95.0,
            metrics=metrics
        )
        
        report_dict = report.to_dict()
        
        assert isinstance(report_dict, dict)
        assert report_dict['overall_health'] == "excellent"
        assert report_dict['health_score'] == 95.0
        assert report_dict['metrics']['design_sync']['drift_resolved'] == 5
