"""
Tests for CodeSmellAnalyzer.

Tests anti-pattern and code quality issue detection.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path

from src.operations.modules.analysis.code_smell_analyzer import (
    CodeSmellAnalyzer,
    CodeSmell
)


class TestCodeSmellAnalyzer:
    """Test suite for CodeSmellAnalyzer."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.analyzer = CodeSmellAnalyzer()
        
    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test analyzer initialization."""
        assert len(self.analyzer.smell_detectors) == 6
        
    def test_analyze_empty_directory(self):
        """Test analysis on empty directory."""
        result = self.analyzer.analyze(self.project_root)
        
        assert 'smells' in result
        assert 'total_smells' in result
        assert 'by_type' in result
        assert 'by_severity' in result
        assert 'priority_fixes' in result
        assert result['total_smells'] == 0
        
    def test_detect_long_methods(self):
        """Test detection of long methods."""
        test_file = self.project_root / "long_method.py"
        code = "def long_func():\n" + "    pass\n" * 60
        test_file.write_text(code)
        
        result = self.analyzer.analyze(test_file)
        
        smells = [s for s in result['smells'] if s.smell_type == 'long_method']
        assert len(smells) > 0
        assert smells[0].severity == 'medium'
        
    def test_detect_large_classes(self):
        """Test detection of classes with too many methods."""
        test_file = self.project_root / "large_class.py"
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(25)])
        code = f"class LargeClass:\n{methods}"
        test_file.write_text(code)
        
        result = self.analyzer.analyze(test_file)
        
        smells = [s for s in result['smells'] if s.smell_type == 'large_class']
        assert len(smells) > 0
        assert smells[0].severity == 'high'
        
    def test_detect_god_objects(self):
        """Test detection of god objects."""
        test_file = self.project_root / "god_object.py"
        methods = "\n".join([f"    def method_{i}(self): pass" for i in range(20)])
        code = f"class GodObject:\n{methods}"
        test_file.write_text(code)
        
        result = self.analyzer.analyze(test_file)
        
        smells = [s for s in result['smells'] if s.smell_type == 'god_object']
        assert len(smells) > 0
        
    def test_detect_magic_numbers(self):
        """Test detection of magic numbers."""
        test_file = self.project_root / "magic_numbers.py"
        code = """
def calculate():
    result = 42 * 3.14159
    if value > 99:
        return result + 256
"""
        test_file.write_text(code)
        
        result = self.analyzer.analyze(test_file)
        
        smells = [s for s in result['smells'] if s.smell_type == 'magic_number']
        assert len(smells) >= 3  # 42, 3.14159, 99, 256
        
    def test_detect_deep_nesting(self):
        """Test detection of deep nesting."""
        test_file = self.project_root / "deep_nesting.py"
        code = """
def deeply_nested():
    if condition1:
        if condition2:
            if condition3:
                if condition4:
                    if condition5:
                        if condition6:
                            pass
"""
        test_file.write_text(code)
        
        result = self.analyzer.analyze(test_file)
        
        smells = [s for s in result['smells'] if s.smell_type == 'deep_nesting']
        assert len(smells) > 0
        assert smells[0].severity == 'medium'
        
    def test_detect_too_many_parameters(self):
        """Test detection of functions with too many parameters."""
        test_file = self.project_root / "many_params.py"
        code = "def func(a, b, c, d, e, f, g): pass"
        test_file.write_text(code)
        
        result = self.analyzer.analyze(test_file)
        
        smells = [s for s in result['smells'] if s.smell_type == 'too_many_parameters']
        assert len(smells) > 0
        assert smells[0].severity == 'medium'
        
    def test_group_by_type(self):
        """Test grouping smells by type."""
        smells = [
            CodeSmell('long_method', 'file.py', 10, 'desc', 'medium', 'rec'),
            CodeSmell('long_method', 'file.py', 20, 'desc', 'medium', 'rec'),
            CodeSmell('magic_number', 'file.py', 30, 'desc', 'low', 'rec')
        ]
        
        grouped = self.analyzer._group_by_type(smells)
        
        assert grouped['long_method'] == 2
        assert grouped['magic_number'] == 1
        
    def test_group_by_severity(self):
        """Test grouping smells by severity."""
        smells = [
            CodeSmell('type1', 'file.py', 10, 'desc', 'high', 'rec'),
            CodeSmell('type2', 'file.py', 20, 'desc', 'high', 'rec'),
            CodeSmell('type3', 'file.py', 30, 'desc', 'medium', 'rec'),
            CodeSmell('type4', 'file.py', 40, 'desc', 'low', 'rec')
        ]
        
        grouped = self.analyzer._group_by_severity(smells)
        
        assert grouped['high'] == 2
        assert grouped['medium'] == 1
        assert grouped['low'] == 1
        
    def test_prioritize_fixes(self):
        """Test fix prioritization."""
        smells = [
            CodeSmell('type1', 'file.py', 10, 'low priority', 'low', 'rec'),
            CodeSmell('type2', 'file.py', 20, 'high priority', 'high', 'rec'),
            CodeSmell('type3', 'file.py', 30, 'medium priority', 'medium', 'rec')
        ]
        
        priorities = self.analyzer._prioritize_fixes(smells)
        
        # High severity should come first
        assert 'high priority' in priorities[0]
        assert 'medium priority' in priorities[1]
        assert 'low priority' in priorities[2]
        
    def test_prioritize_fixes_limited(self):
        """Test fix prioritization limits to top 10."""
        smells = [
            CodeSmell('type', 'file.py', i, f'smell {i}', 'high', 'rec')
            for i in range(20)
        ]
        
        priorities = self.analyzer._prioritize_fixes(smells)
        
        assert len(priorities) == 10
        
    def test_analyze_file_invalid_python(self):
        """Test analyzing file with invalid Python syntax."""
        test_file = self.project_root / "invalid.py"
        test_file.write_text("def invalid syntax here")
        
        result = self.analyzer.analyze(test_file)
        
        # Should handle gracefully
        assert isinstance(result, dict)
        
    def test_analyze_multiple_files(self):
        """Test analyzing multiple files."""
        file1 = self.project_root / "file1.py"
        file1.write_text("def func(a, b, c, d, e, f): pass")
        
        file2 = self.project_root / "file2.py"
        file2.write_text("x = 42")
        
        result = self.analyzer.analyze(self.project_root)
        
        assert result['total_smells'] >= 2  # At least params + magic number


class TestCodeSmell:
    """Test suite for CodeSmell dataclass."""
    
    def test_creation(self):
        """Test CodeSmell creation."""
        smell = CodeSmell(
            smell_type='long_method',
            file_path='/path/to/file.py',
            line_number=42,
            description='Method too long',
            severity='medium',
            recommendation='Break into smaller methods'
        )
        
        assert smell.smell_type == 'long_method'
        assert smell.file_path == '/path/to/file.py'
        assert smell.line_number == 42
        assert smell.severity == 'medium'
        
    def test_severity_levels(self):
        """Test different severity levels."""
        high = CodeSmell('type', 'file', 1, 'desc', 'high', 'rec')
        medium = CodeSmell('type', 'file', 1, 'desc', 'medium', 'rec')
        low = CodeSmell('type', 'file', 1, 'desc', 'low', 'rec')
        
        assert high.severity == 'high'
        assert medium.severity == 'medium'
        assert low.severity == 'low'
