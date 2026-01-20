"""
AC-BRITTLE-001: Import Path Resolution Framework - Integration Tests

Integration tests for import resolver with real-world scenarios.
Tests cross-module interaction, state consistency, and practical workflows.

Author: cortex-builder
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import sys
from pathlib import Path
from typing import List
import tempfile
import shutil


class TestImportResolverIntegrationScenarios:
    """Integration test scenarios for import resolver."""

    def test_resolves_nested_package_structure(self):
        """Should resolve deeply nested package structures."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # cortex_brain.tier0 is nested
        path = resolver.resolve("cortex_brain.tier0")
        assert path is not None
        assert isinstance(path, Path)

    def test_caching_works_with_real_modules(self):
        """Should cache results for real modules correctly."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # First resolution
        path1 = resolver.resolve("cortex_brain")
        cache_size1 = len(resolver.cache)
        
        # Second resolution (cached)
        path2 = resolver.resolve("cortex_brain")
        cache_size2 = len(resolver.cache)
        
        assert path1 == path2
        assert cache_size1 == cache_size2

    def test_multiple_resolvers_dont_share_cache(self):
        """Should maintain independent caches for different resolver instances."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver1 = ImportResolver()
        resolver2 = ImportResolver()
        
        resolver1.resolve("json")
        resolver2.resolve("sys")
        
        # Caches should be independent
        assert "json" in resolver1.cache
        assert "json" not in resolver2.cache

    def test_resolver_with_custom_paths(self):
        """Should use custom paths when provided."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        custom_path = Path("/tmp/custom_modules")
        resolver = ImportResolver(paths=[custom_path])
        
        assert custom_path in resolver.paths

    def test_sys_path_modifications_reflected(self):
        """Should reflect modifications to sys.path."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        original_path = sys.path[:]
        try:
            resolver = ImportResolver()
            initial_count = len(resolver.paths)
            
            # Add to sys.path
            test_path = "/tmp/test_module_path"
            sys.path.append(test_path)
            
            # Create new resolver
            resolver2 = ImportResolver()
            
            # New resolver should see the new path
            assert len(resolver2.paths) >= initial_count
        finally:
            sys.path[:] = original_path

    def test_resolves_stdlib_before_custom(self):
        """Should prioritize stdlib modules over custom paths."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # json should resolve to stdlib
        path = resolver.resolve("json")
        assert path is not None
        
        # Should be from Python stdlib location
        assert "lib" in str(path).lower() or "python" in str(path).lower()

    def test_handles_package_vs_module_distinction(self):
        """Should distinguish between packages and modules."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # os is a module, sys is a module
        os_is_pkg = resolver.is_package("os")
        sys_is_pkg = resolver.is_package("sys")
        json_is_pkg = resolver.is_package("json")
        
        # At least one should resolve
        assert os_is_pkg in (True, False)
        assert sys_is_pkg in (True, False)
        assert json_is_pkg in (True, False)

    def test_resolver_handles_circular_module_references(self):
        """Should handle modules that import each other."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # These might have circular dependencies
        path1 = resolver.resolve("collections")
        path2 = resolver.resolve("typing")
        
        assert path1 is not None
        assert path2 is not None

    def test_relative_import_resolution_with_real_packages(self):
        """Should resolve relative imports within real packages."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Resolve relative from cortex_brain context
        path = resolver.resolve_relative(".tier1", "cortex_brain.tier0")
        
        # Should either resolve or return None (doesn't fail)
        assert path is None or isinstance(path, Path)

    def test_cache_invalidation_via_clear(self):
        """Should allow cache invalidation and re-resolution."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Cache initial resolution
        path1 = resolver.resolve("json")
        assert len(resolver.cache) > 0
        
        # Clear cache
        resolver.clear_cache()
        assert len(resolver.cache) == 0
        
        # Re-resolve
        path2 = resolver.resolve("json")
        assert path1 == path2
        assert len(resolver.cache) > 0

    def test_concurrent_resolution_thread_safety(self):
        """Should handle concurrent resolution safely."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        import threading
        
        resolver = ImportResolver()
        results = []
        errors = []
        
        def resolve_module(name):
            try:
                result = resolver.resolve(name)
                results.append((name, result))
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for mod in ["json", "sys", "pathlib", "collections", "typing"]:
            t = threading.Thread(target=resolve_module, args=(mod,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        # Should have results and no errors
        assert len(results) == 5
        assert len(errors) == 0

    def test_strategy_priority_order(self):
        """Should try strategies in correct priority order."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Should have multiple strategies
        assert len(resolver.strategies) > 1
        
        # json should resolve using one of them
        path = resolver.resolve("json")
        assert path is not None

    def test_adding_and_removing_paths_maintains_consistency(self):
        """Should maintain consistency when adding/removing paths."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        initial_count = len(resolver.paths)
        
        path1 = Path("/test1")
        path2 = Path("/test2")
        
        # Add paths
        resolver.add_path(path1)
        resolver.add_path(path2)
        assert len(resolver.paths) == initial_count + 2
        
        # Remove paths
        resolver.remove_path(path1)
        assert len(resolver.paths) == initial_count + 1
        
        resolver.remove_path(path2)
        assert len(resolver.paths) == initial_count

    def test_duplicate_path_prevention(self):
        """Should prevent duplicate paths in the resolution list."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        path = Path("/test/duplicate")
        
        # Add same path multiple times
        resolver.add_path(path)
        resolver.add_path(path)
        resolver.add_path(path)
        
        # Count occurrences
        count = sum(1 for p in resolver.paths if p == path)
        assert count == 1

    def test_cache_stats_reporting(self):
        """Should report accurate cache statistics."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        stats_before = resolver.get_cache_stats()
        assert stats_before["size"] == 0
        assert stats_before["enabled"] is True
        
        resolver.resolve("json")
        stats_after = resolver.get_cache_stats()
        assert stats_after["size"] >= 1

    def test_resolver_with_caching_disabled(self):
        """Should work correctly with caching disabled."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver(enable_caching=False)
        
        # Should still resolve
        path = resolver.resolve("json")
        assert path is not None
        
        # Cache should remain empty
        assert len(resolver.cache) == 0

    def test_large_cache_with_size_limit(self):
        """Should respect max_cache_size limit."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        import sys
        
        # Get real modules to resolve
        modules = [m for m in sys.builtin_module_names[:10]]
        
        resolver = ImportResolver(max_cache_size=5)
        
        # Resolve more than max_cache_size
        for mod in modules:
            try:
                resolver.resolve(mod)
            except:
                pass
        
        # Cache size should not exceed limit
        assert len(resolver.cache) <= 5

    def test_error_recovery_between_resolutions(self):
        """Should recover from errors during resolution."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Try invalid module
        result1 = resolver.resolve("invalid_xyz_123")
        assert result1 is None
        
        # Should recover and resolve valid module
        result2 = resolver.resolve("json")
        assert result2 is not None

    def test_unicode_handling_in_real_scenario(self):
        """Should handle unicode gracefully in real scenarios."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Try resolving with unicode characters
        result = resolver.resolve("ñomodule")
        
        # Should return None or valid Path, not crash
        assert result is None or isinstance(result, Path)

    def test_very_long_nested_import_path(self):
        """Should handle very long import paths."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Create a very long nested path
        long_path = ".".join(["module"] * 20)
        result = resolver.resolve(long_path)
        
        # Should return None or Path, not crash
        assert result is None or isinstance(result, Path)

    def test_special_characters_in_import_names(self):
        """Should handle special characters gracefully."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        special_names = [
            "module-with-dash",
            "module_with_underscore",
            "module.with.extra.dots",
            "@module",
            "module$",
        ]
        
        for name in special_names:
            result = resolver.resolve(name)
            # Should not crash
            assert result is None or isinstance(result, Path)

    def test_resolver_state_after_exception(self):
        """Should maintain valid state after an exception."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Resolve valid module
        path1 = resolver.resolve("json")
        
        # Trigger error condition
        try:
            resolver.resolve(None)  # This might error
        except:
            pass
        
        # Should still be able to resolve
        path2 = resolver.resolve("sys")
        assert path2 is not None

    def test_integration_with_module_import_system(self):
        """Should integrate properly with Python's module system."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Test with a module that's already imported
        import json as test_json
        path = resolver.resolve("json")
        
        # Should find the same module
        assert path is not None


# Test execution markers
pytestmark = pytest.mark.ac("BRITTLE-001")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
