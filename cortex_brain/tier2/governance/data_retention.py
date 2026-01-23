"""Tier2 Governance: Data Retention

Implements DATA-002: Data Retention Policy.
Manages data retention policies and expiration checks.

Author: CORTEX Framework
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict


class RetentionPeriod(Enum):
    """Data retention periods."""
    SHORT = 30  # 30 days
    MEDIUM = 90  # 90 days
    LONG = 365  # 1 year
    PERMANENT = -1  # Forever


@dataclass
class DataRetentionPolicy:
    """Data retention policy."""
    data_type: str
    retention_days: int
    created_date: datetime
    auto_delete: bool = True
    
    def is_expired(self) -> bool:
        """Check if data retention has expired.
        
        Returns:
            True if expired, False otherwise
        """
        if self.retention_days < 0:  # Permanent
            return False
        
        expiry_date = self.created_date + timedelta(days=self.retention_days)
        return datetime.utcnow() > expiry_date


class RetentionManager:
    """Manage data retention policies."""
    
    def __init__(self):
        """Initialize retention manager."""
        self.policies: Dict[str, DataRetentionPolicy] = {}
    
    def set_policy(self, data_id: str, policy: DataRetentionPolicy) -> None:
        """Set retention policy for data.
        
        Args:
            data_id: Data identifier
            policy: Retention policy to apply
        """
        self.policies[data_id] = policy
    
    def check_expiry(self, data_id: str) -> bool:
        """Check if data has expired.
        
        Args:
            data_id: Data identifier
            
        Returns:
            True if expired, False otherwise
        """
        if data_id not in self.policies:
            return False
        
        return self.policies[data_id].is_expired()


__all__ = ["RetentionPeriod", "DataRetentionPolicy", "RetentionManager"]
