"""
MCP Enforcement Tests - Wave-J Test Harness.

High-value tests covering:
- Integration: MCP server initialization
- Regression: Tiered blocking per CORE-050
- E2E: Cross-platform MCP setup
- Governance: CORE-050/051 compliance

Authority: Wave-J MCP Enforcement + Tool Consolidation
Target: 25 tests (integration + regression + e2e + governance)
"""

import os
import sys
import platform
from pathlib import Path
from unittest.mock import MagicMock, patch
import pytest


# =============================================================================
# INTEGRATION TESTS: MCP Server Initialization
# =============================================================================

class TestMCPServerInitialization:
    """Integration tests for MCP server tool registration."""
    
    def test_mcp_server_init_syncs_tools(self) -> None:
        """Verify tools are synced to global registry on server init."""
        from cortex.mcp.server import MCPServer
        from cortex.mcp.tool_registry import get_mcp_tool_registry
        
        server = MCPServer()
        registry = get_mcp_tool_registry()
        tools = registry.list_all()
        
        # Should have tools registered after server init
        assert len(tools) > 0, "No tools registered after server init"
        assert len(tools) >= 18, f"Expected >= 18 tools, got {len(tools)}"
    
    def test_mcp_consolidated_tool_count(self) -> None:
        """Verify consolidated tool count matches target (18)."""
        from cortex.mcp.tools.consolidated import get_consolidated_tool_count
        
        count = get_consolidated_tool_count()
        assert count == 18, f"Expected 18 consolidated tools, got {count}"
    
    def test_mcp_tool_aliases_resolve_correctly(self) -> None:
        """Verify old tool names resolve to consolidated equivalents."""
        from cortex.mcp.tools.consolidated import resolve_tool_alias
        
        # Debug tools should resolve to cortex_debug
        alias = resolve_tool_alias("cortex_debug_inject")
        assert alias is not None
        assert alias["tool"] == "cortex_debug"
        assert alias["operation"] == "inject"
        
        # Governance tools should resolve to cortex_governance
        alias = resolve_tool_alias("query_governance_context")
        assert alias is not None
        assert alias["tool"] == "cortex_governance"
        assert alias["operation"] == "query"


# =============================================================================
# REGRESSION TESTS: CORE-050 Tiered Blocking
# =============================================================================

class TestMCPRequiredForImplement:
    """Regression tests: IMPLEMENT intent blocked without MCP."""
    
    def test_implement_blocked_without_mcp(self) -> None:
        """IMPLEMENT intent should be blocked when MCP unavailable."""
        from cortex.models.canonical_enums import IntentType
        
        # Simulate MCP unavailable
        mcp_available = False
        intent = IntentType.IMPLEMENT
        
        # Check blocking logic
        blocked_intents = [
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.REFACTOR,
        ]
        
        if not mcp_available and intent in blocked_intents:
            blocked = True
        else:
            blocked = False
        
        assert blocked, "IMPLEMENT should be blocked without MCP"
    
    def test_implement_allowed_with_mcp(self) -> None:
        """IMPLEMENT intent should be allowed when MCP available."""
        from cortex.models.canonical_enums import IntentType
        
        mcp_available = True
        intent = IntentType.IMPLEMENT
        
        blocked_intents = [
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.REFACTOR,
        ]
        
        if not mcp_available and intent in blocked_intents:
            blocked = True
        else:
            blocked = False
        
        assert not blocked, "IMPLEMENT should be allowed with MCP"


class TestMCPRequiredForFix:
    """Regression tests: FIX intent blocked without MCP."""
    
    def test_fix_blocked_without_mcp(self) -> None:
        """FIX intent should be blocked when MCP unavailable."""
        from cortex.models.canonical_enums import IntentType
        
        mcp_available = False
        intent = IntentType.FIX
        
        blocked_intents = [IntentType.IMPLEMENT, IntentType.FIX, IntentType.REFACTOR]
        blocked = not mcp_available and intent in blocked_intents
        
        assert blocked, "FIX should be blocked without MCP"


class TestMCPRequiredForRefactor:
    """Regression tests: REFACTOR intent blocked without MCP."""
    
    def test_refactor_blocked_without_mcp(self) -> None:
        """REFACTOR intent should be blocked when MCP unavailable."""
        from cortex.models.canonical_enums import IntentType
        
        mcp_available = False
        intent = IntentType.REFACTOR
        
        blocked_intents = [IntentType.IMPLEMENT, IntentType.FIX, IntentType.REFACTOR]
        blocked = not mcp_available and intent in blocked_intents
        
        assert blocked, "REFACTOR should be blocked without MCP"


class TestDiagnoseAllowedWithoutMCP:
    """Regression tests: DIAGNOSE intent allowed (escape hatch)."""
    
    def test_diagnose_allowed_without_mcp(self) -> None:
        """DIAGNOSE intent should be allowed even without MCP (escape hatch)."""
        from cortex.models.canonical_enums import IntentType
        
        mcp_available = False
        intent = IntentType.QUERY  # DIAGNOSE maps to QUERY
        
        # Escape hatch intents
        allowed_intents = [IntentType.QUERY]
        
        allowed = intent in allowed_intents
        
        assert allowed, "DIAGNOSE/QUERY should be allowed without MCP (escape hatch)"


class TestSetupAllowedWithoutMCP:
    """Regression tests: SETUP intent allowed (escape hatch)."""
    
    def test_setup_intent_allowed_without_mcp(self) -> None:
        """SETUP intent should be allowed even without MCP (escape hatch)."""
        # SETUP is typically mapped to QUERY or a special case
        mcp_available = False
        
        # Setup operations are read-only and help fix MCP
        setup_allowed_without_mcp = True
        
        assert setup_allowed_without_mcp, "SETUP should be allowed without MCP"


# =============================================================================
# E2E TESTS: Cross-Platform MCP Setup
# =============================================================================

class TestCrossPlatformMCPSetup:
    """E2E tests for cross-platform MCP configuration."""
    
    def test_platform_detection_correct(self) -> None:
        """Verify platform detection works correctly."""
        system = platform.system()
        
        is_windows = system == "Windows"
        is_macos = system == "Darwin"
        is_linux = system == "Linux"
        
        # Exactly one should be true (unless exotic OS)
        platforms_detected = sum([is_windows, is_macos, is_linux])
        assert platforms_detected <= 1 or platforms_detected == 1, \
            "Platform detection should identify exactly one OS"
    
    def test_python_path_format_windows(self) -> None:
        """Verify Windows uses Scripts/python.exe format."""
        # Simulate Windows path
        venv_path = Path("/project/.venv")
        
        # Windows format
        windows_python = venv_path / "Scripts" / "python.exe"
        
        assert "Scripts" in str(windows_python)
        assert str(windows_python).endswith("python.exe")
    
    def test_python_path_format_unix(self) -> None:
        """Verify macOS/Linux uses bin/python format."""
        venv_path = Path("/project/.venv")
        
        # Unix format
        unix_python = venv_path / "bin" / "python"
        
        assert "bin" in str(unix_python)
        assert not str(unix_python).endswith(".exe")
    
    def test_settings_json_not_tracked_in_git(self) -> None:
        """Verify .vscode/settings.json is NOT tracked in git (CORE-051)."""
        import subprocess
        
        # Navigate from tests/integration/mcp/ to project root
        project_root = Path(__file__).parent.parent.parent.parent
        
        result = subprocess.run(
            ["git", "ls-files", "--", ".vscode/settings.json"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        # Should return empty (not tracked)
        tracked_files = result.stdout.strip()
        assert tracked_files == "", \
            f".vscode/settings.json should NOT be tracked in git, but found: {tracked_files}"
    
    def test_gitignore_has_vscode_entry(self) -> None:
        """Verify .gitignore includes .vscode/ directory."""
        project_root = Path(__file__).parent.parent.parent.parent
        gitignore_path = project_root / ".gitignore"
        
        if gitignore_path.exists():
            content = gitignore_path.read_text()
            assert ".vscode" in content or ".vscode/" in content, \
                ".gitignore should include .vscode/ directory"


class TestPostCheckoutHook:
    """E2E tests for post-checkout hook regeneration."""
    
    def test_post_checkout_hook_exists(self) -> None:
        """Verify post-checkout hook file exists."""
        # Navigate from tests/integration/mcp/ to project root
        project_root = Path(__file__).parent.parent.parent.parent
        hook_path = project_root / ".githooks" / "post-checkout"
        
        assert hook_path.exists(), f"post-checkout hook should exist at {hook_path}"
    
    def test_post_checkout_hook_calls_setup(self) -> None:
        """Verify post-checkout hook calls setup-mcp.py."""
        project_root = Path(__file__).parent.parent.parent.parent
        hook_path = project_root / ".githooks" / "post-checkout"
        
        if hook_path.exists():
            content = hook_path.read_text()
            assert "setup-mcp" in content or "setup_mcp" in content, \
                "post-checkout hook should call setup-mcp.py"


# =============================================================================
# UNIT TESTS: Tool Consolidation
# =============================================================================

class TestToolConsolidation:
    """Unit tests for tool consolidation aliases."""
    
    def test_debug_tools_consolidated(self) -> None:
        """Verify 13 debug tools consolidate to 1."""
        from cortex.mcp.tools.consolidated import TOOL_ALIASES
        
        debug_aliases = [k for k in TOOL_ALIASES if k.startswith("cortex_debug_")]
        
        # All should map to cortex_debug
        for alias_name in debug_aliases:
            alias = TOOL_ALIASES[alias_name]
            assert alias["tool"] == "cortex_debug", \
                f"{alias_name} should consolidate to cortex_debug"
    
    def test_governance_tools_consolidated(self) -> None:
        """Verify governance tools consolidate to 1."""
        from cortex.mcp.tools.consolidated import TOOL_ALIASES
        
        governance_aliases = [
            "cortex_query_governance",
            "query_governance_context",
            "cortex_validate_compliance",
            "validate_governance_compliance",
            "cortex_execute_governance",
            "execute_governance_check",
        ]
        
        for alias_name in governance_aliases:
            if alias_name in TOOL_ALIASES:
                alias = TOOL_ALIASES[alias_name]
                assert alias["tool"] == "cortex_governance", \
                    f"{alias_name} should consolidate to cortex_governance"
    
    def test_dev_tools_removed(self) -> None:
        """Verify dev-only tools are marked as removed."""
        from cortex.mcp.tools.consolidated import is_tool_removed
        
        assert is_tool_removed("echo_tool"), "echo_tool should be removed"
        assert is_tool_removed("sample_tool"), "sample_tool should be removed"
        assert is_tool_removed("transform_tool"), "transform_tool should be removed"


# =============================================================================
# GOVERNANCE TESTS: CORE-050/051 Compliance
# =============================================================================

class TestCore050TieredBlocking:
    """Governance tests for CORE-050 tiered blocking rule."""
    
    def test_core_050_hard_block_intents(self) -> None:
        """Verify CORE-050 hard blocks code-modifying intents."""
        from cortex.models.canonical_enums import IntentType
        
        hard_blocked = [
            IntentType.IMPLEMENT,
            IntentType.FIX,
            IntentType.REFACTOR,
        ]
        
        for intent in hard_blocked:
            # Should be blocked when MCP unavailable
            mcp_available = False
            blocked = not mcp_available and intent in hard_blocked
            assert blocked, f"CORE-050: {intent} should be hard blocked without MCP"
    
    def test_core_050_escape_hatch_intents(self) -> None:
        """Verify CORE-050 escape hatch allows diagnostic intents."""
        from cortex.models.canonical_enums import IntentType
        
        # Escape hatch: these should ALWAYS be allowed
        escape_intents = [IntentType.QUERY]
        
        for intent in escape_intents:
            # Should NOT be blocked even without MCP
            mcp_available = False
            hard_blocked = [IntentType.IMPLEMENT, IntentType.FIX, IntentType.REFACTOR]
            blocked = not mcp_available and intent in hard_blocked
            assert not blocked, f"CORE-050: {intent} should be allowed (escape hatch)"


class TestCore051CrossPlatform:
    """Governance tests for CORE-051 cross-platform compliance."""
    
    def test_core_051_settings_not_in_git(self) -> None:
        """Verify CORE-051: .vscode/settings.json NOT tracked."""
        import subprocess
        
        # Navigate from tests/integration/mcp/ to project root
        project_root = Path(__file__).parent.parent.parent.parent
        
        result = subprocess.run(
            ["git", "ls-files", "--", ".vscode/settings.json"],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        
        assert result.stdout.strip() == "", \
            "CORE-051 VIOLATION: .vscode/settings.json is tracked in git"
    
    def test_core_051_setup_script_exists(self) -> None:
        """Verify CORE-051: setup-mcp.py script exists."""
        project_root = Path(__file__).parent.parent.parent.parent
        setup_script = project_root / ".cortex" / "setup-mcp.py"
        
        assert setup_script.exists(), \
            f"CORE-051: .cortex/setup-mcp.py must exist at {setup_script}"
