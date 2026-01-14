import pytest
from src.mcp.housekeeping_tools import get_tool_for_capability, get_tool_executor_for_capability

class TestCleanupCapabilityMapping:
    def test_get_tool_for_state_sync(self):
        tool = get_tool_for_capability('state_synchronization')
        assert tool is not None
    
    def test_get_tool_for_archival(self):
        tool = get_tool_for_capability('archival_operations')
        assert tool is not None
    
    def test_get_tool_returns_metadata(self):
        """AC-CLEAN-305: get_tool_for_capability returns tool metadata dict"""
        tool = get_tool_for_capability('remediation')
        assert tool is not None
        assert isinstance(tool, dict)
        assert 'type' in tool
        assert 'priority' in tool
    
    def test_get_executor_returns_callable(self):
        """AC-CLEAN-311: get_tool_executor_for_capability returns callable"""
        executor = get_tool_executor_for_capability('remediation')
        assert callable(executor)
