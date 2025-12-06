"""
Trend Analyzer - Dashboard Overview Tab

Analyzes trends by comparing current snapshots with previous snapshots.
Classifies trends as improving, stable, or declining based on delta thresholds.

Author: Asif Hussain
Created: 2025-12-06
Phase: REFACTOR (Optimize & Clean)
"""

from typing import Dict, Optional, Tuple, Any, Union


class TrendAnalyzer:
    """
    Analyzes trends in dashboard metrics by comparing snapshots.
    
    Classification thresholds:
        - Improving: delta > +2.0
        - Stable: -2.0 <= delta <= +2.0
        - Declining: delta < -2.0
    
    Confidence scoring:
        - High (0.8-1.0): Large deltas (≥5.0)
        - Medium (0.5-0.8): Moderate deltas (2.1-5.0)
        - Low (0.0-0.5): Small deltas or at threshold (≤2.0)
    
    Example:
        >>> analyzer = TrendAnalyzer()
        >>> trend = analyzer.analyze_trend(85.0, 80.0)
        >>> print(trend)  # "improving" (delta = +5.0)
        >>> indicator = analyzer.get_trend_indicator(trend)
        >>> print(indicator)  # "↑"
    """
    
    # Threshold constants for trend classification
    IMPROVING_THRESHOLD = 2.0
    STABLE_LOWER = -2.0
    STABLE_UPPER = 2.0
    
    # Visual indicators for trends
    TREND_INDICATORS = {
        "improving": "↑",
        "stable": "→",
        "declining": "↓",
        "N/A": "—"
    }
    
    # Confidence thresholds
    CONFIDENCE_VERY_HIGH = 10.0
    CONFIDENCE_HIGH = 5.0
    CONFIDENCE_MEDIUM = 3.0
    
    def analyze_trend(
        self,
        current_value: Union[int, float],
        previous_value: Optional[Union[int, float]]
    ) -> str:
        """
        Analyze trend between current and previous values.
        
        Args:
            current_value: Current metric value
            previous_value: Previous metric value (or None if not available)
            
        Returns:
            Trend classification: "improving", "stable", "declining", or "N/A"
            
        Example:
            >>> analyzer = TrendAnalyzer()
            >>> analyzer.analyze_trend(92, 88)
            'improving'
            >>> analyzer.analyze_trend(81, 80)
            'stable'
            >>> analyzer.analyze_trend(75, 80)
            'declining'
            >>> analyzer.analyze_trend(85, None)
            'N/A'
        """
        if previous_value is None:
            return "N/A"
        
        delta = self.calculate_delta(current_value, previous_value)
        return self._classify_trend(delta)
    
    def _classify_trend(self, delta: float) -> str:
        """
        Classify trend based on delta value.
        
        Private helper method to keep classification logic centralized.
        
        Args:
            delta: Change in value (current - previous)
            
        Returns:
            Trend classification string
        """
        if delta > self.IMPROVING_THRESHOLD:
            return "improving"
        elif delta < self.STABLE_LOWER:
            return "declining"
        else:
            return "stable"
    
    def compare_snapshots(
        self,
        current_snapshot: Dict[str, Any],
        previous_snapshot: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        Compare two snapshots and determine trends for all metrics.
        
        Args:
            current_snapshot: Current metrics snapshot
            previous_snapshot: Previous metrics snapshot (or None)
            
        Returns:
            Dictionary mapping metric names to trend classifications
            
        Example:
            >>> analyzer = TrendAnalyzer()
            >>> current = {"health": 92, "quality": 88}
            >>> previous = {"health": 88, "quality": 85}
            >>> trends = analyzer.compare_snapshots(current, previous)
            >>> print(trends)
            {'health': 'improving', 'quality': 'improving'}
        """
        if previous_snapshot is None:
            return {key: "N/A" for key in current_snapshot.keys()}
        
        trends = {}
        for metric_name, current_value in current_snapshot.items():
            previous_value = previous_snapshot.get(metric_name)
            trends[metric_name] = self.analyze_trend(current_value, previous_value)
        
        return trends
    
    def calculate_delta(
        self,
        current_value: Union[int, float],
        previous_value: Optional[Union[int, float]]
    ) -> Optional[float]:
        """
        Calculate delta between current and previous values.
        
        Args:
            current_value: Current value
            previous_value: Previous value (or None)
            
        Returns:
            Delta (current - previous) or None if previous is None
            
        Example:
            >>> analyzer = TrendAnalyzer()
            >>> analyzer.calculate_delta(85.0, 80.0)
            5.0
            >>> analyzer.calculate_delta(75.0, 80.0)
            -5.0
            >>> analyzer.calculate_delta(85.0, None) is None
            True
        """
        if previous_value is None:
            return None
        
        return float(current_value - previous_value)
    
    def get_trend_indicator(self, trend: str) -> str:
        """
        Get visual indicator symbol for a trend.
        
        Args:
            trend: Trend classification string
            
        Returns:
            Unicode arrow symbol (↑, →, ↓, or —)
            
        Example:
            >>> analyzer = TrendAnalyzer()
            >>> analyzer.get_trend_indicator("improving")
            '↑'
            >>> analyzer.get_trend_indicator("stable")
            '→'
            >>> analyzer.get_trend_indicator("declining")
            '↓'
            >>> analyzer.get_trend_indicator("N/A")
            '—'
        """
        return self.TREND_INDICATORS.get(trend, "—")
    
    def batch_analyze(
        self,
        metrics: Dict[str, Tuple[Union[int, float], Optional[Union[int, float]]]]
    ) -> Dict[str, str]:
        """
        Analyze trends for multiple metrics at once.
        
        More efficient than calling analyze_trend() repeatedly.
        
        Args:
            metrics: Dictionary mapping metric names to (current, previous) tuples
            
        Returns:
            Dictionary mapping metric names to trend classifications
            
        Example:
            >>> analyzer = TrendAnalyzer()
            >>> metrics = {
            ...     "health": (92, 88),
            ...     "quality": (85, 84),
            ...     "security": (96, 96),
            ...     "tests": (80, 85)
            ... }
            >>> trends = analyzer.batch_analyze(metrics)
            >>> print(trends)
            {'health': 'improving', 'quality': 'stable', 'security': 'stable', 'tests': 'declining'}
        """
        return {
            metric_name: self.analyze_trend(current_value, previous_value)
            for metric_name, (current_value, previous_value) in metrics.items()
        }
    
    def calculate_confidence(self, delta: Union[int, float]) -> float:
        """
        Calculate confidence score for trend accuracy based on delta magnitude.
        
        Higher deltas indicate more reliable trends. Deltas near thresholds
        have lower confidence due to potential noise or measurement variance.
        
        Args:
            delta: Absolute delta value
            
        Returns:
            Confidence score between 0.0 and 1.0
            
        Example:
            >>> analyzer = TrendAnalyzer()
            >>> analyzer.calculate_confidence(10.0)  # Very high confidence
            0.95
            >>> analyzer.calculate_confidence(5.0)   # High confidence
            0.8
            >>> analyzer.calculate_confidence(3.0)   # Medium confidence
            0.65
            >>> analyzer.calculate_confidence(2.0)   # Low confidence (at threshold)
            0.25
        """
        abs_delta = abs(delta)
        
        if abs_delta >= self.CONFIDENCE_VERY_HIGH:
            return 0.95  # Very high confidence for large changes
        elif abs_delta >= self.CONFIDENCE_HIGH:
            return 0.8   # High confidence for moderate changes
        elif abs_delta >= self.CONFIDENCE_MEDIUM:
            return 0.65  # Medium confidence
        elif abs_delta > self.IMPROVING_THRESHOLD:
            return 0.5   # Low-medium confidence just above threshold
        elif abs_delta == self.IMPROVING_THRESHOLD:
            return 0.25  # Low confidence at exact threshold
        else:
            return 0.15  # Very low confidence in stable zone
