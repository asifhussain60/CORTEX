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
        """Add documentation entry."""
        self.entries[key] = entry
    
    def get_entry(self, key: str) -> Optional[DocumentationEntry]:
        """Get documentation entry."""
        return self.entries.get(key)
    
    def search(self, query: str) -> List[DocumentationEntry]:
        """Search documentation."""
        return [
            entry for entry in self.entries.values()
            if query.lower() in entry.content.lower() or query.lower() in entry.title.lower()
        ]


__all__ = ["DocumentationEntry", "DocumentationManager"]
