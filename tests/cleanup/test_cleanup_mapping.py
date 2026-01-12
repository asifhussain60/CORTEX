import pytest
from src.mcp.housekeeping_tools import get_tool_for_capability

class TestCleanupCapabilityMapping:
    def test_get_tool_for_state_sync(self):
        tool = get_tool_for_capability('state_synchronization')
        assert tool is not None
    
    def test_get_tool_for_archival(self):
        tool = get_tool_for_capability('archival_operations')
        assert tool is not None
    
    def test_get_tool_returns_callable(self):
        tool = get_tool_for_capability('remediation')
        assert callable(tool)
