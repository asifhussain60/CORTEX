import pytest
from src.mcp.housekeeping_tools import execute_tool

class TestToolExecution:
    def test_execute_tool_success(self):
        result = execute_tool({'tool': 'state_sync', 'action': 'validate'})
        assert isinstance(result, dict)
    
    def test_execute_tool_with_params(self):
        result = execute_tool({'tool': 'archival', 'source': 'test/'})
        assert result is not None
    
    def test_execute_tool_handles_error(self):
        result = execute_tool({'tool': 'unknown_tool'})
        assert result is not None
