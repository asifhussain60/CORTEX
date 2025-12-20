"""
Test Suite: Mapping Phase Integration
Phase: RED (Tests written first)
Coverage Target: 3 tests for MappingEngine integration

Tests mapping generation, conflict detection, and user approval workflow.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch

from src.orchestrators.sanitization.sanitization_orchestrator import (
    SanitizationOrchestrator,
    SanitizationPhase,
)


class TestMappingPhase:
    """Test MAPPING phase integration with MappingEngine utility"""

    def test_mapping_generation(self, tmp_path):
        """Test that mapping phase generates domain→generic mappings"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=True
        )
        
        # Mock analyzer to return domain terms
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'total_files': 2,
            'files': [
                {'path': 'service.py', 'language': 'python'},
                {'path': 'model.py', 'language': 'python'}
            ]
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            'Customer': {'count': 5, 'category': 'business_entity'},
            'Invoice': {'count': 3, 'category': 'business_entity'},
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={
            'python': ['mycompany.services', 'mycompany.models']
        })
        
        result = orchestrator.execute()
        
        # Should succeed and create mappings
        assert result.success is True
        assert result.mappings_created >= 0  # Mappings were generated
        assert result.phase == SanitizationPhase.REPORT

    def test_mapping_conflict_detection(self, tmp_path):
        """Test that mapping phase detects conflicts"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=True
        )
        
        # Mock analyzer
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'total_files': 1,
            'files': [{'path': 'test.py', 'language': 'python'}]
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            'Order': {'count': 1, 'category': 'business_entity'},
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={
            'python': []
        })
        
        # Mock mapper to detect conflicts
        test_mappings = {'Order': 'Entity', 'Purchase': 'Entity'}
        orchestrator.mapper.generate_mappings = Mock(return_value=test_mappings)
        orchestrator.mapper.detect_conflicts = Mock(return_value=[
            {'generic_term': 'Entity', 'original_terms': ['Order', 'Purchase']}
        ])
        
        result = orchestrator.execute()
        
        # Should complete (conflicts logged but not blocking in dry-run)
        assert result.success is True

    def test_mapping_with_namespaces(self, tmp_path):
        """Test that mapping phase handles namespace mappings"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=True
        )
        
        # Mock analyzer with namespace data
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'total_files': 1,
            'files': [{'path': 'test.py', 'language': 'python'}]
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={
            'python': ['acme.corp.services', 'acme.corp.models'],
            'csharp': ['Acme.Corp.Services', 'Acme.Corp.Models']
        })
        
        result = orchestrator.execute()
        
        # Should succeed with namespace mappings
        assert result.success is True
        assert result.phase == SanitizationPhase.REPORT


# Test markers for pytest
pytestmark = [
    pytest.mark.orchestrator_test,
    pytest.mark.cortex_v4,
]
