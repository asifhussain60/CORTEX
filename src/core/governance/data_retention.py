"""DATA-002: Data Retention Policy"""
from dataclasses import dataclass
from typing import Dict, Optional
from datetime import datetime, timedelta
from enum import Enum

class RetentionPeriod(Enum):
    DAYS_30 = 30
    DAYS_90 = 90
    DAYS_365 = 365
    INDEFINITE = None

@dataclass
class DataRetentionPolicy:
    data_type: str
    retention_days: int
    created_date: datetime
    
    def is_expired(self) -> bool:
        expiry = self.created_date + timedelta(days=self.retention_days)
        return datetime.utcnow() > expiry
    
    def days_remaining(self) -> int:
        expiry = self.created_date + timedelta(days=self.retention_days)
        remaining = (expiry - datetime.utcnow()).days
        return max(0, remaining)

class RetentionManager:
    def __init__(self):
        self.policies: Dict[str, DataRetentionPolicy] = {}
    
    def set_policy(self, data_id: str, policy: DataRetentionPolicy) -> None:
        self.policies[data_id] = policy
    
    def check_expiry(self, data_id: str) -> bool:
        if data_id not in self.policies:
            return False
        return self.policies[data_id].is_expired()
