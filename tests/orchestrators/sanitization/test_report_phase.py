"""
Test Suite: Report Phase Integration
Phase: RED (Tests written first)
Coverage Target: 3 tests for ReportGenerator integration

Tests report generation, metrics collection, and output format.
ReportGenerator workflow: generate_audit_report(results) → markdown report
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


class TestReportPhase:
    """Test REPORT phase integration"""

    @pytest.mark.skipif(
        SanitizationOrchestrator is None,
        reason="Orchestrator not yet implemented (RED phase)"
    )
    def test_report_generation(self, tmp_path):
        """Test report generates with complete workflow results"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Mock all phases
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': 'main.py'}], 'total_files': 10
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            'Customer': {'count': 5, 'category': 'business_entity'}
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={'python': ['app', 'services']})
        orchestrator.mapper.generate_mappings = Mock(return_value={
            'Customer': 'Entity', 'Order': 'Transaction'
        })
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 10, 'transformations_applied': 42
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={
            'success': True, 'tests_passed': 25, 'tests_failed': 0
        })
        
        # Mock report generator
        orchestrator.reporter.generate_audit_report = Mock(return_value=str(target_dir / "report.md"))
        
        result = orchestrator.execute()
        
        # Verify report generation called
        assert result.success is True
        assert orchestrator.reporter.generate_audit_report.called
        
        # Verify results dict passed to report generator
        call_args = orchestrator.reporter.generate_audit_report.call_args
        assert call_args is not None
        results = call_args[0][0]  # First positional arg
        assert 'phases' in results
        assert 'status' in results

    @pytest.mark.skipif(
        SanitizationOrchestrator is None,
        reason="Orchestrator not yet implemented (RED phase)"
    )
    def test_report_metrics_collection(self, tmp_path):
        """Test report captures all phase metrics"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Mock phases with detailed metrics
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': f'file{i}.py'} for i in range(50)], 
            'total_files': 50
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            f'Term{i}': {'count': i, 'category': 'business_entity'} for i in range(10)
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={'python': ['ns1', 'ns2', 'ns3']})
        orchestrator.mapper.generate_mappings = Mock(return_value={
            f'Term{i}': f'Generic{i}' for i in range(10)
        })
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 50, 
            'transformations_applied': 150,
            'files_renamed': 5
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={
            'success': True, 
            'tests_passed': 100, 
            'tests_failed': 0,
            'coverage': 92.5
        })
        
        orchestrator.reporter.generate_audit_report = Mock(return_value=str(target_dir / "report.md"))
        
        result = orchestrator.execute()
        
        # Verify comprehensive metrics passed
        call_args = orchestrator.reporter.generate_audit_report.call_args
        results = call_args[0][0]
        
        assert results['phases']['analyze']['file_inventory']['total_files'] == 50
        assert len(results['phases']['analyze']['domain_terms']) == 10
        assert len(results['phases']['mapping']['mappings']) == 10
        assert results['phases']['transform']['files_transformed'] == 50
        # Validate results are in test_result sub-dict
        assert results['phases']['validate']['test_result']['tests_passed'] == 100

    @pytest.mark.skipif(
        SanitizationOrchestrator is None,
        reason="Orchestrator not yet implemented (RED phase)"
    )
    def test_report_output_format(self, tmp_path):
        """Test report generator returns valid file path"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Mock minimal phases
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': 'main.py'}], 'total_files': 1
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        orchestrator.mapper.generate_mappings = Mock(return_value={'Customer': 'Entity'})
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        orchestrator.transformer.transform_codebase = Mock(return_value={'files_transformed': 1})
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True})
        
        # Mock report to return realistic path
        expected_path = str(target_dir / "sanitization-audit-report.md")
        orchestrator.reporter.generate_audit_report = Mock(return_value=expected_path)
        
        result = orchestrator.execute()
        
        # Verify report path captured
        assert result.success is True
        assert orchestrator.reporter.generate_audit_report.called
        
        # Verify path format
        returned_path = orchestrator.reporter.generate_audit_report.return_value
        assert returned_path.endswith(".md")
        assert "report" in returned_path.lower()


# Test markers for pytest
pytestmark = [
    pytest.mark.orchestrator_test,
    pytest.mark.cortex_v4,
]
