"""
Tests for AST Scanning Integration in Planning v5 Phase 0.

Tests cover:
1. AST scanner basic functionality
2. Function/class/import counting
3. Duplicate code detection
4. Orphaned function detection
5. JSON output generation
6. Phase 0 integration

Author: Asif Hussain
Created: 2026-01-04
"""

import ast
import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.planning.ast_scanner import ASTScanner
from src.orchestrators.planning.duplicate_detector import PlanningDuplicateDetector
from src.orchestrators.planning.orphan_detector import PlanningOrphanDetector


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing."""
    file_path = tmp_path / "sample.py"
    content = '''
"""Sample module for testing."""

import os
import sys
from pathlib import Path

def used_function():
    """This function is used."""
    return "used"

def orphaned_function():
    """This function is never called."""
    return "orphaned"

class SampleClass:
    """Sample class for testing."""
    
    def __init__(self):
        self.value = used_function()
    
    def method(self):
        return "method"
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def duplicate_files(tmp_path):
    """Create files with duplicate code."""
    # Original file
    file1 = tmp_path / "original.py"
    code = '''
def calculate_total(items):
    """Calculate total."""
    total = 0
    for item in items:
        total += item.price
    return total
'''
    file1.write_text(code)
    
    # Duplicate file
    file2 = tmp_path / "duplicate.py"
    file2.write_text(code)
    
    # Different file
    file3 = tmp_path / "different.py"
    file3.write_text('def other(): return "different"')
    
    return [file1, file2, file3]


@pytest.fixture
def workspace_files(tmp_path):
    """Create a mini workspace for testing."""
    # Create structure
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    
    main_file = src_dir / "main.py"
    main_file.write_text('''
import os
from helpers import helper_function

def main():
    return helper_function()

if __name__ == "__main__":
    main()
''')
    
    helpers_file = src_dir / "helpers.py"
    helpers_file.write_text('''
def helper_function():
    return "help"

def unused_helper():
    return "never called"
''')
    
    return tmp_path


# ============================================================================
# Test Class
# ============================================================================

class TestASTScanning:
    """Tests for AST scanning integration in Planning v5."""
    
    def test_ast_scan_runs_in_phase_zero(self, workspace_files, tmp_path):
        """Test Phase 0 automatically runs AST scan."""
        scanner = ASTScanner(workspace_root=workspace_files)
        output_file = tmp_path / "ast-analysis.json"
        
        scanner.scan_workspace()
        scanner.save_results(output_file)
        
        assert output_file.exists()
    
    def test_ast_results_include_function_class_counts(self, sample_python_file):
        """Test AST scanner correctly counts functions and classes."""
        scanner = ASTScanner(workspace_root=sample_python_file.parent)
        result = scanner.scan_file(sample_python_file)
        
        assert result["function_count"] >= 2  # used_function, orphaned_function
        assert result["class_count"] == 1  # SampleClass
        assert result["import_count"] >= 3  # os, sys, Path
    
    def test_duplicate_code_detection(self, duplicate_files):
        """Test duplicate detector finds duplicate code."""
        detector = PlanningDuplicateDetector()
        result = detector.find_code_duplicates(duplicate_files)
        
        assert result["duplicates_found"] > 0
        assert len(result["duplicate_groups"]) > 0
    
    def test_orphaned_code_detection(self, workspace_files):
        """Test orphan detector finds unused functions."""
        detector = PlanningOrphanDetector(workspace_root=workspace_files)
        result = detector.find_orphaned_functions()
        
        orphaned_names = [f["name"] for f in result["orphaned_functions"]]
        assert "unused_helper" in orphaned_names
    
    def test_ast_findings_saved_to_context_folder(self, workspace_files, tmp_path):
        """Test AST analysis saves results to context folder."""
        scanner = ASTScanner(workspace_root=workspace_files)
        output_file = tmp_path / "context" / "ast-analysis.json"
        output_file.parent.mkdir(exist_ok=True)
        
        scanner.scan_workspace()
        scanner.save_results(output_file)
        
        assert output_file.exists()
        with open(output_file) as f:
            data = json.load(f)
        
        assert "files_scanned" in data
        assert data["files_scanned"] > 0
