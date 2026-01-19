"""
Tool Discovery & Registry Service Implementation.

Provides the ToolDiscoveryService for tool catalog management,
capability matching, and progressive exposure based on user role
and skill level.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional, Set
from enum import Enum


class ToolComplexity(Enum):
    """Tool complexity levels for progressive exposure."""
    SIMPLE = 1
    INTERMEDIATE = 2
    ADVANCED = 3
    EXPERT = 4


@dataclass
class ToolSchema:
    """Schema definition for a tool."""
    tool_id: str
    name: str
    description: str
    tags: List[str]
    complexity: ToolComplexity
    required_roles: List[str]


@dataclass
class ToolInfo:
    """Information about an available tool."""
    tool_id: str
    name: str
    description: str
    tags: List[str]
    complexity: int
    roles: List[str]


class ToolDiscoveryService:
    """Service for discovering and filtering tools based on user profile."""
    
    def __init__(self):
        """Initialize the tool discovery service."""
        self.tool_registry: Dict[str, ToolSchema] = {}
        self.complexity_levels = {
            ToolComplexity.SIMPLE: 1,
            ToolComplexity.INTERMEDIATE: 2,
            ToolComplexity.ADVANCED: 3,
            ToolComplexity.EXPERT: 4
        }
    
    def register_tool(self, schema: ToolSchema) -> bool:
        """
        Register a tool in the registry.
        
        Args:
            schema: Tool schema definition
            
        Returns:
            True if registration successful, False if tool already exists
        """
        if schema.tool_id in self.tool_registry:
            return False
        
        self.tool_registry[schema.tool_id] = schema
        return True
    
    def get_tool_catalog(self) -> List[ToolInfo]:
        """
        Get complete tool catalog.
        
        Returns:
            List of all registered tools
        """
        return [
            ToolInfo(
                tool_id=schema.tool_id,
                name=schema.name,
                description=schema.description,
                tags=schema.tags,
                complexity=self.complexity_levels[schema.complexity],
                roles=schema.required_roles
            )
            for schema in self.tool_registry.values()
        ]
    
    def discover_tools_by_role(self, user_role: str) -> List[ToolInfo]:
        """
        Discover tools available for a specific user role.
        
        Args:
            user_role: User's role
            
        Returns:
            List of tools matching the user role
        """
        matching_tools = []
        
        for schema in self.tool_registry.values():
            if not schema.required_roles or user_role in schema.required_roles:
                matching_tools.append(
                    ToolInfo(
                        tool_id=schema.tool_id,
                        name=schema.name,
                        description=schema.description,
                        tags=schema.tags,
                        complexity=self.complexity_levels[schema.complexity],
                        roles=schema.required_roles
                    )
                )
        
        return matching_tools
    
    def discover_tools_by_tags(self, tags: List[str]) -> List[ToolInfo]:
        """
        Discover tools by tags.
        
        Args:
            tags: Tags to search for
            
        Returns:
            List of tools matching any of the tags
        """
        tag_set = set(tags)
        matching_tools = []
        
        for schema in self.tool_registry.values():
            tool_tags = set(schema.tags)
            if tool_tags & tag_set:  # Intersection
                matching_tools.append(
                    ToolInfo(
                        tool_id=schema.tool_id,
                        name=schema.name,
                        description=schema.description,
                        tags=schema.tags,
                        complexity=self.complexity_levels[schema.complexity],
                        roles=schema.required_roles
                    )
                )
        
        return matching_tools
    
    def discover_tools_progressive(
        self,
        user_role: str,
        skill_level: int
    ) -> List[ToolInfo]:
        """
        Discover tools with progressive exposure based on skill level.
        
        Args:
            user_role: User's role
            skill_level: User's skill level (1-4, matching complexity levels)
            
        Returns:
            List of tools appropriate for user's role and skill level
        """
        matching_tools = []
        
        for schema in self.tool_registry.values():
            # Check role match
            if schema.required_roles and user_role not in schema.required_roles:
                continue
            
            # Check complexity vs skill level
            tool_complexity = self.complexity_levels[schema.complexity]
            if tool_complexity <= skill_level:
                matching_tools.append(
                    ToolInfo(
                        tool_id=schema.tool_id,
                        name=schema.name,
                        description=schema.description,
                        tags=schema.tags,
                        complexity=tool_complexity,
                        roles=schema.required_roles
                    )
                )
        
        # Sort by complexity (simple tools first)
        matching_tools.sort(key=lambda t: t.complexity)
        
        return matching_tools
    
    def get_tool_info(self, tool_id: str) -> Optional[ToolInfo]:
        """
        Get information about a specific tool.
        
        Args:
            tool_id: Tool identifier
            
        Returns:
            Tool information if found, None otherwise
        """
        if tool_id not in self.tool_registry:
            return None
        
        schema = self.tool_registry[tool_id]
        return ToolInfo(
            tool_id=schema.tool_id,
            name=schema.name,
            description=schema.description,
            tags=schema.tags,
            complexity=self.complexity_levels[schema.complexity],
            roles=schema.required_roles
        )
    
    def get_tools_by_complexity(self, max_complexity: int) -> List[ToolInfo]:
        """
        Get all tools up to a maximum complexity level.
        
        Args:
            max_complexity: Maximum complexity level (1-4)
            
        Returns:
            List of tools at or below the complexity level
        """
        matching_tools = []
        
        for schema in self.tool_registry.values():
            tool_complexity = self.complexity_levels[schema.complexity]
            if tool_complexity <= max_complexity:
                matching_tools.append(
                    ToolInfo(
                        tool_id=schema.tool_id,
                        name=schema.name,
                        description=schema.description,
                        tags=schema.tags,
                        complexity=tool_complexity,
                        roles=schema.required_roles
                    )
                )
        
        # Sort by complexity
        matching_tools.sort(key=lambda t: t.complexity)
        
        return matching_tools
