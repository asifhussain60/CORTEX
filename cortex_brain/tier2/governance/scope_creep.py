"""Tier2 Governance: Scope Creep

Author: CORTEX Framework
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class ScopeStatus(Enum):
    """Scope status."""
    WITHIN_SCOPE = "within_scope"
    AT_LIMIT = "at_limit"
    EXCEEDED = "exceeded"
    CREEPING = "creeping"


@dataclass
class ScopeItem:
    """Scope item.
    
    Attributes:
        name: Item name
        effort: Effort estimate
        description: Item description
        cost: Item cost
    """
    name: str
    effort: float
    description: str = ""
    cost: float = 0.0
    
    # Support legacy API
    item_id: str = None
    
    def __post_init__(self):
        """Initialize item_id from name for backward compatibility."""
        if self.item_id is None:
            self.item_id = self.name


class ScopeManager:
    """Manage scope creep.
    
    Attributes:
        original_scope: Items in original approved scope
        current_scope: All items in current scope
        max_scope: Maximum allowed scope size
    """
    
    def __init__(self, max_scope: int = 100):
        """Initialize scope manager.
        
        Args:
            max_scope: Maximum allowed scope size
        """
        self.max_scope = max_scope
        self.original_scope: List[ScopeItem] = []
        self.current_scope: List[ScopeItem] = []
        # Keep added_items for backward compatibility
        self.added_items: List[ScopeItem] = []
    
    def define_scope(self, items: List[ScopeItem]) -> None:
        """Define initial project scope.
        
        Args:
            items: List of scope items
        """
        self.original_scope = items.copy()
        self.current_scope = items.copy()
        self.added_items = []
    
    def add_item(self, item: ScopeItem) -> ScopeStatus:
        """Add item to scope.
        
        Args:
            item: Item to add
            
        Returns:
            ScopeStatus indicating if within scope
        """
        # Check if item is in original scope
        for scope_item in self.original_scope:
            if scope_item.name == item.name:
                return ScopeStatus.WITHIN_SCOPE
        
        # Item is not in original scope - scope creep
        self.current_scope.append(item)
        self.added_items.append(item)
        return ScopeStatus.CREEPING
    
    def get_creep_percentage(self) -> float:
        """Get scope creep percentage.
        
        Returns:
            Percentage growth in number of scope items
        """
        if not self.original_scope:
            return 0.0
        
        original_count = len(self.original_scope)
        current_count = len(self.current_scope)
        
        return ((current_count - original_count) / original_count) * 100.0
    
    def check_scope(self, current_scope: int) -> bool:
        """Check if current scope is within limit.
        
        Args:
            current_scope: Current scope size
            
        Returns:
            True if within limit
        """
        return current_scope <= self.max_scope


__all__ = ["ScopeStatus", "ScopeItem", "ScopeManager"]
