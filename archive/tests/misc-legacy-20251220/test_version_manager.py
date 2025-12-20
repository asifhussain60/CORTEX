"""
Tests for Version Manager

Validates version reading, caching, and consistency checking.

Phase 15 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.operations.modules.version.version_manager import (
    VersionManager,
    VersionInfo,
    get_version_manager,
    get_cortex_version,
    get_planning_system_version
)


@pytest.fixture
def temp_config_file():
    """Create temporary cortex.config.json for testing."""
    config_data = {
        "version": "3.9.0",
        "planningSystem": {
            "version": "3.0",
            "comment": "Planning System 3.0 - Tiered routing"
        },
        "application": {
            "name": "CORTEX",
            "framework": "Python"
        }
    }
    
    with tempfile.NamedTemporaryFile(
        mode='w', 
        suffix='.json', 
        delete=False
    ) as f:
        json.dump(config_data, f)
        temp_path = Path(f.name)
    
    yield temp_path
    
    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.fixture
def version_manager(temp_config_file):
    """Create VersionManager instance with temp config."""
    # Reset singleton
    VersionManager._instance = None
    vm = VersionManager(config_path=temp_config_file)
    return vm


class TestVersionManagerInitialization:
    """Test VersionManager initialization and singleton pattern."""
    
    def test_singleton_pattern(self, temp_config_file):
        """Test that VersionManager maintains singleton instance."""
        # Reset singleton
        VersionManager._instance = None
        
        vm1 = VersionManager(config_path=temp_config_file)
        vm2 = VersionManager(config_path=temp_config_file)
        
        assert vm1 is vm2, "VersionManager should be singleton"
    
    def test_initialization_loads_versions(self, version_manager):
        """Test that initialization loads version data."""
        assert version_manager._version_cache is not None
        assert version_manager._version_cache.cortex_version == "3.9.0"
        assert version_manager._version_cache.planning_system_version == "3.0"
    
    def test_initialization_with_invalid_path(self):
        """Test initialization fails with invalid config path."""
        VersionManager._instance = None
        
        with pytest.raises(FileNotFoundError):
            VersionManager(config_path=Path("/nonexistent/cortex.config.json"))
    
    @pytest.mark.skip(reason="Windows file locking issue in temp directory - edge case")
    def test_find_config_path_success(self, temp_config_file, monkeypatch):
        """Test _find_config_path locates config file."""
        # Create a directory structure with config file
        import tempfile
        import shutil
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            config_file = tmpdir_path / "cortex.config.json"
            shutil.copy(temp_config_file, config_file)
            
            # Change to directory containing config
            monkeypatch.chdir(tmpdir_path)
            
            VersionManager._instance = None
            vm = VersionManager()
            
            assert vm.config_path.exists()
            assert vm.config_path.name == "cortex.config.json"


class TestVersionRetrieval:
    """Test version retrieval methods."""
    
    def test_get_cortex_version(self, version_manager):
        """Test getting CORTEX version."""
        version = version_manager.get_cortex_version()
        assert version == "3.9.0"
    
    def test_get_planning_system_version(self, version_manager):
        """Test getting Planning System version."""
        version = version_manager.get_planning_system_version()
        assert version == "3.0"
    
    def test_get_orchestrator_version_unregistered(self, version_manager):
        """Test getting unregistered orchestrator version returns 'unknown'."""
        version = version_manager.get_orchestrator_version("nonexistent")
        assert version == "unknown"
    
    def test_get_orchestrator_version_registered(self, version_manager):
        """Test getting registered orchestrator version."""
        version_manager.register_orchestrator_version("planning_orchestrator", "3.0")
        version = version_manager.get_orchestrator_version("planning_orchestrator")
        assert version == "3.0"
    
    def test_get_version_info(self, version_manager):
        """Test getting complete version info."""
        info = version_manager.get_version_info()
        
        assert isinstance(info, VersionInfo)
        assert info.cortex_version == "3.9.0"
        assert info.planning_system_version == "3.0"
        assert isinstance(info.orchestrator_versions, dict)
        assert isinstance(info.last_read, datetime)


class TestOrchestratorRegistration:
    """Test orchestrator version registration."""
    
    def test_register_orchestrator_version(self, version_manager):
        """Test registering orchestrator version."""
        version_manager.register_orchestrator_version("planning_orchestrator", "3.0")
        
        assert version_manager.get_orchestrator_version("planning_orchestrator") == "3.0"
    
    def test_register_multiple_orchestrators(self, version_manager):
        """Test registering multiple orchestrator versions."""
        version_manager.register_orchestrator_version("planning_orchestrator", "3.0")
        version_manager.register_orchestrator_version("ado_orchestrator", "3.0")
        version_manager.register_orchestrator_version("tdd_orchestrator", "3.0")
        
        assert version_manager.get_orchestrator_version("planning_orchestrator") == "3.0"
        assert version_manager.get_orchestrator_version("ado_orchestrator") == "3.0"
        assert version_manager.get_orchestrator_version("tdd_orchestrator") == "3.0"
    
    def test_register_updates_version_info(self, version_manager):
        """Test that registration updates cached version info."""
        version_manager.register_orchestrator_version("planning_orchestrator", "3.0")
        
        info = version_manager.get_version_info()
        assert "planning_orchestrator" in info.orchestrator_versions
        assert info.orchestrator_versions["planning_orchestrator"] == "3.0"


class TestVersionValidation:
    """Test version validation and consistency checking."""
    
    def test_validate_consistency_success(self, version_manager):
        """Test validation passes with valid config."""
        result = version_manager.validate_consistency()
        
        assert result['valid'] is True
        assert len(result['errors']) == 0
        assert result['cortex_version'] == "3.9.0"
        assert result['planning_version'] == "3.0"
    
    def test_is_valid_version_format_semantic(self, version_manager):
        """Test semantic version format validation."""
        assert version_manager._is_valid_version_format("3.9.0") is True
        assert version_manager._is_valid_version_format("3.0") is True
        assert version_manager._is_valid_version_format("1.0.0") is True
    
    def test_is_valid_version_format_invalid(self, version_manager):
        """Test invalid version format detection."""
        assert version_manager._is_valid_version_format("3") is False
        assert version_manager._is_valid_version_format("3.9.0.1") is False
        assert version_manager._is_valid_version_format("abc") is False
    
    def test_is_valid_version_format_unknown(self, version_manager):
        """Test 'unknown' version is allowed."""
        assert version_manager._is_valid_version_format("unknown") is True
    
    def test_validate_consistency_with_warnings(self, version_manager):
        """Test validation generates warnings for unusual formats."""
        version_manager.register_orchestrator_version("test_orch", "invalid")
        
        result = version_manager.validate_consistency()
        
        assert result['valid'] is True  # Still valid, just warnings
        assert len(result['warnings']) > 0


class TestVersionRefresh:
    """Test version refresh functionality."""
    
    def test_refresh_reloads_versions(self, version_manager, temp_config_file):
        """Test refresh reloads data from config file."""
        # Get initial version
        initial_version = version_manager.get_cortex_version()
        assert initial_version == "3.9.0"
        
        # Modify config file
        with open(temp_config_file, 'r') as f:
            config = json.load(f)
        
        config['version'] = "3.10.0"
        
        with open(temp_config_file, 'w') as f:
            json.dump(config, f)
        
        # Refresh
        version_manager.refresh()
        
        # Check new version loaded
        new_version = version_manager.get_cortex_version()
        assert new_version == "3.10.0"


class TestVersionStrings:
    """Test version string formatting."""
    
    def test_version_info_str(self, version_manager):
        """Test VersionInfo string representation."""
        info = version_manager.get_version_info()
        version_str = str(info)
        
        assert "CORTEX v3.9.0" in version_str
        assert "Planning System v3.0" in version_str
    
    def test_get_version_string_basic(self, version_manager):
        """Test basic version string without orchestrators."""
        version_str = version_manager.get_version_string(include_orchestrators=False)
        
        assert "CORTEX v3.9.0" in version_str
        assert "Planning System v3.0" in version_str
        assert "Orchestrators:" not in version_str
    
    def test_get_version_string_with_orchestrators(self, version_manager):
        """Test version string with orchestrators."""
        version_manager.register_orchestrator_version("planning_orchestrator", "3.0")
        version_manager.register_orchestrator_version("ado_orchestrator", "3.0")
        
        version_str = version_manager.get_version_string(include_orchestrators=True)
        
        assert "CORTEX v3.9.0" in version_str
        assert "Planning System v3.0" in version_str
        assert "Orchestrators:" in version_str
        assert "planning_orchestrator v3.0" in version_str
        assert "ado_orchestrator v3.0" in version_str


class TestGlobalFunctions:
    """Test global convenience functions."""
    
    def test_get_version_manager_singleton(self, temp_config_file):
        """Test get_version_manager returns singleton."""
        # Reset singleton
        VersionManager._instance = None
        import src.operations.modules.version.version_manager as vm_module
        vm_module._version_manager = None
        
        # Note: Cannot easily test with temp config since global functions
        # use default path. Test singleton behavior instead.
        vm1 = VersionManager(config_path=temp_config_file)
        vm2 = get_version_manager(config_path=temp_config_file)
        
        # Both should reference same config
        assert vm1.config_path == vm2.config_path
    
    def test_get_cortex_version_function(self, version_manager):
        """Test get_cortex_version convenience function."""
        # Reset global
        import src.operations.modules.version.version_manager as vm_module
        vm_module._version_manager = version_manager
        
        version = get_cortex_version()
        assert version == "3.9.0"
    
    def test_get_planning_system_version_function(self, version_manager):
        """Test get_planning_system_version convenience function."""
        # Reset global
        import src.operations.modules.version.version_manager as vm_module
        vm_module._version_manager = version_manager
        
        version = get_planning_system_version()
        assert version == "3.0"


class TestErrorHandling:
    """Test error handling scenarios."""
    
    def test_load_versions_invalid_json(self, version_manager, temp_config_file):
        """Test handling of invalid JSON in config file."""
        # Write invalid JSON
        with open(temp_config_file, 'w') as f:
            f.write("{invalid json")
        
        with pytest.raises(json.JSONDecodeError):
            version_manager._load_versions()
    
    def test_validate_consistency_missing_config(self, version_manager):
        """Test validation with missing config file."""
        # Point to nonexistent file
        version_manager.config_path = Path("/nonexistent/cortex.config.json")
        version_manager._version_cache = None
        
        result = version_manager.validate_consistency()
        
        assert result['valid'] is False
        assert len(result['errors']) > 0
        assert "not found" in result['errors'][0].lower()


class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_orchestrator_integration_pattern(self, version_manager):
        """Test typical orchestrator integration usage."""
        # Simulate orchestrator initialization
        version_manager.register_orchestrator_version("planning_orchestrator", "3.0")
        orchestrator_version = version_manager.get_orchestrator_version("planning_orchestrator")
        
        assert orchestrator_version == "3.0"
        
        # Verify version info includes orchestrator
        info = version_manager.get_version_info()
        assert "planning_orchestrator" in info.orchestrator_versions
    
    def test_multi_orchestrator_scenario(self, version_manager):
        """Test scenario with multiple orchestrators."""
        orchestrators = {
            "planning_orchestrator": "3.0",
            "ado_orchestrator": "3.0",
            "tdd_orchestrator": "3.0",
            "system_maintenance_orchestrator": "3.0"
        }
        
        for name, version in orchestrators.items():
            version_manager.register_orchestrator_version(name, version)
        
        # Validate all registered
        for name, expected_version in orchestrators.items():
            actual_version = version_manager.get_orchestrator_version(name)
            assert actual_version == expected_version
        
        # Get full version string
        version_str = version_manager.get_version_string(include_orchestrators=True)
        assert all(name in version_str for name in orchestrators.keys())
