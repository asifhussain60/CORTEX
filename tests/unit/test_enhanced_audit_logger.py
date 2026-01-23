"""
Enhanced Audit Logger Tests - TDD for FR-001

Tests for:
- AC-FR-001-01: Operations logged before execution
- AC-FR-001-02: Hash chain integrity maintained
- AC-FR-001-03: Audit logs queryable by AC-ID

Author: Asif Hussain
"""

from pathlib import Path

import pytest

from cortex.infrastructure.database import DatabaseManager, DatabaseConfig
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@pytest.mark.ac("FR-001-01")
class TestPreExecutionLogging:
    """Test that operations are logged before execution."""
    
    def test_pre_execution_logging(self, tmp_path):
        """AC-FR-001-01: Operations should be logged before execution."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        # Log operation START before doing anything
        result = logger.log_operation_start(
            ac_id="AC-TEST-001",
            operation="AC_EXECUTE",
            details={"action": "implementing feature"},
        )
        
        assert result.is_ok()
        operation_id = result.unwrap()
        assert operation_id  # Should return hash
        
        # Verify it was logged
        query_result = db.execute(
            "SELECT COUNT(*) FROM audit_log WHERE ac_id = 'AC-TEST-001'"
        )
        assert query_result.is_ok()
        count = query_result.unwrap()[0][0]
        assert count > 0
        
        db.close()
    
    def test_operation_lifecycle(self, tmp_path):
        """Operations should log start, then completion."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        ac_id = "AC-LIFECYCLE-001"
        
        # 1. Log start
        start_result = logger.log_operation_start(
            ac_id=ac_id,
            operation="AC_EXECUTE",
        )
        assert start_result.is_ok()
        
        # 2. Simulate work (would happen between start and complete)
        
        # 3. Log completion
        complete_result = logger.log_operation_complete(
            ac_id=ac_id,
            operation="AC_EXECUTE",
            success=True,
            details={"result": "success"},
        )
        assert complete_result.is_ok()
        
        # Verify both logged
        query_result = db.execute(
            "SELECT COUNT(*) FROM audit_log WHERE ac_id = ?",
            (ac_id,),
        )
        assert query_result.is_ok()
        count = query_result.unwrap()[0][0]
        assert count == 2  # Start and complete
        
        db.close()


@pytest.mark.ac("FR-001-02")
class TestHashChainIntegrity:
    """Test that hash chain integrity is maintained."""
    
    def test_hash_chain_integrity(self, tmp_path):
        """AC-FR-001-02: Hash chain integrity must be maintained."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        # Log multiple operations
        for i in range(3):
            logger.log_operation_start(
                ac_id=f"AC-CHAIN-{i:03d}",
                operation="AC_EXECUTE",
            )
        
        # Verify chain
        verify_result = logger.verify_hash_chain()
        assert verify_result.is_ok()
        assert verify_result.unwrap() is True
        
        db.close()
    
    def test_each_entry_has_hash(self, tmp_path):
        """Each audit entry should have entry hash and previous hash."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        logger.log_operation_start(
            ac_id="AC-HASH-001",
            operation="AC_EXECUTE",
        )
        
        # Query the entry
        query_result = db.execute(
            "SELECT entry_hash, previous_hash FROM audit_log WHERE ac_id = 'AC-HASH-001'"
        )
        assert query_result.is_ok()
        rows = query_result.unwrap()
        assert len(rows) > 0
        
        entry_hash, previous_hash = rows[0]
        assert entry_hash is not None
        assert len(entry_hash) == 64  # SHA-256 hex
        assert previous_hash is not None
        
        db.close()
    
    def test_chain_continuity(self, tmp_path):
        """Hashes should form continuous chain."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        # Log sequence
        hashes = []
        for i in range(3):
            hash_result = logger.log_operation_start(
                ac_id=f"AC-CONT-{i:03d}",
                operation="AC_EXECUTE",
            )
            if hash_result.is_ok():
                hashes.append(hash_result.unwrap())
        
        # Each hash should be different
        assert len(set(hashes)) == len(hashes)
        
        db.close()


@pytest.mark.ac("FR-001-03")
class TestAuditQueryByAcId:
    """Test that audit logs are queryable by AC-ID."""
    
    def test_audit_query_by_ac_id(self, tmp_path):
        """AC-FR-001-03: Audit logs should be queryable by AC-ID."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        ac_id = "AC-QUERY-001"
        
        # Log multiple operations for same AC-ID
        logger.log_operation_start(ac_id=ac_id, operation="AC_START")
        logger.log_operation_start(ac_id=ac_id, operation="AC_EXECUTE")
        logger.log_operation_complete(ac_id=ac_id, operation="AC_EXECUTE", success=True)
        
        # Query by AC-ID
        result = logger.query_by_ac_id(ac_id)
        assert result.is_ok()
        
        rows = result.unwrap()
        assert len(rows) == 3
        
        # Verify all have correct AC-ID (dicts now)
        for row in rows:
            assert row["ac_id"] == ac_id
        
        db.close()
    
    def test_get_operation_history(self, tmp_path):
        """Should retrieve operation history in order."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        ac_id = "AC-HISTORY-001"
        
        # Log operation sequence
        logger.log_operation_start(ac_id=ac_id, operation="OP1")
        logger.log_operation_complete(ac_id=ac_id, operation="OP1", success=True)
        logger.log_operation_start(ac_id=ac_id, operation="OP2")
        logger.log_operation_complete(ac_id=ac_id, operation="OP2", success=False)
        
        # Get history
        result = logger.get_operation_history(ac_id)
        assert result.is_ok()
        
        history = result.unwrap()
        assert len(history) == 4
        assert history[0]["ac_id"] == ac_id
        
        db.close()
    
    def test_query_nonexistent_ac_id(self, tmp_path):
        """Query for nonexistent AC-ID should return empty."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        result = logger.query_by_ac_id("AC-NONEXISTENT")
        assert result.is_ok()
        
        rows = result.unwrap()
        assert len(rows) == 0
        
        db.close()


class TestEnhancedAuditLoggerSingleton:
    """Test singleton pattern."""
    
    def test_singleton_instance(self):
        """Should return same instance."""
        EnhancedAuditLogger.reset_instance()
        instance1 = EnhancedAuditLogger.instance()
        instance2 = EnhancedAuditLogger.instance()
        assert instance1 is instance2
    
    def test_reset_instance(self):
        """Should create new instance after reset."""
        EnhancedAuditLogger.reset_instance()
        instance1 = EnhancedAuditLogger.instance()
        EnhancedAuditLogger.reset_instance()
        instance2 = EnhancedAuditLogger.instance()
        assert instance1 is not instance2


class TestChainStatus:
    """Test chain status reporting."""
    
    def test_get_chain_status(self, tmp_path):
        """Should report chain status."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        # Log some entries
        logger.log_operation_start(ac_id="AC-STATUS-001", operation="OP")
        logger.log_operation_start(ac_id="AC-STATUS-002", operation="OP")
        
        # Get status
        result = logger.get_chain_status()
        assert result.is_ok()
        
        status = result.unwrap()
        assert status["total_entries"] >= 2
        assert status["chain_valid"] is True
        assert "current_hash" in status
        assert "timestamp" in status
        
        db.close()


class TestOperationFailure:
    """Test logging of failed operations."""
    
    def test_log_operation_failure(self, tmp_path):
        """Should log operation failure."""
        db_path = tmp_path / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        logger = EnhancedAuditLogger(db)
        logger.initialize(db)
        
        ac_id = "AC-FAILURE-001"
        
        logger.log_operation_start(ac_id=ac_id, operation="OP")
        
        # Log failure
        result = logger.log_operation_complete(
            ac_id=ac_id,
            operation="OP",
            success=False,
            details={"error": "test error"},
        )
        
        assert result.is_ok()
        
        # Verify failure was logged
        history_result = logger.get_operation_history(ac_id)
        assert history_result.is_ok()
        history = history_result.unwrap()
        assert len(history) >= 1
        
        db.close()
