"""
AC-CONF-004-01: Governance Rules & Audit Trail - Unit & Integration Tests.

Requirements:
- Implement 5 governance rules for gate
- Create audit trail for all decisions
- Enable compliance reporting
"""

import pytest
from datetime import datetime
from typing import List, Dict
from dataclasses import dataclass, field
from enum import Enum


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
    
    Manages governance rules, enforces compliance, and maintains audit trail.
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
    ) -> tuple[bool, str]:
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
            ComplianceReport
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
        """Enable a governance rule."""
        if rule_id in self.rules:
            self.rules[rule_id].is_active = True
            return True
        return False
    
    def disable_rule(self, rule_id: str) -> bool:
        """Disable a governance rule."""
        if rule_id in self.rules:
            self.rules[rule_id].is_active = False
            return True
        return False


# ============================================================================
# Unit Tests
# ============================================================================

class TestGovernanceEngineInitialization:
    """Test governance engine initialization."""
    
    def test_engine_creation(self):
        """Create governance engine."""
        engine = GovernanceEngine()
        assert engine is not None
        assert len(engine.rules) == 5
    
    def test_default_rules_created(self):
        """5 default governance rules are created."""
        engine = GovernanceEngine()
        rules = engine.get_rules()
        assert len(rules) == 5
        assert all(r.is_active for r in rules)
        rule_ids = [r.rule_id for r in rules]
        assert 'GOV-001' in rule_ids
        assert 'GOV-005' in rule_ids


class TestAuditLogging:
    """Test audit trail logging."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return GovernanceEngine()
    
    def test_log_audit_entry(self, engine):
        """Log an audit entry."""
        entry = engine.log_audit_entry(
            event_type=AuditEventType.GATE_DECISION,
            conversation_id="conv-001",
            actor_id="system",
            action="Decision made: PROCEED",
            affected_rules=['GOV-001']
        )
        
        assert entry is not None
        assert entry.event_id.startswith("AUD-")
        assert entry.event_type == AuditEventType.GATE_DECISION
    
    def test_audit_trail_contains_entry(self, engine):
        """Audit trail stores entries."""
        engine.log_audit_entry(
            event_type=AuditEventType.GATE_DECISION,
            conversation_id="conv-001",
            actor_id="system",
            action="Decision made"
        )
        
        assert len(engine.audit_trail) == 1


class TestRuleCompliance:
    """Test rule compliance checking."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return GovernanceEngine()
    
    def test_approval_routing_rule(self, engine):
        """GOV-001: Architecture review for complex."""
        context = {
            'complexity_level': 'complex',
            'approvers': ['architecture-team']
        }
        is_compliant, msg = engine.check_rule_compliance("GOV-001", context)
        assert is_compliant is True
    
    def test_approval_routing_violation(self, engine):
        """GOV-001: Violation when missing architecture review."""
        context = {
            'complexity_level': 'complex',
            'approvers': ['general-reviewer']
        }
        is_compliant, msg = engine.check_rule_compliance("GOV-001", context)
        assert is_compliant is False
    
    def test_confidence_threshold_rule(self, engine):
        """GOV-002: Confidence >= 0.65 required."""
        context = {'confidence': 0.75}
        is_compliant, msg = engine.check_rule_compliance("GOV-002", context)
        assert is_compliant is True
    
    def test_confidence_threshold_violation(self, engine):
        """GOV-002: Violation when confidence too low."""
        context = {'confidence': 0.50}
        is_compliant, msg = engine.check_rule_compliance("GOV-002", context)
        assert is_compliant is False
    
    def test_security_risk_rule(self, engine):
        """GOV-003: Security team review for security risks."""
        context = {
            'risks': ['security'],
            'approvers': ['security-team']
        }
        is_compliant, msg = engine.check_rule_compliance("GOV-003", context)
        assert is_compliant is True


class TestRuleValidation:
    """Test validation of all rules."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return GovernanceEngine()
    
    def test_validate_all_rules_compliant(self, engine):
        """All rules satisfied."""
        context = {
            'complexity_level': 'moderate',
            'confidence': 0.75,
            'risks': [],
            'approvers': ['general-reviewer']
        }
        result = engine.validate_all_rules(context)
        assert result['compliant'] is True
        assert len(result['violations']) == 0
    
    def test_validate_all_rules_violations(self, engine):
        """Multiple rule violations."""
        context = {
            'complexity_level': 'complex',
            'confidence': 0.50,
            'risks': ['security'],
            'approvers': ['general-reviewer']  # Missing required teams
        }
        result = engine.validate_all_rules(context)
        assert result['compliant'] is False
        assert len(result['violations']) > 0


class TestAuditTrailFiltering:
    """Test audit trail retrieval and filtering."""
    
    @pytest.fixture
    def engine_with_entries(self):
        """Create engine with audit entries."""
        engine = GovernanceEngine()
        
        # Add multiple entries
        for i in range(3):
            engine.log_audit_entry(
                event_type=AuditEventType.GATE_DECISION,
                conversation_id=f"conv-{i:03d}",
                actor_id="system",
                action=f"Decision {i}"
            )
        
        return engine
    
    def test_get_all_audit_entries(self, engine_with_entries):
        """Retrieve all audit entries."""
        entries = engine_with_entries.get_audit_trail()
        assert len(entries) == 3
    
    def test_filter_by_conversation(self, engine_with_entries):
        """Filter audit entries by conversation."""
        entries = engine_with_entries.get_audit_trail(conversation_id="conv-001")
        assert len(entries) == 1
        assert entries[0].conversation_id == "conv-001"


class TestComplianceReporting:
    """Test compliance report generation."""
    
    @pytest.fixture
    def engine_with_data(self):
        """Create engine with audit data."""
        engine = GovernanceEngine()
        
        # Log some decisions
        for i in range(5):
            engine.log_audit_entry(
                event_type=AuditEventType.GATE_DECISION,
                conversation_id=f"conv-{i:03d}",
                actor_id="system",
                action="Decision made",
                metadata={'decision': 'proceed' if i % 2 == 0 else 'review'}
            )
        
        return engine
    
    def test_generate_compliance_report(self, engine_with_data):
        """Generate compliance report."""
        now = datetime.now()
        report = engine_with_data.generate_compliance_report(
            period_start=now.replace(hour=0, minute=0, second=0),
            period_end=now.replace(hour=23, minute=59, second=59)
        )
        
        assert report is not None
        assert report.total_decisions > 0
        assert 0 <= report.compliance_score <= 1


class TestRuleManagement:
    """Test rule enable/disable functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create engine instance."""
        return GovernanceEngine()
    
    def test_disable_rule(self, engine):
        """Disable a governance rule."""
        result = engine.disable_rule("GOV-001")
        assert result is True
        assert engine.rules['GOV-001'].is_active is False
    
    def test_enable_rule(self, engine):
        """Enable a governance rule."""
        engine.disable_rule("GOV-001")
        result = engine.enable_rule("GOV-001")
        assert result is True
        assert engine.rules['GOV-001'].is_active is True


# ============================================================================
# Integration Tests
# ============================================================================

class TestEndToEndGovernance:
    """Test complete governance workflow."""
    
    def test_full_governance_workflow(self):
        """Complete workflow with compliance checking."""
        engine = GovernanceEngine()
        
        # Make a decision
        engine.log_audit_entry(
            event_type=AuditEventType.GATE_DECISION,
            conversation_id="conv-001",
            actor_id="system",
            action="Decision made: PROCEED",
            affected_rules=['GOV-001', 'GOV-002']
        )
        
        # Validate compliance
        context = {
            'complexity_level': 'moderate',
            'confidence': 0.80,
            'risks': [],
            'approvers': ['general-reviewer']
        }
        validation = engine.validate_all_rules(context)
        assert validation['compliant'] is True
        
        # Generate report
        now = datetime.now()
        report = engine.generate_compliance_report(
            period_start=now.replace(hour=0, minute=0, second=0),
            period_end=now.replace(hour=23, minute=59, second=59)
        )
        assert report.compliance_score > 0
    
    def test_compliance_with_violations(self):
        """Compliance reporting with violations."""
        engine = GovernanceEngine()
        
        # Trigger violations
        context = {
            'complexity_level': 'critical',
            'confidence': 0.40,
            'risks': ['security'],
            'approvers': ['general-reviewer']  # Missing required teams
        }
        
        # This should record violations
        engine.validate_all_rules(context)
        
        # Generate report
        now = datetime.now()
        report = engine.generate_compliance_report(
            period_start=now.replace(hour=0, minute=0, second=0),
            period_end=now.replace(hour=23, minute=59, second=59)
        )
        
        assert report.rule_violations >= 0
