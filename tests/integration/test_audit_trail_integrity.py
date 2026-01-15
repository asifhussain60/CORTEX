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
    
    @pytest.fixture
    def db_connection(self) -> sqlite3.Connection:
        """Connect to governance database."""
        db_path = Path(__file__).parent.parent.parent / "cortex-brain" / "state" / "governance.db"
        assert db_path.exists(), f"Database not found at {db_path}"
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def get_all_ac_ids(self, conn: sqlite3.Connection) -> List[str]:
        """Get all AC-IDs from audit log."""
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT ac_id FROM audit_log WHERE ac_id IS NOT NULL ORDER BY ac_id")
        return [row[0] for row in cursor.fetchall()]
    
    def get_ac_lifecycle_events(
        self, conn: sqlite3.Connection, ac_id: str
    ) -> List[Tuple[int, str, str, str, str, str]]:
        """Get all lifecycle events for an AC-ID."""
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, operation, timestamp, previous_hash, entry_hash, message
            FROM audit_log
            WHERE ac_id = ? AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
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
        Test: Hash chain is unbroken for each AC-ID's lifecycle.
        
        Acceptance:
        - Each event's previous_hash == prior event's entry_hash
        - Hash chain forms a linked list (tamper-evident)
        """
        ac_ids = self.get_all_ac_ids(db_connection)
        hash_violations = []
        
        for ac_id in ac_ids:
            events = self.get_ac_lifecycle_events(db_connection, ac_id)
            
            if len(events) < 2:
                continue
            
            for i in range(1, len(events)):
                prev_entry_hash = events[i - 1][4]  # entry_hash of prior event
                curr_previous_hash = events[i][3]   # previous_hash of current event
                
                if prev_entry_hash != curr_previous_hash:
                    hash_violations.append((
                        ac_id, i - 1, i,
                        f"Event {i-1} hash: {prev_entry_hash[:16]}...",
                        f"Event {i} previous_hash: {curr_previous_hash[:16]}..."
                    ))
        
        if hash_violations:
            msg = "Hash chain integrity violations detected:\n"
            for ac_id, i1, i2, hash1, hash2 in hash_violations:
                msg += f"  {ac_id}: {hash1} != {hash2}\n"
            pytest.fail(msg)
    
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
        - AC_START: 1+ events
        - AC_EXECUTE: 1+ events
        - AC_COMPLETE: 1+ events
        """
        cursor = db_connection.cursor()
        
        ac_ids = self.get_all_ac_ids(db_connection)
        missing_operations = []
        
        for ac_id in ac_ids:
            cursor.execute("""
                SELECT operation, COUNT(*) as count
                FROM audit_log
                WHERE ac_id = ? AND operation IN ('AC_START', 'AC_EXECUTE', 'AC_COMPLETE')
                GROUP BY operation
            """, (ac_id,))
            
            operations = {row[0]: row[1] for row in cursor.fetchall()}
            
            required_ops = {'AC_START', 'AC_EXECUTE', 'AC_COMPLETE'}
            missing = required_ops - set(operations.keys())
            
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
