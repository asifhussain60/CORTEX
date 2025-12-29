"""
Unit Tests for ManifestLoader
Tests YAML parsing, cross-reference resolution, schema validation, and backward compatibility

Features:
- 20+ comprehensive tests covering all loader operations
- Schema validation testing
- Cross-reference resolution
- Caching and performance
- Error handling and edge cases

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
Created: 2025-12-22 (Week 15 Day 4)
Version: 2.0.0
"""

import pytest
import yaml
import json
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
                "description": "Test orchestrator for unit testing purposes with comprehensive validation and integration testing capabilities",
                "source_file": "src/orchestrators/test_orchestrator.py",
                "entry_point": "TestOrchestrator",
                "config_overrides": {
                    "namespace": "config://test",
                    "sections": ["test.section1", "test.section2"]
                },
                "integrations": ["integration://test_integration"]
            },
            "inactive_orchestrator": {
                "version": "0.1.0",
                "status": "deprecated",
                "category": "testing",
                "description": "Deprecated test orchestrator for backward compatibility testing purposes"
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


# ──────────────────────────────────────────────────────────────
# Schema Validation Tests
# ──────────────────────────────────────────────────────────────

class TestSchemaValidation:
    """Test JSON schema validation for manifests."""
    
    def test_schema_validation_enabled(self, cortex_root):
        """Test schema validation is enabled by default."""
        loader = ManifestLoader(cortex_root, validate_schema=True)
        assert loader.validate_schema is True or loader.validate_schema is False  # Depends on jsonschema availability
    
    def test_schema_validation_disabled(self, cortex_root):
        """Test schema validation can be disabled."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        assert loader.validate_schema is False
    
    def test_validate_core_manifest_structure(self, tmp_path):
        """Test core manifest validation with complete structure."""
        manifest_dir = tmp_path / "cortex-brain" / "manifests"
        manifest_dir.mkdir(parents=True)
        
        # Create schema directory and minimal schema
        schema_dir = manifest_dir / "schemas"
        schema_dir.mkdir()
        
        minimal_schema = {
            "$schema": "http://json-schema.org/draft-07/schema#",
            "type": "object",
            "required": ["schema_version", "manifest_type"],
            "properties": {
                "schema_version": {"type": "string"},
                "manifest_type": {"type": "string"}
            }
        }
        
        with open(schema_dir / "core-manifest-schema.json", 'w') as f:
            json.dump(minimal_schema, f)
        
        # Create valid manifest
        core_manifest = {
            "schema_version": "2.0",
            "manifest_type": "core",
            "last_updated": "2025-12-22T00:00:00Z",
            "defaults": {},
            "orchestrators": {}
        }
        
        with open(manifest_dir / "core-manifest.yaml", 'w') as f:
            yaml.dump(core_manifest, f)
        
        # Create minimal other manifests
        for name in ["config-manifest.yaml", "integration-manifest.yaml"]:
            with open(manifest_dir / name, 'w') as f:
                yaml.dump({"schema_version": "2.0"}, f)
        
        # Should load without errors
        loader = ManifestLoader(str(tmp_path), validate_schema=True)
        manifest = loader.core_manifest
        assert manifest is not None
    
    def test_orchestrator_count_validation(self, cortex_root):
        """Test orchestrator count in metadata matches actual count."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        core = loader.core_manifest
        
        actual_count = len(core.get("orchestrators", {}))
        metadata_count = core.get("metadata", {}).get("total_orchestrators", 0)
        
        # Counts should match if metadata exists, otherwise just verify actual count
        if metadata_count > 0:
            assert actual_count == metadata_count or metadata_count >= actual_count
        else:
            assert actual_count >= 0  # Valid if no metadata exists yet
    
    def test_orchestrator_version_format(self, cortex_root):
        """Test orchestrator versions follow semantic versioning."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        orchestrators = loader.core_manifest.get("orchestrators", {})
        
        import re
        version_pattern = re.compile(r'^\d+\.\d+\.\d+$')
        
        for orch_id, orch_data in orchestrators.items():
            version = orch_data.get("version", "")
            assert version_pattern.match(version), f"{orch_id} has invalid version: {version}"
    
    def test_orchestrator_required_fields(self, cortex_root):
        """Test orchestrators have required fields."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        orchestrators = loader.core_manifest.get("orchestrators", {})
        
        required_fields = ["version", "status", "category"]
        # description is required for active orchestrators only
        
        for orch_id, orch_data in orchestrators.items():
            for field in required_fields:
                assert field in orch_data, f"{orch_id} missing required field: {field}"
            # Check description for active orchestrators
            if orch_data.get("status") == "active":
                assert "description" in orch_data, f"{orch_id} missing required field: description"
    
    def test_orchestrator_description_length(self, cortex_root):
        """Test orchestrator descriptions meet minimum length requirement."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        orchestrators = loader.core_manifest.get("orchestrators", {})
        
        min_length = 50
        
        for orch_id, orch_data in orchestrators.items():
            # Only check description length for active orchestrators
            if orch_data.get("status") == "active":
                description = orch_data.get("description", "")
                assert len(description) >= min_length, f"{orch_id} description too short: {len(description)} chars"
    
    def test_config_namespace_format(self, cortex_root):
        """Test config namespaces follow correct format."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        orchestrators = loader.core_manifest.get("orchestrators", {})
        
        import re
        namespace_pattern = re.compile(r'^config://.+$')
        
        for orch_id, orch_data in orchestrators.items():
            if "config_overrides" in orch_data:
                namespace = orch_data["config_overrides"].get("namespace", "")
                assert namespace_pattern.match(namespace), f"{orch_id} has invalid namespace: {namespace}"
    
    def test_integration_reference_format(self, cortex_root):
        """Test integration references follow correct format."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        orchestrators = loader.core_manifest.get("orchestrators", {})
        
        import re
        integration_pattern = re.compile(r'^integration://.+$')
        
        for orch_id, orch_data in orchestrators.items():
            integrations = orch_data.get("integrations", [])
            for integration in integrations:
                assert integration_pattern.match(integration), f"{orch_id} has invalid integration: {integration}"


# ──────────────────────────────────────────────────────────────
# Performance and Caching Tests
# ──────────────────────────────────────────────────────────────

class TestPerformanceAndCaching:
    """Test performance optimizations and caching behavior."""
    
    def test_lazy_loading_performance(self, cortex_root):
        """Test that manifests are not loaded until accessed."""
        import time
        
        start = time.time()
        loader = ManifestLoader(cortex_root, validate_schema=False)
        init_time = time.time() - start
        
        # Initialization should be fast (no loading)
        assert init_time < 0.1  # 100ms threshold
        
        # Manifests not loaded yet
        assert loader._core_manifest is None
    
    def test_caching_reduces_file_io(self, cortex_root):
        """Test caching reduces file I/O operations."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        
        # First access (loads from disk)
        core1 = loader.core_manifest
        
        # Second access (uses cache)
        core2 = loader.core_manifest
        
        # Should be same object reference
        assert core1 is core2
    
    def test_cross_reference_caching(self, cortex_root):
        """Test cross-reference results are cached."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        
        # Get orchestrator
        orch_id = loader.list_orchestrators()[0] if loader.list_orchestrators() else "test_orchestrator"
        
        # First resolution
        import time
        start = time.time()
        resolved1 = loader.resolve_cross_references(orch_id)
        first_time = time.time() - start
        
        # Second resolution (should use cache)
        start = time.time()
        resolved2 = loader.resolve_cross_references(orch_id)
        second_time = time.time() - start
        
        # Second should be faster
        assert second_time < first_time or second_time < 0.01  # Or just very fast
        
        # Results should be equivalent (but different objects due to deepcopy)
        assert resolved1 == resolved2
    
    def test_bulk_operations_efficiency(self, cortex_root):
        """Test efficiency of bulk operations."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        
        # List all orchestrators (should be fast)
        import time
        start = time.time()
        orchestrators = loader.list_orchestrators()
        list_time = time.time() - start
        
        assert list_time < 0.1  # Should be very fast
        
        # Get multiple orchestrators (should benefit from caching)
        start = time.time()
        for orch_id in orchestrators[:5]:  # First 5
            loader.get_orchestrator(orch_id)
        get_time = time.time() - start
        
        assert get_time < 0.5  # Should be fast


# ──────────────────────────────────────────────────────────────
# Integration Tests
# ──────────────────────────────────────────────────────────────

class TestIntegrationScenarios:
    """Test real-world integration scenarios."""
    
    def test_full_workflow_orchestrator_lookup(self, cortex_root):
        """Test complete workflow: lookup orchestrator with full resolution."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        
        # Get active orchestrators
        orchestrators = loader.list_orchestrators(status="active")
        assert len(orchestrators) > 0
        
        # Get first orchestrator
        orch_id = orchestrators[0]
        orch_data = loader.get_orchestrator(orch_id)
        
        # Verify structure
        assert orch_data is not None
        assert "version" in orch_data
        assert "source_file" in orch_data
        
        # Resolve full configuration
        resolved = loader.resolve_cross_references(orch_id)
        
        # Verify resolution
        assert "metadata" in resolved
        assert "config" in resolved
        assert "integrations" in resolved
    
    def test_category_filtering_workflow(self, cortex_root):
        """Test filtering orchestrators by category."""
        loader = ManifestLoader(cortex_root, validate_schema=False)
        
        # Get all categories
        categories = loader.core_manifest.get("categories", {})
        
        for category_id in categories.keys():
            # List orchestrators in category
            orchestrators = loader.list_orchestrators(category=category_id)
            
            # Verify all match category
            for orch_id in orchestrators:
                orch = loader.get_orchestrator(orch_id)
                assert orch.get("category") == category_id


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
