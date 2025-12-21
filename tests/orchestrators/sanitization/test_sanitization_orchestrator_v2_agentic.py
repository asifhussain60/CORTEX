"""
Tests for Sanitization Orchestrator v2.0 - Agentic Enhancement

Purpose: Comprehensive test coverage for agentic features
Version: 2.0.0
Author: CORTEX Development Team
Created: 2025-12-21

Test Coverage:
- Multi-agent parallel file analysis
- Learning engine pattern storage
- Context validation for transformations
- Mapping quality evaluation
- Error prevention metrics
- Integration with BaseOrchestrator
"""

import pytest
import asyncio
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any

from src.orchestrators.sanitization.sanitization_orchestrator_v2_migrated import (
    SanitizationOrchestratorV2,
    SanitizationPhase,
    SanitizationResult,
    MappingPattern,
    AnalysisTask
)


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create a temporary project directory for testing."""
    project = tmp_path / "test_project"
    project.mkdir()
    
    # Create some test files
    (project / "main.py").write_text("# Test file")
    (project / "utils.py").write_text("# Utility file")
    (project / "config.py").write_text("# Config file")
    
    return str(project)


@pytest.fixture
def mock_agentic_components():
    """Mock Phase 5 agentic components."""
    return {
        'multi_agent': Mock(),
        'learning_engine': Mock(),
        'context_validator': Mock(),
        'evaluator': Mock()
    }


@pytest.fixture
def orchestrator(temp_project_dir, mock_agentic_components):
    """Create orchestrator instance with mocked components."""
    with patch('src.orchestrators.sanitization.sanitization_orchestrator_v2_migrated.CodeAnalyzer'), \
         patch('src.orchestrators.sanitization.sanitization_orchestrator_v2_migrated.MappingEngine'), \
         patch('src.orchestrators.sanitization.sanitization_orchestrator_v2_migrated.CodeTransformer'), \
         patch('src.orchestrators.sanitization.sanitization_orchestrator_v2_migrated.BuildValidator'), \
         patch('src.orchestrators.sanitization.sanitization_orchestrator_v2_migrated.ReportGenerator'):
        
        orch = SanitizationOrchestratorV2(
            target_directory=temp_project_dir,
            dry_run=False
        )
        
        # Inject mocked agentic components
        orch.multi_agent = mock_agentic_components['multi_agent']
        orch.learning_engine = mock_agentic_components['learning_engine']
        orch.context_validator = mock_agentic_components['context_validator']
        orch.evaluator = mock_agentic_components['evaluator']
        
        return orch


class TestMultiAgentAnalysis:
    """Test multi-agent parallel file analysis."""
    
    def test_parallel_analysis_speedup(self, orchestrator):
        """Test that parallel analysis provides speedup."""
        # Mock file inventory
        orchestrator.analyzer.scan_file_structure.return_value = {
            'files': ['file1.py', 'file2.py', 'file3.py', 'file4.py', 'file5.py']
        }
        
        orchestrator.analyzer.extract_domain_terminology.return_value = {
            'CustomerOrder': 'Order',
            'PaymentProcessor': 'Processor'
        }
        
        orchestrator.analyzer.extract_namespaces.return_value = {
            'com.acme.orders': 'orders',
            'com.acme.payment': 'payment'
        }
        
        # Execute analysis phase
        result = orchestrator._execute_analyze_phase_agentic()
        
        # Verify success
        assert result['success'] is True
        assert len(result['files']) == 5
        
        # Verify speedup is calculated
        assert 'speedup' in result
        assert result['speedup'] >= 1.0
        
        # Verify terms extracted
        assert len(result['terms']) > 0
    
    @pytest.mark.asyncio
    async def test_parallel_file_analysis_execution(self, orchestrator):
        """Test parallel execution of file analysis tasks."""
        tasks = [
            AnalysisTask(
                task_id=f"task_{i}",
                file_path=Path(f"file{i}.py"),
                analysis_type='terminology',
                priority=1
            )
            for i in range(3)
        ]
        
        # Execute parallel analysis
        results = await orchestrator._parallel_file_analysis(tasks)
        
        # Verify all tasks completed
        assert len(results) == 3
        
        # Verify each result has expected structure
        for result in results:
            assert 'success' in result
            assert 'task_id' in result
    
    @pytest.mark.asyncio
    async def test_single_file_analysis(self, orchestrator):
        """Test single file analysis coroutine."""
        task = AnalysisTask(
            task_id="test_task",
            file_path=Path("test.py"),
            analysis_type='terminology',
            priority=1
        )
        
        result = await orchestrator._analyze_single_file(task)
        
        # Verify result structure
        assert result['success'] is True
        assert result['task_id'] == "test_task"
        assert result['file'] == "test.py"
        assert 'terms' in result
        assert 'namespaces' in result


class TestLearningEngine:
    """Test agent learning engine integration."""
    
    def test_enhance_with_learned_patterns(self, orchestrator):
        """Test mapping enhancement with learned patterns."""
        # Add learned patterns
        orchestrator.learned_patterns = {
            'CustomerOrder': MappingPattern(
                domain_term='CustomerOrder',
                generic_term='Order',
                context='sanitization',
                quality_score=0.9,
                usage_count=5
            )
        }
        
        # Initial mappings
        mappings = {
            'CustomerOrder': 'CustomerData',  # Suboptimal mapping
            'PaymentProcessor': 'Processor'
        }
        
        # Enhance with learned patterns
        enhanced = orchestrator._enhance_with_learned_patterns(mappings)
        
        # Verify learned pattern applied
        assert enhanced['CustomerOrder'] == 'Order'  # Learned pattern used
        assert enhanced['PaymentProcessor'] == 'Processor'  # Unchanged
    
    def test_learn_from_mappings(self, orchestrator):
        """Test learning from successful mappings."""
        mappings = {
            'ShoppingCart': 'Cart',
            'PaymentGateway': 'Gateway'
        }
        
        quality_score = 0.85
        
        # Learn from mappings
        patterns_learned = orchestrator._learn_from_mappings(mappings, quality_score)
        
        # Verify patterns stored
        assert patterns_learned == 2
        assert 'ShoppingCart' in orchestrator.learned_patterns
        assert 'PaymentGateway' in orchestrator.learned_patterns
        
        # Verify pattern properties
        pattern = orchestrator.learned_patterns['ShoppingCart']
        assert pattern.generic_term == 'Cart'
        assert pattern.quality_score == quality_score
        assert pattern.usage_count == 1
    
    def test_update_existing_pattern(self, orchestrator):
        """Test updating existing learned pattern."""
        # Add initial pattern
        orchestrator.learned_patterns['Product'] = MappingPattern(
            domain_term='Product',
            generic_term='Item',
            context='sanitization',
            quality_score=0.8,
            usage_count=3
        )
        
        # Learn from new mapping
        mappings = {'Product': 'Item'}
        new_quality = 0.9
        
        patterns_learned = orchestrator._learn_from_mappings(mappings, new_quality)
        
        # Verify pattern updated (not created)
        assert patterns_learned == 0
        assert orchestrator.learned_patterns['Product'].usage_count == 4
        
        # Verify quality score updated (average)
        pattern = orchestrator.learned_patterns['Product']
        expected_quality = (0.8 * 3 + 0.9) / 4
        assert abs(pattern.quality_score - expected_quality) < 0.01


class TestMappingQualityEvaluation:
    """Test mapping quality evaluation with AgentEvaluator."""
    
    def test_evaluate_mapping_quality(self, orchestrator):
        """Test mapping quality evaluation."""
        mappings = {
            'CustomerOrder': 'Order',
            'PaymentProcessor': 'Processor'
        }
        
        # Mock evaluator response
        orchestrator.evaluator.evaluate.return_value = {
            'clarity': 0.9,
            'consistency': 0.85,
            'genericness': 0.95,
            'maintainability': 0.8
        }
        
        # Evaluate quality
        metrics = orchestrator._evaluate_mapping_quality(mappings)
        
        # Verify overall score calculated
        assert 'overall_score' in metrics
        assert 0.0 <= metrics['overall_score'] <= 1.0
        
        # Verify individual criteria
        assert metrics['clarity'] == 0.9
        assert metrics['consistency'] == 0.85
        assert metrics['genericness'] == 0.95
        assert metrics['maintainability'] == 0.8
        
        # Verify evaluator called
        orchestrator.evaluator.evaluate.assert_called_once()
    
    def test_quality_evaluation_fallback(self, orchestrator):
        """Test fallback when evaluator fails."""
        mappings = {'Test': 'GenericTest'}
        
        # Mock evaluator to raise exception
        orchestrator.evaluator.evaluate.side_effect = Exception("Evaluator error")
        
        # Evaluate quality (should fallback to heuristic)
        metrics = orchestrator._evaluate_mapping_quality(mappings)
        
        # Verify fallback scores used
        assert metrics['overall_score'] == 0.7
        assert all(score == 0.7 for score in [
            metrics['clarity'],
            metrics['consistency'],
            metrics['genericness'],
            metrics['maintainability']
        ])


class TestContextValidation:
    """Test context validation for transformations."""
    
    def test_transform_with_context_validation(self, orchestrator):
        """Test transformation with pre-validation."""
        mappings = {
            'CustomerOrder': 'Order',
            'PaymentProcessor': 'Processor'
        }
        
        # Mock successful validation
        orchestrator.context_validator.validate.return_value = Mock(
            quality='HIGH',
            issues=[]
        )
        
        # Mock transformer
        orchestrator.transformer.transform_codebase.return_value = {
            'files_transformed': 5,
            'success': True
        }
        
        # Execute transform phase
        result = orchestrator._execute_transform_phase_agentic({
            'mappings': mappings
        })
        
        # Verify success
        assert result['success'] is True
        assert result['files_transformed'] == 5
        assert result['prevented_errors'] == 0
        
        # Verify validator called
        orchestrator.context_validator.validate.assert_called_once()
    
    def test_transform_with_validation_errors(self, orchestrator):
        """Test transformation when validation detects errors."""
        from src.orchestration_4_0.frameworks.context_validator import ContextQuality
        
        mappings = {
            'CustomerOrder': 'Order',
            'BadMapping': 'Invalid!Name'  # Invalid identifier
        }
        
        # Mock validation with errors
        orchestrator.context_validator.validate.return_value = Mock(
            quality=ContextQuality.LOW,
            issues=['Invalid identifier: Invalid!Name']
        )
        
        # Mock transformer
        orchestrator.transformer.transform_codebase.return_value = {
            'files_transformed': 5,
            'success': True
        }
        
        # Execute transform phase
        result = orchestrator._execute_transform_phase_agentic({
            'mappings': mappings
        })
        
        # Verify errors prevented
        assert result['success'] is True
        assert result['prevented_errors'] == 1
        assert len(result['validation_warnings']) == 1
    
    def test_filter_problematic_mappings(self, orchestrator):
        """Test filtering of problematic mappings."""
        mappings = {
            'GoodMapping': 'Valid',
            'BadMapping': 'Invalid',
            'AnotherGood': 'AlsoValid'
        }
        
        validation_errors = [
            "Invalid identifier: Invalid in BadMapping"
        ]
        
        # Filter mappings
        filtered = orchestrator._filter_problematic_mappings(
            mappings,
            validation_errors
        )
        
        # Verify problematic mapping removed
        assert 'GoodMapping' in filtered
        assert 'AnotherGood' in filtered
        assert 'BadMapping' not in filtered


class TestEndToEndWorkflow:
    """Test complete workflow with agentic enhancements."""
    
    def test_successful_sanitization_workflow(self, orchestrator):
        """Test complete successful sanitization."""
        # Mock all phases
        orchestrator.analyzer.scan_file_structure.return_value = {
            'files': ['file1.py', 'file2.py']
        }
        
        orchestrator.analyzer.extract_domain_terminology.return_value = {
            'CustomerOrder': 'Order'
        }
        
        orchestrator.analyzer.extract_namespaces.return_value = {}
        
        orchestrator.mapper.generate_mappings.return_value = {
            'CustomerOrder': 'Order'
        }
        
        orchestrator.mapper.detect_conflicts.return_value = []
        
        orchestrator.evaluator.evaluate.return_value = {
            'clarity': 0.9,
            'consistency': 0.9,
            'genericness': 0.9,
            'maintainability': 0.9
        }
        
        orchestrator.context_validator.validate.return_value = Mock(
            quality='HIGH',
            issues=[]
        )
        
        orchestrator.transformer.transform_codebase.return_value = {
            'files_transformed': 2,
            'success': True
        }
        
        orchestrator.validator.detect_build_system.return_value = 'none'
        
        orchestrator.reporter.generate_audit_report.return_value = '/tmp/report.md'
        
        # Execute workflow
        result = orchestrator.execute()
        
        # Verify success
        assert result.success is True
        assert result.phase == SanitizationPhase.REPORT
        assert result.files_analyzed == 2
        assert result.mappings_created == 1
        
        # Verify agentic metrics
        assert 'parallel_speedup' in result.agentic_metrics
        assert 'mapping_quality' in result.agentic_metrics
        assert 'learned_patterns' in result.agentic_metrics
    
    def test_dry_run_workflow(self, orchestrator):
        """Test dry-run mode (no transformations)."""
        orchestrator.dry_run = True
        
        # Mock analysis and mapping phases only
        orchestrator.analyzer.scan_file_structure.return_value = {
            'files': ['file1.py']
        }
        
        orchestrator.analyzer.extract_domain_terminology.return_value = {}
        orchestrator.analyzer.extract_namespaces.return_value = {}
        orchestrator.mapper.generate_mappings.return_value = {}
        orchestrator.mapper.detect_conflicts.return_value = []
        orchestrator.reporter.generate_audit_report.return_value = '/tmp/report.md'
        
        # Execute workflow
        result = orchestrator.execute()
        
        # Verify dry-run behavior
        assert result.success is True
        assert result.files_transformed == 0
        assert result.validation_passed is True
        assert result.agentic_metrics.get('dry_run') is True


class TestAgenticMetrics:
    """Test agentic metrics collection."""
    
    def test_agentic_metrics_structure(self, orchestrator):
        """Test that all agentic metrics are collected."""
        # Mock minimal workflow
        orchestrator.analyzer.scan_file_structure.return_value = {'files': []}
        orchestrator.analyzer.extract_domain_terminology.return_value = {}
        orchestrator.analyzer.extract_namespaces.return_value = {}
        orchestrator.mapper.generate_mappings.return_value = {}
        orchestrator.mapper.detect_conflicts.return_value = []
        orchestrator.reporter.generate_audit_report.return_value = '/tmp/report.md'
        
        # Execute
        result = orchestrator.execute()
        
        # Verify agentic metrics present
        assert 'parallel_speedup' in result.agentic_metrics
        assert 'mapping_quality' in result.agentic_metrics
        assert 'learned_patterns' in result.agentic_metrics
        assert 'duration_seconds' in result.agentic_metrics
    
    def test_metrics_on_failure(self, orchestrator):
        """Test that metrics are preserved on failure."""
        # Mock analysis to fail
        orchestrator.analyzer.scan_file_structure.side_effect = Exception("Analysis failed")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify failure with metrics
        assert result.success is False
        assert 'duration_seconds' in result.agentic_metrics
        assert len(result.errors) > 0


class TestBaseOrchestratorIntegration:
    """Test integration with BaseOrchestrator."""
    
    def test_inherits_base_orchestrator(self):
        """Test that orchestrator inherits from BaseOrchestrator."""
        from src.orchestrators.base.base_orchestrator import BaseOrchestrator
        
        assert issubclass(SanitizationOrchestratorV2, BaseOrchestrator)
    
    def test_configuration_injection(self, orchestrator):
        """Test that configuration is properly injected."""
        # Verify config attributes from BaseOrchestrator
        assert hasattr(orchestrator, 'logger')
        assert orchestrator.logger is not None
    
    def test_engagement_hints(self, orchestrator, caplog):
        """Test that engagement hints are logged."""
        import logging
        
        with caplog.at_level(logging.INFO):
            # Trigger initialization logging
            SanitizationOrchestratorV2(
                target_directory=str(orchestrator.target),
                dry_run=False
            )
        
        # Verify engagement hints in logs
        log_messages = [record.message for record in caplog.records]
        engagement_logs = [msg for msg in log_messages if '🎭' in msg]
        
        assert len(engagement_logs) > 0
        assert any('Orchestrator engaged' in msg for msg in engagement_logs)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
