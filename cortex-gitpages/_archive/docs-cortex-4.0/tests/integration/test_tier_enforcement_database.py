"""
Tests for tier enforcement database schema and operations (AC-REM-002-06/07).

Tests:
- tier_access_log table creation
- TIER-0 immutability trigger
- Index creation
- Per-turn tier access logging
- TIER-0 violation detection

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import sqlite3
import tempfile
from pathlib import Path

from src.core.database.tier_enforcement_queries import TierEnforcementDatabase
from src.core.result import Ok, Err


class TestTierEnforcementSchema:
    """Tests for tier enforcement schema (AC-REM-002-06)."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        yield db_path
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    def test_tier_enforcement_database_initializes(self, temp_db):
        """Test TierEnforcementDatabase initializes successfully."""
        db = TierEnforcementDatabase(db_path=temp_db)
        assert db is not None
        assert db.db_path == temp_db
    
    def test_initialize_schema_creates_table(self, temp_db):
        """Test initialize_schema creates tier_access_log table."""
        db = TierEnforcementDatabase(db_path=temp_db)
        
        # Initialize schema
        result = db.initialize_schema()
        
        # Should succeed
        assert result.is_ok()
        
        # Verify table exists
        verify_result = db.verify_schema_exists()
        assert verify_result.is_ok()
        assert verify_result.unwrap() is True
    
    def test_tier_access_log_table_schema(self, temp_db):
        """Test tier_access_log table has correct schema."""
        db = TierEnforcementDatabase(db_path=temp_db)
        db.initialize_schema()
        
        # Connect and check schema
        conn = sqlite3.connect(temp_db)
        try:
            cursor = conn.cursor()
            
            # Get table info
            cursor.execute("PRAGMA table_info(tier_access_log)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}
            
            # Verify required columns
            assert "id" in columns
            assert "turn_number" in columns
            assert "orchestrator_id" in columns
            assert "rule_id" in columns
            assert "access_type" in columns
            assert "decision" in columns
            assert "violation_reason" in columns
            assert "timestamp" in columns
        
        finally:
            conn.close()
    
    def test_tier_access_log_unique_constraint(self, temp_db):
        """Test UNIQUE constraint on tier_access_log."""
        db = TierEnforcementDatabase(db_path=temp_db)
        db.initialize_schema()
        
        # Log first entry
        result1 = db.log_tier_access(
            turn_number=1,
            orchestrator_id="test-orch",
            rule_id="CORE-001",
            access_type="DECLARE"
        )
        assert result1.is_ok()
        
        # Log duplicate (should be ignored due to UNIQUE constraint)
        result2 = db.log_tier_access(
            turn_number=1,
            orchestrator_id="test-orch",
            rule_id="CORE-001",
            access_type="ACCESS"
        )
        # Should still succeed (ignores duplicates)
        assert result2.is_ok()
    
    def test_tier_access_log_indexes_created(self, temp_db):
        """Test tier_access_log indexes are created."""
        db = TierEnforcementDatabase(db_path=temp_db)
        db.initialize_schema()
        
        conn = sqlite3.connect(temp_db)
        try:
            cursor = conn.cursor()
            
            # List indexes on tier_access_log
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='tier_access_log'")
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Verify expected indexes exist
            assert "idx_tier_access_turn" in indexes
            assert "idx_tier_access_orchestrator" in indexes
            assert "idx_tier_access_rule" in indexes
            assert "idx_tier_access_timestamp" in indexes
        
        finally:
            conn.close()


class TestTierAccessLogging:
    """Tests for per-turn tier access logging (AC-REM-002-07)."""
    
    @pytest.fixture
    def tier_db(self):
        """Create tier enforcement database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = TierEnforcementDatabase(db_path=db_path)
        db.initialize_schema()
        
        yield db
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    def test_log_tier_access_declare(self, tier_db):
        """Test logging DECLARE access type."""
        result = tier_db.log_tier_access(
            turn_number=1,
            orchestrator_id="planning-orch",
            rule_id="CORE-017",
            access_type="DECLARE"
        )
        
        assert result.is_ok()
    
    def test_log_tier_access_normal(self, tier_db):
        """Test logging normal ACCESS type."""
        result = tier_db.log_tier_access(
            turn_number=1,
            orchestrator_id="planning-orch",
            rule_id="CORE-017",
            access_type="ACCESS"
        )
        
        assert result.is_ok()
    
    def test_log_tier_access_violation(self, tier_db):
        """Test logging ATTEMPT_VIOLATION with denial reason."""
        result = tier_db.log_tier_access(
            turn_number=1,
            orchestrator_id="planning-orch",
            rule_id="CORE-017",
            access_type="ATTEMPT_VIOLATION",
            decision="DENIED",
            violation_reason="Undeclared tier access: tier 3 not declared"
        )
        
        assert result.is_ok()
    
    def test_get_tier_access_summary(self, tier_db):
        """Test getting tier access summary."""
        # Log multiple accesses
        tier_db.log_tier_access(1, "orch-1", "CORE-001", "DECLARE")
        tier_db.log_tier_access(1, "orch-1", "CORE-002", "ACCESS")
        tier_db.log_tier_access(2, "orch-1", "CORE-003", "ACCESS")
        
        # Get summary
        result = tier_db.get_tier_access_summary(turn_number=1, orchestrator_id="orch-1")
        
        assert result.is_ok()
        summary = result.unwrap()
        assert summary["total_accesses"] > 0
    
    def test_log_multiple_turns(self, tier_db):
        """Test logging tier access across multiple turns."""
        for turn in range(1, 6):
            result = tier_db.log_tier_access(
                turn_number=turn,
                orchestrator_id="test-orch",
                rule_id=f"CORE-{turn:03d}",
                access_type="ACCESS"
            )
            assert result.is_ok()
    
    def test_log_multiple_orchestrators(self, tier_db):
        """Test logging tier access for multiple orchestrators."""
        orchestrators = ["planning-orch", "ado-orch", "tdd-orch"]
        
        for orch in orchestrators:
            result = tier_db.log_tier_access(
                turn_number=1,
                orchestrator_id=orch,
                rule_id="CORE-017",
                access_type="DECLARE"
            )
            assert result.is_ok()


class TestTierEnforcementViews:
    """Tests for tier enforcement database views."""
    
    @pytest.fixture
    def tier_db(self):
        """Create tier enforcement database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        db = TierEnforcementDatabase(db_path=db_path)
        db.initialize_schema()
        
        yield db
        
        Path(db_path).unlink(missing_ok=True)
    
    def test_tier_access_summary_view_exists(self, tier_db):
        """Test tier_access_summary view exists."""
        conn = sqlite3.connect(tier_db.db_path)
        try:
            cursor = conn.cursor()
            
            # Query the view (it should exist but have no rows initially)
            cursor.execute("SELECT COUNT(*) FROM tier_access_summary")
            result = cursor.fetchone()
            
            assert result is not None
        
        finally:
            conn.close()
    
    def test_tier0_immutability_violations_view_exists(self, tier_db):
        """Test tier0_immutability_violations view exists."""
        conn = sqlite3.connect(tier_db.db_path)
        try:
            cursor = conn.cursor()
            
            # Query the view
            cursor.execute("SELECT COUNT(*) FROM tier0_immutability_violations")
            result = cursor.fetchone()
            
            assert result is not None
        
        finally:
            conn.close()
    
    def test_get_tier0_violations(self, tier_db):
        """Test getting TIER-0 immutability violations."""
        # Log a violation
        tier_db.log_tier_access(
            turn_number=1,
            orchestrator_id="malicious-orch",
            rule_id="CORE-017",
            access_type="ATTEMPT_VIOLATION",
            decision="DENIED",
            violation_reason="Attempted TIER-0 modification"
        )
        
        # Get violations
        result = tier_db.get_tier0_violations()
        
        assert result.is_ok()
        violations = result.unwrap()
        assert len(violations) > 0


class TestTierEnforcementIntegration:
    """Integration tests for tier enforcement (AC-REM-002-06/07)."""
    
    def test_complete_tier_enforcement_workflow(self):
        """Test complete tier enforcement workflow."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        try:
            db = TierEnforcementDatabase(db_path=db_path)
            
            # 1. Initialize schema
            init_result = db.initialize_schema()
            assert init_result.is_ok()
            
            # 2. Verify schema exists
            verify_result = db.verify_schema_exists()
            assert verify_result.is_ok()
            assert verify_result.unwrap() is True
            
            # 3. Log tier accesses for turn 1
            for i in range(1, 4):
                result = db.log_tier_access(
                    turn_number=1,
                    orchestrator_id="planning-orch",
                    rule_id=f"CORE-{i:03d}",
                    access_type="DECLARE"
                )
                assert result.is_ok()
            
            # 4. Get summary
            summary_result = db.get_tier_access_summary(1, "planning-orch")
            assert summary_result.is_ok()
            summary = summary_result.unwrap()
            assert summary["total_accesses"] >= 3
            
            # 5. Log violation
            violation_result = db.log_tier_access(
                turn_number=1,
                orchestrator_id="malicious-orch",
                rule_id="CORE-017",
                access_type="ATTEMPT_VIOLATION",
                decision="DENIED"
            )
            assert violation_result.is_ok()
            
            # 6. Get violations
            violations_result = db.get_tier0_violations()
            assert violations_result.is_ok()
        
        finally:
            Path(db_path).unlink(missing_ok=True)
