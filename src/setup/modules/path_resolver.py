"""
Path Resolution Service

Resolves configured paths, creates directories, and ensures proper file placement.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
from pathlib import Path
from typing import Optional, Union
import logging
from src.setup.models.user_path_config import UserPathConfig
from src.setup.modules.user_profile_storage import UserProfileStorage

logger = logging.getLogger(__name__)


class PathResolver:
    """
    Resolves user-configured paths and ensures directories exist.
    
    Example:
        resolver = PathResolver(workspace_root="/path/to/repo")
        test_dir = resolver.get_test_directory()
        reports_dir = resolver.get_documents_directory("reports")
    """
    
    def __init__(self, workspace_root: Optional[str] = None, config: Optional[UserPathConfig] = None):
        """
        Initialize path resolver.
        
        Args:
            workspace_root: Repository root directory
            config: User path configuration (loads from cortex.config.json if None)
        """
        self.workspace_root = Path(workspace_root or Path.cwd()).resolve()
        
        if config:
            self.config = config
        else:
            # Try to load from cortex.config.json
            storage = UserProfileStorage()
            self.config = storage.load_path_config()
            
            if not self.config:
                # Fallback to default configuration
                logger.warning("No user path configuration found, using defaults")
                self.config = self._get_default_config()
    
    def _get_default_config(self) -> UserPathConfig:
        """Get default path configuration."""
        return UserPathConfig(
            test_directory="tests",
            reports_directory="cortex-brain/documents/reports",
            documents_directory="cortex-brain/documents",
            planning_directory="cortex-brain/documents/planning",
            analysis_directory="cortex-brain/documents/analysis",
            summaries_directory="cortex-brain/documents/summaries",
            investigations_directory="cortex-brain/documents/investigations",
            temp_directory=".cortex-temp",
            custom_paths={}
        )
    
    def get_test_directory(self, create: bool = False) -> Path:
        """
        Get absolute path to test directory.
        
        Args:
            create: If True, creates directory if it doesn't exist
        
        Returns:
            Absolute Path to test directory
        """
        test_dir_str = self.config.get_test_directory(str(self.workspace_root))
        test_dir = Path(test_dir_str)
        
        if not test_dir.is_absolute():
            test_dir = self.workspace_root / test_dir
        
        test_dir = test_dir.resolve()
        
        if create and not test_dir.exists():
            logger.info(f"Creating test directory: {test_dir}")
            test_dir.mkdir(parents=True, exist_ok=True)
            
            # Create __init__.py for Python projects
            if self._is_python_project():
                init_file = test_dir / "__init__.py"
                if not init_file.exists():
                    init_file.touch()
        
        return test_dir
    
    def get_documents_directory(self, category: str = "", create: bool = True) -> Path:
        """
        Get absolute path to documents directory for a specific category.
        
        Args:
            category: Document category (reports, analysis, summaries, planning, investigations)
            create: If True, creates directory if it doesn't exist
        
        Returns:
            Absolute Path to documents directory
        """
        dir_str = self.config.get_documents_directory(category)
        doc_dir = Path(dir_str)
        
        if not doc_dir.is_absolute():
            doc_dir = self.workspace_root / doc_dir
        
        doc_dir = doc_dir.resolve()
        
        if create and not doc_dir.exists():
            logger.info(f"Creating documents directory: {doc_dir}")
            doc_dir.mkdir(parents=True, exist_ok=True)
        
        return doc_dir
    
    def get_temp_directory(self, create: bool = True) -> Optional[Path]:
        """
        Get absolute path to temporary files directory.
        
        Args:
            create: If True, creates directory if it doesn't exist
        
        Returns:
            Absolute Path to temp directory, or None if not configured
        """
        if not self.config.temp_directory:
            return None
        
        temp_dir = Path(self.config.temp_directory)
        
        if not temp_dir.is_absolute():
            temp_dir = self.workspace_root / temp_dir
        
        temp_dir = temp_dir.resolve()
        
        if create and not temp_dir.exists():
            logger.info(f"Creating temp directory: {temp_dir}")
            temp_dir.mkdir(parents=True, exist_ok=True)
        
        return temp_dir
    
    def get_custom_path(self, key: str, create: bool = False) -> Optional[Path]:
        """
        Get absolute path for a custom user-defined path.
        
        Args:
            key: Custom path key
            create: If True, creates directory if it doesn't exist
        
        Returns:
            Absolute Path or None if key not found
        """
        if key not in self.config.custom_paths:
            return None
        
        custom_path = Path(self.config.custom_paths[key])
        
        if not custom_path.is_absolute():
            custom_path = self.workspace_root / custom_path
        
        custom_path = custom_path.resolve()
        
        if create and not custom_path.exists():
            logger.info(f"Creating custom directory '{key}': {custom_path}")
            custom_path.mkdir(parents=True, exist_ok=True)
        
        return custom_path
    
    def resolve_path(self, path: Union[str, Path], create: bool = False) -> Path:
        """
        Resolve a path relative to workspace root.
        
        Args:
            path: Path to resolve
            create: If True, creates directory if it doesn't exist
        
        Returns:
            Absolute resolved Path
        """
        path_obj = Path(path)
        
        if not path_obj.is_absolute():
            path_obj = self.workspace_root / path_obj
        
        path_obj = path_obj.resolve()
        
        if create and not path_obj.exists():
            if path_obj.suffix:
                # It's a file, create parent directory
                path_obj.parent.mkdir(parents=True, exist_ok=True)
            else:
                # It's a directory
                path_obj.mkdir(parents=True, exist_ok=True)
        
        return path_obj
    
    def get_document_path(self, filename: str, category: str = "reports", create_dir: bool = True) -> Path:
        """
        Get full path for a document file in a specific category.
        
        Args:
            filename: Document filename
            category: Document category
            create_dir: If True, creates directory if it doesn't exist
        
        Returns:
            Absolute Path to document file
        """
        doc_dir = self.get_documents_directory(category, create=create_dir)
        return doc_dir / filename
    
    def ensure_directory_exists(self, path: Union[str, Path]) -> Path:
        """
        Ensure a directory exists, creating it if necessary.
        
        Args:
            path: Directory path
        
        Returns:
            Absolute Path to directory
        """
        resolved = self.resolve_path(path, create=False)
        
        if not resolved.exists():
            logger.info(f"Creating directory: {resolved}")
            resolved.mkdir(parents=True, exist_ok=True)
        elif not resolved.is_dir():
            raise ValueError(f"Path exists but is not a directory: {resolved}")
        
        return resolved
    
    def _is_python_project(self) -> bool:
        """Check if workspace is a Python project."""
        indicators = [
            self.workspace_root / "requirements.txt",
            self.workspace_root / "setup.py",
            self.workspace_root / "pyproject.toml",
            self.workspace_root / "Pipfile"
        ]
        return any(indicator.exists() for indicator in indicators)
    
    def get_relative_path(self, absolute_path: Union[str, Path]) -> str:
        """
        Get path relative to workspace root.
        
        Args:
            absolute_path: Absolute path
        
        Returns:
            Relative path string
        """
        try:
            return str(Path(absolute_path).relative_to(self.workspace_root))
        except ValueError:
            # Path is not relative to workspace root
            return str(Path(absolute_path))
    
    def validate_configuration(self) -> dict:
        """
        Validate current path configuration.
        
        Returns:
            Dictionary with validation results
        """
        results = {
            "valid": True,
            "warnings": [],
            "errors": []
        }
        
        # Check test directory
        try:
            test_dir = self.get_test_directory(create=False)
            if not test_dir.exists():
                results["warnings"].append(f"Test directory does not exist: {test_dir}")
        except Exception as e:
            results["errors"].append(f"Invalid test directory configuration: {e}")
            results["valid"] = False
        
        # Check document directories
        categories = ["reports", "analysis", "summaries", "planning", "investigations"]
        for category in categories:
            try:
                doc_dir = self.get_documents_directory(category, create=False)
                if not doc_dir.exists():
                    results["warnings"].append(f"{category.capitalize()} directory does not exist: {doc_dir}")
            except Exception as e:
                results["errors"].append(f"Invalid {category} directory configuration: {e}")
                results["valid"] = False
        
        return results
