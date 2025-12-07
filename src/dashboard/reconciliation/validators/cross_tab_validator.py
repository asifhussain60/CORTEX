"""
Cross-Tab Validator

Validates consistency and correlations across different dashboard tabs/categories.
Detects logical inconsistencies like high architecture score with low security.

Rules:
- R8: Security-Quality Correlation
- R9: Architecture-Security Alignment  
- R10: Maintainability-Complexity Inverse

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Dict, Any, List, Tuple
from src.dashboard.reconciliation.models import Violation, Anomaly


class CrossTabValidator:
    """
    Validates cross-tab relationships and correlations.
    
    Detects inconsistencies where metrics should correlate but don't,
    indicating potential data quality issues or real system problems.
    Supports both flat and nested data formats.
    
    Usage:
        validator = CrossTabValidator()
        violations, anomalies = validator.validate_all(dashboard_data)
    """
    
    @staticmethod
    def _get_score(data: Dict[str, Any], flat_key: str, nested_key: str, default: float = 0.0) -> float:
        """
        Extract score from either flat or nested structure.
        
        Args:
            data: Dictionary with score data
            flat_key: Key for flat structure (e.g., 'security_score')
            nested_key: Key for nested structure (e.g., 'security')
            default: Default value if not found
        
        Returns:
            Score value (0-100)
        """
        # Try flat structure first
        if flat_key in data and isinstance(data[flat_key], (int, float)):
            return float(data[flat_key])
        
        # Try nested structure
        if nested_key in data:
            nested = data[nested_key]
            if isinstance(nested, (int, float)):
                return float(nested)
            elif isinstance(nested, dict) and 'score' in nested:
                return float(nested['score'])
        
        return default
    
    def validate_security_quality_correlation(self, data: Dict[str, Any]) -> List[Violation]:
        """
        R8: Security-Quality Correlation
        
        If BOTH security AND quality are below 50, overall score cannot exceed 50.
        This prevents high overall scores when both fundamental aspects are weak.
        
        Args:
            data: Dashboard data with security, quality, and overall_score
        
        Returns:
            List of violations (empty if passes)
        """
        violations = []
        
        security_score = self._get_score(data, 'security_score', 'security', default=100)
        quality_score = self._get_score(data, 'quality_score', 'quality', default=100)
        overall_score = data.get('overall_score', 0)
        
        # Check if both are low
        if security_score < 50 and quality_score < 50:
            # Cap overall score at 50
            if overall_score > 50:
                violations.append(Violation(
                    rule_id='R8',
                    severity='high',
                    category='overall',
                    message=f'Both security ({security_score}) and quality ({quality_score}) are below 50',
                    original_score=overall_score,
                    adjusted_score=50.0,
                    adjustment=50.0 - overall_score,
                    rationale='When both security and quality are weak, system is at significant risk'
                ))
        
        return violations
    
    def validate_architecture_security_alignment(self, data: Dict[str, Any]) -> List[Anomaly]:
        """
        R9: Architecture-Security Alignment
        
        High architecture score (>80) with low security score (<40) is anomalous.
        Good architecture should include security design patterns.
        
        Args:
            data: Dashboard data with architecture and security scores
        
        Returns:
            List of anomalies (empty if aligned)
        """
        anomalies = []
        
        architecture_score = self._get_score(data, 'architecture_score', 'architecture', default=0)
        security_score = self._get_score(data, 'security_score', 'security', default=100)
        
        # Check for misalignment
        if architecture_score > 80 and security_score < 40:
            # Confidence based on gap size (larger gap = higher confidence)
            gap = architecture_score - security_score
            confidence = min(0.95, 0.5 + (gap / 100.0))
            
            anomalies.append(Anomaly(
                type='score_inconsistency',
                confidence=confidence,
                category='architecture_security',
                message=f'Architecture score ({architecture_score}) is high but security score ({security_score}) is low',
                recommendation='Review architecture for security design patterns (defense in depth, least privilege, etc.)',
                z_score=None,
                metadata={
                    'architecture_score': architecture_score,
                    'security_score': security_score,
                    'gap': architecture_score - security_score
                }
            ))
        
        return anomalies
    
    def validate_maintainability_complexity_inverse(self, data: Dict[str, Any]) -> List[Violation]:
        """
        R10: Maintainability-Complexity Inverse Relationship
        
        High cyclomatic complexity (>15) should reduce maintainability score.
        If maintainability is >80 despite high complexity, adjust it down.
        
        Args:
            data: Dashboard data with maintainability and complexity metrics
        
        Returns:
            List of violations (empty if relationship holds)
        """
        violations = []
        
        maintainability_score = self._get_score(data, 'maintainability_score', 'maintainability', default=0)
        # For complexity, check both flat and nested locations
        avg_complexity = data.get('cyclomatic_complexity', 0)
        if avg_complexity == 0:
            avg_complexity = data.get('health', {}).get('summary', {}).get('average_complexity', 0)
        
        # Check for inverse relationship violation
        if avg_complexity > 15 and maintainability_score > 80:
            # High complexity should cap maintainability at 70
            adjusted_score = 70.0
            
            violations.append(Violation(
                rule_id='R10_MAINTAINABILITY_COMPLEXITY_INVERSE',
                severity='medium',
                category='maintainability',
                message=f'High complexity ({avg_complexity}) inconsistent with high maintainability ({maintainability_score})',
                original_score=maintainability_score,
                adjusted_score=adjusted_score,
                adjustment=adjusted_score - maintainability_score,
                rationale=f'Complexity of {avg_complexity} indicates maintenance challenges'
            ))
        
        return violations
    
    def validate_all(self, data: Dict[str, Any]) -> Tuple[List[Violation], List[Anomaly]]:
        """
        Run all cross-tab validation rules.
        
        Args:
            data: Complete dashboard data
        
        Returns:
            Tuple of (violations, anomalies)
        """
        violations = []
        anomalies = []
        
        # R8: Security-Quality Correlation
        violations.extend(self.validate_security_quality_correlation(data))
        
        # R9: Architecture-Security Alignment
        anomalies.extend(self.validate_architecture_security_alignment(data))
        
        # R10: Maintainability-Complexity Inverse
        violations.extend(self.validate_maintainability_complexity_inverse(data))
        
        return violations, anomalies
