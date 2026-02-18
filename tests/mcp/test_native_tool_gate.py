"""
Tests for Native Tool Gate - Pre-tool invocation blocking (CORE-049, GAP-001).

Authority: CORE-049, MCP-FIRST, ENH-055 Phase 4
Purpose: Prevent native tool bypass for IMPLEMENT/FIX/REFACTOR intents
"""

import pytest
from unittest.mock import Mock, patch
from cortex.mcp.native_tool_gate import (
    NativeToolGate,
    IntentType,
    ToolRestriction,
    is_production_code_file,
    check_tool_allowed_for_intent
)


class TestIntentClassification:
    """Test intent classification from user requests."""
    
    def test_implement_intent_detected(self):
        """RED: Detect IMPLEMENT intent from user request."""
        gate = NativeToolGate()
        request = "implement feature X"
        
        intent = gate.classify_intent(request)
        
        assert intent == IntentType.IMPLEMENT
    
    def test_fix_intent_detected(self):
        """RED: Detect FIX intent from user request."""
        gate = NativeToolGate()
        request = "fix bug in module Y"
        
        intent = gate.classify_intent(request)
        
        assert intent == IntentType.FIX
    
    def test_refactor_intent_detected(self):
        """RED: Detect REFACTOR intent from user request."""
        gate = NativeToolGate()
        request = "refactor code to improve performance"
        
        intent = gate.classify_intent(request)
        
        assert intent == IntentType.REFACTOR
    
    def test_analyze_intent_detected(self):
        """RED: Detect ANALYZE intent from user request."""
        gate = NativeToolGate()
        request = "analyze codebase for issues"
        
        intent = gate.classify_intent(request)
        
        assert intent == IntentType.ANALYZE


class TestProductionCodeDetection:
    """Test production code file detection."""
    
    def test_python_file_detected(self):
        """RED: Detect .py files as production code."""
        assert is_production_code_file("cortex/core/module.py") is True
    
    def test_typescript_file_detected(self):
        """RED: Detect .ts files as production code."""
        assert is_production_code_file("src/component.ts") is True
    
    def test_javascript_file_detected(self):
        """RED: Detect .js files as production code."""
        assert is_production_code_file("lib/utils.js") is True
    
    def test_config_file_exempt(self):
        """RED: Config files not considered production code."""
        assert is_production_code_file(".github/workflows/test.yml") is False
    
    def test_docs_file_exempt(self):
        """RED: Docs files not considered production code."""
        assert is_production_code_file("docs/architecture.md") is False


class TestToolRestrictionMatrix:
    """Test intent-based tool restriction enforcement."""
    
    def test_create_file_blocked_for_implement(self):
        """RED: create_file blocked for IMPLEMENT intent on .py files."""
        allowed = check_tool_allowed_for_intent(
            tool_name="create_file",
            intent=IntentType.IMPLEMENT,
            target_file="cortex/module.py"
        )
        
        assert allowed is False
    
    def test_replace_string_blocked_for_fix(self):
        """RED: replace_string_in_file blocked for FIX intent on .py files."""
        allowed = check_tool_allowed_for_intent(
            tool_name="replace_string_in_file",
            intent=IntentType.FIX,
            target_file="cortex/module.py"
        )
        
        assert allowed is False
    
    def test_read_file_allowed_for_implement(self):
        """RED: read_file allowed for IMPLEMENT intent."""
        allowed = check_tool_allowed_for_intent(
            tool_name="read_file",
            intent=IntentType.IMPLEMENT,
            target_file="cortex/module.py"
        )
        
        assert allowed is True
    
    def test_cortex_process_request_required_for_implement(self):
        """RED: cortex_process_request required for IMPLEMENT intent."""
        allowed = check_tool_allowed_for_intent(
            tool_name="cortex_process_request",
            intent=IntentType.IMPLEMENT,
            target_file="cortex/module.py"
        )
        
        assert allowed is True
    
    def test_create_file_allowed_for_github_prompts(self):
        """RED: create_file allowed for .github/prompts/ directory."""
        allowed = check_tool_allowed_for_intent(
            tool_name="create_file",
            intent=IntentType.DESIGN,
            target_file=".github/prompts/new-prompt.md"
        )
        
        assert allowed is True


class TestBypassAttemptLogging:
    """Test bypass attempt logging for audit trail."""
    
    def test_bypass_attempt_logged(self):
        """RED: Bypass attempts logged to audit trail."""
        gate = NativeToolGate()
        
        with patch.object(gate, '_log_bypass_attempt') as mock_log:
            gate.check_and_block(
                tool_name="create_file",
                intent=IntentType.IMPLEMENT,
                target_file="cortex/module.py"
            )
            
            mock_log.assert_called_once()
    
    def test_bypass_log_contains_metadata(self):
        """RED: Bypass log includes intent, tool, file, session_id."""
        gate = NativeToolGate()
        
        log_entry = gate._build_bypass_log(
            tool="create_file",
            intent=IntentType.IMPLEMENT,
            file="cortex/module.py",
            action="BLOCKED"
        )
        
        assert log_entry["tool"] == "create_file"
        assert log_entry["intent"] == "IMPLEMENT"
        assert log_entry["file"] == "cortex/module.py"
        assert log_entry["action"] == "BLOCKED"
        assert "timestamp" in log_entry


class TestErrorResponses:
    """Test error response generation when bypass blocked."""
    
    def test_error_message_format(self):
        """RED: Error message includes intent, tool, file, replacement."""
        gate = NativeToolGate()
        
        error = gate.generate_block_message(
            tool="create_file",
            intent=IntentType.IMPLEMENT,
            file="cortex/module.py"
        )
        
        assert "create_file" in error
        assert "IMPLEMENT" in error
        assert "cortex_process_request" in error
        assert "cortex/module.py" in error
    
    def test_error_includes_mcp_setup_instructions(self):
        """RED: Error includes MCP setup instructions."""
        gate = NativeToolGate()
        
        error = gate.generate_block_message(
            tool="create_file",
            intent=IntentType.IMPLEMENT,
            file="cortex/module.py"
        )
        
        assert "python .cortex-runtime/setup-mcp.py" in error
        assert "Reload VS Code" in error
