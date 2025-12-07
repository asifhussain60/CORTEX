"""
CVSS Normalizer

Converts CVSS v3.1/v4.0 scores to normalized 0-100 scale per NIST standards.
Aligns with NVD vulnerability scoring system.

Reference: https://nvd.nist.gov/vuln-metrics/cvss

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""


class CVSSNormalizer:
    """
    Normalizes CVSS vulnerability scores to 0-100 scale.
    
    CVSS Score Ranges (per NIST NVD):
    - Critical: 9.0-10.0 → 90-100
    - High: 7.0-8.9 → 70-89
    - Medium: 4.0-6.9 → 40-69
    - Low: 0.1-3.9 → 1-39
    - None: 0.0 → 0
    
    Usage:
        normalizer = CVSSNormalizer()
        score_100 = normalizer.cvss_to_100(7.5)  # 75.0
        severity = normalizer.get_severity_from_cvss(7.5)  # 'high'
    """
    
    # CVSS severity ranges per NIST standards
    CVSS_RANGES = {
        'critical': (9.0, 10.0),
        'high': (7.0, 8.9),
        'medium': (4.0, 6.9),
        'low': (0.1, 3.9),
        'none': (0.0, 0.0)
    }
    
    # Vulnerability impact weights (for score adjustment)
    IMPACT_WEIGHTS = {
        'critical': 1.0,   # 100% impact
        'high': 0.7,       # 70% impact
        'medium': 0.4,     # 40% impact
        'low': 0.1,        # 10% impact
        'none': 0.0        # 0% impact
    }
    
    def cvss_to_100(self, cvss_score: float) -> float:
        """
        Convert CVSS score (0.0-10.0) to normalized 0-100 scale.
        
        Simple linear mapping: cvss_score * 10
        
        Args:
            cvss_score: CVSS score in 0.0-10.0 range
        
        Returns:
            Normalized score in 0-100 range
        
        Raises:
            ValueError: If CVSS score is outside valid range
        
        Examples:
            >>> normalizer.cvss_to_100(7.5)
            75.0
            >>> normalizer.cvss_to_100(9.5)
            95.0
        """
        if cvss_score < 0.0 or cvss_score > 10.0:
            raise ValueError(
                f"CVSS score must be in 0.0-10.0 range, got {cvss_score}"
            )
        
        # Linear conversion: 0-10 → 0-100
        return round(cvss_score * 10.0, 1)
    
    def severity_to_cvss(self, severity: str) -> float:
        """
        Convert severity string to CVSS score (midpoint of range).
        
        Args:
            severity: Severity level ('critical', 'high', 'medium', 'low', 'none')
        
        Returns:
            CVSS score (midpoint of severity range)
        
        Raises:
            ValueError: If severity is not recognized
        
        Examples:
            >>> normalizer.severity_to_cvss('high')
            7.95
            >>> normalizer.severity_to_cvss('critical')
            9.5
        """
        severity_lower = severity.lower().strip()
        
        if severity_lower not in self.CVSS_RANGES:
            valid = ', '.join(self.CVSS_RANGES.keys())
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: {valid}"
            )
        
        min_score, max_score = self.CVSS_RANGES[severity_lower]
        
        # Return midpoint of range
        if min_score == max_score:  # 'none' case
            return min_score
        
        return round((min_score + max_score) / 2.0, 2)
    
    def get_severity_from_cvss(self, cvss_score: float) -> str:
        """
        Determine severity category from CVSS score.
        
        Args:
            cvss_score: CVSS score in 0.0-10.0 range
        
        Returns:
            Severity level string
        
        Examples:
            >>> normalizer.get_severity_from_cvss(8.5)
            'high'
            >>> normalizer.get_severity_from_cvss(9.2)
            'critical'
        """
        # Check ranges in order from highest to lowest
        if cvss_score >= 9.0:
            return 'critical'
        elif cvss_score >= 7.0:
            return 'high'
        elif cvss_score >= 4.0:
            return 'medium'
        elif cvss_score > 0.0:
            return 'low'
        else:
            return 'none'
    
    def get_severity_range(self, severity: str) -> tuple:
        """
        Get CVSS score range for a severity level.
        
        Args:
            severity: Severity level
        
        Returns:
            Tuple of (min_score, max_score)
        
        Raises:
            ValueError: If severity is not recognized
        
        Examples:
            >>> normalizer.get_severity_range('high')
            (7.0, 8.9)
        """
        severity_lower = severity.lower().strip()
        
        if severity_lower not in self.CVSS_RANGES:
            valid = ', '.join(self.CVSS_RANGES.keys())
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: {valid}"
            )
        
        return self.CVSS_RANGES[severity_lower]
    
    def normalize_vulnerability_impact(self, severity: str) -> float:
        """
        Get impact weight for vulnerability severity.
        
        Used to calculate how much a vulnerability should affect overall scores.
        
        Args:
            severity: Vulnerability severity level
        
        Returns:
            Impact weight (0.0-1.0)
        
        Raises:
            ValueError: If severity is not recognized
        
        Examples:
            >>> normalizer.normalize_vulnerability_impact('critical')
            1.0
            >>> normalizer.normalize_vulnerability_impact('high')
            0.7
        """
        severity_lower = severity.lower().strip()
        
        if severity_lower not in self.IMPACT_WEIGHTS:
            valid = ', '.join(self.IMPACT_WEIGHTS.keys())
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: {valid}"
            )
        
        return self.IMPACT_WEIGHTS[severity_lower]
