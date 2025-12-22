"""
Unit Tests for ManifestLoader
Tests YAML parsing, cross-reference resolution, and backward compatibility

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Created: 2025-12-22 (Week 15 Day 4)
Version: 1.0.0
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open
from src.utils.manifest_loader import ManifestLoader, ManifestMigrationAdapter


@pytest.fixture
def cortex_root(tmp_path):
    """Create temporary CORTEX directory structure."""
    manifest_dir = tmp_path / "cortex-brain" / "manifests"
    manifest_dir.mkdir(parents=True)
    
    # Create core manifest
    core_manifest = {
        "schema_version": "2.0",
        "manifest_type": "core",
        "last_updated": "2025-12-22T00:00:00Z",
        "orchestrators": {
            "test_orchestrator": {
                "version": "1.0.0",
                "status": "active",
                "category": "testing",
                "description": "Test orchestrator",
                "config_overrides": {
                    "namespace": "config://test",
                    "sections": ["test.section1", "test.section2"]
                },
                "integrations": ["integration://test_integration"]
            },
            "inactive_orchestrator": {
                "version": "0.1.0",
                "status": "deprecated",
                "category": "testing"
            }
        }
    }
    
    # Create config manifest
    config_manifest = {
        "schema_version": "2.0",
        "manifest_type": "config",
        "last_updated": "2025-12-22T00:00:00Z",
        "defaults": {
            "timeout": 30,
            "retry": 3
        },
        "categories": {
            "test": {
                "section1": {
                    "param1": "value1",
                    "param2": 42
                },
                "section2": {
                    "param3": True
                }
            }
        }
    }
    
    # Create integration manifest
    integration_manifest = {
        "schema_version": "2.0",
        "manifest_type": "integration",
        "last_updated": "2025-12-22T00:00:00Z",
        "integrations": {
            "test_integration": {
                "category": "testing",
                "adapter": {
                    "class_name": "TestAdapter",
                    "module": "test.adapters"
                },
                "endpoints": {
                    "api": "https://api.test.com"
                }
            }
        }
    }
    
    # Write manifests
    with open(manifest_dir / "core-manifest.yaml", 'w') as f:
        yaml.dump(core_manifest, f)
    
    with open(manifest_dir / "config-manifest.yaml", 'w') as f:
        yaml.dump(config_manifest, f)
    
    with open(manifest_dir / "integration-manifest.yaml", 'w') as f:
        yaml.dump(integration_manifest, f)
    
    return str(tmp_path)


# ──────────────────────────────────────────────────────────────
# Initialization Tests
# ──────────────────────────────────────────────────────────────

class TestManifestLoaderInitialization:
    """Test ManifestLoader initialization."""
    
    def test_init_with_valid_cortex_root(self, cortex_root):
        """Test initialization with valid CORTEX root."""
        loader = ManifestLoader(cortex_root)
        assert loader.cortex_root == Path(cortex_root)
        assert loader.manifest_dir.exists()
    
    def test_init_with_invalid_cortex_root(self, tmp_path):
        """Test initialization with invalid CORTEX root."""
        with pytest.raises(FileNotFoundError):
            ManifestLoader(str(tmp_path / "nonexistent"))
    
    def test_lazy_loading_not_loaded_initially(self, cortex_root):
        """Test that manifests are not loaded on initialization."""
        loader = ManifestLoader(cortex_root)
        assert loader._core_manifest is None
        assert loader._config_manifest is None
        assert loader._integration_manifest is None


# ──────────────────────────────────────────────────────────────
# YAML Loading Tests
# ──────────────────────────────────────────────────────────────

class TestYAMLLoading:
    """Test YAML manifest loading."""
    
    def test_load_core_manifest(self, cortex_root):
        """Test loading CoreManifest."""
        loader = ManifestLoader(cortex_root)
        core = loader.core_manifest
        
        assert core is not None
        assert core["schema_version"] == "2.0"
        assert core["manifest_type"] == "core"
        assert "orchestrators" in core
    
    def test_load_config_manifest(self, cortex_root):
        """Test loading ConfigManifest."""
        loader = ManifestLoader(cortex_root)
        config = loader.config_manifest
        
        assert config is not None
        assert config["schema_version"] == "2.0"
        assert config["manifest_type"] == "config"
        assert "categories" in config
    
    def test_load_integration_manifest(self, cortex_root):
        """Test loading IntegrationManifest."""
        loader = ManifestLoader(cortex_root)
        integration = loader.integration_manifest
        
        assert integration is not None
        assert integration["schema_version"] == "2.0"
        assert integration["manifest_type"] == "integration"
        assert "integrations" in integration
    
    def test_lazy_loading_caching(self, cortex_root):
        """Test that manifests are cached after first load."""
        loader = ManifestLoader(cortex_root)
        
        # First access
        core1 = loader.core_manifest
        assert loader._core_manifest is not None
        
        # Second access (should use cache)
        core2 = loader.core_manifest
        assert core1 is core2  # Same object reference
    
    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML."""
        manifest_dir = tmp_path / "cortex-brain" / "manifests"
        manifest_dir.mkdir(parents=True)
        
        # Create invalid YAML
        with open(manifest_dir / "core-manifest.yaml", 'w') as f:
            f.write("invalid: yaml: content: [")
        
        loader = ManifestLoader(str(tmp_path))
        
        with pytest.raises(yaml.YAMLError):
            _ = loader.core_manifest


# ──────────────────────────────────────────────────────────────
# Orchestrator Operations Tests
# ──────────────────────────────────────────────────────────────

class TestOrchestratorOperations:
    """Test orchestrator-related operations."""
    
    def test_get_orchestrator(self, cortex_root):
        """Test getting orchestrator metadata."""
        loader = ManifestLoader(cortex_root)
        orch = loader.get_orchestrator("test_orchestrator")
        
        assert orch is not None
        assert orch["version"] == "1.0.0"
        assert orch["status"] == "active"
        assert orch["category"] == "testing"
    
    def test_get_nonexistent_orchestrator(self, cortex_root):
        """Test getting nonexistent orchestrator."""
        loader = ManifestLoader(cortex_root)
        orch = loader.get_orchestrator("nonexistent")
        
        assert orch is None
    
    def test_list_orchestrators_no_filter(self, cortex_root):
        """Test listing all orchestrators."""
        loader = ManifestLoader(cortex_root)
        orchestrators = loader.list_orchestrators()
        
        assert len(orchestrators) == 2
        assert "test_orchestrator" in orchestrators
        assert "inactive_orchestrator" in orchestrators
    
    def test_list_orchestrators_filter_by_status(self, cortex_root):
        """Test listing orchestrators filtered by status."""
        loader = ManifestLoader(cortex_root)
        orchestrators = loader.list_orchestrators(status="active")
        
        assert len(orchestrators) == 1
        assert "test_orchestrator" in orchestrators
    
    def test_list_orchestrators_filter_by_category(self, cortex_root):
        """Test listing orchestrators filtered by category."""
        loader = ManifestLoader(cortex_root)
        orchestrators = loader.list_orchestrators(category="testing")
        
        assert len(orchestrators) == 2


# ──────────────────────────────────────────────────────────────
# Config Operations Tests
# ──────────────────────────────────────────────────────────────

class TestConfigOperations:
    """Test configuration-related operations."""
    
    def test_get_config_section(self, cortex_root):
        """Test getting config section."""
        loader = ManifestLoader(cortex_root)
        section = loader.get_config_section("test.section1")
        
        assert section is not None
        assert section["param1"] == "value1"
        assert section["param2"] == 42
    
    def test_get_nested_config_section(self, cortex_root):
        """Test getting nested config section."""
        loader = ManifestLoader(cortex_root)
        section = loader.get_config_section("test.section2")
        
        assert section is not None
        assert section["param3"] is True
    
    def test_get_nonexistent_config_section(self, cortex_root):
        """Test getting nonexistent config section."""
        loader = ManifestLoader(cortex_root)
        section = loader.get_config_section("nonexistent.section")
        
        assert section is None
    
    def test_get_orchestrator_config(self, cortex_root):
        """Test getting merged orchestrator config."""
        loader = ManifestLoader(cortex_root)
        config = loader.get_orchestrator_config("test_orchestrator")
        
        assert config is not None
        assert "test.section1" in config
        assert "test.section2" in config


# ──────────────────────────────────────────────────────────────
# Integration Operations Tests
# ──────────────────────────────────────────────────────────────

class TestIntegrationOperations:
    """Test integration-related operations."""
    
    def test_get_integration(self, cortex_root):
        """Test getting integration config."""
        loader = ManifestLoader(cortex_root)
        integration = loader.get_integration("test_integration")
        
        assert integration is not None
        assert integration["category"] == "testing"
        assert integration["adapter"]["class_name"] == "TestAdapter"
    
    def test_get_nonexistent_integration(self, cortex_root):
        """Test getting nonexistent integration."""
        loader = ManifestLoader(cortex_root)
        integration = loader.get_integration("nonexistent")
        
        assert integration is None
    
    def test_list_integrations(self, cortex_root):
        """Test listing integrations."""
        loader = ManifestLoader(cortex_root)
        integrations = loader.list_integrations()
        
        assert len(integrations) == 1
        assert "test_integration" in integrations
    
    def test_list_integrations_filter_by_category(self, cortex_root):
        """Test listing integrations filtered by category."""
        loader = ManifestLoader(cortex_root)
        integrations = loader.list_integrations(category="testing")
        
        assert len(integrations) == 1


# ──────────────────────────────────────────────────────────────
# Cross-Reference Resolution Tests
# ──────────────────────────────────────────────────────────────

class TestCrossReferenceResolution:
    """Test cross-reference resolution."""
    
    def test_resolve_cross_references(self, cortex_root):
        """Test resolving all cross-references."""
        loader = ManifestLoader(cortex_root)
        resolved = loader.resolve_cross_references("test_orchestrator")
        
        assert resolved is not None
        assert "metadata" in resolved
        assert "config" in resolved
        assert "integrations" in resolved
    
    def test_resolve_config_sections(self, cortex_root):
        """Test config sections are resolved."""
        loader = ManifestLoader(cortex_root)
        resolved = loader.resolve_cross_references("test_orchestrator")
        
        config = resolved["config"]
        assert "test.section1" in config
        assert "test.section2" in config
        assert config["test.section1"]["param1"] == "value1"
    
    def test_resolve_integrations(self, cortex_root):
        """Test integrations are resolved."""
        loader = ManifestLoader(cortex_root)
        resolved = loader.resolve_cross_references("test_orchestrator")
        
        integrations = resolved["integrations"]
        assert "test_integration" in integrations
        assert integrations["test_integration"]["adapter"]["class_name"] == "TestAdapter"
    
    def test_resolve_cross_references_caching(self, cortex_root):
        """Test cross-reference results are cached."""
        loader = ManifestLoader(cortex_root)
        
        # First resolution
        resolved1 = loader.resolve_cross_references("test_orchestrator")
        assert "test_orchestrator" in loader._resolved_cache
        
        # Second resolution (should use cache)
        resolved2 = loader.resolve_cross_references("test_orchestrator")
        assert resolved1 is not resolved2  # Different objects (deepcopy)
        assert resolved1 == resolved2  # But same content
    
    def test_resolve_nonexistent_orchestrator(self, cortex_root):
        """Test resolving nonexistent orchestrator."""
        loader = ManifestLoader(cortex_root)
        resolved = loader.resolve_cross_references("nonexistent")
        
        assert resolved == {}


# ──────────────────────────────────────────────────────────────
# Utility Methods Tests
# ──────────────────────────────────────────────────────────────

class TestUtilityMethods:
    """Test utility methods."""
    
    def test_clear_cache(self, cortex_root):
        """Test clearing cache."""
        loader = ManifestLoader(cortex_root)
        
        # Load manifests
        _ = loader.core_manifest
        _ = loader.config_manifest
        _ = loader.integration_manifest
        _ = loader.resolve_cross_references("test_orchestrator")
        
        # Verify loaded
        assert loader._core_manifest is not None
        assert loader._config_manifest is not None
        assert loader._integration_manifest is not None
        assert len(loader._resolved_cache) > 0
        
        # Clear cache
        loader.clear_cache()
        
        # Verify cleared
        assert loader._core_manifest is None
        assert loader._config_manifest is None
        assert loader._integration_manifest is None
        assert len(loader._resolved_cache) == 0
    
    def test_reload_manifests(self, cortex_root):
        """Test reloading manifests."""
        loader = ManifestLoader(cortex_root)
        
        # Load manifests
        core1 = loader.core_manifest
        
        # Reload
        loader.reload_manifests()
        
        # Should have new instance
        core2 = loader.core_manifest
        assert core1 is not core2  # Different objects
        assert core1 == core2  # But same content
    
    def test_get_manifest_stats(self, cortex_root):
        """Test getting manifest statistics."""
        loader = ManifestLoader(cortex_root)
        
        # Load manifests
        _ = loader.core_manifest
        _ = loader.config_manifest
        _ = loader.integration_manifest
        
        stats = loader.get_manifest_stats()
        
        assert stats["core_manifest"]["loaded"] is True
        assert stats["core_manifest"]["orchestrators_count"] == 2
        assert stats["config_manifest"]["loaded"] is True
        assert stats["config_manifest"]["categories_count"] == 1
        assert stats["integration_manifest"]["loaded"] is True
        assert stats["integration_manifest"]["integrations_count"] == 1
    
    def test_deep_merge(self, cortex_root):
        """Test deep merge utility."""
        loader = ManifestLoader(cortex_root)
        
        target = {
            "a": 1,
            "b": {"c": 2, "d": 3},
            "e": [1, 2]
        }
        
        source = {
            "b": {"c": 99, "f": 4},
            "g": 5
        }
        
        loader._deep_merge(target, source)
        
        assert target["a"] == 1  # Unchanged
        assert target["b"]["c"] == 99  # Overwritten
        assert target["b"]["d"] == 3  # Preserved
        assert target["b"]["f"] == 4  # Added
        assert target["g"] == 5  # Added


# ──────────────────────────────────────────────────────────────
# Backward Compatibility Tests
# ──────────────────────────────────────────────────────────────

class TestManifestMigrationAdapter:
    """Test backward compatibility adapter."""
    
    def test_adapter_initialization(self, cortex_root):
        """Test adapter initialization."""
        adapter = ManifestMigrationAdapter(cortex_root)
        
        assert adapter.cortex_root == Path(cortex_root)
        assert adapter.new_loader is not None
    
    def test_load_old_format_not_found(self, cortex_root):
        """Test loading old format when file doesn't exist."""
        adapter = ManifestMigrationAdapter(cortex_root)
        old = adapter.load_old_format("test_orchestrator")
        
        assert old is None
    
    def test_load_new_format(self, cortex_root):
        """Test loading new format."""
        adapter = ManifestMigrationAdapter(cortex_root)
        new = adapter.load_new_format("test_orchestrator")
        
        assert new is not None
        assert "metadata" in new
        assert "config" in new
        assert "integrations" in new
    
    def test_validate_equivalence_no_old_format(self, cortex_root):
        """Test equivalence validation when old format doesn't exist."""
        adapter = ManifestMigrationAdapter(cortex_root)
        is_equivalent = adapter.validate_equivalence("test_orchestrator")
        
        assert is_equivalent is False
    
    def test_migrate_orchestrator(self, cortex_root):
        """Test migration report generation."""
        adapter = ManifestMigrationAdapter(cortex_root)
        report = adapter.migrate_orchestrator("test_orchestrator")
        
        assert report["orchestrator_id"] == "test_orchestrator"
        assert "timestamp" in report
        assert "old_format_exists" in report
        assert "new_format_exists" in report
        assert report["new_format_exists"] is True
        assert "is_equivalent" in report
        assert "recommendation" in report


# ──────────────────────────────────────────────────────────────
# Edge Cases and Error Handling
# ──────────────────────────────────────────────────────────────

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_orchestrators(self, tmp_path):
        """Test handling empty orchestrators section."""
        manifest_dir = tmp_path / "cortex-brain" / "manifests"
        manifest_dir.mkdir(parents=True)
        
        core_manifest = {
            "schema_version": "2.0",
            "manifest_type": "core",
            "orchestrators": {}
        }
        
        with open(manifest_dir / "core-manifest.yaml", 'w') as f:
            yaml.dump(core_manifest, f)
        
        # Create minimal other manifests
        for name in ["config-manifest.yaml", "integration-manifest.yaml"]:
            with open(manifest_dir / name, 'w') as f:
                yaml.dump({"schema_version": "2.0"}, f)
        
        loader = ManifestLoader(str(tmp_path))
        orchestrators = loader.list_orchestrators()
        
        assert len(orchestrators) == 0
    
    def test_missing_config_sections(self, cortex_root):
        """Test handling missing config sections."""
        loader = ManifestLoader(cortex_root)
        config = loader.get_orchestrator_config("inactive_orchestrator")
        
        # Should still return config (from defaults)
        assert config is not None
    
    def test_invalid_section_path(self, cortex_root):
        """Test handling invalid section path."""
        loader = ManifestLoader(cortex_root)
        section = loader.get_config_section("invalid..path")
        
        assert section is None


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
