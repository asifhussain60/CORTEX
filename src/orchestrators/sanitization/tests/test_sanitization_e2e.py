"""
Test Suite: End-to-End Sanitization Workflow
Phase: Integration Testing
Coverage Target: 10+ tests for full workflow scenarios

Tests complete sanitization workflow with proper mocking of utility methods.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.sanitization.sanitization_orchestrator import (
    SanitizationOrchestrator,
    SanitizationPhase,
    SanitizationResult,
)


@pytest.fixture
def temp_project():
    """Create temporary project structure for sanitization"""
    tmpdir = Path(tempfile.mkdtemp())
    
    # Create sample Python project
    src_dir = tmpdir / "src"
    src_dir.mkdir()
    
    (src_dir / "acme_module.py").write_text("""
class AcmeService:
    def process_acme_order(self, order_id):
        return self.acme_api.fetch_order(order_id)
""")
    
    yield tmpdir
    shutil.rmtree(tmpdir)


def mock_analyzer_success(orchestrator, files_count=2, terms_count=2):
    """Helper to mock successful analyzer methods"""
    orchestrator.analyzer.scan_file_structure = Mock(return_value={
        'files': [{'path': f'file{i}.py', 'language': 'python'} for i in range(files_count)],
        'total_files': files_count
    })
    orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
        f'Term{i}': i+1 for i in range(terms_count)
    })
    orchestrator.analyzer.extract_namespaces = Mock(return_value={})


def mock_mapper_success(orchestrator, mappings_count=2):
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


def mock_validator_success(orchestrator):
    """Helper to mock successful validator methods"""
    orchestrator.validator.detect_build_system = Mock(return_value='python')
    orchestrator.validator.execute_build = Mock(return_value={'success': True})
    orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})


def mock_reporter_success(orchestrator, report_path):
    """Helper to mock successful reporter methods"""
    orchestrator.reporter.generate_audit_report = Mock(return_value=report_path)


class TestE2ESanitization:
    """Test end-to-end sanitization workflows"""
    
    def test_complete_workflow_success(self, temp_project):
        """Test successful execution of all 5 phases"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock all utilities for success
        mock_analyzer_success(orchestrator, files_count=2, terms_count=2)
        mock_mapper_success(orchestrator, mappings_count=2)
        mock_transformer_success(orchestrator, files_transformed=2)
        mock_validator_success(orchestrator)
        mock_reporter_success(orchestrator, temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify
        assert result.success is True
        assert result.phase == SanitizationPhase.REPORT
        assert result.files_analyzed == 2
        assert result.mappings_created == 2
        assert result.files_transformed == 2
        assert result.validation_passed is True
        assert result.duration_seconds > 0
        assert len(result.errors) == 0
    
    def test_workflow_with_zero_files(self, temp_project):
        """Test handling of empty project"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock empty scan
        mock_analyzer_success(orchestrator, files_count=0, terms_count=0)
        mock_mapper_success(orchestrator, mappings_count=0)
        mock_transformer_success(orchestrator, files_transformed=0)
        mock_validator_success(orchestrator)
        mock_reporter_success(orchestrator, temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify zero metrics
        assert result.files_analyzed == 0
        assert result.mappings_created == 0
        assert result.files_transformed == 0
    
    def test_dry_run_mode_skips_transformation(self, temp_project):
        """Test that dry-run mode skips TRANSFORM and VALIDATE phases"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=True  # DRY RUN MODE
        )
        
        # Mock analysis and mapping only
        mock_analyzer_success(orchestrator, files_count=5, terms_count=3)
        mock_mapper_success(orchestrator, mappings_count=3)
        mock_reporter_success(orchestrator, temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify transformation skipped
        assert result.success is True
        assert result.files_analyzed == 5
        assert result.mappings_created == 3
        assert result.files_transformed == 0  # Should be 0 in dry-run
        assert result.validation_passed is True  # Always true in dry-run
    
    def test_workflow_analyzer_failure_stops_execution(self, temp_project):
        """Test that analyzer failure prevents later phases"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock analyzer failure - orchestrator catches exceptions
        orchestrator.analyzer.scan_file_structure = Mock(side_effect=Exception("Scan failed"))
        
        # Execute
        result = orchestrator.execute()
        
        # Verify stopped at ANALYZE
        assert result.success is False
        assert result.phase == SanitizationPhase.ANALYZE
        assert len(result.errors) > 0
    
    def test_workflow_metrics_accumulation(self, temp_project):
        """Test that metrics are accumulated correctly"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock with specific counts
        mock_analyzer_success(orchestrator, files_count=10, terms_count=7)
        mock_mapper_success(orchestrator, mappings_count=7)
        mock_transformer_success(orchestrator, files_transformed=8)
        mock_validator_success(orchestrator)
        mock_reporter_success(orchestrator, temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify exact metrics
        assert result.files_analyzed == 10
        assert result.mappings_created == 7
        assert result.files_transformed == 8
    
    def test_workflow_engagement_hints_logged(self, temp_project, caplog):
        """Test that 🎭 engagement hints appear in logs"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock success path
        mock_analyzer_success(orchestrator)
        mock_mapper_success(orchestrator)
        mock_transformer_success(orchestrator)
        mock_validator_success(orchestrator)
        mock_reporter_success(orchestrator, temp_project / "report.md")
        
        # Execute with log capturing
        with caplog.at_level('INFO'):
            result = orchestrator.execute()
        
        # Verify engagement hints
        log_text = caplog.text
        assert '🎭 Orchestrator engaged' in log_text
        assert '🎭 Phase transition' in log_text
        assert '🎭 Orchestrator completing' in log_text
    
    def test_workflow_duration_tracking(self, temp_project):
        """Test that execution duration is measured"""
        import time
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock with delay
        def slow_scan(*args, **kwargs):
            time.sleep(0.05)
            return {'files': [{'path': 'file.py'}], 'total_files': 1}
        
        orchestrator.analyzer.scan_file_structure = Mock(side_effect=slow_scan)
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={'Term': 1})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        mock_mapper_success(orchestrator, mappings_count=1)
        mock_transformer_success(orchestrator, files_transformed=1)
        mock_validator_success(orchestrator)
        mock_reporter_success(orchestrator, temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify duration
        assert result.duration_seconds >= 0.05
        assert result.duration_seconds < 10
    
    def test_workflow_validation_failure_stops_at_validate(self, temp_project):
        """Test that validation failure is reported correctly"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock success until validation
        mock_analyzer_success(orchestrator)
        mock_mapper_success(orchestrator)
        mock_transformer_success(orchestrator)
        
        # Mock validation failure
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={
            'success': False,
            'errors': ['Build failed: syntax error']
        })
        
        # Execute
        result = orchestrator.execute()
        
        # Verify stopped at VALIDATE
        assert result.success is False
        assert result.phase == SanitizationPhase.VALIDATE
        assert result.validation_passed is False
    
    def test_workflow_empty_mappings_still_succeeds(self, temp_project):
        """Test that workflow succeeds even with no mappings"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock with no terms/mappings
        mock_analyzer_success(orchestrator, files_count=3, terms_count=0)
        mock_mapper_success(orchestrator, mappings_count=0)
        mock_transformer_success(orchestrator, files_transformed=0)
        mock_validator_success(orchestrator)
        mock_reporter_success(orchestrator, temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify success with zero mappings
        assert result.success is True
        assert result.files_analyzed == 3
        assert result.mappings_created == 0
        assert result.files_transformed == 0
    
    def test_workflow_phase_order_enforcement(self, temp_project):
        """Test that phases execute in correct order"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        execution_order = []
        
        orchestrator.analyzer.scan_file_structure = Mock(side_effect=lambda: (
            execution_order.append('ANALYZE_scan'),
            {'files': [{'path': 'f.py'}], 'total_files': 1}
        )[1])
        
        orchestrator.analyzer.extract_domain_terminology = Mock(side_effect=lambda: (
            execution_order.append('ANALYZE_extract'),
            {'Term': 1}
        )[1])
        
        orchestrator.analyzer.extract_namespaces = Mock(side_effect=lambda: (
            execution_order.append('ANALYZE_namespaces'),
            {}
        )[1])
        
        orchestrator.mapper.generate_mappings = Mock(side_effect=lambda t, n: (
            execution_order.append('MAPPING'),
            {'Term': 'Generic'}
        )[1])
        
        orchestrator.mapper.detect_conflicts = Mock(side_effect=lambda m: (
            execution_order.append('MAPPING_conflicts'),
            []
        )[1])
        
        orchestrator.transformer.transform_codebase = Mock(side_effect=lambda s, d, m: (
            execution_order.append('TRANSFORM'),
            {'files_transformed': 1, 'success': True}
        )[1])
        
        orchestrator.validator.detect_build_system = Mock(side_effect=lambda p: (
            execution_order.append('VALIDATE_detect'),
            'python'
        )[1])
        
        orchestrator.validator.execute_build = Mock(side_effect=lambda s, p: (
            execution_order.append('VALIDATE_build'),
            {'success': True}
        )[1])
        
        orchestrator.validator.run_tests = Mock(side_effect=lambda s, p: (
            execution_order.append('VALIDATE_test'),
            {'success': True, 'passed': True}
        )[1])
        
        orchestrator.reporter.generate_audit_report = Mock(side_effect=lambda results: (
            execution_order.append('REPORT'),
            temp_project / "report.md"
        )[1])
        
        # Execute
        result = orchestrator.execute()
        
        # Verify order
        expected = [
            'ANALYZE_scan',
            'ANALYZE_extract',
            'ANALYZE_namespaces',
            'MAPPING',
            'MAPPING_conflicts',
            'TRANSFORM',
            'VALIDATE_detect',
            'VALIDATE_build',
            'VALIDATE_test',
            'REPORT'
        ]
        assert execution_order == expected

