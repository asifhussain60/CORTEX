"""
Tests for Native Tool Interception Layer.

Tests CORE-049 (MCP-FIRST) and CORE-050 (MCP Circuit Breaker) enforcement.
"""

import pytest
from unittest.mock import patch, MagicMock
from cortex.governance.enforcement.native_tool_interceptor import (
    NativeToolInterceptor,
    MCPDetector,
    Intent,
    InterceptionResult,
    check_tool_allowed,
)


class TestMCPDetector:
    """Test MCP availability detection (3-method cascade)."""
    
    def test_env_variable_detection(self, monkeypatch):
        """Test MCP detection via environment variable."""
        monkeypatch.setenv("CORTEX_MCP_ENABLED", "true")
        assert MCPDetector.is_mcp_available() is True
    
    def test_settings_file_detection(self, tmp_path, monkeypatch):
        """Test MCP detection via .vscode/settings.json."""
        monkeypatch.delenv("CORTEX_MCP_ENABLED", raising=False)
        
        settings_dir = tmp_path / ".vscode"
        settings_dir.mkdir()
        settings_file = settings_dir / "settings.json"
        settings_file.write_text('{"github.copilot.chat.mcpServers": {"cortex": {}}}')
        
        monkeypatch.chdir(tmp_path)
        assert MCPDetector.is_mcp_available() is True
    
    def test_unavailable_fallback(self, monkeypatch):
        """Test MCP unavailable when no detection methods succeed."""
        monkeypatch.delenv("CORTEX_MCP_ENABLED", raising=False)
        monkeypatch.chdir("/tmp")
        assert MCPDetector.is_mcp_available() is False


class TestNativeToolInterceptor:
    """Test native tool interception logic."""
    
    @pytest.fixture
    def interceptor(self):
        """Create interceptor instance."""
        return NativeToolInterceptor()
    
    # EXEMPT intents (always allowed)
    
    def test_diagnose_intent_always_allowed(self, interceptor):
        """DIAGNOSE intent bypasses MCP requirement."""
        result = interceptor.check("create_file", Intent.DIAGNOSE, "test.py")
        assert result.allowed is True
        assert "exempt" in result.reason.lower()
    
    def test_query_intent_always_allowed(self, interceptor):
        """QUERY intent bypasses MCP requirement."""
        result = interceptor.check("create_file", Intent.QUERY, "test.py")
        assert result.allowed is True
    
    def test_setup_intent_always_allowed(self, interceptor):
        """SETUP intent bypasses MCP requirement (for troubleshooting)."""
        result = interceptor.check("create_file", Intent.SETUP, "test.py")
        assert result.allowed is True
    
    # BLOCKED intents (require MCP)
    
    @patch.object(MCPDetector, "is_mcp_available", return_value=False)
    def test_implement_blocked_without_mcp(self, mock_detector, interceptor):
        """IMPLEMENT intent blocked if MCP unavailable."""
        result = interceptor.check("create_file", Intent.IMPLEMENT, "src/main.py")
        assert result.allowed is False
        assert "CORE-050" in result.reason
        assert result.mcp_tool == "cortex_process_request"
    
    @patch.object(MCPDetector, "is_mcp_available", return_value=False)
    def test_fix_blocked_without_mcp(self, mock_detector, interceptor):
        """FIX intent blocked if MCP unavailable."""
        result = interceptor.check("replace_string_in_file", Intent.FIX, "src/bug.py")
        assert result.allowed is False
        assert "MCP required" in result.reason
    
    @patch.object(MCPDetector, "is_mcp_available", return_value=False)
    def test_refactor_blocked_without_mcp(self, mock_detector, interceptor):
        """REFACTOR intent blocked if MCP unavailable."""
        result = interceptor.check("edit_files", Intent.REFACTOR, "src/old.py")
        assert result.allowed is False
    
    # Production code protection (even with MCP available)
    
    @patch.object(MCPDetector, "is_mcp_available", return_value=True)
    def test_production_code_requires_mcp_tool(self, mock_detector, interceptor):
        """Production code modification requires MCP tool even if MCP available."""
        result = interceptor.check("create_file", Intent.IMPLEMENT, "cortex/main.py")
        assert result.allowed is False
        assert "Production code" in result.reason
        assert result.mcp_tool == "cortex_process_request"
    
    @patch.object(MCPDetector, "is_mcp_available", return_value=True)
    def test_non_production_allowed(self, mock_detector, interceptor):
        """Non-production files allowed even for IMPLEMENT."""
        result = interceptor.check("create_file", Intent.IMPLEMENT, "docs/guide.md")
        assert result.allowed is True
    
    # Read-only operations (always allowed)
    
    def test_read_file_always_allowed(self, interceptor):
        """read_file allowed for all intents."""
        result = interceptor.check("read_file", Intent.IMPLEMENT, "src/main.py")
        assert result.allowed is True
        assert "Read-only" in result.reason
    
    def test_grep_search_always_allowed(self, interceptor):
        """grep_search allowed for all intents."""
        result = interceptor.check("grep_search", Intent.FIX, "src/")
        assert result.allowed is True
    
    def test_file_search_always_allowed(self, interceptor):
        """file_search allowed for discovery."""
        result = interceptor.check("file_search", Intent.IMPLEMENT, "*.py")
        assert result.allowed is True
    
    # Terminal command filtering
    
    def test_terminal_file_ops_blocked(self, interceptor):
        """Terminal file operations blocked for IMPLEMENT."""
        result = interceptor.check(
            "run_in_terminal",
            Intent.IMPLEMENT,
            target_file=None,
            command="echo 'test' > output.txt"
        )
        assert result.allowed is False
        assert "File operations via terminal blocked" in result.reason
    
    def test_terminal_non_file_ops_allowed(self, interceptor):
        """Terminal non-file operations allowed."""
        result = interceptor.check(
            "run_in_terminal",
            Intent.IMPLEMENT,
            command="pytest tests/"
        )
        assert result.allowed is True
    
    # Unknown tools (safe default)
    
    def test_unknown_tool_allowed(self, interceptor):
        """Unknown tools allowed (extensibility)."""
        result = interceptor.check("future_tool", Intent.IMPLEMENT)
        assert result.allowed is True
        assert "Unknown tool" in result.reason


class TestGlobalCheckFunction:
    """Test global check_tool_allowed function."""
    
    @patch.object(MCPDetector, "is_mcp_available", return_value=False)
    def test_global_function_blocks_correctly(self, mock_detector):
        """Global function applies same interception rules."""
        result = check_tool_allowed("create_file", Intent.IMPLEMENT, "src/main.py")
        assert result.allowed is False
        assert result.mcp_tool == "cortex_process_request"
    
    def test_global_function_allows_exempt(self):
        """Global function allows exempt intents."""
        result = check_tool_allowed("create_file", Intent.DIAGNOSE, "test.py")
        assert result.allowed is True
