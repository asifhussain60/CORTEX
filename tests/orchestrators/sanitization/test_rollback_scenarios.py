"""
Rollback Scenarios Test Suite - Sanitization Orchestrator

Tests rollback mechanisms, failure recovery, and error handling for the
sanitization orchestrator. Validates that validation failures are properly
detected and reported (rollback mechanism foundation).

Test Categories:
    - Validation failure detection
    - Build failure handling
    - Test failure handling
    - Partial transformation handling
    - Error recovery mechanisms
    - State consistency on failure

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import Mock
from src.orchestrators.sanitization.sanitization_orchestrator import (
    SanitizationOrchestrator,
    SanitizationPhase,
    SanitizationResult
)


# ========== Fixtures ==========

@pytest.fixture
def temp_project(tmp_path):
    """Create temporary project with sample files"""
    project_dir = tmp_path / "test-project"
    project_dir.mkdir()
    
    # Create source files
    src_dir = project_dir / "src"
    src_dir.mkdir()
    
    (src_dir / "main.py").write_text("""
def acme_process_data():
    return "Processing ACME data"
""")
    
    (src_dir / "utils.py").write_text("""
class AcmeHelper:
    def get_acme_config():
        return {"acme": "config"}
""")
    
    return project_dir


# ========== Mock Helpers ==========

def mock_analyzer_success(orchestrator, files_count=2, terms_count=3):
    """Helper to mock successful analyzer methods"""
    orchestrator.analyzer.scan_file_structure = Mock(return_value={
        'files': [{'path': f'file{i}.py', 'language': 'python'} for i in range(files_count)],
        'total_files': files_count
    })
    orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
        f'Term{i}': i for i in range(terms_count)
    })
    orchestrator.analyzer.extract_namespaces = Mock(return_value={})


def mock_mapper_success(orchestrator, mappings_count=3):
    """Helper to mock successful mapper methods"""
    orchestrator.mapper.generate_mappings = Mock(return_value={
        f'Term{i}': f'Generic{i}' for i in range(mappings_count)
    })
    orchestrator.mapper.detect_conflicts = Mock(return_value=[])


def mock_transformer_success(orchestrator, files_transformed=2):
    """Helper to mock successful transformer methods"""
    orchestrator.transformer.transform_codebase = Mock(return_value={
        'files_transformed': files_transformed,
        'success': True
    })


def mock_validator_build_failure(orchestrator):
    """Helper to mock validator with build failure"""
    orchestrator.validator.detect_build_system = Mock(return_value='pytest')
    orchestrator.validator.execute_build = Mock(return_value={
        'success': False,
        'errors': ['Build failed: ImportError in module X']
    })


def mock_validator_test_failure(orchestrator):
    """Helper to mock validator with test failures"""
    orchestrator.validator.detect_build_system = Mock(return_value='pytest')
    orchestrator.validator.execute_build = Mock(return_value={'success': True})
    orchestrator.validator.run_tests = Mock(return_value={
        'success': False,
        'failures': 3,
        'errors': ['test_feature_x failed', 'test_feature_y failed']
    })


def mock_reporter_success(orchestrator, report_path):
    """Helper to mock successful reporter methods"""
    orchestrator.reporter.generate_audit_report = Mock(return_value=report_path)


# ========== Validation Failure Tests ==========

def test_build_failure_detected(temp_project, caplog):
    """Test that build failures are detected during validation phase"""
    caplog.set_level(logging.INFO)
    
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock components for success up to validation, then failure
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_transformer_success(orchestrator, files_transformed=2)
    mock_validator_build_failure(orchestrator)
    mock_reporter_success(orchestrator, temp_project / "report.md")
    
    result = orchestrator.execute()
    
    # Build failure should be caught
    assert result.success is False
    assert result.validation_passed is False
    assert any('Build failed' in record.message for record in caplog.records)


def test_test_failure_detected(temp_project, caplog):
    """Test that test failures are detected during validation phase"""
    caplog.set_level(logging.INFO)
    
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock components for success up to test execution, then failure
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_transformer_success(orchestrator, files_transformed=2)
    mock_validator_test_failure(orchestrator)
    mock_reporter_success(orchestrator, temp_project / "report.md")
    
    result = orchestrator.execute()
    
    # Test failures should result in failed validation
    assert result.validation_passed is False


def test_validation_failure_stops_workflow(temp_project):
    """Test that validation failure is properly reported"""
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock all components
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_transformer_success(orchestrator, files_transformed=2)
    mock_validator_build_failure(orchestrator)
    mock_reporter_success(orchestrator, temp_project / "report.md")
    
    result = orchestrator.execute()
    
    # Validation failed - this is what matters
    assert result.success is False
    assert result.validation_passed is False


# ========== Error Recovery Tests ==========

def test_analyzer_exception_handling(temp_project, caplog):
    """Test that analyzer exceptions are caught and logged"""
    caplog.set_level(logging.ERROR)
    
    orchestrator = SanitizationOrchestrator(temp_project)
    orchestrator.analyzer.scan_file_structure = Mock(side_effect=Exception("Analyzer crash"))
    
    result = orchestrator.execute()
    
    assert result.success is False
    assert any('Analyzer crash' in record.message for record in caplog.records)


def test_mapper_exception_handling(temp_project, caplog):
    """Test that mapper exceptions are caught and logged"""
    caplog.set_level(logging.ERROR)
    
    orchestrator = SanitizationOrchestrator(temp_project)
    
    # Mock analyzer success, but mapper failure
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    orchestrator.mapper.generate_mappings = Mock(side_effect=Exception("Mapping crash"))
    
    result = orchestrator.execute()
    
    assert result.success is False
    assert any('Mapping crash' in record.message for record in caplog.records)


def test_transformer_exception_handling(temp_project, caplog):
    """Test that transformer exceptions are caught and logged"""
    caplog.set_level(logging.ERROR)
    
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock analyzer and mapper success, but transformer failure
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    orchestrator.transformer.transform_codebase = Mock(side_effect=Exception("Transform crash"))
    
    result = orchestrator.execute()
    
    assert result.success is False
    assert any('Transform crash' in record.message for record in caplog.records)


def test_validator_exception_handling(temp_project, caplog):
    """Test that validator exceptions are caught and logged"""
    caplog.set_level(logging.ERROR)
    
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock success up to validation, then validator crashes
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_transformer_success(orchestrator, files_transformed=2)
    orchestrator.validator.detect_build_system = Mock(side_effect=Exception("Validator crash"))
    
    result = orchestrator.execute()
    
    assert result.success is False
    assert any('Validator crash' in record.message for record in caplog.records)


# ========== State Consistency Tests ==========

def test_result_object_on_build_failure(temp_project):
    """Test that result object has consistent state after build failure"""
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock all components
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_transformer_success(orchestrator, files_transformed=2)
    mock_validator_build_failure(orchestrator)
    mock_reporter_success(orchestrator, temp_project / "report.md")
    
    result = orchestrator.execute()
    
    # Verify result state consistency
    assert isinstance(result, SanitizationResult)
    assert result.success is False
    assert result.validation_passed is False
    assert result.files_analyzed == 2
    assert result.mappings_created > 0
    assert result.files_transformed == 2
    assert result.report_path is not None


def test_result_object_on_test_failure(temp_project):
    """Test that result object has consistent state after test failure"""
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock all components
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_transformer_success(orchestrator, files_transformed=2)
    mock_validator_test_failure(orchestrator)
    mock_reporter_success(orchestrator, temp_project / "report.md")
    
    result = orchestrator.execute()
    
    # Verify result state consistency
    assert isinstance(result, SanitizationResult)
    assert result.validation_passed is False
    assert result.files_analyzed > 0
    assert result.files_transformed > 0


def test_metrics_accurate_on_failure(temp_project):
    """Test that metrics are accurate even when validation fails"""
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=False)
    
    # Mock all components
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_transformer_success(orchestrator, files_transformed=2)
    mock_validator_build_failure(orchestrator)
    mock_reporter_success(orchestrator, temp_project / "report.md")
    
    result = orchestrator.execute()
    
    # Metrics should still be accurate up to the failure point
    assert result.files_analyzed == 2
    assert result.mappings_created == 3
    assert result.files_transformed == 2
    assert result.duration_seconds > 0


# ========== Partial Transformation Tests ==========

def test_no_files_to_transform(temp_project):
    """Test handling when analyzer finds no files to transform"""
    orchestrator = SanitizationOrchestrator(temp_project)
    
    # Mock analyzer returning empty results
    orchestrator.analyzer.scan_file_structure = Mock(return_value={
        'files': [],
        'total_files': 0
    })
    orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
    orchestrator.analyzer.extract_namespaces = Mock(return_value={})
    
    result = orchestrator.execute()
    
    assert result.success is True
    assert result.files_analyzed == 0
    assert result.files_transformed == 0


def test_empty_mappings_handling(temp_project):
    """Test handling when mapper generates no mappings"""
    orchestrator = SanitizationOrchestrator(temp_project)
    
    # Mock analyzer success but empty mappings
    mock_analyzer_success(orchestrator, files_count=2, terms_count=0)
    orchestrator.mapper.generate_mappings = Mock(return_value={})
    orchestrator.mapper.detect_conflicts = Mock(return_value=[])
    
    result = orchestrator.execute()
    
    assert result.success is True
    assert result.mappings_created == 0


# ========== Dry-Run Failure Tests ==========

def test_dry_run_handles_validation_failures_gracefully(temp_project):
    """Test that dry-run mode doesn't run validation that would fail"""
    orchestrator = SanitizationOrchestrator(temp_project, dry_run=True)
    
    # Mock all components - validator would fail, but shouldn't be called in dry-run
    mock_analyzer_success(orchestrator, files_count=2, terms_count=3)
    mock_mapper_success(orchestrator, mappings_count=3)
    mock_validator_build_failure(orchestrator)  # Would fail, but not called
    mock_reporter_success(orchestrator, temp_project / "report.md")
    
    result = orchestrator.execute()
    
    # Dry-run should succeed even though validator would fail
    assert result.success is True
    assert result.validation_passed is True  # No validation run in dry-run
    assert result.files_transformed == 0  # No transformation in dry-run
    
    # Validator should not have been called
    orchestrator.validator.detect_build_system.assert_not_called()
    orchestrator.validator.execute_build.assert_not_called()
