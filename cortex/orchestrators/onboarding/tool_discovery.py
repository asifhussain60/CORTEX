"""Tool Discovery Service

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import IntEnum


class ToolComplexity(IntEnum):
    """Tool complexity level as integer enum for comparison."""
    SIMPLE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


@dataclass
class ToolSchema:
    """Tool schema for registration."""
    tool_id: str
    name: str
    description: str
    tags: List[str] = field(default_factory=list)
    complexity: ToolComplexity = ToolComplexity.SIMPLE
    required_roles: List[str] = field(default_factory=list)


@dataclass
class ToolInfo:
    """Tool information for discovery results."""
    tool_id: str
    name: str
    description: str
    complexity: int
    tags: List[str] = field(default_factory=list)


class ToolDiscoveryService:
    """Discover and recommend tools with role-based filtering and progressive exposure."""
    
    def __init__(self):
        self.tool_registry: Dict[str, ToolSchema] = {}
    
    def register_tool(self, schema: ToolSchema) -> bool:
        """Register a tool in the registry.
        
        Args:
            schema: ToolSchema with tool information
            
        Returns:
            True if registered, False if already exists
        """
        if schema.tool_id in self.tool_registry:
            return False
        
        self.tool_registry[schema.tool_id] = schema
        return True
    
    def get_tool_catalog(self) -> List[ToolInfo]:
        """Get complete tool catalog.
        
        Returns:
            List of all registered tools as ToolInfo
        """
        return [
            ToolInfo(
                tool_id=schema.tool_id,
                name=schema.name,
                description=schema.description,
                complexity=int(schema.complexity),
                tags=schema.tags.copy()
            )
            for schema in self.tool_registry.values()
        ]
    
    def discover_tools_by_role(self, role: str) -> List[ToolInfo]:
        """Discover tools available for a specific role.
        
        Args:
            role: User role (e.g., 'user', 'developer', 'admin')
            
        Returns:
            List of tools accessible by this role
        """
        tools = []
        for schema in self.tool_registry.values():
            # Empty role list means available to all
            if not schema.required_roles or role in schema.required_roles:
                tools.append(ToolInfo(
                    tool_id=schema.tool_id,
                    name=schema.name,
                    description=schema.description,
                    complexity=int(schema.complexity),
                    tags=schema.tags.copy()
                ))
        
        return tools
    
    def discover_tools_by_tags(self, tags: List[str]) -> List[ToolInfo]:
        """Discover tools matching any of the provided tags.
        
        Args:
            tags: List of tags to match
            
        Returns:
            List of tools with at least one matching tag
        """
        tools = []
        for schema in self.tool_registry.values():
            if any(tag in schema.tags for tag in tags):
                tools.append(ToolInfo(
                    tool_id=schema.tool_id,
                    name=schema.name,
                    description=schema.description,
                    complexity=int(schema.complexity),
                    tags=schema.tags.copy()
                ))
        
        return tools
    
    def discover_tools_progressive(self, role: str, max_complexity: int) -> List[ToolInfo]:
        """Discover tools with progressive exposure based on user level.
        
        Args:
            role: User role for filtering
            max_complexity: Maximum complexity level to show (1-4)
            
        Returns:
            List of tools ordered by complexity (simple to complex)
        """
        # Get role-filtered tools
        role_tools = self.discover_tools_by_role(role)
        
        # Filter by complexity and sort
        filtered_tools = [
            tool for tool in role_tools
            if tool.complexity <= max_complexity
        ]
        
        # Sort by complexity
        filtered_tools.sort(key=lambda t: t.complexity)
        
        return filtered_tools
    
    def get_tool_info(self, tool_id: str) -> Optional[ToolInfo]:
        """Get information for a specific tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            ToolInfo if found, None otherwise
        """
        schema = self.tool_registry.get(tool_id)
        if not schema:
            return None
        
        return ToolInfo(
            tool_id=schema.tool_id,
            name=schema.name,
            description=schema.description,
            complexity=int(schema.complexity),
            tags=schema.tags.copy()
        )
    
    def get_tools_by_complexity(self, max_complexity: int) -> List[ToolInfo]:
        """Get all tools up to a specific complexity level.
        
        Args:
            max_complexity: Maximum complexity level (1-4)
            
        Returns:
            List of tools with complexity <= max_complexity
        """
        tools = []
        for schema in self.tool_registry.values():
            if int(schema.complexity) <= max_complexity:
                tools.append(ToolInfo(
                    tool_id=schema.tool_id,
                    name=schema.name,
                    description=schema.description,
                    complexity=int(schema.complexity),
                    tags=schema.tags.copy()
                ))
        
        return tools


class ToolDiscoveryOrchestrator:
    """Orchestrate tool discovery."""
    
    def __init__(self):
        self.service = ToolDiscoveryService()
    
    def orchestrate(self) -> List[str]:
        """Orchestrate discovery."""
        catalog = self.service.get_tool_catalog()
        return [tool.tool_id for tool in catalog]

__all__ = ["ToolComplexity", "ToolDiscoveryService", "ToolDiscoveryOrchestrator", "ToolSchema", "ToolInfo"]
