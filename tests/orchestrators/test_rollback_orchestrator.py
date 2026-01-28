"""
Tests for RollbackOrchestrator - safe rollback to previous versions.

TDD Tests for rollback on upgrade failure.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestRollbackOrchestratorDetection:
    """Tests for detecting rollback conditions."""

    def test_detect_upgrade_failure(self, tmp_path):
        """Should detect when upgrade has failed."""
        from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
        
        orchestrator = RollbackOrchestrator(tmp_path)
        
        # Simulate failure conditions
        failure_indicators = {
            "tests_failed": 5,
            "validation_errors": ["CORE-008 not enforced"]
        }
        
        result = orchestrator.detect_upgrade_failure(failure_indicators)
        
        assert result["should_rollback"] is True
        assert any("tests_failed" in reason for reason in result["reasons"])

    def test_no_rollback_on_success(self, tmp_path):
        """Should not trigger rollback on successful upgrade."""
        from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
        
        orchestrator = RollbackOrchestrator(tmp_path)
        
        success_indicators = {
            "tests_failed": 0,
            "validation_errors": []
        }
        
        result = orchestrator.detect_upgrade_failure(success_indicators)
        
        assert result["should_rollback"] is False


class TestRollbackOrchestratorExecution:
    """Tests for executing rollback."""

    def test_rollback_on_failure(self, tmp_path):
        """Should rollback to previous version on failure."""
        from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
        
        # Create snapshot
        snapshot_dir = tmp_path / ".cortex-snapshots" / "v7.2.0"
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "governance.db").write_text("backup db")
        
        orchestrator = RollbackOrchestrator(tmp_path)
        result = orchestrator.rollback_to_version("7.2.0")
        
        assert result["success"] is True
        assert result["restored_version"] == "7.2.0"

    def test_rollback_restores_all_components(self, tmp_path):
        """Should restore all components during rollback."""
        from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
        
        # Create comprehensive snapshot
        snapshot_dir = tmp_path / ".cortex-snapshots" / "v7.2.0"
        snapshot_dir.mkdir(parents=True)
        (snapshot_dir / "governance.db").write_text("db")
        
        tier1_snap = snapshot_dir / "tier1"
        tier1_snap.mkdir()
        (tier1_snap / "rules.yaml").write_text("rules: []")
        
        (snapshot_dir / "learned_patterns.json").write_text("{}")
        
        orchestrator = RollbackOrchestrator(tmp_path)
        result = orchestrator.rollback_to_version("7.2.0")
        
        assert "governance.db" in result["restored_files"]
        assert "tier1" in str(result["restored_files"])


class TestRollbackOrchestratorSafety:
    """Tests for rollback safety measures."""

    def test_create_rollback_checkpoint(self, tmp_path):
        """Should create checkpoint before rollback."""
        from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
        
        orchestrator = RollbackOrchestrator(tmp_path)
        
        result = orchestrator.create_rollback_checkpoint("7.3.0")
        
        assert result["success"] is True
        assert "checkpoint_id" in result

    def test_verify_rollback_integrity(self, tmp_path):
        """Should verify integrity after rollback."""
        from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
        
        # Create mock restored files
        state_dir = tmp_path / "cortex_brain" / "state"
        state_dir.mkdir(parents=True)
        (state_dir / "governance.db").write_text("restored")
        
        orchestrator = RollbackOrchestrator(tmp_path)
        result = orchestrator.verify_rollback_integrity()
        
        assert result["valid"] is True

    def test_generate_rollback_report(self, tmp_path):
        """Should generate rollback report."""
        from cortex.orchestrators.support.rollback_orchestrator import RollbackOrchestrator
        
        orchestrator = RollbackOrchestrator(tmp_path)
        
        report = orchestrator.generate_rollback_report(
            from_version="7.3.0",
            to_version="7.2.0",
            reason="Validation tests failed"
        )
        
        assert report["from"] == "7.3.0"
        assert report["to"] == "7.2.0"
        assert "reason" in report
        assert "timestamp" in report
