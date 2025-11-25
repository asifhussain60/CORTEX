"""
CORTEX 3.0 Phase 2 - Brain Health Monitoring System
==================================================

Advanced brain health monitoring system with predictive analytics and auto-healing.
Integrates Phase 1 data collectors with Phase 2 brain optimization for intelligent monitoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Phase: Phase 2 - Data Collection Integration (Task 3)
Integration: Real-time health assessment + Predictive analytics + Auto-healing
"""

import time
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import logging
import json

# Import dashboard for metrics access
try:
    from .real_time_metrics_dashboard import (
        RealTimeMetricsDashboard, 
        UnifiedMetricsSnapshot, 
        DashboardAlert, 
        MetricSeverity
    )
except ImportError:
    from real_time_metrics_dashboard import (
        RealTimeMetricsDashboard, 
        UnifiedMetricsSnapshot, 
        DashboardAlert, 
        MetricSeverity
    )

# Import Phase 2 brain optimization
try:
    from src.operations.modules.brain.brain_performance_integration import IntegratedBrainPerformanceSystem
except ImportError:
    IntegratedBrainPerformanceSystem = None


class HealthStatus(Enum):
    """System health status levels"""
    EXCELLENT = "excellent"    # 90-100%
    GOOD = "good"             # 80-89%
    WARNING = "warning"       # 60-79%
    CRITICAL = "critical"     # 40-59%
    FAILING = "failing"       # <40%


class HealthTrend(Enum):
    """Health trend directions"""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    RAPID_DECLINE = "rapid_decline"


@dataclass
class HealthPrediction:
    """Health prediction data structure"""
    predicted_health_score: float
    confidence_level: float
    time_horizon_hours: int
    predicted_status: HealthStatus
    risk_factors: List[str]
    recommended_actions: List[str]


@dataclass
class AutoHealingAction:
    """Auto-healing action data structure"""
    action_id: str
    timestamp: datetime
    action_type: str
    target_component: str
    description: str
    success: bool
    improvement_achieved: float
    details: Dict[str, Any]


class BrainHealthMonitor:
    """
    Advanced brain health monitoring system for CORTEX 3.0.
    
    Features:
    - Real-time health assessment
    - Predictive health analytics
    - Trend analysis and forecasting
    - Auto-healing triggers
    - Component-specific health tracking
    - Performance correlation analysis
    """
    
    def __init__(self, 
                 dashboard: RealTimeMetricsDashboard,
                 brain_system = None,  # IntegratedBrainPerformanceSystem
                 monitoring_config: Dict[str, Any] = None):
        """
        Initialize brain health monitoring system.
        
        Args:
            dashboard: Real-time metrics dashboard
            brain_system: Brain optimization system
            monitoring_config: Health monitoring configuration
        """
        self.dashboard = dashboard
        self.brain_system = brain_system
        self.config = monitoring_config or self._default_monitoring_config()
        
        # Health tracking
        self.health_history: List[Tuple[datetime, float]] = []
        self.component_health_history: Dict[str, List[Tuple[datetime, float]]] = {
            'data_collectors': [],
            'brain_performance': [],
            'cache_system': [],
            'memory_manager': [],
            'template_system': [],
            'workspace_health': []
        }
        
        # Predictive analytics
        self.health_predictions: List[HealthPrediction] = []
        self.trend_analysis_window_hours = self.config.get('trend_window_hours', 6)
        
        # Auto-healing
        self.auto_healing_enabled = self.config.get('auto_healing_enabled', True)
        self.healing_actions: List[AutoHealingAction] = []
        self.healing_cooldown_minutes = self.config.get('healing_cooldown_minutes', 30)
        self.last_healing_action = None
        
        # Monitoring state
        self.monitoring_active = False
        self.monitoring_thread = None
        self.stop_monitoring = False
        
        # Logger
        self.logger = logging.getLogger(__name__)
        self.logger.info("Brain health monitoring system initialized")
    
    def _default_monitoring_config(self) -> Dict[str, Any]:
        """Get default monitoring configuration."""
        return {
            'auto_healing_enabled': True,
            'trend_window_hours': 6,
            'prediction_horizon_hours': 24,
            'healing_cooldown_minutes': 30,
            'health_check_interval_seconds': 60,
            'prediction_confidence_threshold': 0.7,
            'auto_healing_thresholds': {
                'critical_health_threshold': 40,
                'declining_trend_threshold': -10,  # % decline over window
                'component_failure_threshold': 3   # Number of failing components
            },
            'component_weights': {
                'data_collectors': 0.25,
                'brain_performance': 0.30,
                'cache_system': 0.20,
                'memory_manager': 0.15,
                'template_system': 0.05,
                'workspace_health': 0.05
            }
        }
    
    def start_health_monitoring(self):
        """Start real-time health monitoring."""
        if self.monitoring_active:
            return
        
        self.stop_monitoring = False
        self.monitoring_thread = threading.Thread(
            target=self._health_monitoring_loop,
            daemon=True
        )
        self.monitoring_thread.start()
        self.monitoring_active = True
        
        self.logger.info("Brain health monitoring started")
    
    def stop_health_monitoring(self):
        """Stop real-time health monitoring."""
        self.stop_monitoring = True
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=10)
        self.monitoring_active = False
        
        self.logger.info("Brain health monitoring stopped")
    
    def get_comprehensive_health_assessment(self) -> Dict[str, Any]:
        """Get comprehensive health assessment."""
        try:
            # Get latest metrics from dashboard
            dashboard_state = self.dashboard.get_current_dashboard_state()
            latest_metrics = dashboard_state.get('latest_metrics', {})
            
            if not latest_metrics:
                return {'error': 'No metrics available for health assessment'}
            
            # Calculate overall health score
            overall_health = self._calculate_overall_health_score(latest_metrics)
            health_status = self._determine_health_status(overall_health)
            
            # Calculate component health scores
            component_health = self._calculate_component_health_scores(latest_metrics)
            
            # Analyze health trends
            health_trend = self._analyze_health_trends()
            
            # Generate health predictions
            predictions = self._generate_health_predictions()
            
            # Identify risk factors
            risk_factors = self._identify_risk_factors(latest_metrics, component_health)
            
            # Generate recommendations
            recommendations = self._generate_health_recommendations(
                overall_health, component_health, risk_factors
            )
            
            # Check for auto-healing triggers
            auto_healing_status = self._check_auto_healing_triggers(
                overall_health, component_health, health_trend
            )
            
            assessment = {
                'timestamp': datetime.now().isoformat(),
                'overall_health': {
                    'score': overall_health,
                    'status': health_status.value,
                    'trend': health_trend.value if health_trend else 'unknown'
                },
                'component_health': component_health,
                'predictions': [
                    {
                        'predicted_score': p.predicted_health_score,
                        'confidence': p.confidence_level,
                        'horizon_hours': p.time_horizon_hours,
                        'predicted_status': p.predicted_status.value,
                        'risk_factors': p.risk_factors,
                        'recommendations': p.recommended_actions
                    } for p in predictions
                ],
                'risk_factors': risk_factors,
                'recommendations': recommendations,
                'auto_healing': auto_healing_status,
                'recent_alerts': [
                    {
                        'severity': alert.severity.value,
                        'component': alert.component,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat()
                    }
                    for alert in latest_metrics.get('active_alerts', [])[-5:]
                ]
            }
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Failed to generate health assessment: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def _calculate_overall_health_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate overall health score from metrics."""
        weights = self.config['component_weights']
        
        # Data collectors health (25%)
        collectors_active = metrics.get('collectors_active', 0)
        collectors_total = metrics.get('collectors_total', 1)
        collection_success = metrics.get('collection_success_rate', 0)
        avg_collection_time = metrics.get('avg_collection_time_ms', 100)
        
        collectors_health = (
            (collectors_active / collectors_total) * 30 +  # Availability
            collection_success * 50 +                      # Success rate
            max(0, (200 - avg_collection_time) / 200) * 20 # Performance
        )
        
        # Brain performance health (30%)
        brain_health = metrics.get('brain_health_score', 0)
        tier1_perf = min(100, max(0, (100 - metrics.get('tier1_performance_ms', 50)) / 100 * 100))
        tier2_perf = min(100, max(0, (300 - metrics.get('tier2_performance_ms', 150)) / 300 * 100))
        tier3_perf = min(100, max(0, (400 - metrics.get('tier3_performance_ms', 200)) / 400 * 100))
        
        brain_performance_health = (brain_health + tier1_perf + tier2_perf + tier3_perf) / 4
        
        # Cache system health (20%)
        cache_hit_rate = metrics.get('cache_hit_rate', 0)
        cache_memory = metrics.get('cache_memory_mb', 0)
        cache_health = (
            cache_hit_rate * 80 +  # Hit rate is primary
            min(20, max(0, (100 - cache_memory) / 100 * 20))  # Memory efficiency
        )
        
        # Memory manager health (15%)
        memory_usage = metrics.get('memory_usage_mb', 0)
        memory_pressure = metrics.get('memory_pressure', 'low')
        memory_pressure_scores = {
            'low': 100, 'medium': 80, 'high': 50, 'critical': 20
        }
        memory_health = (
            memory_pressure_scores.get(memory_pressure, 50) * 0.7 +
            max(0, (300 - memory_usage) / 300 * 100) * 0.3
        )
        
        # Template system health (5%)
        template_success = metrics.get('template_success_rate', 0)
        template_response_time = metrics.get('avg_template_response_time_ms', 50)
        template_health = (
            template_success * 70 +
            max(0, (150 - template_response_time) / 150 * 30)
        )
        
        # Workspace health (5%)
        workspace_health = metrics.get('workspace_health_score', 0)
        
        # Calculate weighted overall health
        overall_health = (
            collectors_health * weights['data_collectors'] +
            brain_performance_health * weights['brain_performance'] +
            cache_health * weights['cache_system'] +
            memory_health * weights['memory_manager'] +
            template_health * weights['template_system'] +
            workspace_health * weights['workspace_health']
        )
        
        return min(100, max(0, overall_health))
    
    def _calculate_component_health_scores(self, metrics: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Calculate individual component health scores."""
        component_health = {}
        
        # Data collectors
        collectors_active = metrics.get('collectors_active', 0)
        collectors_total = metrics.get('collectors_total', 1)
        collection_success = metrics.get('collection_success_rate', 0)
        collectors_score = (collectors_active / collectors_total) * 50 + collection_success * 50
        
        component_health['data_collectors'] = {
            'score': collectors_score,
            'status': self._determine_health_status(collectors_score).value,
            'metrics': {
                'active_collectors': collectors_active,
                'total_collectors': collectors_total,
                'success_rate': collection_success
            }
        }
        
        # Brain performance
        brain_score = metrics.get('brain_health_score', 0)
        component_health['brain_performance'] = {
            'score': brain_score,
            'status': self._determine_health_status(brain_score).value,
            'metrics': {
                'tier1_ms': metrics.get('tier1_performance_ms', 0),
                'tier2_ms': metrics.get('tier2_performance_ms', 0),
                'tier3_ms': metrics.get('tier3_performance_ms', 0)
            }
        }
        
        # Cache system
        cache_score = metrics.get('cache_hit_rate', 0) * 100
        component_health['cache_system'] = {
            'score': cache_score,
            'status': self._determine_health_status(cache_score).value,
            'metrics': {
                'hit_rate': metrics.get('cache_hit_rate', 0),
                'memory_mb': metrics.get('cache_memory_mb', 0)
            }
        }
        
        # Memory manager
        memory_pressure = metrics.get('memory_pressure', 'low')
        memory_pressure_scores = {'low': 90, 'medium': 70, 'high': 40, 'critical': 10}
        memory_score = memory_pressure_scores.get(memory_pressure, 50)
        
        component_health['memory_manager'] = {
            'score': memory_score,
            'status': self._determine_health_status(memory_score).value,
            'metrics': {
                'usage_mb': metrics.get('memory_usage_mb', 0),
                'pressure': memory_pressure
            }
        }
        
        # Template system
        template_score = metrics.get('template_success_rate', 0) * 100
        component_health['template_system'] = {
            'score': template_score,
            'status': self._determine_health_status(template_score).value,
            'metrics': {
                'success_rate': metrics.get('template_success_rate', 0),
                'avg_response_ms': metrics.get('avg_template_response_time_ms', 0)
            }
        }
        
        # Workspace health
        workspace_score = metrics.get('workspace_health_score', 0)
        component_health['workspace_health'] = {
            'score': workspace_score,
            'status': self._determine_health_status(workspace_score).value,
            'metrics': {
                'files_monitored': metrics.get('files_monitored', 0),
                'build_status': metrics.get('build_status', 'unknown')
            }
        }
        
        return component_health
    
    def _determine_health_status(self, score: float) -> HealthStatus:
        """Determine health status from score."""
        if score >= 90:
            return HealthStatus.EXCELLENT
        elif score >= 80:
            return HealthStatus.GOOD
        elif score >= 60:
            return HealthStatus.WARNING
        elif score >= 40:
            return HealthStatus.CRITICAL
        else:
            return HealthStatus.FAILING
    
    def _analyze_health_trends(self) -> Optional[HealthTrend]:
        """Analyze health trends over time."""
        if len(self.health_history) < 3:
            return None
        
        # Look at recent trend
        window_start = datetime.now() - timedelta(hours=self.trend_analysis_window_hours)
        recent_scores = [
            score for timestamp, score in self.health_history
            if timestamp >= window_start
        ]
        
        if len(recent_scores) < 3:
            return HealthTrend.STABLE
        
        # Calculate trend
        start_avg = sum(recent_scores[:len(recent_scores)//3]) / (len(recent_scores)//3)
        end_avg = sum(recent_scores[-len(recent_scores)//3:]) / (len(recent_scores)//3)
        
        change_percent = (end_avg - start_avg) / start_avg * 100 if start_avg > 0 else 0
        
        if change_percent > 5:
            return HealthTrend.IMPROVING
        elif change_percent < -15:
            return HealthTrend.RAPID_DECLINE
        elif change_percent < -5:
            return HealthTrend.DECLINING
        else:
            return HealthTrend.STABLE
    
    def _generate_health_predictions(self) -> List[HealthPrediction]:
        """Generate health predictions using trend analysis."""
        predictions = []
        
        if len(self.health_history) < 5:
            return predictions
        
        # Simple linear trend prediction
        recent_scores = [score for _, score in self.health_history[-10:]]
        
        # Calculate trend slope
        x_values = list(range(len(recent_scores)))
        n = len(recent_scores)
        
        if n < 2:
            return predictions
        
        # Linear regression
        x_mean = sum(x_values) / n
        y_mean = sum(recent_scores) / n
        
        numerator = sum((x_values[i] - x_mean) * (recent_scores[i] - y_mean) for i in range(n))
        denominator = sum((x_values[i] - x_mean) ** 2 for i in range(n))
        
        if denominator == 0:
            return predictions
        
        slope = numerator / denominator
        intercept = y_mean - slope * x_mean
        
        # Predict for different horizons
        for hours in [1, 6, 24]:
            # Assume 1 data point per hour for prediction
            future_x = n + hours
            predicted_score = slope * future_x + intercept
            
            # Clamp to valid range
            predicted_score = max(0, min(100, predicted_score))
            
            # Calculate confidence based on trend consistency
            confidence = self._calculate_prediction_confidence(recent_scores, slope)
            
            # Determine risk factors
            risk_factors = []
            if predicted_score < 70:
                risk_factors.append("Declining health trend")
            if slope < -2:
                risk_factors.append("Rapid performance degradation")
            
            # Generate recommendations
            recommendations = self._generate_prediction_recommendations(predicted_score, slope)
            
            prediction = HealthPrediction(
                predicted_health_score=predicted_score,
                confidence_level=confidence,
                time_horizon_hours=hours,
                predicted_status=self._determine_health_status(predicted_score),
                risk_factors=risk_factors,
                recommended_actions=recommendations
            )
            
            predictions.append(prediction)
        
        return predictions
    
    def _calculate_prediction_confidence(self, scores: List[float], slope: float) -> float:
        """Calculate confidence level for predictions."""
        if len(scores) < 3:
            return 0.5
        
        # Calculate variance in scores
        mean_score = sum(scores) / len(scores)
        variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
        
        # Lower variance = higher confidence
        variance_confidence = max(0, min(1, (100 - variance) / 100))
        
        # Consistent trend = higher confidence
        trend_changes = sum(
            1 for i in range(1, len(scores) - 1)
            if (scores[i] - scores[i-1]) * (scores[i+1] - scores[i]) < 0
        )
        trend_confidence = max(0, 1 - (trend_changes / (len(scores) - 2)))
        
        # Combine confidences
        overall_confidence = (variance_confidence + trend_confidence) / 2
        
        return overall_confidence
    
    def _generate_prediction_recommendations(self, predicted_score: float, slope: float) -> List[str]:
        """Generate recommendations based on predictions."""
        recommendations = []
        
        if predicted_score < 60:
            recommendations.append("Immediate optimization required")
            recommendations.append("Consider triggering comprehensive brain optimization")
        
        if slope < -3:
            recommendations.append("Address rapidly declining performance")
            recommendations.append("Investigate resource bottlenecks")
        
        if predicted_score < 80:
            recommendations.append("Proactive performance monitoring needed")
            recommendations.append("Review optimization thresholds")
        
        return recommendations
    
    def _identify_risk_factors(self, metrics: Dict[str, Any], component_health: Dict[str, Dict[str, Any]]) -> List[str]:
        """Identify current risk factors."""
        risk_factors = []
        
        # Component-specific risks
        for component, health in component_health.items():
            if health['score'] < 60:
                risk_factors.append(f"{component} performance degraded ({health['score']:.1f}%)")
        
        # Metric-specific risks
        if metrics.get('collection_success_rate', 1) < 0.8:
            risk_factors.append("Data collection reliability issues")
        
        if metrics.get('cache_hit_rate', 1) < 0.6:
            risk_factors.append("Cache performance severely degraded")
        
        if metrics.get('memory_pressure') in ['high', 'critical']:
            risk_factors.append("Memory pressure affecting performance")
        
        # Alert-based risks
        active_alerts = metrics.get('active_alerts', [])
        critical_alerts = [a for a in active_alerts if a.severity == MetricSeverity.CRITICAL]
        if critical_alerts:
            risk_factors.append(f"{len(critical_alerts)} critical alerts active")
        
        return risk_factors
    
    def _generate_health_recommendations(self, 
                                       overall_health: float, 
                                       component_health: Dict[str, Dict[str, Any]], 
                                       risk_factors: List[str]) -> List[str]:
        """Generate health improvement recommendations."""
        recommendations = []
        
        # Overall health recommendations
        if overall_health < 70:
            recommendations.append("System health requires immediate attention")
            recommendations.append("Consider triggering comprehensive optimization")
        
        # Component-specific recommendations
        for component, health in component_health.items():
            if health['score'] < 70:
                if component == 'data_collectors':
                    recommendations.append("Restart failed data collectors")
                    recommendations.append("Check collector configuration and dependencies")
                elif component == 'brain_performance':
                    recommendations.append("Optimize brain tier performance")
                    recommendations.append("Clear query caches and rebuild indexes")
                elif component == 'cache_system':
                    recommendations.append("Clear and rebuild cache system")
                    recommendations.append("Adjust cache size and retention policies")
                elif component == 'memory_manager':
                    recommendations.append("Release unused memory allocations")
                    recommendations.append("Trigger garbage collection")
        
        # Risk-based recommendations
        if "Memory pressure affecting performance" in risk_factors:
            recommendations.append("Increase memory limits or reduce allocation")
        
        if "Data collection reliability issues" in risk_factors:
            recommendations.append("Review collector error logs and restart services")
        
        return list(set(recommendations))  # Remove duplicates
    
    def _check_auto_healing_triggers(self, 
                                   overall_health: float,
                                   component_health: Dict[str, Dict[str, Any]],
                                   health_trend: Optional[HealthTrend]) -> Dict[str, Any]:
        """Check if auto-healing should be triggered."""
        auto_healing_status = {
            'enabled': self.auto_healing_enabled,
            'trigger_conditions_met': False,
            'cooldown_active': False,
            'next_action_available': None,
            'last_action': None
        }
        
        if not self.auto_healing_enabled:
            return auto_healing_status
        
        # Check cooldown
        if (self.last_healing_action and 
            datetime.now() - self.last_healing_action < timedelta(minutes=self.healing_cooldown_minutes)):
            auto_healing_status['cooldown_active'] = True
            auto_healing_status['next_action_available'] = (
                self.last_healing_action + timedelta(minutes=self.healing_cooldown_minutes)
            ).isoformat()
            return auto_healing_status
        
        thresholds = self.config['auto_healing_thresholds']
        
        # Check trigger conditions
        triggers = []
        
        # Critical overall health
        if overall_health < thresholds['critical_health_threshold']:
            triggers.append(f"Overall health critical: {overall_health:.1f}%")
        
        # Rapid health decline
        if health_trend == HealthTrend.RAPID_DECLINE:
            triggers.append("Rapid health decline detected")
        
        # Multiple component failures
        failing_components = sum(
            1 for health in component_health.values()
            if health['score'] < 50
        )
        if failing_components >= thresholds['component_failure_threshold']:
            triggers.append(f"{failing_components} components failing")
        
        if triggers:
            auto_healing_status['trigger_conditions_met'] = True
            auto_healing_status['triggered_by'] = triggers
            
            # Trigger auto-healing if not in cooldown
            if not auto_healing_status['cooldown_active']:
                healing_action = self._trigger_auto_healing(overall_health, component_health)
                auto_healing_status['action_triggered'] = healing_action
        
        # Include last action info
        if self.healing_actions:
            last_action = self.healing_actions[-1]
            auto_healing_status['last_action'] = {
                'timestamp': last_action.timestamp.isoformat(),
                'action_type': last_action.action_type,
                'success': last_action.success,
                'improvement': last_action.improvement_achieved
            }
        
        return auto_healing_status
    
    def _trigger_auto_healing(self, 
                            overall_health: float, 
                            component_health: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Trigger appropriate auto-healing action."""
        self.logger.warning(f"Auto-healing triggered - Overall health: {overall_health:.1f}%")
        
        # Determine best healing action
        healing_action = self._determine_optimal_healing_action(overall_health, component_health)
        
        # Execute healing action
        result = self._execute_healing_action(healing_action)
        
        # Record action
        action_record = AutoHealingAction(
            action_id=f"heal_{int(time.time())}",
            timestamp=datetime.now(),
            action_type=healing_action['type'],
            target_component=healing_action.get('target', 'system'),
            description=healing_action['description'],
            success=result['success'],
            improvement_achieved=result.get('improvement', 0.0),
            details=result
        )
        
        self.healing_actions.append(action_record)
        self.last_healing_action = datetime.now()
        
        return {
            'action_id': action_record.action_id,
            'action_type': action_record.action_type,
            'success': action_record.success,
            'improvement': action_record.improvement_achieved,
            'details': action_record.details
        }
    
    def _determine_optimal_healing_action(self, 
                                        overall_health: float, 
                                        component_health: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Determine the most appropriate healing action."""
        # Find the worst-performing component
        worst_component = min(component_health.items(), key=lambda x: x[1]['score'])
        worst_component_name, worst_component_health = worst_component
        
        # Choose action based on worst component and overall health
        if overall_health < 30:
            return {
                'type': 'comprehensive_optimization',
                'target': 'system',
                'description': 'Comprehensive system optimization due to critical health'
            }
        elif worst_component_health['score'] < 40:
            return {
                'type': 'component_restart',
                'target': worst_component_name,
                'description': f'Restart {worst_component_name} due to poor performance'
            }
        else:
            return {
                'type': 'cache_optimization',
                'target': 'cache_system',
                'description': 'Cache optimization to improve overall performance'
            }
    
    def _execute_healing_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute auto-healing action."""
        action_type = action['type']
        
        try:
            if action_type == 'comprehensive_optimization':
                return self._execute_comprehensive_optimization()
            elif action_type == 'component_restart':
                return self._execute_component_restart(action['target'])
            elif action_type == 'cache_optimization':
                return self._execute_cache_optimization()
            else:
                return {'success': False, 'error': f'Unknown action type: {action_type}'}
                
        except Exception as e:
            self.logger.error(f"Auto-healing action failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_comprehensive_optimization(self) -> Dict[str, Any]:
        """Execute comprehensive system optimization."""
        if not self.brain_system:
            return {'success': False, 'error': 'Brain system not available'}
        
        try:
            optimization_results = self.brain_system.trigger_comprehensive_optimization()
            
            return {
                'success': optimization_results['success'],
                'improvement': optimization_results.get('overall_improvement', 0.0),
                'details': optimization_results
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _execute_component_restart(self, component: str) -> Dict[str, Any]:
        """Execute component restart."""
        if component == 'data_collectors' and self.dashboard.collector_manager:
            try:
                # Stop and restart collectors
                stop_results = self.dashboard.collector_manager.stop_all_collectors()
                time.sleep(2)  # Brief pause
                start_results = self.dashboard.collector_manager.start_all_collectors()
                
                success = all(start_results.values())
                return {
                    'success': success,
                    'improvement': 50.0 if success else 0.0,  # Estimated improvement
                    'details': {'stop_results': stop_results, 'start_results': start_results}
                }
            except Exception as e:
                return {'success': False, 'error': str(e)}
        
        return {'success': False, 'error': f'Component restart not implemented for {component}'}
    
    def _execute_cache_optimization(self) -> Dict[str, Any]:
        """Execute cache optimization."""
        if not self.brain_system:
            return {'success': False, 'error': 'Brain system not available'}
        
        try:
            # Optimize query cache
            cache_results = self.brain_system.query_cache.cache_engine.optimize_cache()
            
            return {
                'success': True,
                'improvement': 25.0,  # Estimated improvement
                'details': cache_results
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _health_monitoring_loop(self):
        """Health monitoring loop."""
        self.logger.info("Brain health monitoring loop started")
        
        while not self.stop_monitoring:
            try:
                # Get current health assessment
                assessment = self.get_comprehensive_health_assessment()
                
                if 'overall_health' in assessment:
                    # Record health score
                    current_health = assessment['overall_health']['score']
                    self.health_history.append((datetime.now(), current_health))
                    
                    # Keep limited history
                    if len(self.health_history) > 200:
                        self.health_history = self.health_history[-200:]
                    
                    # Log health status periodically
                    if len(self.health_history) % 10 == 0:
                        self.logger.info(
                            f"Brain health: {current_health:.1f}% "
                            f"({assessment['overall_health']['status']}) - "
                            f"Trend: {assessment['overall_health']['trend']}"
                        )
                
                # Sleep for monitoring interval
                time.sleep(self.config.get('health_check_interval_seconds', 60))
                
            except Exception as e:
                self.logger.error(f"Health monitoring loop error: {e}")
                time.sleep(30)  # Wait before retrying
        
        self.logger.info("Brain health monitoring loop stopped")


# Convenience functions for health monitoring
def create_brain_health_monitor(dashboard: RealTimeMetricsDashboard,
                              brain_system = None,  # IntegratedBrainPerformanceSystem
                              config: Dict[str, Any] = None) -> BrainHealthMonitor:
    """
    Create and start brain health monitoring system.
    
    Args:
        dashboard: Real-time metrics dashboard
        brain_system: Brain optimization system
        config: Health monitoring configuration
        
    Returns:
        Initialized BrainHealthMonitor
    """
    monitor = BrainHealthMonitor(dashboard, brain_system, config)
    monitor.start_health_monitoring()
    return monitor


def get_health_summary(monitor: BrainHealthMonitor) -> Dict[str, Any]:
    """
    Get comprehensive health summary.
    
    Args:
        monitor: Health monitoring system
        
    Returns:
        Health assessment summary
    """
    return monitor.get_comprehensive_health_assessment()


if __name__ == "__main__":
    # Test the brain health monitoring system
    print("🏥 CORTEX 3.0 Phase 2 - Brain Health Monitoring System Test")
    print("=" * 75)
    
    # This would typically be run with actual dashboard and brain system
    print("⚠️  Note: Health monitoring requires active dashboard and brain system")
    print("   Use create_brain_health_monitor() with real components for full functionality")
    print()
    
    print("🎯 Brain health monitoring system ready for integration!")
    print("   Features: Real-time assessment + Predictive analytics + Auto-healing")
    print("   Integration: Phase 1 collectors + Phase 2 optimization")