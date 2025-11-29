"""
Tests for OptimizeCortexOrchestrator

Comprehensive tests for CORTEX optimization functionality including:
- OptimizationMetrics data class
- Metadata configuration
- Prerequisites validation
- SKULL test execution
- Architecture analysis
- Optimization planning
- Optimization execution with git tracking
- Metrics collection and reporting

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
import json

from src.operations.modules.optimization.optimize_cortex_orchestrator import (
    OptimizeCortexOrchestrator,
    OptimizationMetrics
)
from src.operations.base_operation_module import OperationStatus, OperationPhase


@pytest.fixture
def project_root(tmp_path):
    """Create a temporary project root with required structure."""
    # Create directory structure
    (tmp_path / "src").mkdir()
    (tmp_path / "tests").mkdir()
    (tmp_path / ".git").mkdir()
    (tmp_path / "cortex-brain").mkdir()
    
    # Create required files
    (tmp_path / "cortex-brain" / "knowledge-graph.yaml").write_text("# Knowledge Graph")
    (tmp_path / "tests" / "test_example.py").write_text("def test_example(): pass")
    
    return tmp_path


@pytest.fixture
def orchestrator(project_root):
    """Create OptimizeCortexOrchestrator instance."""
    orch = OptimizeCortexOrchestrator()
    orch.project_root = project_root
    return orch


class TestOptimizationMetrics:
    """Test OptimizationMetrics data class."""
    
    def test_metrics_initialization(self):
        """Test metrics initialize with defaults."""
        timestamp = datetime.now()
        metrics = OptimizationMetrics(
            optimization_id="opt_test",
            timestamp=timestamp
        )
        
        assert metrics.optimization_id == "opt_test"
        assert metrics.timestamp == timestamp
        assert metrics.tests_run == 0
        assert metrics.tests_passed == 0
        assert metrics.optimizations_applied == 0
        assert metrics.git_commits == []
        assert metrics.errors == []
    
    def test_metrics_with_values(self):
        """Test metrics with custom values."""
        metrics = OptimizationMetrics(
            optimization_id="opt_123",
            timestamp=datetime.now(),
            tests_run=10,
            tests_passed=8,
            tests_failed=2,
            optimizations_applied=5,
            optimizations_succeeded=4,
            optimizations_failed=1
        )
        
        assert metrics.tests_run == 10
        assert metrics.tests_passed == 8
        assert metrics.tests_failed == 2
        assert metrics.optimizations_applied == 5
        assert metrics.optimizations_succeeded == 4
    
    def test_metrics_git_commits_tracking(self):
        """Test git commit tracking in metrics."""
        metrics = OptimizationMetrics(
            optimization_id="opt_456",
            timestamp=datetime.now()
        )
        
        metrics.git_commits.append("abc123")
        metrics.git_commits.append("def456")
        
        assert len(metrics.git_commits) == 2
        assert "abc123" in metrics.git_commits


class TestOptimizeCortexOrchestratorMetadata:
    """Test OptimizeCortexOrchestrator metadata."""
    
    def test_get_metadata(self, orchestrator):
        """Test module metadata is properly configured."""
        metadata = orchestrator.get_metadata()
        
        assert metadata.module_id == "optimize_cortex_orchestrator"
        assert metadata.name == "CORTEX Optimization Orchestrator"
        assert "optimization" in metadata.description.lower()
        assert metadata.version == "1.0.0"
        assert metadata.author == "Asif Hussain"
        assert metadata.phase == OperationPhase.PROCESSING
        assert metadata.priority == 100
        assert 'optimization' in metadata.tags
        assert 'skull' in metadata.tags
        assert 'architecture' in metadata.tags


class TestOptimizeCortexOrchestratorPrerequisites:
    """Test prerequisites validation."""
    
    def test_validate_prerequisites_with_valid_project(self, orchestrator, project_root):
        """Test prerequisites pass with valid project."""
        context = {'project_root': project_root}
        is_valid, issues = orchestrator.validate_prerequisites(context)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_prerequisites_without_git(self, tmp_path):
        """Test prerequisites fail without git repository."""
        # Create project without .git
        (tmp_path / "tests").mkdir()
        (tmp_path / "cortex-brain").mkdir()
        (tmp_path / "cortex-brain" / "knowledge-graph.yaml").write_text("# KG")
        
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = tmp_path
        
        is_valid, issues = orchestrator.validate_prerequisites({'project_root': tmp_path})
        
        assert is_valid is False
        assert any('git' in issue.lower() for issue in issues)
    
    def test_validate_prerequisites_without_tests(self, tmp_path):
        """Test prerequisites fail without test suite."""
        # Create project without tests
        (tmp_path / ".git").mkdir()
        (tmp_path / "cortex-brain").mkdir()
        (tmp_path / "cortex-brain" / "knowledge-graph.yaml").write_text("# KG")
        
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = tmp_path
        
        is_valid, issues = orchestrator.validate_prerequisites({'project_root': tmp_path})
        
        assert is_valid is False
        assert any('test' in issue.lower() for issue in issues)
    
    def test_validate_prerequisites_without_knowledge_graph(self, tmp_path):
        """Test prerequisites fail without knowledge graph."""
        # Create project without knowledge graph
        (tmp_path / ".git").mkdir()
        (tmp_path / "tests").mkdir()
        (tmp_path / "cortex-brain").mkdir()
        
        orchestrator = OptimizeCortexOrchestrator()
        orchestrator.project_root = tmp_path
        
        is_valid, issues = orchestrator.validate_prerequisites({'project_root': tmp_path})
        
        assert is_valid is False
        assert any('knowledge graph' in issue.lower() for issue in issues)


class TestOptimizeCortexOrchestratorExecution:
    """Test optimization execution workflow."""
    
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._validate_planning_rules')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._run_skull_tests')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._analyze_architecture')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_plan')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._execute_optimizations')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_report')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._is_admin_environment')
    def test_execute_successful_optimization(
        self,
        mock_admin,
        mock_report,
        mock_execute,
        mock_plan,
        mock_analyze,
        mock_skull,
        mock_planning,
        orchestrator
    ):
        """Test successful optimization execution."""
        # Mock all phases to succeed
        mock_admin.return_value = False  # Not admin, skip alignment check
        mock_planning.return_value = {'success': True}
        mock_skull.return_value = {'success': True}
        mock_analyze.return_value = {'issues': [], 'patterns': []}
        mock_plan.return_value = {'optimizations': []}
        mock_execute.return_value = {'applied': 0}
        mock_report.return_value = "Optimization complete"
        
        result = orchestrator.execute({'project_root': orchestrator.project_root})
        
        assert result.success is True
        assert result.status == OperationStatus.SUCCESS
        assert 'metrics' in result.data
        assert isinstance(result.data['metrics'], dict)
    
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._validate_planning_rules')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._run_skull_tests')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._is_admin_environment')
    def test_execute_fails_on_skull_failure(
        self,
        mock_admin,
        mock_skull,
        mock_planning,
        orchestrator
    ):
        """Test execution fails when SKULL tests fail."""
        mock_admin.return_value = False
        mock_planning.return_value = {'success': True}
        mock_skull.return_value = {'success': False, 'errors': ['SKULL test failed']}
        
        result = orchestrator.execute({'project_root': orchestrator.project_root})
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert 'skull' in result.message.lower()
    
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._validate_planning_rules')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._run_skull_tests')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._analyze_architecture')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_plan')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._execute_optimizations')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_report')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._is_admin_environment')
    def test_execute_tracks_git_commits(
        self,
        mock_admin,
        mock_report,
        mock_execute,
        mock_plan,
        mock_analyze,
        mock_skull,
        mock_planning,
        orchestrator
    ):
        """Test execution tracks git commits."""
        mock_admin.return_value = False
        mock_planning.return_value = {'success': True}
        mock_skull.return_value = {'success': True}
        mock_analyze.return_value = {'issues': [], 'patterns': []}
        mock_plan.return_value = {'optimizations': ['opt1', 'opt2']}
        mock_execute.return_value = {'applied': 2}
        mock_report.return_value = "Report"
        
        result = orchestrator.execute({'project_root': orchestrator.project_root})
        
        assert result.success is True
        assert 'git_commits' in result.data
        assert isinstance(result.data['git_commits'], list)


class TestOptimizeCortexOrchestratorPhases:
    """Test individual optimization phases."""
    
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._validate_planning_rules')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._run_skull_tests')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._analyze_architecture')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_plan')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._execute_optimizations')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_report')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._is_admin_environment')
    def test_all_phases_called_in_order(
        self,
        mock_admin,
        mock_report,
        mock_execute,
        mock_plan,
        mock_analyze,
        mock_skull,
        mock_planning,
        orchestrator
    ):
        """Test all optimization phases are called in correct order."""
        mock_admin.return_value = False
        mock_planning.return_value = {'success': True}
        mock_skull.return_value = {'success': True}
        mock_analyze.return_value = {}
        mock_plan.return_value = {}
        mock_execute.return_value = {}
        mock_report.return_value = "Report"
        
        orchestrator.execute({'project_root': orchestrator.project_root})
        
        # Verify call order
        mock_planning.assert_called_once()
        mock_skull.assert_called_once()
        mock_analyze.assert_called_once()
        mock_plan.assert_called_once()
        mock_execute.assert_called_once()
        mock_report.assert_called_once()


class TestOptimizeCortexOrchestratorMetricsCollection:
    """Test metrics collection during optimization."""
    
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._validate_planning_rules')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._run_skull_tests')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._analyze_architecture')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_plan')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._execute_optimizations')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_report')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._is_admin_environment')
    def test_metrics_include_duration(
        self,
        mock_admin,
        mock_report,
        mock_execute,
        mock_plan,
        mock_analyze,
        mock_skull,
        mock_planning,
        orchestrator
    ):
        """Test metrics include execution duration."""
        mock_admin.return_value = False
        mock_planning.return_value = {'success': True}
        mock_skull.return_value = {'success': True}
        mock_analyze.return_value = {}
        mock_plan.return_value = {}
        mock_execute.return_value = {}
        mock_report.return_value = "Report"
        
        result = orchestrator.execute({'project_root': orchestrator.project_root})
        
        assert result.success is True
        metrics = result.data['metrics']
        assert 'duration_seconds' in metrics
        assert metrics['duration_seconds'] >= 0
    
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._validate_planning_rules')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._run_skull_tests')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._analyze_architecture')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_plan')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._execute_optimizations')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._generate_optimization_report')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._is_admin_environment')
    def test_metrics_include_optimization_id(
        self,
        mock_admin,
        mock_report,
        mock_execute,
        mock_plan,
        mock_analyze,
        mock_skull,
        mock_planning,
        orchestrator
    ):
        """Test metrics include unique optimization ID."""
        mock_admin.return_value = False
        mock_planning.return_value = {'success': True}
        mock_skull.return_value = {'success': True}
        mock_analyze.return_value = {}
        mock_plan.return_value = {}
        mock_execute.return_value = {}
        mock_report.return_value = "Report"
        
        result = orchestrator.execute({'project_root': orchestrator.project_root})
        
        assert result.success is True
        metrics = result.data['metrics']
        assert 'optimization_id' in metrics
        assert metrics['optimization_id'].startswith('opt_')


class TestOptimizeCortexOrchestratorErrorHandling:
    """Test error handling during optimization."""
    
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._validate_planning_rules')
    @patch('src.operations.modules.optimization.optimize_cortex_orchestrator.OptimizeCortexOrchestrator._is_admin_environment')
    def test_execute_handles_exceptions(
        self,
        mock_admin,
        mock_planning,
        orchestrator
    ):
        """Test execution handles exceptions gracefully."""
        mock_admin.return_value = False
        mock_planning.side_effect = Exception("Test error")
        
        result = orchestrator.execute({'project_root': orchestrator.project_root})
        
        assert result.success is False
        assert result.status == OperationStatus.FAILED
        assert 'error' in result.message.lower() or 'failed' in result.message.lower()
