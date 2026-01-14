"""
Orchestrator Registry - Central registration and discovery system.

Manages all orchestrator metadata, lifecycle, and discovery operations.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, List, Optional, Any, Type, Tuple
from pathlib import Path
import json

from src.mcp.metadata import OrchestratorMetadata, OrchestratorType, OrchestratorCategory


class OrchestratorRegistry:
    """
    Central registry for all orchestrators.
    
    Features:
    - Orchestrator registration and discovery
    - Metadata storage and retrieval
    - Pattern-based matching
    - Dependency resolution
    - Health monitoring
    - Persistence to JSON
    
    Usage:
        registry = OrchestratorRegistry()
        
        # Register orchestrator
        registry.register(
            id="planning_v5",
            name="Planning System v5",
            version="5.0.0",
            type=OrchestratorType.AUTONOMOUS,
            category=OrchestratorCategory.PLANNING,
            class_name="PlanningOrchestratorV5",
            module_path="src.orchestrators.planning.planning_orchestrator_v5",
            patterns=[r"^(plan|create a plan|make a plan).*$"]
        )
        
        # Discover orchestrators
        matches = registry.find_by_pattern("plan authentication")
        orchestrator = registry.get("planning_v5")
    """
    
    def __init__(self, registry_path: Optional[str] = None):
        """
        Initialize orchestrator registry.
        
        Args:
            registry_path: Path to persist registry data (JSON)
        """
        self.logger = logging.getLogger("cortex.mcp.registry")
        self.registry_path = Path(registry_path) if registry_path else None
        
        # Core storage
        self._orchestrators: Dict[str, OrchestratorMetadata] = {}
        self._loaded_instances: Dict[str, Any] = {}  # Cached instances
        
        # Load persisted registry if exists
        if self.registry_path and self.registry_path.exists():
            self._load_from_disk()
        
        self.logger.info(f"OrchestratorRegistry initialized (registry_path={registry_path})")
    
    def register(
        self,
        id: str,
        name: str,
        version: str,
        type: OrchestratorType,
        category: OrchestratorCategory,
        class_name: str,
        module_path: str,
        description: str = "",
        manifest_path: Optional[str] = None,
        patterns: Optional[List[str]] = None,
        dependencies: Optional[List[str]] = None,
        capabilities: Optional[List[str]] = None,
        tags: Optional[Dict[str, Any]] = None,
        enabled: bool = True,
        overwrite: bool = False
    ) -> None:
        """
        Register an orchestrator in the registry.
        
        Args:
            id: Unique orchestrator identifier
            name: Human-readable name
            version: Semantic version
            type: Execution type
            category: Functional category
            class_name: Python class name
            module_path: Full module import path
            description: Brief description
            manifest_path: Path to YAML manifest
            patterns: Regex patterns for intent matching
            dependencies: List of required orchestrator IDs
            capabilities: List of capability strings
            tags: Additional metadata
            enabled: Whether orchestrator is active
            overwrite: Whether to overwrite existing registration
        
        Raises:
            ValueError: If orchestrator already registered and overwrite=False
        """
        if id in self._orchestrators and not overwrite:
            raise ValueError(
                f"Orchestrator '{id}' already registered. Use overwrite=True to replace."
            )
        
        metadata = OrchestratorMetadata(
            id=id,
            name=name,
            version=version,
            type=type,
            category=category,
            class_name=class_name,
            module_path=module_path,
            description=description,
            manifest_path=manifest_path,
            patterns=patterns or [],
            dependencies=dependencies or [],
            capabilities=capabilities or [],
            tags=tags or {},
            enabled=enabled,
        )
        
        self._orchestrators[id] = metadata
        self.logger.info(f"Registered orchestrator: {id} (v{version})")
        
        # Persist to disk if configured
        if self.registry_path:
            self._save_to_disk()
    
    def unregister(self, id: str) -> None:
        """
        Unregister an orchestrator.
        
        Args:
            id: Orchestrator identifier
        
        Raises:
            KeyError: If orchestrator not found
        """
        if id not in self._orchestrators:
            raise KeyError(f"Orchestrator '{id}' not found in registry")
        
        del self._orchestrators[id]
        
        # Remove cached instance if exists
        if id in self._loaded_instances:
            del self._loaded_instances[id]
        
        self.logger.info(f"Unregistered orchestrator: {id}")
        
        # Persist to disk
        if self.registry_path:
            self._save_to_disk()
    
    def get(self, id: str) -> Optional[OrchestratorMetadata]:
        """
        Retrieve orchestrator metadata by ID.
        
        Args:
            id: Orchestrator identifier
        
        Returns:
            OrchestratorMetadata if found, None otherwise
        """
        return self._orchestrators.get(id)
    
    def is_registered(self, id: str) -> bool:
        """
        Check if an orchestrator is registered.
        
        AC-CORTEX-002: Registry validation capability
        
        Args:
            id: Orchestrator identifier
        
        Returns:
            True if registered, False otherwise
        """
        return id in self._orchestrators
    
    def validate_for_routing(self, orchestrator_id: str) -> Tuple[bool, str]:
        """
        Validate that an orchestrator is ready for routing.
        
        AC-CORTEX-003: Routing validation
        
        Args:
            orchestrator_id: Orchestrator to validate
        
        Returns:
            (is_valid, reason_or_ok)
        """
        # Check if registered
        if not self.is_registered(orchestrator_id):
            return False, f"Orchestrator not registered: {orchestrator_id}"
        
        metadata = self.get(orchestrator_id)
        if not metadata:
            return False, f"Orchestrator metadata not found: {orchestrator_id}"
        
        # Check if enabled
        if not metadata.enabled:
            return False, f"Orchestrator is disabled: {orchestrator_id}"
        
        # Check if has valid patterns
        if not metadata.patterns or len(metadata.patterns) == 0:
            return False, f"Orchestrator has no routing patterns: {orchestrator_id}"
        
        # Check if class is loadable (basic check)
        if not metadata.class_name or not metadata.module_path:
            return False, f"Orchestrator missing class or module: {orchestrator_id}"
        
        return True, "OK"
    
    def instantiate(self, orchestrator_id: str, init_args: Optional[Dict[str, Any]] = None) -> Any:
        """
        Instantiate an orchestrator by ID.
        
        Args:
            orchestrator_id: Orchestrator identifier
            init_args: Optional initialization arguments
        
        Returns:
            Orchestrator instance
        
        Raises:
            KeyError: If orchestrator not found
            ImportError: If module cannot be imported
        """
        # Check cache first
        if orchestrator_id in self._loaded_instances and init_args is None:
            self.logger.debug(f"Using cached instance: {orchestrator_id}")
            return self._loaded_instances[orchestrator_id]
        
        # Get metadata
        metadata = self.get(orchestrator_id)
        if not metadata:
            raise KeyError(f"Orchestrator '{orchestrator_id}' not found in registry")
        
        # Use loader to instantiate
        from src.mcp.loader import OrchestratorLoader
        loader = OrchestratorLoader(self)
        instance = loader.load_instance(orchestrator_id, init_args=init_args)
        
        # Cache instance if no custom init_args
        if init_args is None:
            self._loaded_instances[orchestrator_id] = instance
        
        return instance
    
    def list_all(
        self,
        enabled_only: bool = True,
        category: Optional[OrchestratorCategory] = None,
        type: Optional[OrchestratorType] = None
    ) -> List[OrchestratorMetadata]:
        """
        List all registered orchestrators with optional filtering.
        
        Args:
            enabled_only: Only return enabled orchestrators
            category: Filter by category
            type: Filter by execution type
        
        Returns:
            List of OrchestratorMetadata
        """
        orchestrators = list(self._orchestrators.values())
        
        # Apply filters
        if enabled_only:
            orchestrators = [o for o in orchestrators if o.enabled]
        
        if category:
            orchestrators = [o for o in orchestrators if o.category == category]
        
        if type:
            orchestrators = [o for o in orchestrators if o.type == type]
        
        return orchestrators
    
    def find_by_pattern(
        self,
        user_input: str,
        enabled_only: bool = True
    ) -> List[OrchestratorMetadata]:
        """
        Find orchestrators matching user input pattern.
        
        Args:
            user_input: User request string
            enabled_only: Only return enabled orchestrators
        
        Returns:
            List of matching OrchestratorMetadata (sorted by relevance)
        """
        matches = []
        
        for orchestrator in self.list_all(enabled_only=enabled_only):
            if orchestrator.matches_pattern(user_input):
                matches.append(orchestrator)
        
        return matches
    
    def resolve_dependencies(
        self,
        id: str,
        visited: Optional[set] = None
    ) -> List[str]:
        """
        Resolve orchestrator dependencies (topological order).
        
        Args:
            id: Orchestrator identifier
            visited: Track visited nodes (for cycle detection)
        
        Returns:
            List of orchestrator IDs in dependency order
        
        Raises:
            ValueError: If circular dependency detected
            KeyError: If orchestrator or dependency not found
        """
        if visited is None:
            visited = set()
        
        if id in visited:
            raise ValueError(f"Circular dependency detected: {id}")
        
        orchestrator = self.get(id)
        if not orchestrator:
            raise KeyError(f"Orchestrator '{id}' not found")
        
        visited.add(id)
        resolved = []
        
        # Recursively resolve dependencies
        for dep_id in orchestrator.dependencies:
            dep_resolved = self.resolve_dependencies(dep_id, visited.copy())
            resolved.extend(dep_resolved)
        
        # Add current orchestrator
        resolved.append(id)
        
        return resolved
    
    def get_instance(self, id: str) -> Any:
        """
        Get cached orchestrator instance (lazy loading).
        
        Args:
            id: Orchestrator identifier
        
        Returns:
            Orchestrator instance
        
        Raises:
            KeyError: If orchestrator not found
            ImportError: If module cannot be imported
        """
        # Return cached instance if exists
        if id in self._loaded_instances:
            return self._loaded_instances[id]
        
        # Get metadata
        metadata = self.get(id)
        if not metadata:
            raise KeyError(f"Orchestrator '{id}' not found in registry")
        
        # Load instance (this will be handled by OrchestratorLoader)
        from src.mcp.loader import OrchestratorLoader
        loader = OrchestratorLoader(self)
        instance = loader.load_instance(id)
        
        # Cache instance
        self._loaded_instances[id] = instance
        
        return instance
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform health check on all registered orchestrators.
        
        Returns:
            Health check results with status for each orchestrator
        """
        results = {
            'total': len(self._orchestrators),
            'enabled': len([o for o in self._orchestrators.values() if o.enabled]),
            'disabled': len([o for o in self._orchestrators.values() if not o.enabled]),
            'orchestrators': {}
        }
        
        for id, metadata in self._orchestrators.items():
            try:
                # Try to import module
                import importlib
                module = importlib.import_module(metadata.module_path)
                class_obj = getattr(module, metadata.class_name)
                
                results['orchestrators'][id] = {
                    'status': 'healthy',
                    'enabled': metadata.enabled,
                    'version': metadata.version,
                    'class_found': True
                }
            except ImportError as e:
                results['orchestrators'][id] = {
                    'status': 'error',
                    'enabled': metadata.enabled,
                    'error': f"Import error: {str(e)}",
                    'class_found': False
                }
            except AttributeError as e:
                results['orchestrators'][id] = {
                    'status': 'error',
                    'enabled': metadata.enabled,
                    'error': f"Class not found: {str(e)}",
                    'class_found': False
                }
        
        return results
    
    def _save_to_disk(self) -> None:
        """Persist registry to JSON file."""
        if not self.registry_path:
            return
        
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            id: metadata.to_dict()
            for id, metadata in self._orchestrators.items()
        }
        
        with open(self.registry_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        self.logger.debug(f"Registry saved to {self.registry_path}")
    
    def _load_from_disk(self) -> None:
        """Load registry from JSON file."""
        if not self.registry_path or not self.registry_path.exists():
            return
        
        with open(self.registry_path, 'r') as f:
            data = json.load(f)
        
        for id, metadata_dict in data.items():
            self._orchestrators[id] = OrchestratorMetadata.from_dict(metadata_dict)
        
        self.logger.info(f"Loaded {len(self._orchestrators)} orchestrators from {self.registry_path}")
    
    def export_to_yaml(self, output_path: str) -> None:
        """
        Export registry to YAML format.
        
        Args:
            output_path: Path to output YAML file
        """
        import yaml
        
        data = {
            id: metadata.to_dict()
            for id, metadata in self._orchestrators.items()
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        self.logger.info(f"Registry exported to {output_path}")
