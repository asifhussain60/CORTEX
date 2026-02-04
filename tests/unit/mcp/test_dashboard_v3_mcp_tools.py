"""
Test Dashboard v3 MCP Tools Registration.

Verifies that cortex_aggregate_dashboard_data_v3, cortex_serve_dashboard,
and cortex_test_dashboard_e2e are properly registered in MCP tools catalog.

AC-ID: DASHBOARD-V3-MCP-TEST-001
"""

import pytest
from cortex.mcp.tools import (
    cortex_aggregate_dashboard_data_v3,
    cortex_serve_dashboard,
    cortex_test_dashboard_e2e,
)
from cortex.mcp.decorators import MCP_TOOLS_REGISTRY


def test_dashboard_v3_tools_registered():
    """Test that all 3 dashboard v3 MCP tools are registered."""
    # MCP_TOOLS_REGISTRY is a dict where keys are tool names
    assert "cortex_aggregate_dashboard_data_v3" in MCP_TOOLS_REGISTRY
    assert "cortex_serve_dashboard" in MCP_TOOLS_REGISTRY
    assert "cortex_test_dashboard_e2e" in MCP_TOOLS_REGISTRY


def test_cortex_aggregate_dashboard_data_v3_metadata():
    """Test cortex_aggregate_dashboard_data_v3 tool metadata."""
    tool = MCP_TOOLS_REGISTRY.get("cortex_aggregate_dashboard_data_v3")
    
    assert tool is not None
    assert "dashboard-data.json" in tool["description"]
    assert "repo_path" in tool["parameters"]
    assert "output_path" in tool["parameters"]
    assert tool["parameters"]["repo_path"] == "string"


def test_cortex_serve_dashboard_metadata():
    """Test cortex_serve_dashboard tool metadata."""
    tool = MCP_TOOLS_REGISTRY.get("cortex_serve_dashboard")
    
    assert tool is not None
    assert "HTTP" in tool["description"]
    assert "port" in tool["parameters"]
    assert "directory" in tool["parameters"]


def test_cortex_test_dashboard_e2e_metadata():
    """Test cortex_test_dashboard_e2e tool metadata."""
    tool = MCP_TOOLS_REGISTRY.get("cortex_test_dashboard_e2e")
    
    assert tool is not None
    assert "Playwright" in tool["description"]
    assert "test_pattern" in tool["parameters"]
    assert "headed" in tool["parameters"]


def test_cortex_aggregate_dashboard_data_v3_callable():
    """Test that cortex_aggregate_dashboard_data_v3 is callable."""
    assert callable(cortex_aggregate_dashboard_data_v3)


def test_cortex_serve_dashboard_callable():
    """Test that cortex_serve_dashboard is callable."""
    assert callable(cortex_serve_dashboard)


def test_cortex_test_dashboard_e2e_callable():
    """Test that cortex_test_dashboard_e2e is callable."""
    assert callable(cortex_test_dashboard_e2e)


def test_cortex_aggregate_dashboard_data_v3_invalid_path():
    """Test cortex_aggregate_dashboard_data_v3 with invalid path."""
    result = cortex_aggregate_dashboard_data_v3(
        repo_path="/nonexistent/path/12345",
        output_path=None,
    )
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "not found" in result["error"].lower()


def test_cortex_serve_dashboard_invalid_directory():
    """Test cortex_serve_dashboard with invalid directory."""
    result = cortex_serve_dashboard(
        port=9999,
        directory="/nonexistent/directory/12345",
    )
    
    assert result["success"] is False
    assert result["error"] is not None
    assert "not found" in result["error"].lower()


def test_dashboard_tools_in_mcp_tools_catalog():
    """Test that dashboard tools appear in MCP_TOOLS catalog."""
    from cortex.mcp.tools import MCP_TOOLS
    
    assert "cortex_aggregate_dashboard_data_v3" in MCP_TOOLS
    assert "cortex_serve_dashboard" in MCP_TOOLS
    assert "cortex_test_dashboard_e2e" in MCP_TOOLS
    
    # Check categories
    agg_tool = MCP_TOOLS["cortex_aggregate_dashboard_data_v3"]
    assert agg_tool["category"] == "dashboard"
    
    serve_tool = MCP_TOOLS["cortex_serve_dashboard"]
    assert serve_tool["category"] == "dashboard"
    
    test_tool = MCP_TOOLS["cortex_test_dashboard_e2e"]
    assert test_tool["category"] == "testing"
