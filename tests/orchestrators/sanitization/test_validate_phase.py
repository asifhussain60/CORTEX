"""
Test Suite: Validate Phase Integration
Phase: RED (Tests written first)
Coverage Target: 3 tests for BuildValidator integration

Tests build system detection, build execution, and test running.
BuildValidator workflow: detect_build_system() → execute_build() → run_tests()
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

try:
    from src.orchestrators.sanitization.sanitization_orchestrator import (
        SanitizationOrchestrator,
        SanitizationPhase,
    )
except ImportError:
    # Expected during RED phase
    SanitizationOrchestrator = None
    SanitizationPhase = None


class TestValidatePhase:
    """Test VALIDATE phase integration"""

    @pytest.mark.skipif(
        SanitizationOrchestrator is None,
        reason="Orchestrator not yet implemented (RED phase)"
    )
    def test_validation_success(self, tmp_path):
        """Test successful validation with build and tests passing"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        # Create test files
        (target_dir / "main.py").write_text("print('hello')")
        (target_dir / "test_main.py").write_text("def test_hello(): pass")
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Mock all phases to focus on validation
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': 'main.py'}], 'total_files': 1
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        orchestrator.mapper.generate_mappings = Mock(return_value={'Customer': 'Entity'})
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        orchestrator.transformer.transform_codebase = Mock(return_value={'files_transformed': 1})
        
        # Mock validation to succeed
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={
            'success': True, 
            'tests_passed': 5, 
            'tests_failed': 0
        })
        
        result = orchestrator.execute()
        
        # Verify validation succeeded
        assert result.success is True
        assert result.validation_passed is True
        assert orchestrator.validator.detect_build_system.called
        assert orchestrator.validator.execute_build.called
        assert orchestrator.validator.run_tests.called

    @pytest.mark.skipif(
        SanitizationOrchestrator is None,
        reason="Orchestrator not yet implemented (RED phase)"
    )
    def test_validation_failure(self, tmp_path):
        """Test validation failure when build or tests fail"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Mock all phases
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': 'main.py'}], 'total_files': 1
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        orchestrator.mapper.generate_mappings = Mock(return_value={'Customer': 'Entity'})
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        orchestrator.transformer.transform_codebase = Mock(return_value={'files_transformed': 1})
        
        # Mock validation to fail
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': False, 'error': 'Build failed'})
        
        result = orchestrator.execute()
        
        # Verify validation failed
        assert result.success is False
        assert result.validation_passed is False
        assert orchestrator.validator.detect_build_system.called
        assert orchestrator.validator.execute_build.called

    @pytest.mark.skipif(
        SanitizationOrchestrator is None,
        reason="Orchestrator not yet implemented (RED phase)"
    )
    def test_validation_with_test_results(self, tmp_path):
        """Test validation captures test execution details"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Mock all phases
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': 'main.py'}], 'total_files': 1
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        orchestrator.mapper.generate_mappings = Mock(return_value={'Customer': 'Entity'})
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        orchestrator.transformer.transform_codebase = Mock(return_value={'files_transformed': 1})
        
        # Mock validation with detailed test results
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={
            'success': True,
            'tests_passed': 42,
            'tests_failed': 0,
            'coverage': 85.7
        })
        
        result = orchestrator.execute()
        
        # Verify test results captured
        assert result.success is True
        assert result.validation_passed is True
        assert orchestrator.validator.run_tests.called
        
        # Verify test execution happened
        call_args = orchestrator.validator.run_tests.call_args
        assert call_args is not None  # Method was called


# Test markers for pytest
pytestmark = [
    pytest.mark.orchestrator_test,
    pytest.mark.cortex_v4,
]
