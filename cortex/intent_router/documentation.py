"""Documentation Module - Framework documentation integration.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DocumentationEntry:
    """Documentation entry."""
    title: str
    content: str
    category: str = "general"
    tags: List[str] = field(default_factory=list)


class DocumentationManager:
    """Manages framework documentation."""
    
    def __init__(self):
        """Initialize documentation manager."""
        self.entries: Dict[str, DocumentationEntry] = {}
    
    def add_entry(self, key: str, entry: DocumentationEntry) -> None:
        """Add documentation entry.
        
        Args:
            key: Unique key for the entry
            entry: DocumentationEntry to add
        """
        self.entries[key] = entry
    
    def get_entry(self, key: str) -> Optional[DocumentationEntry]:
        """Get documentation entry.
        
        Args:
            key: Key of the entry to retrieve
            
        Returns:
            DocumentationEntry if found, None otherwise
        """
        return self.entries.get(key)
    
    def search(self, query: str) -> List[DocumentationEntry]:
        """Search documentation.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching DocumentationEntry objects
        """
        return [
            entry for entry in self.entries.values()
            if query.lower() in entry.content.lower() or query.lower() in entry.title.lower()
        ]


def get_documentation() -> Dict[str, Any]:
    """Get framework documentation.
    
    Returns:
        Dictionary containing framework documentation
    """
    manager = DocumentationManager()
    return {
        "manager": manager,
        "version": "1.0",
        "entries": list(manager.entries.values())
    }


__all__ = ["DocumentationEntry", "DocumentationManager", "get_documentation"]
