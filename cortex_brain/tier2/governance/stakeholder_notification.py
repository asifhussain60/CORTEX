"""Tier2 Governance: Stakeholder Notification

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List
from datetime import datetime


class NotificationLevel(Enum):
    """Notification priority levels."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class Notification:
    """Individual notification.
    
    Attributes:
        level: Notification priority level
        message: Notification message
        timestamp: When notification was created
    """
    level: NotificationLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.now)


class NotificationManager:
    """Manage stakeholder notifications.
    
    Attributes:
        notifications: List of all notifications
        enabled: Whether notification system is enabled
    """
    
    def __init__(self, enabled: bool = True):
        """Initialize notification manager.
        
        Args:
            enabled: Enable notification system
        """
        self.enabled = enabled
        self.notifications: List[Notification] = []
    
    def notify(self, level: NotificationLevel, message: str) -> bool:
        """Send notification.
        
        Args:
            level: Notification priority level
            message: Notification message
            
        Returns:
            True if notification was sent
        """
        notification = Notification(level=level, message=message)
        self.notifications.append(notification)
        return True
    
    def get_notifications_by_level(self, level: NotificationLevel) -> List[Notification]:
        """Get notifications by priority level.
        
        Args:
            level: Priority level to filter by
            
        Returns:
            List of notifications at specified level
        """
        return [n for n in self.notifications if n.level == level]


__all__ = ["NotificationLevel", "Notification", "NotificationManager"]
