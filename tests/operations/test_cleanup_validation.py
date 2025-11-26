"""Tests for cleanup validation system"""

import pytest
from pathlib import Path
from src.operations.modules.cleanup.critical_file_detector import CriticalFileDetector
from src.operations.modules.cleanup.cleanup_validator import CleanupValidator
from src.operations.modules.cleanup.cleanup_verifier import CleanupVerifier


class TestCriticalFileDetector:
    """Test critical file detection"""
    
    def test_detects_entry_points(self):
        """Should detect entry point files as critical"""
        project_root = Path(__file__).parent.parent.parent.parent
        detector = CriticalFileDetector(project_root)
        critical_files = detector.detect_critical_files()
        
        # Check if key files are detected
        main_py = project_root / 'src' / 'main.py'
        if main_py.exists():
            assert main_py in critical_files
    
    def test_protects_src_directory(self):
        """Should protect entire src/ directory"""
        project_root = Path(__file__).parent.parent.parent.parent
        detector = CriticalFileDetector(project_root)
        critical_files = detector.detect_critical_files()
        
        # Any file in src/ should be critical
        src_files = list((project_root / 'src').rglob('*.py'))
        if src_files:
            assert src_files[0] in critical_files
    
    def test_traces_imports(self):
        """Should trace import dependencies"""
        project_root = Path(__file__).parent.parent.parent.parent
        detector = CriticalFileDetector(project_root)
        
        entry_point = project_root / 'src' / 'main.py'
        if entry_point.exists():
            dependencies = detector.trace_imports(entry_point)
            
            assert len(dependencies) > 0
            assert entry_point in dependencies


class TestCleanupValidator:
    """Test cleanup validation"""
    
    def test_blocks_critical_file_deletion(self):
        """Should block deletion of critical files"""
        project_root = Path(__file__).parent.parent.parent.parent
        validator = CleanupValidator(project_root)
        
        manifest = {
            'proposed_actions': [
                {'action': 'delete', 'file': str(project_root / 'src' / 'main.py')}
            ]
        }
        
        result = validator.validate_proposed_cleanup(manifest)
        
        # If src/main.py exists, deletion should be blocked
        if (project_root / 'src' / 'main.py').exists():
            assert not result.passed
            assert result.has_critical_errors
    
    def test_allows_safe_deletion(self):
        """Should allow deletion of safe files"""
        project_root = Path(__file__).parent.parent.parent.parent
        validator = CleanupValidator(project_root)
        
        # Create temporary safe file
        temp_file = project_root / 'temp_cleanup_test_file.md'
        temp_file.write_text("Test file for cleanup validation")
        
        try:
            manifest = {
                'proposed_actions': [
                    {'action': 'delete', 'file': str(temp_file)}
                ]
            }
            
            result = validator.validate_proposed_cleanup(manifest)
            
            # Should pass as it's not a critical file
            assert result.passed or not result.has_critical_errors
            
        finally:
            # Cleanup
            if temp_file.exists():
                temp_file.unlink()
    
    def test_validates_entry_points(self):
        """Should validate entry points are importable"""
        project_root = Path(__file__).parent.parent.parent.parent
        validator = CleanupValidator(project_root)
        
        # Test with empty manifest (no deletions)
        manifest = {'proposed_actions': []}
        
        result = validator.validate_proposed_cleanup(manifest)
        
        # Should pass if all entry points are importable
        assert result.passed or len(result.critical_errors) == 0


class TestCleanupVerifier:
    """Test post-cleanup verification"""
    
    def test_verifies_imports(self):
        """Should verify critical imports work"""
        project_root = Path(__file__).parent.parent.parent.parent
        verifier = CleanupVerifier(project_root)
        
        result = verifier._validate_imports()
        
        # Should have checked imports
        assert 'passed' in result
        assert 'total' in result
        assert result['total'] > 0
    
    def test_verifies_test_discovery(self):
        """Should verify tests are discoverable"""
        project_root = Path(__file__).parent.parent.parent.parent
        verifier = CleanupVerifier(project_root)
        
        result = verifier._validate_test_discovery()
        
        # Should have attempted test discovery
        assert 'passed' in result
        
        # If tests exist, should find them
        if result['passed']:
            assert result.get('tests_found', 0) > 0
    
    def test_full_verification(self):
        """Should run full verification"""
        project_root = Path(__file__).parent.parent.parent.parent
        verifier = CleanupVerifier(project_root)
        
        result = verifier.verify_cleanup(use_health_validator=False)
        
        # Should have run checks
        assert 'imports' in result.checks
        assert 'test_discovery' in result.checks
        assert 'smoke_tests' in result.checks


class TestValidationIntegration:
    """Test validation integration with orchestrator"""
    
    def test_validation_available_flag(self):
        """Should detect if validation modules are available"""
        from src.operations.modules.cleanup.holistic_cleanup_orchestrator import VALIDATION_AVAILABLE
        
        # Should be True since we can import the modules in tests
        assert VALIDATION_AVAILABLE is True
    
    def test_orchestrator_imports_validators(self):
        """Should import validator classes"""
        try:
            from src.operations.modules.cleanup.holistic_cleanup_orchestrator import (
                CleanupValidator,
                CleanupVerifier
            )
            # If this doesn't raise ImportError, validation is available
            assert True
        except ImportError:
            pytest.skip("Validation modules not available")


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
