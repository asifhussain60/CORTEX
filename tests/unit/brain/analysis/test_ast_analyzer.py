"""
Tests for ASTAnalyzer.

Authority: CORE-008 (TDD - Tests BEFORE code)
"""

import ast
from pathlib import Path
from typing import List

import pytest

from cortex.lens.analyzers.ast_analyzer import (
    ASTAnalyzer,
    FunctionInfo,
    ClassInfo,
    ImportInfo,
    ASTAnalysisResult,
)


class TestFunctionInfo:
    """Test FunctionInfo dataclass."""
    
    def test_function_info_creation(self):
        """Test creating FunctionInfo."""
        func = FunctionInfo(
            name="calculate",
            line_number=10,
            parameters=["x", "y"],
            return_type="int",
            docstring="Calculate sum",
            decorators=["staticmethod"],
            is_async=False,
        )
        assert func.name == "calculate"
        assert len(func.parameters) == 2
        assert func.return_type == "int"


class TestClassInfo:
    """Test ClassInfo dataclass."""
    
    def test_class_info_creation(self):
        """Test creating ClassInfo."""
        cls = ClassInfo(
            name="Calculator",
            line_number=5,
            bases=["object"],
            methods=["add", "subtract"],
            docstring="A simple calculator",
            decorators=[],
        )
        assert cls.name == "Calculator"
        assert len(cls.methods) == 2


class TestImportInfo:
    """Test ImportInfo dataclass."""
    
    def test_import_info_creation(self):
        """Test creating ImportInfo."""
        imp = ImportInfo(
            module="os.path",
            names=["join", "exists"],
            alias="",
            line_number=1,
        )
        assert imp.module == "os.path"
        assert len(imp.names) == 2


class TestASTAnalyzer:
    """Test ASTAnalyzer functionality."""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance."""
        return ASTAnalyzer()
    
    def test_analyzer_initialization(self, analyzer: ASTAnalyzer):
        """Test analyzer initialization."""
        assert analyzer is not None
    
    def test_analyze_simple_function(self, analyzer: ASTAnalyzer):
        """Test analyzing a simple function."""
        code = '''
def add(x, y):
    """Add two numbers."""
    return x + y
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.functions) == 1
        assert result.functions[0].name == "add"
        assert result.functions[0].parameters == ["x", "y"]
        assert "Add two numbers" in result.functions[0].docstring
    
    def test_analyze_async_function(self, analyzer: ASTAnalyzer):
        """Test analyzing async function."""
        code = '''
async def fetch_data(url):
    """Fetch data asynchronously."""
    pass
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.functions) == 1
        assert result.functions[0].name == "fetch_data"
        assert result.functions[0].is_async is True
    
    def test_analyze_function_with_decorators(self, analyzer: ASTAnalyzer):
        """Test analyzing function with decorators."""
        code = '''
@staticmethod
@property
def get_value():
    return 42
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.functions) == 1
        assert "staticmethod" in result.functions[0].decorators
        assert "property" in result.functions[0].decorators
    
    def test_analyze_simple_class(self, analyzer: ASTAnalyzer):
        """Test analyzing a simple class."""
        code = '''
class Calculator:
    """A simple calculator."""
    
    def add(self, x, y):
        return x + y
    
    def subtract(self, x, y):
        return x - y
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.classes) == 1
        assert result.classes[0].name == "Calculator"
        assert "add" in result.classes[0].methods
        assert "subtract" in result.classes[0].methods
        assert "simple calculator" in result.classes[0].docstring.lower()
    
    def test_analyze_class_with_inheritance(self, analyzer: ASTAnalyzer):
        """Test analyzing class with inheritance."""
        code = '''
class AdvancedCalculator(Calculator, Loggable):
    """An advanced calculator."""
    pass
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.classes) == 1
        assert "Calculator" in result.classes[0].bases
        assert "Loggable" in result.classes[0].bases
    
    def test_analyze_imports(self, analyzer: ASTAnalyzer):
        """Test analyzing import statements."""
        code = '''
import os
import sys
from pathlib import Path
from typing import List, Dict
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.imports) == 4
        
        # Check os import
        os_import = [i for i in result.imports if i.module == "os"][0]
        assert os_import.names == ["os"]
        
        # Check pathlib import
        path_import = [i for i in result.imports if i.module == "pathlib"][0]
        assert "Path" in path_import.names
    
    def test_analyze_import_with_alias(self, analyzer: ASTAnalyzer):
        """Test analyzing import with alias."""
        code = '''
import numpy as np
from collections import OrderedDict as OD
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.imports) == 2
        
        numpy_import = [i for i in result.imports if i.module == "numpy"][0]
        assert numpy_import.alias == "np"
    
    def test_analyze_invalid_syntax(self, analyzer: ASTAnalyzer):
        """Test analyzing code with syntax errors."""
        code = '''
def broken(
    # Missing closing parenthesis and colon
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is False
        assert "syntax" in result.error.lower()
    
    def test_analyze_file_success(self, analyzer: ASTAnalyzer, tmp_path: Path):
        """Test analyzing a file."""
        file_path = tmp_path / "test.py"
        file_path.write_text('''
def hello():
    """Say hello."""
    return "Hello, World!"
''')
        
        result = analyzer.analyze_file(file_path)
        
        assert result.success is True
        assert len(result.functions) == 1
        assert result.functions[0].name == "hello"
    
    def test_analyze_file_not_found(self, analyzer: ASTAnalyzer):
        """Test analyzing non-existent file."""
        result = analyzer.analyze_file(Path("/nonexistent/file.py"))
        
        assert result.success is False
        assert "not found" in result.error.lower()
    
    def test_get_function_signatures(self, analyzer: ASTAnalyzer):
        """Test extracting function signatures."""
        code = '''
def add(x: int, y: int) -> int:
    return x + y

def greet(name: str = "World") -> str:
    return f"Hello, {name}!"
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert len(result.functions) == 2
        
        add_func = result.functions[0]
        assert add_func.return_type == "int"
        
        greet_func = result.functions[1]
        assert greet_func.return_type == "str"
    
    def test_get_complexity_metrics(self, analyzer: ASTAnalyzer):
        """Test extracting complexity metrics."""
        code = '''
def complex_function(x):
    if x > 0:
        if x > 10:
            return "high"
        else:
            return "medium"
    else:
        return "low"
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        assert "line_count" in result.metadata
        assert result.metadata["line_count"] > 0
    
    def test_nested_class_analysis(self, analyzer: ASTAnalyzer):
        """Test analyzing nested classes."""
        code = '''
class Outer:
    class Inner:
        def method(self):
            pass
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        # Should find both Outer and Inner classes
        class_names = [c.name for c in result.classes]
        assert "Outer" in class_names
        assert "Inner" in class_names
    
    def test_lambda_functions(self, analyzer: ASTAnalyzer):
        """Test that lambda functions are not included in function list."""
        code = '''
add = lambda x, y: x + y

def real_function():
    return 42
'''
        result = analyzer.analyze_code(code)
        
        assert result.success is True
        # Should only find real_function, not lambda
        assert len(result.functions) == 1
        assert result.functions[0].name == "real_function"


class TestASTIntegration:
    """Integration tests for AST analysis."""
    
    def test_analyze_real_python_file(self, tmp_path: Path):
        """Test analyzing a complete Python module."""
        file_path = tmp_path / "module.py"
        file_path.write_text('''
"""A test module."""

import os
from typing import List

class DataProcessor:
    """Process data."""
    
    def __init__(self, data: List[str]):
        self.data = data
    
    def process(self) -> List[str]:
        """Process the data."""
        return [item.upper() for item in self.data]

def main():
    """Main entry point."""
    processor = DataProcessor(["hello", "world"])
    print(processor.process())

if __name__ == "__main__":
    main()
''')
        
        analyzer = ASTAnalyzer()
        result = analyzer.analyze_file(file_path)
        
        assert result.success is True
        assert len(result.classes) == 1
        assert len(result.functions) >= 1  # main + possibly __init__
        assert len(result.imports) == 2
        assert result.classes[0].name == "DataProcessor"
