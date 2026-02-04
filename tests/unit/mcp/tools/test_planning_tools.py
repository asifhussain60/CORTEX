"""Test Phase 7 MCP tools."""
from cortex.mcp.tools.planning_tools import cortex_generate_code_plan, cortex_validate_plan_coherence, cortex_execute_phase_review

def test_generate_code_plan():
    result = cortex_generate_code_plan("test task")
    assert result["status"] == "success"

def test_validate_coherence():
    result = cortex_validate_plan_coherence({})
    assert result["status"] == "pass"

def test_execute_review():
    result = cortex_execute_phase_review("phase1")
    assert result["status"] == "pass"
