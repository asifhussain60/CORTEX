"""
Governance Rules & Audit Trail - Production Implementation.

Manages governance rules, enforces compliance, and maintains audit trail for
all gate decisions and operations.
"""

from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class GovernanceRuleType(Enum):
    """Types of governance rules."""
    APPROVAL_ROUTING = "approval_routing"
    CONFIDENCE_THRESHOLD = "confidence_threshold"
    RISK_ASSESSMENT = "risk_assessment"
    AUDIT_LOGGING = "audit_logging"
    COMPLIANCE_CHECK = "compliance_check"


class AuditEventType(Enum):
    """Types of audit events."""
    GATE_DECISION = "gate_decision"
    APPROVER_ASSIGNED = "approver_assigned"
    REVIEW_REQUESTED = "review_requested"
    REVIEW_COMPLETED = "review_completed"
    DECISION_OVERRIDDEN = "decision_overridden"
    RULE_VIOLATION = "rule_violation"
    COMPLIANCE_CHECK = "compliance_check"


@dataclass
class GovernanceRule:
    """Definition of a governance rule."""
    
    rule_id: str
    rule_type: GovernanceRuleType
    description: str
    enforcement_level: str  # "strict", "warning", "informational"
    is_active: bool
    created_at: datetime
    created_by: str


@dataclass
class AuditEntry:
    """Single audit trail entry."""
    
    event_id: str
    event_type: AuditEventType
    conversation_id: str
    actor_id: str
    action: str
    affected_rules: List[str] = field(default_factory=list)
    metadata: Dict = field(default_factory=dict)
    timestamp: datetime = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization."""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type.value,
            'conversation_id': self.conversation_id,
            'actor_id': self.actor_id,
            'action': self.action,
            'affected_rules': self.affected_rules,
            'metadata': self.metadata,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
        }


@dataclass
class ComplianceReport:
    """Compliance report for a period."""
    
    report_id: str
    period_start: datetime
    period_end: datetime
    total_decisions: int
    decisions_by_type: Dict[str, int]
    rule_violations: int
    violations_by_rule: Dict[str, int]
    audit_entries_count: int
    compliance_score: float  # 0-1
    generated_at: datetime


class GovernanceEngine:
    """
    Governance and Audit Trail Engine.
    
    Manages governance rules, enforces compliance, and maintains audit trail
    for all gate decisions and operations.
    """
    
    def __init__(self):
        """Initialize governance engine."""
        self.rules: Dict[str, GovernanceRule] = {}
        self.audit_trail: List[AuditEntry] = []
        self.rule_violations: List[Dict] = []
        self._initialize_default_rules()
    
    def _initialize_default_rules(self) -> None:
        """Initialize 5 default governance rules."""
        rules = [
            GovernanceRule(
                rule_id="GOV-001",
                rule_type=GovernanceRuleType.APPROVAL_ROUTING,
                description="All high-complexity decisions require architecture team review",
                enforcement_level="strict",
                is_active=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            GovernanceRule(
                rule_id="GOV-002",
                rule_type=GovernanceRuleType.CONFIDENCE_THRESHOLD,
                description="Minimum confidence threshold of 0.65 required for review",
                enforcement_level="strict",
                is_active=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            GovernanceRule(
                rule_id="GOV-003",
                rule_type=GovernanceRuleType.RISK_ASSESSMENT,
                description="Security risks must be reviewed by security team",
                enforcement_level="strict",
                is_active=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            GovernanceRule(
                rule_id="GOV-004",
                rule_type=GovernanceRuleType.AUDIT_LOGGING,
                description="All gate decisions must be logged to audit trail",
                enforcement_level="strict",
                is_active=True,
                created_at=datetime.now(),
                created_by="system"
            ),
            GovernanceRule(
                rule_id="GOV-005",
                rule_type=GovernanceRuleType.COMPLIANCE_CHECK,
                description="Monthly compliance reports required",
                enforcement_level="informational",
                is_active=True,
                created_at=datetime.now(),
                created_by="system"
            ),
        ]
        
        for rule in rules:
            self.rules[rule.rule_id] = rule
    
    def log_audit_entry(
        self,
        event_type: AuditEventType,
        conversation_id: str,
        actor_id: str,
        action: str,
        affected_rules: List[str] = None,
        metadata: Dict = None
    ) -> AuditEntry:
        """
        Log an audit entry.
        
        Args:
            event_type: Type of event
            conversation_id: Related conversation ID
            actor_id: ID of actor performing action
            action: Description of action
            affected_rules: Rules affected by this action
            metadata: Additional metadata
        
        Returns:
            AuditEntry
        """
        entry = AuditEntry(
            event_id=f"AUD-{len(self.audit_trail)+1:08d}",
            event_type=event_type,
            conversation_id=conversation_id,
            actor_id=actor_id,
            action=action,
            affected_rules=affected_rules or [],
            metadata=metadata or {},
            timestamp=datetime.now()
        )
        
        self.audit_trail.append(entry)
        return entry
    
    def check_rule_compliance(
        self,
        rule_id: str,
        context: Dict
    ) -> Tuple[bool, str]:
        """
        Check if rule is satisfied.
        
        Args:
            rule_id: Rule to check
            context: Execution context
        
        Returns:
            (is_compliant, message)
        """
        if rule_id not in self.rules:
            return False, f"Rule {rule_id} not found"
        
        rule = self.rules[rule_id]
        
        if not rule.is_active:
            return True, "Rule not active"
        
        # Specific rule checks
        if rule_id == "GOV-001":
            complexity = context.get('complexity_level')
            if complexity in ['complex', 'critical']:
                approvers = context.get('approvers', [])
                if 'architecture-team' not in approvers:
                    return False, "Architecture team review required for complex/critical"
        
        elif rule_id == "GOV-002":
            confidence = context.get('confidence')
            if confidence is not None and confidence < 0.65:
                return False, f"Confidence {confidence} below threshold 0.65"
        
        elif rule_id == "GOV-003":
            risks = context.get('risks', [])
            if 'security' in risks:
                approvers = context.get('approvers', [])
                if 'security-team' not in approvers:
                    return False, "Security team review required for security risks"
        
        elif rule_id == "GOV-004":
            # Always compliant if we're logging
            return True, "Audit logging in progress"
        
        elif rule_id == "GOV-005":
            # Informational only
            return True, "Compliance check informational"
        
        return True, "Rule satisfied"
    
    def validate_all_rules(self, context: Dict) -> Dict:
        """
        Validate all active rules against context.
        
        Returns:
            {'compliant': bool, 'violations': list, 'warnings': list}
        """
        violations = []
        warnings = []
        
        for rule_id, rule in self.rules.items():
            if not rule.is_active:
                continue
            
            is_compliant, message = self.check_rule_compliance(rule_id, context)
            
            if not is_compliant:
                if rule.enforcement_level == "strict":
                    violations.append({'rule_id': rule_id, 'message': message})
                    self.rule_violations.append({
                        'rule_id': rule_id,
                        'timestamp': datetime.now(),
                        'context': context
                    })
                elif rule.enforcement_level == "warning":
                    warnings.append({'rule_id': rule_id, 'message': message})
        
        return {
            'compliant': len(violations) == 0,
            'violations': violations,
            'warnings': warnings,
        }
    
    def get_audit_trail(
        self,
        conversation_id: str = None,
        event_type: AuditEventType = None,
        start_time: datetime = None,
        end_time: datetime = None
    ) -> List[AuditEntry]:
        """
        Retrieve filtered audit trail.
        
        Args:
            conversation_id: Filter by conversation
            event_type: Filter by event type
            start_time: Filter by start time
            end_time: Filter by end time
        
        Returns:
            Filtered audit entries
        """
        entries = self.audit_trail
        
        if conversation_id:
            entries = [e for e in entries if e.conversation_id == conversation_id]
        
        if event_type:
            entries = [e for e in entries if e.event_type == event_type]
        
        if start_time:
            entries = [e for e in entries if e.timestamp >= start_time]
        
        if end_time:
            entries = [e for e in entries if e.timestamp <= end_time]
        
        return entries
    
    def generate_compliance_report(
        self,
        period_start: datetime,
        period_end: datetime
    ) -> ComplianceReport:
        """
        Generate compliance report for period.
        
        Args:
            period_start: Report period start
            period_end: Report period end
        
        Returns:
            ComplianceReport with compliance metrics
        """
        entries = self.get_audit_trail(
            start_time=period_start,
            end_time=period_end
        )
        
        decisions_by_type = {}
        for entry in entries:
            if entry.event_type == AuditEventType.GATE_DECISION:
                decision = entry.metadata.get('decision', 'unknown')
                decisions_by_type[decision] = decisions_by_type.get(decision, 0) + 1
        
        violations_by_rule = {}
        for violation in self.rule_violations:
            timestamp = violation.get('timestamp')
            if period_start <= timestamp <= period_end:
                rule_id = violation.get('rule_id')
                violations_by_rule[rule_id] = violations_by_rule.get(rule_id, 0) + 1
        
        total_decisions = sum(decisions_by_type.values())
        total_violations = sum(violations_by_rule.values())
        
        # Compliance score: 1.0 - (violations / decisions)
        compliance_score = 1.0 if total_decisions == 0 else 1.0 - (total_violations / total_decisions)
        compliance_score = max(0, min(1, compliance_score))  # Clamp 0-1
        
        return ComplianceReport(
            report_id=f"COMP-{len(self.audit_trail):08d}",
            period_start=period_start,
            period_end=period_end,
            total_decisions=total_decisions,
            decisions_by_type=decisions_by_type,
            rule_violations=total_violations,
            violations_by_rule=violations_by_rule,
            audit_entries_count=len(entries),
            compliance_score=compliance_score,
            generated_at=datetime.now()
        )
    
    def get_rules(self) -> List[GovernanceRule]:
        """Get all governance rules."""
        return list(self.rules.values())
    
    def enable_rule(self, rule_id: str) -> bool:
        """
        Enable a governance rule.
        
        Args:
            rule_id: Rule to enable
        
        Returns:
            True if successful
        """
        if rule_id in self.rules:
            self.rules[rule_id].is_active = True
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """
        Disable a governance rule.
        
        Args:
            rule_id: Rule to disable
        
        Returns:
            True if successful
        """
        if rule_id in self.rules:
            self.rules[rule_id].is_active = False
            return True
        return False
    
    def export_audit_trail(self) -> List[Dict]:
        """Export audit trail as list of dictionaries."""
        return [entry.to_dict() for entry in self.audit_trail]
    
    def get_audit_trail_size(self) -> int:
        """Get current audit trail size."""
        return len(self.audit_trail)
    
    def clear_history(self) -> None:
        """Clear audit trail and violations."""
        self.audit_trail = []
        self.rule_violations = []
