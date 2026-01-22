"""MCP Discovery

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from cortex.mcp.registry import ToolRegistry


@dataclass
class DiscoveryFilter:
    """Filter for tool discovery."""
    tags: Optional[List[str]] = None
    name_contains: Optional[str] = None
    domain: Optional[str] = None
    limit: Optional[int] = None
    include_deprecated: bool = False
    filter_type: Optional[str] = None
    criteria: Optional[dict] = None
    
    def __post_init__(self) -> None:
        """Initialize filter criteria from fields.
        
        Returns:
            None
        """
        if self.criteria is None:
            self.criteria = {}
        
        # Build criteria from fields
        if self.tags is not None:
            self.criteria["tags"] = self.tags
        if self.name_contains is not None:
            self.criteria["name"] = self.name_contains
        if self.domain is not None:
            self.criteria["domain"] = self.domain
        if self.limit is not None:
            self.criteria["limit"] = self.limit
        if self.include_deprecated:
            self.criteria["deprecated"] = True


@dataclass
class DiscoveryMetadata:
    """Metadata about discovery capabilities."""
    supported_filters: List[str] = field(default_factory=list)
    supported_patterns: List[str] = field(default_factory=list)
    version: str = "1.0"
    
    def __post_init__(self) -> None:
        """Initialize metadata with defaults.
        
        Returns:
            None
        """
        if not self.supported_filters:
            self.supported_filters = ["tags", "name", "domain", "limit", "deprecated"]
        if not self.supported_patterns:
            self.supported_patterns = ["list_all", "by_tag", "search", "by_capability", "by_domain"]


class ToolDiscovery:
    """Tool discovery service with registry integration."""
    
    def __init__(self, registry: "ToolRegistry" = None):
        """Initialize discovery service.
        
        Args:
            registry: Tool registry to search.
        """
        self.registry = registry
        self._capabilities: Dict[str, List[str]] = {}  # capability -> tool_ids
        self._domains: Dict[str, List[str]] = {}  # domain -> tool_ids
        self._metadata = DiscoveryMetadata()
    
    def discover_all(self, limit: Optional[int] = None, include_deprecated: bool = False) -> List[Any]:
        """Discover all tools.
        
        Args:
            limit: Maximum number of tools to return.
            include_deprecated: Include deprecated tools.
            
        Returns:
            List of tool definitions.
        """
        if not self.registry:
            return []
        
        tools = self.registry.list_tools(include_deprecated=include_deprecated)
        
        # Convert to definitions
        definitions = []
        for entry in tools:
            from cortex.mcp.protocol import ToolDefinition
            definitions.append(ToolDefinition(
                id=entry.tool_id,
                name=entry.name,
                description=entry.description,
                tags=entry.tags,
                deprecated=entry.deprecated
            ))
        
        if limit is not None:
            definitions = definitions[:limit]
        
        return definitions
    
    def discover_by_tag(self, tag: str) -> List[Any]:
        """Discover tools by tag.
        
        Args:
            tag: Tag to search for.
            
        Returns:
            List of tool definitions with the tag.
        """
        if not self.registry:
            return []
        
        entries = self.registry.find_by_tag(tag)
        
        from cortex.mcp.protocol import ToolDefinition
        return [ToolDefinition(
            id=e.tool_id,
            name=e.name,
            description=e.description,
            tags=e.tags,
            deprecated=e.deprecated
        ) for e in entries]
    
    def search(self, query: str) -> List[Any]:
        """Search tools by name or description.
        
        Args:
            query: Search query (case-insensitive).
            
        Returns:
            List of matching tool definitions.
        """
        if not self.registry:
            return []
        
        query_lower = query.lower()
        results = []
        
        from cortex.mcp.protocol import ToolDefinition
        for entry in self.registry.list_tools():
            if query_lower in entry.name.lower() or query_lower in entry.description.lower():
                results.append(ToolDefinition(
                    id=entry.tool_id,
                    name=entry.name,
                    description=entry.description,
                    tags=entry.tags,
                    deprecated=entry.deprecated
                ))
        
        return results
    
    def discover_with_filter(self, filter_obj: DiscoveryFilter) -> List[Any]:
        """Discover tools with a filter.
        
        Args:
            filter_obj: Filter criteria.
            
        Returns:
            List of matching tool definitions.
        """
        results = self.discover_all(include_deprecated=filter_obj.criteria.get("deprecated", False))
        
        criteria = filter_obj.criteria
        
        # Apply tag filter
        if "tags" in criteria:
            tags = criteria["tags"]
            results = [r for r in results if any(t in r.tags for t in tags)]
        
        # Apply name filter
        if "name" in criteria:
            name_query = criteria["name"].lower()
            results = [r for r in results if name_query in r.name.lower()]
        
        # Apply domain filter
        if "domain" in criteria:
            domain = criteria["domain"]
            tool_ids = self._domains.get(domain, [])
            results = [r for r in results if r.id in tool_ids]
        
        # Apply limit
        if "limit" in criteria:
            results = results[:criteria["limit"]]
        
        return results
    
    def register_capability(self, tool_id: str, capability: str) -> None:
        """Register a capability for a tool.
        
        Args:
            tool_id: Tool identifier.
            capability: Capability name.
        """
        if capability not in self._capabilities:
            self._capabilities[capability] = []
        if tool_id not in self._capabilities[capability]:
            self._capabilities[capability].append(tool_id)
    
    def get_capabilities(self) -> Dict[str, List[str]]:
        """Get all registered capabilities.
        
        Returns:
            Dictionary mapping capability names to list of tool IDs.
        """
        return self._capabilities
    
    def discover_by_capability(self, capability: str) -> List[Any]:
        """Discover tools by capability.
        
        Args:
            capability: Capability to search for.
            
        Returns:
            List of tool definitions with the capability.
        """
        if not self.registry:
            return []
        
        tool_ids = self._capabilities.get(capability, [])
        
        from cortex.mcp.protocol import ToolDefinition
        results = []
        for tool_id in tool_ids:
            entry = self.registry.get_tool(tool_id)
            if entry:
                results.append(ToolDefinition(
                    id=entry.tool_id,
                    name=entry.name,
                    description=entry.description,
                    tags=entry.tags,
                    deprecated=entry.deprecated
                ))
        
        return results
    
    def register_domain(self, tool_id: str, domain: str) -> None:
        """Register a domain for a tool.
        
        Args:
            tool_id: Tool identifier.
            domain: Domain name.
        """
        if domain not in self._domains:
            self._domains[domain] = []
        if tool_id not in self._domains[domain]:
            self._domains[domain].append(tool_id)
    
    def get_domains(self) -> Dict[str, List[str]]:
        """Get all registered domains.
        
        Returns:
            Dictionary mapping domain names to list of tool IDs.
        """
        return self._domains
    
    def discover_by_domain(self, domain: str) -> List[Any]:
        """Discover tools by domain.
        
        Args:
            domain: Domain to search for.
            
        Returns:
            List of tool definitions in the domain.
        """
        if not self.registry:
            return []
        
        tool_ids = self._domains.get(domain, [])
        
        from cortex.mcp.protocol import ToolDefinition
        results = []
        for tool_id in tool_ids:
            entry = self.registry.get_tool(tool_id)
            if entry:
                results.append(ToolDefinition(
                    id=entry.tool_id,
                    name=entry.name,
                    description=entry.description,
                    tags=entry.tags,
                    deprecated=entry.deprecated
                ))
        
        return results
    
    def discover_related(self, tool_id: str, limit: Optional[int] = None) -> List[Any]:
        """Discover tools related to a given tool.
        
        Args:
            tool_id: Tool to find related tools for.
            limit: Maximum number of results.
            
        Returns:
            List of related tool definitions.
        """
        if not self.registry:
            return []
        
        entry = self.registry.get_tool(tool_id)
        if not entry:
            return []
        
        # Find tools with overlapping tags
        related = set()
        for tag in entry.tags:
            for tool in self.registry.find_by_tag(tag):
                if tool.tool_id != tool_id:
                    related.add(tool.tool_id)
        
        from cortex.mcp.protocol import ToolDefinition
        results = []
        for related_id in related:
            rel_entry = self.registry.get_tool(related_id)
            if rel_entry:
                results.append(ToolDefinition(
                    id=rel_entry.tool_id,
                    name=rel_entry.name,
                    description=rel_entry.description,
                    tags=rel_entry.tags,
                    deprecated=rel_entry.deprecated
                ))
        
        if limit is not None:
            results = results[:limit]
        
        return results
    
    def get_discovery_metadata(self) -> Dict[str, Any]:
        """Get discovery metadata.
        
        Returns:
            Discovery metadata dictionary.
        """
        total_tools = len(self.discover_all()) if self.registry else 0
        return {
            "total_tools": total_tools,
            "capabilities": self._capabilities,
            "domains": self._domains,
            "supported_filters": self._metadata.supported_filters,
            "supported_patterns": self._metadata.supported_patterns,
            "version": self._metadata.version
        }


from enum import Enum

class DiscoveryPattern(Enum):
    """Discovery patterns."""
    FILE_SYSTEM = "file_system"
    REGISTRY = "registry"
    ANNOTATION = "annotation"
    PLUGIN = "plugin"


class ToolDiscoveryEngine:
    """Enhanced tool discovery."""
    
    def __init__(self, registry: "ToolRegistry" = None):
        """Initialize discovery engine.
        
        Args:
            registry: Optional registry to use.
        """
        self.registry = registry
        self.discovery = ToolDiscovery(registry)
    
    def scan(self) -> List[str]:
        """Scan for tools."""
        return [t.id for t in self.discovery.discover_all()]

__all__ = ["DiscoveryFilter", "DiscoveryMetadata", "ToolDiscovery", "DiscoveryPattern", "ToolDiscoveryEngine"]
