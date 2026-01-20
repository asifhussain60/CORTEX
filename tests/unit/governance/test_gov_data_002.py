"""Test for DATA-002: Data Retention Policy"""
import pytest
from datetime import datetime, timedelta
from cortex.core.governance.data_retention import (
    RetentionManager,
    DataRetentionPolicy,
    RetentionPeriod,
)

class TestDataRetention:
    def test_create_policy(self):
        policy = DataRetentionPolicy(
            data_type="logs",
            retention_days=90,
            created_date=datetime.utcnow()
        )
        assert policy.retention_days == 90
    
    def test_not_expired(self):
        policy = DataRetentionPolicy(
            data_type="logs",
            retention_days=90,
            created_date=datetime.utcnow()
        )
        assert not policy.is_expired()
    
    def test_expired(self):
        old_date = datetime.utcnow() - timedelta(days=100)
        policy = DataRetentionPolicy(
            data_type="logs",
            retention_days=90,
            created_date=old_date
        )
        assert policy.is_expired()
    
    def test_manager(self):
        manager = RetentionManager()
        policy = DataRetentionPolicy("logs", 90, datetime.utcnow())
        manager.set_policy("data1", policy)
        assert not manager.check_expiry("data1")
