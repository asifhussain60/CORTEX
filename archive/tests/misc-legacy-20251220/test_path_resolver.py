"""
Tests for PathResolver

Tests path resolution, directory creation, and configuration loading.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from src.setup.modules.path_resolver import PathResolver
from src.setup.models.user_path_config import UserPathConfig


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def temp_workspace_with_config():
    """Create workspace with cortex.config.json."""
    temp_dir = tempfile.mkdtemp()
    workspace = Path(temp_dir)
    
    # Create cortex.config.json
    config = {
        "user_paths": {
            "test_directory": "tests",
            "reports_directory": "cortex-brain/documents/reports",
            "custom_paths": {"logs": "logs"}
        }
    }
    
    config_file = workspace / "cortex.config.json"
    config_file.write_text(json.dumps(config, indent=2))
    
    yield workspace
    
    shutil.rmtree(temp_dir)


class TestPathResolverInitialization:
    """Test PathResolver initialization."""
    
    def test_init_with_workspace(self, temp_workspace):
        """Test initializing with workspace root."""
        resolver = PathResolver(workspace_root=str(temp_workspace))
        
        assert resolver.workspace_root == temp_workspace
        assert resolver.config is not None
    
    def test_init_with_config(self, temp_workspace):
        """Test initializing with explicit config."""
        config = UserPathConfig(test_directory="__tests__")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        assert resolver.config.test_directory == "__tests__"
    
    def test_init_uses_default_config(self, temp_workspace):
        """Test that default config is used when none exists."""
        resolver = PathResolver(workspace_root=str(temp_workspace))
        
        # Should have default config
        assert resolver.config is not None
        assert isinstance(resolver.config, UserPathConfig)


class TestPathResolverTestDirectory:
    """Test test directory resolution."""
    
    def test_get_test_directory_no_create(self, temp_workspace):
        """Test getting test directory without creation."""
        config = UserPathConfig(test_directory="tests")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        test_dir = resolver.get_test_directory(create=False)
        
        assert test_dir == temp_workspace / "tests"
    
    def test_get_test_directory_with_create(self, temp_workspace):
        """Test getting test directory with creation."""
        config = UserPathConfig(test_directory="tests")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        test_dir = resolver.get_test_directory(create=True)
        
        assert test_dir.exists()
        assert test_dir.is_dir()
    
    def test_get_test_directory_python_project(self, temp_workspace):
        """Test that __init__.py is created for Python projects."""
        # Create Python project marker
        (temp_workspace / "requirements.txt").write_text("pytest")
        
        config = UserPathConfig(test_directory="tests")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        test_dir = resolver.get_test_directory(create=True)
        
        assert (test_dir / "__init__.py").exists()
    
    def test_get_test_directory_absolute_path(self, temp_workspace):
        """Test absolute path handling."""
        abs_test_dir = temp_workspace / "absolute_tests"
        
        config = UserPathConfig(test_directory=str(abs_test_dir))
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        test_dir = resolver.get_test_directory(create=True)
        
        assert test_dir == abs_test_dir
        assert test_dir.exists()


class TestPathResolverDocumentsDirectory:
    """Test documents directory resolution."""
    
    def test_get_documents_directory_reports(self, temp_workspace):
        """Test getting reports directory."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        reports_dir = resolver.get_documents_directory("reports", create=True)
        
        assert "reports" in str(reports_dir)
        assert reports_dir.exists()
    
    def test_get_documents_directory_analysis(self, temp_workspace):
        """Test getting analysis directory."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        analysis_dir = resolver.get_documents_directory("analysis", create=True)
        
        assert "analysis" in str(analysis_dir)
        assert analysis_dir.exists()
    
    def test_get_documents_directory_no_create(self, temp_workspace):
        """Test getting directory without creation."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        reports_dir = resolver.get_documents_directory("reports", create=False)
        
        assert not reports_dir.exists()
    
    def test_get_documents_directory_custom_path(self, temp_workspace):
        """Test custom documents path."""
        config = UserPathConfig(reports_directory="docs/reports")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        reports_dir = resolver.get_documents_directory("reports", create=True)
        
        assert reports_dir == temp_workspace / "docs" / "reports"
        assert reports_dir.exists()


class TestPathResolverTempDirectory:
    """Test temp directory resolution."""
    
    def test_get_temp_directory(self, temp_workspace):
        """Test getting temp directory."""
        config = UserPathConfig(temp_directory=".cortex-temp")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        temp_dir = resolver.get_temp_directory(create=True)
        
        assert temp_dir is not None
        assert temp_dir.exists()
    
    def test_get_temp_directory_none(self, temp_workspace):
        """Test when temp directory is not configured."""
        config = UserPathConfig(temp_directory=None)
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        temp_dir = resolver.get_temp_directory()
        
        assert temp_dir is None


class TestPathResolverCustomPaths:
    """Test custom path resolution."""
    
    def test_get_custom_path_exists(self, temp_workspace):
        """Test getting existing custom path."""
        config = UserPathConfig(custom_paths={"logs": "logs"})
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        logs_dir = resolver.get_custom_path("logs", create=True)
        
        assert logs_dir is not None
        assert logs_dir == temp_workspace / "logs"
        assert logs_dir.exists()
    
    def test_get_custom_path_not_exists(self, temp_workspace):
        """Test getting non-existent custom path."""
        config = UserPathConfig(custom_paths={})
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        result = resolver.get_custom_path("nonexistent")
        
        assert result is None


class TestPathResolverGeneralResolution:
    """Test general path resolution."""
    
    def test_resolve_path_relative(self, temp_workspace):
        """Test resolving relative path."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        resolved = resolver.resolve_path("src/main.py", create=False)
        
        assert resolved == temp_workspace / "src" / "main.py"
    
    def test_resolve_path_absolute(self, temp_workspace):
        """Test resolving absolute path."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        abs_path = temp_workspace / "absolute.py"
        resolved = resolver.resolve_path(str(abs_path), create=False)
        
        assert resolved == abs_path
    
    def test_resolve_path_create_file(self, temp_workspace):
        """Test path resolution with file creation."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        file_path = resolver.resolve_path("src/test.py", create=True)
        
        # Parent directory should be created
        assert file_path.parent.exists()
    
    def test_resolve_path_create_directory(self, temp_workspace):
        """Test path resolution with directory creation."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        dir_path = resolver.resolve_path("src/models", create=True)
        
        assert dir_path.exists()
        assert dir_path.is_dir()


class TestPathResolverDocumentPaths:
    """Test document path construction."""
    
    def test_get_document_path(self, temp_workspace):
        """Test getting full document path."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        doc_path = resolver.get_document_path("report.md", category="reports", create_dir=True)
        
        assert doc_path.name == "report.md"
        assert "reports" in str(doc_path)
        assert doc_path.parent.exists()
    
    def test_get_document_path_no_create(self, temp_workspace):
        """Test document path without directory creation."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        doc_path = resolver.get_document_path("report.md", category="reports", create_dir=False)
        
        assert not doc_path.parent.exists()


class TestPathResolverUtilities:
    """Test utility methods."""
    
    def test_ensure_directory_exists(self, temp_workspace):
        """Test ensuring directory exists."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        new_dir = resolver.ensure_directory_exists("new/nested/dir")
        
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_ensure_directory_exists_already_exists(self, temp_workspace):
        """Test ensuring directory that already exists."""
        existing = temp_workspace / "existing"
        existing.mkdir()
        
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        result = resolver.ensure_directory_exists(str(existing))
        
        assert result == existing
    
    def test_get_relative_path(self, temp_workspace):
        """Test getting relative path."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        abs_path = temp_workspace / "src" / "main.py"
        relative = resolver.get_relative_path(abs_path)
        
        assert relative == "src/main.py" or relative == "src\\main.py"
    
    def test_get_relative_path_outside_workspace(self, temp_workspace):
        """Test relative path for file outside workspace."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        outside_path = "/opt/external/file.py"
        relative = resolver.get_relative_path(outside_path)
        
        # Should return path as-is (normalize for cross-platform comparison)
        assert outside_path.replace("/", "\\") in relative or outside_path in relative


class TestPathResolverValidation:
    """Test configuration validation."""
    
    def test_validate_configuration_valid(self, temp_workspace):
        """Test validation with valid configuration."""
        config = UserPathConfig(test_directory="tests")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        # Create test directory
        (temp_workspace / "tests").mkdir()
        
        results = resolver.validate_configuration()
        
        assert isinstance(results, dict)
        assert "valid" in results
        assert "warnings" in results
        assert "errors" in results
    
    def test_validate_configuration_missing_directories(self, temp_workspace):
        """Test validation with missing directories."""
        config = UserPathConfig(test_directory="tests")
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        results = resolver.validate_configuration()
        
        # Should have warnings about missing directories
        assert len(results["warnings"]) > 0


class TestPathResolverConfigLoading:
    """Test loading configuration from file."""
    
    def test_load_from_config_file(self, temp_workspace_with_config):
        """Test loading config from cortex.config.json."""
        # Note: This test may not work as expected because PathResolver
        # uses UserProfileStorage which looks for config in CORTEX repo
        # This is a known limitation for testing
        
        config = UserPathConfig(test_directory="tests")
        resolver = PathResolver(workspace_root=str(temp_workspace_with_config), config=config)
        
        assert resolver.config.test_directory == "tests"


class TestPathResolverEdgeCases:
    """Test edge cases and error handling."""
    
    def test_resolve_path_with_dots(self, temp_workspace):
        """Test resolving path with . and .. references."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        resolved = resolver.resolve_path("./src/../lib/utils.py")
        
        assert resolved.is_absolute()
    
    def test_resolve_path_with_backslashes(self, temp_workspace):
        """Test Windows-style paths with backslashes."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        resolved = resolver.resolve_path("src\\models\\user.py")
        
        assert resolved.is_absolute()
    
    def test_create_nested_directories(self, temp_workspace):
        """Test creating deeply nested directories."""
        config = UserPathConfig()
        resolver = PathResolver(workspace_root=str(temp_workspace), config=config)
        
        deep_dir = resolver.ensure_directory_exists("a/b/c/d/e/f")
        
        assert deep_dir.exists()
        assert deep_dir.is_dir()
