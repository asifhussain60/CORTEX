"""
Component Bulkhead Isolation Manager.

AC-INFRA-001-02: Implements bulkhead pattern for component isolation.
Each component gets dedicated connection pool with independent limits,
timeouts, and circuit breakers to prevent cascading failures.
"""

import sqlite3
import threading
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Optional, Any

from cortex.infrastructure.connection_pool import (
from cortex.models.canonical_enums import ComponentHealth
    ConnectionPool,
    ConnectionPoolConfig,
    PoolExhaustedError,
)


class ComponentType(str, Enum):
    """Types of components with isolated resources."""
    GOVERNANCE = "governance"
    AUDIT = "audit"
    KNOWLEDGE = "knowledge"




class BulkheadException(Exception):
    """Raised when bulkhead operation fails."""
    pass


@dataclass
class BulkheadConfig:
    """Configuration for bulkhead isolation."""
    
    component_pools: Dict[ComponentType, Dict[str, Any]] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Validate configuration."""
        if not self.component_pools:
            # Default configuration
            self.component_pools = {
                ComponentType.GOVERNANCE: {
                    "max_connections": 5,
                    "timeout": 1.0,
                },
                ComponentType.AUDIT: {
                    "max_connections": 3,
                    "timeout": 5.0,
                },
                ComponentType.KNOWLEDGE: {
                    "max_connections": 10,
                    "timeout": 10.0,
                },
            }


class BulkheadManager:
    """
    Manages component-level resource isolation using bulkhead pattern.
    
    Each component gets:
    - Dedicated connection pool
    - Independent timeout settings
    - Separate circuit breaker
    - Isolated failure domain
    
    This prevents failures in one component from cascading to others.
    
    Example:
        >>> config = BulkheadConfig(component_pools={
        ...     ComponentType.GOVERNANCE: {"max_connections": 5, "timeout": 1.0}
        ... })
        >>> manager = BulkheadManager(Path("db.sqlite"), config)
        >>> conn = manager.acquire_connection(ComponentType.GOVERNANCE)
        >>> manager.release_connection(ComponentType.GOVERNANCE, conn)
        >>> manager.shutdown()
    """
    
    def __init__(
        self,
        database_path: Path,
        config: Optional[BulkheadConfig] = None,
    ) -> None:
        """
        Initialize bulkhead manager.
        
        Args:
            database_path: Path to SQLite database
            config: Bulkhead configuration (uses defaults if None)
        """
        self.database_path = database_path
        self.config = config or BulkheadConfig()
        
        self._lock = threading.RLock()
        self._pools: Dict[ComponentType, ConnectionPool] = {}
        self._circuit_breakers: Dict[ComponentType, str] = {}
        self._health_status: Dict[ComponentType, ComponentHealth] = {}
        self._shutdown_flag = False
        
        # Initialize pools for each component
        self._initialize_pools()
    
    def _initialize_pools(self) -> None:
        """Create connection pools for each component."""
        for component_type, pool_config in self.config.component_pools.items():
            max_conn = pool_config.get("max_connections", 5)
            timeout = pool_config.get("timeout", 5.0)
            
            # Create pool with component-specific limits
            pool_config_obj = ConnectionPoolConfig(
                min_connections=max(1, max_conn // 2),
                max_connections=max_conn,
                connection_timeout_seconds=timeout,
                idle_timeout_seconds=300.0,
                health_check_enabled=True,
            )
            
            self._pools[component_type] = ConnectionPool(
                database_path=self.database_path,
                config=pool_config_obj,
            )
            
            # Initialize circuit breaker and health
            self._circuit_breakers[component_type] = "CLOSED"
            self._health_status[component_type] = ComponentHealth.HEALTHY
    
    def acquire_connection(
        self,
        component_type: ComponentType,
        timeout: Optional[float] = None,
    ) -> sqlite3.Connection:
        """
        Acquire a connection for a specific component.
        
        Args:
            component_type: Type of component requesting connection
            timeout: Override default timeout for this acquisition
            
        Returns:
            Database connection
            
        Raises:
            BulkheadException: If acquisition fails or pool exhausted
            RuntimeError: If manager is shutdown
        """
        if self._shutdown_flag:
            raise RuntimeError("Bulkhead manager is shutdown")
        
        pool = self._pools.get(component_type)
        if pool is None:
            raise BulkheadException(f"No pool configured for {component_type}")
        
        # Use component-specific timeout if not overridden
        if timeout is None:
            timeout = self.config.component_pools[component_type]["timeout"]
        
        try:
            return pool.acquire(timeout=timeout)
        except PoolExhaustedError as e:
            # Update health status on exhaustion
            with self._lock:
                if self._health_status[component_type] == ComponentHealth.HEALTHY:
                    self._health_status[component_type] = ComponentHealth.DEGRADED
            raise BulkheadException(f"Component {component_type} pool exhausted: {e}") from e
    
    def release_connection(
        self,
        component_type: ComponentType,
        connection: sqlite3.Connection,
    ) -> None:
        """
        Release a connection back to component pool.
        
        Args:
            component_type: Type of component releasing connection
            connection: Connection to release
        """
        if self._shutdown_flag:
            return
        
        pool = self._pools.get(component_type)
        if pool is None:
            return
        
        try:
            pool.release(connection)
            
            # Update health on successful release
            with self._lock:
                if self._health_status[component_type] == ComponentHealth.DEGRADED:
                    # Check if pool is no longer exhausted
                    metrics = pool.get_metrics()
                    if metrics["idle"] > 0:
                        self._health_status[component_type] = ComponentHealth.HEALTHY
        except Exception:
            # Don't propagate release errors
            pass
    
    def get_health_status(self) -> Dict[ComponentType, ComponentHealth]:
        """
        Get health status of all components.
        
        Returns:
            Dictionary mapping component type to health status
        """
        with self._lock:
            return self._health_status.copy()
    
    def get_component_metrics(self, component_type: ComponentType) -> Dict[str, Any]:
        """
        Get metrics for a specific component.
        
        Args:
            component_type: Component to get metrics for
            
        Returns:
            Dictionary with metrics including active, idle, total connections
        """
        pool = self._pools.get(component_type)
        if pool is None:
            return {}
        
        metrics = pool.get_metrics()
        
        # Add component-specific config
        component_config = self.config.component_pools.get(component_type, {})
        metrics["max_connections"] = component_config.get("max_connections", 0)
        metrics["timeout_seconds"] = component_config.get("timeout", 0.0)
        
        return metrics
    
    def get_circuit_breaker_states(self) -> Dict[ComponentType, str]:
        """
        Get circuit breaker states for all components.
        
        Returns:
            Dictionary mapping component type to circuit breaker state
            
        Note:
            Circuit breaker implementation is in AC-INFRA-001-03.
            Currently returns "CLOSED" for all components.
        """
        with self._lock:
            return self._circuit_breakers.copy()
    
    def shutdown(self, timeout: float = 5.0) -> None:
        """
        Shutdown bulkhead manager and all component pools.
        
        Args:
            timeout: Maximum time to wait for shutdown per pool
        """
        with self._lock:
            self._shutdown_flag = True
            
            # Shutdown all pools
            for pool in self._pools.values():
                try:
                    pool.shutdown(timeout=timeout)
                except Exception:
                    pass  # Best effort shutdown
            
            self._pools.clear()
            self._circuit_breakers.clear()
            self._health_status.clear()
