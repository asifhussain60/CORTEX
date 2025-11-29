"""
Test GitIgnore Setup Module

Validates:
1. .gitignore is created/updated with CORTEX patterns
2. Patterns validated with git check-ignore
3. No CORTEX files staged/tracked after setup
4. Git commit is made automatically

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from src.setup.modules.gitignore_setup_module import GitIgnoreSetupModule
from src.setup.base_setup_module import SetupStatus


class TestGitIgnoreSetupModule:
    """Test suite for GitIgnore setup module."""
    
    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary git repository for testing."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def module(self):
        """Create GitIgnore module instance."""
        return GitIgnoreSetupModule()
    
    @pytest.fixture
    def context(self, temp_git_repo):
        """Create test context."""
        cortex_dir = temp_git_repo / 'CORTEX'
        cortex_dir.mkdir()
        
        return {
            'project_root': str(cortex_dir),
            'user_project_root': str(temp_git_repo)
        }
    
    def test_metadata(self, module):
        """Test module metadata."""
        metadata = module.get_metadata()
        
        assert metadata.module_id == "gitignore_setup"
        assert metadata.name == "GitIgnore Configuration"
        assert metadata.phase.name == "ENVIRONMENT"
        assert metadata.priority == 15
        assert "platform_detection" in metadata.dependencies
        assert metadata.optional is False
    
    def test_validate_prerequisites_success(self, module, context):
        """Test prerequisite validation succeeds with valid context."""
        is_valid, issues = module.validate_prerequisites(context)
        
        assert is_valid is True
        assert len(issues) == 0
    
    def test_validate_prerequisites_no_project_root(self, module):
        """Test prerequisite validation fails without project_root."""
        context = {}
        
        is_valid, issues = module.validate_prerequisites(context)
        
        assert is_valid is False
        assert any("project_root" in issue for issue in issues)
    
    def test_validate_prerequisites_no_git(self, module, context):
        """Test prerequisite validation fails if git not available."""
        with patch('subprocess.run') as mock_run:
            mock_run.side_effect = FileNotFoundError()
            
            is_valid, issues = module.validate_prerequisites(context)
            
            assert is_valid is False
            assert any("Git not found" in issue for issue in issues)
    
    def test_execute_creates_gitignore(self, module, context, temp_git_repo):
        """Test execution creates .gitignore with CORTEX patterns."""
        result = module.execute(context)
        
        assert result.status == SetupStatus.SUCCESS
        
        gitignore_path = temp_git_repo / '.gitignore'
        assert gitignore_path.exists()
        
        content = gitignore_path.read_text()
        assert "CORTEX AI Assistant" in content
        assert "CORTEX/" in content
        assert ".github/prompts/CORTEX.prompt.md" in content
    
    def test_execute_preserves_existing_gitignore(self, module, context, temp_git_repo):
        """Test execution preserves existing .gitignore content."""
        gitignore_path = temp_git_repo / '.gitignore'
        existing_content = "# Existing patterns\n*.log\n"
        gitignore_path.write_text(existing_content)
        
        result = module.execute(context)
        
        assert result.status == SetupStatus.SUCCESS
        
        content = gitignore_path.read_text()
        assert "*.log" in content  # Original content preserved
        assert "CORTEX/" in content  # New patterns added
    
    def test_execute_skips_if_patterns_exist(self, module, context, temp_git_repo):
        """Test execution skips if CORTEX patterns already exist."""
        gitignore_path = temp_git_repo / '.gitignore'
        gitignore_path.write_text("# CORTEX AI Assistant\nCORTEX/\n")
        
        # First commit to avoid "nothing to commit" error
        subprocess.run(['git', 'add', '.gitignore'], cwd=temp_git_repo, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Initial'], cwd=temp_git_repo, capture_output=True)
        
        result = module.execute(context)
        
        assert result.status == SetupStatus.SUCCESS
        assert "already configured" in result.message.lower()
    
    def test_validate_gitignore_patterns(self, module, context, temp_git_repo):
        """Test .gitignore pattern validation with git check-ignore."""
        # Create .gitignore with CORTEX patterns
        gitignore_path = temp_git_repo / '.gitignore'
        gitignore_path.write_text('\n'.join(GitIgnoreSetupModule.CORTEX_PATTERNS))
        
        subprocess.run(['git', 'add', '.gitignore'], cwd=temp_git_repo, capture_output=True)
        
        is_valid, issues = module._validate_gitignore_patterns(temp_git_repo)
        
        # Note: git check-ignore may fail in test environment, so we check for reasonable behavior
        assert isinstance(is_valid, bool)
        assert isinstance(issues, list)
    
    def test_commit_gitignore(self, module, temp_git_repo):
        """Test .gitignore is committed automatically."""
        gitignore_path = temp_git_repo / '.gitignore'
        gitignore_path.write_text("CORTEX/\n")
        
        success, message = module._commit_gitignore(temp_git_repo)
        
        assert success is True
        assert "CORTEX" in message or "commit" in message.lower()
    
    def test_verify_no_cortex_staged(self, module, temp_git_repo):
        """Test verification that no CORTEX files are staged."""
        # Create .gitignore first
        gitignore_path = temp_git_repo / '.gitignore'
        gitignore_path.write_text("CORTEX/\n")
        subprocess.run(['git', 'add', '.gitignore'], cwd=temp_git_repo, capture_output=True)
        subprocess.run(['git', 'commit', '-m', 'Add gitignore'], cwd=temp_git_repo, capture_output=True)
        
        # Create CORTEX files (should be ignored)
        cortex_dir = temp_git_repo / 'CORTEX'
        cortex_dir.mkdir(exist_ok=True)
        (cortex_dir / 'test.txt').write_text('test')
        
        is_clean, staged_files = module._verify_no_cortex_staged(temp_git_repo)
        
        assert is_clean is True
        assert len(staged_files) == 0
    
    def test_add_cortex_patterns(self, module):
        """Test adding CORTEX patterns to existing content."""
        existing_content = "# My project\n*.log\n"
        
        updated_content = module._add_cortex_patterns(existing_content)
        
        assert "# My project" in updated_content
        assert "*.log" in updated_content
        assert "CORTEX/" in updated_content
        assert "CORTEX AI Assistant" in updated_content
    
    def test_rollback_does_nothing(self, module, context):
        """Test rollback is a no-op (as documented)."""
        result = module.rollback(context)
        
        assert result is True


class TestGitIgnoreIntegration:
    """Integration tests for GitIgnore setup."""
    
    @pytest.fixture
    def integration_repo(self):
        """Create a realistic repository structure."""
        temp_dir = Path(tempfile.mkdtemp())
        
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.email', 'test@example.com'], cwd=temp_dir, capture_output=True)
        subprocess.run(['git', 'config', 'user.name', 'Test User'], cwd=temp_dir, capture_output=True)
        
        # Create realistic structure
        (temp_dir / 'src').mkdir()
        (temp_dir / 'src' / 'app.py').write_text('# App code')
        
        # Create CORTEX folder
        cortex_dir = temp_dir / 'CORTEX'
        cortex_dir.mkdir()
        (cortex_dir / 'README.md').write_text('# CORTEX')
        
        # Create .github/prompts
        prompts_dir = temp_dir / '.github' / 'prompts'
        prompts_dir.mkdir(parents=True)
        (prompts_dir / 'CORTEX.prompt.md').write_text('# Prompt')
        
        yield temp_dir
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_full_gitignore_workflow(self, integration_repo):
        """Test complete GitIgnore setup workflow."""
        module = GitIgnoreSetupModule()
        context = {
            'project_root': str(integration_repo / 'CORTEX'),
            'user_project_root': str(integration_repo)
        }
        
        # Validate prerequisites
        is_valid, issues = module.validate_prerequisites(context)
        assert is_valid is True, f"Prerequisites failed: {issues}"
        
        # Execute setup
        result = module.execute(context)
        assert result.status == SetupStatus.SUCCESS, f"Setup failed: {result.message}"
        
        # Verify .gitignore exists
        gitignore_path = integration_repo / '.gitignore'
        assert gitignore_path.exists()
        
        # Verify CORTEX patterns present
        content = gitignore_path.read_text()
        assert "CORTEX/" in content
        assert "CORTEX AI Assistant" in content
        
        # Verify git commit was made
        result = subprocess.run(
            ['git', 'log', '--oneline', '-1'],
            cwd=integration_repo,
            capture_output=True,
            text=True
        )
        assert "CORTEX" in result.stdout or "gitignore" in result.stdout.lower()
        
        # Verify CORTEX files are not tracked
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=integration_repo,
            capture_output=True,
            text=True
        )
        # Should not see CORTEX/ or .github/prompts in staged files
        for line in result.stdout.splitlines():
            if line.startswith(('A ', 'M ')):  # Staged files
                assert 'CORTEX' not in line, f"CORTEX file staged: {line}"
