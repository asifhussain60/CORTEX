"""
Unit tests for GovernanceAuditor.

Tests comprehensive governance audit including CORE-051, CORE-052,
CORE-002, and registry validation.

AC_START: AC-WAVE-4-AUDIT-001
Description: Tests for governance audit functionality
"""

import tempfile
from datetime import datetime
from pathlib import Path
import subprocess

import pytest
import yaml

from cortex.governance.governance_auditor import GovernanceAuditor


class TestGovernanceAuditor:
    """Tests for GovernanceAuditor."""
    
    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create temporary git repository."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Initialize git
        subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "config", "user.email", "test@cortex.local"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "config", "user.name", "Test User"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        
        # Create cortex-registry
        registry_path = repo_path / "cortex-registry"
        master_dir = registry_path / "_cortex-master"
        phases_dir = master_dir / "phases" / "active"
        phases_dir.mkdir(parents=True)
        
        # Create sample phase
        phase_file = phases_dir / "phase-test.yaml"
        phase_data = {
            "id": "phase-test",
            "status": "ACTIVE",
            "updated_at": datetime.now().isoformat()
        }
        with open(phase_file, "w") as f:
            yaml.dump(phase_data, f)
            
        # Initial commit
        subprocess.run(["git", "add", "."], cwd=repo_path, check=True, capture_output=True)
        subprocess.run(
            ["git", "commit", "-m", "Initial commit"],
            cwd=repo_path,
            check=True,
            capture_output=True
        )
        
        return repo_path
        
    def test_init_default_paths(self):
        """Test initialization with default paths."""
        auditor = GovernanceAuditor()
        assert auditor.repo_path == Path.cwd()
        assert auditor.registry_path == Path.cwd() / "cortex-registry"
        
    def test_init_custom_paths(self, temp_repo):
        """Test initialization with custom paths."""
        registry_path = temp_repo / "cortex-registry"
        auditor = GovernanceAuditor(repo_path=temp_repo, registry_path=registry_path)
        
        assert auditor.repo_path == temp_repo
        assert auditor.registry_path == registry_path
        
    def test_check_settings_json_not_tracked_pass(self, temp_repo):
        """Test settings.json check when not tracked."""
        auditor = GovernanceAuditor(repo_path=temp_repo)
        
        result = auditor._check_settings_json_not_tracked()
        
        assert result["passed"] is True
        assert "not tracked" in result["details"]
        
    def test_check_settings_json_not_tracked_fail(self, temp_repo):
        """Test settings.json check when tracked."""
        # Create and track settings.json
        vscode_dir = temp_repo / ".vscode"
        vscode_dir.mkdir()
        settings_file = vscode_dir / "settings.json"
        settings_file.write_text("{}")
        
        subprocess.run(
            ["git", "add", ".vscode/settings.json"],
            cwd=temp_repo,
            check=True,
            capture_output=True
        )
        subprocess.run(
            ["git", "commit", "-m", "Add settings"],
            cwd=temp_repo,
            check=True,
            capture_output=True
        )
        
        auditor = GovernanceAuditor(repo_path=temp_repo)
        result = auditor._check_settings_json_not_tracked()
        
        assert result["passed"] is False
        assert "VIOLATION" in result["details"]
        
    def test_check_single_branch_policy_pass(self, temp_repo):
        """Test single branch policy check when compliant."""
        # Rename master to CORTEX
        subprocess.run(
            ["git", "branch", "-m", "CORTEX"],
            cwd=temp_repo,
            check=True,
            capture_output=True
        )
        
        auditor = GovernanceAuditor(repo_path=temp_repo)
        result = auditor._check_single_branch_policy()
        
        assert result["passed"] is True
        
    def test_check_markdown_sprawl_pass(self, temp_repo):
        """Test markdown sprawl check when under limit."""
        auditor = GovernanceAuditor(repo_path=temp_repo)
        
        result = auditor._check_markdown_sprawl()
        
        assert result["passed"] is True
        
    def test_check_markdown_sprawl_fail(self, temp_repo):
        """Test markdown sprawl check when over limit."""
        # Create 26+ markdown files
        master_dir = temp_repo / "cortex-registry" / "_cortex-master"
        for i in range(30):
            md_file = master_dir / f"doc-{i}.md"
            md_file.write_text(f"# Doc {i}")
            
        auditor = GovernanceAuditor(repo_path=temp_repo)
        result = auditor._check_markdown_sprawl()
        
        assert result["passed"] is False
        assert "30 markdown files" in result["details"]
        
    def test_check_git_hygiene_pass(self, temp_repo):
        """Test git hygiene check with clean working directory."""
        auditor = GovernanceAuditor(repo_path=temp_repo)
        
        result = auditor._check_git_hygiene()
        
        assert result["passed"] is True
        assert "0 uncommitted files" in result["details"]
        
    def test_check_git_hygiene_fail(self, temp_repo):
        """Test git hygiene check with dirty working directory."""
        # Create multiple uncommitted files
        for i in range(5):
            file = temp_repo / f"test-{i}.txt"
            file.write_text("test")
            
        auditor = GovernanceAuditor(repo_path=temp_repo)
        result = auditor._check_git_hygiene()
        
        assert result["passed"] is False
        assert "5 uncommitted files" in result["details"]
        
    def test_run_comprehensive_audit(self, temp_repo):
        """Test full comprehensive audit."""
        # Rename branch to CORTEX for compliance
        subprocess.run(
            ["git", "branch", "-m", "CORTEX"],
            cwd=temp_repo,
            check=True,
            capture_output=True
        )
        
        auditor = GovernanceAuditor(repo_path=temp_repo)
        results = auditor.run_comprehensive_audit()
        
        assert "compliant" in results
        assert "p0_violations" in results
        assert "p1_warnings" in results
        assert "p2_notices" in results
        assert results["checks_performed"] == 5
        assert "timestamp" in results
        
    def test_generate_compliance_report(self, temp_repo):
        """Test compliance report generation."""
        subprocess.run(
            ["git", "branch", "-m", "CORTEX"],
            cwd=temp_repo,
            check=True,
            capture_output=True
        )
        
        auditor = GovernanceAuditor(repo_path=temp_repo)
        results = auditor.run_comprehensive_audit()
        
        report_yaml = auditor.generate_compliance_report(results)
        
        assert report_yaml is not None
        assert "governance_compliance_report" in report_yaml
        
        # Verify YAML is valid
        report_data = yaml.safe_load(report_yaml)
        assert "governance_compliance_report" in report_data
        assert "compliant" in report_data["governance_compliance_report"]
