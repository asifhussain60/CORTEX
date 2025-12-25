"""
OrchestratorRegistry - Dynamic Orchestrator Discovery & Registration System

Phase: Task 13.5 - GREEN Phase
Objective: Implement dynamic orchestrator registration with auto-discovery
Features:
  - Singleton pattern for global registry access
  - Manual registration with metadata support
  - Automatic orchestrator discovery from directories
  - Lazy loading with instance caching
  - Thread-safe concurrent access
  - Plugin decorator for custom registration
  - Graceful error handling

Author: CORTEX Phase 13 Task 13.5
Created: December 25, 2025
Version: 1.0.0
"""

import logging
import threading
import inspect
from pathlib import Path
from typing import Type, Dict, List, Optional, Any, Callable
from functools import wraps
import importlib.util
import sys

# Import base orchestrator for type checking
try:
    from src.orchestrators.base.base_orchestrator import BaseOrchestrator
except ImportError:
    BaseOrchestrator = None  # Type: ignore


logger = logging.getLogger(__name__)


# ============================================================================
# Plugin Decorator
# ============================================================================

def orchestrator_plugin(name: str, version: str = "1.0.0", **metadata) -> Callable:
    """
    Decorator to mark a class as an orchestrator plugin with custom metadata.
    
    Usage:
        @orchestrator_plugin("my_orchestrator", version="2.0.0", capabilities=["planning"])
        class MyOrchestrator(BaseOrchestrator):
            pass
    
    Args:
        name: Custom name for orchestrator registration
        version: Version string
        **metadata: Additional metadata (capabilities, description, etc.)
    
    Returns:
        Decorator function
    """
    def decorator(cls: Type) -> Type:
        cls._orchestrator_plugin_name = name
        cls._orchestrator_plugin_version = version
        cls._orchestrator_plugin_metadata = metadata
        return cls
    return decorator


# ============================================================================
# OrchestratorRegistry Class
# ============================================================================

class OrchestratorRegistry:
    """
    Registry for dynamic orchestrator discovery and lazy instantiation.
    
    Features:
    - Singleton pattern for global access
    - Manual registration with metadata
    - Auto-discovery from directories
    - Lazy instantiation with caching
    - Thread-safe operations
    - Graceful error handling
    
    Example:
        registry = OrchestratorRegistry.get_instance()
        registry.discover([Path("src/orchestrators")])
        orchestrator = registry.get("planning", workspace_root="/path")
    """
    
    _instance: Optional['OrchestratorRegistry'] = None
    _lock = threading.Lock()
    
    def __init__(self):
        """Initialize empty registry."""
        self._orchestrators: Dict[str, Type] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}
        self._instances: Dict[str, Any] = {}
        self._instance_lock = threading.Lock()
        
        logger.debug("OrchestratorRegistry initialized")
    
    @classmethod
    def get_instance(cls) -> 'OrchestratorRegistry':
        """
        Get or create singleton registry instance.
        
        Returns:
            Singleton OrchestratorRegistry instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:  # Double-check locking
                    cls._instance = cls()
        return cls._instance
    
    def register(
        self,
        name: str,
        orchestrator_class: Type,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Manually register an orchestrator class.
        
        Args:
            name: Registration name (e.g., "planning", "tdd")
            orchestrator_class: Orchestrator class (must inherit BaseOrchestrator)
            metadata: Optional metadata (version, capabilities, etc.)
        
        Raises:
            ValueError: If name already registered
            TypeError: If class doesn't inherit from BaseOrchestrator
        """
        # Check if BaseOrchestrator is available
        if BaseOrchestrator is not None:
            if not issubclass(orchestrator_class, BaseOrchestrator):
                raise TypeError(
                    f"Class {orchestrator_class.__name__} must inherit from BaseOrchestrator"
                )
        
        # Check for duplicate registration
        if name in self._orchestrators:
            raise ValueError(
                f"Orchestrator '{name}' is already registered "
                f"({self._orchestrators[name].__name__})"
            )
        
        # Register orchestrator
        self._orchestrators[name] = orchestrator_class
        self._metadata[name] = metadata or {}
        
        logger.info(f"Registered orchestrator: {name} ({orchestrator_class.__name__})")
    
    def discover(self, directories: List[Path]) -> int:
        """
        Auto-discover orchestrators in given directories.
        
        Scans Python files for classes inheriting from BaseOrchestrator.
        Extracts metadata from docstrings and @orchestrator_plugin decorators.
        
        Args:
            directories: List of directory paths to scan
        
        Returns:
            Number of orchestrators discovered and registered
        """
        discovered_count = 0
        
        for directory in directories:
            if not directory.exists():
                logger.warning(f"Directory not found: {directory}")
                continue
            
            # Find all Python files
            python_files = list(directory.rglob("*.py"))
            
            for py_file in python_files:
                try:
                    discovered_count += self._discover_in_file(py_file)
                except Exception as e:
                    # Gracefully handle import/parsing errors
                    logger.debug(f"Skipping {py_file}: {e}")
                    continue
        
        logger.info(f"Discovery complete: {discovered_count} orchestrators found")
        return discovered_count
    
    def _discover_in_file(self, file_path: Path) -> int:
        """
        Discover orchestrators in a single Python file.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            Number of orchestrators discovered in file
        """
        count = 0
        
        # Load module dynamically
        spec = importlib.util.spec_from_file_location(
            f"dynamic_module_{file_path.stem}",
            file_path
        )
        if spec is None or spec.loader is None:
            return 0
        
        module = importlib.util.module_from_spec(spec)
        
        # Execute module to get classes
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            logger.debug(f"Failed to import {file_path}: {e}")
            return 0
        
        # Find orchestrator classes
        for name, obj in inspect.getmembers(module, inspect.isclass):
            # Skip if not BaseOrchestrator subclass
            if BaseOrchestrator is None or not issubclass(obj, BaseOrchestrator):
                continue
            
            # Skip BaseOrchestrator itself
            if obj is BaseOrchestrator:
                continue
            
            # Check for plugin decorator
            if hasattr(obj, '_orchestrator_plugin_name'):
                reg_name = obj._orchestrator_plugin_name
                version = getattr(obj, '_orchestrator_plugin_version', "1.0.0")
                extra_metadata = getattr(obj, '_orchestrator_plugin_metadata', {})
            else:
                # Use class name (convert CamelCase to snake_case)
                reg_name = self._to_snake_case(name)
                version = self._extract_version_from_docstring(obj)
                extra_metadata = {}
            
            # Skip if already registered
            if reg_name in self._orchestrators:
                continue
            
            # Extract capabilities from docstring
            capabilities = self._extract_capabilities_from_docstring(obj)
            
            # Build metadata - ALWAYS include version
            metadata = {
                "version": version,  # Always present, even if "1.0.0"
                "capabilities": capabilities,
                "file": str(file_path),
            }
            # Merge extra metadata from decorator
            metadata.update(extra_metadata)
            
            try:
                self.register(reg_name, obj, metadata)
                count += 1
            except (ValueError, TypeError) as e:
                logger.debug(f"Skipping {name}: {e}")
                continue
        
        return count
    
    def _to_snake_case(self, name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _extract_version_from_docstring(self, cls: Type) -> str:
        """Extract version from class docstring."""
        doc = inspect.getdoc(cls)
        if not doc:
            return "1.0.0"
        
        import re
        match = re.search(r'Version:\s*(\d+\.\d+\.\d+)', doc)
        if match:
            return match.group(1)
        return "1.0.0"
    
    def _extract_capabilities_from_docstring(self, cls: Type) -> List[str]:
        """Extract capabilities list from class docstring."""
        doc = inspect.getdoc(cls)
        if not doc:
            return []
        
        import re
        match = re.search(r'Capabilities:\s*([^\n]+)', doc)
        if match:
            caps_str = match.group(1)
            return [c.strip() for c in caps_str.split(',')]
        return []
    
    def get(self, name: str, *args, **kwargs) -> Optional[Any]:
        """
        Get or instantiate orchestrator (lazy loading with caching).
        
        Args:
            name: Orchestrator name
            *args: Arguments to pass to orchestrator constructor
            **kwargs: Keyword arguments to pass to constructor
        
        Returns:
            Orchestrator instance or None if not found/failed
        """
        # Check if registered
        if name not in self._orchestrators:
            logger.warning(f"Orchestrator '{name}' not found in registry")
            return None
        
        # Thread-safe lazy instantiation
        with self._instance_lock:
            # Return cached instance if exists
            if name in self._instances:
                return self._instances[name]
            
            # Instantiate orchestrator
            try:
                orchestrator_class = self._orchestrators[name]
                instance = orchestrator_class(*args, **kwargs)
                self._instances[name] = instance
                logger.debug(f"Instantiated orchestrator: {name}")
                return instance
            except Exception as e:
                logger.error(f"Failed to instantiate '{name}': {e}")
                return None
    
    def is_available(self, name: str) -> bool:
        """
        Check if orchestrator is registered and can be instantiated.
        
        Note: This does NOT actually instantiate - just checks if registered.
        Actual availability (can instantiate) is only verified during get().
        
        Args:
            name: Orchestrator name
        
        Returns:
            True if registered, False otherwise
        """
        return name in self._orchestrators
    
    def get_metadata(self, name: str) -> Dict[str, Any]:
        """
        Get metadata for registered orchestrator.
        
        Args:
            name: Orchestrator name
        
        Returns:
            Metadata dictionary (empty if not found)
        """
        return self._metadata.get(name, {})
    
    def list_all(self) -> List[str]:
        """
        Get list of all registered orchestrator names.
        
        Returns:
            List of orchestrator names
        """
        return list(self._orchestrators.keys())
    
    def count(self) -> int:
        """
        Get count of registered orchestrators.
        
        Returns:
            Number of registered orchestrators
        """
        return len(self._orchestrators)
    
    def clear(self) -> None:
        """Clear all registrations (for testing)."""
        self._orchestrators.clear()
        self._metadata.clear()
        self._instances.clear()
        logger.debug("Registry cleared")


# ============================================================================
# Module-level convenience functions
# ============================================================================

def get_registry() -> OrchestratorRegistry:
    """
    Get global registry instance (convenience function).
    
    Returns:
        Singleton OrchestratorRegistry instance
    """
    return OrchestratorRegistry.get_instance()


def auto_discover_orchestrators(
    directories: Optional[List[Path]] = None
) -> OrchestratorRegistry:
    """
    Auto-discover orchestrators and return registry (convenience function).
    
    Args:
        directories: Optional list of paths (defaults to src/orchestrators)
    
    Returns:
        Registry with discovered orchestrators
    """
    registry = get_registry()
    
    if directories is None:
        directories = [Path("src/orchestrators")]
    
    registry.discover(directories)
    return registry
