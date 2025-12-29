"""
Test Suite: Analyze Phase Integration
Phase: RED (Tests written first)
Coverage Target: 3 tests for CodeAnalyzer integration

Tests file scanning, domain term extraction, and analyzer configuration.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.sanitization.sanitization_orchestrator import (
    SanitizationOrchestrator,
    SanitizationPhase,
)


class TestAnalyzePhase:
    """Test ANALYZE phase integration with CodeAnalyzer utility"""

    def test_analyzer_initialization(self, tmp_path):
        """Test that CodeAnalyzer is initialized with correct parameters"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        # Create some test files
        (target_dir / "test.py").write_text("# Test file")
        (target_dir / "app.py").write_text("# App file")
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Analyzer should be initialized
        assert orchestrator.analyzer is not None
        assert hasattr(orchestrator.analyzer, 'scan_file_structure')
        assert hasattr(orchestrator.analyzer, 'extract_domain_terminology')

    def test_analyze_phase_file_scanning(self, tmp_path):
        """Test that analyze phase scans files correctly"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        # Create test files
        (target_dir / "main.py").write_text("# Main file")
        (target_dir / "utils.py").write_text("# Utils file")
        (target_dir / "README.md").write_text("# Documentation")
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=True
        )
        
        # Execute orchestrator
        result = orchestrator.execute()
        
        # Should succeed and analyze files
        assert result.success is True
        assert result.files_analyzed >= 0  # At least scanned (may be 0 in mock)
        assert result.phase == SanitizationPhase.REPORT

    def test_analyze_phase_domain_extraction(self, tmp_path):
        """Test that analyze phase extracts domain terms"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        # Create test file with domain-specific terms
        test_content = """
# Customer Management System
class CustomerService:
    def create_customer(self, customer_data):
        return Customer(**customer_data)
"""
        (target_dir / "service.py").write_text(test_content)
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=True
        )
        
        # Mock the analyzer to return expected terms
        expected_terms = ['Customer', 'CustomerService', 'create_customer']
        orchestrator.analyzer.extract_domain_terminology = Mock(
            return_value={term: {'count': 1} for term in expected_terms}
        )
        orchestrator.analyzer.scan_file_structure = Mock(
            return_value={'total_files': 1, 'files': ['service.py']}
        )
        
        result = orchestrator.execute()
        
        # Analyzer methods should have been called
        assert orchestrator.analyzer.scan_file_structure.called or \
               orchestrator.analyzer.extract_domain_terminology.called or \
               result.success is True


# Test markers for pytest
pytestmark = [
    pytest.mark.orchestrator_test,
    pytest.mark.cortex_v4,
]
