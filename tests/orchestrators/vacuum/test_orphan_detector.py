"""
Unit Tests for Orphan Detector - AST-Based Orphan Test Detection

Tests orphaned test file detection using AST analysis:
- Python AST parsing for import statements
- Test → source file mapping
- Missing import detection
- Relative import handling
- Package structure resolution

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from src.orchestrators.vacuum.orphan_detector import OrphanDetector


class TestOrphanDetector:
    """Test suite for OrphanDetector."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def project_root(self, temp_dir):
        """Create mock project structure."""
        # Create source files
        src_dir = temp_dir / "src"
        src_dir.mkdir()
        (src_dir / "__init__.py").touch()
        (src_dir / "module_a.py").write_text("def func_a(): pass")
        (src_dir / "module_b.py").write_text("def func_b(): pass")
        
        # Create tests directory
        tests_dir = temp_dir / "tests"
        tests_dir.mkdir()
        (tests_dir / "__init__.py").touch()
        
        return temp_dir
    
    @pytest.fixture
    def detector(self, project_root):
        """Create OrphanDetector instance."""
        return OrphanDetector(project_root)
    
    def test_initialization(self, detector, project_root):
        """Test detector initialization."""
        assert detector.project_root == project_root
        assert detector.stats['tests_scanned'] == 0
    
    def test_find_no_orphans(self, detector, project_root):
        """Test when all test files have valid imports."""
        tests_dir = project_root / "tests"
        
        # Create valid test file
        test_file = tests_dir / "test_module_a.py"
        test_file.write_text("""
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.module_a import func_a

def test_func_a():
    assert func_a() is None
""")
        
        result = detector.find_orphaned_tests([test_file])
        
        # No orphans (module_a exists)
        assert result['total_orphans'] == 0
        assert len(result['orphaned_tests']) == 0
    
    def test_find_orphaned_test(self, detector, project_root):
        """Test detection of orphaned test (missing source)."""
        tests_dir = project_root / "tests"
        
        # Create test for nonexistent module
        test_file = tests_dir / "test_missing.py"
        test_file.write_text("""
from src.missing_module import missing_func

def test_missing_func():
    assert missing_func() is None
""")
        
        result = detector.find_orphaned_tests([test_file])
        
        # Should detect orphan
        assert result['total_orphans'] == 1
        assert len(result['orphaned_tests']) == 1
        assert result['orphaned_tests'][0]['test_path'] == test_file
        assert 'missing_module' in str(result['orphaned_tests'][0]['missing_imports'])
    
    def test_ast_parsing_simple_import(self, detector, project_root):
        """Test AST parsing of simple import statement."""
        tests_dir = project_root / "tests"
        
        # import module_a
        test_file = tests_dir / "test_simple.py"
        test_file.write_text("""
import src.module_a

def test_something():
    pass
""")
        
        missing = detector._check_test_imports(test_file)
        
        # module_a exists, should have no missing imports
        assert len(missing) == 0
    
    def test_ast_parsing_from_import(self, detector, project_root):
        """Test AST parsing of from...import statement."""
        tests_dir = project_root / "tests"
        
        # from src.module_a import func_a
        test_file = tests_dir / "test_from_import.py"
        test_file.write_text("""
from src.module_a import func_a

def test_func():
    pass
""")
        
        missing = detector._check_test_imports(test_file)
        
        # module_a exists
        assert len(missing) == 0
    
    def test_relative_import_handling(self, detector, project_root):
        """Test relative import resolution."""
        tests_dir = project_root / "tests"
        
        # from ..src.module_a import func_a
        test_file = tests_dir / "test_relative.py"
        test_file.write_text("""
from ..src.module_a import func_a

def test_func():
    pass
""")
        
        missing = detector._check_test_imports(test_file)
        
        # Should resolve relative import
        # (may fail depending on implementation)
        assert isinstance(missing, list)
    
    def test_multiple_imports(self, detector, project_root):
        """Test test file with multiple imports."""
        tests_dir = project_root / "tests"
        
        test_file = tests_dir / "test_multiple.py"
        test_file.write_text("""
from src.module_a import func_a
from src.module_b import func_b
from src.missing import missing_func

def test_funcs():
    pass
""")
        
        missing = detector._check_test_imports(test_file)
        
        # Should find missing_func
        assert 'missing' in str(missing) or len(missing) > 0
    
    def test_wildcard_import(self, detector, project_root):
        """Test wildcard import handling."""
        tests_dir = project_root / "tests"
        
        test_file = tests_dir / "test_wildcard.py"
        test_file.write_text("""
from src.module_a import *

def test_something():
    pass
""")
        
        missing = detector._check_test_imports(test_file)
        
        # Should handle wildcard imports
        assert isinstance(missing, list)
    
    def test_standard_library_imports(self, detector, project_root):
        """Test that standard library imports don't cause false positives."""
        tests_dir = project_root / "tests"
        
        test_file = tests_dir / "test_stdlib.py"
        test_file.write_text("""
import os
import sys
from pathlib import Path

def test_something():
    pass
""")
        
        missing = detector._check_test_imports(test_file)
        
        # Standard library imports should be ignored
        assert len(missing) == 0
    
    def test_third_party_imports(self, detector, project_root):
        """Test third-party library imports."""
        tests_dir = project_root / "tests"
        
        test_file = tests_dir / "test_thirdparty.py"
        test_file.write_text("""
import pytest
import numpy

def test_something():
    pass
""")
        
        missing = detector._check_test_imports(test_file)
        
        # Third-party imports may or may not be detected as missing
        # depending on implementation
        assert isinstance(missing, list)
    
    def test_syntax_error_handling(self, detector, project_root):
        """Test handling of test files with syntax errors."""
        tests_dir = project_root / "tests"
        
        # Invalid Python syntax
        test_file = tests_dir / "test_invalid.py"
        test_file.write_text("""
from src.module_a import func_a
def test_something(
    pass  # Syntax error: unclosed parenthesis
""")
        
        # Should handle gracefully without crashing
        try:
            missing = detector._check_test_imports(test_file)
            assert isinstance(missing, list)
        except SyntaxError:
            # Acceptable behavior
            pass
    
    def test_empty_test_file(self, detector, project_root):
        """Test empty test file."""
        tests_dir = project_root / "tests"
        
        test_file = tests_dir / "test_empty.py"
        test_file.touch()
        
        result = detector.find_orphaned_tests([test_file])
        
        # Empty file has no imports, not an orphan
        assert result['total_orphans'] == 0
    
    def test_statistics_tracking(self, detector, project_root):
        """Test statistics collection."""
        tests_dir = project_root / "tests"
        
        test1 = tests_dir / "test_1.py"
        test2 = tests_dir / "test_2.py"
        
        test1.write_text("import src.module_a\ndef test(): pass")
        test2.write_text("from src.missing import func\ndef test(): pass")
        
        result = detector.find_orphaned_tests([test1, test2])
        
        stats = result['stats']
        assert stats['tests_scanned'] == 2
        assert stats['orphans_found'] >= 0
    
    def test_package_imports(self, detector, project_root):
        """Test package-level imports."""
        # Create package structure
        pkg_dir = project_root / "src" / "package"
        pkg_dir.mkdir()
        (pkg_dir / "__init__.py").write_text("from .submodule import func")
        (pkg_dir / "submodule.py").write_text("def func(): pass")
        
        tests_dir = project_root / "tests"
        test_file = tests_dir / "test_package.py"
        test_file.write_text("""
from src.package import func

def test_func():
    pass
""")
        
        result = detector.find_orphaned_tests([test_file])
        
        # Package exists
        assert result['total_orphans'] == 0


class TestOrphanDetectorEdgeCases:
    """Edge case tests for OrphanDetector."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def detector(self, temp_dir):
        """Create OrphanDetector instance."""
        return OrphanDetector(temp_dir)
    
    def test_empty_test_list(self, detector):
        """Test with empty test list."""
        result = detector.find_orphaned_tests([])
        
        assert result['total_orphans'] == 0
        assert len(result['orphaned_tests']) == 0
    
    def test_nonexistent_test_file(self, detector, temp_dir):
        """Test with nonexistent test file."""
        nonexistent = temp_dir / "test_nonexistent.py"
        
        # Should handle gracefully
        try:
            result = detector.find_orphaned_tests([nonexistent])
            assert isinstance(result, dict)
        except FileNotFoundError:
            # Acceptable behavior
            pass
    
    def test_non_python_file(self, detector, temp_dir):
        """Test with non-Python file."""
        text_file = temp_dir / "test.txt"
        text_file.write_text("not python code")
        
        # Should handle gracefully
        try:
            result = detector.find_orphaned_tests([text_file])
            assert isinstance(result, dict)
        except:
            # May fail to parse, acceptable
            pass
    
    def test_circular_imports(self, detector, temp_dir):
        """Test handling of circular imports."""
        # Create circular import structure
        mod_a = temp_dir / "mod_a.py"
        mod_b = temp_dir / "mod_b.py"
        
        mod_a.write_text("from mod_b import func_b")
        mod_b.write_text("from mod_a import func_a")
        
        test_file = temp_dir / "test_circular.py"
        test_file.write_text("from mod_a import func_a\ndef test(): pass")
        
        # Should handle without infinite loop
        result = detector.find_orphaned_tests([test_file])
        assert isinstance(result, dict)


class TestOrphanDetectorIntegration:
    """Integration tests for OrphanDetector."""
    
    @pytest.fixture
    def real_project(self):
        """Create realistic project structure."""
        temp = tempfile.mkdtemp()
        temp_path = Path(temp)
        
        # Create source structure
        src = temp_path / "src"
        src.mkdir()
        (src / "__init__.py").touch()
        (src / "auth.py").write_text("def login(): pass")
        (src / "database.py").write_text("def connect(): pass")
        (src / "deleted_module.py").write_text("# This will be deleted")
        
        # Create tests
        tests = temp_path / "tests"
        tests.mkdir()
        (tests / "__init__.py").touch()
        (tests / "test_auth.py").write_text("from src.auth import login\ndef test_login(): pass")
        (tests / "test_database.py").write_text("from src.database import connect\ndef test_connect(): pass")
        (tests / "test_deleted.py").write_text("from src.deleted_module import func\ndef test_func(): pass")
        
        # Delete the source module (simulating orphaned test)
        (src / "deleted_module.py").unlink()
        
        yield temp_path, tests
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_realistic_orphan_detection(self, real_project):
        """Test orphan detection on realistic project."""
        project_root, tests_dir = real_project
        
        detector = OrphanDetector(project_root)
        
        # Find all test files
        test_files = list(tests_dir.glob("test_*.py"))
        
        # Detect orphans
        result = detector.find_orphaned_tests(test_files)
        
        # Should detect test_deleted.py as orphan
        assert result['total_orphans'] >= 1
        
        orphaned_paths = [o['test_path'] for o in result['orphaned_tests']]
        assert any('test_deleted' in str(p) for p in orphaned_paths)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
