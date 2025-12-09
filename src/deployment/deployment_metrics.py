"""
Deployment Metrics & Analytics

Comprehensive metrics tracking for deployments with health monitoring,
alerting, and integration with existing health reports.

Features:
- Metric recording (duration, gate pass rates, rollbacks, success rate)
- Persistent storage (JSONL format)
- Metric querying and filtering
- Aggregated statistics
- Health threshold checking with alerts
- Report generation
- Trend analysis
- Health report integration

Author: Asif Hussain
Version: 1.0.0
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import CORTEX config
try:
    from src.config import config
    CORTEX_ROOT = Path(config.root_path)
except ImportError:
    # Fallback if config not available
    CORTEX_ROOT = Path(__file__).resolve().parents[3]


class MetricType(Enum):
    """Types of deployment metrics."""
    DEPLOYMENT_DURATION = "deployment_duration"
    PHASE_DURATION = "phase_duration"
    GATE_PASS_RATE = "gate_pass_rate"
    ROLLBACK_COUNT = "rollback_count"
    DEPLOYMENT_SUCCESS = "deployment_success"


class AlertLevel(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class DeploymentMetric:
    """Deployment metric data point."""
    metric_type: MetricType
    value: float
    deployment_id: str
    timestamp: str
    metadata: Optional[Dict] = None


@dataclass
class DeploymentAlert:
    """Deployment health alert."""
    alert_level: AlertLevel
    message: str
    metric_type: MetricType
    timestamp: str
    current_value: Optional[float] = None
    threshold_value: Optional[float] = None


class DeploymentMetricsCollector:
    """Manages deployment metrics collection and analysis."""
    
    # Health thresholds
    MAX_DURATION_SECONDS = 300  # 5 minutes
    MAX_ROLLBACKS_PER_WEEK = 2
    MIN_GATE_PASS_RATE = 0.75  # 75%
    
    def __init__(self, cortex_root: Path = None):
        """
        Initialize metrics collector.
        
        Args:
            cortex_root: Path to CORTEX root (default: from config)
        """
        self.cortex_root = cortex_root or CORTEX_ROOT
        self.metrics_dir = self.cortex_root / "cortex-brain" / "metrics" / "deployments"
        self.metrics_file = self.metrics_dir / "deployment-metrics.jsonl"
        
        # Ensure metrics directory exists
        self.metrics_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"📊 Deployment Metrics Collector initialized: {self.cortex_root}")
    
    def record_metric(
        self,
        metric_type: MetricType,
        value: float,
        deployment_id: str,
        metadata: Optional[Dict] = None
    ) -> DeploymentMetric:
        """
        Record a deployment metric.
        
        Args:
            metric_type: Type of metric
            value: Metric value
            deployment_id: Deployment identifier
            metadata: Additional metadata
            
        Returns:
            DeploymentMetric object
        """
        metric = DeploymentMetric(
            metric_type=metric_type,
            value=value,
            deployment_id=deployment_id,
            timestamp=datetime.now().isoformat(),
            metadata=metadata or {}
        )
        
        # Persist to disk
        self._save_metric(metric)
        
        logger.info(f"📈 Metric recorded: {metric_type.value} = {value} (deployment={deployment_id})")
        
        return metric
    
    def get_metrics(
        self,
        metric_type: Optional[MetricType] = None,
        deployment_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> List[DeploymentMetric]:
        """
        Query metrics with filters.
        
        Args:
            metric_type: Filter by metric type
            deployment_id: Filter by deployment ID
            start_time: Filter by start time
            end_time: Filter by end time
            
        Returns:
            List of matching metrics
        """
        if not self.metrics_file.exists():
            return []
        
        metrics = []
        
        with open(self.metrics_file, 'r') as f:
            for line in f:
                data = json.loads(line)
                
                # Reconstruct metric
                data['metric_type'] = MetricType(data['metric_type'])
                metric = DeploymentMetric(**data)
                
                # Apply filters
                if metric_type and metric.metric_type != metric_type:
                    continue
                
                if deployment_id and metric.deployment_id != deployment_id:
                    continue
                
                metric_time = datetime.fromisoformat(metric.timestamp)
                
                if start_time and metric_time < start_time:
                    continue
                
                if end_time and metric_time > end_time:
                    continue
                
                metrics.append(metric)
        
        return metrics
    
    def get_average_duration(self, days: int = 7) -> float:
        """Calculate average deployment duration."""
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.get_metrics(
            metric_type=MetricType.DEPLOYMENT_DURATION,
            start_time=start_time
        )
        
        if not metrics:
            return 0.0
        
        return sum(m.value for m in metrics) / len(metrics)
    
    def get_success_rate(self, days: int = 7) -> float:
        """Calculate deployment success rate."""
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.get_metrics(
            metric_type=MetricType.DEPLOYMENT_SUCCESS,
            start_time=start_time
        )
        
        if not metrics:
            return 0.0
        
        successes = sum(m.value for m in metrics)
        return successes / len(metrics)
    
    def get_rollback_count(self, days: int = 7) -> int:
        """Get rollback count in time period."""
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.get_metrics(
            metric_type=MetricType.ROLLBACK_COUNT,
            start_time=start_time
        )
        
        return sum(int(m.value) for m in metrics)
    
    def get_average_gate_pass_rate(self, days: int = 7) -> float:
        """Calculate average gate pass rate."""
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.get_metrics(
            metric_type=MetricType.GATE_PASS_RATE,
            start_time=start_time
        )
        
        if not metrics:
            return 0.0
        
        return sum(m.value for m in metrics) / len(metrics)
    
    def check_health_thresholds(self, days: int = 7) -> List[DeploymentAlert]:
        """
        Check if metrics exceed health thresholds.
        
        Args:
            days: Number of days to check
            
        Returns:
            List of alerts for threshold violations
        """
        alerts = []
        start_time = datetime.now() - timedelta(days=days)
        
        # Check deployment duration
        avg_duration = self.get_average_duration(days=days)
        if avg_duration > self.MAX_DURATION_SECONDS:
            alerts.append(self.create_alert(
                alert_level=AlertLevel.WARNING,
                message=f"Average deployment duration ({avg_duration:.1f}s) exceeds threshold ({self.MAX_DURATION_SECONDS}s)",
                metric_type=MetricType.DEPLOYMENT_DURATION,
                current_value=avg_duration,
                threshold_value=self.MAX_DURATION_SECONDS
            ))
        
        # Check rollback frequency
        rollback_count = self.get_rollback_count(days=7)  # Always check 1 week
        if rollback_count > self.MAX_ROLLBACKS_PER_WEEK:
            alerts.append(self.create_alert(
                alert_level=AlertLevel.WARNING,
                message=f"Rollback frequency ({rollback_count} rollbacks/week) exceeds threshold ({self.MAX_ROLLBACKS_PER_WEEK})",
                metric_type=MetricType.ROLLBACK_COUNT,
                current_value=float(rollback_count),
                threshold_value=float(self.MAX_ROLLBACKS_PER_WEEK)
            ))
        
        # Check gate pass rate
        avg_gate_pass = self.get_average_gate_pass_rate(days=days)
        if avg_gate_pass > 0 and avg_gate_pass < self.MIN_GATE_PASS_RATE:
            alerts.append(self.create_alert(
                alert_level=AlertLevel.WARNING,
                message=f"Average gate pass rate ({avg_gate_pass:.1%}) below threshold ({self.MIN_GATE_PASS_RATE:.1%})",
                metric_type=MetricType.GATE_PASS_RATE,
                current_value=avg_gate_pass,
                threshold_value=self.MIN_GATE_PASS_RATE
            ))
        
        return alerts
    
    def create_alert(
        self,
        alert_level: AlertLevel,
        message: str,
        metric_type: MetricType,
        current_value: Optional[float] = None,
        threshold_value: Optional[float] = None
    ) -> DeploymentAlert:
        """Create a deployment alert."""
        return DeploymentAlert(
            alert_level=alert_level,
            message=message,
            metric_type=metric_type,
            timestamp=datetime.now().isoformat(),
            current_value=current_value,
            threshold_value=threshold_value
        )
    
    def generate_report(self, days: int = 7) -> Dict:
        """
        Generate comprehensive metrics report.
        
        Args:
            days: Number of days to include in report
            
        Returns:
            Report dictionary
        """
        start_time = datetime.now() - timedelta(days=days)
        
        # Get all deployments in time period
        duration_metrics = self.get_metrics(
            metric_type=MetricType.DEPLOYMENT_DURATION,
            start_time=start_time
        )
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "period_days": days,
            "total_deployments": len(duration_metrics),
            "average_duration": self.get_average_duration(days=days),
            "success_rate": self.get_success_rate(days=days),
            "rollback_count": self.get_rollback_count(days=days),
            "average_gate_pass_rate": self.get_average_gate_pass_rate(days=days),
            "alerts": [
                {
                    "level": alert.alert_level.value,
                    "message": alert.message,
                    "metric_type": alert.metric_type.value,
                    "current_value": alert.current_value,
                    "threshold_value": alert.threshold_value
                }
                for alert in self.check_health_thresholds(days=days)
            ]
        }
        
        return report
    
    def save_report(self, days: int = 7) -> Path:
        """
        Save metrics report to disk.
        
        Args:
            days: Number of days to include
            
        Returns:
            Path to saved report
        """
        report = self.generate_report(days=days)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = self.metrics_dir / f"deployment-metrics-report-{timestamp}.json"
        
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"📊 Report saved: {report_path}")
        
        return report_path
    
    def export_for_health_report(self, days: int = 7) -> Dict:
        """
        Export metrics in health report format.
        
        Args:
            days: Number of days to include
            
        Returns:
            Health report compatible data
        """
        health_score = self.calculate_health_score(days=days)
        
        return {
            "deployment_metrics": self.generate_report(days=days),
            "health_score": health_score,
            "status": "healthy" if health_score > 80 else "degraded" if health_score > 60 else "unhealthy"
        }
    
    def calculate_health_score(self, days: int = 7) -> float:
        """
        Calculate deployment health score (0-100).
        
        Args:
            days: Number of days to consider
            
        Returns:
            Health score
        """
        score = 100.0
        
        # Duration penalty (up to -20 points)
        avg_duration = self.get_average_duration(days=days)
        if avg_duration > 0:
            duration_ratio = avg_duration / self.MAX_DURATION_SECONDS
            if duration_ratio > 1.0:
                score -= min(20, (duration_ratio - 1.0) * 20)
        
        # Success rate bonus/penalty (up to ±30 points)
        success_rate = self.get_success_rate(days=days)
        if success_rate > 0:
            score = score * success_rate + (score * (1 - success_rate) * 0.4)
        
        # Gate pass rate penalty (up to -25 points)
        gate_pass = self.get_average_gate_pass_rate(days=days)
        if gate_pass > 0 and gate_pass < self.MIN_GATE_PASS_RATE:
            gate_penalty = (self.MIN_GATE_PASS_RATE - gate_pass) * 100
            score -= min(25, gate_penalty)
        
        # Rollback penalty (up to -25 points)
        rollback_count = self.get_rollback_count(days=7)
        if rollback_count > self.MAX_ROLLBACKS_PER_WEEK:
            rollback_penalty = (rollback_count - self.MAX_ROLLBACKS_PER_WEEK) * 10
            score -= min(25, rollback_penalty)
        
        return max(0.0, min(100.0, score))
    
    def analyze_trend(self, metric_type: MetricType, days: int = 7) -> Dict:
        """
        Analyze trend for a metric type.
        
        Args:
            metric_type: Type of metric to analyze
            days: Number of days to analyze
            
        Returns:
            Trend analysis
        """
        start_time = datetime.now() - timedelta(days=days)
        metrics = self.get_metrics(metric_type=metric_type, start_time=start_time)
        
        if len(metrics) < 2:
            return {"direction": "insufficient_data"}
        
        # Simple trend detection: compare first half vs second half
        midpoint = len(metrics) // 2
        first_half_avg = sum(m.value for m in metrics[:midpoint]) / midpoint
        second_half_avg = sum(m.value for m in metrics[midpoint:]) / (len(metrics) - midpoint)
        
        change_pct = ((second_half_avg - first_half_avg) / first_half_avg * 100) if first_half_avg > 0 else 0
        
        if abs(change_pct) < 5:
            direction = "stable"
        elif change_pct > 0:
            direction = "increasing"
        else:
            direction = "decreasing"
        
        return {
            "direction": direction,
            "change_percentage": change_pct,
            "first_half_average": first_half_avg,
            "second_half_average": second_half_avg
        }
    
    def _save_metric(self, metric: DeploymentMetric) -> None:
        """Save metric to JSONL file."""
        # Convert metric to dict
        metric_dict = asdict(metric)
        # Convert enum to string
        metric_dict['metric_type'] = metric.metric_type.value
        
        # Append to file
        with open(self.metrics_file, 'a') as f:
            f.write(json.dumps(metric_dict) + '\n')


# Convenience functions

def generate_metrics_report(days: int = 7, cortex_root: Path = None) -> Dict:
    """
    Generate metrics report (convenience function).
    
    Args:
        days: Number of days to include
        cortex_root: CORTEX root path
        
    Returns:
        Report dictionary
    """
    collector = DeploymentMetricsCollector(cortex_root=cortex_root)
    return collector.generate_report(days=days)


def check_health_thresholds(days: int = 7, cortex_root: Path = None) -> List[DeploymentAlert]:
    """
    Check health thresholds (convenience function).
    
    Args:
        days: Number of days to check
        cortex_root: CORTEX root path
        
    Returns:
        List of alerts
    """
    collector = DeploymentMetricsCollector(cortex_root=cortex_root)
    return collector.check_health_thresholds(days=days)


if __name__ == "__main__":
    print("=" * 60)
    print("Deployment Metrics & Analytics - Direct Test")
    print("=" * 60)
    
    # Test metrics collection
    collector = DeploymentMetricsCollector()
    
    print("\n[Test 1] Recording metrics...")
    collector.record_metric(MetricType.DEPLOYMENT_DURATION, 120.0, "deploy-test-1")
    collector.record_metric(MetricType.GATE_PASS_RATE, 0.95, "deploy-test-1")
    collector.record_metric(MetricType.DEPLOYMENT_SUCCESS, 1, "deploy-test-1")
    print("✅ Metrics recorded")
    
    print("\n[Test 2] Generating report...")
    report = collector.generate_report(days=7)
    print(f"✅ Report generated:")
    print(f"   Total deployments: {report['total_deployments']}")
    print(f"   Success rate: {report['success_rate']:.1%}")
    print(f"   Health score: {collector.calculate_health_score():.1f}")
    
    print("\n[Test 3] Checking health thresholds...")
    alerts = collector.check_health_thresholds()
    print(f"✅ Found {len(alerts)} alert(s)")
    
    print("\n" + "=" * 60)
    print("✅ Metrics tests complete")
    print("=" * 60)
