"""
Tests for IntelligencePreserver - snapshot and restore CORTEX intelligence.

TDD Tests for preserving governance.db, tier1 rules, and learned patterns.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import sqlite3
import hashlib


class TestIntelligencePreserverSnapshot:
    """Tests for creating intelligence snapshots."""

    def test_snapshot_governance_db(self, tmp_path):
        """Should snapshot governance.db to .cortex-snapshots."""
        from cortex.orchestrators.intelligence_preserver import IntelligencePreserver
        
        # Create mock governance.db
        state_dir = tmp_path / "cortex_brain" / "state"
        state_dir.mkdir(parents=True)
        db_path = state_dir / "governance.db"
        
        conn = sqlite3.connect(db_path)
        conn.execute("CREATE TABLE audit (id INTEGER PRIMARY KEY, data TEXT)")
        conn.execute("INSERT INTO audit VALUES (1, 'test data')")
        conn.commit()
        conn.close()
        
        preserver = IntelligencePreserver(tmp_path)
        result = preserver.snapshot_governance_db("7.2.0")
        
        assert result["success"] is True
        snapshot_path = tmp_path / ".cortex-snapshots" / "v7.2.0" / "governance.db"
        assert snapshot_path.exists()

    def test_snapshot_tier1_rules(self, tmp_path):
        """Should snapshot tier1 rules directory."""
        from cortex.orchestrators.intelligence_preserver import IntelligencePreserver
        
        # Create mock tier1 rules
        tier1_dir = tmp_path / "cortex_brain" / "tier1"
        tier1_dir.mkdir(parents=True)
        (tier1_dir / "finops-rules.yaml").write_text("rules: [cost-tracking]")
        (tier1_dir / "auth-rules.yaml").write_text("rules: [session-mgmt]")
        
        preserver = IntelligencePreserver(tmp_path)
        result = preserver.snapshot_tier1_rules("7.2.0")
        
        assert result["success"] is True
        assert result["files_copied"] == 2

    def test_snapshot_learned_patterns(self, tmp_path):
        """Should snapshot learned patterns (rule hits, routing decisions)."""
        from cortex.orchestrators.intelligence_preserver import IntelligencePreserver
        
        # Create mock learned patterns
        state_dir = tmp_path / "cortex_brain" / "state"
        state_dir.mkdir(parents=True)
        
        patterns = {
            "rule_hits": {"CORE-008": 1247, "CORE-011": 982},
            "routing_decisions": {"BuilderOrchestrator": 0.84},
            "duration_baselines": {"p50": 1.2, "p95": 3.4, "p99": 8.1}
        }
        (state_dir / "learned_patterns.json").write_text(str(patterns))
        
        preserver = IntelligencePreserver(tmp_path)
        result = preserver.snapshot_learned_patterns("7.2.0")
        
        assert result["success"] is True


class TestIntelligencePreserverManifest:
    """Tests for snapshot manifest generation."""

    def test_generate_snapshot_manifest(self, tmp_path):
        """Should generate manifest with timestamp and file list."""
        from cortex.orchestrators.intelligence_preserver import IntelligencePreserver
        
        preserver = IntelligencePreserver(tmp_path)
        
        manifest = preserver.generate_snapshot_manifest(
            version="7.2.0",
            files=["governance.db", "tier1/finops-rules.yaml"]
        )
        
        assert manifest["version"] == "7.2.0"
        assert "timestamp" in manifest
        assert len(manifest["files"]) == 2

    def test_validate_snapshot_integrity(self, tmp_path):
        """Should validate snapshot integrity via hash verification."""
        from cortex.orchestrators.intelligence_preserver import IntelligencePreserver
        
        # Create snapshot with manifest
        snapshot_dir = tmp_path / ".cortex-snapshots" / "v7.2.0"
        snapshot_dir.mkdir(parents=True)
        
        test_file = snapshot_dir / "test.txt"
        test_file.write_text("test content")
        
        # Create manifest with hash
        file_hash = hashlib.sha256(test_file.read_bytes()).hexdigest()
        manifest = {"files": {"test.txt": file_hash}}
        (snapshot_dir / "manifest.json").write_text(str(manifest).replace("'", '"'))
        
        preserver = IntelligencePreserver(tmp_path)
        result = preserver.validate_snapshot_integrity("7.2.0")
        
        assert result["valid"] is True


class TestIntelligencePreserverRestore:
    """Tests for restoring from snapshots."""

    def test_restore_from_snapshot(self, tmp_path):
        """Should restore all files from a snapshot."""
        from cortex.orchestrators.intelligence_preserver import IntelligencePreserver
        
        # Create snapshot
        snapshot_dir = tmp_path / ".cortex-snapshots" / "v7.1.0"
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "governance.db").write_text("db content")
        
        tier1_snapshot = snapshot_dir / "tier1"
        tier1_snapshot.mkdir()
        (tier1_snapshot / "rules.yaml").write_text("rules: []")
        
        preserver = IntelligencePreserver(tmp_path)
        result = preserver.restore_from_snapshot("7.1.0")
        
        assert result["success"] is True
        assert result["files_restored"] >= 2

    def test_list_available_snapshots(self, tmp_path):
        """Should list all available snapshots."""
        from cortex.orchestrators.intelligence_preserver import IntelligencePreserver
        
        # Create multiple snapshots
        (tmp_path / ".cortex-snapshots" / "v7.0.0").mkdir(parents=True)
        (tmp_path / ".cortex-snapshots" / "v7.1.0").mkdir(parents=True)
        (tmp_path / ".cortex-snapshots" / "v7.2.0").mkdir(parents=True)
        
        preserver = IntelligencePreserver(tmp_path)
        snapshots = preserver.list_snapshots()
        
        assert len(snapshots) == 3
        assert "7.2.0" in snapshots
