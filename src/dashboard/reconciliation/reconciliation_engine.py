"""
Reconciliation Engine - Main Orchestrator

Coordinates all reconciliation components: normalization, validation,
scoring, anomaly detection, and reporting.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import time
from datetime import datetime
from typing import Dict, Any
from src.dashboard.reconciliation.normalizers.score_normalizer import ScoreNormalizer
from src.dashboard.reconciliation.normalizers.cvss_normalizer import CVSSNormalizer
from src.dashboard.reconciliation.validators.cross_tab_validator import CrossTabValidator
from src.dashboard.reconciliation.models import (
    ReconciliationResult,
    AuditTrail,
    AuditTrailChange,
    ReconciliationMetrics
)


class ReconciliationEngine:
    """
    Main reconciliation engine orchestrator.
    
    Workflow:
    1. Normalize: Convert all scores to 0-100 scale
    2. Validate: Apply cross-tab validation rules
    3. Score: Calculate weighted overall score
    4. Detect: Find statistical anomalies
    5. Report: Generate audit trail
    
    Usage:
        engine = ReconciliationEngine()
        result = engine.reconcile(dashboard_data, repository='my-repo')
    """
    
    VERSION = "1.0.0"
    
    # Scoring weights per industry standards
    WEIGHTS = {
        'security': 0.35,       # 35% - Highest priority
        'quality': 0.25,        # 25% - Code health
        'maintainability': 0.15,  # 15% - Long-term sustainability
        'architecture': 0.15,   # 15% - Structural integrity
        'test_coverage': 0.10   # 10% - Verification confidence
    }
    
    def __init__(self):
        """Initialize reconciliation engine with all components."""
        self.score_normalizer = ScoreNormalizer()
        self.cvss_normalizer = CVSSNormalizer()
        self.cross_tab_validator = CrossTabValidator()
    
    def reconcile(
        self,
        data: Dict[str, Any],
        repository: str = "unknown"
    ) -> ReconciliationResult:
        """
        Reconcile dashboard data for accuracy and consistency.
        
        Args:
            data: Raw dashboard data from collectors
            repository: Repository name for tracking
        
        Returns:
            ReconciliationResult with reconciled data and audit trail
        """
        start_time = time.time()
        audit_changes = []
        all_violations = []
        all_anomalies = []
        
        # Phase 1: Normalize scores to 0-100 scale
        normalized_data = self._normalize_scores(data, audit_changes)
        
        # Phase 2a: Run R9 and R10 validation (don't need overall_score)
        r9_anomalies = self.cross_tab_validator.validate_architecture_security_alignment(normalized_data)
        r10_violations = self.cross_tab_validator.validate_maintainability_complexity_inverse(normalized_data)
        all_anomalies.extend(r9_anomalies)
        all_violations.extend(r10_violations)
        
        # Phase 2b: Apply R9/R10 adjustments
        adjusted_data = self._apply_violations(normalized_data, r10_violations, audit_changes)
        
        # Phase 3: Calculate weighted overall score
        overall_score = self._calculate_overall_score(adjusted_data)
        adjusted_data['overall_score'] = overall_score
        
        # Phase 4: Run R8 validation (needs overall_score)
        r8_violations = self.cross_tab_validator.validate_security_quality_correlation(adjusted_data)
        all_violations.extend(r8_violations)
        
        # Phase 5: Apply R8 adjustments if any
        if r8_violations:
            adjusted_data = self._apply_violations(adjusted_data, r8_violations, audit_changes)
        
        # Calculate execution time
        execution_time_ms = (time.time() - start_time) * 1000
        
        # Build audit trail
        audit_trail = AuditTrail(
            changes=audit_changes,
            rules_triggered=len(all_violations),
            anomalies_detected=len(all_anomalies),
            execution_time_ms=execution_time_ms
        )
        
        # Build metrics
        metrics = ReconciliationMetrics(
            total_adjustments=len(audit_changes),
            total_score_delta=sum(c.after - c.before for c in audit_changes if isinstance(c.before, (int, float)) and isinstance(c.after, (int, float))),
            rules_triggered=len(all_violations),
            violations_count=len(all_violations),
            anomalies_count=len(all_anomalies),
            confidence_average=sum(a.confidence for a in all_anomalies) / len(all_anomalies) if all_anomalies else 0.0,
            execution_time_ms=execution_time_ms
        )
        
        # Build result
        result = ReconciliationResult(
            reconciliation_timestamp=datetime.now().isoformat(),
            reconciliation_version=self.VERSION,
            repository=repository,
            execution_time_ms=execution_time_ms,
            reconciled_data=adjusted_data,
            violations=all_violations,
            anomalies=all_anomalies,
            audit_trail=audit_trail,
            metrics=metrics
        )
        
        return result
    
    def _normalize_scores(
        self,
        data: Dict[str, Any],
        audit_changes: list
    ) -> Dict[str, Any]:
        """
        Normalize all scores to 0-100 scale.
        Supports both flat ('security_score') and nested ('security': {'score': X}) formats.
        
        Args:
            data: Raw data
            audit_changes: List to append changes to
        
        Returns:
            Normalized data
        """
        normalized = data.copy()
        
        # Helper to normalize a score field
        def normalize_field(flat_key: str, nested_key: str):
            """Normalize score from either flat or nested structure"""
            if flat_key in normalized and isinstance(normalized[flat_key], (int, float)):
                original = normalized[flat_key]
                clamped = self.score_normalizer.clamp_score(original)
                if original != clamped:
                    normalized[flat_key] = clamped
                    audit_changes.append(AuditTrailChange(
                        category=nested_key,
                        field='score',
                        before=original,
                        after=clamped,
                        reason='Normalized to 0-100 range'
                    ))
            elif nested_key in normalized and isinstance(normalized[nested_key], dict):
                if 'score' in normalized[nested_key]:
                    original = normalized[nested_key]['score']
                    clamped = self.score_normalizer.clamp_score(original)
                    if original != clamped:
                        normalized[nested_key]['score'] = clamped
                        audit_changes.append(AuditTrailChange(
                            category=nested_key,
                            field='score',
                            before=original,
                            after=clamped,
                            reason='Normalized to 0-100 range'
                        ))
        
        # Normalize all component scores
        normalize_field('security_score', 'security')
        normalize_field('quality_score', 'quality')
        normalize_field('architecture_score', 'architecture')
        normalize_field('maintainability_score', 'maintainability')
        normalize_field('test_coverage', 'test_coverage')
        
        return normalized
    
    def _apply_violations(
        self,
        data: Dict[str, Any],
        violations: list,
        audit_changes: list
    ) -> Dict[str, Any]:
        """
        Apply violation adjustments to data.
        
        Args:
            data: Normalized data
            violations: List of violations to apply
            audit_changes: List to append changes to
        
        Returns:
            Adjusted data
        """
        adjusted = data.copy()
        
        for violation in violations:
            category = violation.category
            
            # Apply adjustment based on category
            if category == 'overall':
                adjusted['overall_score'] = violation.adjusted_score
            elif category in adjusted and 'score' in adjusted[category]:
                adjusted[category]['score'] = violation.adjusted_score
            
            # Record change
            audit_changes.append(AuditTrailChange(
                category=category,
                field='score',
                before=violation.original_score,
                after=violation.adjusted_score,
                reason=f"{violation.rule_id}: {violation.message}"
            ))
        
        return adjusted
    
    def _calculate_overall_score(self, data: Dict[str, Any]) -> float:
        """
        Calculate weighted overall score from component scores.
        
        Args:
            data: Dashboard data with component scores
        
        Returns:
            Weighted overall score (0-100)
        """
        weighted_sum = 0.0
        total_weight = 0.0
        
        # Helper to get score value (handles both flat 'security_score' and nested 'security': {'score': X})
        def get_score(data: Dict, flat_key: str, nested_key: str) -> float:
            """Extract score from either flat or nested structure"""
            if flat_key in data and isinstance(data[flat_key], (int, float)):
                return float(data[flat_key])
            elif nested_key in data:
                nested = data[nested_key]
                if isinstance(nested, (int, float)):
                    return float(nested)
                elif isinstance(nested, dict) and 'score' in nested:
                    return float(nested['score'])
            return 0.0
        
        # Security
        sec_score = get_score(data, 'security_score', 'security')
        if sec_score > 0:
            weighted_sum += sec_score * self.WEIGHTS['security']
            total_weight += self.WEIGHTS['security']
        
        # Quality
        qual_score = get_score(data, 'quality_score', 'quality')
        if qual_score > 0:
            weighted_sum += qual_score * self.WEIGHTS['quality']
            total_weight += self.WEIGHTS['quality']
        
        # Maintainability
        maint_score = get_score(data, 'maintainability_score', 'maintainability')
        if maint_score > 0:
            weighted_sum += maint_score * self.WEIGHTS['maintainability']
            total_weight += self.WEIGHTS['maintainability']
        
        # Architecture
        arch_score = get_score(data, 'architecture_score', 'architecture')
        if arch_score > 0:
            weighted_sum += arch_score * self.WEIGHTS['architecture']
            total_weight += self.WEIGHTS['architecture']
        
        # Test coverage
        test_score = get_score(data, 'test_coverage', 'test_coverage')
        if test_score > 0:
            weighted_sum += test_score * self.WEIGHTS['test_coverage']
            total_weight += self.WEIGHTS['test_coverage']
        
        # Calculate weighted average
        if total_weight > 0:
            overall = weighted_sum / total_weight
        else:
            overall = 0.0
        
        return round(overall, 1)

