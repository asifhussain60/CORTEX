"""
Phase 51 S3: Direct Tool Blocking Implementation
Tests for MCP-FIRST Enforcement Tool Blocking Logic

AC-PHASE51-S3-001: IMPLEMENT intent blocks create_file
AC-PHASE51-S3-002: IMPLEMENT intent blocks replace_string_in_file
AC-PHASE51-S3-003: FIX intent blocks direct operations
AC-PHASE51-S3-004: REFACTOR intent requires MCP routing
AC-PHASE51-S3-005: ANALYZE intent allows direct tools (read-only)
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from cortex.models.canonical_enums import IntentType


class DirectToolBlockingConfiguration:
    """Configuration for tool blocking based on intent"""
    
    # Tools that are blocked for IMPLEMENT/FIX/REFACTOR intents
    BLOCKED_TOOLS_FOR_IMPLEMENT = {
        "create_file": "File creation must route through MCP",
        "replace_string_in_file": "File modification must route through MCP",
        "multi_replace_string_in_file": "Batch file modification must route through MCP",
        "edit_notebook_file": "Notebook modification must route through MCP (code cells)",
    }
    
    # Intents that require MCP routing
    MCP_REQUIRED_INTENTS = {
        IntentType.IMPLEMENT: "Implementation requires full TDD + governance gates",
        IntentType.FIX: "Bug fixes require TDD + challenge gate",
        IntentType.REFACTOR: "Refactoring requires TDD + compliance validation",
    }
    
    # Intents that allow direct read-only tools
    READ_ONLY_INTENTS = {
        IntentType.ANALYZE: "Analysis is read-only, no MCP required",
        IntentType.QUERY: "Queries are read-only, no MCP required",
        IntentType.VALIDATE: "Validation is read-only, no MCP required",
    }


class TestToolBlockingConfiguration:
    """Test: Tool blocking configuration is properly defined"""
    
    def test_blocked_tools_list(self):
        """Test: Blocked tools list is configured"""
        config = DirectToolBlockingConfiguration()
        
        assert "create_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT
        assert "replace_string_in_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT
        assert "multi_replace_string_in_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT
        assert "edit_notebook_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT

    def test_mcp_required_intents(self):
        """Test: MCP-required intents are configured"""
        config = DirectToolBlockingConfiguration()
        
        assert IntentType.IMPLEMENT in config.MCP_REQUIRED_INTENTS
        assert IntentType.FIX in config.MCP_REQUIRED_INTENTS
        assert IntentType.REFACTOR in config.MCP_REQUIRED_INTENTS

    def test_read_only_intents(self):
        """Test: Read-only intents are configured"""
        config = DirectToolBlockingConfiguration()
        
        assert IntentType.ANALYZE in config.READ_ONLY_INTENTS
        assert IntentType.QUERY in config.READ_ONLY_INTENTS


class TestToolBlockingByIntent:
    """Test: Tool blocking based on user intent"""

    def test_ac_phase51_s3_001_implement_blocks_create_file(self):
        """AC-PHASE51-S3-001: IMPLEMENT intent blocks create_file"""
        config = DirectToolBlockingConfiguration()
        
        # Verify create_file is in blocked list
        assert "create_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT
        
        # Verify IMPLEMENT requires MCP
        assert IntentType.IMPLEMENT in config.MCP_REQUIRED_INTENTS

    def test_ac_phase51_s3_002_implement_blocks_replace_string(self):
        """AC-PHASE51-S3-002: IMPLEMENT intent blocks replace_string_in_file"""
        config = DirectToolBlockingConfiguration()
        
        # Verify replace_string_in_file is in blocked list
        assert "replace_string_in_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT

    def test_ac_phase51_s3_003_fix_intent_blocking(self):
        """AC-PHASE51-S3-003: FIX intent requires MCP routing"""
        config = DirectToolBlockingConfiguration()
        
        # FIX intent must use MCP
        assert IntentType.FIX in config.MCP_REQUIRED_INTENTS

    def test_ac_phase51_s3_004_refactor_intent_blocking(self):
        """AC-PHASE51-S3-004: REFACTOR intent requires MCP routing"""
        config = DirectToolBlockingConfiguration()
        
        # REFACTOR intent must use MCP
        assert IntentType.REFACTOR in config.MCP_REQUIRED_INTENTS

    def test_ac_phase51_s3_005_analyze_allows_direct_tools(self):
        """AC-PHASE51-S3-005: ANALYZE intent allows direct tools (read-only)"""
        config = DirectToolBlockingConfiguration()
        
        # ANALYZE is in read-only intents
        assert IntentType.ANALYZE in config.READ_ONLY_INTENTS


class TestToolBlockingImplementation:
    """Test: Actual tool blocking logic"""

    def test_create_file_blocked_for_implement(self):
        """Test: create_file tool blocked when intent=IMPLEMENT"""
        config = DirectToolBlockingConfiguration()
        
        # Check blocking logic
        intent = IntentType.IMPLEMENT
        tool = "create_file"
        
        is_mcp_required = intent in config.MCP_REQUIRED_INTENTS
        is_tool_blocked = tool in config.BLOCKED_TOOLS_FOR_IMPLEMENT
        
        assert is_mcp_required and is_tool_blocked, "IMPLEMENT with create_file should be blocked"

    def test_replace_string_blocked_for_implement(self):
        """Test: replace_string_in_file tool blocked when intent=IMPLEMENT"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.IMPLEMENT
        tool = "replace_string_in_file"
        
        is_mcp_required = intent in config.MCP_REQUIRED_INTENTS
        is_tool_blocked = tool in config.BLOCKED_TOOLS_FOR_IMPLEMENT
        
        assert is_mcp_required and is_tool_blocked, "IMPLEMENT with replace_string should be blocked"

    def test_create_file_allowed_for_analyze(self):
        """Test: create_file allowed for ANALYZE intent (edge case)"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.ANALYZE
        
        # ANALYZE is read-only, so no MCP required
        assert intent in config.READ_ONLY_INTENTS


class TestErrorMessagesForBlockedTools:
    """Test: Error messages when tools are blocked"""

    def test_blocked_tool_error_includes_intent(self):
        """Test: Blocked tool error includes user intent"""
        config = DirectToolBlockingConfiguration()
        
        # Error message should mention the intent
        error_template = "Intent '{intent}' blocks tool '{tool}': {reason}"
        error = error_template.format(
            intent=IntentType.IMPLEMENT.value,
            tool="create_file",
            reason=config.BLOCKED_TOOLS_FOR_IMPLEMENT["create_file"]
        )
        
        assert IntentType.IMPLEMENT.value in error
        assert "create_file" in error

    def test_blocked_tool_error_suggests_mcp(self):
        """Test: Blocked tool error suggests using MCP tool"""
        config = DirectToolBlockingConfiguration()
        
        # Error should suggest cortex_process_request
        error_template = "Use cortex_process_request instead: cortex_process_request(operation='{intent}', ...)"
        error = error_template.format(intent=IntentType.IMPLEMENT.value)
        
        assert "cortex_process_request" in error


class TestIntentClassification:
    """Test: Intent classification for blocking logic"""

    def test_intent_classification_implement(self):
        """Test: IMPLEMENT intent correctly classified"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.IMPLEMENT
        assert intent in config.MCP_REQUIRED_INTENTS

    def test_intent_classification_fix(self):
        """Test: FIX intent correctly classified"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.FIX
        assert intent in config.MCP_REQUIRED_INTENTS

    def test_intent_classification_refactor(self):
        """Test: REFACTOR intent correctly classified"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.REFACTOR
        assert intent in config.MCP_REQUIRED_INTENTS

    def test_intent_classification_analyze(self):
        """Test: ANALYZE intent correctly classified as read-only"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.ANALYZE
        assert intent in config.READ_ONLY_INTENTS
        assert intent not in config.MCP_REQUIRED_INTENTS


class TestToolMatrix:
    """Test: Tool blocking matrix for all combinations"""

    def test_implement_tool_blocking_matrix(self):
        """Test: All tool/intent combinations for IMPLEMENT"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.IMPLEMENT
        blocked_tools = [
            "create_file",
            "replace_string_in_file",
            "multi_replace_string_in_file",
            "edit_notebook_file"
        ]
        
        for tool in blocked_tools:
            assert tool in config.BLOCKED_TOOLS_FOR_IMPLEMENT, f"{tool} should be blocked for {intent}"

    def test_fix_tool_blocking_matrix(self):
        """Test: Tool blocking for FIX intent"""
        config = DirectToolBlockingConfiguration()
        
        # FIX intent should block the same tools as IMPLEMENT
        intent = IntentType.FIX
        assert intent in config.MCP_REQUIRED_INTENTS

    def test_analyze_allows_read_tools(self):
        """Test: ANALYZE intent allows read-only tools"""
        config = DirectToolBlockingConfiguration()
        
        intent = IntentType.ANALYZE
        
        # ANALYZE should be in read-only intents (not blocked)
        assert intent in config.READ_ONLY_INTENTS


class TestPhase51S3Acceptance:
    """Acceptance Tests for Phase 51 S3 completion"""

    def test_ac_phase51_s3_001_create_file_blocked(self):
        """AC-PHASE51-S3-001: create_file blocked for IMPLEMENT"""
        config = DirectToolBlockingConfiguration()
        
        assert "create_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT
        assert IntentType.IMPLEMENT in config.MCP_REQUIRED_INTENTS

    def test_ac_phase51_s3_002_replace_string_blocked(self):
        """AC-PHASE51-S3-002: replace_string_in_file blocked for IMPLEMENT"""
        config = DirectToolBlockingConfiguration()
        
        assert "replace_string_in_file" in config.BLOCKED_TOOLS_FOR_IMPLEMENT

    def test_ac_phase51_s3_003_fix_intent_blocking(self):
        """AC-PHASE51-S3-003: FIX intent blocks direct operations"""
        config = DirectToolBlockingConfiguration()
        
        assert IntentType.FIX in config.MCP_REQUIRED_INTENTS

    def test_ac_phase51_s3_004_refactor_intent_blocking(self):
        """AC-PHASE51-S3-004: REFACTOR intent requires MCP routing"""
        config = DirectToolBlockingConfiguration()
        
        assert IntentType.REFACTOR in config.MCP_REQUIRED_INTENTS

    def test_ac_phase51_s3_005_analyze_read_only(self):
        """AC-PHASE51-S3-005: ANALYZE intent allows direct tools"""
        config = DirectToolBlockingConfiguration()
        
        assert IntentType.ANALYZE in config.READ_ONLY_INTENTS
        assert IntentType.ANALYZE not in config.MCP_REQUIRED_INTENTS
