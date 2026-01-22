"""
Alert Pipeline Service for managing alert routing and notification channels.

Manages alert threshold configuration, notification channel registration,
alert routing, and complete audit trail support for knowledge base alerts.

Governance:
  - CORE-008: Tests written before code (TDD)
  - CORE-011: 100% type hints on all parameters and returns
  - CORE-012: Google-style docstrings on public APIs
  - CORE-013: Specific exception handling (no bare except)
"""

from typing import Dict, List, Optional, Any, Callable, Set
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import uuid
import logging


logger = logging.getLogger(__name__)


class SeverityLevel(Enum):
    """Severity levels for alerts."""
    
    CRITICAL = 0.9
    HIGH = 0.7
    MEDIUM = 0.5
    LOW = 0.2


class ChannelType(Enum):
    """Types of notification channels."""
    
    EMAIL = "email"
    WEBHOOK = "webhook"
    SLACK = "slack"
    SMS = "sms"
    AUDIT_TRAIL = "audit_trail"


@dataclass
class NotificationChannel:
    """Represents a notification channel."""
    
    channel_id: str
    name: str
    channel_type: ChannelType
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    severity_filter: Optional[List[SeverityLevel]] = None


@dataclass
class AlertMessage:
    """Represents an alert message."""
    
    alert_id: str
    severity: SeverityLevel
    message: str
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    acknowledged: bool = False
    acknowledged_by: Optional[str] = None
    acknowledged_at: Optional[datetime] = None


class AlertPipeline:
    """Service for managing alert routing and notification channels.
    
    Handles alert threshold configuration, channel registration,
    alert routing, and audit trail logging.
    """
    
    def __init__(
        self,
        backends: Optional[Dict[str, Any]] = None,
        thresholds: Optional[Dict[str, float]] = None,
    ) -> None:
        """Initialize AlertPipeline.
        
        Args:
            backends: Dictionary of notification backends.
            thresholds: Alert severity thresholds (CRITICAL, HIGH, MEDIUM, LOW).
        """
        self.backends = backends or {}
        self.thresholds = thresholds or {
            'CRITICAL': 0.9,
            'HIGH': 0.7,
            'MEDIUM': 0.5,
            'LOW': 0.2,
        }
        self.channels: Dict[str, NotificationChannel] = {}
        self.alert_history: List[AlertMessage] = []
        self.failed_alerts: List[AlertMessage] = []
        self.deduplication_cache: Set[str] = set()
        self.alert_metrics: Dict[str, Any] = {
            'total_alerts': 0,
            'routed_successfully': 0,
            'failed_routes': 0,
            'deduplicated': 0,
            'acknowledged': 0,
        }
        logger.info(f"AlertPipeline initialized with {len(self.backends)} backends")
    
    def register_channel(
        self,
        name: str,
        channel_type: ChannelType,
        config: Optional[Dict[str, Any]] = None,
        severity_filter: Optional[List[SeverityLevel]] = None,
    ) -> str:
        """Register a notification channel.
        
        Args:
            name: Channel name.
            channel_type: Type of channel.
            config: Channel configuration.
            severity_filter: Severity levels this channel accepts.
            
        Returns:
            Channel ID.
        """
        channel_id = str(uuid.uuid4())
        channel = NotificationChannel(
            channel_id=channel_id,
            name=name,
            channel_type=channel_type,
            config=config or {},
            severity_filter=severity_filter,
        )
        self.channels[channel_id] = channel
        logger.info(f"Channel registered: {name} ({channel_id})")
        return channel_id
    
    def deregister_channel(self, channel_id: str) -> bool:
        """Deregister a notification channel.
        
        Args:
            channel_id: Channel ID to remove.
            
        Returns:
            True if removed, False if not found.
        """
        if channel_id in self.channels:
            channel_name = self.channels[channel_id].name
            del self.channels[channel_id]
            logger.info(f"Channel deregistered: {channel_name}")
            return True
        return False
    
    def route_alert(
        self,
        severity: SeverityLevel,
        message: str,
        source: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Route an alert to configured channels.
        
        Args:
            severity: Alert severity level.
            message: Alert message.
            source: Alert source.
            metadata: Additional metadata.
            
        Returns:
            True if routed successfully, False otherwise.
        """
        alert = AlertMessage(
            alert_id=str(uuid.uuid4()),
            severity=severity,
            message=message,
            source=source,
            metadata=metadata or {},
        )
        
        # Check deduplication
        alert_hash = f"{source}:{message}"
        if alert_hash in self.deduplication_cache:
            self.alert_metrics['deduplicated'] += 1
            logger.info(f"Alert deduplicated: {alert.alert_id}")
            return True
        
        self.deduplication_cache.add(alert_hash)
        self.alert_history.append(alert)
        self.alert_metrics['total_alerts'] += 1
        
        # Route to applicable channels
        routed_count = 0
        for channel_id, channel in self.channels.items():
            if not channel.enabled:
                continue
            
            # Check severity filter
            if channel.severity_filter and severity not in channel.severity_filter:
                continue
            
            try:
                self._send_to_channel(channel, alert)
                routed_count += 1
            except Exception as e:
                logger.error(f"Failed to route to channel {channel_id}: {e}")
                self.failed_alerts.append(alert)
                self.alert_metrics['failed_routes'] += 1
        
        if routed_count > 0:
            self.alert_metrics['routed_successfully'] += 1
        
        logger.info(f"Alert routed to {routed_count} channels: {alert.alert_id}")
        return routed_count > 0
    
    def _send_to_channel(self, channel: NotificationChannel, alert: AlertMessage) -> None:
        """Send alert to a specific channel.
        
        Args:
            channel: Notification channel.
            alert: Alert to send.
        """
        backend = self.backends.get(channel.channel_type.value)
        if backend and hasattr(backend, 'send'):
            backend.send(alert)
    
    def filter_by_severity(self, severity: SeverityLevel) -> List[AlertMessage]:
        """Filter alerts by severity level.
        
        Args:
            severity: Severity level to filter by.
            
        Returns:
            List of alerts matching severity.
        """
        return [a for a in self.alert_history if a.severity == severity]
    
    def acknowledge_alert(
        self,
        alert_id: str,
        acknowledged_by: str = "system",
    ) -> bool:
        """Acknowledge an alert.
        
        Args:
            alert_id: Alert ID to acknowledge.
            acknowledged_by: User or system acknowledging the alert.
            
        Returns:
            True if acknowledged, False if not found.
        """
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = acknowledged_by
                alert.acknowledged_at = datetime.now()
                self.alert_metrics['acknowledged'] += 1
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def override_alert(
        self,
        alert_id: str,
        new_severity: Optional[SeverityLevel] = None,
        suppress: bool = False,
    ) -> bool:
        """Override alert decision.
        
        Args:
            alert_id: Alert ID to override.
            new_severity: New severity level if changing.
            suppress: Whether to suppress this alert.
            
        Returns:
            True if overridden, False if not found.
        """
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                if new_severity:
                    alert.severity = new_severity
                if suppress:
                    alert.metadata['suppressed'] = True
                logger.info(f"Alert overridden: {alert_id}")
                return True
        return False
    
    def retry_failed_alerts(self) -> int:
        """Retry routing of failed alerts.
        
        Returns:
            Number of alerts successfully rerouted.
        """
        success_count = 0
        remaining_failed = []
        
        for alert in self.failed_alerts:
            try:
                routed = self.route_alert(
                    severity=alert.severity,
                    message=alert.message,
                    source=alert.source,
                    metadata=alert.metadata,
                )
                if routed:
                    success_count += 1
                else:
                    remaining_failed.append(alert)
            except Exception as e:
                logger.error(f"Retry failed for alert {alert.alert_id}: {e}")
                remaining_failed.append(alert)
        
        self.failed_alerts = remaining_failed
        logger.info(f"Retry completed: {success_count} alerts rerouted")
        return success_count
    
    def deduplicate_alerts(self, window_seconds: int = 60) -> int:
        """Deduplicate recent alerts.
        
        Args:
            window_seconds: Time window for deduplication.
            
        Returns:
            Number of duplicate alerts removed.
        """
        cutoff_time = datetime.now() - __import__('datetime').timedelta(seconds=window_seconds)
        recent_alerts = [a for a in self.alert_history if a.timestamp >= cutoff_time]
        
        # Simple deduplication by source and message
        seen = {}
        duplicates = []
        
        for alert in recent_alerts:
            key = f"{alert.source}:{alert.message}"
            if key in seen:
                duplicates.append(alert)
            else:
                seen[key] = alert
        
        logger.info(f"Deduplicated {len(duplicates)} alerts")
        return len(duplicates)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get alert pipeline metrics.
        
        Returns:
            Dictionary with metrics.
        """
        return {
            **self.alert_metrics,
            'total_channels': len(self.channels),
            'enabled_channels': len([c for c in self.channels.values() if c.enabled]),
            'alert_history_size': len(self.alert_history),
            'failed_alerts_pending': len(self.failed_alerts),
        }
    
    def log_alert_event(
        self,
        alert_id: str,
        event_type: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Log an alert event to audit trail.
        
        Args:
            alert_id: Alert ID.
            event_type: Type of event.
            details: Event details.
        """
        if 'audit_trail' in self.backends:
            backend = self.backends['audit_trail']
            if hasattr(backend, 'log'):
                try:
                    backend.log({
                        'alert_id': alert_id,
                        'event_type': event_type,
                        'timestamp': datetime.now().isoformat(),
                        'details': details or {},
                    })
                except Exception as e:
                    logger.error(f"Failed to log alert event: {e}")
        
        logger.info(f"Alert event logged: {alert_id} - {event_type}")


__all__ = [
    "AlertPipeline",
    "AlertMessage",
    "NotificationChannel",
    "SeverityLevel",
    "ChannelType",
]
