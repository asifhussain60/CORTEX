"""
Test suite for native tool bypass prevention enforcement layer.

Validates that IMPLEMENT/FIX/REFACTOR intents correctly block native tools
and enforce MCP-FIRST routing.

CORE-008: TDD enforcement
CORE-049: MCP-FIRST architecture
ENH-055: Lean prompt architecture
"""

import pytest
from typing import Dict, List, Optional, Tuple


class IntentClassifier:
    """Mock intent classifier for testing."""
    
    INTENTS = ["IMPLEMENT", "FIX", "REFACTOR", "ANALYZE", "AUDIT", "DESIGN"]
    
    @staticmethod
    def classify(user_request: str) -> str:
        """Classify user intent from request."""
        request_lower = user_request.lower()
        
        if any(word in request_lower for word in ["implement", "create", "add"]):
            return "IMPLEMENT"
        elif any(word in request_lower for word in ["fix", "bug", "error"]):
            return "FIX"
        elif any(word in request_lower for word in ["refactor", "improve", "optimize"]):
            return "REFACTOR"
        elif any(word in request_lower for word in ["analyze", "inspect", "review"]):
            return "ANALYZE"
        elif any(word in request_lower for word in ["audit", "check", "validate"]):
            return "AUDIT"
        elif any(word in request_lower for word in ["design", "architecture", "plan"]):
            return "DESIGN"
        
        return "ANALYZE"  # Default safe intent


class ToolValidator:
    """Validates tool usage against intent-based restrictions."""
    
    # Blocked tools for production intents
    BLOCKED_TOOLS_PRODUCTION = {
        "create_file",
        "replace_string_in_file",
        "edit_files",
        "run_in_terminal",  # For file operations only
        "edit_notebook_file",  # For code cells only
    }
    
    # Production code extensions
    PRODUCTION_EXTENSIONS = {
        ".py", ".ts", ".js", ".tsx", ".jsx",
        ".java", ".cs", ".go", ".rs"
    }
    
    # Exempt paths (allowed to use native tools)
    EXEMPT_PATHS = {".github/", "docs/", "tests/"}
    
    @classmethod
    def is_production_code(cls, file_path: str) -> bool:
        """Check if file is production code requiring MCP routing."""
        # Check if exempt path
        if any(exempt in file_path for exempt in cls.EXEMPT_PATHS):
            return False
        
        # Check extension
        return any(file_path.endswith(ext) for ext in cls.PRODUCTION_EXTENSIONS)
    
    @classmethod
    def validate_tool_for_intent(
        cls,
        tool: str,
        intent: str,
        file_path: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Validate if tool is allowed for given intent.
        
        Args:
            tool: Tool name (e.g., "create_file")
            intent: User intent (e.g., "IMPLEMENT")
            file_path: Target file path (optional)
        
        Returns:
            Tuple of (is_allowed, reason)
        """
        # Check if production intent (IMPLEMENT/FIX/REFACTOR)
        if intent in ["IMPLEMENT", "FIX", "REFACTOR"]:
            # Check if blocked tool
            if tool in cls.BLOCKED_TOOLS_PRODUCTION:
                # Check if targeting production code
                if file_path and cls.is_production_code(file_path):
                    return (
                        False,
                        f"Tool '{tool}' blocked for {intent} intent on production code. "
                        f"Use cortex_process_request instead."
                    )
        
        # Tool allowed
        return (True, "Tool allowed for this intent")


# ============================================================================
# TEST SUITE
# ============================================================================

class TestIntentClassification:
    """Test intent classification logic."""
    
    def test_implement_intent(self):
        """Test IMPLEMENT intent detection."""
        requests = [
            "implement user authentication",
            "create new API endpoint",
            "add logging functionality",
        ]
        for req in requests:
            assert IntentClassifier.classify(req) == "IMPLEMENT"
    
    def test_fix_intent(self):
        """Test FIX intent detection."""
        requests = [
            "fix the login bug",
            "resolve error in database connection",
            "bug in payment processing",
        ]
        for req in requests:
            assert IntentClassifier.classify(req) == "FIX"
    
    def test_refactor_intent(self):
        """Test REFACTOR intent detection."""
        requests = [
            "refactor the authentication module",
            "improve code structure",
            "optimize database queries",
        ]
        for req in requests:
            assert IntentClassifier.classify(req) == "REFACTOR"
    
    def test_analyze_intent(self):
        """Test ANALYZE intent detection."""
        requests = [
            "analyze the codebase",
            "inspect the API design",
            "review the architecture",
        ]
        for req in requests:
            assert IntentClassifier.classify(req) == "ANALYZE"


class TestProductionCodeDetection:
    """Test production code file detection."""
    
    def test_python_production_code(self):
        """Test Python production files are detected."""
        assert ToolValidator.is_production_code("src/main.py") is True
        assert ToolValidator.is_production_code("cortex/orchestrators/master.py") is True
    
    def test_typescript_production_code(self):
        """Test TypeScript production files are detected."""
        assert ToolValidator.is_production_code("src/app.ts") is True
        assert ToolValidator.is_production_code("frontend/components/Header.tsx") is True
    
    def test_exempt_paths_not_production(self):
        """Test exempt paths are not considered production code."""
        assert ToolValidator.is_production_code(".github/agents/core/CORTEX.md") is False
        assert ToolValidator.is_production_code("docs/architecture.md") is False
        assert ToolValidator.is_production_code("tests/unit/test_orchestrator.py") is False
    
    def test_non_code_files_not_production(self):
        """Test non-code files are not production code."""
        assert ToolValidator.is_production_code("README.md") is False
        assert ToolValidator.is_production_code("config.yaml") is False
        assert ToolValidator.is_production_code("data.json") is False


class TestToolValidation:
    """Test tool validation against intents."""
    
    def test_native_tools_blocked_for_implement(self):
        """Test native tools are blocked for IMPLEMENT intent on production code."""
        blocked_tools = [
            "create_file",
            "replace_string_in_file",
            "edit_files",
        ]
        
        for tool in blocked_tools:
            allowed, reason = ToolValidator.validate_tool_for_intent(
                tool=tool,
                intent="IMPLEMENT",
                file_path="src/main.py"
            )
            assert allowed is False
            assert "cortex_process_request" in reason
    
    def test_native_tools_blocked_for_fix(self):
        """Test native tools are blocked for FIX intent on production code."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="replace_string_in_file",
            intent="FIX",
            file_path="cortex/orchestrators/master.py"
        )
        assert allowed is False
        assert "cortex_process_request" in reason
    
    def test_native_tools_blocked_for_refactor(self):
        """Test native tools are blocked for REFACTOR intent on production code."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="edit_files",
            intent="REFACTOR",
            file_path="src/utils/helpers.ts"
        )
        assert allowed is False
        assert "cortex_process_request" in reason
    
    def test_native_tools_allowed_for_github_files(self):
        """Test native tools are allowed for .github files."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="create_file",
            intent="DESIGN",
            file_path=".github/agents/core/new-agent.md"
        )
        assert allowed is True
    
    def test_native_tools_allowed_for_docs(self):
        """Test native tools are allowed for docs files."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="replace_string_in_file",
            intent="IMPLEMENT",
            file_path="docs/architecture.md"
        )
        assert allowed is True
    
    def test_native_tools_allowed_for_analyze(self):
        """Test native tools are allowed for ANALYZE intent."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="create_file",
            intent="ANALYZE",
            file_path="src/main.py"
        )
        assert allowed is True


class TestBypassPrevention:
    """Test comprehensive bypass prevention scenarios."""
    
    def test_implement_on_python_file_blocks_create(self):
        """Test IMPLEMENT intent blocks create_file on Python production code."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="create_file",
            intent="IMPLEMENT",
            file_path="cortex/new_module.py"
        )
        assert allowed is False
        assert "IMPLEMENT" in reason
        assert "cortex_process_request" in reason
    
    def test_fix_on_typescript_file_blocks_replace(self):
        """Test FIX intent blocks replace_string_in_file on TypeScript code."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="replace_string_in_file",
            intent="FIX",
            file_path="src/services/auth.ts"
        )
        assert allowed is False
        assert "FIX" in reason
    
    def test_refactor_on_java_file_blocks_edit(self):
        """Test REFACTOR intent blocks edit_files on Java code."""
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool="edit_files",
            intent="REFACTOR",
            file_path="src/main/java/com/example/App.java"
        )
        assert allowed is False
        assert "REFACTOR" in reason
    
    def test_mcp_tools_always_allowed(self):
        """Test MCP tools are always allowed for any intent."""
        mcp_tools = [
            "cortex_process_request",
            "cortex_lens_analyze",
            "cortex_validate_environment",
        ]
        
        for tool in mcp_tools:
            # MCP tools not in BLOCKED_TOOLS_PRODUCTION
            assert tool not in ToolValidator.BLOCKED_TOOLS_PRODUCTION


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestEndToEndEnforcement:
    """End-to-end enforcement layer tests."""
    
    def test_full_workflow_implement_with_bypass_attempt(self):
        """Test full workflow: IMPLEMENT intent with native tool bypass attempt."""
        # User request
        user_request = "implement user authentication module"
        
        # Step 1: Classify intent
        intent = IntentClassifier.classify(user_request)
        assert intent == "IMPLEMENT"
        
        # Step 2: Attempt to use native tool
        tool = "create_file"
        file_path = "cortex/auth/user_authentication.py"
        
        # Step 3: Validate (should be blocked)
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool=tool,
            intent=intent,
            file_path=file_path
        )
        assert allowed is False
        assert "cortex_process_request" in reason
    
    def test_full_workflow_design_with_github_file(self):
        """Test full workflow: DESIGN intent with .github file (should be allowed)."""
        # User request
        user_request = "design new agent specification"
        
        # Step 1: Classify intent
        intent = IntentClassifier.classify(user_request)
        assert intent == "DESIGN"
        
        # Step 2: Attempt to use native tool
        tool = "create_file"
        file_path = ".github/agents/core/new-agent.md"
        
        # Step 3: Validate (should be allowed)
        allowed, reason = ToolValidator.validate_tool_for_intent(
            tool=tool,
            intent=intent,
            file_path=file_path
        )
        assert allowed is True


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
