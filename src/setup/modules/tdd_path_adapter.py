"""
TDD Workflow Path Integration Example

Demonstrates how to integrate user-configured paths into TDD workflows.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Optional
from src.setup.modules.path_resolver import PathResolver
from src.workflows.test_execution_manager import TestExecutionManager
import logging

logger = logging.getLogger(__name__)


class TDDWorkflowPathAdapter:
    """
    Adapter for TDD workflows to use user-configured paths.
    
    This class bridges the TDD workflow with user path preferences,
    ensuring tests are created in the correct location based on
    user configuration.
    
    Example:
        adapter = TDDWorkflowPathAdapter(workspace_root="/path/to/repo")
        test_path = adapter.get_test_path_for_source("src/login.py")
        # Returns: "/path/to/repo/tests/test_login.py" (or user-configured path)
    """
    
    def __init__(self, workspace_root: str):
        """
        Initialize TDD workflow path adapter.
        
        Args:
            workspace_root: Repository root directory
        """
        self.workspace_root = Path(workspace_root).resolve()
        self.path_resolver = PathResolver(workspace_root=str(self.workspace_root))
        
    def get_test_directory(self) -> Path:
        """
        Get test directory respecting user configuration.
        
        Returns:
            Absolute Path to test directory
        """
        return self.path_resolver.get_test_directory(create=True)
    
    def get_test_path_for_source(self, source_file: str) -> Path:
        """
        Determine test file path for a source file.
        
        Args:
            source_file: Path to source file
        
        Returns:
            Path where test file should be created
        
        Examples:
            src/login.py -> tests/test_login.py
            app/models/user.py -> tests/models/test_user.py
        """
        source_path = Path(source_file)
        test_dir = self.get_test_directory()
        
        # Determine test filename
        if source_path.stem.startswith("test_"):
            test_filename = source_path.name
        else:
            test_filename = f"test_{source_path.name}"
        
        # Try to preserve directory structure within test directory
        try:
            # Find common source directories
            source_dirs = ["src", "app", "lib", "core"]
            relative_path = None
            
            for source_dir in source_dirs:
                try:
                    # Check if source file is under this directory
                    parts = source_path.parts
                    if source_dir in parts:
                        idx = parts.index(source_dir)
                        # Get path after source directory
                        relative_path = Path(*parts[idx + 1:])
                        break
                except ValueError:
                    continue
            
            if relative_path:
                # Preserve directory structure
                test_path = test_dir / relative_path.parent / test_filename
            else:
                # Flat structure
                test_path = test_dir / test_filename
        
        except Exception as e:
            logger.warning(f"Failed to determine relative structure, using flat: {e}")
            test_path = test_dir / test_filename
        
        # Ensure parent directory exists
        test_path.parent.mkdir(parents=True, exist_ok=True)
        
        return test_path
    
    def is_test_file(self, file_path: str) -> bool:
        """
        Check if file is a test file based on location and naming.
        
        Args:
            file_path: Path to check
        
        Returns:
            True if file is a test file
        """
        path = Path(file_path)
        test_dir = self.get_test_directory()
        
        # Check if file is under test directory
        try:
            path.resolve().relative_to(test_dir)
            return True
        except ValueError:
            pass
        
        # Check naming pattern
        name = path.name.lower()
        return (name.startswith("test_") or 
                name.endswith("_test.py") or 
                ".test." in name or 
                ".spec." in name)
    
    def get_source_for_test(self, test_file: str) -> Optional[Path]:
        """
        Find corresponding source file for a test file.
        
        Args:
            test_file: Path to test file
        
        Returns:
            Path to source file if found, None otherwise
        """
        test_path = Path(test_file)
        test_dir = self.get_test_directory()
        
        # Get test filename without prefix
        name = test_path.stem
        if name.startswith("test_"):
            source_name = name[5:]  # Remove "test_" prefix
        elif name.endswith("_test"):
            source_name = name[:-5]  # Remove "_test" suffix
        else:
            source_name = name
        
        source_filename = f"{source_name}{test_path.suffix}"
        
        # Try to find source file
        try:
            # Get relative path within test directory
            relative_test_path = test_path.relative_to(test_dir)
            relative_dir = relative_test_path.parent
            
            # Common source directories
            source_dirs = ["src", "app", "lib", "core"]
            
            for source_dir in source_dirs:
                potential_source = self.workspace_root / source_dir / relative_dir / source_filename
                if potential_source.exists():
                    return potential_source
            
            # Try flat structure in source directories
            for source_dir in source_dirs:
                potential_source = self.workspace_root / source_dir / source_filename
                if potential_source.exists():
                    return potential_source
        
        except Exception as e:
            logger.debug(f"Failed to find source for test: {e}")
        
        return None
    
    def create_test_execution_manager(self) -> TestExecutionManager:
        """
        Create TestExecutionManager configured with user paths.
        
        Returns:
            TestExecutionManager instance
        """
        return TestExecutionManager(workspace_root=str(self.workspace_root))
    
    def validate_test_setup(self) -> dict:
        """
        Validate test setup and configuration.
        
        Returns:
            Validation results
        """
        results = {
            "valid": True,
            "test_directory": str(self.get_test_directory()),
            "test_directory_exists": self.get_test_directory().exists(),
            "warnings": [],
            "errors": []
        }
        
        # Check test directory accessibility
        test_dir = self.get_test_directory()
        if not test_dir.exists():
            results["warnings"].append(f"Test directory will be created: {test_dir}")
        
        # Check write permissions
        try:
            test_file = test_dir / ".cortex_write_test"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            results["errors"].append(f"Cannot write to test directory: {e}")
            results["valid"] = False
        
        return results


# Integration helper functions for existing code

def get_configured_test_directory(workspace_root: str) -> Path:
    """
    Get user-configured test directory for a workspace.
    
    Args:
        workspace_root: Repository root
    
    Returns:
        Absolute Path to test directory
    
    Example:
        test_dir = get_configured_test_directory("/path/to/repo")
        # Use test_dir for test file operations
    """
    adapter = TDDWorkflowPathAdapter(workspace_root)
    return adapter.get_test_directory()


def get_test_path(workspace_root: str, source_file: str) -> Path:
    """
    Get test file path for a source file.
    
    Args:
        workspace_root: Repository root
        source_file: Source file path
    
    Returns:
        Path where test should be created
    
    Example:
        test_path = get_test_path("/path/to/repo", "src/login.py")
        # Returns: "/path/to/repo/tests/test_login.py"
    """
    adapter = TDDWorkflowPathAdapter(workspace_root)
    return adapter.get_test_path_for_source(source_file)


def resolve_document_path(category: str, filename: str, workspace_root: Optional[str] = None) -> Path:
    """
    Resolve document path using user configuration.
    
    Args:
        category: Document category (reports, analysis, summaries, etc.)
        filename: Document filename
        workspace_root: Repository root (optional)
    
    Returns:
        Full path to document file
    
    Example:
        report_path = resolve_document_path("reports", "validation-report.md")
        # Returns: "cortex-brain/documents/reports/validation-report.md" (or user-configured)
    """
    resolver = PathResolver(workspace_root=workspace_root)
    return resolver.get_document_path(filename, category=category)
