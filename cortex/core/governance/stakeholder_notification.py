"""Stakeholder notification and communication module."""

from typing import List, Dict, Any
from datetime import datetime


class NotificationLevel:
    """Notification severity levels."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class StakeholderNotification:
    """Manage stakeholder notifications."""
    
    def __init__(self):
        self.notifications: List[Dict[str, Any]] = []
        self.recipients: Dict[str, List[str]] = {}
    
    def notify(self, stakeholder_id: str, message: str, level: str = NotificationLevel.INFO) -> bool:
        """Send notification to stakeholder."""
        notification = {
            "stakeholder_id": stakeholder_id,
            "message": message,
            "level": level,
            "timestamp": datetime.now()
        }
        self.notifications.append(notification)
        return True
    
    def register_recipient(self, stakeholder_id: str, email: str) -> None:
        """Register recipient for notifications."""
        if stakeholder_id not in self.recipients:
            self.recipients[stakeholder_id] = []
        self.recipients[stakeholder_id].append(email)
