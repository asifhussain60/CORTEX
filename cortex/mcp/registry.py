"""
MCP Tool Registry - Centralized tool discovery and categorization.

Provides:
- ToolCategory: Enumeration of tool categories
- ToolMetadata: Dataclass containing tool information
- ToolRegistry: Central registry with discovery and lookup

Author: CORTEX Framework
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import logging


logger = logging.getLogger(__name__)


class ToolCategory(Enum):
    """Tool category classification for MCP tools."""
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE = "knowledge"
    UTILITY = "utility"


@dataclass
class ToolMetadata:
    """Metadata for a registered MCP tool."""
    id: str
    name: str
    category: ToolCategory
    description: str
    parameters: Dict[str, Any]
    auth_required: bool = False
    version: str = "1.0.0"

    def __post_init__(self) -> None:
        """Validate metadata after initialization."""
        if not self.id or not self.id.strip():
            raise ValueError("Tool ID cannot be empty")
        if not self.name or not self.name.strip():
            raise ValueError("Tool name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Tool description cannot be empty")
        if not isinstance(self.parameters, dict):
            raise ValueError("Tool parameters must be a dictionary")


class ToolRegistry:
    """Central registry for MCP tools with discovery capabilities."""

    def __init__(self) -> None:
        """Initialize empty tool registry."""
        self._tools: Dict[str, ToolMetadata] = {}
        logger.debug("Tool registry initialized")

    def register(self, metadata: ToolMetadata) -> None:
        """Register a new tool in the registry.
        
        Args:
            metadata: Tool metadata to register.
            
        Raises:
            ValueError: If tool with same ID already registered.
        """
        if metadata.id in self._tools:
            error_msg = f"Tool '{metadata.id}' already registered in registry"
            logger.error(error_msg)
            raise ValueError(error_msg)
        
        self._tools[metadata.id] = metadata
        logger.info(f"Registered tool: {metadata.id} ({metadata.category.value})")

    def get(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID.
        
        Args:
            tool_id: Tool identifier to look up.
            
        Returns:
            Tool metadata if found, None otherwise.
        """
        return self._tools.get(tool_id)

    def list_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """List all tools in a specific category.
        
        Args:
            category: Category to filter by.
            
        Returns:
            List of tools in the specified category.
        """
        return [t for t in self._tools.values() if t.category == category]

    def discover(self) -> Dict[str, List[str]]:
        """Return tool discovery information.
        
        Returns:
            Dictionary mapping category names to lists of tool IDs.
        """
        result: Dict[str, List[str]] = {}
        for category in ToolCategory:
            tools_in_category = self.list_by_category(category)
            result[category.value] = [t.id for t in tools_in_category]
        
        logger.debug(f"Tool discovery requested: {len(self._tools)} total tools")
        return result

    def list_all(self) -> List[ToolMetadata]:
        """List all registered tools.
        
        Returns:
            List of all tool metadata in registration order.
        """
        return list(self._tools.values())

    def count(self) -> int:
        """Get total number of registered tools.
        
        Returns:
            Total count of registered tools.
        """
        return len(self._tools)

    def count_by_category(self, category: ToolCategory) -> int:
        """Get tool count for a specific category.
        
        Args:
            category: Category to count.
            
        Returns:
            Number of tools in the specified category.
        """
        return len(self.list_by_category(category))

    def get_auth_required_tools(self) -> List[ToolMetadata]:
        """Get all tools that require authentication.
        
        Returns:
            List of tools with auth_required=True.
        """
        return [t for t in self._tools.values() if t.auth_required]

    def summary(self) -> Dict[str, Any]:
        """Get registry summary statistics.
        
        Returns:
            Dictionary with registry metadata and statistics.
        """
        summary_dict: Dict[str, Any] = {
            "total_tools": self.count(),
            "by_category": {
                category.value: self.count_by_category(category)
                for category in ToolCategory
            },
            "auth_required_count": len(self.get_auth_required_tools()),
            "categories": [cat.value for cat in ToolCategory],
        }
        
        logger.debug(f"Registry summary: {summary_dict}")
        return summary_dict
