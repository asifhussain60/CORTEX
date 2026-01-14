import pytest
from src.mcp.housekeeping_tools import get_available_tools

class TestAvailableToolsInventory:
    def test_get_available_tools_returns_list(self):
        tools = get_available_tools()
        assert isinstance(tools, list)
    
    def test_available_tools_not_empty(self):
        tools = get_available_tools()
        assert len(tools) > 0
    
    def test_available_tools_have_names(self):
        tools = get_available_tools()
        for tool in tools:
            assert 'name' in tool or isinstance(tool, str)
