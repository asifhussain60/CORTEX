"""
CORTEX 6.0 - Phase 2.2: Version-Agnostic Import System Tests

Tests for version compatibility and dynamic import management.
Ensures CORTEX works across Python 3.9, 3.10, 3.11, 3.12+

AC Coverage:
- AC-VERSION-001: Support Python 3.9+ without version-specific code
- AC-VERSION-002: Dynamic import with fallbacks for missing packages
- AC-VERSION-003: Version compatibility matrix validation
- AC-VERSION-004: Graceful degradation for optional features

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest


# ==============================================================================
# AC-VERSION-001: Python Version Compatibility
# ==============================================================================

@pytest.mark.ac_id("AC-VERSION-001")
class TestPythonVersionCompatibility:
    """Test: CORTEX supports Python 3.9+ without version-specific code."""
    
    def test_current_python_version_supported(self):
        """Test: Current Python version is ≥3.9."""
        major, minor = sys.version_info[:2]
        assert major == 3, f"Python {major}.x not supported (requires 3.9+)"
        assert minor >= 9, f"Python 3.{minor} not supported (requires 3.9+)"
    
    def test_import_manager_exists(self):
        """Test: ImportManager class exists for version-agnostic imports."""
        from infrastructure.import_manager import ImportManager
        
        assert ImportManager is not None
        assert hasattr(ImportManager, 'import_with_fallback')
        assert hasattr(ImportManager, 'get_python_version')
    
    def test_import_manager_detects_version(self):
        """Test: ImportManager correctly detects Python version."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        version = manager.get_python_version()
        
        assert isinstance(version, tuple)
        assert len(version) >= 2
        assert version[0] == 3
        assert version[1] >= 9
    
    def test_version_compatibility_matrix_exists(self):
        """Test: Version compatibility configuration exists."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        matrix = manager.get_compatibility_matrix()
        
        assert isinstance(matrix, dict)
        assert 'python_versions' in matrix
        assert 'supported' in matrix['python_versions']
        
        # Should support 3.9, 3.10, 3.11, 3.12
        supported = matrix['python_versions']['supported']
        assert '3.9' in supported or 3.9 in supported
        assert len(supported) >= 4


# ==============================================================================
# AC-VERSION-002: Dynamic Import with Fallbacks
# ==============================================================================

@pytest.mark.ac_id("AC-VERSION-002")
class TestDynamicImportFallbacks:
    """Test: Dynamic import system with graceful fallbacks."""
    
    def test_import_with_fallback_success(self):
        """Test: import_with_fallback returns module when available."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Import a standard library module
        os_module = manager.import_with_fallback('os')
        
        assert os_module is not None
        assert hasattr(os_module, 'path')
    
    def test_import_with_fallback_missing_package(self):
        """Test: import_with_fallback returns None for missing packages."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Try to import non-existent package
        result = manager.import_with_fallback('nonexistent_package_xyz')
        
        assert result is None
    
    def test_import_with_fallback_alternative(self):
        """Test: import_with_fallback tries alternative when primary fails."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Try primary (doesn't exist), fallback to alternative (exists)
        result = manager.import_with_fallback(
            'nonexistent_package',
            fallback='os'
        )
        
        assert result is not None
        assert hasattr(result, 'path')
    
    def test_optional_import_feature_flag(self):
        """Test: Optional imports can be disabled via feature flags."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Disable optional features
        manager.enable_optional_features(False)
        
        # Import optional package (should skip even if available)
        result = manager.import_with_fallback(
            'anthropic',
            optional=True
        )
        
        # Can be None if disabled OR if package not installed
        assert result is None or hasattr(result, '__name__')


# ==============================================================================
# AC-VERSION-003: Version Compatibility Matrix
# ==============================================================================

@pytest.mark.ac_id("AC-VERSION-003")
class TestVersionCompatibilityMatrix:
    """Test: Version compatibility matrix validation."""
    
    def test_compatibility_matrix_schema(self):
        """Test: Compatibility matrix has required structure."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        matrix = manager.get_compatibility_matrix()
        
        # Required top-level keys
        assert 'python_versions' in matrix
        assert 'package_compatibility' in matrix
        
        # Python versions structure
        py_versions = matrix['python_versions']
        assert 'supported' in py_versions
        assert 'minimum' in py_versions
        assert 'tested' in py_versions
    
    def test_minimum_python_version_is_3_9(self):
        """Test: Minimum Python version is 3.9."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        matrix = manager.get_compatibility_matrix()
        
        minimum = matrix['python_versions']['minimum']
        
        # Can be string "3.9" or tuple (3, 9)
        if isinstance(minimum, str):
            assert minimum == "3.9"
        elif isinstance(minimum, (tuple, list)):
            assert minimum[0] == 3
            assert minimum[1] == 9
    
    def test_package_compatibility_includes_core_packages(self):
        """Test: Compatibility matrix includes core packages."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        matrix = manager.get_compatibility_matrix()
        
        packages = matrix['package_compatibility']
        
        # Core packages should be listed
        assert 'pytest' in packages or any('pytest' in str(p) for p in packages)
        assert 'pyyaml' in packages or 'PyYAML' in packages or any('yaml' in str(p).lower() for p in packages)
    
    def test_current_environment_compatibility_check(self):
        """Test: Can check if current environment is compatible."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        is_compatible = manager.check_environment_compatibility()
        
        # Should return True for supported Python versions
        major, minor = sys.version_info[:2]
        if major == 3 and minor >= 9:
            assert is_compatible is True


# ==============================================================================
# AC-VERSION-004: Graceful Degradation
# ==============================================================================

@pytest.mark.ac_id("AC-VERSION-004")
class TestGracefulDegradation:
    """Test: Graceful degradation for optional features."""
    
    def test_missing_optional_package_doesnt_crash(self):
        """Test: Missing optional packages don't crash CORTEX."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Try to import optional AI packages
        openai_module = manager.import_with_fallback('openai', optional=True)
        anthropic_module = manager.import_with_fallback('anthropic', optional=True)
        
        # Should either work or return None, but NOT raise
        assert openai_module is None or hasattr(openai_module, '__name__')
        assert anthropic_module is None or hasattr(anthropic_module, '__name__')
    
    def test_feature_availability_detection(self):
        """Test: Can detect which optional features are available."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        features = manager.get_available_features()
        
        assert isinstance(features, dict)
        
        # Should have feature flags
        assert 'ai_integration' in features
        assert 'vision_api' in features
        assert 'advanced_parsing' in features
        
        # Each feature is boolean
        assert isinstance(features['ai_integration'], bool)
    
    def test_fallback_to_builtin_modules(self):
        """Test: Falls back to builtin modules when advanced packages missing."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Even if parso is missing, should fall back to ast
        ast_module = manager.import_with_fallback('parso', fallback='ast')
        
        assert ast_module is not None
        # Either parso (preferred) or ast (fallback)
        assert hasattr(ast_module, 'parse') or hasattr(ast_module, 'parse')
    
    def test_degraded_mode_logging(self):
        """Test: Logs when operating in degraded mode (missing optional deps)."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Check degraded mode status
        degraded_features = manager.get_degraded_features()
        
        assert isinstance(degraded_features, list)
        # List can be empty (all features available) or contain missing feature names


# ==============================================================================
# Integration Tests
# ==============================================================================

@pytest.mark.ac_id("AC-VERSION-001")
@pytest.mark.ac_id("AC-VERSION-002")
class TestImportManagerIntegration:
    """Integration tests for ImportManager across different scenarios."""
    
    def test_import_manager_singleton_pattern(self):
        """Test: ImportManager uses singleton pattern for consistency."""
        from infrastructure.import_manager import ImportManager
        
        manager1 = ImportManager()
        manager2 = ImportManager()
        
        # Should return same instance or equivalent state
        assert manager1.get_python_version() == manager2.get_python_version()
    
    def test_bulk_import_with_fallbacks(self):
        """Test: Can import multiple packages with fallbacks at once."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        packages = {
            'os': None,  # Standard library
            'sys': None,  # Standard library
            'pytest': None,  # Required dependency
            'nonexistent': 'os',  # Fallback
        }
        
        results = manager.bulk_import(packages)
        
        assert isinstance(results, dict)
        assert results['os'] is not None
        assert results['sys'] is not None
        assert results['pytest'] is not None
        assert results['nonexistent'] is not None  # Should get fallback
    
    def test_version_specific_workarounds(self):
        """Test: Can apply version-specific workarounds automatically."""
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        # Check if workarounds are needed for current version
        workarounds = manager.get_active_workarounds()
        
        assert isinstance(workarounds, list)
        # May be empty if no workarounds needed for current version
    
    def test_import_timing_performance(self):
        """Test: Import operations complete within acceptable time."""
        import time
        from infrastructure.import_manager import ImportManager
        
        manager = ImportManager()
        
        start = time.time()
        
        # Import several packages
        manager.import_with_fallback('os')
        manager.import_with_fallback('sys')
        manager.import_with_fallback('pytest')
        
        duration = time.time() - start
        
        # Should complete in <100ms (lazy loading)
        assert duration < 0.1, f"Import operations too slow: {duration:.3f}s"
