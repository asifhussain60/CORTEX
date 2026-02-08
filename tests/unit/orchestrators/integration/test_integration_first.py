"""
Tests for Integration-First components.

AC_START: AC-INTEGRATION-005
Description: Test intent classification, MCP pre-flight, and phase completion hooks
"""

import pytest
from cortex.orchestrators.integration.intent_classifier import (
    IntentClassifier,
    UserIntent,
)
from cortex.orchestrators.integration.mcp_preflight_checker import (
    MCPPreFlightChecker,
    ManagedStatus,
)


class TestIntentClassification:
    """Test intent classification from natural language."""
    
    def test_classify_implement_intent(self) -> None:
        """Detect IMPLEMENT intent from request."""
        requests = [
            "implement user authentication feature",
            "add error handling to API",
            "create new dashboard component",
            "build reporting system",
        ]
        
        for req in requests:
            intent = IntentClassifier.classify(req)
            assert intent == UserIntent.IMPLEMENT, f"Failed: {req}"
    
    def test_classify_fix_intent(self) -> None:
        """Detect FIX intent from request."""
        requests = [
            "fix broken HTML rendering",
            "error in console-log",
            "debug packages.slice issue",
            "fix dashboard crash",
        ]
        
        for req in requests:
            intent = IntentClassifier.classify(req)
            assert intent == UserIntent.FIX, f"Failed: {req}"
    
    def test_classify_refactor_intent(self) -> None:
        """Detect REFACTOR intent from request."""
        requests = [
            "refactor legacy code",
            "improve performance of component",
            "clean up implementation",
            "simplify orchestrator logic",
        ]
        
        for req in requests:
            intent = IntentClassifier.classify(req)
            assert intent == UserIntent.REFACTOR, f"Failed: {req}"
    
    def test_classify_analyze_intent(self) -> None:
        """Detect ANALYZE intent from request."""
        requests = [
            "analyze the code structure",
            "explain the implementation",
            "review this approach",
            "examine the system architecture",
        ]
        
        for req in requests:
            intent = IntentClassifier.classify(req)
            assert intent == UserIntent.ANALYZE, f"Failed: {req}"
    
    def test_get_mcp_tool_for_intent(self) -> None:
        """Get recommended MCP tool for each intent."""
        assert IntentClassifier.get_mcp_tool(UserIntent.IMPLEMENT) == "cortex_process_request"
        assert IntentClassifier.get_mcp_tool(UserIntent.FIX) == "cortex_process_request"
        assert IntentClassifier.get_mcp_tool(UserIntent.REFACTOR) == "cortex_process_request"
        assert IntentClassifier.get_mcp_tool(UserIntent.ANALYZE) == "cortex_lens_analyze"
        assert IntentClassifier.get_mcp_tool(UserIntent.AUDIT) == "cortex_lens_analyze"
        assert IntentClassifier.get_mcp_tool(UserIntent.PLAN) == "cortex_plan_setup"
        assert IntentClassifier.get_mcp_tool(UserIntent.QUERY) is None
    
    def test_requires_mcp_blocking_intents(self) -> None:
        """Verify MCP requirement for each intent."""
        assert IntentClassifier.requires_mcp(UserIntent.IMPLEMENT)
        assert IntentClassifier.requires_mcp(UserIntent.FIX)
        assert IntentClassifier.requires_mcp(UserIntent.REFACTOR)
        assert IntentClassifier.requires_mcp(UserIntent.ANALYZE)
        assert IntentClassifier.requires_mcp(UserIntent.AUDIT)
        assert IntentClassifier.requires_mcp(UserIntent.PLAN)
        assert not IntentClassifier.requires_mcp(UserIntent.QUERY)
        assert not IntentClassifier.requires_mcp(UserIntent.UNKNOWN)
    
    def test_requires_tdd_for_implementation(self) -> None:
        """Verify TDD requirement for implementation intents."""
        assert IntentClassifier.requires_tdd(UserIntent.IMPLEMENT)
        assert IntentClassifier.requires_tdd(UserIntent.FIX)
        assert IntentClassifier.requires_tdd(UserIntent.REFACTOR)
        assert not IntentClassifier.requires_tdd(UserIntent.ANALYZE)
        assert not IntentClassifier.requires_tdd(UserIntent.QUERY)


class TestMCPPreFlightChecker:
    """Test MCP pre-flight availability checks."""
    
    def test_mcp_available_status(self) -> None:
        """Test status when all tools available."""
        checker = MCPPreFlightChecker()
        
        all_tools = [
            "cortex_process_request",
            "cortex_lens_analyze",
            "cortex_challenge",
            "cortex_total_recall",
            "cortex_git_history",
            "cortex_ast_analyze",
            "cortex_detect_duplicates",
            "cortex_plan_setup",
            "cortex_plan_teardown",
            "cortex_plan_execute_autonomous",
        ]
        
        result = checker.check_mcp_availability(
            available_tools=all_tools,
            mcp_server_running=True,
            config_valid=True
        )
        
        assert result.is_available()
        assert result.status == ManagedStatus.AVAILABLE
        assert len(result.missing_tools) == 0
    
    def test_mcp_degraded_status(self) -> None:
        """Test status when some tools missing."""
        checker = MCPPreFlightChecker()
        
        partial_tools = [
            "cortex_process_request",
            "cortex_lens_analyze",
            "cortex_challenge",
        ]
        
        result = checker.check_mcp_availability(
            available_tools=partial_tools,
            mcp_server_running=True,
            config_valid=True
        )
        
        assert not result.is_available()
        assert result.status == ManagedStatus.DEGRADED
        assert len(result.missing_tools) > 0
    
    def test_mcp_unavailable_no_server(self) -> None:
        """Test status when MCP server not running."""
        checker = MCPPreFlightChecker()
        
        result = checker.check_mcp_availability(
            available_tools=[],
            mcp_server_running=False,
            config_valid=False
        )
        
        assert not result.is_available()
        assert result.status == ManagedStatus.UNAVAILABLE
    
    def test_should_block_implement_without_mcp(self) -> None:
        """Verify IMPLEMENT intent blocked when MCP unavailable."""
        checker = MCPPreFlightChecker()
        
        result = checker.check_mcp_availability(
            available_tools=[],
            mcp_server_running=False,
            config_valid=False
        )
        
        should_block = checker.should_block_operation("IMPLEMENT", result)
        assert should_block is True
    
    def test_should_not_block_query_without_mcp(self) -> None:
        """Verify QUERY intent not blocked when MCP unavailable."""
        checker = MCPPreFlightChecker()
        
        result = checker.check_mcp_availability(
            available_tools=[],
            mcp_server_running=False,
            config_valid=False
        )
        
        should_block = checker.should_block_operation("QUERY", result)
        assert should_block is False
    
    def test_status_report_generation(self) -> None:
        """Test human-readable status report generation."""
        checker = MCPPreFlightChecker()
        
        result = checker.check_mcp_availability(
            available_tools=["cortex_process_request", "cortex_lens_analyze"],
            mcp_server_running=True,
            config_valid=True
        )
        
        report = checker.get_status_report(result)
        
        assert "MCP System Status" in report
        assert "Server Running: ✅ Yes" in report
        assert "Tools Available: 2/10" in report
        assert "🔴 NOT READY" in report


class TestPhaseCompletionIntegration:
    """Test phase completion hook integration."""
    
    def test_detect_phase_context_with_phase_file(self) -> None:
        """Detect phase context from execution context."""
        from cortex.orchestrators.integration.phase_completion_hook_integrator import (
            PhaseCompletionHookIntegrator,
        )
        
        integrator = PhaseCompletionHookIntegrator()
        
        context = {
            "phase_file": "/path/to/phase-44.yaml",
            "phase_key": "phase_44_1",
            "phase_id": "phase-44",
        }
        
        phase_context = integrator.detect_phase_context(context)
        
        assert phase_context is not None
        assert phase_context["phase_id"] == "phase-44"
        assert phase_context["phase_file"] == "/path/to/phase-44.yaml"
    
    def test_detect_no_phase_context(self) -> None:
        """Return None when no phase context."""
        from cortex.orchestrators.integration.phase_completion_hook_integrator import (
            PhaseCompletionHookIntegrator,
        )
        
        integrator = PhaseCompletionHookIntegrator()
        
        context = {
            "user_request": "analyze code",
            "intent": "ANALYZE",
        }
        
        phase_context = integrator.detect_phase_context(context)
        
        assert phase_context is None
    
    def test_should_generate_continuation_prompt(self) -> None:
        """Check when continuation prompt should be generated."""
        from cortex.orchestrators.integration.phase_completion_hook_integrator import (
            PhaseCompletionHookIntegrator,
        )
        
        integrator = PhaseCompletionHookIntegrator()
        
        # At 75% of budget
        assert integrator.should_generate_continuation_prompt(150000, 200000)
        
        # Below 75%
        assert not integrator.should_generate_continuation_prompt(100000, 200000)
        
        # Exactly at 75%
        assert integrator.should_generate_continuation_prompt(150000, 200000)


# AC_COMPLETE: AC-INTEGRATION-005 ✅
