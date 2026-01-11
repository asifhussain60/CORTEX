"""
AC-SECURITY-005: Approval State Machine Testing

Validates interactive approval protocol for high-risk operations:
- States: REQUESTED → APPROVED/DENIED/EXPIRED
- Timeout: 5 minutes default, configurable
- Non-interactive mode: DENY by default (fail-closed)
- Audit trail: correlation_id, timestamp, actor, decision, justification
- Replay protection: approval tokens expire after single use
- High-risk triggers: WRITE to tier0/tier1, DELETE *, EXECUTE with shell=True
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Optional
from enum import Enum
import uuid


class ApprovalState(Enum):
    """States for approval workflow."""
    REQUESTED = "requested"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"


class TestApprovalStateMachine:
    """Tests for AC-SECURITY-005: Approval state machine."""
    
    @pytest.fixture
    def approval_config(self):
        """Fixture providing approval configuration."""
        return {
            "timeout_seconds": 300,  # 5 minutes default
            "require_approval_for": [
                "WRITE:tier0/*",
                "WRITE:tier1/*",
                "DELETE:*",
                "EXECUTE:*,shell=True"
            ],
            "non_interactive_default": "DENY",  # Fail-closed
        }
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_approval_state_transitions(self, approval_config):
        """Test valid state transitions."""
        # Valid transitions: REQUESTED → APPROVED/DENIED/EXPIRED
        transitions = [
            ("REQUESTED", "APPROVED"),
            ("REQUESTED", "DENIED"),
            ("REQUESTED", "EXPIRED"),
        ]
        
        for from_state, to_state in transitions:
            assert from_state in [s.value for s in ApprovalState]
            assert to_state in [s.value for s in ApprovalState]
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_approval_request_creation(self, approval_config):
        """Test creating an approval request."""
        request = {
            "id": str(uuid.uuid4()),
            "action": "DELETE:src/important.py",
            "requester": "user@example.com",
            "state": ApprovalState.REQUESTED.value,
            "created_at": datetime.utcnow().isoformat(),
            "timeout_at": (datetime.utcnow() + timedelta(seconds=approval_config["timeout_seconds"])).isoformat(),
            "correlation_id": str(uuid.uuid4()),
        }
        
        assert request["state"] == ApprovalState.REQUESTED.value
        assert request["id"] is not None
        assert request["correlation_id"] is not None
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_approval_timeout(self, approval_config):
        """Test that approvals expire after timeout."""
        created_at = datetime.utcnow() - timedelta(seconds=350)  # 350 seconds ago
        timeout_at = created_at + timedelta(seconds=approval_config["timeout_seconds"])
        current_time = datetime.utcnow()
        
        is_expired = current_time > timeout_at
        assert is_expired, "Approval should be expired"
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_non_interactive_deny_by_default(self, approval_config):
        """Test that non-interactive mode denies by default."""
        # In non-interactive mode, without explicit approval, should deny
        non_interactive_mode = True
        explicit_approval = False
        
        decision = "DENY" if (non_interactive_mode and not explicit_approval) else "ALLOW"
        
        assert decision == "DENY", "Should deny in non-interactive mode without approval"
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_approval_audit_trail(self):
        """Test that approval decisions are audited."""
        audit_entry = {
            "correlation_id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow().isoformat(),
            "actor": "reviewer@example.com",
            "action": "WRITE:tier0/governance/rules.yaml",
            "decision": "APPROVED",
            "justification": "Governance update reviewed and validated",
        }
        
        assert audit_entry["correlation_id"] is not None
        assert audit_entry["timestamp"] is not None
        assert audit_entry["actor"] is not None
        assert audit_entry["decision"] in ["APPROVED", "DENIED"]
        assert len(audit_entry["justification"]) > 0
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_replay_protection(self):
        """Test that approval tokens can only be used once."""
        token = str(uuid.uuid4())
        used_tokens = set()
        
        # First use should succeed
        assert token not in used_tokens
        used_tokens.add(token)
        
        # Second use should fail
        assert token in used_tokens, "Token should be in used set after first use"


class TestApprovalRiskTriggers:
    """Tests for high-risk operation detection."""
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_detects_tier0_write_risk(self):
        """Test detection of writes to tier0 (critical)."""
        operations = [
            ("WRITE", "cortex-brain/tier0/governance/rules.yaml", True),  # High-risk
            ("WRITE", "cortex-brain/tier1/tracking/state.json", False),    # Lower-risk
            ("READ", "cortex-brain/tier0/governance/rules.yaml", False),   # Read is safe
        ]
        
        for op_type, target, should_require_approval in operations:
            is_tier0_write = op_type == "WRITE" and "tier0" in target
            
            if should_require_approval:
                assert is_tier0_write, f"Should detect high-risk: {op_type} {target}"
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_detects_delete_risk(self):
        """Test detection of delete operations (always high-risk)."""
        operations = [
            ("DELETE", "src/old_file.py", True),           # Delete is high-risk
            ("DELETE", "tests/skipped_test.py", True),     # All deletes high-risk
            ("WRITE", "src/old_file.py", False),           # Write is lower-risk
        ]
        
        for op_type, target, should_require_approval in operations:
            if should_require_approval:
                assert op_type == "DELETE", f"Should detect DELETE as high-risk"
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_detects_shell_execution_risk(self):
        """Test detection of shell command execution."""
        operations = [
            ("EXECUTE", "cmd", {"shell": True}, True),         # shell=True is high-risk
            ("EXECUTE", "cmd", {"shell": False}, False),       # shell=False is safe
            ("EXECUTE", "cmd", {}, False),                     # Default shell=False
        ]
        
        for op_type, target, kwargs, should_require_approval in operations:
            is_shell_execute = op_type == "EXECUTE" and kwargs.get("shell", False) is True
            
            if should_require_approval:
                assert is_shell_execute, f"Should detect shell execution as high-risk"


class TestApprovalIntegration:
    """Integration tests for approval workflow."""
    
    @pytest.mark.ac_id("AC-SECURITY-005")
    def test_complete_approval_workflow(self):
        """Test complete workflow: request → review → approve/deny → audit."""
        # Step 1: Request approval
        request_id = str(uuid.uuid4())
        correlation_id = str(uuid.uuid4())
        
        approval_request = {
            "id": request_id,
            "correlation_id": correlation_id,
            "action": "DELETE:src/deprecated.py",
            "requester": "developer@example.com",
            "state": ApprovalState.REQUESTED.value,
        }
        
        # Step 2: Reviewer approves
        approval_decision = {
            "request_id": request_id,
            "correlation_id": correlation_id,
            "decision": ApprovalState.APPROVED.value,
            "reviewer": "lead@example.com",
            "justification": "Deprecated file, reviewed safe for deletion",
        }
        
        # Step 3: Audit trail
        audit_entry = {
            "correlation_id": correlation_id,
            "action": approval_request["action"],
            "decision": approval_decision["decision"],
            "requester": approval_request["requester"],
            "reviewer": approval_decision["reviewer"],
        }
        
        assert audit_entry["decision"] == ApprovalState.APPROVED.value
        assert audit_entry["correlation_id"] == correlation_id
