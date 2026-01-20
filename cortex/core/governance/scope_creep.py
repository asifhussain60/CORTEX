"""Scope creep detection and prevention."""

from typing import Dict, List, Any, Set
from datetime import datetime


class ScopeCreepDetector:
    """Detect and prevent scope creep."""
    
    def __init__(self):
        self.original_scope: Set[str] = set()
        self.current_scope: Set[str] = set()
        self.scope_changes: List[Dict[str, Any]] = []
    
    def set_original_scope(self, scope_items: List[str]) -> None:
        """Set original project scope."""
        self.original_scope = set(scope_items)
        self.current_scope = set(scope_items)
    
    def propose_addition(self, item: str) -> bool:
        """Propose scope addition."""
        if item in self.original_scope:
            return False
        
        self.scope_changes.append({
            "type": "addition",
            "item": item,
            "timestamp": datetime.now()
        })
        return True
    
    def detect_creep(self) -> Dict[str, Any]:
        """Detect scope creep."""
        additions = [c for c in self.scope_changes if c["type"] == "addition"]
        
        return {
            "has_creep": len(additions) > 0,
            "additions_count": len(additions),
            "creep_percentage": (len(additions) / len(self.original_scope) * 100) if self.original_scope else 0
        }
