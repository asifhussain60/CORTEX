"""
Tests for Git Isolation Enforcement
Validates that CORTEX code cannot be committed to user application repositories.
"""

import pytest
from pathlib import Path
import subprocess
import shutil
from src.tier0.git_isolation import (
    GitIsolationEnforcer,
    install_git_isolation_hooks,
    check_git_isolation,
    CORTEX_PROTECTED_PATHS
)


@pytest.fixture
def temp_user_repo(tmp_path):
    """Create a temporary git repository (simulates user's app repo)."""
    repo_path = tmp_path / "user_app"
    repo_path.mkdir()
    
    # Initialize git
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
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
    
    yield repo_path
    
    # Cleanup
    shutil.rmtree(repo_path, ignore_errors=True)


@pytest.fixture
def enforcer(temp_user_repo):
    """Create GitIsolationEnforcer instance."""
    return GitIsolationEnforcer(temp_user_repo)


class TestGitIsolationEnforcer:
    """Test GitIsolationEnforcer class."""
    
    def test_initializes_with_user_repo_path(self, temp_user_repo):
        """Should initialize with path to user repository."""
        enforcer = GitIsolationEnforcer(temp_user_repo)
        
        assert enforcer.user_repo_path == temp_user_repo
        assert enforcer.git_dir == temp_user_repo / ".git"
        assert enforcer.hooks_dir == temp_user_repo / ".git" / "hooks"
    
    def test_detects_git_repository(self, temp_user_repo):
        """Should detect if directory is a git repository."""
        enforcer = GitIsolationEnforcer(temp_user_repo)
        
        assert enforcer.git_dir.exists()
    
    def test_fails_if_not_git_repo(self, tmp_path):
        """Should fail gracefully if not a git repository."""
        non_git_path = tmp_path / "not_a_repo"
        non_git_path.mkdir()
        
        enforcer = GitIsolationEnforcer(non_git_path)
        result = enforcer.install_hooks()
        
        assert result is False


class TestHookInstallation:
    """Test git hook installation."""
    
    def test_installs_pre_commit_hook(self, enforcer):
        """Should install pre-commit hook."""
        result = enforcer.install_hooks()
        
        assert result is True
        
        hook_path = enforcer.hooks_dir / "pre-commit"
        assert hook_path.exists()
        
        # Verify hook content
        content = hook_path.read_text()
        assert "CORTEX Git Isolation" in content
        assert "Pre-Commit Hook" in content
    
    def test_installs_pre_push_hook(self, enforcer):
        """Should install pre-push hook."""
        result = enforcer.install_hooks()
        
        assert result is True
        
        hook_path = enforcer.hooks_dir / "pre-push"
        assert hook_path.exists()
        
        # Verify hook content
        content = hook_path.read_text()
        assert "CORTEX Git Isolation" in content
        assert "Pre-Push Hook" in content
    
    def test_creates_hooks_directory_if_missing(self, temp_user_repo):
        """Should create hooks directory if it doesn't exist."""
        hooks_dir = temp_user_repo / ".git" / "hooks"
        if hooks_dir.exists():
            shutil.rmtree(hooks_dir)
        
        enforcer = GitIsolationEnforcer(temp_user_repo)
        enforcer.install_hooks()
        
        assert hooks_dir.exists()
    
    def test_does_not_overwrite_existing_hooks_with_cortex_marker(self, enforcer):
        """Should not overwrite hooks that already have CORTEX marker."""
        # Install once
        enforcer.install_hooks()
        
        hook_path = enforcer.hooks_dir / "pre-commit"
        original_content = hook_path.read_text()
        
        # Install again
        enforcer.install_hooks()
        
        # Should be identical (not appended)
        assert hook_path.read_text() == original_content


class TestProtectedPathDetection:
    """Test detection of CORTEX protected paths."""
    
    def test_detects_tier0_path(self, enforcer):
        """Should detect src/tier0/ as protected."""
        assert enforcer._is_cortex_path("src/tier0/brain_protector.py")
    
    def test_detects_tier1_path(self, enforcer):
        """Should detect src/tier1/ as protected."""
        assert enforcer._is_cortex_path("src/tier1/conversation_tracker.py")
    
    def test_detects_tier2_path(self, enforcer):
        """Should detect src/tier2/ as protected."""
        assert enforcer._is_cortex_path("src/tier2/knowledge_graph.py")
    
    def test_detects_cortex_agents_path(self, enforcer):
        """Should detect src/cortex_agents/ as protected."""
        assert enforcer._is_cortex_path("src/cortex_agents/executor.py")
    
    def test_detects_cortex_brain_path(self, enforcer):
        """Should detect cortex-brain/ as protected."""
        assert enforcer._is_cortex_path("cortex-brain/knowledge-graph.yaml")
    
    def test_detects_prompts_path(self, enforcer):
        """Should detect prompts/ as protected."""
        assert enforcer._is_cortex_path("prompts/user/cortex.md")
    
    def test_allows_application_code(self, enforcer):
        """Should NOT flag user's application code."""
        assert not enforcer._is_cortex_path("src/my_app/main.py")
        assert not enforcer._is_cortex_path("tests/test_my_feature.py")
        assert not enforcer._is_cortex_path("README.md")
    
    def test_allows_team_knowledge_directory(self, enforcer):
        """Should allow team-knowledge/ (exported YAML patterns)."""
        # Note: _is_cortex_path returns True, but check_staged_files has exception
        assert not enforcer._is_cortex_path("team-knowledge/parking-patterns.yaml")


class TestStagedFileChecking:
    """Test checking staged files for violations."""
    
    def test_allows_clean_commit(self, temp_user_repo, enforcer):
        """Should allow commit with no CORTEX files."""
        # Stage user application file
        app_file = temp_user_repo / "src" / "app.py"
        app_file.parent.mkdir(parents=True)
        app_file.write_text("print('Hello')")
        
        subprocess.run(["git", "add", "src/app.py"], cwd=temp_user_repo, check=True)
        
        is_safe, violations = enforcer.check_staged_files()
        
        assert is_safe is True
        assert len(violations) == 0
    
    def test_blocks_cortex_tier0_file(self, temp_user_repo, enforcer):
        """Should block commit containing CORTEX tier0 file."""
        # Stage CORTEX file
        cortex_file = temp_user_repo / "src" / "tier0" / "brain_protector.py"
        cortex_file.parent.mkdir(parents=True)
        cortex_file.write_text("# CORTEX code")
        
        subprocess.run(
            ["git", "add", "src/tier0/brain_protector.py"],
            cwd=temp_user_repo,
            check=True
        )
        
        is_safe, violations = enforcer.check_staged_files()
        
        assert is_safe is False
        assert len(violations) == 1
        assert "src/tier0/brain_protector.py" in violations[0]
    
    def test_blocks_cortex_brain_directory(self, temp_user_repo, enforcer):
        """Should block commit containing cortex-brain/ files."""
        # Stage brain file
        brain_file = temp_user_repo / "cortex-brain" / "knowledge-graph.yaml"
        brain_file.parent.mkdir(parents=True)
        brain_file.write_text("patterns: []")
        
        subprocess.run(
            ["git", "add", "cortex-brain/knowledge-graph.yaml"],
            cwd=temp_user_repo,
            check=True
        )
        
        is_safe, violations = enforcer.check_staged_files()
        
        assert is_safe is False
        assert "cortex-brain/knowledge-graph.yaml" in violations[0]
    
    def test_allows_team_knowledge_yaml(self, temp_user_repo, enforcer):
        """Should allow team-knowledge/ YAML files (exported patterns)."""
        # Stage team knowledge file
        knowledge_file = temp_user_repo / "team-knowledge" / "parking-patterns.yaml"
        knowledge_file.parent.mkdir(parents=True)
        knowledge_file.write_text("patterns: []")
        
        subprocess.run(
            ["git", "add", "team-knowledge/parking-patterns.yaml"],
            cwd=temp_user_repo,
            check=True
        )
        
        is_safe, violations = enforcer.check_staged_files()
        
        assert is_safe is True
        assert len(violations) == 0


class TestHookUninstallation:
    """Test removal of git hooks."""
    
    def test_uninstalls_hooks(self, enforcer):
        """Should remove CORTEX git hooks."""
        # Install hooks
        enforcer.install_hooks()
        
        assert (enforcer.hooks_dir / "pre-commit").exists()
        assert (enforcer.hooks_dir / "pre-push").exists()
        
        # Uninstall
        result = enforcer.uninstall_hooks()
        
        assert result is True
        assert not (enforcer.hooks_dir / "pre-commit").exists()
        assert not (enforcer.hooks_dir / "pre-push").exists()
    
    def test_only_removes_cortex_hooks(self, enforcer):
        """Should not remove non-CORTEX hooks."""
        # Create non-CORTEX hook
        other_hook = enforcer.hooks_dir / "pre-commit"
        enforcer.hooks_dir.mkdir(parents=True, exist_ok=True)
        other_hook.write_text("#!/bin/sh\n# Some other hook\necho 'test'\n")
        
        # Try to uninstall
        result = enforcer.uninstall_hooks()
        
        # Should not remove (no CORTEX marker)
        assert result is False
        assert other_hook.exists()


class TestPublicAPI:
    """Test public API functions."""
    
    def test_install_git_isolation_hooks_function(self, temp_user_repo):
        """Should install hooks via public API."""
        result = install_git_isolation_hooks(temp_user_repo)
        
        assert result is True
        assert (temp_user_repo / ".git" / "hooks" / "pre-commit").exists()
    
    def test_check_git_isolation_function(self, temp_user_repo):
        """Should check isolation via public API."""
        # Stage safe file
        app_file = temp_user_repo / "app.py"
        app_file.write_text("print('Hello')")
        subprocess.run(["git", "add", "app.py"], cwd=temp_user_repo, check=True)
        
        is_safe, violations = check_git_isolation(temp_user_repo)
        
        assert is_safe is True
        assert len(violations) == 0


class TestProtectedPathsConstant:
    """Test CORTEX_PROTECTED_PATHS constant."""
    
    def test_includes_all_tier_directories(self):
        """Should include all CORTEX tier directories."""
        assert "src/tier0/" in CORTEX_PROTECTED_PATHS
        assert "src/tier1/" in CORTEX_PROTECTED_PATHS
        assert "src/tier2/" in CORTEX_PROTECTED_PATHS
        assert "src/tier3/" in CORTEX_PROTECTED_PATHS
    
    def test_includes_cortex_agents(self):
        """Should include cortex_agents directory."""
        assert "src/cortex_agents/" in CORTEX_PROTECTED_PATHS
    
    def test_includes_cortex_brain(self):
        """Should include cortex-brain directory."""
        assert "cortex-brain/" in CORTEX_PROTECTED_PATHS
    
    def test_includes_prompts(self):
        """Should include prompts directory."""
        assert "prompts/" in CORTEX_PROTECTED_PATHS


class TestBrainProtectionRuleIntegration:
    """Test integration with brain protection rules."""
    
    def test_git_isolation_enforcement_in_tier0_instincts(self):
        """Should have GIT_ISOLATION_ENFORCEMENT in tier0_instincts."""
        from pathlib import Path
        import yaml
        
        rules_path = Path("cortex-brain/brain-protection-rules.yaml")
        if rules_path.exists():
            rules = yaml.safe_load(rules_path.read_text())
            
            assert "GIT_ISOLATION_ENFORCEMENT" in rules["tier0_instincts"]
    
    def test_git_isolation_layer_exists(self):
        """Should have Layer 8: Git Isolation in protection layers."""
        from pathlib import Path
        import yaml
        
        rules_path = Path("cortex-brain/brain-protection-rules.yaml")
        if rules_path.exists():
            rules = yaml.safe_load(rules_path.read_text())
            
            # Find git_isolation layer
            layers = rules.get("protection_layers", [])
            git_layer = next(
                (l for l in layers if l["layer_id"] == "git_isolation"),
                None
            )
            
            assert git_layer is not None
            assert git_layer["name"] == "Git Isolation Enforcement"
            assert git_layer["priority"] == 8


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
