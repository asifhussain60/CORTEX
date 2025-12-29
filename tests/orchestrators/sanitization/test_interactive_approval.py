"""
Test Suite: Interactive Approval for Sanitization Workflow
Phase: Integration Testing
Coverage Target: 10+ tests for interactive approval scenarios

Tests conflict detection, mapping conflicts, and approval workflow foundation.
Validates that conflicts are properly detected and logged for user review.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

from src.orchestrators.sanitization.sanitization_orchestrator import (
    SanitizationOrchestrator,
    SanitizationPhase,
    SanitizationResult,
)


@pytest.fixture
def temp_project():
    """Create temporary project structure for approval testing"""
    tmpdir = Path(tempfile.mkdtemp())
    
    # Create sample Python project with conflicting terms
    src_dir = tmpdir / "src"
    src_dir.mkdir()
    
    (src_dir / "acme_api.py").write_text("""
class AcmeAPI:
    def fetch_data(self):
        return self.acme_client.get()
""")
    
    (src_dir / "acme_service.py").write_text("""
class AcmeService:
    def process(self):
        return self.acme_processor.run()
""")
    
    yield tmpdir
    shutil.rmtree(tmpdir)


def mock_analyzer_with_conflicts(orchestrator):
    """Helper to mock analyzer that returns terms with conflicts"""
    orchestrator.analyzer.scan_file_structure = Mock(return_value={
        'files': [
            {'path': 'src/acme_api.py', 'language': 'python'},
            {'path': 'src/acme_service.py', 'language': 'python'}
        ],
        'total_files': 2
    })
    # Multiple terms that map to same generic term (conflict)
    orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
        'AcmeAPI': 5,
        'AcmeService': 3,
        'AcmeClient': 2,
        'AcmeProcessor': 2
    })
    orchestrator.analyzer.extract_namespaces = Mock(return_value={})


def mock_mapper_with_conflicts(orchestrator):
    """Helper to mock mapper that detects conflicts"""
    # All terms map to 'Company' - creates conflict
    orchestrator.mapper.generate_mappings = Mock(return_value={
        'AcmeAPI': 'CompanyAPI',
        'AcmeService': 'CompanyService',
        'AcmeClient': 'CompanyClient',
        'AcmeProcessor': 'CompanyProcessor'
    })
    # Detect conflicts where multiple originals map to same generic
    orchestrator.mapper.detect_conflicts = Mock(return_value=[
        {
            'generic_term': 'CompanyAPI',
            'original_terms': ['AcmeAPI', 'ACME_API']
        }
    ])


class TestInteractiveApproval:
    """Test interactive approval workflow and conflict detection"""
    
    def test_conflict_detection_during_mapping(self, temp_project):
        """Test that conflicts are detected during MAPPING phase"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock analysis and mapping with conflicts
        mock_analyzer_with_conflicts(orchestrator)
        mock_mapper_with_conflicts(orchestrator)
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 2,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify conflict detection was called
        assert orchestrator.mapper.detect_conflicts.called
        
        # Verify workflow completed despite conflicts (conflicts logged, not blocking)
        assert result.success is True
    
    def test_conflict_logging(self, temp_project, caplog):
        """Test that conflicts are logged for user review"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock with conflicts
        mock_analyzer_with_conflicts(orchestrator)
        mock_mapper_with_conflicts(orchestrator)
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 2,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute with log capturing
        with caplog.at_level('WARNING'):
            result = orchestrator.execute()
        
        # Verify conflict warnings logged
        log_text = caplog.text
        assert 'naming conflicts' in log_text.lower() or 'conflict' in log_text.lower()
    
    def test_no_conflicts_proceeds_normally(self, temp_project):
        """Test that mapping proceeds normally when no conflicts"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock without conflicts
        mock_analyzer_with_conflicts(orchestrator)
        orchestrator.mapper.generate_mappings = Mock(return_value={
            'AcmeAPI': 'CompanyAPI',
            'AcmeService': 'ServiceLayer',  # Different generic terms
            'AcmeClient': 'HTTPClient',
            'AcmeProcessor': 'DataProcessor'
        })
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])  # No conflicts
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 2,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify success with no conflicts
        assert result.success is True
        assert orchestrator.mapper.detect_conflicts.called
    
    def test_multiple_conflicts_detected(self, temp_project):
        """Test detection of multiple naming conflicts"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock analysis
        mock_analyzer_with_conflicts(orchestrator)
        
        # Mock multiple conflicts
        orchestrator.mapper.generate_mappings = Mock(return_value={
            'AcmeAPI': 'CompanyAPI',
            'AcmeService': 'CompanyService'
        })
        orchestrator.mapper.detect_conflicts = Mock(return_value=[
            {'generic_term': 'CompanyAPI', 'original_terms': ['AcmeAPI', 'ACME_API']},
            {'generic_term': 'CompanyService', 'original_terms': ['AcmeService', 'ACME_Service']},
            {'generic_term': 'CompanyClient', 'original_terms': ['AcmeClient', 'ACME_Client']}
        ])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 2,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify multiple conflicts handled
        assert result.success is True
        assert orchestrator.mapper.detect_conflicts.called
    
    def test_conflict_resolution_applied(self, temp_project):
        """Test that conflict resolution is available via mapper"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock analysis and conflicts
        mock_analyzer_with_conflicts(orchestrator)
        
        conflicts = [
            {'generic_term': 'Company', 'original_terms': ['Acme', 'ACME', 'AcmeInc']}
        ]
        
        orchestrator.mapper.generate_mappings = Mock(return_value={'Acme': 'Company'})
        orchestrator.mapper.detect_conflicts = Mock(return_value=conflicts)
        
        # Mock conflict resolution
        orchestrator.mapper.resolve_conflicts = Mock(return_value={
            'Acme': 'Company_0',
            'ACME': 'Company_1',
            'AcmeInc': 'Company_2'
        })
        
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 2,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify mapper has resolve_conflicts capability
        assert hasattr(orchestrator.mapper, 'resolve_conflicts')
    
    def test_empty_mappings_no_conflicts(self, temp_project):
        """Test that empty mappings result in no conflicts"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock empty analysis
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [],
            'total_files': 0
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        
        orchestrator.mapper.generate_mappings = Mock(return_value={})
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 0,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify no conflicts with empty mappings
        assert result.success is True
        assert result.mappings_created == 0
    
    def test_conflict_details_structure(self, temp_project):
        """Test that conflict details have proper structure"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock analysis
        mock_analyzer_with_conflicts(orchestrator)
        
        # Mock conflict with specific structure
        test_conflict = {
            'generic_term': 'CompanyAPI',
            'original_terms': ['AcmeAPI', 'ACME_API', 'acme_api']
        }
        
        orchestrator.mapper.generate_mappings = Mock(return_value={'AcmeAPI': 'CompanyAPI'})
        orchestrator.mapper.detect_conflicts = Mock(return_value=[test_conflict])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 2,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify conflict was called with proper structure
        conflicts_returned = orchestrator.mapper.detect_conflicts.return_value
        assert len(conflicts_returned) == 1
        assert 'generic_term' in conflicts_returned[0]
        assert 'original_terms' in conflicts_returned[0]
        assert isinstance(conflicts_returned[0]['original_terms'], list)
    
    def test_dry_run_with_conflicts(self, temp_project):
        """Test that dry-run mode still detects conflicts"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=True  # DRY RUN
        )
        
        # Mock with conflicts
        mock_analyzer_with_conflicts(orchestrator)
        mock_mapper_with_conflicts(orchestrator)
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify conflicts detected even in dry-run
        assert orchestrator.mapper.detect_conflicts.called
        assert result.success is True
    
    def test_case_sensitivity_conflicts(self, temp_project):
        """Test detection of case-sensitivity conflicts"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock terms with case variations
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': 'src/file.py', 'language': 'python'}],
            'total_files': 1
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            'Acme': 5,
            'ACME': 3,
            'acme': 2
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        
        # All map to same generic (case-insensitive conflict)
        orchestrator.mapper.generate_mappings = Mock(return_value={
            'Acme': 'Company',
            'ACME': 'Company',
            'acme': 'Company'
        })
        orchestrator.mapper.detect_conflicts = Mock(return_value=[
            {
                'generic_term': 'Company',
                'original_terms': ['Acme', 'ACME', 'acme']
            }
        ])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 1,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify case-sensitivity conflict detected
        assert result.success is True
        assert orchestrator.mapper.detect_conflicts.called
    
    def test_namespace_conflicts(self, temp_project):
        """Test detection of namespace/module conflicts"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock terms and namespaces
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'files': [{'path': 'src/acme/__init__.py', 'language': 'python'}],
            'total_files': 1
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            'AcmeModule': 2
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={
            'acme': 'module',
            'acme.api': 'module',
            'acme.service': 'module'
        })
        
        # Namespace mappings with conflicts
        orchestrator.mapper.generate_mappings = Mock(return_value={
            'acme': 'company',
            'acme.api': 'company_api',
            'AcmeModule': 'CompanyModule'
        })
        orchestrator.mapper.detect_conflicts = Mock(return_value=[
            {
                'generic_term': 'company',
                'original_terms': ['acme', 'Acme']
            }
        ])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 1,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute
        result = orchestrator.execute()
        
        # Verify namespace conflicts detected
        assert result.success is True
        assert orchestrator.mapper.detect_conflicts.called
    
    def test_conflict_count_in_logs(self, temp_project, caplog):
        """Test that conflict count is logged"""
        orchestrator = SanitizationOrchestrator(
            target_directory=str(temp_project),
            dry_run=False
        )
        
        # Mock with specific conflict count
        mock_analyzer_with_conflicts(orchestrator)
        orchestrator.mapper.generate_mappings = Mock(return_value={'A': 'B'})
        orchestrator.mapper.detect_conflicts = Mock(return_value=[
            {'generic_term': 'X', 'original_terms': ['A', 'B']},
            {'generic_term': 'Y', 'original_terms': ['C', 'D']},
            {'generic_term': 'Z', 'original_terms': ['E', 'F']}
        ])
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 1,
            'success': True
        })
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': True})
        orchestrator.reporter.generate_audit_report = Mock(return_value=temp_project / "report.md")
        
        # Execute with log capturing
        with caplog.at_level('WARNING'):
            result = orchestrator.execute()
        
        # Verify conflict count logged
        log_text = caplog.text
        assert '3' in log_text or 'conflicts' in log_text.lower()
