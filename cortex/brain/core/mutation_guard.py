"""
Mutation Guard: Prevents modifications to locked phases and immutable resources.

Implements hallucination prevention by enforcing:
1. Locked phase immutability (read-only after locked: true)
2. Tier 0 rule immutability (governance rules cannot be modified)
3. AC-ID completeness requirements (MIN 3 audit entries)
4. Holistic change validation (dependencies must remain valid)

All mutation attempts are logged with full audit trail.

Classes:
    MutationAttempt: Record of a modification attempt (success or blocked)
    MutationGuard: Core immutability enforcement system
    PhaseImmutabilityValidator: Validates phase lock status
    RuleImmutabilityValidator: Validates Tier 0 rule protection
    ACCompletenessValidator: Validates AC-ID audit requirements
"""

import hashlib
import os
import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

# =============================================================================
# DATA STRUCTURES
# =============================================================================

class MutationType(Enum):
    """Type of mutation being attempted."""
    PHASE_MODIFICATION = "phase_modification"
    AC_ID_MODIFICATION = "ac_id_modification"
    RULE_MODIFICATION = "rule_modification"
    TIER_MODIFICATION = "tier_modification"
    DEPENDENCY_MODIFICATION = "dependency_modification"
    CONFIG_MODIFICATION = "config_modification"
    TIER0_RULE_MODIFICATION = "tier0_rule_modification"
    PHASE_LOCK_MODIFICATION = "phase_lock_modification"


class MutationResult(Enum):
    """Result of mutation validation."""
    ALLOWED = "allowed"
    BLOCKED_PHASE_LOCKED = "blocked_phase_locked"
    BLOCKED_RULE_IMMUTABLE = "blocked_rule_immutable"
    BLOCKED_AC_INCOMPLETE = "blocked_ac_incomplete"
    BLOCKED_DEPENDENCY_VIOLATION = "blocked_dependency_violation"
    BLOCKED_AUDIT_REQUIRED = "blocked_audit_required"
    BLOCKED_HOLISTIC_VALIDATION_FAILED = "blocked_holistic_validation_failed"
    ERROR = "error"


@dataclass
class MutationAttempt:
    """Record of a modification attempt."""

    timestamp: str
    mutation_type: str  # MutationType.value
    target: str  # What was being modified (phase_id, ac_id, etc.)
    result: str  # MutationResult.value
    reason: str  # Why allowed or blocked
    actor: str = "system"  # Who attempted the mutation
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "timestamp": self.timestamp,
            "mutation_type": self.mutation_type,
            "target": self.target,
            "result": self.result,
            "reason": self.reason,
            "actor": self.actor,
            "details": self.details
        }


@dataclass
class ImmutabilityPolicy:
    """Policy defining what can/cannot be modified."""

    locked_phase_modification_allowed: bool = False
    tier0_rule_modification_allowed: bool = False
    phase_lock_modification_allowed: bool = False
    ac_completion_requires_audit_entries: int = 3
    require_holistic_validation: bool = True

    @classmethod
    def strict_enforcement(cls) -> 'ImmutabilityPolicy':
        """Create strict policy (no exceptions)."""
        return cls(
            locked_phase_modification_allowed=False,
            tier0_rule_modification_allowed=False,
            phase_lock_modification_allowed=False,
            ac_completion_requires_audit_entries=3,
            require_holistic_validation=True
        )

    @classmethod
    def development_mode(cls) -> 'ImmutabilityPolicy':
        """Create development policy (allows some modifications for testing)."""
        return cls(
            locked_phase_modification_allowed=True,
            tier0_rule_modification_allowed=False,
            phase_lock_modification_allowed=False,
            ac_completion_requires_audit_entries=1,
            require_holistic_validation=False
        )


# =============================================================================
# VALIDATORS
# =============================================================================

class PhaseImmutabilityValidator:
    """Validates that locked phases cannot be modified."""

    def __init__(self, phase_tracker: Dict[str, Any]):
        """
        Initialize validator.

        Args:
            phase_tracker: Dict from cortex-master.yaml phase_tracker section
        """
        self.phase_tracker = phase_tracker

    def validate_phase_locked(self, phase_id: str) -> Tuple[bool, str]:
        """
        Check if phase is locked.

        Args:
            phase_id: Phase identifier (e.g., "PHASE-01")

        Returns:
            Tuple of (is_locked, reason)
        """
        if phase_id not in self.phase_tracker:
            return False, f"Phase {phase_id} not found in tracker"

        phase_info = self.phase_tracker[phase_id]
        is_locked = phase_info.get("locked", False)

        if is_locked:
            return True, f"Phase {phase_id} is LOCKED (status: {phase_info.get('status')})"

        return False, f"Phase {phase_id} is unlocked"

    def validate_modification_allowed(self, phase_id: str, policy: ImmutabilityPolicy) -> Tuple[bool, str]:
        """
        Check if modification to phase is allowed.

        Args:
            phase_id: Phase identifier
            policy: ImmutabilityPolicy to enforce

        Returns:
            Tuple of (allowed, reason)
        """
        is_locked, lock_reason = self.validate_phase_locked(phase_id)

        if is_locked and not policy.locked_phase_modification_allowed:
            return False, f"Modification blocked: {lock_reason}"

        if is_locked and policy.locked_phase_modification_allowed:
            return True, f"Modification allowed (development mode): {lock_reason}"

        return True, "Phase is unlocked - modification allowed"

    def get_phase_status(self, phase_id: str) -> Dict[str, Any]:
        """Get phase status information."""
        if phase_id not in self.phase_tracker:
            return {}

        phase = self.phase_tracker[phase_id]
        return {
            "id": phase_id,
            "title": phase.get("title", ""),
            "status": phase.get("status", ""),
            "locked": phase.get("locked", False),
            "ac_ids": phase.get("ac_ids", 0),
            "completed_ac_ids": phase.get("completed_ac_ids", 0),
            "requires": phase.get("requires")
        }


class RuleImmutabilityValidator:
    """Validates that Tier 0 rules cannot be modified."""

    def __init__(self, tier0_rules_path: str):
        """
        Initialize validator.

        Args:
            tier0_rules_path: Path to tier 0 governance rules directory
        """
        self.tier0_rules_path = tier0_rules_path
        self.loaded_rules: Dict[str, Dict[str, Any]] = {}
        self.rule_hashes: Dict[str, str] = {}
        self._load_rules()

    def _load_rules(self) -> None:
        """Load all Tier 0 rules from YAML files."""
        tier0_path = Path(self.tier0_rules_path)

        if not tier0_path.exists():
            return

        for yaml_file in tier0_path.glob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data:
                        self.loaded_rules[yaml_file.stem] = data
                        # Compute hash for integrity checking
                        content = yaml.dump(data, sort_keys=True)
                        self.rule_hashes[yaml_file.stem] = hashlib.sha256(content.encode()).hexdigest()
            except Exception:
                pass

    def validate_rule_immutable(self, rule_id: str) -> Tuple[bool, str]:
        """
        Check if Tier 0 rule can be modified.

        Args:
            rule_id: Rule identifier (e.g., "SKULL-001")

        Returns:
            Tuple of (is_immutable, reason)
        """
        # Tier 0 rules are always immutable
        return True, f"Tier 0 rule {rule_id} is IMMUTABLE and cannot be modified"

    def validate_rule_integrity(self, rule_set: str) -> Tuple[bool, str]:
        """
        Verify Tier 0 rules have not been modified.

        Args:
            rule_set: Name of rule set (e.g., "core-rules")

        Returns:
            Tuple of (integrity_valid, reason)
        """
        if rule_set not in self.loaded_rules:
            return False, f"Rule set {rule_set} not loaded"

        tier0_path = Path(self.tier0_rules_path)
        yaml_file = tier0_path / f"{rule_set}.yaml"

        if not yaml_file.exists():
            return False, f"Rule set file not found: {yaml_file}"

        try:
            with open(yaml_file, 'r') as f:
                current_data = yaml.safe_load(f)
                current_content = yaml.dump(current_data, sort_keys=True)
                current_hash = hashlib.sha256(current_content.encode()).hexdigest()

                if current_hash != self.rule_hashes.get(rule_set):
                    return False, f"Rule set {rule_set} has been modified (hash mismatch)"

                return True, f"Rule set {rule_set} integrity verified"
        except Exception as e:
            return False, f"Error verifying rule set: {e}"


class ACCompletenessValidator:
    """Validates AC-ID completeness requirements."""

    def __init__(self, db_path: str):
        """
        Initialize validator with database connection.

        Args:
            db_path: Path to governance.db
        """
        self.db_path = db_path

    def validate_ac_audit_entries(self, ac_id: str, required_count: int = 3) -> Tuple[bool, int, str]:
        """
        Check if AC-ID has minimum required audit entries.

        Args:
            ac_id: Acceptance criteria identifier
            required_count: Minimum required entries (default 3: START, EXECUTE, COMPLETE)

        Returns:
            Tuple of (has_required_entries, actual_count, reason)
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT COUNT(*) FROM audit_log WHERE ac_id = ?",
                (ac_id,)
            )
            result = cursor.fetchone()
            actual_count = result[0] if result else 0

            conn.close()

            if actual_count >= required_count:
                return True, actual_count, f"AC {ac_id} has {actual_count} audit entries (required: {required_count})"
            else:
                return False, actual_count, f"AC {ac_id} has {actual_count} audit entries (required: {required_count})"

        except Exception as e:
            return False, 0, f"Error checking audit entries: {e}"

    def validate_ac_completeness(self, ac_id: str) -> Tuple[bool, Dict[str, Any]]:
        """
        Comprehensive AC completeness check.

        Returns:
            Tuple of (is_complete, details_dict)
        """
        has_entries, count, reason = self.validate_ac_audit_entries(ac_id)

        details = {
            "ac_id": ac_id,
            "audit_entry_count": count,
            "required_entry_count": 3,
            "has_start": False,
            "has_execute": False,
            "has_complete": False
        }

        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute(
                "SELECT DISTINCT operation FROM audit_log WHERE ac_id = ?",
                (ac_id,)
            )
            operations = {row[0] for row in cursor.fetchall()}

            details["has_start"] = "AC_START" in operations
            details["has_execute"] = "AC_EXECUTE" in operations
            details["has_complete"] = "AC_COMPLETE" in operations

            conn.close()
        except Exception:
            pass

        return has_entries, details


# =============================================================================
# MUTATION GUARD (Main Class)
# =============================================================================

class MutationGuard:
    """
    Core immutability enforcement system.

    Prevents modifications to locked phases, Tier 0 rules, and incomplete ACs.
    All attempts (allowed or blocked) are logged with full audit trail.
    """

    def __init__(
        self,
        phase_tracker_path: str,
        tier0_rules_path: str,
        db_path: str,
        policy: Optional[ImmutabilityPolicy] = None
    ):
        """
        Initialize MutationGuard.

        Args:
            phase_tracker_path: Path to phase_tracker YAML or cortex-master.yaml
            tier0_rules_path: Path to tier 0 governance rules directory
            db_path: Path to governance.db
            policy: ImmutabilityPolicy to enforce (defaults to strict)
        """
        self.phase_tracker_path = phase_tracker_path
        self.tier0_rules_path = tier0_rules_path
        self.db_path = db_path
        self.policy = policy or ImmutabilityPolicy.strict_enforcement()

        # Load phase tracker
        self.phase_tracker = self._load_phase_tracker()

        # Initialize validators
        self.phase_validator = PhaseImmutabilityValidator(self.phase_tracker)
        self.rule_validator = RuleImmutabilityValidator(tier0_rules_path)
        self.ac_validator = ACCompletenessValidator(db_path)

        # Mutation history
        self.mutation_log: List[MutationAttempt] = []

    def _load_phase_tracker(self) -> Dict[str, Any]:
        """Load phase_tracker from YAML file."""
        try:
            with open(self.phase_tracker_path, 'r') as f:
                data = yaml.safe_load(f)

                # Handle both direct phase_tracker YAML and full cortex-master.yaml
                if "phase_tracker" in data:
                    return data["phase_tracker"]
                else:
                    return data

        except Exception:
            return {}

    def can_modify_phase(self, phase_id: str) -> Tuple[bool, str]:
        """
        Check if phase can be modified.

        Args:
            phase_id: Phase identifier

        Returns:
            Tuple of (allowed, reason)
        """
        allowed, reason = self.phase_validator.validate_modification_allowed(phase_id, self.policy)

        # Log mutation attempt
        self._log_mutation(
            mutation_type=MutationType.PHASE_MODIFICATION,
            target=phase_id,
            result=MutationResult.ALLOWED if allowed else MutationResult.BLOCKED_PHASE_LOCKED,
            reason=reason
        )

        return allowed, reason

    def can_modify_rule(self, rule_id: str) -> Tuple[bool, str]:
        """
        Check if Tier 0 rule can be modified.

        Args:
            rule_id: Rule identifier

        Returns:
            Tuple of (allowed, reason)
        """
        is_immutable, reason = self.rule_validator.validate_rule_immutable(rule_id)

        allowed = not is_immutable and self.policy.tier0_rule_modification_allowed
        result = MutationResult.ALLOWED if allowed else MutationResult.BLOCKED_RULE_IMMUTABLE

        self._log_mutation(
            mutation_type=MutationType.TIER0_RULE_MODIFICATION,
            target=rule_id,
            result=result,
            reason=reason
        )

        return allowed, reason

    def can_complete_ac(self, ac_id: str) -> Tuple[bool, str]:
        """
        Check if AC-ID can be marked as complete.

        Args:
            ac_id: Acceptance criteria identifier

        Returns:
            Tuple of (allowed, reason)
        """
        has_entries, details = self.ac_validator.validate_ac_completeness(ac_id)

        if not has_entries:
            result = MutationResult.BLOCKED_AC_INCOMPLETE
            reason = (f"AC {ac_id} cannot be completed: "
                     f"only {details['audit_entry_count']} audit entries "
                     f"(required: {details['required_entry_count']})")
        else:
            result = MutationResult.ALLOWED
            reason = f"AC {ac_id} has sufficient audit entries ({details['audit_entry_count']})"

        self._log_mutation(
            mutation_type=MutationType.AC_ID_MODIFICATION,
            target=ac_id,
            result=result,
            reason=reason,
            details=details
        )

        return has_entries, reason

    def can_modify_dependency(self, from_phase: str, to_phase: str) -> Tuple[bool, str]:
        """
        Check if phase dependency can be modified (holistic validation).

        Args:
            from_phase: Phase that requires the dependency
            to_phase: Phase being depended on

        Returns:
            Tuple of (allowed, reason)
        """
        if not self.policy.require_holistic_validation:
            return True, "Holistic validation disabled"

        # Check if dependency would break any locked phases
        for phase_id, phase_info in self.phase_tracker.items():
            if phase_info.get("locked", False):
                requires = phase_info.get("requires")
                if requires == to_phase:
                    # Locked phase depends on to_phase - cannot modify
                    result = MutationResult.BLOCKED_DEPENDENCY_VIOLATION
                    reason = f"Cannot modify dependency: locked phase {phase_id} depends on {to_phase}"

                    self._log_mutation(
                        mutation_type=MutationType.DEPENDENCY_MODIFICATION,
                        target=f"{from_phase}->{to_phase}",
                        result=result,
                        reason=reason
                    )

                    return False, reason

        result = MutationResult.ALLOWED
        reason = "Dependency modification would not break locked phases"

        self._log_mutation(
            mutation_type=MutationType.DEPENDENCY_MODIFICATION,
            target=f"{from_phase}->{to_phase}",
            result=result,
            reason=reason
        )

        return True, reason

    def _log_mutation(
        self,
        mutation_type: MutationType,
        target: str,
        result: MutationResult,
        reason: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """Log mutation attempt."""
        attempt = MutationAttempt(
            timestamp=datetime.utcnow().isoformat(),
            mutation_type=mutation_type.value,
            target=target,
            result=result.value,
            reason=reason,
            details=details or {}
        )

        self.mutation_log.append(attempt)

    def get_mutation_history(self) -> List[Dict[str, Any]]:
        """Get complete mutation history."""
        return [attempt.to_dict() for attempt in self.mutation_log]

    def get_mutation_stats(self) -> Dict[str, Any]:
        """Get mutation statistics."""
        total = len(self.mutation_log)
        allowed = sum(1 for m in self.mutation_log if m.result == MutationResult.ALLOWED.value)
        blocked = total - allowed

        by_type = {}
        by_result = {}

        for mutation in self.mutation_log:
            mtype = mutation.mutation_type
            result = mutation.result

            by_type[mtype] = by_type.get(mtype, 0) + 1
            by_result[result] = by_result.get(result, 0) + 1

        return {
            "total_attempts": total,
            "allowed": allowed,
            "blocked": blocked,
            "by_type": by_type,
            "by_result": by_result
        }

    def get_phase_status(self, phase_id: str) -> Dict[str, Any]:
        """Get comprehensive phase status."""
        status = self.phase_validator.get_phase_status(phase_id)

        # Add immutability status
        can_modify, reason = self.can_modify_phase(phase_id)
        status["can_modify"] = can_modify
        status["modification_reason"] = reason

        return status
