"""
AC-ROLLOUT-SIMPLE-003: Deployment Monitoring
Track deployment health metrics and trigger alerts/rollbacks.
"""
from enum import Enum
from typing import Dict
from src.orchestrators.rollout_gates import RolloutGateManager


class HealthStatus(Enum):
    """Deployment health status."""
    HEALTHY = "healthy"          # >=95% success
    DEGRADED = "degraded"        # 80-95% success
    UNHEALTHY = "unhealthy"      # <80% success


class DeploymentMonitor:
    """
    Monitors deployment health and triggers alerts.
    
    Health thresholds:
    - HEALTHY: >=95% success rate
    - DEGRADED: 80-95% success rate (warning)
    - UNHEALTHY: <80% success rate (alert + consider rollback)
    """
    
    HEALTHY_THRESHOLD = 0.95
    DEGRADED_THRESHOLD = 0.80
    
    def __init__(self, gate_manager: RolloutGateManager):
        self.gate_manager = gate_manager
        self._metrics: Dict[str, Dict] = {}
    
    def record_metric(self, feature_id: str, success: bool):
        """
        Record deployment metric.
        
        Args:
            feature_id: Feature being monitored
            success: Whether operation succeeded
        """
        if feature_id not in self._metrics:
            self._metrics[feature_id] = {
                'total': 0,
                'successes': 0,
                'failures': 0
            }
        
        self._metrics[feature_id]['total'] += 1
        if success:
            self._metrics[feature_id]['successes'] += 1
        else:
            self._metrics[feature_id]['failures'] += 1
    
    def get_metrics(self, feature_id: str) -> Dict:
        """Get metrics for feature."""
        return self._metrics.get(feature_id, {
            'total': 0,
            'successes': 0,
            'failures': 0
        })
    
    def get_health_status(self, feature_id: str) -> HealthStatus:
        """
        Calculate health status from metrics.
        
        Args:
            feature_id: Feature to check
            
        Returns:
            HealthStatus enum value
        """
        metrics = self.get_metrics(feature_id)
        
        if metrics['total'] == 0:
            return HealthStatus.HEALTHY  # No data = assume healthy
        
        success_rate = metrics['successes'] / metrics['total']
        
        if success_rate >= self.HEALTHY_THRESHOLD:
            return HealthStatus.HEALTHY
        elif success_rate >= self.DEGRADED_THRESHOLD:
            return HealthStatus.DEGRADED
        else:
            return HealthStatus.UNHEALTHY
    
    def should_trigger_alert(self, feature_id: str) -> bool:
        """Check if feature health should trigger alert."""
        health = self.get_health_status(feature_id)
        return health == HealthStatus.UNHEALTHY
