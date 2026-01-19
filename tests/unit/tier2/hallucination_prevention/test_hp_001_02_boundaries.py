"""
Test suite for AC-HP-001-02: Behavioral Boundary Rules

Tests enforcement of behavioral boundaries to prevent:
- Locked phase modification
- AC deletion without approval
- Governance bypass attempts
- Unauthorized modifications

Target: 28/28 tests passing
"""

import sys
import pytest
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

# Add cortex_brain to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / 'cortex_brain'))

try:
    from tier2.hallucination_prevention.boundary_rules import (
        BoundaryRule,
        BoundaryViolation,
        BoundaryEnforcer,
        BoundaryRecovery,
        BoundaryAuditLogger,
    )
except ModuleNotFoundError:
    # Alternative import path for development
    import os
    cortex_brain_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../../cortex_brain'))
    sys.path.insert(0, cortex_brain_path)
    from tier2.hallucination_prevention.boundary_rules import (
        BoundaryRule,
        BoundaryViolation,
        BoundaryEnforcer,
        BoundaryRecovery,
        BoundaryAuditLogger,
    )


# =========================================================================
# FIXTURES
# =========================================================================

@pytest.fixture
def enforcer() -> BoundaryEnforcer:
    """Create BoundaryEnforcer instance."""
    return BoundaryEnforcer()


@pytest.fixture
def recovery() -> BoundaryRecovery:
    """Create BoundaryRecovery instance."""
    return BoundaryRecovery()


@pytest.fixture
def audit_logger() -> BoundaryAuditLogger:
    """Create BoundaryAuditLogger instance."""
    return BoundaryAuditLogger()


@pytest.fixture
def sample_phase_state() -> Dict[str, Any]:
    """Create sample phase state for testing."""
    return {
        'phase_id': 'PHASE-11',
        'status': 'IN_PROGRESS',
        'locked': True,
        'ac_ids': ['HP-001-01', 'HP-001-02'],
        'completed_ac_ids': ['HP-001-01'],
        'progress_percentage': 50.0,
        'created_at': '2026-01-17T00:00:00Z',
    }


@pytest.fixture
def sample_ac_state() -> Dict[str, Any]:
    """Create sample AC state for testing."""
    return {
        'ac_id': 'HP-001-02',
        'phase_id': 'PHASE-11',
        'status': 'NOT_STARTED',
        'files': ['file1.py', 'file2.py'],
        'test_count': 28,
        'created_at': '2026-01-17T00:00:00Z',
        'protected': True,
    }


# =========================================================================
# TEST: BoundaryRule Data Structure
# =========================================================================

class TestBoundaryRule:
    """Tests for BoundaryRule dataclass."""

    def test_boundary_rule_creation(self):
        """Test creating a BoundaryRule instance."""
        rule = BoundaryRule(
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            description='Prevent modification of locked phases',
            severity='CRITICAL',
            action='REJECT',
            recovery_action='LOG_AND_ALERT',
        )
        assert rule.rule_id == 'BR-001'
        assert rule.rule_type == 'PHASE_LOCK'
        assert rule.severity == 'CRITICAL'
        assert rule.action == 'REJECT'

    def test_boundary_rule_with_metadata(self):
        """Test BoundaryRule with optional metadata."""
        rule = BoundaryRule(
            rule_id='BR-002',
            rule_type='AC_DELETION',
            description='Prevent AC deletion without approval',
            severity='HIGH',
            action='REQUIRE_APPROVAL',
            recovery_action='QUARANTINE',
            metadata={'requires_roles': ['admin', 'lead'], 'approval_count': 2},
        )
        assert rule.metadata is not None
        assert rule.metadata['approval_count'] == 2


# =========================================================================
# TEST: BoundaryViolation Detection
# =========================================================================

class TestBoundaryViolation:
    """Tests for BoundaryViolation detection."""

    def test_violation_creation(self):
        """Test creating a BoundaryViolation instance."""
        violation = BoundaryViolation(
            violation_id='BV-001',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Attempted modification of locked phase PHASE-11',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
        )
        assert violation.rule_id == 'BR-001'
        assert violation.severity == 'CRITICAL'
        assert violation.actor == 'user@example.com'

    def test_violation_with_context(self):
        """Test BoundaryViolation with context data."""
        violation = BoundaryViolation(
            violation_id='BV-002',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Phase modification blocked',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
            context={'phase_id': 'PHASE-11', 'locked': True},
        )
        assert violation.context is not None
        assert violation.context['phase_id'] == 'PHASE-11'


# =========================================================================
# TEST: Locked Phase Enforcement
# =========================================================================

class TestLockedPhaseEnforcement:
    """Tests for preventing locked phase modification."""

    def test_prevent_modify_locked_phase(self, enforcer: BoundaryEnforcer, sample_phase_state: Dict):
        """Test that modifying locked phase is rejected."""
        violation = enforcer.check_phase_modification(
            phase_state=sample_phase_state,
            modification_type='STATUS_UPDATE',
            actor='user@example.com',
        )
        assert violation is not None
        assert violation.rule_type == 'PHASE_LOCK'
        assert violation.severity == 'CRITICAL'

    def test_prevent_delete_locked_phase(self, enforcer: BoundaryEnforcer, sample_phase_state: Dict):
        """Test that deleting locked phase is rejected."""
        violation = enforcer.check_phase_modification(
            phase_state=sample_phase_state,
            modification_type='DELETE_PHASE',
            actor='user@example.com',
        )
        assert violation is not None
        assert violation.attempted_action == 'DELETE_PHASE'

    def test_prevent_reset_locked_phase(self, enforcer: BoundaryEnforcer, sample_phase_state: Dict):
        """Test that resetting locked phase is rejected."""
        violation = enforcer.check_phase_modification(
            phase_state=sample_phase_state,
            modification_type='RESET_PROGRESS',
            actor='user@example.com',
        )
        assert violation is not None
        assert 'RESET' in violation.attempted_action

    def test_allow_modify_unlocked_phase(self, enforcer: BoundaryEnforcer, sample_phase_state: Dict):
        """Test that modifying unlocked phase is allowed."""
        sample_phase_state['locked'] = False
        violation = enforcer.check_phase_modification(
            phase_state=sample_phase_state,
            modification_type='STATUS_UPDATE',
            actor='user@example.com',
        )
        assert violation is None


# =========================================================================
# TEST: AC Deletion Prevention
# =========================================================================

class TestACDeletionPrevention:
    """Tests for preventing AC deletion without approval."""

    def test_prevent_ac_deletion_without_approval(self, enforcer: BoundaryEnforcer):
        """Test that AC deletion without approval is rejected."""
        violation = enforcer.check_ac_deletion(
            ac_id='HP-001-02',
            phase_id='PHASE-11',
            actor='user@example.com',
            approval_count=0,
        )
        assert violation is not None
        assert violation.rule_type == 'AC_DELETION'
        assert violation.severity == 'HIGH'

    def test_prevent_ac_deletion_insufficient_approval(self, enforcer: BoundaryEnforcer):
        """Test that AC deletion with insufficient approval is rejected."""
        violation = enforcer.check_ac_deletion(
            ac_id='HP-001-02',
            phase_id='PHASE-11',
            actor='user@example.com',
            approval_count=1,  # Requires 2
        )
        assert violation is not None
        assert 'insufficient' in violation.description.lower()

    def test_allow_ac_deletion_with_approval(self, enforcer: BoundaryEnforcer):
        """Test that AC deletion with proper approval is allowed."""
        violation = enforcer.check_ac_deletion(
            ac_id='HP-001-02',
            phase_id='PHASE-11',
            actor='user@example.com',
            approval_count=2,
        )
        assert violation is None

    def test_prevent_completed_ac_deletion(self, enforcer: BoundaryEnforcer):
        """Test that completed AC deletion is prevented."""
        violation = enforcer.check_ac_deletion(
            ac_id='HP-001-01',
            phase_id='PHASE-11',
            actor='user@example.com',
            ac_status='COMPLETED',
            approval_count=2,
        )
        assert violation is not None
        assert 'completed' in violation.description.lower()


# =========================================================================
# TEST: Governance Bypass Prevention
# =========================================================================

class TestGovernanceBypassPrevention:
    """Tests for preventing governance bypass attempts."""

    def test_detect_direct_file_modification(self, enforcer: BoundaryEnforcer):
        """Test detection of direct YAML file modification bypassing API."""
        violation = enforcer.check_governance_bypass(
            operation_type='DIRECT_FILE_WRITE',
            target='cortex-master.yaml',
            actor='user@example.com',
            bypass_method='DIRECT_EDIT',
        )
        assert violation is not None
        assert violation.rule_type == 'GOVERNANCE_BYPASS'

    def test_detect_database_direct_modification(self, enforcer: BoundaryEnforcer):
        """Test detection of direct database modification."""
        violation = enforcer.check_governance_bypass(
            operation_type='DIRECT_DB_WRITE',
            target='governance.db',
            actor='user@example.com',
            bypass_method='DIRECT_SQL',
        )
        assert violation is not None
        assert 'db' in violation.description.lower() or 'database' in violation.description.lower()

    def test_detect_audit_log_tampering(self, enforcer: BoundaryEnforcer):
        """Test detection of audit log tampering."""
        violation = enforcer.check_governance_bypass(
            operation_type='AUDIT_LOG_MODIFICATION',
            target='governance.db',
            actor='user@example.com',
            bypass_method='LOG_DELETION',
        )
        assert violation is not None
        assert violation.severity == 'CRITICAL'

    def test_allow_authorized_api_operation(self, enforcer: BoundaryEnforcer):
        """Test that authorized API operations are allowed."""
        violation = enforcer.check_governance_bypass(
            operation_type='API_CALL',
            target='cortex_brain/update_phase',
            actor='user@example.com',
            bypass_method=None,
        )
        assert violation is None


# =========================================================================
# TEST: Unauthorized Modification Detection
# =========================================================================

class TestUnauthorizedModification:
    """Tests for detecting unauthorized modifications."""

    def test_detect_unauthorized_actor_modification(self, enforcer: BoundaryEnforcer):
        """Test detection of modification by unauthorized actor."""
        violation = enforcer.check_unauthorized_modification(
            modification_type='AC_STATUS_UPDATE',
            ac_id='HP-001-02',
            actor='junior_user@example.com',
            required_role='LEAD',
        )
        assert violation is not None
        assert 'unauthorized' in violation.description.lower()

    def test_detect_out_of_sequence_modification(self, enforcer: BoundaryEnforcer):
        """Test detection of out-of-sequence phase modification."""
        violation = enforcer.check_unauthorized_modification(
            modification_type='PHASE_UPDATE',
            phase_id='PHASE-11',
            actor='user@example.com',
            current_sequence=11,
            target_sequence=12,
            phase_dependencies_met=False,
        )
        assert violation is not None
        assert 'sequence' in violation.description.lower()

    def test_allow_authorized_modification(self, enforcer: BoundaryEnforcer):
        """Test that authorized modification is allowed."""
        violation = enforcer.check_unauthorized_modification(
            modification_type='AC_STATUS_UPDATE',
            ac_id='HP-001-02',
            actor='lead_user@example.com',
            required_role='LEAD',
        )
        assert violation is None


# =========================================================================
# TEST: Boundary Violation Logging
# =========================================================================

class TestBoundaryViolationLogging:
    """Tests for logging and tracking boundary violations."""

    def test_log_violation(self, audit_logger: BoundaryAuditLogger):
        """Test logging a boundary violation."""
        violation = BoundaryViolation(
            violation_id='BV-001',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Attempted modification of locked phase',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
        )
        logged_id = audit_logger.log_violation(violation)
        assert logged_id is not None
        assert logged_id == violation.violation_id

    def test_retrieve_violation_history(self, audit_logger: BoundaryAuditLogger):
        """Test retrieving violation history."""
        violation = BoundaryViolation(
            violation_id='BV-002',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Attempted modification',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
        )
        audit_logger.log_violation(violation)
        
        history = audit_logger.get_violations_by_rule('BR-001')
        assert len(history) > 0
        assert history[0].rule_id == 'BR-001'

    def test_get_violations_by_actor(self, audit_logger: BoundaryAuditLogger):
        """Test retrieving violations by actor."""
        violation = BoundaryViolation(
            violation_id='BV-003',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Attempted modification',
            attempted_action='MODIFY_PHASE',
            actor='suspicious_user@example.com',
            timestamp=datetime.now(),
        )
        audit_logger.log_violation(violation)
        
        violations = audit_logger.get_violations_by_actor('suspicious_user@example.com')
        assert len(violations) > 0
        assert violations[0].actor == 'suspicious_user@example.com'


# =========================================================================
# TEST: Boundary Recovery Mechanisms
# =========================================================================

class TestBoundaryRecovery:
    """Tests for boundary recovery mechanisms."""

    def test_recover_from_phase_lock_violation(self, recovery: BoundaryRecovery):
        """Test recovery from phase lock violation."""
        violation = BoundaryViolation(
            violation_id='BV-004',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Phase modification attempted',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
            context={'phase_id': 'PHASE-11'},
        )
        
        recovery_plan = recovery.create_recovery_plan(violation)
        assert recovery_plan is not None
        assert recovery_plan.action in ['LOG_ALERT', 'ISOLATE', 'ROLLBACK']

    def test_recover_from_ac_deletion_violation(self, recovery: BoundaryRecovery):
        """Test recovery from AC deletion violation."""
        violation = BoundaryViolation(
            violation_id='BV-005',
            rule_id='BR-002',
            rule_type='AC_DELETION',
            severity='HIGH',
            description='AC deletion without approval',
            attempted_action='DELETE_AC',
            actor='user@example.com',
            timestamp=datetime.now(),
            context={'ac_id': 'HP-001-02'},
        )
        
        recovery_plan = recovery.create_recovery_plan(violation)
        assert recovery_plan is not None
        assert 'quarantine' in recovery_plan.action.lower() or 'isolation' in recovery_plan.action.lower()

    def test_execute_recovery_action(self, recovery: BoundaryRecovery):
        """Test executing a recovery action."""
        violation = BoundaryViolation(
            violation_id='BV-006',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Phase modification attempted',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
            context={'phase_id': 'PHASE-11'},
        )
        
        recovery_plan = recovery.create_recovery_plan(violation)
        result = recovery.execute_recovery(violation, recovery_plan)
        assert result is not None
        assert result['status'] in ['SUCCESS', 'IN_PROGRESS', 'QUEUED']


# =========================================================================
# TEST: Complex Scenarios
# =========================================================================

class TestComplexScenarios:
    """Tests for complex boundary violation scenarios."""

    def test_multiple_violations_in_sequence(self, enforcer: BoundaryEnforcer, audit_logger: BoundaryAuditLogger):
        """Test handling multiple violations in sequence."""
        violations = []
        
        # Attempt 1: Modify locked phase
        v1 = enforcer.check_phase_modification(
            phase_state={'phase_id': 'PHASE-11', 'locked': True, 'status': 'IN_PROGRESS'},
            modification_type='STATUS_UPDATE',
            actor='user@example.com',
        )
        violations.append(v1)
        
        # Attempt 2: Delete AC without approval
        v2 = enforcer.check_ac_deletion(
            ac_id='HP-001-02',
            phase_id='PHASE-11',
            actor='user@example.com',
            approval_count=0,
        )
        violations.append(v2)
        
        # Attempt 3: Direct file modification
        v3 = enforcer.check_governance_bypass(
            operation_type='DIRECT_FILE_WRITE',
            target='cortex-master.yaml',
            actor='user@example.com',
            bypass_method='DIRECT_EDIT',
        )
        violations.append(v3)
        
        # All three should be violations
        assert all(v is not None for v in violations)
        assert len(violations) == 3

    def test_violation_escalation_by_severity(self, audit_logger: BoundaryAuditLogger):
        """Test violation escalation based on severity."""
        critical_violation = BoundaryViolation(
            violation_id='BV-007',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Critical boundary violation',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
        )
        
        high_violation = BoundaryViolation(
            violation_id='BV-008',
            rule_id='BR-002',
            rule_type='AC_DELETION',
            severity='HIGH',
            description='High severity violation',
            attempted_action='DELETE_AC',
            actor='user@example.com',
            timestamp=datetime.now(),
        )
        
        audit_logger.log_violation(critical_violation)
        audit_logger.log_violation(high_violation)
        
        critical_count = len([v for v in audit_logger.get_all_violations() if v.severity == 'CRITICAL'])
        high_count = len([v for v in audit_logger.get_all_violations() if v.severity == 'HIGH'])
        
        assert critical_count >= 1
        assert high_count >= 1


# =========================================================================
# TEST: Edge Cases
# =========================================================================

class TestEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_handle_none_phase_state(self, enforcer: BoundaryEnforcer):
        """Test handling None phase state gracefully."""
        with pytest.raises((TypeError, AttributeError, ValueError)):
            enforcer.check_phase_modification(
                phase_state=None,
                modification_type='STATUS_UPDATE',
                actor='user@example.com',
            )

    def test_handle_empty_violation_context(self, enforcer: BoundaryEnforcer):
        """Test handling violation with empty context."""
        violation = BoundaryViolation(
            violation_id='BV-009',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Violation with no context',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
            context={},
        )
        assert violation.context is not None
        assert isinstance(violation.context, dict)

    def test_handle_invalid_rule_type(self, enforcer: BoundaryEnforcer):
        """Test handling invalid rule type."""
        rule = BoundaryRule(
            rule_id='BR-INVALID',
            rule_type='UNKNOWN_RULE_TYPE',
            description='Invalid rule',
            severity='MEDIUM',
            action='LOG',
            recovery_action='NONE',
        )
        assert rule.rule_type == 'UNKNOWN_RULE_TYPE'

    def test_handle_unicode_in_violation_description(self, audit_logger: BoundaryAuditLogger):
        """Test handling unicode characters in violation descriptions."""
        violation = BoundaryViolation(
            violation_id='BV-010',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description='Unauthorized modification attempt: 日本語 français 中文',
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
        )
        logged_id = audit_logger.log_violation(violation)
        assert logged_id == violation.violation_id

    def test_handle_very_long_violation_description(self, audit_logger: BoundaryAuditLogger):
        """Test handling very long violation descriptions."""
        long_desc = 'A' * 5000
        violation = BoundaryViolation(
            violation_id='BV-011',
            rule_id='BR-001',
            rule_type='PHASE_LOCK',
            severity='CRITICAL',
            description=long_desc,
            attempted_action='MODIFY_PHASE',
            actor='user@example.com',
            timestamp=datetime.now(),
        )
        logged_id = audit_logger.log_violation(violation)
        assert logged_id == violation.violation_id


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
