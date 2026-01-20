"""Data retention and lifecycle management."""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum


class RetentionStatus(Enum):
    """Data retention status."""
    ACTIVE = "active"
    ARCHIVED = "archived"
    PURGED = "purged"


class DataRetention:
    """Manage data retention policies."""
    
    def __init__(self, retention_days: int = 90):
        self.retention_days = retention_days
        self.data_items: Dict[str, Dict[str, Any]] = {}
    
    def store(self, data_id: str, data: Any) -> None:
        """Store data with retention timestamp."""
        self.data_items[data_id] = {
            "data": data,
            "created_at": datetime.now(),
            "status": RetentionStatus.ACTIVE
        }
    
    def check_retention(self, data_id: str) -> RetentionStatus:
        """Check data retention status."""
        if data_id not in self.data_items:
            return RetentionStatus.PURGED
        
        item = self.data_items[data_id]
        age_days = (datetime.now() - item["created_at"]).days
        
        if age_days > self.retention_days:
            return RetentionStatus.PURGED
        return RetentionStatus.ACTIVE
    
    def purge_expired(self) -> List[str]:
        """Purge expired data items."""
        expired = []
        for data_id, item in list(self.data_items.items()):
            if self.check_retention(data_id) == RetentionStatus.PURGED:
                del self.data_items[data_id]
                expired.append(data_id)
        return expired
