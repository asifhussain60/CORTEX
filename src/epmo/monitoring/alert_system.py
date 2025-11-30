"""
CORTEX 3.0 Alert System
=======================

Comprehensive alerting system with multiple channels, escalation policies,
and intelligent alert management for production monitoring.
"""

import time
import threading
import asyncio
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
import sqlite3

# Optional imports for email and web functionality
try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False


logger = logging.getLogger(__name__)


class AlertSeverity(Enum):
    """Alert severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    EMERGENCY = "emergency"


class AlertStatus(Enum):
    """Alert status."""
    ACTIVE = "active"
    ACKNOWLEDGED = "acknowledged"
    RESOLVED = "resolved"
    SUPPRESSED = "suppressed"


class ChannelType(Enum):
    """Types of alert channels."""
    EMAIL = "email"
    SLACK = "slack"
    WEBHOOK = "webhook"
    SMS = "sms"
    CONSOLE = "console"
    CUSTOM = "custom"


@dataclass
class AlertChannel:
    """Alert notification channel configuration."""
    name: str
    channel_type: ChannelType
    config: Dict[str, Any]
    enabled: bool = True
    severity_filter: List[AlertSeverity] = field(default_factory=list)  # Empty = all severities
    
    # Rate limiting
    max_alerts_per_hour: Optional[int] = None
    alert_count_current_hour: int = 0
    current_hour_start: float = 0.0
    
    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: int = 60
    
    def can_send_alert(self) -> bool:
        """Check if channel can send alerts (rate limiting)."""
        if self.max_alerts_per_hour is None:
            return True
        
        current_time = time.time()
        current_hour = int(current_time // 3600)
        
        # Reset counter if we're in a new hour
        if int(self.current_hour_start // 3600) != current_hour:
            self.alert_count_current_hour = 0
            self.current_hour_start = current_time
        
        return self.alert_count_current_hour < self.max_alerts_per_hour
    
    def record_alert_sent(self) -> None:
        """Record that an alert was sent through this channel."""
        current_time = time.time()
        current_hour = int(current_time // 3600)
        
        if int(self.current_hour_start // 3600) != current_hour:
            self.alert_count_current_hour = 0
            self.current_hour_start = current_time
        
        self.alert_count_current_hour += 1


@dataclass
class EscalationPolicy:
    """Alert escalation policy."""
    name: str
    escalation_steps: List[Dict[str, Any]]  # [{"channels": [...], "delay_minutes": 0}]
    enabled: bool = True
    
    def get_channels_for_step(self, step: int) -> List[str]:
        """Get channel names for escalation step."""
        if step < len(self.escalation_steps):
            return self.escalation_steps[step].get('channels', [])
        return []
    
    def get_delay_for_step(self, step: int) -> int:
        """Get delay in minutes for escalation step."""
        if step < len(self.escalation_steps):
            return self.escalation_steps[step].get('delay_minutes', 0)
        return 0


@dataclass
class Alert:
    """Alert instance."""
    id: str
    title: str
    message: str
    severity: AlertSeverity
    source: str
    status: AlertStatus = AlertStatus.ACTIVE
    
    # Metadata
    tags: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    # Timing
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    acknowledged_at: Optional[float] = None
    resolved_at: Optional[float] = None
    
    # Escalation tracking
    escalation_step: int = 0
    last_escalation_time: Optional[float] = None
    
    # Notification tracking
    notifications_sent: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert alert to dictionary."""
        return {
            'id': self.id,
            'title': self.title,
            'message': self.message,
            'severity': self.severity.value,
            'source': self.source,
            'status': self.status.value,
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'acknowledged_at': self.acknowledged_at,
            'resolved_at': self.resolved_at,
            'escalation_step': self.escalation_step,
            'notifications_sent': self.notifications_sent
        }
    
    def acknowledge(self, acknowledged_by: str = "system") -> None:
        """Acknowledge the alert."""
        if self.status == AlertStatus.ACTIVE:
            self.status = AlertStatus.ACKNOWLEDGED
            self.acknowledged_at = time.time()
            self.updated_at = time.time()
            self.metadata['acknowledged_by'] = acknowledged_by
    
    def resolve(self, resolved_by: str = "system") -> None:
        """Resolve the alert."""
        if self.status in [AlertStatus.ACTIVE, AlertStatus.ACKNOWLEDGED]:
            self.status = AlertStatus.RESOLVED
            self.resolved_at = time.time()
            self.updated_at = time.time()
            self.metadata['resolved_by'] = resolved_by


class AlertSystem:
    """
    Comprehensive alert management system with multiple notification channels,
    escalation policies, and intelligent alert grouping and suppression.
    """
    
    def __init__(
        self,
        storage_path: Optional[str] = None,
        enable_persistence: bool = True,
        default_escalation_policy: Optional[str] = None
    ):
        self.storage_path = storage_path or "cortex_alerts.db"
        self.enable_persistence = enable_persistence
        self.default_escalation_policy = default_escalation_policy
        
        # Alert storage
        self._alerts: Dict[str, Alert] = {}
        self._alerts_lock = threading.RLock()
        
        # Notification channels
        self._channels: Dict[str, AlertChannel] = {}
        self._escalation_policies: Dict[str, EscalationPolicy] = {}
        
        # Alert processing
        self._processing_active = False
        self._processing_thread: Optional[threading.Thread] = None
        self._alert_queue: List[Alert] = []
        self._queue_lock = threading.Lock()
        
        # Suppression and grouping
        self._suppression_rules: List[Dict[str, Any]] = []
        self._grouped_alerts: Dict[str, List[str]] = {}  # group_key -> alert_ids
        
        # Alert callbacks
        self._alert_callbacks: List[Callable[[Alert], None]] = []
        
        # Initialize storage
        if self.enable_persistence:
            self._init_storage()
        
        # Register default console channel
        self._register_default_channels()
    
    def start_processing(self) -> None:
        """Start alert processing."""
        if self._processing_active:
            return
        
        self._processing_active = True
        self._processing_thread = threading.Thread(
            target=self._processing_loop,
            daemon=True
        )
        self._processing_thread.start()
        
        logger.info("Alert processing started")
    
    def stop_processing(self) -> None:
        """Stop alert processing."""
        self._processing_active = False
        if self._processing_thread:
            self._processing_thread.join(timeout=5.0)
        
        logger.info("Alert processing stopped")
    
    def create_alert(
        self,
        title: str,
        message: str,
        severity: AlertSeverity,
        source: str,
        tags: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        alert_id: Optional[str] = None
    ) -> Alert:
        """
        Create and queue a new alert.
        
        Args:
            title: Alert title
            message: Alert message
            severity: Alert severity level
            source: Alert source identifier
            tags: Additional tags
            metadata: Additional metadata
            alert_id: Optional custom alert ID
            
        Returns:
            Created alert
        """
        if alert_id is None:
            alert_id = f"{source}_{int(time.time() * 1000)}"
        
        # Check for existing active alert with same ID
        with self._alerts_lock:
            existing_alert = self._alerts.get(alert_id)
            if existing_alert and existing_alert.status == AlertStatus.ACTIVE:
                # Update existing alert
                existing_alert.message = message
                existing_alert.severity = severity
                existing_alert.updated_at = time.time()
                if tags:
                    existing_alert.tags.update(tags)
                if metadata:
                    existing_alert.metadata.update(metadata)
                return existing_alert
        
        # Create new alert
        alert = Alert(
            id=alert_id,
            title=title,
            message=message,
            severity=severity,
            source=source,
            tags=tags or {},
            metadata=metadata or {}
        )
        
        # Check suppression rules
        if self._is_alert_suppressed(alert):
            logger.info(f"Alert suppressed: {alert.id}")
            return alert
        
        # Store alert
        with self._alerts_lock:
            self._alerts[alert.id] = alert
        
        # Queue for processing
        with self._queue_lock:
            self._alert_queue.append(alert)
        
        # Notify callbacks
        for callback in self._alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.warning(f"Alert callback error: {e}")
        
        logger.info(f"Alert created: {alert.id} ({severity.value}): {title}")
        return alert
    
    def acknowledge_alert(self, alert_id: str, acknowledged_by: str = "system") -> bool:
        """
        Acknowledge an alert.
        
        Args:
            alert_id: ID of alert to acknowledge
            acknowledged_by: Who acknowledged the alert
            
        Returns:
            True if alert was acknowledged
        """
        with self._alerts_lock:
            alert = self._alerts.get(alert_id)
            if alert:
                alert.acknowledge(acknowledged_by)
                logger.info(f"Alert acknowledged: {alert_id} by {acknowledged_by}")
                return True
            return False
    
    def resolve_alert(self, alert_id: str, resolved_by: str = "system") -> bool:
        """
        Resolve an alert.
        
        Args:
            alert_id: ID of alert to resolve
            resolved_by: Who resolved the alert
            
        Returns:
            True if alert was resolved
        """
        with self._alerts_lock:
            alert = self._alerts.get(alert_id)
            if alert:
                alert.resolve(resolved_by)
                logger.info(f"Alert resolved: {alert_id} by {resolved_by}")
                return True
            return False
    
    def get_active_alerts(self) -> List[Alert]:
        """Get all active alerts."""
        with self._alerts_lock:
            return [
                alert for alert in self._alerts.values()
                if alert.status == AlertStatus.ACTIVE
            ]
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get alert statistics."""
        with self._alerts_lock:
            total_alerts = len(self._alerts)
            
            status_counts = {status.value: 0 for status in AlertStatus}
            severity_counts = {severity.value: 0 for severity in AlertSeverity}
            source_counts = {}
            
            for alert in self._alerts.values():
                status_counts[alert.status.value] += 1
                severity_counts[alert.severity.value] += 1
                source_counts[alert.source] = source_counts.get(alert.source, 0) + 1
        
        return {
            'total_alerts': total_alerts,
            'status_distribution': status_counts,
            'severity_distribution': severity_counts,
            'top_sources': dict(sorted(source_counts.items(), key=lambda x: x[1], reverse=True)[:10]),
            'active_channels': len([ch for ch in self._channels.values() if ch.enabled]),
            'escalation_policies': len(self._escalation_policies)
        }
    
    def register_channel(self, channel: AlertChannel) -> None:
        """Register a notification channel."""
        self._channels[channel.name] = channel
        logger.info(f"Registered alert channel: {channel.name} ({channel.channel_type.value})")
    
    def register_escalation_policy(self, policy: EscalationPolicy) -> None:
        """Register an escalation policy."""
        self._escalation_policies[policy.name] = policy
        logger.info(f"Registered escalation policy: {policy.name}")
    
    def add_suppression_rule(
        self,
        rule_name: str,
        condition: Dict[str, Any],
        duration_minutes: int = 60
    ) -> None:
        """
        Add alert suppression rule.
        
        Args:
            rule_name: Name of suppression rule
            condition: Condition to match alerts (tags, source, etc.)
            duration_minutes: How long to suppress matching alerts
        """
        rule = {
            'name': rule_name,
            'condition': condition,
            'duration_minutes': duration_minutes,
            'created_at': time.time()
        }
        
        self._suppression_rules.append(rule)
        logger.info(f"Added suppression rule: {rule_name}")
    
    def add_alert_callback(self, callback: Callable[[Alert], None]) -> None:
        """Add callback for alert creation."""
        self._alert_callbacks.append(callback)
    
    def _register_default_channels(self) -> None:
        """Register default notification channels."""
        # Console channel (always available)
        console_channel = AlertChannel(
            name="console",
            channel_type=ChannelType.CONSOLE,
            config={},
            enabled=True
        )
        self.register_channel(console_channel)
        
        # Default escalation policy
        default_policy = EscalationPolicy(
            name="default",
            escalation_steps=[
                {"channels": ["console"], "delay_minutes": 0},
                {"channels": ["console"], "delay_minutes": 15}
            ]
        )
        self.register_escalation_policy(default_policy)
    
    def configure_email_channel(
        self,
        name: str,
        smtp_server: str,
        smtp_port: int,
        username: str,
        password: str,
        from_address: str,
        to_addresses: List[str],
        enabled: bool = True
    ) -> None:
        """Configure email notification channel."""
        config = {
            'smtp_server': smtp_server,
            'smtp_port': smtp_port,
            'username': username,
            'password': password,
            'from_address': from_address,
            'to_addresses': to_addresses
        }
        
        channel = AlertChannel(
            name=name,
            channel_type=ChannelType.EMAIL,
            config=config,
            enabled=enabled,
            max_alerts_per_hour=20  # Reasonable default
        )
        
        self.register_channel(channel)
    
    def configure_slack_channel(
        self,
        name: str,
        webhook_url: str,
        channel: str,
        username: str = "CORTEX Alert System",
        enabled: bool = True
    ) -> None:
        """Configure Slack notification channel."""
        config = {
            'webhook_url': webhook_url,
            'channel': channel,
            'username': username
        }
        
        channel_obj = AlertChannel(
            name=name,
            channel_type=ChannelType.SLACK,
            config=config,
            enabled=enabled,
            max_alerts_per_hour=50  # Slack can handle more
        )
        
        self.register_channel(channel_obj)
    
    def configure_webhook_channel(
        self,
        name: str,
        webhook_url: str,
        method: str = "POST",
        headers: Optional[Dict[str, str]] = None,
        enabled: bool = True
    ) -> None:
        """Configure webhook notification channel."""
        config = {
            'webhook_url': webhook_url,
            'method': method.upper(),
            'headers': headers or {'Content-Type': 'application/json'}
        }
        
        channel = AlertChannel(
            name=name,
            channel_type=ChannelType.WEBHOOK,
            config=config,
            enabled=enabled
        )
        
        self.register_channel(channel)
    
    def _is_alert_suppressed(self, alert: Alert) -> bool:
        """Check if alert matches any suppression rules."""
        current_time = time.time()
        
        for rule in self._suppression_rules:
            # Check if rule has expired
            rule_age_minutes = (current_time - rule['created_at']) / 60
            if rule_age_minutes > rule['duration_minutes']:
                continue
            
            # Check if alert matches rule condition
            condition = rule['condition']
            matches = True
            
            if 'source' in condition and alert.source != condition['source']:
                matches = False
            
            if 'severity' in condition and alert.severity.value != condition['severity']:
                matches = False
            
            if 'tags' in condition:
                for key, value in condition['tags'].items():
                    if alert.tags.get(key) != value:
                        matches = False
                        break
            
            if matches:
                return True
        
        return False
    
    def _process_alert(self, alert: Alert) -> None:
        """Process a single alert through escalation."""
        # Determine escalation policy
        policy_name = alert.metadata.get('escalation_policy', self.default_escalation_policy or 'default')
        policy = self._escalation_policies.get(policy_name)
        
        if not policy or not policy.enabled:
            logger.warning(f"No escalation policy found for alert {alert.id}")
            return
        
        # Check if it's time for next escalation step
        current_time = time.time()
        delay_minutes = policy.get_delay_for_step(alert.escalation_step)
        
        if alert.last_escalation_time is None:
            should_escalate = True  # First escalation
        else:
            time_since_last = (current_time - alert.last_escalation_time) / 60
            should_escalate = time_since_last >= delay_minutes
        
        if not should_escalate or alert.status != AlertStatus.ACTIVE:
            return
        
        # Get channels for current escalation step
        channel_names = policy.get_channels_for_step(alert.escalation_step)
        
        # Send notifications
        for channel_name in channel_names:
            self._send_notification(alert, channel_name)
        
        # Update escalation tracking
        alert.last_escalation_time = current_time
        alert.escalation_step += 1
        alert.updated_at = current_time
    
    def _send_notification(self, alert: Alert, channel_name: str) -> bool:
        """Send notification through specified channel."""
        channel = self._channels.get(channel_name)
        if not channel or not channel.enabled:
            return False
        
        # Check severity filter
        if channel.severity_filter and alert.severity not in channel.severity_filter:
            return False
        
        # Check rate limiting
        if not channel.can_send_alert():
            logger.warning(f"Rate limit exceeded for channel {channel_name}")
            return False
        
        # Send based on channel type
        success = False
        error_message = None
        
        try:
            if channel.channel_type == ChannelType.EMAIL:
                success = self._send_email(alert, channel)
            elif channel.channel_type == ChannelType.SLACK:
                success = self._send_slack(alert, channel)
            elif channel.channel_type == ChannelType.WEBHOOK:
                success = self._send_webhook(alert, channel)
            elif channel.channel_type == ChannelType.CONSOLE:
                success = self._send_console(alert, channel)
            else:
                logger.warning(f"Unsupported channel type: {channel.channel_type}")
        
        except Exception as e:
            error_message = str(e)
            logger.error(f"Failed to send alert via {channel_name}: {e}")
        
        # Record notification attempt
        notification_record = {
            'channel': channel_name,
            'timestamp': time.time(),
            'success': success,
            'error': error_message
        }
        
        alert.notifications_sent.append(notification_record)
        
        if success:
            channel.record_alert_sent()
        
        return success
    
    def _send_email(self, alert: Alert, channel: AlertChannel) -> bool:
        """Send email notification."""
        if not EMAIL_AVAILABLE:
            logger.error("Email functionality not available - email packages not installed")
            return False
        
        config = channel.config
        
        # Create message
        msg = MimeMultipart()
        msg['From'] = config['from_address']
        msg['To'] = ', '.join(config['to_addresses'])
        msg['Subject'] = f"[{alert.severity.value.upper()}] {alert.title}"
        
        # Create body
        body = f"""
Alert Details:
--------------
Title: {alert.title}
Severity: {alert.severity.value.upper()}
Source: {alert.source}
Created: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.created_at))}

Message:
{alert.message}

Tags: {alert.tags}
Metadata: {alert.metadata}

Alert ID: {alert.id}
"""
        
        msg.attach(MimeText(body, 'plain'))
        
        # Send email
        with smtplib.SMTP(config['smtp_server'], config['smtp_port']) as server:
            server.starttls()
            server.login(config['username'], config['password'])
            server.send_message(msg)
        
        return True
    
    def _send_slack(self, alert: Alert, channel: AlertChannel) -> bool:
        """Send Slack notification."""
        if not REQUESTS_AVAILABLE:
            logger.error("Requests library not available - cannot send Slack notifications")
            return False
        
        config = channel.config
        
        # Create Slack message
        color_map = {
            AlertSeverity.INFO: "good",
            AlertSeverity.WARNING: "warning",
            AlertSeverity.CRITICAL: "danger",
            AlertSeverity.EMERGENCY: "danger"
        }
        
        payload = {
            "channel": config['channel'],
            "username": config['username'],
            "attachments": [
                {
                    "color": color_map.get(alert.severity, "warning"),
                    "title": alert.title,
                    "text": alert.message,
                    "fields": [
                        {"title": "Severity", "value": alert.severity.value.upper(), "short": True},
                        {"title": "Source", "value": alert.source, "short": True},
                        {"title": "Alert ID", "value": alert.id, "short": True},
                        {"title": "Created", "value": time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(alert.created_at)), "short": True}
                    ]
                }
            ]
        }
        
        # Send to Slack
        response = requests.post(config['webhook_url'], json=payload)
        response.raise_for_status()
        
        return True
    
    def _send_webhook(self, alert: Alert, channel: AlertChannel) -> bool:
        """Send webhook notification."""
        if not REQUESTS_AVAILABLE:
            logger.error("Requests library not available - cannot send webhook notifications")
            return False
        
        config = channel.config
        
        payload = alert.to_dict()
        
        # Send webhook
        response = requests.request(
            method=config['method'],
            url=config['webhook_url'],
            json=payload,
            headers=config['headers']
        )
        response.raise_for_status()
        
        return True
    
    def _send_console(self, alert: Alert, channel: AlertChannel) -> bool:
        """Send console notification."""
        severity_symbols = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.CRITICAL: "🔥",
            AlertSeverity.EMERGENCY: "🚨"
        }
        
        symbol = severity_symbols.get(alert.severity, "❗")
        timestamp = time.strftime('%H:%M:%S', time.localtime(alert.created_at))
        
        print(f"{symbol} [{timestamp}] [{alert.severity.value.upper()}] {alert.title}")
        print(f"   Source: {alert.source}")
        print(f"   Message: {alert.message}")
        print(f"   Alert ID: {alert.id}")
        if alert.tags:
            print(f"   Tags: {alert.tags}")
        print()
        
        return True
    
    def _init_storage(self) -> None:
        """Initialize SQLite storage for alert persistence."""
        try:
            conn = sqlite3.connect(self.storage_path)
            cursor = conn.cursor()
            
            # Create alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    message TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    source TEXT NOT NULL,
                    status TEXT NOT NULL,
                    tags TEXT,
                    metadata TEXT,
                    created_at REAL NOT NULL,
                    updated_at REAL NOT NULL,
                    acknowledged_at REAL,
                    resolved_at REAL,
                    escalation_step INTEGER DEFAULT 0,
                    notifications_sent TEXT
                )
            """)
            
            # Create index for efficient queries
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_alerts_status_created 
                ON alerts(status, created_at)
            """)
            
            conn.commit()
            conn.close()
            
            logger.info(f"Initialized alert storage: {self.storage_path}")
        
        except Exception as e:
            logger.error(f"Failed to initialize alert storage: {e}")
    
    def _processing_loop(self) -> None:
        """Main alert processing loop."""
        logger.info("Alert processing loop started")
        
        while self._processing_active:
            try:
                # Process queued alerts
                alerts_to_process = []
                with self._queue_lock:
                    alerts_to_process = self._alert_queue[:]
                    self._alert_queue.clear()
                
                # Process new alerts
                for alert in alerts_to_process:
                    self._process_alert(alert)
                
                # Check existing active alerts for escalation
                active_alerts = self.get_active_alerts()
                for alert in active_alerts:
                    self._process_alert(alert)
                
                # Wait before next check
                time.sleep(60)  # Check every minute
            
            except Exception as e:
                logger.error(f"Alert processing loop error: {e}")
                time.sleep(60)
        
        logger.info("Alert processing loop stopped")


# Global alert system instance
default_alert_system = AlertSystem()