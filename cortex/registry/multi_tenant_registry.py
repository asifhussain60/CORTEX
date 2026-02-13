"""
Phase 48-registry Stage 2: Multi-Tenant Registry - Workspace-Aware YAML Loader

Authority: phase-48-registry-isolation.yaml
AC-IDs: AC-PHASE48-REG-S2-001 through AC-PHASE48-REG-S2-005

Multi-tenant registry loader with:
- Workspace-specific YAML loading (cortex-registry/{workspace_id}/)
- Fallback to global registry (_cortex-master/) for shared resources
- Per-tenant caching (≥70% hit rate target)
- Zero cross-tenant data leakage
- Backward compatibility with single-tenant mode

Example:
    # Multi-tenant mode
    >>> registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
    >>> data = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
    # Loads from cortex-registry/acme-dev/ first, falls back to _cortex-master/
    
    # Single-tenant mode (backward compatible)
    >>> registry = MultiTenantRegistry()  # Defaults to workspace_id="local"
    >>> data = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
    # Loads from cortex-registry/_cortex-master/ directly
"""

# AC_START: AC-PHASE48-REG-S2-001
# Description: Multi-tenant registry loader with workspace-specific YAML loading
# Stage: Phase 48-registry S2

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MultiTenantRegistry:
    """
    Workspace-aware registry loader with tenant isolation.
    
    Provides:
    - Load YAML from cortex-registry/{workspace_id}/ first
    - Fallback to cortex-registry/_cortex-master/ for shared resources
    - Per-tenant caching with ≥70% hit rate
    - Zero cross-tenant data leakage
    
    Attributes:
        workspace_id: Unique workspace identifier (default: "local")
        tenant_id: Tenant identifier (default: "local")
        registry_root: Root path to cortex-registry/ directory
        
    Example:
        >>> # Multi-tenant workspace
        >>> registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
        >>> data = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
        
        >>> # Single-tenant mode (backward compatible)
        >>> registry = MultiTenantRegistry()
        >>> data = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
    """
    
    def __init__(
        self,
        workspace_id: str = "local",
        tenant_id: Optional[str] = None,
        registry_root: Optional[Path] = None
    ) -> None:
        """
        Initialize multi-tenant registry.
        
        Args:
            workspace_id: Workspace identifier (default: "local" for single-tenant mode)
            tenant_id: Tenant identifier (default: same as workspace_id)
            registry_root: Root path to registry (default: cortex-registry/)
        """
        self.workspace_id = workspace_id
        self.tenant_id = tenant_id or workspace_id
        self.registry_root = registry_root or Path("cortex-registry")
        
        # Per-tenant cache
        self._cache: Dict[str, Any] = {}
        self._cache_hits = 0
        self._cache_misses = 0
        
        logger.debug(
            f"MultiTenantRegistry initialized: workspace_id={workspace_id}, "
            f"tenant_id={self.tenant_id}"
        )
    
    def load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Load YAML from workspace-specific or global registry.
        
        Load order:
        1. cortex-registry/{workspace_id}/{file_path} (workspace-specific)
        2. cortex-registry/_cortex-master/{file_path} (global fallback)
        
        Args:
            file_path: Relative path within registry (e.g., "agents/core/tdd-orchestrator.yaml")
        
        Returns:
            Parsed YAML content as dict
        
        Raises:
            FileNotFoundError: If file not found in workspace or global registry
        
        Example:
            >>> registry = MultiTenantRegistry(workspace_id="acme-dev")
            >>> data = registry.load_yaml("agents/core/tdd-orchestrator.yaml")
            >>> print(data["orchestrator_name"])
        """
        # Check cache first
        cache_key = self.get_cache_key(file_path)
        if cache_key in self._cache:
            self._cache_hits += 1
            logger.debug(f"Cache HIT: {cache_key}")
            return self._cache[cache_key]
        
        self._cache_misses += 1
        logger.debug(f"Cache MISS: {cache_key}")
        
        # Try workspace-specific registry first (if not local mode)
        if self.workspace_id != "local":
            workspace_path = self.registry_root / self.workspace_id / file_path
            if workspace_path.exists():
                logger.info(f"Loading from workspace registry: {workspace_path}")
                data = self._load_yaml_file(workspace_path)
                self._cache[cache_key] = data
                return data
        
        # Fallback to global registry (_cortex-master/)
        global_path = self.registry_root / "_cortex-master" / file_path
        if global_path.exists():
            logger.info(f"Loading from global registry: {global_path}")
            data = self._load_yaml_file(global_path)
            self._cache[cache_key] = data
            return data
        
        # File not found anywhere
        raise FileNotFoundError(
            f"File not found in workspace or global registry: {file_path}\n"
            f"Searched paths:\n"
            f"  - {self.registry_root / self.workspace_id / file_path}\n"
            f"  - {self.registry_root / '_cortex-master' / file_path}"
        )
    
    def _load_yaml_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Load and parse YAML file.
        
        Args:
            file_path: Absolute path to YAML file
        
        Returns:
            Parsed YAML content as dict
        
        Raises:
            yaml.YAMLError: If YAML parsing fails
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data is not None else {}
        except yaml.YAMLError as e:
            logger.error(f"YAML parsing error in {file_path}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading file {file_path}: {e}")
            raise
    
    def get_cache_key(self, file_path: str) -> str:
        """
        Generate cache key for workspace+tenant+file.
        
        Args:
            file_path: Relative file path
        
        Returns:
            Cache key string (format: "workspace_id:tenant_id:file_path")
        
        Example:
            >>> registry = MultiTenantRegistry(workspace_id="acme-dev", tenant_id="acme")
            >>> key = registry.get_cache_key("agents/core/tdd.yaml")
            >>> print(key)
            acme-dev:acme:agents/core/tdd.yaml
        """
        return f"{self.workspace_id}:{self.tenant_id}:{file_path}"
    
    def get_cache_hit_rate(self) -> float:
        """
        Calculate cache hit rate.
        
        Returns:
            Hit rate as float (0.0 to 1.0)
        
        Example:
            >>> registry = MultiTenantRegistry()
            >>> # After some loads...
            >>> hit_rate = registry.get_cache_hit_rate()
            >>> print(f"Cache hit rate: {hit_rate:.2%}")
        """
        total = self._cache_hits + self._cache_misses
        if total == 0:
            return 0.0
        return self._cache_hits / total
    
    def clear_cache(self) -> None:
        """
        Clear cache for this registry instance.
        
        Resets:
        - Cached data
        - Hit/miss counters
        
        Example:
            >>> registry = MultiTenantRegistry()
            >>> registry.clear_cache()
            >>> assert len(registry._cache) == 0
        """
        self._cache.clear()
        self._cache_hits = 0
        self._cache_misses = 0
        logger.debug(f"Cache cleared for workspace_id={self.workspace_id}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.
        
        Returns:
            Dict with cache metrics (hits, misses, size, hit_rate)
        
        Example:
            >>> registry = MultiTenantRegistry()
            >>> stats = registry.get_cache_stats()
            >>> print(f"Hit rate: {stats['hit_rate']:.2%}")
        """
        return {
            "hits": self._cache_hits,
            "misses": self._cache_misses,
            "size": len(self._cache),
            "hit_rate": self.get_cache_hit_rate()
        }
    
    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"MultiTenantRegistry(workspace_id={self.workspace_id!r}, "
            f"tenant_id={self.tenant_id!r}, "
            f"cache_size={len(self._cache)})"
        )


# AC_COMPLETE: AC-PHASE48-REG-S2-001 ✅ Multi-tenant registry loader with workspace-specific YAML loading
