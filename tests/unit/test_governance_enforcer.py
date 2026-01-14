"""
Governance Enforcer Tests - TDD for Runtime Enforcement

Tests for:
- Phase lock checking
- AC-ID validation
- Intent canonicalization
- Hallucination prevention

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest

from src.core.governance_enforcer import (
    GovernanceEnforcer,
    EnforcementResult,
    IntentType,
)
from src.infrastructure.database import DatabaseManager, DatabaseConfig


@pytest.fixture
def enforcer(temp_dir):
    """Create a governance enforcer with test database."""
    db_path = temp_dir / "governance.db"
    config = DatabaseConfig(db_path=db_path)
    db = DatabaseManager(config)
    db.initialize()
    
    enforcer = GovernanceEnforcer(db)
    yield enforcer
    
    db.close()


@pytest.fixture
def populated_enforcer(enforcer):
    """Enforcer with pre-populated AC-IDs and phases."""
    db = enforcer._db
    
    # Add AC-IDs for PHASE-01
    for i in range(1, 4):
        db.insert_ac(f"AC-AR-001-0{i}", "PHASE-01", f"Test AC {i}")
    
    # Add AC-IDs for PHASE-02
    for i in range(1, 4):
        db.insert_ac(f"AC-AR-006-0{i}", "PHASE-02", f"Test AC {i}")
    
    return enforcer


class TestPhaseLockEnforcement:
    """Test phase lock enforcement."""
    
    def test_allows_operation_on_unlocked_phase(self, populated_enforcer):
        """Operations on unlocked phases should be allowed."""
        result = populated_enforcer.check_phase_lock("PHASE-01")
        
        assert result.allowed is True
        assert result.reason is None
    
    def test_blocks_operation_on_locked_phase(self, populated_enforcer):
        """Operations on locked phases should be blocked."""
        # Lock PHASE-01
        populated_enforcer._db.lock_phase("PHASE-01", "test")
        
        result = populated_enforcer.check_phase_lock("PHASE-01")
        
        assert result.allowed is False
        assert "locked" in result.reason.lower()
    
    def test_returns_lock_info_when_blocked(self, populated_enforcer):
        """Should return lock details when phase is blocked."""
        populated_enforcer._db.lock_phase(
            "PHASE-01", 
            locked_by="builder-agent",
            git_checkpoint="abc123"
        )
        
        result = populated_enforcer.check_phase_lock("PHASE-01")
        
        assert result.allowed is False
        assert result.metadata is not None
        assert result.metadata.get("locked_by") == "builder-agent"
        assert result.metadata.get("git_checkpoint") == "abc123"


class TestACIDValidation:
    """Test AC-ID existence validation (AC-VALIDATE-002)."""
    
    def test_validates_existing_ac_id(self, populated_enforcer):
        """Existing AC-ID should validate successfully."""
        result = populated_enforcer.validate_ac_id("AC-AR-001-01")
        
        assert result.allowed is True
    
    def test_rejects_nonexistent_ac_id(self, populated_enforcer):
        """Non-existent AC-ID should be rejected."""
        result = populated_enforcer.validate_ac_id("AC-FAKE-999-99")
        
        assert result.allowed is False
        assert "not found" in result.reason.lower()
    
    def test_rejects_malformed_ac_id(self, enforcer):
        """Malformed AC-ID should be rejected."""
        result = enforcer.validate_ac_id("invalid-format")
        
        assert result.allowed is False
        assert "invalid format" in result.reason.lower()
    
    def test_validates_ac_id_format(self, enforcer):
        """AC-ID format should match pattern AC-XXX-NNN-NN."""
        # Valid formats
        assert enforcer.is_valid_ac_format("AC-AR-001-01") is True
        assert enforcer.is_valid_ac_format("AC-FR-002-03") is True
        assert enforcer.is_valid_ac_format("AC-NFR-001-01") is True
        assert enforcer.is_valid_ac_format("AC-VALIDATE-001") is True
        assert enforcer.is_valid_ac_format("AC-BRITTLE-014") is True
        
        # Invalid formats
        assert enforcer.is_valid_ac_format("invalid") is False
        assert enforcer.is_valid_ac_format("AC-") is False
        assert enforcer.is_valid_ac_format("AC-001") is False


class TestIntentCanonicalization:
    """Test intent canonicalization (AC-VALIDATE-001)."""
    
    def test_canonicalizes_implement_intent(self, enforcer):
        """Should canonicalize implementation intent."""
        intents = [
            "implement AC-AR-001-01",
            "create AC-AR-001-01",
            "build AC-AR-001-01",
            "develop AC-AR-001-01",
            "code AC-AR-001-01",
        ]
        
        for intent in intents:
            result = enforcer.canonicalize_intent(intent)
            assert result.intent_type == IntentType.IMPLEMENT
            assert result.ac_id == "AC-AR-001-01"
    
    def test_canonicalizes_review_intent(self, enforcer):
        """Should canonicalize review intent."""
        intents = [
            "review AC-AR-001-01",
            "check AC-AR-001-01",
            "verify AC-AR-001-01",
            "validate AC-AR-001-01",
        ]
        
        for intent in intents:
            result = enforcer.canonicalize_intent(intent)
            assert result.intent_type == IntentType.REVIEW
    
    def test_canonicalizes_query_intent(self, enforcer):
        """Should canonicalize query intent."""
        intents = [
            "status of AC-AR-001-01",
            "show AC-AR-001-01",
            "get AC-AR-001-01",
            "what is AC-AR-001-01",
        ]
        
        for intent in intents:
            result = enforcer.canonicalize_intent(intent)
            assert result.intent_type == IntentType.QUERY
    
    def test_extracts_ac_id_from_intent(self, enforcer):
        """Should extract AC-ID from various intent formats."""
        test_cases = [
            ("implement AC-AR-001-01 now", "AC-AR-001-01"),
            ("please review AC-FR-002-03", "AC-FR-002-03"),
            ("what is the status of AC-VALIDATE-001?", "AC-VALIDATE-001"),
        ]
        
        for intent, expected_ac_id in test_cases:
            result = enforcer.canonicalize_intent(intent)
            assert result.ac_id == expected_ac_id
    
    def test_returns_unknown_for_ambiguous_intent(self, enforcer):
        """Should return UNKNOWN for ambiguous intents."""
        result = enforcer.canonicalize_intent("do something")
        assert result.intent_type == IntentType.UNKNOWN


class TestPhaseGating:
    """Test phase dependency gating."""
    
    def test_allows_phase_with_locked_predecessor(self, populated_enforcer):
        """Should allow phase if predecessor is locked."""
        # Lock PHASE-01
        populated_enforcer._db.lock_phase("PHASE-01", "test")
        
        result = populated_enforcer.can_start_phase("PHASE-02")
        
        assert result.allowed is True
    
    def test_blocks_phase_with_unlocked_predecessor(self, populated_enforcer):
        """Should block phase if predecessor is not locked."""
        # PHASE-01 is unlocked
        result = populated_enforcer.can_start_phase("PHASE-02")
        
        assert result.allowed is False
        assert "PHASE-01" in result.reason
    
    def test_allows_phase_01_without_predecessor(self, populated_enforcer):
        """PHASE-01 should always be allowed (no predecessor)."""
        result = populated_enforcer.can_start_phase("PHASE-01")
        
        assert result.allowed is True
    
    def test_allows_parallel_phase(self, populated_enforcer):
        """PHASE-PARALLEL should be allowed if PHASE-01 is locked."""
        populated_enforcer._db.lock_phase("PHASE-01", "test")
        
        result = populated_enforcer.can_start_phase("PHASE-PARALLEL")
        
        assert result.allowed is True


class TestOperationEnforcement:
    """Test full operation enforcement."""
    
    def test_enforce_blocks_on_locked_phase(self, populated_enforcer):
        """Should block operation if target phase is locked."""
        populated_enforcer._db.lock_phase("PHASE-01", "test")
        
        result = populated_enforcer.enforce_operation(
            operation="implement",
            ac_id="AC-AR-001-01",
            phase="PHASE-01"
        )
        
        assert result.allowed is False
        assert "locked" in result.reason.lower()
    
    def test_enforce_blocks_on_invalid_ac_id(self, populated_enforcer):
        """Should block operation if AC-ID doesn't exist."""
        result = populated_enforcer.enforce_operation(
            operation="implement",
            ac_id="AC-FAKE-999-99",
            phase="PHASE-01"
        )
        
        assert result.allowed is False
        assert "not found" in result.reason.lower()
    
    def test_enforce_allows_valid_operation(self, populated_enforcer):
        """Should allow valid operation on unlocked phase."""
        result = populated_enforcer.enforce_operation(
            operation="implement",
            ac_id="AC-AR-001-01",
            phase="PHASE-01"
        )
        
        assert result.allowed is True
    
    def test_enforce_logs_to_audit(self, populated_enforcer):
        """Should log enforcement decision to audit trail."""
        populated_enforcer.enforce_operation(
            operation="implement",
            ac_id="AC-AR-001-01",
            phase="PHASE-01"
        )
        
        # Check audit log
        entries = populated_enforcer._db.query_audit_by_ac_id("AC-AR-001-01")
        assert entries.is_ok()
        assert len(entries.unwrap()) > 0


class TestEnforcementResult:
    """Test EnforcementResult dataclass."""
    
    def test_allowed_result(self):
        """Should create allowed result."""
        result = EnforcementResult(allowed=True)
        assert result.allowed is True
        assert result.reason is None
    
    def test_blocked_result_with_reason(self):
        """Should create blocked result with reason."""
        result = EnforcementResult(
            allowed=False,
            reason="Phase is locked"
        )
        assert result.allowed is False
        assert result.reason == "Phase is locked"
    
    def test_result_with_metadata(self):
        """Should include metadata."""
        result = EnforcementResult(
            allowed=False,
            reason="Phase locked",
            metadata={"locked_by": "test", "locked_at": "2026-01-14"}
        )
        assert result.metadata["locked_by"] == "test"
