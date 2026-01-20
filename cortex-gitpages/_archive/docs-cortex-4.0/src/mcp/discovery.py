"""Tool Discovery - Multiple discovery patterns."""
from typing import List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from enum import Enum

from src.mcp.protocol import ToolDefinition
from src.mcp.registry import ToolRegistry

class DiscoveryPattern(Enum):
    """Tool discovery patterns."""
    LIST_ALL = "list_all"
    BY_TAG = "by_tag"
    BY_NAME = "by_name"
    BY_DOMAIN = "by_domain"
    SEARCH = "search"
    BY_CAPABILITY = "by_capability"

@dataclass
class DiscoveryFilter:
    """Discovery filter criteria."""
    tags: Optional[List[str]] = None
    name_contains: Optional[str] = None
    domain: Optional[str] = None
    include_deprecated: bool = False
    limit: Optional[int] = None

class ToolDiscovery:
    """Tool discovery service."""
    
    def __init__(self, registry: ToolRegistry):
        """Initialize discovery service."""
        self.registry = registry
        self.capability_index: Dict[str, List[str]] = {}
        self.domain_index: Dict[str, List[str]] = {}
    
    def discover_all(self, limit: Optional[int] = None) -> List[ToolDefinition]:
        """Discover all available tools."""
        tools = self.registry.list_tools()
        if limit:
            return tools[:limit]
        return tools
    
    def discover_by_tag(self, tag: str) -> List[ToolDefinition]:
        """Discover tools by tag."""
        return self.registry.find_by_tag(tag)
    
    def discover_by_capability(self, capability: str) -> List[ToolDefinition]:
        """Discover tools by capability."""
        tool_ids = self.capability_index.get(capability, [])
        return [self.registry.get_definition(tid) for tid in tool_ids if self.registry.get_definition(tid)]
    
    def discover_by_domain(self, domain: str) -> List[ToolDefinition]:
        """Discover tools by domain."""
        tool_ids = self.domain_index.get(domain, [])
        return [self.registry.get_definition(tid) for tid in tool_ids if self.registry.get_definition(tid)]
    
    def search(self, query: str) -> List[ToolDefinition]:
        """Search for tools."""
        return self.registry.search(query)
    
    def discover_with_filter(self, filter: DiscoveryFilter) -> List[ToolDefinition]:
        """Discover tools with complex filtering."""
        tools = self.registry.list_tools()
        
        # Apply filters
        if filter.tags:
            tools = [t for t in tools if any(tag in t.tags for tag in filter.tags)]
        
        if filter.name_contains:
            tools = [t for t in tools if filter.name_contains.lower() in t.name.lower()]
        
        if filter.domain:
            domain_tools = self.discover_by_domain(filter.domain)
            tool_ids = {t.id for t in domain_tools}
            tools = [t for t in tools if t.id in tool_ids]
        
        # Include/exclude deprecated
        if not filter.include_deprecated:
            tools = [t for t in tools if not t.deprecated]
        
        # Apply limit
        if filter.limit:
            tools = tools[:filter.limit]
        
        return tools
    
    def register_capability(self, tool_id: str, capability: str) -> None:
        """Register a tool as having a capability."""
        if capability not in self.capability_index:
            self.capability_index[capability] = []
        if tool_id not in self.capability_index[capability]:
            self.capability_index[capability].append(tool_id)
    
    def register_domain(self, tool_id: str, domain: str) -> None:
        """Register a tool as belonging to a domain."""
        if domain not in self.domain_index:
            self.domain_index[domain] = []
        if tool_id not in self.domain_index[domain]:
            self.domain_index[domain].append(tool_id)
    
    def get_capabilities(self) -> List[str]:
        """Get all available capabilities."""
        return list(self.capability_index.keys())
    
    def get_domains(self) -> List[str]:
        """Get all available domains."""
        return list(self.domain_index.keys())
    
    def get_discovery_metadata(self) -> Dict[str, Any]:
        """Get discovery service metadata."""
        all_tools = self.registry.list_tools()
        
        return {
            "total_tools": len(all_tools),
            "total_capabilities": len(self.capability_index),
            "total_domains": len(self.domain_index),
            "capabilities": self.get_capabilities(),
            "domains": self.get_domains(),
            "supported_patterns": [p.value for p in DiscoveryPattern]
        }
    
    def discover_related(self, tool_id: str) -> List[ToolDefinition]:
        """Discover tools related to a given tool."""
        definition = self.registry.get_definition(tool_id)
        if not definition:
            return []
        
        related = []
        
        # Find tools with same tags
        for tag in definition.tags:
            related.extend(self.discover_by_tag(tag))
        
        # Find tools in same domains
        tool_domains = self.domain_index.get(tool_id, [])
        for domain in tool_domains:
            related.extend(self.discover_by_domain(domain))
        
        # Remove duplicates and original tool
        related_ids = {t.id for t in related if t.id != tool_id}
        return [self.registry.get_definition(tid) for tid in related_ids if self.registry.get_definition(tid)]
