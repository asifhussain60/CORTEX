"""
MCP Governance Tools Tests - TDD for MCP-Exposed Tools

Tests for MCP-decorated governance tools that wrap core enforcement logic.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest

from src.infrastructure.database import DatabaseManager, DatabaseConfig
from src.core.governance_enforcer import GovernanceEnforcer
from src.mcp.tools.governance_tools import (
    check_phase_lock,
    validate_ac_id,
    canonicalize_intent,
    enforce_operation,
    get_phase_status,
    get_tool_registry,
)


@pytest.fixture
def initialized_db(temp_dir):
    """Create an initialized database for tests."""
    db_path = temp_dir / "governance.db"
    config = DatabaseConfig(db_path=db_path)
    db = DatabaseManager(config)
    db.initialize()
    
    # Populate with test data
    for i in range(1, 4):
        db.insert_ac(f"AC-AR-001-0{i}", "PHASE-01", f"Test AC {i}")
    for i in range(1, 4):
        db.insert_ac(f"AC-AR-006-0{i}", "PHASE-02", f"Test AC {i}")
    
    yield db
    db.close()


@pytest.fixture
def mock_enforcer(initialized_db, monkeypatch):
    """Provide a mock enforcer for MCP tools."""
    enforcer = GovernanceEnforcer(initialized_db)
    
    # Patch the global enforcer in the tools module
    from src.mcp.tools import governance_tools
    monkeypatch.setattr(governance_tools, "_enforcer", enforcer)
    monkeypatch.setattr(governance_tools, "_db", initialized_db)
    
    return enforcer


class TestCheckPhaseLockTool:
    """Test check_phase_lock MCP tool."""
    
    def test_returns_unlocked_status(self, mock_enforcer):
        """Should return unlocked status for unlocked phase."""
        result = check_phase_lock("PHASE-01")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["phase_id"] == "PHASE-01"
        assert data["locked"] is False
    
    def test_returns_locked_status(self, mock_enforcer):
        """Should return locked status with details."""
        mock_enforcer._db.lock_phase("PHASE-01", "test-agent", "abc123")
        
        result = check_phase_lock("PHASE-01")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["locked"] is True
        assert data["locked_by"] == "test-agent"
    
    def test_returns_error_for_invalid_phase(self, mock_enforcer):
        """Should handle invalid phase gracefully."""
        result = check_phase_lock("")
        
        assert result.is_err()


class TestValidateACIDTool:
    """Test validate_ac_id MCP tool."""
    
    def test_validates_existing_ac(self, mock_enforcer):
        """Should validate existing AC-ID."""
        result = validate_ac_id("AC-AR-001-01")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["valid"] is True
        assert data["ac_id"] == "AC-AR-001-01"
    
    def test_rejects_missing_ac(self, mock_enforcer):
        """Should reject non-existent AC-ID."""
        result = validate_ac_id("AC-FAKE-999-99")
        
        assert result.is_ok()  # Tool returns ok with valid=False
        data = result.unwrap()
        assert data["valid"] is False
        assert "not found" in data["reason"].lower()
    
    def test_rejects_malformed_ac(self, mock_enforcer):
        """Should reject malformed AC-ID."""
        result = validate_ac_id("not-an-ac-id")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["valid"] is False
        assert "invalid format" in data["reason"].lower()


class TestCanonicalizeIntentTool:
    """Test canonicalize_intent MCP tool."""
    
    def test_canonicalizes_implement(self, mock_enforcer):
        """Should canonicalize implement intent."""
        result = canonicalize_intent("implement AC-AR-001-01")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["intent_type"] == "IMPLEMENT"
        assert data["ac_id"] == "AC-AR-001-01"
    
    def test_canonicalizes_review(self, mock_enforcer):
        """Should canonicalize review intent."""
        result = canonicalize_intent("review AC-AR-001-01")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["intent_type"] == "REVIEW"
    
    def test_returns_unknown_for_ambiguous(self, mock_enforcer):
        """Should return UNKNOWN for ambiguous intent."""
        result = canonicalize_intent("do something")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["intent_type"] == "UNKNOWN"


class TestEnforceOperationTool:
    """Test enforce_operation MCP tool."""
    
    def test_allows_valid_operation(self, mock_enforcer):
        """Should allow valid operation."""
        result = enforce_operation(
            operation="implement",
            ac_id="AC-AR-001-01",
            phase="PHASE-01"
        )
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["allowed"] is True
    
    def test_blocks_on_locked_phase(self, mock_enforcer):
        """Should block operation on locked phase."""
        mock_enforcer._db.lock_phase("PHASE-01", "test")
        
        result = enforce_operation(
            operation="implement",
            ac_id="AC-AR-001-01",
            phase="PHASE-01"
        )
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["allowed"] is False
        assert "locked" in data["reason"].lower()
    
    def test_blocks_invalid_ac_id(self, mock_enforcer):
        """Should block operation with invalid AC-ID."""
        result = enforce_operation(
            operation="implement",
            ac_id="AC-FAKE-999-99",
            phase="PHASE-01"
        )
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["allowed"] is False


class TestGetPhaseStatusTool:
    """Test get_phase_status MCP tool."""
    
    def test_returns_phase_status(self, mock_enforcer):
        """Should return comprehensive phase status."""
        result = get_phase_status("PHASE-01")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["phase_id"] == "PHASE-01"
        assert "locked" in data
        assert "ac_count" in data
    
    def test_includes_ac_breakdown(self, mock_enforcer):
        """Should include AC status breakdown."""
        result = get_phase_status("PHASE-01")
        
        assert result.is_ok()
        data = result.unwrap()
        assert data["ac_count"] == 3  # We inserted 3 ACs


class TestToolRegistry:
    """Test MCP tool registration."""
    
    def test_all_tools_registered(self):
        """All governance tools should be registered."""
        registry = get_tool_registry()
        
        expected_tools = [
            "check_phase_lock",
            "validate_ac_id",
            "canonicalize_intent",
            "enforce_operation",
            "get_phase_status",
        ]
        
        for tool_name in expected_tools:
            assert tool_name in registry, f"Tool {tool_name} not registered"
    
    def test_tools_have_descriptions(self):
        """All tools should have descriptions for MCP."""
        registry = get_tool_registry()
        
        for name, info in registry.items():
            assert "description" in info, f"Tool {name} missing description"
            assert len(info["description"]) > 10, f"Tool {name} description too short"
