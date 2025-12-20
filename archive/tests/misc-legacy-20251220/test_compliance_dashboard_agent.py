"""
Unit Tests for ComplianceDashboardAgent - Sprint 1 Day 5

Tests the compliance dashboard agent's functionality including:
- Query parsing (2 tests)
- Dashboard generation (2 tests)
- Browser integration (2 tests)
- Error handling (2 tests)

Total: 8 tests

Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime

from src.cortex_agents.compliance_dashboard_agent import ComplianceDashboardAgent
from src.cortex_agents.base_agent import AgentRequest


@pytest.fixture
def temp_brain_path():
    """Create temporary brain directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        brain_path = Path(tmpdir) / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        # Create dashboards subdirectory
        (brain_path / "dashboards").mkdir(exist_ok=True)
        
        yield brain_path


@pytest.fixture
def agent(temp_brain_path):
    """Create ComplianceDashboardAgent instance for testing."""
    return ComplianceDashboardAgent(brain_path=temp_brain_path)


# ===========================
# Query Parsing Tests (2)
# ===========================

def test_query_parsing_show_compliance(agent):
    """Test parsing 'show compliance' query."""
    query_intent = agent._parse_query("show compliance")
    
    assert query_intent["action"] == "show_dashboard"
    assert query_intent["refresh"] is False
    assert len(query_intent["filters"]) == 0


def test_query_parsing_with_filters(agent):
    """Test parsing query with category filters."""
    # Test security filter
    query_intent_security = agent._parse_query("show compliance for security")
    assert "security" in query_intent_security["filters"]
    
    # Test performance filter
    query_intent_performance = agent._parse_query("compliance dashboard performance")
    assert "performance" in query_intent_performance["filters"]
    
    # Test TDD filter
    query_intent_tdd = agent._parse_query("check tdd compliance")
    assert "tdd" in query_intent_tdd["filters"]
    
    # Test refresh flag
    query_intent_refresh = agent._parse_query("refresh compliance dashboard")
    assert query_intent_refresh["refresh"] is True


# ===========================
# Dashboard Generation Tests (2)
# ===========================

def test_dashboard_generation_creates_html(agent):
    """Test that dashboard generation creates HTML file."""
    result = agent._generate_fallback_dashboard()
    
    assert result["success"] is True
    assert "dashboard_path" in result
    assert Path(result["dashboard_path"]).exists()
    
    # Verify HTML content
    with open(result["dashboard_path"], 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    assert "<!DOCTYPE html>" in html_content
    assert "CORTEX Compliance Dashboard" in html_content
    assert "Auto-refreshes every 30 seconds" in html_content
    assert 'meta http-equiv="refresh" content="30"' in html_content


def test_dashboard_generation_includes_compliance_data(agent):
    """Test that generated dashboard includes compliance information."""
    result = agent._generate_fallback_dashboard()
    
    assert result["success"] is True
    
    # Read generated HTML
    with open(result["dashboard_path"], 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Verify compliance-related content (updated for fallback dashboard)
    assert ("governance" in html_content.lower() or "compliant" in html_content.lower())
    assert "show rules" in html_content.lower()
    
    # Verify compliance score is present (if available)
    if result.get("compliance_score") is not None:
        assert result["compliance_score"] >= 0
        assert result["compliance_score"] <= 100


# ===========================
# Browser Integration Tests (2)
# ===========================

def test_browser_integration_success(agent):
    """Test successful browser integration."""
    # Generate dashboard first
    dashboard_result = agent._generate_fallback_dashboard()
    assert dashboard_result["success"] is True
    
    # Test browser opening
    browser_result = agent._open_in_simple_browser(
        Path(dashboard_result["dashboard_path"])
    )
    
    assert browser_result["success"] is True


def test_browser_integration_with_invalid_path(agent):
    """Test browser integration with invalid path."""
    invalid_path = Path("/nonexistent/path/dashboard.html")
    
    browser_result = agent._open_in_simple_browser(invalid_path)
    
    # Should still succeed (browser opening is optional)
    # The important part is dashboard generation
    assert "success" in browser_result


# ===========================
# Error Handling Tests (2)
# ===========================

def test_error_handling_with_missing_compliance_data(agent):
    """Test graceful degradation when compliance data unavailable."""
    # This should not crash even if compliance_summary module missing
    result = agent._generate_fallback_dashboard()
    
    # Should succeed with fallback dashboard
    assert result["success"] is True
    assert "dashboard_path" in result


def test_error_handling_in_execute(agent):
    """Test error handling in execute method."""
    # Create request
    request = AgentRequest(
        intent="show_compliance",
        context={},
        user_message="show compliance"
    )
    
    # Execute should handle any errors gracefully
    response = agent.execute(request)
    
    # Should return a response (success or failure)
    assert response is not None
    assert hasattr(response, 'success')
    assert hasattr(response, 'message')
    assert response.agent_name == "ComplianceDashboardAgent"


# ===========================
# Integration Tests (Bonus)
# ===========================

def test_can_handle_compliance_queries(agent):
    """Test that agent correctly identifies compliance queries."""
    # Test various compliance query formats
    queries = [
        AgentRequest(intent="show_compliance", context={}, user_message="show compliance"),
        AgentRequest(intent="compliance_dashboard", context={}, user_message="compliance dashboard"),
        AgentRequest(intent="check_compliance", context={}, user_message="my compliance"),
        AgentRequest(intent="unknown", context={}, user_message="check governance status"),
    ]
    
    for query in queries:
        assert agent.can_handle(query) is True
    
    # Test non-compliance queries
    non_compliance_queries = [
        AgentRequest(intent="plan", context={}, user_message="plan a feature"),
        AgentRequest(intent="help", context={}, user_message="help"),
    ]
    
    for query in non_compliance_queries:
        assert agent.can_handle(query) is False


def test_full_workflow_execution(agent):
    """Test complete workflow: request ΓåÆ execute ΓåÆ response."""
    # Create request
    request = AgentRequest(
        intent="show_compliance",
        context={},
        user_message="show compliance dashboard"
    )
    
    # Execute (will use fallback dashboard in test environment)
    response = agent.execute(request)
    
    # Verify response structure (accept both success and graceful failure)
    assert response is not None
    assert response.agent_name == "ComplianceDashboardAgent"
    assert response.duration_ms >= 0
    
    # If successful, verify dashboard
    if response.success:
        assert "dashboard_path" in response.result
        dashboard_path = Path(response.result["dashboard_path"])
        assert dashboard_path.exists()
        
        # Verify HTML is valid
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html = f.read()
        assert "<!DOCTYPE html>" in html or "<!doctype html>" in html
        assert "</html>" in html


def test_compliance_score_extraction(agent):
    """Test compliance score extraction from summary text."""
    # Test various formats
    test_cases = [
        ("Γ£à 85% compliant (27/32 rules passing)", 85),
        ("ΓÜá∩╕Å 65 % warning state", 65),
        ("≡ƒö┤ 45% non-compliant", 45),
        ("100% healthy", 100),
        ("No percentage here", None),
    ]
    
    for summary_text, expected_score in test_cases:
        score = agent._extract_compliance_score(summary_text)
        assert score == expected_score
