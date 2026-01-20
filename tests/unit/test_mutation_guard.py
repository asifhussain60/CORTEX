"""
Test suite for MutationGuard: Locked phase immutability enforcement.

Tests cover:
- Phase lock enforcement
- Tier 0 rule immutability
- AC-ID audit requirement validation
- Holistic dependency validation
- Mutation logging and history
- Development vs. strict mode policies
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from cortex.core.mutation_guard import (
    MutationType,
    MutationResult,
    MutationAttempt,
    ImmutabilityPolicy,
    PhaseImmutabilityValidator,
    RuleImmutabilityValidator,
    ACCompletenessValidator,
    MutationGuard,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def phase_tracker_yaml():
    """Create a test phase_tracker YAML."""
    return {
        "PHASE-01": {
            "title": "Foundation",
            "status": "COMPLETED",
            "locked": True,
            "ac_ids": 36,
            "completed_ac_ids": 36
        },
        "PHASE-02": {
            "title": "Orchestration Core",
            "status": "COMPLETED",
            "locked": True,
            "ac_ids": 27,
            "completed_ac_ids": 27,
            "requires": "PHASE-01"
        },
        "PHASE-VISION-CORE": {
            "title": "Brain Activation",
            "status": "IN_PROGRESS",
            "locked": False,
            "ac_ids": 24,
            "completed_ac_ids": 6,
            "requires": "PHASE-02"
        }
    }


@pytest.fixture
def phase_tracker_file(phase_tracker_yaml):
    """Create temporary phase_tracker YAML file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump({"phase_tracker": phase_tracker_yaml}, f)
        f.flush()
        yield f.name
    Path(f.name).unlink()


@pytest.fixture
def tier0_rules_dir():
    """Create temporary tier 0 rules directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create sample rule file
        rules = {
            "metadata": {
                "tier": 0,
                "immutable": True
            },
            "rules": {
                "SKULL-001": {
                    "name": "Governance Core",
                    "description": "Core governance rule"
                },
                "SKULL-002": {
                    "name": "Phase Lock",
                    "description": "Phase lock immutability"
                }
            }
        }
        
        with open(Path(tmpdir) / "core-rules.yaml", 'w') as f:
            yaml.dump(rules, f)
        
        yield tmpdir


@pytest.fixture
def governance_db():
    """Create temporary governance database."""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        db_path = f.name
    
    # Create schema
    import sqlite3
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE audit_log (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            ac_id TEXT,
            operation TEXT,
            actor TEXT,
            details TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    yield db_path
    
    Path(db_path).unlink()


# =============================================================================
# TEST: MutationAttempt
# =============================================================================

class TestMutationAttempt:
    """Test MutationAttempt dataclass."""
    
    def test_create_mutation_attempt(self):
        """Test creating a mutation attempt record."""
        attempt = MutationAttempt(
            timestamp="2026-01-15T10:00:00Z",
            mutation_type=MutationType.PHASE_MODIFICATION.value,
            target="PHASE-01",
            result=MutationResult.BLOCKED_PHASE_LOCKED.value,
            reason="Phase is locked"
        )
        
        assert attempt.timestamp == "2026-01-15T10:00:00Z"
        assert attempt.mutation_type == "phase_modification"
        assert attempt.result == "blocked_phase_locked"
    
    def test_mutation_to_dict(self):
        """Test converting mutation to dictionary."""
        attempt = MutationAttempt(
            timestamp="2026-01-15T10:00:00Z",
            mutation_type=MutationType.PHASE_MODIFICATION.value,
            target="PHASE-01",
            result=MutationResult.ALLOWED.value,
            reason="Phase is unlocked",
            details={"key": "value"}
        )
        
        d = attempt.to_dict()
        assert d["target"] == "PHASE-01"
        assert d["details"]["key"] == "value"


# =============================================================================
# TEST: ImmutabilityPolicy
# =============================================================================

class TestImmutabilityPolicy:
    """Test ImmutabilityPolicy configurations."""
    
    def test_strict_enforcement_policy(self):
        """Test strict enforcement policy."""
        policy = ImmutabilityPolicy.strict_enforcement()
        
        assert policy.locked_phase_modification_allowed is False
        assert policy.tier0_rule_modification_allowed is False
        assert policy.ac_completion_requires_audit_entries == 3
        assert policy.require_holistic_validation is True
    
    def test_development_mode_policy(self):
        """Test development mode policy."""
        policy = ImmutabilityPolicy.development_mode()
        
        assert policy.locked_phase_modification_allowed is True
        assert policy.tier0_rule_modification_allowed is False
        assert policy.ac_completion_requires_audit_entries == 1
        assert policy.require_holistic_validation is False


# =============================================================================
# TEST: PhaseImmutabilityValidator
# =============================================================================

class TestPhaseImmutabilityValidator:
    """Test phase lock validation."""
    
    def test_locked_phase_detected(self, phase_tracker_yaml):
        """Test detecting locked phases."""
        validator = PhaseImmutabilityValidator(phase_tracker_yaml)
        is_locked, reason = validator.validate_phase_locked("PHASE-01")
        
        assert is_locked is True
        assert "LOCKED" in reason
    
    def test_unlocked_phase_detected(self, phase_tracker_yaml):
        """Test detecting unlocked phases."""
        validator = PhaseImmutabilityValidator(phase_tracker_yaml)
        is_locked, reason = validator.validate_phase_locked("PHASE-VISION-CORE")
        
        assert is_locked is False
        assert "unlocked" in reason
    
    def test_nonexistent_phase(self, phase_tracker_yaml):
        """Test handling nonexistent phase."""
        validator = PhaseImmutabilityValidator(phase_tracker_yaml)
        is_locked, reason = validator.validate_phase_locked("PHASE-INVALID")
        
        assert is_locked is False
        assert "not found" in reason
    
    def test_modification_blocked_on_locked_phase(self, phase_tracker_yaml):
        """Test modification blocked on locked phase."""
        validator = PhaseImmutabilityValidator(phase_tracker_yaml)
        policy = ImmutabilityPolicy.strict_enforcement()
        
        allowed, reason = validator.validate_modification_allowed("PHASE-01", policy)
        
        assert allowed is False
        assert "blocked" in reason.lower()
    
    def test_modification_allowed_on_unlocked_phase(self, phase_tracker_yaml):
        """Test modification allowed on unlocked phase."""
        validator = PhaseImmutabilityValidator(phase_tracker_yaml)
        policy = ImmutabilityPolicy.strict_enforcement()
        
        allowed, reason = validator.validate_modification_allowed("PHASE-VISION-CORE", policy)
        
        assert allowed is True
    
    def test_development_mode_allows_locked_modification(self, phase_tracker_yaml):
        """Test development mode allows locked phase modification."""
        validator = PhaseImmutabilityValidator(phase_tracker_yaml)
        policy = ImmutabilityPolicy.development_mode()
        
        allowed, reason = validator.validate_modification_allowed("PHASE-01", policy)
        
        assert allowed is True
    
    def test_get_phase_status(self, phase_tracker_yaml):
        """Test getting phase status."""
        validator = PhaseImmutabilityValidator(phase_tracker_yaml)
        status = validator.get_phase_status("PHASE-01")
        
        assert status["id"] == "PHASE-01"
        assert status["locked"] is True
        assert status["ac_ids"] == 36


# =============================================================================
# TEST: RuleImmutabilityValidator
# =============================================================================

class TestRuleImmutabilityValidator:
    """Test Tier 0 rule immutability."""
    
    def test_tier0_rule_immutable(self, tier0_rules_dir):
        """Test that Tier 0 rules are immutable."""
        validator = RuleImmutabilityValidator(tier0_rules_dir)
        is_immutable, reason = validator.validate_rule_immutable("SKULL-001")
        
        assert is_immutable is True
        assert "IMMUTABLE" in reason
    
    def test_rule_integrity_verification(self, tier0_rules_dir):
        """Test rule integrity verification."""
        validator = RuleImmutabilityValidator(tier0_rules_dir)
        valid, reason = validator.validate_rule_integrity("core-rules")
        
        assert valid is True
        assert "verified" in reason
    
    def test_modified_rule_detected(self, tier0_rules_dir):
        """Test detection of modified Tier 0 rules."""
        validator = RuleImmutabilityValidator(tier0_rules_dir)
        
        # Modify the rule file
        rules_path = Path(tier0_rules_dir) / "core-rules.yaml"
        with open(rules_path, 'r') as f:
            data = yaml.safe_load(f)
        
        data["rules"]["SKULL-001"]["name"] = "MODIFIED"
        
        with open(rules_path, 'w') as f:
            yaml.dump(data, f)
        
        # Verify detects modification
        valid, reason = validator.validate_rule_integrity("core-rules")
        
        assert valid is False
        assert "modified" in reason.lower()


# =============================================================================
# TEST: ACCompletenessValidator
# =============================================================================

@pytest.mark.ac("AR-014-01")
class TestACCompletenessValidator:
    """Test AC-ID audit requirement validation."""
    
    def test_ac_without_audit_entries(self, governance_db):
        """Test AC without audit entries."""
        validator = ACCompletenessValidator(governance_db)
        has_entries, count, reason = validator.validate_ac_audit_entries("AC-AR-014-01")
        
        assert has_entries is False
        assert count == 0
        assert "0" in reason
    
    def test_ac_with_sufficient_audit_entries(self, governance_db):
        """Test AC with sufficient audit entries."""
        import sqlite3
        
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Add audit entries
        cursor.execute(
            "INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) VALUES (?, ?, ?, ?, ?)",
            ("2026-01-15T10:00:00Z", "AC-AR-014-01", "AC_START", "system", "{}")
        )
        cursor.execute(
            "INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) VALUES (?, ?, ?, ?, ?)",
            ("2026-01-15T10:01:00Z", "AC-AR-014-01", "AC_EXECUTE", "system", "{}")
        )
        cursor.execute(
            "INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) VALUES (?, ?, ?, ?, ?)",
            ("2026-01-15T10:02:00Z", "AC-AR-014-01", "AC_COMPLETE", "system", "{}")
        )
        
        conn.commit()
        conn.close()
        
        validator = ACCompletenessValidator(governance_db)
        has_entries, count, reason = validator.validate_ac_audit_entries("AC-AR-014-01")
        
        assert has_entries is True
        assert count == 3
    
    def test_ac_completeness_check(self, governance_db):
        """Test comprehensive AC completeness check."""
        import sqlite3
        
        conn = sqlite3.connect(governance_db)
        cursor = conn.cursor()
        
        # Add audit entries - need 3 entries minimum (we add 2, so incomplete)
        cursor.execute(
            "INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) VALUES (?, ?, ?, ?, ?)",
            ("2026-01-15T10:00:00Z", "AC-TEST", "AC_START", "system", "{}")
        )
        cursor.execute(
            "INSERT INTO audit_log (timestamp, ac_id, operation, actor, details) VALUES (?, ?, ?, ?, ?)",
            ("2026-01-15T10:01:00Z", "AC-TEST", "AC_COMPLETE", "system", "{}")
        )
        
        conn.commit()
        conn.close()
        
        validator = ACCompletenessValidator(governance_db)
        is_complete, details = validator.validate_ac_completeness("AC-TEST")
        
        assert is_complete is False  # Only 2 entries, need 3
        assert details["ac_id"] == "AC-TEST"
        assert details["audit_entry_count"] == 2
        assert details["has_start"] is True
        assert details["has_execute"] is False
        assert details["has_complete"] is True


# =============================================================================
# TEST: MutationGuard (Integration)
# =============================================================================

class TestMutationGuard:
    """Test MutationGuard core functionality."""
    
    def test_guard_blocks_locked_phase_modification(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test guard blocks modification to locked phase."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db,
            ImmutabilityPolicy.strict_enforcement()
        )
        
        allowed, reason = guard.can_modify_phase("PHASE-01")
        
        assert allowed is False
        assert "LOCKED" in reason
    
    def test_guard_allows_unlocked_phase_modification(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test guard allows modification to unlocked phase."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db,
            ImmutabilityPolicy.strict_enforcement()
        )
        
        allowed, reason = guard.can_modify_phase("PHASE-VISION-CORE")
        
        assert allowed is True
    
    def test_guard_blocks_tier0_rule_modification(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test guard blocks Tier 0 rule modification."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db,
            ImmutabilityPolicy.strict_enforcement()
        )
        
        allowed, reason = guard.can_modify_rule("SKULL-001")
        
        assert allowed is False
        assert "IMMUTABLE" in reason
    
    def test_guard_blocks_incomplete_ac_completion(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test guard blocks completion of AC without audit entries."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db,
            ImmutabilityPolicy.strict_enforcement()
        )
        
        allowed, reason = guard.can_complete_ac("AC-AR-014-01")
        
        assert allowed is False
        assert "audit entries" in reason
    
    def test_development_mode_allows_locked_phase(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test development mode allows locked phase modification."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db,
            ImmutabilityPolicy.development_mode()
        )
        
        allowed, reason = guard.can_modify_phase("PHASE-01")
        
        assert allowed is True
    
    def test_mutation_logging(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test mutation attempts are logged."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db
        )
        
        # Attempt modifications
        guard.can_modify_phase("PHASE-01")
        guard.can_modify_phase("PHASE-VISION-CORE")
        guard.can_modify_rule("SKULL-001")
        
        # Check log
        history = guard.get_mutation_history()
        
        assert len(history) == 3
        assert history[0]["target"] == "PHASE-01"
        assert history[1]["target"] == "PHASE-VISION-CORE"
    
    def test_mutation_statistics(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test mutation statistics tracking."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db
        )
        
        # Multiple attempts
        guard.can_modify_phase("PHASE-01")  # Blocked
        guard.can_modify_phase("PHASE-VISION-CORE")  # Allowed
        guard.can_modify_rule("SKULL-001")  # Blocked
        
        stats = guard.get_mutation_stats()
        
        assert stats["total_attempts"] == 3
        assert stats["blocked"] == 2
        assert stats["allowed"] == 1
    
    def test_phase_status_report(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test comprehensive phase status report."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db
        )
        
        status = guard.get_phase_status("PHASE-01")
        
        assert status["id"] == "PHASE-01"
        assert status["locked"] is True
        assert status["can_modify"] is False


# =============================================================================
# TEST: Holistic Validation
# =============================================================================

class TestHolisticValidation:
    """Test holistic dependency validation."""
    
    def test_dependency_modification_validation(self, phase_tracker_yaml):
        """Test dependency modification validation blocks locked phase changes."""
        # Update phase tracker to add a phase that depends on locked phase
        phase_tracker_yaml["PHASE-03"] = {
            "title": "Next Phase",
            "status": "PLANNED",
            "locked": True,  # Locked phase
            "requires": "PHASE-02"  # Depends on PHASE-02 (which is locked)
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"phase_tracker": phase_tracker_yaml}, f)
            f.flush()
            phase_file = f.name
        
        try:
            # Create minimal tier0 dir and db
            with tempfile.TemporaryDirectory() as tier0_dir:
                # Create dummy tier0 file
                with open(Path(tier0_dir) / "core-rules.yaml", 'w') as f:
                    yaml.dump({"metadata": {"tier": 0}}, f)
                
                with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
                    db_path = f.name
                
                try:
                    # Create DB schema
                    import sqlite3
                    conn = sqlite3.connect(db_path)
                    cursor = conn.cursor()
                    cursor.execute("""
                        CREATE TABLE audit_log (
                            id INTEGER PRIMARY KEY,
                            timestamp TEXT,
                            ac_id TEXT,
                            operation TEXT,
                            actor TEXT,
                            details TEXT
                        )
                    """)
                    conn.commit()
                    conn.close()
                    
                    guard = MutationGuard(
                        phase_file,
                        tier0_dir,
                        db_path,
                        ImmutabilityPolicy.strict_enforcement()
                    )
                    
                    # Try to modify dependency that locked phase depends on
                    # This should be blocked because PHASE-03 is locked and depends on PHASE-02
                    allowed, reason = guard.can_modify_dependency("PHASE-NEW", "PHASE-02")
                    
                    assert allowed is False
                    assert "locked" in reason.lower()
                finally:
                    Path(db_path).unlink()
        finally:
            Path(phase_file).unlink()
    
    def test_safe_dependency_modification(self, phase_tracker_file, tier0_rules_dir, governance_db):
        """Test safe dependency modification."""
        guard = MutationGuard(
            phase_tracker_file,
            tier0_rules_dir,
            governance_db,
            ImmutabilityPolicy.strict_enforcement()
        )
        
        # Modify dependency that doesn't affect locked phases
        allowed, reason = guard.can_modify_dependency("PHASE-VISION-CORE", "PHASE-NEW")
        
        assert allowed is True
