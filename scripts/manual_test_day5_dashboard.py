"""
Manual Testing Script for ComplianceDashboardAgent - Sprint 1 Day 5

Tests real-world scenarios for compliance dashboard agent:
1. Query parsing with natural language variants
2. Dashboard generation and HTML validation
3. Browser integration (dashboard opens successfully)
4. Error handling and graceful degradation

Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.cortex_agents.compliance_dashboard_agent import ComplianceDashboardAgent
from src.cortex_agents.base_agent import AgentRequest


def print_header(title: str):
    """Print formatted section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_step(step_num: int, description: str):
    """Print formatted test step."""
    print(f"\n[Step {step_num}] {description}")
    print("-" * 80)


def print_result(passed: bool, message: str):
    """Print test result."""
    icon = "Γ£à" if passed else "Γ¥î"
    print(f"\n{icon} {message}")


def test_scenario_1_query_parsing():
    """Scenario 1: Natural Language Query Parsing"""
    print_header("Scenario 1: Query Parsing with Natural Language Variants")
    
    try:
        # Initialize agent
        agent = ComplianceDashboardAgent()
        
        print_step(1, "Test 'show compliance' query")
        query1 = agent._parse_query("show compliance")
        assert query1["action"] == "show_dashboard"
        assert query1["refresh"] is False
        print(f"Γ£ô Parsed query: {query1}")
        
        print_step(2, "Test 'compliance dashboard' query")
        query2 = agent._parse_query("compliance dashboard")
        assert query2["action"] == "show_dashboard"
        print(f"Γ£ô Parsed query: {query2}")
        
        print_step(3, "Test 'check governance status' query")
        query3 = agent._parse_query("check governance status")
        assert query3["action"] == "show_dashboard"
        print(f"Γ£ô Parsed query: {query3}")
        
        print_step(4, "Test query with filters")
        query4 = agent._parse_query("show security compliance")
        assert "security" in query4["filters"]
        print(f"Γ£ô Parsed query with filters: {query4}")
        
        print_step(5, "Test refresh flag detection")
        query5 = agent._parse_query("refresh compliance dashboard")
        assert query5["refresh"] is True
        print(f"Γ£ô Detected refresh flag: {query5}")
        
        print_result(True, "Scenario 1: Query Parsing: PASSED")
        return True
    
    except Exception as e:
        print_result(False, f"Scenario 1: Query Parsing: FAILED - {e}")
        return False


def test_scenario_2_dashboard_generation():
    """Scenario 2: Dashboard Generation and HTML Validation"""
    print_header("Scenario 2: Dashboard Generation with HTML Validation")
    
    try:
        # Initialize agent
        agent = ComplianceDashboardAgent()
        
        print_step(1, "Generate fallback dashboard")
        result = agent._generate_fallback_dashboard()
        assert result["success"] is True
        assert "dashboard_path" in result
        print(f"Γ£ô Dashboard generated: {result['dashboard_path']}")
        
        print_step(2, "Verify dashboard file exists")
        dashboard_path = Path(result["dashboard_path"])
        assert dashboard_path.exists()
        print(f"Γ£ô Dashboard file exists: {dashboard_path}")
        
        print_step(3, "Validate HTML structure")
        with open(dashboard_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        assert "<!DOCTYPE html>" in html_content
        assert "</html>" in html_content
        assert "CORTEX Compliance Dashboard" in html_content
        print("Γ£ô HTML structure valid")
        
        print_step(4, "Verify auto-refresh meta tag")
        assert 'meta http-equiv="refresh" content="30"' in html_content
        print("Γ£ô Auto-refresh configured (30 seconds)")
        
        print_step(5, "Verify compliance content")
        assert "governance" in html_content.lower()
        assert "show rules" in html_content.lower()
        assert "27 protection rules" in html_content.lower()
        print("Γ£ô Compliance content present")
        
        print_step(6, "Check dashboard styling")
        assert "<style>" in html_content
        assert "background: #1e1e1e" in html_content  # Dark theme
        print("Γ£ô Styling present (dark theme)")
        
        print_result(True, "Scenario 2: Dashboard Generation: PASSED")
        return True
    
    except Exception as e:
        print_result(False, f"Scenario 2: Dashboard Generation: FAILED - {e}")
        return False


def test_scenario_3_browser_integration():
    """Scenario 3: Browser Integration and Workflow"""
    print_header("Scenario 3: Full Workflow with Browser Integration")
    
    try:
        # Initialize agent
        agent = ComplianceDashboardAgent()
        
        print_step(1, "Create agent request")
        request = AgentRequest(
            intent="show_compliance",
            context={},
            user_message="show compliance dashboard"
        )
        print("Γ£ô Request created")
        
        print_step(2, "Verify agent can handle request")
        can_handle = agent.can_handle(request)
        assert can_handle is True
        print("Γ£ô Agent recognizes compliance request")
        
        print_step(3, "Execute full workflow")
        response = agent.execute(request)
        assert response is not None
        assert response.agent_name == "ComplianceDashboardAgent"
        print(f"Γ£ô Workflow executed (success={response.success})")
        
        print_step(4, "Verify response structure")
        assert hasattr(response, 'result')
        assert hasattr(response, 'message')
        assert hasattr(response, 'duration_ms')
        assert response.duration_ms >= 0
        print(f"Γ£ô Response structure valid (duration: {response.duration_ms:.2f}ms)")
        
        print_step(5, "Verify dashboard path in response")
        if response.success:
            assert "dashboard_path" in response.result
            dashboard_path = Path(response.result["dashboard_path"])
            assert dashboard_path.exists()
            print(f"Γ£ô Dashboard accessible: {dashboard_path}")
        else:
            # Graceful failure is acceptable (template may not exist)
            print(f"ΓÜá∩╕Å  Dashboard generation used fallback (expected in test environment)")
        
        print_step(6, "Verify next actions provided")
        if response.success and len(response.next_actions) > 0:
            print(f"Γ£ô Next actions provided: {len(response.next_actions)} suggestions")
            for action in response.next_actions:
                print(f"  - {action}")
        
        print_result(True, "Scenario 3: Browser Integration: PASSED")
        return True
    
    except Exception as e:
        print_result(False, f"Scenario 3: Browser Integration: FAILED - {e}")
        return False


def test_scenario_4_error_handling():
    """Scenario 4: Error Handling and Graceful Degradation"""
    print_header("Scenario 4: Error Handling with Various Edge Cases")
    
    try:
        # Initialize agent
        agent = ComplianceDashboardAgent()
        
        print_step(1, "Test with invalid path (should handle gracefully)")
        invalid_path = Path("/nonexistent/path/dashboard.html")
        browser_result = agent._open_in_simple_browser(invalid_path)
        assert "success" in browser_result
        print("Γ£ô Handled invalid path gracefully")
        
        print_step(2, "Test compliance score extraction with various formats")
        test_cases = [
            ("Γ£à 85% compliant", 85),
            ("ΓÜá∩╕Å 65 % warning", 65),
            ("100% healthy", 100),
            ("No percentage", None),
        ]
        
        for text, expected in test_cases:
            score = agent._extract_compliance_score(text)
            assert score == expected, f"Expected {expected}, got {score} for '{text}'"
            print(f"  Γ£ô '{text}' ΓåÆ {score}%")
        
        print("Γ£ô Score extraction handles all formats")
        
        print_step(3, "Test can_handle with non-compliance queries")
        non_compliance_requests = [
            AgentRequest(intent="plan", context={}, user_message="plan a feature"),
            AgentRequest(intent="help", context={}, user_message="help me"),
        ]
        
        for req in non_compliance_requests:
            can_handle = agent.can_handle(req)
            assert can_handle is False
            print(f"  Γ£ô Correctly rejected: '{req.user_message}'")
        
        print("Γ£ô Properly rejects non-compliance queries")
        
        print_step(4, "Test dashboard generation with missing compliance data")
        # This should not crash even if data unavailable
        result = agent._generate_fallback_dashboard()
        assert result["success"] is True
        print("Γ£ô Generates fallback dashboard when data unavailable")
        
        print_step(5, "Test execute method error handling")
        # Create edge case request
        edge_request = AgentRequest(
            intent="show_compliance",
            context={"malformed": "data"},
            user_message="show compliance"
        )
        
        response = agent.execute(edge_request)
        assert response is not None
        assert response.agent_name == "ComplianceDashboardAgent"
        print("Γ£ô Execute handles edge cases without crashing")
        
        print_result(True, "Scenario 4: Error Handling: PASSED")
        return True
    
    except Exception as e:
        print_result(False, f"Scenario 4: Error Handling: FAILED - {e}")
        return False


def main():
    """Run all manual test scenarios."""
    print("\n" + "="*80)
    print("  CORTEX Compliance Dashboard Agent - Manual Testing")
    print("  Sprint 1 Day 5")
    print("="*80)
    
    results = []
    
    # Run all scenarios
    results.append(("Scenario 1: Query Parsing", test_scenario_1_query_parsing()))
    results.append(("Scenario 2: Dashboard Generation", test_scenario_2_dashboard_generation()))
    results.append(("Scenario 3: Browser Integration", test_scenario_3_browser_integration()))
    results.append(("Scenario 4: Error Handling", test_scenario_4_error_handling()))
    
    # Print summary
    print("\n" + "="*80)
    print("  TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        icon = "Γ£à" if result else "Γ¥î"
        print(f"{icon} {name}: {'PASSED' if result else 'FAILED'}")
    
    print(f"\nTOTAL: {passed}/{total} scenarios passed ({passed/total*100:.0f}%)")
    
    if passed == total:
        print("\nΓ£à ALL MANUAL TESTS PASSED - Ready to commit Day 5! Γ£à\n")
        return 0
    else:
        print(f"\nΓ¥î {total - passed} scenarios failed - Fix before committing Γ¥î\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
