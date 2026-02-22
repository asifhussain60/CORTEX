"""
Tests for Cleanup Auditor (WAVE-J)

AC_START: AC-WAVE-J-002
"""

import pytest
import yaml
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from click.testing import CliRunner
import tempfile
import shutil

from cortex.cli.cleanup_auditor import (
    CleanupAuditor,
    FileArtifact,
    AuditResult,
    cli,
)


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def temp_workspace():
    """Create temporary workspace with test structure."""
    workspace = Path(tempfile.mkdtemp())
    
    # Create directory structure
    (workspace / "cortex").mkdir()
    (workspace / "cortex.intelligence").mkdir()
    (workspace / "cortex-registry" / "_cortex-master" / "phases" / "active").mkdir(parents=True)
    (workspace / "cortex-registry" / "_cortex-master" / "phases" / "completed").mkdir(parents=True)
    
    # Create test files
    (workspace / "cortex" / "test_module.py").write_text("# Test module")
    (workspace / "cortex" / "old_module.py").write_text("# Old module")
    
    # Create completed phase spec
    phase_spec = {
        "enhancement_id": "ENH-001",
        "title": "Test Phase",
        "status": "complete",
        "deliverables": ["Component 1", "Component 2"],
    }
    (workspace / "cortex-registry" / "_cortex-master" / "phases" / "active" / "enh-001.yaml").write_text(
        yaml.dump(phase_spec)
    )
    
    yield workspace
    
    # Cleanup
    shutil.rmtree(workspace)


@pytest.fixture
def auditor(temp_workspace):
    """Create auditor instance with temp workspace."""
    return CleanupAuditor(temp_workspace)


# ============================================================================
# FILEARTIFACT TESTS
# ============================================================================

class TestFileArtifact:
    """Tests for FileArtifact dataclass."""
    
    def test_file_artifact_creation(self):
        """FileArtifact can be created with required fields."""
        artifact = FileArtifact(
            path=Path("test.py"),
            classification="essential",
            last_modified=datetime.now(),
            last_commit_date=datetime.now(),
            import_count=5,
            phase_id="ENH-001",
            size_bytes=1024,
            recommendation="Keep",
        )
        
        assert artifact.path == Path("test.py")
        assert artifact.classification == "essential"
        assert artifact.import_count == 5
        assert artifact.phase_id == "ENH-001"
    
    def test_file_artifact_to_dict(self):
        """FileArtifact converts to dictionary correctly."""
        artifact = FileArtifact(
            path=Path("test.py"),
            classification="orphaned",
            last_modified=datetime(2025, 1, 1, 12, 0, 0),
            last_commit_date=datetime(2024, 6, 1, 12, 0, 0),
            import_count=0,
            phase_id=None,
            size_bytes=2048,
            recommendation="Archive",
        )
        
        result = artifact.to_dict()
        
        assert result["path"] == "test.py"
        assert result["classification"] == "orphaned"
        assert result["import_count"] == 0
        assert result["size_kb"] == 2.0
        assert result["recommendation"] == "Archive"
    
    def test_file_artifact_none_values(self):
        """FileArtifact handles None values correctly."""
        artifact = FileArtifact(
            path=Path("test.py"),
            classification="stale",
            last_modified=datetime.now(),
            last_commit_date=None,
            import_count=1,
            phase_id=None,
            size_bytes=512,
            recommendation="Migrate",
        )
        
        result = artifact.to_dict()
        
        assert result["last_commit_date"] is None
        assert result["phase_id"] is None


# ============================================================================
# AUDITRESULT TESTS
# ============================================================================

class TestAuditResult:
    """Tests for AuditResult dataclass."""
    
    def test_audit_result_initialization(self):
        """AuditResult initializes with default values."""
        result = AuditResult()
        
        assert result.total_files_scanned == 0
        assert result.completed_phases_found == 0
        assert result.essential_files == []
        assert result.stale_files == []
        assert result.orphaned_files == []
        assert result.deprecated_files == []
        assert result.cleanup_savings_kb == 0
        assert result.phases_to_migrate == []
    
    def test_audit_result_summary(self):
        """AuditResult generates summary correctly."""
        result = AuditResult()
        result.total_files_scanned = 100
        result.completed_phases_found = 5
        result.essential_files = [Mock()] * 50
        result.stale_files = [Mock()] * 20
        result.orphaned_files = [Mock()] * 15
        result.deprecated_files = [Mock()] * 15
        result.cleanup_savings_kb = 5120
        result.phases_to_migrate = ["ENH-001", "ENH-002"]
        
        summary = result.summary()
        
        assert summary["total_scanned"] == 100
        assert summary["completed_phases"] == 5
        assert summary["classification"]["essential"] == 50
        assert summary["classification"]["stale"] == 20
        assert summary["classification"]["orphaned"] == 15
        assert summary["classification"]["deprecated"] == 15
        assert summary["cleanup_potential_mb"] == 5.0
        assert summary["phases_to_migrate"] == 2


# ============================================================================
# CLEANUPAUDITOR TESTS
# ============================================================================

class TestCleanupAuditor:
    """Tests for CleanupAuditor class."""
    
    def test_auditor_initialization(self, auditor, temp_workspace):
        """CleanupAuditor initializes with correct paths."""
        assert auditor.workspace_root == temp_workspace
        assert auditor.cortex_dir == temp_workspace / "cortex"
        assert auditor.cortex.intelligence_dir == temp_workspace / "cortex.intelligence"
        assert auditor.registry_dir == temp_workspace / "cortex-registry" / "_cortex-master"
    
    def test_audit_completed_phases(self, auditor):
        """audit_completed_phases discovers completed phases."""
        completed = auditor.audit_completed_phases()
        
        assert len(completed) == 1
        assert "ENH-001" in completed
    
    def test_audit_completed_phases_empty(self, temp_workspace):
        """audit_completed_phases handles empty directory."""
        # Remove the phase file
        (temp_workspace / "cortex-registry" / "_cortex-master" / "phases" / "active" / "enh-001.yaml").unlink()
        
        auditor = CleanupAuditor(temp_workspace)
        completed = auditor.audit_completed_phases()
        
        assert completed == []
    
    def test_audit_completed_phases_invalid_yaml(self, temp_workspace):
        """audit_completed_phases skips invalid YAML files."""
        # Create invalid YAML
        (temp_workspace / "cortex-registry" / "_cortex-master" / "phases" / "active" / "invalid.yaml").write_text(
            "{ invalid yaml content [["
        )
        
        auditor = CleanupAuditor(temp_workspace)
        completed = auditor.audit_completed_phases()
        
        # Should still find ENH-001, skip invalid
        assert "ENH-001" in completed
    
    @patch("cortex.cli.cleanup_auditor.subprocess.run")
    def test_get_file_last_commit_success(self, mock_run, auditor, temp_workspace):
        """get_file_last_commit returns datetime from git."""
        # Mock git log output (Unix timestamp)
        mock_run.return_value = Mock(returncode=0, stdout="1609459200\n")  # 2021-01-01 UTC
        
        test_file = temp_workspace / "cortex" / "test_module.py"
        result = auditor.get_file_last_commit(test_file)
        
        assert result is not None
        # Check it's around that date (account for timezone differences)
        assert result.year in [2020, 2021]
        assert result.month in [12, 1]
    
    @patch("cortex.cli.cleanup_auditor.subprocess.run")
    def test_get_file_last_commit_failure(self, mock_run, auditor, temp_workspace):
        """get_file_last_commit returns None on failure."""
        mock_run.return_value = Mock(returncode=1, stdout="")
        
        test_file = temp_workspace / "cortex" / "test_module.py"
        result = auditor.get_file_last_commit(test_file)
        
        assert result is None
    
    @patch("cortex.cli.cleanup_auditor.subprocess.run")
    def test_get_file_last_commit_timeout(self, mock_run, auditor, temp_workspace):
        """get_file_last_commit handles timeout gracefully."""
        mock_run.side_effect = subprocess.TimeoutExpired("git", 5)
        
        test_file = temp_workspace / "cortex" / "test_module.py"
        result = auditor.get_file_last_commit(test_file)
        
        assert result is None
    
    def test_classify_file_essential(self, auditor, temp_workspace):
        """classify_file identifies essential files."""
        # Mock import count as high
        test_file = temp_workspace / "cortex" / "test_module.py"
        auditor._inbound_references["cortex.test_module"] = 10
        
        artifact = auditor.classify_file(test_file, ["ENH-001"])
        
        assert artifact.classification == "essential"
        assert artifact.recommendation == "Keep - core infrastructure"
    
    def test_classify_file_orphaned(self, auditor, temp_workspace):
        """classify_file identifies orphaned files."""
        # Create old file
        test_file = temp_workspace / "cortex" / "old_module.py"
        old_time = (datetime.now() - timedelta(days=200)).timestamp()
        Path(test_file).touch()
        import os
        os.utime(test_file, (old_time, old_time))
        
        # Mock 0 import count
        auditor._inbound_references["cortex.old_module"] = 0
        
        artifact = auditor.classify_file(test_file, [])
        
        assert artifact.classification == "orphaned"
        assert "Archive" in artifact.recommendation
    
    def test_classify_file_stale(self, auditor, temp_workspace):
        """classify_file identifies stale files from completed phases."""
        # Create file with phase ID in name
        test_file = temp_workspace / "cortex" / "enh-001-component.py"
        test_file.write_text("# Component from ENH-001")
        
        artifact = auditor.classify_file(test_file, ["ENH-001"])
        
        assert artifact.classification == "stale"
        assert artifact.phase_id == "ENH-001"
        assert "Migrate" in artifact.recommendation


# ============================================================================
# CLI TESTS
# ============================================================================

class TestCLI:
    """Tests for CLI commands."""
    
    def test_cli_audit_command(self, temp_workspace):
        """CLI audit command executes successfully."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ["audit", "--workspace", str(temp_workspace), "--format", "text"])
        
        assert result.exit_code == 0
        assert "WAVE-J CLEANUP AUDIT REPORT" in result.output
        assert "Completed Phases:" in result.output
    
    def test_cli_audit_yaml_output(self, temp_workspace):
        """CLI audit command generates YAML report."""
        runner = CliRunner()
        
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            output_file = f.name
        
        try:
            result = runner.invoke(
                cli,
                ["audit", "--workspace", str(temp_workspace), "--format", "yaml", "--output", output_file]
            )
            
            assert result.exit_code == 0
            assert Path(output_file).exists()
            
            # Verify YAML content
            with open(output_file) as f:
                report = yaml.safe_load(f)
            
            assert "audit_date" in report
            assert "summary" in report
            assert "phases_to_migrate" in report
        finally:
            Path(output_file).unlink(missing_ok=True)
    
    def test_cli_migrate_dry_run(self, temp_workspace):
        """CLI migrate command shows dry-run output."""
        runner = CliRunner()
        
        result = runner.invoke(cli, ["migrate", "--workspace", str(temp_workspace), "--dry-run"])
        
        assert result.exit_code == 0
        assert "Would migrate" in result.output
    
    def test_cli_migrate_execution(self, temp_workspace):
        """CLI migrate command moves files to completed/."""
        runner = CliRunner()
        
        # Verify file exists in active/
        active_file = temp_workspace / "cortex-registry" / "_cortex-master" / "phases" / "active" / "enh-001.yaml"
        assert active_file.exists()
        
        result = runner.invoke(cli, ["migrate", "--workspace", str(temp_workspace)])
        
        assert result.exit_code == 0
        assert "Migrated" in result.output
        
        # Verify file moved to completed/
        completed_file = temp_workspace / "cortex-registry" / "_cortex-master" / "phases" / "completed" / "enh-001.yaml"
        assert completed_file.exists()
        assert not active_file.exists()
    
    def test_cli_migrate_no_phases(self, temp_workspace):
        """CLI migrate handles no phases gracefully."""
        # Remove completed phase
        (temp_workspace / "cortex-registry" / "_cortex-master" / "phases" / "active" / "enh-001.yaml").unlink()
        
        # Create active phase that's not completed
        active_spec = {
            "enhancement_id": "ENH-002",
            "status": "in_progress",
            "deliverables": ["Component"],
        }
        (temp_workspace / "cortex-registry" / "_cortex-master" / "phases" / "active" / "enh-002.yaml").write_text(
            yaml.dump(active_spec)
        )
        
        runner = CliRunner()
        result = runner.invoke(cli, ["migrate", "--workspace", str(temp_workspace)])
        
        assert result.exit_code == 0
        assert "No phases to migrate" in result.output


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestCleanupAuditorIntegration:
    """End-to-end integration tests."""
    
    def test_full_audit_workflow(self, temp_workspace):
        """Complete audit workflow from scan to report."""
        # Create additional test files
        (temp_workspace / "cortex" / "core_module.py").write_text("# Core module")
        (temp_workspace / "cortex" / "deprecated_module.py").write_text("# Deprecated")
        
        # Set old modification time for deprecated module
        deprecated_file = temp_workspace / "cortex" / "deprecated_module.py"
        old_time = (datetime.now() - timedelta(days=200)).timestamp()
        import os
        os.utime(deprecated_file, (old_time, old_time))
        
        # Create auditor and run audit
        auditor = CleanupAuditor(temp_workspace)
        auditor._inbound_references["cortex.core_module"] = 5  # Essential
        auditor._inbound_references["cortex.deprecated_module"] = 0  # Orphaned
        
        result = auditor.audit_workspace()
        
        # Verify results
        assert result.total_files_scanned >= 3
        assert result.completed_phases_found == 1
        assert len(result.essential_files) > 0
        
        # Generate report
        report = auditor.generate_report(result, output_format="text")
        
        assert "WAVE-J CLEANUP AUDIT REPORT" in report
        assert "Summary" in report
        assert "Next Actions" in report


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

# AC_COMPLETE: AC-WAVE-J-002 ✅
