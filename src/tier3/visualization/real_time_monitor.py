"""
Real-Time Monitor

Real-time monitoring dashboard with WebSocket updates and alert system.
Tracks live metrics and sends notifications for threshold violations.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional, Callable
import sqlite3
from pathlib import Path
import asyncio
import json
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class MonitorConfig:
    """Configuration for real-time monitoring"""
    update_interval_seconds: int = 60  # Check every minute
    acceptance_rate_threshold: float = 0.3  # Alert if below 30%
    success_rate_threshold: float = 0.5  # Alert if below 50%
    enable_alerts: bool = True
    alert_cooldown_minutes: int = 30  # Don't repeat alerts within 30 min


@dataclass
class Alert:
    """Alert notification"""
    level: AlertLevel
    metric: str
    current_value: float
    threshold: float
    timestamp: datetime
    message: str


@dataclass
class LiveMetrics:
    """Current live metrics snapshot"""
    timestamp: datetime
    copilot_acceptance_rate: float
    cortex_success_rate: float
    active_engineers: int
    total_requests_today: int
    alerts: List[Alert]


class RealTimeMonitor:
    """
    Real-time monitoring system for adoption analytics.
    
    Features:
    - Live metrics updates (configurable interval)
    - Threshold-based alerting system
    - Alert cooldown to prevent spam
    - Historical comparison
    - WebSocket-ready data streaming
    - Async/await support for non-blocking operation
    
    Usage:
        config = MonitorConfig(
            update_interval_seconds=60,
            acceptance_rate_threshold=0.3,
            enable_alerts=True
        )
        
        monitor = RealTimeMonitor(
            db_path="/path/to/db",
            config=config
        )
        
        # Synchronous check
        metrics = monitor.get_current_metrics()
        
        # Async monitoring loop
        async def monitor_loop():
            async for metrics in monitor.stream_metrics():
                print(f"Acceptance Rate: {metrics.copilot_acceptance_rate:.1%}")
                for alert in metrics.alerts:
                    print(f"ALERT: {alert.message}")
        
        asyncio.run(monitor_loop())
    """
    
    def __init__(self, db_path: str, config: Optional[MonitorConfig] = None):
        """
        Initialize real-time monitor.
        
        Args:
            db_path: Path to Tier 3 development_context.db
            config: MonitorConfig with monitoring parameters
        """
        self.db_path = Path(db_path)
        self.config = config or MonitorConfig()
        self._alert_history: Dict[str, datetime] = {}
    
    def get_current_metrics(self) -> LiveMetrics:
        """
        Get current metrics snapshot (synchronous).
        
        Returns:
            LiveMetrics with current values and any alerts
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = date.today()
        
        # Get today's Copilot metrics
        cursor.execute("""
            SELECT 
                SUM(acceptances) as total_acceptances,
                SUM(total_suggestions) as total_suggestions,
                COUNT(DISTINCT engineer_hash) as active_engineers
            FROM copilot_metrics
            WHERE metric_date = ?
        """, (today.isoformat(),))
        
        cop_row = cursor.fetchone()
        total_acceptances = cop_row[0] or 0
        total_suggestions = cop_row[1] or 0
        active_engineers = cop_row[2] or 0
        
        acceptance_rate = (
            total_acceptances / total_suggestions 
            if total_suggestions > 0 
            else 0.0
        )
        
        # Get today's CORTEX metrics
        cursor.execute("""
            SELECT 
                SUM(successful_count) as total_successful,
                SUM(total_count) as total_requests
            FROM cortex_usage_metrics
            WHERE metric_date = ?
        """, (today.isoformat(),))
        
        ctx_row = cursor.fetchone()
        total_successful = ctx_row[0] or 0
        total_requests = ctx_row[1] or 0
        
        success_rate = (
            total_successful / total_requests 
            if total_requests > 0 
            else 0.0
        )
        
        conn.close()
        
        # Check for alerts
        alerts = []
        if self.config.enable_alerts:
            alerts.extend(self._check_thresholds(
                acceptance_rate,
                success_rate,
                active_engineers
            ))
        
        return LiveMetrics(
            timestamp=datetime.now(),
            copilot_acceptance_rate=acceptance_rate,
            cortex_success_rate=success_rate,
            active_engineers=active_engineers,
            total_requests_today=total_requests,
            alerts=alerts
        )
    
    async def stream_metrics(self) -> 'AsyncGenerator[LiveMetrics, None]':
        """
        Stream metrics updates (async generator).
        
        Yields:
            LiveMetrics snapshots at configured intervals
            
        Example:
            async for metrics in monitor.stream_metrics():
                print(f"Rate: {metrics.copilot_acceptance_rate:.1%}")
        """
        while True:
            yield self.get_current_metrics()
            await asyncio.sleep(self.config.update_interval_seconds)
    
    def get_historical_comparison(self, days: int = 7) -> Dict[str, Any]:
        """
        Compare current metrics with historical averages.
        
        Args:
            days: Number of days to look back for comparison
            
        Returns:
            Dictionary with current vs historical comparison
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        today = date.today()
        start_date = today - timedelta(days=days)
        
        # Historical averages
        cursor.execute("""
            SELECT 
                AVG(CAST(acceptances AS FLOAT) / NULLIF(total_suggestions, 0)) as avg_acceptance,
                AVG(CAST(successful_count AS FLOAT) / NULLIF(total_count, 0)) as avg_success
            FROM copilot_metrics cm
            LEFT JOIN cortex_usage_metrics cum 
                ON cm.engineer_hash = cum.engineer_hash 
                AND cm.metric_date = cum.metric_date
            WHERE cm.metric_date BETWEEN ? AND ?
                AND cm.metric_date < ?
        """, (start_date.isoformat(), today.isoformat(), today.isoformat()))
        
        row = cursor.fetchone()
        historical_acceptance = row[0] or 0.0
        historical_success = row[1] or 0.0
        
        conn.close()
        
        # Current metrics
        current = self.get_current_metrics()
        
        return {
            'current': {
                'acceptance_rate': current.copilot_acceptance_rate,
                'success_rate': current.cortex_success_rate,
                'active_engineers': current.active_engineers
            },
            'historical_avg': {
                'acceptance_rate': historical_acceptance,
                'success_rate': historical_success
            },
            'comparison': {
                'acceptance_change': current.copilot_acceptance_rate - historical_acceptance,
                'success_change': current.cortex_success_rate - historical_success
            },
            'period_days': days
        }
    
    def _check_thresholds(
        self,
        acceptance_rate: float,
        success_rate: float,
        active_engineers: int
    ) -> List[Alert]:
        """Check metrics against thresholds and generate alerts"""
        alerts = []
        now = datetime.now()
        
        # Check acceptance rate
        if acceptance_rate < self.config.acceptance_rate_threshold:
            alert_key = "acceptance_rate_low"
            if self._should_send_alert(alert_key, now):
                alerts.append(Alert(
                    level=AlertLevel.WARNING,
                    metric="copilot_acceptance_rate",
                    current_value=acceptance_rate,
                    threshold=self.config.acceptance_rate_threshold,
                    timestamp=now,
                    message=f"Copilot acceptance rate ({acceptance_rate:.1%}) below threshold ({self.config.acceptance_rate_threshold:.1%})"
                ))
                self._alert_history[alert_key] = now
        
        # Check success rate
        if success_rate < self.config.success_rate_threshold:
            alert_key = "success_rate_low"
            if self._should_send_alert(alert_key, now):
                alerts.append(Alert(
                    level=AlertLevel.WARNING,
                    metric="cortex_success_rate",
                    current_value=success_rate,
                    threshold=self.config.success_rate_threshold,
                    timestamp=now,
                    message=f"CORTEX success rate ({success_rate:.1%}) below threshold ({self.config.success_rate_threshold:.1%})"
                ))
                self._alert_history[alert_key] = now
        
        # Check active engineers (info alert if zero)
        if active_engineers == 0:
            alert_key = "no_active_engineers"
            if self._should_send_alert(alert_key, now):
                alerts.append(Alert(
                    level=AlertLevel.INFO,
                    metric="active_engineers",
                    current_value=float(active_engineers),
                    threshold=1.0,
                    timestamp=now,
                    message="No active engineers detected today"
                ))
                self._alert_history[alert_key] = now
        
        return alerts
    
    def _should_send_alert(self, alert_key: str, now: datetime) -> bool:
        """Check if alert should be sent based on cooldown"""
        if alert_key not in self._alert_history:
            return True
        
        last_sent = self._alert_history[alert_key]
        cooldown = timedelta(minutes=self.config.alert_cooldown_minutes)
        
        return (now - last_sent) >= cooldown
    
    def register_alert_callback(
        self,
        callback: Callable[[Alert], None]
    ):
        """
        Register callback function to be called when alerts are triggered.
        
        Args:
            callback: Function that takes Alert as parameter
            
        Example:
            def alert_handler(alert: Alert):
                print(f"ALERT: {alert.message}")
                # Send email, Slack message, etc.
            
            monitor.register_alert_callback(alert_handler)
        """
        self._alert_callback = callback
    
    def to_json(self, metrics: LiveMetrics) -> str:
        """
        Convert metrics to JSON for WebSocket streaming.
        
        Args:
            metrics: LiveMetrics to serialize
            
        Returns:
            JSON string ready for WebSocket transmission
        """
        return json.dumps({
            'timestamp': metrics.timestamp.isoformat(),
            'copilot_acceptance_rate': round(metrics.copilot_acceptance_rate, 4),
            'cortex_success_rate': round(metrics.cortex_success_rate, 4),
            'active_engineers': metrics.active_engineers,
            'total_requests_today': metrics.total_requests_today,
            'alerts': [
                {
                    'level': alert.level.value,
                    'metric': alert.metric,
                    'current_value': round(alert.current_value, 4),
                    'threshold': round(alert.threshold, 4),
                    'timestamp': alert.timestamp.isoformat(),
                    'message': alert.message
                }
                for alert in metrics.alerts
            ]
        })
