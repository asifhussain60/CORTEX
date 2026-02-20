"""Test for BDOM-003: Stakeholder Notification"""
import pytest

try:
    from cortex.intelligence.memory.tier2_adaptive import (
        NotificationManager,
        NotificationLevel,
    )
except (ModuleNotFoundError, ImportError):
    # Placeholder classes for test collection
    class NotificationManager:
        pass
    class NotificationLevel:
        pass


class TestNotificationGov:
    def test_create_manager(self):
        manager = NotificationManager()
        assert len(manager.notifications) == 0
    
    def test_notify(self):
        manager = NotificationManager()
        manager.notify(NotificationLevel.INFO, "Test message")
        assert len(manager.notifications) == 1
    
    def test_get_by_level(self):
        manager = NotificationManager()
        manager.notify(NotificationLevel.INFO, "Info msg")
        manager.notify(NotificationLevel.CRITICAL, "Critical msg")
        
        info_notifs = manager.get_notifications_by_level(NotificationLevel.INFO)
        assert len(info_notifs) == 1
