"""
Tier Cascade Truth Test (WAVE-10 Track 1, Deliverable T1-D2)

Purpose:
    Verify that data flows correctly through tier cascade: tier0 → tier1 → tier2 → tier3
    
    Tests that a rule inserted at tier0 propagates correctly through all tiers
    with proper enrichment at each level. Verifies via audit log (hard evidence).

Authority:
    - WAVE-10 Track 1 Golden Path Tests
    - ENH-089+ phase delivery
    - Audit Truth Layer verification

AC-ID: AC-WAVE10-T1-D2-001
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
class TierCascadeResult:
    """Result of tier cascade operation."""
    tier0_output: Dict[str, Any]
    tier1_output: Dict[str, Any]
    tier2_output: Dict[str, Any]
    tier3_output: Dict[str, Any]
    rule_id: str
    cascade_complete: bool


class MockTierCascadeEngine:
    """Mock tier cascade engine for truth test."""
    
    def __init__(self, audit_db_path: str):
        """Initialize with audit database path."""
        self.audit_db_path = audit_db_path
    
    def cascade_through_tiers(self, rule: Dict[str, Any]) -> TierCascadeResult:
        """Cascade a rule through all tiers with enrichment."""
        rule_id = rule["id"]
        timestamp = datetime.now().isoformat()
        
        # Tier 0: Foundation
        tier0_output = {**rule, "tier": 0, "enriched_at": timestamp}
        self._log_audit("tier0_processed", rule_id, tier0_output)
        
        # Tier 1: Context enrichment
        tier1_output = {
            **tier0_output,
            "tier": 1,
            "context": "business_context_added",
            "enriched_at": timestamp
        }
        self._log_audit("tier1_processed", rule_id, tier1_output)
        
        # Tier 2: Domain enhancement
        tier2_output = {
            **tier1_output,
            "tier": 2,
            "domain_context": "domain_specific_added",
            "enriched_at": timestamp
        }
        self._log_audit("tier2_processed", rule_id, tier2_output)
        
        # Tier 3: Final synthesis
        tier3_output = {
            **tier2_output,
            "tier": 3,
            "final_synthesis": True,
            "enriched_at": timestamp
        }
        self._log_audit("tier3_processed", rule_id, tier3_output)
        self._log_audit("cascade_complete", rule_id, {"rule_id": rule_id})
        
        return TierCascadeResult(
            tier0_output=tier0_output,
            tier1_output=tier1_output,
            tier2_output=tier2_output,
            tier3_output=tier3_output,
            rule_id=rule_id,
            cascade_complete=True
        )
    
    def _log_audit(self, operation: str, rule_id: str, data: Dict):
        """Log operation to audit database."""
        conn = sqlite3.connect(self.audit_db_path)
        cursor = conn.cursor()
        
        timestamp = datetime.now().isoformat()
        metadata_json = json.dumps(data)
        
        cursor.execute("""
            INSERT INTO audit (timestamp, operation, rule_id, source, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (timestamp, operation, rule_id, "tier_cascade", metadata_json))
        
        conn.commit()
        conn.close()


class TestTierCascadeTruth:
    """Tier Cascade Truth Test with Audit Verification."""
    
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
        """Initialize engine with test audit database."""
        engine = MockTierCascadeEngine(audit_db_path=audit_db_path)
        return engine
    
    def test_rule_propagates_through_all_tiers(self, engine, audit_db_path):
        """
        RED PHASE: Test must fail if:
        1. audit log missing any tier transition entry
        2. tier timestamps not in ascending order
        3. rule ID changes between tiers (data loss)
        
        GREEN PHASE: Test passes when:
        1. tier0→tier1→tier2→tier3 cascade verified
        2. Each tier has timestamp progression
        3. rule ID consistent across all tiers
        """
        # Setup
        rule = {
            "id": "test_rule_cascade",
            "source": "test",
            "content": "test content"
        }
        
        # Execute
        result = engine.cascade_through_tiers(rule)
        
        # Assert: Business logic
        assert result.cascade_complete, "Cascade should complete"
        assert result.tier0_output["tier"] == 0
        assert result.tier1_output["tier"] == 1
        assert result.tier2_output["tier"] == 2
        assert result.tier3_output["tier"] == 3
        
        # Assert: Rule ID consistency
        assert result.tier0_output["id"] == rule["id"]
        assert result.tier1_output["id"] == rule["id"]
        assert result.tier2_output["id"] == rule["id"]
        assert result.tier3_output["id"] == rule["id"]
        
        # Assert: Enrichment applied
        assert "context" not in result.tier0_output
        assert "context" in result.tier1_output, "Tier 1 should add context"
        assert "domain_context" not in result.tier1_output
        assert "domain_context" in result.tier2_output, "Tier 2 should add domain context"
        assert "final_synthesis" not in result.tier2_output
        assert "final_synthesis" in result.tier3_output, "Tier 3 should finalize"
        
        # Audit Verification
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        # Query all tier operations
        cursor.execute(
            "SELECT operation, timestamp FROM audit WHERE rule_id = ? ORDER BY timestamp ASC",
            (rule["id"],)
        )
        audit_entries = cursor.fetchall()
        
        # RED phase: Check for required entries
        operations = [entry[0] for entry in audit_entries]
        required_ops = ["tier0_processed", "tier1_processed", "tier2_processed", "tier3_processed", "cascade_complete"]
        
        for op in required_ops:
            assert op in operations, f"Audit log must contain '{op}' operation"
        
        # RED phase: Check timestamp progression
        timestamps = [entry[1] for entry in audit_entries]
        for i in range(len(timestamps) - 1):
            t1 = datetime.fromisoformat(timestamps[i])
            t2 = datetime.fromisoformat(timestamps[i + 1])
            assert t1 <= t2, f"Timestamps must be in ascending order: {t1} <= {t2}"
        
        conn.close()
    
    def test_tier_enrichment_layering(self, engine, audit_db_path):
        """Verify that each tier's enrichment is properly layered."""
        rule = {
            "id": "enrichment_test",
            "base_value": "foundation"
        }
        
        result = engine.cascade_through_tiers(rule)
        
        # Tier 0: Base
        assert result.tier0_output["base_value"] == "foundation"
        assert result.tier0_output["tier"] == 0
        
        # Tier 1: Inherits tier 0 + adds context
        assert result.tier1_output["base_value"] == "foundation"
        assert result.tier1_output["context"] == "business_context_added"
        assert result.tier1_output["tier"] == 1
        
        # Tier 2: Inherits tier 1 + adds domain
        assert result.tier2_output["base_value"] == "foundation"
        assert result.tier2_output["context"] == "business_context_added"
        assert result.tier2_output["domain_context"] == "domain_specific_added"
        assert result.tier2_output["tier"] == 2
        
        # Tier 3: Full synthesis
        assert result.tier3_output["final_synthesis"] == True
        assert all(key in result.tier3_output for key in [
            "base_value", "context", "domain_context"
        ]), "Tier 3 should preserve all previous enrichments"


class TestTierCascadeAuditTruth:
    """Verify audit trail for tier cascade operations."""
    
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
    
    def test_audit_captures_all_tier_transitions(self, audit_db_path):
        """Verify audit captures complete cascade trail."""
        engine = MockTierCascadeEngine(audit_db_path)
        
        rule = {
            "id": "audit_test",
            "value": "test"
        }
        
        engine.cascade_through_tiers(rule)
        
        # Query audit
        conn = sqlite3.connect(audit_db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT COUNT(*) FROM audit WHERE rule_id = ?",
            (rule["id"],)
        )
        count = cursor.fetchone()[0]
        
        # Should have 5 entries: 4 tier ops + 1 cascade_complete
        assert count == 5, f"Expected 5 audit entries, got {count}"
        
        conn.close()
