"""
Test Suite for Config Wiring Fixes (Phase 23)

Tests essential backward compatibility fixes:
- config singleton export from src.config
- config.brain_path property
- config.ensure_paths_exist() method

TDD Cycle: RED → GREEN → REFACTOR
Phase: Phase 23 (Python CLI Import Chain)
"""

import pytest
import os
import tempfile
import shutil
from pathlib import Path


class TestConfigSingletonExport:
    """Test that config singleton is properly exported from src.config."""
    
    def test_config_import_succeeds(self):
        """RED: Test that 'from src.config import config' works."""
        from src.config import config
        assert config is not None, "config should be importable"
    
    def test_config_is_cortex_config_instance(self):
        """RED: Test that config is a CortexConfig instance."""
        from src.config import config, CortexConfig
        assert isinstance(config, CortexConfig), \
            f"config should be CortexConfig instance, got {type(config)}"
    
    def test_config_has_version(self):
        """RED: Test that config has version attribute."""
        from src.config import config
        assert hasattr(config, 'version'), "config should have version attribute"
        assert config.version.startswith('4.'), \
            f"Expected version 4.x, got {config.version}"


class TestConfigBrainPathProperty:
    """Test that config.brain_path property works correctly."""
    
    def test_brain_path_exists(self):
        """RED: Test that config has brain_path attribute."""
        from src.config import config
        assert hasattr(config, 'brain_path'), \
            "config should have brain_path property"
    
    def test_brain_path_returns_path_object(self):
        """RED: Test that brain_path returns Path instance."""
        from src.config import config
        brain_path = config.brain_path
        assert isinstance(brain_path, Path), \
            f"brain_path should be Path instance, got {type(brain_path)}"
    
    def test_brain_path_points_to_cortex_brain(self):
        """RED: Test that brain_path points to cortex-brain directory."""
        from src.config import config
        brain_path = config.brain_path
        assert brain_path.name == 'cortex-brain', \
            f"brain_path should point to cortex-brain, got {brain_path.name}"
    
    def test_brain_path_is_absolute(self):
        """RED: Test that brain_path returns absolute path."""
        from src.config import config
        brain_path = config.brain_path
        assert brain_path.is_absolute(), \
            f"brain_path should be absolute, got {brain_path}"


class TestConfigEnsurePathsExist:
    """Test that config.ensure_paths_exist() creates required directories."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        temp_dir = tempfile.mkdtemp(prefix='cortex_test_')
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        yield Path(temp_dir)
        os.chdir(original_cwd)
        shutil.rmtree(temp_dir)
    
    def test_ensure_paths_exist_method_exists(self):
        """RED: Test that config has ensure_paths_exist method."""
        from src.config import config
        assert hasattr(config, 'ensure_paths_exist'), \
            "config should have ensure_paths_exist method"
        assert callable(config.ensure_paths_exist), \
            "ensure_paths_exist should be callable"
    
    def test_ensure_paths_creates_tier_directories(self, temp_workspace):
        """RED: Test that ensure_paths_exist creates tier0-3 directories."""
        from src.config import config
        
        # Call ensure_paths_exist
        config.ensure_paths_exist()
        
        # Verify tier directories created
        brain_path = temp_workspace / 'cortex-brain'
        assert (brain_path / 'tier0').exists(), "tier0 directory should be created"
        assert (brain_path / 'tier1').exists(), "tier1 directory should be created"
        assert (brain_path / 'tier2').exists(), "tier2 directory should be created"
        assert (brain_path / 'tier3').exists(), "tier3 directory should be created"
    
    def test_ensure_paths_creates_corpus_callosum(self, temp_workspace):
        """RED: Test that ensure_paths_exist creates corpus-callosum directory."""
        from src.config import config
        
        config.ensure_paths_exist()
        
        brain_path = temp_workspace / 'cortex-brain'
        assert (brain_path / 'corpus-callosum').exists(), \
            "corpus-callosum directory should be created"
    
    def test_ensure_paths_creates_logs_directory(self, temp_workspace):
        """RED: Test that ensure_paths_exist creates logs directory."""
        from src.config import config
        
        config.ensure_paths_exist()
        
        assert (temp_workspace / 'logs').exists(), \
            "logs directory should be created"
    
    def test_ensure_paths_creates_cache_directory(self, temp_workspace):
        """RED: Test that ensure_paths_exist creates cache directory."""
        from src.config import config
        
        config.ensure_paths_exist()
        
        assert (temp_workspace / '.cortex' / 'cache').exists(), \
            "cache directory should be created"
    
    def test_ensure_paths_is_idempotent(self, temp_workspace):
        """RED: Test that calling ensure_paths_exist multiple times is safe."""
        from src.config import config
        
        # Call multiple times
        config.ensure_paths_exist()
        config.ensure_paths_exist()
        config.ensure_paths_exist()
        
        # Should not raise any errors
        brain_path = temp_workspace / 'cortex-brain'
        assert (brain_path / 'tier0').exists(), "tier0 should still exist"


class TestBackwardCompatibility:
    """Test backward compatibility with legacy code patterns."""
    
    def test_legacy_code_imports_work(self):
        """RED: Test that legacy import patterns work."""
        # Pattern 1: from src.config import config
        from src.config import config
        assert config is not None
        
        # Pattern 2: from src.config import ConfigManager
        from src.config import ConfigManager
        assert ConfigManager is not None
        
        # Pattern 3: from src.config import get_config
        from src.config import get_config
        assert callable(get_config)
    
    def test_config_used_by_cortex_entry(self):
        """RED: Test that CortexEntry can import and use config."""
        try:
            from src.entry_point.cortex_entry import CortexEntry
            # If import succeeds, config wiring is correct
            assert True
        except ImportError as e:
            pytest.fail(f"CortexEntry import failed: {e}")
    
    def test_config_used_in_multiple_files(self):
        """RED: Test that config can be imported in multiple modules simultaneously."""
        from src.config import config as config1
        from src.config import config as config2
        
        # Should be same singleton instance
        assert config1 is config2, \
            "config should be singleton (same instance across imports)"


# TDD Summary
"""
Phase 23 Test Coverage:

✅ Config Singleton Export (3 tests)
   - Import succeeds
   - Instance type correct
   - Version present

✅ brain_path Property (4 tests)
   - Property exists
   - Returns Path object
   - Points to cortex-brain
   - Returns absolute path

✅ ensure_paths_exist Method (6 tests)
   - Method exists and callable
   - Creates tier0-3 directories
   - Creates corpus-callosum
   - Creates logs directory
   - Creates cache directory
   - Idempotent (safe to call multiple times)

✅ Backward Compatibility (3 tests)
   - Legacy imports work
   - CortexEntry uses config
   - Singleton across imports

TOTAL: 16 tests
EXPECTED: ALL RED (functions not yet implemented)
NEXT: Implement fixes to make tests GREEN
"""
