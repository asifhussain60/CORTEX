"""
Conflict Resolution Truth Test (WAVE-10 Track 1, Deliverable T1-D5)

Purpose:
    Verify conflict detection and resolution using precedence-based winner selection.
    Tests that conflicting rules are properly resolved with clear audit trail.
    
    Checks: Precedence-based selection, conflict detection, audit recording,
    winner/loser determination with clear reasoning.

Authority:
    - WAVE-10 Track 1 Golden Path Tests
    - ENH-089+ phase delivery
    - Audit Truth Layer verification

AC-ID: AC-WAVE10-T1-D5-001
"""

import pytest
import sqlite3
import tempfile
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import Dict, Any, List, Optional


@dataclass
class ConflictingRule:
    """Definition of a conflicting rule."""
    rule_id: str
    precedence: int
    source: str
    value: str


@dataclass
class ConflictResolution:
    """Result of resolving a conflict."""
    winner: ConflictingRule
    loser: ConflictingRule
    resolution_reason: str
    resolved_at: str


@dataclass
class ConflictResolutionResult:
    """Batch conflict resolution result."""
    conflicts_detected: int
    resolutions: List[ConflictResolution]
    all_resolved: bool
    total_precedence_wins: int


class MockConflictResolutionEngine:
    """Mock conflict resolution engine."""
    
    def __init__(self, audit_db_path: str):
        """Initialize with audit database path."""
        self.audit_db_path = audit_db_path
    
    def detect_and_resolve_conflicts(self, rules: List[Dict[str, Any]]) -> ConflictResolutionResult:
        """
        Detect conflicting rules and resolve via precedence.
        Rules with same ID but different values = conflict.
        Highest precedence wins.
        """
        resolutions = []
        conflicts_detected = 0
        timestamp = datetime.now().isoformat()
        
        # Group by rule ID to find conflicts
        rule_groups = {}
        for rule in rules:
            rule_id = rule.get("id")
            if rule_id not in rule_groups:
                rule_groups[rule_id] = []
            rule_groups[rule_id].append(rule)
        
        # Resolve conflicts
        for rule_id, rule_list in rule_groups.items():
            if len(rule_list) > 1:
                # Conflict detected
                conflicts_detected += 1
                
                # Sort by precedence (highest first)
                sorted_rules = sorted(rule_list, key=lambda r: r.get("precedence", 0), reverse=True)
                
                winner_data = sorted_rules[0]
                loser_data = sorted_rules[1]
                
                winner = ConflictingRule(
                    rule_id=rule_id,
                    precedence=winner_data.get("precedence", 0),
                    source=winner_data.get("source", "unknown"),
                    value=winner_data.get("value", "")
                )
                
                loser = ConflictingRule(
                    rule_id=rule_id,
                    precedence=loser_data.get("precedence", 0),
                    source=loser_data.get("source", "unknown"),
                    value=loser_data.get("value", "")
                )
                
                resolution = ConflictResolution(
                    winner=winner,
                    loser=loser,
                    resolution_reason=f"Precedence-based: {winner.precedence} > {loser.precedence}",
                    resolved_at=timestamp
                )
                resolutions.append(resolution)
                
                # Log to audit
                self._log_audit("conflict_resolved", rule_id, {
                    "winner_precedence": winner.precedence,
                    "loser_precedence": loser.precedence,
                    "reason": resolution.resolution_reason,
                    "timestamp": timestamp
                })
        
        return ConflictResolutionResult(
            conflicts_detected=conflicts_detected,
            resolutions=resolutions,
            all_resolved=len(resolutions) == conflicts_detected,
            total_precedence_wins=len([r for r in resolutions if r.winner.precedence > r.loser.precedence])
        )
    
    def validate_resolution_logic(self, conflicts: List[Dict[str, Any]]) -> bool:
        """Validate that all resolutions follow precedence rule correctly."""
        timestamp = datetime.now().isoformat()
        valid = True
        
        for conflict in conflicts:
            winner_prec = conflict.get("winner_precedence", 0)
            loser_prec = conflict.get("loser_precedence", 0)
            
            if winner_prec <= loser_prec:
                valid = False
                self._log_audit("invalid_resolution", conflict.get("rule_id"), {
                    "error": "Winner precedence not higher than loser",
                    "timestamp": timestamp
                })
        
        if valid:
            self._log_audit("resolution_validation_passed", "all", {
                "total_conflicts_validated": len(conflicts),
                "timestamp": timestamp
            })
        
        return valid
    
    def _log_audit(self, operation: str, rule_id: str, metadata: Dict):
        """Log operation to audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(metadata)
        
        cursor.execute("""
            INSERT INTO audit (timestamp, operation, rule_id, source, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, operation, rule_id, "conflict_resolution", metadata_json))
        
        conn.commit()
        conn.close()


class TestConflictDetectionTruth:
    """Conflict Detection Truth Test with Audit Verification."""
    
    @pytest.fixture
    def audit_db_path(self):
        """Create temporary audit database for test."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        # Initialize schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                rule_id TEXT,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        yield db_path
        Path(db_path).unlink()
    
    @pytest.fixture
    def engine(self, audit_db_path):
        """Initialize conflict resolution engine."""
        return MockConflictResolutionEngine(audit_db_path=audit_db_path)
    
    def test_conflicts_detected_correctly(self, engine, audit_db_path):
        """
        RED PHASE: Test must fail if:
        1. conflicts not detected when rules conflict
        2. detection count incorrect
        3. audit trail missing conflict_resolved entries
        
        GREEN PHASE: Test passes when:
        1. all conflicts detected
        2. count accurate
        3. audit complete
        """
        # Setup: Conflicting rules
        rules = [
            {"id": "RULE-A", "precedence": 10, "source": "cortex", "value": "value1"},
            {"id": "RULE-A", "precedence": 5, "source": "company", "value": "value2"},  # Conflict!
            {"id": "RULE-B", "precedence": 8, "source": "cortex", "value": "value3"},
            {"id": "RULE-B", "precedence": 12, "source": "company", "value": "value4"},  # Conflict!
            {"id": "RULE-C", "precedence": 7, "source": "cortex", "value": "value5"},
        ]
        
        # Execute
        result = engine.detect_and_resolve_conflicts(rules)
        
        # Assert: Correct conflict count
        assert result.conflicts_detected == 2, "Should detect 2 conflicts"
        assert len(result.resolutions) == 2
        assert result.all_resolved is True
        
        # Audit Verification
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        # Query conflict resolutions
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE operation = 'conflict_resolved'"
        )
        resolution_count = cursor.fetchone()[0]
        
        # RED phase
        assert resolution_count == 2, f"Expected 2 conflict resolutions in audit, got {resolution_count}"
        
        conn.close()
    
    def test_precedence_based_winner_selection(self, engine, audit_db_path):
        """Verify winner selected by highest precedence."""
        # Setup: Clear precedence difference
        rules = [
            {"id": "RULE-X", "precedence": 5, "source": "company", "value": "company_value"},
            {"id": "RULE-X", "precedence": 15, "source": "cortex", "value": "cortex_value"},
        ]
        
        # Execute
        result = engine.detect_and_resolve_conflicts(rules)
        
        # Assert: Winner is cortex (precedence 15)
        assert len(result.resolutions) == 1
        resolution = result.resolutions[0]
        assert resolution.winner.precedence == 15
        assert resolution.winner.source == "cortex"
        assert resolution.loser.precedence == 5
        assert resolution.loser.source == "company"
        
        # Assert: Precedence rule verified
        assert result.total_precedence_wins == 1
        
        # Audit: Winner precedence should be in metadata
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT metadata FROM audit WHERE operation = 'conflict_resolved' "
            "AND rule_id = 'RULE-X'"
        )
        metadata = cursor.fetchone()
        
        assert metadata is not None
        data = json.loads(metadata[0])
        assert data["winner_precedence"] == 15
        assert data["loser_precedence"] == 5
        
        conn.close()
    
    def test_no_conflicts_when_rules_unique(self, engine, audit_db_path):
        """Verify no conflicts when rules don't overlap."""
        # Setup: No conflicts
        rules = [
            {"id": "RULE-1", "precedence": 10, "source": "cortex", "value": "v1"},
            {"id": "RULE-2", "precedence": 8, "source": "company", "value": "v2"},
            {"id": "RULE-3", "precedence": 12, "source": "cortex", "value": "v3"},
        ]
        
        # Execute
        result = engine.detect_and_resolve_conflicts(rules)
        
        # Assert: No conflicts
        assert result.conflicts_detected == 0
        assert len(result.resolutions) == 0
        assert result.all_resolved is True
        
        # Audit: No conflict_resolved entries
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE operation = 'conflict_resolved'"
        )
        count = cursor.fetchone()[0]
        
        assert count == 0
        
        conn.close()


class TestConflictResolutionValidationTruth:
    """Validate conflict resolution logic correctness."""
    
    @pytest.fixture
    def audit_db_path(self):
        """Create temporary audit database for test."""
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
            db_path = f.name
        
        # Initialize schema
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                operation TEXT NOT NULL,
                rule_id TEXT,
                source TEXT,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()
        
        yield db_path
        Path(db_path).unlink()
    
    def test_resolution_logic_validation_passes(self, audit_db_path):
        """Verify resolution logic validates correctly."""
        engine = MockConflictResolutionEngine(audit_db_path)
        
        # Setup: Valid resolutions (winner > loser)
        conflicts = [
            {"rule_id": "R1", "winner_precedence": 15, "loser_precedence": 5},
            {"rule_id": "R2", "winner_precedence": 10, "loser_precedence": 8},
            {"rule_id": "R3", "winner_precedence": 20, "loser_precedence": 1},
        ]
        
        # Execute
        is_valid = engine.validate_resolution_logic(conflicts)
        
        # Assert
        assert is_valid is True
        
        # Audit: Validation passed entry
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE operation = 'resolution_validation_passed'"
        )
        count = cursor.fetchone()[0]
        
        assert count == 1
        
        conn.close()
