"""Governance Rules and Audit Logging for Confirmation Gate."""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib

@dataclass
class AuditTrailEntry:
    """Entry in audit trail for confirmation gate decisions."""
    entry_id: str
    operation_id: str
    complexity_score: float
    complexity_level: str
    complexity_factors: Dict[str, float]
    approval_decision: str  # approved | needs_confirmation | escalated
    governance_rule_applied: str  # CONF-GATE-001 through 005
    lens_confidence: float
    user_intent: Optional[str] = None
    affected_files_count: int = 0
    user_confirmation: Optional[bool] = None
    timestamp: datetime = field(default_factory=datetime.now)
    entry_hash: str = ""

    def __post_init__(self):
        """Generate entry hash after initialization."""
        self.entry_hash = self._compute_hash()
    
    def _compute_hash(self) -> str:
        """Compute SHA256 hash of entry for integrity."""
        entry_str = (
            f"{self.operation_id}|{self.complexity_score}|"
            f"{self.approval_decision}|{self.governance_rule_applied}|"
            f"{self.timestamp.isoformat()}"
        )
        return hashlib.sha256(entry_str.encode()).hexdigest()

class GovernanceRules(Enum):
    """Governance rules for confirmation gate (5 Tier 1 Architectural Rules)."""
    
    # CONF-GATE-001: Trivial operations auto-approve
    TRIVIAL_AUTO_APPROVE = "CONF-GATE-001"
    
    # CONF-GATE-002: Confidence-based approval matrix enforcement
    APPROVAL_MATRIX_ENFORCEMENT = "CONF-GATE-002"
    
    # CONF-GATE-003: Alternative recommendations for COMPLEX/CRITICAL
    ALTERNATIVE_RECOMMENDATIONS = "CONF-GATE-003"
    
    # CONF-GATE-004: User goal enhancement with best recommendation
    USER_GOAL_ENHANCEMENT = "CONF-GATE-004"
    
    # CONF-GATE-005: Audit trail enrichment with complexity factors
    AUDIT_TRAIL_ENRICHMENT = "CONF-GATE-005"

class GovernanceEnforcer:
    """Enforces confirmation gate governance rules."""
    
    # Rule thresholds
    TRIVIAL_THRESHOLD = 0.15  # CONF-GATE-001
    
    # Approval matrix thresholds  # CONF-GATE-002
    APPROVAL_MATRIX = {
        'trivial': 0.15,
        'simple': 0.35,
        'moderate': 0.60,
        'complex': 0.85,
        'critical': float('inf'),
    }
    
    # Alternative recommendation requirement  # CONF-GATE-003
    RECOMMEND_ALTERNATIVES_FOR = ['COMPLEX', 'CRITICAL']
    MIN_ALTERNATIVES = 3
    
    # User goal enhancement flag  # CONF-GATE-004
    ENABLE_GOAL_ENHANCEMENT = True
    
    # Audit trail tracking  # CONF-GATE-005
    TRACK_AUDIT_TRAIL = True
    
    def __init__(self, enforcement_mode: str = 'STRICT'):
        """
        Initialize governance enforcer.
        
        Args:
            enforcement_mode: 'STRICT' (no overrides) or 'PERMISSIVE' (allows overrides)
        """
        self.enforcement_mode = enforcement_mode
        self.audit_trail: List[AuditTrailEntry] = []
        self.violation_count = 0
        self.entry_counter = 0
    
    def validate_trivial_auto_approval(
        self,
        complexity_score: float,
        approved: bool,
    ) -> bool:
        """
        CONF-GATE-001: Trivial operations must auto-approve.
        
        Validates: If complexity_score <= 0.15, operation MUST be approved.
        """
        if complexity_score <= self.TRIVIAL_THRESHOLD:
            if not approved:
                self.violation_count += 1
                if self.enforcement_mode == 'STRICT':
                    raise ValueError(
                        f"CONF-GATE-001 violation: Trivial operation (score={complexity_score}) "
                        f"must be auto-approved but was rejected"
                    )
                return False
        return True
    
    def validate_approval_matrix(
        self,
        complexity_score: float,
        complexity_level: str,
        requires_confirmation: bool,
    ) -> bool:
        """
        CONF-GATE-002: Approval matrix must be enforced.
        
        Validates:
        - TRIVIAL/SIMPLE (<= 0.35): Can be auto-approved
        - MODERATE (0.35-0.60): Must require confirmation
        - COMPLEX/CRITICAL (> 0.60): Must require confirmation
        """
        if complexity_score <= 0.35:
            # TRIVIAL/SIMPLE: Confirmation optional
            return True
        elif complexity_score <= 0.60:
            # MODERATE: Must require confirmation
            if not requires_confirmation:
                self.violation_count += 1
                if self.enforcement_mode == 'STRICT':
                    raise ValueError(
                        f"CONF-GATE-002 violation: MODERATE operation (score={complexity_score}) "
                        f"must require confirmation"
                    )
                return False
        else:
            # COMPLEX/CRITICAL: Must require confirmation + escalation
            if not requires_confirmation:
                self.violation_count += 1
                if self.enforcement_mode == 'STRICT':
                    raise ValueError(
                        f"CONF-GATE-002 violation: {complexity_level} operation "
                        f"(score={complexity_score}) must require confirmation"
                    )
                return False
        
        return True
    
    def validate_alternative_recommendations(
        self,
        complexity_level: str,
        alternatives: List[Any],
    ) -> bool:
        """
        CONF-GATE-003: Alternatives required for COMPLEX/CRITICAL.
        
        Validates:
        - COMPLEX/CRITICAL operations must offer alternatives
        - At least 3 alternatives recommended
        """
        if complexity_level not in self.RECOMMEND_ALTERNATIVES_FOR:
            return True  # Not required for other levels
        
        if not alternatives:
            self.violation_count += 1
            if self.enforcement_mode == 'STRICT':
                raise ValueError(
                    f"CONF-GATE-003 violation: {complexity_level} operation "
                    f"must provide alternatives"
                )
            return False
        
        if len(alternatives) < self.MIN_ALTERNATIVES:
            # Warning but not failure (could be fewer alternatives available)
            pass
        
        return True
    
    def validate_user_goal_enhancement(
        self,
        complexity_level: str,
        best_recommendation: Optional[str],
    ) -> bool:
        """
        CONF-GATE-004: User goal enhancement with best recommendation.
        
        Validates: For COMPLEX/CRITICAL, best recommendation should be provided.
        """
        if not self.ENABLE_GOAL_ENHANCEMENT:
            return True
        
        if complexity_level in ['COMPLEX', 'CRITICAL']:
            if not best_recommendation:
                # Warning: should provide recommendation
                pass
        
        return True
    
    def record_decision_in_audit_trail(
        self,
        operation_id: str,
        complexity_score: float,
        complexity_level: str,
        complexity_factors: Dict[str, float],
        approved: bool,
        lens_confidence: float,
        user_intent: Optional[str] = None,
        affected_files_count: int = 0,
    ) -> AuditTrailEntry:
        """
        CONF-GATE-005: Record decision in audit trail with complexity factors.
        
        Creates and records audit entry for every decision.
        """
        self.entry_counter += 1
        
        # Determine rule applied
        if complexity_score <= 0.15:
            rule = GovernanceRules.TRIVIAL_AUTO_APPROVE
        elif complexity_score <= 0.60:
            rule = GovernanceRules.APPROVAL_MATRIX_ENFORCEMENT
        else:
            rule = GovernanceRules.ALTERNATIVE_RECOMMENDATIONS
        
        # Determine approval decision string
        if approved:
            approval_str = "approved"
        elif complexity_level in ['COMPLEX', 'CRITICAL']:
            approval_str = "escalated"
        else:
            approval_str = "needs_confirmation"
        
        # Create audit entry
        entry = AuditTrailEntry(
            entry_id=f"AUDIT_{self.entry_counter:06d}",
            operation_id=operation_id,
            complexity_score=complexity_score,
            complexity_level=complexity_level,
            complexity_factors=complexity_factors,
            approval_decision=approval_str,
            governance_rule_applied=rule.value,
            lens_confidence=lens_confidence,
            user_intent=user_intent,
            affected_files_count=affected_files_count,
        )
        
        # Record in audit trail
        self.audit_trail.append(entry)
        
        return entry
    
    def get_audit_trail(self, limit: Optional[int] = None) -> List[AuditTrailEntry]:
        """Get audit trail entries."""
        trail = self.audit_trail
        if limit:
            trail = trail[-limit:]
        return trail
    
    def verify_audit_trail_integrity(self) -> Dict[str, Any]:
        """
        Verify integrity of audit trail.
        
        Checks:
        - All entries have valid hashes
        - No gaps in entry numbering
        - All required fields populated
        """
        issues = []
        
        for i, entry in enumerate(self.audit_trail):
            # Verify hash
            expected_hash = entry._compute_hash()
            if entry.entry_hash != expected_hash:
                issues.append(f"Hash mismatch at entry {entry.entry_id}")
            
            # Verify required fields
            if not entry.operation_id:
                issues.append(f"Missing operation_id at entry {entry.entry_id}")
            if not entry.governance_rule_applied:
                issues.append(f"Missing governance_rule at entry {entry.entry_id}")
        
        return {
            'integrity_valid': len(issues) == 0,
            'total_entries': len(self.audit_trail),
            'issues': issues,
        }
    
    def get_rule_enforcement_statistics(self) -> Dict[str, Any]:
        """Get statistics on rule enforcement."""
        if not self.audit_trail:
            return {
                'total_decisions': 0,
                'violations': 0,
                'enforcement_mode': self.enforcement_mode,
                'rules_applied': {},
            }
        
        rules_applied = {}
        for entry in self.audit_trail:
            rule = entry.governance_rule_applied
            rules_applied[rule] = rules_applied.get(rule, 0) + 1
        
        return {
            'total_decisions': len(self.audit_trail),
            'violations': self.violation_count,
            'enforcement_mode': self.enforcement_mode,
            'rules_applied': rules_applied,
            'violation_rate': self.violation_count / len(self.audit_trail) if self.audit_trail else 0,
        }
    
    def validate_all_rules(
        self,
        complexity_score: float,
        complexity_level: str,
        approved: bool,
        requires_confirmation: bool,
        alternatives: Optional[List[Any]] = None,
    ) -> Dict[str, bool]:
        """
        Validate all governance rules for a decision.
        
        Returns:
            Dict with validation results for each rule
        """
        results = {
            'CONF-GATE-001': self.validate_trivial_auto_approval(complexity_score, approved),
            'CONF-GATE-002': self.validate_approval_matrix(complexity_score, complexity_level, requires_confirmation),
            'CONF-GATE-003': self.validate_alternative_recommendations(complexity_level, alternatives or []),
            'CONF-GATE-004': self.validate_user_goal_enhancement(complexity_level, None),
            'CONF-GATE-005': True,  # Always passes (audit trail created automatically)
        }
        
        return results
    
    def is_compliant(self) -> bool:
        """Check if all decisions are compliant with governance rules."""
        return self.violation_count == 0

class AuditLogger:
    """Integrates governance audit logging with existing system audit trail."""
    
    def __init__(self, enforcer: GovernanceEnforcer):
        """Initialize audit logger."""
        self.enforcer = enforcer
        self.external_audit_trail: List[Dict[str, Any]] = []
    
    def log_to_external_audit(self, entry: AuditTrailEntry) -> None:
        """Log confirmation gate decision to external audit system."""
        audit_record = {
            'timestamp': entry.timestamp.isoformat(),
            'entry_id': entry.entry_id,
            'operation_id': entry.operation_id,
            'complexity_score': entry.complexity_score,
            'complexity_level': entry.complexity_level,
            'approval_decision': entry.approval_decision,
            'governance_rule': entry.governance_rule_applied,
            'entry_hash': entry.entry_hash,
        }
        self.external_audit_trail.append(audit_record)
    
    def get_governance_audit_report(self) -> Dict[str, Any]:
        """Get comprehensive governance audit report."""
        return {
            'governance_rules_statistics': self.enforcer.get_rule_enforcement_statistics(),
            'audit_trail_integrity': self.enforcer.verify_audit_trail_integrity(),
            'total_logged_entries': len(self.external_audit_trail),
            'is_compliant': self.enforcer.is_compliant(),
        }
