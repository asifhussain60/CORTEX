"""
Unit tests for Tool Discovery & Registry Service.

Validates the ToolDiscoveryService implementation with:
- Tool registry populated from schema
- Capability matching (tool tags vs user role)
- Progressive exposure (show simple tools first, complex later)
- Discovery API with filtered catalog
"""

import pytest
from cortex.orchestrators.onboarding.tool_discovery import (
    ToolDiscoveryService,
    ToolSchema,
    ToolInfo,
    ToolComplexity
)


class TestToolDiscoveryService:
    """Test suite for tool discovery service."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.service = ToolDiscoveryService()
        
        # Register sample tools
        self.service.register_tool(ToolSchema(
            tool_id='tool_list',
            name='List Files',
            description='List files in a directory',
            tags=['file', 'simple'],
            complexity=ToolComplexity.SIMPLE,
            required_roles=['user', 'developer']
        ))
        
        self.service.register_tool(ToolSchema(
            tool_id='tool_query',
            name='Query Database',
            description='Query a database',
            tags=['database', 'intermediate'],
            complexity=ToolComplexity.INTERMEDIATE,
            required_roles=['developer', 'analyst']
        ))
        
        self.service.register_tool(ToolSchema(
            tool_id='tool_deploy',
            name='Deploy Application',
            description='Deploy an application',
            tags=['deployment', 'advanced'],
            complexity=ToolComplexity.ADVANCED,
            required_roles=['admin']
        ))
    
    def test_register_tool(self):
        """Test registering a tool."""
        result = self.service.register_tool(ToolSchema(
            tool_id='new_tool',
            name='New Tool',
            description='Test tool',
            tags=['test'],
            complexity=ToolComplexity.SIMPLE,
            required_roles=[]
        ))
        
        assert result is True
        assert 'new_tool' in self.service.tool_registry
    
    def test_register_tool_duplicate(self):
        """Test that duplicate tools are rejected."""
        result = self.service.register_tool(ToolSchema(
            tool_id='tool_list',
            name='Duplicate',
            description='Duplicate tool',
            tags=[],
            complexity=ToolComplexity.SIMPLE,
            required_roles=[]
        ))
        
        assert result is False
    
    def test_get_tool_catalog(self):
        """Test retrieving complete tool catalog."""
        catalog = self.service.get_tool_catalog()
        
        assert len(catalog) == 3
        assert any(t.tool_id == 'tool_list' for t in catalog)
    
    def test_discover_tools_by_role_developer(self):
        """Test discovering tools for developer role."""
        tools = self.service.discover_tools_by_role('developer')
        
        assert len(tools) == 2  # tool_list and tool_query
        tool_ids = [t.tool_id for t in tools]
        assert 'tool_list' in tool_ids
        assert 'tool_query' in tool_ids
    
    def test_discover_tools_by_role_admin(self):
        """Test discovering tools for admin role."""
        tools = self.service.discover_tools_by_role('admin')
        
        assert len(tools) == 1
        assert tools[0].tool_id == 'tool_deploy'
    
    def test_discover_tools_by_role_user(self):
        """Test discovering tools for user role."""
        tools = self.service.discover_tools_by_role('user')
        
        assert len(tools) == 1
        assert tools[0].tool_id == 'tool_list'
    
    def test_discover_tools_by_tags_file(self):
        """Test discovering tools by file tag."""
        tools = self.service.discover_tools_by_tags(['file'])
        
        assert len(tools) == 1
        assert tools[0].tool_id == 'tool_list'
    
    def test_discover_tools_by_tags_database(self):
        """Test discovering tools by database tag."""
        tools = self.service.discover_tools_by_tags(['database'])
        
        assert len(tools) == 1
        assert tools[0].tool_id == 'tool_query'
    
    def test_discover_tools_by_tags_multiple(self):
        """Test discovering tools by multiple tags."""
        tools = self.service.discover_tools_by_tags(['file', 'database'])
        
        assert len(tools) == 2
    
    def test_discover_tools_progressive_beginner(self):
        """Test progressive discovery for beginner."""
        tools = self.service.discover_tools_progressive('developer', 1)
        
        # Only simple tools
        assert all(t.complexity <= 1 for t in tools)
    
    def test_discover_tools_progressive_intermediate(self):
        """Test progressive discovery for intermediate user."""
        tools = self.service.discover_tools_progressive('developer', 2)
        
        # Simple and intermediate tools
        assert all(t.complexity <= 2 for t in tools)
        assert len(tools) == 2  # tool_list and tool_query
    
    def test_discover_tools_progressive_ordered(self):
        """Test that progressive discovery is ordered by complexity."""
        tools = self.service.discover_tools_progressive('developer', 4)
        
        # Should be ordered from simple to complex
        complexities = [t.complexity for t in tools]
        assert complexities == sorted(complexities)
    
    def test_get_tool_info_exists(self):
        """Test getting info for existing tool."""
        info = self.service.get_tool_info('tool_list')
        
        assert info is not None
        assert info.name == 'List Files'
        assert info.complexity == 1
    
    def test_get_tool_info_not_found(self):
        """Test getting info for non-existent tool."""
        info = self.service.get_tool_info('nonexistent')
        
        assert info is None
    
    def test_get_tools_by_complexity_simple(self):
        """Test getting tools by complexity level."""
        tools = self.service.get_tools_by_complexity(1)
        
        assert len(tools) == 1
        assert all(t.complexity <= 1 for t in tools)
    
    def test_get_tools_by_complexity_all(self):
        """Test getting all tools."""
        tools = self.service.get_tools_by_complexity(4)
        
        assert len(tools) == 3
    
    def test_capability_matching_role_filter(self):
        """Test capability matching with role filter."""
        analyst_tools = self.service.discover_tools_by_role('analyst')
        
        assert len(analyst_tools) == 1
        assert analyst_tools[0].tool_id == 'tool_query'
    
    def test_progressive_exposure_complexity_order(self):
        """Test that progressive exposure shows simpler tools first."""
        tools = self.service.discover_tools_progressive('developer', 3)
        
        # Should have: simple, intermediate, advanced (in order)
        names = [t.name for t in tools]
        assert names[0] == 'List Files'  # Simple
        assert names[1] == 'Query Database'  # Intermediate
    
    def test_empty_role_match(self):
        """Test that tools with empty role list are available to all."""
        self.service.register_tool(ToolSchema(
            tool_id='tool_universal',
            name='Universal Tool',
            description='Available to everyone',
            tags=['universal'],
            complexity=ToolComplexity.SIMPLE,
            required_roles=[]
        ))
        
        tools_user = self.service.discover_tools_by_role('user')
        tools_admin = self.service.discover_tools_by_role('admin')
        
        # Universal tool should be available to both
        assert any(t.tool_id == 'tool_universal' for t in tools_user)
        assert any(t.tool_id == 'tool_universal' for t in tools_admin)
