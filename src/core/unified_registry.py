"""
Unified Registry for CORTEX 4.0 Phase 13.5

Consolidates command, orchestrator, and tool registries into a single unified system.
Provides type-based registration with thread safety, validation, and auto-discovery.

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import logging
import threading
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable
import yaml

logger = logging.getLogger(__name__)


class RegistryItemType(Enum):
    """Types of items that can be registered."""
    COMMAND = "command"
    ORCHESTRATOR = "orchestrator"
    TOOL = "tool"
    WORKSPACE = "workspace"
    VALIDATOR = "validator"
    PLUGIN = "plugin"
    TEMPLATE = "template"
    PARSER = "parser"


@dataclass
class RegistryItem:
    """
    Base class for registry items.
    
    All registered items must have:
    - item_id: Unique identifier
    - item_type: Type of item (command, orchestrator, etc.)
    - metadata: Type-specific data
    """
    item_id: str
    item_type: RegistryItemType
    metadata: Dict[str, Any] = field(default_factory=dict)
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    registered_by: Optional[str] = None  # Plugin/module that registered this
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['item_type'] = self.item_type.value
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'RegistryItem':
        """Create from dictionary."""
        data['item_type'] = RegistryItemType(data['item_type'])
        return cls(**data)


class RegistryConflictError(Exception):
    """Raised when attempting to register duplicate item IDs."""
    pass


class RegistryValidationError(Exception):
    """Raised when item fails validation."""
    pass


class UnifiedRegistry:
    """
    Central registry for all CORTEX components.
    
    Features:
    - Type-based registration (commands, orchestrators, tools, etc.)
    - Thread-safe operations
    - Automatic conflict detection
    - O(1) lookup performance
    - Persistent storage (optional)
    - Auto-discovery support
    - Validation hooks
    
    Design Principles:
    - Single source of truth for all registrations
    - Consistent interface across all item types
    - Backward compatible with existing registries
    - Plugin-friendly (easy to extend)
    
    Usage:
        registry = UnifiedRegistry()
        
        # Register a command
        registry.register(
            item_type=RegistryItemType.COMMAND,
            item_id="/mac",
            metadata={
                "natural_language": "switched to mac",
                "plugin_id": "platform_switch",
                "description": "Switch to macOS environment"
            }
        )
        
        # Retrieve command
        command = registry.get(RegistryItemType.COMMAND, "/mac")
        
        # List all commands
        commands = registry.list(RegistryItemType.COMMAND)
        
        # Unregister
        registry.unregister(RegistryItemType.COMMAND, "/mac")
    """
    
    def __init__(
        self,
        storage_path: Optional[Path] = None,
        enable_persistence: bool = False,
        validators: Optional[Dict[RegistryItemType, Callable]] = None
    ):
        """
        Initialize unified registry.
        
        Args:
            storage_path: Path to persistent storage file (YAML)
            enable_persistence: Whether to auto-save on changes
            validators: Custom validators per item type
        """
        self._items: Dict[RegistryItemType, Dict[str, RegistryItem]] = {
            item_type: {} for item_type in RegistryItemType
        }
        self._lock = threading.RLock()
        self._storage_path = storage_path
        self._enable_persistence = enable_persistence
        self._validators = validators or {}
        
        # Statistics
        self._stats = {
            'total_registrations': 0,
            'total_unregistrations': 0,
            'conflict_detections': 0,
            'validation_failures': 0
        }
        
        # Load from storage if exists
        if self._storage_path and self._storage_path.exists():
            self._load_from_storage()
    
    def register(
        self,
        item_type: RegistryItemType,
        item_id: str,
        metadata: Optional[Dict[str, Any]] = None,
        registered_by: Optional[str] = None,
        allow_override: bool = False
    ) -> bool:
        """
        Register an item in the registry.
        
        Args:
            item_type: Type of item (command, orchestrator, etc.)
            item_id: Unique identifier for the item
            metadata: Type-specific metadata
            registered_by: Plugin/module registering the item
            allow_override: If True, allow overwriting existing items
        
        Returns:
            True if registered successfully
        
        Raises:
            RegistryConflictError: If item_id already registered (unless allow_override)
            RegistryValidationError: If item fails validation
        """
        with self._lock:
            # Check for conflicts
            if not allow_override and item_id in self._items[item_type]:
                self._stats['conflict_detections'] += 1
                raise RegistryConflictError(
                    f"Item already registered: {item_type.value}/{item_id}"
                )
            
            # Create registry item
            item = RegistryItem(
                item_id=item_id,
                item_type=item_type,
                metadata=metadata or {},
                registered_by=registered_by
            )
            
            # Validate if validator exists
            if item_type in self._validators:
                try:
                    if not self._validators[item_type](item):
                        self._stats['validation_failures'] += 1
                        raise RegistryValidationError(
                            f"Validation failed for {item_type.value}/{item_id}"
                        )
                except Exception as e:
                    self._stats['validation_failures'] += 1
                    raise RegistryValidationError(
                        f"Validation error for {item_type.value}/{item_id}: {e}"
                    )
            
            # Register
            self._items[item_type][item_id] = item
            self._stats['total_registrations'] += 1
            
            logger.debug(
                f"Registered {item_type.value}: {item_id}" +
                (f" by {registered_by}" if registered_by else "")
            )
            
            # Persist if enabled
            if self._enable_persistence:
                self._save_to_storage()
            
            return True
    
    def get(
        self,
        item_type: RegistryItemType,
        item_id: str
    ) -> Optional[RegistryItem]:
        """
        Get item from registry.
        
        Args:
            item_type: Type of item
            item_id: Item identifier
        
        Returns:
            RegistryItem or None if not found
        """
        with self._lock:
            return self._items[item_type].get(item_id)
    
    def get_metadata(
        self,
        item_type: RegistryItemType,
        item_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get metadata for item (convenience method).
        
        Args:
            item_type: Type of item
            item_id: Item identifier
        
        Returns:
            Metadata dictionary or None if not found
        """
        item = self.get(item_type, item_id)
        return item.metadata if item else None
    
    def list(
        self,
        item_type: RegistryItemType,
        filter_fn: Optional[Callable[[RegistryItem], bool]] = None
    ) -> List[RegistryItem]:
        """
        List all items of a given type.
        
        Args:
            item_type: Type of items to list
            filter_fn: Optional filter function
        
        Returns:
            List of RegistryItems
        """
        with self._lock:
            items = list(self._items[item_type].values())
            
            if filter_fn:
                items = [item for item in items if filter_fn(item)]
            
            return items
    
    def list_ids(
        self,
        item_type: RegistryItemType,
        filter_fn: Optional[Callable[[RegistryItem], bool]] = None
    ) -> List[str]:
        """
        List all item IDs of a given type (convenience method).
        
        Args:
            item_type: Type of items
            filter_fn: Optional filter function
        
        Returns:
            List of item IDs
        """
        items = self.list(item_type, filter_fn)
        return [item.item_id for item in items]
    
    def unregister(
        self,
        item_type: RegistryItemType,
        item_id: str
    ) -> bool:
        """
        Unregister an item from the registry.
        
        Args:
            item_type: Type of item
            item_id: Item identifier
        
        Returns:
            True if unregistered, False if not found
        """
        with self._lock:
            if item_id in self._items[item_type]:
                del self._items[item_type][item_id]
                self._stats['total_unregistrations'] += 1
                
                logger.debug(f"Unregistered {item_type.value}: {item_id}")
                
                # Persist if enabled
                if self._enable_persistence:
                    self._save_to_storage()
                
                return True
            return False
    
    def exists(
        self,
        item_type: RegistryItemType,
        item_id: str
    ) -> bool:
        """
        Check if item exists in registry.
        
        Args:
            item_type: Type of item
            item_id: Item identifier
        
        Returns:
            True if exists
        """
        with self._lock:
            return item_id in self._items[item_type]
    
    def count(self, item_type: Optional[RegistryItemType] = None) -> int:
        """
        Count registered items.
        
        Args:
            item_type: Type to count (None for all types)
        
        Returns:
            Count of registered items
        """
        with self._lock:
            if item_type:
                return len(self._items[item_type])
            return sum(len(items) for items in self._items.values())
    
    def clear(self, item_type: Optional[RegistryItemType] = None):
        """
        Clear registry.
        
        Args:
            item_type: Type to clear (None for all types)
        """
        with self._lock:
            if item_type:
                self._items[item_type].clear()
            else:
                for items in self._items.values():
                    items.clear()
            
            if self._enable_persistence:
                self._save_to_storage()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get registry statistics.
        
        Returns:
            Statistics dictionary
        """
        with self._lock:
            stats = self._stats.copy()
            stats['items_by_type'] = {
                item_type.value: len(items)
                for item_type, items in self._items.items()
            }
            stats['total_items'] = sum(
                len(items) for items in self._items.values()
            )
            return stats
    
    def _save_to_storage(self):
        """Save registry to persistent storage."""
        if not self._storage_path:
            return
        
        try:
            # Convert to serializable format
            data = {
                'version': '1.0.0',
                'last_saved': datetime.now().isoformat(),
                'items': {}
            }
            
            for item_type, items in self._items.items():
                data['items'][item_type.value] = [
                    item.to_dict() for item in items.values()
                ]
            
            # Ensure directory exists
            self._storage_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write YAML
            with open(self._storage_path, 'w', encoding='utf-8') as f:
                yaml.safe_dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.debug(f"Saved registry to {self._storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")
    
    def _load_from_storage(self):
        """Load registry from persistent storage."""
        if not self._storage_path or not self._storage_path.exists():
            return
        
        try:
            with open(self._storage_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not data or 'items' not in data:
                return
            
            # Load items
            for type_str, items_data in data['items'].items():
                item_type = RegistryItemType(type_str)
                for item_data in items_data:
                    item = RegistryItem.from_dict(item_data)
                    self._items[item_type][item.item_id] = item
            
            logger.info(
                f"Loaded registry from {self._storage_path}: "
                f"{self.count()} items"
            )
        
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")


# Global singleton instance
_registry_instance: Optional[UnifiedRegistry] = None


def get_unified_registry(
    storage_path: Optional[Path] = None,
    enable_persistence: bool = False
) -> UnifiedRegistry:
    """
    Get global unified registry instance (singleton).
    
    Args:
        storage_path: Path to persistent storage (first call only)
        enable_persistence: Enable auto-persistence (first call only)
    
    Returns:
        UnifiedRegistry singleton
    """
    global _registry_instance
    
    if _registry_instance is None:
        _registry_instance = UnifiedRegistry(
            storage_path=storage_path,
            enable_persistence=enable_persistence
        )
    
    return _registry_instance
