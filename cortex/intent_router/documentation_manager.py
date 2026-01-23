"""Documentation Manager - Manages documentation for intent router components.

Author: CORTEX Framework
"""

from typing import Dict, Any, List, Optional
from pathlib import Path
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentationEntry:
    """Represents a documentation entry."""
    
    component: str
    title: str
    description: str
    examples: List[str] = field(default_factory=list)
    related_components: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class DocumentationManager:
    """Manages documentation for intent router components."""
    
    def __init__(self) -> None:
        """Initialize documentation manager."""
        self.entries: Dict[str, DocumentationEntry] = {}
        self._indexed: bool = False
    
    def register_component(
        self,
        component: str,
        title: str,
        description: str,
        examples: Optional[List[str]] = None,
        related_components: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register documentation for a component.
        
        Args:
            component: Component name/identifier
            title: Human-readable title
            description: Component description
            examples: List of usage examples
            related_components: List of related component names
            metadata: Additional metadata
        """
        entry = DocumentationEntry(
            component=component,
            title=title,
            description=description,
            examples=examples or [],
            related_components=related_components or [],
            metadata=metadata or {}
        )
        self.entries[component] = entry
        logger.debug(f"Registered documentation for: {component}")
    
    def get_documentation(self, component: str) -> Optional[DocumentationEntry]:
        """Get documentation for a component.
        
        Args:
            component: Component name
            
        Returns:
            DocumentationEntry if found, None otherwise
        """
        return self.entries.get(component)
    
    def search_documentation(self, query: str) -> List[DocumentationEntry]:
        """Search documentation entries.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching documentation entries
        """
        query_lower = query.lower()
        results = []
        
        for entry in self.entries.values():
            if (query_lower in entry.component.lower() or
                query_lower in entry.title.lower() or
                query_lower in entry.description.lower()):
                results.append(entry)
        
        return results
    
    def get_all_components(self) -> List[str]:
        """Get list of all documented components.
        
        Returns:
            List of component names
        """
        return list(self.entries.keys())
    
    def get_related_documentation(self, component: str) -> List[DocumentationEntry]:
        """Get documentation for related components.
        
        Args:
            component: Component name
            
        Returns:
            List of related component documentation
        """
        entry = self.get_documentation(component)
        if not entry:
            return []
        
        related_docs = []
        for related_name in entry.related_components:
            related_entry = self.get_documentation(related_name)
            if related_entry:
                related_docs.append(related_entry)
        
        return related_docs
    
    def export_to_dict(self) -> Dict[str, Dict[str, Any]]:
        """Export all documentation to dictionary format.
        
        Returns:
            Dictionary mapping component names to documentation data
        """
        return {
            name: {
                "component": entry.component,
                "title": entry.title,
                "description": entry.description,
                "examples": entry.examples,
                "related_components": entry.related_components,
                "metadata": entry.metadata
            }
            for name, entry in self.entries.items()
        }
    
    def clear(self) -> None:
        """Clear all documentation entries."""
        self.entries.clear()
        self._indexed = False
