"""
Import Path Resolution Framework - AC-BRITTLE-001

Centralized import path resolution framework supporting absolute and relative imports.
Handles package detection, caching, and multiple resolution strategies.

This module provides:
- Centralized sys.path management
- Cached import resolution for performance
- Support for absolute and relative imports
- Multiple resolution strategies with fallback
- Package detection and identification

Type Hints: 100% coverage
Docstrings: Comprehensive

Author: cortex-builder
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import sys
import os
import importlib.util
from pathlib import Path
from typing import Optional, List, Dict, Callable, Tuple
from threading import RLock


class ImportStrategy:
    """
    Strategy interface for import path resolution.
    
    Implementations should provide different approaches to resolving
    import paths (e.g., sys.modules, importlib.util, filesystem search).
    """
    
    def __call__(self, name: str) -> Optional[Path]:
        """
        Resolve an import name to a file path.
        
        Args:
            name: Module or package name (e.g., 'os', 'cortex_brain.tier0')
            
        Returns:
            Path to the module/package, or None if not found
        """
        raise NotImplementedError


class SystemModuleStrategy(ImportStrategy):
    """Resolve imports using sys.modules."""
    
    def __call__(self, name: str) -> Optional[Path]:
        """
        Resolve using already-loaded sys.modules.
        
        Args:
            name: Module name to resolve
            
        Returns:
            Path to module file, or None if not found
        """
        try:
            if name in sys.modules:
                module = sys.modules[name]
                if hasattr(module, '__file__') and module.__file__:
                    return Path(module.__file__).parent
            return None
        except (AttributeError, ValueError):
            return None


class ImportlibUtilStrategy(ImportStrategy):
    """Resolve imports using importlib.util."""
    
    def __call__(self, name: str) -> Optional[Path]:
        """
        Resolve using importlib.util.find_spec.
        
        Args:
            name: Module name to resolve
            
        Returns:
            Path to module file, or None if not found
        """
        try:
            spec = importlib.util.find_spec(name)
            if spec is None:
                return None
            
            if spec.origin:
                return Path(spec.origin).parent
            
            if spec.submodule_search_locations:
                return Path(spec.submodule_search_locations[0])
            
            return None
        except (ImportError, ValueError, AttributeError, TypeError):
            return None


class FilesystemSearchStrategy(ImportStrategy):
    """Search for imports in sys.path directories."""
    
    def __init__(self, paths: Optional[List[Path]] = None) -> None:
        """
        Initialize filesystem search strategy.
        
        Args:
            paths: List of paths to search. Defaults to sys.path.
        """
        self.search_paths = paths or [Path(p) for p in sys.path if p]
    
    def __call__(self, name: str) -> Optional[Path]:
        """
        Search for module/package in filesystem.
        
        Args:
            name: Module name to resolve (e.g., 'cortex_brain.tier0')
            
        Returns:
            Path to module file, or None if not found
        """
        try:
            # Convert module name to path components
            parts = name.split('.')
            
            for search_path in self.search_paths:
                if not search_path.exists():
                    continue
                
                # Try as package (directory with __init__.py)
                package_path = search_path.joinpath(*parts)
                if package_path.is_dir() and (package_path / "__init__.py").exists():
                    return package_path
                
                # Try as module (.py file)
                module_file = search_path.joinpath(f"{parts[0]}.py")
                if module_file.is_file():
                    return module_file.parent
            
            return None
        except (ValueError, TypeError, OSError):
            return None


class ImportResolver:
    """
    Centralized import path resolution framework.
    
    Provides unified interface for resolving absolute and relative imports,
    with caching, package detection, and multiple resolution strategies.
    
    Features:
    - Centralized sys.path management
    - Import resolution caching for performance
    - Support for absolute imports
    - Support for relative imports (with context)
    - Package detection and __init__.py identification
    - Multiple resolution strategies with fallback
    - Thread-safe operations with RLock
    - 100% type hints and comprehensive docstrings
    
    Example:
        >>> resolver = ImportResolver()
        >>> path = resolver.resolve("cortex_brain.tier0")
        >>> print(path)
        PosixPath('/path/to/cortex_brain/tier0')
        
        >>> resolver.add_path(Path("/custom/modules"))
        >>> resolver.is_package("cortex_brain")
        True
    """
    
    def __init__(
        self,
        paths: Optional[List[Path]] = None,
        enable_caching: bool = True,
        max_cache_size: int = 1000,
    ) -> None:
        """
        Initialize the import resolver.
        
        Args:
            paths: Custom list of search paths. Defaults to sys.path.
            enable_caching: Whether to cache resolved imports (default: True).
            max_cache_size: Maximum cache size (default: 1000).
            
        Raises:
            ValueError: If max_cache_size is <= 0.
        """
        if max_cache_size <= 0:
            raise ValueError("max_cache_size must be > 0")
        
        # Initialize paths
        self.paths: List[Path] = paths or [Path(p) for p in sys.path if p]
        
        # Initialize caching
        self._enable_caching = enable_caching
        self._max_cache_size = max_cache_size
        self.cache: Dict[str, Optional[Path]] = {}
        
        # Initialize strategies
        self.strategies: List[ImportStrategy] = [
            SystemModuleStrategy(),
            ImportlibUtilStrategy(),
            FilesystemSearchStrategy(self.paths),
        ]
        
        # Thread safety
        self._lock = RLock()
    
    def resolve(self, name: str) -> Optional[Path]:
        """
        Resolve an absolute import path.
        
        Attempts to resolve the given module/package name using multiple
        strategies in order. Results are cached for performance.
        
        Args:
            name: Module or package name (e.g., 'cortex_brain', 'json', 'os.path')
            
        Returns:
            Path to the module/package, or None if not found.
            
        Example:
            >>> resolver = ImportResolver()
            >>> path = resolver.resolve("json")
            >>> path is not None
            True
            >>> path.name
            'json'
        """
        with self._lock:
            # Check cache first
            if self._enable_caching and name in self.cache:
                return self.cache[name]
            
            # Try each strategy
            result = None
            for strategy in self.strategies:
                try:
                    result = strategy(name)
                    if result is not None:
                        break
                except Exception:
                    # Strategy failed, try next
                    continue
            
            # Cache result
            if self._enable_caching:
                self._update_cache(name, result)
            
            return result
    
    def resolve_relative(self, name: str, context: str) -> Optional[Path]:
        """
        Resolve a relative import within a package context.
        
        Converts relative import (with leading dots) to absolute import
        using the provided package context.
        
        Args:
            name: Relative import name (e.g., '.module', '..tier1.subpkg')
            context: Package context for resolution (e.g., 'cortex_brain.tier0')
            
        Returns:
            Path to the module/package, or None if not found.
            
        Raises:
            ValueError: If name doesn't start with a dot or context is invalid.
            
        Example:
            >>> resolver = ImportResolver()
            >>> path = resolver.resolve_relative(".submodule", "cortex_brain.tier0")
            >>> path is not None
            True
        """
        if not isinstance(name, str) or not name.startswith('.'):
            raise ValueError("Relative import must start with a dot")
        
        if not isinstance(context, str) or not context:
            raise ValueError("Context must be a non-empty string")
        
        # Count leading dots
        level = len(name) - len(name.lstrip('.'))
        relative_part = name[level:]
        
        # Go up levels in context
        context_parts = context.split('.')
        if level > len(context_parts):
            return None
        
        # Go up 'level' packages
        for _ in range(level - 1):
            if context_parts:
                context_parts.pop()
        
        # Build absolute name
        if relative_part:
            absolute_name = '.'.join(context_parts) + '.' + relative_part
        else:
            absolute_name = '.'.join(context_parts)
        
        return self.resolve(absolute_name)
    
    def is_package(self, name: str) -> bool:
        """
        Determine if a module name refers to a package.
        
        A package is a module that contains an __init__.py file.
        
        Args:
            name: Module or package name to check
            
        Returns:
            True if name refers to a package, False otherwise.
            
        Example:
            >>> resolver = ImportResolver()
            >>> resolver.is_package("cortex_brain")
            True
            >>> resolver.is_package("json")
            True  # json is a package in Python 3.9+
        """
        try:
            path = self.resolve(name)
            if path is None:
                return False
            
            # Check for __init__.py
            init_file = path / "__init__.py"
            return init_file.exists() and init_file.is_file()
        except Exception:
            return False
    
    def add_path(self, path: Path) -> None:
        """
        Add a path to the resolution search list.
        
        Prevents duplicate paths. New paths are added to the end
        and have lower priority than existing paths.
        
        Args:
            path: Path to add
            
        Raises:
            TypeError: If path is not a Path object.
            
        Example:
            >>> resolver = ImportResolver()
            >>> resolver.add_path(Path("/custom/modules"))
            >>> Path("/custom/modules") in resolver.paths
            True
        """
        if not isinstance(path, Path):
            raise TypeError("path must be a Path object")
        
        with self._lock:
            if path not in self.paths:
                self.paths.append(path)
    
    def remove_path(self, path: Path) -> None:
        """
        Remove a path from the resolution search list.
        
        Does nothing if path is not in the list.
        
        Args:
            path: Path to remove
            
        Example:
            >>> resolver = ImportResolver()
            >>> custom_path = Path("/custom")
            >>> resolver.add_path(custom_path)
            >>> resolver.remove_path(custom_path)
            >>> custom_path in resolver.paths
            False
        """
        with self._lock:
            while path in self.paths:
                self.paths.remove(path)
    
    def clear_cache(self) -> None:
        """
        Clear the import resolution cache.
        
        Useful when filesystem changes occur or for testing.
        
        Example:
            >>> resolver = ImportResolver()
            >>> resolver.resolve("json")
            >>> len(resolver.cache) > 0
            True
            >>> resolver.clear_cache()
            >>> len(resolver.cache)
            0
        """
        with self._lock:
            self.cache.clear()
    
    def add_strategy(self, strategy: ImportStrategy) -> None:
        """
        Add a custom resolution strategy.
        
        Strategies are tried in order. New strategies are appended
        and tried after built-in strategies.
        
        Args:
            strategy: Callable that takes a module name and returns Path or None.
            
        Raises:
            TypeError: If strategy is not callable.
            
        Example:
            >>> resolver = ImportResolver()
            >>> def my_strategy(name):
            ...     return None
            >>> resolver.add_strategy(my_strategy)
            >>> len(resolver.strategies) > 3
            True
        """
        if not callable(strategy):
            raise TypeError("strategy must be callable")
        
        with self._lock:
            self.strategies.append(strategy)
    
    def _update_cache(self, name: str, result: Optional[Path]) -> None:
        """
        Update the resolution cache with new result.
        
        Respects max_cache_size by clearing oldest entries if needed.
        
        Args:
            name: Module name being cached
            result: Resolution result (Path or None)
            
        Note:
            Private method. Called internally by resolve().
        """
        if len(self.cache) >= self._max_cache_size:
            # Remove oldest entry (FIFO)
            first_key = next(iter(self.cache))
            del self.cache[first_key]
        
        self.cache[name] = result
    
    def get_cache_stats(self) -> Dict[str, int]:
        """
        Get cache statistics.
        
        Returns:
            Dictionary with cache metrics.
            
        Example:
            >>> resolver = ImportResolver()
            >>> resolver.resolve("json")
            >>> stats = resolver.get_cache_stats()
            >>> stats["size"]
            1
        """
        with self._lock:
            return {
                "size": len(self.cache),
                "max_size": self._max_cache_size,
                "enabled": self._enable_caching,
            }


__all__ = [
    "ImportResolver",
    "ImportStrategy",
    "SystemModuleStrategy",
    "ImportlibUtilStrategy",
    "FilesystemSearchStrategy",
]
