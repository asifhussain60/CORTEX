"""
Git-Backed Orchestrator Registry - Single source of truth from YAML.

Authority: _workspaces/docker-plan/migration-phases-plan.yaml (Phase 3)
Rule: CORE-035 (Single Canonical Implementation)
"""

from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml
import hashlib
import logging

from cortex.wiring.registry.lazy_orchestrator import LazyOrchestrator

logger = logging.getLogger(__name__)


class GitBackedRegistry:
    """
    Load orchestrator wiring from Git-tracked YAML file.
    
    Key features:
    - Single source of truth (wiring.yaml)
    - Git-tracked and diff-able
    - No SQLite databases
    - Lazy loading for fast startup
    - Dependency resolution
    - Circular dependency detection
    
    Example:
        >>> registry = GitBackedRegistry()
        >>> registry.load()
        >>> orch = registry.get_orchestrator("TDDOrchestrator")
        >>> orchestrators = registry.list_orchestrators()
    """
    
    def __init__(self, wiring_file: Optional[Path] = None) -> None:
        """
        Initialize registry.
        
        Args:
            wiring_file: Path to wiring.yaml (default: cortex/wiring/specifications/wiring.yaml)
        """
        if wiring_file is None:
            wiring_file = Path("cortex/wiring/specifications/wiring.yaml")
        
        self.wiring_file = wiring_file
        self._orchestrators: Dict[str, LazyOrchestrator] = {}
        self._spec: Optional[Dict[str, Any]] = None
        self._loaded = False
        
    def load(self) -> None:
        """
        Load orchestrator specifications from YAML.
        
        Raises:
            FileNotFoundError: If wiring.yaml not found
            yaml.YAMLError: If YAML is invalid
            ValueError: If specification is malformed
        """
        if self._loaded:
            logger.debug("Registry already loaded")
            return
            
        logger.info(f"Loading orchestrator wiring from {self.wiring_file}")
        
        if not self.wiring_file.exists():
            raise FileNotFoundError(
                f"Wiring specification not found: {self.wiring_file}. "
                f"Run Phase 3 migration to create it."
            )
        
        try:
            with open(self.wiring_file, 'r') as f:
                self._spec = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Invalid YAML in {self.wiring_file}: {e}")
        
        if not self._spec or 'orchestrators' not in self._spec:
            raise ValueError(f"Invalid wiring specification: missing 'orchestrators' key")
        
        # Load orchestrators from all categories
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                logger.warning(f"No {category} orchestrators defined")
                continue
                
            for orch_spec in self._spec['orchestrators'][category]:
                self._register_orchestrator(orch_spec, category)
        
        self._loaded = True
        logger.info(f"✅ Loaded {len(self._orchestrators)} orchestrators from {self.wiring_file}")
    
    def _register_orchestrator(self, spec: Dict[str, Any], category: str) -> None:
        """
        Register a single orchestrator from specification.
        
        Args:
            spec: Orchestrator specification dict
            category: Category (core/domain/support)
        """
        name = spec.get('name')
        if not name:
            logger.warning(f"Skipping orchestrator with no name in {category}")
            return
        
        module_path = spec.get('module')
        class_name = spec.get('class')
        
        if not module_path or not class_name:
            logger.warning(f"Skipping {name}: missing module or class")
            return
        
        lazy_orch = LazyOrchestrator(
            name=name,
            module_path=module_path,
            class_name=class_name,
            dependencies=spec.get('dependencies', []),
            required_params=spec.get('requires_params', {})
        )
        
        self._orchestrators[name] = lazy_orch
        logger.debug(f"Registered {category} orchestrator: {name}")
    
    def get_orchestrator(self, name: str) -> Optional[Any]:
        """
        Get orchestrator by name (lazy-loads on first access).
        
        Args:
            name: Orchestrator name (e.g., "TDDOrchestrator")
            
        Returns:
            Orchestrator instance or None if not found
        """
        if not self._loaded:
            self.load()
        
        lazy_orch = self._orchestrators.get(name)
        if lazy_orch is None:
            logger.warning(f"Orchestrator not found: {name}")
            return None
        
        try:
            return lazy_orch.instance(registry=self)
        except Exception as e:
            logger.error(f"Failed to load {name}: {e}")
            return None
    
    def list_orchestrators(self) -> List[str]:
        """
        List all registered orchestrator names.
        
        Returns:
            List of orchestrator names
        """
        if not self._loaded:
            self.load()
        
        return list(self._orchestrators.keys())
    
    def get_all_orchestrators(self) -> Dict[str, Any]:
        """
        Get all orchestrators as a dict (lazy-loads each on access).
        
        Returns:
            Dict mapping orchestrator names to LazyOrchestrator proxies
        """
        if not self._loaded:
            self.load()
        
        return dict(self._orchestrators)
    
    def get_wiring_hash(self) -> str:
        """
        Compute hash of wiring.yaml for change detection.
        
        Returns:
            SHA256 hash (16 chars) of wiring specification
        """
        if not self.wiring_file.exists():
            return "no-wiring-file"
        
        try:
            with open(self.wiring_file, 'rb') as f:
                content = f.read()
                return hashlib.sha256(content).hexdigest()[:16]
        except Exception as e:
            logger.error(f"Failed to compute wiring hash: {e}")
            return "hash-error"
    
    def is_wired(self) -> bool:
        """Check if registry has been loaded."""
        return self._loaded
    
    @property
    def orchestrator_count(self) -> int:
        """Get count of registered orchestrators."""
        if not self._loaded:
            self.load()
        return len(self._orchestrators)
    
    def get_orchestrator_spec(self, name: str) -> Optional[Dict[str, Any]]:
        """
        Get raw specification for an orchestrator.
        
        Args:
            name: Orchestrator name
            
        Returns:
            Specification dict or None
        """
        if not self._loaded:
            self.load()
        
        # Search in all categories
        for category in ['core', 'domain', 'support']:
            if category not in self._spec['orchestrators']:
                continue
            for orch_spec in self._spec['orchestrators'][category]:
                if orch_spec.get('name') == name:
                    return orch_spec
        
        return None
    
    def validate(self) -> List[str]:
        """
        Validate wiring specification for common issues.
        
        Returns:
            List of validation errors (empty if valid)
        """
        if not self._loaded:
            self.load()
        
        errors: List[str] = []
        
        # Check for circular dependencies
        def has_cycle(node: str, visited: set, rec_stack: set) -> bool:
            visited.add(node)
            rec_stack.add(node)
            
            lazy_orch = self._orchestrators.get(node)
            if lazy_orch:
                for dep in lazy_orch.dependencies:
                    if dep not in visited:
                        if has_cycle(dep, visited, rec_stack):
                            return True
                    elif dep in rec_stack:
                        errors.append(f"Circular dependency: {node} -> {dep}")
                        return True
            
            rec_stack.remove(node)
            return False
        
        visited: set = set()
        for name in self._orchestrators:
            if name not in visited:
                has_cycle(name, visited, set())
        
        # Check all dependencies exist
        for name, lazy_orch in self._orchestrators.items():
            for dep in lazy_orch.dependencies:
                if dep not in self._orchestrators:
                    errors.append(f"{name} depends on non-existent orchestrator: {dep}")
        
        return errors


# Singleton instance
_registry: Optional[GitBackedRegistry] = None


def get_registry() -> GitBackedRegistry:
    """
    Get singleton registry instance.
    
    Returns:
        GitBackedRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = GitBackedRegistry()
        _registry.load()
    return _registry


def reset_registry() -> None:
    """Reset singleton registry (for testing)."""
    global _registry
    _registry = None
