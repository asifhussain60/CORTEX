"""
Folder Structure Tests - PHASE-PARALLEL

Verification tests for PHASE-PARALLEL folder structure migration:
- AC-AR-010-01: New folder structure created
- AC-AR-010-02: All imports updated to new paths
- AC-AR-010-03: Cross-platform path resolution working

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import os
import sys
from pathlib import Path
from typing import List, Set

import pytest

from src.core.path_resolver import get_project_root


class TestAC_AR_010_01_FolderStructure:
    """AC-AR-010-01: New folder structure created."""
    
    def test_folder_structure_exists(self):
        """All required nested folders should exist."""
        project_root = get_project_root()
        
        required_folders = [
            project_root / "src" / "orchestrators" / "core",
            project_root / "src" / "orchestrators" / "domain",
            project_root / "src" / "orchestrators" / "custom",
            project_root / "src" / "infrastructure",
        ]
        
        for folder in required_folders:
            assert folder.exists(), f"Folder missing: {folder}"
            assert folder.is_dir(), f"Expected directory but got file: {folder}"
    
    def test_orchestrators_init_files_exist(self):
        """All orchestrators subfolders should have __init__.py."""
        project_root = get_project_root()
        
        init_files = [
            project_root / "src" / "orchestrators" / "core" / "__init__.py",
            project_root / "src" / "orchestrators" / "domain" / "__init__.py",
            project_root / "src" / "orchestrators" / "custom" / "__init__.py",
        ]
        
        for init_file in init_files:
            assert init_file.exists(), f"Missing __init__.py: {init_file}"
            assert init_file.is_file(), f"Expected file but got directory: {init_file}"
    
    def test_orchestrator_modules_exist(self):
        """Core orchestrator modules should be in new locations."""
        project_root = get_project_root()
        
        required_modules = [
            project_root / "src" / "orchestrators" / "core" / "master_orchestrator.py",
            project_root / "src" / "orchestrators" / "core" / "orchestrator_registry.py",
            project_root / "src" / "orchestrators" / "domain" / "planning_orchestrator.py",
        ]
        
        for module in required_modules:
            assert module.exists(), f"Module missing: {module}"
            assert module.is_file(), f"Expected file but got directory: {module}"


class TestAC_AR_010_02_ImportsUpdated:
    """AC-AR-010-02: All imports updated to new paths."""
    
    def test_absolute_imports_in_orchestrators(self):
        """All imports in orchestrators should use absolute paths."""
        project_root = get_project_root()
        orchestrators_dir = project_root / "src" / "orchestrators"
        
        py_files = list(orchestrators_dir.rglob("*.py"))
        assert len(py_files) > 0, "No Python files found in orchestrators"
        
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue
            
            with open(py_file, "r") as f:
                content = f.read()
            
            # Check that imports use absolute paths (from src.*)
            lines = content.split("\n")
            for line in lines:
                if line.startswith("from ") or line.startswith("import "):
                    # Relative imports (../ or ./) should not exist
                    assert not line.startswith("from .."), \
                        f"Found relative import in {py_file}: {line}"
                    assert not line.startswith("from ."), \
                        f"Found relative import in {py_file}: {line}"
    
    def test_imports_resolvable(self):
        """All imports should be resolvable without errors."""
        project_root = get_project_root()
        
        # Import the orchestrator modules to verify imports are correct
        try:
            # These imports should succeed if imports are updated correctly
            from src.orchestrators.core import master_orchestrator
            from src.orchestrators.core import orchestrator_registry
            from src.orchestrators.domain import planning_orchestrator
        except ImportError as e:
            pytest.fail(f"Import failed: {e}")


class TestAC_AR_010_03_CrossPlatformPaths:
    """AC-AR-010-03: Cross-platform path resolution working."""
    
    def test_pathlib_usage(self):
        """Code should use pathlib for cross-platform compatibility."""
        project_root = get_project_root()
        orchestrators_dir = project_root / "src" / "orchestrators"
        
        py_files = list(orchestrators_dir.rglob("*.py"))
        assert len(py_files) > 0, "No Python files found in orchestrators"
        
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue
            
            with open(py_file, "r") as f:
                content = f.read()
            
            # Check that pathlib Path is used instead of os.path
            if "import os" in content and "os.path" in content:
                # Make sure pathlib is also imported and used
                assert "from pathlib import Path" in content or "import pathlib" in content, \
                    f"File {py_file} uses os.path but doesn't import pathlib"
    
    def test_paths_work_on_current_platform(self):
        """All paths should resolve correctly on current platform."""
        project_root = get_project_root()
        
        test_paths = [
            project_root / "src" / "orchestrators" / "core",
            project_root / "src" / "orchestrators" / "domain",
            project_root / "src" / "orchestrators" / "custom",
        ]
        
        for path in test_paths:
            # Should resolve without errors
            resolved = path.resolve()
            assert resolved.exists(), f"Path doesn't exist: {resolved}"
            # Should have consistent string representation
            assert str(resolved) == str(path.resolve()), \
                f"Path resolution inconsistent: {path}"
    
    def test_no_hardcoded_separators(self):
        """Code should not use hardcoded path separators."""
        project_root = get_project_root()
        orchestrators_dir = project_root / "src" / "orchestrators"
        
        py_files = list(orchestrators_dir.rglob("*.py"))
        
        for py_file in py_files:
            if "__pycache__" in str(py_file):
                continue
            
            with open(py_file, "r") as f:
                content = f.read()
            
            # Check for hardcoded separators (except in strings/comments)
            lines = content.split("\n")
            for line_num, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith("#"):
                    continue
                
                # Check for suspicious path constructions
                if '"\\\\"' in line and "Path" not in line:
                    pytest.fail(f"Found hardcoded path separator in {py_file}:{line_num}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
