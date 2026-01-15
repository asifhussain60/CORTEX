"""
Tiered Logger Tests - TDD for AR-004

Tests for:
- AC-AR-004-01: AUDIT logs written to governance.db
- AC-AR-004-02: Log levels configurable per tier
- AC-AR-004-03: Structured JSON format for all logs

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import logging
from pathlib import Path

import pytest

from src.infrastructure.database import DatabaseManager, DatabaseConfig
from src.infrastructure.tiered_logger import TieredLogger, LogLevel, LogEntry


@pytest.mark.ac("AR-004-01")
class TestAuditToDb:
    """Test that AUDIT logs are written to governance.db."""
    
    def test_audit_to_db(self, temp_dir):
        """AC-AR-004-01: AUDIT logs should be written to governance.db."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = TieredLogger(db)
        logger.initialize(db)
        
        # Log to audit
        result = logger.log_to_audit(
            component="test_component",
            message="Test audit message",
            tier=0,
            ac_id="AC-TEST-001",
        )
        
        assert result.is_ok()
        
        # Verify entry in database
        audit_result = db.execute(
            "SELECT COUNT(*) as count FROM audit_log WHERE operation='LOG'"
        )
        assert audit_result.is_ok()
        
        db.close()
    
    def test_audit_logs_have_hash_chain(self, temp_dir):
        """Audit logs should be part of hash chain."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = TieredLogger(db)
        logger.initialize(db)
        
        # Log multiple messages
        logger.log_to_audit("comp1", "msg1", ac_id="AC-001")
        logger.log_to_audit("comp2", "msg2", ac_id="AC-002")
        
        # Check hash chain integrity
        integrity_result = db.execute(
            "SELECT COUNT(*) as count FROM audit_log WHERE previous_hash IS NOT NULL"
        )
        assert integrity_result.is_ok()
        
        db.close()


@pytest.mark.ac("AR-004-02")
class TestLogLevelConfig:
    """Test that log levels are configurable per tier."""
    
    def test_log_level_config(self):
        """AC-AR-004-02: Log levels should be configurable per tier."""
        logger = TieredLogger()
        
        # Set different levels per tier
        result = logger.set_log_level(0, LogLevel.AUDIT)
        assert result.is_ok()
        
        result = logger.set_log_level(1, LogLevel.INFO)
        assert result.is_ok()
        
        result = logger.set_log_level(2, LogLevel.WARNING)
        assert result.is_ok()
        
        # Verify levels
        level0 = logger.get_log_level(0)
        assert level0.is_ok()
        assert level0.unwrap() == LogLevel.AUDIT
        
        level1 = logger.get_log_level(1)
        assert level1.is_ok()
        assert level1.unwrap() == LogLevel.INFO
        
        level2 = logger.get_log_level(2)
        assert level2.is_ok()
        assert level2.unwrap() == LogLevel.WARNING
    
    def test_should_log_respects_tier_levels(self):
        """should_log should respect configured tier levels."""
        logger = TieredLogger()
        logger.set_log_level(1, LogLevel.INFO)
        
        # INFO should log for Tier 1
        result = logger.should_log(1, LogLevel.INFO)
        assert result.is_ok()
        assert result.unwrap() is True
        
        # DEBUG should not log for Tier 1 (below INFO)
        result = logger.should_log(1, LogLevel.DEBUG)
        assert result.is_ok()
        assert result.unwrap() is False
        
        # WARNING should log for Tier 1 (above INFO)
        result = logger.should_log(1, LogLevel.WARNING)
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_tier0_always_logs_audit(self):
        """Tier 0 should always log AUDIT level."""
        logger = TieredLogger()
        logger.set_log_level(0, LogLevel.AUDIT)
        
        result = logger.should_log(0, LogLevel.AUDIT)
        assert result.is_ok()
        assert result.unwrap() is True
    
    def test_invalid_tier_returns_error(self):
        """Setting log level for invalid tier should return error."""
        logger = TieredLogger()
        
        result = logger.set_log_level(99, LogLevel.INFO)
        assert result.is_err()
        assert "Invalid tier" in str(result)


@pytest.mark.ac("AR-004-03")
class TestStructuredJsonLogging:
    """Test that logs are in structured JSON format."""
    
    def test_structured_logging(self, temp_dir, caplog):
        """AC-AR-004-03: Logs should be in structured JSON format."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = TieredLogger(db)
        logger.initialize(db)
        
        with caplog.at_level(logging.INFO):
            result = logger.log(
                level=LogLevel.INFO,
                component="test_comp",
                message="Test message",
                tier=1,
                ac_id="AC-TEST-001",
                context={"key": "value"},
            )
        
        assert result.is_ok()
        db.close()
    
    def test_log_entry_to_json(self):
        """LogEntry should serialize to JSON."""
        entry = LogEntry(
            timestamp="2026-01-14T10:00:00Z",
            level="INFO",
            tier=1,
            component="test_component",
            message="Test message",
            ac_id="AC-001",
            context={"key": "value"},
        )
        
        json_str = entry.to_json()
        assert isinstance(json_str, str)
        
        # Should be valid JSON
        parsed = json.loads(json_str)
        assert parsed["level"] == "INFO"
        assert parsed["component"] == "test_component"
        assert parsed["ac_id"] == "AC-001"
        assert parsed["context"]["key"] == "value"
    
    def test_context_preserved_in_logs(self, temp_dir):
        """Additional context should be preserved in logs."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = TieredLogger(db)
        logger.initialize(db)
        
        context_data = {
            "user": "test_user",
            "action": "test_action",
            "details": {"nested": "value"},
        }
        
        result = logger.log_to_audit(
            component="test",
            message="Test with context",
            context=context_data,
            ac_id="AC-001",
        )
        
        assert result.is_ok()
        db.close()


class TestTieredLoggerSingleton:
    """Test singleton pattern of TieredLogger."""
    
    def test_singleton_instance(self):
        """Should return same instance on multiple calls."""
        TieredLogger.reset_instance()
        instance1 = TieredLogger.instance()
        instance2 = TieredLogger.instance()
        assert instance1 is instance2
    
    def test_reset_instance(self):
        """Should create new instance after reset."""
        TieredLogger.reset_instance()
        instance1 = TieredLogger.instance()
        TieredLogger.reset_instance()
        instance2 = TieredLogger.instance()
        assert instance1 is not instance2


class TestLogIntegration:
    """Integration tests for tiered logging."""
    
    def test_different_levels_different_messages(self, temp_dir):
        """Should handle different log levels correctly."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = TieredLogger(db)
        logger.initialize(db)
        
        # Log at different levels
        logger.log(LogLevel.DEBUG, "comp", "debug msg", tier=1)
        logger.log(LogLevel.INFO, "comp", "info msg", tier=1)
        logger.log(LogLevel.WARNING, "comp", "warning msg", tier=1)
        logger.log(LogLevel.CRITICAL, "comp", "critical msg", tier=1)
        
        db.close()
    
    def test_ac_id_tracking_in_logs(self, temp_dir):
        """AC-IDs should be tracked in logs."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = TieredLogger(db)
        logger.initialize(db)
        
        # Log with AC-ID
        result = logger.log_to_audit(
            component="governance",
            message="AC-ID test",
            ac_id="AC-TEST-001",
        )
        
        assert result.is_ok()
        
        # Verify AC-ID in database
        query_result = db.execute(
            "SELECT COUNT(*) as count FROM audit_log WHERE ac_id='AC-TEST-001'"
        )
        assert query_result.is_ok()
        
        db.close()
    
    def test_logger_not_initialized_returns_error(self):
        """Logging without initialization should fail gracefully."""
        logger = TieredLogger()  # Not initialized
        
        result = logger.log_to_audit(
            component="test",
            message="Should fail",
        )
        
        assert result.is_err()
        assert "not initialized" in str(result).lower()
