"""
Tests for CodeAnalyzer - Python code analysis
"""

import ast
import pytest
from pathlib import Path
from textwrap import dedent

from src.orchestration_4_0.orchestrators.documentation.extractors.code_analyzer import (
    CodeAnalyzer,
    ModuleInfo,
    ClassInfo,
    FunctionInfo,
    MethodInfo
)


@pytest.fixture
def analyzer():
    """Create a CodeAnalyzer instance"""
    return CodeAnalyzer()


@pytest.fixture
def sample_python_file(tmp_path):
    """Create a sample Python file for testing"""
    content = dedent('''
        """Sample module for testing"""
        
        from typing import List, Optional
        import os
        
        class BaseClass:
            """Base class docstring"""
            pass
        
        class SampleClass(BaseClass):
            """Sample class docstring"""
            
            attribute: str
            count: int = 0
            
            def __init__(self, name: str):
                """Initialize sample"""
                self.name = name
            
            def public_method(self, value: int) -> str:
                """Public method with docstring"""
                return str(value)
            
            def _private_method(self) -> None:
                """Private method"""
                pass
            
            @property
            def name_property(self) -> str:
                """Property docstring"""
                return self.name
            
            @abstractmethod
            def abstract_method(self) -> None:
                """Abstract method"""
                pass
        
        def standalone_function(param1: str, param2: Optional[int] = None) -> bool:
            """Standalone function docstring"""
            return True
    ''')
    
    file_path = tmp_path / "sample.py"
    file_path.write_text(content)
    return file_path


class TestCodeAnalyzer:
    """Tests for CodeAnalyzer class"""
    
    def test_analyze_file_basic(self, analyzer, sample_python_file):
        """Test basic file analysis"""
        module_info = analyzer.analyze_file(sample_python_file)
        
        assert isinstance(module_info, ModuleInfo)
        assert module_info.name == "sample"
        assert module_info.path == sample_python_file
        assert "Sample module for testing" in module_info.docstring
    
    def test_analyze_file_not_found(self, analyzer):
        """Test analyzing non-existent file"""
        with pytest.raises(FileNotFoundError):
            analyzer.analyze_file(Path("nonexistent.py"))
    
    def test_analyze_invalid_syntax(self, analyzer, tmp_path):
        """Test analyzing file with invalid Python syntax"""
        invalid_file = tmp_path / "invalid.py"
        invalid_file.write_text("def broken syntax(:")
        
        with pytest.raises(SyntaxError):
            analyzer.analyze_file(invalid_file)
    
    def test_extract_imports(self, analyzer, sample_python_file):
        """Test import extraction"""
        module_info = analyzer.analyze_file(sample_python_file)
        
        assert 'typing' in module_info.imports
        assert 'os' in module_info.imports
        assert 'typing' in module_info.dependencies
        assert 'os' in module_info.dependencies
    
    def test_extract_classes(self, analyzer, sample_python_file):
        """Test class extraction"""
        module_info = analyzer.analyze_file(sample_python_file)
        
        assert len(module_info.classes) == 2
        
        # Check SampleClass
        sample_class = next(cls for cls in module_info.classes if cls.name == "SampleClass")
        assert sample_class.docstring == "Sample class docstring"
        assert "BaseClass" in sample_class.base_classes
        assert len(sample_class.methods) >= 4
    
    def test_extract_class_attributes(self, analyzer, sample_python_file):
        """Test class attribute extraction"""
        module_info = analyzer.analyze_file(sample_python_file)
        sample_class = next(cls for cls in module_info.classes if cls.name == "SampleClass")
        
        # Check attributes
        attr_names = [attr['name'] for attr in sample_class.attributes]
        assert 'attribute' in attr_names
        assert 'count' in attr_names
    
    def test_extract_methods(self, analyzer, sample_python_file):
        """Test method extraction"""
        module_info = analyzer.analyze_file(sample_python_file)
        sample_class = next(cls for cls in module_info.classes if cls.name == "SampleClass")
        
        # Check public_method
        public_method = next(m for m in sample_class.methods if m.name == "public_method")
        assert public_method.docstring == "Public method with docstring"
        assert public_method.return_type == "str"
        assert len(public_method.parameters) == 2  # self, value
        assert public_method.parameters[1]['name'] == 'value'
        assert public_method.parameters[1]['type'] == 'int'
    
    def test_extract_properties(self, analyzer, sample_python_file):
        """Test property decorator detection"""
        module_info = analyzer.analyze_file(sample_python_file)
        sample_class = next(cls for cls in module_info.classes if cls.name == "SampleClass")
        
        name_property = next(m for m in sample_class.methods if m.name == "name_property")
        assert name_property.is_property
        assert 'property' in name_property.decorators
    
    def test_extract_abstract_methods(self, analyzer, sample_python_file):
        """Test abstract method detection"""
        module_info = analyzer.analyze_file(sample_python_file)
        sample_class = next(cls for cls in module_info.classes if cls.name == "SampleClass")
        
        abstract_method = next(m for m in sample_class.methods if m.name == "abstract_method")
        assert abstract_method.is_abstract
        assert 'abstractmethod' in abstract_method.decorators
    
    def test_extract_functions(self, analyzer, sample_python_file):
        """Test standalone function extraction"""
        module_info = analyzer.analyze_file(sample_python_file)
        
        assert len(module_info.functions) == 1
        
        func = module_info.functions[0]
        assert func.name == "standalone_function"
        assert func.docstring == "Standalone function docstring"
        assert func.return_type == "bool"
        assert len(func.parameters) == 2
    
    def test_extract_function_parameters(self, analyzer, sample_python_file):
        """Test function parameter extraction with defaults"""
        module_info = analyzer.analyze_file(sample_python_file)
        func = module_info.functions[0]
        
        # param1: str
        assert func.parameters[0]['name'] == 'param1'
        assert func.parameters[0]['type'] == 'str'
        assert func.parameters[0]['default'] is None
        
        # param2: Optional[int] = None
        assert func.parameters[1]['name'] == 'param2'
        assert 'Optional[int]' in func.parameters[1]['type']
        assert func.parameters[1]['default'] == 'None'
    
    def test_method_signature_generation(self, analyzer, sample_python_file):
        """Test method signature string generation"""
        module_info = analyzer.analyze_file(sample_python_file)
        sample_class = next(cls for cls in module_info.classes if cls.name == "SampleClass")
        
        public_method = next(m for m in sample_class.methods if m.name == "public_method")
        assert "public_method(self, value: int) -> str" in public_method.signature
    
    def test_line_numbers(self, analyzer, sample_python_file):
        """Test that line numbers are captured"""
        module_info = analyzer.analyze_file(sample_python_file)
        
        for cls in module_info.classes:
            assert cls.line_number > 0
            for method in cls.methods:
                assert method.line_number > 0
        
        for func in module_info.functions:
            assert func.line_number > 0
