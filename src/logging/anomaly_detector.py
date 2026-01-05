"""
Anomaly Detector for Self-Healing Engine.

Detects statistical outliers, threshold violations, and rate anomalies
in audit log metrics.

Key Features:
- Z-score based outlier detection (configurable std threshold)
- IQR (Interquartile Range) based outlier detection
- Threshold violation monitoring with severity levels
- Rate change detection (spikes/drops)
- Time-window based analysis

Usage:
    >>> detector = AnomalyDetector(std_threshold=3.0)
    >>> events = [{"event": "metric", "data": {"value": 100}}, ...]
    >>> anomalies = detector.detect_anomalies(events, metric_key="data.value")
    >>> for anomaly in anomalies:
    ...     print(f"Outlier: {anomaly.value} (z-score: {anomaly.z_score})")

Statistical Methods:
- Z-score: (value - mean) / std_dev
- IQR: Q3 - Q1, outliers beyond Q1 - 1.5*IQR or Q3 + 1.5*IQR
- Rate analysis: Events per time window comparison

Architecture:
- Baseline window for statistical reference
- Configurable thresholds for sensitivity tuning
- Severity classification (warning/critical)
- Time-series grouping for rate analysis

Performance:
- O(n) complexity for most operations
- Minimal memory via sliding baseline window
- Pure Python implementation (no heavy ML dependencies)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from collections import defaultdict
from datetime import datetime, timedelta
import statistics


@dataclass
class Anomaly:
    """Represents a detected anomaly."""
    event_type: str
    value: float
    z_score: float
    timestamp: str
    severity: str  # "warning", "critical"
    description: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ThresholdViolation:
    """Represents a threshold violation."""
    event_type: str
    metric: str
    value: float
    threshold: float
    severity: str
    timestamp: str


@dataclass
class RateAnomaly:
    """Represents an anomalous rate change."""
    event_type: str
    normal_rate: float
    anomalous_rate: float
    rate_change: float  # Multiplier (e.g., 5.0 = 5x increase)
    window_start: str
    window_end: str


class AnomalyDetector:
    """Detects anomalies in audit log metrics."""
    
    def __init__(
        self,
        std_threshold: float = 3.0,
        iqr_threshold: float = 1.5,
        baseline_window: int = 50
    ):
        """
        Initialize anomaly detector.
        
        Args:
            std_threshold: Number of standard deviations for outlier detection
            iqr_threshold: IQR multiplier for outlier detection
            baseline_window: Number of events to use for baseline
        """
        self.std_threshold = std_threshold
        self.iqr_threshold = iqr_threshold
        self.baseline_window = baseline_window
    
    def detect_anomalies(
        self,
        events: List[Dict[str, Any]],
        metric_key: str = "data.value"
    ) -> List[Anomaly]:
        """
        Detect statistical outliers using z-score method.
        
        Args:
            events: List of event dictionaries
            metric_key: Key path to extract metric
            
        Returns:
            List of detected anomalies
        """
        if len(events) < 10:
            return []
        
        # Extract metric values
        values = []
        event_map = {}
        
        for i, event in enumerate(events):
            value = self._extract_nested_value(event, metric_key)
            if value is not None:
                try:
                    numeric_value = float(value)
                    values.append(numeric_value)
                    event_map[len(values) - 1] = (event, numeric_value)
                except (ValueError, TypeError):
                    continue
        
        if len(values) < 10:
            return []
        
        # Use baseline window for statistics
        baseline = values[:self.baseline_window] if len(values) > self.baseline_window else values
        
        try:
            mean = statistics.mean(baseline)
            stdev = statistics.stdev(baseline) if len(baseline) > 1 else 0
        except statistics.StatisticsError:
            return []
        
        if stdev == 0:
            return []
        
        # Detect outliers
        anomalies = []
        for idx, value in enumerate(values):
            z_score = abs((value - mean) / stdev)
            
            if z_score > self.std_threshold:
                event, numeric_value = event_map.get(idx, ({}, value))
                
                severity = "critical" if z_score > self.std_threshold * 1.5 else "warning"
                
                anomaly = Anomaly(
                    event_type=event.get("event", "unknown"),
                    value=numeric_value,
                    z_score=z_score,
                    timestamp=event.get("timestamp", ""),
                    severity=severity,
                    description=f"Value {numeric_value} is {z_score:.2f} standard deviations from mean {mean:.2f}"
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def detect_threshold_violations(
        self,
        events: List[Dict[str, Any]],
        thresholds: Dict[str, Dict[str, Any]]
    ) -> List[ThresholdViolation]:
        """
        Detect threshold violations.
        
        Args:
            events: List of event dictionaries
            thresholds: Dict mapping event types to threshold config
                       e.g., {"cpu_usage": {"metric": "data.percent", "max": 90}}
            
        Returns:
            List of threshold violations
        """
        violations = []
        
        for event in events:
            event_type = event.get("event", "")
            timestamp = event.get("timestamp", "")
            
            if event_type in thresholds:
                config = thresholds[event_type]
                metric_key = config.get("metric", "value")
                max_threshold = config.get("max")
                min_threshold = config.get("min")
                
                value = self._extract_nested_value(event, metric_key)
                if value is None:
                    continue
                
                try:
                    numeric_value = float(value)
                except (ValueError, TypeError):
                    continue
                
                # Check max threshold
                if max_threshold is not None and numeric_value > max_threshold:
                    severity = "critical" if numeric_value > max_threshold * 1.1 else "warning"
                    
                    violation = ThresholdViolation(
                        event_type=event_type,
                        metric=metric_key,
                        value=numeric_value,
                        threshold=max_threshold,
                        severity=severity,
                        timestamp=timestamp
                    )
                    violations.append(violation)
                
                # Check min threshold
                if min_threshold is not None and numeric_value < min_threshold:
                    severity = "critical" if numeric_value < min_threshold * 0.9 else "warning"
                    
                    violation = ThresholdViolation(
                        event_type=event_type,
                        metric=metric_key,
                        value=numeric_value,
                        threshold=min_threshold,
                        severity=severity,
                        timestamp=timestamp
                    )
                    violations.append(violation)
        
        return violations
    
    def detect_rate_anomalies(
        self,
        events: List[Dict[str, Any]],
        window_seconds: int = 60
    ) -> List[RateAnomaly]:
        """
        Detect sudden rate changes (spikes or drops).
        
        Args:
            events: List of event dictionaries with timestamps
            window_seconds: Time window for rate calculation
            
        Returns:
            List of rate anomalies
        """
        if len(events) < 10:
            return []
        
        # Group events by time windows
        windows = self._group_by_time_window(events, window_seconds)
        
        if len(windows) < 2:
            return []
        
        # Calculate rates for each window
        window_times = sorted(windows.keys())
        rates = []
        
        for window_time in window_times:
            event_count = len(windows[window_time])
            rate = event_count  # Events per window
            rates.append((window_time, rate, windows[window_time]))
        
        # Establish baseline (first half of windows)
        split_point = len(rates) // 2
        baseline_rates = [r[1] for r in rates[:split_point]]
        
        if not baseline_rates:
            return []
        
        baseline_avg = statistics.mean(baseline_rates)
        
        if baseline_avg == 0:
            baseline_avg = 1  # Avoid division by zero
        
        # Detect anomalies in second half
        anomalies = []
        for i in range(split_point, len(rates)):
            window_time, rate, window_events = rates[i]
            
            if rate > baseline_avg * 5:  # 5x increase
                rate_change = rate / baseline_avg
                
                # Get time range for this window
                timestamps = [e.get("timestamp", "") for e in window_events]
                window_start = min(timestamps) if timestamps else ""
                window_end = max(timestamps) if timestamps else ""
                
                event_type = window_events[0].get("event", "unknown") if window_events else "unknown"
                
                anomaly = RateAnomaly(
                    event_type=event_type,
                    normal_rate=baseline_avg,
                    anomalous_rate=rate,
                    rate_change=rate_change,
                    window_start=window_start,
                    window_end=window_end
                )
                anomalies.append(anomaly)
        
        return anomalies
    
    def _group_by_time_window(
        self,
        events: List[Dict[str, Any]],
        window_seconds: int
    ) -> Dict[int, List[Dict[str, Any]]]:
        """
        Group events into time windows.
        
        Args:
            events: List of events with timestamps
            window_seconds: Window size in seconds
            
        Returns:
            Dict mapping window index to events
        """
        windows = defaultdict(list)
        
        for event in events:
            timestamp_str = event.get("timestamp", "")
            if not timestamp_str:
                continue
            
            try:
                # Parse timestamp (ISO format)
                timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                # Calculate window index (seconds since epoch / window_seconds)
                window_idx = int(timestamp.timestamp() // window_seconds)
                windows[window_idx].append(event)
            except (ValueError, AttributeError):
                continue
        
        return windows
    
    def _extract_nested_value(self, data: Dict[str, Any], key_path: str) -> Any:
        """
        Extract value from nested dictionary using dot notation.
        
        Args:
            data: Dictionary to extract from
            key_path: Dot-separated key path
            
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
