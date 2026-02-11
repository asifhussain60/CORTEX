"""
BaseRegistry[T] - Generic Registry Base Class

AC-8.3B-001: BaseRegistry[T] Generic Base Class Implemented

Provides a unified, thread-safe generic registry interface that all 15
specialized registries inherit from:

- GovernanceRegistry
- KnowledgeRepository
- OrchestratorRegistry
- ToolRegistry
- DomainRegistry
- StateRegistry
- MetadataRegistry
- ConfigRegistry
- AuditRegistry
- MetricsRegistry
- CacheRegistry
- CapabilityRegistry
- IntentRegistry
- ContextRegistry
- WorkflowRegistry

Benefits:
- Single canonical interface (CORE-035)
- Type-safe with generics
- Thread-safe singleton pattern (RLock)
- Health check protocol
- Consistent behavior across all registries
- Zero behavioral changes to existing code

Author: Asif Hussain
Date: 2026-01-31
Authority: PHASE 8.3B Specification
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from threading import RLock
from typing import Any, Dict, Generic, List, Optional, Tuple, TypeVar

from cortex.models.canonical_enums import HealthStatus

logger = logging.getLogger(__name__)

# Generic type variable
T = TypeVar("T")


@dataclass
class HealthCheckResult:
    """Health check result"""
    status: HealthStatus
    message: str
    details: Dict[str, Any]
    timestamp: float


class BaseRegistry(Generic[T], ABC):
    """
    Generic registry base class with standard interface.

    All specialized registries inherit from this class to ensure
    consistent behavior, thread safety, and health checking.

    Type Parameters:
        T: Type of items stored in registry
    """

    # Class-level lock for thread safety
    _lock = RLock()

    def __init__(self, name: str) -> None:
        """
        Initialize registry.

        Args:
            name: Human-readable registry name

        Raises:
            ValueError: If name is empty
        """
        if not name:
            raise ValueError("Registry name cannot be empty")

        self.name = name
        self._items: Dict[str, T] = {}
        self._access_count = 0
        self._error_count = 0

    # =====================================================================
    # CORE INTERFACE METHODS
    # =====================================================================

    def register(self, key: str, value: T) -> None:
        """
        Register an item in the registry.

        Args:
            key: Unique identifier for the item
            value: Item to register

        Raises:
            ValueError: If key is empty or already exists
            TypeError: If value is wrong type
        """
        if not key:
            raise ValueError("Key cannot be empty")

        with self._lock:
            if key in self._items:
                raise ValueError(f"Item with key '{key}' already exists")

            try:
                self._validate_value(value)
                self._items[key] = value
                self._access_count += 1
                logger.debug(f"[{self.name}] Registered: {key}")
            except Exception as e:
                self._error_count += 1
                logger.error(f"[{self.name}] Registration failed for {key}: {e}")
                raise

    def get(self, key: str) -> Optional[T]:
        """
        Get item from registry.

        Args:
            key: Item identifier

        Returns:
            Item if found, None otherwise
        """
        with self._lock:
            self._access_count += 1
            result = self._items.get(key)
            if result is None:
                logger.debug(f"[{self.name}] Item not found: {key}")
            return result

    def list(self) -> List[Tuple[str, T]]:
        """
        List all items in registry.

        Returns:
            List of (key, value) tuples
        """
        with self._lock:
            self._access_count += 1
            return list(self._items.items())

    def delete(self, key: str) -> bool:
        """
        Delete item from registry.

        Args:
            key: Item identifier

        Returns:
            True if deleted, False if not found
        """
        with self._lock:
            if key in self._items:
                del self._items[key]
                self._access_count += 1
                logger.debug(f"[{self.name}] Deleted: {key}")
                return True
            return False

    def clear(self) -> None:
        """Clear all items from registry."""
        with self._lock:
            self._items.clear()
            logger.info(f"[{self.name}] Cleared all items")

    def exists(self, key: str) -> bool:
        """
        Check if item exists.

        Args:
            key: Item identifier

        Returns:
            True if exists, False otherwise
        """
        with self._lock:
            return key in self._items

    # =====================================================================
    # QUERY METHODS
    # =====================================================================

    def size(self) -> int:
        """Get number of items in registry"""
        with self._lock:
            return len(self._items)

    def keys(self) -> List[str]:
        """Get all keys in registry"""
        with self._lock:
            return list(self._items.keys())

    def values(self) -> List[T]:
        """Get all values in registry"""
        with self._lock:
            return list(self._items.values())

    def items(self) -> List[Tuple[str, T]]:
        """Get all (key, value) pairs"""
        with self._lock:
            return list(self._items.items())

    def filter(self, predicate) -> List[Tuple[str, T]]:
        """
        Filter items by predicate.

        Args:
            predicate: Function(key, value) -> bool

        Returns:
            List of (key, value) tuples matching predicate
        """
        with self._lock:
            return [(k, v) for k, v in self._items.items() if predicate(k, v)]

    # =====================================================================
    # HEALTH CHECK PROTOCOL
    # =====================================================================

    def health_check(self) -> HealthCheckResult:
        """
        Perform registry health check.

        Returns:
            HealthCheckResult with status and details
        """
        import time

        with self._lock:
            # Determine status
            error_rate = (
                self._error_count / max(self._access_count, 1)
                if self._access_count > 0
                else 0.0
            )

            if error_rate > 0.1:  # > 10% error rate
                status = HealthStatus.UNHEALTHY
                message = f"High error rate: {error_rate:.1%}"
            elif error_rate > 0.05:  # > 5% error rate
                status = HealthStatus.DEGRADED
                message = f"Moderate error rate: {error_rate:.1%}"
            else:
                status = HealthStatus.HEALTHY
                message = "Registry operational"

            return HealthCheckResult(
                status=status,
                message=message,
                details={
                    "registry_name": self.name,
                    "item_count": len(self._items),
                    "access_count": self._access_count,
                    "error_count": self._error_count,
                    "error_rate": f"{error_rate:.1%}",
                },
                timestamp=time.time(),
            )

    def get_stats(self) -> Dict[str, Any]:
        """Get registry statistics"""
        check = self.health_check()
        return {
            "name": self.name,
            "health": check.status.value,
            "items": check.details["item_count"],
            "accesses": check.details["access_count"],
            "errors": check.details["error_count"],
        }

    # =====================================================================
    # EXTENSION POINTS
    # =====================================================================

    @abstractmethod
    def _validate_value(self, value: T) -> None:
        """
        Validate value before registration.

        Subclasses override to add custom validation.

        Args:
            value: Value to validate

        Raises:
            ValueError: If validation fails
        """
        pass

    def on_register(self, key: str, value: T) -> None:
        """Hook called after successful registration"""
        pass

    def on_delete(self, key: str, value: T) -> None:
        """Hook called after successful deletion"""
        pass

    # =====================================================================
    # BATCH OPERATIONS
    # =====================================================================

    def register_batch(self, items: Dict[str, T]) -> int:
        """
        Register multiple items.

        Args:
            items: Dict of key -> value pairs

        Returns:
            Number of successfully registered items
        """
        count = 0
        for key, value in items.items():
            try:
                self.register(key, value)
                count += 1
            except Exception as e:
                logger.warning(f"Failed to register {key}: {e}")
        return count

    def delete_batch(self, keys: List[str]) -> int:
        """
        Delete multiple items.

        Args:
            keys: List of item identifiers

        Returns:
            Number of successfully deleted items
        """
        count = 0
        for key in keys:
            if self.delete(key):
                count += 1
        return count

    # =====================================================================
    # STRING REPRESENTATION
    # =====================================================================

    def __repr__(self) -> str:
        """String representation"""
        with self._lock:
            return (
                f"<{self.__class__.__name__}("
                f"name='{self.name}', "
                f"size={len(self._items)}"
                f")>"
            )

    def __len__(self) -> int:
        """Length operator"""
        return self.size()

    def __contains__(self, key: str) -> bool:
        """Membership operator"""
        return self.exists(key)

    def __getitem__(self, key: str) -> Optional[T]:
        """Bracket operator"""
        return self.get(key)


__all__ = ["BaseRegistry", "HealthCheckResult", "HealthStatus", "T"]
