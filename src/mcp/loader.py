"""
Orchestrator Loader - Dynamic orchestrator loading and instantiation.

Handles dynamic import and instantiation of orchestrators based on registry metadata.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import importlib
from typing import Any, Optional, Dict, Type
from pathlib import Path

from src.mcp.metadata import OrchestratorMetadata


class OrchestratorLoader:
    """
    Dynamic orchestrator loader with caching and error handling.
    
    Features:
    - Dynamic module import
    - Class instantiation with dependency injection
    - Instance caching
    - Manifest loading
    - Error handling and fallback
    
    Usage:
        loader = OrchestratorLoader(registry)
        
        # Load orchestrator instance
        instance = loader.load_instance("planning_v5")
        
        # Load with custom arguments
        instance = loader.load_instance(
            "planning_v5",
            init_args={'state_db': db, 'plan_type': 'epic'}
        )
    """
    
    def __init__(self, registry: 'OrchestratorRegistry'):
        """
        Initialize orchestrator loader.
        
        Args:
            registry: OrchestratorRegistry instance for metadata lookup
        """
        self.registry = registry
        self.logger = logging.getLogger("cortex.mcp.loader")
        
        # Cache for loaded modules and classes
        self._module_cache: Dict[str, Any] = {}
        self._class_cache: Dict[str, Type] = {}
    
    def load_class(self, metadata: OrchestratorMetadata) -> Type:
        """
        Load orchestrator class from metadata.
        
        Args:
            metadata: OrchestratorMetadata with module path and class name
        
        Returns:
            Orchestrator class object
        
        Raises:
            ImportError: If module cannot be imported
            AttributeError: If class not found in module
        """
        cache_key = f"{metadata.module_path}.{metadata.class_name}"
        
        # Return cached class if exists
        if cache_key in self._class_cache:
            self.logger.debug(f"Using cached class: {cache_key}")
            return self._class_cache[cache_key]
        
        try:
            # Load module
            if metadata.module_path not in self._module_cache:
                self.logger.debug(f"Importing module: {metadata.module_path}")
                module = importlib.import_module(metadata.module_path)
                self._module_cache[metadata.module_path] = module
            else:
                module = self._module_cache[metadata.module_path]
            
            # Get class from module
            if not hasattr(module, metadata.class_name):
                raise AttributeError(
                    f"Class '{metadata.class_name}' not found in module '{metadata.module_path}'"
                )
            
            class_obj = getattr(module, metadata.class_name)
            
            # Cache class
            self._class_cache[cache_key] = class_obj
            
            self.logger.info(f"Loaded class: {cache_key}")
            return class_obj
        
        except ImportError as e:
            self.logger.error(
                f"Failed to import module '{metadata.module_path}': {e}",
                exc_info=True
            )
            raise
        
        except AttributeError as e:
            self.logger.error(
                f"Failed to get class '{metadata.class_name}': {e}",
                exc_info=True
            )
            raise
    
    def load_instance(
        self,
        orchestrator_id: str,
        init_args: Optional[Dict[str, Any]] = None,
        lazy: bool = False
    ) -> Any:
        """
        Load and instantiate orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier from registry
            init_args: Custom initialization arguments (overrides defaults)
            lazy: If True, return class without instantiation
        
        Returns:
            Orchestrator instance (or class if lazy=True)
        
        Raises:
            KeyError: If orchestrator not found in registry
            ImportError: If module cannot be imported
            TypeError: If instantiation fails
        """
        # Get metadata from registry
        metadata = self.registry.get(orchestrator_id)
        if not metadata:
            raise KeyError(f"Orchestrator '{orchestrator_id}' not found in registry")
        
        # Check if enabled
        if not metadata.enabled:
            self.logger.warning(
                f"Orchestrator '{orchestrator_id}' is disabled but being loaded"
            )
        
        # Load class
        orchestrator_class = self.load_class(metadata)
        
        # Return class if lazy loading
        if lazy:
            return orchestrator_class
        
        # Prepare initialization arguments
        init_args = init_args or {}
        
        # Add manifest path if available
        if metadata.manifest_path and 'config_path' not in init_args:
            init_args['config_path'] = metadata.manifest_path
        
        try:
            # Instantiate orchestrator
            self.logger.debug(f"Instantiating {orchestrator_id} with args: {init_args}")
            instance = orchestrator_class(**init_args)
            
            self.logger.info(f"Loaded orchestrator instance: {orchestrator_id}")
            return instance
        
        except TypeError as e:
            self.logger.error(
                f"Failed to instantiate '{orchestrator_id}': {e}",
                exc_info=True
            )
            raise
    
    def load_manifest(
        self,
        orchestrator_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load orchestrator manifest (YAML) if available.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            Manifest dict or None if no manifest
        """
        import yaml
        
        metadata = self.registry.get(orchestrator_id)
        if not metadata or not metadata.manifest_path:
            return None
        
        manifest_path = Path(metadata.manifest_path)
        if not manifest_path.exists():
            self.logger.warning(
                f"Manifest file not found: {manifest_path}"
            )
            return None
        
        try:
            with open(manifest_path, 'r') as f:
                manifest = yaml.safe_load(f)
            
            self.logger.info(f"Loaded manifest for {orchestrator_id}")
            return manifest
        
        except Exception as e:
            self.logger.error(
                f"Failed to load manifest '{manifest_path}': {e}",
                exc_info=True
            )
            return None
    
    def reload_module(self, module_path: str) -> None:
        """
        Reload a module (useful for development/hot-reload).
        
        Args:
            module_path: Full module import path
        """
        if module_path in self._module_cache:
            module = self._module_cache[module_path]
            importlib.reload(module)
            self.logger.info(f"Reloaded module: {module_path}")
            
            # Clear class cache for this module
            keys_to_remove = [
                k for k in self._class_cache.keys()
                if k.startswith(f"{module_path}.")
            ]
            for key in keys_to_remove:
                del self._class_cache[key]
        else:
            self.logger.warning(
                f"Module '{module_path}' not in cache, cannot reload"
            )
    
    def clear_cache(self) -> None:
        """Clear all cached modules and classes."""
        self._module_cache.clear()
        self._class_cache.clear()
        self.logger.info("Cleared orchestrator loader cache")


class CustomOrchestratorLoader:
    """
    Custom orchestrator loader for user-defined orchestrators.
    
    Allows loading orchestrators from custom paths outside the CORTEX
    src tree (e.g., user plugins, extensions).
    
    Usage:
        loader = CustomOrchestratorLoader()
        
        # Register custom path
        loader.add_search_path("/path/to/custom/orchestrators")
        
        # Load custom orchestrator
        instance = loader.load_custom(
            class_name="MyCustomOrchestrator",
            module_name="my_orchestrator"
        )
    """
    
    def __init__(self):
        """Initialize custom orchestrator loader."""
        self.logger = logging.getLogger("cortex.mcp.custom_loader")
        self.search_paths: list[Path] = []
    
    def add_search_path(self, path: str) -> None:
        """
        Add custom search path for orchestrators.
        
        Args:
            path: Directory path to search for orchestrator modules
        """
        search_path = Path(path)
        if not search_path.exists():
            raise FileNotFoundError(f"Search path does not exist: {path}")
        
        if search_path not in self.search_paths:
            self.search_paths.append(search_path)
            self.logger.info(f"Added search path: {path}")
    
    def load_custom(
        self,
        class_name: str,
        module_name: str,
        init_args: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Load custom orchestrator from search paths.
        
        Args:
            class_name: Name of orchestrator class
            module_name: Name of module file (without .py)
            init_args: Initialization arguments
        
        Returns:
            Orchestrator instance
        
        Raises:
            FileNotFoundError: If module file not found
            ImportError: If module cannot be imported
            AttributeError: If class not found
        """
        import sys
        import importlib.util
        
        # Search for module file
        module_file = None
        for search_path in self.search_paths:
            candidate = search_path / f"{module_name}.py"
            if candidate.exists():
                module_file = candidate
                break
        
        if not module_file:
            raise FileNotFoundError(
                f"Module '{module_name}' not found in search paths: "
                f"{[str(p) for p in self.search_paths]}"
            )
        
        try:
            # Load module from file
            spec = importlib.util.spec_from_file_location(
                module_name,
                module_file
            )
            if not spec or not spec.loader:
                raise ImportError(f"Failed to create module spec for {module_file}")
            
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
            
            # Get class
            if not hasattr(module, class_name):
                raise AttributeError(
                    f"Class '{class_name}' not found in module '{module_name}'"
                )
            
            orchestrator_class = getattr(module, class_name)
            
            # Instantiate
            init_args = init_args or {}
            instance = orchestrator_class(**init_args)
            
            self.logger.info(
                f"Loaded custom orchestrator: {class_name} from {module_file}"
            )
            
            return instance
        
        except Exception as e:
            self.logger.error(
                f"Failed to load custom orchestrator '{class_name}': {e}",
                exc_info=True
            )
            raise
