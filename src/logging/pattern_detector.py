"""
Pattern Detector for Self-Healing Engine.

Detects recurring error patterns and performance degradation trends
in audit log events.

Key Features:
- Recurring error pattern detection (configurable threshold)
- Performance degradation trend analysis
- Confidence scoring for pattern reliability
- Support for nested data extraction

Usage:
    >>> detector = PatternDetector(window_size=100, min_occurrences=3)
    >>> events = [{"event": "error", "timestamp": "..."}, ...]
    >>> patterns = detector.detect_patterns(events)
    >>> for pattern in patterns:
    ...     print(f"{pattern.signature}: {pattern.occurrences} occurrences")

Architecture:
- Window-based analysis (configurable size)
- Frequency counting with confidence scoring
- Time-series trend detection for performance metrics
- Nested value extraction via dot notation

Performance:
- O(n) pattern detection where n = window_size
- Minimal memory footprint via sliding window
- No external dependencies (pure Python)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import Counter
from datetime import datetime, timedelta
import statistics


@dataclass
class DetectedPattern:
    """Represents a detected pattern in audit logs."""
    signature: str
    occurrences: int
    confidence: float
    first_seen: str
    last_seen: str
    affected_orchestrators: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PerformanceDegradation:
    """Represents detected performance degradation."""
    metric: str
    degradation_rate: float
    severity: str  # "low", "medium", "high"
    baseline_avg: float
    current_avg: float
    trend: List[float] = field(default_factory=list)


class PatternDetector:
    """Detects recurring patterns and performance degradation in audit logs."""
    
    def __init__(
        self,
        window_size: int = 100,
        min_occurrences: int = 3,
        confidence_threshold: float = 0.7
    ):
        """
        Initialize pattern detector.
        
        Args:
            window_size: Number of recent events to analyze
            min_occurrences: Minimum occurrences to consider a pattern
            confidence_threshold: Confidence level required (0.0-1.0)
        """
        self.window_size = window_size
        self.min_occurrences = min_occurrences
        self.confidence_threshold = confidence_threshold
    
    def detect_patterns(self, events: List[Dict[str, Any]]) -> List[DetectedPattern]:
        """
        Detect recurring patterns in event stream.
        
        Args:
            events: List of event dictionaries
            
        Returns:
            List of detected patterns
        """
        if not events:
            return []
        
        # Take most recent events within window
        recent_events = events[-self.window_size:] if len(events) > self.window_size else events
        
        # Count event types
        event_counter = Counter()
        event_orchestrators: Dict[str, set] = {}
        event_timestamps: Dict[str, List[str]] = {}
        
        for event in recent_events:
            event_type = event.get("event", "unknown")
            orchestrator = event.get("orchestrator", "unknown")
            timestamp = event.get("timestamp", "")
            
            event_counter[event_type] += 1
            
            if event_type not in event_orchestrators:
                event_orchestrators[event_type] = set()
                event_timestamps[event_type] = []
            
            event_orchestrators[event_type].add(orchestrator)
            event_timestamps[event_type].append(timestamp)
        
        # Identify patterns above threshold
        patterns = []
        for event_type, count in event_counter.items():
            if count >= self.min_occurrences:
                # Calculate confidence based on frequency
                # More occurrences = higher confidence, but cap at 1.0
                confidence = min(1.0, (count / len(recent_events)) * 10)
                
                if confidence >= self.confidence_threshold:
                    timestamps = event_timestamps[event_type]
                    pattern = DetectedPattern(
                        signature=event_type,
                        occurrences=count,
                        confidence=confidence,
                        first_seen=timestamps[0] if timestamps else "",
                        last_seen=timestamps[-1] if timestamps else "",
                        affected_orchestrators=list(event_orchestrators[event_type])
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def detect_performance_degradation(
        self,
        events: List[Dict[str, Any]],
        metric_key: str = "data.duration_ms"
    ) -> Optional[PerformanceDegradation]:
        """
        Detect performance degradation trends.
        
        Args:
            events: List of event dictionaries with performance metrics
            metric_key: Key path to extract metric (e.g., "data.duration_ms")
            
        Returns:
            PerformanceDegradation object if degradation detected, else None
        """
        if len(events) < 5:
            return None
        
        # Extract metric values
        values = []
        for event in events:
            value = self._extract_nested_value(event, metric_key)
            if value is not None:
                values.append(float(value))
        
        if len(values) < 5:
            return None
        
        # Split into baseline (first half) and current (second half)
        split_point = len(values) // 2
        baseline = values[:split_point]
        current = values[split_point:]
        
        baseline_avg = statistics.mean(baseline)
        current_avg = statistics.mean(current)
        
        # Calculate degradation rate (negative = improvement, positive = degradation)
        if baseline_avg > 0:
            degradation_rate = (current_avg - baseline_avg) / baseline_avg
        else:
            degradation_rate = 0.0
        
        # Only report if there's actual degradation
        if degradation_rate <= 0:
            return None
        
        # Determine severity
        if degradation_rate > 1.0:  # >100% increase
            severity = "high"
        elif degradation_rate > 0.5:  # >50% increase
            severity = "medium"
        else:
            severity = "low"
        
        return PerformanceDegradation(
            metric=metric_key,
            degradation_rate=degradation_rate,
            severity=severity,
            baseline_avg=baseline_avg,
            current_avg=current_avg,
            trend=values
        )
    
    def _extract_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """
        Extract value from nested dictionary using dot notation.
        
        Args:
            data: Dictionary to extract from
            key_path: Dot-separated key path (e.g., "data.duration_ms")
            
        Returns:
            Extracted value or None
        """
        keys = key_path.split(".")
        value = data
        
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return None
        
        return value
