"""
CORTEX Incident Response Automation

Purpose: Automated security incident detection, classification,
         containment procedures, and AI-assisted response.

Version: 1.0.0
Author: CORTEX Development Team
Created: December 30, 2025
Status: Phase 5 Security Enhancement

Features:
- Automated incident detection
- Severity classification (CVSS-based)
- Containment playbooks
- AI-assisted analysis
- Escalation workflows
- Post-incident reporting
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import json
import hashlib
import re

logger = logging.getLogger(__name__)


class IncidentSeverity(Enum):
    """Incident severity levels aligned with NIST."""
    CRITICAL = "CRITICAL"  # Immediate action required
    HIGH = "HIGH"          # Response within 1 hour
    MEDIUM = "MEDIUM"      # Response within 4 hours
    LOW = "LOW"            # Response within 24 hours
    INFORMATIONAL = "INFO" # No immediate action needed


class IncidentStatus(Enum):
    """Incident lifecycle status."""
    DETECTED = "detected"
    TRIAGED = "triaged"
    INVESTIGATING = "investigating"
    CONTAINING = "containing"
    ERADICATING = "eradicating"
    RECOVERING = "recovering"
    CLOSED = "closed"


class IncidentCategory(Enum):
    """NIST incident categories."""
    UNAUTHORIZED_ACCESS = "unauthorized_access"
    MALWARE = "malware"
    DATA_BREACH = "data_breach"
    DOS_ATTACK = "dos_attack"
    INSIDER_THREAT = "insider_threat"
    PHISHING = "phishing"
    SUPPLY_CHAIN = "supply_chain"
    MISCONFIGURATION = "misconfiguration"
    CREDENTIAL_COMPROMISE = "credential_compromise"
    VULNERABILITY_EXPLOIT = "vulnerability_exploit"


@dataclass
class IncidentIndicator:
    """Indicator of Compromise (IOC)."""
    indicator_type: str  # ip, domain, hash, email, url, file_path
    value: str
    confidence: float  # 0.0 - 1.0
    first_seen: str
    last_seen: str
    context: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class IncidentTimelineEvent:
    """Event in incident timeline."""
    timestamp: str
    event_type: str
    description: str
    actor: str  # system, analyst, automation
    evidence: List[str] = field(default_factory=list)


@dataclass
class SecurityIncident:
    """Security incident record."""
    incident_id: str
    title: str
    description: str
    severity: IncidentSeverity
    category: IncidentCategory
    status: IncidentStatus
    created_at: str
    updated_at: str
    indicators: List[IncidentIndicator] = field(default_factory=list)
    affected_systems: List[str] = field(default_factory=list)
    affected_users: List[str] = field(default_factory=list)
    timeline: List[IncidentTimelineEvent] = field(default_factory=list)
    containment_actions: List[str] = field(default_factory=list)
    root_cause: Optional[str] = None
    remediation_steps: List[str] = field(default_factory=list)
    lessons_learned: Optional[str] = None
    assigned_to: Optional[str] = None
    escalated: bool = False


@dataclass
class ContainmentPlaybook:
    """Automated containment playbook."""
    playbook_id: str
    name: str
    description: str
    category: IncidentCategory
    severity_threshold: IncidentSeverity
    automated: bool
    steps: List[Dict[str, Any]]
    rollback_steps: List[Dict[str, Any]]
    approval_required: bool = True


class IncidentResponseAutomation:
    """
    Automated incident response system for CORTEX.
    
    Provides:
    - Pattern-based incident detection
    - Severity classification
    - Automated containment playbooks
    - AI-assisted analysis
    - Escalation management
    - Post-incident reporting
    """
    
    # Detection patterns
    DETECTION_PATTERNS = {
        'brute_force': {
            'pattern': r'failed login.*(\d+) attempts',
            'threshold': 5,
            'category': IncidentCategory.UNAUTHORIZED_ACCESS,
            'severity': IncidentSeverity.MEDIUM
        },
        'sql_injection': {
            'pattern': r"(union\s+select|or\s+1\s*=\s*1|'\s*or\s*'|drop\s+table)",
            'category': IncidentCategory.VULNERABILITY_EXPLOIT,
            'severity': IncidentSeverity.HIGH
        },
        'data_exfiltration': {
            'pattern': r'(large\s+download|bulk\s+export|unusual\s+data\s+transfer)',
            'category': IncidentCategory.DATA_BREACH,
            'severity': IncidentSeverity.CRITICAL
        },
        'privilege_escalation': {
            'pattern': r'(sudo|admin|privilege).*escalat',
            'category': IncidentCategory.UNAUTHORIZED_ACCESS,
            'severity': IncidentSeverity.HIGH
        },
        'suspicious_process': {
            'pattern': r'(nc\s+-|netcat|reverse\s+shell|powershell.*encoded)',
            'category': IncidentCategory.MALWARE,
            'severity': IncidentSeverity.CRITICAL
        },
        'credential_dump': {
            'pattern': r'(mimikatz|credential\s+dump|password\s+spray)',
            'category': IncidentCategory.CREDENTIAL_COMPROMISE,
            'severity': IncidentSeverity.CRITICAL
        },
    }
    
    # Response time SLAs
    RESPONSE_SLA = {
        IncidentSeverity.CRITICAL: timedelta(minutes=15),
        IncidentSeverity.HIGH: timedelta(hours=1),
        IncidentSeverity.MEDIUM: timedelta(hours=4),
        IncidentSeverity.LOW: timedelta(hours=24),
        IncidentSeverity.INFORMATIONAL: timedelta(days=7),
    }
    
    def __init__(
        self,
        incident_store: Optional[Path] = None,
        playbook_store: Optional[Path] = None,
        notification_handler: Optional[Callable] = None
    ):
        """Initialize incident response system."""
        self.incident_store = incident_store or Path('cortex-brain/incidents')
        self.playbook_store = playbook_store or Path('cortex-brain/playbooks')
        self.notification_handler = notification_handler
        self.incidents: Dict[str, SecurityIncident] = {}
        self.playbooks: Dict[str, ContainmentPlaybook] = {}
        
        self._load_playbooks()
        self._load_incidents()
        logger.info("🚨 Incident Response Automation initialized")
    
    def _load_playbooks(self):
        """Load containment playbooks from storage."""
        self.playbooks = self._get_default_playbooks()
        
        playbook_file = self.playbook_store / 'playbooks.json'
        if playbook_file.exists():
            try:
                data = json.loads(playbook_file.read_text())
                # Merge with defaults
                for pb_id, pb_data in data.items():
                    self.playbooks[pb_id] = ContainmentPlaybook(**pb_data)
            except Exception as e:
                logger.warning(f"Could not load playbooks: {e}")
    
    def _load_incidents(self):
        """Load existing incidents from storage."""
        incident_file = self.incident_store / 'incidents.json'
        if incident_file.exists():
            try:
                data = json.loads(incident_file.read_text())
                for inc_id, inc_data in data.items():
                    # Reconstruct enums
                    inc_data['severity'] = IncidentSeverity(inc_data['severity'])
                    inc_data['category'] = IncidentCategory(inc_data['category'])
                    inc_data['status'] = IncidentStatus(inc_data['status'])
                    self.incidents[inc_id] = SecurityIncident(**inc_data)
            except Exception as e:
                logger.warning(f"Could not load incidents: {e}")
    
    def _save_incidents(self):
        """Persist incidents to storage."""
        self.incident_store.mkdir(parents=True, exist_ok=True)
        
        data = {}
        for inc_id, incident in self.incidents.items():
            inc_dict = {
                'incident_id': incident.incident_id,
                'title': incident.title,
                'description': incident.description,
                'severity': incident.severity.value,
                'category': incident.category.value,
                'status': incident.status.value,
                'created_at': incident.created_at,
                'updated_at': incident.updated_at,
                'indicators': [vars(i) for i in incident.indicators],
                'affected_systems': incident.affected_systems,
                'affected_users': incident.affected_users,
                'timeline': [vars(e) for e in incident.timeline],
                'containment_actions': incident.containment_actions,
                'root_cause': incident.root_cause,
                'remediation_steps': incident.remediation_steps,
                'lessons_learned': incident.lessons_learned,
                'assigned_to': incident.assigned_to,
                'escalated': incident.escalated,
            }
            data[inc_id] = inc_dict
        
        incident_file = self.incident_store / 'incidents.json'
        incident_file.write_text(json.dumps(data, indent=2))
    
    def _get_default_playbooks(self) -> Dict[str, ContainmentPlaybook]:
        """Get default containment playbooks."""
        return {
            'pb-brute-force': ContainmentPlaybook(
                playbook_id='pb-brute-force',
                name='Brute Force Containment',
                description='Automated response to brute force attacks',
                category=IncidentCategory.UNAUTHORIZED_ACCESS,
                severity_threshold=IncidentSeverity.MEDIUM,
                automated=True,
                approval_required=False,
                steps=[
                    {'action': 'block_ip', 'duration': '24h'},
                    {'action': 'lock_account', 'duration': '1h'},
                    {'action': 'notify_user', 'template': 'account_locked'},
                    {'action': 'log_event', 'severity': 'HIGH'},
                ],
                rollback_steps=[
                    {'action': 'unblock_ip'},
                    {'action': 'unlock_account'},
                    {'action': 'notify_user', 'template': 'account_restored'},
                ]
            ),
            'pb-sql-injection': ContainmentPlaybook(
                playbook_id='pb-sql-injection',
                name='SQL Injection Response',
                description='Response to detected SQL injection attempts',
                category=IncidentCategory.VULNERABILITY_EXPLOIT,
                severity_threshold=IncidentSeverity.HIGH,
                automated=True,
                approval_required=True,
                steps=[
                    {'action': 'block_ip', 'duration': 'permanent'},
                    {'action': 'capture_payload', 'store': True},
                    {'action': 'waf_rule', 'rule_type': 'block_pattern'},
                    {'action': 'notify_security_team'},
                    {'action': 'create_ticket', 'priority': 'high'},
                ],
                rollback_steps=[
                    {'action': 'review_block'},
                    {'action': 'unblock_ip_if_false_positive'},
                ]
            ),
            'pb-data-exfiltration': ContainmentPlaybook(
                playbook_id='pb-data-exfiltration',
                name='Data Exfiltration Response',
                description='Critical response to potential data breach',
                category=IncidentCategory.DATA_BREACH,
                severity_threshold=IncidentSeverity.CRITICAL,
                automated=False,  # Requires manual approval
                approval_required=True,
                steps=[
                    {'action': 'suspend_user_session'},
                    {'action': 'block_egress', 'target': 'affected_systems'},
                    {'action': 'capture_network_traffic', 'duration': '1h'},
                    {'action': 'preserve_evidence'},
                    {'action': 'notify_security_team', 'escalate': True},
                    {'action': 'notify_management'},
                    {'action': 'legal_hold_if_required'},
                ],
                rollback_steps=[
                    {'action': 'restore_network_access'},
                    {'action': 'restore_user_session'},
                ]
            ),
            'pb-credential-compromise': ContainmentPlaybook(
                playbook_id='pb-credential-compromise',
                name='Credential Compromise Response',
                description='Response to compromised credentials',
                category=IncidentCategory.CREDENTIAL_COMPROMISE,
                severity_threshold=IncidentSeverity.HIGH,
                automated=True,
                approval_required=False,
                steps=[
                    {'action': 'force_password_reset'},
                    {'action': 'revoke_all_sessions'},
                    {'action': 'revoke_api_keys'},
                    {'action': 'enable_mfa_if_not_set'},
                    {'action': 'notify_user', 'template': 'credential_reset'},
                    {'action': 'audit_recent_activity', 'days': 30},
                ],
                rollback_steps=[]  # No rollback for credential reset
            ),
        }
    
    def _generate_incident_id(self) -> str:
        """Generate unique incident ID."""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        hash_suffix = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:6]
        return f"INC-{timestamp}-{hash_suffix}"
    
    def detect_incident(
        self,
        log_entry: str,
        source: str = "unknown"
    ) -> Optional[SecurityIncident]:
        """
        Detect potential incident from log entry.
        
        Args:
            log_entry: Log line or event to analyze
            source: Source system of the log
            
        Returns:
            SecurityIncident if detected, None otherwise
        """
        for pattern_name, pattern_config in self.DETECTION_PATTERNS.items():
            if re.search(pattern_config['pattern'], log_entry, re.IGNORECASE):
                # Check threshold if applicable
                if 'threshold' in pattern_config:
                    match = re.search(r'(\d+)', log_entry)
                    if match:
                        count = int(match.group(1))
                        if count < pattern_config['threshold']:
                            continue
                
                # Create incident
                incident = self.create_incident(
                    title=f"Detected: {pattern_name.replace('_', ' ').title()}",
                    description=f"Automated detection triggered by pattern match.\n\nLog entry: {log_entry[:500]}",
                    severity=pattern_config['severity'],
                    category=pattern_config['category'],
                    affected_systems=[source],
                    indicators=[
                        IncidentIndicator(
                            indicator_type='pattern_match',
                            value=pattern_name,
                            confidence=0.8,
                            first_seen=datetime.now().isoformat(),
                            last_seen=datetime.now().isoformat(),
                            context=log_entry[:200]
                        )
                    ]
                )
                
                return incident
        
        return None
    
    def create_incident(
        self,
        title: str,
        description: str,
        severity: IncidentSeverity,
        category: IncidentCategory,
        affected_systems: Optional[List[str]] = None,
        affected_users: Optional[List[str]] = None,
        indicators: Optional[List[IncidentIndicator]] = None
    ) -> SecurityIncident:
        """
        Create new security incident.
        
        Args:
            title: Incident title
            description: Detailed description
            severity: Incident severity level
            category: Incident category
            affected_systems: List of affected system names
            affected_users: List of affected usernames
            indicators: Initial IOCs
            
        Returns:
            Created SecurityIncident
        """
        now = datetime.now().isoformat()
        incident_id = self._generate_incident_id()
        
        incident = SecurityIncident(
            incident_id=incident_id,
            title=title,
            description=description,
            severity=severity,
            category=category,
            status=IncidentStatus.DETECTED,
            created_at=now,
            updated_at=now,
            affected_systems=affected_systems or [],
            affected_users=affected_users or [],
            indicators=indicators or [],
            timeline=[
                IncidentTimelineEvent(
                    timestamp=now,
                    event_type='created',
                    description='Incident created',
                    actor='system'
                )
            ]
        )
        
        self.incidents[incident_id] = incident
        self._save_incidents()
        
        # Trigger notification
        if self.notification_handler:
            self.notification_handler(incident, 'created')
        
        # Auto-triage
        self._auto_triage(incident)
        
        logger.info(f"🚨 Incident created: {incident_id} - {title}")
        return incident
    
    def _auto_triage(self, incident: SecurityIncident):
        """Perform automatic incident triage."""
        # Update status
        incident.status = IncidentStatus.TRIAGED
        incident.updated_at = datetime.now().isoformat()
        
        # Add triage event
        incident.timeline.append(
            IncidentTimelineEvent(
                timestamp=datetime.now().isoformat(),
                event_type='triaged',
                description=f'Auto-triaged. Severity: {incident.severity.value}. Category: {incident.category.value}',
                actor='automation'
            )
        )
        
        # Check for applicable playbook
        for pb in self.playbooks.values():
            if (pb.category == incident.category and 
                self._severity_meets_threshold(incident.severity, pb.severity_threshold)):
                
                if pb.automated and not pb.approval_required:
                    self._execute_playbook(incident, pb)
                else:
                    incident.timeline.append(
                        IncidentTimelineEvent(
                            timestamp=datetime.now().isoformat(),
                            event_type='playbook_suggested',
                            description=f'Playbook "{pb.name}" recommended - awaiting approval',
                            actor='automation'
                        )
                    )
                break
        
        self._save_incidents()
    
    def _severity_meets_threshold(
        self,
        incident_severity: IncidentSeverity,
        threshold: IncidentSeverity
    ) -> bool:
        """Check if incident severity meets playbook threshold."""
        severity_order = [
            IncidentSeverity.INFORMATIONAL,
            IncidentSeverity.LOW,
            IncidentSeverity.MEDIUM,
            IncidentSeverity.HIGH,
            IncidentSeverity.CRITICAL
        ]
        return severity_order.index(incident_severity) >= severity_order.index(threshold)
    
    def _execute_playbook(
        self,
        incident: SecurityIncident,
        playbook: ContainmentPlaybook
    ):
        """Execute containment playbook."""
        incident.status = IncidentStatus.CONTAINING
        incident.timeline.append(
            IncidentTimelineEvent(
                timestamp=datetime.now().isoformat(),
                event_type='playbook_started',
                description=f'Executing playbook: {playbook.name}',
                actor='automation'
            )
        )
        
        for step in playbook.steps:
            action = step.get('action', 'unknown')
            
            # Simulate action execution
            # In production, this would call actual security tools
            incident.containment_actions.append(
                f"[SIMULATED] {action}: {json.dumps(step)}"
            )
            
            incident.timeline.append(
                IncidentTimelineEvent(
                    timestamp=datetime.now().isoformat(),
                    event_type='action_executed',
                    description=f'Action: {action}',
                    actor='automation',
                    evidence=[json.dumps(step)]
                )
            )
        
        incident.timeline.append(
            IncidentTimelineEvent(
                timestamp=datetime.now().isoformat(),
                event_type='playbook_completed',
                description=f'Playbook "{playbook.name}" execution completed',
                actor='automation'
            )
        )
        
        incident.updated_at = datetime.now().isoformat()
        self._save_incidents()
    
    def update_incident(
        self,
        incident_id: str,
        status: Optional[IncidentStatus] = None,
        description: Optional[str] = None,
        root_cause: Optional[str] = None,
        remediation_steps: Optional[List[str]] = None,
        lessons_learned: Optional[str] = None,
        assigned_to: Optional[str] = None
    ) -> Optional[SecurityIncident]:
        """Update existing incident."""
        if incident_id not in self.incidents:
            return None
        
        incident = self.incidents[incident_id]
        
        if status:
            incident.status = status
            incident.timeline.append(
                IncidentTimelineEvent(
                    timestamp=datetime.now().isoformat(),
                    event_type='status_changed',
                    description=f'Status changed to: {status.value}',
                    actor='analyst'
                )
            )
        
        if description:
            incident.description = description
        if root_cause:
            incident.root_cause = root_cause
        if remediation_steps:
            incident.remediation_steps = remediation_steps
        if lessons_learned:
            incident.lessons_learned = lessons_learned
        if assigned_to:
            incident.assigned_to = assigned_to
        
        incident.updated_at = datetime.now().isoformat()
        self._save_incidents()
        
        return incident
    
    def close_incident(
        self,
        incident_id: str,
        root_cause: str,
        lessons_learned: str
    ) -> Optional[SecurityIncident]:
        """Close incident with post-mortem."""
        if incident_id not in self.incidents:
            return None
        
        incident = self.incidents[incident_id]
        incident.status = IncidentStatus.CLOSED
        incident.root_cause = root_cause
        incident.lessons_learned = lessons_learned
        incident.updated_at = datetime.now().isoformat()
        
        incident.timeline.append(
            IncidentTimelineEvent(
                timestamp=datetime.now().isoformat(),
                event_type='closed',
                description='Incident closed',
                actor='analyst',
                evidence=[f'Root cause: {root_cause}']
            )
        )
        
        self._save_incidents()
        logger.info(f"✅ Incident closed: {incident_id}")
        
        return incident
    
    def escalate_incident(
        self,
        incident_id: str,
        reason: str
    ) -> Optional[SecurityIncident]:
        """Escalate incident to higher tier."""
        if incident_id not in self.incidents:
            return None
        
        incident = self.incidents[incident_id]
        incident.escalated = True
        
        # Upgrade severity if not already critical
        if incident.severity != IncidentSeverity.CRITICAL:
            severity_order = [
                IncidentSeverity.INFORMATIONAL,
                IncidentSeverity.LOW,
                IncidentSeverity.MEDIUM,
                IncidentSeverity.HIGH,
                IncidentSeverity.CRITICAL
            ]
            current_index = severity_order.index(incident.severity)
            incident.severity = severity_order[min(current_index + 1, len(severity_order) - 1)]
        
        incident.timeline.append(
            IncidentTimelineEvent(
                timestamp=datetime.now().isoformat(),
                event_type='escalated',
                description=f'Incident escalated. Reason: {reason}',
                actor='analyst'
            )
        )
        
        incident.updated_at = datetime.now().isoformat()
        self._save_incidents()
        
        # Trigger escalation notification
        if self.notification_handler:
            self.notification_handler(incident, 'escalated')
        
        return incident
    
    def add_indicator(
        self,
        incident_id: str,
        indicator: IncidentIndicator
    ) -> Optional[SecurityIncident]:
        """Add indicator of compromise to incident."""
        if incident_id not in self.incidents:
            return None
        
        incident = self.incidents[incident_id]
        incident.indicators.append(indicator)
        
        incident.timeline.append(
            IncidentTimelineEvent(
                timestamp=datetime.now().isoformat(),
                event_type='indicator_added',
                description=f'IOC added: {indicator.indicator_type} = {indicator.value[:50]}',
                actor='analyst'
            )
        )
        
        incident.updated_at = datetime.now().isoformat()
        self._save_incidents()
        
        return incident
    
    def get_incident(self, incident_id: str) -> Optional[SecurityIncident]:
        """Get incident by ID."""
        return self.incidents.get(incident_id)
    
    def list_incidents(
        self,
        status: Optional[IncidentStatus] = None,
        severity: Optional[IncidentSeverity] = None,
        category: Optional[IncidentCategory] = None,
        limit: int = 50
    ) -> List[SecurityIncident]:
        """List incidents with optional filters."""
        incidents = list(self.incidents.values())
        
        if status:
            incidents = [i for i in incidents if i.status == status]
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        if category:
            incidents = [i for i in incidents if i.category == category]
        
        # Sort by created_at descending
        incidents.sort(key=lambda x: x.created_at, reverse=True)
        
        return incidents[:limit]
    
    def get_incident_metrics(self) -> Dict[str, Any]:
        """Get incident metrics summary."""
        total = len(self.incidents)
        
        by_status = {}
        by_severity = {}
        by_category = {}
        
        for incident in self.incidents.values():
            by_status[incident.status.value] = by_status.get(incident.status.value, 0) + 1
            by_severity[incident.severity.value] = by_severity.get(incident.severity.value, 0) + 1
            by_category[incident.category.value] = by_category.get(incident.category.value, 0) + 1
        
        open_incidents = sum(1 for i in self.incidents.values() 
                           if i.status not in [IncidentStatus.CLOSED])
        
        return {
            'total_incidents': total,
            'open_incidents': open_incidents,
            'closed_incidents': total - open_incidents,
            'by_status': by_status,
            'by_severity': by_severity,
            'by_category': by_category,
            'escalated_count': sum(1 for i in self.incidents.values() if i.escalated),
        }
    
    def generate_incident_report(
        self,
        incident_id: str
    ) -> str:
        """Generate incident report."""
        incident = self.get_incident(incident_id)
        if not incident:
            return "Incident not found"
        
        report = f"""
# Incident Report: {incident.incident_id}

## Summary
- **Title:** {incident.title}
- **Severity:** {incident.severity.value}
- **Category:** {incident.category.value}
- **Status:** {incident.status.value}
- **Created:** {incident.created_at}
- **Updated:** {incident.updated_at}
- **Assigned To:** {incident.assigned_to or 'Unassigned'}
- **Escalated:** {'Yes' if incident.escalated else 'No'}

## Description
{incident.description}

## Affected Systems
{chr(10).join('- ' + s for s in incident.affected_systems) or 'None identified'}

## Affected Users
{chr(10).join('- ' + u for u in incident.affected_users) or 'None identified'}

## Indicators of Compromise (IOCs)
{chr(10).join(f'- [{i.indicator_type}] {i.value} (confidence: {i.confidence})' for i in incident.indicators) or 'None recorded'}

## Timeline
{chr(10).join(f'- {e.timestamp}: [{e.event_type}] {e.description} (by {e.actor})' for e in incident.timeline)}

## Containment Actions
{chr(10).join('- ' + a for a in incident.containment_actions) or 'None taken'}

## Root Cause
{incident.root_cause or 'Not yet determined'}

## Remediation Steps
{chr(10).join(f'{i+1}. {s}' for i, s in enumerate(incident.remediation_steps)) or 'None documented'}

## Lessons Learned
{incident.lessons_learned or 'Post-incident review pending'}

---
*Report generated: {datetime.now().isoformat()}*
"""
        
        return report


# CLI Interface
if __name__ == "__main__":
    ira = IncidentResponseAutomation()
    
    # Demo: Detect incident from log
    test_log = "Alert: 25 failed login attempts detected from IP 192.168.1.100"
    incident = ira.detect_incident(test_log, source="auth-server-01")
    
    if incident:
        print(f"Incident detected: {incident.incident_id}")
        print(ira.generate_incident_report(incident.incident_id))
