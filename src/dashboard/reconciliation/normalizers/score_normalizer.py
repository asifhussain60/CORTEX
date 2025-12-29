"""
Score Normalizer

Normalizes scores from various scales to standardized 0-100 scale.
Handles percentage conversions and severity string mappings.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from typing import Union


class ScoreNormalizer:
    """
    Normalizes scores from different scales to 0-100 standard scale.
    
    Features:
    - Scale conversion (0-10, 0-5, etc. to 0-100)
    - Percentage normalization (0.0-1.0 to 0-100)
    - Severity string to numeric conversion
    - Score clamping and rounding
    
    Usage:
        normalizer = ScoreNormalizer()
        score_100 = normalizer.normalize_to_100(7.5, scale=10)  # 75.0
        severity_score = normalizer.normalize_severity('high')   # 75.0
    """
    
    # Severity to score mapping (aligned with CVSS ranges)
    SEVERITY_MAP = {
        'critical': 100.0,  # 90-100 range midpoint
        'high': 75.0,       # 70-89 range midpoint
        'medium': 50.0,     # 40-69 range midpoint
        'low': 25.0,        # 1-39 range midpoint
        'none': 0.0         # 0
    }
    
    # Score ranges for reverse mapping
    SCORE_RANGES = {
        'critical': (90, 100),
        'high': (70, 89),
        'medium': (40, 69),
        'low': (1, 39),
        'none': (0, 0)
    }
    
    def normalize_to_100(self, value: float, scale: Union[int, float]) -> float:
        """
        Normalize a value from any scale to 0-100 scale.
        
        Args:
            value: Value to normalize
            scale: Original scale maximum (e.g., 10 for 0-10 scale)
        
        Returns:
            Normalized value in 0-100 scale
        
        Raises:
            ValueError: If value is negative, exceeds scale, or scale is invalid
        
        Examples:
            >>> normalizer.normalize_to_100(5.0, scale=10)
            50.0
            >>> normalizer.normalize_to_100(2.5, scale=5)
            50.0
        """
        if scale <= 0:
            raise ValueError(f"Scale must be positive, got {scale}")
        
        if value < 0:
            raise ValueError(f"Value cannot be negative, got {value}")
        
        if value > scale:
            raise ValueError(f"Value {value} exceeds scale {scale}")
        
        # Convert to 0-100 scale
        normalized = (value / scale) * 100.0
        
        return round(normalized, 2)
    
    def normalize_percentage(self, percentage: float) -> float:
        """
        Normalize percentage to 0-100 scale.
        
        Handles both decimal (0.0-1.0) and whole number (0-100) percentages.
        
        Args:
            percentage: Percentage value (0.0-1.0 or 0-100)
        
        Returns:
            Normalized percentage in 0-100 scale
        
        Raises:
            ValueError: If percentage is negative or > 100
        
        Examples:
            >>> normalizer.normalize_percentage(0.85)
            85.0
            >>> normalizer.normalize_percentage(85.0)
            85.0
        """
        if percentage < 0:
            raise ValueError(f"Percentage cannot be negative, got {percentage}")
        
        if percentage > 100:
            raise ValueError(f"Percentage cannot exceed 100, got {percentage}")
        
        # If decimal format (0.0-1.0), convert to 0-100
        if percentage <= 1.0:
            return percentage * 100.0
        
        # Already in 0-100 format
        return percentage
    
    def normalize_severity(self, severity: str) -> float:
        """
        Convert severity string to numeric score (0-100).
        
        Args:
            severity: Severity level ('critical', 'high', 'medium', 'low', 'none')
        
        Returns:
            Numeric score corresponding to severity
        
        Raises:
            ValueError: If severity is not recognized
        
        Examples:
            >>> normalizer.normalize_severity('high')
            75.0
            >>> normalizer.normalize_severity('CRITICAL')
            100.0
        """
        severity_lower = severity.lower().strip()
        
        if severity_lower not in self.SEVERITY_MAP:
            valid = ', '.join(self.SEVERITY_MAP.keys())
            raise ValueError(
                f"Invalid severity '{severity}'. Must be one of: {valid}"
            )
        
        return self.SEVERITY_MAP[severity_lower]
    
    def denormalize_to_severity(self, score: float) -> str:
        """
        Convert numeric score (0-100) back to severity string.
        
        Args:
            score: Numeric score (0-100)
        
        Returns:
            Severity level string
        
        Raises:
            ValueError: If score is outside 0-100 range
        
        Examples:
            >>> normalizer.denormalize_to_severity(85)
            'high'
            >>> normalizer.denormalize_to_severity(95)
            'critical'
        """
        if score < 0 or score > 100:
            raise ValueError(f"Score must be in 0-100 range, got {score}")
        
        # Find matching range
        for severity, (min_score, max_score) in self.SCORE_RANGES.items():
            if min_score <= score <= max_score:
                return severity
        
        # Fallback (should not reach here with valid input)
        return 'none'
    
    def clamp_score(self, score: float, min_val: float = 0.0, max_val: float = 100.0) -> float:
        """
        Clamp score to valid range.
        
        Args:
            score: Score to clamp
            min_val: Minimum allowed value (default: 0.0)
            max_val: Maximum allowed value (default: 100.0)
        
        Returns:
            Clamped score
        
        Examples:
            >>> normalizer.clamp_score(150.0)
            100.0
            >>> normalizer.clamp_score(-10.0)
            0.0
        """
        return max(min_val, min(max_val, score))
    
    def round_score(self, score: float, precision: int = 1) -> float:
        """
        Round score to specified decimal precision.
        
        Args:
            score: Score to round
            precision: Number of decimal places (default: 1)
        
        Returns:
            Rounded score
        
        Examples:
            >>> normalizer.round_score(75.4567, precision=1)
            75.5
            >>> normalizer.round_score(75.4567, precision=2)
            75.46
        """
        return round(score, precision)
