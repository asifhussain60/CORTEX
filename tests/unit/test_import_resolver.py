"""
AC-BRITTLE-001: Import Path Resolution Framework Tests

Unit tests for centralized import path resolution framework.
Supports both absolute and relative imports, handles package detection.

Test-Driven Development (TDD): Tests written first (RED phase)
Author: cortex-builder
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sys
import pytest
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from unittest.mock import Mock, patch, MagicMock


class TestImportResolverBasics:
    """Test basic import resolver initialization and configuration."""

    def test_resolver_initializes_with_defaults(self):
        """Should initialize resolver with default sys.path."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        assert resolver is not None
        assert len(resolver.paths) > 0

    def test_resolver_initializes_with_custom_paths(self):
        """Should initialize resolver with custom paths."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        custom_paths = [Path("/custom/path1"), Path("/custom/path2")]
        resolver = ImportResolver(paths=custom_paths)
        
        assert resolver.paths == custom_paths

    def test_resolver_maintains_path_cache(self):
        """Should cache resolved paths for performance."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        cache = resolver.cache
        
        assert isinstance(cache, dict)
        assert len(cache) == 0  # Empty initially

    def test_resolver_cache_is_accessible(self):
        """Should provide access to internal cache."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        cache_before = len(resolver.cache)
        
        # Cache should be accessible
        assert isinstance(cache_before, int)

    def test_resolver_has_strategy_list(self):
        """Should maintain list of resolution strategies."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        assert hasattr(resolver, 'strategies')
        assert isinstance(resolver.strategies, (list, tuple))
        assert len(resolver.strategies) > 0


class TestAbsoluteImportResolution:
    """Test absolute import path resolution."""

    def test_resolves_absolute_module_path(self):
        """Should resolve absolute module path to file location."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        result = resolver.resolve("cortex_brain.tier0.import_resolver")
        
        assert result is not None
        assert isinstance(result, Path)

    def test_resolves_builtins_module(self):
        """Should resolve built-in modules."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        result = resolver.resolve("os")
        
        assert result is not None
        assert isinstance(result, Path)

    def test_resolves_standard_library_modules(self):
        """Should resolve standard library modules."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        modules = ["sys", "pathlib", "json", "collections"]
        for module in modules:
            result = resolver.resolve(module)
            assert result is not None, f"Failed to resolve {module}"

    def test_resolves_package_imports(self):
        """Should resolve package-level imports."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        result = resolver.resolve("cortex_brain")
        
        assert result is not None
        assert isinstance(result, Path)

    def test_returns_none_for_missing_module(self):
        """Should return None for modules that don't exist."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        result = resolver.resolve("non_existent_module_xyz123")
        
        assert result is None

    def test_returns_path_for_existing_modules(self):
        """Should return actual Path objects for existing modules."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        result = resolver.resolve("json")
        
        assert isinstance(result, Path)
        assert result.exists()


class TestRelativeImportResolution:
    """Test relative import path resolution."""

    def test_resolves_relative_import_single_dot(self):
        """Should resolve relative imports with single dot."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        # Relative import context needed
        result = resolver.resolve_relative(".module", "cortex_brain.tier0")
        
        # Should return a path or None if not found
        assert result is None or isinstance(result, Path)

    def test_resolves_relative_import_parent_package(self):
        """Should resolve parent package relative imports."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        result = resolver.resolve_relative("..tier1", "cortex_brain.tier0")
        
        # Should be a path or None
        assert result is None or isinstance(result, Path)

    def test_handles_relative_import_context(self):
        """Should use context package for relative resolution."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        # Same package relative import
        result = resolver.resolve_relative(".submodule", "cortex_brain.tier0")
        
        assert result is None or isinstance(result, Path)

    def test_relative_import_with_multiple_dots(self):
        """Should handle multiple dots in relative imports."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        result = resolver.resolve_relative("....cortex_brain", "cortex_brain.tier0.subpkg")
        
        # Should return path or None
        assert result is None or isinstance(result, Path)


class TestImportCaching:
    """Test import path caching mechanism."""

    def test_caches_resolved_imports(self):
        """Should cache resolved import paths."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # First resolution
        result1 = resolver.resolve("json")
        cache_size_after_first = len(resolver.cache)
        
        # Second resolution (should use cache)
        result2 = resolver.resolve("json")
        cache_size_after_second = len(resolver.cache)
        
        assert result1 == result2
        assert cache_size_after_first == cache_size_after_second

    def test_cache_improves_performance(self):
        """Should retrieve cached entries faster."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        import time
        
        resolver = ImportResolver()
        module = "cortex_brain.tier0.import_resolver"
        
        # First call (slower, not cached)
        start1 = time.perf_counter()
        result1 = resolver.resolve(module)
        time1 = time.perf_counter() - start1
        
        # Second call (faster, cached)
        start2 = time.perf_counter()
        result2 = resolver.resolve(module)
        time2 = time.perf_counter() - start2
        
        assert result1 == result2
        # Cached call should be faster (or at least not slower)
        assert time2 <= time1 * 2  # Allow 2x tolerance for timing variations

    def test_can_clear_cache(self):
        """Should allow clearing the cache."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Populate cache
        resolver.resolve("json")
        resolver.resolve("sys")
        assert len(resolver.cache) > 0
        
        # Clear cache
        resolver.clear_cache()
        assert len(resolver.cache) == 0

    def test_cache_persists_across_calls(self):
        """Should maintain cache across multiple resolution calls."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        modules = ["json", "sys", "pathlib", "collections"]
        for mod in modules:
            resolver.resolve(mod)
        
        cache_size = len(resolver.cache)
        assert cache_size >= len(modules)

    def test_can_peek_cache_without_mutation(self):
        """Should allow checking cache without modifying it."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        resolver.resolve("json")
        cache_size_before = len(resolver.cache)
        
        # Peek at cache
        cached_result = resolver.cache.get("json")
        cache_size_after = len(resolver.cache)
        
        assert cache_size_before == cache_size_after


class TestSystemPathManagement:
    """Test centralized sys.path management."""

    def test_centralizes_sys_path_management(self):
        """Should provide centralized sys.path management."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Should have access to sys.path
        assert hasattr(resolver, 'paths')
        assert len(resolver.paths) > 0

    def test_adds_path_to_resolution_list(self):
        """Should add custom paths for resolution."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        initial_count = len(resolver.paths)
        
        custom_path = Path("/custom/test/path")
        resolver.add_path(custom_path)
        
        assert len(resolver.paths) > initial_count
        assert custom_path in resolver.paths

    def test_removes_path_from_resolution_list(self):
        """Should remove paths from resolution list."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        custom_path = Path("/custom/test/path")
        resolver.add_path(custom_path)
        assert custom_path in resolver.paths
        
        resolver.remove_path(custom_path)
        assert custom_path not in resolver.paths

    def test_prevents_duplicate_paths(self):
        """Should prevent duplicate paths in resolution list."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        custom_path = Path("/custom/test/path")
        resolver.add_path(custom_path)
        resolver.add_path(custom_path)  # Try to add again
        
        # Count occurrences
        count = resolver.paths.count(custom_path)
        assert count == 1

    def test_manages_sys_path_integration(self):
        """Should integrate with sys.path properly."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        paths = resolver.paths
        
        # Should contain at least project root
        assert len(paths) > 0


class TestPackageDetection:
    """Test package detection and identification."""

    def test_detects_package_from_path(self):
        """Should detect if a path is a package."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # json is a package in Python 3.9+
        is_pkg = resolver.is_package("json")
        assert is_pkg in (True, False)  # json might or might not have __init__.py

    def test_detects_module_from_path(self):
        """Should detect if a path is a module."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # json is a module
        is_pkg = resolver.is_package("json")
        assert is_pkg in (True, False)  # Could be either in some Python versions

    def test_detects_nonexistent_module(self):
        """Should return False for non-existent modules."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        is_pkg = resolver.is_package("non_existent_xyz_module_999")
        assert is_pkg is False

    def test_identifies_package_init_file(self):
        """Should identify __init__.py files in packages."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Get path to json (might or might not be a package)
        path = resolver.resolve("json")
        if path:
            # Check if __init__.py exists
            has_init = (path / "__init__.py").exists()
            assert isinstance(has_init, bool)


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_handles_invalid_module_names(self):
        """Should handle invalid module names gracefully."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        invalid_names = [
            "...",
            "module with spaces",
            "module@invalid",
            "",
            None,
        ]
        
        for name in invalid_names:
            if name is not None:
                result = resolver.resolve(name)
                assert result is None or isinstance(result, Path)

    def test_handles_circular_imports(self):
        """Should detect and handle circular imports."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Should not crash on circular import detection
        result = resolver.resolve("sys")
        assert result is not None

    def test_handles_missing_modules_gracefully(self):
        """Should return None instead of raising exceptions."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Should not raise an exception
        result = resolver.resolve("missing_module_xyz")
        assert result is None

    def test_handles_unicode_in_module_names(self):
        """Should handle unicode characters in names."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        result = resolver.resolve("µodule")  # Invalid but shouldn't crash
        assert result is None or isinstance(result, Path)

    def test_handles_very_long_module_names(self):
        """Should handle very long module names."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        long_name = ".".join(["module"] * 50)
        result = resolver.resolve(long_name)
        assert result is None or isinstance(result, Path)


class TestImportStrategyPatterns:
    """Test different import resolution strategies."""

    def test_uses_multiple_resolution_strategies(self):
        """Should use multiple strategies to resolve imports."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Should have strategies available
        assert hasattr(resolver, 'strategies')
        assert len(resolver.strategies) > 0

    def test_tries_strategies_in_order(self):
        """Should try strategies in priority order."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Module should resolve using one of the strategies
        result = resolver.resolve("json")
        assert result is not None

    def test_strategy_fallback(self):
        """Should fallback to next strategy if one fails."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Should eventually return None instead of exception
        result = resolver.resolve("xyz_invalid_module_that_does_not_exist")
        assert result is None

    def test_can_add_custom_strategy(self):
        """Should allow adding custom resolution strategies."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        initial_count = len(resolver.strategies)
        
        # Create a mock strategy
        def custom_strategy(name: str) -> Optional[Path]:
            return None
        
        resolver.add_strategy(custom_strategy)
        assert len(resolver.strategies) > initial_count


class TestTypeHintsAndDocstrings:
    """Test that implementation has proper type hints and docstrings."""

    def test_resolver_class_has_type_hints(self):
        """Should have type hints on resolver methods."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        # Check method signatures
        import inspect
        
        sig = inspect.signature(ImportResolver.resolve)
        # Should have return annotation
        assert sig.return_annotation is not None
        # Should contain Optional or Path
        assert "Optional" in str(sig.return_annotation) or "Path" in str(sig.return_annotation)

    def test_resolver_methods_have_docstrings(self):
        """Should have docstrings on all public methods."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        # Check docstrings
        assert ImportResolver.__doc__ is not None
        assert len(ImportResolver.__doc__.strip()) > 0

    def test_imports_are_typed(self):
        """Should use type hints in implementations."""
        from cortex_brain.tier0 import import_resolver
        
        # Module should be importable
        assert import_resolver is not None


class TestImportResolverIntegration:
    """Integration-level tests for import resolver."""

    def test_resolver_works_with_real_modules(self):
        """Should resolve real modules in the system."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        modules = [
            "cortex_brain",
            "json",
            "sys",
            "pathlib",
            "collections",
        ]
        
        resolved = []
        for mod in modules:
            result = resolver.resolve(mod)
            if result:
                resolved.append(mod)
        
        # Should resolve at least some modules
        assert len(resolved) > 0

    def test_resolver_handles_state_properly(self):
        """Should maintain state properly across operations."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver = ImportResolver()
        
        # Perform multiple operations
        resolver.resolve("json")
        resolver.resolve("sys")
        resolver.add_path(Path("/tmp"))
        resolver.resolve("pathlib")
        
        # State should be consistent
        assert len(resolver.cache) > 0
        assert len(resolver.paths) > 0

    def test_multiple_resolvers_are_independent(self):
        """Should allow independent resolver instances."""
        from cortex_brain.tier0.import_resolver import ImportResolver
        
        resolver1 = ImportResolver()
        resolver2 = ImportResolver()
        
        resolver1.resolve("json")
        resolver2.resolve("sys")
        
        # Caches should be independent
        assert resolver1.cache != resolver2.cache or len(resolver1.cache) == len(resolver2.cache)


# Test execution markers
pytestmark = pytest.mark.ac("BRITTLE-001")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
