"""BDOM-003: Stakeholder Notification Governance"""
from dataclasses import dataclass, field
from typing import List, Dict
from enum import Enum
from datetime import datetime

class NotificationLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

@dataclass
class Notification:
    level: NotificationLevel
    message: str
    timestamp: datetime = field(default_factory=datetime.utcnow)

class NotificationManager:
    def __init__(self):
        self.notifications: List[Notification] = []
    
    def notify(self, level: NotificationLevel, message: str) -> None:
        self.notifications.append(Notification(level=level, message=message))
    
    def get_notifications_by_level(self, level: NotificationLevel) -> List[Notification]:
        return [n for n in self.notifications if n.level == level]
