"""
CORTEX 3.0 Error Analytics
===========================

Advanced error analytics and pattern detection for proactive
error management and system improvement insights.
"""

import time
import statistics
import threading
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter
import logging
import json


logger = logging.getLogger(__name__)


class PatternType(Enum):
    """Types of error patterns."""
    FREQUENCY_SPIKE = "frequency_spike"
    RECURRING_ERROR = "recurring_error"
    ERROR_CHAIN = "error_chain"
    TEMPORAL_CLUSTER = "temporal_cluster"
    COMPONENT_HOTSPOT = "component_hotspot"
    CASCADING_FAILURE = "cascading_failure"
    PERFORMANCE_DEGRADATION = "performance_degradation"


@dataclass
class ErrorPattern:
    """Detected error pattern."""
    pattern_id: str
    pattern_type: PatternType
    description: str
    confidence_score: float  # 0.0 to 1.0
    first_detected: float
    last_updated: float
    occurrences: int = 0
    affected_components: List[str] = field(default_factory=list)
    error_codes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    recommendations: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert pattern to dictionary."""
        return {
            'pattern_id': self.pattern_id,
            'pattern_type': self.pattern_type.value,
            'description': self.description,
            'confidence_score': self.confidence_score,
            'first_detected': self.first_detected,
            'last_updated': self.last_updated,
            'occurrences': self.occurrences,
            'affected_components': self.affected_components,
            'error_codes': self.error_codes,
            'metadata': self.metadata,
            'recommendations': self.recommendations
        }


@dataclass
class ErrorTrend:
    """Error trend analysis."""
    time_period: str
    total_errors: int
    error_rate: float
    trend_direction: str  # "increasing", "decreasing", "stable"
    change_percentage: float
    dominant_error_types: List[str]
    peak_error_times: List[float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert trend to dictionary."""
        return {
            'time_period': self.time_period,
            'total_errors': self.total_errors,
            'error_rate': self.error_rate,
            'trend_direction': self.trend_direction,
            'change_percentage': self.change_percentage,
            'dominant_error_types': self.dominant_error_types,
            'peak_error_times': self.peak_error_times
        }


@dataclass
class ComponentHealth:
    """Component health analysis."""
    component_name: str
    error_count: int
    error_rate: float
    reliability_score: float  # 0.0 to 1.0
    most_common_errors: List[str]
    trend: str  # "improving", "degrading", "stable"
    last_error_time: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert component health to dictionary."""
        return {
            'component_name': self.component_name,
            'error_count': self.error_count,
            'error_rate': self.error_rate,
            'reliability_score': self.reliability_score,
            'most_common_errors': self.most_common_errors,
            'trend': self.trend,
            'last_error_time': self.last_error_time
        }


class ErrorAnalytics:
    """
    Advanced error analytics system for pattern detection,
    trend analysis, and proactive error management insights.
    """
    
    def __init__(
        self,
        analysis_window_hours: float = 24.0,
        pattern_detection_threshold: int = 5,
        trend_analysis_intervals: int = 6,
        enable_real_time_analysis: bool = True
    ):
        self.analysis_window_hours = analysis_window_hours
        self.pattern_detection_threshold = pattern_detection_threshold
        self.trend_analysis_intervals = trend_analysis_intervals
        self.enable_real_time_analysis = enable_real_time_analysis
        
        # Error data storage
        self._error_history: List[Dict[str, Any]] = []
        self._lock = threading.RLock()
        
        # Pattern tracking
        self._detected_patterns: Dict[str, ErrorPattern] = {}
        self._pattern_history: List[ErrorPattern] = []
        
        # Analytics state
        self._last_analysis_time = time.time()
        self._analysis_results: Dict[str, Any] = {}
        
        # Component tracking
        self._component_metrics: Dict[str, Dict[str, Any]] = defaultdict(dict)
        
        # Thresholds for pattern detection
        self._thresholds = {
            'frequency_spike_multiplier': 3.0,  # 3x normal rate
            'recurring_error_count': 5,
            'temporal_cluster_window': 300,  # 5 minutes
            'cascade_correlation_threshold': 0.8,
            'performance_degradation_threshold': 2.0  # 2x normal response time
        }
    
    def add_error_event(
        self,
        error_code: str,
        component: str,
        severity: str,
        timestamp: Optional[float] = None,
        context: Optional[Dict[str, Any]] = None,
        response_time: Optional[float] = None
    ) -> None:
        """
        Add an error event for analysis.
        
        Args:
            error_code: Error code
            component: Component that generated the error
            severity: Error severity level
            timestamp: Error timestamp (default: current time)
            context: Additional context information
            response_time: Response time if available
        """
        timestamp = timestamp or time.time()
        
        error_event = {
            'error_code': error_code,
            'component': component,
            'severity': severity,
            'timestamp': timestamp,
            'context': context or {},
            'response_time': response_time
        }
        
        with self._lock:
            self._error_history.append(error_event)
            
            # Maintain window size
            cutoff_time = time.time() - (self.analysis_window_hours * 3600)
            self._error_history = [
                event for event in self._error_history
                if event['timestamp'] > cutoff_time
            ]
            
            # Update component metrics
            self._update_component_metrics(error_event)
        
        # Real-time analysis
        if self.enable_real_time_analysis:
            self._check_real_time_patterns(error_event)
    
    def analyze_patterns(self) -> List[ErrorPattern]:
        """
        Perform comprehensive pattern analysis on error data.
        
        Returns:
            List of detected error patterns
        """
        with self._lock:
            current_time = time.time()
            
            # Get recent errors for analysis
            analysis_window = current_time - (self.analysis_window_hours * 3600)
            recent_errors = [
                error for error in self._error_history
                if error['timestamp'] > analysis_window
            ]
            
            if not recent_errors:
                return []
            
            new_patterns = []
            
            # Frequency spike detection
            frequency_patterns = self._detect_frequency_spikes(recent_errors)
            new_patterns.extend(frequency_patterns)
            
            # Recurring error detection
            recurring_patterns = self._detect_recurring_errors(recent_errors)
            new_patterns.extend(recurring_patterns)
            
            # Temporal clustering
            temporal_patterns = self._detect_temporal_clusters(recent_errors)
            new_patterns.extend(temporal_patterns)
            
            # Component hotspot detection
            hotspot_patterns = self._detect_component_hotspots(recent_errors)
            new_patterns.extend(hotspot_patterns)
            
            # Cascading failure detection
            cascade_patterns = self._detect_cascading_failures(recent_errors)
            new_patterns.extend(cascade_patterns)
            
            # Performance degradation patterns
            performance_patterns = self._detect_performance_degradation(recent_errors)
            new_patterns.extend(performance_patterns)
            
            # Update pattern registry
            for pattern in new_patterns:
                self._detected_patterns[pattern.pattern_id] = pattern
                if pattern not in self._pattern_history:
                    self._pattern_history.append(pattern)
            
            self._last_analysis_time = current_time
            
            return new_patterns
    
    def get_error_trends(self, time_periods: List[str] = None) -> List[ErrorTrend]:
        """
        Analyze error trends over different time periods.
        
        Args:
            time_periods: List of time periods to analyze ("1h", "6h", "24h", "7d")
            
        Returns:
            List of error trends
        """
        if time_periods is None:
            time_periods = ["1h", "6h", "24h"]
        
        trends = []
        
        for period in time_periods:
            trend = self._analyze_trend_for_period(period)
            if trend:
                trends.append(trend)
        
        return trends
    
    def get_component_health(self) -> List[ComponentHealth]:
        """
        Get health analysis for all components.
        
        Returns:
            List of component health analyses
        """
        with self._lock:
            health_analyses = []
            
            for component, metrics in self._component_metrics.items():
                health = self._calculate_component_health(component, metrics)
                health_analyses.append(health)
            
            # Sort by reliability score (worst first)
            health_analyses.sort(key=lambda h: h.reliability_score)
            
            return health_analyses
    
    def get_analytics_summary(self) -> Dict[str, Any]:
        """Get comprehensive analytics summary."""
        with self._lock:
            patterns = list(self._detected_patterns.values())
            trends = self.get_error_trends()
            component_health = self.get_component_health()
            
            # Calculate overall metrics
            total_errors = len(self._error_history)
            unique_error_codes = len(set(error['error_code'] for error in self._error_history))
            affected_components = len(set(error['component'] for error in self._error_history))
            
            # Error distribution
            error_by_severity = Counter(error['severity'] for error in self._error_history)
            error_by_component = Counter(error['component'] for error in self._error_history)
            error_by_code = Counter(error['error_code'] for error in self._error_history)
            
            return {
                'analysis_timestamp': time.time(),
                'analysis_window_hours': self.analysis_window_hours,
                'summary': {
                    'total_errors': total_errors,
                    'unique_error_codes': unique_error_codes,
                    'affected_components': affected_components,
                    'detected_patterns': len(patterns),
                    'critical_patterns': len([p for p in patterns if p.confidence_score > 0.8])
                },
                'distribution': {
                    'by_severity': dict(error_by_severity),
                    'by_component': dict(error_by_component.most_common(10)),
                    'by_error_code': dict(error_by_code.most_common(10))
                },
                'patterns': [pattern.to_dict() for pattern in patterns],
                'trends': [trend.to_dict() for trend in trends],
                'component_health': [health.to_dict() for health in component_health],
                'recommendations': self._generate_recommendations(patterns, trends, component_health)
            }
    
    def export_analytics(self, filepath: str) -> bool:
        """
        Export analytics data to file.
        
        Args:
            filepath: Output file path
            
        Returns:
            True if export successful
        """
        try:
            analytics_data = self.get_analytics_summary()
            
            with open(filepath, 'w') as f:
                json.dump(analytics_data, f, indent=2, default=str)
            
            logger.info(f"Exported analytics data to {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export analytics: {e}")
            return False
    
    def _detect_frequency_spikes(self, errors: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Detect frequency spike patterns."""
        patterns = []
        
        # Group errors by hour
        hourly_counts = defaultdict(int)
        for error in errors:
            hour_bucket = int(error['timestamp'] // 3600)
            hourly_counts[hour_bucket] += 1
        
        if len(hourly_counts) < 2:
            return patterns
        
        # Calculate baseline and detect spikes
        counts = list(hourly_counts.values())
        baseline = statistics.mean(counts)
        std_dev = statistics.stdev(counts) if len(counts) > 1 else 0
        
        spike_threshold = baseline + (2 * std_dev)  # 2 standard deviations above mean
        
        for hour, count in hourly_counts.items():
            if count > spike_threshold and count > baseline * self._thresholds['frequency_spike_multiplier']:
                pattern = ErrorPattern(
                    pattern_id=f"freq_spike_{hour}",
                    pattern_type=PatternType.FREQUENCY_SPIKE,
                    description=f"Error frequency spike detected: {count} errors in hour {hour}",
                    confidence_score=min(1.0, (count - baseline) / max(baseline, 1)),
                    first_detected=time.time(),
                    last_updated=time.time(),
                    occurrences=count,
                    metadata={'hour': hour, 'count': count, 'baseline': baseline},
                    recommendations=[
                        "Investigate system load during spike period",
                        "Check for configuration changes",
                        "Monitor resource usage patterns"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_recurring_errors(self, errors: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Detect recurring error patterns."""
        patterns = []
        
        # Count error codes
        error_counts = Counter(error['error_code'] for error in errors)
        
        for error_code, count in error_counts.items():
            if count >= self._thresholds['recurring_error_count']:
                # Calculate time distribution
                error_times = [
                    error['timestamp'] for error in errors
                    if error['error_code'] == error_code
                ]
                
                time_intervals = []
                if len(error_times) > 1:
                    sorted_times = sorted(error_times)
                    time_intervals = [
                        sorted_times[i+1] - sorted_times[i]
                        for i in range(len(sorted_times) - 1)
                    ]
                
                pattern = ErrorPattern(
                    pattern_id=f"recurring_{error_code}",
                    pattern_type=PatternType.RECURRING_ERROR,
                    description=f"Recurring error detected: {error_code} occurred {count} times",
                    confidence_score=min(1.0, count / 10.0),  # Scale with frequency
                    first_detected=min(error_times),
                    last_updated=max(error_times),
                    occurrences=count,
                    error_codes=[error_code],
                    metadata={
                        'avg_interval': statistics.mean(time_intervals) if time_intervals else None,
                        'total_timespan': max(error_times) - min(error_times) if len(error_times) > 1 else 0
                    },
                    recommendations=[
                        f"Investigate root cause of {error_code}",
                        "Check for periodic triggers or scheduled tasks",
                        "Consider implementing preventive measures"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_temporal_clusters(self, errors: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Detect temporal clustering patterns."""
        patterns = []
        
        if len(errors) < 3:
            return patterns
        
        # Sort errors by timestamp
        sorted_errors = sorted(errors, key=lambda e: e['timestamp'])
        
        # Find clusters of errors within time window
        cluster_window = self._thresholds['temporal_cluster_window']
        clusters = []
        current_cluster = [sorted_errors[0]]
        
        for error in sorted_errors[1:]:
            if error['timestamp'] - current_cluster[-1]['timestamp'] <= cluster_window:
                current_cluster.append(error)
            else:
                if len(current_cluster) >= 3:  # Minimum cluster size
                    clusters.append(current_cluster)
                current_cluster = [error]
        
        # Check final cluster
        if len(current_cluster) >= 3:
            clusters.append(current_cluster)
        
        # Create patterns for significant clusters
        for i, cluster in enumerate(clusters):
            if len(cluster) >= 5:  # Significant cluster threshold
                error_codes = [error['error_code'] for error in cluster]
                components = [error['component'] for error in cluster]
                
                pattern = ErrorPattern(
                    pattern_id=f"temporal_cluster_{i}_{int(cluster[0]['timestamp'])}",
                    pattern_type=PatternType.TEMPORAL_CLUSTER,
                    description=f"Temporal cluster: {len(cluster)} errors in {cluster_window}s",
                    confidence_score=min(1.0, len(cluster) / 10.0),
                    first_detected=cluster[0]['timestamp'],
                    last_updated=cluster[-1]['timestamp'],
                    occurrences=len(cluster),
                    affected_components=list(set(components)),
                    error_codes=list(set(error_codes)),
                    metadata={
                        'cluster_duration': cluster[-1]['timestamp'] - cluster[0]['timestamp'],
                        'error_density': len(cluster) / cluster_window
                    },
                    recommendations=[
                        "Investigate system events during cluster period",
                        "Check for cascading failures",
                        "Review system logs for common triggers"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_component_hotspots(self, errors: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Detect component hotspot patterns."""
        patterns = []
        
        # Count errors by component
        component_counts = Counter(error['component'] for error in errors)
        total_errors = len(errors)
        
        for component, count in component_counts.items():
            # Calculate component error rate
            error_rate = count / total_errors if total_errors > 0 else 0
            
            # Detect if component has unusually high error rate
            if error_rate > 0.3 and count >= 5:  # Component contributes >30% of errors
                component_errors = [e for e in errors if e['component'] == component]
                error_codes = [e['error_code'] for e in component_errors]
                
                pattern = ErrorPattern(
                    pattern_id=f"hotspot_{component}",
                    pattern_type=PatternType.COMPONENT_HOTSPOT,
                    description=f"Component hotspot: {component} generated {count} errors ({error_rate:.1%})",
                    confidence_score=min(1.0, error_rate * 2),  # Scale with error rate
                    first_detected=min(e['timestamp'] for e in component_errors),
                    last_updated=max(e['timestamp'] for e in component_errors),
                    occurrences=count,
                    affected_components=[component],
                    error_codes=list(set(error_codes)),
                    metadata={
                        'error_rate': error_rate,
                        'unique_error_types': len(set(error_codes))
                    },
                    recommendations=[
                        f"Focus debugging efforts on {component}",
                        "Check component configuration and resources",
                        "Consider component refactoring or scaling"
                    ]
                )
                patterns.append(pattern)
        
        return patterns
    
    def _detect_cascading_failures(self, errors: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Detect cascading failure patterns."""
        patterns = []
        
        # Group errors by time windows and analyze component sequences
        window_size = 60  # 1 minute windows
        time_windows = defaultdict(list)
        
        for error in errors:
            window_key = int(error['timestamp'] // window_size)
            time_windows[window_key].append(error)
        
        for window_key, window_errors in time_windows.items():
            if len(window_errors) < 3:
                continue
            
            # Check for component sequence patterns
            components = [error['component'] for error in sorted(window_errors, key=lambda e: e['timestamp'])]
            
            # Look for patterns where one component failure leads to others
            if len(set(components)) >= 2:
                component_sequence = []
                for component in components:
                    if not component_sequence or component != component_sequence[-1]:
                        component_sequence.append(component)
                
                if len(component_sequence) >= 3:  # Cascade involving 3+ components
                    pattern = ErrorPattern(
                        pattern_id=f"cascade_{window_key}",
                        pattern_type=PatternType.CASCADING_FAILURE,
                        description=f"Cascading failure: {' -> '.join(component_sequence)}",
                        confidence_score=min(1.0, len(component_sequence) / 5.0),
                        first_detected=min(e['timestamp'] for e in window_errors),
                        last_updated=max(e['timestamp'] for e in window_errors),
                        occurrences=len(window_errors),
                        affected_components=component_sequence,
                        metadata={
                            'cascade_sequence': component_sequence,
                            'window_duration': window_size
                        },
                        recommendations=[
                            "Identify root cause component in cascade",
                            "Implement circuit breakers between components",
                            "Add failure isolation mechanisms"
                        ]
                    )
                    patterns.append(pattern)
        
        return patterns
    
    def _detect_performance_degradation(self, errors: List[Dict[str, Any]]) -> List[ErrorPattern]:
        """Detect performance degradation patterns."""
        patterns = []
        
        # Filter errors with response time data
        timed_errors = [error for error in errors if error.get('response_time')]
        
        if len(timed_errors) < 10:
            return patterns
        
        # Calculate baseline response time
        response_times = [error['response_time'] for error in timed_errors]
        baseline_response_time = statistics.median(response_times[:len(response_times)//2])  # First half as baseline
        
        # Detect degradation periods
        degradation_threshold = baseline_response_time * self._thresholds['performance_degradation_threshold']
        degraded_errors = [
            error for error in timed_errors
            if error['response_time'] > degradation_threshold
        ]
        
        if len(degraded_errors) >= 5:
            pattern = ErrorPattern(
                pattern_id=f"performance_degradation_{int(time.time())}",
                pattern_type=PatternType.PERFORMANCE_DEGRADATION,
                description=f"Performance degradation: {len(degraded_errors)} slow responses detected",
                confidence_score=min(1.0, len(degraded_errors) / len(timed_errors)),
                first_detected=min(e['timestamp'] for e in degraded_errors),
                last_updated=max(e['timestamp'] for e in degraded_errors),
                occurrences=len(degraded_errors),
                affected_components=list(set(e['component'] for e in degraded_errors)),
                metadata={
                    'baseline_response_time': baseline_response_time,
                    'avg_degraded_response_time': statistics.mean(e['response_time'] for e in degraded_errors),
                    'degradation_ratio': len(degraded_errors) / len(timed_errors)
                },
                recommendations=[
                    "Check system resource utilization",
                    "Analyze database query performance",
                    "Review recent configuration changes"
                ]
            )
            patterns.append(pattern)
        
        return patterns
    
    def _analyze_trend_for_period(self, period: str) -> Optional[ErrorTrend]:
        """Analyze error trends for a specific time period."""
        # Parse period
        period_seconds = {
            "1h": 3600,
            "6h": 6 * 3600,
            "24h": 24 * 3600,
            "7d": 7 * 24 * 3600
        }.get(period)
        
        if not period_seconds:
            return None
        
        current_time = time.time()
        period_start = current_time - period_seconds
        
        # Get errors in period
        period_errors = [
            error for error in self._error_history
            if error['timestamp'] > period_start
        ]
        
        if not period_errors:
            return None
        
        # Calculate trend
        total_errors = len(period_errors)
        error_rate = total_errors / (period_seconds / 3600)  # Errors per hour
        
        # Compare with previous period for trend direction
        previous_period_start = period_start - period_seconds
        previous_errors = [
            error for error in self._error_history
            if previous_period_start < error['timestamp'] <= period_start
        ]
        
        trend_direction = "stable"
        change_percentage = 0.0
        
        if previous_errors:
            previous_count = len(previous_errors)
            if total_errors > previous_count * 1.2:
                trend_direction = "increasing"
                change_percentage = ((total_errors - previous_count) / previous_count) * 100
            elif total_errors < previous_count * 0.8:
                trend_direction = "decreasing"
                change_percentage = ((previous_count - total_errors) / previous_count) * 100
        
        # Find dominant error types
        error_counter = Counter(error['error_code'] for error in period_errors)
        dominant_error_types = [code for code, count in error_counter.most_common(5)]
        
        # Find peak error times
        hourly_buckets = defaultdict(int)
        for error in period_errors:
            hour_bucket = int(error['timestamp'] // 3600)
            hourly_buckets[hour_bucket] += 1
        
        peak_hours = sorted(hourly_buckets.items(), key=lambda x: x[1], reverse=True)[:3]
        peak_error_times = [hour * 3600 for hour, count in peak_hours]
        
        return ErrorTrend(
            time_period=period,
            total_errors=total_errors,
            error_rate=error_rate,
            trend_direction=trend_direction,
            change_percentage=change_percentage,
            dominant_error_types=dominant_error_types,
            peak_error_times=peak_error_times
        )
    
    def _update_component_metrics(self, error_event: Dict[str, Any]) -> None:
        """Update component metrics with new error event."""
        component = error_event['component']
        
        if component not in self._component_metrics:
            self._component_metrics[component] = {
                'error_count': 0,
                'error_codes': Counter(),
                'last_error_time': None,
                'error_times': []
            }
        
        metrics = self._component_metrics[component]
        metrics['error_count'] += 1
        metrics['error_codes'][error_event['error_code']] += 1
        metrics['last_error_time'] = error_event['timestamp']
        metrics['error_times'].append(error_event['timestamp'])
        
        # Maintain sliding window
        cutoff_time = time.time() - (self.analysis_window_hours * 3600)
        metrics['error_times'] = [
            t for t in metrics['error_times'] if t > cutoff_time
        ]
    
    def _calculate_component_health(self, component: str, metrics: Dict[str, Any]) -> ComponentHealth:
        """Calculate health score for a component."""
        error_count = len(metrics['error_times'])
        
        # Calculate error rate (errors per hour)
        if metrics['error_times']:
            time_span = max(metrics['error_times']) - min(metrics['error_times'])
            if time_span > 0:
                error_rate = error_count / (time_span / 3600)
            else:
                error_rate = error_count
        else:
            error_rate = 0
        
        # Calculate reliability score (inverse of error rate, scaled 0-1)
        max_error_rate = 10.0  # Assume 10 errors/hour is very poor
        reliability_score = max(0, 1 - (error_rate / max_error_rate))
        
        # Determine trend
        if len(metrics['error_times']) >= 4:
            mid_point = len(metrics['error_times']) // 2
            first_half = metrics['error_times'][:mid_point]
            second_half = metrics['error_times'][mid_point:]
            
            first_half_rate = len(first_half) / max(1, len(first_half))
            second_half_rate = len(second_half) / max(1, len(second_half))
            
            if second_half_rate > first_half_rate * 1.5:
                trend = "degrading"
            elif second_half_rate < first_half_rate * 0.5:
                trend = "improving"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Get most common errors
        most_common_errors = [
            code for code, count in metrics['error_codes'].most_common(5)
        ]
        
        return ComponentHealth(
            component_name=component,
            error_count=error_count,
            error_rate=error_rate,
            reliability_score=reliability_score,
            most_common_errors=most_common_errors,
            trend=trend,
            last_error_time=metrics['last_error_time']
        )
    
    def _check_real_time_patterns(self, error_event: Dict[str, Any]) -> None:
        """Check for real-time pattern detection."""
        # This is a simplified real-time check
        # In production, you might want more sophisticated streaming analysis
        
        current_time = time.time()
        recent_window = current_time - 300  # Last 5 minutes
        
        recent_errors = [
            error for error in self._error_history
            if error['timestamp'] > recent_window
        ]
        
        # Check for immediate frequency spikes
        if len(recent_errors) > 10:  # More than 10 errors in 5 minutes
            logger.warning(f"Real-time frequency spike detected: {len(recent_errors)} errors in 5 minutes")
    
    def _generate_recommendations(
        self,
        patterns: List[ErrorPattern],
        trends: List[ErrorTrend],
        component_health: List[ComponentHealth]
    ) -> List[str]:
        """Generate actionable recommendations based on analysis."""
        recommendations = []
        
        # Pattern-based recommendations
        critical_patterns = [p for p in patterns if p.confidence_score > 0.8]
        if critical_patterns:
            recommendations.append(f"Address {len(critical_patterns)} critical error patterns immediately")
        
        # Trend-based recommendations
        increasing_trends = [t for t in trends if t.trend_direction == "increasing"]
        if increasing_trends:
            recommendations.append("Investigate increasing error trends - system may be degrading")
        
        # Component-based recommendations
        unhealthy_components = [c for c in component_health if c.reliability_score < 0.5]
        if unhealthy_components:
            recommendations.append(f"Focus on {len(unhealthy_components)} components with low reliability scores")
        
        # General recommendations
        if not recommendations:
            recommendations.append("System error patterns appear normal - continue monitoring")
        
        return recommendations


# Global error analytics instance
default_error_analytics = ErrorAnalytics()