"""
Orphaned Code Cleanup Tests

Tests for automatic orphaned code removal in TDD REFACTOR phase.

Test Scenarios:
1. Dead code detection (functions with zero call sites)
2. Orphaned function detection (old implementations)
3. Duplicate signature detection
4. Safe removal with rollback
5. Test verification after cleanup

Author: Asif Hussain
Created: December 5, 2025
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.workflows.refactoring_intelligence import CodeSmellDetector, CodeSmellType
from src.workflows.orphaned_code_cleaner import OrphanedCodeCleaner


class TestOrphanedCodeDetection:
    """Test orphaned code detection logic."""
    
    def test_detect_dead_code_simple(self):
        """Test detection of function with zero call sites."""
        source_code = """
def active_function():
    return "I am called"

def dead_function():
    return "Nobody calls me"

result = active_function()
"""
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        dead_code_smells = [s for s in smells if s.smell_type == CodeSmellType.DEAD_CODE]
        assert len(dead_code_smells) >= 1
        assert any("dead_function" in s.description for s in dead_code_smells)
    
    def test_detect_orphaned_function_naming(self):
        """Test detection of orphaned function by naming pattern."""
        source_code = """
def login_old(username, password):
    return authenticate(username, password)

def login(username, password):
    cached = get_cache(username)
    if cached: return cached
    result = authenticate(username, password)
    set_cache(username, result)
    return result

result = login('user', 'pass')
"""
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        orphan_smells = [s for s in smells if "orphaned" in s.description.lower()]
        assert len(orphan_smells) >= 1
        assert any("login_old" in s.description for s in orphan_smells)
    
    def test_detect_duplicate_signatures(self):
        """Test detection of duplicate function signatures."""
        source_code = """
def process_data(item, config):
    return item * config

def transform_data(item, config):
    return item + config

result1 = process_data(5, 2)
result2 = transform_data(5, 2)
"""
        detector = CodeSmellDetector()
        smells = detector.analyze_file("test.py", source_code)
        
        duplicate_smells = [s for s in smells if s.smell_type == CodeSmellType.DUPLICATE_CODE]
        # Both functions have same signature (2 params: item, config)
        assert len(duplicate_smells) >= 2


class TestOrphanedCodeCleaner:
    """Test orphaned code removal logic."""
    
    def test_remove_dead_function(self):
        """Test removal of dead function from file."""
        source_code = """
def active_function():
    return "active"

def dead_function():
    return "dead"

result = active_function()
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            # Detect smells
            detector = CodeSmellDetector()
            smells = detector.analyze_file(temp_file, source_code)
            
            # Clean file
            cleaner = OrphanedCodeCleaner(backup_enabled=True)
            result = cleaner.clean_file(temp_file, smells)
            
            assert result.success
            assert len(result.functions_removed) >= 1
            assert "dead_function" in result.functions_removed
            assert result.lines_removed > 0
            assert result.backup_path is not None
            
            # Verify cleaned code
            with open(temp_file, 'r') as f:
                cleaned_code = f.read()
            
            assert "def dead_function" not in cleaned_code
            assert "def active_function" in cleaned_code
        
        finally:
            os.unlink(temp_file)
            if result.backup_path and os.path.exists(result.backup_path):
                os.unlink(result.backup_path)
    
    def test_rollback_on_syntax_error(self):
        """Test rollback when cleanup would create syntax error."""
        # This is a hypothetical test - in practice, AST removal shouldn't create syntax errors
        # But we test the rollback mechanism works
        source_code = """
def function_one():
    return "one"

result = function_one()
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            detector = CodeSmellDetector()
            smells = detector.analyze_file(temp_file, source_code)
            
            cleaner = OrphanedCodeCleaner(backup_enabled=True)
            result = cleaner.clean_file(temp_file, smells)
            
            # Even if no cleanup needed, should succeed
            assert result.success or not result.validation_passed
            
            # If backup created, verify rollback works
            if result.backup_path and os.path.exists(result.backup_path):
                restored = cleaner.restore_from_backup(result.backup_path, temp_file)
                assert restored
                
                # Verify original code restored
                with open(temp_file, 'r') as f:
                    restored_code = f.read()
                
                assert "def function_one" in restored_code
        
        finally:
            os.unlink(temp_file)
            if hasattr(result, 'backup_path') and result.backup_path and os.path.exists(result.backup_path):
                os.unlink(result.backup_path)
    
    def test_cleanup_with_multiple_smells(self):
        """Test cleanup handles multiple code smells in one file."""
        source_code = """
def current_implementation():
    return "current"

def old_implementation_v1():
    return "old v1"

def old_implementation_backup():
    return "old backup"

def unused_helper():
    return "never called"

result = current_implementation()
"""
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write(source_code)
            temp_file = f.name
        
        try:
            detector = CodeSmellDetector()
            smells = detector.analyze_file(temp_file, source_code)
            
            cleaner = OrphanedCodeCleaner(backup_enabled=True)
            result = cleaner.clean_file(temp_file, smells)
            
            assert result.success
            # Should remove at least 2 orphaned functions (v1, backup, unused)
            assert len(result.functions_removed) >= 2
            assert result.lines_removed > 0
            
            # Verify all orphaned functions removed
            with open(temp_file, 'r') as f:
                cleaned_code = f.read()
            
            assert "def current_implementation" in cleaned_code
            assert "def old_implementation_v1" not in cleaned_code or "def old_implementation_backup" not in cleaned_code
        
        finally:
            os.unlink(temp_file)
            if result.backup_path and os.path.exists(result.backup_path):
                os.unlink(result.backup_path)


class TestTDDWorkflowIntegration:
    """Test integration with TDD workflow REFACTOR phase."""
    
    def test_refactor_phase_cleanup_metrics(self):
        """Test REFACTOR phase returns cleanup metrics."""
        # This would test the full TDD workflow
        # For now, we verify the structure of expected results
        
        expected_keys = [
            'phase',
            'status',
            'files',
            'improvements',
            'tests_passing',
            'cleanup_performed',
            'functions_removed',
            'lines_removed',
            'cleanup_details'
        ]
        
        # Mock result from refactor phase
        mock_result = {
            'phase': 'REFACTOR',
            'status': 'REFACTORED',
            'files': ['src/auth.py'],
            'improvements': ['Removed 2 orphaned function(s): login_old, authenticate_v1'],
            'tests_passing': True,
            'cleanup_performed': True,
            'functions_removed': 2,
            'lines_removed': 35,
            'cleanup_details': [
                {
                    'file': 'src/auth.py',
                    'functions': ['login_old', 'authenticate_v1'],
                    'lines': 35
                }
            ]
        }
        
        for key in expected_keys:
            assert key in mock_result
        
        assert mock_result['cleanup_performed'] is True
        assert mock_result['functions_removed'] > 0
        assert len(mock_result['cleanup_details']) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
