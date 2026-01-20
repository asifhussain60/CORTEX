"""
MCP Tool Registration System

Manages registration and discovery of CORTEX tools in MCP client with
dynamic registration and capability-based discovery.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ToolCapability(Enum):
    """Tool capability enumeration.
    
    Defines capabilities that tools can have.
    """
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    ADMIN = "admin"


@dataclass
class ToolSchema:
    """Tool schema definition.
    
    Args:
        name: Tool name
        description: Tool description
        version: Tool version
        capabilities: List of capabilities
        parameters: Input parameters schema
        output_schema: Output schema
    """
    name: str
    description: str
    version: str
    capabilities: List[ToolCapability]
    parameters: Dict[str, Any]
    output_schema: Dict[str, Any]


@dataclass
class MCPTool:
    """Represents a tool in MCP client.
    
    Args:
        schema: Tool schema
        enabled: Whether tool is enabled
        registered_at: Registration timestamp
        metadata: Additional metadata
    """
    schema: ToolSchema
    enabled: bool = True
    registered_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MCPToolRegistry:
    """Registry for MCP tools.
    
    Manages registration, retrieval, and discovery of tools in MCP client.
    """
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, MCPTool] = {}
        self.registration_history: List[str] = []
    
    def register_tool(self, schema: ToolSchema) -> bool:
        """Register a tool.
        
        Args:
            schema: Tool schema to register
            
        Returns:
            True if registration successful, False if already registered
        """
        if schema.name in self.tools:
            return False
        
        tool = MCPTool(schema=schema, enabled=True)
        self.tools[schema.name] = tool
        self.registration_history.append(f"registered:{schema.name}")
        return True
    
    def register_tools_batch(self, schemas: List[ToolSchema]) -> int:
        """Register multiple tools.
        
        Args:
            schemas: List of tool schemas
            
        Returns:
            Number of successfully registered tools
        """
        count = 0
        for schema in schemas:
            if self.register_tool(schema):
                count += 1
        return count
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get tool by name.
        
        Args:
            name: Tool name
            
        Returns:
            Tool or None if not found
        """
        return self.tools.get(name)
    
    def get_all_tools(self) -> Dict[str, MCPTool]:
        """Get all registered tools.
        
        Returns:
            Dictionary of all tools
        """
        return dict(self.tools)
    
    def enable_tool(self, name: str) -> bool:
        """Enable a tool.
        
        Args:
            name: Tool name
            
        Returns:
            True if enabled successfully, False if tool not found
        """
        tool = self.tools.get(name)
        if not tool:
            return False
        tool.enabled = True
        return True
    
    def disable_tool(self, name: str) -> bool:
        """Disable a tool.
        
        Args:
            name: Tool name
            
        Returns:
            True if disabled successfully, False if tool not found
        """
        tool = self.tools.get(name)
        if not tool:
            return False
        tool.enabled = False
        return True
    
    def get_enabled_tools(self) -> List[MCPTool]:
        """Get all enabled tools.
        
        Returns:
            List of enabled tools
        """
        return [tool for tool in self.tools.values() if tool.enabled]
    
    def get_tools_by_capability(self, capability: ToolCapability) -> List[MCPTool]:
        """Get tools by capability.
        
        Args:
            capability: Capability to filter by
            
        Returns:
            List of tools with capability
        """
        return [
            tool for tool in self.tools.values()
            if capability in tool.schema.capabilities
        ]
    
    def unregister_tool(self, name: str) -> bool:
        """Unregister a tool.
        
        Args:
            name: Tool name
            
        Returns:
            True if unregistered successfully, False if tool not found
        """
        if name in self.tools:
            del self.tools[name]
            self.registration_history.append(f"unregistered:{name}")
            return True
        return False
    
    def get_tool_count(self) -> int:
        """Get total number of registered tools.
        
        Returns:
            Tool count
        """
        return len(self.tools)


class ToolDiscoveryService:
    """Service for discovering tools by various criteria.
    
    Provides multiple discovery methods for finding tools in registry.
    """
    
    def __init__(self, registry: MCPToolRegistry):
        """Initialize discovery service.
        
        Args:
            registry: Tool registry to search
        """
        self.registry = registry
    
    def discover_by_name_pattern(self, pattern: str) -> List[MCPTool]:
        """Discover tools by name pattern.
        
        Args:
            pattern: Name pattern to match (case-insensitive)
            
        Returns:
            List of matching tools
        """
        return [
            tool for tool in self.registry.get_all_tools().values()
            if pattern.lower() in tool.schema.name.lower()
        ]
    
    def discover_by_capability(self, capability: ToolCapability) -> List[MCPTool]:
        """Discover tools by capability.
        
        Args:
            capability: Required capability
            
        Returns:
            List of tools with capability
        """
        return self.registry.get_tools_by_capability(capability)
    
    def discover_enabled_tools(self) -> List[MCPTool]:
        """Discover all enabled tools.
        
        Returns:
            List of enabled tools
        """
        return self.registry.get_enabled_tools()
    
    def discover_by_version(self, version: str) -> List[MCPTool]:
        """Discover tools by version.
        
        Args:
            version: Version to match
            
        Returns:
            List of tools with matching version
        """
        return [
            tool for tool in self.registry.get_all_tools().values()
            if tool.schema.version == version
        ]
