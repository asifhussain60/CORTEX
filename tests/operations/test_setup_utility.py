"""
Test Suite for Setup Utility

Tests version-specific shared environment creation and utility functions.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import pytest
from pathlib import Path
from src.operations.modules.setup.setup_utility import (
    create_versioned_shared_venv,
    create_shared_venv
)


class TestSetupUtility:
    """Test setup utility functions."""
    
    def test_create_versioned_shared_venv_auto_detect(self, tmp_path):
        """Test version-specific venv creation with auto-detection."""
        result = create_versioned_shared_venv(home_dir=tmp_path)
        
        assert result['success'] is True
        assert result['created'] is True
        expected_version = f"{sys.version_info.major}.{sys.version_info.minor}"
        assert result['python_version'] == expected_version
        assert f"venv-{expected_version}" in result['venv_path']
        
        venv_path = Path(result['venv_path'])
        assert venv_path.exists()
        assert venv_path.is_dir()
    
    def test_create_versioned_shared_venv_specific_version(self, tmp_path):
        """Test version-specific venv creation with specified version."""
        result = create_versioned_shared_venv(python_version="3.11", home_dir=tmp_path)
        
        assert result['success'] is True
        assert result['python_version'] == "3.11"
        assert "venv-3.11" in result['venv_path']
        
        venv_path = Path(result['venv_path'])
        assert venv_path.exists()
    
    def test_create_versioned_shared_venv_already_exists(self, tmp_path):
        """Test creating venv when it already exists."""
        # Create first time
        result1 = create_versioned_shared_venv(python_version="3.10", home_dir=tmp_path)
        assert result1['success'] is True
        assert result1['created'] is True
        
        # Create again - should detect existing
        result2 = create_versioned_shared_venv(python_version="3.10", home_dir=tmp_path)
        assert result2['success'] is True
        assert result2['created'] is False
        assert "already exists" in result2['message']
    
    def test_create_versioned_shared_venv_path_structure(self, tmp_path):
        """Test correct directory structure is created."""
        result = create_versioned_shared_venv(python_version="3.12", home_dir=tmp_path)
        
        venv_path = Path(result['venv_path'])
        assert venv_path.parent.name == ".cortex"
        assert venv_path.name == "venv-3.12"
        
        # Check for venv structure
        assert (venv_path / "pyvenv.cfg").exists()
        # Check for Python executable (Unix or Windows)
        has_python = (venv_path / "bin" / "python").exists() or \
                    (venv_path / "Scripts" / "python.exe").exists()
        assert has_python
    
    def test_create_shared_venv_backward_compatibility(self, tmp_path):
        """Test backward compatibility of non-versioned function."""
        result = create_shared_venv(home_dir=tmp_path)
        
        assert result['success'] is True
        assert ".cortex/venv" in result['venv_path']
        # Should not have version in path
        assert "venv-" not in result['venv_path'] or result['venv_path'].endswith("venv")
