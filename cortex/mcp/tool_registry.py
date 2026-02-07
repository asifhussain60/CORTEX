"""MCP Tool Registry - Centralized tool discovery and categorization.

This module provides a singleton registry for MCP tools with:
- Tool registration and metadata management
- Category-based organization
- Discovery and lookup capabilities
- Thread-safe singleton pattern

Used by MCP server, tool discovery, and governance systems.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Phase: MCP Server Fix (Holistic)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import threading


class ToolCategory(Enum):
    """Tool category classification for MCP tools.
    
    Categories organize tools by their primary purpose:
    - GOVERNANCE: Rules enforcement, compliance, audit
    - ORCHESTRATION: Workflow management, task coordination
    - KNOWLEDGE: Information retrieval, documentation
    - UTILITY: General-purpose helpers, utilities
    """
    GOVERNANCE = "governance"
    ORCHESTRATION = "orchestration"
    KNOWLEDGE = "knowledge"
    UTILITY = "utility"


@dataclass
class ToolMetadata:
    """Metadata for a registered MCP tool.
    
    Captures all information needed to discover, authorize,
    and invoke an MCP tool.
    
    Attributes:
        id: Unique tool identifier (e.g., "cortex_process_request")
        name: Human-readable tool name
        category: Tool category for organization
        description: What the tool does (shown to users)
        parameters: Parameter schema (dict of param specs)
        auth_required: Whether authentication is required (default: False)
        version: Tool version string (default: "1.0.0")
    
    Example:
        ```python
        metadata = ToolMetadata(
            id="cortex_process_request",
            name="Process Request",
            category=ToolCategory.ORCHESTRATION,
            description="Routes requests to appropriate orchestrator",
            parameters={
                "request": {"type": "string", "required": True},
                "context": {"type": "object", "required": False}
            },
            auth_required=True,
            version="2.0.0"
        )
        ```
    """
    id: str
    name: str
    category: ToolCategory
    description: str
    parameters: Dict[str, Any]
    auth_required: bool = False
    version: str = "1.0.0"


class ToolRegistry:
    """Central registry for MCP tools with discovery capabilities.
    
    Provides thread-safe singleton registry for registering, discovering,
    and retrieving MCP tool metadata. Used by MCP server to enumerate
    available tools and by governance systems to enforce policies.
    
    Thread Safety: All operations are protected by internal lock.
    Singleton: Use get_mcp_tool_registry() to access the shared instance.
    
    Usage:
        ```python
        # Get singleton instance
        registry = get_mcp_tool_registry()
        
        # Register a tool
        metadata = ToolMetadata(
            id="my_tool",
            name="My Tool",
            category=ToolCategory.UTILITY,
            description="Does something useful",
            parameters={"input": {"type": "string", "required": True}}
        )
        registry.register(metadata)
        
        # Retrieve tool metadata
        tool = registry.get("my_tool")
        
        # List all tools
        all_tools = registry.list_all()
        
        # Filter by category
        utils = registry.list_by_category(ToolCategory.UTILITY)
        
        # Count tools per category
        count = registry.count_by_category(ToolCategory.UTILITY)
        ```
    """

    def __init__(self) -> None:
        """Initialize empty tool registry.
        
        Creates internal storage for tool metadata and sets up thread lock
        for safe concurrent access.
        """
        self._tools: Dict[str, ToolMetadata] = {}
        self._lock = threading.RLock()

    def register(self, metadata: ToolMetadata) -> None:
        """Register a new tool in the registry.
        
        Adds tool metadata to the registry. Tools are indexed by ID for
        fast lookup. Prevents duplicate registrations.
        
        Args:
            metadata: Tool metadata to register.
            
        Raises:
            ValueError: If tool with same ID already registered.
            
        Example:
            ```python
            registry = get_mcp_tool_registry()
            registry.register(ToolMetadata(
                id="cortex_analyze",
                name="Analyze Code",
                category=ToolCategory.KNOWLEDGE,
                description="Analyzes code quality",
                parameters={"path": {"type": "string", "required": True}}
            ))
            ```
        """
        with self._lock:
            if metadata.id in self._tools:
                raise ValueError(
                    f"Tool '{metadata.id}' already registered. "
                    f"Existing: {self._tools[metadata.id].name}"
                )
            self._tools[metadata.id] = metadata

    def get(self, tool_id: str) -> Optional[ToolMetadata]:
        """Get tool metadata by ID.
        
        Args:
            tool_id: Tool identifier to look up.
            
        Returns:
            Tool metadata if found, None otherwise.
            
        Example:
            ```python
            registry = get_mcp_tool_registry()
            tool = registry.get("cortex_process_request")
            if tool:
                print(f"Found: {tool.name}")
            ```
        """
        with self._lock:
            return self._tools.get(tool_id)

    def list_all(self) -> List[ToolMetadata]:
        """List all registered tools.
        
        Returns:
            List of all tool metadata in the registry.
            
        Example:
            ```python
            registry = get_mcp_tool_registry()
            for tool in registry.list_all():
                print(f"{tool.id}: {tool.description}")
            ```
        """
        with self._lock:
            return list(self._tools.values())

    def list_by_category(self, category: ToolCategory) -> List[ToolMetadata]:
        """List all tools in a specific category.
        
        Args:
            category: Category to filter by.
            
        Returns:
            List of tools in the specified category.
            
        Example:
            ```python
            registry = get_mcp_tool_registry()
            gov_tools = registry.list_by_category(ToolCategory.GOVERNANCE)
            print(f"Found {len(gov_tools)} governance tools")
            ```
        """
        with self._lock:
            return [
                tool for tool in self._tools.values()
                if tool.category == category
            ]

    def count_by_category(self, category: ToolCategory) -> int:
        """Count tools in a specific category.
        
        Args:
            category: Category to count.
            
        Returns:
            Number of tools in the category.
            
        Example:
            ```python
            registry = get_mcp_tool_registry()
            count = registry.count_by_category(ToolCategory.ORCHESTRATION)
            print(f"{count} orchestration tools available")
            ```
        """
        with self._lock:
            return sum(
                1 for tool in self._tools.values()
                if tool.category == category
            )

    def discover(self) -> Dict[str, List[str]]:
        """Return tool discovery information organized by category.
        
        Returns:
            Dictionary mapping category names to lists of tool IDs.
            
        Example:
            ```python
            registry = get_mcp_tool_registry()
            discovery = registry.discover()
            for category, tool_ids in discovery.items():
                print(f"{category}: {', '.join(tool_ids)}")
            ```
        """
        with self._lock:
            result: Dict[str, List[str]] = {}
            for category in ToolCategory:
                result[category.value] = [
                    tool.id for tool in self.list_by_category(category)
                ]
            return result


# Singleton instance
_registry_instance: Optional[ToolRegistry] = None
_registry_lock = threading.RLock()


def get_mcp_tool_registry() -> ToolRegistry:
    """Get the singleton MCP tool registry instance.
    
    Returns the shared ToolRegistry instance, creating it if necessary.
    Thread-safe singleton pattern ensures only one registry exists.
    
    Returns:
        The singleton ToolRegistry instance.
        
    Example:
        ```python
        # Multiple calls return the same instance
        registry1 = get_mcp_tool_registry()
        registry2 = get_mcp_tool_registry()
        assert registry1 is registry2  # True - same instance
        
        # Use the registry
        registry1.register(ToolMetadata(...))
        tools = registry2.list_all()  # Sees tools registered via registry1
        ```
    """
    global _registry_instance
    
    if _registry_instance is None:
        with _registry_lock:
            # Double-check locking pattern
            if _registry_instance is None:
                _registry_instance = ToolRegistry()
    
    return _registry_instance
