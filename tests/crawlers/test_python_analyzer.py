"""
Test suite for PythonAnalyzer class.

TDD approach for Python code analysis using AST.
"""

import pytest
from pathlib import Path


class TestPythonAnalyzerInitialization:
    """Test PythonAnalyzer initialization."""
    
    def test_analyzer_exists(self):
        """Test that PythonAnalyzer class can be imported and instantiated."""
        from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
        
        analyzer = PythonAnalyzer()
        assert analyzer is not None


class TestPythonAnalyzerBasicAnalysis:
    """Test basic Python file analysis."""
    
    def test_analyze_method_exists(self, tmp_path):
        """Test that analyze() method exists."""
        from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
        
        # Create simple Python file
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        
        analyzer = PythonAnalyzer()
        result = analyzer.analyze(str(test_file))
        assert result is not None
    
    def test_analyze_returns_dict(self, tmp_path):
        """Test that analyze() returns a dictionary with metrics."""
        from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
        
        test_file = tmp_path / "test.py"
        test_file.write_text("print('hello')")
        
        analyzer = PythonAnalyzer()
        result = analyzer.analyze(str(test_file))
        
        assert isinstance(result, dict)
        assert 'file_path' in result
        assert 'language' in result
        assert result['language'] == 'python'


class TestPythonAnalyzerFunctionDetection:
    """Test function detection in Python files."""
    
    def test_detect_functions(self, tmp_path):
        """Test that analyzer detects function definitions."""
        from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
        
        code = """
def hello():
    print('hello')

def goodbye():
    print('bye')
"""
        test_file = tmp_path / "functions.py"
        test_file.write_text(code)
        
        analyzer = PythonAnalyzer()
        result = analyzer.analyze(str(test_file))
        
        assert 'functions' in result
        assert len(result['functions']) == 2
        assert 'hello' in result['functions']
        assert 'goodbye' in result['functions']


class TestPythonAnalyzerClassDetection:
    """Test class detection in Python files."""
    
    def test_detect_classes(self, tmp_path):
        """Test that analyzer detects class definitions."""
        from src.crawlers.analyzers.python_analyzer import PythonAnalyzer
        
        code = """
class Person:
    def __init__(self, name):
        self.name = name

class Animal:
    pass
"""
        test_file = tmp_path / "classes.py"
        test_file.write_text(code)
        
        analyzer = PythonAnalyzer()
        result = analyzer.analyze(str(test_file))
        
        assert 'classes' in result
        assert len(result['classes']) == 2
        assert 'Person' in result['classes']
        assert 'Animal' in result['classes']
