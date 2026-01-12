import pytest
from src.mcp.housekeeping_tools import run_cleanup_workflow

class TestCleanupWorkflow:
    def test_cleanup_workflow_returns_dict(self):
        result = run_cleanup_workflow({})
        assert isinstance(result, dict)
    
    def test_cleanup_workflow_has_status(self):
        result = run_cleanup_workflow({})
        assert 'status' in result or 'success' in result
