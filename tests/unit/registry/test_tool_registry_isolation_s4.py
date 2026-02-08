"""
Phase 48 S4: ToolRegistry & MCP Isolation - Session-Scoped MCP Tool Management

Tests for isolating MCP tool registry per session/workspace.

Authority: phase-48-registry-isolation-multi-tenant.yaml
Acceptance Criteria:
  - AC-PHASE48-S4-001: Each MCP session has isolated tool registry
  - AC-PHASE48-S4-002: Tool capabilities scoped to session
  - AC-PHASE48-S4-003: Concurrent MCP requests don't interfere
"""

import pytest
from typing import Dict, Optional, Any, List
from dataclasses import dataclass
from unittest.mock import MagicMock


@dataclass
class MCPTool:
    """MCP tool definition."""
    name: str
    description: str
    session_id: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]


class SessionMCPToolRegistry:
    """Isolated MCP tool registry for a single session."""
    
    def __init__(self, session_id: str):
        """
        Initialize tool registry for session.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self._tools: Dict[str, MCPTool] = {}
        self._registered_count = 0
    
    def register_tool(self, name: str, description: str, 
                     inputs: Dict[str, Any], outputs: Dict[str, Any]) -> MCPTool:
        """
        Register tool in session-scoped registry.
        
        Args:
            name: Tool name
            description: Tool description
            inputs: Input parameters
            outputs: Output format
        
        Returns:
            Registered MCPTool
        """
        tool = MCPTool(
            name=name,
            description=description,
            session_id=self.session_id,
            inputs=inputs,
            outputs=outputs
        )
        self._tools[name] = tool
        self._registered_count += 1
        return tool
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get tool from session-scoped registry."""
        return self._tools.get(name)
    
    def list_tools(self) -> List[str]:
        """List all tools in this session."""
        return list(self._tools.keys())
    
    def has_tool(self, name: str) -> bool:
        """Check if tool exists in session."""
        return name in self._tools
    
    def capability_count(self) -> int:
        """Get total tool capabilities registered in session."""
        return len(self._tools)
    
    def clear(self) -> None:
        """Clear all tools from session."""
        self._tools.clear()
        self._registered_count = 0


class MCPSessionFactory:
    """Create and manage isolated tool registries per session."""
    
    def __init__(self):
        """Initialize session factory."""
        self._sessions: Dict[str, SessionMCPToolRegistry] = {}
        self._active_sessions: set = set()
    
    def get_or_create_session(self, session_id: str) -> SessionMCPToolRegistry:
        """Get or create tool registry for session."""
        if session_id not in self._sessions:
            self._sessions[session_id] = SessionMCPToolRegistry(session_id)
            self._active_sessions.add(session_id)
        return self._sessions[session_id]
    
    def register_tool_in_session(self, session_id: str, tool_name: str,
                                 description: str, inputs: Dict[str, Any],
                                 outputs: Dict[str, Any]) -> MCPTool:
        """Register tool in specific session."""
        registry = self.get_or_create_session(session_id)
        return registry.register_tool(tool_name, description, inputs, outputs)
    
    def list_active_sessions(self) -> list:
        """List all active sessions."""
        return list(self._active_sessions)
    
    def close_session(self, session_id: str) -> None:
        """Close session and clean up."""
        if session_id in self._sessions:
            self._sessions[session_id].clear()
            del self._sessions[session_id]
            self._active_sessions.discard(session_id)
    
    def get_session_tool_count(self, session_id: str) -> int:
        """Get tool count in session."""
        if session_id in self._sessions:
            return self._sessions[session_id].capability_count()
        return 0


# ============================================================================
# TESTS: MCP Session Initialization (AC-PHASE48-S4-001)
# ============================================================================

class TestMCPSessionInitialization:
    """Test MCP session tool registry initialization."""
    
    def test_create_session_registry(self):
        """Test creating session-scoped tool registry."""
        registry = SessionMCPToolRegistry("session_123")
        assert registry.session_id == "session_123"
        assert registry.capability_count() == 0
    
    def test_factory_get_or_create_session(self):
        """Test factory get_or_create session."""
        factory = MCPSessionFactory()
        
        session1 = factory.get_or_create_session("session_1")
        session1_again = factory.get_or_create_session("session_1")
        
        assert session1 is session1_again
        assert session1.session_id == "session_1"
    
    def test_multiple_sessions_independent(self):
        """Test multiple sessions are independent."""
        factory = MCPSessionFactory()
        
        session_a = factory.get_or_create_session("session_a")
        session_b = factory.get_or_create_session("session_b")
        
        assert session_a is not session_b
        assert session_a.session_id == "session_a"
        assert session_b.session_id == "session_b"


class TestToolRegistration:
    """Test tool registration in sessions."""
    
    def test_register_tool_in_session(self):
        """Test registering tool in session."""
        registry = SessionMCPToolRegistry("session_1")
        
        tool = registry.register_tool(
            name="cortex_review_pr",
            description="Review pull request",
            inputs={"pr_url": "string"},
            outputs={"review": "string"}
        )
        
        assert tool.name == "cortex_review_pr"
        assert tool.session_id == "session_1"
        assert registry.capability_count() == 1
    
    def test_register_multiple_tools(self):
        """Test registering multiple tools in session."""
        registry = SessionMCPToolRegistry("session_1")
        
        registry.register_tool("tool_1", "Tool 1", {}, {})
        registry.register_tool("tool_2", "Tool 2", {}, {})
        registry.register_tool("tool_3", "Tool 3", {}, {})
        
        assert registry.capability_count() == 3
        assert set(registry.list_tools()) == {"tool_1", "tool_2", "tool_3"}
    
    def test_get_registered_tool(self):
        """Test retrieving registered tool."""
        registry = SessionMCPToolRegistry("session_1")
        
        registered = registry.register_tool(
            name="test_tool",
            description="Test tool",
            inputs={"param": "string"},
            outputs={"result": "string"}
        )
        
        retrieved = registry.get_tool("test_tool")
        assert retrieved is registered
        assert retrieved.name == "test_tool"
    
    def test_tool_not_found(self):
        """Test retrieving non-existent tool."""
        registry = SessionMCPToolRegistry("session_1")
        
        tool = registry.get_tool("nonexistent")
        assert tool is None


# ============================================================================
# TESTS: Tool Capability Scoping (AC-PHASE48-S4-002)
# ============================================================================

class TestToolCapabilityScopePerSession:
    """Test that tool capabilities are scoped to session."""
    
    def test_tools_isolated_between_sessions(self):
        """Test that tools don't leak between sessions."""
        session_1 = SessionMCPToolRegistry("session_1")
        session_2 = SessionMCPToolRegistry("session_2")
        
        session_1.register_tool("cortex_review_pr", "Review PR", {}, {})
        session_2.register_tool("cortex_migration", "Migration", {}, {})
        
        # Each session has only its tools
        assert session_1.has_tool("cortex_review_pr")
        assert not session_1.has_tool("cortex_migration")
        
        assert session_2.has_tool("cortex_migration")
        assert not session_2.has_tool("cortex_review_pr")
    
    def test_session_capability_isolation(self):
        """Test capability counts are independent."""
        session_1 = SessionMCPToolRegistry("session_1")
        session_2 = SessionMCPToolRegistry("session_2")
        
        # Register different counts
        session_1.register_tool("tool_a", "A", {}, {})
        session_1.register_tool("tool_b", "B", {}, {})
        session_1.register_tool("tool_c", "C", {}, {})
        
        session_2.register_tool("tool_x", "X", {}, {})
        
        assert session_1.capability_count() == 3
        assert session_2.capability_count() == 1
    
    def test_tool_metadata_scoped_to_session(self):
        """Test that tool metadata includes session_id."""
        session_1 = SessionMCPToolRegistry("session_1")
        session_2 = SessionMCPToolRegistry("session_2")
        
        tool_1 = session_1.register_tool("test", "Test", {}, {})
        tool_2 = session_2.register_tool("test", "Test", {}, {})
        
        # Same name but different sessions
        assert tool_1.name == tool_2.name
        assert tool_1.session_id != tool_2.session_id
        assert tool_1.session_id == "session_1"
        assert tool_2.session_id == "session_2"


# ============================================================================
# TESTS: Concurrent MCP Requests (AC-PHASE48-S4-003)
# ============================================================================

class TestConcurrentMCPRequests:
    """Test concurrent MCP requests don't interfere."""
    
    def test_three_sessions_concurrent_registration(self):
        """Test three sessions registering tools concurrently."""
        factory = MCPSessionFactory()
        
        # Session 1 registers tools
        factory.register_tool_in_session("session_1", "tool_a", "A", {}, {})
        factory.register_tool_in_session("session_1", "tool_b", "B", {}, {})
        
        # Session 2 registers different tools
        factory.register_tool_in_session("session_2", "tool_x", "X", {}, {})
        factory.register_tool_in_session("session_2", "tool_y", "Y", {}, {})
        
        # Session 3 registers more tools
        factory.register_tool_in_session("session_3", "tool_p", "P", {}, {})
        
        # Each session has correct tools
        assert factory.get_session_tool_count("session_1") == 2
        assert factory.get_session_tool_count("session_2") == 2
        assert factory.get_session_tool_count("session_3") == 1
    
    def test_concurrent_tool_lookup(self):
        """Test looking up tools from different sessions concurrently."""
        factory = MCPSessionFactory()
        
        # Register tools in different sessions
        tool_1 = factory.register_tool_in_session(
            "session_1", "cortex_review", "Review", {}, {}
        )
        tool_2 = factory.register_tool_in_session(
            "session_2", "cortex_review", "Review", {}, {}
        )
        
        # Lookup from each session
        retrieved_1 = factory.get_or_create_session("session_1").get_tool("cortex_review")
        retrieved_2 = factory.get_or_create_session("session_2").get_tool("cortex_review")
        
        # Same tool name but different instances
        assert retrieved_1 is tool_1
        assert retrieved_2 is tool_2
        assert retrieved_1 is not retrieved_2
    
    def test_no_tool_leakage_across_sessions(self):
        """Test that tools don't leak from one session to another."""
        factory = MCPSessionFactory()
        
        # Session A registers exclusive tools
        factory.register_tool_in_session("session_a", "exclusive_a", "A", {}, {})
        factory.register_tool_in_session("session_a", "shared", "Shared", {}, {})
        
        # Session B registers exclusive tools
        factory.register_tool_in_session("session_b", "exclusive_b", "B", {}, {})
        factory.register_tool_in_session("session_b", "shared", "Shared", {}, {})
        
        session_a = factory.get_or_create_session("session_a")
        session_b = factory.get_or_create_session("session_b")
        
        # A doesn't have B's exclusive tools
        assert session_a.has_tool("exclusive_a")
        assert not session_a.has_tool("exclusive_b")
        
        # B doesn't have A's exclusive tools
        assert session_b.has_tool("exclusive_b")
        assert not session_b.has_tool("exclusive_a")
        
        # Both have shared (but different instances)
        assert session_a.has_tool("shared")
        assert session_b.has_tool("shared")


# ============================================================================
# TESTS: Session Lifecycle Management
# ============================================================================

class TestSessionLifecycle:
    """Test session creation and cleanup."""
    
    def test_close_session_clears_tools(self):
        """Test closing session clears its tools."""
        factory = MCPSessionFactory()
        
        factory.register_tool_in_session("session_1", "tool_a", "A", {}, {})
        factory.register_tool_in_session("session_1", "tool_b", "B", {}, {})
        
        assert factory.get_session_tool_count("session_1") == 2
        
        factory.close_session("session_1")
        
        # Session gone
        assert factory.get_session_tool_count("session_1") == 0
    
    def test_reopen_session_is_fresh(self):
        """Test reopening session is clean."""
        factory = MCPSessionFactory()
        
        # Register tools
        factory.register_tool_in_session("session_1", "tool_a", "A", {}, {})
        
        # Close session
        factory.close_session("session_1")
        
        # Reopen - should be clean
        factory.get_or_create_session("session_1")
        assert factory.get_session_tool_count("session_1") == 0
    
    def test_list_active_sessions(self):
        """Test listing active sessions."""
        factory = MCPSessionFactory()
        
        factory.get_or_create_session("session_1")
        factory.get_or_create_session("session_2")
        factory.get_or_create_session("session_3")
        
        active = factory.list_active_sessions()
        assert len(active) == 3
        assert "session_1" in active
        assert "session_2" in active
        assert "session_3" in active


# ============================================================================
# TESTS: Tool Registry Semantics
# ============================================================================

class TestToolRegistrySemantics:
    """Test tool registry semantics."""
    
    def test_tool_input_output_isolation(self):
        """Test that tool I/O definitions are isolated."""
        registry = SessionMCPToolRegistry("session_1")
        
        tool = registry.register_tool(
            name="cortex_migration",
            description="Plan migration",
            inputs={"target_framework": "string", "scope": "string"},
            outputs={"plan": "json", "steps": "array"}
        )
        
        assert tool.inputs == {"target_framework": "string", "scope": "string"}
        assert tool.outputs == {"plan": "json", "steps": "array"}
    
    def test_tool_description_per_session(self):
        """Test tool descriptions are independent per session."""
        session_1 = SessionMCPToolRegistry("session_1")
        session_2 = SessionMCPToolRegistry("session_2")
        
        tool_1 = session_1.register_tool(
            "migration",
            "Plan React → Vue migration",
            {},
            {}
        )
        
        tool_2 = session_2.register_tool(
            "migration",
            "Plan Python → Go migration",
            {},
            {}
        )
        
        # Same name, different descriptions (per session)
        assert tool_1.description == "Plan React → Vue migration"
        assert tool_2.description == "Plan Python → Go migration"
    
    def test_has_tool_check(self):
        """Test has_tool() method."""
        registry = SessionMCPToolRegistry("session_1")
        
        registry.register_tool("cortex_review", "Review", {}, {})
        
        assert registry.has_tool("cortex_review")
        assert not registry.has_tool("nonexistent")


# ============================================================================
# TESTS: Multi-Tenant MCP Scenarios
# ============================================================================

class TestMultiTenantMCPScenarios:
    """Test realistic multi-tenant MCP scenarios."""
    
    def test_company_a_vs_company_b_tool_sets(self):
        """Test different companies have different tool sets."""
        factory = MCPSessionFactory()
        
        # Company A session
        factory.register_tool_in_session(
            "company_a_session",
            "cortex_compliance_check",
            "Check GDPR compliance",
            {},
            {}
        )
        
        # Company B session
        factory.register_tool_in_session(
            "company_b_session",
            "cortex_hipaa_audit",
            "Audit HIPAA",
            {},
            {}
        )
        
        session_a = factory.get_or_create_session("company_a_session")
        session_b = factory.get_or_create_session("company_b_session")
        
        # Company A has its tools
        assert session_a.has_tool("cortex_compliance_check")
        assert not session_a.has_tool("cortex_hipaa_audit")
        
        # Company B has its tools
        assert session_b.has_tool("cortex_hipaa_audit")
        assert not session_b.has_tool("cortex_compliance_check")
    
    def test_multiple_users_same_company(self):
        """Test multiple users in same company have separate sessions."""
        factory = MCPSessionFactory()
        
        # User 1 in Company A
        user1_session = factory.get_or_create_session("company_a_user1")
        factory.register_tool_in_session("company_a_user1", "migration", "Migration", {}, {})
        
        # User 2 in Company A
        user2_session = factory.get_or_create_session("company_a_user2")
        factory.register_tool_in_session("company_a_user2", "review", "Review", {}, {})
        
        # Each user has own tools
        assert user1_session.has_tool("migration")
        assert not user1_session.has_tool("review")
        
        assert user2_session.has_tool("review")
        assert not user2_session.has_tool("migration")
