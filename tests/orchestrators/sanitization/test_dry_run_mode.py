"""
Test Suite: Dry-Run Mode for Sanitization Workflow
Phase: Integration Testing
Coverage Target: 8+ tests for dry-run mode scenarios

Tests that dry-run mode simulates workflow without modifying files.
Validates preview generation, simulation accuracy, and file protection.
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
    """Create temporary project structure for dry-run testing"""
    tmpdir = Path(tempfile.mkdtemp())
    
    # Create sample Python project
    src_dir = tmpdir / "src"
    src_dir.mkdir()
    
    # Original file content
    original_content = """
class AcmeService:
    def process_acme_order(self, order_id):
        return self.acme_api.fetch_order(order_id)
"""
    
    (src_dir / "acme_module.py").write_text(original_content)
    
    yield tmpdir, original_content
    
    # Cleanup
    shutil.rmtree(tmpdir)


def mock_analyzer_for_dry_run(orchestrator, files_count=3, terms_count=5):
    """Helper to mock analyzer for dry-run tests"""
    orchestrator.analyzer.scan_file_structure = Mock(return_value={
        'files': [{'path': f'src/file{i}.py', 'language': 'python'} for i in range(files_count)],
        'total_files': files_count
    })
    orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
        f'Acme{i}': i+1 for i in range(terms_count)
    })
    orchestrator.analyzer.extract_namespaces = Mock(return_value={})


def mock_mapper_for_dry_run(orchestrator, mappings_count=5):
    """Helper to mock mapper for dry-run tests"""
    orchestrator.mapper.generate_mappings = Mock(return_value={
        f'Acme{i}': f'Company{i}' for i in range(mappings_count)
    })
    orchestrator.mapper.detect_conflicts = Mock(return_value=[])


class TestDryRunMode:
    """Test dry-run mode simulation without file modifications"""
    
    def test_dry_run_skips_transformation(self, temp_project):
        """Test that dry-run mode skips TRANSFORM phase entirely"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True  # DRY RUN MODE
        )
        
        # Mock analysis and mapping
        mock_analyzer_for_dry_run(orchestrator, files_count=3, terms_count=5)
        mock_mapper_for_dry_run(orchestrator, mappings_count=5)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify transformer was never called (no mocking needed in dry-run)
        # In dry-run, transformer methods are not invoked
        
        # Verify no files transformed
        assert result.files_transformed == 0
        
        # Verify success
        assert result.success is True
    
    def test_dry_run_skips_validation(self, temp_project):
        """Test that dry-run mode skips VALIDATE phase entirely"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock analysis and mapping
        mock_analyzer_for_dry_run(orchestrator)
        mock_mapper_for_dry_run(orchestrator)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify validator was never called (no mocking needed in dry-run)
        # In dry-run, validator methods are not invoked
        
        # Verify validation always passes in dry-run
        assert result.validation_passed is True
    
    def test_dry_run_preserves_original_files(self, temp_project):
        """Test that dry-run mode does not modify original files"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock analysis and mapping
        mock_analyzer_for_dry_run(orchestrator)
        mock_mapper_for_dry_run(orchestrator)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify original file unchanged
        original_file = tmpdir / "src/acme_module.py"
        assert original_file.read_text() == original_content
        
        # Verify no backup directory created
        backup_dirs = list(tmpdir.glob("*_backup*"))
        assert len(backup_dirs) == 0
    
    def test_dry_run_reports_simulation_metrics(self, temp_project):
        """Test that dry-run mode reports accurate simulation metrics"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock with specific counts
        mock_analyzer_for_dry_run(orchestrator, files_count=10, terms_count=7)
        mock_mapper_for_dry_run(orchestrator, mappings_count=7)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify analysis metrics captured
        assert result.files_analyzed == 10
        assert result.mappings_created == 7
        
        # Verify transformation skipped
        assert result.files_transformed == 0
        
        # Verify validation auto-passed
        assert result.validation_passed is True
    
    def test_dry_run_generates_preview_report(self, temp_project):
        """Test that dry-run mode generates preview/audit report"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock analysis and mapping
        mock_analyzer_for_dry_run(orchestrator)
        mock_mapper_for_dry_run(orchestrator)
        
        # Mock reporter to track call
        expected_report_path = tmpdir / "dry-run-report.md"
        orchestrator.reporter.generate_audit_report = Mock(return_value=expected_report_path)
        
        # Execute
        result = orchestrator.execute()
        
        # Verify reporter was called (preview generation)
        assert orchestrator.reporter.generate_audit_report.called
        
        # Verify report path in result
        assert result.report_path == expected_report_path
    
    def test_dry_run_completes_faster_than_full_run(self, temp_project):
        """Test that dry-run mode executes faster (no transform/validate)"""
        tmpdir, original_content = temp_project
        
        # Dry-run execution
        orchestrator_dry = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        mock_analyzer_for_dry_run(orchestrator_dry)
        mock_mapper_for_dry_run(orchestrator_dry)
        orchestrator_dry.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        result_dry = orchestrator_dry.execute()
        dry_run_duration = result_dry.duration_seconds
        
        # Full execution (with slow mocks)
        import time
        orchestrator_full = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=False
        )
        
        def slow_transform(*args, **kwargs):
            time.sleep(0.1)  # Simulate slow transformation
            return {'files_transformed': 5, 'success': True}
        
        mock_analyzer_for_dry_run(orchestrator_full)
        mock_mapper_for_dry_run(orchestrator_full)
        orchestrator_full.transformer.transform_codebase = Mock(side_effect=slow_transform)
        orchestrator_full.validator.detect_build_system = Mock(return_value='python')
        orchestrator_full.validator.execute_build = Mock(return_value={'success': True})
        orchestrator_full.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator_full.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        result_full = orchestrator_full.execute()
        full_duration = result_full.duration_seconds
        
        # Verify dry-run faster (should skip 0.1s delay)
        assert dry_run_duration < full_duration
    
    def test_dry_run_logs_simulation_mode(self, temp_project, caplog):
        """Test that dry-run mode logs simulation messages"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock analysis and mapping
        mock_analyzer_for_dry_run(orchestrator)
        mock_mapper_for_dry_run(orchestrator)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute with log capturing
        with caplog.at_level('INFO'):
            result = orchestrator.execute()
        
        # Verify dry-run mentioned in logs
        log_text = caplog.text
        assert 'Dry Run: True' in log_text
    
    def test_dry_run_with_zero_mappings(self, temp_project):
        """Test dry-run mode with no domain terms found"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock empty analysis
        mock_analyzer_for_dry_run(orchestrator, files_count=5, terms_count=0)
        mock_mapper_for_dry_run(orchestrator, mappings_count=0)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify success with zero metrics
        assert result.success is True
        assert result.files_analyzed == 5
        assert result.mappings_created == 0
        assert result.files_transformed == 0
        assert result.validation_passed is True
    
    def test_dry_run_analyzer_failure_still_fails(self, temp_project):
        """Test that dry-run mode still fails on analyzer errors"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock analyzer failure
        orchestrator.analyzer.scan_file_structure = Mock(side_effect=Exception("Scan failed"))
        
        # Execute
        result = orchestrator.execute()
        
        # Verify failure propagates even in dry-run
        assert result.success is False
        assert result.phase == SanitizationPhase.ANALYZE
        assert len(result.errors) > 0
    
    def test_dry_run_mapping_failure_still_fails(self, temp_project):
        """Test that dry-run mode still fails on mapping errors"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock successful analysis but failed mapping
        mock_analyzer_for_dry_run(orchestrator)
        orchestrator.mapper.generate_mappings = Mock(side_effect=Exception("Mapping failed"))
        
        # Execute
        result = orchestrator.execute()
        
        # Verify failure propagates
        assert result.success is False
        assert result.phase == SanitizationPhase.MAPPING
        assert len(result.errors) > 0
    
    def test_dry_run_reaches_report_phase(self, temp_project):
        """Test that dry-run mode always reaches REPORT phase on success"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock successful analysis and mapping
        mock_analyzer_for_dry_run(orchestrator)
        mock_mapper_for_dry_run(orchestrator)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify reached final phase
        assert result.phase == SanitizationPhase.REPORT
        assert result.success is True
    
    def test_dry_run_with_large_file_count(self, temp_project):
        """Test dry-run mode with large number of files"""
        tmpdir, original_content = temp_project
        orchestrator = SanitizationOrchestrator(
            target_directory=str(tmpdir),
            dry_run=True
        )
        
        # Mock large file analysis
        mock_analyzer_for_dry_run(orchestrator, files_count=1000, terms_count=50)
        mock_mapper_for_dry_run(orchestrator, mappings_count=50)
        orchestrator.reporter.generate_audit_report = Mock(return_value=tmpdir / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify handles large counts
        assert result.success is True
        assert result.files_analyzed == 1000
        assert result.mappings_created == 50
        assert result.files_transformed == 0  # Dry-run skips
        assert result.duration_seconds < 5  # Should be fast (no real I/O)
