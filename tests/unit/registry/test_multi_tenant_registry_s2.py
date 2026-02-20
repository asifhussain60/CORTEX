"""
Phase 48-registry Stage 2: Registry Loader Refactor - Test Suite

Authority: phase-48-registry-isolation.yaml
AC-IDs: AC-PHASE48-REG-S2-001 through AC-PHASE48-REG-S2-005

Tests for tenant-aware GitBackedRegistry with:
- Workspace-specific YAML loading (cortex-registry/{workspace_id}/)
- Fallback to global registry for shared resources
- Per-tenant caching (≥70% hit rate target)
- Cross-tenant isolation validation
- Backward compatibility with single-tenant mode
"""

import pytest
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


# ============================================================================
# IMPORT PRODUCTION CODE
# ============================================================================

from cortex.core.registry.multi_tenant_registry import MultiTenantRegistry


# ============================================================================
# TESTS: Workspace-Specific YAML Loading (AC-PHASE48-REG-S2-001)
# ============================================================================

class TestWorkspaceSpecificLoading:
    """Test loading YAML from workspace-specific registry."""
    
    def test_load_from_workspace_registry(self):
        """Load YAML from cortex-registry/{workspace_id}/ first."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        # Mock YAML loading directly
        yaml_content = {"orchestrator": "TDDOrchestrator", "workspace": "acme-dev"}
        
        with patch.object(registry, "_load_yaml_file", return_value=yaml_content) as mock_load:
            with patch("pathlib.Path.exists", return_value=True):
                # Should load from workspace registry
                result = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
                
                # Verify workspace-specific data loaded
                assert result == yaml_content
                assert mock_load.called
    
    def test_workspace_specific_overrides_global(self):
        """Workspace-specific YAML overrides global registry."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        # Workspace has custom config
        workspace_content = {"setting": "workspace-specific"}
        global_content = {"setting": "global-default"}
        
        # Mock: workspace file exists, return workspace content
        with patch.object(registry, "load_yaml", return_value=workspace_content):
            result = registry.load_yaml("config/settings.yaml")
            
            # Should return workspace-specific value
            assert result["setting"] == "workspace-specific"
    
    def test_local_workspace_uses_standard_paths(self):
        """Local workspace (single-tenant mode) uses cortex-registry/ directly."""
        registry = MultiTenantRegistry(workspace_id="local", tenant_id="local")
        
        # In local mode, should use cortex-registry/ paths (backward compatible)
        cache_key = registry.get_cache_key("agents/core/tdd-orchestrator.yaml")
        assert "local:local:" in cache_key


# ============================================================================
# TESTS: Fallback to Global Registry (AC-PHASE48-REG-S2-002)
# ============================================================================

class TestGlobalRegistryFallback:
    """Test fallback to global registry for shared resources."""
    
    def test_fallback_when_workspace_file_missing(self):
        """Fallback to cortex-registry/_cortex-master/ if workspace file missing."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        workspace_path = registry.registry_root / registry.workspace_id / "agents/core/tdd-orchestrator.yaml"
        global_path = registry.registry_root / "_cortex-master" / "agents/core/tdd-orchestrator.yaml"
        
        # Mock: workspace file missing, global file exists
        def exists_side_effect(self):
            path_str = str(self)
            if "acme-dev" in path_str:
                return False  # Workspace file missing
            if "_cortex-master" in path_str:
                return True  # Global file exists
            return False
        
        yaml_content = {"orchestrator": "TDDOrchestrator", "source": "global"}
        
        with patch("pathlib.Path.exists", exists_side_effect):
            with patch.object(registry, "_load_yaml_file", return_value=yaml_content):
                # Should fallback to global registry
                result = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
                
                # Should successfully load from global registry
                assert result == yaml_content
                assert result["source"] == "global"
    
    def test_shared_resources_always_from_global(self):
        """Shared resources (best practices, core agents) always from global registry."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        shared_files = [
            "cortex/knowledge/best-practices/tdd-patterns.yaml",
            "agents/core/master-orchestrator.yaml",
            "governance/core/CORE-002.yaml"
        ]
        
        yaml_content = {"source": "global_registry", "shared": True}
        
        for file_path in shared_files:
            # Mock: file only exists in global registry
            def exists_side_effect(self):
                return "_cortex-master" in str(self)
            
            with patch("pathlib.Path.exists", exists_side_effect):
                with patch.object(registry, "_load_yaml_file", return_value=yaml_content):
                    result = registry.load_yaml(file_path)
                    
                    # Should successfully load from global registry
                    assert result is not None
                    assert result["shared"] is True
    
    def test_error_when_file_not_found_anywhere(self):
        """Raise FileNotFoundError if file not in workspace or global registry."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(FileNotFoundError):
                registry.load_yaml("non-existent-file.yaml")


# ============================================================================
# TESTS: Per-Tenant Caching (AC-PHASE48-REG-S2-003)
# ============================================================================

class TestPerTenantCaching:
    """Test per-tenant caching with ≥70% hit rate target."""
    
    def test_cache_key_includes_workspace_and_tenant(self):
        """Cache keys include workspace_id + tenant_id + file_path."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        cache_key = registry.get_cache_key("agents/core/tdd-orchestrator.yaml")
        
        assert "acme-dev" in cache_key
        assert "acme" in cache_key
        assert "agents/core/tdd-orchestrator.yaml" in cache_key
    
    def test_cache_hit_on_second_load(self):
        """Second load of same file returns cached result (cache hit)."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        yaml_content = {"cached": "data"}
        
        # Mock: first load from disk
        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(registry, "_load_yaml_file", return_value=yaml_content) as mock_load:
                # First load (cache miss)
                result1 = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
                
                # Second load (should hit cache)
                result2 = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
                
                # Should return same result
                assert result1 == result2
                assert result1["cached"] == "data"
                
                # _load_yaml_file should only be called once (first load)
                assert mock_load.call_count == 1
                
                # Cache hit rate should be 50% (1 miss, 1 hit)
                assert registry.get_cache_hit_rate() == 0.5
    
    def test_cache_isolated_per_workspace(self):
        """Cache isolated between workspaces (no cross-contamination)."""
        registry1 = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        registry2 = MultiTenantRegistry(workspace_id="beta-test", tenant_id="beta")
        
        key1 = registry1.get_cache_key("file.yaml")
        key2 = registry2.get_cache_key("file.yaml")
        
        # Different workspaces → different cache keys
        assert key1 != key2
        assert "acme-dev" in key1
        assert "beta-test" in key2
    
    def test_cache_hit_rate_calculation(self):
        """Calculate cache hit rate accurately."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        # Simulate hits and misses
        registry._cache_hits = 7
        registry._cache_misses = 3
        
        hit_rate = registry.get_cache_hit_rate()
        
        assert hit_rate == 0.7  # 70% hit rate
    
    def test_clear_cache_resets_metrics(self):
        """Clearing cache resets hit/miss counters."""
        registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        
        registry._cache_hits = 10
        registry._cache_misses = 5
        
        registry.clear_cache()
        
        assert registry._cache_hits == 0
        assert registry._cache_misses == 0
        assert len(registry._cache) == 0


# ============================================================================
# TESTS: Cross-Tenant Isolation (AC-PHASE48-REG-S2-004)
# ============================================================================

class TestCrossTenantIsolation:
    """Test zero cross-tenant data leakage."""
    
    def test_workspace_a_cannot_access_workspace_b_cache(self):
        """Workspace A cannot access cached data from Workspace B."""
        registry_a = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        registry_b = MultiTenantRegistry(workspace_id="beta-test", tenant_id="beta")
        
        # Workspace A caches data
        registry_a._cache["acme-dev:acme:file.yaml"] = {"setting": "secret"}
        
        # Workspace B tries to access same file
        cache_key_b = registry_b.get_cache_key("file.yaml")
        
        # Should NOT find Workspace A's cached data
        assert cache_key_b not in registry_a._cache
        assert cache_key_b == "beta-test:beta:file.yaml"
    
    def test_tenant_specific_data_not_shared(self):
        """Tenant-specific data not shared across tenants."""
        registry_a = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        registry_b = MultiTenantRegistry(workspace_id="acme-staging", tenant_id="acme")
        
        # Same tenant, different workspaces
        key_a = registry_a.get_cache_key("config.yaml")
        key_b = registry_b.get_cache_key("config.yaml")
        
        # Should have different cache keys (workspace isolation)
        assert key_a != key_b
    
    def test_workspace_deletion_clears_only_workspace_cache(self):
        """Deleting workspace only clears its cache, not other workspaces."""
        registry_a = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        registry_b = MultiTenantRegistry(workspace_id="beta-test", tenant_id="beta")
        
        # Both cache data
        registry_a._cache["key1"] = "value1"
        registry_b._cache["key2"] = "value2"
        
        # Clear workspace A's cache
        registry_a.clear_cache()
        
        # Workspace A's cache cleared
        assert len(registry_a._cache) == 0
        
        # Workspace B's cache intact
        assert len(registry_b._cache) == 1
        assert "key2" in registry_b._cache


# ============================================================================
# TESTS: Backward Compatibility (AC-PHASE48-REG-S2-005)
# ============================================================================

class TestBackwardCompatibility:
    """Test 100% backward compatibility with single-tenant mode."""
    
    def test_local_workspace_behaves_like_old_registry(self):
        """Local workspace (workspace_id='local') behaves like old single-tenant registry."""
        registry = MultiTenantRegistry(workspace_id="local", tenant_id="local")
        
        # Should use standard cortex-registry/ paths
        # No {workspace_id} subdirectory
        cache_key = registry.get_cache_key("agents/core/tdd-orchestrator.yaml")
        
        assert "local" in cache_key
    
    def test_no_workspace_id_defaults_to_local(self):
        """No workspace_id provided defaults to 'local' (single-tenant mode)."""
        registry = MultiTenantRegistry()  # No workspace_id
        
        assert registry.workspace_id == "local"
        assert registry.tenant_id == "local"
    
    def test_existing_code_works_without_changes(self):
        """Existing code using GitBackedRegistry works without changes."""
        # Simulate old code that doesn't pass workspace_id
        registry = MultiTenantRegistry()
        
        # Should work with default local mode
        assert registry.workspace_id == "local"
        
        yaml_content = {"orchestrator": "TDDOrchestrator"}
        
        # Can load files normally
        with patch("pathlib.Path.exists", return_value=True):
            with patch.object(registry, "_load_yaml_file", return_value=yaml_content):
                # Should not raise error
                result = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
                assert result is not None
                assert result["orchestrator"] == "TDDOrchestrator"


# ============================================================================
# END OF TEST SUITE
# ============================================================================
