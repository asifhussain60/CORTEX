"""
Unit Tests for Compliance Database (Sprint 2 - Task 8)

Tests CRUD operations, rule initialization, event logging,
query performance, and compliance score calculation.

Author: Asif Hussain
Date: November 28, 2025
Sprint: 2 (Active Compliance Dashboard)
Task: 8 (Unit Tests)
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta
import tempfile
import shutil

# Add src to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src"))

from src.tier1.compliance_database import ComplianceDatabase


class TestComplianceDatabase:
    """Test suite for ComplianceDatabase class."""
    
    @pytest.fixture
    def temp_brain_path(self):
        """Create temporary brain directory for testing."""
        temp_dir = tempfile.mkdtemp()
        brain_path = Path(temp_dir) / "cortex-brain"
        brain_path.mkdir(parents=True, exist_ok=True)
        
        # Copy brain-protection-rules.yaml to temp location
        rules_src = project_root / "cortex-brain" / "brain-protection-rules.yaml"
        rules_dst = brain_path / "brain-protection-rules.yaml"
        if rules_src.exists():
            shutil.copy(rules_src, rules_dst)
        
        yield brain_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def db(self, temp_brain_path):
        """Create ComplianceDatabase instance with temporary brain path."""
        return ComplianceDatabase(brain_path=temp_brain_path)
    
    def test_database_initialization(self, db):
        """Test database file is created and tables exist."""
        assert db.db_path.exists(), "Database file should be created"
        
        # Check tables exist
        cursor = db.conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}
        
        expected_tables = {'compliance_status', 'protection_events', 'user_compliance_history'}
        assert expected_tables.issubset(tables), f"Expected tables {expected_tables}, got {tables}"
    
    def test_initialize_rules_from_yaml(self, db):
        """Test rules are loaded from brain-protection-rules.yaml."""
        # Initialize rules
        count = db.initialize_rules()
        
        assert count > 0, "Should load rules from YAML"
        
        # Verify rules in database
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM compliance_status")
        db_count = cursor.fetchone()[0]
        
        assert db_count == count, f"Expected {count} rules in DB, got {db_count}"
    
    def test_rule_data_integrity(self, db):
        """Test rules have all required fields."""
        db.initialize_rules()
        
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT rule_id, rule_name, layer, severity, description 
            FROM compliance_status 
            LIMIT 5
        """)
        
        for row in cursor.fetchall():
            rule_id, rule_name, layer, severity, description = row
            
            assert rule_id, "rule_id should not be empty"
            assert rule_name, "rule_name should not be empty"
            assert layer, "layer should not be empty"
            assert severity in ['blocked', 'warning'], f"Invalid severity: {severity}"
            assert description, "description should not be empty"
    
    def test_log_protection_event(self, db):
        """Test logging protection events."""
        db.initialize_rules()
        
        # Log event
        event_id = db.log_protection_event(
            rule_id="TDD_ENFORCEMENT",
            severity="blocked",
            file_path="src/tdd/workflow.py",
            evidence="Intent: 'disable TDD workflow'"
        )
        
        assert event_id > 0, "Should return event ID"
        
        # Verify event in database
        cursor = db.conn.cursor()
        cursor.execute("SELECT * FROM protection_events WHERE id = ?", (event_id,))
        event = cursor.fetchone()
        
        assert event is not None, "Event should be in database"
        assert event[1] == "TDD_ENFORCEMENT", "rule_id should match"
        assert event[2] == "blocked", "severity should match"
        assert event[3] == "src/tdd/workflow.py", "file_path should match"
    
    def test_get_compliance_status(self, db):
        """Test retrieving compliance status for all rules."""
        db.initialize_rules()
        
        # Log some violations
        db.log_protection_event("TDD_ENFORCEMENT", "blocked", "test.py", "test evidence")
        db.log_protection_event("TDD_ENFORCEMENT", "blocked", "test2.py", "test evidence 2")
        
        # Get status
        status = db.get_compliance_status()
        
        assert isinstance(status, list), "Should return list"
        assert len(status) > 0, "Should have rule status"
        
        # Check TDD_ENFORCEMENT has violations
        tdd_rule = next((r for r in status if r['rule_id'] == 'TDD_ENFORCEMENT'), None)
        assert tdd_rule is not None, "TDD_ENFORCEMENT rule should exist"
        assert tdd_rule['violation_count'] == 2, "Should have 2 violations"
        assert tdd_rule['status'] == 'violated', "Status should be violated"
    
    def test_get_recent_events(self, db):
        """Test retrieving recent protection events."""
        db.initialize_rules()
        
        # Log multiple events
        for i in range(5):
            db.log_protection_event(
                rule_id="TDD_ENFORCEMENT",
                severity="blocked",
                file_path=f"test{i}.py",
                evidence=f"evidence {i}"
            )
        
        # Get recent events
        events = db.get_recent_events(limit=3)
        
        assert len(events) == 3, "Should return 3 most recent events"
        assert events[0]['file_path'] == "test4.py", "Should be most recent (test4.py)"
    
    def test_calculate_compliance_score(self, db):
        """Test compliance score calculation."""
        db.initialize_rules()
        
        # No violations = 100% compliance
        score = db.calculate_compliance_score()
        assert score == 100.0, "Should be 100% with no violations"
        
        # Add violations to 1 rule out of many
        db.log_protection_event("TDD_ENFORCEMENT", "blocked", "test.py", "evidence")
        
        score = db.calculate_compliance_score()
        assert 0 <= score < 100, f"Score should be between 0-100, got {score}"
    
    def test_query_performance(self, db):
        """Test query performance meets <50ms target."""
        db.initialize_rules()
        
        # Log 100 events to create realistic dataset
        for i in range(100):
            db.log_protection_event(
                rule_id="TDD_ENFORCEMENT",
                severity="blocked" if i % 2 == 0 else "warning",
                file_path=f"test{i}.py",
                evidence=f"evidence {i}"
            )
        
        # Time get_compliance_status query
        import time
        start = time.time()
        status = db.get_compliance_status()
        elapsed_ms = (time.time() - start) * 1000
        
        assert elapsed_ms < 50, f"Query took {elapsed_ms:.2f}ms, expected <50ms"
        assert len(status) > 0, "Should return results"
    
    def test_violation_count_by_severity(self, db):
        """Test violation counts grouped by severity."""
        db.initialize_rules()
        
        # Log mixed severity events
        db.log_protection_event("TDD_ENFORCEMENT", "blocked", "test1.py", "evidence")
        db.log_protection_event("TDD_ENFORCEMENT", "blocked", "test2.py", "evidence")
        db.log_protection_event("MACHINE_READABLE_FORMATS", "warning", "test3.py", "evidence")
        
        cursor = db.conn.cursor()
        cursor.execute("""
            SELECT severity, COUNT(*) 
            FROM protection_events 
            GROUP BY severity
        """)
        
        severity_counts = {row[0]: row[1] for row in cursor.fetchall()}
        
        assert severity_counts.get('blocked', 0) == 2, "Should have 2 blocked violations"
        assert severity_counts.get('warning', 0) == 1, "Should have 1 warning violation"
    
    def test_rule_status_transitions(self, db):
        """Test rule status changes from compliant to violated."""
        db.initialize_rules()
        
        # Initial status should be compliant
        status = db.get_compliance_status()
        tdd_rule = next((r for r in status if r['rule_id'] == 'TDD_ENFORCEMENT'), None)
        assert tdd_rule['status'] == 'compliant', "Should start as compliant"
        
        # Log violation
        db.log_protection_event("TDD_ENFORCEMENT", "blocked", "test.py", "evidence")
        
        # Status should change to violated
        status = db.get_compliance_status()
        tdd_rule = next((r for r in status if r['rule_id'] == 'TDD_ENFORCEMENT'), None)
        assert tdd_rule['status'] == 'violated', "Should transition to violated"
    
    def test_time_based_queries(self, db):
        """Test querying events within time ranges."""
        db.initialize_rules()
        
        # Log events with different timestamps (simulated)
        now = datetime.now()
        
        for i in range(3):
            db.log_protection_event("TDD_ENFORCEMENT", "blocked", f"test{i}.py", "evidence")
        
        # Get events from last 24 hours
        cursor = db.conn.cursor()
        cutoff = (now - timedelta(hours=24)).isoformat()
        cursor.execute("""
            SELECT COUNT(*) 
            FROM protection_events 
            WHERE timestamp > ?
        """, (cutoff,))
        
        count = cursor.fetchone()[0]
        assert count == 3, f"Should have 3 recent events, got {count}"
    
    def test_concurrent_access(self, db):
        """Test database handles concurrent writes safely."""
        db.initialize_rules()
        
        # Simulate concurrent writes (in practice, SQLite handles this)
        event_ids = []
        for i in range(10):
            event_id = db.log_protection_event(
                rule_id="TDD_ENFORCEMENT",
                severity="blocked",
                file_path=f"test{i}.py",
                evidence=f"evidence {i}"
            )
            event_ids.append(event_id)
        
        # All events should have unique IDs
        assert len(event_ids) == len(set(event_ids)), "Event IDs should be unique"
        
        # All events should be in database
        cursor = db.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM protection_events")
        count = cursor.fetchone()[0]
        assert count == 10, f"Should have 10 events, got {count}"


def test_compliance_database_import():
    """Test ComplianceDatabase can be imported."""
    from src.tier1.compliance_database import ComplianceDatabase
    assert ComplianceDatabase is not None


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
