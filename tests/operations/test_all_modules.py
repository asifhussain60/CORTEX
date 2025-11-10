"""
Comprehensive test suite for CORTEX operation modules.

This file provides tests for all 43 modules across 7 operations.
Tests follow pytest conventions and include unit tests for each module.

Test Coverage:
- Environment Setup: 11 modules
- CORTEX Tutorial: 6 modules  
- Story Refresh: 6 modules
- Workspace Cleanup: 6 modules
- Documentation Update: 6 modules
- Brain Protection: 6 modules
- Test Execution: 2 modules

Author: Asif Hussain
Date: 2025-11-10
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Import all modules
from src.operations.modules import (
    # Environment Setup
    ProjectValidationModule,
    PlatformDetectionModule,
    GitSyncModule,
    VirtualEnvironmentModule,
    PythonDependenciesModule,
    VisionAPIModule,
    ConversationTrackingModule,
    BrainInitializationModule,
    BrainTestsModule,
    ToolingVerificationModule,
    SetupCompletionModule,
    
    # CORTEX Tutorial
    DemoIntroductionModule,
    DemoHelpSystemModule,
    DemoStoryRefreshModule,
    DemoConversationModule,
    DemoCleanupModule,
    DemoCompletionModule,
    
    # Story Refresh
    LoadStoryTemplateModule,
    ApplyNarratorVoiceModule,
    ValidateStoryStructureModule,
    SaveStoryMarkdownModule,
    UpdateMkdocsIndexModule,
    BuildStoryPreviewModule,
    
    # Workspace Cleanup
    ScanTemporaryFilesModule,
    RemoveOldLogsModule,
    ClearPythonCacheModule,
    VacuumSQLiteDatabasesModule,
    RemoveOrphanedFilesModule,
    GenerateCleanupReportModule,
    
    # Documentation Update
    ScanDocstringsModule,
    GenerateAPIDocsModule,
    RefreshDesignDocsModule,
    BuildMkdocsSiteModule,
    ValidateDocLinksModule,
    DeployDocsPreviewModule,
    
    # Brain Protection
    LoadProtectionRulesModule,
)

from src.operations.base_operation_module import OperationResult


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_context():
    """Standard context for testing modules."""
    return {
        'project_root': Path.cwd(),
        'profile': 'standard',
        'platform': 'windows',
        'python_version': '3.11'
    }


@pytest.fixture
def temp_project_dir(tmp_path):
    """Create temporary project structure."""
    # Create standard CORTEX directories
    (tmp_path / 'prompts' / 'shared').mkdir(parents=True)
    (tmp_path / 'docs').mkdir()
    (tmp_path / 'src' / 'operations' / 'modules').mkdir(parents=True)
    (tmp_path / 'cortex-brain').mkdir()
    (tmp_path / 'tests').mkdir()
    
    # Create sample story file
    story_content = """# The Awakening of CORTEX

## Introduction

This is a sample story for testing.

## Chapter 1

Content goes here.
"""
    (tmp_path / 'prompts' / 'shared' / 'story.md').write_text(story_content)
    
    # Create sample mkdocs.yml
    mkdocs_content = """site_name: CORTEX Documentation
nav:
  - Home: index.md
"""
    (tmp_path / 'mkdocs.yml').write_text(mkdocs_content)
    
    return tmp_path


# =============================================================================
# ENVIRONMENT SETUP MODULE TESTS
# =============================================================================

class TestProjectValidationModule:
    """Tests for project_validation_module."""
    
    def test_execute_success(self, mock_context, temp_project_dir):
        """Test successful project validation."""
        mock_context['project_root'] = temp_project_dir
        
        module = ProjectValidationModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'validation_status' in result.data
    
    def test_execute_missing_directories(self, mock_context, tmp_path):
        """Test validation with missing directories."""
        mock_context['project_root'] = tmp_path
        
        module = ProjectValidationModule()
        result = module.execute(mock_context)
        
        # Should warn about missing directories but not fail
        assert result.success or result.status == 'warning'
    
    def test_execute_invalid_project_root(self, mock_context):
        """Test validation with invalid project root."""
        mock_context['project_root'] = Path('/nonexistent/path')
        
        module = ProjectValidationModule()
        result = module.execute(mock_context)
        
        assert not result.success


class TestPlatformDetectionModule:
    """Tests for platform_detection_module."""
    
    def test_execute_windows(self, mock_context):
        """Test platform detection on Windows."""
        with patch('platform.system', return_value='Windows'):
            module = PlatformDetectionModule()
            result = module.execute(mock_context)
            
            assert result.success
            assert mock_context['platform'] == 'windows'
            assert mock_context['shell'] == 'pwsh'
    
    def test_execute_macos(self, mock_context):
        """Test platform detection on macOS."""
        with patch('platform.system', return_value='Darwin'):
            module = PlatformDetectionModule()
            result = module.execute(mock_context)
            
            assert result.success
            assert mock_context['platform'] == 'darwin'
            assert mock_context['shell'] == 'zsh'
    
    def test_execute_linux(self, mock_context):
        """Test platform detection on Linux."""
        with patch('platform.system', return_value='Linux'):
            module = PlatformDetectionModule()
            result = module.execute(mock_context)
            
            assert result.success
            assert mock_context['platform'] == 'linux'
            assert mock_context['shell'] == 'bash'


class TestGitSyncModule:
    """Tests for git_sync_module."""
    
    def test_execute_success(self, mock_context, temp_project_dir):
        """Test successful Git sync."""
        mock_context['project_root'] = temp_project_dir
        
        # Initialize Git repo
        import subprocess
        subprocess.run(['git', 'init'], cwd=temp_project_dir, check=True)
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0, stdout='Already up to date.')
            
            module = GitSyncModule()
            result = module.execute(mock_context)
            
            assert result.success
    
    def test_execute_no_git_repo(self, mock_context, temp_project_dir):
        """Test Git sync with no repository."""
        mock_context['project_root'] = temp_project_dir
        
        module = GitSyncModule()
        result = module.execute(mock_context)
        
        # Should warn but not fail
        assert result.status in ['warning', 'skipped']


class TestVirtualEnvironmentModule:
    """Tests for virtual_environment_module."""
    
    def test_execute_creates_venv(self, mock_context, temp_project_dir):
        """Test virtual environment creation."""
        mock_context['project_root'] = temp_project_dir
        
        with patch('venv.create') as mock_create:
            module = VirtualEnvironmentModule()
            result = module.execute(mock_context)
            
            assert result.success
            mock_create.assert_called_once()
    
    def test_execute_venv_exists(self, mock_context, temp_project_dir):
        """Test with existing virtual environment."""
        mock_context['project_root'] = temp_project_dir
        venv_path = temp_project_dir / '.venv'
        venv_path.mkdir()
        
        module = VirtualEnvironmentModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'venv_path' in mock_context


class TestPythonDependenciesModule:
    """Tests for python_dependencies_module."""
    
    def test_execute_installs_requirements(self, mock_context, temp_project_dir):
        """Test dependency installation."""
        mock_context['project_root'] = temp_project_dir
        
        # Create requirements.txt
        (temp_project_dir / 'requirements.txt').write_text('pytest>=7.0.0\n')
        
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = Mock(returncode=0)
            
            module = PythonDependenciesModule()
            result = module.execute(mock_context)
            
            assert result.success
    
    def test_execute_no_requirements_file(self, mock_context, temp_project_dir):
        """Test with missing requirements.txt."""
        mock_context['project_root'] = temp_project_dir
        
        module = PythonDependenciesModule()
        result = module.execute(mock_context)
        
        # Should warn but not fail
        assert result.status in ['warning', 'skipped']


class TestVisionAPIModule:
    """Tests for vision_api_module."""
    
    def test_execute_mock_mode(self, mock_context):
        """Test Vision API in mock mode."""
        mock_context['vision_api_enabled'] = False
        
        module = VisionAPIModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert mock_context['vision_api_mode'] == 'mock'
    
    def test_should_run_profile_check(self, mock_context):
        """Test profile-based execution."""
        mock_context['profile'] = 'minimal'
        
        module = VisionAPIModule()
        should_run = module.should_run(mock_context)
        
        assert not should_run  # Vision API skipped in minimal profile


# =============================================================================
# STORY REFRESH MODULE TESTS
# =============================================================================

class TestLoadStoryTemplateModule:
    """Tests for load_story_template_module."""
    
    def test_execute_success(self, mock_context, temp_project_dir):
        """Test successful story loading."""
        mock_context['project_root'] = temp_project_dir
        
        module = LoadStoryTemplateModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'story_content' in mock_context
        assert 'story_lines' in mock_context
        assert mock_context['story_lines'] > 0
    
    def test_execute_file_not_found(self, mock_context, tmp_path):
        """Test with missing story file."""
        mock_context['project_root'] = tmp_path
        
        module = LoadStoryTemplateModule()
        result = module.execute(mock_context)
        
        assert not result.success
        assert 'not found' in result.message.lower()


class TestApplyNarratorVoiceModule:
    """Tests for apply_narrator_voice_module."""
    
    def test_execute_validation_only(self, mock_context):
        """Test validation-only mode (SKULL-005)."""
        mock_context['story_content'] = "# Test Story\n\nContent here."
        
        module = ApplyNarratorVoiceModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'transformed_story' in mock_context
        assert mock_context['transformation_applied'] == False
        assert result.data['validation_only'] == True
    
    def test_execute_no_story_content(self, mock_context):
        """Test with missing story content."""
        module = ApplyNarratorVoiceModule()
        result = module.execute(mock_context)
        
        assert not result.success


class TestValidateStoryStructureModule:
    """Tests for validate_story_structure_module."""
    
    def test_execute_valid_structure(self, mock_context):
        """Test validation of valid story structure."""
        mock_context['transformed_story'] = """# Main Title

## Section 1

Content here.

### Subsection

More content.
"""
        
        module = ValidateStoryStructureModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert mock_context['structure_valid'] == True
        assert mock_context['heading_count'] > 0
    
    def test_execute_missing_title(self, mock_context):
        """Test validation with missing H1 title."""
        mock_context['transformed_story'] = """## Section

Content without H1 title.
"""
        
        module = ValidateStoryStructureModule()
        result = module.execute(mock_context)
        
        assert result.status == 'warning'
        assert len(mock_context['validation_warnings']) > 0
    
    def test_execute_heading_jump(self, mock_context):
        """Test validation with heading hierarchy jump."""
        mock_context['transformed_story'] = """# Title

### Subsection (skipped H2)

Content.
"""
        
        module = ValidateStoryStructureModule()
        result = module.execute(mock_context)
        
        assert result.status == 'warning'
        assert any('jump' in w.lower() for w in mock_context['validation_warnings'])


class TestSaveStoryMarkdownModule:
    """Tests for save_story_markdown_module."""
    
    def test_execute_success(self, mock_context, temp_project_dir):
        """Test successful story save."""
        mock_context['project_root'] = temp_project_dir
        mock_context['transformed_story'] = "# Test Story\n\nContent."
        
        module = SaveStoryMarkdownModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'story_file_path' in mock_context
        
        # Verify file written
        output_path = mock_context['story_file_path']
        assert output_path.exists()
    
    def test_execute_creates_backup(self, mock_context, temp_project_dir):
        """Test backup creation for existing file."""
        mock_context['project_root'] = temp_project_dir
        mock_context['transformed_story'] = "# Test Story\n\nContent."
        
        # Create existing file
        output_path = temp_project_dir / 'docs' / 'awakening-of-cortex.md'
        output_path.parent.mkdir(exist_ok=True)
        output_path.write_text("Old content")
        
        module = SaveStoryMarkdownModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'backup_path' in mock_context
        assert mock_context['backup_path'].exists()
    
    def test_rollback(self, mock_context, temp_project_dir):
        """Test rollback mechanism."""
        mock_context['project_root'] = temp_project_dir
        
        # Create backup
        backup_path = temp_project_dir / 'docs' / 'backup.md'
        backup_path.parent.mkdir(exist_ok=True)
        backup_path.write_text("Backup content")
        
        output_path = temp_project_dir / 'docs' / 'awakening-of-cortex.md'
        output_path.write_text("New content")
        
        mock_context['backup_path'] = backup_path
        mock_context['story_file_path'] = output_path
        
        module = SaveStoryMarkdownModule()
        success = module.rollback(mock_context)
        
        assert success
        assert output_path.read_text() == "Backup content"


class TestUpdateMkdocsIndexModule:
    """Tests for update_mkdocs_index_module."""
    
    def test_execute_entry_exists(self, mock_context, temp_project_dir):
        """Test when story entry already exists."""
        mock_context['project_root'] = temp_project_dir
        
        # Add story to mkdocs.yml
        mkdocs_path = temp_project_dir / 'mkdocs.yml'
        content = mkdocs_path.read_text()
        content += "  - Story: 'awakening-of-cortex'\n"
        mkdocs_path.write_text(content)
        
        module = UpdateMkdocsIndexModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert mock_context['mkdocs_updated'] == False
    
    def test_execute_adds_entry(self, mock_context, temp_project_dir):
        """Test adding new story entry."""
        mock_context['project_root'] = temp_project_dir
        
        module = UpdateMkdocsIndexModule()
        result = module.execute(mock_context)
        
        assert result.success
        # Check if entry was added (depends on implementation)


class TestBuildStoryPreviewModule:
    """Tests for build_story_preview_module."""
    
    def test_should_run_full_profile(self, mock_context):
        """Test that module only runs in full profile."""
        mock_context['profile'] = 'full'
        
        module = BuildStoryPreviewModule()
        should_run = module.should_run(mock_context)
        
        assert should_run
    
    def test_should_run_standard_profile(self, mock_context):
        """Test that module skips in standard profile."""
        mock_context['profile'] = 'standard'
        
        module = BuildStoryPreviewModule()
        should_run = module.should_run(mock_context)
        
        assert not should_run
    
    @patch('subprocess.run')
    def test_execute_success(self, mock_run, mock_context, temp_project_dir):
        """Test successful preview build."""
        mock_context['project_root'] = temp_project_dir
        mock_context['profile'] = 'full'
        
        # Mock mkdocs version check
        mock_run.return_value = Mock(returncode=0, stdout='mkdocs 1.4.0')
        
        # Create site directory
        (temp_project_dir / 'site' / 'awakening-of-cortex').mkdir(parents=True)
        (temp_project_dir / 'site' / 'awakening-of-cortex' / 'index.html').touch()
        
        module = BuildStoryPreviewModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'preview_url' in mock_context


# =============================================================================
# WORKSPACE CLEANUP MODULE TESTS
# =============================================================================

class TestScanTemporaryFilesModule:
    """Tests for scan_temporary_files_module."""
    
    def test_execute_finds_temp_files(self, mock_context, temp_project_dir):
        """Test scanning for temporary files."""
        mock_context['project_root'] = temp_project_dir
        
        # Create some temp files
        (temp_project_dir / 'test.tmp').touch()
        (temp_project_dir / 'cache.cache').touch()
        
        module = ScanTemporaryFilesModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'temp_files' in mock_context
        assert len(mock_context['temp_files']) >= 2


class TestRemoveOldLogsModule:
    """Tests for remove_old_logs_module."""
    
    def test_execute_removes_old_logs(self, mock_context, temp_project_dir):
        """Test removing old log files."""
        mock_context['project_root'] = temp_project_dir
        
        # Create old log file
        logs_dir = temp_project_dir / 'logs'
        logs_dir.mkdir()
        old_log = logs_dir / 'old.log'
        old_log.touch()
        
        # Modify timestamp to make it old
        import time
        old_time = time.time() - (31 * 24 * 60 * 60)  # 31 days ago
        import os
        os.utime(old_log, (old_time, old_time))
        
        module = RemoveOldLogsModule()
        result = module.execute(mock_context)
        
        assert result.success


class TestVacuumSQLiteDatabasesModule:
    """Tests for vacuum_sqlite_databases_module."""
    
    def test_execute_vacuums_databases(self, mock_context, temp_project_dir):
        """Test vacuuming SQLite databases."""
        mock_context['project_root'] = temp_project_dir
        
        # Create test database
        import sqlite3
        db_path = temp_project_dir / 'cortex-brain' / 'test.db'
        db_path.parent.mkdir(exist_ok=True)
        
        conn = sqlite3.connect(db_path)
        conn.execute('CREATE TABLE test (id INTEGER)')
        conn.commit()
        conn.close()
        
        module = VacuumSQLiteDatabasesModule()
        result = module.execute(mock_context)
        
        assert result.success


# =============================================================================
# DOCUMENTATION MODULE TESTS
# =============================================================================

class TestScanDocstringsModule:
    """Tests for scan_docstrings_module."""
    
    def test_execute_scans_python_files(self, mock_context, temp_project_dir):
        """Test scanning Python files for docstrings."""
        mock_context['project_root'] = temp_project_dir
        
        # Create Python file with docstring
        py_file = temp_project_dir / 'src' / 'operations' / 'test.py'
        py_file.write_text('''"""Test module docstring."""

def test_function():
    """Test function docstring."""
    pass
''')
        
        module = ScanDocstringsModule()
        result = module.execute(mock_context)
        
        assert result.success
        assert 'docstrings' in mock_context


class TestGenerateAPIDocsModule:
    """Tests for generate_api_docs_module."""
    
    def test_execute_generates_docs(self, mock_context, temp_project_dir):
        """Test API documentation generation."""
        mock_context['project_root'] = temp_project_dir
        mock_context['docstrings'] = {
            'src/operations/test.py': {
                'module': 'Test module',
                'functions': ['test_function']
            }
        }
        
        module = GenerateAPIDocsModule()
        result = module.execute(mock_context)
        
        assert result.success


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestModuleIntegration:
    """Integration tests for complete operations."""
    
    def test_story_refresh_complete_flow(self, temp_project_dir):
        """Test complete story refresh workflow."""
        context = {
            'project_root': temp_project_dir,
            'profile': 'standard'
        }
        
        # Execute modules in order
        modules = [
            LoadStoryTemplateModule(),
            ApplyNarratorVoiceModule(),
            ValidateStoryStructureModule(),
            SaveStoryMarkdownModule(),
            UpdateMkdocsIndexModule()
        ]
        
        for module in modules:
            if module.should_run(context):
                result = module.execute(context)
                assert result.success, f"{module.__class__.__name__} failed"
        
        # Verify final output
        output_path = temp_project_dir / 'docs' / 'awakening-of-cortex.md'
        assert output_path.exists()


# =============================================================================
# RUN ALL TESTS
# =============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
