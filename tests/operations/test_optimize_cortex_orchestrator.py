"""
Tests for CORTEX Optimization Orchestrator

Tests cover:
- Prerequisites validation
- SKULL test execution
- Architecture analysis
- Optimization plan generation
- Optimization execution with git tracking
- Metrics collection

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.operations.modules.optimization import (
    OptimizeCortexOrchestrator,
    OptimizationMetrics
)
from src.operations.base_operation_module import OperationResult


@pytest.fixture
def project_root(tmp_path):
    """Create a mock CORTEX project structure."""
    # Create directories
    (tmp_path / '.git').mkdir()
    (tmp_path / 'tests' / 'tier0').mkdir(parents=True)
    (tmp_path / 'cortex-brain').mkdir()
    (tmp_path / 'src' / 'operations' / 'modules').mkdir(parents=True)
    
    # Create files
    (tmp_path / 'cortex-brain' / 'knowledge-graph.yaml').write_text('version: 1.0\n')
    (tmp_path / 'cortex-brain' / 'brain-protection-rules.yaml').write_text('version: 2.0\n')
    
    return tmp_path


@pytest.fixture
def orchestrator(project_root):
    """Create orchestrator instance."""
    return OptimizeCortexOrchestrator(project_root=project_root)


class TestOptimizeCortexOrchestrator:
    """Tests for optimization orchestrator."""
    
    def test_metadata(self, orchestrator):
        """Test module metadata."""
        metadata = orchestrator.metadata
        
        assert metadata.module_id == "optimize_cortex_orchestrator"
        assert "optimization" in metadata.name.lower()
        assert metadata.version == "1.0.0"
        assert not metadata.optional
    
    def test_validate_prerequisites_success(self, orchestrator, project_root):
        """Test prerequisites validation succeeds with valid setup."""
        is_valid, issues = orchestrator.validate_prerequisites({
            'project_root': project_root
        })
        
        assert is_valid
        assert len(issues) == 0
    
    def test_validate_prerequisites_missing_git(self, orchestrator, tmp_path):
        """Test prerequisites validation fails without git."""
        # No .git directory
        is_valid, issues = orchestrator.validate_prerequisites({
            'project_root': tmp_path
        })
        
        assert not is_valid
        assert any('git' in issue.lower() for issue in issues)
    
    def test_validate_prerequisites_missing_tests(self, orchestrator, tmp_path):
        """Test prerequisites validation fails without tests."""
        (tmp_path / '.git').mkdir()
        
        is_valid, issues = orchestrator.validate_prerequisites({
            'project_root': tmp_path
        })
        
        assert not is_valid
        assert any('test' in issue.lower() for issue in issues)
    
    def test_validate_prerequisites_missing_knowledge_graph(self, orchestrator, tmp_path):
        """Test prerequisites validation fails without knowledge graph."""
        (tmp_path / '.git').mkdir()
        (tmp_path / 'tests').mkdir()
        (tmp_path / 'cortex-brain').mkdir()
        
        is_valid, issues = orchestrator.validate_prerequisites({
            'project_root': tmp_path
        })
        
        assert not is_valid
        assert any('knowledge' in issue.lower() for issue in issues)


class TestSKULLTests:
    """Tests for SKULL test execution."""
    
    @patch('subprocess.run')
    def test_run_skull_tests_success(self, mock_run, orchestrator, project_root):
        """Test successful SKULL test execution."""
        # Mock pytest output
        mock_run.return_value = Mock(
            stdout="test_skull_001 PASSED\ntest_skull_002 PASSED\n20 tests PASSED",
            stderr="",
            returncode=0
        )
        
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        result = orchestrator._run_skull_tests(project_root, metrics)
        
        assert result['success']
        assert metrics.tests_run > 0
        assert metrics.tests_passed > 0
        assert metrics.tests_failed == 0
    
    @patch('subprocess.run')
    def test_run_skull_tests_failure(self, mock_run, orchestrator, project_root):
        """Test failed SKULL test execution."""
        # Mock pytest failure
        mock_run.return_value = Mock(
            stdout="test_skull_001 PASSED\ntest_skull_002 FAILED\n18 PASSED, 2 FAILED",
            stderr="",
            returncode=1
        )
        
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        result = orchestrator._run_skull_tests(project_root, metrics)
        
        assert not result['success']
        assert metrics.tests_failed > 0
        assert len(metrics.errors) > 0
    
    @patch('subprocess.run')
    def test_run_skull_tests_timeout(self, mock_run, orchestrator, project_root):
        """Test SKULL test timeout handling."""
        import subprocess
        mock_run.side_effect = subprocess.TimeoutExpired(cmd='pytest', timeout=120)
        
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        result = orchestrator._run_skull_tests(project_root, metrics)
        
        assert not result['success']
        assert 'timeout' in result['error'].lower()


class TestArchitectureAnalysis:
    """Tests for architecture analysis."""
    
    def test_analyze_knowledge_graph(self, orchestrator, project_root):
        """Test knowledge graph analysis."""
        # Create knowledge graph with patterns
        kg_content = """
validation_insights:
  pattern1:
    frequency: 5
  pattern2:
    frequency: 2
workflow_patterns:
  pattern3: {}
"""
        (project_root / 'cortex-brain' / 'knowledge-graph.yaml').write_text(kg_content)
        
        result = orchestrator._analyze_knowledge_graph(project_root)
        
        assert 'insights' in result
        assert len(result['insights']) > 0
        assert result['stats']['validation_insights'] == 2
        assert result['stats']['workflow_patterns'] == 1
    
    def test_analyze_operations(self, orchestrator, project_root):
        """Test operations analysis."""
        # Create operation modules
        ops_dir = project_root / 'src' / 'operations' / 'modules'
        (ops_dir / 'setup').mkdir(parents=True)
        (ops_dir / 'cleanup').mkdir(parents=True)
        (ops_dir / 'setup' / 'test.py').write_text('# test')
        
        result = orchestrator._analyze_operations(project_root)
        
        assert 'insights' in result
        assert 'stats' in result
        assert result['stats']['operation_categories'] >= 2
    
    def test_analyze_brain_protection(self, orchestrator, project_root):
        """Test brain protection analysis."""
        # Create brain protection rules
        rules_content = """
version: "2.0"
protection_layers:
  - layer_id: "layer1"
    rules:
      - rule_id: "SKULL_001"
      - rule_id: "RULE_002"
  - layer_id: "layer2"
    rules:
      - rule_id: "SKULL_003"
"""
        (project_root / 'cortex-brain' / 'brain-protection-rules.yaml').write_text(rules_content)
        
        result = orchestrator._analyze_brain_protection(project_root)
        
        assert 'insights' in result
        assert result['stats']['protection_layers'] == 2
        assert result['stats']['total_rules'] == 3
        assert result['stats']['skull_rules'] == 2


class TestOptimizationPlan:
    """Tests for optimization plan generation."""
    
    def test_generate_plan_with_issues(self, orchestrator):
        """Test plan generation with identified issues."""
        analysis = {
            'knowledge_graph': {
                'insights': ['High-frequency pattern: test_pattern (5 occurrences)'],
                'issues': ['Knowledge graph corrupted']
            },
            'operations': {
                'insights': [],
                'issues': ['Empty operation category: broken']
            }
        }
        
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        plan = orchestrator._generate_optimization_plan(analysis, metrics)
        
        assert 'critical' in plan
        assert 'high' in plan
        assert 'medium' in plan
        assert len(plan['critical']) > 0  # Corrupted knowledge graph
        assert len(plan['medium']) > 0  # Empty category
    
    def test_generate_plan_with_high_frequency_patterns(self, orchestrator):
        """Test plan identifies high-frequency patterns."""
        analysis = {
            'knowledge_graph': {
                'insights': [
                    'High-frequency pattern: powershell_regex (5 occurrences)',
                    'High-frequency pattern: wpf_tdd (4 occurrences)'
                ],
                'issues': []
            }
        }
        
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        plan = orchestrator._generate_optimization_plan(analysis, metrics)
        
        assert len(plan['high']) >= 2  # Two high-frequency patterns


class TestOptimizationExecution:
    """Tests for optimization execution."""
    
    @patch.object(OptimizeCortexOrchestrator, '_git_commit')
    @patch.object(OptimizeCortexOrchestrator, '_apply_optimization')
    def test_execute_optimizations(self, mock_apply, mock_commit, orchestrator, project_root):
        """Test optimization execution with git tracking."""
        mock_apply.return_value = True
        mock_commit.return_value = "abc123def"
        
        plan = {
            'critical': [
                {'action': 'Fix critical issue', 'category': 'test'}
            ],
            'high': [
                {'action': 'Optimize performance', 'category': 'test'}
            ],
            'medium': [],
            'low': []
        }
        
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        result = orchestrator._execute_optimizations(plan, project_root, metrics)
        
        assert len(result['applied']) == 2
        assert metrics.optimizations_succeeded == 2
        assert len(metrics.git_commits) == 2
    
    @patch.object(OptimizeCortexOrchestrator, '_git_commit')
    @patch.object(OptimizeCortexOrchestrator, '_apply_optimization')
    def test_execute_optimizations_with_failures(self, mock_apply, mock_commit, orchestrator, project_root):
        """Test optimization execution handles failures."""
        mock_apply.side_effect = [True, False]  # First succeeds, second fails
        mock_commit.return_value = "abc123"
        
        plan = {
            'critical': [
                {'action': 'Fix issue 1', 'category': 'test'},
                {'action': 'Fix issue 2', 'category': 'test'}
            ],
            'high': [],
            'medium': [],
            'low': []
        }
        
        metrics = OptimizationMetrics(
            optimization_id="test",
            timestamp=datetime.now()
        )
        
        result = orchestrator._execute_optimizations(plan, project_root, metrics)
        
        assert len(result['applied']) == 1
        assert len(result['failed']) == 1
        assert metrics.optimizations_succeeded == 1
        assert metrics.optimizations_failed == 1


class TestGitOperations:
    """Tests for git operations."""
    
    @patch('subprocess.run')
    def test_git_commit_success(self, mock_run, orchestrator, project_root):
        """Test successful git commit."""
        # Mock git status (has changes)
        mock_run.side_effect = [
            Mock(stdout="M  file.py\n", returncode=0),  # status
            Mock(returncode=0),  # add
            Mock(returncode=0),  # commit
            Mock(stdout="abc123def\n", returncode=0)  # rev-parse
        ]
        
        commit_hash = orchestrator._git_commit(
            project_root,
            "[OPTIMIZATION] Test commit"
        )
        
        assert commit_hash == "abc123def"
    
    @patch('subprocess.run')
    def test_git_commit_no_changes(self, mock_run, orchestrator, project_root):
        """Test git commit with no changes."""
        # Mock git status (no changes)
        mock_run.return_value = Mock(stdout="", returncode=0)
        
        commit_hash = orchestrator._git_commit(
            project_root,
            "[OPTIMIZATION] Test commit"
        )
        
        assert commit_hash is None


class TestIntegration:
    """Integration tests for full workflow."""
    
    @patch('subprocess.run')
    def test_full_optimization_workflow(self, mock_run, orchestrator, project_root):
        """Test complete optimization workflow."""
        # Mock SKULL tests success
        mock_run.return_value = Mock(
            stdout="20 tests PASSED",
            stderr="",
            returncode=0
        )
        
        # Create valid knowledge graph
        kg_content = """
validation_insights:
  skull_protection:
    frequency: 1
"""
        (project_root / 'cortex-brain' / 'knowledge-graph.yaml').write_text(kg_content)
        
        context = {'project_root': project_root}
        result = orchestrator.execute(context)
        
        assert result.success
        assert 'metrics' in result.data
        assert result.data['metrics']['tests_passed'] > 0


class TestMetrics:
    """Tests for metrics collection."""
    
    def test_optimization_metrics_initialization(self):
        """Test metrics initialization."""
        metrics = OptimizationMetrics(
            optimization_id="test_123",
            timestamp=datetime.now()
        )
        
        assert metrics.optimization_id == "test_123"
        assert metrics.tests_run == 0
        assert metrics.optimizations_applied == 0
        assert len(metrics.git_commits) == 0
        assert len(metrics.errors) == 0
    
    def test_generate_optimization_report(self, orchestrator):
        """Test report generation."""
        metrics = OptimizationMetrics(
            optimization_id="test_123",
            timestamp=datetime.now(),
            tests_run=25,
            tests_passed=24,
            tests_failed=1,
            issues_identified=5,
            optimizations_applied=3,
            optimizations_succeeded=2,
            git_commits=["abc123", "def456"],
            duration_seconds=45.5
        )
        
        report = orchestrator._generate_optimization_report(metrics)
        
        assert "test_123" in report
        assert "25" in report  # tests_run
        assert "24" in report  # tests_passed
        assert "abc123" in report  # commit hash
        assert "45.5" in report or "45.50" in report  # duration
