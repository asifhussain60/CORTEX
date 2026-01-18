"""
Unit Tests: DatabaseTransactionManager Hash Chain Calculation

Tests AC-FIX-001-02: Verify that hash chain calculation correctly links entries.

This test suite validates CORE-025 compliance:
- Each audit entry's previous_hash must equal the prior entry's entry_hash
- This creates an unbroken cryptographic chain across all entries for an AC-ID
- Breaking the chain provides tamper-evidence if any entry is modified

IMPORTANT: These tests initially FAIL to demonstrate the bug (TDD approach).
After AC-FIX-001-02 implementation, they PASS.

AC-FIX-001-02 Status: IN PROGRESS
"""

import pytest
import sqlite3
import tempfile
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, Generator

from src.infrastructure.database_transaction_manager import DatabaseTransactionManager


class TestHashChainCalculation:
    """Tests for hash chain integrity in audit logging."""
    
    @pytest.fixture
    def temp_db(self) -> Generator[str, None, None]:
        """Create a temporary database for testing."""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name
        
        # Initialize database with audit_log table
        conn = sqlite3.connect(db_path)
        conn.execute("""
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                component TEXT NOT NULL,
                level TEXT NOT NULL DEFAULT 'INFO',
                message TEXT NOT NULL,
                ac_id TEXT,
                metadata TEXT,
                previous_hash TEXT NOT NULL DEFAULT '',
                entry_hash TEXT NOT NULL
            )
        """)
        conn.commit()
        conn.close()
        
        yield db_path
        
        # Cleanup
        Path(db_path).unlink(missing_ok=True)
    
    @pytest.fixture
    def manager(self, temp_db: str) -> DatabaseTransactionManager:
        """Create a DatabaseTransactionManager instance."""
        return DatabaseTransactionManager(temp_db)
    
    def test_hash_chain_first_entry_uses_empty_genesis(
        self, manager: DatabaseTransactionManager, temp_db: str
    ) -> None:
        """
        Test: First entry for an AC-ID should have empty previous_hash (GENESIS).
        
        Acceptance:
        - First entry has previous_hash = ""
        - entry_hash is calculated correctly
        - No prior entry to link to
        """
        # Manually log first entry (using _log_audit_entry directly)
        conn = sqlite3.connect(temp_db)
        
        manager._log_audit_entry(
            conn,
            ac_id="AC-FIX-001-02",
            operation="AC_START",
            user="builder",
            status="AC_START",
            details={"first": True}
        )
        conn.commit()
        
        # Verify in database
        cursor = conn.cursor()
        cursor.execute("""
            SELECT previous_hash, entry_hash FROM audit_log
            WHERE ac_id = 'AC-FIX-001-02'
            ORDER BY id ASC
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        assert row is not None, "AC_START entry should exist"
        
        previous_hash, entry_hash = row
        
        # First entry should have empty previous_hash (GENESIS)
        assert previous_hash == "", f"First entry should have empty previous_hash, got '{previous_hash}'"
        
        # entry_hash should be 64-char hex (SHA256)
        assert len(entry_hash) == 64, f"entry_hash should be 64 chars, got {len(entry_hash)}"
        assert all(c in '0123456789abcdef' for c in entry_hash), "entry_hash should be hex"
        
        conn.close()
    
    def test_hash_chain_second_entry_links_to_first(
        self, manager: DatabaseTransactionManager, temp_db: str
    ) -> None:
        """
        Test: Second entry for an AC-ID should link to first entry's hash.
        
        CRITICAL TEST (Currently fails - this is the bug we're fixing)
        
        Acceptance:
        - Second entry's previous_hash == first entry's entry_hash
        - This creates an unbroken chain (CORE-025)
        - Chain is cryptographically verifiable
        
        Current Status: ❌ FAILS (hardcoded previous_hash = "")
        After AC-FIX-001-02: ✅ PASSES
        """
        # Manually test the _log_audit_entry method with multiple calls
        conn = sqlite3.connect(temp_db)
        
        # First entry - should have empty previous_hash (GENESIS)
        manager._log_audit_entry(
            conn,
            ac_id="AC-FIX-001-02",
            operation="AC_START",
            user="builder",
            status="AC_START",
            details={"step": 1}
        )
        conn.commit()
        
        # Second entry - should have previous_hash = first entry's entry_hash
        manager._log_audit_entry(
            conn,
            ac_id="AC-FIX-001-02",
            operation="AC_EXECUTE",
            user="builder",
            status="AC_EXECUTE",
            details={"step": 2}
        )
        conn.commit()
        
        # Query the entries
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, operation, previous_hash, entry_hash FROM audit_log
            WHERE ac_id = 'AC-FIX-001-02'
            ORDER BY id ASC
        """)
        
        entries = cursor.fetchall()
        assert len(entries) >= 2, f"Should have at least 2 entries, got {len(entries)}"
        
        # Check first entry (GENESIS)
        entry1_id, entry1_op, entry1_prev, entry1_hash = entries[0]
        assert entry1_prev == "", f"First entry previous_hash should be '', got '{entry1_prev}'"
        
        # Check second entry (should link to first)
        entry2_id, entry2_op, entry2_prev, entry2_hash = entries[1]
        
        # 🔴 THIS IS THE CRITICAL TEST - Currently FAILS
        # The bug is: entry2_prev is "" (hardcoded) when it should be entry1_hash
        assert (
            entry2_prev == entry1_hash
        ), (
            f"❌ CHAIN BREAK: Second entry should link to first entry's hash\n"
            f"  First entry hash:      {entry1_hash}\n"
            f"  Second entry previous: {entry2_prev}\n"
            f"  Status: 🔴 FAILS (hardcoded previous_hash = '')\n"
            f"  Fix: Use _get_prior_entry_hash() method"
        )
        
        conn.close()
    
    def test_hash_chain_multiple_entries_form_continuous_chain(
        self, manager: DatabaseTransactionManager, temp_db: str
    ) -> None:
        """
        Test: Multiple entries should form a continuous unbroken chain.
        
        Acceptance:
        - Entry 1: previous_hash = "" (GENESIS)
        - Entry 2: previous_hash = entry1.entry_hash
        - Entry 3: previous_hash = entry2.entry_hash
        - ... (pattern continues)
        
        This validates CORE-025: Hash chain integrity
        """
        # Create 5 entries for the same AC-ID
        for i in range(5):
            with manager.atomic_operation("AC-FIX-001-02", f"step{i}") as txn:
                pass  # Each logs AC_START
        
        # Query all entries
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, operation, previous_hash, entry_hash FROM audit_log
            WHERE ac_id = 'AC-FIX-001-02' AND operation = 'AC_START'
            ORDER BY id ASC
        """)
        
        entries = cursor.fetchall()
        
        # Validate chain
        chain_breaks = []
        for i, entry in enumerate(entries):
            entry_id, operation, previous_hash, entry_hash = entry
            
            if i == 0:
                # First entry: should have empty previous_hash
                if previous_hash != "":
                    chain_breaks.append((i, f"First entry should have empty previous_hash, got '{previous_hash}'"))
            else:
                # Subsequent entries: should link to prior entry
                prior_entry = entries[i - 1]
                prior_hash = prior_entry[3]  # entry_hash of prior entry
                
                if previous_hash != prior_hash:
                    chain_breaks.append((
                        i,
                        f"Entry {i} previous_hash should be {prior_hash}, got {previous_hash}"
                    ))
        
        if chain_breaks:
            msg = f"❌ Chain breaks detected ({len(chain_breaks)}):\n"
            for idx, reason in chain_breaks:
                msg += f"  Entry {idx}: {reason}\n"
            msg += f"\nStatus: 🔴 FAILS (hardcoded previous_hash = '')\n"
            pytest.fail(msg)
    
    def test_hash_chain_different_ac_ids_have_separate_chains(
        self, manager: DatabaseTransactionManager, temp_db: str
    ) -> None:
        """
        Test: Different AC-IDs should have separate hash chains.
        
        Acceptance:
        - AC-FIX-001-02 has its own chain
        - AC-FIX-001-03 has its own chain (doesn't link to AC-FIX-001-02)
        - Each chain independently validates (CORE-025)
        
        Architecture:
        - NOT a global chain (that's handled by integration tests)
        - Each AC-ID has its own per-AC-ID chain
        """
        # Create entries for AC-FIX-001-02
        with manager.atomic_operation("AC-FIX-001-02", "test") as txn:
            pass
        
        # Create entry for different AC-ID
        with manager.atomic_operation("AC-FIX-001-03", "test") as txn:
            pass
        
        # Create second entry for AC-FIX-001-02
        with manager.atomic_operation("AC-FIX-001-02", "test2") as txn:
            pass
        
        # Query entries
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT ac_id, operation, previous_hash, entry_hash FROM audit_log
            WHERE ac_id IN ('AC-FIX-001-02', 'AC-FIX-001-03')
            ORDER BY id ASC
        """)
        
        entries = cursor.fetchall()
        
        # Group by AC-ID
        ac_entries = {}
        for ac_id, op, prev_hash, entry_hash in entries:
            if ac_id not in ac_entries:
                ac_entries[ac_id] = []
            ac_entries[ac_id].append((op, prev_hash, entry_hash))
        
        # Validate each AC-ID's chain is separate
        for ac_id in ['AC-FIX-001-02', 'AC-FIX-001-03']:
            if ac_id in ac_entries:
                ac_chain = ac_entries[ac_id]
                
                for i, (op, prev_hash, entry_hash) in enumerate(ac_chain):
                    if i == 0:
                        # First entry should have empty previous_hash
                        assert prev_hash == "", f"{ac_id} first entry should have empty previous_hash"
                    else:
                        # Subsequent entries should link to prior entry in SAME AC-ID
                        prior_hash = ac_chain[i - 1][2]  # Prior entry's entry_hash
                        assert prev_hash == prior_hash, (
                            f"{ac_id}: Entry {i} should link to prior entry in same AC-ID"
                        )
        
        conn.close()
    
    def test_hash_calculation_includes_all_fields(
        self, manager: DatabaseTransactionManager, temp_db: str
    ) -> None:
        """
        Test: Hash calculation includes all relevant fields for tamper detection.
        
        Acceptance:
        - Hash includes: timestamp, operation, component, level, message, ac_id, metadata, previous_hash
        - Changing any field changes the hash
        - This provides CORE-025 tamper-evidence property
        
        Architecture:
        - Hash is calculated before insertion
        - Used in next entry's previous_hash
        - Breaking any field breaks the chain (detected by integration test)
        """
        with manager.atomic_operation("AC-FIX-001-02", "hash_test") as txn:
            pass
        
        # Query entry
        conn = sqlite3.connect(temp_db)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT timestamp, operation, component, level, message, ac_id, metadata, previous_hash, entry_hash
            FROM audit_log
            WHERE ac_id = 'AC-FIX-001-02'
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        assert row is not None, "Entry should exist"
        
        ts, op, comp, level, msg, ac_id, metadata, prev_hash, entry_hash = row
        
        # Manually calculate what hash should be
        # (must match the algorithm in _log_audit_entry)
        entry_data = f"{ts}{op}{comp}{level}{msg}{ac_id}{metadata}{prev_hash}"
        expected_hash = hashlib.sha256(entry_data.encode()).hexdigest()
        
        # Verify calculated hash matches stored hash
        assert entry_hash == expected_hash, (
            f"Hash mismatch:\n"
            f"  Expected: {expected_hash}\n"
            f"  Stored:   {entry_hash}\n"
            f"  This verifies the hash calculation includes all fields correctly"
        )
        
        conn.close()




# Markers for test status
pytestmark = [
    pytest.mark.slow,
    pytest.mark.integration,
]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
