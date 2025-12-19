"""
Tests for UserPathConfig Model

Tests Pydantic validation and helper methods.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pydantic import ValidationError
from src.setup.models.user_path_config import UserPathConfig


class TestUserPathConfigValidation:
    """Test UserPathConfig model validation."""
    
    def test_default_configuration(self):
        """Test creating config with all defaults."""
        config = UserPathConfig()
        
        assert config.test_directory is None
        assert config.reports_directory == "cortex-brain/documents/reports"
        assert config.documents_directory == "cortex-brain/documents"
        assert config.planning_directory == "cortex-brain/documents/planning"
        assert config.custom_paths == {}
    
    def test_custom_test_directory(self):
        """Test setting custom test directory."""
        config = UserPathConfig(test_directory="__tests__")
        
        assert config.test_directory == "__tests__"
    
    def test_custom_all_paths(self):
        """Test setting all custom paths."""
        config = UserPathConfig(
            test_directory="test",
            reports_directory="docs/reports",
            documents_directory="docs",
            planning_directory="docs/planning",
            analysis_directory="docs/analysis",
            summaries_directory="docs/summaries",
            investigations_directory="docs/investigations",
            temp_directory=".temp",
            custom_paths={"logs": "logs", "screenshots": "screenshots"}
        )
        
        assert config.test_directory == "test"
        assert config.reports_directory == "docs/reports"
        assert config.documents_directory == "docs"
        assert config.temp_directory == ".temp"
        assert config.custom_paths == {"logs": "logs", "screenshots": "screenshots"}
    
    def test_invalid_path_characters(self):
        """Test that invalid characters in paths raise validation error."""
        with pytest.raises(ValidationError):
            UserPathConfig(test_directory="test<>dir")
        
        with pytest.raises(ValidationError):
            UserPathConfig(reports_directory="reports|invalid")
    
    def test_none_values_allowed(self):
        """Test that None is allowed for optional paths."""
        config = UserPathConfig(
            test_directory=None,
            temp_directory=None
        )
        
        assert config.test_directory is None
        assert config.temp_directory is None


class TestUserPathConfigMethods:
    """Test UserPathConfig helper methods."""
    
    def test_get_test_directory_without_workspace(self):
        """Test getting test directory without workspace root."""
        config = UserPathConfig(test_directory="tests")
        
        test_dir = config.get_test_directory()
        assert "tests" in test_dir
    
    def test_get_test_directory_with_workspace(self):
        """Test getting test directory with workspace root."""
        config = UserPathConfig(test_directory="tests")
        
        test_dir = config.get_test_directory(workspace_root="/home/user/project")
        # Normalize path for cross-platform comparison
        assert test_dir.replace("\\", "/") == "/home/user/project/tests"
    
    def test_get_test_directory_absolute_path(self):
        """Test that absolute paths are preserved."""
        config = UserPathConfig(test_directory="/opt/tests")
        
        test_dir = config.get_test_directory(workspace_root="/home/user/project")
        # Normalize path for cross-platform comparison
        assert test_dir.replace("\\", "/") == "/opt/tests"
    
    def test_get_test_directory_none_default(self):
        """Test default test directory when None."""
        config = UserPathConfig(test_directory=None)
        
        test_dir = config.get_test_directory(workspace_root="/home/user/project")
        # Normalize path for cross-platform comparison
        assert test_dir.replace("\\", "/") == "/home/user/project/tests"
    
    def test_get_documents_directory_reports(self):
        """Test getting reports directory."""
        config = UserPathConfig()
        
        reports_dir = config.get_documents_directory("reports")
        assert reports_dir == "cortex-brain/documents/reports"
    
    def test_get_documents_directory_analysis(self):
        """Test getting analysis directory."""
        config = UserPathConfig()
        
        analysis_dir = config.get_documents_directory("analysis")
        assert analysis_dir == "cortex-brain/documents/analysis"
    
    def test_get_documents_directory_unknown_category(self):
        """Test getting documents directory for unknown category."""
        config = UserPathConfig()
        
        docs_dir = config.get_documents_directory("unknown")
        assert docs_dir == "cortex-brain/documents"
    
    def test_get_documents_directory_no_category(self):
        """Test getting base documents directory."""
        config = UserPathConfig()
        
        docs_dir = config.get_documents_directory()
        assert docs_dir == "cortex-brain/documents"
    
    def test_to_dict_conversion(self):
        """Test converting config to dictionary."""
        config = UserPathConfig(
            test_directory="tests",
            custom_paths={"logs": "logs"}
        )
        
        data = config.to_dict()
        
        assert isinstance(data, dict)
        assert data["test_directory"] == "tests"
        assert data["custom_paths"] == {"logs": "logs"}
        assert "reports_directory" in data


class TestUserPathConfigSchema:
    """Test schema compatibility and serialization."""
    
    def test_model_dump(self):
        """Test Pydantic model_dump method."""
        config = UserPathConfig(test_directory="tests")
        
        data = config.model_dump()
        
        assert isinstance(data, dict)
        assert data["test_directory"] == "tests"
    
    def test_model_dump_exclude_none(self):
        """Test excluding None values from dump."""
        config = UserPathConfig(test_directory=None)
        
        data = config.model_dump(exclude_none=True)
        
        assert "test_directory" not in data or data.get("test_directory") is None
    
    def test_json_schema(self):
        """Test JSON schema generation."""
        schema = UserPathConfig.model_json_schema()
        
        assert "properties" in schema
        assert "test_directory" in schema["properties"]
        assert "custom_paths" in schema["properties"]
    
    def test_from_dict(self):
        """Test creating config from dictionary."""
        data = {
            "test_directory": "tests",
            "reports_directory": "docs/reports",
            "custom_paths": {"logs": "logs"}
        }
        
        config = UserPathConfig(**data)
        
        assert config.test_directory == "tests"
        assert config.reports_directory == "docs/reports"
        assert config.custom_paths == {"logs": "logs"}


class TestUserPathConfigEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_custom_paths(self):
        """Test empty custom paths dictionary."""
        config = UserPathConfig(custom_paths={})
        
        assert config.custom_paths == {}
    
    def test_windows_style_paths(self):
        """Test Windows-style paths."""
        config = UserPathConfig(test_directory="C:\\Users\\test\\tests")
        
        assert config.test_directory == "C:\\Users\\test\\tests"
    
    def test_unix_style_paths(self):
        """Test Unix-style paths."""
        config = UserPathConfig(test_directory="/home/user/tests")
        
        assert config.test_directory == "/home/user/tests"
    
    def test_relative_paths_with_parent(self):
        """Test relative paths with parent directory references."""
        config = UserPathConfig(test_directory="../tests")
        
        assert config.test_directory == "../tests"
    
    def test_paths_with_spaces(self):
        """Test paths with spaces."""
        config = UserPathConfig(test_directory="test directory")
        
        assert config.test_directory == "test directory"
