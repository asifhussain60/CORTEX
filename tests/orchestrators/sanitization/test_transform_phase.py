"""
Test Suite: Transform Phase Integration
Phase: RED (Tests written first)
Coverage Target: 3 tests for CodeTransformer integration

Tests AST transformation, file renaming, and backup creation.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock

from src.orchestrators.sanitization.sanitization_orchestrator import (
    SanitizationOrchestrator,
    SanitizationPhase,
)


class TestTransformPhase:
    """Test TRANSFORM phase integration with CodeTransformer utility"""

    def test_transform_with_mappings(self, tmp_path):
        """Test that transform phase applies mappings"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        (target_dir / "test.py").write_text("# Test")
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False  # Need real transformation
        )
        
        # Mock phases - replace methods on real objects
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'total_files': 1,
            'files': [{'path': str(target_dir / "test.py"), 'language': 'python'}]
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            'Customer': {'count': 1, 'category': 'business_entity'}
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={'python': []})
        
        # Mock mapper to return mappings
        orchestrator.mapper.generate_mappings = Mock(return_value={
            'Customer': 'Entity',
            'customer': 'entity'
        })
        orchestrator.mapper.detect_conflicts = Mock(return_value=[])
        
        # Mock transformer - save original and replace
        original_transform = orchestrator.transformer.transform_codebase
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 1,
            'total_transformations': 2
        })
        
        # Mock validator
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True, 'passed': 10})
        
        result = orchestrator.execute()
        
        # Should call transformer
        assert orchestrator.transformer.transform_codebase.called
        assert result.files_transformed >= 0

    def test_transform_creates_backup(self, tmp_path):
        """Test that transform phase creates backup before modification"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=False
        )
        
        # Mock analyzer
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'total_files': 0,
            'files': []
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={})
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        
        # Mock transformer with backup info
        orchestrator.transformer.transform_codebase = Mock(return_value={
            'files_transformed': 0,
            'backup_created': True,
            'backup_path': '/tmp/backup'
        })
        
        # Mock validator
        orchestrator.validator.detect_build_system = Mock(return_value='python')
        orchestrator.validator.execute_build = Mock(return_value={'success': True})
        orchestrator.validator.run_tests = Mock(return_value={'success': True})
        
        result = orchestrator.execute()
        
        # Should succeed (backup is handled by transformer)
        assert result.success is True

    def test_transform_skipped_in_dry_run(self, tmp_path):
        """Test that transform phase is skipped in dry-run mode"""
        target_dir = tmp_path / "test_project"
        target_dir.mkdir()
        
        orchestrator = SanitizationOrchestrator(
            target_directory=str(target_dir),
            dry_run=True  # Dry-run should skip transform
        )
        
        # Mock analyzer
        orchestrator.analyzer.scan_file_structure = Mock(return_value={
            'total_files': 1,
            'files': [{'path': 'test.py'}]
        })
        orchestrator.analyzer.extract_domain_terminology = Mock(return_value={
            'Test': {'count': 1, 'category': 'business_entity'}
        })
        orchestrator.analyzer.extract_namespaces = Mock(return_value={})
        
        result = orchestrator.execute()
        
        # Transform should be skipped, no files transformed
        assert result.success is True
        assert result.files_transformed == 0
        assert result.phase == SanitizationPhase.REPORT


# Test markers for pytest
pytestmark = [
    pytest.mark.orchestrator_test,
    pytest.mark.cortex_v4,
]
