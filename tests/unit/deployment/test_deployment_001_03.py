"""
Tests for AC-DEPLOY-001-03: MCP Tool Registration in Client

Tests registering CORTEX tools in MCP client, dynamic registration, and tool discovery.
"""
import pytest
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum


class ToolCapability(Enum):
    """Tool capability enumeration."""
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
    """
    schema: ToolSchema
    enabled: bool = True
    registered_at: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MCPToolRegistry:
    """Registry for MCP tools."""
    
    def __init__(self):
        """Initialize tool registry."""
        self.tools: Dict[str, MCPTool] = {}
        self.registration_history: List[str] = []
    
    def register_tool(self, schema: ToolSchema) -> bool:
        """Register a tool.
        
        Args:
            schema: Tool schema to register
            
        Returns:
            True if registration successful
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
            True if enabled successfully
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
            True if disabled successfully
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
            True if unregistered successfully
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
    """Service for discovering tools by various criteria."""
    
    def __init__(self, registry: MCPToolRegistry):
        """Initialize discovery service.
        
        Args:
            registry: Tool registry to search
        """
        self.registry = registry
    
    def discover_by_name_pattern(self, pattern: str) -> List[MCPTool]:
        """Discover tools by name pattern.
        
        Args:
            pattern: Name pattern to match
            
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


# Test Cases

class TestToolSchema:
    """Test tool schema."""
    
    def test_schema_creation(self):
        """Test creating tool schema."""
        schema = ToolSchema(
            name="analyze",
            description="Analyze text",
            version="1.0.0",
            capabilities=[ToolCapability.READ, ToolCapability.EXECUTE],
            parameters={"text": {"type": "string"}},
            output_schema={"result": {"type": "object"}}
        )
        assert schema.name == "analyze"
        assert len(schema.capabilities) == 2
    
    def test_tool_capability_enum(self):
        """Test tool capability enum."""
        assert ToolCapability.READ.value == "read"
        assert ToolCapability.WRITE.value == "write"
        assert ToolCapability.EXECUTE.value == "execute"
        assert ToolCapability.ADMIN.value == "admin"


class TestMCPToolRegistry:
    """Test MCP tool registry."""
    
    def test_registry_initialization(self):
        """Test registry initialization."""
        registry = MCPToolRegistry()
        assert registry.get_tool_count() == 0
        assert len(registry.get_all_tools()) == 0
    
    def test_register_single_tool(self):
        """Test registering a single tool."""
        registry = MCPToolRegistry()
        schema = ToolSchema(
            name="analyze",
            description="Analyze text",
            version="1.0.0",
            capabilities=[ToolCapability.READ],
            parameters={},
            output_schema={}
        )
        result = registry.register_tool(schema)
        assert result is True
        assert registry.get_tool_count() == 1
    
    def test_register_duplicate_tool(self):
        """Test registering duplicate tool."""
        registry = MCPToolRegistry()
        schema = ToolSchema(
            name="analyze",
            description="Analyze text",
            version="1.0.0",
            capabilities=[ToolCapability.READ],
            parameters={},
            output_schema={}
        )
        registry.register_tool(schema)
        result = registry.register_tool(schema)
        assert result is False
        assert registry.get_tool_count() == 1
    
    def test_get_tool(self):
        """Test getting tool by name."""
        registry = MCPToolRegistry()
        schema = ToolSchema(
            name="analyze",
            description="Analyze text",
            version="1.0.0",
            capabilities=[ToolCapability.READ],
            parameters={},
            output_schema={}
        )
        registry.register_tool(schema)
        tool = registry.get_tool("analyze")
        assert tool is not None
        assert tool.schema.name == "analyze"
    
    def test_get_nonexistent_tool(self):
        """Test getting non-existent tool."""
        registry = MCPToolRegistry()
        tool = registry.get_tool("nonexistent")
        assert tool is None
    
    def test_register_multiple_tools(self):
        """Test registering multiple tools."""
        registry = MCPToolRegistry()
        schemas = [
            ToolSchema(
                name=f"tool{i}",
                description=f"Tool {i}",
                version="1.0.0",
                capabilities=[ToolCapability.READ],
                parameters={},
                output_schema={}
            )
            for i in range(3)
        ]
        count = registry.register_tools_batch(schemas)
        assert count == 3
        assert registry.get_tool_count() == 3


class TestToolEnabledState:
    """Test tool enabled/disabled state."""
    
    def test_enable_tool(self):
        """Test enabling a tool."""
        registry = MCPToolRegistry()
        schema = ToolSchema(
            name="analyze",
            description="Analyze text",
            version="1.0.0",
            capabilities=[ToolCapability.READ],
            parameters={},
            output_schema={}
        )
        registry.register_tool(schema)
        registry.disable_tool("analyze")
        assert registry.get_tool("analyze").enabled is False
        result = registry.enable_tool("analyze")
        assert result is True
        assert registry.get_tool("analyze").enabled is True
    
    def test_disable_tool(self):
        """Test disabling a tool."""
        registry = MCPToolRegistry()
        schema = ToolSchema(
            name="analyze",
            description="Analyze text",
            version="1.0.0",
            capabilities=[ToolCapability.READ],
            parameters={},
            output_schema={}
        )
        registry.register_tool(schema)
        result = registry.disable_tool("analyze")
        assert result is True
        assert registry.get_tool("analyze").enabled is False
    
    def test_get_enabled_tools(self):
        """Test getting enabled tools."""
        registry = MCPToolRegistry()
        for i in range(3):
            schema = ToolSchema(
                name=f"tool{i}",
                description=f"Tool {i}",
                version="1.0.0",
                capabilities=[ToolCapability.READ],
                parameters={},
                output_schema={}
            )
            registry.register_tool(schema)
        
        registry.disable_tool("tool1")
        enabled = registry.get_enabled_tools()
        assert len(enabled) == 2
        assert all(tool.enabled for tool in enabled)


class TestToolCapabilities:
    """Test tool capability filtering."""
    
    def test_get_tools_by_capability(self):
        """Test getting tools by capability."""
        registry = MCPToolRegistry()
        schemas = [
            ToolSchema(
                name="read_tool",
                description="Read tool",
                version="1.0.0",
                capabilities=[ToolCapability.READ],
                parameters={},
                output_schema={}
            ),
            ToolSchema(
                name="write_tool",
                description="Write tool",
                version="1.0.0",
                capabilities=[ToolCapability.WRITE],
                parameters={},
                output_schema={}
            ),
            ToolSchema(
                name="admin_tool",
                description="Admin tool",
                version="1.0.0",
                capabilities=[ToolCapability.READ, ToolCapability.ADMIN],
                parameters={},
                output_schema={}
            )
        ]
        for schema in schemas:
            registry.register_tool(schema)
        
        read_tools = registry.get_tools_by_capability(ToolCapability.READ)
        assert len(read_tools) == 2
        
        admin_tools = registry.get_tools_by_capability(ToolCapability.ADMIN)
        assert len(admin_tools) == 1


class TestToolDiscovery:
    """Test tool discovery service."""
    
    def test_discover_by_name_pattern(self):
        """Test discovering by name pattern."""
        registry = MCPToolRegistry()
        schemas = [
            ToolSchema(name="analyze_text", description="", version="1.0.0", capabilities=[], parameters={}, output_schema={}),
            ToolSchema(name="analyze_image", description="", version="1.0.0", capabilities=[], parameters={}, output_schema={}),
            ToolSchema(name="transform_data", description="", version="1.0.0", capabilities=[], parameters={}, output_schema={})
        ]
        for schema in schemas:
            registry.register_tool(schema)
        
        service = ToolDiscoveryService(registry)
        results = service.discover_by_name_pattern("analyze")
        assert len(results) == 2
    
    def test_discover_enabled_tools(self):
        """Test discovering enabled tools."""
        registry = MCPToolRegistry()
        schemas = [
            ToolSchema(name="tool1", description="", version="1.0.0", capabilities=[], parameters={}, output_schema={}),
            ToolSchema(name="tool2", description="", version="1.0.0", capabilities=[], parameters={}, output_schema={})
        ]
        for schema in schemas:
            registry.register_tool(schema)
        
        registry.disable_tool("tool1")
        service = ToolDiscoveryService(registry)
        enabled = service.discover_enabled_tools()
        assert len(enabled) == 1
        assert enabled[0].schema.name == "tool2"
    
    def test_discover_by_version(self):
        """Test discovering by version."""
        registry = MCPToolRegistry()
        schemas = [
            ToolSchema(name="tool1", description="", version="1.0.0", capabilities=[], parameters={}, output_schema={}),
            ToolSchema(name="tool2", description="", version="2.0.0", capabilities=[], parameters={}, output_schema={}),
            ToolSchema(name="tool3", description="", version="1.0.0", capabilities=[], parameters={}, output_schema={})
        ]
        for schema in schemas:
            registry.register_tool(schema)
        
        service = ToolDiscoveryService(registry)
        v1_tools = service.discover_by_version("1.0.0")
        assert len(v1_tools) == 2


class TestToolUnregistration:
    """Test tool unregistration."""
    
    def test_unregister_tool(self):
        """Test unregistering a tool."""
        registry = MCPToolRegistry()
        schema = ToolSchema(
            name="analyze",
            description="Analyze text",
            version="1.0.0",
            capabilities=[ToolCapability.READ],
            parameters={},
            output_schema={}
        )
        registry.register_tool(schema)
        result = registry.unregister_tool("analyze")
        assert result is True
        assert registry.get_tool_count() == 0
    
    def test_unregister_nonexistent_tool(self):
        """Test unregistering non-existent tool."""
        registry = MCPToolRegistry()
        result = registry.unregister_tool("nonexistent")
        assert result is False
