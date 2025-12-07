"""
Reconciliation Engine Models

Data structures for reconciliation results, violations, and anomalies.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional
from datetime import datetime


@dataclass
class Violation:
    """
    Represents a validation rule violation.
    
    Attributes:
        rule_id: Unique rule identifier (e.g., 'R1_CRITICAL_VULN_CAP')
        severity: Violation severity ('blocker', 'critical', 'high', 'medium', 'low')
        category: Affected category ('security', 'quality', 'overall', etc.)
        message: Human-readable violation description
        original_score: Score before adjustment
        adjusted_score: Score after applying rule
        adjustment: Delta between original and adjusted (-15 means reduced by 15)
        rationale: Explanation of why rule was triggered
    """
    rule_id: str
    severity: str
    category: str
    message: str
    original_score: float
    adjusted_score: float
    adjustment: float
    rationale: str


@dataclass
class Anomaly:
    """
    Represents a detected data anomaly or inconsistency.
    
    Attributes:
        type: Anomaly type ('score_inconsistency', 'outlier', 'trend_deviation', etc.)
        confidence: Confidence score (0.0-1.0) that this is a true anomaly
        category: Affected category or cross-category relationship
        message: Human-readable anomaly description
        recommendation: Suggested action to investigate or resolve
        z_score: Statistical z-score if applicable (optional)
        metadata: Additional context data
    """
    type: str
    confidence: float
    category: str
    message: str
    recommendation: str
    z_score: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AuditTrailChange:
    """
    Records a single score change in the audit trail.
    
    Attributes:
        category: Category affected ('security', 'quality', 'overall', etc.)
        field: Specific field changed ('score', 'vulnerability_count', etc.)
        before: Value before reconciliation
        after: Value after reconciliation
        reason: Rule or process that caused the change
        timestamp: When change occurred
    """
    category: str
    field: str
    before: Any
    after: Any
    reason: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AuditTrail:
    """
    Complete audit trail of all reconciliation changes.
    
    Attributes:
        changes: List of all changes made during reconciliation
        rules_triggered: Number of validation rules triggered
        anomalies_detected: Number of anomalies found
        execution_time_ms: Total reconciliation execution time
    """
    changes: List[AuditTrailChange]
    rules_triggered: int
    anomalies_detected: int
    execution_time_ms: float


@dataclass
class ReconciliationMetrics:
    """
    Summary metrics for reconciliation execution.
    
    Attributes:
        total_adjustments: Total number of score adjustments made
        total_score_delta: Sum of all score changes (can be negative)
        rules_triggered: Number of validation rules that fired
        violations_count: Number of violations found
        anomalies_count: Number of anomalies detected
        confidence_average: Average confidence of anomalies (0.0-1.0)
        execution_time_ms: Time taken to run reconciliation
    """
    total_adjustments: int
    total_score_delta: float
    rules_triggered: int
    violations_count: int
    anomalies_count: int
    confidence_average: float
    execution_time_ms: float


@dataclass
class ReconciliationResult:
    """
    Complete result of dashboard data reconciliation.
    
    This is the primary output structure containing reconciled scores,
    violations, anomalies, audit trail, and metrics.
    
    Attributes:
        reconciliation_timestamp: ISO timestamp when reconciliation ran
        reconciliation_version: Version of reconciliation engine
        repository: Repository name being analyzed
        execution_time_ms: Total execution time
        reconciled_data: All dashboard data with adjusted scores
        violations: List of validation rule violations
        anomalies: List of detected anomalies
        audit_trail: Complete change tracking
        metrics: Summary metrics
    """
    reconciliation_timestamp: str
    reconciliation_version: str
    repository: str
    execution_time_ms: float
    reconciled_data: Dict[str, Any]
    violations: List[Violation]
    anomalies: List[Anomaly]
    audit_trail: AuditTrail
    metrics: ReconciliationMetrics
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'reconciliation_timestamp': self.reconciliation_timestamp,
            'reconciliation_version': self.reconciliation_version,
            'repository': self.repository,
            'execution_time_ms': self.execution_time_ms,
            'reconciled_data': self.reconciled_data,
            'violations': [
                {
                    'rule_id': v.rule_id,
                    'severity': v.severity,
                    'category': v.category,
                    'message': v.message,
                    'original_score': v.original_score,
                    'adjusted_score': v.adjusted_score,
                    'adjustment': v.adjustment,
                    'rationale': v.rationale
                }
                for v in self.violations
            ],
            'anomalies': [
                {
                    'type': a.type,
                    'confidence': a.confidence,
                    'category': a.category,
                    'message': a.message,
                    'recommendation': a.recommendation,
                    'z_score': a.z_score,
                    'metadata': a.metadata
                }
                for a in self.anomalies
            ],
            'audit_trail': {
                'changes': [
                    {
                        'category': c.category,
                        'field': c.field,
                        'before': c.before,
                        'after': c.after,
                        'reason': c.reason,
                        'timestamp': c.timestamp
                    }
                    for c in self.audit_trail.changes
                ],
                'rules_triggered': self.audit_trail.rules_triggered,
                'anomalies_detected': self.audit_trail.anomalies_detected,
                'execution_time_ms': self.audit_trail.execution_time_ms
            },
            'metrics': {
                'total_adjustments': self.metrics.total_adjustments,
                'total_score_delta': self.metrics.total_score_delta,
                'rules_triggered': self.metrics.rules_triggered,
                'violations_count': self.metrics.violations_count,
                'anomalies_count': self.metrics.anomalies_count,
                'confidence_average': self.metrics.confidence_average,
                'execution_time_ms': self.metrics.execution_time_ms
            }
        }
