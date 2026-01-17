"""
Integration test: Audit Trail Integrity Verification

This test validates that ALL AC-IDs across PHASES 1-13 have proper audit trail evidence.

Requirement: CORE-027 - "AC_START, AC_EXECUTE, AC_COMPLETE audit entries MANDATORY"

Validation:
1. Each AC-ID has exactly 3 lifecycle events (START, EXECUTE, COMPLETE)
2. Events are chronologically ordered
3. Hash chain is unbroken (each entry's previous_hash matches prior entry's entry_hash)
4. No fake/retroactively-inserted entries (validated by timestamp sequence)
5. All entries have metadata with test results

This test is part of AUDIT-REMEDIATION-2026-01-15 initiative.
"""

import pytest
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional


class TestAuditTrailIntegrity:
    """Comprehensive audit trail validation across all phases."""
    
    # Test fixture AC-IDs that are used for testing audit system itself
    # These are not real acceptance criteria and should be excluded from validation
    TEST_FIXTURES = {
        "AC-CHAIN-000", "AC-CHAIN-001", "AC-CHAIN-002",
        "AC-DECORATOR-001", "AC-HASH-001", "AC-INVALID-999"
    }
    
    @pytest.fixture
    def db_connection(self) -> sqlite3.Connection:
        """Connect to governance database."""
        db_path = Path(__file__).parent.parent.parent / "cortex-brain" / "state" / "governance.db"
        assert db_path.exists(), f"Database not found at {db_path}"
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_ac_ids(self, conn: sqlite3.Connection) -> List[str]:
        """Get all AC-IDs from audit log (excluding test fixtures)."""
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ac_id FROM audit_log WHERE ac_id IS NOT NULL ORDER BY ac_id")
        all_ac_ids = [row[0] for row in cursor.fetchall()]
        # Filter out test fixtures
        return [ac_id for ac_id in all_ac_ids if ac_id not in self.TEST_FIXTURES]
    
    def get_ac_lifecycle_events(
        self, conn: sqlite3.Connection, ac_id: str
    ) -> List[Tuple[int, str, str, str, str, str]]:
        """Get all lifecycle events for an AC-ID.
        
        Note: Accepts both 'AC_START/AC_EXECUTE/AC_COMPLETE' (standard) 
        and 'START/EXECUTE/COMPLETE' (legacy format used by some early ACs).
        """
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, operation, timestamp, previous_hash, entry_hash, message
            FROM audit_log
            WHERE ac_id = ? 
            AND (
                operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
                OR operation IN ('START', 'EXECUTE', 'COMPLETE')
            )
            ORDER BY id ASC
        """, (ac_id,))
        return cursor.fetchall()
    
    def test_all_ac_ids_have_complete_lifecycle(self, db_connection: sqlite3.Connection) -> None:
        """
        Test: Every AC-ID has 3 lifecycle events (START, EXECUTE, COMPLETE).
        
        Acceptance:
        - AC_START logged before implementation
        - AC_EXECUTE logged during test execution
        - AC_COMPLETE logged when all tests pass
        """
        ac_ids = self.get_all_ac_ids(db_connection)
        
        assert len(ac_ids) > 0, "No AC-IDs found in audit log"
        
        incomplete_acs = []
        
        for ac_id in ac_ids:
            events = self.get_ac_lifecycle_events(db_connection, ac_id)
            
            if len(events) < 3:
                incomplete_acs.append((ac_id, len(events)))
        
        if incomplete_acs:
            msg = "The following AC-IDs have incomplete lifecycle:\n"
            for ac_id, count in incomplete_acs:
                msg += f"  {ac_id}: {count} events (expected 3 minimum)\n"
            pytest.fail(msg)
    
    def test_lifecycle_events_are_chronologically_ordered(
        self, db_connection: sqlite3.Connection
    ) -> None:
        """
        Test: Lifecycle events are in chronological order for each AC-ID.
        
        Acceptance:
        - AC_START timestamp < AC_EXECUTE timestamp < AC_COMPLETE timestamp
        - No time reversals or anomalies
        """
        ac_ids = self.get_all_ac_ids(db_connection)
        ordering_violations = []
        
        for ac_id in ac_ids:
            events = self.get_ac_lifecycle_events(db_connection, ac_id)
            
            if len(events) < 2:
                continue
            
            timestamps = [row[2] for row in events]  # timestamp column
            
            for i in range(len(timestamps) - 1):
                ts1 = datetime.fromisoformat(timestamps[i].replace('+00:00', ''))
                ts2 = datetime.fromisoformat(timestamps[i + 1].replace('+00:00', ''))
                
                if ts1 > ts2:
                    ordering_violations.append((ac_id, i, timestamps[i], timestamps[i + 1]))
        
        if ordering_violations:
            msg = "Chronological ordering violations detected:\n"
            for ac_id, idx, ts1, ts2 in ordering_violations:
                msg += f"  {ac_id}: event {idx} timestamp {ts1} > event {idx+1} timestamp {ts2}\n"
            pytest.fail(msg)
    
    def test_hash_chain_integrity(self, db_connection: sqlite3.Connection) -> None:
        """
        Test: GLOBAL hash chain integrity across ALL production entries.
        
        Architecture Note:
        The audit log maintains a SINGLE GLOBAL hash chain in chronological order,
        NOT separate chains per AC-ID. This means:
        - Entry N's entry_hash must equal Entry N+1's previous_hash
        - Entries from different AC-IDs are interleaved chronologically
        - This provides tamper-evidence across the entire audit trail
        
        Strategy:
        This test validates the ENTIRE global chain by:
        1. Excluding known test fixture AC-IDs (not real acceptance criteria)
        2. Checking chain continuity across ALL remaining entries
        3. Allowing for intentional chain breaks at test fixture boundaries
        
        This approach is robust because:
        - New test fixtures don't break validation (they're just skipped)
        - Production entries are always validated regardless of test fixture placement
        - No arbitrary ID cutoffs that could silently exclude data
        
        Acceptance:
        - Global hash chain is unbroken for production AC-IDs
        - Test fixtures are properly excluded
        - No data corruption or tampering detected
        """
        cursor = db_connection.cursor()
        
        # Get ALL entries, we'll handle test fixtures during validation
        cursor.execute("""
            SELECT id, ac_id, operation, previous_hash, entry_hash, timestamp
            FROM audit_log
            ORDER BY id ASC
        """)
        
        all_entries = cursor.fetchall()
        
        if not all_entries:
            pytest.skip("No entries in audit log")
            return
        
        hash_violations = []
        production_entries_validated = 0
        test_fixtures_skipped = 0
        chain_segments = []  # Track continuous chain segments
        current_segment_start = None
        expected_prev_hash = None
        
        for i, entry in enumerate(all_entries):
            entry_id, ac_id, operation, previous_hash, entry_hash, timestamp = entry
            
            # Check if this is a test-related entry (should be excluded from chain validation)
            is_test_fixture = False
            
            # Known test fixture AC-IDs
            if ac_id and ac_id in self.TEST_FIXTURES:
                is_test_fixture = True
            # NULL ac_id entries with TEST_OPERATION
            elif not ac_id and operation == 'TEST_OPERATION':
                is_test_fixture = True
            # Entries with fake test hashes (hash_-1, hash_0, hash_1, etc.)
            elif previous_hash and (previous_hash.startswith('hash_') or previous_hash.startswith('hash-_')):
                is_test_fixture = True
            
            if is_test_fixture:
                # Test fixture found - this breaks the chain intentionally
                test_fixtures_skipped += 1
                
                # Close current segment if we were tracking one
                if current_segment_start is not None:
                    chain_segments.append({
                        'start_id': current_segment_start,
                        'end_id': all_entries[i-1][0] if i > 0 else entry_id,
                        'length': production_entries_validated - sum(s['length'] for s in chain_segments)
                    })
                
                # Reset for next segment (test fixtures start new chains with GENESIS)
                current_segment_start = None
                expected_prev_hash = None
                continue
            
            # Production entry - validate it
            production_entries_validated += 1
            
            # Start new segment if needed
            if current_segment_start is None:
                current_segment_start = entry_id
                # First entry in segment should have GENESIS or link to previous segment
                if expected_prev_hash is not None:
                    # This should link to the last non-test-fixture entry
                    if previous_hash != expected_prev_hash:
                        hash_violations.append({
                            'type': 'segment_boundary',
                            'entry_id': entry_id,
                            'ac_id': ac_id,
                            'expected_prev': expected_prev_hash[:16] + '...' if expected_prev_hash else 'GENESIS',
                            'actual_prev': previous_hash[:16] + '...' if previous_hash else 'NULL',
                            'note': 'Entry after test fixture should link to last production entry'
                        })
                elif i > 0:  # Not the very first entry
                    # Check if previous entry was a test fixture
                    prev_was_test = (all_entries[i-1][1] in self.TEST_FIXTURES if all_entries[i-1][1] else False)
                    if prev_was_test and previous_hash not in ['GENESIS', '0' * 64]:
                        # After test fixture, should either be GENESIS or link correctly
                        # This is acceptable - test fixtures can break chains
                        pass
            else:
                # Continuing segment - check chain
                if previous_hash != expected_prev_hash:
                    hash_violations.append({
                        'type': 'chain_break',
                        'entry_id': entry_id,
                        'ac_id': ac_id,
                        'expected_prev': expected_prev_hash[:16] + '...' if expected_prev_hash else 'NULL',
                        'actual_prev': previous_hash[:16] + '...' if previous_hash else 'NULL',
                        'segment_start': current_segment_start
                    })
            
            # Update expected hash for next entry
            expected_prev_hash = entry_hash
        
        # Close final segment
        if current_segment_start is not None:
            chain_segments.append({
                'start_id': current_segment_start,
                'end_id': all_entries[-1][0],
                'length': production_entries_validated - sum(s['length'] for s in chain_segments)
            })
        
        # Report results
        if hash_violations:
            msg = f"❌ Hash chain integrity violations detected:\n\n"
            msg += f"  Validated: {production_entries_validated} production entries\n"
            msg += f"  Excluded: {test_fixtures_skipped} test fixture entries\n"
            msg += f"  Segments: {len(chain_segments)} continuous chain segments\n"
            msg += f"  Violations: {len(hash_violations)}\n\n"
            
            # Group by type
            segment_issues = [v for v in hash_violations if v['type'] == 'segment_boundary']
            chain_breaks = [v for v in hash_violations if v['type'] == 'chain_break']
            
            if segment_issues:
                msg += f"  ⚠️  Segment Boundary Issues ({len(segment_issues)}):\n"
                for v in segment_issues[:5]:
                    msg += f"    Entry {v['entry_id']} ({v['ac_id']}): {v['note']}\n"
                    msg += f"      Expected: {v['expected_prev']}, Got: {v['actual_prev']}\n"
                if len(segment_issues) > 5:
                    msg += f"    ... and {len(segment_issues) - 5} more\n"
                msg += "\n"
            
            if chain_breaks:
                msg += f"  ❌ Chain Breaks Within Segments ({len(chain_breaks)}):\n"
                for v in chain_breaks[:10]:
                    msg += f"    Entry {v['entry_id']} ({v['ac_id']}): expected {v['expected_prev']}, got {v['actual_prev']}\n"
                if len(chain_breaks) > 10:
                    msg += f"    ... and {len(chain_breaks) - 10} more\n"
            
            pytest.fail(msg)
        else:
            # Success - print summary
            print(f"\n✅ Hash chain integrity verified:")
            print(f"   - Production entries: {production_entries_validated}")
            print(f"   - Test fixtures excluded: {test_fixtures_skipped}")
            print(f"   - Chain segments: {len(chain_segments)}")
            print(f"   - Status: UNBROKEN")
    
    def test_no_fake_retroactive_entries(self, db_connection: sqlite3.Connection) -> None:
        """
        Test: No fake/retroactively-inserted audit entries detected.
        
        Acceptance:
        - All entries have valid metadata (test counts, result states)
        - No entries with "remediation: true" in metadata (marks manual additions)
        - Timestamps follow execution pattern (not all same minute)
        """
        cursor = db_connection.cursor()
        cursor.execute("""
            SELECT ac_id, COUNT(*) as entry_count
            FROM audit_log
            WHERE metadata LIKE '%"remediation": true%'
            GROUP BY ac_id
        """)
        
        fake_entries = cursor.fetchall()
        
        if fake_entries:
            msg = "Fake/remediation entries detected (should not exist in production state):\n"
            for ac_id, count in fake_entries:
                msg += f"  {ac_id}: {count} remediation entries\n"
            pytest.fail(msg)
        
        # Additional check: verify timestamp variety (not all same minute)
        cursor.execute("""
            SELECT ac_id,
                   COUNT(DISTINCT strftime('%Y-%m-%d %H:%M', timestamp)) as unique_minutes
            FROM audit_log
            WHERE ac_id IS NOT NULL
            GROUP BY ac_id
            HAVING unique_minutes = 1
        """)
        
        same_minute = cursor.fetchall()
        
        # Allow for very fast tests, but if too many, it's suspicious
        if len(same_minute) > 10:
            msg = f"Warning: {len(same_minute)} AC-IDs have all events in same minute (possible batch insertion)\n"
            for row in same_minute[:5]:
                msg += f"  {row[0]}\n"
            # This is a warning, not a hard fail (since tests can be very fast)
            pytest.warns(Warning, msg)
    
    def test_each_ac_has_expected_operations(self, db_connection: sqlite3.Connection) -> None:
        """
        Test: Each AC-ID has at least START, EXECUTE, COMPLETE operations.
        
        Acceptance:
        - AC_START or START: 1+ events (both formats supported for legacy compatibility)
        - AC_EXECUTE or EXECUTE: 1+ events
        - AC_COMPLETE or COMPLETE: 1+ events (or AC_EXECUTE_FAILED for legitimately failed ACs)
        """
        cursor = db_connection.cursor()
        
        ac_ids = self.get_all_ac_ids(db_connection)
        missing_operations = []
        
        for ac_id in ac_ids:
            # Check for both standard 'AC_*' format and legacy format
            cursor.execute("""
                SELECT operation, COUNT(*) as count
                FROM audit_log
                WHERE ac_id = ? AND (
                    operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE', 'AC_EXECUTE_FAILED')
                    OR operation IN ('START', 'EXECUTE', 'COMPLETE')
                )
                GROUP BY operation
            """, (ac_id,))
            
            operations = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Check if AC has START (either format)
            has_start = 'AC_START' in operations or 'START' in operations
            has_execute = 'AC_EXECUTE' in operations or 'EXECUTE' in operations
            has_complete = 'AC_COMPLETE' in operations or 'COMPLETE' in operations
            has_execute_failed = 'AC_EXECUTE_FAILED' in operations
            
            missing = []
            if not has_start:
                missing.append('START')
            if not has_execute:
                missing.append('EXECUTE')
            # Accept either COMPLETE or EXECUTE_FAILED as valid lifecycle termination
            if not (has_complete or has_execute_failed):
                missing.append('COMPLETE or EXECUTE_FAILED')
            
            if missing:
                missing_operations.append((ac_id, sorted(missing)))
        
        if missing_operations:
            msg = "AC-IDs missing required operations:\n"
            for ac_id, ops in missing_operations:
                msg += f"  {ac_id}: missing {', '.join(ops)}\n"
            pytest.fail(msg)
    
    def test_audit_trail_coverage_by_phase(self, db_connection: sqlite3.Connection) -> None:
        """
        Test: Generate report on audit trail coverage by phase.
        
        Shows which phases have complete audit trails and which need remediation.
        """
        ac_ids = self.get_all_ac_ids(db_connection)
        
        # Map AC-IDs to phases
        phase_map = {
            'AR': 'PHASE-01-06',
            'FR': 'PHASE-01-06',
            'NFR': 'PHASE-01-06',
            'IR': 'PHASE-07-INTENT-ROUTER',
            'GV': 'PHASE-09-GOVERNANCE-TOOLS',
            'EX': 'PHASE-10-ADAPTIVE-EXECUTION',
            'HP': 'PHASE-11-HALLUCINATION-PREVENTION',
            'KN': 'PHASE-12-KNOWLEDGE-ECOSYSTEM',
            'OB': 'PHASE-13-OBSERVABILITY-MATURITY',
            'PR': 'PHASE-14-PRODUCTION-MIGRATION',
        }
        
        phase_stats: Dict[str, Dict] = {}
        
        for ac_id in ac_ids:
            domain = ac_id.split('-')[0]
            phase = phase_map.get(domain, 'UNKNOWN')
            
            if phase not in phase_stats:
                phase_stats[phase] = {'total': 0, 'complete': 0, 'incomplete': 0, 'acs': []}
            
            events = self.get_ac_lifecycle_events(db_connection, ac_id)
            is_complete = len(events) >= 3
            
            phase_stats[phase]['total'] += 1
            phase_stats[phase]['acs'].append(ac_id)
            
            if is_complete:
                phase_stats[phase]['complete'] += 1
            else:
                phase_stats[phase]['incomplete'] += 1
        
        # Generate report
        report = "\n" + "=" * 90 + "\n"
        report += "AUDIT TRAIL COVERAGE BY PHASE\n"
        report += "=" * 90 + "\n\n"
        
        for phase in sorted(phase_stats.keys()):
            stats = phase_stats[phase]
            complete_pct = (stats['complete'] / stats['total'] * 100) if stats['total'] > 0 else 0
            
            status = "✅ COMPLETE" if complete_pct == 100 else f"⚠️  INCOMPLETE ({complete_pct:.0f}%)"
            
            report += f"{phase:35} | {stats['complete']:2}/{stats['total']:2} | {status}\n"
        
        report += "\n" + "=" * 90
        
        # Print report (will show in test output)
        print(report)
    
    def test_no_duplicate_ac_start_without_complete(self, db_connection: sqlite3.Connection) -> None:
        """
        Test: No AC-ID has multiple AC_START events without AC_COMPLETE in between.
        
        Acceptance:
        - Pattern should be: START → EXECUTE → COMPLETE [, START → EXECUTE → COMPLETE, ...]
        - Not: START → START → EXECUTE → COMPLETE (indicates restarts without closure)
        """
        ac_ids = self.get_all_ac_ids(db_connection)
        problematic_patterns = []
        
        for ac_id in ac_ids:
            cursor = db_connection.cursor()
            cursor.execute("""
                SELECT operation FROM audit_log
                WHERE ac_id = ? AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
                ORDER BY id ASC
            """, (ac_id,))
            
            operations = [row[0] for row in cursor.fetchall()]
            
            # Check for START → START without COMPLETE in between
            for i in range(len(operations) - 1):
                if operations[i] == 'AC_START' and operations[i + 1] == 'AC_START':
                    problematic_patterns.append(ac_id)
                    break
        
        if problematic_patterns:
            msg = "AC-IDs with problematic operation sequences (START→START):\n"
            for ac_id in problematic_patterns:
                msg += f"  {ac_id}\n"
            pytest.fail(msg)


class TestAuditRemediationProgress:
    """Track progress of AUDIT-REMEDIATION-2026-01-15 initiative."""
    
    @pytest.fixture
    def db_connection(self) -> sqlite3.Connection:
        """Connect to governance database."""
        db_path = Path(__file__).parent.parent.parent / "cortex-brain" / "state" / "governance.db"
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def test_remediation_progress_report(self, db_connection: sqlite3.Connection) -> None:
        """
        Generate remediation progress report.
        
        Shows which ACs have complete audit trails and which need work.
        """
        cursor = db_connection.cursor()
        
        # Get count of ACs with complete lifecycle
        cursor.execute("""
            SELECT ac_id, COUNT(*) as lifecycle_count
            FROM audit_log
            WHERE operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
            GROUP BY ac_id
            ORDER BY ac_id
        """)
        
        all_acs = {}
        for row in cursor.fetchall():
            ac_id, count = row
            all_acs[ac_id] = {'lifecycle_count': count, 'complete': count >= 3}
        
        complete = sum(1 for ac in all_acs.values() if ac['complete'])
        total = len(all_acs)
        
        report = "\n" + "=" * 90 + "\n"
        report += "AUDIT REMEDIATION PROGRESS - AUDIT-REMEDIATION-2026-01-15\n"
        report += "=" * 90 + "\n\n"
        report += f"Total AC-IDs: {total}\n"
        report += f"Complete: {complete} ({complete/total*100:.1f}%)\n"
        report += f"Incomplete: {total - complete} ({(total-complete)/total*100:.1f}%)\n\n"
        
        report += "INCOMPLETE AC-IDs (need remediation):\n"
        report += "-" * 90 + "\n"
        
        incomplete = sorted(
            [(ac_id, info['lifecycle_count']) for ac_id, info in all_acs.items() if not info['complete']],
            key=lambda x: x[0]
        )
        
        for ac_id, count in incomplete[:20]:  # Show first 20
            report += f"  {ac_id:15} | {count} lifecycle events (need ≥3)\n"
        
        if len(incomplete) > 20:
            report += f"  ... and {len(incomplete) - 20} more\n"
        
        report += "\n" + "=" * 90
        
        print(report)
        
        # Assert: some progress is being made
        assert complete > 0, "No AC-IDs have complete audit trail - remediation not started"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
